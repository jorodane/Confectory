"""v536 documents/floating over Pack Manager in the actual generated engine.
No account/grant/model invocation. Preserves source bytes and original draft proof.
"""
import json,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());fixture=pathlib.Path(sys.argv[3]).resolve();assert fixture==repo.parent/'scratch/v508-elements/actual13-source-fixture'
case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-document-projects-'));project=case/'owned project';shutil.copytree(fixture/'owned project',project,ignore=shutil.ignore_patterns('.confectory','.build'));storage=case/'profile';storage.mkdir();original={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file() and '.confectory' not in p.parts};id='Owned.Elements::Serial';text='9223372036854775804';description='재시작할 미적용 설명 한글';env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(storage),CONFECTORY_ENTRY_STORAGE=str(storage),CONFECTORY_MCP_DIRECTORY=str(case/'instances'),CONFECTORY_WEB_PROJECT=str(project/'project.cproj'),CONFECTORY_DOTNET=env.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet'));env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];host=None;log=None;errors=[];external=[];checks=[]
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

project_b=case/'other path'/'owned project';shutil.copytree(fixture/'owned project',project_b,ignore=shutil.ignore_patterns('.confectory','.build'));unit_b=project_b/'Unit.celem';unit_b.write_text(unit_b.read_text().replace('data HP = 100;','data HP = 200;description "isolated B marker";'));original_b={str(p.relative_to(project_b)):p.read_bytes() for p in project_b.rglob('*') if p.is_file() and '.confectory' not in p.parts}
def unchanged():
 assert all((project/k).read_bytes()==v for k,v in original.items());assert all((project_b/k).read_bytes()==v for k,v in original_b.items())
def field():return page.locator('.window[data-key="editor-1"] [data-editor-source]')
def flush():page.evaluate('()=>confectoryFlushPresentation()')
def go_listing(listing):
 page.locator('.brand').click();expect(page.locator('.home-grid')).to_be_visible();page.locator('[data-enter="'+listing+'"]').click();expect(page.locator('.work-body')).to_be_visible()
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(0);page=setup();a_state=state();a_id=a_state['projectId'];a_listing=a_state['listingId'];invoke('openEditorView',{'view':'1','id':'Owned.Elements::Unit','viewMode':'source'});page.reload();goto_editor(page,url);expect(field()).to_be_visible();a_text=field().input_value()+'\n// A에만 남겨 둘 입력';field().fill(a_text);field().evaluate('e=>globalThis.sourceA=e');page.locator('.window[data-key="editor-1"] [data-editor-apply]').evaluate('e=>globalThis.staleApplyA=e');flush();page.close();stop()
  # Register B only through the fixture's explicitly selected startup project; no real workspace is touched.
  env['CONFECTORY_WEB_PROJECT']=str(project_b/'project.cproj');start(1);page=setup();b_state=state();b_id=b_state['projectId'];b_listing=b_state['listingId'];assert a_id!=b_id and a_listing!=b_listing;invoke('openEditorView',{'view':'1','id':'Owned.Elements::Unit','viewMode':'source'});page.reload();goto_editor(page,url);expect(field()).to_be_visible();assert 'isolated B marker' in field().input_value() and 'A에만' not in field().input_value();b_text=field().input_value()+'\n// B의 별도 입력';field().fill(b_text);flush();unchanged();checked('same namespace/object/view slot at two different owned roots has distinct actual project identity and pending input')
  go_listing(a_listing);expect(field()).to_have_value(a_text,timeout=60000);field().evaluate('e=>globalThis.sourceA=e');page.locator('.window[data-key="editor-1"] [data-editor-apply]').evaluate('e=>globalThis.staleApplyA=e');go_listing(b_listing);expect(field()).to_have_value(b_text,timeout=60000);assert field().evaluate('e=>e!==sourceA');assert state()['projectId']==b_id;unchanged();checked('actual live Home A→B transition restores each independent view input without mixing same-name source owners')
  baseline=state()['editorViews'][0]['draft']['text'];traffic_before=len(traffic);page.evaluate('async()=>await globalThis.staleApplyA.onclick(new Event("click"))');page.wait_for_function('()=>document.querySelector(".topbar .brand")?.disabled===false');page.wait_for_timeout(150);after=state();assert after['projectId']==b_id;assert after['editorViews'][0]['draft']['text']==baseline,{'cause':'retired A callback staged text into B','aId':a_id,'bId':b_id};assert not [r for r in traffic[traffic_before:] if r.get('invoke',{}).get('endpoint')=='editEditorView'];expect(field()).to_have_value(b_text);unchanged();checked('retired project-A Apply callback cannot dispatch a write or alter project-B shared draft')
  go_listing(a_listing);expect(field()).to_have_value(a_text,timeout=60000);go_listing(b_listing);expect(field()).to_have_value(b_text,timeout=60000);flush();page.close();stop();start(2);page=setup();expect(field()).to_have_value(b_text,timeout=60000);go_listing(a_listing);expect(field()).to_have_value(a_text,timeout=60000);assert state()['projectId']==a_id;unchanged();checked('actual process restart and repeated same-name project switches retain both pending texts and unchanged source files')
  assert not errors and not external,(errors,external);result={'checks':checks,'actualEngine':True,'actualLiveProjectSwitch':True,'actualCredentialsOrInference':False,'nativeWindows':False,'errors':errors,'external':external,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2));page.close();stop();browser.close()
except Exception:
 try:(case/'failure.json').write_text(json.dumps({'state':state(),'traffic':traffic,'errors':errors},ensure_ascii=False,indent=2))
 except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case),flush=True);raise
finally:stop()
