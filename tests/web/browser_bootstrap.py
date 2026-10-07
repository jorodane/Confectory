"""Real Chromium verifies a neutral generated entry using static installed target resources."""
import http.server,json,pathlib,sys,threading
from playwright.sync_api import sync_playwright
report=json.load(open(sys.argv[1]));site=pathlib.Path(report['output'])/'site'
class Static(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(site),**kwargs)
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Static);threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page();errors=[];requests=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:requests.append((r.method,r.url)));page.goto('http://127.0.0.1:'+str(server.server_port));page.wait_for_function('globalThis.confectoryPlatform?.result === 0');assert page.evaluate('confectoryPlatform.hosts.size')==0;assert page.evaluate('confectoryPlatform.loops.size')==0;assert not errors,errors;assert any(url.endswith('.wasm') for _,url in requests);assert all(method=='GET' and '/api/' not in url for method,url in requests);print('PASS neutral actual entry',report['entry'],'static WASM, no Home model owner/snapshot requirement');browser.close()
finally:server.shutdown()
