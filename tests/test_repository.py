from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "quake-openapi"
SKILLS = (
    "quake-openapi-navigate",
    "quake-openapi-auth",
    "quake-installed-app-actions",
)


class RepositoryTests(unittest.TestCase):
    def test_marketplace_points_to_plugin(self) -> None:
        marketplace = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text())
        self.assertEqual(marketplace["name"], "quake")
        entry = marketplace["plugins"][0]
        self.assertEqual(entry["name"], "quake-openapi")
        self.assertEqual(entry["source"]["path"], "./plugins/quake-openapi")

    def test_plugin_declares_skills_only_package(self) -> None:
        manifest = json.loads((PLUGIN / ".codex-plugin/plugin.json").read_text())
        self.assertEqual(manifest["version"], "0.1.0")
        self.assertEqual(manifest["skills"], "./skills/")
        for forbidden in ("mcpServers", "apps", "hooks"):
            self.assertNotIn(forbidden, manifest)

    def test_skill_names_match_directories_and_prompts(self) -> None:
        for name in SKILLS:
            skill_dir = PLUGIN / "skills" / name
            skill_text = (skill_dir / "SKILL.md").read_text()
            name_match = re.search(r"^name: (.+)$", skill_text, re.MULTILINE)
            self.assertIsNotNone(name_match, name)
            self.assertEqual(name_match.group(1), name)
            self.assertIn("license: Apache-2.0", skill_text)
            self.assertIn(
                "compatibility: Requires Python 3 and outbound HTTPS access to api.quake.dev.",
                skill_text,
            )

            metadata = (skill_dir / "agents/openai.yaml").read_text()
            self.assertIn(f"${name}", metadata)
            description_match = re.search(r'^  short_description: "(.+)"$', metadata, re.MULTILINE)
            self.assertIsNotNone(description_match, name)
            self.assertGreaterEqual(len(description_match.group(1)), 25)
            self.assertLessEqual(len(description_match.group(1)), 64)

    def test_evaluation_inventory_is_complete_and_unique(self) -> None:
        inventory = json.loads((ROOT / "evals/cases/v0.1.json").read_text())
        cases = inventory["cases"]
        identifiers = [case["id"] for case in cases]
        self.assertGreaterEqual(len(cases), 16)
        self.assertEqual(len(identifiers), len(set(identifiers)))
        for case in cases:
            self.assertIn(case["skill"], SKILLS)
            self.assertTrue(case["must"])
            self.assertTrue(case["must_not"])

    def test_customer_install_and_support_routes_are_documented(self) -> None:
        readme = (ROOT / "README.md").read_text()
        self.assertIn("--ref main", readme)
        self.assertIn("--ref stable", readme)
        self.assertIn("do not use it before then", readme)
        self.assertIn("codex plugin list --json", readme)
        self.assertIn("codex plugin marketplace upgrade quake", readme)
        self.assertIn("<RELEASE_TAG>", readme)
        self.assertIn("https://github.com/QuakeAI/skills/issues", readme)
        self.assertIn("https://quake.dev/contact", readme)

    def test_customer_files_contain_no_obvious_secret_values(self) -> None:
        suspicious = re.compile(
            r"(?:sk-[A-Za-z0-9]{16,}|ghp_[A-Za-z0-9]{20,}|Bearer\s+[A-Za-z0-9._~-]{20,})"
        )
        for path in ROOT.rglob("*"):
            if not path.is_file() or ".git" in path.parts or path.suffix not in {".md", ".json", ".yaml", ".py"}:
                continue
            self.assertIsNone(suspicious.search(path.read_text(errors="ignore")), str(path))


if __name__ == "__main__":
    unittest.main()
