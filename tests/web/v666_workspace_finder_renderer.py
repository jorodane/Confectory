"""Controlled browser ownership/IME/private-field guards, not a native authority test."""
import http.server,json,pathlib,sys,tempfile,threading
from playwright.sync_api import sync_playwright,expect
repo=pathlib.Path(sys.argv[1]).resolve();out=pathlib.Path(tempfile.mkdtemp(prefix='confectory-finder-renderer-'));errors=[]
class Handler(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(repo),**kw)
 def log_message(self,*a):pass
 def do_GET(self):
  if self.path=='/fixture':
   self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.end_headers();self.wfile.write('''<link rel="stylesheet" href="/examples/editor-home/ui/style.css"><main id="workspace" style="width:1100px;height:700px"><div class="window" id="node" style="position:relative;width:500px;height:160px"><header class="window-title"><span class="caption"><strong>창 한글</strong></span></header><div>VisibleNeedle</div><input value="PrivateCurrentValue"><input type="password" value="SecretPasswordNever"><input name="api-token" value="SecretTokenNever"><div hidden><input value="HiddenInputNever"></div><div aria-hidden="true"><input value="AriaHiddenNever"></div></div><div class="bubble-dock"><button id="worker-finder-bubble" aria-expanded="false">검색</button></div></main>'''.encode())
  else:super().do_GET()
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright()as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page(viewport=dict(width=1440,height=1000));page.on('pageerror',lambda e:errors.append(str(e)));page.goto('http://127.0.0.1:'+str(server.server_port)+'/fixture')
  page.evaluate('''async()=>{const {createPlacedTextFind}=await import('/examples/editor-home/ui/find.js'),{createWorkspaceFinder}=await import('/examples/editor-home/ui/workspace-finder.js');const placed=createPlacedTextFind({context:()=>null}),host=document.querySelector('main'),anchor=document.querySelector('#worker-finder-bubble'),element=document.querySelector('#node');globalThis.scope='A';globalThis.ready=true;globalThis.rows=[{id:'A::Same',name:'Same',kind:'function',owned:true},{id:'B::Same',name:'Same',kind:'schema',owned:false}];globalThis.calls=[];globalThis.finder=createWorkspaceFinder({context:()=>scope?{key:scope,host,anchor}:null,ready:()=>ready,beforeOpen:()=>placed.close(),nodes:()=>[{key:'node',el:element,placed:true,kind:'window'}],windows:()=>[],objects:()=>rows,text:el=>placed.text(el),decorationName:()=>'',openObject:id=>calls.push(id),focusNode:key=>calls.push(key)});anchor.onclick=()=>finder.open();finder.open();}''')
  panel=page.locator('#workspace-find-panel');field=panel.get_by_role('searchbox');buttons=panel.locator('.workspace-find-result')
  field.fill('Same');expect(buttons).to_have_count(2);buttons.nth(1).click();assert page.evaluate('calls')==['B::Same'];print('PASS equal display names retain exact permitted projection IDs, never positional identity',flush=True)
  page.locator('#worker-finder-bubble').click();panel.locator('[data-find-mode="text"]').click()
  for text,count in [('VisibleNeedle',1),('PrivateCurrentValue',1),('SecretPasswordNever',0),('SecretTokenNever',0),('HiddenInputNever',0),('AriaHiddenNever',0)]:
   field.fill(text);print('CHECK field guard '+text,flush=True);(out/'field-guard.json').write_text(json.dumps(dict(query=text,expected=count)));expect(buttons).to_have_count(count)
  print('PASS text uses existing visible private inputs while excluding secret/password/hidden/aria-hidden fields',flush=True)
  panel.locator('[data-find-mode="elements"]').click();field.fill('Same');page.evaluate('()=>{globalThis.oldResult=document.querySelectorAll(".workspace-find-result")[1];rows=rows.slice(0,1);oldResult.click()}');assert page.evaluate('calls')==['B::Same'];expect(buttons).to_have_count(1);print('PASS result removed from current permission-filtered projection is revalidated before activation',flush=True)
  page.evaluate('()=>{ready=false;finder.update()}');expect(buttons).to_be_disabled();page.evaluate('()=>{oldResult.click();ready=true;finder.update()}');expect(buttons).to_be_enabled();assert page.evaluate('calls')==['B::Same']
  for key,code,composing in [('Enter',13,True),('Escape',27,True),('Enter',229,False),('Escape',229,False)]:
   prevented=field.evaluate('(el,args)=>{const e=new KeyboardEvent("keydown",{key:args[0],keyCode:args[1],isComposing:args[2],bubbles:true,cancelable:true});el.dispatchEvent(e);return e.defaultPrevented}',[key,code,composing]);assert not prevented;expect(panel).to_be_visible()
  page.evaluate('()=>{globalThis.staleResult=document.querySelector(".workspace-find-result");scope="B";staleResult.click();finder.update()}');expect(panel).to_have_count(0);assert page.evaluate('calls')==['B::Same'];page.locator('#worker-finder-bubble').click();expect(field).to_have_value('');field.press('Escape');expect(panel).to_have_count(0);print('PASS busy, IME and stale project callbacks preserve inputs and cannot navigate; reentry has no old query',flush=True)
  assert not errors,errors;page.screenshot(path=str(out/'finder-guards.png'));page.close();browser.close()
finally:server.shutdown();server.server_close()
print('FINDER_RENDERER',out,flush=True)
