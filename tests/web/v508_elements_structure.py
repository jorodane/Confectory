"""Actual owned element draft/Review/compiler-Confirm regression; no accounts or project execution."""
from pathlib import Path
import os,json,subprocess,tempfile,signal,time,urllib.request,sys,hashlib,uuid,re
from playwright.sync_api import sync_playwright,expect
repo=Path(sys.argv[1]).resolve();sys.path.insert(0,str(repo/'tests/web'));from editor_navigation import goto_editor
case=Path(tempfile.mkdtemp(prefix='confectory-elements-structure-'));project=case/'owned project';project.mkdir();storage=case/'profile';storage.mkdir();n='Owned.Elements::'
items={'Main':('function','function '+n+'Main () -> int {provide '+n+'Main with '+n+'MainBody;}'),'MainBody':('implementation','implementation '+n+'MainBody for '+n+'Main () -> int {body common "Main.csbody";}'),'Vitals':('schema','schema '+n+'Vitals {field HP single general long;}'),'Stats':('schema','schema '+n+'Stats {field Speed single general int;}'),'Unit':('object','object '+n+'Unit {use schema '+n+'Vitals;data HP = 100;}'),'Monster':('object','object '+n+'Monster extends '+n+'Unit {use schema '+n+'Stats;data Speed = 2;description "Owned monster";}'),'AltUnit':('object','object '+n+'AltUnit {use schema '+n+'Vitals;data HP = 200;}'),'Slime':('object','object '+n+'Slime extends '+n+'Monster {}')}
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
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page(viewport={'width':1280,'height':900});page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',observe);page.route('**/*',lambda r:r.continue_() if r.request.url.startswith(origin) else (external.append(r.request.url),r.abort()));goto_editor(page,url);page.locator('#workspace').click(button='right',position={'x':700,'y':300});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=page.locator('.window[data-key^="browser:project:"]');row=b.locator('[data-object="'+n+'Monster"]');expect(row).to_be_visible(timeout=30000);row.get_by_role('button',name='정의 열기',exact=True).click();w=page.locator('.window[data-key="schema"]');expect(w.locator('.object-header')).to_be_visible(timeout=30000);expect(w.locator('.object-parent-reference')).to_contain_text('Unit');expect(w.locator('[data-inherited-source="'+n+'Unit"]')).to_contain_text('HP');expect(w.locator('[aria-label="HP 기본값"]')).to_have_value('100');expect(w.locator('.own-property-body [data-property-name]')).to_have_value('Speed');expect(w.locator('[data-object="'+n+'Slime"]')).to_be_visible();page.screenshot(path=str(case/'monster-real.png'));s=state();assert s['draft']['id']==n+'Monster';checks.append('actual declaration pipeline renders Monster parent Unit, inherited HP, own Speed, child Slime')
  # Original parent picker changes local input only until Save, and excludes descendants.
  w.locator('.object-parent-change').click();picker=page.get_by_role('dialog',name='부모 변경',exact=True);expect(picker.locator('[data-parent-choice="'+n+'Slime"]')).to_have_count(0);picker.locator('[data-parent-choice="'+n+'AltUnit"]').click();expect(w.locator('.object-parent-reference')).to_contain_text('AltUnit');w.locator('[data-element-action="discard"]').click();expect(w.locator('.object-parent-reference')).to_contain_text('Unit');expect(w.locator('[data-element-action="discard"]')).to_be_disabled();assert all((project/k).read_bytes()==v for k,v in original.items());checks.append('original parent picker excludes descendants; local cancel restores parent without source writes')
  w.locator('.object-parent-change').click();page.locator('[data-parent-choice="'+n+'AltUnit"]').click();w.locator('[data-element-action="save"]').click();expect(w.locator('[aria-label="HP 기본값"]')).to_have_value('200',timeout=30000);completed('saveDraft');s=state();assert n+'AltUnit' in s['draft']['text'];assert all((project/k).read_bytes()==v for k,v in original.items());checks.append('actual validated parent change changes inherited HP and saves private checkpoint only')
  basis=s['schema'];proof={k:basis[k] for k in ['revision','textHash']}
  for parent in [n+'Slime',n+'Stats','Other::Unit']:
   failed=invoke('editObjectStructure',{'id':n+'Monster','revision':basis['revision'],'hash':basis['textHash'],'edit':{'parent':parent}},False);assert failed['state']['draft']['text']==s['draft']['text'];assert failed['state']['draft']['revision']==s['draft']['revision']
  failed=invoke('editObjectStructure',{'id':n+'Monster','revision':basis['revision']-1,'hash':basis['textHash'],'edit':{'parent':n+'Unit'}},False);assert failed['state']['draft']['revision']==s['draft']['revision'];checks.append('server rejects cycle, wrong kind, other namespace and stale object version without editing drafts')
  for fields in [[{'name':'Power','type':'long','valueJson':'1'},{'name':'Power','type':'long','valueJson':'2'}],[{'name':'Speed','type':'int','valueJson':'3'}],[{'name':'Power','type':'long','valueJson':'"wrong"'}]]:
   failed=invoke('editObjectStructure',{'id':n+'Monster','revision':basis['revision'],'hash':basis['textHash'],'edit':{'fields':fields}},False);assert failed['state']['draft']['revision']==s['draft']['revision'];assert failed['state']['draft']['text']==s['draft']['text']
  assert all((project/k).read_bytes()==v for k,v in original.items());checks.append('duplicate new/existing inherited definitions and invalid scalar type reject atomically, preserving every prior field and source')
  invoke('editField',{'id':n+'Monster','path':['HP'],'field':'HP','valueJson':'155','revision':basis['revision'],'hash':basis['textHash']});newbasis=invoke('schema',{'id':n+'Monster'})['state']['schema'];failed=invoke('editObjectStructure',{'id':n+'Monster','revision':newbasis['revision'],'hash':newbasis['textHash'],'edit':{'parent':None}},False);assert 'data HP = 155' in failed['state']['draft']['text'];checked=invoke('schema',{'id':n+'Monster'})['state']['schema'];assert checked['parent']==n+'AltUnit';expect(w.locator('[aria-label="HP 기본값"]')).to_have_value('155');expect(w.locator('[data-element-action="discard"]')).to_be_enabled(timeout=30000);w.locator('[data-element-action="discard"]').click();expect(w.locator('[aria-label="HP 기본값"]')).to_have_value('200',timeout=30000);checks.append('Root change cannot orphan explicit inherited overrides; rejected data remains, ordinary Discard restores saved parent and data')
  # Add a new property in the original row structure, including an exact long default.
  w.locator('[data-schema-add]').click();field=w.locator('[data-definition-key]').last;field.locator('[data-property-name]').fill('Power');field.locator('[data-property-type]').click();page.get_by_role('dialog',name='속성 타입 선택',exact=True).locator('[data-type="long"]').click();field=w.locator('[data-definition-key]').last;field.locator('[data-property-value]').fill('9223372036854775804');page.screenshot(path=str(case/'property-pending.png'));w.locator('[data-element-action="save"]').click();expect(w.locator('[data-property-name][value="Power"]')).to_be_visible(timeout=30000);expect(w.locator('[aria-label="Power 기본값"]')).to_have_value('9223372036854775804');s=state();assert '9223372036854775804' in s['draft']['text'];group=s['draft']['creationReviewIds'];assert n+'Monster' in group and n+'ProjectManifest' in group and len(group)==3,group;assert all((project/k).read_bytes()==v for k,v in original.items());checks.append('new scalar definition stages dedicated owned schema, attachment, exact long value and registration together; original files unchanged')
  # Cold process restart must retain the private creation owner/group and exact value.
  page.evaluate('async()=>{await confectoryFlushPresentation();}');page.close();os.killpg(host.pid,signal.SIGTERM);host.wait(timeout=15);log.close();log=(case/'host-restart.log').open('w');host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  for _ in range(600):
   urls=[l.split(' ',1)[1] for l in (case/'host-restart.log').read_text().splitlines() if l.startswith('CONFECTORY_WEB_UI ')]
   if urls:break
   assert host.poll() is None,(case/'host-restart.log').read_text();time.sleep(.05)
  url=urls[-1];origin,token=url.split('/#');page=browser.new_page(viewport={'width':1280,'height':900});page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',observe);page.route('**/*',lambda r:r.continue_() if r.request.url.startswith(origin) else (external.append(r.request.url),r.abort()));goto_editor(page,url);w=page.locator('.window[data-key="schema"]');expect(w.locator('[aria-label="Power 기본값"]')).to_have_value('9223372036854775804',timeout=30000);expect(w.locator('.object-parent-reference')).to_contain_text('AltUnit');s=state();assert set(s['draft']['creationReviewIds'])==set(group);assert all((project/k).read_bytes()==v for k,v in original.items());page.screenshot(path=str(case/'structure-restarted.png'));checks.append('cold restart restores saved parent, exact new field/default, and required object/schema/manifest review group without source writes')
  # The group cannot be published by reviewing the owner alone.
  failed=invoke('reviewGroup',{'ids':[n+'Monster'],'target':'portable'},False);assert not (project/'elements').exists();checks.append('incomplete property/schema/registration review fails closed')
  w.locator('.object-title-name').click();expect(w.locator('[data-element-action="confirm"]')).to_be_enabled(timeout=30000);w.locator('[data-element-action="confirm"]').click();page.locator('#review-creation').click();review=page.locator('.window[data-key="review"]');expect(review).to_be_visible(timeout=30000)
  for b in review.locator('input[type=checkbox][data-review-id]').all():b.check()
  if review.locator('[data-additional-changes]').count():
   review.locator('[data-review-advanced]').click();ack=review.locator('[data-advanced-reviewed]')
   if ack.count():ack.check()
  expect(review.locator('#confirm')).to_be_enabled(timeout=30000);review.locator('#confirm').click();result=completed('confirmGroup');assert result['result']['sourceConfirmed'] is True,result;expect(review).to_have_count(0,timeout=30000);assert all((project/k).read_bytes()==v for k,v in original.items() if k not in ['Monster.celem','project.cproj']);assert (project/'elements').is_dir();assert '9223372036854775804' in (project/'Monster.celem').read_text();page.screenshot(path=str(case/'structure-confirmed.png'));checks.append('explicit full grouped Review and compiler Confirm publish only Monster, new schema and manifest; parent/schema sources untouched')
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
