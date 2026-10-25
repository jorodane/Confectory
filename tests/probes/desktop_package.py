"""Cross-publish/composition checks plus packaged engine web startup from unrelated cwd.
A Linux pass is not Windows apphost/WebView2 or actual double-click execution.
Only fixture data is used; no CLI login, plugin relay or external request.
An optional fixture path after repo/package reuses hash-verified fixture copies
read-only while new host/browser scratch follows TMPDIR.
"""
import hashlib,json,os,pathlib,re,shutil,signal,subprocess,sys,tempfile,time,urllib.request
repo=pathlib.Path(sys.argv[1]).resolve();reuse=pathlib.Path(sys.argv[3]).resolve() if len(sys.argv)>3 else None;root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-desktop-package-'));outside=root/'unrelated cwd';outside.mkdir();storage=root/'owned-data';storage.mkdir()
dotnet=os.environ.get('CONFECTORY_DOTNET','dotnet');tool=repo/'targets/editor-desktop/bin/Release/net10.0/Confectory.dll'
env=os.environ.copy();env.update(CONFECTORY_HOME_STORAGE=str(storage),CONFECTORY_ENTRY_STORAGE=str(storage),HOME=str(root/'owned-home'),CONFECTORY_MCP_DIRECTORY=str(root/'instances'))
package=pathlib.Path(sys.argv[2]).resolve() if len(sys.argv)>2 else root/'Windows result 한글'
if len(sys.argv)==2:
 result=subprocess.run([dotnet,str(tool),'package',str(repo),str(package)],cwd=outside,env=env,text=True,capture_output=True,timeout=360);assert result.returncode==0,result.stdout+result.stderr

def check(ok=True):
 result=subprocess.run([dotnet,str(package/'Confectory.dll'),'--check-package',str(package)+os.sep],cwd=outside,env=env,text=True,capture_output=True,timeout=45)
 assert (result.returncode==0)==ok,result.stdout+result.stderr
 return json.loads(result.stdout) if ok else result.stderr
# An owned copy of the existing runtime, deliberately without sdk/packs, proves
# startup does not accidentally depend on the build machine's SDK being found.
source=pathlib.Path(dotnet).resolve().parent;runtime=(reuse if reuse else root)/'runtime only'
if reuse:
 # Reuse only an exact, link-free SDK-less fixture; never alter the old copy.
 assert runtime.is_dir() and not runtime.is_symlink()
 expected={pathlib.Path('dotnet'):source/'dotnet'}
 for part in ['host','shared/Microsoft.NETCore.App']:
  expected.update({p.relative_to(source):p for p in (source/part).rglob('*') if p.is_file()})
 actual={p.relative_to(runtime):p for p in runtime.rglob('*') if p.is_file()}
 assert set(actual)==set(expected) and not any(p.is_symlink() for p in runtime.rglob('*'))
 assert all(hashlib.sha256(actual[name].read_bytes()).digest()==hashlib.sha256(path.read_bytes()).digest() for name,path in expected.items())
else:
 runtime.mkdir();shutil.copy2(source/'dotnet',runtime/'dotnet');shutil.copytree(source/'host',runtime/'host');(runtime/'shared').mkdir();shutil.copytree(source/'shared/Microsoft.NETCore.App',runtime/'shared/Microsoft.NETCore.App')
dotnet=str(runtime/'dotnet');env['CONFECTORY_DOTNET']=dotnet;env['DOTNET_ROOT']=str(runtime);env['PATH']=str(runtime)+os.pathsep+'/usr/bin:/bin'
assert subprocess.check_output([dotnet,'--list-sdks'],env=env,text=True).strip()==''
plan=check();assert plan['rid']=='win-x64' and plan['windowsExecuted'] is False
content=package/'content';assert pathlib.Path(plan['workingDirectory'])==content and pathlib.Path(plan['engineAssembly'])==content/'runtime/Confectory.App.dll'
for key in ['CONFECTORY_EDITOR_REPO','CONFECTORY_WEBVIEW_HOST','CONFECTORY_ELEMENT_AUTHORING_HOST','CONFECTORY_PROJECT_EXECUTION_HOST']:
 assert pathlib.Path(plan['environment'][key]).is_relative_to(package),key
assert pathlib.Path(plan['environment']['CONFECTORY_HOME_STORAGE'])==storage
resources=json.loads(re.search(r'\n(\{.*\})\n',(content/'examples/editor-home/WebBundle.csbody').read_text()).group(1))
# Verification rejects a changed resource and missing dependency before starting.
asset=content/'examples/editor-home/ui/index.html';original=asset.read_bytes()
try:asset.write_bytes(original+b'fixture corruption');assert 'missing or changed' in check(False)
finally:asset.write_bytes(original)
missing=content/'targets/webview-windows/bin/Release/net10.0-windows/Microsoft.Web.WebView2.Core.dll';held=missing.with_suffix('.fixture-held');missing.rename(held)
try:assert 'missing or changed' in check(False)
finally:held.rename(missing)
check()
# Default output in an owned checkout reuses existing settings instead of opening
# an empty profile. Explicit overrides above still win. Never touch user profiles.
legacy=(reuse if reuse else root)/'owned checkout';legacy_package=legacy/'Builds/Windows-x64';legacy_storage=legacy/'.confectory/editor-home';sentinel=legacy_storage/'retained-settings'
if reuse:
 marker='confectory-desktop-package.json';manifest=json.loads((package/marker).read_text())
 assert (legacy_package/marker).read_bytes()==(package/marker).read_bytes()
 actual={p.relative_to(legacy_package).as_posix():p for p in legacy_package.rglob('*') if p.is_file()}
 assert set(actual)==set(manifest['files'])|{marker} and not any(p.is_symlink() for p in legacy_package.rglob('*'))
 assert all(hashlib.sha256(actual[name].read_bytes()).hexdigest()==digest for name,digest in manifest['files'].items())
 assert (legacy/'examples/editor-home/project.cpack').read_text()=='owned source marker' and sentinel.read_bytes()==b'fixture user profile unchanged'
else:
 shutil.copytree(package,legacy_package);(legacy/'examples/editor-home').mkdir(parents=True);(legacy/'examples/editor-home/project.cpack').write_text('owned source marker');legacy_storage.mkdir(parents=True);sentinel.write_bytes(b'fixture user profile unchanged')
no_override=env.copy();no_override.pop('CONFECTORY_HOME_STORAGE',None);no_override.pop('CONFECTORY_ENTRY_STORAGE',None)
legacy_plan=json.loads(subprocess.check_output([dotnet,str(legacy_package/'Confectory.dll'),'--check-package',str(legacy_package)],cwd=outside,env=no_override,text=True))
assert pathlib.Path(legacy_plan['environment']['CONFECTORY_HOME_STORAGE'])==legacy_storage and sentinel.read_bytes()==b'fixture user profile unchanged'
launch=env.copy();launch.update(plan['environment']);launch.update(CONFECTORY_UI='web',CONFECTORY_MCP_DIRECTORY=str(root/'instances'))
for key in ['CONFECTORY_WEB_PROJECT','CONFECTORY_BROWSER_PROJECT','CONFECTORY_WINDOWLESS_EDIT','CONFECTORY_ELEMENT_UI']:launch.pop(key,None)
log_path=root/'packaged-host.log';log=log_path.open('w');host=subprocess.Popen([dotnet,plan['engineAssembly']],cwd=outside,env=launch,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
try:
 deadline=time.monotonic()+60;url=None
 while time.monotonic()<deadline:
  for line in log_path.read_text().splitlines():
   if line.startswith('CONFECTORY_WEB_UI '):url=line.split(' ',1)[1]
  if url:break
  assert host.poll() is None,log_path.read_text();time.sleep(.05)
 assert url,log_path.read_text();origin,token=url.split('/#')
 for name,row in resources.items():
  data=urllib.request.urlopen(origin+'/'+name,timeout=10).read();assert len(data)==row.get('canonicalSize',row.get('size')) and hashlib.sha256(data).hexdigest()==row.get('canonicalSha256',row.get('sha256')),name
 sys.path.insert(0,str(repo/'tests/web'));from editor_navigation import goto_editor
 from playwright.sync_api import sync_playwright,expect
 with sync_playwright() as playwright:
  browser=playwright.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu']);page=browser.new_page(viewport={'width':1440,'height':1000});errors=[];external=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  def route(r):
   if r.request.url.startswith(origin):r.continue_()
   else:external.append(r.request.url);r.abort()
  page.route('**/*',route);goto_editor(page,url);page.locator('#add-agent').click();dialog=page.get_by_role('dialog',name='Agent 추가',exact=True);dialog.get_by_role('button',name='Codex',exact=True).click();expect(dialog.locator('[data-cli-login]')).to_be_enabled();expect(dialog.locator('[data-connection-advanced],input,select,textarea')).to_have_count(0);page.screenshot(path=str(root/'packaged-login.png'));assert not errors and not external,(errors,external);browser.close()
finally:
 if host.poll() is None:os.killpg(host.pid,signal.SIGTERM)
 host.wait(timeout=15);log.close()
record={'pass':True,'package':str(package),'files':plan['files'],'crossPublishedWindowsX64PE':True,'unrelatedWorkingDirectory':True,'packageTamperAndMissingDependencyRejected':True,'packagedEngineWebStartup':True,'runtimeOnlyNoInstalledSDK':True,'existingCheckoutProfileReusedAndExplicitOverrideRetained':True,'fixtureCopiesReusedReadOnly':str(reuse) if reuse else None,'resources':len(resources),'renderedMinimalLogin':True,'windowsApphostExecuted':False,'webView2Executed':False,'actualLoginOrInference':False,'evidence':str(root)}
(root/'evidence.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2));print('PASS Windows x64 package composition and actual packaged engine web startup; Windows execution unverified')
