"""v536 embedded Browser parent movement in an isolated actual engine.
No account/grant/model invocation. Preserves source bytes and original draft proof.
"""
import json,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());fixture=pathlib.Path(sys.argv[3]).resolve();assert fixture==repo.parent/'scratch/v508-elements/actual13-source-fixture'
case=pathlib.Path(sys.argv[4]).resolve();assert str(case).startswith('/tmp/confectory-element-mutation-');project=case/'owned project';storage=case/'profile';original={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file() and '.confectory' not in p.parts};id='Owned.Elements::Serial';text='9223372036854775804';description='재시작할 미적용 설명 한글';env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(storage),CONFECTORY_ENTRY_STORAGE=str(storage),CONFECTORY_MCP_DIRECTORY=str(case/'instances'),CONFECTORY_WEB_PROJECT=str(project/'project.cproj'),CONFECTORY_DOTNET=env.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet'));env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];host=None;log=None;errors=[];external=[];checks=[]
def stop():
 global host,log
 if host and host.poll() is None:os.killpg(host.pid,signal.SIGTERM)
 if host:host.wait(timeout=15)
 if log:log.close()
def start(i):
 global host,log,origin,token,url
 file=case/f'host-category-final-{"resume-setup" if "--resume-setup" in sys.argv else "initial"}-{i}.log';log=file.open('w');host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
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
def raw_source(name):return source(name)
def proof(name):
 row=folder_node(name);return {'id':row['id'],'revision':row['revision'],'hash':row['textHash']}
def move_payload(name,folder):
 value=proof(name);target=folder_node(folder) if folder else None;return {**value,'folder':target['id'] if target else None,'folderRevision':target['revision'] if target else None,'folderHash':target['textHash'] if target else None}
def checkpoint(stage):
 (case/'multi-root-progress.json').write_text(json.dumps({'stage':stage,'checks':checks},ensure_ascii=False,indent=2))
def same_except(ids):assert all((project/k).read_bytes()==v for k,v in original.items() if k not in ids)
def choose_multi():
 definition('Unit');section=w.locator('.object-variations');other=section.locator('[data-object="Owned.Elements::Other"]');third=section.locator('[data-object="Owned.Elements::Third"]');other.click();third.click(modifiers=['Control']);assert section.locator('[data-object][aria-selected=true]').count()==2;return other

def multi_drop():
 other=choose_multi();after=len(traffic);drop(other,b.locator('[data-tree-id="Owned.Elements::GroupB"]'));wait_operation('moveBrowserFolders',after);expect(node('Other')).to_have_attribute('aria-level',str(level('GroupB')+1));expect(node('Third')).to_have_attribute('aria-level',str(level('GroupB')+1));assert tree_parent('Other')=='decl:Owned.Elements::GroupB';assert tree_parent('Third')=='decl:Owned.Elements::GroupB';assert set(state()['folderMove']['movingIds'])=={'Owned.Elements::Other','Owned.Elements::Third'};assert 'extends Owned.Elements::Unit' in raw_source('Other');assert 'extends Owned.Elements::Unit' in raw_source('Third');preserved()
def namespace_drop(name,namespace):
 filter_name(name);after=len(traffic);drop(b.locator('[data-object="Owned.Elements::'+name+'"]'),b.locator('[data-namespace="'+namespace+'"]'));return wait_any('moveBrowserFolders',after)
def reopen(i):
 global page,b,w
 idle();flush();page.close();stop();start(i);page=setup();page.set_viewport_size({'width':1480,'height':1050});b=page.locator('.window[data-key^="browser:project:"]');w=page.locator('.window[data-key=schema]');idle()
try:
 assert (case/'nested-success.json').exists(),'consume only the successfully completed category nesting fixture'
 if (case/'multi-root-progress.json').exists():
  prior=json.loads((case/'multi-root-progress.json').read_text());failure=json.loads((case/'folder-multi-root-failure.json').read_text());assert '--resume-setup' in sys.argv and prior['stage']=='started' and prior['checks']==[]
  assert not any(row.get('invoke',{}).get('endpoint') in ['moveBrowserFolders','editDeclaration','editObjectStructure','confirmGroup','saveDraft'] for row in failure['traffic']),'an authoring operation was attempted; inspect outcome first'
  assert not (case/'multi-root-setup-retry.json').exists(),'setup retry is single-use'
  (case/'multi-root-setup-retry.json').write_text(json.dumps({'reason':'read authoritative relations after hydration; first attempt stopped before authoring'}))
 checkpoint('started')
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(0);page=setup();page.set_viewport_size({'width':1480,'height':1050});b=page.locator('.window[data-key^="browser:project:"]');w=page.locator('.window[data-key=schema]');idle();invoke('relationsMap',{});preserved();assert tree_parent('GroupA')=='decl:Owned.Elements::GroupB';assert state()['folderMove'] is None;old=[move_payload('Other','GroupB'),move_payload('Third','GroupB')];before=raw_source('Other');edit_description('Third','newer preserved third draft');invoke('moveBrowserFolders',{'moves':old},False);assert state()['folderMove'] is None;assert raw_source('Other')==before;assert 'newer preserved third draft' in raw_source('Third');source_same();preserved();invoke('saveDraft',{});checked('actual two-source classification rejects a genuinely stale second source atomically, keeping both the first source and newer second-source draft intact');checkpoint('stale-batch-rejected')
  multi_drop();source_same();idle();focus_window(b);after=len(traffic);b.locator('[data-browser-discard]').click();wait_draft_action('discard',after);idle();assert state()['folderMove'] is None;assert 'editorFolder = "Owned.Elements::GroupA"' in raw_source('Other');third=raw_source('Third');assert 'newer preserved third draft' in third and 'editorFolder' not in third;source_same();preserved();checked('real embedded multi-selection moves both objects together; header Cancel restores their saved classification and prior draft without losing unrelated private input');checkpoint('multi-cancelled')
  multi_drop();idle();focus_window(b);after=len(traffic);b.locator('[data-browser-save]').click();wait_draft_action('save',after);reopen(1);assert set(state()['folderMove']['movingIds'])=={'Owned.Elements::Other','Owned.Elements::Third'};assert tree_parent('Other')=='decl:Owned.Elements::GroupB' and tree_parent('Third')=='decl:Owned.Elements::GroupB';preserved();source_same();review=ui_confirm();assert {r['id'] for r in state()['review']['units']}=={'Owned.Elements::Other','Owned.Elements::Third','Owned.Elements::GroupA','Owned.Elements::GroupB'};review.locator('[data-reject]').click();expect(review).to_be_hidden();source_same();review=ui_confirm();accept(review);idle();assert state()['folderMove'] is None;assert 'editorFolder = "Owned.Elements::GroupB"' in (project/'Other.celem').read_text();assert 'editorFolder = "Owned.Elements::GroupB"' in (project/'Third.celem').read_text();assert 'newer preserved third draft' in (project/'Third.celem').read_text();same_except({'Other.celem','Third.celem'});preserved();assert 'unrelated shared fixture draft' in raw_source('Monster');page.screenshot(path=str(case/'category-multi-confirmed.png'));checked('atomic multi-classification survives restart and Review cancel; explicit full-group compiler Confirm retains both inheritance parents and all unrelated source bytes/drafts');checkpoint('multi-confirmed')
  result=namespace_drop('Other','Owned.Elements');assert result['ok'] and result['result']['moved'];expect(node('Other')).to_have_attribute('aria-level',str(level('GroupB')));assert tree_parent('Other')=='ns:Owned.Elements';assert 'extends Owned.Elements::Unit' in raw_source('Other');assert 'editorFolder = ""' in raw_source('Other');preserved();same_except({'Other.celem','Third.celem'});idle();focus_window(b);after=len(traffic);b.locator('[data-browser-discard]').click();wait_draft_action('discard',after);idle();assert state()['folderMove'] is None;assert tree_parent('Other')=='decl:Owned.Elements::GroupB';filter_name('Monster');after=len(traffic);drop(b.locator('[data-object="Owned.Elements::Monster"]'),b.locator('.browser-items'));no_op=wait_any('moveBrowserFolders',after);assert no_op['ok'] and no_op['result']['moved'] is False;assert state()['folderMove'] is None;assert 'extends Owned.Elements::Unit' in raw_source('Monster');assert not [r for r in traffic if r.get('invoke',{}).get('endpoint') in ['editObjectStructure','moveBrowserObjects']];preserved();checked('namespace Root and empty Root drops use classification only: explicit Root is displayed as Root, Cancel restores the folder and an unclassified inherited object is a truthful no-op without parent-removal calls');checkpoint('root-cancelled')
  filter_name('Other');before=raw_source('Other');after=len(traffic);drop(b.locator('[data-object="Owned.Elements::Other"]'),b.locator('[data-namespace="Confectory.Build.DotNet"]'));page.wait_for_function("()=>document.querySelector('[role=status]')?.textContent.includes('소유 카테고리')");idle();assert not [r for r in traffic[after:] if r.get('invoke',{}).get('endpoint')=='moveBrowserFolders'];assert raw_source('Other')==before and state()['folderMove'] is None;preserved();checked('foreign namespace drop is rejected in the actual UI without navigation, server mutation or source-identity reassignment');checkpoint('foreign-rejected')
  namespace_drop('Other','Owned.Elements');idle();focus_window(b);after=len(traffic);b.locator('[data-browser-save]').click();wait_draft_action('save',after);reopen(2);assert tree_parent('Other')=='ns:Owned.Elements';definition('Other');focus_window(w);w.locator('[data-element-action=confirm]').click();dlg=page.locator('.modal');expect(dlg).to_have_attribute('aria-label','분류 위치 변경 검토');expect(dlg).not_to_contain_text('부모 이동');dlg.get_by_role('button',name='닫기',exact=True).click();assert not page.locator('#app').evaluate('el=>el.inert');idle();focus_window(w);w.locator('[data-element-action=confirm]').click();dlg=page.locator('.modal');expect(dlg).to_have_attribute('aria-label','분류 위치 변경 검토');dlg.locator('#review-creation').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=60000);expect(review).to_contain_text('Root');assert {r['id'] for r in state()['review']['units']}=={'Owned.Elements::Other','Owned.Elements::GroupB'};accept(review);idle();assert state()['folderMove'] is None;assert 'editorFolder = ""' in (project/'Other.celem').read_text();assert 'extends Owned.Elements::Unit' in (project/'Other.celem').read_text();same_except({'Other.celem','Third.celem'});preserved();assert 'unrelated shared fixture draft' in raw_source('Monster');page.screenshot(path=str(case/'category-root-confirmed.png'));checked('saved Root classification survives restart and the existing element Confirm path labels it as classification, cleans modal inert/focus and explicitly confirms only Root metadata while preserving inheritance and unrelated input');checkpoint('root-confirmed')
  definition('Other');before=(project/'Other.celem').read_bytes();focus_window(w);w.locator('.object-parent-change').click();page.locator('.object-parent-picker [data-parent-choice=""]').click();after=len(traffic);w.locator('[data-element-action=save]').click();rejected=wait_any('editObjectStructure',after);assert not rejected['ok'];assert 'extends Owned.Elements::Unit' in raw_source('Other');assert (project/'Other.celem').read_bytes()==before;idle();focus_window(w);after=len(traffic);w.locator('[data-element-action=discard]').click();wait_operation('schema',after);preserved();definition('Unit');after=len(traffic);w.locator('[data-element-action=save]').click();wait_operation('saveDraft',after);assert '112' in state()['draft']['text'];assert (project/'Unit.celem').read_bytes()==original['Unit.celem'];checked('explicit inheritance Root still runs the original full schema guard and rejects invalid inherited data; Cancel and separate private-input Save preserve both source and pending work');checkpoint('complete')
  assert not errors and not external,(errors,external);print(json.dumps({'checks':checks,'case':str(case),'nativeWindows':False,'nativeTouch':False},ensure_ascii=False,indent=2));page.close();stop();browser.close()
except Exception:
 try:(case/'folder-multi-root-failure.json').write_text(json.dumps({'state':state(),'traffic':traffic,'errors':errors},ensure_ascii=False,indent=2))
 except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case),flush=True);raise
finally:stop()
