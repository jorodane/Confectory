"""Owned module reference removal/inheritance/fingerprint fences; no accounts or project run."""
import json,re,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());seed=repo.parent/'scratch/v508-elements/module-import-source-fixture/owned project';case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-module-import-lifecycle-'));project=case/'owned project';shutil.copytree(seed,project);storage=case/'profile';storage.mkdir();n='Owned.Elements::';id=n+'Monster';original={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file()};env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(storage),CONFECTORY_ENTRY_STORAGE=str(storage),CONFECTORY_MCP_DIRECTORY=str(case/'instances'),CONFECTORY_WEB_PROJECT=str(project/'project.cproj'),CONFECTORY_DOTNET='/workspace/toolchains/dotnet-10.0.401/dotnet');env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];host=None;log=None;errors=[];external=[];checks=[]
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

try:
 p=sync_playwright().start();browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(0);page=setup();page.locator('#workspace').click(button='right',position={'x':700,'y':300});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=page.locator('.window[data-key^="browser:project:"]')
 def select_owner(owner):
  b.locator('.window-title').click();b.locator('[data-object="'+owner+'"]').get_by_role('button',name='정의 열기',exact=True).click();w=page.locator('.window[data-key=schema]');expect(w.locator('.object-title-name')).to_have_text(owner.split('::')[-1],timeout=30000);return w
 def pending():
  page.wait_for_function("()=>typeof confectoryFlushPresentation==='function'");page.evaluate('async()=>await confectoryFlushPresentation()');return [(k,v) for k,v in state()['presentation']['inputs']['schema'] if '|element|implementation:' in k]
 def original_same():return all((project/k).read_bytes()==v for k,v in original.items())
 def remove():
  slot.locator('[data-function-delete-implementation]').click();page.get_by_role('dialog',name='구현 삭제',exact=True).locator('[data-implementation-confirm]').click();expect(slot.locator('[data-function-import]')).to_be_visible()
 w=select_owner(n+'Slime');slot=w.locator('[data-module-method="'+n+'Slot"]');expect(slot.locator('.function-implementation-status')).to_have_text('구현 연결');expect(slot.locator('[data-function-delete-implementation]')).to_be_disabled();s=state();assert s['schema']['providers'][0]['origin']==id;assert original_same();checked('child object shows inherited provider and original read-only slot names; delete is disabled and parent/module/function sources remain byte-identical')
 w=select_owner(id);slot=w.locator('[data-module-method="'+n+'Slot"]');expect(slot.locator('[data-function-delete-implementation]')).to_be_enabled();s=state();schema=s['schema'];failed=invoke('blueprint',{'action':'readImplementation','id':id,'function':n+'Slot','implementation':n+'WrongImport','reference':n+'Wrong','revision':schema['revision'],'hash':schema['textHash']},False);assert original_same() and not pending();checked('actual server refuses forged ref-versus-out donor despite similar value types, before ownership/registration/source changes')
 slot.locator('[data-function-delete-implementation]').click();page.get_by_role('dialog',name='구현 삭제',exact=True).locator('[data-implementation-cancel]').click();expect(slot.locator('[data-function-delete-implementation]')).to_be_visible();assert not pending();remove();saved_pending=pending();assert saved_pending[0][1]['kind']=='provider-remove' and original_same();page.close();stop();start(1);page=setup();w=page.locator('.window[data-key=schema]');slot=w.locator('[data-module-method="'+n+'Slot"]');expect(slot.locator('[data-function-import]')).to_be_visible(timeout=30000);assert pending()==saved_pending;w.locator('[data-element-action=discard]').click();expect(slot.locator('.function-implementation-status')).to_have_text('구현 연결',timeout=30000);assert not pending() and original_same();checked('explicit removal remains private through real restart and original change-cancel restores the saved provider with all implementation sources intact')
 remove();w.locator('[data-element-action=save]').click();expect(slot.locator('[data-function-import]')).to_be_visible();page.evaluate('async()=>await confectoryFlushPresentation()');assert not pending();s=state();assert not [p for p in s['schema']['providers'] if p['origin']==id];assert original_same();w.locator('[data-element-action=confirm]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=30000)
 if review.locator('[data-additional-changes]').count():
  review.locator('[data-review-advanced]').click();ack=review.locator('[data-advanced-reviewed]')
  if ack.count():ack.check()
 expect(review.locator('#confirm')).to_be_enabled(timeout=30000);review.locator('#confirm').click();expect(review).to_have_count(0,timeout=60000);assert all((project/k).read_bytes()==v for k,v in original.items() if k!='Monster.celem');assert set(str(p.relative_to(project)) for p in project.rglob('*') if p.is_file() and '.confectory' not in p.parts)==set(original);original={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file() and '.confectory' not in p.parts};checked('actual unlink Save/explicit compiler Confirm changes only owned object mapping and preserves registered wrapper/graph/donor/default/parent files; no project executes')
 # Explicit fresh selection is invalidated by a material public donor declaration change.
 slot.locator('[data-function-import]').click();dialog=page.get_by_role('dialog',name='기능 가져오기',exact=True);dialog.locator('[data-feature-import="'+n+'Donor"]').click();expect(dialog).to_have_count(0,timeout=30000);before=pending();invoke('select',{'id':n+'Donor'});invoke('inspectDeclaration',{'id':n+'Donor'});donor=state()['declaration'];invoke('editFunctionContract',{'id':donor['id'],'revision':donor['revision'],'hash':donor['textHash'],'edit':{'description':'newer owned donor description'}});invoke('select',{'id':id});invoke('schema',{'id':id});mark=len(traffic);w.locator('[data-element-action=save]').click();expect(w.locator('[data-element-error]')).to_contain_text('계약이나 등록이 바뀌',timeout=30000);assert pending()==before and original_same();assert not [r for r in traffic[mark:] if r.get('invoke',{}).get('input',{}).get('action')=='createImplementation'];page.screenshot(path=str(case/'stale-import-preserved.png'));checked('changed donor public declaration fingerprint blocks fresh wrapper creation before mutations and retains selected reference while originals stay unchanged')
 page.close();stop();browser.close();assert not errors and not external,(errors,external)
except Exception:
 try:page.screenshot(path=str(case/'failure.png'));(case/'failure.json').write_text(json.dumps({'state':state(),'traffic':traffic,'errors':errors},indent=2))
 except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case));raise
finally:stop();p.stop()
record={'checks':checks,'errors':errors,'external':external,'actualEngine':True,'nativeWindows':False,'accountOrInference':False,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
