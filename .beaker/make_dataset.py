"""Write the HANDBOOK tasks as a Beaker dataset JSONL: one row per task, rubrics as the labels."""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = REPO_ROOT / ".beaker" / "handbook_tasks.jsonl"

with OUTPUT_PATH.open("w") as output_file:
    for task_dir in sorted((REPO_ROOT / "tasks").iterdir()):
        rubrics = json.loads((task_dir / "tests" / "rubrics.json").read_text())
        row = {
            "id": task_dir.name,
            "input": {"task_name": task_dir.name},
            "expected": {
                "rubrics": [
                    {"id": r["id"], "rubric_text": r["rubric_text"], "verifier_code": r["verifier_code"]}
                    for r in rubrics
                ]
            },
        }
        output_file.write(json.dumps(row) + "\n")
print(f"wrote {OUTPUT_PATH}")
