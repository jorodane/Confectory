"""Production WASM UI: stable schema IDs and scoped local inputs; no command injection."""
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
  def click(text):
   page.wait_for_function('(s)=>uiLabels[s]&&performance.now()-uiLabels[s].time<500',arg=text)
   q=page.evaluate('(s)=>uiLabels[s]',text);page.mouse.click(q['x']+12,q['y']+8);page.wait_for_timeout(250)
  def field(i):return page.locator('[data-control="'+str(i)+'"]:visible')
  def save():click('Save draft');page.wait_for_timeout(300)
  page.goto('http://127.0.0.1:'+str(server.server_port),wait_until='networkidle');click('Later');click('New');field(10).fill('BrowserInputs');click('Create');click('Object browser')
  # Create ordinary drafts through the product's existing controls, not a special fixture pack.
  click('New object (change kind)');field(84).fill('Project.BrowserInputs::Shape');click('Create draft');click('Source');field(54).fill('schema Project.BrowserInputs::Shape { field count single general int; }');save()
  click('Explore')
  for kind in ['schema','concept','category','function','module']:click('New '+kind+' (change kind)')
  field(84).fill('Project.BrowserInputs::Thing');click('Create draft');click('Source');field(54).fill('object Project.BrowserInputs::Thing { use schema Project.BrowserInputs::Shape; data count = 7; }');save();original=field(54).get_attribute('data-binding')
  click('Properties');expect(field(88)).to_have_value('["count"]');click('Open schema');expect(field(208)).to_be_visible();click('Source');expect(field(54)).to_have_value('schema Project.BrowserInputs::Shape { field count single general int; }')
  field(54).fill('schema Project.BrowserInputs::Shape { field count single general int; field note single general string; }');save();click('Properties');click('Back to object');expect(field(88)).to_have_value('["count"]');expect(field(89)).to_have_value('7');click('Source');assert field(54).get_attribute('data-binding')==original
  field(38).fill('project draft stays here');click('Augment');click('Review 3 proposals / direction reroll');expect(field(309)).to_have_value('');field(309).fill('object direction only');direction=field(309).get_attribute('data-binding');click('Back to proposals');click('Review 3 proposals / direction reroll');expect(field(309)).to_have_value('object direction only');assert field(309).get_attribute('data-binding')==direction;click('Back to proposals');click('Close menu')
  click('Helper  0');click('Create Main Helper');click('main-helper | global');field(310).fill('main helper draft');binding=field(310).get_attribute('data-binding');expect(field(38)).to_have_value('project draft stays here');click('Choose Helper');click('Create Project Helper')
  page.wait_for_function('Object.keys(uiLabels).some(s=>s.endsWith(" | project")&&performance.now()-uiLabels[s].time<500)')
  other=page.evaluate('Object.keys(uiLabels).find(s=>s.endsWith(" | project")&&performance.now()-uiLabels[s].time<500)');click(other);expect(field(310)).to_have_value('');field(310).fill('project helper draft');click('Choose Helper');click('main-helper | global');expect(field(310)).to_have_value('main helper draft');assert field(310).get_attribute('data-binding')==binding
  page.screenshot(path='/tmp/confectory-ui-scoped-inputs-browser.png');click('Close menu');click('BrowserInputs  - Menu');click('Hide project');click('Open');click('Helper  1');click('main-helper | global');expect(field(310)).to_have_value('main helper draft');assert field(310).get_attribute('data-binding')==binding
  assert not errors,errors;browser.close();print('Production EditorHome WASM schema-origin navigation, shared drafts, Helper scopes and separate direction input PASS')
finally:server.shutdown()
