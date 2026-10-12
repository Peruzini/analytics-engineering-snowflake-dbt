"""Offline checks for deterministic fixtures and relational integrity."""
import csv
import io
import unittest
from decimal import Decimal
from pathlib import Path

from scripts.generate_data import build_rows, render_csvs, HEADERS, CONFIG, orders_per_day

ROOT = Path(__file__).resolve().parents[1]


class TestSeedQuality(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tables = build_rows()
        cls.data = {
            name: [dict(zip(HEADERS[name], record)) for record in rows]
            for name, rows in cls.tables.items()
        }

    def test_fixtures_are_reproducible(self):
        for filename, expected in render_csvs().items():
            with self.subTest(filename=filename):
                self.assertEqual((ROOT / "seeds" / filename).read_text(encoding="utf-8"), expected)

    def test_row_counts(self):
        self.assertEqual(len(self.data["raw_customers.csv"]), CONFIG["customers"])
        self.assertEqual(len(self.data["raw_products.csv"]), len(CONFIG["product_catalog"]))
        self.assertEqual(len(self.data["raw_campaigns.csv"]), len(CONFIG["channels"]) * CONFIG["campaigns_per_channel"])
        self.assertEqual(len(self.data["raw_orders.csv"]), CONFIG["orders"])
        self.assertGreaterEqual(len(self.data["raw_order_items.csv"]), CONFIG["orders"])


    def test_twelve_months_and_seasonality(self):
        from collections import Counter
        from datetime import date
        orders = self.data["raw_orders.csv"]
        months = Counter(r["order_date"][:7] for r in orders)
        self.assertEqual(len(months), 12)
        self.assertEqual(min(r["order_date"] for r in orders), CONFIG["start_date"])
        self.assertEqual(max(r["order_date"] for r in orders), "2026-09-30")
        self.assertGreater(months["2025-11"], months["2026-02"])
        self.assertTrue(all(q > 0 for _, q in orders_per_day()))

    def test_repurchase_and_diverse_channels(self):
        from collections import Counter
        orders = self.data["raw_orders.csv"]
        counts = Counter(r["customer_id"] for r in orders)
        self.assertGreaterEqual(sum(x > 1 for x in counts.values()), 250)
        campaigns = {c["campaign_id"]: c["channel"] for c in self.data["raw_campaigns.csv"]}
        actual = {campaigns.get(o["campaign_id"], "unattributed") for o in orders}
        self.assertEqual(actual, set(CONFIG["channels"]) | {"unattributed"})
        self.assertEqual({r["region"] for r in self.data["raw_customers.csv"]},
                         {"SP", "RJ", "MG", "PR", "SC", "RS", "BA"})

    def test_all_business_keys_unique_and_nonempty(self):
        keys = {
            "raw_customers.csv": "customer_id",
            "raw_products.csv": "product_id",
            "raw_campaigns.csv": "campaign_id",
            "raw_orders.csv": "order_id",
            "raw_order_items.csv": "order_item_id",
            "raw_payments.csv": "payment_id",
        }
        for filename, column in keys.items():
            with self.subTest(filename=filename):
                values = [row[column] for row in self.data[filename]]
                self.assertTrue(all(values))
                self.assertEqual(len(values), len(set(values)))

    def test_foreign_keys(self):
        customers = {r["customer_id"] for r in self.data["raw_customers.csv"]}
        products = {r["product_id"] for r in self.data["raw_products.csv"]}
        campaigns = {r["campaign_id"] for r in self.data["raw_campaigns.csv"]}
        orders = {r["order_id"] for r in self.data["raw_orders.csv"]}
        for row in self.data["raw_orders.csv"]:
            self.assertIn(row["customer_id"], customers)
            if row["campaign_id"]:
                self.assertIn(row["campaign_id"], campaigns)
        for row in self.data["raw_order_items.csv"]:
            self.assertIn(row["order_id"], orders)
            self.assertIn(row["product_id"], products)
        for row in self.data["raw_payments.csv"]:
            self.assertIn(row["order_id"], orders)

    def test_order_status_and_financials(self):
        allowed = {"completed", "cancelled", "pending", "refunded"}
        totals = {}
        for row in self.data["raw_order_items.csv"]:
            qty = int(row["quantity"])
            price = Decimal(row["unit_price"])
            discount = Decimal(row["discount_amount"])
            self.assertGreater(qty, 0)
            self.assertGreater(price, Decimal("0"))
            self.assertGreaterEqual(discount, Decimal("0"))
            self.assertLessEqual(discount, price * qty)
            totals[row["order_id"]] = totals.get(row["order_id"], Decimal("0")) + qty * price - discount

        orders = {row["order_id"]: row for row in self.data["raw_orders.csv"]}
        payments = {row["order_id"]: row for row in self.data["raw_payments.csv"]}
        for order_id, order in orders.items():
            status = order["order_status"]
            self.assertIn(status, allowed)
            if status in {"completed", "refunded"}:
                self.assertIn(order_id, payments)
                self.assertEqual(Decimal(payments[order_id]["amount"]), totals[order_id])
                self.assertEqual(payments[order_id]["payment_status"],
                                 "paid" if status == "completed" else "refunded")
            else:
                self.assertNotIn(order_id, payments)


if __name__ == "__main__":
    unittest.main()
