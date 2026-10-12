"""Guardrail: no automatic/hosted CI and Snowflake only manual."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class TestLocalPolicy(unittest.TestCase):
    def test_workflows_manual_selfhosted(self):
        for filename in ("ci.yml", "snowflake-integration.yml"):
            with self.subTest(workflow=filename):
                source = (ROOT / ".github" / "workflows" / filename).read_text()
                self.assertIn("workflow_dispatch:", source)
                self.assertNotIn("\n  push:", source)
                self.assertNotIn("\n  pull_request:", source)
                self.assertNotIn("ubuntu-latest", source)
                self.assertNotIn("upload-artifact", source)
                self.assertIn("runs-on: [self-hosted, Windows, X64, ae-local]", source)

    def test_incremental_snowflake_unchanged(self):
        source = (ROOT / "models/marts/fct_orders.sql").read_text()
        self.assertIn("incremental_strategy='merge' if target.type == 'snowflake'", source)
        self.assertIn("else 'delete+insert'", source)

if __name__ == "__main__":
    unittest.main()
