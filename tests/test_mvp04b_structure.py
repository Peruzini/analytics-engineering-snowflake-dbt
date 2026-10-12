"""Static MVP-04B contract: campaign attribution, time-aware channels and DAX grain."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
BI = ROOT / "powerbi"
PAGES = BI / "EcommerceAnalytics.Report" / "definition" / "pages"
MODEL = BI / "EcommerceAnalytics.SemanticModel" / "model.bim"

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def projections(visual):
    roles = visual.get("query", {}).get("queryState", {})
    for role in roles.values():
        for p in role.get("projections", []):
            field = p["field"]
            spec = field.get("Column") or field.get("Measure")
            if spec:
                yield (spec["Expression"]["SourceRef"]["Entity"], spec["Property"])

class TestMVP04BSemantics(unittest.TestCase):
    def test_attribution_sql_and_incremental_guard(self):
        intermediate = (ROOT / "models/intermediate/int_customer_orders.sql").read_text(encoding="utf-8")
        fact = (ROOT / "models/marts/fct_orders.sql").read_text(encoding="utf-8")
        self.assertIn("coalesce(c.channel, 'unattributed') as channel", intermediate)
        self.assertIn("ref('stg_campaigns')", intermediate)
        self.assertIn("existing.channel is not distinct from incoming.channel", fact)
        test = ROOT / "tests/dbt/assert_order_channel_attribution.sql"
        self.assertTrue(test.exists())
        self.assertIn("ref('stg_campaigns')", test.read_text(encoding="utf-8"))

    def test_channel_page_uses_fact_not_historical_mart(self):
        tables = {t["name"]: t for t in load(MODEL)["model"]["tables"]}
        self.assertIn("channel", {c["name"] for c in tables["FatoPedidos"]["columns"]})
        page = PAGES / "aea00000000000000004"
        self.assertEqual(load(page / "page.json")["displayName"], "Canais e Pedidos")
        all_refs = []
        types = []
        for file in (page / "visuals").glob("*/visual.json"):
            obj = load(file)
            types.append(obj["visual"]["visualType"])
            all_refs.extend(projections(obj["visual"]))
        self.assertEqual(len(list((page / "visuals").glob("*/visual.json"))), 12)
        self.assertIn(("FatoPedidos", "channel"), all_refs)
        self.assertIn(("DimData", "AnoMes"), all_refs)
        self.assertIn(("Medidas", "Participação Receita Canal %"), all_refs)
        self.assertNotIn("ResumoCanais", {t for t, _ in all_refs})
        self.assertIn("lineChart", types)
        self.assertIn("clusteredBarChart", types)

    def test_month_over_month_is_month_grain(self):
        model = load(MODEL)["model"]
        measures = {m["name"]: m["expression"] for table in model["tables"]
                    for m in table.get("measures", [])}
        self.assertEqual(len(measures), 39)
        self.assertIn("HASONEVALUE(DimData[AnoMes])", measures["Receita Mês Anterior"])
        self.assertIn("FILTER(ALL(DimData)", measures["Receita Mês Anterior"])
        self.assertIn("DISTINCTCOUNT(DimData[Data])", measures["Receita por Dia"])
        month_table = load(PAGES / "aea00000000000000002" / "visuals" /
                           "0000000000000000aa6c" / "visual.json")
        fields = set(projections(month_table["visual"]))
        self.assertIn(("DimData", "AnoMes"), fields)
        self.assertIn(("Medidas", "Variação Receita MoM %"), fields)
        self.assertIn(("Medidas", "Receita por Dia"), fields)

    def test_no_unjustified_business_measures(self):
        model = load(MODEL)["model"]
        names = {m["name"].lower() for t in model["tables"]
                 for m in t.get("measures", [])}
        for unsupported in ("roas", "cac", "margem", "churn", "conversão", "ltv previsto"):
            self.assertNotIn(unsupported, names)

if __name__ == "__main__":
    unittest.main()
