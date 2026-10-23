"""v536 documents/floating over Pack Manager in the actual generated engine.
No account/grant/model invocation. Preserves source bytes and original draft proof.
"""
import json,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());fixture=pathlib.Path(sys.argv[3]).resolve();assert fixture==repo.parent/'scratch/v508-elements/actual13-source-fixture'
case=pathlib.Path(sys.argv[4]).resolve();assert str(case).startswith('/tmp/confectory-element-data-create-') and (case/'profile').is_dir();project=case/'owned project';storage=case/'profile';original={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file() and '.confectory' not in p.parts and '.build' not in p.parts};id='Owned.Elements::Serial';text='9223372036854775804';description='재시작할 미적용 설명 한글';env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(storage),CONFECTORY_ENTRY_STORAGE=str(storage),CONFECTORY_MCP_DIRECTORY=str(case/'instances'),CONFECTORY_WEB_PROJECT=str(project/'project.cproj'),CONFECTORY_DOTNET=env.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet'));env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];host=None;log=None;errors=[];external=[];checks=[]
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
 if isinstance(body,dict) and body.get('op')=='invoke' and body.get('endpoint')=='createVariation' and injected==0:
  # Actual server rejects an explicitly stale transport revision before execution.
  injected+=1;body['expectedRevision']-=1;request.continue_(post_data=json.dumps(body));return
 request.continue_()

def setup():
 page=browser.new_page(viewport={'width':1280,'height':900});page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',observe);page.route('**/*',route);goto_editor(page,url);return page

def source_same():
 actual={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file() and '.confectory' not in p.parts and '.build' not in p.parts};assert actual==original
def idle():page.wait_for_function('()=>document.querySelector(".topbar .brand")?.disabled===false')
def flush():page.evaluate('()=>confectoryFlushPresentation()');return state()
def wait_operation(endpoint,after):
 for _ in range(6000):
  ids={r['invoke']['requestId'] for r in traffic[after:] if r.get('invoke',{}).get('endpoint')==endpoint};results=[r['result'] for r in traffic[after:] if r.get('result',{}).get('requestId') in ids];good=[r for r in results if r.get('ok')]
  if good:return good[-1]
  bad=[r for r in results if r.get('error',{}).get('code')!='stale_revision'];assert not bad,bad;page.wait_for_timeout(10)
 raise AssertionError('operation did not complete: '+endpoint)
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(2);page=setup();page.set_viewport_size({'width':1480,'height':1050});w=page.locator('.window[data-key=schema]');expect(w.locator('[aria-label="HP 기본값"]')).to_have_value('111',timeout=60000);section=w.locator('.object-variations');expect(section.locator('[aria-label="FreshVariant HP"]')).to_have_value('222',timeout=30000);idle();w.locator('.object-title-name').click();after=len(traffic);w.locator('[data-element-action=save]').click();wait_operation('saveDraft',after);expect(w.locator('[data-element-error]')).to_have_text('');idle();fresh=section.locator('[data-object="Owned.Elements::FreshVariant"]');fresh.get_by_role('button',name='FreshVariant 편집',exact=True).click();child=page.locator('.window[data-key=editor-1]');expect(child.locator('[aria-label="HP 기본값"]')).to_have_value('222',timeout=30000);child.locator('[aria-label="HP 기본값"]').fill('333');child.locator('[data-element-action=discard]').click();expect(child.locator('[aria-label="HP 기본값"]')).to_have_value('222',timeout=30000);expect(w.locator('[aria-label="HP 기본값"]')).to_have_value('111');source_same();child.locator('[data-close]').click();w.locator('.object-title-name').click();fresh.scroll_into_view_if_needed();w.locator('.window-body').first.evaluate('e=>e.scrollLeft=0');page.screenshot(path=str(case/'final-original-data-and-child.png'));checked('after real cold restore, ordinary header focus makes the parent available; checked parent Save and Data child reentry/discard preserve child222, parent111 and all final source bytes')
  assert not errors and not external,(errors,external);record={'checks':checks,'actualEngine':True,'nativeWindowsOrAndroid':False,'actualCredentialsOrInference':False,'errors':errors,'evidence':str(case)};(case/'focus-evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False,indent=2));page.close();stop();browser.close()
except Exception:
 try:(case/'focus-failure.json').write_text(json.dumps({'state':state(),'traffic':traffic,'errors':errors},ensure_ascii=False,indent=2))
 except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case),flush=True);raise
finally:stop()
