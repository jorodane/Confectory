"""v536 non-destructive Browser deletion/recovery in an isolated actual engine.
No account/grant/model invocation. Preserves source bytes and original draft proof.
"""
import json,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());fixture=pathlib.Path(sys.argv[3]).resolve();assert fixture==repo.parent/'scratch/v508-elements/actual13-source-fixture'
case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-element-mutation-'));project=case/'owned project';shutil.copytree(fixture/'owned project',project,ignore=shutil.ignore_patterns('.confectory','.build'));(project/'Other.celem').write_bytes(bytes([239,187,191])+b'object Owned.Elements::Other extends Owned.Elements::Unit {data HP = 50;}');(project/'project.cproj').write_text((project/'project.cproj').read_text().replace('registry Confectory.Build.DotNet','element Other object "Other.celem";registry Confectory.Build.DotNet',1));(project/'Third.celem').write_text('object Owned.Elements::Third extends Owned.Elements::Unit {data HP = 60;}');(project/'project.cproj').write_text((project/'project.cproj').read_text().replace('registry Confectory.Build.DotNet','element Third object \"Third.celem\";registry Confectory.Build.DotNet',1));
for name,source in [('GroupA','category Owned.Elements::GroupA {contain object Owned.Elements::Third;}'),('GroupB','category Owned.Elements::GroupB {}'),('Nested','category Owned.Elements::Nested {value editorFolder = "Owned.Elements::GroupA";}')]:
 (project/(name+'.celem')).write_bytes((bytes([239,187,191]) if name=='GroupA' else b'')+source.encode());(project/'project.cproj').write_text((project/'project.cproj').read_text().replace('registry Confectory.Build.DotNet','element '+name+' category "'+name+'.celem";registry Confectory.Build.DotNet',1))
(project/'Other.celem').write_bytes(bytes([239,187,191])+b'object Owned.Elements::Other extends Owned.Elements::Unit {data HP = 50;value editorFolder = "Owned.Elements::GroupA";}')
storage=case/'profile';storage.mkdir();original={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file() and '.confectory' not in p.parts};id='Owned.Elements::Serial';text='9223372036854775804';description='재시작할 미적용 설명 한글';env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(storage),CONFECTORY_ENTRY_STORAGE=str(storage),CONFECTORY_MCP_DIRECTORY=str(case/'instances'),CONFECTORY_WEB_PROJECT=str(project/'project.cproj'),CONFECTORY_DOTNET=env.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet'));env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];host=None;log=None;errors=[];external=[];checks=[]
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

def source_same():assert all((project/k).read_bytes()==v for k,v in original.items())
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
def focus_window(win):
 point=win.evaluate("""el=>{const r=el.getBoundingClientRect();for(let y=r.top+5;y<Math.min(innerHeight-5,r.bottom-5);y+=20)for(let x=r.left+5;x<Math.min(innerWidth-5,r.right-5);x+=20){const at=document.elementFromPoint(x,y);if(at?.closest('.window')===el&&!at.closest('button,input,textarea,select,[data-resize]'))return {x,y};}return null;}""");assert point;page.mouse.click(point['x'],point['y'])
def definition(name):
 idle();focus_window(b);q=b.locator('[data-browser-control="object-query"]');q.fill(name);b.locator('[data-browser-control="object-search"]').click();expect(q).to_have_value(name);b.locator('[data-object="Owned.Elements::'+name+'"]').click(button='right');page.get_by_role('button',name='스키마 열기',exact=True).click();expect(w.locator('.object-title-name')).to_have_text(name,timeout=30000);idle();focus_window(w)
def drop(source,target):
 transfer=page.evaluate_handle('()=>new DataTransfer()');source.dispatch_event('dragstart',{'dataTransfer':transfer});target.dispatch_event('dragover',{'dataTransfer':transfer});target.dispatch_event('drop',{'dataTransfer':transfer})
def edit_description(name,text):
 import hashlib
 invoke('select',{'id':'Owned.Elements::'+name});unit=state()['draft'];invoke('editDeclaration',{'id':unit['id'],'revision':unit['revision'],'hash':hashlib.sha256(unit['text'].encode()).hexdigest(),'edit':{'action':'properties','values':{'description':text}}})
def plan():
 result=invoke('planBrowserRemoval',{'ids':['Owned.Elements::Other']})['result']['result'];assert result['state']=='planned';return result['token']
def archive(action,token):return invoke('browserRetirement',{'action':action,'token':token})['result']['result']
def confirm(ids):
 invoke('select',{'id':manifest});invoke('reviewGroup',{'ids':ids,'target':'portable'});review=state()['review'];assert {row['id'] for row in review['units']}==set(ids);result=invoke('confirmGroup',{'ids':ids,'token':review['token']})['result']['result'];assert result['sourceConfirmed'],result
def filter_name(name):
 idle();focus_window(b);q=b.locator('[data-browser-control="object-query"]');q.fill(name);b.locator('[data-browser-control="object-search"]').click();expect(q).to_have_value(name)
def deletion(name):
 filter_name(name);b.locator('[data-object="Owned.Elements::'+name+'"]').click(button='right');page.get_by_role('button',name='삭제',exact=True).click();return page.locator('.modal')
def preserved():
 assert any('Owned.Elements::Unit|element|' in key and value.get('text')=='111' for key,value in flush()['presentation']['inputs']['schema'])
def ui_confirm():
 idle();focus_window(b);b.locator('[data-browser-confirm]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=60000);return review

def accept(review):
 if review.locator('[data-additional-changes]').count():
  review.locator('[data-review-advanced]').click();ack=review.locator('[data-advanced-reviewed]')
  if ack.count():ack.check()
 after=len(traffic);review.locator('#confirm').click();result=wait_operation('confirmGroup',after);assert result['result']['sourceConfirmed'];expect(review).to_be_hidden(timeout=60000)
def wait_draft_action(action,after):
 for _ in range(3000):
  ids={r['invoke']['requestId'] for r in traffic[after:] if r.get('invoke',{}).get('endpoint')=='browserDrafts' and r['invoke']['input'].get('action')==action};results=[r['result'] for r in traffic[after:] if r.get('result',{}).get('requestId') in ids];good=[r for r in results if r.get('ok')]
  if good:return good[-1]
  bad=[r for r in results if r.get('error',{}).get('code')!='stale_revision'];assert not bad,bad;page.wait_for_timeout(10)
 raise AssertionError('Browser action did not finish: '+action)
def folder_drop(name,category):
 filter_name(name);source=b.locator('[data-object="Owned.Elements::'+name+'"]');target=b.locator('[data-tree-id="Owned.Elements::'+category+'"]');after=len(traffic);drop(source,target);wait_operation('moveBrowserFolders',after);return state()
def tree_parent(name):
 return b.evaluate("""(el,id)=>{const rows=[...el.querySelectorAll('[data-tree-key]')],index=rows.findIndex(row=>row.dataset.treeKey==='decl:Owned.Elements::'+id),row=rows[index];if(!row)return null;const level=Number(row.getAttribute('aria-level'));for(let i=index-1;i>=0;i--)if(Number(rows[i].getAttribute('aria-level'))===level-1)return rows[i].dataset.treeKey;return null;}""",name)
def folder_node(name):return next(row for row in state()['relationsMap']['nodes'] if row['id']=='Owned.Elements::'+name)
def level(name):return int(b.locator('[data-tree-key="decl:Owned.Elements::'+name+'"]').get_attribute('aria-level'))
def current_other():
 invoke('select',{'id':'Owned.Elements::Other'});return state()['draft']
def preserved():
 assert any('Owned.Elements::Unit|element|' in key and value.get('text')=='112' for key,value in flush()['presentation']['inputs']['schema'])
def source(name):
 invoke('select',{'id':'Owned.Elements::'+name});return state()['draft']['text']
def node(name):return b.locator('[data-tree-key="decl:Owned.Elements::'+name+'"]')
def staged_nested():
 folder_drop('GroupA','GroupB');expect(node('GroupA')).to_have_attribute('aria-level',str(level('GroupB')+1));expect(node('Nested')).to_have_attribute('aria-level',str(level('GroupA')+1));expect(node('Other')).to_have_attribute('aria-level',str(level('GroupA')+1));assert tree_parent('GroupA')=='decl:Owned.Elements::GroupB';assert tree_parent('Nested')=='decl:Owned.Elements::GroupA';assert tree_parent('Other')=='decl:Owned.Elements::GroupA';assert folder_node('GroupA')['folder']=='Owned.Elements::GroupB';assert 'contain object Owned.Elements::Third' in source('GroupA');assert 'extends Owned.Elements::Unit' in source('Other');assert state()['folderMove']['movingIds']==['Owned.Elements::GroupA'];source_same();preserved()
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(0);page=setup();page.set_viewport_size({'width':1480,'height':1050});idle();page.locator('#workspace').click(button='right',position={'x':700,'y':100});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=page.locator('.window[data-key^="browser:project:"]');w=page.locator('.window[data-key=schema]');definition('Unit');w.locator('[aria-label="HP 기본값"]').fill('112');edit_description('Monster','unrelated shared fixture draft');invoke('saveDraft',{});staged_nested();before=state()['folderMove'];filter_name('GroupB');after=len(traffic);drop(b.locator('[data-object="Owned.Elements::GroupB"]'),b.locator('[data-tree-id="Owned.Elements::Nested"]'));failed=wait_any('moveBrowserFolders',after);assert not failed['ok'];assert state()['folderMove']==before;assert 'editorFolder' not in source('GroupB');assert 'editorFolder = "Owned.Elements::GroupB"' in source('GroupA');source_same();preserved();checked('actual category nesting moves the full displayed subtree without rewriting descendants/typed contains/inheritance/namespace; cyclic follow-up fails with no partial state')
  idle();focus_window(b);after=len(traffic);b.locator('[data-browser-discard]').click();wait_draft_action('discard',after);idle();assert state()['folderMove'] is None;assert 'editorFolder' not in source('GroupA');source_same();preserved();assert 'unrelated shared fixture draft' in source('Monster');checked('category group Cancel restores the previous hierarchy while preserving saved unrelated shared draft and private112')
  staged_nested();idle();focus_window(b);after=len(traffic);b.locator('[data-browser-save]').click();wait_draft_action('save',after);idle();flush();page.close();stop();start(1);page=setup();page.set_viewport_size({'width':1480,'height':1050});b=page.locator('.window[data-key^="browser:project:"]');w=page.locator('.window[data-key=schema]');filter_name('GroupA');assert state()['folderMove'];assert level('GroupA')==level('GroupB')+1;assert level('Nested')==level('GroupA')+1;preserved();source_same();review=ui_confirm();assert {r['id'] for r in state()['review']['units']}=={'Owned.Elements::GroupA','Owned.Elements::GroupB'};review.locator('[data-reject]').click();expect(review).to_be_hidden();source_same();review=ui_confirm();accept(review);idle();assert state()['folderMove'] is None;assert 'editorFolder = "Owned.Elements::GroupB"' in (project/'GroupA.celem').read_text();assert 'contain object Owned.Elements::Third' in (project/'GroupA.celem').read_text();assert all((project/k).read_bytes()==v for k,v in original.items() if k!='GroupA.celem');preserved();assert 'unrelated shared fixture draft' in source('Monster');page.screenshot(path=str(case/'category-nested-confirmed.png'));checked('saved category nesting survives restart and Review cancel; explicit compiler Confirm changes only the category, retaining all descendant files and unrelated inputs')
  assert not errors and not external,(errors,external);(case/'nested-success.json').write_text(json.dumps({'checks':checks,'originalKeys':list(original),'confirmed':['GroupA'],'pendingPrivate':'112','nativeWindows':False},ensure_ascii=False,indent=2));print(json.dumps({'checks':checks,'case':str(case),'nativeWindows':False,'nativeTouch':False},ensure_ascii=False,indent=2));page.close();stop();browser.close()
except Exception:
 try:(case/'folder-nested-failure.json').write_text(json.dumps({'state':state(),'traffic':traffic,'errors':errors},ensure_ascii=False,indent=2))
 except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case),flush=True);raise
finally:stop()
