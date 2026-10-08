"""Same generated EditorHome: actual folder import, draft edit, IndexedDB commit and reload."""
import http.server,json,pathlib,sys,tempfile,threading
from playwright.sync_api import sync_playwright,expect
report=json.load(open(sys.argv[1]));site=pathlib.Path(report['output'])/'site'
assert report['entry']=='Confectory.EditorHome::Main'
class Static(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(site),**kw)
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Static);threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with tempfile.TemporaryDirectory() as tmp,sync_playwright() as p:
  folder=pathlib.Path(tmp)/'PersistentProduct';folder.mkdir();(folder/'project.cproj').write_text('project PersistentProduct version "1" { standalone true; entry PersistentProduct::Main; }')
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page(viewport={'width':1200,'height':850});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto('http://127.0.0.1:'+str(server.server_port));page.wait_for_function('globalThis.confectoryPlatform?.loops.size>0');page.wait_for_timeout(2100)
  page.mouse.click(600,510);page.wait_for_timeout(150)
  with page.expect_file_chooser() as chooser:page.mouse.click(540,164)
  chooser.value.set_files(str(folder));chat=page.locator('textarea[data-control="38"]');chat.wait_for(state='visible');chat.fill('durable actual draft 한글 😀');page.wait_for_timeout(500)
  page.mouse.click(270,30);page.wait_for_timeout(100);page.mouse.click(270,236);page.wait_for_timeout(200)
  page.evaluate("()=>{window.storageHost=[...confectoryPlatform.hosts.keys()][0];confectoryPlatform.request('native',JSON.stringify({host:storageHost,operation:'storage-flush',payload:'{}'}));}")
  page.wait_for_function("()=>{const s=JSON.parse(confectoryPlatform.request('native',JSON.stringify({host:storageHost,operation:'storage-poll',payload:'{}'})));if(s.state==='error')throw Error(s.error);return s.state==='saved';}");assert page.evaluate('confectoryPlatform.storage.error') is None
  saved=page.evaluate('confectoryPlatform.bridge.ExportStorage()');assert 'PersistentProduct' in saved
  page.reload();page.wait_for_function('globalThis.confectoryPlatform?.loops.size>0');page.wait_for_timeout(2100)
  restored=page.evaluate('confectoryPlatform.bridge.ExportStorage()');assert json.loads(saved)==json.loads(restored)
  page.mouse.click(600,510);page.wait_for_timeout(150);page.mouse.click(800,174);chat.wait_for(state='visible');expect(chat).to_have_value('')
  assert not errors,errors;assert page.evaluate('confectoryPlatform.storage.error') is None
  print('PASS actual EditorHome import/edit/committed IndexedDB/reload/recent reopen/runtime-only chat scope; unmodified generated output');browser.close()
finally:server.shutdown()
