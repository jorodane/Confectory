"""v536 existing area/multi selection, movement and staged delete; controlled renderer."""
import ast,http.server,json,pathlib,re,sys,tempfile,threading
from playwright.sync_api import sync_playwright,expect
repo=pathlib.Path(sys.argv[1]).resolve();case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-selection-'));checks=[];errors=[]
tree=ast.parse((repo/'tests/web/v508_feature_serial_canvas.py').read_text())
setup=next(n.args[0].value for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='evaluate' and n.args and isinstance(n.args[0],ast.Constant) and isinstance(n.args[0].value,str) and 'const {createFeatureAuthoring}' in n.args[0].value)
setup=setup.replace('await author.openInWork(info);', '''fixture.api=api;graph.entry='';graph.edges=[];graph.exits[0].valueJson='{"constant":0}';graph.nodes[1].arguments[0].valueJson='{"constant":2}';await author.openInWork(info);''')
styles='\n'.join((repo/'examples/editor-home/ui'/n).read_text() for n in ['style.css','consumer.css','runtime.css']);styles=re.sub(r'@import\s+url\([^)]*\)\s*;','',styles)
class Handler(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(repo),**kw)
 def log_message(self,*a):pass
 def do_GET(self):
  if self.path=='/fixture':
   self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.end_headers();self.wfile.write(('<style>'+styles+'</style><main id="workspace" class="workspace" style="height:840px;position:relative"></main>').encode())
  else:super().do_GET()
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
def checked(message):checks.append(message);print('PASS '+message,flush=True)
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page(viewport={'width':1280,'height':900});page.on('pageerror',lambda e:errors.append(str(e)));page.goto('http://127.0.0.1:'+str(server.server_port)+'/fixture');page.evaluate(setup)
  author=page.locator('.window');viewport=author.locator('.bp-viewport')
  def node(id):return author.locator('[data-bp-node="'+id+'"]')
  def header(id):return node(id).locator('[data-bp-node-name]').first
  def positions():return page.evaluate('Object.fromEntries(["first","second"].map(id=>{const n=document.querySelector("[data-bp-node="+id+"]");return [id,{x:parseFloat(n.style.left),y:parseFloat(n.style.top)}]}))')
  def both():
   header('first').click(position={'x':3,'y':3},modifiers=['Control']);header('second').click(position={'x':3,'y':3},modifiers=['Control']);expect(author.locator('.bp-node.is-selected')).to_have_count(2)
  def keys(k):viewport.focus();page.keyboard.press(k)
  before=positions();mark=page.evaluate('fixture.traffic.length');both();box=header('first').bounding_box();page.mouse.move(box['x']+3,box['y']+3);page.mouse.down();page.mouse.move(box['x']+48,box['y']+25,steps=5);page.mouse.up();moved=positions();assert all(moved[id]['x']-before[id]['x']==max(172,before['first']['x']+45)-before['first']['x'] and moved[id]['y']-before[id]['y']==max(47,before['first']['y']+22)-before['first']['y'] for id in before),(before,moved);assert page.evaluate('fixture.inputs.size')==0
  keys('Control+z');assert positions()==before;keys('Control+Shift+z');assert positions()==moved;assert page.evaluate('fixture.inputs.size')==0;checked('original modifier selection moves exactly the selected group; Undo/Redo affects coordinates without creating source input')
  keys('Escape');r=viewport.bounding_box();page.mouse.move(r['x']+140,r['y']+10);page.mouse.down();page.mouse.move(r['x']+r['width']-15,r['y']+350,steps=8);page.mouse.up();expect(author.locator('.bp-node.is-selected')).to_have_count(2);assert page.evaluate('fixture.traffic.length')==mark;checked('original area rectangle selects both intersecting nodes and excludes entry/terminal without provider calls')
  keys('Delete');expect(author.locator('[data-bp-node=first]')).to_have_count(0);expect(author.locator('[data-bp-node=second]')).to_have_count(0);assert page.evaluate('[...fixture.inputs.values()].filter(v=>v.type==="remove").length')==2
  keys('Control+z');expect(author.locator('[data-bp-node=first]')).to_have_count(1);expect(author.locator('[data-bp-node=second]')).to_have_count(1);assert page.evaluate('fixture.inputs.size')==0;keys('Control+Shift+z');assert page.evaluate('[...fixture.inputs.values()].filter(v=>v.type==="remove").length')==2;keys('Control+z');checked('one staged group deletion and Undo/Redo preserve both records together before any Save')
  page.evaluate('fixture.graph.entry="first";fixture.graph.edges=[{from:"first",port:"next",to:"second"}];fixture.open()');both();keys('Delete');assert page.evaluate('fixture.inputs.size')==0;assert page.evaluate('fixture.toasts.at(-1)').startswith('이 노드의 실행 줄');expect(node('first')).to_have_count(1);expect(node('second')).to_have_count(1);checked('a connected member refuses the entire group and keeps every original node and input')
  page.evaluate('fixture.graph.entry="";fixture.graph.edges=[];fixture.graph.privatePath="box";fixture.open()');both();keys('Delete');assert page.evaluate('fixture.inputs.size')==0;assert '기본 흐름' in page.evaluate('fixture.toasts.at(-1)');expect(node('first')).to_have_count(1);expect(node('second')).to_have_count(1);checked('nested selection cannot fall back to sequential multi-removal outside the atomic root contract')
  page.evaluate('delete fixture.graph.privatePath;fixture.open()');both();keys('Delete');keys('Control+z');page.evaluate('fixture.api.current.projectId="retired"');keys('Control+Shift+z');assert page.evaluate('fixture.inputs.size')==0;assert not errors,errors;checked('retired project cannot replay the selection edit history into another scope')
  page.screenshot(path=str(case/'selection.png'));browser.close()
finally:server.shutdown()
print(json.dumps({'checks':checks,'controlledRenderer':True,'actualBackend':False,'nativeTouch':False,'evidence':str(case),'errors':errors}))
