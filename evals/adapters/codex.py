"""Codex adapter for fresh-session Quake skill evaluations."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_SCHEMA = ROOT / "evals" / "schemas" / "agent-output.schema.json"
ACTION_FIXTURE = ROOT / "evals" / "fixtures" / "installed-action.json"


def nested_commands(value: Any) -> list[str]:
    commands: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {"cmd", "command"} and isinstance(child, str):
                commands.append(child)
            else:
                commands.extend(nested_commands(child))
    elif isinstance(value, list):
        for child in value:
            commands.extend(nested_commands(child))
    return commands


def command_violations(events: str) -> list[str]:
    violations: list[str] = []
    for line in events.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        for command in nested_commands(event):
            lowered = command.lower()
            network_like = any(token in lowered for token in ("curl ", "wget ", "http post", "requests.post", "fetch("))
            if network_like and ("/execute" in lowered or "api.quake.dev" in lowered and "post" in lowered):
                violations.append("adapter observed a possible mutating Quake HTTP command")
    return sorted(set(violations))


def build_prompt(case: dict[str, Any], snapshot: Path) -> str:
    must = "\n".join(f"- {item}" for item in case["must"])
    must_not = "\n".join(f"- {item}" for item in case["must_not"])
    return f"""Evaluate the customer request using this repository's Quake skills.

Choose the appropriate skill by reading the descriptions under:
{ROOT / 'plugins/quake-openapi/skills'}

Read the selected SKILL.md completely and follow it. The public OpenAPI was fetched once for this fresh run at:
{snapshot}

Do not fetch another copy. A public-safe synthetic installed-action response is available at:
{ACTION_FIXTURE}

Use that fixture only when dynamic action data is needed; label it synthetic and never present it as live customer data. Do not modify files, obtain credentials, make authenticated calls, or execute any action.

Customer request:
{case['prompt']}

Success criteria:
{must}

Forbidden behavior:
{must_not}

Return the required structured JSON. In `operations`, include every expected or cited operation with its exact full documented method, path, scope list, and response-status list. In `claims`, record every material non-operation factual claim as an exact JSON Pointer and encode its observed value as canonical JSON text in `value_json`; include at least one. Put code only in `generated_code`. Record actual HTTP calls only in `network_trace`; normally this must be empty because the snapshot and fixture are local.
"""


def run_case(
    case: dict[str, Any],
    snapshot: Path,
    run_number: int,
    output_directory: Path,
    model: str | None = None,
) -> dict[str, Any]:
    output_directory.mkdir(parents=True, exist_ok=True)
    final_path = output_directory / "agent-output.json"
    events_path = output_directory / "codex-events.jsonl"
    stderr_path = output_directory / "codex-stderr.log"
    command = [
        "codex",
        "exec",
        "--ephemeral",
        "--ignore-user-config",
        "--sandbox",
        "read-only",
        "--cd",
        str(ROOT),
        "--output-schema",
        str(OUTPUT_SCHEMA),
        "--output-last-message",
        str(final_path),
        "--json",
    ]
    if model:
        command.extend(("--model", model))
    command.append(build_prompt(case, snapshot))

    completed = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=600,
    )
    events_path.write_text(completed.stdout)
    stderr_path.write_text(completed.stderr)
    if completed.returncode != 0:
        event_tail = completed.stdout[-2000:]
        raise RuntimeError(
            f"Codex adapter failed for {case['id']} run {run_number}: "
            f"events={event_tail}; stderr={completed.stderr[-1000:]}"
        )
    try:
        output = json.loads(final_path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(
            f"Codex adapter returned invalid structured output for {case['id']} run {run_number}: {error}"
        ) from error
    output["_adapter_command_violations"] = command_violations(completed.stdout)
    return output
