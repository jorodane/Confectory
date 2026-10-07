"""Actual Chromium loads static independent WASM output; no .NET backend process."""
import contextlib, http.server, json, os, pathlib, re, tempfile, threading
from playwright.sync_api import sync_playwright, expect
import sys
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());site=pathlib.Path(report['output'])/'site'
assert (site/'_framework/dotnet.js').is_file() and list(site.rglob('*.wasm'))
requests=[]
class Static(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(site),**kwargs)
 def log_message(self,*args):pass
 def do_GET(self):requests.append(('GET',self.path));super().do_GET()
 def do_POST(self):requests.append(('POST',self.path));self.send_error(405)
with tempfile.TemporaryDirectory(prefix='confectory-wasm-browser-') as temporary:
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Static);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
 origin=f'http://127.0.0.1:{server.server_port}/'
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-gpu'])
   page=browser.new_page(viewport={'width':1200,'height':850});errors=[];network=[];page.on('request',lambda request:network.append((request.method,request.url)));page.on('pageerror',lambda e:errors.append(str(e)))
   page.goto(origin);page.get_by_role('status').filter(has_text='Ready').wait_for()
   assert page.get_by_role('heading',name='Confectory',exact=True).is_visible()
   capabilities=page.evaluate("async()=>{const {browserBridge}=await import('./app.js');return JSON.parse(browserBridge.Request('capabilities','{}'));}");assert capabilities['runtime']=='independent-browser-wasm' and not capabilities['backendRequired']
   bad={'name':'broken.cproj','mimeType':'text/plain','buffer':b'not a pack'}
   page.locator('#file').set_input_files(bad);expect(page.locator('#status')).to_contain_text(re.compile('expected|error',re.I))
   assert page.locator('#project').is_hidden()
   pack={'name':'한글 공백 프로젝트.cproj','mimeType':'text/plain','buffer':b'project BrowserUser version "1" { standalone true; entry BrowserUser::Main; registry Untrusted "DO_NOT_EXECUTE"; target web Untrusted::Build; }'}
   page.locator('#file').set_input_files(pack);page.locator('#project').wait_for(state='visible');assert page.locator('#title').inner_text()=='BrowserUser'
   assert 'standalone declaration: true' in page.locator('#capabilities').inner_text()
   assert 'DO_NOT_EXECUTE' in page.locator('#source').input_value()
   page.evaluate("window.initialProjectCard=document.querySelector('.card');window.initialSourceField=document.querySelector('#source');")
   page.locator('#chat').click();page.keyboard.type('keyboard input',delay=3);assert page.locator('#chat').input_value()=='keyboard input'
   page.locator('#chat').fill('미제출 draft');page.locator('#source').fill(page.locator('#source').input_value()+'\n// browser edit')
   page.locator('#file').set_input_files(pack);expect(page.locator('#status')).to_contain_text('Already open')
   assert page.locator('#chat').input_value()=='미제출 draft' and '// browser edit' in page.locator('#source').input_value()
   assert page.evaluate("window.initialProjectCard===document.querySelector('.card') && window.initialSourceField===document.querySelector('#source')")
   other={'name':'library.cpack','mimeType':'text/plain','buffer':b'pack SharedLibrary version "1" { standalone false; }'}
   page.locator('#file').set_input_files(other);expect(page.locator('#status')).to_contain_text('Leave the current')
   assert page.locator('#title').inner_text()=='BrowserUser' and page.locator('#chat').input_value()=='미제출 draft'
   with page.expect_file_chooser() as chooser:page.locator('#file').click()
   chooser.value.set_files([]);assert page.locator('#chat').input_value()=='미제출 draft'
   page.once('dialog',lambda dialog:dialog.dismiss());page.locator('#leave').click();assert page.locator('#project').is_visible()
   with page.expect_download() as pending:page.locator('#download').click()
   download=pending.value;download.save_as(str(pathlib.Path(temporary)/'download.cproj'));assert '// browser edit' in pathlib.Path(download.path()).read_text()
   assert 'Unsaved changes' in page.locator('#dirty').inner_text(),'download initiation must not claim durable save'
   page.once('dialog',lambda dialog:dialog.accept());page.locator('#leave').click();page.locator('#project').wait_for(state='hidden')
   page.locator('#file').set_input_files(other);page.locator('#project').wait_for(state='visible');assert page.locator('#title').inner_text()=='SharedLibrary'
   assert 'standalone declaration: false' in page.locator('#capabilities').inner_text()
   # A clean active project also prevents replacement; no dirty-state prerequisite.
   page.locator('#file').set_input_files(pack);expect(page.locator('#status')).to_contain_text('Leave the current')
   assert page.locator('#title').inner_text()=='SharedLibrary'
   page.locator('#leave').click();page.locator('#project').wait_for(state='hidden');page.locator('#file').set_input_files(pack);page.locator('#project').wait_for(state='visible')
   assert page.locator('#chat').input_value()=='미제출 draft' and '// browser edit' in page.locator('#source').input_value(),'explicit Leave/reopen lost retained session drafts'
   page.set_viewport_size({'width':390,'height':844});assert page.locator('#source').bounding_box()['width']<390
   page.screenshot(path=os.environ.get('CONFECTORY_BROWSER_SCREENSHOT',str(pathlib.Path(temporary)/'browser.png')));assert not errors,errors
   # Direct WASM bridge refuses unsupported commands without an HTTP API.
   unsupported=page.evaluate("async () => { const { browserBridge }=await import('./app.js'); return browserBridge.Request('run','{}'); }");assert 'does not expose' in unsupported
   closed=page.evaluate("async()=>{const {browserBridge}=await import('./app.js');browserBridge.Close();browserBridge.Close();return JSON.parse(browserBridge.Request('snapshot','{}'));}");assert 'error' in closed
   page.reload();expect(page.locator('#status')).to_contain_text('Ready');assert page.locator('#project').is_hidden() and page.locator('#cards').inner_text()==''
   assert all(method=='GET' and url.startswith(origin) for method,url in network),network
   browser.close()
  assert not any(method!='GET' or path.startswith('/api/') for method,path in requests),requests
  assert any('.wasm' in path for _,path in requests),'No actual WASM runtime fetched'
  print('Independent Chromium WASM PASS: static-only startup/render/input/import/repeat/cancel/unsaved/clean-active guard/leave/reopen/download; no .NET backend or API')
 finally:server.shutdown();server.server_close();thread.join(timeout=5)
