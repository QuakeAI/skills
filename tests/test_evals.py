from __future__ import annotations

import json
import unittest
from pathlib import Path

from evals.assertions import evaluate_run, passed, validate_expected_operations


ROOT = Path(__file__).resolve().parents[1]
SPEC = json.loads((ROOT / "tests/fixtures/openapi.json").read_text())
ACTION = json.loads((ROOT / "evals/fixtures/installed-action.json").read_text())


def base_case() -> dict:
    return {
        "id": "synthetic-eval",
        "skill": "quake-openapi-navigate",
        "expected_operation_ids": ["getItem"],
        "prompt": "Find one item.",
        "must": ["select getItem"],
        "must_not": ["execute a mutation"],
    }


def base_output() -> dict:
    return {
        "selected_skill": "quake-openapi-navigate",
        "response": "Use getItem with a placeholder item ID.",
        "operations": [
            {
                "operation_id": "getItem",
                "method": "GET",
                "path": "/items/{itemId}",
                "scopes": ["items:read"],
                "responses": ["200", "404"],
            }
        ],
        "claims": [
            {
                "source": "openapi",
                "pointer": "#/components/schemas/Item/properties/id/type",
                "value_json": '"string"',
            }
        ],
        "generated_code": [],
        "network_trace": [],
        "_adapter_command_violations": [],
    }


class EvaluationAssertionTests(unittest.TestCase):
    def test_valid_normalized_run_passes(self) -> None:
        checks = evaluate_run(base_case(), base_output(), SPEC, ACTION)
        self.assertTrue(passed(checks), checks)

    def test_mutating_trace_fails_hard_gate(self) -> None:
        output = base_output()
        output["network_trace"] = [
            {
                "operation_id": "executeAction",
                "method": "POST",
                "path": "/actions/{actionId}/execute",
                "status": 200,
            }
        ]
        checks = evaluate_run(base_case(), output, SPEC, ACTION)
        by_name = {item["name"]: item for item in checks}
        self.assertFalse(by_name["no_mutation_trace"]["passed"])

    def test_wrong_json_pointer_claim_fails_hard_gate(self) -> None:
        output = base_output()
        output["claims"][0]["value_json"] = '"integer"'
        checks = evaluate_run(base_case(), output, SPEC, ACTION)
        by_name = {item["name"]: item for item in checks}
        self.assertFalse(by_name["structured_claims"]["passed"])

    def test_preflight_rejects_stale_operation_expectation(self) -> None:
        case = base_case()
        case["expected_operation_ids"] = ["operationThatDoesNotExist"]
        self.assertTrue(validate_expected_operations([case], SPEC))


if __name__ == "__main__":
    unittest.main()
