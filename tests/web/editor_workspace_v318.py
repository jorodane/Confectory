import json,os,pathlib,subprocess,tempfile,time,shutil,sys,signal,urllib.request
from playwright.sync_api import sync_playwright,expect
expect.set_options(timeout=30000)
repo=pathlib.Path(sys.argv[1]).resolve();report=json.load(open(sys.argv[2]));root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-workspace-v318-'))
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
  with urllib.request.urlopen(request,timeout=30) as reply:return json.load(reply)
 mounted=send({'op':'mount'});assert mounted['ok'],mounted
 try:return mounted['state']
 finally:assert send({'op':'dispose','view':mounted['view']})['ok']
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);errors=[]
 try:
  for n in range(2):
   host,stream,url=start(n)
   try:
    page=browser.new_page(viewport={'width':1440,'height':1000});page.set_default_timeout(60000);page.on('pageerror',lambda e:errors.append(str(e)));page.goto(url);page.locator('#workspace-home-tab').wait_for()
    def create(kind,x,y):
     page.locator('#workspace').click(button='right',position={'x':x,'y':y});page.get_by_role('button',name={'note':'메모 만들기','group':'그룹 만들기','portal':'하위 Workspace 만들기'}[kind],exact=True).click();expect(page.locator('.workspace-'+kind)).not_to_have_count(0)
     return page.locator('.workspace-'+kind).last
    def open_browser():
     page.locator('#nav').click();page.locator('.nav-menu button').filter(has_text='개념').first.click();expect(page.locator('#nav')).to_be_enabled();page.locator('#nav').click();page.locator('[data-id="Example.ButtonGame::Score"]').wait_for()
    def advanced():
     page.locator('#browser-actions').click();page.locator('#advanced-source').click();expect(page.locator('#source')).to_be_visible()
    def drag(locator,point):
     box=locator.bounding_box();page.mouse.move(box['x']+box['width']-85,box['y']+16);page.mouse.down();page.mouse.move(point[0],point[1],steps=12);page.mouse.up()
    if n==0:
     open_browser();page.locator('[data-id="Example.ButtonGame::Score"]').click();expect(page.locator('[data-description]')).to_be_visible();page.locator('[data-description]').fill('pending workspace description');page.locator('.window[data-key="schema"] [data-close]').click();page.locator('#browser-actions').click();page.locator('#keep-properties').click();prop=page.locator('.window[data-key="editor-1"]');expect(prop.locator('[data-description]')).to_be_visible();prop.locator('[data-description]').fill('pending independent description');prop.locator('[data-close]').click();advanced();original=page.locator('#source').input_value();page.locator('#source').fill(original+'\n// WORKSPACE_PENDING_INPUT')
     note=create('note',370,580);note.locator('textarea').fill('root note X');group=create('group',630,610);portal=create('portal',950,625);portal_id=portal.get_attribute('data-workspace-id')
     target=portal.bounding_box();drag(page.locator('.window[data-key="source"] .window-title'),(target['x']+target['width']/2,target['y']+target['height']/2));expect(page.locator('#source')).to_have_count(0);portal.dblclick();expect(page.locator('#source')).to_have_value(original+'\n// WORKSPACE_PENDING_INPUT');page.locator('.workspace-parent-node').dblclick();expect(page.locator('.workspace-note')).to_have_count(1)
     page.locator('#workspace-tab-'+portal_id).click();page.get_by_role('button',name='Workspace 1 탭 닫기',exact=True).click();expect(page.locator('#workspace-tab-'+portal_id)).to_have_count(0);expect(page.locator('.workspace-portal')).to_have_count(1);page.locator('.workspace-portal').dblclick();expect(page.locator('#source')).to_have_value(original+'\n// WORKSPACE_PENDING_INPUT');page.locator('.workspace-parent-node').dblclick()
     note=page.locator('.workspace-note');note.locator('textarea').focus();note.locator('textarea').press('Home');note.locator('textarea').press('Delete');expect(page.locator('.workspace-note')).to_have_count(1)
     page.locator('#workspace-home-tab').click();page.locator('#workspace').click(position={'x':1100,'y':650})
     canvas=page.locator('#workspace').bounding_box();page.mouse.move(canvas['x']+3,canvas['y']+42);page.mouse.down();page.mouse.move(canvas['x']+canvas['width']-8,canvas['y']+canvas['height']-8,steps=12);page.mouse.up()
     expect(page.locator('.multi-selected')).to_have_count(4)
     geometry=lambda:page.locator('.multi-selected').evaluate_all("nodes=>nodes.map(n=>[n.dataset.key||n.dataset.workspaceItem,n.style.left,n.style.top,n.style.width,n.style.height])")
     before_drag=geometry();handle=page.locator('.workspace-note .workspace-multi-drag-surface');box=handle.bounding_box();page.mouse.move(box['x']+30,box['y']+50);page.mouse.down();page.mouse.move(box['x']+50,box['y']+70,steps=6);page.evaluate("() => {const node=[...document.querySelectorAll('*')].find(n=>n.hasPointerCapture?.(1));if(!node)throw Error('Actual pointer capture absent');node.dispatchEvent(new PointerEvent('pointercancel',{pointerId:1,bubbles:true}));}");page.mouse.up();assert geometry()==before_drag;expect(page.locator('.multi-selected')).to_have_count(4)
     page.locator('#workspace').press('Delete');expect(page.locator('.modal')).to_contain_text('실제 객체와 프로젝트 파일은 삭제하지');page.locator('.modal [data-cancel]').click();expect(page.locator('.multi-selected')).to_have_count(4);page.locator('#workspace').press('Delete');page.locator('.modal [data-confirm]').click();expect(page.locator('.workspace-decoration')).to_have_count(0);expect(page.locator('.window[data-key="browser"]')).to_have_count(0);expect(page.locator('.window[data-key="editor-1"]')).to_be_hidden()
     open_browser();advanced();expect(page.locator('#source')).to_have_value(original+'\n// WORKSPACE_PENDING_INPUT')
     portal=create('portal',960,625);target=portal.bounding_box();drag(page.locator('.window[data-key="source"] .window-title'),(target['x']+target['width']/2,target['y']+target['height']/2));portal.dblclick();child=create('note',820,590);child.locator('textarea').fill('persistent child note');size=child.evaluate('n=>parseFloat(n.style.width)');child.locator('.resize-se').press('ArrowRight');assert child.evaluate('n=>parseFloat(n.style.width)')==size+20
     canvas=page.locator('#workspace').bounding_box();page.mouse.move(canvas['x']+1100,canvas['y']+630);page.mouse.down(button='middle');page.mouse.move(canvas['x']+1120,canvas['y']+650,steps=6);page.mouse.up(button='middle');page.locator('#workspace').hover(position={'x':1100,'y':620});page.mouse.wheel(0,-100);page.wait_for_timeout(600);expect(page.locator('#workspace-save-state')).to_have_text('배치 저장됨');snapshot=saved();assert snapshot['activeWorkspaceId']!='root';assert snapshot['workspaceView']['scale']>1;assert snapshot['inputs']['source']['dirty'];assert 'WORKSPACE_PENDING_INPUT' in snapshot['inputs']['source']['text'];state=public_state(url);assert state['draft']['text']==original;assert not state['draft']['dirty'];assert state['editorViews'][0]['schema']['description']!='pending independent description';assert not state['editorViews'][0]['draft']['dirty'];page.screenshot(path=str(root/'actual-before-restart.png'))
    else:
     expect(page.locator('#workspace-save-state')).to_have_text('배치 저장됨')
     expect(page.locator('#workspace-home-tab')).to_have_attribute('aria-selected','false');expect(page.locator('.workspace-note textarea')).to_have_value('persistent child note');assert 'WORKSPACE_PENDING_INPUT' in page.locator('#source').input_value();assert any(value.get('text')=='pending workspace description' for _,value in saved()['inputs']['schema']);assert any(row['view']=='1' and row['id']=='Example.ButtonGame::Score' for row in saved()['editorBindings']);page.screenshot(path=str(root/'actual-after-restart.png'));assert float(page.locator('#workspace').evaluate("n=>n.style.getPropertyValue('--canvas-grid-size').replace('px','')"))>22;page.locator('.workspace-tabs [aria-selected="true"]').click();page.locator('.workspace-parent-node').dblclick();open_browser();page.locator('[data-id="Example.ButtonGame::Score"]').click(button='right');page.get_by_role('button',name='스키마 열기',exact=True).click();expect(page.locator('.window[data-key="schema"] [data-description]')).to_have_value('pending workspace description');page.screenshot(path=str(root/'actual-restored-description.png'));page.locator('.window[data-key="schema"] [data-close]').click();page.locator('#browser-actions').click();page.get_by_role('button',name='유지된 창 · Example.ButtonGame::Score',exact=True).click();expect(page.locator('.window[data-key="editor-1"] [data-description]')).to_have_value('pending independent description');page.screenshot(path=str(root/'actual-restored-view.png'))
    assert not errors,errors;page.close()
   except Exception as error:
    page.screenshot(path=str(root/f'failure-{n}.png'));(root/f'failure-{n}.html').write_text(page.content());raise AssertionError(str(error)+'\nPage errors: '+str(errors)+'\nStatus: '+str(page.locator('#toast').text_content())+'\nEvidence: '+str(root)) from error
   finally:stop(host,stream)
 finally:browser.close()
for name,data in before.items():assert (project/name).read_bytes()==data,name
print('PASS ordinary ProjectPack common Workspace child move close cancel mixed Delete pending input presentation restart and source preservation',root)
