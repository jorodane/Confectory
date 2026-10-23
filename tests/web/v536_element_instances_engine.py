"""v536 documents/floating over Pack Manager in the actual generated engine.
No account/grant/model invocation. Preserves source bytes and original draft proof.
"""
import json,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());fixture=pathlib.Path(sys.argv[3]).resolve();assert fixture==repo.parent/'scratch/v508-elements/actual13-source-fixture'
case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-element-instances-'));project=case/'owned project';shutil.copytree(fixture/'owned project',project,ignore=shutil.ignore_patterns('.confectory','.build'));storage=case/'profile';storage.mkdir();original={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file() and '.confectory' not in p.parts};id='Owned.Elements::Serial';text='9223372036854775804';description='재시작할 미적용 설명 한글';env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(storage),CONFECTORY_ENTRY_STORAGE=str(storage),CONFECTORY_MCP_DIRECTORY=str(case/'instances'),CONFECTORY_WEB_PROJECT=str(project/'project.cproj'),CONFECTORY_DOTNET=env.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet'));env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];host=None;log=None;errors=[];external=[];checks=[]
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
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(0);page=setup();page.set_viewport_size({'width':2700,'height':1500});page.locator('#workspace').click(button='right',position={'x':80,'y':100});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=page.locator('.window[data-key^="browser:project:"]');q=b.locator('[data-browser-control="object-query"]');expect(q).to_be_enabled();q.fill('Unit');b.locator('[data-browser-control="object-search"]').click();row=b.locator('[data-object="Owned.Elements::Unit"]');expect(row).to_be_visible()
  def window(slot):return page.locator('.window[data-key="editor-'+slot+'"]')
  def hp(slot):return window(slot).locator('[aria-label="HP 기본값"]')
  created=[0]
  def new():
   row.click(button='right',position={'x':8,'y':8});page.locator('.context-menu').get_by_role('button',name='새 창으로 열기',exact=True).click();created[0]+=1
   if created[0]<=3:
    w=window(str(created[0]));name=w.locator('.object-title-name');expect(name).to_have_text('Unit',timeout=30000);head=name.bounding_box();box=w.bounding_box();target=980+(created[0]-1)*500;page.mouse.move(head['x']+10,head['y']+8);page.mouse.down();page.mouse.move(target+head['x']-box['x']+10,160+head['y']-box['y']+8,steps=15);page.mouse.up()

  def flush():page.evaluate('()=>confectoryFlushPresentation()');return state()
  def unchanged():assert all((project/k).read_bytes()==v for k,v in original.items())
  new();expect(window('1').locator('.object-title-name')).to_have_text('Unit',timeout=30000);expect(hp('1')).to_have_value('100');assert window('1').locator('[data-editor-source],[data-description],[data-schema-id]').count()==0;hp('1').fill('111');window('1').locator('.object-title-description').fill('첫 창의 입력');hp('1').evaluate('e=>globalThis.firstHP=e');new();expect(hp('2')).to_have_value('100',timeout=30000);hp('2').fill('222');window('2').locator('.object-title-description').fill('둘째 창의 입력');expect(hp('1')).to_have_value('111');assert len(state()['editorViews'])==2;page.screenshot(path=str(case/'two-original-element-windows.png'));checked('original v536 new-window context entry opens two real owned element renderers with distinct pending values and no generic/source fallback')
  window('1').locator('[data-close]').click();expect(window('1')).to_be_hidden();row.get_by_role('button',name='정의 열기',exact=True).click(position={'x':8,'y':8});expect(hp('1')).to_have_value('111');expect(window('1')).to_be_visible();assert hp('1').evaluate('e=>e===firstHP');assert len(state()['editorViews'])==2;expect(hp('2')).to_have_value('222');checked('ordinary definition reentry reopens hidden owned view with exact input DOM instead of allocating or losing its draft')
  new();expect(hp('3')).to_have_value('100',timeout=30000);hp('3').fill('333');new();expect(page.locator('#toast')).to_contain_text('세 개');assert len(state()['editorViews'])==3;expect(hp('1')).to_have_value('111');expect(hp('2')).to_have_value('222');expect(hp('3')).to_have_value('333');unchanged();before=flush();pending=before['presentation']['inputs']['schema'];assert all(any('|view:'+slot+'|element|' in key for key,value in pending) for slot in ['1','2','3']);page.close();stop();checked('existing three-view backend cap fails visibly while preserving all independent unsaved input scopes and original source bytes')
  start(1);page=setup();page.set_viewport_size({'width':2700,'height':1500});expect(hp('1')).to_have_value('111',timeout=60000);expect(hp('2')).to_have_value('222');expect(hp('3')).to_have_value('333');expect(window('1').locator('.object-title-description')).to_have_value('첫 창의 입력');expect(window('2').locator('.object-title-description')).to_have_value('둘째 창의 입력');unchanged();page.screenshot(path=str(case/'cold-three-element-windows.png'));checked('actual process restart restores three original element windows and per-view Korean/value input proofs')
  window('1').locator('[data-element-action="save"]').click();expect(window('1').locator('[data-element-error]')).to_have_text('',timeout=30000);page.wait_for_function('()=>document.querySelector(".topbar .brand")?.disabled===false');s=state();assert '111' in next(r for r in s['editorViews'] if r['view']=='1')['draft']['text'];expect(hp('2')).to_have_value('222');expect(hp('3')).to_have_value('333');unchanged();checked('view-one explicit staged Save uses bound server view and preserves other window inputs without final source Confirm')
  baseline=next(r for r in state()['editorViews'] if r['view']=='1')['draft']['text'];window('2').locator('[data-element-action="save"]').click();expect(window('2').locator('[data-element-error]')).not_to_have_text('',timeout=30000);expect(hp('2')).to_have_value('222');assert next(r for r in state()['editorViews'] if r['view']=='1')['draft']['text']==baseline;unchanged();checked('stale second-view revision/hash is refused with its input retained and shared draft unchanged')
  window('2').locator('[data-element-action="discard"]').click();expect(hp('2')).to_have_value('111',timeout=30000);expect(hp('3')).to_have_value('333');unchanged();page.screenshot(path=str(case/'independent-stale-and-discard.png'));checked('explicit local input cancel reads the saved shared value while a third window pending input remains untouched')
  assert not errors and not external,(errors,external);result={'checks':checks,'errors':errors,'external':external,'actualEngine':True,'newWindowViaOriginalMenu':True,'originalSourcesUnchanged':True,'nativeWindows':False,'actualCredentialsOrInference':False,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2));page.close();stop();browser.close()
except Exception:
 try:(case/'failure.json').write_text(json.dumps({'state':state(),'traffic':traffic,'errors':errors},ensure_ascii=False,indent=2))
 except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case),flush=True);raise
finally:stop()
