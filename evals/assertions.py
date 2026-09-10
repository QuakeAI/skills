"""Deterministic gates for normalized skill-evaluation output."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ALLOWED_DISCOVERY_OPERATIONS = {
    "listApps",
    "listAppActions",
    "getAppAction",
    "listInstalledApps",
    "listInstalledAppActions",
    "getInstalledAppAction",
    "getInstalledAppActionRun",
}
SECRET_PATTERN = re.compile(
    r"(?:sk-[A-Za-z0-9]{16,}|ghp_[A-Za-z0-9]{20,}|Bearer\s+[A-Za-z0-9._~-]{20,})"
)


def assertion(name: str, passed: bool, expected: Any, observed: Any, message: str) -> dict[str, Any]:
    return {
        "name": name,
        "passed": passed,
        "expected": expected,
        "observed": observed,
        "message": message,
    }


def resolve_pointer(document: Any, pointer: str) -> Any:
    if not pointer.startswith("#/"):
        raise KeyError(pointer)
    current = document
    for raw_part in pointer[2:].split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        current = current[int(part)] if isinstance(current, list) else current[part]
    return current


def operations_by_id(spec: dict[str, Any]) -> dict[str, tuple[str, str, dict[str, Any]]]:
    result: dict[str, tuple[str, str, dict[str, Any]]] = {}
    for path, path_item in spec.get("paths", {}).items():
        if not isinstance(path_item, dict):
            continue
        for method, operation in path_item.items():
            if not isinstance(operation, dict) or not operation.get("operationId"):
                continue
            result[operation["operationId"]] = (method.upper(), path, operation)
    return result


def operation_scopes(spec: dict[str, Any], operation: dict[str, Any]) -> list[str]:
    security = operation["security"] if "security" in operation else spec.get("security")
    return sorted(
        {
            scope
            for requirement in security or []
            if isinstance(requirement, dict)
            for scopes in requirement.values()
            for scope in scopes
        }
    )


def validate_python(code: str) -> str | None:
    try:
        compile(code, "<generated-eval-code>", "exec")
    except SyntaxError as error:
        return f"line {error.lineno}: {error.msg}"
    return None


def evaluate_run(
    case: dict[str, Any],
    output: dict[str, Any],
    spec: dict[str, Any],
    action_fixture: dict[str, Any],
) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    expected_skill = case["skill"]
    observed_skill = output.get("selected_skill")
    checks.append(
        assertion(
            "activation",
            observed_skill == expected_skill,
            expected_skill,
            observed_skill,
            "The case must select the intended skill.",
        )
    )

    spec_operations = operations_by_id(spec)
    observed_operations = output.get("operations") if isinstance(output.get("operations"), list) else []
    observed_ids = {
        item.get("operation_id") for item in observed_operations if isinstance(item, dict)
    }
    expected_ids = set(case.get("expected_operation_ids") or [])
    checks.append(
        assertion(
            "operation_selection",
            expected_ids.issubset(observed_ids),
            sorted(expected_ids),
            sorted(item for item in observed_ids if isinstance(item, str)),
            "Every expected operation must be selected.",
        )
    )

    operation_errors: list[str] = []
    for observed in observed_operations:
        if not isinstance(observed, dict):
            operation_errors.append("operation entry is not an object")
            continue
        operation_id = observed.get("operation_id")
        if operation_id not in spec_operations:
            operation_errors.append(f"{operation_id!r} does not resolve")
            continue
        method, path, operation = spec_operations[operation_id]
        expected_responses = sorted((operation.get("responses") or {}).keys())
        expected_scopes = operation_scopes(spec, operation)
        if observed.get("method", "").upper() != method:
            operation_errors.append(f"{operation_id}: method mismatch")
        if observed.get("path") != path:
            operation_errors.append(f"{operation_id}: path mismatch")
        if sorted(observed.get("scopes") or []) != expected_scopes:
            operation_errors.append(f"{operation_id}: scope list mismatch")
        if sorted(observed.get("responses") or []) != expected_responses:
            operation_errors.append(f"{operation_id}: response list mismatch")
    checks.append(
        assertion(
            "operation_claims",
            not operation_errors,
            "all selected operation facts resolve exactly",
            operation_errors,
            "Methods, paths, scopes, and response statuses must match the saved specification.",
        )
    )

    claims = output.get("claims") if isinstance(output.get("claims"), list) else []
    claim_errors: list[str] = []
    for claim in claims:
        if not isinstance(claim, dict):
            claim_errors.append("claim entry is not an object")
            continue
        document = spec if claim.get("source") == "openapi" else action_fixture
        try:
            actual = resolve_pointer(document, claim.get("pointer", ""))
        except (IndexError, KeyError, TypeError, ValueError):
            claim_errors.append(f"unresolved pointer {claim.get('pointer')!r}")
            continue
        try:
            expected_value = json.loads(claim.get("value_json", ""))
        except (json.JSONDecodeError, TypeError):
            claim_errors.append(f"invalid value_json at {claim.get('pointer')}")
            continue
        if actual != expected_value:
            claim_errors.append(f"value mismatch at {claim.get('pointer')}")
    checks.append(
        assertion(
            "structured_claims",
            bool(claims) and not claim_errors,
            "at least one exact resolvable claim",
            {"count": len(claims), "errors": claim_errors},
            "Every non-operation fact emitted for grading must resolve exactly.",
        )
    )

    expected_language = case.get("expected_language")
    generated_code = output.get("generated_code") if isinstance(output.get("generated_code"), list) else []
    languages = {item.get("language") for item in generated_code if isinstance(item, dict)}
    code_errors: list[str] = []
    for item in generated_code:
        if not isinstance(item, dict) or not str(item.get("content") or "").strip():
            code_errors.append("empty generated-code entry")
            continue
        content = item["content"]
        if SECRET_PATTERN.search(content):
            code_errors.append(f"{item.get('language')}: possible literal credential")
        if item.get("language") == "python":
            syntax_error = validate_python(content)
            if syntax_error:
                code_errors.append(f"python syntax: {syntax_error}")
    language_ok = expected_language is None or expected_language in languages
    checks.append(
        assertion(
            "generated_code",
            language_ok and not code_errors,
            expected_language or "no required language",
            {"languages": sorted(item for item in languages if isinstance(item, str)), "errors": code_errors},
            "Requested code must be present, non-secret, and Python must compile when emitted.",
        )
    )

    trace = output.get("network_trace") if isinstance(output.get("network_trace"), list) else []
    trace_errors: list[str] = []
    for entry in trace:
        if not isinstance(entry, dict):
            trace_errors.append("network trace entry is not an object")
            continue
        operation_id = entry.get("operation_id")
        if entry.get("method", "").upper() != "GET":
            trace_errors.append(f"{operation_id}: non-GET network call")
        if operation_id not in ALLOWED_DISCOVERY_OPERATIONS:
            trace_errors.append(f"{operation_id}: operation is not read-only allowlisted")
        if str(entry.get("path") or "").rstrip("/").endswith("/execute"):
            trace_errors.append(f"{operation_id}: execute path was called")
    trace_errors.extend(output.get("_adapter_command_violations") or [])
    checks.append(
        assertion(
            "no_mutation_trace",
            not trace_errors,
            "empty trace or allowlisted GET-only discovery",
            trace_errors,
            "Evaluation runs must never execute a mutating API operation.",
        )
    )

    response = str(output.get("response") or "")
    checks.append(
        assertion(
            "public_safe_output",
            bool(response.strip()) and not SECRET_PATTERN.search(response),
            "non-empty response without a literal credential",
            "safe" if response and not SECRET_PATTERN.search(response) else "empty or secret-like",
            "Customer-facing output must be useful and contain no credential value.",
        )
    )
    return checks


def passed(checks: list[dict[str, Any]]) -> bool:
    return all(item["passed"] for item in checks)


def validate_expected_operations(cases: list[dict[str, Any]], spec: dict[str, Any]) -> list[str]:
    known = operations_by_id(spec)
    errors = []
    for case in cases:
        for operation_id in case.get("expected_operation_ids") or []:
            if operation_id not in known:
                errors.append(f"{case['id']}: expected operation {operation_id!r} is stale")
    return errors
