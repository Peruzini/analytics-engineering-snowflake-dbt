"""V3-05D3D: local-only browser acceptance gate. No deploy."""
import argparse
import csv
import functools
import hashlib
import http.server
import io
import json
import struct
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
LAB = Path(__file__).resolve().parents[1].name
FLEET = LAB == "fleet-analytics"
PAGES = ({"executiva": 2, "performance": 3, "manutencao": 4, "criticidade": 2}
         if FLEET else {"executiva": 3, "pedidos": 4, "clientes": 4, "canais": 3})
VIEWPORTS = [(1440, 900), (1024, 768), (390, 844), (320, 720)]
FILTERS = (dict.fromkeys(PAGES, "id") if FLEET else
           {"executiva": "region", "pedidos": "status", "clientes": "category", "canais": "channel"})

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--executable", help="Local Chromium/Chrome executable, optional")
    args = parser.parse_args()
    out = args.output.resolve()
    if ROOT == out or ROOT in out.parents:
        raise SystemExit("Use --output outside the repository")
    out.mkdir(parents=True, exist_ok=True)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0),
        functools.partial(QuietHandler, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{server.server_port}/labs/{LAB}/"
    checks, screenshots = [], []
    def check(name, condition, detail=None):
        checks.append({"name": name, "pass": bool(condition), "detail": detail})
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(**({"executable_path": args.executable} if args.executable else {}))
            version = browser.version
            for width, height in VIEWPORTS:
                context = browser.new_context(viewport={"width": width, "height": height},
                                              accept_downloads=True, locale="pt-BR")
                page = context.new_page()
                errors = []
                page.on("pageerror", lambda exc: errors.append(str(exc)))
                page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
                page.goto(url)
                page.locator("#navigation a").first.wait_for(timeout=30000)
                for name, chart_count in PAGES.items():
                    prefix = f"{width}x{height}/{name}"
                    try:
                        page.locator(f"#navigation a[data-page='{name}']").click()
                        page.locator(f"#navigation a[data-page='{name}'][aria-current='page']").wait_for()
                        page.locator("#dashboard .kpi").first.wait_for()
                        check(prefix+"/KPIs", page.locator("#dashboard .kpi").count() == 4)
                        check(prefix+"/charts", page.locator("#dashboard svg.chart").count() == chart_count)
                        check(prefix+"/body width", page.evaluate(
                            "document.documentElement.scrollWidth <= innerWidth+1"))
                        check(prefix+"/valid SVG", page.locator("#dashboard svg").evaluate_all(
                            "(xs)=>xs.every(s=>s.viewBox.baseVal.width>0 && !/NaN|Infinity|undefined/.test(s.outerHTML))"))
                        check(prefix+"/unique IDs", page.evaluate(
                            "()=>{const ids=[...document.querySelectorAll('[id]')].map(x=>x.id);return new Set(ids).size===ids.length}"))
                        check(prefix+"/chart fit", page.locator("#dashboard .chart-scroll").evaluate_all(
                            "xs=>xs.every(x=>x.scrollWidth<=x.clientWidth+2)"))
                        collisions = page.locator("#dashboard svg").evaluate_all(
                            """xs=>xs.flatMap(s=>{const scatter=s.getAttribute('aria-label')||'';
                            if(!['Produtividade e custo','Indisponibilidade e custo','Receita e recompra','Ticket e conclusão'].includes(scatter))return [];
                            const labels=Array.from(s.querySelectorAll('g[data-asset] text'));
                            return labels.flatMap((a,i)=>labels.slice(i+1).filter(b=>{const x=a.getBoundingClientRect(),y=b.getBoundingClientRect();
                            return x.left<y.right&&x.right>y.left&&x.top<y.bottom&&x.bottom>y.top}).map(b=>a.textContent+' / '+b.textContent))})""")
                        check(prefix+"/scatter labels", not collisions, collisions)
                        if not FLEET and name=="clientes":
                            contrast = page.locator("[data-heat-cell]").evaluate_all(
                                """xs=>{const lum=h=>{const a=h.slice(1).match(/../g).map(x=>parseInt(x,16)/255).map(x=>x<=.04045?x/12.92:((x+.055)/1.055)**2.4);return a[0]*.2126+a[1]*.7152+a[2]*.0722};
                                return xs.map(g=>{const a=lum(g.querySelector('rect').getAttribute('fill')),b=lum(g.querySelector('text').getAttribute('fill'));return (Math.max(a,b)+.05)/(Math.min(a,b)+.05)})}""")
                            check(prefix+"/heatmap contrast", len(contrast)==42 and min(contrast)>=4.5,
                                  {"cells":len(contrast),"minimum":min(contrast) if contrast else None})
                            ticks=page.locator("#repurchase svg text").evaluate_all(
                                "xs=>xs.map(x=>x.textContent).filter(t=>/^\\d+[,.]?\\d*%$/.test(t)).map(t=>Number(t.replace('%','').replace(',','.')))")
                            check(prefix+"/percentage axis", bool(ticks) and max(ticks)<=100 and min(ticks)>=0,ticks)
                        clipping = page.locator("#dashboard svg.chart").evaluate_all(
                            """xs=>xs.flatMap(s=>Array.from(s.querySelectorAll('text')).map(t=>{
                            let b=t.getBoundingClientRect(),r=s.getBoundingClientRect();
                            return (b.left<r.left-2||b.right>r.right+2||b.top<r.top-2||b.bottom>r.bottom+2)
                            ?{chart:s.getAttribute('aria-label'),text:t.textContent}:null
                            }).filter(Boolean))""")
                        check(prefix+"/text in SVG", not clipping, clipping)
                        image = out / (f"{width}x{height}-{name}.png")
                        page.screenshot(path=str(image), full_page=True, animations="disabled")
                        screenshots.append({"file": image.name, "sha256": hashlib.sha256(image.read_bytes()).hexdigest()})
                        if width != 1440:
                            continue
                        if not FLEET:
                            check(prefix+"/grain", page.locator("select[name=channel]").is_disabled() == (name=="clientes")
                                  and page.locator("select[name=category]").is_disabled() == (name!="clientes"))
                        for button in page.locator("#dashboard [data-png]").all():
                            chart_id = button.get_attribute("data-png")
                            dims = page.locator(f"#{chart_id} svg").evaluate(
                                "s=>[s.viewBox.baseVal.width*2,s.viewBox.baseVal.height*2]")
                            with page.expect_download(timeout=15000) as d:
                                button.click()
                            path = out / f"{name}-{chart_id}-export.png"
                            d.value.save_as(str(path))
                            buf = path.read_bytes()
                            valid = (buf[:8] == b"\x89PNG\r\n\x1a\n" and len(buf)>24
                                     and list(struct.unpack(">II", buf[16:24])) == dims)
                            check(prefix+"/PNG/"+chart_id, valid, {"bytes": len(buf), "dims": dims})
                        with page.expect_download(timeout=15000) as d:
                            page.locator("#export").click()
                        path = out / f"{name}-export.csv"
                        d.value.save_as(str(path))
                        records = list(csv.reader(io.StringIO(path.read_text(encoding="utf-8-sig")), delimiter=";"))
                        check(prefix+"/CSV", len(records)>1 and all(len(x)==len(records[0]) for x in records))
                        key = FILTERS[name]
                        target = page.locator("#dashboard [data-asset]").first
                        value = target.get_attribute("data-asset")
                        target.focus()
                        page.keyboard.press("Enter")
                        check(prefix+"/keyboard filter", page.locator(f"[name={key}]").input_value()==value)
                        page.locator("#reset").click()
                        check(prefix+"/reset", page.locator(f"[name={key}]").input_value()=="")
                        target = page.locator("#dashboard [data-asset]").first
                        value = target.get_attribute("data-asset")
                        target.locator("rect,circle").first.click()
                        check(prefix+"/pointer filter", page.locator(f"[name={key}]").input_value()==value)
                        next_name = next(x for x in PAGES if x != name)
                        page.locator(f"#navigation a[data-page='{next_name}']").click()
                        page.locator(f"#navigation a[data-page='{next_name}'][aria-current='page']").wait_for()
                        page.locator(f"#navigation a[data-page='{name}']").click()
                        page.locator(f"#navigation a[data-page='{name}'][aria-current='page']").wait_for()
                        check(prefix+"/filter persistence", page.locator(f"[name={key}]").input_value()==value)
                        page.locator("#reset").click()
                        page.locator("[name=start]").fill("2026-09-30")
                        page.locator("[name=end]").fill("2025-10-01")
                        check(prefix+"/empty context", page.locator("#dashboard .empty").count()==1
                              and page.locator("#export").is_disabled())
                        page.locator("#reset").click()
                    except Exception as exc:
                        check(prefix+"/exception", False, str(exc))
                        page.reload()
                        page.locator("#navigation a").first.wait_for(timeout=30000)
                        page.locator("#reset").click()
                check(f"{width}x{height}/console", not errors, errors)
                context.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    result = {"lab": LAB, "browser": version, "checks": checks,
              "screenshots": screenshots, "pass": all(x["pass"] for x in checks)}
    (out/"browser-validation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{LAB}: {sum(x['pass'] for x in checks)}/{len(checks)} PASS")
    return 0 if result["pass"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
