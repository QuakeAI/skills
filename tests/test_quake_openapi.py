from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "tooling" / "quake_openapi.py"
SPEC = ROOT / "tests" / "fixtures" / "openapi.json"
ACTION = ROOT / "tests" / "fixtures" / "installed-action.json"


def run_helper(*arguments: str) -> tuple[int, dict]:
    completed = subprocess.run(
        [sys.executable, str(HELPER), *arguments],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if not completed.stdout:
        raise AssertionError(f"helper produced no JSON; stderr={completed.stderr!r}")
    return completed.returncode, json.loads(completed.stdout)


class QuakeOpenApiHelperTests(unittest.TestCase):
    def test_find_ranks_operation(self) -> None:
        code, output = run_helper("--spec", str(SPEC), "find", "get item", "--kind", "operation")
        self.assertEqual(code, 0)
        self.assertTrue(output["ok"])
        self.assertEqual(output["result"]["matches"][0]["operation_id"], "getItem")

    def test_find_reports_no_match(self) -> None:
        code, output = run_helper("--spec", str(SPEC), "find", "unrelated-absent-term")
        self.assertEqual(code, 4)
        self.assertFalse(output["ok"])
        self.assertEqual(output["diagnostics"][0]["code"], "NO_SPEC_MATCH")

    def test_show_operation_merges_parameters_with_operation_override(self) -> None:
        code, output = run_helper(
            "--spec", str(SPEC), "show", "operation", "--method", "GET", "--path", "/items/{itemId}"
        )
        self.assertEqual(code, 0)
        parameters = output["result"]["parameters"]
        self.assertEqual(len(parameters), 1)
        self.assertEqual(parameters[0]["schema"]["format"], "uuid")
        self.assertEqual(output["result"]["security_source"], "operation")
        self.assertEqual(output["result"]["servers_source"], "document")
        self.assertEqual(output["result"]["servers"][0]["url"], "https://api.example.invalid")

    def test_show_operation_flags_undefined_security_scheme(self) -> None:
        code, output = run_helper("--spec", str(SPEC), "show", "operation", "--id", "executeAction")
        self.assertEqual(code, 0)
        self.assertIn("SECURITY_SCHEME_UNDEFINED", {item["code"] for item in output["diagnostics"]})

    def test_show_schema_resolves_nested_fields(self) -> None:
        code, output = run_helper("--spec", str(SPEC), "show", "schema", "--name", "Item")
        self.assertEqual(code, 0)
        fields = {item["name"]: item for item in output["result"]["fields"]}
        self.assertTrue(fields["id"]["required"])
        self.assertTrue(fields["details"]["required"])
        self.assertTrue(fields["details.label"]["nullable"])
        self.assertEqual(fields["details.label"]["maxLength"], 100)

    def test_show_security_lists_documented_schemes(self) -> None:
        code, output = run_helper("--spec", str(SPEC), "show", "security")
        self.assertEqual(code, 0)
        self.assertIn("DemoOAuth", output["result"]["security_schemes"])

    def test_verify_operation_passes_supported_claims(self) -> None:
        code, output = run_helper(
            "--spec",
            str(SPEC),
            "verify",
            "operation",
            "--id",
            "getItem",
            "--method",
            "GET",
            "--path",
            "/items/{itemId}",
            "--scope",
            "items:read",
            "--response",
            "200",
        )
        self.assertEqual(code, 0)
        self.assertTrue(output["result"]["verified"])

    def test_verify_operation_rejects_unsupported_claims(self) -> None:
        code, output = run_helper(
            "--spec", str(SPEC), "verify", "operation", "--id", "getItem", "--scope", "items:write"
        )
        self.assertEqual(code, 6)
        self.assertFalse(output["result"]["verified"])

    def test_verify_value_checks_exact_and_contained_schema_claims(self) -> None:
        code, output = run_helper(
            "--spec",
            str(SPEC),
            "verify",
            "value",
            "--pointer",
            "#/components/schemas/Item/required",
            "--contains",
            '"details"',
        )
        self.assertEqual(code, 0)
        self.assertTrue(output["result"]["verified"])

        code, output = run_helper(
            "verify",
            "value",
            "--input",
            str(ACTION),
            "--pointer",
            "#/input_schema/1/arrayFormat",
            "--equals",
            '"repeat"',
        )
        self.assertEqual(code, 0)
        self.assertEqual(output["result"]["actual"], "repeat")

    def test_verify_value_rejects_wrong_field_claim(self) -> None:
        code, output = run_helper(
            "--spec",
            str(SPEC),
            "verify",
            "value",
            "--pointer",
            "#/components/schemas/Item/properties/id/type",
            "--equals",
            '"integer"',
        )
        self.assertEqual(code, 6)
        self.assertFalse(output["result"]["verified"])

    def test_describe_action_preserves_field_semantics_and_warns_on_text(self) -> None:
        code, output = run_helper("describe-action", "--input", str(ACTION))
        self.assertEqual(code, 0)
        groups = {item["location"]: item for item in output["result"]["input_groups"]}
        path_fields = {item["name"]: item for item in groups["path"]["fields"]}
        query_fields = {item["name"]: item for item in groups["query"]["fields"]}
        self.assertTrue(path_fields["recordId"]["required"])
        self.assertEqual(path_fields["recordId"]["minLength"], 1)
        self.assertEqual(
            path_fields["documents[].base64"]["conditionally_required_in"], ["oneOf[0]"]
        )
        self.assertEqual(
            path_fields["documents[].url"]["conditionally_required_in"], ["oneOf[1]"]
        )
        self.assertTrue(query_fields["locale"]["nullable"])
        self.assertTrue(query_fields["legacyNullable"]["nullable"])
        self.assertEqual(query_fields["locale"]["default"], "en")
        self.assertEqual(query_fields["include"]["items"]["type"], "string")
        self.assertEqual(query_fields["include"]["items"]["enum"], ["summary", "history"])
        self.assertEqual(groups["query"]["array_format"], "repeat")
        self.assertEqual(output["result"]["output_summary"]["type"], "array")
        self.assertIn("[].record", {item["name"] for item in output["result"]["output_fields"]})
        self.assertEqual(output["result"]["untrusted_app_text_fields"], ["app_ai_instructions"])
        self.assertIn("APP_TEXT_UNTRUSTED", {item["code"] for item in output["diagnostics"]})

    def test_describe_action_rejects_missing_schema_fields(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(HELPER), "describe-action", "--input", "-"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            input='{"id":"incomplete"}',
        )
        output = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 5)
        self.assertEqual(output["diagnostics"][0]["code"], "ACTION_INVALID")

    def test_every_skill_bundles_the_canonical_helper(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "sync_skill_helpers.py"), "--check"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr + completed.stdout)


if __name__ == "__main__":
    unittest.main()
