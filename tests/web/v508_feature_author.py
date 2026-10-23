"""Actual owned element draft/Review/compiler-Confirm regression; no accounts or project execution."""
from pathlib import Path
import os,json,subprocess,tempfile,signal,time,urllib.request,sys,hashlib,uuid,re
from playwright.sync_api import sync_playwright,expect
repo=Path(sys.argv[1]).resolve();sys.path.insert(0,str(repo/'tests/web'));from editor_navigation import goto_editor
case=Path(tempfile.mkdtemp(prefix='confectory-feature-author-'));project=case/'owned project';project.mkdir();storage=case/'profile';storage.mkdir();n='Owned.Elements::'
items={'Main':('function','function '+n+'Main () -> int {provide '+n+'Main with '+n+'MainBody;}'),'MainBody':('implementation','implementation '+n+'MainBody for '+n+'Main () -> int {body common "Main.csbody";}'),'Vitals':('schema','schema '+n+'Vitals {field HP single general long;}'),'Stats':('schema','schema '+n+'Stats {field Speed single general int;}'),'Unit':('object','object '+n+'Unit {use schema '+n+'Vitals;data HP = 100;}'),'Monster':('object','object '+n+'Monster extends '+n+'Unit {use schema '+n+'Stats;data Speed = 2;description "Owned monster";}'),'Slime':('object','object '+n+'Slime extends '+n+'Monster {}')}
items['Attack']=('function','function '+n+'Attack (long amount) -> long {provide '+n+'Attack with '+n+'AttackBody;}')
items['AttackBody']=('implementation','implementation '+n+'AttackBody for '+n+'Attack (long amount) -> long {body common "Attack.csbody";}')
items['Rules']=('module','module '+n+'Rules {require '+n+'Attack (long) -> long;default '+n+'Attack with '+n+'AttackBody;}')
(project/'Attack.csbody').write_text('return amount + 1;')
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
 def checked(text):
  checks.append(text);(case/'progress.json').write_text(json.dumps(checks,indent=2));print('PASS '+text,flush=True)
 def state():
  for _ in range(200):
   r=json.load(urllib.request.urlopen(urllib.request.Request(origin+'/api/request',data=b'{"op":"mount"}',headers={'Content-Type':'application/json','X-Confectory-Session':token}),timeout=30))
   if not r.get('ok'):time.sleep(.02);continue
   try:return r['state']
   finally:urllib.request.urlopen(urllib.request.Request(origin+'/api/request',data=json.dumps({'op':'dispose','view':r['view']}).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':token}),timeout=30).close()
  raise AssertionError('state busy')
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page(viewport={'width':1280,'height':900});page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',observe);page.route('**/*',lambda r:r.continue_() if r.request.url.startswith(origin) else (external.append(r.request.url),r.abort()));goto_editor(page,url);page.locator('#workspace').click(button='right',position={'x':700,'y':300});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=page.locator('.window[data-key^="browser:project:"]');expect(b).to_be_visible(timeout=30000)
  b.locator('[data-tab=feature]').click();before=state();b.locator('[data-new]').click();page.get_by_role('button',name='기능 생성',exact=True).click();dialog=page.get_by_role('dialog',name='새 기능 만들기',exact=True);expect(dialog.locator('#object-name')).to_be_visible();expect(dialog).to_contain_text('소유 팩 · ProjectPack');expect(dialog.get_by_role('button',name='생성',exact=True)).to_be_visible();dialog.locator('#object-name').fill('Cancelled');dialog.locator('[data-close]').click();assert state()['draft']['text']==before['draft']['text'];assert all((project/k).read_bytes()==v for k,v in original.items());checked('original new-feature dialog cancels without adding a declaration, registration or final file')
  b.locator('[data-new]').click();page.get_by_role('button',name='기능 생성',exact=True).click();dialog=page.get_by_role('dialog',name='새 기능 만들기',exact=True);dialog.locator('#object-name').fill('Spell');dialog.get_by_role('button',name='생성',exact=True).click();expect(dialog).to_have_count(0,timeout=30000);w=page.locator('.window[data-key=declaration]');expect(w.locator('.object-title-name')).to_have_text('Spell',timeout=30000);expect(w.locator('.standalone-feature-definition')).to_be_visible();expect(w.locator('[data-feature-action=save]')).to_be_enabled(timeout=30000);s=state();assert s['draft']['id']==n+'Spell' and s['draft']['creationReviewIds'];assert not (project/'elements/Spell.celem').exists();assert all((project/k).read_bytes()==v for k,v in original.items());checked('explicit creation stages real owned function and registration atomically and opens original feature frame without a generic source form')
  w.locator('[data-inline-description]').fill('새 주문 설명');w.locator('[data-feature-action=save]').click();expect(w.locator('[data-feature-action=save]')).to_be_enabled(timeout=30000)
  for _ in range(600):
   s=state()
   if (s.get('declaration') or {}).get('description')=='새 주문 설명':break
   page.wait_for_timeout(20)
  assert s['declaration']['description']=='새 주문 설명';assert all((project/k).read_bytes()==v for k,v in original.items());page.screenshot(path=str(case/'new-feature-saved.png'));checked('new owned function description Save preserves required creation review group and leaves all final files unchanged; body remains unimplemented')
  w.locator('[data-function-write-direct]').click();author=page.locator('.window[data-key=blueprint]');expect(author.locator('.blueprint-editor')).to_be_visible(timeout=30000);expect(author.locator('.bp-entry-wall')).to_be_visible();expect(author.locator('.bp-function-card')).to_have_count(1);expect(author.locator('[data-inline-description]')).to_have_value('새 주문 설명');assert all((project/k).read_bytes()==v for k,v in original.items());checked('original Blueprint canvas/action-card/Script control opens over new function contract without creating graph files or invoking AI')
  author.locator('[data-inline-description]').fill('실제 노드 설명');author.locator('[data-internal-code]').click();script=page.get_by_role('dialog',name='C# Script · Spell',exact=True);code=script.locator('[data-code-source]');expect(code).to_contain_text('')
  original_code=code.input_value();code.press('Control+Home');code.press('Delete');expect(code).to_have_value(original_code);expect(script.locator('[data-code-status]')).to_contain_text('고정된 선언');code.evaluate("(el,delimiter)=>{const at=el.value.indexOf(delimiter)+3;el.setSelectionRange(at,at)}", "\n{\n");page.keyboard.insert_text('return 7;');script.locator('[data-code-cancel]').click();author.locator('[data-internal-code]').click();script=page.get_by_role('dialog',name='C# Script · Spell',exact=True);code=script.locator('[data-code-source]');assert 'return 7;' not in code.input_value();checked('original Script popup protects fixed signature/scaffolding; cancel retains original body and pending natural-language node description')
  code.evaluate("(el,delimiter)=>{const at=el.value.indexOf(delimiter)+3;el.setSelectionRange(at,at)}", "\n{\n");page.keyboard.insert_text('return 7;');script.locator('[data-code-save]').click();author.locator('[data-bp-save]').click();expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);expect(author.locator('.bp-status')).to_have_text('저장됨',timeout=30000);rows=invoke('blueprint',{'action':'list','feature':n+'Spell'})['result']['result']['rows'];assert len(rows)==1;graph=invoke('blueprint',{'action':'read','id':rows[0]['id']})['result']['result'];assert graph['nodes'][0]['intent']=='실제 노드 설명';assert graph['nodes'][0]['source']=='return 7;';assert graph['diagnostics']['state']=='source-ready';assert all((project/k).read_bytes()==v for k,v in original.items());page.screenshot(path=str(case/'original-author-saved.png'));checked('original author Save creates actual owned graph/implementation/node/registration and checkpoints intent/body with receipt/CAS; final sources unchanged and no execution')
  author.locator('[data-bp-complete]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=30000)
  if review.locator('[data-additional-changes]').count():
   review.locator('[data-review-advanced]').click();ack=review.locator('[data-advanced-reviewed]')
   if ack.count():ack.check()
  expect(review.locator('#confirm')).to_be_enabled(timeout=30000);review.locator('#confirm').click();expect(review).to_have_count(0,timeout=60000);assert all((project/k).read_bytes()==v for k,v in original.items() if k!='project.cproj');assert (project/'elements/Spell.celem').exists();assert any(source['kind']=='blueprint' for source in graph['sources']);assert any(source['kind']=='blueprint-node' for source in graph['sources']);assert all(hashlib.sha256((project/source['path']).read_bytes()).hexdigest()==source['hash'] for source in graph['sources']);checked('explicit complete then grouped Review/compiler Confirm publishes new typed function implementation and owned sources without running the project')
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
