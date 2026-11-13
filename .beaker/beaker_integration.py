"""Beaker repository Integration for HANDBOOK.md SOP tasks.

The candidate is ``candidate/system_prompt.md``, prepended to each task's own system prompt.
Each case runs a tool-calling loop against an in-process copy of the task's mock office
(see ``world.py``), then scores the task's deterministic rubric verifiers on the final state.
"""

from __future__ import annotations

import asyncio
import base64
import json
import os
import shutil
import tempfile
import tomllib
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

from beaker import (
    Case,
    CaseResult,
    CaseScore,
    Check,
    Integration,
    JsonValue,
    RetryableCaseError,
    RolloutRuntime,
    RunSetup,
    SetupRuntime,
    inference_target,
    repository,
)
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from world import TASKS_DIR, World

DEFAULT_MODEL = "gpt-5.6-luna"
MAX_AGENT_STEPS = 40
CASE_TIMEOUT_SECONDS = 600


class TaskRow(BaseModel):
    id: str = Field(min_length=1)
    input: dict[str, JsonValue]
    expected: dict[str, JsonValue]


class TaskSetup(RunSetup[TaskRow]):
    row_model = TaskRow

    async def load_cases(self, row: TaskRow, *, runtime: SetupRuntime) -> AsyncIterator[Case]:
        del runtime
        yield Case(id=row.id, input=row.input, expected=row.expected)


def _task_dir(case_input: JsonValue) -> Path:
    task_name = str(case_input["task_name"]) if isinstance(case_input, dict) else ""
    task_dir = TASKS_DIR / task_name
    if not (task_dir / "task.toml").is_file():
        raise KeyError(f"unknown HANDBOOK task {task_name!r}")
    return task_dir


def _task_environment(task_dir: Path) -> dict[str, str]:
    return tomllib.loads((task_dir / "task.toml").read_text())["environment"]["env"]


def _client_and_model(runtime: RolloutRuntime[Any]) -> tuple[AsyncOpenAI, str]:
    """The selected model through Beaker's gateway, else the default through the provider proxy."""
    if runtime.model:
        target = inference_target(runtime)
        return AsyncOpenAI(base_url=target.base_url, api_key=target.api_key, max_retries=0), target.model
    return AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"), max_retries=0), DEFAULT_MODEL


async def _run_agent(client: AsyncOpenAI, model: str, world: World, system_prompt: str, instruction: str) -> int:
    tools = [{"type": "function", "function": spec} for spec in world.tool_specs]
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": instruction},
    ]
    for step in range(MAX_AGENT_STEPS):
        response = await client.chat.completions.create(model=model, messages=messages, tools=tools)
        message = response.choices[0].message
        messages.append(message.model_dump(exclude_none=True))
        if not message.tool_calls:
            return step + 1
        for call in message.tool_calls:
            try:
                arguments = json.loads(call.function.arguments or "{}")
                result = await world.call_tool(call.function.name, arguments)
            except json.JSONDecodeError as error:
                result = f"Error: invalid JSON arguments: {error}"
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
    return MAX_AGENT_STEPS


async def run_case(*, case_input: JsonValue, runtime: RolloutRuntime[Any]) -> CaseResult:
    task_dir = _task_dir(case_input)
    environment = _task_environment(task_dir)
    candidate_prompt = (Path(runtime.targets_dir) / "candidate" / "system_prompt.md").read_text()
    system_prompt = f"{candidate_prompt.strip()}\n\n{(task_dir / 'system_prompt.md').read_text().strip()}"
    instruction = (task_dir / "instruction.md").read_text().strip()
    client, model = _client_and_model(runtime)
    case_dir = Path(tempfile.mkdtemp(prefix="handbook-case-"))
    world = await World.create(
        task_dir, case_dir / "world", environment["HANDBOOK_TOOL_SETS"].split(), environment["HANDBOOK_CURRENT_TIME"]
    )
    try:
        with runtime.trace.stage("handbook.agent_loop", inputs={"task": task_dir.name, "model": model}) as stage:
            try:
                steps = await asyncio.wait_for(
                    _run_agent(client, model, world, system_prompt, instruction), CASE_TIMEOUT_SECONDS
                )
            except TimeoutError as error:
                stage.output({"error": "timeout"})
                raise RetryableCaseError(f"timeout after {CASE_TIMEOUT_SECONDS}s") from error
            stage.output({"steps": steps})
        service_states = await world.service_states()
        workspace_changes = {
            relative: base64.b64encode(content).decode()
            for relative, content in world.changed_workspace_files().items()
        }
    finally:
        await client.close()
        world.close()
    return CaseResult(
        output={"steps": steps, "changed_workspace_files": sorted(workspace_changes)},
        output_kind="record",
        context={"service_states": service_states, "workspace_changes": workspace_changes},
    )


def _run_rubrics(
    rubrics: list[dict[str, Any]], task_dir: Path, service_states: dict[str, Any], workspace_changes: dict[str, str]
) -> list[dict[str, Any]]:
    with tempfile.TemporaryDirectory(prefix="handbook-score-") as scratch:
        workspace = Path(scratch) / "workspace"
        state_dir = Path(scratch) / "external_services"
        shutil.copytree(task_dir / "environment" / "initial_workspace", workspace)
        state_dir.mkdir()
        for relative, encoded in workspace_changes.items():
            target = workspace / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(base64.b64decode(encoded))
        for filename, state in service_states.items():
            (state_dir / filename).write_text(json.dumps(state))
        outcomes = []
        for rubric in rubrics:
            namespace: dict[str, Any] = {}
            try:
                exec(compile(rubric["verifier_code"], f"<{rubric['id']}>", "exec"), namespace)
                raw = namespace["verify"](str(workspace), str(state_dir))
                passed = bool(raw.get("pass", raw.get("passed", False))) if isinstance(raw, dict) else bool(raw)
                score = float(raw.get("score", 1.0 if passed else 0.0)) if isinstance(raw, dict) else float(passed)
                feedback = str(raw.get("feedback", "")) if isinstance(raw, dict) else ""
            except Exception as error:
                passed, score, feedback = False, 0.0, f"verifier error: {type(error).__name__}: {error}"
            outcomes.append(
                {"rubric": rubric, "passed": passed, "score": max(0.0, min(1.0, score)), "feedback": feedback}
            )
        return outcomes


async def score_case(*, case: Case, result: CaseResult, case_files_dir: Path) -> CaseScore:
    del case_files_dir
    rubrics = case.expected["rubrics"]
    outcomes = await asyncio.to_thread(
        _run_rubrics,
        rubrics,
        _task_dir(case.input),
        result.context["service_states"],
        result.context["workspace_changes"],
    )
    mean_score = sum(outcome["score"] for outcome in outcomes) / len(outcomes)
    all_passed = all(outcome["passed"] for outcome in outcomes)
    return CaseScore(
        objective=mean_score,
        field_scores={"rubric_score": mean_score, "all_rubrics_passed": float(all_passed)},
        checks=tuple(
            Check(
                name=outcome["rubric"]["rubric_text"][:200],
                verdict="pass" if outcome["passed"] else "fail",
                message=outcome["feedback"][:500] or None,
            )
            for outcome in outcomes
        ),
    )


integration = Integration(
    targets=repository(paths=("candidate",)),
    run_setup=TaskSetup,
    run_case=run_case,
    score_case=score_case,
)
