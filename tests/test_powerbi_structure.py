"""Static validation of PBIP/PBIR/TMSL contracts; no Power BI Desktop required."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
BI = ROOT / "powerbi"
REPORT = BI / "EcommerceAnalytics.Report"
MODEL = BI / "EcommerceAnalytics.SemanticModel"

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

class TestPBIP(unittest.TestCase):
    def test_entrypoint_and_four_pages(self):
        pbip = read(BI / "EcommerceAnalytics.pbip")
        self.assertEqual(pbip["artifacts"][0]["report"]["path"], REPORT.name)
        pbir = read(REPORT / "definition.pbir")
        self.assertEqual(pbir["datasetReference"]["byPath"]["path"], "../" + MODEL.name)
        pages = read(REPORT / "definition/pages/pages.json")
        self.assertEqual(len(pages["pageOrder"]), 4)
        for ident in pages["pageOrder"]:
            page = REPORT / "definition/pages" / ident
            self.assertEqual(read(page / "page.json")["name"], ident)
            self.assertGreaterEqual(len(list((page / "visuals").glob("*/visual.json"))), 7)

    def test_refs_resolve_to_columns_or_measures(self):
        model = read(MODEL / "model.bim")["model"]
        tables = {t["name"]: {c["name"] for c in t["columns"]} |
                  {m["name"] for m in t.get("measures", [])} for t in model["tables"]}
        self.assertEqual(len(tables["Medidas"]), 27)
        for path in (REPORT / "definition/pages").glob("*/visuals/*/visual.json"):
            visual = read(path)
            self.assertEqual(visual["name"], path.parent.name)
            roles = visual["visual"].get("query", {}).get("queryState", {})
            for projections in roles.values():
                for projection in projections.get("projections", []):
                    f = projection["field"]
                    info = f.get("Column") or f.get("Measure")
                    table, prop = info["Expression"]["SourceRef"]["Entity"], info["Property"]
                    self.assertIn(table, tables, str(path))
                    self.assertIn(prop, tables[table], f"{path}: {table}.{prop}")

    def test_sources_relationships_and_no_secrets(self):
        model = read(MODEL / "model.bim")["model"]
        tables = {t["name"]: t for t in model["tables"]}
        self.assertEqual(len(model["relationships"]), 5)
        for rel in model["relationships"]:
            self.assertIn(rel["fromColumn"], {c["name"] for c in tables[rel["fromTable"]]["columns"]})
            self.assertIn(rel["toColumn"], {c["name"] for c in tables[rel["toTable"]]["columns"]})
        for t in model["tables"]:
            expr = "\n".join(t["partitions"][0]["source"]["expression"])
            self.assertNotIn("DBT_SNOWFLAKE_PRIVATE_KEY", expr)
            if t["name"] not in ("DimData", "Medidas"):
                self.assertIn("raw.githubusercontent.com/Peruzini/analytics-engineering-snowflake-dbt/main/", expr)
                self.assertIn("/powerbi/data/", expr)

    def test_all_pbir_files_are_json(self):
        for path in REPORT.rglob("*.json"):
            with self.subTest(path=path):
                self.assertIsInstance(read(path), dict)

if __name__ == "__main__":
    unittest.main()
