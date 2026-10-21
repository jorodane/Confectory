"""Actual generated EditorHome workspace read/presentation regression; owned projects.
No Agent registration, account process, OAuth or model request.
"""
import json,os,pathlib,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-workspace-engine-'));project=root/'owned project';project.mkdir();storage=root/'profile'
(project/'project.cproj').write_text('project Owned.Workspace version "1" { standalone true; entry Owned.Workspace::Main; element Main function "Main.celem"; element MainBody implementation "MainBody.celem"; element Unit object "Unit.celem"; element Child object "Child.celem"; element Stats schema "Stats.celem"; element Tools module "Tools.celem"; registry Confectory.Build.DotNet "/workspace/Confectory/targets/dotnet/pack.cpack"; dependency Confectory.Build.DotNet version "0.1.0"; target portable Confectory.Build.DotNet::Portable; }')
for file,text in {'Main.celem':'function Owned.Workspace::Main () -> int { provide Owned.Workspace::Main with Owned.Workspace::MainBody; }','MainBody.celem':'implementation Owned.Workspace::MainBody for Owned.Workspace::Main () -> int { body common "Main.csbody"; }','Main.csbody':'return 0;','Unit.celem':'object Owned.Workspace::Unit { description "Owned parent"; }','Child.celem':'object Owned.Workspace::Child extends Owned.Workspace::Unit { }','Stats.celem':'schema Owned.Workspace::Stats { field hp single general int; }','Tools.celem':'module Owned.Workspace::Tools { description "Owned module"; }'}.items():(project/file).write_text(text)
manifest=project/'project.cproj';manifest.write_text(manifest.read_text().replace('/workspace/Confectory/targets/dotnet/pack.cpack',str(repo/'targets/dotnet/pack.cpack')));original={p.name:p.read_bytes() for p in project.iterdir()};env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_HOME_STORAGE=str(storage),CONFECTORY_ENTRY_STORAGE=str(storage),CONFECTORY_MCP_DIRECTORY=str(root/'instances'),CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_WEB_PROJECT=str(project/'project.cproj'),CONFECTORY_DOTNET=env.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet'));env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH']
checks=[];errors=[];external=[];traffic=[];host=None;log=None
def stop():
 global host,log
 if host and host.poll() is None:os.killpg(host.pid,signal.SIGTERM)
 if host:host.wait(timeout=15)
 if log:log.close()
def start(n):
 global host,log
 path=root/f'host-{n}.log';log=path.open('w');host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 for _ in range(600):
  urls=[l.split(' ',1)[1] for l in path.read_text().splitlines() if l.startswith('CONFECTORY_WEB_UI ')]
  if urls:return urls[-1]
  assert host.poll() is None,path.read_text()[-1800:];time.sleep(.05)
 raise AssertionError('host startup timeout')
def observe(response):
 try:
  payload=response.request.post_data_json
  if isinstance(payload,dict) and payload.get("op")=="invoke" and payload.get("endpoint")=="browserDrafts":traffic.append({"invoke":payload["input"],"requestId":payload["requestId"]})
  if isinstance(payload,dict) and payload.get("op")=="update":
   for item in response.json().get("results",[]):
    if any(row.get("requestId")==item.get("requestId") for row in traffic):traffic.append({"result":item})
 except Exception:pass
def completed(action):
 for _ in range(600):
  ids={row['requestId'] for row in traffic if row.get('invoke',{}).get('action')==action}
  results=[row['result'] for row in traffic if row.get('result',{}).get('requestId') in ids]
  accepted=[r for r in results if r.get('ok') and r.get('result',{}).get('state')=='applied']
  if accepted:return
  terminal=[r for r in results if not r.get('ok') and r.get('error',{}).get('code')!='stale_revision']
  assert not terminal,terminal
  page.wait_for_timeout(20)
 raise AssertionError('actual UI action not completed: '+action+' '+str(traffic[-5:]))
def raw(body):
 req=urllib.request.Request(origin+'/api/request',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':token});return json.load(urllib.request.urlopen(req,timeout=30))
def mount():
 for _ in range(300):
  v=raw({'op':'mount'})
  if v.get('error',{}).get('code')=='busy':page.wait_for_timeout(20);continue
  assert v['ok'],v;return v
 raise AssertionError('owned transport remained busy')
def state():
 v=mount()
 try:return v['state']
 finally:raw({'op':'dispose','view':v['view']})
def invoke(endpoint,body):
 for attempt in range(4):
  v=mount();rid=uuid.uuid4().hex
  try:
   ack=raw({'op':'invoke','view':v['view'],'scope':v['scope'],'expectedRevision':v['revision'],'requestId':rid,'endpoint':endpoint,'input':body});assert ack['ok'],ack
   for _ in range(600):
    update=raw({'op':'update','view':v['view'],'scope':v['scope']});found=[row for row in update.get('results',[]) if row['requestId']==rid]
    if found:result=found[0];break
    page.wait_for_timeout(10)
   else:raise AssertionError('owned action pending')
  finally:raw({'op':'dispose','view':v['view']})
  if result.get('error',{}).get('code')=='stale_revision' and attempt<3:continue
  assert 'error' not in result,result;return result
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);context=browser.new_context(viewport={'width':1280,'height':892})
  for iteration in range(2):
   url=start(iteration);origin,token=url.split('/#');page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',observe);page.route('**/*',lambda r:r.continue_() if r.request.url.startswith(origin) else (external.append(r.request.url),r.abort()));goto_editor(page,url);expect(page.locator('#workspace-pack-tab')).to_be_visible();assert not errors,errors
   if iteration==0:
    page.locator('#workspace-pack-tab').click();expect(page.locator('#pack-manager-view')).to_be_visible();expect(page.locator('#pack-manager-view [data-pack]')).to_have_count(2,timeout=30000);expect(page.locator('#pack-manager-view [data-pack="Owned.Workspace"]')).to_have_count(1);expect(page.locator('#pack-manager-view [data-pack="Confectory.Build.DotNet"]')).to_have_count(1);page.locator('[data-pack-favorite]').click();page.locator('[data-pack-group="favorite"]').click();expect(page.locator('#pack-manager-view [data-pack]')).to_have_count(1);page.screenshot(path=str(root/'actual-pack-manager.png'));checks.append('actual generated engine starts and projects real inventory into original Pack Manager')
    page.locator('#workspace-home-tab').click();page.locator('[data-workspace-zoom]').click();page.locator('[data-zoom-value]').fill('87.5');page.locator('[data-zoom-value]').press('Enter');page.locator('[data-zoom-value]').press('Escape');expect(page.locator('[data-workspace-zoom]')).to_have_text('87.5%')
    page.locator('#workspace').click(button='right',position={'x':700,'y':300});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();w=page.locator('.window[data-key^="browser:project:"]');expect(w).to_be_visible();expect(w.locator('[data-tab]')).to_have_count(4);expect(w.locator('[data-density]')).to_have_count(6);expect(w.locator('[data-tree-query],[data-tree-details],[data-browser-projection-refresh]')).to_have_count(0);expect(w.locator('.browser-title-path')).to_be_visible();
    for group,id in [('concept','Unit'),('feature','Main'),('module','Tools'),('info','Stats')]:
     w.locator('[data-tab="'+group+'"]').click();expect(w.locator('[data-object="Owned.Workspace::'+id+'"]')).to_be_visible()
    checks.append('real concept/info/feature/module rows use original chrome without developer panels')
    w.locator('[data-tab="concept"]').click();invoke('select',{'id':'Owned.Workspace::Unit'});draft=state()['draft'];saved_text='object Owned.Workspace::Unit { description "saved-one"; }';invoke('editDraft',{'id':draft['id'],'text':saved_text,'revision':draft['revision']});expect(w.locator('[data-browser-save]')).to_be_enabled(timeout=30000);w.locator('[data-browser-save]').click();completed('save');expect(w.locator('[data-browser-save]')).to_be_disabled();assert (project/'Unit.celem').read_bytes()==original['Unit.celem'];draft=state()['draft'];invoke('editDraft',{'id':draft['id'],'text':'object Owned.Workspace::Unit { description "unsaved-two"; }','revision':draft['revision']});expect(w.locator('[data-browser-discard]')).to_be_enabled(timeout=30000);w.locator('[data-browser-discard]').click();completed('discard')
    for _ in range(400):
     if state()['draft']['text']==saved_text:break
     page.wait_for_timeout(20)
    else:
     (root/'discard-failure.json').write_text(json.dumps({'state':state(),'traffic':traffic,'visibleText':page.locator('body').inner_text()},indent=2));page.screenshot(path=str(root/'discard-failure.png'));raise AssertionError('discard did not restore saved owned text; '+str(root))
    assert (project/'Unit.celem').read_bytes()==original['Unit.celem'];assert len({row['result']['requestId'] for row in traffic if row.get('result',{}).get('ok') and row['result'].get('result',{}).get('action') in ('save','discard')})==2;expect(w.locator('[data-browser-confirm]')).to_be_enabled();w.locator('[data-browser-confirm]').click();review=page.locator('.window[data-key="review"]');expect(review).to_be_visible(timeout=30000);expect(review.locator('#confirm')).to_be_visible();assert (project/'Unit.celem').read_bytes()==original['Unit.celem'];page.screenshot(path=str(root/'actual-browser-review.png'));review.locator('[data-reject]').click();checks.append('original Browser Save/Discard use real private checkpoint; Confirm opens guarded Review without final source writes')
    w.locator('[data-tab="info"]').click();expect(w.locator('[data-object="Owned.Workspace::Stats"]')).to_be_visible();w.locator('[data-browser-control="object-query"]').fill('Stats');w.locator('.window-title').click(button='right');page.locator('.context-menu').get_by_role('button',name='탭으로 열기',exact=True).click();expect(w).to_have_class(__import__('re').compile('window-document'));tab=page.locator('[data-window-tab]').first;tab.click();page.locator('#workspace-pack-tab').click();expect(w).to_be_hidden();expect(page.locator('#workspace-pack-tab')).to_have_attribute('aria-selected','true');tab.click();expect(w).to_be_visible();expect(page.locator('#pack-manager-view')).to_be_hidden();expect(w.locator('[data-browser-control="object-query"]')).to_have_value('Stats');checks.append('Project Browser info projection and window document/Pack Manager transitions preserve input')
    page.locator('#workspace-pack-tab').click();page.evaluate('async()=>{await confectoryFlushPresentation();}');page.screenshot(path=str(root/'before-restart.png'))
   else:
    expect(page.locator('#pack-manager-view')).to_be_visible(timeout=30000);expect(page.locator('[data-pack-group="favorite"]')).to_have_attribute('aria-selected','true');expect(page.locator('#pack-manager-view [data-pack]')).to_have_count(1);page.locator('#workspace-home-tab').click();expect(page.locator('[data-workspace-zoom]')).to_have_text('87.5%');tab=page.locator('[data-window-tab]').first;expect(tab).to_be_visible();tab.click();w=page.locator('.window[data-key^="browser:project:"]');expect(w.locator('[data-browser-control="object-query"]')).to_have_value('Stats');page.screenshot(path=str(root/'after-restart.png'));checks.append('engine restart restores Pack Manager selection/favorite, zoom and document search without editing project')
   page.close();stop()
  assert not errors and not external,(errors,external);assert all((project/name).read_bytes()==data for name,data in original.items());assert {p.name for p in project.iterdir() if p.is_file()}==set(original);browser.close()
finally:stop()
record={'checks':checks,'pageErrors':errors,'external':external,'actualEngine':True,'accountOrInference':False,'nativeWindows':False,'evidence':str(root)};(root/'evidence.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
