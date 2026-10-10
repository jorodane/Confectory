"""Actual EditorHome WASM connection selection/settings; no model or command injection."""
import http.server,json,pathlib,sys,threading
from playwright.sync_api import sync_playwright
report=json.load(open(sys.argv[1]));site=pathlib.Path(report['output'])/'site'
assert report['entry']=='Confectory.EditorHome::Main' and report['tool']['ok']
class Static(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(site),**kw)
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Static);threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page(viewport={'width':1200,'height':1050});errors=[]
  page.add_init_script("window.uiLabels={};const original=CanvasRenderingContext2D.prototype.fillText;CanvasRenderingContext2D.prototype.fillText=function(text,x,y,...args){uiLabels[String(text)]={x,y,time:performance.now()};return original.call(this,text,x,y,...args);};")
  page.on('pageerror',lambda e:errors.append(str(e)))
  def click(text):
   try:page.wait_for_function('(s)=>uiLabels[s]&&performance.now()-uiLabels[s].time<500',arg=text)
   except Exception:
    print(page.evaluate('uiLabels'),flush=True);page.screenshot(path='/tmp/confectory-ai-browser-connections-failure.png');raise
   point=page.evaluate('(s)=>uiLabels[s]',text);page.mouse.click(point['x']+12,point['y']+8);page.wait_for_timeout(200)
  def field(i):return page.locator('[data-control="'+str(i)+'"]:visible')
  page.goto('http://127.0.0.1:'+str(server.server_port),wait_until='networkidle');click('Agent connection');click('Confectory.Agent.Responses::Connection');field(89).wait_for(state='visible')
  assert field(88).input_value()=='["credentialReference"]'
  field(89).fill('env:CONFECTORY_AI_BROWSER_FIXTURE');click('Set value');click('Refresh');field(88).wait_for(state='visible')
  field(88).fill('["model"]');field(89).fill('explicit-browser-fixture-model');click('Set value');click('Source');field(54).wait_for(state='visible');assert 'explicit-browser-fixture-model' in field(54).input_value()
  page.screenshot(path='/tmp/confectory-ai-browser-responses-settings.png');click('AI settings: Confectory.Agent.Responses::Connection  - Menu');click('Hide project');click('Agent  unbound');click('Confectory.Agent.Codex::Connection');field(89).wait_for(state='visible')
  # Existing Properties navigation supplies fields from the selected inherited schema.
  assert field(88).input_value()=='["credentialReference"]';click('Next');assert field(88).input_value()=='["executable"]';click('Next');assert field(88).input_value()=='["managedHome"]'
  page.screenshot(path='/tmp/confectory-ai-browser-codex-settings.png')
  field(38).fill('Browser scoped draft');click('Helper  0');click('Create Main Helper');click('main-helper | global')
  click('Remember draft in project');page.wait_for_function('(s)=>uiLabels[s]&&performance.now()-uiLabels[s].time<500',arg='Current project memories: 1 | Common included: 0')
  click('Remember draft as common');click('Common memory: excluded');page.wait_for_function('(s)=>uiLabels[s]&&performance.now()-uiLabels[s].time<500',arg='Current project memories: 1 | Common included: 1')
  click('Common memory: allowed');page.wait_for_function('(s)=>uiLabels[s]&&performance.now()-uiLabels[s].time<500',arg='Current project memories: 1 | Common included: 0')
  page.screenshot(path='/tmp/confectory-ai-browser-helper-scope.png');click('Close menu');field(89).wait_for(state='visible')
  click('Agent  unbound');click('Confectory.Agent.Responses::Connection');click('Review current message')
  field(53).wait_for(state='visible');assert 'credential relay' in field(53).input_value() and 'permissionPolicy' in field(53).input_value()
  click('Cancel permission review');field(89).wait_for(state='visible')

  click('Helper  1');click('main-helper | global');field(310).fill('Only the selected Helper message');click('Review Helper message')
  field(53).wait_for(state='visible');preview=json.loads(field(53).input_value());assert preview['message']=='Only the selected Helper message' and preview['helperContext']['helper']=='main-helper'
  click('Cancel permission review');field(89).wait_for(state='visible')

  retired=field(89).get_attribute('data-binding');assert retired
  click('AI settings: Confectory.Agent.Codex::Connection  - Menu');click('Close project')
  page.wait_for_function('(binding)=>!Array.from(document.querySelectorAll("[data-binding]")).some(el=>el.getAttribute("data-binding")===binding)',arg=retired)
  click('Agent  unbound');click('Confectory.Agent.Codex::Connection');field(89).wait_for(state='visible')
  assert field(89).get_attribute('data-binding')!=retired
  assert not errors,errors
  browser.close();print('Actual EditorHome browser connection choices / declared Properties / typed draft / Codex fields / real local scoped Helper controls / close binding retirement and reopen; no authentication/model call PASS')
finally:server.shutdown()
