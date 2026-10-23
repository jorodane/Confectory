"""Actual owned Data cells: staged writes, cold recovery, and original detail entry.
Fixture-only; no user accounts, grants or inference. Native Windows/Android untested.
"""
import json,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());fixture=pathlib.Path(sys.argv[3]).resolve();assert fixture==repo.parent/'scratch/v508-elements/actual13-source-fixture'
case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-element-data-write-'));project=case/'owned project';shutil.copytree(fixture/'owned project',project,ignore=shutil.ignore_patterns('.confectory','.build'));storage=case/'profile';storage.mkdir()
n='Owned.Elements::'
(project/'Details.celem').write_text('schema '+n+'Details {field Power single general long;field Label single general string;}')
(project/'Stats.celem').write_text('schema '+n+'Stats {field Speed single general int;field Combat single compound '+n+'Details;field Counts multiple general long;field Target single reference '+n+'Vitals;}')
(project/'Vitals.celem').write_text('schema '+n+'Vitals {field HP single general long;field Loadout single compound '+n+'Details;}')
(project/'Unit.celem').write_text('object '+n+'Unit {use schema '+n+'Vitals;data HP = 100;data Loadout = {Power = 3;Label = "부모";};}')
(project/'Monster.celem').write_text('object '+n+'Monster extends '+n+'Unit {use schema '+n+'Stats;data Speed = 2;data Combat = {Power = 9223372036854775804;Label = "처음";};data Counts = [9223372036854775804, 2];data Target = '+n+'Unit;description "Owned monster";}')
manifest=(project/'project.cproj').read_text();(project/'project.cproj').write_text(manifest.replace('registry Confectory.Build.DotNet','element Details schema "Details.celem";registry Confectory.Build.DotNet',1))
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
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(0);page=setup();page.set_viewport_size({'width':1480,'height':1050});page.locator('#workspace').click(button='right',position={'x':700,'y':100});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=page.locator('.window[data-key^="browser:project:"]');q=b.locator('[data-browser-control="object-query"]');expect(q).to_be_enabled();q.fill('Unit');b.locator('[data-browser-control="object-search"]').click();b.locator('[data-object="Owned.Elements::Unit"]').get_by_role('button',name='정의 열기',exact=True).click();w=page.locator('.window[data-key=schema]');expect(w.locator('[aria-label="HP 기본값"]')).to_have_value('100',timeout=30000);section=w.locator('.object-variations');idle();section.locator('[data-density="100"]').click();cell=lambda name:section.get_by_role('spinbutton',name='Monster '+name,exact=True);expect(cell('HP')).to_have_value('100',timeout=30000);expect(cell('Combat.Power')).to_have_value('9223372036854775804');section.locator('[data-object="Owned.Elements::Monster"]').get_by_role('button',name='Monster 편집',exact=True).click();old=page.locator('.window[data-key=editor-1]');expect(old.locator('[aria-label="HP 기본값"]')).to_have_value('100',timeout=30000);old.locator('[aria-label="HP 기본값"]').fill('150');old.locator('[data-close]').click();w.click(position={'x':4,'y':4});w.locator('[aria-label="HP 기본값"]').fill('111');idle();before=invoke('browserElements',{'ids':['Owned.Elements::Monster']})['result']['result']['rows'][0];cell('HP').fill('200');after=len(traffic);cell('HP').press('Enter');result=wait_operation('editBrowserElement',after);assert result['result']['accepted'];assert injected==1;assert result['result']['row']['id']=='Owned.Elements::Monster';assert result['result']['row']['revision']>before['revision'];expect(w.locator('[aria-label="HP 기본값"]')).to_have_value('111');s0=flush();assert any('|view:1|element|' in key and value.get('text')=='150' for key,value in s0['presentation']['inputs']['schema']);assert state()['draft']['id']=='Owned.Elements::Unit';source_same();checked('actual Data scalar Enter stages only owned Monster HP200 after one rejected transport admission, retaining parent111 and another window HP150 without final source writes')
  idle();cell('HP').fill('201');count=sum(r.get('invoke',{}).get('endpoint')=='editBrowserElement' for r in traffic);cell('HP').press('Escape');expect(cell('HP')).to_have_value('200',timeout=30000);assert sum(r.get('invoke',{}).get('endpoint')=='editBrowserElement' for r in traffic)==count;source_same();checked('Escape cancels an unsubmitted Data edit and rereads the actual staged value without reverting another window or issuing a write')
  stale=invoke('editBrowserElement',{'id':'Owned.Elements::Monster','column':'data:["HP"]','valueJson':'999','version':{key:before[key] for key in ['revision','textHash','viewHash']}})['result']['result'];assert stale.get('accepted') is False and stale['code']=='element-value-stale';current=invoke('browserElements',{'ids':['Owned.Elements::Monster']})['result']['result']['rows'][0];assert next(f for f in current['fields'] if f['column']=='data:["HP"]')['valueJson']=='200';invoke('editBrowserElement',{'id':'Other.Project::Unit','column':'data:["HP"]','valueJson':'999','version':{key:current[key] for key in ['revision','textHash','viewHash']}},False);invoke('editBrowserElement',{'id':'Owned.Elements::Monster','column':'data:["Loadout","Power"]','valueJson':'999','version':{key:current[key] for key in ['revision','textHash','viewHash']}},False);source_same();checked('server refuses old displayed proof, foreign objects and inherited compound child writes that require explicit parent override')
  w.click(position={'x':4,'y':4});idle();cell('Speed').fill('2.5');after=len(traffic);cell('Speed').press('Enter');bad=wait_any('editBrowserElement',after);assert bad.get('ok') is False or bad.get('result',{}).get('accepted') is False;expect(cell('Speed')).to_have_value('2.5');expect(cell('Speed')).to_have_attribute('aria-invalid','true');cell('Speed').fill('3');after=len(traffic);cell('Speed').press('Enter');good=wait_operation('editBrowserElement',after);assert good['result']['accepted'];assert next(f for f in good['result']['row']['fields'] if f['column']=='data:["Speed"]')['valueJson']=='3';source_same();checked('typed int rejection preserves invalid Data text and explicit corrected retry stages3 through unchanged schema validation')
  idle();cell('Combat.Power').fill('9223372036854775805');after=len(traffic);cell('Combat.Power').press('Enter');good=wait_operation('editBrowserElement',after);assert next(f for f in good['result']['row']['fields'] if f['column']=='data:["Combat","Power"]')['valueJson']=='9223372036854775805';count=sum(r.get('invoke',{}).get('endpoint')=='editBrowserElement' for r in traffic);cell('Combat.Power').press('Enter');page.evaluate('()=>Promise.resolve()');assert sum(r.get('invoke',{}).get('endpoint')=='editBrowserElement' for r in traffic)==count;idle();label=section.get_by_role('textbox',name='Monster Combat.Label',exact=True);label.fill('재시작 한글');flush();stop();page.close();cold_start=len(traffic);start(1);page=setup();page.set_viewport_size({'width':1480,'height':1050});w=page.locator('.window[data-key=schema]');expect(w.locator('[aria-label="HP 기본값"]')).to_have_value('111',timeout=60000);section=w.locator('.object-variations');label=section.get_by_role('textbox',name='Monster Combat.Label',exact=True);expect(label).to_have_value('재시작 한글',timeout=30000);assert not any(row.get('invoke',{}).get('endpoint')=='editBrowserElement' for row in traffic[cold_start:]);label.press('Escape');expect(label).to_have_value('처음',timeout=30000);expect(section.get_by_role('spinbutton',name='Monster Combat.Power',exact=True)).to_have_value('9223372036854775805');source_same();checked('exact 64-bit nested Data value and private Korean text survive isolated process stop/restart; restart does not auto-apply and Escape preserves the actual old label')
  # Cold rendering keeps acknowledged but unsaved intent, and only explicit Enter
  # reapplies it against a previously observed exact own rollback snapshot.
  for field in ['HP','Speed','Combat.Power']:
   control=section.get_by_role('spinbutton',name='Monster '+field,exact=True);after=len(traffic);control.press('Enter');assert wait_operation('editBrowserElement',after)['result']['accepted'];idle()
  proof=invoke('browserElements',{'ids':[n+'Monster']})['result']['result']['rows'][0];assert next(f for f in proof['fields'] if f['column']=='data:["HP"]')['valueJson']=='200';assert next(f for f in proof['fields'] if f['column']=='data:["Speed"]')['valueJson']=='3';source_same();checked('cold acknowledged intents require explicit retry against known own snapshots; HP200, Speed3 and exact long5805 recover without auto-save or final writes')
  idle();w.click(position={'x':4,'y':4});root=section.locator('[data-object="Owned.Elements::Monster"]');detail=root.locator('.browser-data-field').filter(has=page.locator('.browser-property-label',has_text='Counts')).get_by_role('button',name='2개 값 · 편집',exact=True);detail.click();new=page.locator('.window[data-key=editor-2]');expect(new.locator('.object-title-name')).to_have_text('Monster',timeout=30000);array=new.locator('section[data-property-path]').filter(has=page.get_by_role('button',name='Counts 값 펼치기/접기',exact=True));expect(array.locator('.property-multi-values')).to_be_visible();expect(array.locator('input[data-property-value]')).to_have_count(2);expect(new.locator('[aria-label="HP 기본값"]')).to_have_value('200');assert any('|view:1|element|' in key and value.get('text')=='150' for key,value in flush()['presentation']['inputs']['schema']);array.locator('input[data-property-value]').first.fill('9223372036854775806');after=len(traffic);new.locator('[data-element-action=save]').click();wait_operation('saveEditorView',after);expect(new.locator('[data-element-error]')).to_have_text('');expect(w.locator('[aria-label="HP 기본값"]')).to_have_value('111');source_same();page.screenshot(path=str(case/'actual-data-and-array-detail.png'));checked('original detail opens a separate bound window at expanded Counts, preserves another window stale input, and saves exact array edit through existing element CAS without final Confirm')
  assert not errors and not external,(errors,external);(case/'evidence.json').write_text(json.dumps({'checks':checks,'errors':errors,'actualEngine':True,'nativeWindowsOrAndroid':False,'evidence':str(case)},ensure_ascii=False,indent=2));print(json.dumps({'checks':checks,'errors':errors,'evidence':str(case)},ensure_ascii=False,indent=2));page.close();stop();browser.close()
except Exception:
 try:(case/'failure.json').write_text(json.dumps({'state':state(),'traffic':traffic,'errors':errors},ensure_ascii=False,indent=2))
 except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case),flush=True);raise
finally:stop()
