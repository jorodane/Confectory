"""Actual EditorHome UI create/edit/Save/reload/export; unmodified generated product."""
import base64,http.server,io,json,pathlib,sys,tempfile,threading,zipfile
from playwright.sync_api import sync_playwright,expect
report=json.load(open(sys.argv[1]));site=pathlib.Path(report['output'])/'site'
assert report['entry']=='Confectory.EditorHome::Main';assert report['tool']['ok']
class Static(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(site),**kw)
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Static);threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page(viewport={'width':1200,'height':850},accept_downloads=True);errors=[];requests=[]
  # Passive observation of the actual canvas labels: original renderer remains invoked.
  page.add_init_script("window.drawnLabels=[];const draw=CanvasRenderingContext2D.prototype.fillText;CanvasRenderingContext2D.prototype.fillText=function(text,...args){drawnLabels.push(String(text));if(drawnLabels.length>2048)drawnLabels.splice(0,1024);return draw.call(this,text,...args);};")
  page.on('console',lambda m:print(m.type,m.text,flush=True));page.on('pageerror',lambda e:(errors.append(str(e)),print('PAGEERROR',e.stack,flush=True)));page.on('request',lambda r:requests.append((r.method,r.url)))
  def click(x,y):
   before=page.evaluate('confectoryPlatform.presented');page.mouse.click(x,y);page.wait_for_function('(n)=>confectoryPlatform.presented>n+1',arg=before)
  def ready():
   page.wait_for_function('globalThis.confectoryPlatform?.loops.size>0');page.wait_for_timeout(2100);click(600,510)
  def files():return json.loads(page.evaluate('confectoryPlatform.bridge.ExportStorage()'))
  page.goto('http://127.0.0.1:'+str(server.server_port));ready();click(275,164)
  name=page.locator('input[data-control="10"]');name.wait_for(state='visible');name.fill('WorkspaceActual');page.locator('textarea[data-control="11"]').fill('actual reusable workspace 한글')
  click(360,462);page.wait_for_function("drawnLabels.some(s=>s==='Edit sources')");click(1106,100)
  editor=page.locator('textarea[data-control="54"]');editor.wait_for(state='visible');initial=editor.input_value();assert initial.strip()
  originals=files();bodies={k:v for k,v in originals.items() if k.endswith('/main.csbody')};assert len(bodies)==1,bodies
  body_path,original_body=next(iter(bodies.items()));assert base64.b64decode(original_body).decode()==initial
  edited='// actual browser workspace 한글 😀\nreturn 17;\n';editor.fill(edited);page.evaluate('window.ownedEditor=document.querySelector("textarea[data-control=\\"54\\"]");window.drawnLabels=[]')
  click(378,92);page.wait_for_function("drawnLabels.some(s=>s.includes('Local source draft saved; final sources unchanged'))")
  assert page.evaluate('window.ownedEditor===document.querySelector("textarea[data-control=\\"54\\"]")');expect(editor).to_have_value(edited)
  assert files()[body_path]==original_body,'Save draft changed final source without Confirm'
  click(270,30);click(270,236);click(800,174);click(1106,100);editor.wait_for(state='visible');expect(editor).to_have_value(edited)
  page.evaluate('window.narrowEditor=document.querySelector(`textarea[data-control="54"]`)');page.set_viewport_size({'width':480,'height':850});page.wait_for_timeout(250)
  expect(editor).to_be_visible();expect(editor).to_have_value(edited);assert page.evaluate('window.narrowEditor===document.querySelector(`textarea[data-control="54"]`)')
  bounds=editor.bounding_box();assert bounds and bounds['x']>=0 and bounds['y']>=180 and bounds['x']+bounds['width']<=480 and bounds['height']>100,bounds
  page.evaluate('window.drawnLabels=[]');click(221,128);page.wait_for_function("drawnLabels.some(s=>s.includes('Local source draft saved; final sources unchanged'))")
  assert page.evaluate('window.narrowEditor===document.querySelector(`textarea[data-control="54"]`)');expect(editor).to_have_value(edited);assert files()[body_path]==original_body
  page.set_viewport_size({'width':1200,'height':850});page.wait_for_timeout(250)
  page.reload();ready();click(800,174);click(1106,100);editor.wait_for(state='visible');expect(editor).to_have_value(edited)
  assert files()[body_path]==original_body
  with page.expect_download() as transfer:click(502,92)
  download=transfer.value;assert download.failure() is None
  with zipfile.ZipFile(download.path()) as archive:
   members=archive.namelist();body=next(k for k in members if k.endswith('main.csbody'));assert archive.read(body).decode()==edited
   manifest=next(k for k in members if k.endswith('project.cproj'));assert 'WorkspaceActual' in archive.read(manifest).decode()
   assert any('ProjectInfo' in archive.read(k).decode() for k in members if k.endswith('.celem'))
  assert files()[body_path]==original_body
  assert not errors,errors;assert any(url.endswith('.wasm') for _,url in requests);assert all(method=='GET' and '/api/' not in url for method,url in requests)
  assert page.evaluate('confectoryPlatform.bridge.Close()');browser.close()
  print('PASS actual EditorHome UI create/edit/stable field/Save acknowledged/leave/reopen/480px resize/narrow Save/reload/ZIP export; final source unchanged, static GET-only WASM')
finally:server.shutdown()
