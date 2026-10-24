"""Original v536 own-function heading/pin geometry; static, not native QA."""
import http.server
import json
import pathlib
import re
import sys
import tempfile
import threading
import zipfile
from playwright.sync_api import sync_playwright

repo = pathlib.Path(sys.argv[1]).resolve()
case = pathlib.Path(tempfile.mkdtemp(prefix='confectory-function-order-visual-'))
with zipfile.ZipFile(repo / 'reference/site-ui/Confectory-Editor-Prototype-v536.zip') as z:
    source = z.read('Confectory-v536/dist/app.js').decode()
    original_css = z.read('Confectory-v536/dist/style.css').decode()


def function(name):
    start = source.index('function ' + name + '(')
    end = source.find('\nfunction ', start + 1)
    return source[start:end]


functions = '\n'.join(function(name) for name in ['functionGearIcon', 'functionIconMarkup', 'receivedFunctionName', 'functionPinContourMarkup', 'functionPinsMarkup', 'functionFlowMarkup', 'functionWritingActionsMarkup', 'functionCollapseToggleMarkup', 'functionNodeMarkup'])
styles = re.sub(r'@import\s+url\([^)]*\)\s*;', '', '\n'.join((repo / 'examples/editor-home/ui' / n).read_text() for n in ['style.css', 'consumer.css', 'runtime.css']))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kw):
        super().__init__(*args, directory=str(repo), **kw)

    def log_message(self, *args):
        pass


server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
try:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1100, 'height': 800})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto('http://127.0.0.1:' + str(server.server_port))
        page.set_content('<style></style><div id="workspace"><section class="window" style="left:40px;top:40px;width:460px;height:680px"><div class="window-body"><section class="object-functions"><div class="own-function-list"><div class="inline-function-row function-node" data-inline-method="own"></div></div></section></div></section></div>')
        page.locator('style').evaluate('(el,css)=>el.textContent=css', original_css)
        page.add_script_tag(content='''const $=(s,r=document)=>r.querySelector(s),esc=v=>String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('"','&quot;');const profileIconMarkup=esc,blueprintIsAsync=()=>false,blueprintClockMarkup=()=>'',blueprintIsComplete=()=>false,functionSignatureFields=(m,side)=>m[side]||[],propertyTypeSummary=f=>f.type,functionPinColor=()=> '#73dca4';const method={id:'own',name:'한글 기능',description:'기존 설명과 함수 식별성',inputs:[{name:'amount',type:'정수'},{name:'count',type:'정수'}],outputs:[{name:'count',type:'정수'},{name:'결과',type:'정수'}]};''' + functions + "\ndocument.querySelector('[data-inline-method]').innerHTML=functionNodeMarkup(method);")
        selectors = [':scope', '.function-node-heading', '[data-inline-name]', '.function-node-symbol', '[data-function-toggle]', '[data-function-delete]', '.function-node-flow', '[data-pin-side=inputs]', '[data-pin-side=outputs]', '.function-node-description', '.function-node-writing-actions', '[data-function-write-description]', '[data-function-write-direct]']
        measure = '''selectors=>selectors.map(selector=>{const root=document.querySelector('[data-inline-method]'),el=selector===':scope'?root:root.querySelector(selector),r=el.getBoundingClientRect(),b=root.getBoundingClientRect();return {selector,x:r.x-b.x,y:r.y-b.y,width:r.width,height:r.height,color:getComputedStyle(el).color}})'''
        before = page.evaluate(measure, selectors)
        page.screenshot(path=str(case / 'original.png'))
        page.locator('style').evaluate('(el,css)=>el.textContent=css', styles)
        page.evaluate('''async()=>{const {createFunctionPresentation}=await import('/examples/editor-home/ui/element-functions.js');document.querySelector('[data-inline-method]').innerHTML=createFunctionPresentation({$,esc,name:id=>id}).functionNodeMarkup(method);}''')
        after = page.evaluate(measure, selectors)
        page.screenshot(path=str(case / 'adapted.png'))
        assert not errors, errors
        assert before == after, {'before': before, 'after': after, 'evidence': str(case)}
        assert page.locator('.function-node-heading').get_attribute('draggable') == 'true'
        assert page.locator('.function-node-heading').get_attribute('title') == '끌어서 기능 순서 바꾸기 · Alt+↑/↓'
        (case / 'comparison.json').write_text(json.dumps({'original': before, 'adapted': after, 'pageErrors': errors, 'scope': 'same own function original v536 geometry/colors; no native/engine persistence proof'}, ensure_ascii=False, indent=2))
        print(json.dumps({'pass': True, 'rectangles': len(selectors), 'evidence': str(case)}))
        browser.close()
finally:
    server.shutdown()
