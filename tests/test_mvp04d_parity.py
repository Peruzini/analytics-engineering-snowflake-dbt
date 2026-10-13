"""Unit coverage for the release parity checker (does not require dbt)."""
import unittest
from scripts.export_powerbi import first_difference, TABLES

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

    def test_all_seven_marts_are_covered(self):
        self.assertEqual(len(TABLES), 7)
        self.assertIn("fct_orders", TABLES)
        self.assertIn("fct_order_items", TABLES)
        self.assertIn("mart_channel_performance", TABLES)

if __name__ == "__main__":
    unittest.main()
