"""MVP-02: independent Python checks of the documented business rules.
These verify synthetic fixture arithmetic, NOT Snowflake SQL execution.
"""
from collections import defaultdict
from decimal import Decimal
from pathlib import Path
import unittest

from scripts.generate_data import build_rows, HEADERS, CONFIG

EXPECTED_MODELS = {
    "intermediate": {"int_order_financials", "int_customer_orders"},
    "marts": {
        "dim_customers", "dim_products", "fct_orders", "fct_order_items",
        "mart_daily_sales", "mart_customer_ltv", "mart_channel_performance"
    }
}


def fixture_tables():
    return {
        filename.replace("raw_", "").replace(".csv", ""): [
            dict(zip(HEADERS[filename], record)) for record in records
        ]
        for filename, records in build_rows().items()
    }


class TestModelContracts(unittest.TestCase):
    def test_sql_models_exist_with_refs(self):
        root = Path(__file__).resolve().parents[1] / "models"
        for layer, names in EXPECTED_MODELS.items():
            for name in names:
                with self.subTest(name=name):
                    path = root / layer / (name + ".sql")
                    self.assertTrue(path.is_file())
                    self.assertIn("ref(", path.read_text(encoding="utf-8"))

    def test_status_rules_explicit(self):
        path = Path(__file__).resolve().parents[1] / "models/intermediate/int_customer_orders.sql"
        content = path.read_text(encoding="utf-8")
        self.assertIn("order_status = 'completed'", content)
        self.assertIn("order_status = 'refunded'", content)


class TestFinancialExpectations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data = fixture_tables()
        cls.orders = data["orders"]
        cls.items = data["order_items"]
        cls.payments = data["payments"]
        cls.campaigns = data["campaigns"]

    def test_revenue_reconciles_by_day_customer_and_channel(self):
        net_by_order = defaultdict(lambda: Decimal("0.00"))
        for row in self.items:
            quantity = int(row["quantity"])
            net_by_order[row["order_id"]] += (
                Decimal(row["unit_price"]) * quantity - Decimal(row["discount_amount"])
            )
        channels = {c["campaign_id"]: c["channel"] for c in self.campaigns}
        by_day = defaultdict(lambda: Decimal("0.00"))
        by_customer = defaultdict(lambda: Decimal("0.00"))
        by_channel = defaultdict(lambda: Decimal("0.00"))
        by_item_order = Decimal("0.00")
        for order in self.orders:
            amount = net_by_order[order["order_id"]] if order["order_status"] == "completed" else Decimal("0.00")
            by_day[order["order_date"]] += amount
            by_customer[order["customer_id"]] += amount
            by_channel[channels.get(order["campaign_id"], "unattributed")] += amount
            by_item_order += amount
        self.assertGreater(by_item_order, Decimal("0"))
        self.assertEqual(by_item_order, sum(by_day.values(), Decimal("0.00")))
        self.assertEqual(by_item_order, sum(by_customer.values(), Decimal("0.00")))
        self.assertEqual(by_item_order, sum(by_channel.values(), Decimal("0.00")))
        self.assertEqual(set(by_channel), {"organic", "paid_search", "social", "email", "unattributed"})

    def test_payments_aggregated_at_order_grain(self):
        net_by_order = defaultdict(lambda: Decimal("0.00"))
        for item in self.items:
            net_by_order[item["order_id"]] += (
                Decimal(item["unit_price"]) * int(item["quantity"]) - Decimal(item["discount_amount"])
            )
        order_status = {order["order_id"]: order["order_status"] for order in self.orders}
        self.assertEqual(
            {pay["order_id"] for pay in self.payments},
            {oid for oid, status in order_status.items() if status in {"completed", "refunded"}}
        )
        for payment in self.payments:
            self.assertEqual(Decimal(payment["amount"]), net_by_order[payment["order_id"]])

    def test_all_statuses_present_and_non_completed_excluded(self):
        statuses = {o["order_status"] for o in self.orders}
        self.assertEqual(statuses, {"completed", "pending", "cancelled", "refunded"})
        self.assertEqual(len(self.orders), CONFIG["orders"])
        for order in self.orders:
            should_recognize = order["order_status"] == "completed"
            if order["order_status"] in {"refunded", "pending", "cancelled"}:
                self.assertFalse(should_recognize)


if __name__ == "__main__":
    unittest.main()
