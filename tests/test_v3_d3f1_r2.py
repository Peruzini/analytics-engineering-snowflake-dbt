import json, hashlib, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MODEL=ROOT/'powerbi/EcommerceAnalytics.SemanticModel/model.bim'
PAGES=ROOT/'powerbi/EcommerceAnalytics.Report/definition/pages'
class TestNativeRefinement(unittest.TestCase):
    def test_prior_semantic_objects_exact(self):
        m=json.loads(MODEL.read_text(encoding='utf-8'))
        for t in m['model']['tables']:
            if t['name']=='Medidas':
                self.assertEqual(len(t['measures']),50)
                t['measures']=t['measures'][:44]
            else:
                t['columns']=[c for c in t['columns'] if c['name'] not in ('Categoria PT','Canal PT','Status PT')]
        digest=hashlib.sha256(json.dumps(m,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
        self.assertEqual(digest,"8a69fe4ca01ddb946108cb0a2daef034c74750500446c04b041538f475d51853")
    def test_reference_bindings(self):
        for ident in ('d3e2000000000000000a','d3e2000000000000000e'):
            f=next(PAGES.glob('*/visuals/'+ident+'/visual.json'))
            z=json.loads(f.read_text(encoding='utf-8'))['visual']
            refs={p['queryRef'] for p in z['query']['queryState']['Tooltips']['projections']}
            for axis in ('xAxisReferenceLine','y1AxisReferenceLine'):
                o=z['objects'][axis][0]
                self.assertEqual(o['selector']['id'],'0')
                self.assertIn(o['properties']['value']['expr']['SelectRef']['ExpressionName'],refs)
    def test_localized_columns_keep_source_columns(self):
        m=json.loads(MODEL.read_text(encoding='utf-8'))
        tables={t['name']:{c['name']:c for c in t['columns']} for t in m['model']['tables']}
        for t,raw,localized in [('DimProdutos','category','Categoria PT'),('FatoPedidos','channel','Canal PT'),('FatoPedidos','order_status','Status PT'),('FatoItens','order_status','Status PT')]:
            self.assertIn(raw,tables[t])
            c=tables[t][localized]
            self.assertEqual(c['type'],'calculated')
            self.assertIn(t+'['+raw+']',c['expression'])
