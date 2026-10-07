"""Actual same editor ProjectPack: static browser runtime, common Canvas layout and native-field editing."""
import http.server,threading,json,pathlib,sys
from playwright.sync_api import sync_playwright
report=json.load(open(sys.argv[1]));site=pathlib.Path(report['output'])/'site'
class S(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(site),**k)
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),S);threading.Thread(target=server.serve_forever,daemon=True).start()
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=b.new_page(viewport={'width':1200,'height':850});errors=[];network=[];page.on('console',lambda m:print(m.type,m.text));page.on('pageerror',lambda e:(errors.append(str(e)),print('PAGEERROR',e)));page.on('request',lambda r:network.append((r.method,r.url)));page.goto('http://127.0.0.1:'+str(server.server_port));page.wait_for_function('globalThis.confectoryPlatform?.loops.size>0');page.wait_for_timeout(2100);page.screenshot(path='/tmp/confectory-same-editor-first.png');page.mouse.click(600,510);page.wait_for_timeout(500);page.mouse.click(275,164);page.wait_for_selector('input[data-control="10"]:visible');page.locator('input[data-control="10"]').fill('BrowserActual');page.locator('textarea[data-control="11"]').fill('actual common layout draft');page.wait_for_timeout(150);assert page.locator('input[data-control="10"]').input_value()=='BrowserActual';page.screenshot(path='/tmp/confectory-same-editor-create.png');print('PASS actual editor startup render New text editing');page.evaluate('confectoryPlatform.bridge.Close()');page.wait_for_timeout(100);assert page.locator('#fields input').count()==0;print('PASS close owner cleanup');assert not errors,errors;assert any(url.endswith('.wasm') for _,url in network);assert all(method=='GET' and '/api/' not in url for method,url in network);b.close()
server.shutdown()
