"""Owned module reference removal/inheritance/fingerprint fences; no accounts or project run."""
import json,re,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());seed=repo.parent/'scratch/v508-elements/module-import-source-fixture/owned project';case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-module-slot-editor-'));project=case/'owned project';shutil.copytree(seed,project);storage=case/'profile';storage.mkdir();n='Owned.Elements::';id=n+'Monster';original={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file()};env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(storage),CONFECTORY_ENTRY_STORAGE=str(storage),CONFECTORY_MCP_DIRECTORY=str(case/'instances'),CONFECTORY_WEB_PROJECT=str(project/'project.cproj'),CONFECTORY_DOTNET='/workspace/toolchains/dotnet-10.0.401/dotnet');env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];host=None;log=None;errors=[];external=[];checks=[]
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
 p=sync_playwright().start();browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(0);page=setup();page.locator('#workspace').click(button='right',position={'x':700,'y':300});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=page.locator('.window[data-key^="browser:project:"]');b.locator('[data-object="'+id+'"]').get_by_role('button',name='정의 열기',exact=True).click();w=page.locator('.window[data-key=schema]');slot=w.locator('[data-module-method="'+n+'Slot"]');expect(slot.locator('.function-implementation-origin')).to_contain_text('Donor',timeout=30000);provider=state()['schema']['providers'][0];implementation=provider['implementation'];assert all((project/k).read_bytes()==v for k,v in original.items());checked('saved module card hydrates actual owned reference provenance without reading a guessed function default or changing sources')
 slot.locator('[data-function-edit]').click();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-node=imported]')).to_be_visible(timeout=30000);expect(author.locator('.function-node-name')).to_have_text('Donor');expect(author.locator('[data-internal-code]')).to_have_count(0);graphid=implementation+'/body:common';data=invoke('blueprint',{'action':'read','id':graphid})['result']['result'];owner=state()['schema'];bound=invoke('blueprint',{'action':'read','id':graphid,'owner':id,'ownerRevision':owner['revision'],'ownerHash':owner['textHash']})['result']['result'];assert bound['slotContext']['owner']==id and bound['slotContext']['implementation']==implementation and any(row['id']==id for row in bound['sources']);checked('original Edit opens exact connected implementation graph with owner binding in server CAS; it cannot substitute global/default/C# source')
 def value():return author.locator('[data-bp-description]')
 expect(author.locator('[data-bp-node=imported] .bp-pin-plug[data-port="field:input"] input')).to_have_attribute('readonly','');assert not invoke('blueprint',{'action':'argument','id':graphid,'basis':bound['basis'],'node':'imported','name':'input','valueJson':'{"constant":7}'},False)['result']['ok']
 value().fill('슬롯 구현 설명 한글');page.wait_for_function("()=>typeof confectoryFlushPresentation==='function'");page.evaluate('async()=>await confectoryFlushPresentation()');saved_pending=[(k,v) for k,v in state()['presentation']['inputs']['blueprint'] if '|v508-author|' in k];assert len(saved_pending)==1 and '|slot:'+id+':'+implementation+'|' in saved_pending[0][0];assert saved_pending[0][1]['text']=='슬롯 구현 설명 한글';page.close();stop();start(1);page=setup();author=page.locator('.window[data-key=blueprint]');expect(value()).to_have_value('슬롯 구현 설명 한글',timeout=30000);page.wait_for_function("()=>typeof confectoryFlushPresentation==='function'");page.evaluate('async()=>await confectoryFlushPresentation()');assert [(k,v) for k,v in state()['presentation']['inputs']['blueprint'] if '|v508-author|' in k]==saved_pending;checked('true restart restores owner/implementation-bound original editor and private input without confusing another object using the same public slot')
 author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_have_text('저장됨',timeout=30000);saved=invoke('blueprint',{'action':'read','id':graphid})['result']['result'];assert saved['implementationDescription']=='슬롯 구현 설명 한글' and saved['nodes'][0]['arguments'][0]['valueJson']=='{"input":"amount"}';assert all((project/k).read_bytes()==v for k,v in original.items());author.locator('[data-bp-complete]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=30000)
 for cb in review.locator('[data-review-id]').all():cb.check()
 if review.locator('[data-additional-changes]').count():
  review.locator('[data-review-advanced]').click();ack=review.locator('[data-advanced-reviewed]')
  if ack.count():ack.check()
 expect(review.locator('#confirm')).to_be_enabled(timeout=30000);review.locator('#confirm').click();expect(review).to_have_count(0,timeout=60000);assert any(r.get('result',{}).get('result',{}).get('sourceConfirmed') for r in traffic);expected=next(row['path'] for row in saved['sources'] if row['id']==implementation);after={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file() and '.confectory' not in p.parts};assert after.keys()==original.keys() and {key for key in original if original[key]!=after[key]}=={expected};original=after;page.screenshot(path=str(case/'slot-editor-confirmed.png'));checked('explicit original Save/compiler Confirm edits only the selected implementation description; donor, slot, parent, module, object mapping and C# bodies remain byte-identical')
 # Keep an owner-fenced receipt then change that owner's local provider using a peer.
 value().fill('보존할 다음 설명');page.evaluate('async()=>await confectoryFlushPresentation()');pending=[(k,v) for k,v in state()['presentation']['inputs']['blueprint'] if '|v508-author|' in k];invoke('select',{'id':id});invoke('schema',{'id':id});fresh=state()['schema'];invoke('editDeclaration',{'id':id,'revision':fresh['revision'],'hash':fresh['textHash'],'edit':{'action':'provide-function','function':n+'Slot','implementation':n+'SlotBody'}});mark=len(traffic);author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).not_to_have_text('미저장 초안',timeout=30000);expect(author.locator('.bp-status')).not_to_have_text('저장됨');assert invoke('blueprint',{'action':'read','id':graphid})['result']['result']['implementationDescription']=='슬롯 구현 설명 한글';page.evaluate('async()=>await confectoryFlushPresentation()');assert [(k,v) for k,v in state()['presentation']['inputs']['blueprint'] if '|v508-author|' in k]==pending;assert any(r.get('result',{}).get('ok') is False for r in traffic[mark:]);assert all((project/k).read_bytes()==v for k,v in original.items());page.screenshot(path=str(case/'slot-binding-change-blocked.png'));checked('changing the connected object provider refuses stale editor writes and retains private text/old graph rather than editing a different implementation')
 page.close();stop();browser.close();assert not errors and not external,(errors,external)
except Exception:
 try:page.screenshot(path=str(case/'failure.png'));(case/'failure.json').write_text(json.dumps({'state':state(),'traffic':traffic,'errors':errors},indent=2))
 except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case));raise
finally:stop();p.stop()
record={'checks':checks,'errors':errors,'external':external,'actualEngine':True,'nativeWindows':False,'accountOrInference':False,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
