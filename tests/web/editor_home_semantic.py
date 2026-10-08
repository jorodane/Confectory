"""Exercise semantic authoring through the unchanged actual EditorHome entry and native inputs."""
import base64,http.server,json,pathlib,re,sys,threading,time
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
  # Passive label coordinates; no command injection, replacement entry or renderer bypass.
  page.add_init_script("window.uiLabels={};const original=CanvasRenderingContext2D.prototype.fillText;CanvasRenderingContext2D.prototype.fillText=function(text,x,y,...args){uiLabels[String(text)]={x,y,time:performance.now()};return original.call(this,text,x,y,...args);};")
  page.on('console',lambda m:print(m.type,m.text,flush=True));page.on('pageerror',lambda e:errors.append(str(e)))
  def click(text):
   print('CLICK',text,flush=True)
   try:page.wait_for_function('(s)=>uiLabels[s]&&performance.now()-uiLabels[s].time<400',arg=text)
   except Exception:
    print(page.evaluate('uiLabels'),flush=True);page.screenshot(path='/tmp/confectory-semantic-failure.png');raise
   point=page.evaluate('(s)=>uiLabels[s]',text);page.mouse.click(point['x']+12,point['y']+8);page.wait_for_timeout(160)
  def field(i):return page.locator('[data-control="'+str(i)+'"]:visible')
  def labels(fragment):page.wait_for_function('(s)=>Object.keys(uiLabels).some(k=>k.includes(s)&&performance.now()-uiLabels[k].time<500)',arg=fragment)
  def source():click('Source');field(54).wait_for(state='visible');return field(54)
  def properties():click('Properties');click('Data');field(88).wait_for(state='visible');page.wait_for_timeout(180)
  def pick(path):
   for _ in range(30):
    before=field(88).input_value();click('Prev')
    if field(88).input_value()==before:break
   for _ in range(30):
    if field(88).input_value()==json.dumps(path,separators=(',',':')):return
    click('Next')
   raise AssertionError('Missing property '+str(path))
  page.goto('http://127.0.0.1:'+str(server.server_port));page.wait_for_function('globalThis.confectoryPlatform?.loops.size>0');page.wait_for_timeout(2100);click('Later');click('New');field(10).fill('SemanticActual');field(11).fill('schema controls');click('Create');labels('Edit sources');click('Edit sources');field(54).wait_for(state='visible')
  originals=json.loads(page.evaluate('confectoryPlatform.bridge.ExportStorage()'))
  declarations=[base64.b64decode(v).decode() for k,v in originals.items() if k.endswith('.celem')]
  ns=next(re.search(r'function\s+([^: ]+)::Main',s).group(1) for s in declarations if re.search(r'function\s+([^: ]+)::Main',s))
  def create(kind,name):
   click('Explore');field(84).wait_for(state='visible')
   for _ in range(6):
    current=page.evaluate('Object.keys(uiLabels).filter(k=>k.startsWith("New ")&&k.endsWith(" (change kind)")&&performance.now()-uiLabels[k].time<500).sort((a,b)=>uiLabels[b].time-uiLabels[a].time)[0]')
    assert current
    if current=='New '+kind+' (change kind)':break
    click(current)
   field(84).fill(ns+'::'+name);click('Create draft');labels(ns+'::'+name)
  create('schema','Leaf');properties();click('Schema');field(208).fill('flag');field(93).fill('bool');click('Set field');labels('flag | bool')
  assert 'field flag single general bool;' in source().input_value()
  create('schema','Shape');properties();click('Schema');field(208).fill('score');field(93).fill('int');click('Set field');labels('score | int');assert 'field score single general int;' in source().input_value()
  # Compound/list/function fields use actual source mode; entering Properties explicitly applies the buffer first.
  field(54).fill('schema '+ns+'::Shape {\n field score single general int;\n field title single general string;\n field values multiple general int;\n field child single compound '+ns+'::Leaf;\n field callback single function '+ns+'::Main;\n}\n');properties();labels('score | int')
  create('object','Item');source().fill('object '+ns+'::Item {\n use schema '+ns+'::Shape;\n data score = 0;\n data title = "";\n data values = [0, 2];\n data child = { flag = false; };\n data callback = '+ns+'::MainBody;\n}\n');properties();labels('callback |')
  assert field(88).input_value()=='["callback"]';click('Function');field(95).fill('[1]');field(96).fill('browser');click('Check inputs');labels('CALL_TARGET');field(96).fill('linux');click('Check inputs');labels('CALL_ARGUMENTS');field(95).fill('[]');click('Check inputs');labels('"status":"valid"');labels('executionAuthorized');labels('Runtime-call provider unavailable')
  click('Data');pick(['child','flag']);expect(field(89)).to_have_value('false');field(89).fill('true');click('Set value');source_text=source().input_value();assert 'true' in source_text
  properties();pick(['values']);field(89).fill('[3,4]');click('Set value');pick(['values',1]);field(89).fill('9');click('Set value');assert re.search(r'data values = \[3,\s*9\];',source().input_value())
  properties();pick(['title']);field(89).fill('');click('Set value');assert 'data title = "";' in source().input_value()
  properties();pick(['score']);expect(field(89)).to_have_value('0');field(89).fill('7');click('Set value');labels('score | int');
  # Retained native input and draft survive presentation switches, repeat hide/open and resize.
  page.evaluate('window.propertyInput=Array.from(document.querySelectorAll("[data-control=\\"89\\"]")).find(e=>e.offsetParent)');field(89).fill('pending');source();properties();expect(field(89)).to_have_value('pending');assert page.evaluate('propertyInput===Array.from(document.querySelectorAll("[data-control=\\"89\\"]")).find(e=>e.offsetParent)');page.wait_for_function('document.activeElement?.dataset.control==="89"')
  field(89).fill('8');click('Set value');source_text=source().input_value();assert 'data score = 8;' in source_text
  click('Save draft');labels('Local source draft saved; final sources unchanged');assert json.loads(page.evaluate('confectoryPlatform.bridge.ExportStorage()'))[next(k for k in originals if k.endswith('/main.csbody'))]==originals[next(k for k in originals if k.endswith('/main.csbody'))]
  for _ in range(2):click('Hide');click('Edit sources');source();assert 'data score = 8;' in field(54).input_value()
  click('Explore');field(77).fill('::Item');click('Search');labels(ns+'::Item');click('List');click('Grid');click('Table');labels('List')
  # Duplicate declaration failure keeps current draft and typed creation input.
  field(84).fill(ns+'::Item');click('Create draft');labels('Error:');expect(field(84)).to_have_value(ns+'::Item');source();assert 'data score = 8;' in field(54).input_value()
  page.screenshot(path='/tmp/confectory-semantic-ui-wide.png')
  page.set_viewport_size({'width':480,'height':1050});properties();expect(field(89)).to_be_visible();bounds=field(89).bounding_box();assert bounds and bounds['x']>=0 and bounds['x']+bounds['width']<=480,bounds
  page.screenshot(path='/tmp/confectory-semantic-ui.png');assert not errors,errors;assert page.evaluate('confectoryPlatform.bridge.Close()');browser.close()
  print('PASS actual EditorHome semantic create/schema field/compound data/source flush/function preflight/no execution/stable draft and input/repeated hide-open/search/modes/duplicate failure/480px/owned close')
finally:server.shutdown()
