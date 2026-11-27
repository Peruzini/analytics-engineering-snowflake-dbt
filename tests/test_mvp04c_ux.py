"""MVP-04C: deterministic static PBIR layout/storytelling quality gates.

Does not assert visual rendering or data refresh in Power BI Desktop.
"""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
BI = ROOT / "powerbi"
REPORT = BI / "EcommerceAnalytics.Report"
PAGES = REPORT / "definition" / "pages"

EXPECTED = {
    "aea00000000000000001": ("Visão Executiva", 16, "RECEITA & PERFORMANCE"),
    "aea00000000000000002": ("Receita e Pedidos", 17, "PEDIDOS & EFICIÊNCIA"),
    "aea00000000000000003": ("Clientes e Produtos", 17, "CLIENTES & MIX"),
    "aea00000000000000004": ("Canais e Pedidos", 16, "CANAIS & ATRIBUIÇÃO"),
}

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def text_content(visual):
    result = []
    for section in visual["visual"].get("objects", {}).get("general", []):
        for paragraph in section.get("properties", {}).get("paragraphs", []):
            result.extend(run.get("value", "") for run in paragraph.get("textRuns", []))
    return " ".join(result)

class TestReportUX(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page_content = {}
        for name in EXPECTED:
            folder = PAGES / name
            cls.page_content[name] = [
                load(path) for path in sorted(folder.glob("visuals/*/visual.json"))
            ]

    def test_page_order_and_visual_inventory(self):
        manifest = load(PAGES / "pages.json")
        self.assertEqual(manifest["pageOrder"], list(EXPECTED))
        self.assertEqual(manifest["activePageName"], list(EXPECTED)[0])
        self.assertEqual(sum(len(v) for v in self.page_content.values()), 66)
        for page_id, (label, count, title) in EXPECTED.items():
            with self.subTest(page=label):
                self.assertEqual(load(PAGES / page_id / "page.json")["displayName"], label)
                self.assertEqual(len(self.page_content[page_id]), count)
                texts = " ".join(
                    text_content(v) for v in self.page_content[page_id]
                )
                self.assertIn(title, texts)
                self.assertIn("DADOS SINTÉTICOS", texts)
                self.assertIn("LEITURA", texts)

    def test_no_out_of_bounds_or_visual_overlap(self):
        for page_id, visuals in self.page_content.items():
            page = load(PAGES / page_id / "page.json")
            for idx, visual in enumerate(visuals):
                p = visual["position"]
                with self.subTest(page=page_id, visual=visual["name"]):
                    self.assertEqual(visual["name"], p.get("name", visual["name"]))
                    self.assertGreaterEqual(p["x"], 0)
                    self.assertGreaterEqual(p["y"], 0)
                    self.assertLessEqual(p["x"] + p["width"], page["width"])
                    self.assertLessEqual(p["y"] + p["height"], page["height"])
                    self.assertGreater(p["width"], 0)
                    self.assertGreater(p["height"], 0)
                for other in visuals[idx + 1:]:
                    q = other["position"]
                    x_overlap = min(p["x"] + p["width"], q["x"] + q["width"]) - max(p["x"], q["x"])
                    y_overlap = min(p["y"] + p["height"], q["y"] + q["height"]) - max(p["y"], q["y"])
                    self.assertFalse(x_overlap > 0 and y_overlap > 0,
                                     f"Layout overlap: {page_id} {visual['name']} {other['name']}")

    def test_design_system_and_recruiter_first_read(self):
        theme = load(REPORT / "StaticResources" / "RegisteredResources" /
                     "EcommercePortfolio.json")
        self.assertGreaterEqual(len(theme["dataColors"]), 5)
        for page_id, visuals in self.page_content.items():
            texts = [v for v in visuals if v["visual"]["visualType"] == "textbox"]
            self.assertEqual(len(texts), 4)
            banner = next(v for v in texts if " / 04 " in text_content(v))
            self.assertEqual(banner["position"]["y"], 12)
            cards = [v for v in visuals if v["visual"]["visualType"] == "cardVisual"]
            self.assertEqual(len(cards), 4)
            self.assertEqual({v["position"]["y"] for v in cards}, {178})
            self.assertEqual({v["position"]["height"] for v in cards}, {92})
            tabs = [v for v in visuals if v["visual"]["visualType"] == "slicer"]
            self.assertEqual(len(tabs), 4)
            self.assertEqual({v["position"]["y"] for v in tabs}, {106})
            self.assertEqual(len([v for v in visuals if v["visual"]["visualType"] == "tableEx"]), 1)
            self.assertEqual(len([v for v in visuals if v["visual"]["visualType"] in {"lineChart", "clusteredBarChart", "scatterChart", "pivotTable", "lineClusteredColumnComboChart"}]), 3 if page_id in (list(EXPECTED)[0], list(EXPECTED)[3]) else 4)
            self.assertEqual(len({v["position"]["tabOrder"] for v in visuals}), len(visuals))
            for v in visuals:
                if v["visual"]["visualType"] != "textbox":
                    self.assertTrue(v["visual"]["visualContainerObjects"]["general"][0]["properties"]["altText"])
            self.assertTrue(any("LEITURA" in text_content(v) for v in texts))

    def test_product_chart_uses_category_not_40_individual_bars(self):
        page = self.page_content["aea00000000000000003"]
        bars = [v for v in page if v["visual"]["visualType"] == "clusteredBarChart"]
        self.assertEqual(len(bars), 1)
        refs = [v["visual"]["query"]["queryState"]["Category"]["projections"][0]["queryRef"]
                for v in bars]
        self.assertIn("DimProdutos.category", refs)
        self.assertNotIn("DimProdutos.product_name", refs)
        matrix = next(v for v in page if v["visual"]["visualType"] == "pivotTable")
        roles = matrix["visual"]["query"]["queryState"]
        self.assertEqual(roles["Rows"]["projections"][0]["queryRef"], "DimProdutos.category")
        self.assertEqual(roles["Columns"]["projections"][0]["queryRef"], "DimClientes.region")
        self.assertEqual(roles["Values"]["projections"][0]["queryRef"], "Medidas.Receita Itens")
        pareto = next(v for v in page if v["visual"]["visualType"] == "lineClusteredColumnComboChart")
        self.assertEqual(pareto["visual"]["query"]["queryState"]["Y2"]["projections"][0]["queryRef"], "Medidas.Pareto Produtos Top 10 %")
        table = next(v for v in page if v["visual"]["visualType"] == "tableEx")
        detail = [x["queryRef"] for x in table["visual"]["query"]["queryState"]["Values"]["projections"]]
        self.assertIn("DimProdutos.product_name", detail)

    def test_channel_date_and_synthetic_caveat(self):
        page = self.page_content["aea00000000000000004"]
        refs = [p["queryRef"] for visual in page
                for obj in visual["visual"].get("query", {}).get("queryState", {}).values()
                for p in obj.get("projections", [])]
        self.assertIn("FatoPedidos.channel", refs)
        self.assertIn("DimData.AnoMes", refs)
        texts = " ".join(text_content(v) for v in page)
        self.assertIn("não há investimento realizado", texts.casefold())
        self.assertIn("ROAS", texts)
        self.assertIn("CAC", texts)
        line = next(v for v in page if v["visual"]["visualType"] == "lineChart")
        self.assertEqual(line["visual"]["query"]["queryState"]["Rows"]["projections"][0]["queryRef"], "FatoPedidos.channel")

if __name__ == "__main__":
    unittest.main()
