#!/usr/bin/env python3
"""Run repeatable, deterministic gates over the Quake skill golden cases."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EVALS = Path(__file__).resolve().parent
ROOT = EVALS.parent
sys.path.insert(0, str(EVALS))

from adapters.codex import run_case  # noqa: E402
from assertions import evaluate_run, passed, validate_expected_operations  # noqa: E402


SPEC_URL = "https://api.quake.dev/openapi.json"
CASES_FILE = EVALS / "cases" / "v0.1.json"
ACTION_FIXTURE = EVALS / "fixtures" / "installed-action.json"


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return parsed


def load_cases(selected: list[str]) -> list[dict[str, Any]]:
    inventory = json.loads(CASES_FILE.read_text())
    cases = inventory["cases"]
    if not selected:
        return cases
    wanted = set(selected)
    matches = [case for case in cases if case["id"] in wanted]
    missing = wanted - {case["id"] for case in matches}
    if missing:
        raise ValueError(f"Unknown case(s): {', '.join(sorted(missing))}")
    return matches


def prepare_spec(location: str | None, output_directory: Path) -> tuple[dict[str, Any], dict[str, Any], Path]:
    if location:
        snapshot = Path(location).resolve()
        raw = snapshot.read_bytes()
        source_kind = "file"
    else:
        request = urllib.request.Request(
            SPEC_URL,
            headers={"Accept": "application/json", "User-Agent": "quake-skill-eval/0.1"},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read()
        snapshot = output_directory / "openapi.json"
        snapshot.write_bytes(raw)
        source_kind = "url"
    spec = json.loads(raw)
    if not isinstance(spec, dict) or not str(spec.get("openapi", "")).startswith("3."):
        raise ValueError("Expected an OpenAPI 3.x document")
    identity = {
        "kind": source_kind,
        "location": location or SPEC_URL,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "openapi": spec.get("openapi"),
        "api_version": spec.get("info", {}).get("version"),
    }
    return spec, identity, snapshot


def write_junit(report: dict[str, Any], path: Path) -> None:
    records = [record for case in report["cases"] for record in case["runs"]]
    failures = sum(1 for record in records if not record["passed"])
    suite = ET.Element(
        "testsuite",
        name="quake-skill-evals",
        tests=str(len(records)),
        failures=str(failures),
    )
    for record in records:
        test = ET.SubElement(
            suite,
            "testcase",
            classname=record["case_id"],
            name=f"run-{record['run']}",
        )
        if not record["passed"]:
            failed = [item for item in record["assertions"] if not item["passed"]]
            failure = ET.SubElement(test, "failure", message="; ".join(item["name"] for item in failed))
            failure.text = json.dumps(failed, indent=2, sort_keys=True)
    ET.ElementTree(suite).write(path, encoding="utf-8", xml_declaration=True)


def write_summary(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Quake skill evaluation",
        "",
        f"- Result: {'PASS' if report['passed'] else 'FAIL'}",
        f"- OpenAPI SHA-256: `{report['spec']['sha256']}`",
        f"- Runs per case: {report['runs_per_case']}",
        f"- Activation and operation-selection rate: {report['summary']['activation_operation_rate']:.1%}",
        "",
        "| Case | Passing runs | Required | Result |",
        "| --- | ---: | ---: | --- |",
    ]
    for case in report["cases"]:
        lines.append(
            f"| `{case['case_id']}` | {case['passing_runs']} | {case['required_passes']} | "
            f"{'PASS' if case['passed'] else 'FAIL'} |"
        )
    lines.extend(
        (
            "",
            "Semantic `must` and `must_not` criteria remain visible in the JSON report for human or advisory-model review. They cannot override a failed deterministic gate.",
        )
    )
    path.write_text("\n".join(lines) + "\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", action="append", default=[], help="case ID; repeatable")
    parser.add_argument("--runs", type=positive_int, default=3, help="fresh runs per case")
    parser.add_argument("--spec", help="saved OpenAPI snapshot; omit to fetch once")
    parser.add_argument("--model", help="optional Codex model override")
    parser.add_argument("--output", help="artifact directory under .artifacts by default")
    parser.add_argument(
        "--preflight-only",
        action="store_true",
        help="fetch and validate case expectations without starting agent runs",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_directory = Path(args.output).resolve() if args.output else ROOT / ".artifacts" / "evals" / timestamp
    output_directory.mkdir(parents=True, exist_ok=True)

    try:
        cases = load_cases(args.case)
        spec, identity, snapshot = prepare_spec(args.spec, output_directory)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"preflight failed: {error}", file=sys.stderr)
        return 2

    preflight_errors = validate_expected_operations(cases, spec)
    if preflight_errors:
        for error in preflight_errors:
            print(error, file=sys.stderr)
        return 2
    print(f"preflight ok: {len(cases)} case(s), OpenAPI {identity['sha256']}")
    if args.preflight_only:
        return 0

    action_fixture = json.loads(ACTION_FIXTURE.read_text())
    required_passes = args.runs // 2 + 1
    case_reports: list[dict[str, Any]] = []
    activation_operation_total = 0
    activation_operation_passed = 0

    for case in cases:
        records = []
        for run_number in range(1, args.runs + 1):
            run_directory = output_directory / case["id"] / f"run-{run_number}"
            run_directory.mkdir(parents=True, exist_ok=True)
            output_file = run_directory / "agent-output.json"
            try:
                output = run_case(case, snapshot, run_number, run_directory, args.model)
                checks = evaluate_run(case, output, spec, action_fixture)
            except (OSError, RuntimeError, json.JSONDecodeError) as error:
                checks = [
                    {
                        "name": "adapter",
                        "passed": False,
                        "expected": "successful fresh Codex run",
                        "observed": str(error),
                        "message": "The host adapter failed before deterministic grading.",
                    }
                ]
            for check in checks:
                if check["name"] in {"activation", "operation_selection"}:
                    activation_operation_total += 1
                    activation_operation_passed += int(check["passed"])
            records.append(
                {
                    "case_id": case["id"],
                    "run": run_number,
                    "passed": passed(checks),
                    "assertions": checks,
                    "output_file": str(output_file.relative_to(output_directory)),
                }
            )
            print(f"{case['id']} run {run_number}: {'PASS' if records[-1]['passed'] else 'FAIL'}")
        passing_runs = sum(1 for record in records if record["passed"])
        case_reports.append(
            {
                "case_id": case["id"],
                "passing_runs": passing_runs,
                "required_passes": required_passes,
                "passed": passing_runs >= required_passes,
                "advisory_criteria": {"must": case["must"], "must_not": case["must_not"]},
                "runs": records,
            }
        )

    rate = activation_operation_passed / activation_operation_total if activation_operation_total else 0.0
    report: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "spec": identity,
        "runs_per_case": args.runs,
        "cases": case_reports,
        "summary": {
            "case_count": len(case_reports),
            "passing_case_count": sum(1 for case in case_reports if case["passed"]),
            "activation_operation_rate": rate,
        },
        "passed": all(case["passed"] for case in case_reports) and rate >= 0.9,
    }
    (output_directory / "eval-report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    write_junit(report, output_directory / "junit.xml")
    write_summary(report, output_directory / "summary.md")
    print(f"report: {output_directory}")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
