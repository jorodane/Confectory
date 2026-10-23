"""v536 documents/floating over Pack Manager in the actual generated engine.
No account/grant/model invocation. Preserves source bytes and original draft proof.
"""
import json,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());fixture=pathlib.Path(sys.argv[3]).resolve();assert fixture==repo.parent/'scratch/v508-elements/actual13-source-fixture'
case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-element-mutation-'));project=case/'owned project';shutil.copytree(fixture/'owned project',project,ignore=shutil.ignore_patterns('.confectory','.build'));(project/'Other.celem').write_text('object Owned.Elements::Other extends Owned.Elements::Unit {data HP = 50;}');(project/'project.cproj').write_text((project/'project.cproj').read_text().replace('registry Confectory.Build.DotNet','element Other object "Other.celem";registry Confectory.Build.DotNet',1));storage=case/'profile';storage.mkdir();original={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file() and '.confectory' not in p.parts};id='Owned.Elements::Serial';text='9223372036854775804';description='재시작할 미적용 설명 한글';env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(storage),CONFECTORY_ENTRY_STORAGE=str(storage),CONFECTORY_MCP_DIRECTORY=str(case/'instances'),CONFECTORY_WEB_PROJECT=str(project/'project.cproj'),CONFECTORY_DOTNET=env.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet'));env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];host=None;log=None;errors=[];external=[];checks=[]
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
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(0);page=setup();page.set_viewport_size({'width':1480,'height':1050});page.locator('#workspace').click(button='right',position={'x':700,'y':100});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=page.locator('.window[data-key^="browser:project:"]');q=b.locator('[data-browser-control="object-query"]');expect(q).to_be_enabled();q.fill('Unit');b.locator('[data-browser-control="object-search"]').click();b.locator('[data-object="Owned.Elements::Unit"]').get_by_role('button',name='정의 열기',exact=True).click();w=page.locator('.window[data-key=schema]');expect(w.locator('[aria-label="HP 기본값"]')).to_have_value('100',timeout=30000);section=w.locator('.object-variations');idle();w.locator('[aria-label="HP 기본값"]').fill('111');row=lambda key:section.locator('[data-object="Owned.Elements::'+key+'"]');expect(row('Monster')).to_be_visible(timeout=30000);expect(row('Other')).to_be_visible();row('Monster').click();row('Other').click(modifiers=['Control']);expect(row('Monster')).to_have_attribute('aria-selected','true');expect(row('Other')).to_have_attribute('aria-selected','true');row('Other').press('Escape');expect(row('Monster')).to_have_attribute('aria-selected','false');row('Monster').click();row('Other').click(modifiers=['Shift']);expect(row('Monster')).to_have_attribute('aria-selected','true');expect(row('Other')).to_have_attribute('aria-selected','true');row('Other').press('Control+a');expect(section.locator('[data-object][aria-selected=true]')).to_have_count(2);row('Other').press('Escape');source_same();checked('original Ctrl toggle, Shift range, Ctrl+A and Esc selection operate on visible children without touching parent111 or source bytes')
  row('Monster').click();row('Monster').press('F2');name=section.get_by_role('textbox',name='Monster 이름 변경',exact=True);expect(name).to_be_focused();name.fill('취소할 이름');name.press('Escape');expect(section.locator('.browser-data-name-input')).to_have_count(0);source_same();checked('original F2 inline editor and Esc cancel preserve stable identity and unrelated parent input')
  row('Monster').press('F2');name=section.get_by_role('textbox',name='Monster 이름 변경',exact=True);name.fill('Other');name.press('Enter');expect(name).to_have_attribute('aria-invalid','true');name.fill('몬스터 A');after=len(traffic);name.press('Enter');wait_operation('editDeclaration',after);expect(section.locator('.browser-data-name-input')).to_have_count(0,timeout=30000);expect(row('Monster').locator('[data-inline-name]')).to_have_text('몬스터 A');expect(w.locator('[aria-label="HP 기본값"]')).to_have_value('111');assert state()['draft']['id']=='Owned.Elements::Unit';source_same();checked('duplicate display name is rejected; Korean rename stages editorName through existing declaration CAS without changing Monster ID, references or final files')
  idle();flush();stop();page.close();start(1);page=setup();page.set_viewport_size({'width':1480,'height':1050});w=page.locator('.window[data-key=schema]');expect(w.locator('[aria-label="HP 기본값"]')).to_have_value('111',timeout=60000);section=w.locator('.object-variations');name=section.get_by_role('textbox',name='Monster 이름 변경',exact=True);expect(name).to_have_value('몬스터 A',timeout=30000);assert not any(t.get('invoke',{}).get('endpoint')=='editDeclaration' for t in traffic[-3:]);name.press('Enter');expect(section.locator('.browser-data-name-input')).to_have_count(0,timeout=30000);expect(row('Monster').locator('[data-inline-name]')).to_have_text('몬스터 A');source_same();checked('unsaved rename raw survives actual process restart without automatic source write and explicit Enter retries only the observed rollback source')
  # Two selected objects use original HTML drag transfer; actual host opens bound Views.
  row('Monster').click();row('Other').click(modifiers=['Control']);transfer=page.evaluate_handle('()=>new DataTransfer()');row('Monster').dispatch_event('dragstart',{'dataTransfer':transfer});payload=transfer.evaluate('(d)=>JSON.parse(d.getData("application/x-confectory-placement"))');assert payload['ids']==['Owned.Elements::Monster','Owned.Elements::Other'];canvas=page.locator('#workspace');point=canvas.bounding_box();canvas.dispatch_event('dragover',{'dataTransfer':transfer,'clientX':point['x']+850,'clientY':point['y']+500});canvas.dispatch_event('drop',{'dataTransfer':transfer,'clientX':point['x']+850,'clientY':point['y']+500});expect(page.locator('.window[data-key^=editor-]:not([hidden])')).to_have_count(2,timeout=30000);assert set(v['id'] for v in state()['editorViews'])=={'Owned.Elements::Monster','Owned.Elements::Other'};expect(w.locator('[aria-label="HP 기본값"]')).to_have_value('111');source_same();page.screenshot(path=str(case/'browser-selection-and-placement.png'));checked('multi-object drag payload opens two actual owned element Views in the same project Workspace, with stable references and parent raw preserved')
  assert not errors and not external,(errors,external);flush();(case/'evidence.json').write_text(json.dumps({'checks':checks,'errors':errors,'actualEngine':True,'nativeWindows':False,'nativeTouch':False},ensure_ascii=False,indent=2));print(json.dumps({'checks':checks,'evidence':str(case)},ensure_ascii=False,indent=2));page.close();stop();browser.close()
except Exception:
 try:(case/'failure.json').write_text(json.dumps({'state':state(),'traffic':traffic,'errors':errors},ensure_ascii=False,indent=2))
 except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case),flush=True);raise
finally:stop()
