import json,os,pathlib,subprocess,tempfile,time,shutil,sys,signal,urllib.request
from playwright.sync_api import sync_playwright,expect
expect.set_options(timeout=30000)
repo=pathlib.Path(sys.argv[1]).resolve();report=json.load(open(sys.argv[2]));root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-inventory-v318-'))
project=root/'ordinary-button-game';shutil.copytree(repo/'examples/button-game',project,ignore=shutil.ignore_patterns('.confectory'));manifest=project/'project.cpack';manifest.write_text(manifest.read_text().replace('../../',str(repo)+'/'))
before={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file()}
env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(root/'storage'),CONFECTORY_ENTRY_STORAGE=str(root/'storage'),CONFECTORY_WEB_PROJECT=str(manifest),PATH=str(pathlib.Path(env.get('CONFECTORY_DOTNET','dotnet')).parent)+os.pathsep+env['PATH'])
def start(n):
 log=root/f'host-{n}.log';stream=log.open('w');host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
 deadline=time.monotonic()+60
 while time.monotonic()<deadline:
  for line in log.read_text().splitlines():
   if line.startswith('CONFECTORY_WEB_UI '):return host,stream,line.split(' ',1)[1]
  if host.poll() is not None:raise AssertionError(log.read_text())
  time.sleep(.1)
 os.killpg(host.pid,signal.SIGTERM);host.wait(timeout=10);stream.close();raise AssertionError(log.read_text())
def stop(host,stream):
 os.killpg(host.pid,signal.SIGTERM)
 try:host.wait(timeout=10)
 except subprocess.TimeoutExpired:os.killpg(host.pid,signal.SIGKILL);host.wait()
 stream.close()
def saved():
 files=list((root/'storage/presentations').glob('*.json'));assert len(files)==1,files
 return json.loads(files[0].read_text())
def public_state(url):
 token=url.split('#',1)[1];endpoint=url.split('#',1)[0]+'api/request'
 def send(body):
  request=urllib.request.Request(endpoint,data=json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':token})
  for _ in range(400):
   with urllib.request.urlopen(request,timeout=30) as reply:result=json.load(reply)
   if result.get('error',{}).get('code')!='busy':return result
   time.sleep(.01)
  raise AssertionError('read-only mount/dispose remained busy')
 mounted=send({'op':'mount'});assert mounted['ok'],mounted
 try:return mounted['state']
 finally:assert send({'op':'dispose','view':mounted['view']})['ok']
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for n in range(3):
  if n==2:env['CONFECTORY_WEB_PROJECT']=str(repo/'examples/editor-home/project.cpack')
  host,stream,url=start(n);page=browser.new_page(viewport={'width':1440,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(url);page.locator('.work-body').wait_for(timeout=30000)
  try:
   if n==0:
    page.locator('#nav').click();page.locator('.nav-menu button').filter(has_text='개념').first.click();expect(page.locator('#nav')).to_be_enabled();page.locator('#nav').click();main=page.locator('.window[data-key="browser"]');main.locator('[data-browser-projection-refresh]').click();expect(main.locator('[data-namespace="Example.ButtonGame"]')).to_be_visible();main.locator('[data-toggle-namespace="Confectory"]').click();expect(main.locator('[data-namespace="Confectory.BaseUI"]')).to_have_count(0);main.locator('[data-toggle-namespace="Confectory"]').click();state=public_state(url);inventory=state['inventory'];assert inventory['status']=='available';assert inventory['namespace']=='Example.ButtonGame';assert len(inventory['packs'])>1;assert not any('path' in p for p in inventory['packs']);assert any(p['namespace']=='Confectory.BaseUI' for p in inventory['packs']);owned=[d for d in inventory['declarations'] if d['owned']];assert any(d['id']=='Example.ButtonGame::Score' for d in owned)
    main.locator('[data-namespace="Example.ButtonGame"]').click();expect(main.locator('[data-id="Example.ButtonGame::Score"]')).to_be_visible();main.locator('[data-catalog-root]').click();expect(main.locator('[data-id="Example.ButtonGame::Score"]')).to_be_visible();expect(main.locator('[data-new]')).to_be_enabled();main.locator('[data-namespace="Example.ButtonGame"]').click();main.locator('[data-id="Example.ButtonGame::Score"]').click();expect(page.locator('[data-description]')).to_be_visible();page.locator('[data-description]').fill('inventory pending input');page.locator('.window[data-key="schema"] [data-close]').click()
    main.locator('#browser-actions').click();page.get_by_role('button',name='같은 브라우저 새 창으로 열기',exact=True).click();other=page.locator('.window[data-key^="browser:"]');expect(other).to_have_count(1);other.locator('[data-namespace="Confectory.BaseUI"]').click();expect(other.locator('[data-new]')).to_be_disabled();other.locator('[data-tab="feature"]').click();expect(other.locator('[data-readonly=true]').first).to_be_visible();other.locator('[data-readonly=true]').first.click();expect(page.locator('.modal')).to_contain_text('읽기 전용');page.locator('.modal [data-close]').click();other.locator('[data-browser-control="object-query"]').fill('nonexistent namespace declaration');other.locator('[data-browser-control="object-search"]').click();expect(other.locator('.empty')).to_contain_text('검색 결과');expect(main.locator('[data-id="Example.ButtonGame::Score"]')).to_be_visible();other.locator('input[type=range]').fill('100');expect(other.locator('[data-browser-control="density-label"]')).to_have_text('Data');page.wait_for_function('()=>typeof globalThis.confectoryFlushPresentation==="function"');page.evaluate('()=>globalThis.confectoryFlushPresentation()');expect(page.locator('#workspace-save-state')).to_have_text('');other.locator('[data-toggle-namespace="Confectory"]').click();expect(other.locator('[data-namespace="Confectory.BaseUI"]')).to_have_count(0);expect(main.locator('[data-namespace="Confectory.BaseUI"]')).to_have_count(1);state=public_state(url);assert not state['draft']['dirty'];assert state['schema']['description']!='inventory pending input';page.screenshot(path=str(root/'actual-browser-instances.png'));other.locator('[data-browser-control="browser-actions"]').click();page.get_by_role('button',name='로컬 팩 목록',exact=True).click();expect(page.locator('.window[data-key="packs"] [data-pack="Example.ButtonGame"]')).to_be_visible();expect(page.locator('.window[data-key="packs"] input:not([disabled])')).to_have_count(0);page.screenshot(path=str(root/'actual-project-packs.png'))
    page.locator('.brand').click();expect(page.locator('.home-grid')).to_be_visible();page.locator('#home-tab-packs').click();expect(page.locator('.home-pack-row').first).to_be_visible();expect(page.locator('.home-section-title h1')).to_have_text('팩');expect(page.locator('.home-project-controls')).to_be_hidden();home=public_state(url)['inventory'];assert home['namespace']=='Confectory.EditorHome';assert len(home['packs'])>20;assert next(d for d in home['declarations'] if d['id']=='Confectory.EditorHome::AndroidExport')['parent']=='Confectory.AndroidExport.Settings::Defaults';page.locator('#home-pack-search').fill('Confectory.WorkerTasks');page.locator('#home-pack-search-form').get_by_role('button',name='검색 확인').click();expect(page.locator('.home-pack-row')).to_have_count(1);expect(page.locator('#home-pack-detail')).to_contain_text('Confectory.WorkerTasks');page.screenshot(path=str(root/'actual-local-catalogue.png'));page.locator('[data-pack-group="explore"]').click();expect(page.locator('#home-pack-list')).to_contain_text('계약은 연결되지');expect(page.locator('.home-pack-row')).to_have_count(0);expect(page.locator('#home-pack-refresh')).to_be_disabled();page.screenshot(path=str(root/'actual-local-packs.png'));page.locator('#home-tab-projects').click();expect(page.locator('.home-section-title h1')).to_have_text('프로젝트');expect(page.locator('.home-project-controls')).to_be_visible();page.locator('[data-enter]').first.click();expect(page.locator('.work-body')).to_be_visible();assert any(row['meta'].get('namespace')=='Confectory.BaseUI' for row in saved()['layout'])
   elif n==1:
    other=page.locator('.window[data-key^="browser:"]');expect(other).to_have_count(1);expect(other.locator('[data-browser-control="object-query"]')).to_have_value('nonexistent namespace declaration');expect(other.locator('input[type=range]')).to_have_value('100');expect(other.locator('[data-tab="feature"]')).to_have_class('selected');expect(other.locator('[data-toggle-namespace="Confectory"]')).to_have_attribute('aria-expanded','false');expect(page.locator('.window[data-key="packs"] [data-pack="Example.ButtonGame"]')).to_be_visible();page.locator('.window[data-key="packs"] [data-close]').click();main=page.locator('.window[data-key="browser"]');expect(main.locator('[data-namespace="Example.ButtonGame"]')).to_be_visible();main.locator('.window-title').click(position={'x':50,'y':15});expect(other.locator('.empty')).to_contain_text('검색 결과');main.locator('[data-id="Example.ButtonGame::Score"]').click();expect(page.locator('[data-description]')).to_have_value('inventory pending input');page.screenshot(path=str(root/'actual-browser-restart.png'))
   else:
    page.locator('#nav').click();page.locator('.nav-menu button').filter(has_text='개념').first.click();expect(page.locator('#nav')).to_be_enabled();page.locator('#nav').click();main=page.locator('.window[data-key="browser"]');main.locator('[data-browser-projection-refresh]').click();parent=main.locator('[data-parent="Confectory.AndroidExport.Settings::Defaults"]');expect(parent).to_have_count(1);parent.click();expect(main.locator('[data-id="Confectory.EditorHome::AndroidExport"]')).to_be_visible();assert main.locator('[data-readonly=true]').count()==0;page.screenshot(path=str(root/'actual-declaration-inheritance.png'))
   assert not errors,errors
   assert all((project/name).read_bytes()==data for name,data in before.items())
  except Exception as e:
   page.screenshot(path=str(root/f'failure-{n}.png'));raise AssertionError(str(e)+'\nEvidence: '+str(root)+'\nErrors: '+str(errors)) from e
  finally:page.close();stop(host,stream)
 browser.close()
print('PASS ordinary ProjectPack actual local inventory and independent namespace browsers '+str(root))
