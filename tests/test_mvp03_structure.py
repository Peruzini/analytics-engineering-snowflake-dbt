"""Offline guardrails for the MVP-03 SQL contracts and manual integration."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SINGULAR_TESTS = {
    "assert_order_revenue_status.sql",
    "assert_daily_sales_reconciles.sql",
    "assert_order_items_reconcile.sql",
    "assert_customer_ltv_reconciles.sql",
    "assert_channel_revenue_reconciles.sql",
}


class TestMVP03Structure(unittest.TestCase):
    def test_incremental_merge_and_no_date_watermark(self):
        code = (ROOT / "models/marts/fct_orders.sql").read_text(encoding="utf-8")
        for token in ("materialized='incremental'", "unique_key='order_id'",
                      "incremental_strategy='merge'", "is_incremental()",
                      "is not distinct from", "{{ this }}"):
            with self.subTest(token=token):
                self.assertIn(token, code)
        self.assertNotIn("dateadd(", code.lower())

    def test_snapshot_tracks_mutable_fields(self):
        snapshot = (ROOT / "snapshots/customers.yml").read_text(encoding="utf-8")
        for token in ("snap_customers", "strategy: check", "unique_key: customer_id",
                      "check_cols: [email, region]", "hard_deletes: ignore"):
            with self.subTest(token=token):
                self.assertIn(token, snapshot)

    def test_singular_tests_use_dbt_refs(self):
        for filename in SINGULAR_TESTS:
            with self.subTest(filename=filename):
                path = ROOT / "tests/dbt" / filename
                self.assertTrue(path.is_file())
                self.assertIn("{{ ref(", path.read_text(encoding="utf-8"))

    def test_snowflake_integration_never_runs_on_push(self):
        workflow = (ROOT / ".github/workflows/snowflake-integration.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("workflow_dispatch:", workflow)
        self.assertNotIn("\n  push:", workflow)
        self.assertIn("inputs.confirm == 'yes'", workflow)
        for command in ("dbt debug", "dbt seed", "dbt run", "dbt snapshot", "dbt test"):
            self.assertIn(command, workflow)


if __name__ == "__main__":
    unittest.main()
