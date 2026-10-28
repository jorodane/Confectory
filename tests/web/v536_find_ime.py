"""Placed search keyboard/IME ownership; controlled renderer, no domain/provider calls."""
import http.server,json,pathlib,sys,tempfile,threading
from playwright.sync_api import sync_playwright,expect
repo=pathlib.Path(sys.argv[1]).resolve();out=pathlib.Path(tempfile.mkdtemp(prefix='confectory-find-ime-'));errors=[]
class Handler(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(repo),**kw)
 def log_message(self,*a):pass
 def do_GET(self):
  if self.path=='/fixture':
   self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.end_headers();self.wfile.write('<main id="workspace" tabindex="0"><article>한글 첫 노드</article><article>한글 두 번째 노드</article></main>'.encode())
  else:super().do_GET()
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.goto('http://127.0.0.1:'+str(server.server_port)+'/fixture')
  page.evaluate('''async()=>{const {createPlacedTextFind}=await import('/examples/editor-home/ui/find.js'),host=document.querySelector('main');globalThis.focused=[];globalThis.valid=true;const context={key:'owned',title:'수용 찾기',host,isCurrent:()=>valid,items:()=>[...host.children].map((element,id)=>({id,element})),focus:item=>focused.push(item.id)};globalThis.finder=createPlacedTextFind({context:()=>context});finder.open();}''')
  panel=page.get_by_role('dialog',name='수용 찾기');field=panel.get_by_role('searchbox');field.fill('한글');expect(panel.locator('[data-find-count]')).to_have_text('1 / 2')
  before=page.evaluate('focused.length')
  for key,code,composing in [('Enter',13,True),('Escape',27,True),('Enter',229,False),('Escape',229,False)]:
   prevented=field.evaluate('(el,args)=>{const e=new KeyboardEvent("keydown",{key:args[0],keyCode:args[1],isComposing:args[2],bubbles:true,cancelable:true});el.dispatchEvent(e);return e.defaultPrevented}',[key,code,composing])
   expect(panel).to_be_visible();expect(field).to_have_value('한글');expect(panel.locator('[data-find-count]')).to_have_text('1 / 2');assert page.evaluate('focused.length')==before and not prevented
  print('PASS composition Enter/Escape and legacy229 preserve Korean query, current result and search overlay without navigation',flush=True)
  field.press('Enter');expect(panel.locator('[data-find-count]')).to_have_text('2 / 2');field.press('Shift+Enter');expect(panel.locator('[data-find-count]')).to_have_text('1 / 2');field.press('Escape');expect(panel).to_have_count(0);assert page.locator('#workspace').evaluate('e=>document.activeElement===e')
  page.locator('#workspace').press('Control+f');expect(panel).to_be_visible();expect(panel.get_by_role('searchbox')).to_have_value('');page.evaluate('valid=false;document.querySelector("main").append(document.createElement("span"))');expect(panel).to_have_count(0);assert not errors,errors
  print('PASS ordinary Enter/Shift+Enter/Escape/Ctrl+F remain scoped and retired context removes its overlay',flush=True)
  page.screenshot(path=str(out/'find-ime.png'));browser.close()
finally:server.shutdown()
print(json.dumps({'evidence':str(out),'controlledRenderer':True,'nativeIME':False,'actualBackend':False,'errors':errors}))
