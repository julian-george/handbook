"""In-process HANDBOOK world: the mock services run as libraries, one isolated copy per case.

Each mock keeps its state in module globals, so a case's copy is swapped in and out of those
globals under one lock around every tool call. Nothing in docker/packages is modified.
"""

from __future__ import annotations

import asyncio
import copy
import importlib
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fastmcp import Client

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGES_DIR = REPO_ROOT / "docker" / "packages"
TASKS_DIR = REPO_ROOT / "tasks"

MAX_TOOL_RESULT_CHARS = 2000
BASH_TIMEOUT_SECONDS = 60


@dataclass(frozen=True)
class ServiceSpec:
    name: str
    import_root: str
    state_module: str
    server_module: str
    state_globals: tuple[str, ...]
    seed_dirname: str
    verifier_state_filename: str


SERVICES: dict[str, ServiceSpec] = {
    spec.name: spec
    for spec in (
        ServiceSpec(
            "google_mail",
            "google_mail/src",
            "google_mail.state",
            "google_mail.server",
            ("_mailboxes", "_final_path", "_bundle_state_path"),
            "google_mail",
            "inbox.json",
        ),
        ServiceSpec(
            "slack",
            "slack/src",
            "slack_mock.state",
            "slack_mock.server",
            (
                "_workspaces",
                "_active_workspace_id",
                "_current_state",
                "_last_timestamp_us",
                "_final_path",
                "_bundle_state_path",
            ),
            "slack",
            "slack.json",
        ),
        ServiceSpec(
            "jira",
            "jira/src",
            "jira_mock.state",
            "jira_mock.server",
            ("_state_file", "_sites", "_active_site_id", "_current_state", "_bundle_state_path", "_final_path"),
            "jira",
            "jira_state.json",
        ),
        ServiceSpec(
            "google_calendar",
            "google_calendar",
            "google_calendar.state",
            "google_calendar.server",
            ("_AGENT_WORKSPACE_ARG", "_DATA_FILE", "_final_path", "_bundle_state_path", "_active_account_id", "_accounts"),
            "google_calendar",
            "calendar_data.json",
        ),
    )
}

# Serializes every swap of module globals; held across the whole tool call.
_world_lock = asyncio.Lock()
_pristine_globals: dict[str, dict[str, Any]] = {}


def _import_service(spec: ServiceSpec) -> tuple[Any, Any]:
    package_root = str(PACKAGES_DIR / spec.import_root)
    if package_root not in sys.path:
        sys.path.append(package_root)
    state_module = importlib.import_module(spec.state_module)
    if spec.name not in _pristine_globals:
        _pristine_globals[spec.name] = {
            name: copy.deepcopy(getattr(state_module, name)) for name in spec.state_globals
        }
    return state_module, importlib.import_module(spec.server_module)


def _mcp_tool_toolsets(service_name: str) -> dict[str, list[str]]:
    return json.loads((PACKAGES_DIR / service_name / "mcp.json").read_text()).get("toolsets", {})


def _allowed_tool_names(service_name: str, tool_sets: list[str]) -> set[str] | None:
    """Tool names enabled by HANDBOOK_TOOL_SETS entries like ``slack_core``; None means all."""
    toolsets = _mcp_tool_toolsets(service_name)
    if not toolsets:
        return None
    allowed: set[str] = set()
    for tool_set in tool_sets:
        prefix = f"{service_name}_"
        if tool_set.startswith(prefix):
            allowed.update(toolsets.get(tool_set.removeprefix(prefix), []))
    return allowed


def _clip(text: str) -> str:
    if len(text) <= MAX_TOOL_RESULT_CHARS:
        return text
    return text[:MAX_TOOL_RESULT_CHARS] + f"\n...[truncated {len(text) - MAX_TOOL_RESULT_CHARS} chars]"


class World:
    """One case's mock services plus its private /workdir."""

    def __init__(self, task_dir: Path, case_dir: Path, tool_sets: list[str], current_time: str) -> None:
        self.task_dir = task_dir
        self.case_dir = case_dir
        self.workdir = case_dir / "workdir"
        self.tool_sets = tool_sets
        self.current_time = current_time
        self._service_globals: dict[str, dict[str, Any]] = {}
        self._modules: dict[str, tuple[Any, Any]] = {}
        self._tool_specs: dict[str, dict[str, Any]] = {}
        self._tool_routes: dict[str, tuple[str, str]] = {}

    @classmethod
    async def create(cls, task_dir: Path, case_dir: Path, tool_sets: list[str], current_time: str) -> World:
        world = cls(task_dir, case_dir, tool_sets, current_time)
        shutil.copytree(task_dir / "environment" / "initial_workspace", world.workdir)
        async with _world_lock:
            for spec in SERVICES.values():
                world._init_service(spec)
        for spec in SERVICES.values():
            await world._register_tools(spec)
        world._register_workspace_tools()
        return world

    def _init_service(self, spec: ServiceSpec) -> None:
        state_module, server_module = _import_service(spec)
        self._modules[spec.name] = (state_module, server_module)
        seed_dir = self.task_dir / "environment" / "initial_external_services" / spec.seed_dirname
        input_dir = self.case_dir / "initial_data" / spec.seed_dirname
        output_dir = self.case_dir / "data" / spec.name
        if seed_dir.is_dir():
            shutil.copytree(seed_dir, input_dir)
        else:
            input_dir.mkdir(parents=True)
        output_dir.mkdir(parents=True)
        for name, pristine in _pristine_globals[spec.name].items():
            setattr(state_module, name, copy.deepcopy(pristine))
        previous_env = {key: os.environ.get(key) for key in ("INPUTDIR", "OUTPUTDIR", "BUNDLEDIR", "BUNDLE_OUTPUT_DIR")}
        os.environ["INPUTDIR"] = str(input_dir)
        os.environ["OUTPUTDIR"] = str(output_dir)
        os.environ.pop("BUNDLEDIR", None)
        os.environ.pop("BUNDLE_OUTPUT_DIR", None)
        try:
            state_module.init_state()
        finally:
            for key, value in previous_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
        self._capture(spec)

    def _install(self, spec: ServiceSpec) -> None:
        state_module = self._modules[spec.name][0]
        for name, value in self._service_globals[spec.name].items():
            setattr(state_module, name, value)

    def _capture(self, spec: ServiceSpec) -> None:
        state_module = self._modules[spec.name][0]
        self._service_globals[spec.name] = {name: getattr(state_module, name) for name in spec.state_globals}

    async def _register_tools(self, spec: ServiceSpec) -> None:
        server_module = self._modules[spec.name][1]
        allowed = _allowed_tool_names(spec.name, self.tool_sets)
        async with Client(server_module.mcp) as client:
            for tool in await client.list_tools():
                if allowed is not None and tool.name not in allowed:
                    continue
                exposed_name = f"{spec.name}__{tool.name}"
                self._tool_routes[exposed_name] = (spec.name, tool.name)
                self._tool_specs[exposed_name] = {
                    "name": exposed_name,
                    "description": tool.description or "",
                    "parameters": tool.inputSchema,
                }

    def _register_workspace_tools(self) -> None:
        string_arg = {"type": "string"}
        for name, description, properties, required in (
            ("bash", "Run a bash command in /workdir.", {"command": string_arg}, ["command"]),
            ("listFiles", "List files and directories in a directory under /workdir.", {"directory": string_arg}, []),
            ("readFile", "Read a text file under /workdir.", {"file_path": string_arg}, ["file_path"]),
            ("readPDF", "Extract the text of a PDF under /workdir.", {"file_path": string_arg}, ["file_path"]),
            (
                "writeFile",
                "Write content to a file under /workdir.",
                {"file_path": string_arg, "content": string_arg},
                ["file_path", "content"],
            ),
        ):
            self._tool_specs[name] = {
                "name": name,
                "description": description,
                "parameters": {"type": "object", "properties": properties, "required": required},
            }

    @property
    def tool_specs(self) -> list[dict[str, Any]]:
        return list(self._tool_specs.values())

    def _resolve(self, path: str) -> Path:
        relative = path.removeprefix("/workdir").lstrip("/")
        resolved = (self.workdir / relative).resolve()
        if not resolved.is_relative_to(self.workdir.resolve()):
            raise ValueError(f"path {path!r} is outside /workdir")
        return resolved

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> str:
        """Run one tool and return its text result; tool errors come back as text for the agent."""
        if tool_name not in self._tool_specs:
            return f"Error: unknown tool {tool_name!r}"
        try:
            if tool_name in self._tool_routes:
                return _clip(await self._call_service_tool(tool_name, arguments))
            return _clip(await self._call_workspace_tool(tool_name, arguments))
        except Exception as error:
            return f"Error: {type(error).__name__}: {error}"

    async def _call_service_tool(self, exposed_name: str, arguments: dict[str, Any]) -> str:
        service_name, tool_name = self._tool_routes[exposed_name]
        spec = SERVICES[service_name]
        async with _world_lock:
            self._install(spec)
            try:
                async with Client(self._modules[service_name][1].mcp) as client:
                    result = await client.call_tool(tool_name, arguments, raise_on_error=False)
            finally:
                self._capture(spec)
        text = "\n".join(part.text for part in result.content if hasattr(part, "text"))
        return f"Error: {text}" if result.is_error else text

    async def _call_workspace_tool(self, tool_name: str, arguments: dict[str, Any]) -> str:
        if tool_name == "bash":
            command = arguments["command"].replace("/workdir", str(self.workdir))
            env = {**os.environ, "HANDBOOK_CURRENT_TIME": self.current_time}
            completed = await asyncio.to_thread(
                subprocess.run,
                ["bash", "-c", command],
                cwd=self.workdir,
                env=env,
                capture_output=True,
                text=True,
                timeout=BASH_TIMEOUT_SECONDS,
            )
            return json.dumps({"stdout": completed.stdout, "stderr": completed.stderr, "returncode": completed.returncode})
        if tool_name == "listFiles":
            directory = self._resolve(arguments.get("directory", "."))
            entries = sorted(directory.iterdir())
            return json.dumps(
                {
                    "files": [entry.name for entry in entries if entry.is_file()],
                    "directories": [entry.name for entry in entries if entry.is_dir()],
                }
            )
        if tool_name == "readFile":
            return self._resolve(arguments["file_path"]).read_text(errors="replace")
        if tool_name == "readPDF":
            import pdfplumber

            with pdfplumber.open(self._resolve(arguments["file_path"])) as pdf:
                return json.dumps({"pages": [page.extract_text() or "" for page in pdf.pages]})
        if tool_name == "writeFile":
            target = self._resolve(arguments["file_path"])
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(arguments["content"])
            return json.dumps({"file_path": arguments["file_path"], "returncode": 0})
        raise ValueError(f"unhandled workspace tool {tool_name!r}")

    async def service_states(self) -> dict[str, Any]:
        """Final JSON state of every service, keyed by the filename the verifiers expect."""
        states: dict[str, Any] = {}
        async with _world_lock:
            for spec in SERVICES.values():
                self._install(spec)
                states[spec.verifier_state_filename] = self._modules[spec.name][0].state_to_json()
        return states

    def changed_workspace_files(self) -> dict[str, bytes]:
        """Workspace files that are new or differ from the task's initial workspace."""
        initial_dir = self.task_dir / "environment" / "initial_workspace"
        changed: dict[str, bytes] = {}
        for path in sorted(self.workdir.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(self.workdir)
            initial_path = initial_dir / relative
            content = path.read_bytes()
            if not initial_path.is_file() or initial_path.read_bytes() != content:
                changed[str(relative)] = content
        return changed
