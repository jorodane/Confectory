"""Preserved unconfirmed creation fixture: explicit Review/Cancel/compiler Confirm, then cold.
Fixture-only; no user accounts, grants or inference. Native Windows/Android untested.
"""
import json,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());fixture=pathlib.Path(sys.argv[3]).resolve();assert fixture==repo.parent/'scratch/v508-elements/actual13-source-fixture'
case=pathlib.Path(sys.argv[4]).resolve();assert str(case).startswith('/tmp/confectory-element-data-create-') and (case/'profile').is_dir();project=case/'owned project';storage=case/'profile';original={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file() and '.confectory' not in p.parts and '.build' not in p.parts};id='Owned.Elements::Serial';text='9223372036854775804';description='재시작할 미적용 설명 한글';env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(storage),CONFECTORY_ENTRY_STORAGE=str(storage),CONFECTORY_MCP_DIRECTORY=str(case/'instances'),CONFECTORY_WEB_PROJECT=str(project/'project.cproj'),CONFECTORY_DOTNET=env.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet'));env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];host=None;log=None;errors=[];external=[];checks=[]
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
 if isinstance(body,dict) and body.get('op')=='invoke' and body.get('endpoint')=='createVariation' and injected==0:
  # Actual server rejects an explicitly stale transport revision before execution.
  injected+=1;body['expectedRevision']-=1;request.continue_(post_data=json.dumps(body));return
 request.continue_()

def setup():
 page=browser.new_page(viewport={'width':1280,'height':900});page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',observe);page.route('**/*',route);goto_editor(page,url);return page

def source_same():
 actual={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file() and '.confectory' not in p.parts and '.build' not in p.parts};assert actual==original
def idle():page.wait_for_function('()=>document.querySelector(".topbar .brand")?.disabled===false')
def flush():page.evaluate('()=>confectoryFlushPresentation()');return state()
def wait_operation(endpoint,after):
 for _ in range(6000):
  ids={r['invoke']['requestId'] for r in traffic[after:] if r.get('invoke',{}).get('endpoint')==endpoint};results=[r['result'] for r in traffic[after:] if r.get('result',{}).get('requestId') in ids];good=[r for r in results if r.get('ok')]
  if good:return good[-1]
  bad=[r for r in results if r.get('error',{}).get('code')!='stale_revision'];assert not bad,bad;page.wait_for_timeout(10)
 raise AssertionError('operation did not complete: '+endpoint)
def final_unchanged():assert all((project/k).read_bytes()==v for k,v in original.items()) and not (project/'elements/FreshVariant.celem').exists()
def close_floating_views():
 # Retained floating Views intentionally stay above workspace contents. Use their
 # original close controls (input metadata stays retained), not forced clicks.
 while True:
  floating=page.locator('.workspace-floating-window-layer > .window:not([hidden])');keys=floating.evaluate_all('(rows)=>rows.sort((a,b)=>Number(b.style.zIndex)-Number(a.style.zIndex)).map(el=>el.dataset.key)')
  if not keys:return
  page.locator('.window[data-key="'+keys[0]+'"]').locator(':scope > .object-header [data-close],:scope > .window-title [data-close]').click()
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(3);page=setup();page.set_viewport_size({'width':1480,'height':1050});idle();close_floating_views();b=page.locator('.window[data-key^="browser:project:"]');b.click(position={'x':4,'y':4});b.locator('[data-object="Owned.Elements::Unit"]').get_by_role('button',name='정의 열기',exact=True).click();w=page.locator('.window[data-key=schema]');expect(w.locator('.object-title-name')).to_have_text('Unit',timeout=60000);idle();w.click(position={'x':4,'y':4});section=w.locator('.object-variations');section.locator('[data-density="100"]').click();expect(section.locator('[aria-label="FreshVariant HP"]')).to_have_value('222',timeout=30000);section.locator('[data-object="Owned.Elements::FreshVariant"]').get_by_role('button',name='FreshVariant 편집',exact=True).click();child=page.locator('.workspace-floating-window-layer > .window[data-key^=editor-]:not([hidden])').filter(has=page.locator('.object-title-name',has_text='FreshVariant')).last;expect(child.locator('[aria-label="HP 기본값"]')).to_have_value('222',timeout=30000)
  def review():
   expect(child.locator('[data-element-action=confirm]')).to_be_enabled(timeout=30000);child.locator('[data-element-action=confirm]').click();expect(page.locator('#review-creation')).to_be_visible(timeout=30000);assert page.locator('[data-creation-review-id="Owned.Elements::FreshVariant"]').count()==1;assert page.locator('[data-creation-review-id="Owned.Elements::ProjectManifest"]').count()==1;page.locator('#review-creation').click();v=page.locator('.window[data-key=review]');expect(v).to_be_visible(timeout=60000);ids=[row['id'] for row in state()['review']['units']];assert set(ids)=={'Owned.Elements::FreshVariant','Owned.Elements::ProjectManifest'},ids;return v
  v=review();final_unchanged();v.locator('[data-reject]').click();expect(v).to_be_hidden();final_unchanged();checked('new child Confirm enters explicit child-plus-registration Review only; cancelling leaves all final sources absent/unchanged and other Unit draft outside the group')
  child.locator('.object-title-name').click();v=review();
  for cb in v.locator('[data-review-group]').all():expect(cb).to_be_checked()
  if v.locator('[data-additional-changes]').count():
   v.locator('[data-review-advanced]').click();ack=v.locator('[data-advanced-reviewed]')
   if ack.count():ack.check()
  v.locator('#confirm').scroll_into_view_if_needed();hit=v.locator('#confirm').evaluate('(el)=>{const r=el.getBoundingClientRect(),at=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2);return {clickable:el===at||el.contains(at),layer:el.closest(".workspace-floating-window-layer")!==null,focusInside:el.closest(".window").contains(document.activeElement)}}');assert hit['clickable'] and hit['layer'],hit;page.screenshot(path=str(case/'reachable-creation-review.png'));(case/'review-layer.json').write_text(json.dumps(hit,indent=2))
  after=len(traffic);v.locator('#confirm').click();result=wait_operation('confirmGroup',after);assert result['result']['sourceConfirmed'];expect(v).to_be_hidden(timeout=60000);assert 'data HP = 222' in (project/'elements/FreshVariant.celem').read_text();assert 'FreshVariant' in (project/'project.cproj').read_text();assert all((project/k).read_bytes()==value for k,value in original.items() if k!='project.cproj');assert any(row['id']=='Owned.Elements::Unit' and row['dirty'] for row in state()['units']);page.screenshot(path=str(case/'new-creation-explicit-confirm.png'));checked('explicit compiler Confirm writes exactly new FreshVariant and manifest registration while Unit111 remains an unconfirmed separate draft')
  idle();flush();page.close();stop();start(4);page=setup();page.set_viewport_size({'width':1480,'height':1050});idle();close_floating_views();b=page.locator('.window[data-key^="browser:project:"]');b.locator('[data-object="Owned.Elements::Unit"]').get_by_role('button',name='정의 열기',exact=True).click();w=page.locator('.window[data-key=schema]');expect(w.locator('.object-title-name')).to_have_text('Unit',timeout=60000);expect(w.locator('[aria-label="HP 기본값"]')).to_have_value('111');w.click(position={'x':4,'y':4});section=w.locator('.object-variations');section.locator('[data-density="100"]').click();expect(section.locator('[aria-label="FreshVariant HP"]')).to_have_value('222',timeout=30000);section.locator('[data-object="Owned.Elements::FreshVariant"]').get_by_role('button',name='FreshVariant 편집',exact=True).click();child=page.locator('.workspace-floating-window-layer > .window[data-key^=editor-]:not([hidden])').filter(has=page.locator('.object-title-name',has_text='FreshVariant')).last;expect(child.locator('[aria-label="HP 기본값"]')).to_have_value('222',timeout=30000);child.locator('[aria-label="HP 기본값"]').fill('223');child.locator('[data-element-action=discard]').click();expect(child.locator('[aria-label="HP 기본값"]')).to_have_value('222',timeout=30000);assert 'data HP = 222' in (project/'elements/FreshVariant.celem').read_text();assert all((project/k).read_bytes()==value for k,value in original.items() if k!='project.cproj');checked('confirmed creation survives actual process restart and normal source reentry; cancelling new child input restores222 while unrelated staged Unit111 and original Unit file remain intact')
  assert not errors and not external,(errors,external);(case/'creation-confirm-evidence.json').write_text(json.dumps({'checks':checks,'actualEngine':True,'nativeWindowsOrAndroid':False,'errors':errors},ensure_ascii=False,indent=2));print(json.dumps({'checks':checks,'evidence':str(case),'errors':errors},ensure_ascii=False,indent=2));page.close();stop();browser.close()
except Exception:
 try:page.screenshot(path=str(case/'creation-confirm-failure.png'))
 except Exception:pass
 try:(case/'creation-confirm-failure.json').write_text(json.dumps({'state':state(),'traffic':traffic,'errors':errors},ensure_ascii=False,indent=2))
 except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case),flush=True);raise
finally:stop()
