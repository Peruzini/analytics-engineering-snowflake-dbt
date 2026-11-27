"""Unit coverage for the release parity checker (does not require dbt)."""
import unittest
from decimal import Decimal
from scripts.export_powerbi import first_difference, TABLES, canonical_average_ticket

class TestExporterDiagnostics(unittest.TestCase):
    def test_first_changed_csv_row(self):
        value = first_difference("id,value\n1,2.00\n", "id,value\n1,2.01\n")
        self.assertIn("line 2", value)
        self.assertIn("2.00", value)
        self.assertIn("2.01", value)

    def test_missing_output_line(self):
        value = first_difference("id\n1\n", "id\n")
        self.assertIn("line 2", value)
        self.assertIn("<missing>", value)

    def test_half_cent_ticket_uses_exact_decimal_half_even(self):
        self.assertEqual(canonical_average_ticket({
            "lifetime_recognized_revenue": Decimal("4172.43"),
            "completed_orders": 6, "avg_completed_ticket": 695.4050000000001,
        }), "695.40")
        self.assertEqual(canonical_average_ticket({
            "recognized_revenue": Decimal("2.03"),
            "completed_orders": 2, "avg_completed_ticket": 1.015,
        }), "1.02")

    def test_ticket_rejects_inconsistent_sql(self):
        with self.assertRaises(ValueError):
            canonical_average_ticket({
                "recognized_revenue": Decimal("100.00"),
                "completed_orders": 2, "avg_completed_ticket": 50.01,
            })

    def test_ticket_without_completed_orders(self):
        self.assertEqual(canonical_average_ticket({
            "recognized_revenue": Decimal("0.00"),
            "completed_orders": 0, "avg_completed_ticket": None,
        }), "")
        with self.assertRaises(ValueError):
            canonical_average_ticket({
                "recognized_revenue": Decimal("0.00"),
                "completed_orders": 0, "avg_completed_ticket": 0,
            })

    def test_all_seven_marts_are_covered(self):
        self.assertEqual(len(TABLES), 7)
        self.assertIn("fct_orders", TABLES)
        self.assertIn("fct_order_items", TABLES)
        self.assertIn("mart_channel_performance", TABLES)

if __name__ == "__main__":
    unittest.main()
