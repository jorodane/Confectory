"""Generated EditorHome titlebar/display profile integration, empty private fixture.
Pass an isolated build report. Uses simulated window replies, not Win32.
"""
import json,os,pathlib,re,signal,subprocess,sys,tempfile,time
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-titlebar-engine-'));storage=root/'profile'
env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_HOME_STORAGE=str(storage),CONFECTORY_ENTRY_STORAGE=str(storage),CONFECTORY_MCP_DIRECTORY=str(root/'instances'),CONFECTORY_EDITOR_REPO=str(report.get('sourceRoot',pathlib.Path(sys.argv[2]).parent)),CONFECTORY_DOTNET=env.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet'))
env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];env.pop('CONFECTORY_WEB_PROJECT',None)
bridge="""globalThis.windowCalls=[];globalThis.windowState={supported:true,customCaption:false,state:'normal',dpi:96,active:true};Object.defineProperty(window,'confectoryWebUI',{value:Object.freeze({windowChromeSupported:true,async windowCommand(command,enabled){windowCalls.push({command,enabled});if(command==='chrome')windowState.customCaption=enabled;if(command==='toggle-maximize')windowState.state=windowState.state==='normal'?'maximized':'normal';return {ok:true,state:{...windowState}};}})});"""
checks=[];errors=[];external=[];host=None;log=None
def stop():
 global host,log
 if host and host.poll() is None:os.killpg(host.pid,signal.SIGTERM)
 if host:host.wait(timeout=15)
 if log:log.close()
def start(number):
 global host,log
 path=root/f'host-{number}.log';log=path.open('w');host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 for _ in range(600):
  urls=[s.split(' ',1)[1] for s in path.read_text().splitlines() if s.startswith('CONFECTORY_WEB_UI ')]
  if urls:return urls[-1]
  assert host.poll() is None,path.read_text();time.sleep(.05)
 raise AssertionError('engine URL not available')
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);context=browser.new_context(viewport={'width':1280,'height':892});context.add_init_script(bridge)
  for iteration in range(3):
   if iteration==2:
    project=root/'owned project';project.mkdir();(project/'project.cproj').write_text('project Owned.Window version "1" { standalone true; entry Owned.Window::Main; element Main function "Main.celem"; element MainBody implementation "MainBody.celem"; }');(project/'Main.celem').write_text('function Owned.Window::Main () -> int { provide Owned.Window::Main with Owned.Window::MainBody; }');(project/'MainBody.celem').write_text('implementation Owned.Window::MainBody for Owned.Window::Main () -> int { body common "Main.csbody"; }');(project/'Main.csbody').write_text('return 0;');env['CONFECTORY_WEB_PROJECT']=str(project/'project.cproj')
   url=start(iteration);origin=url.split('/#')[0];page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
   page.route('**/*',lambda r:r.continue_() if r.request.url.startswith(origin) else (external.append(r.request.url),r.abort()))
   goto_editor(page,url);page.wait_for_function("()=>document.documentElement.dataset.nativeCaption==='true'");expect(page.locator('.app-my-info-button')).to_have_count(1);expect(page.locator('.app-window-controls')).to_be_visible();page.locator('.app-my-info-button').click();expect(page.locator('#my-info-name')).to_have_value('나' if iteration==0 else '지속되는 표시 이름')
   if iteration==0:
    page.locator('#my-info-name').fill('지속되는 표시 이름');page.locator('#my-info-title').fill('표시 프로필');page.locator('#my-info-form button[type=submit]').click();expect(page.locator('#my-info-form')).to_have_count(0);assert json.loads((storage/'user-profile.json').read_text())['name']=='지속되는 표시 이름';checks.append('real owned userProfile endpoint stores display fields without account/auth')
    page.reload();goto_editor(page,page.url);page.wait_for_function("()=>document.documentElement.dataset.nativeCaption==='true'");page.locator('.app-my-info-button').click();expect(page.locator('#my-info-name')).to_have_value('지속되는 표시 이름');checks.append('actual renderer reload rehydrates profile')
   else:checks.append('engine process restart uses private persisted display profile' if iteration==1 else 'project screen uses same native titlebar and display profile')
   page.screenshot(path=str(root/f'engine-profile-{iteration}.png'));page.get_by_role('dialog',name='내 정보',exact=True).locator('[data-close]').click();assert page.evaluate('async()=>{await confectoryFlushPresentation();return true;}');assert page.locator('#app').evaluate('(e)=>!e.inert');page.locator('[data-app-maximize]').click();expect(page.locator('[data-app-maximize]')).to_have_attribute('aria-pressed','true');checks.append('generated runtime flush and native simulated maximize leave app usable')
   page.screenshot(path=str(root/f'engine-home-{iteration}.png'));page.close();stop()
  assert not errors and not external,(errors,external);browser.close()
finally:stop()
record={'checks':checks,'pageErrors':errors,'externalRequests':external,'nativeWindowsExecuted':False,'accountOrInference':False,'evidence':str(root)};(root/'evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False,indent=2))
