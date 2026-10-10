"""Ordinary browser ProjectPack: real controls, bounded panels and retained scoped inputs."""
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
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page(viewport={'width':960,'height':700});errors=[]
  page.add_init_script('window.uiLabels={};const original=CanvasRenderingContext2D.prototype.fillText;CanvasRenderingContext2D.prototype.fillText=function(text,x,y,...args){uiLabels[String(text)]={x,y,time:performance.now()};return original.call(this,text,x,y,...args);};')
  page.on('pageerror',lambda e:errors.append(str(e)))
  def point(text):
   page.wait_for_function('s=>uiLabels[s]&&performance.now()-uiLabels[s].time<500',arg=text);return page.evaluate('s=>uiLabels[s]',text)
  def click(text):
   q=point(text);page.mouse.click(q['x']+12,q['y']+8);page.wait_for_timeout(250)
  def field(id):return page.locator('[data-control="'+str(id)+'"]:visible')
  def bound_helper():
   c=field(38).bounding_box();h=field(310).bounding_box();o=field(313).bounding_box();q=point('Close menu');assert o['y']+o['height']<=h['y'] and h['y']+h['height']<=q['y'] and q['y']+24<point('Project chat')['y'],(c,h,o,q)
  page.goto('http://127.0.0.1:'+str(server.server_port),wait_until='networkidle');click('Later');click('New');field(10).fill('Browser Layout');click('Create');field(38).fill('Project draft stays here');chat=field(38).get_attribute('data-binding');click('Edit sources');source=field(54).get_attribute('data-binding');click('Helper  0');click('Create Main Helper');click('main-helper | global');field(310).fill('Helper draft stays here');helper=field(310).get_attribute('data-binding')
  for w,h in [(960,700),(1200,900),(640,520),(960,700)]:
   page.set_viewport_size({'width':w,'height':h});page.wait_for_timeout(500);expect(field(310)).to_have_value('Helper draft stays here');expect(field(38)).to_have_value('Project draft stays here');bound_helper();assert field(310).get_attribute('data-binding')==helper and field(38).get_attribute('data-binding')==chat;page.screenshot(path=f'/tmp/confectory-layout-browser-helper-{w}x{h}.png')
  field(38).fill('Project draft stays editable');expect(field(310)).to_have_value('Helper draft stays here');click('Close menu');assert field(54).get_attribute('data-binding')==source;click('Augment')
  q=[point('Proposal '+str(i)) for i in [1,2,3]];assert q[0]['x']<q[1]['x']<q[2]['x'] and q[0]['y']==q[1]['y']==q[2]['y'];assert point('Close menu')['y']+24<point('Project chat')['y'];page.screenshot(path='/tmp/confectory-layout-browser-columns.png')
  page.set_viewport_size({'width':640,'height':520});page.wait_for_timeout(500);point('Proposal 1 / 3');click('Next');point('Proposal 2 / 3');click('Next');point('Proposal 3 / 3');assert point('Close menu')['y']+24<point('Project chat')['y'];page.screenshot(path='/tmp/confectory-layout-browser-compact.png');click('Previous');point('Proposal 2 / 3');click('Close menu');click('Helper  1');click('main-helper | global');expect(field(310)).to_have_value('Helper draft stays here');bound_helper()
  assert not errors,errors;browser.close();print('Actual browser bounded Helper/chat/Dock, three proposal columns, compact paging and retained native bindings PASS')
finally:server.shutdown()
