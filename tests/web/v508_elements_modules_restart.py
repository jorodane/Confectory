"""Cold pending-input restoration in a previously compiler-confirmed OWNED element fixture.
No account/grant/model invocation. Preserves source bytes and original draft proof.
"""
import json,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());fixture=pathlib.Path(sys.argv[3]).resolve();assert fixture.parent==pathlib.Path('/tmp') and fixture.name.startswith('confectory-elements-modules-')
case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-elements-modules-restart-'));project=fixture/'owned project';storage=case/'profile';shutil.copytree(fixture/'profile',storage);original={p.name:p.read_bytes() for p in project.iterdir() if p.is_file()};id='Owned.Elements::Monster';text='9223372036854775804';description='재시작할 미적용 설명 한글';env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(storage),CONFECTORY_ENTRY_STORAGE=str(storage),CONFECTORY_MCP_DIRECTORY=str(case/'instances'),CONFECTORY_WEB_PROJECT=str(project/'project.cproj'),CONFECTORY_DOTNET=env.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet'));env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];host=None;log=None;errors=[];external=[];checks=[]
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
def invoke(endpoint,body):
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
   assert rows[0].get('ok'),rows;return u.get('state')
  finally:raw({'op':'dispose','view':v['view']})
 raise AssertionError('admission failed')
def setup():
 page=browser.new_page(viewport={'width':1280,'height':900});page.on('pageerror',lambda e:errors.append(str(e)));page.route('**/*',lambda r:r.continue_() if r.request.url.startswith(origin) else (external.append(r.request.url),r.abort()));goto_editor(page,url);return page
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(0);page=setup();w=page.locator('.window[data-key="schema"]');card=w.locator('[data-behavior-source="Owned.Elements::Rules"]');expect(card.locator('.function-node-name')).to_have_text('Attack',timeout=30000);card.locator('[data-behavior-unlink]').click();expect(card).to_have_count(0);page.wait_for_function("()=>typeof confectoryFlushPresentation==='function'");page.evaluate('async()=>await confectoryFlushPresentation()');s=state();scope=s['projectId'];key=scope+'|'+id+'|element|modules';proof=next(v for k,v in s['presentation']['inputs']['schema'] if k==key);assert proof['value']==[];page.close();stop()
  start(1);page=setup();w=page.locator('.window[data-key="schema"]');expect(w.locator('.object-title-name')).to_have_text('Monster',timeout=30000);card=w.locator('[data-behavior-source="Owned.Elements::Rules"]');expect(card).to_have_count(0);page.wait_for_function("()=>typeof confectoryFlushPresentation==='function'");page.evaluate('async()=>await confectoryFlushPresentation()');s=state();assert next(v for k,v in s['presentation']['inputs']['schema'] if k==key)==proof;assert all((project/k).read_bytes()==v for k,v in original.items());w.locator('[data-element-action="discard"]').click();expect(card.locator('.function-node-name')).to_have_text('Attack');checks.append('cold restart preserves pending module unlink and exact original CAS proof; cancel restores actual saved contract without source writes')
  card.locator('[data-behavior-unlink]').click();expect(card).to_have_count(0);w.locator('[data-element-action="save"]').click();page.wait_for_function("()=>typeof confectoryFlushPresentation==='function'");page.evaluate('async()=>await confectoryFlushPresentation()');s=state();assert 'module Owned.Elements::Rules' not in s['draft']['text'];assert not s['schema']['modules'];assert all((project/k).read_bytes()==v for k,v in original.items());page.close();stop()
  start(2);page=setup();w=page.locator('.window[data-key="schema"]');expect(w.locator('.object-title-name')).to_have_text('Monster',timeout=30000);expect(w.locator('[data-behavior-source="Owned.Elements::Rules"]')).to_have_count(0);page.wait_for_function("()=>typeof confectoryFlushPresentation==='function'");page.evaluate('async()=>await confectoryFlushPresentation()');s=state();assert 'module Owned.Elements::Rules' not in s['draft']['text'];assert not [v for k,v in s['presentation']['inputs']['schema'] if k==key];assert all((project/k).read_bytes()==v for k,v in original.items());page.screenshot(path=str(case/'module-unlinked-restarted.png'));checks.append('saved unlink and its empty contract/card state survive another cold restart without duplicate cards or final source changes');page.close();stop();browser.close()
  assert not errors and not external,(errors,external)
except Exception:
 try:(case/'failure-state.json').write_text(json.dumps(state(),indent=2));(case/'errors.json').write_text(json.dumps(errors))
 except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case));raise
finally:stop()
record={'checks':checks,'errors':errors,'external':external,'actualEngine':True,'accountOrInference':False,'nativeWindows':False,'sourcePreserved':True,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
