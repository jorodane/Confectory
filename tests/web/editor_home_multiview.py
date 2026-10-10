"""Actual browser Main, ordinary projects and borrowed draft views; no injected commands."""
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
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page(viewport={'width':1400,'height':1050});errors=[]
  page.add_init_script('window.uiLabels={};const original=CanvasRenderingContext2D.prototype.fillText;CanvasRenderingContext2D.prototype.fillText=function(text,x,y,...args){uiLabels[String(text)+"|"+x+"|"+y]={text:String(text),x,y,time:performance.now()};return original.call(this,text,x,y,...args);};')
  page.on('pageerror',lambda e:errors.append(str(e)))
  def click(text,max_y=2000,min_y=0):
   page.wait_for_function('([s,y,m])=>Object.values(uiLabels).some(v=>v.text===s&&v.y>=m&&v.y<y&&performance.now()-v.time<500)',arg=[text,max_y,min_y]);q=page.evaluate('([s,y,m])=>Object.values(uiLabels).filter(v=>v.text===s&&v.y>=m&&v.y<y&&performance.now()-v.time<500).sort((a,b)=>b.time-a.time)[0]',[text,max_y,min_y]);page.mouse.click(q['x']+12,q['y']+8);page.wait_for_timeout(300)
  def field(i):return page.locator('[data-control="'+str(i)+'"]:visible')
  def retained(i):return page.locator('[data-control="'+str(i)+'"]')
  def main():page.mouse.click(236,69);page.wait_for_timeout(450)
  def save():click('Save draft',150);page.wait_for_timeout(300)
  def select(id):main();click('Explore');field(82).fill(id);click('Open');page.wait_for_timeout(300)
  def pin_action(slot,part):
   click('View '+str(slot));b=field(400+(slot-1)*4).bounding_box();page.mouse.click(b['x']+(b['width']-8)/3*(part+.5)+part*4,b['y']+b['height']+20);page.wait_for_timeout(500)
  ns='Project.BrowserViews'
  page.goto('http://127.0.0.1:'+str(server.server_port),wait_until='networkidle');click('Later');click('New');field(10).fill('BrowserViews');click('Create');click('Object browser');click('New object (change kind)')
  for name,text in [('Leaf','field flag single general bool;'),('Shape','field count single general int; field child single compound '+ns+'::Leaf;')]:
   field(84).fill(ns+'::'+name);click('Create draft');click('Source');field(54).fill('schema '+ns+'::'+name+' { '+text+' }');save();click('Explore')
  for kind in ['schema','concept','category','function','module']:click('New '+kind+' (change kind)')
  for name,count in [('First',7),('Second',11)]:
   field(84).fill(ns+'::'+name);click('Create draft');click('Source');field(54).fill('object '+ns+'::'+name+' { use schema '+ns+'::Shape; data count = '+str(count)+'; data child = { flag = false; }; }');save();click('Explore')
  select(ns+'::First');click('Source');first=field(54).input_value();source_binding=field(54).get_attribute('data-binding');click('Keep view');expect(retained(400)).to_have_value(first);assert field(400).get_attribute('data-binding')==source_binding
  first=first.replace('count = 7','count = 9');field(400).fill(first);expect(field(54)).to_have_value(first);pin_action(1,0);main();first=first.replace('count = 9','count = 10');field(54).fill(first);expect(retained(400)).to_have_value(first);save()
  select(ns+'::Second');click('Source');click('Keep view');second=field(404).input_value().replace('count = 11','count = 12');field(404).fill(second);pin_action(2,0);expect(retained(400)).to_have_value(first);assert field(404).get_attribute('data-binding')!=source_binding
  select(ns+'::First');click('Source')
  assert 'object '+ns+'::First' in field(54).input_value();click('Properties');expect(field(88)).to_be_visible()
  for _ in range(5):
   if field(88).input_value()=='["child"]':break
   click('Next',250,180)
  expect(field(88)).to_have_value('["child"]');click('Keep view');expect(field(408)).to_have_value('{"flag":false}');field(408).fill('{"flag":true}');pin_action(3,0)
  page.wait_for_function('document.querySelector("[data-control=\\"400\\"]").value.includes("flag = true")');main();expect(field(89)).to_have_value('{"flag":true}');click('Open schema');click('Source');field(54).fill('schema '+ns+'::Shape { field count single general int; field child single compound '+ns+'::Leaf; field note single general string; }');save();click('View 3');expect(field(408)).to_have_value('{"flag":true}');page.screenshot(path='/tmp/confectory-multiview-browser.png')
  # Native DOM identity survives presentation close, fold, hide and project return.
  # Use Playwright's default immediate pair; an artificial per-event delay can exceed
  # the existing 400ms gesture threshold on a busy wasm runtime.
  click('View 1');binding=field(400).get_attribute('data-binding');b=field(400).bounding_box();page.mouse.dblclick(b['x']+12,b['y']-89,delay=0);page.wait_for_timeout(400);expect(field(400)).to_have_count(0);click('View 1');page.mouse.dblclick(b['x']+12,b['y']-89,delay=0);expect(field(400)).to_be_visible();assert field(400).get_attribute('data-binding')==binding
  pin_action(1,2);expect(field(400)).to_have_count(0);click('Reopen 1');expect(field(400)).to_be_visible();assert field(400).get_attribute('data-binding')==binding
  click('BrowserViews  - Menu');click('Hide project');click('New');field(10).fill('OtherViews');click('Create');expect(field(400)).to_have_count(0);click('OtherViews  - Menu');click('Hide project')
  # Home card order is the creation order; click the first visible Open label.
  q=page.evaluate('Object.values(uiLabels).filter(v=>v.text==="Open"&&performance.now()-v.time<500).sort((a,b)=>a.y-b.y||a.x-b.x)[0]');page.mouse.click(q['x']+12,q['y']+8);expect(field(400)).to_be_visible();assert field(400).get_attribute('data-binding')==binding;expect(field(408)).to_have_value('{"flag":true}')
  assert not errors,errors;browser.close();print('Actual browser simultaneous object/compound/schema views, shared draft, fold/close and project isolation PASS')
finally:server.shutdown()
