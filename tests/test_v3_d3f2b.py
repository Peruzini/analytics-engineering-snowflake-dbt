import json,csv,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PAGES=ROOT/"powerbi/EcommerceAnalytics.Report/definition/pages"
class TestEcommerceFunctional(unittest.TestCase):
 def test_common_and_local_slicers(self):
  groups={}
  local=[]
  for f in PAGES.glob("*/visuals/*/visual.json"):
   v=json.loads(f.read_text(encoding="utf-8"))["visual"]
   if v["visualType"]!="slicer":continue
   field=v["query"]["queryState"]["Values"]["projections"][0]["queryRef"]
   if "syncGroup" not in v:local.append(field);continue
   g=v["syncGroup"];self.assertTrue(g["fieldChanges"] and g["filterChanges"])
   groups.setdefault(g["groupName"],[]).append((f.parts[-4],field))
  self.assertEqual(local,["DimProdutos.Categoria PT"])
  self.assertEqual(len(groups),4)
  for vals in groups.values():
   self.assertEqual(len(vals),4);self.assertEqual(len({x[0] for x in vals}),4);self.assertEqual(len({x[1] for x in vals}),1)
 def test_interaction_contract(self):
  for f in PAGES.glob("*/page.json"):
   page=json.loads(f.read_text(encoding="utf-8"))
   v={x.parent.name:json.loads(x.read_text(encoding="utf-8"))["visual"]["visualType"] for x in f.parent.glob("visuals/*/visual.json")}
   pairs=page["visualInteractions"]
   self.assertEqual(len(pairs),len({(p["source"],p["target"]) for p in pairs}))
   for p in pairs:
    self.assertIn(p["source"],v);self.assertIn(p["target"],v);self.assertNotEqual(p["source"],p["target"])
    self.assertEqual(p["type"],"NoFilter" if v[p["source"]]!="slicer" and v[p["target"]]=="slicer" else "DataFilter")
 def test_item_status_consistency(self):
  with (ROOT/"powerbi/data/fct_orders.csv").open(encoding="utf-8-sig",newline="") as f:orders={r["order_id"]:r["order_status"] for r in csv.DictReader(f)}
  with (ROOT/"powerbi/data/fct_order_items.csv").open(encoding="utf-8-sig",newline="") as f:items=list(csv.DictReader(f))
  self.assertEqual(len(items),8400)
  self.assertTrue(all(r["order_status"]==orders[r["order_id"]] for r in items))
