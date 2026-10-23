"""Cold pending-input restoration in a previously compiler-confirmed OWNED element fixture.
No account/grant/model invocation. Preserves source bytes and original draft proof.
"""
import json,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());fixture=pathlib.Path(sys.argv[3]).resolve();assert fixture.parent==pathlib.Path('/tmp') and fixture.name.startswith('confectory-elements-typed-')
case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-elements-typed-restart-'));project=fixture/'owned project';storage=case/'profile';shutil.copytree(fixture/'profile',storage);original={p.name:p.read_bytes() for p in project.iterdir() if p.is_file()};id='Owned.Elements::Monster';text='9223372036854775804';description='재시작할 미적용 설명 한글';env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(storage),CONFECTORY_ENTRY_STORAGE=str(storage),CONFECTORY_MCP_DIRECTORY=str(case/'instances'),CONFECTORY_WEB_PROJECT=str(project/'project.cproj'),CONFECTORY_DOTNET=env.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet'));env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];host=None;log=None;errors=[];external=[];checks=[]
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
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(0);page=setup();w=page.locator('.window[data-key="schema"]');expect(w.locator('.object-title-name')).to_have_text('Monster',timeout=30000);expect(w.locator('[data-property-path='+json.dumps('["Combat","Power"]')+'] input')).to_have_value('9223372036854775805')
  if w.locator('[data-element-action="discard"]').is_enabled():w.locator('[data-element-action="discard"]').click();expect(w.locator('[data-property-path='+json.dumps('["Combat","Power"]')+'] input')).to_have_value('9223372036854775805')
  # Close the read Browser through the original UI; only the object pane must hydrate children on cold start.
  for b in page.locator('.window[data-key^="browser"] [data-close]').all():b.click()
  expect(page.locator('.window[data-key="review"]')).to_be_hidden();assert state()['review'] is None
  w.locator('[data-property-path='+json.dumps('["Combat","Power"]')+'] input').fill(text);w.locator('.object-title-description').fill(description);page.wait_for_function("()=>typeof globalThis.confectoryFlushPresentation==='function'");page.evaluate('async()=>{await confectoryFlushPresentation();}');s=state();scope=s['projectId'];prefix=scope+'|'+id+'|element|';pending=[row for row in s['presentation']['inputs']['schema'] if row[0].startswith(prefix)];assert len(pending)==2,pending;proof={key:value.copy() for key,value in pending};assert all((project/name).read_bytes()==value for name,value in original.items());page.close();stop()
  start(1);page=setup();w=page.locator('.window[data-key="schema"]');expect(w.locator('[data-property-path='+json.dumps('["Combat","Power"]')+'] input')).to_have_value(text,timeout=30000);expect(w.locator('.object-title-description')).to_have_value(description);expect(w.locator('[data-object="Owned.Elements::Slime"]')).to_be_visible(timeout=30000);expect(page.locator('.window[data-key="review"]')).to_be_hidden();expect(page.get_by_text('이 창의 실제 기능을 다시 연결해야 합니다.',exact=False)).to_have_count(0);page.screenshot(path=str(case/'cold-pending.png'));page.wait_for_function("()=>typeof globalThis.confectoryFlushPresentation==='function'");page.evaluate('async()=>{await confectoryFlushPresentation();}');s=state();current={key:value for key,value in s['presentation']['inputs']['schema'] if key.startswith(prefix)};assert current==proof,(current,proof);assert all((project/name).read_bytes()==value for name,value in original.items());checks.append('actual cold restart restores pending compound JSON/exact long/Korean description with unchanged original proof and source bytes')
  # Public private-presentation API seeds only the older owned fixture format; no grant or source write.
  presentation=s['presentation'];rootRecord=proof[prefix+'["Combat"]'];converted=[[scope+'|'+id+'|primary|["Combat","Power"]',{'text':text,'revision':rootRecord['revision'],'hash':rootRecord['hash']}],[scope+'|'+id+'|primary|description',{'text':description,'revision':rootRecord['revision'],'hash':rootRecord['hash']}]]
  legacyExpected={prefix+'["Combat","Power"]':{'kind':'field','path':['Combat','Power'],'text':text,'revision':rootRecord['revision'],'hash':rootRecord['hash']},prefix+'description':{'kind':'description','text':description,'revision':rootRecord['revision'],'hash':rootRecord['hash']}}
  presentation['inputs']['schema']=converted;page.close();invoke('savePresentation',{'presentation':presentation});stop()
  start(2);page=setup();w=page.locator('.window[data-key="schema"]');expect(w.locator('[data-property-path='+json.dumps('["Combat","Power"]')+'] input')).to_have_value(text,timeout=30000);expect(w.locator('.object-title-description')).to_have_value(description);page.wait_for_function("()=>typeof globalThis.confectoryFlushPresentation==='function'");page.evaluate('async()=>{await confectoryFlushPresentation();}');s=state();current={key:value for key,value in s['presentation']['inputs']['schema'] if key.startswith(prefix)};assert current==legacyExpected,(current,legacyExpected);expect(w.locator('[data-object="Owned.Elements::Slime"]')).to_be_visible(timeout=30000);expect(page.get_by_text('이 창의 실제 기능을 다시 연결해야 합니다.',exact=False)).to_have_count(0);expect(page.locator('.window[data-key="review"]')).to_be_hidden();assert not [row for row in s['presentation']['inputs']['schema'] if row[0].startswith(scope+'|'+id+'|primary|')];assert all((project/name).read_bytes()==value for name,value in original.items());page.screenshot(path=str(case/'legacy-pending.png'));checks.append('cold legacy nested scalar/description migrate visibly without rebasing proof, preserving source bytes')
  assert not errors and not external,(errors,external);page.close();stop();browser.close()
except Exception:
 try:(case/'failure-errors.json').write_text(json.dumps(errors));(case/'failure-state.json').write_text(json.dumps(state(),indent=2))
 except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case));raise
finally:stop()
record={'checks':checks,'errors':errors,'external':external,'actualEngine':True,'accountOrInference':False,'nativeWindows':False,'sourcePreserved':True,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
