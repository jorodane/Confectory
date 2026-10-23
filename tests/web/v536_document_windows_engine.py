"""v536 documents/floating over Pack Manager in the actual generated engine.
No account/grant/model invocation. Preserves source bytes and original draft proof.
"""
import json,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());fixture=pathlib.Path(sys.argv[3]).resolve();assert fixture==repo.parent/'scratch/v508-elements/actual13-source-fixture'
case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-document-engine-'));project=case/'owned project';shutil.copytree(fixture/'owned project',project,ignore=shutil.ignore_patterns('.confectory','.build'));storage=case/'profile';storage.mkdir();original={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file() and '.confectory' not in p.parts};id='Owned.Elements::Serial';text='9223372036854775804';description='재시작할 미적용 설명 한글';env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(storage),CONFECTORY_ENTRY_STORAGE=str(storage),CONFECTORY_MCP_DIRECTORY=str(case/'instances'),CONFECTORY_WEB_PROJECT=str(project/'project.cproj'),CONFECTORY_DOTNET=env.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet'));env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];host=None;log=None;errors=[];external=[];checks=[]
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
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(0);page=setup();page.set_viewport_size({'width':1440,'height':1000})
  # Owned fixture setup uses ordinary server-enforced view admission, never a permission bypass.
  for slot,unit in [('1','Owned.Elements::Unit'),('2','Owned.Elements::Monster')]:invoke('openEditorView',{'view':slot,'id':unit,'viewMode':'source'})
  page.reload();goto_editor(page,url)
  def window(key):return page.locator('.window[data-key="'+key+'"]')
  def tab(key):return page.locator('[data-window-tab="'+key+'"]')
  def group(key):return page.locator('[data-tab-order-key="window:'+key+'"]')
  def context(key,label):group(key).click(button='right');page.locator('.context-menu').get_by_role('button',name=label,exact=True).click()
  def dock(key):
   if tab(key).count():tab(key).click();return
   window(key).locator('.window-title').click(button='right',position={'x':100,'y':8});page.locator('.context-menu').get_by_role('button',name='탭으로 열기',exact=True).click();expect(tab(key)).to_be_visible()
  def flush():page.evaluate('()=>confectoryFlushPresentation()');return state()['presentation']
  def same_sources():assert all((project/k).read_bytes()==v for k,v in original.items())
  first=window('editor-1').locator('[data-editor-source]');second=window('editor-2').locator('[data-editor-source]');expect(first).to_be_visible(timeout=30000);expect(second).to_be_visible();a=first.input_value()+'\n// 문서 A 미저장 한글';b=second.input_value()+'\n// 문서 B 별도 입력';first.fill(a);second.fill(b);first.evaluate('e=>globalThis.originalDocumentA=e');second.evaluate('e=>globalThis.originalDocumentB=e');dock('editor-1');page.locator('#workspace-home-tab').click();dock('editor-2');expect(second).to_have_value(b);tab('editor-1').click();expect(first).to_have_value(a);assert first.evaluate('e=>e===originalDocumentA');geometry={'document':window('editor-1').bounding_box(),'canvas':page.locator('#workspace').bounding_box()};assert geometry['document']['x']==geometry['canvas']['x'] and geometry['document']['width']==geometry['canvas']['width'] and geometry['document']['y']==geometry['canvas']['y']+38;(case/'geometry.json').write_text(json.dumps(geometry));assert len(state()['editorViews'])==2;same_sources();checked('actual server-owned two editor views retain independent pending source DOM through original document tab selection')
  page.locator('#workspace-pack-tab').click();expect(page.locator('#pack-manager-view')).to_be_visible();group('editor-1').drag_to(page.locator('#workspace'),target_position={'x':700,'y':280});expect(tab('editor-1')).to_have_count(0);expect(first).to_be_visible();first.click();expect(page.locator('#workspace-pack-tab')).to_have_attribute('aria-selected','true');assert first.evaluate('e=>e===originalDocumentA');saved=flush();layout=next(row for row in saved['layout'] if row['key']=='editor-1');assert not layout['placed'] and layout['floatingTabId']=='pack-manager';assert saved['activeWorkspacePanel']=='pack-manager';page.screenshot(path=str(case/'actual-floating-pack.png'));checked('actual Pack Manager floating detachment keeps same source DOM, active background and persisted screen-space layout')
  dock('editor-1');tab('editor-2').click();group('editor-1').drag_to(page.locator('#workspace'),target_position={'x':700,'y':280});expect(first).to_be_visible();expect(second).to_be_visible();expect(tab('editor-2')).to_have_attribute('aria-selected','true');expect(second).to_have_value(b);first.fill(a+'\n// 플로팅 뒤 입력');a=first.input_value();same_sources();checked('actual floating above a second document preserves both pending inputs and server View bindings')
  # Browser has an ordinary shipped reopen route through the mobile List button.
  page.set_viewport_size({'width':390,'height':844});page.locator('[data-mobile-files]').click();browser_key='browser:project:mobile';expect(tab(browser_key)).to_be_visible();query=window(browser_key).locator('[data-browser-control="object-query"]');expect(query).to_be_enabled();query.fill('목록의 미전송 검색');page.set_viewport_size({'width':1440,'height':1000});context(browser_key,'왼쪽 탭 닫기');expect(tab('editor-2')).to_have_count(0);expect(second).to_have_value(b);assert len(state()['editorViews'])==2;context(browser_key,'모든 탭 닫기');expect(page.locator('[data-window-tab]')).to_have_count(0);expect(page.locator('#workspace-pack-tab')).to_have_count(1);page.set_viewport_size({'width':390,'height':844});page.locator('[data-mobile-files]').click();expect(query).to_have_value('목록의 미전송 검색');page.set_viewport_size({'width':1440,'height':1000});expect(first).to_have_value(a);expect(second).to_have_value(b);assert first.evaluate('e=>e===originalDocumentA');assert second.evaluate('e=>e===originalDocumentB');checked('actual left/all close preserves fixed tabs and server Views; ordinary mobile List reopens retained Browser without losing unrelated source inputs')
  page.locator('#workspace-pack-tab').click();flush();before=state();same_sources();page.close();stop();start(1);page=setup();page.set_viewport_size({'width':1440,'height':1000});first=window('editor-1').locator('[data-editor-source]');second=window('editor-2').locator('[data-editor-source]');expect(first).to_have_value(a,timeout=60000);expect(second).to_have_value(b,timeout=60000);expect(first).to_be_visible();expect(page.locator('#workspace-pack-tab')).to_have_attribute('aria-selected','true');expect(page.locator('#pack-manager-view')).to_be_visible();after=state();assert after['projectId']==before['projectId'] and len(after['editorViews'])==2;layout=next(row for row in after['presentation']['layout'] if row['key']=='editor-1');assert not layout['placed'] and layout.get('floatingTabId')==next(row for row in before['presentation']['layout'] if row['key']=='editor-1').get('floatingTabId');page.screenshot(path=str(case/'actual-cold-floating.png'));same_sources();checked('actual process restart restores floating owner/layout plus both unsaved source inputs and active Pack Manager without source writes')
  page.set_viewport_size({'width':390,'height':844});expect(page.locator('[data-mobile-files]')).to_be_visible();page.locator('[data-mobile-files]').click();query=window(browser_key).locator('[data-browser-control="object-query"]');expect(query).to_have_value('목록의 미전송 검색');page.screenshot(path=str(case/'actual-mobile-documents.png'));same_sources();checked('mobile document reopen after cold restoration keeps Browser text and project identity with native caption behavior unclaimed')
  assert not errors and not external,(errors,external);bad=[row['invoke']['endpoint'] for row in traffic if 'invoke' in row and row['invoke']['endpoint'] in ['confirm','saveDraft','saveEditorView','startAI','run','revoke']];assert not bad,bad;result={'checks':checks,'errors':errors,'external':external,'actualEngine':True,'viewSetupViaServer':True,'actualNativeWindows':False,'actualCredentialsOrInference':False,'sourceBytesUnchanged':True,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2));page.close();stop();browser.close()
except Exception:
 try:(case/'failure.json').write_text(json.dumps({'state':state(),'traffic':traffic,'errors':errors},ensure_ascii=False,indent=2))
 except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case),flush=True);raise
finally:stop()
