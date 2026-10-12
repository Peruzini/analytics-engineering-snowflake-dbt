"""Freeze descriptive contract facts; these are synthetic, not measured business KPIs."""
import unittest
from scripts.analyze_business import summarize

class MVP04BAnalytics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kpis = summarize()

    def test_revenue_and_scale(self):
        self.assertEqual(self.kpis["orders"], 4200)
        self.assertEqual(self.kpis["items"], 8400)
        self.assertEqual(self.kpis["recognized_revenue"], "2699981.55")
        self.assertEqual(self.kpis["completed_orders"], 3588)

    def test_calendar_and_mom(self):
        k = self.kpis
        self.assertEqual(k["period"], ["2025-10-01", "2026-09-30"])
        self.assertEqual(len(k["monthly"]), 12)
        self.assertEqual(k["monthly"]["2025-11"]["revenue"], "338418.72")
        self.assertEqual(k["monthly"]["2025-10"]["revenue"], "238223.92")
        self.assertEqual(k["monthly"]["2026-02"]["days"], 28)

    def test_channel_and_repurchase(self):
        k = self.kpis
        self.assertEqual(set(k["channels"]), {
            "email", "organic", "social", "paid_search", "unattributed"
        })
        self.assertEqual(k["buyers"], 420)
        self.assertEqual(k["repeat_buyers_2plus_completed"], 414)
        self.assertEqual(k["channels"]["unattributed"]["orders"], 466)

if __name__ == "__main__":
    unittest.main()
