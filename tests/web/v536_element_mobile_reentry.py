"""Resume only an isolated failed three-view fixture; verify cancel without resetting its data."""
import json,os,pathlib,signal,subprocess,sys,time,urllib.request
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());case=pathlib.Path(sys.argv[3]).resolve();assert case.parent==pathlib.Path('/tmp') and case.name.startswith('confectory-element-reentry-') and (case/'failure.json').is_file()
project=case/'owned project';original={p:p.read_bytes() for p in project.iterdir() if p.is_file()};env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(case/'profile'),CONFECTORY_ENTRY_STORAGE=str(case/'profile'),CONFECTORY_MCP_DIRECTORY=str(case/'mobile-reentry-instances'),CONFECTORY_WEB_PROJECT=str(project/'project.cproj'),CONFECTORY_DOTNET='/workspace/toolchains/dotnet-10.0.401/dotnet');env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];log=(case/'mobile-reentry.log').open('w');host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);errors=[];traffic=[]
def observe(response):
 try:
  data=response.request.post_data_json
  if not isinstance(data,dict):return
  if data.get('op')=='invoke':traffic.append({'invoke':data})
  elif data.get('op')=='update':
   for result in response.json().get('results',[]):traffic.append({'result':result})
 except Exception:pass
initial_third=sys.argv[4] if len(sys.argv)>4 else '226';assert initial_third in ['225','226']
try:
 for _ in range(600):
  urls=[s.split(' ',1)[1] for s in (case/'mobile-reentry.log').read_text().splitlines() if s.startswith('CONFECTORY_WEB_UI ')]
  if urls:url=urls[-1];origin,token=url.split('/#');break
  assert host.poll() is None;time.sleep(.05)
 else:raise AssertionError('startup timeout')
 def send(body):return json.load(urllib.request.urlopen(urllib.request.Request(origin+'/api/request',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':token}),timeout=20))
 def state():
  for _ in range(300):
   value=send({'op':'mount'})
   if value.get('ok'):break
   assert value.get('error',{}).get('code')=='busy';time.sleep(.02)
  try:return value['state']
  finally:send({'op':'dispose','view':value['view']})
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page(viewport={'width':2700,'height':1500});page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',observe);page.route('**/*',lambda r:r.continue_() if r.request.url.startswith(origin+'/') else r.abort());goto_editor(page,url)
  def w(slot):return page.locator('.window[data-key="editor-'+str(slot)+'"]')
  def hp(slot):return w(slot).locator('[aria-label="HP 기본값"]')
  expect(hp(1)).to_have_value('111',timeout=60000);expect(hp(2)).to_have_value('225');expect(hp(3)).to_have_value(initial_third);before=state();assert len(before['editorViews'])==3;owner=before['projectId']
  # A floating window correctly intercepts covered controls. Use its shipped close,
  # preserving input, before asking the mobile Browser underneath to receive clicks.
  for slot in [1,2,3]:
   if w(slot).is_visible():
    close_tab=page.locator('[data-window-tab-close="editor-'+str(slot)+'"]')
    if close_tab.count():close_tab.click()
    else:w(slot).locator('[data-close]').click()
  expect(hp(1)).to_have_value('111');expect(hp(3)).to_have_value(initial_third);page.set_viewport_size({'width':390,'height':844});page.locator('[data-mobile-files]').click();b=page.locator('.window[data-key="browser:project:mobile"]');q=b.locator('[data-browser-control="object-query"]');expect(q).to_be_enabled();q.fill('Slime');b.locator('[data-browser-control="object-search"]').click();b.locator('[data-object="Owned.Elements::Slime"]').get_by_role('button',name='정의 열기',exact=True).click();expect(page.locator('[data-window-tab="editor-1"]')).to_have_attribute('aria-selected','true');expect(hp(1)).to_have_value('111');assert not (page.locator('#toast').evaluate('e=>e.classList.contains("show")') and page.locator('#toast').inner_text()=='stale_revision');page.screenshot(path=str(case/'mobile-reentry-rechecked.png'));page.set_viewport_size({'width':2700,'height':1500});expect(hp(3)).to_have_value(initial_third);after=state();assert after['projectId']==owner and len(after['editorViews'])==3;assert all(p.read_bytes()==text for p,text in original.items());print('PASS actual mobile List reentry retains Slime111 and three source-owned bindings after explicit floating close; original files unchanged',flush=True)
  page.locator('[data-window-tab="browser:project:mobile"]').click();q.fill('Monster');b.locator('[data-browser-control="object-search"]').click();b.locator('[data-object="Owned.Elements::Monster"]').click(button='right',position={'x':8,'y':8});page.locator('.context-menu').get_by_role('button',name='새 창으로 열기',exact=True).click();expect(hp(3)).to_be_visible();expect(hp(3)).to_have_value(initial_third);assert len(state()['editorViews'])==3
  if initial_third=='225':hp(3).fill('227')
  w(3).locator('[data-element-action="discard"]').click();expect(hp(3)).to_have_value('225');expect(hp(1)).to_have_value('111');page.evaluate('()=>confectoryFlushPresentation()');messages=page.locator('[data-element-error]').all_text_contents();assert all(not message.strip() for message in messages),messages;after=state();assert after['projectId']==owner and len(after['editorViews'])==3;assert all(p.read_bytes()==text for p,text in original.items());assert not errors,errors;page.screenshot(path=str(case/'final-cursors-rechecked.png'));result={'actualEngine':True,'fixtureReusedWithoutReset':True,'initialThirdValue':initial_third,'checks':['mobile List definition reentry preserves pending Slime111 and source-owned three-cursor identities','original new-window reentry restores hidden Monster cursor rather than allocating a new slot','legacy cursor local cancel reads saved225 while Slime111 remains and all background status error fields are empty'],'elementStatusErrors':messages,'errors':errors,'sourceBytesUnchanged':True,'nativeWindows':False,'actualCredentialsOrInference':False};(case/'mobile-reentry-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2));browser.close()
except Exception:
 (case/'mobile-reentry-failure.json').write_text(json.dumps({'traffic':traffic,'errors':errors},ensure_ascii=False,indent=2))
 raise
finally:
 if host.poll() is None:os.killpg(host.pid,signal.SIGTERM);host.wait(timeout=15)
 log.close()
