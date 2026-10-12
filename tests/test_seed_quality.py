"""Offline checks for deterministic fixtures and relational integrity."""
import csv
import io
import unittest
from decimal import Decimal
from pathlib import Path

from scripts.generate_data import build_rows, render_csvs, HEADERS

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
        self.assertEqual(len(self.data["raw_customers.csv"]), 12)
        self.assertEqual(len(self.data["raw_products.csv"]), 8)
        self.assertEqual(len(self.data["raw_campaigns.csv"]), 4)
        self.assertEqual(len(self.data["raw_orders.csv"]), 36)
        self.assertEqual(len(self.data["raw_order_items.csv"]), 72)

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
