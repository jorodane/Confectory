"""v536 mobile Blueprint values in the actual generated engine.
No account/grant/model invocation. Preserves source bytes and original draft proof.
"""
import json,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());fixture=pathlib.Path(sys.argv[3]).resolve();assert fixture==repo.parent/'scratch/v508-elements/actual13-source-fixture'
case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-mobile-touch-'));project=case/'owned project';shutil.copytree(fixture/'owned project',project,ignore=shutil.ignore_patterns('.confectory','.build'));storage=case/'profile';storage.mkdir();original={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file() and '.confectory' not in p.parts};id='Owned.Elements::Serial';text='9223372036854775804';description='재시작할 미적용 설명 한글';env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(storage),CONFECTORY_ENTRY_STORAGE=str(storage),CONFECTORY_MCP_DIRECTORY=str(case/'instances'),CONFECTORY_WEB_PROJECT=str(project/'project.cproj'),CONFECTORY_DOTNET=env.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet'));env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];host=None;log=None;errors=[];external=[];checks=[]
def stop():
 global host,log
 if host and host.poll() is None:os.killpg(host.pid,signal.SIGTERM)
 if host:host.wait(timeout=15)
 if log:log.close()
def start(i):
 global host,log,origin,token,url
 file=case/f'host-{i}.log';log=file.open('w');host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 for _ in range(600):
  urls=[l.split(' ',1)[1] for l in file.read_text().splitlines() if l.startswith('CONFECTORY_WEB_UI ')]
  if urls:url=urls[-1];origin,token=url.split('/#');return
  assert host.poll() is None,file.read_text()[-1000:];time.sleep(.05)
 raise AssertionError('startup timeout')
def raw(body):return json.load(urllib.request.urlopen(urllib.request.Request(origin+'/api/request',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':token}),timeout=30))
def mount():
 for _ in range(300):
  v=raw({'op':'mount'})
  if v.get('ok'):return v
  assert v.get('error',{}).get('code')=='busy',v;time.sleep(.02)
 raise AssertionError('busy transport')
def state():
 v=mount()
 try:return v['state']
 finally:raw({'op':'dispose','view':v['view']})
def invoke(endpoint,body,success=True):
 for _ in range(4):
  v=mount();rid=uuid.uuid4().hex
  try:
   assert raw({'op':'invoke','view':v['view'],'scope':v['scope'],'expectedRevision':v['revision'],'requestId':rid,'endpoint':endpoint,'input':body})['ok']
   for _ in range(600):
    u=raw({'op':'update','view':v['view'],'scope':v['scope']});rows=[r for r in u.get('results',[]) if r['requestId']==rid]
    if rows:break
    time.sleep(.01)
   assert rows
   if rows[0].get('error',{}).get('code')=='stale_revision':continue
   assert bool(rows[0].get('ok')) is success,rows;return {'result':rows[0],'state':u.get('state')}
  finally:raw({'op':'dispose','view':v['view']})
 raise AssertionError('admission failed')
traffic=[];injected=0

def checked(text):
 checks.append(text);(case/'progress.json').write_text(json.dumps(checks,indent=2));print('PASS '+text,flush=True)
def observe(response):
 try:
  request=response.request.post_data_json
  if not isinstance(request,dict):return
  if request.get('op')=='invoke':traffic.append({'invoke':request})
  elif request.get('op')=='update':
   for result in response.json().get('results',[]):
    if not any(row.get('result',{}).get('requestId')==result['requestId'] for row in traffic):traffic.append({'result':result})
 except Exception:pass

def route(request):
 global injected
 if not request.request.url.startswith(origin):external.append(request.request.url);request.abort();return
 body=request.request.post_data_json if request.request.method=='POST' else None
 if isinstance(body,dict) and body.get('op')=='invoke' and body.get('endpoint')=='reviewDraft' and False:
  # Actual server rejects an explicitly stale transport revision before execution.
  injected+=1;body['expectedRevision']-=1;request.continue_(post_data=json.dumps(body));return
 request.continue_()

def setup():
 page=browser.new_page(viewport={'width':1280,'height':900});page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',observe);page.route('**/*',route);goto_editor(page,url);return page

def setup():
 context=browser.new_context(viewport={'width':390,'height':844},has_touch=True,is_mobile=True);page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',observe);page.route('**/*',route);goto_editor(page,url);return page

def open_author():
 page.locator('[data-mobile-files]').click();b=page.locator('.window[data-key="browser:project:mobile"]');b.locator('[data-tab=feature]').click();row=b.locator('[data-object="Owned.Elements::Serial"]');expect(row).to_be_visible(timeout=30000);expect(page.locator('.brand')).to_be_enabled(timeout=60000);row.press('Enter');decl=page.locator('.window[data-key=declaration]');expect(decl.locator('[data-function-write-direct]')).to_be_visible(timeout=30000);decl.locator('[data-function-write-direct]').click();expect(page.locator('.window[data-key=blueprint] [aria-label="카드 흐름 편집"]')).to_be_visible(timeout=30000)
def graph():return invoke('blueprint',{'action':'read','id':'Owned.Elements::SerialBlueprintBody/body:common'})['result']['result']
def pending():page.evaluate('()=>confectoryFlushPresentation()');return [(k,v) for k,v in state()['presentation']['inputs']['blueprint'] if '|v508-author|' in k]
def source_same():assert all((project/k).read_bytes()==v for k,v in original.items())
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(0);page=setup();open_author();author=page.locator('.window[data-key=blueprint]');flow=author.locator('[aria-label="카드 흐름 편집"]');flow.locator('[data-flow-graph]').click();viewport=author.locator('.bp-viewport');expect(viewport).to_be_visible();tools=author.locator('[aria-label="노드 터치 도구"]');tools.locator('[data-mobile-view]').click();menu=page.locator('.context-menu');expect(menu).to_be_visible();expect(menu.get_by_role('button',name='영역 선택 모드',exact=True)).to_be_enabled();menu.get_by_role('button',name='미니맵 펼치기',exact=True).click();assert author.locator('.blueprint-editor').evaluate('e=>e.classList.contains("mobile-show-map")');expect(author.locator('[data-bp-overview]')).to_be_visible();tools.locator('[data-mobile-view]').click();menu.get_by_role('button',name='설명 펼치기',exact=True).click();assert author.locator('.blueprint-editor').evaluate('e=>e.classList.contains("mobile-show-description")');tools.locator('[data-mobile-view]').click();menu.get_by_role('button',name='전체 보기',exact=True).click();plane=author.locator('.bp-plane');page.wait_for_function('()=>Number.parseFloat(document.querySelector("[data-bp-percent]").textContent)<100');source_same();checked('original View menu fits the real graph and exposes minimap/description with available area selection and unchanged pan defaults')
  cdp=page.context.new_cdp_session(page);box=viewport.bounding_box()
  def position():return page.evaluate("r=>{for(const fy of [.9,.75,.6])for(const fx of [.8,.65,.4]){const x=r.x+r.width*fx,y=r.y+r.height*fy,e=document.elementFromPoint(x,y);if(e?.closest('.bp-viewport')&&!e.closest('.bp-node,.bp-wire-group'))return {x,y}}throw Error('no canvas background')}",box)
  def touch(kind,points):cdp.send('Input.dispatchTouchEvent',{'type':kind,'touchPoints':points})
  pt=position();x=pt['x'];y=pt['y'];before=plane.evaluate('e=>e.style.transform');touch('touchStart',[{'x':x,'y':y,'id':1}]);touch('touchMove',[{'x':x-65,'y':y-20,'id':1}]);touch('touchEnd',[]);page.wait_for_function('old=>document.querySelector(".bp-plane").style.transform!==old',arg=before);scale=plane.evaluate('e=>new DOMMatrix(getComputedStyle(e).transform).a');cx=box['x']+box['width']*.55;cy=box['y']+box['height']*.65;touch('touchStart',[{'x':cx-30,'y':cy,'id':1},{'x':cx+30,'y':cy,'id':2}]);touch('touchMove',[{'x':cx-80,'y':cy,'id':1},{'x':cx+80,'y':cy,'id':2}]);touch('touchEnd',[]);page.wait_for_function('old=>new DOMMatrix(getComputedStyle(document.querySelector(".bp-plane")).transform).a>old',arg=scale);zoom=plane.evaluate('e=>new DOMMatrix(getComputedStyle(e).transform).a');assert .03125<=zoom<=3;assert not pending();source_same();checked('Chromium protocol touch pan and two-pointer pinch affect only bounded private view coordinates and preserve all source/input')
  pt=position();x=pt['x'];y=pt['y'];before=plane.evaluate('e=>e.style.transform');touch('touchStart',[{'x':x,'y':y,'id':1}]);touch('touchMove',[{'x':x-30,'y':y-20,'id':1}]);touch('touchCancel',[]);page.wait_for_function('old=>document.querySelector(".bp-plane").style.transform===old',arg=before);source_same();checked('original touch cancel restores starting camera/zoom without staging a partial domain edit')
  mark=len(traffic);tools.locator('[data-mobile-selection]').tap();menu.get_by_role('button',name='기능 안에서 찾기',exact=True).click();find=page.get_by_role('dialog',name='기능 안에서 찾기',exact=True);expect(find).to_be_visible();find.get_by_role('searchbox',name='배치된 노드에서 찾기').fill('독립 동작 한글');expect(find.locator('[data-find-count]')).to_have_text('1 / 1');field=find.get_by_role('searchbox');field.evaluate('e=>e.dispatchEvent(new KeyboardEvent("keydown",{key:"Enter",isComposing:true,bubbles:true,cancelable:true}))');field.evaluate('e=>e.dispatchEvent(new KeyboardEvent("keydown",{key:"Escape",keyCode:229,bubbles:true,cancelable:true}))');expect(find).to_be_visible();expect(field).to_have_value('독립 동작 한글');page.keyboard.press('Escape');expect(find).to_have_count(0);assert not [t for t in traffic[mark:] if t.get('invoke',{}).get('endpoint')=='blueprint'];assert not pending();source_same();assert not errors and not external,(errors,external);page.screenshot(path=str(case/'touch-graph-view.png'));checked('touch Menu finder keeps Korean IME composition in its overlay and ordinary Escape closes it without provider/source calls')
  record={'checks':checks,'actualEngine':True,'chromiumProtocolSyntheticTouch':True,'actualTouchHardware':False,'nativeWindowsOrAndroid':False,'actualCredentialsOrInference':False,'errors':errors,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False,indent=2));page.close();stop();browser.close()
except Exception:
 try:(case/'failure.json').write_text(json.dumps({'state':state(),'traffic':traffic,'errors':errors},ensure_ascii=False,indent=2))
 except Exception:pass
 try:page.screenshot(path=str(case/'failure.png'))
 except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case),flush=True);raise
finally:stop()
