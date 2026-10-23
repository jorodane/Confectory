"""v536 embedded Browser parent movement in an isolated actual engine.
No account/grant/model invocation. Preserves source bytes and original draft proof.
"""
import json,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());fixture=pathlib.Path(sys.argv[3]).resolve();assert fixture==repo.parent/'scratch/v508-elements/actual13-source-fixture'
case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-element-mutation-'));project=case/'owned project';shutil.copytree(fixture/'owned project',project,ignore=shutil.ignore_patterns('.confectory','.build'));(project/'Other.celem').write_bytes(bytes([239,187,191])+b'object Owned.Elements::Other extends Owned.Elements::Unit {data HP = 50;}');(project/'project.cproj').write_text((project/'project.cproj').read_text().replace('registry Confectory.Build.DotNet','element Other object "Other.celem";registry Confectory.Build.DotNet',1));(project/'Third.celem').write_text('object Owned.Elements::Third extends Owned.Elements::Unit {data HP = 60;}');(project/'project.cproj').write_text((project/'project.cproj').read_text().replace('registry Confectory.Build.DotNet','element Third object \"Third.celem\";registry Confectory.Build.DotNet',1));storage=case/'profile';storage.mkdir();original={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file() and '.confectory' not in p.parts};id='Owned.Elements::Serial';text='9223372036854775804';description='재시작할 미적용 설명 한글';env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(storage),CONFECTORY_ENTRY_STORAGE=str(storage),CONFECTORY_MCP_DIRECTORY=str(case/'instances'),CONFECTORY_WEB_PROJECT=str(project/'project.cproj'),CONFECTORY_DOTNET=env.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet'));env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];host=None;log=None;errors=[];external=[];checks=[]
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
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(0);page=setup();page.set_viewport_size({'width':1480,'height':1050});idle();page.locator('#workspace').click(button='right',position={'x':700,'y':100});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=page.locator('.window[data-key^="browser:project:"]');w=page.locator('.window[data-key=schema]');definition('Unit');w.locator('[aria-label="HP 기본값"]').fill('111');manifest='Owned.Elements::ProjectManifest';edit_description('Monster','unrelated saved fixture draft');invoke('saveDraft',{});stale=plan();edit_description('Other','archived edited fixture draft');invoke('browserRetirement',{'action':'apply','token':stale},False);invoke('select',{'id':'Owned.Elements::Other'});assert 'archived edited fixture draft' in state()['draft']['text'];source_same();checked('stale removal plan rejects a newer edit without losing either source or draft')
  archive_token=plan();archive('apply',archive_token);assert all(row['id']!='Owned.Elements::Other' for row in state()['units']);invoke('select',{'id':manifest});assert 'Other.celem' not in state()['draft']['text'];source_same();invoke('saveDraft',{});archive('recover',archive_token);invoke('select',{'id':'Owned.Elements::Other'});assert 'archived edited fixture draft' in state()['draft']['text'];invoke('select',{'id':'Owned.Elements::Monster'});assert 'unrelated saved fixture draft' in state()['draft']['text'];source_same();invoke('saveDraft',{});checked('actual unregistration stages only the owned manifest; recovery restores the edited source draft and unrelated drafts while all final bytes remain original')
  archive_token=plan();archive('apply',archive_token);invoke('saveDraft',{});flush();page.close();stop();start(1);page=setup();idle();assert all(row['id']!='Owned.Elements::Other' for row in state()['units']);source_same();assert any('Owned.Elements::Unit|element|' in key and value.get('text')=='111' for key,value in flush()['presentation']['inputs']['schema']);checked('saved deletion draft survives actual restart, hiding only its selected owned declaration and preserving other input/source bytes')
  confirm([manifest]);assert 'Other.celem' not in (project/'project.cproj').read_text();assert (project/'Other.celem').read_bytes()==original['Other.celem'];assert (project/'Other.celem').read_bytes().startswith(bytes([239,187,191]));assert all((project/k).read_bytes()==v for k,v in original.items() if k!='project.cproj');checked('explicit compiler Confirm unregisters Other and preserves the retained UTF-8 BOM original byte for byte under read-only source checks')
  idle();flush();page.close();stop();start(2);page=setup();idle();assert all(row['id']!='Owned.Elements::Other' for row in state()['units']);archive('recover',archive_token);invoke('select',{'id':'Owned.Elements::Other'});assert 'archived edited fixture draft' in state()['draft']['text'];assert set(state()['draft']['creationReviewIds'])=={manifest,'Owned.Elements::Other'};archive('cancel',archive_token);assert all(row['id']!='Owned.Elements::Other' for row in state()['units']);assert 'Other.celem' not in (project/'project.cproj').read_text();assert (project/'Other.celem').read_bytes()==original['Other.celem'];invoke('saveDraft',{});checked('confirmed archive survives restart; staged recovery can be cancelled without changing registered files or losing the saved edited draft')
  archive('recover',archive_token);invoke('saveDraft',{});idle();flush();page.close();stop();start(3);page=setup();idle();invoke('select',{'id':'Owned.Elements::Other'});assert 'archived edited fixture draft' in state()['draft']['text'];invoke('reviewGroup',{'ids':['Owned.Elements::Other'],'target':'portable'},False);confirm([manifest,'Owned.Elements::Other']);assert 'Other.celem' in (project/'project.cproj').read_text();assert 'archived edited fixture draft' in (project/'Other.celem').read_text();assert all((project/k).read_bytes()==v for k,v in original.items() if k not in ['project.cproj','Other.celem']);invoke('select',{'id':'Owned.Elements::Monster'});assert 'unrelated saved fixture draft' in state()['draft']['text'];assert any('Owned.Elements::Unit|element|' in key and value.get('text')=='111' for key,value in flush()['presentation']['inputs']['schema']);checked('recovery draft survives restart and partial Review is rejected; explicit grouped compiler Confirm restores registration plus reviewed edited source without changing other final files or drafts')
  assert not errors and not external,(errors,external);(case/'retirement-contract-evidence.json').write_text(json.dumps({'checks':checks,'actualEngine':True,'nativeWindows':False,'uiDeletion':False},ensure_ascii=False,indent=2));print(json.dumps({'checks':checks,'case':str(case)},ensure_ascii=False,indent=2));page.close();stop();browser.close()
except Exception:
 try:(case/'retirement-failure.json').write_text(json.dumps({'state':state(),'traffic':traffic,'errors':errors},ensure_ascii=False,indent=2))
 except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case),flush=True);raise
finally:stop()
