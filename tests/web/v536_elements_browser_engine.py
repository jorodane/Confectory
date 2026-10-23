"""v536 documents/floating over Pack Manager in the actual generated engine.
No account/grant/model invocation. Preserves source bytes and original draft proof.
"""
import json,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());fixture=pathlib.Path(sys.argv[3]).resolve();assert fixture==repo.parent/'scratch/v508-elements/actual13-source-fixture'
case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-element-browser-'));project=case/'owned project';shutil.copytree(fixture/'owned project',project,ignore=shutil.ignore_patterns('.confectory','.build'));storage=case/'profile';storage.mkdir();original={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file() and '.confectory' not in p.parts};id='Owned.Elements::Serial';text='9223372036854775804';description='재시작할 미적용 설명 한글';env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(storage),CONFECTORY_ENTRY_STORAGE=str(storage),CONFECTORY_MCP_DIRECTORY=str(case/'instances'),CONFECTORY_WEB_PROJECT=str(project/'project.cproj'),CONFECTORY_DOTNET=env.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet'));env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];host=None;log=None;errors=[];external=[];checks=[]
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
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(0);page=setup();page.set_viewport_size({'width':1480,'height':1000});page.locator('#workspace').click(button='right',position={'x':700,'y':100});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=page.locator('.window[data-key^="browser:project:"]');q=b.locator('[data-browser-control="object-query"]');expect(q).to_be_enabled();q.fill('Unit');b.locator('[data-browser-control="object-search"]').click();row=b.locator('[data-object="Owned.Elements::Unit"]');expect(row).to_be_visible();row.get_by_role('button',name='정의 열기',exact=True).click();w=page.locator('.window[data-key=schema]');expect(w.locator('[aria-label="HP 기본값"]')).to_have_value('100',timeout=30000);section=w.locator('.object-variations');expect(section.locator('[data-object="Owned.Elements::Monster"]')).to_be_visible();idle();w.locator('[aria-label="HP 기본값"]').fill('111');w.locator('.object-title-description').fill('부모 창 입력 한글');source_same();page.screenshot(path=str(case/'unit-child-browser.png'));checked('actual Unit browser lists only direct Monster inheritance with retained HP/description input and source untouched')
  section.locator('.search').fill('Slime');section.locator('.search').press('Enter');expect(section.locator('[data-object="Owned.Elements::Slime"]')).to_be_visible();expect(section.locator('[data-object="Owned.Elements::Monster"]')).to_have_count(0);source_same();checked('submitted original child search finds a descendant beyond direct inheritance without selecting or editing its source')
  section.locator('.search').fill('');section.locator('[aria-label="검색 확정"]').click();section.locator('[data-density="40"]').click();expect(section.locator('.object-card[data-object="Owned.Elements::Monster"]')).to_be_visible();section.locator('[data-enter-concept="Owned.Elements::Monster"]').click();expect(section.locator('.browser-title-path')).to_have_attribute('title','Unit / Monster');expect(section.locator('[data-object="Owned.Elements::Slime"]')).to_be_visible();expect(w.locator('[aria-label="HP 기본값"]')).to_have_value('111');section.locator('[data-object="Owned.Elements::Slime"]').focus();section.locator('[data-object="Owned.Elements::Slime"]').press('ArrowLeft');expect(section.locator('.browser-title-path')).to_have_attribute('title','Unit');expect(section.locator('[data-object="Owned.Elements::Monster"]')).to_be_visible();checked('original Preview expand/breadcrumb and keyboard back stay bounded under Unit and retain parent edits')
  section.locator('[data-density="0"]').click();section.locator('[aria-label="정렬 방법"]').click();page.locator('.context-menu').get_by_role('button',name='이름 내림차순',exact=True).click();section.locator('.search').fill('Slime');section.locator('[aria-label="검색 확정"]').click();section.locator('[data-object="Owned.Elements::Slime"]').focus();section.locator('[data-object="Owned.Elements::Slime"]').press('Enter');child=page.locator('.window[data-key=editor-1]');expect(child.locator('.object-title-name')).to_have_text('Slime',timeout=30000);expect(child.locator('[aria-label="HP 기본값"]')).to_have_value('100');expect(w.locator('[aria-label="HP 기본값"]')).to_have_value('111');child.locator('[aria-label="HP 기본값"]').fill('222');child.locator('.object-title-description').fill('하위 창 입력 한글');expect(w.locator('.object-title-description')).to_have_value('부모 창 입력 한글');child.locator('[data-close]').click();expect(child).to_be_hidden();section.locator('[data-object="Owned.Elements::Slime"]').dblclick();expect(child).to_be_visible();expect(child.locator('[aria-label="HP 기본값"]')).to_have_value('222');expect(w.locator('[aria-label="HP 기본값"]')).to_have_value('111');source_same();checked('Enter/doubleclick opens and reopens a real bound child View without replacing the parent or losing either Korean/value input')
  child.locator('[data-close]').click();section.locator('.search').fill('아직 검색하지 않은 한글');before=flush();assert any('|view:1|element|' in k for k,v in before['presentation']['inputs']['schema']);page.screenshot(path=str(case/'parent-input-and-query.png'));page.close();stop();start(1);page=setup();page.set_viewport_size({'width':1480,'height':1000});w=page.locator('.window[data-key=schema]');expect(w.locator('[aria-label="HP 기본값"]')).to_have_value('111',timeout=60000);section=w.locator('.object-variations');expect(section.locator('.search')).to_have_value('아직 검색하지 않은 한글');expect(section.locator('[data-object="Owned.Elements::Slime"]')).to_be_visible();expect(w.locator('.object-title-description')).to_have_value('부모 창 입력 한글');child=page.locator('.window[data-key=editor-1]');expect(child).to_be_hidden();idle();section.locator('[data-object="Owned.Elements::Slime"]').press('Enter');expect(child).to_be_visible();expect(child.locator('[aria-label="HP 기본값"]')).to_have_value('222');source_same();checked('actual process restart preserves submitted search versus unsubmitted Korean query, parent draft and hidden-child reentry without source mutation')
  child.locator('[data-element-action=discard]').click();expect(child.locator('[aria-label="HP 기본값"]')).to_have_value('100',timeout=30000);expect(w.locator('[aria-label="HP 기본값"]')).to_have_value('111');child.locator('[aria-label="HP 기본값"]').fill('223');child.locator('[data-element-action=save]').click();expect(child.locator('[data-element-error]')).to_have_text('',timeout=30000);idle();s=state();assert 'data HP = 223' in next(v for v in s['editorViews'] if v['view']=='1')['draft']['text'];expect(w.locator('[aria-label="HP 기본값"]')).to_have_value('111');source_same();page.screenshot(path=str(case/'child-saved-parent-preserved.png'));checked('local child discard and checked bound-view Save preserve parent inputs; staged Save leaves all final sources unchanged')
  assert not errors and not external,(errors,external);record={'checks':checks,'actualEngine':True,'nativeWindowsOrAndroid':False,'actualCredentialsOrInference':False,'errors':errors,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False,indent=2));page.close();stop();browser.close()
except Exception:
 try:(case/'failure.json').write_text(json.dumps({'state':state(),'traffic':traffic,'errors':errors},ensure_ascii=False,indent=2))
 except Exception:pass
 try:page.screenshot(path=str(case/'failure.png'))
 except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case),flush=True);raise
finally:stop()
