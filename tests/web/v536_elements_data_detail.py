"""Continuation of a preserved failed detail fixture: view-bound Save and receipt cleanup.
Fixture-only; no user accounts, grants or inference. Native Windows/Android untested.
"""
import json,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());fixture=pathlib.Path(sys.argv[3]).resolve();assert fixture==repo.parent/'scratch/v508-elements/actual13-source-fixture'
case=pathlib.Path(sys.argv[4]).resolve();assert str(case).startswith('/tmp/confectory-element-data-write-');project=case/'owned project';storage=case/'profile';n='Owned.Elements::'
original={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file() and '.confectory' not in p.parts};id='Owned.Elements::Serial';text='9223372036854775804';description='재시작할 미적용 설명 한글';env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(storage),CONFECTORY_ENTRY_STORAGE=str(storage),CONFECTORY_MCP_DIRECTORY=str(case/'instances'),CONFECTORY_WEB_PROJECT=str(project/'project.cproj'),CONFECTORY_DOTNET=env.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet'));env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];host=None;log=None;errors=[];external=[];checks=[]
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
 if isinstance(body,dict) and body.get('op')=='invoke' and body.get('endpoint')=='editBrowserElement' and injected==0:
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
def wait_any(endpoint,after):
 for _ in range(6000):
  ids={r['invoke']['requestId'] for r in traffic[after:] if r.get('invoke',{}).get('endpoint')==endpoint};results=[r['result'] for r in traffic[after:] if r.get('result',{}).get('requestId') in ids and r.get('result',{}).get('error',{}).get('code')!='stale_revision']
  if results:return results[-1]
  page.wait_for_timeout(10)
 raise AssertionError('no result '+endpoint)
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(2);page=setup();page.set_viewport_size({'width':1480,'height':1050});idle()
  def close_floating():
   while True:
    keys=page.locator('.workspace-floating-window-layer > .window:not([hidden])').evaluate_all('(rows)=>rows.sort((a,b)=>Number(b.style.zIndex)-Number(a.style.zIndex)).map(el=>el.dataset.key)')
    if not keys:return
    page.locator('.window[data-key="'+keys[0]+'"]').locator(':scope > .object-header [data-close],:scope > .window-title [data-close]').click()
  close_floating();b=page.locator('.window[data-key^="browser:project:"]');b.click(position={'x':4,'y':4});b.locator('[data-object="Owned.Elements::Unit"]').get_by_role('button',name='정의 열기',exact=True).click();w=page.locator('.window[data-key=schema]');expect(w.locator('[aria-label="HP 기본값"]')).to_have_value('111',timeout=60000);section=w.locator('.object-variations');cell=lambda field:section.get_by_role('spinbutton',name='Monster '+field,exact=True)
  for field in ['HP','Speed','Combat.Power']:
   control=cell(field);after=len(traffic);control.press('Enter');assert wait_operation('editBrowserElement',after)['result']['accepted'];idle()
  root=section.locator('[data-object="Owned.Elements::Monster"]');root.locator('.browser-data-field').filter(has=page.locator('.browser-property-label',has_text='Counts')).get_by_role('button',name='2개 값 · 편집',exact=True).click();new=page.locator('.window[data-key=editor-3]');expect(new.locator('.object-title-name')).to_have_text('Monster',timeout=30000);array=new.locator('section[data-property-path]').filter(has=page.get_by_role('button',name='Counts 값 펼치기/접기',exact=True));expect(array.locator('.property-multi-values')).to_be_visible();expect(array.locator('input[data-property-value]')).to_have_count(2);expect(new.locator('[aria-label="HP 기본값"]')).to_have_value('200');snapshot=flush();assert any('|view:1|element|' in key and value.get('text')=='150' for key,value in snapshot['presentation']['inputs']['schema']);assert any('|view:2|element|' in key and '9223372036854775806' in value.get('text','') for key,value in snapshot['presentation']['inputs']['schema']);source_same();checked('detail reentry unfolds Counts in a third owned View and retains parent111, other HP150 and failed second View array input')
  array.locator('input[data-property-value]').first.fill('9223372036854775806');after=len(traffic);new.locator('[data-element-action=save]').click();wait_operation('saveEditorView',after);expect(new.locator('[data-element-error]')).to_have_text('');source_same();status=invoke('browserElements',{'ids':[n+'Monster']})['result']['result']['rows'][0];assert status['checkpointSaved'] is True;assert next(f for f in status['fields'] if f['column']=='data:["Counts"]')['valueJson']=='[9223372036854775806,2]';page.screenshot(path=str(case/'actual-data-and-array-detail.png'));checked('separate View detail saves exact 64-bit array through its own bound source CAS, keeping final source unchanged and checkpointSaved verified')
  close_floating();b.click(position={'x':4,'y':4});b.locator('[data-object="Owned.Elements::Unit"]').get_by_role('button',name='정의 열기',exact=True).click();expect(w.locator('[aria-label="HP 기본값"]')).to_have_value('111',timeout=30000);expect(cell('Combat.Power')).to_have_value('9223372036854775805',timeout=30000)
  def receipts():
   x=flush()['presentation'];return next(row['meta']['variations'].get('dataInputs',{}) for row in x['layout'] if row['key']=='schema')
  assert not receipts(),receipts();source_same();checked('fresh saved-checkpoint projection clears only acknowledged matching Data recovery receipts; parent and other View private fields stay intact')
  # This single unsubmitted value must not be silently omitted by Review.
  cell('HP').fill('201');page.locator('[data-object="Owned.Elements::Monster"]').filter(has=page.get_by_role('button',name='Monster 편집',exact=True)).last.get_by_role('button',name='Monster 편집',exact=True).click();new=page.locator('.window[data-key^=editor-]').filter(has=page.locator('.object-title-name',has_text='Monster')).last;after=len(traffic);new.locator('[data-element-action=confirm]').click();page.wait_for_function('()=>document.querySelector("#toast")?.textContent.includes("보관된 Data 입력")');assert not any(row.get('invoke',{}).get('endpoint') in ['reviewDraft','confirmGroup'] for row in traffic[after:]);source_same();checked('original Confirm refuses to omit unsubmitted Data input, retains it in the original root archive and does not issue Review or Confirm')
  flush();stop();page.close();start(3);page=setup();page.set_viewport_size({'width':1480,'height':1050});idle();close_floating();b=page.locator('.window[data-key^="browser:project:"]');b.click(position={'x':4,'y':4});b.locator('[data-object="Owned.Elements::Unit"]').get_by_role('button',name='정의 열기',exact=True).click();w=page.locator('.window[data-key=schema]');section=w.locator('.object-variations');expect(w.locator('[aria-label="HP 기본값"]')).to_have_value('111',timeout=60000);expect(cell('HP')).to_have_value('201',timeout=30000);cell('HP').press('Escape');expect(cell('HP')).to_have_value('200',timeout=30000);expect(cell('Combat.Power')).to_have_value('9223372036854775805');source_same();checked('manual detail Save checkpoint survives actual process restart; pending201 cancels to saved200, preserving parent111 and exact long source without final Confirm')
  assert not errors and not external,(errors,external);(case/'detail-evidence.json').write_text(json.dumps({'checks':checks,'errors':errors,'actualEngine':True,'nativeWindowsOrAndroid':False},ensure_ascii=False,indent=2));print(json.dumps({'checks':checks,'evidence':str(case)},ensure_ascii=False,indent=2));page.close();stop();browser.close()
except Exception:
 try:(case/'detail-failure.json').write_text(json.dumps({'state':state(),'traffic':traffic,'errors':errors},ensure_ascii=False,indent=2))
 except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case),flush=True);raise
finally:stop()
