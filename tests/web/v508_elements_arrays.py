"""Actual owned element draft/Review/compiler-Confirm regression; no accounts or project execution."""
from pathlib import Path
import os,json,subprocess,tempfile,signal,time,urllib.request,sys,hashlib,uuid,re
from playwright.sync_api import sync_playwright,expect
repo=Path(sys.argv[1]).resolve();sys.path.insert(0,str(repo/'tests/web'));from editor_navigation import goto_editor
case=Path(tempfile.mkdtemp(prefix='confectory-elements-arrays-'));project=case/'owned project';project.mkdir();storage=case/'profile';storage.mkdir();n='Owned.Elements::'
items={'Main':('function','function '+n+'Main () -> int {provide '+n+'Main with '+n+'MainBody;}'),'MainBody':('implementation','implementation '+n+'MainBody for '+n+'Main () -> int {body common "Main.csbody";}'),'Vitals':('schema','schema '+n+'Vitals {field HP single general long;}'),'Stats':('schema','schema '+n+'Stats {field Speed single general int;}'),'Unit':('object','object '+n+'Unit {use schema '+n+'Vitals;data HP = 100;}'),'Monster':('object','object '+n+'Monster extends '+n+'Unit {use schema '+n+'Stats;data Speed = 2;data Counts = [9223372036854775804, 2];data Target = '+n+'Unit;data Targets = ['+n+'Unit];description "Owned monster";}'),'Slime':('object','object '+n+'Slime extends '+n+'Monster {}')}
items['Details']=('schema','schema '+n+'Details {field Power single general long;field Label single general string;}')
items['Stats']=('schema','schema '+n+'Stats {field Speed single general int;field Combat single compound '+n+'Details;field Counts multiple general long;field Target single reference '+n+'Vitals;field Targets multiple reference '+n+'Vitals;}')
items['Vitals']=('schema','schema '+n+'Vitals {field HP single general long;field Loadout single compound '+n+'Details;}')
items['Unit']=('object','object '+n+'Unit {use schema '+n+'Vitals;data HP = 100;data Loadout = {Power = 3;Label = "부모";};}')
items['Monster']=('object','object '+n+'Monster extends '+n+'Unit {use schema '+n+'Stats;data Speed = 2;data Combat = {Power = 9223372036854775804;Label = "처음";};data Counts = [9223372036854775804, 2];data Target = '+n+'Unit;data Targets = ['+n+'Unit];description "Owned monster";}')
items['Other']=('object','object '+n+'Other {use schema '+n+'Vitals;data HP = 50;}')
items['Wrong']=('object','object '+n+'Wrong {}')
items['Stats']=('schema','schema '+n+'Stats {field Speed single general int;field Combats multiple compound '+n+'Details;field Targets multiple reference '+n+'Vitals;}')
items['Monster']=('object','object '+n+'Monster extends '+n+'Unit {use schema '+n+'Stats;data Speed = 2;data Combats = [{Power = 9223372036854775804;Label = "첫째";},{Power = 2;Label = "둘째";}];data Targets = ['+n+'Unit];description "Owned monster";}')
for name,(kind,text) in items.items():(project/(name+'.celem')).write_text(text)
(project/'Main.csbody').write_text('return 0;');(project/'project.cproj').write_text('project Owned.Elements version "1" {standalone true;entry '+n+'Main;'+''.join('element '+name+' '+kind+' "'+name+'.celem";' for name,(kind,text) in items.items())+'registry Confectory.Build.DotNet "'+str(repo/'targets/dotnet/pack.cpack')+'";dependency Confectory.Build.DotNet version "0.1.0";target portable Confectory.Build.DotNet::Portable;}');original={p.name:p.read_bytes() for p in project.iterdir()};report=json.loads(Path(sys.argv[2]).resolve().read_text());env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(storage),CONFECTORY_ENTRY_STORAGE=str(storage),CONFECTORY_MCP_DIRECTORY=str(case/'instances'),CONFECTORY_WEB_PROJECT=str(project/'project.cproj'),CONFECTORY_DOTNET='/workspace/toolchains/dotnet-10.0.401/dotnet');env['PATH']=str(Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];log=(case/'host.log').open('w');host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);errors=[];external=[];checks=[];traffic=[]
try:
 for _ in range(600):
  urls=[l.split(' ',1)[1] for l in (case/'host.log').read_text().splitlines() if l.startswith('CONFECTORY_WEB_UI ')]
  if urls:break
  assert host.poll() is None,(case/'host.log').read_text();time.sleep(.05)
 url=urls[-1];origin,token=url.split('/#')
 def raw(body):return json.load(urllib.request.urlopen(urllib.request.Request(origin+'/api/request',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':token}),timeout=30))
 def observe(response):
  try:
   body=response.request.post_data_json
   if isinstance(body,dict) and body.get('op')=='invoke':traffic.append({'invoke':body,'id':body['requestId']})
   elif isinstance(body,dict) and body.get('op')=='update':
    for r in response.json().get('results',[]):traffic.append({'result':r,'id':r['requestId']})
  except Exception:pass
 def completed(endpoint,action=None):
  for _ in range(900):
   ids={r['id'] for r in traffic if r.get('invoke',{}).get('endpoint')==endpoint and (action is None or r['invoke'].get('input',{}).get('action')==action)};results=[r['result'] for r in traffic if 'result' in r and r['id'] in ids]
   good=[r for r in results if r.get('ok')]
   if good:return good[-1]
   errors=[r for r in results if not r.get('ok') and r.get('error',{}).get('code')!='stale_revision'];assert not errors,errors;page.wait_for_timeout(20)
  raise AssertionError('endpoint did not complete '+endpoint)
 def invoke(endpoint,body,success=True):
  for attempt in range(4):
   v=raw({'op':'mount'})
   if not v.get('ok'):page.wait_for_timeout(20);continue
   rid=uuid.uuid4().hex
   try:
    ack=raw({'op':'invoke','view':v['view'],'scope':v['scope'],'expectedRevision':v['revision'],'requestId':rid,'endpoint':endpoint,'input':body});assert ack['ok']
    for _ in range(600):
     u=raw({'op':'update','view':v['view'],'scope':v['scope']});r=[row for row in u.get('results',[]) if row['requestId']==rid]
     if r:break
     page.wait_for_timeout(10)
    assert r
    if r[0].get('error',{}).get('code')=='stale_revision':continue
    assert bool(r[0].get('ok')) is success,r[0];return {'result':r[0],'state':u.get('state')}
   finally:raw({'op':'dispose','view':v['view']})
  raise AssertionError('fixture action could not be admitted')
 def state():
  for _ in range(200):
   r=json.load(urllib.request.urlopen(urllib.request.Request(origin+'/api/request',data=b'{"op":"mount"}',headers={'Content-Type':'application/json','X-Confectory-Session':token}),timeout=30))
   if not r.get('ok'):time.sleep(.02);continue
   try:return r['state']
   finally:urllib.request.urlopen(urllib.request.Request(origin+'/api/request',data=json.dumps({'op':'dispose','view':r['view']}).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':token}),timeout=30).close()
  raise AssertionError('state busy')
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page(viewport={'width':1280,'height':900});page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',observe);page.route('**/*',lambda r:r.continue_() if r.request.url.startswith(origin) else (external.append(r.request.url),r.abort()));goto_editor(page,url);page.locator('#workspace').click(button='right',position={'x':700,'y':300});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=page.locator('.window[data-key^="browser:project:"]');row=b.locator('[data-object="'+n+'Monster"]');expect(row).to_be_visible(timeout=30000);row.get_by_role('button',name='정의 열기',exact=True).click();w=page.locator('.window[data-key="schema"]');expect(w.locator('.object-header')).to_be_visible(timeout=30000);w.locator('.inherited-property-source .inherited-source-toggle').click()
  def field(path):return w.locator('[data-property-path='+json.dumps(json.dumps(path,separators=(',',':')))+']')
  combats=field(['Combats']);expect(combats.locator('[data-property-type]').first).to_contain_text('여러 개');entries=combats.locator(':scope>.property-content-box>.property-multi-values>.property-multi-item');expect(entries).to_have_count(2);expect(field(['Combats',0,'Power']).locator('input')).to_have_value('9223372036854775804');expect(field(['Combats',1,'Label']).locator('input')).to_have_value('둘째')
  target=entries.last.bounding_box();entries.first.locator('.property-multi-index').drag_to(entries.last,source_position={'x':3,'y':3},target_position={'x':12,'y':target['height']-3});expect(field(['Combats',0,'Power']).locator('input')).to_have_value('2');expect(field(['Combats',1,'Power']).locator('input')).to_have_value('9223372036854775804');assert state()['draft']['revision']==0;checks.append('real rendered HTML drag reorders original compound-array items without staging, preserving exact long and Korean members')
  combats.locator(':scope>.property-content-box>.object-property-default>.property-add-value').click();expect(entries).to_have_count(3);field(['Combats',2,'Label']).locator('input').fill('셋째 "한글"');field(['Combats',2,'Power']).locator('input').fill('9223372036854775806');entries.last.focus();entries.last.press('ArrowUp');entries.nth(1).focus();entries.nth(1).press('ArrowUp');entries.nth(1).locator('.property-multi-remove').first.click();expect(entries).to_have_count(2);expect(field(['Combats',0,'Power']).locator('input')).to_have_value('9223372036854775806');expect(field(['Combats',1,'Power']).locator('input')).to_have_value('9223372036854775804');checks.append('new compound-array template member edits, keyboard order and removal retain latest input, exact long tokens and untouched siblings')
  power=field(['Combats',0,'Power']).locator('input');power.fill('');before=state()['draft'];w.locator('[data-element-action="save"]').click();expect(w.locator('[data-element-error]')).to_contain_text('형식');expect(power).to_have_value('');assert state()['draft']['revision']==before['revision'];power.fill('9223372036854775806');checks.append('invalid numeric child remains visible and blocks Save before shared mutation; correcting it preserves every other array member')
  w.locator('[data-element-action="save"]').click();completed('saveDraft');s=state();assert '9223372036854775806' in s['draft']['text'] and '9223372036854775804' in s['draft']['text'];assert all((project/k).read_bytes()==v for k,v in original.items());checks.append('actual compound-array Save checkpoints full ordered exact typed data while every final source remains unchanged')
  power.fill('9');page.wait_for_function("()=>typeof confectoryFlushPresentation==='function'");page.evaluate('async()=>await confectoryFlushPresentation()');beforePending=state()['presentation']['inputs']['schema'];assert any(v.get('path')==['Combats'] and '9' in v.get('text','') for k,v in beforePending),beforePending;basis=state()['schema'];invoke('editDescription',{'id':n+'Monster','revision':basis['revision'],'hash':basis['textHash'],'value':'다른 편집창'});invoke('schema',{'id':n+'Monster'});w.locator('[data-element-action="save"]').click();expect(w.locator('[data-element-error]')).to_contain_text('바뀌었습니다');expect(power).to_have_value('9');expect(w.locator('[data-element-action="discard"]')).to_be_enabled(timeout=30000);w.locator('[data-element-action="discard"]').click();expect(power).to_have_value('9223372036854775806');expect(field(['Combats',1,'Power']).locator('input')).to_have_value('9223372036854775804');assert all((project/k).read_bytes()==v for k,v in original.items());checks.append('external draft CAS change blocks stale array Save and retains input; explicit shared Discard restores saved order/members')
  w.locator('.object-title-name').click();expect(w.locator('[data-element-action="confirm"]')).to_be_enabled(timeout=30000);w.locator('[data-element-action="confirm"]').click();review=page.locator('.window[data-key="review"]');expect(review).to_be_visible(timeout=30000)
  for cb in review.locator('[data-review-id]').all():cb.check()
  if review.locator('[data-additional-changes]').count():
   review.locator('[data-review-advanced]').click();ack=review.locator('[data-advanced-reviewed]')
   if ack.count():ack.check()
  expect(review.locator('#confirm')).to_be_enabled(timeout=30000);review.locator('#confirm').click();result=completed('confirmGroup');assert result['result']['sourceConfirmed'] is True,result;expect(review).to_have_count(0,timeout=30000);assert all((project/k).read_bytes()==v for k,v in original.items() if k!='Monster.celem');assert '9223372036854775806' in (project/'Monster.celem').read_text();page.screenshot(path=str(case/'arrays-confirmed.png'));checks.append('explicit compiler Confirm writes only ordered Monster array data; all schemas, parent and reference sources preserved')
  assert not errors and not external,(errors,external);browser.close()
except Exception:
 if 'page' in globals():
  try:(case/'failure.json').write_text(json.dumps({'errors':errors,'traffic':traffic,'state':state()},indent=2))
  except Exception:pass
  try:page.screenshot(path=str(case/'failure.png'))
  except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case));raise
finally:
 if host.poll() is None:os.killpg(host.pid,signal.SIGTERM)
 host.wait(timeout=15);log.close()
record={'checks':checks,'errors':errors,'external':external,'actualEngine':True,'nativeWindows':False,'accountOrInference':False,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
