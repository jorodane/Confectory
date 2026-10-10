"""Same actual Main: browser pointer fold/drag and native DOM draft retention."""
import http.server,json,pathlib,sys,threading
from playwright.sync_api import sync_playwright,expect
report=json.load(open(sys.argv[1]));site=pathlib.Path(report['output'])/'site'
assert report['entry']=='Confectory.EditorHome::Main' and report['tool']['ok']
class Static(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(site),**kw)
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Static);threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page(viewport={'width':1200,'height':1050});errors=[]
  page.add_init_script('window.uiLabels={};const original=CanvasRenderingContext2D.prototype.fillText;CanvasRenderingContext2D.prototype.fillText=function(text,x,y,...args){uiLabels[String(text)]={x,y,time:performance.now()};return original.call(this,text,x,y,...args);};')
  page.on('pageerror',lambda e:errors.append(str(e)))
  def point(text):
   page.wait_for_function('(s)=>uiLabels[s]&&performance.now()-uiLabels[s].time<500',arg=text)
   return page.evaluate('(s)=>uiLabels[s]',text)
  def click(text):
   q=point(text);page.mouse.click(q['x']+12,q['y']+8);page.wait_for_timeout(200)
  def field(i):return page.locator('[data-control="'+str(i)+'"]:visible')
  page.goto('http://127.0.0.1:'+str(server.server_port),wait_until='networkidle');click('Later');click('New');field(10).fill('BrowserWindows');click('Create');click('Edit sources');field(54).wait_for(state='visible')
  field(54).fill('return 0; // retained browser draft');click('Save draft');before=field(54).get_attribute('data-binding');content=field(54).input_value()
  # The existing workspace's eight-pixel top inset is its ordinary drag handle.
  # Use the normal immediate double-click; added per-event delay can stretch
  # beyond the 400ms production gesture threshold on a busy wasm runtime.
  box=field(54).bounding_box();x=box['x']+12;y=69
  page.mouse.dblclick(x,y,delay=0);expect(field(54)).to_have_count(0);q=point('Double-click to expand')
  page.mouse.move(q['x']+12,q['y']);page.mouse.down();page.mouse.move(q['x']+12,q['y']+40,steps=8);page.mouse.up();page.wait_for_timeout(200)
  moved=point('Double-click to expand');assert moved['y']>q['y']+25
  page.mouse.dblclick(moved['x']+12,moved['y'],delay=0);field(54).wait_for(state='visible');assert field(54).get_attribute('data-binding')==before and field(54).input_value()==content
  click('BrowserWindows  - Menu');click('Hide project');click('Open');click('Edit sources');field(54).wait_for(state='visible');assert field(54).get_attribute('data-binding')==before and field(54).input_value()==content
  page.set_viewport_size({'width':600,'height':550});page.wait_for_timeout(250);page.set_viewport_size({'width':1200,'height':1050});field(54).wait_for(state='visible');assert field(54).input_value()==content
  page.screenshot(path='/tmp/confectory-browser-retained-windows.png');assert not errors,errors
  browser.close();print('Actual EditorHome browser fold/drag, DOM binding and draft retention, hide/reopen and resize PASS')
finally:server.shutdown()
