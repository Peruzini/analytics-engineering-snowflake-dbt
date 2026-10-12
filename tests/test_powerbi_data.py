"""Validate published Power BI CSV dataset contracts without any cloud calls."""
import csv
from decimal import Decimal
from pathlib import Path
from scripts.generate_data import CONFIG
import unittest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "powerbi" / "data"

def load(name):
    with (DATA / (name + ".csv")).open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))

class TestPowerBIFixtures(unittest.TestCase):
    def test_row_counts_and_unique_keys(self):
        for name, key, count in [
            ("dim_customers", "customer_id", CONFIG["customers"]),
            ("dim_products", "product_id", len(CONFIG["product_catalog"])),
            ("fct_orders", "order_id", CONFIG["orders"]),
            ("fct_order_items", "order_item_id", None),
            ("mart_daily_sales", "order_date", CONFIG["days"]),
            ("mart_customer_ltv", "customer_id", CONFIG["customers"]),
            ("mart_channel_performance", "channel", 5),
        ]:
            with self.subTest(table=name):
                rows = load(name)
                if count is not None:
                    self.assertEqual(len(rows), count)
                else:
                    self.assertGreater(len(rows), CONFIG["orders"])
                keys = [row[key] for row in rows]
                self.assertEqual(len(set(keys)), len(rows))

    def test_revenue_reconciles_across_grains(self):
        orders, items, daily, customers, channels = (
            load(n) for n in ("fct_orders", "fct_order_items", "mart_daily_sales",
                              "mart_customer_ltv", "mart_channel_performance")
        )
        for field, rows in (("recognized_revenue", orders), ("recognized_item_revenue", items),
                            ("recognized_revenue", daily), ("lifetime_recognized_revenue", customers),
                            ("recognized_revenue", channels)):
            total = sum((Decimal(r[field]) for r in rows), Decimal("0"))
            expected = sum((Decimal(r["recognized_revenue"]) for r in orders), Decimal("0"))
            self.assertEqual(total, expected)
        for row in orders:
            if row["order_status"] != "completed":
                self.assertEqual(Decimal(row["recognized_revenue"]), Decimal("0"))
        self.assertEqual({c["channel"] for c in channels},
                         {"organic", "paid_search", "social", "email", "unattributed"})

if __name__ == "__main__":
    unittest.main()
