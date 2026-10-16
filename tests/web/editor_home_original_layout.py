import json,os,pathlib,subprocess,tempfile,time,shutil,http.server,threading
from playwright.sync_api import sync_playwright,expect
import sys
repo=pathlib.Path(sys.argv[1]).resolve();report=json.load(open(sys.argv[2]));reference=pathlib.Path(sys.argv[3]).resolve()
root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-original-layout-'));project=root/'regular-button-game';shutil.copytree(repo/'examples/button-game',project,ignore=shutil.ignore_patterns('.confectory'));manifest=project/'project.cpack';manifest.write_text(manifest.read_text().replace('../../',str(repo)+'/'));env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_ENTRY_STORAGE=str(root/'storage'),CONFECTORY_HOME_STORAGE=str(root/'storage'),CONFECTORY_WEB_PROJECT=str(manifest),PATH=str(pathlib.Path(env.get('CONFECTORY_DOTNET','dotnet')).parent)+os.pathsep+env['PATH'])
log=(root/'host.log').open('w');host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT)
class Static(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(reference),**k)
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Static);threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 deadline=time.monotonic()+50;url=None
 while time.monotonic()<deadline:
  for l in (root/'host.log').read_text().splitlines():
   if l.startswith('CONFECTORY_WEB_UI '):url=l.split(' ',1)[1]
  if url:break
  if host.poll() is not None:raise Exception((root/'host.log').read_text())
  time.sleep(.1)
 assert url
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=b.new_page(viewport={'width':1440,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(url);page.locator('.work-body').wait_for();page.wait_for_timeout(3600);page.screenshot(path=str(root/'consumer-project.png'))
  def open_browser():
   selected=page.locator('.window[data-key="browser"] [data-tab].selected');group=selected.get_attribute('data-tab') if selected.count() else 'concept'
   page.locator('#nav').click();page.locator('.nav-menu button').filter(has_text={'concept':'개념','feature':'기능','module':'모듈'}[group]).first.click();expect(page.locator('#nav')).to_be_enabled();page.locator('#nav').click()
  page.locator('.brand').click();page.locator('.home-grid').wait_for();page.wait_for_timeout(3600);page.screenshot(path=str(root/'consumer-home.png'));assert page.locator('.home-side').count()==1;assert page.locator('.home-project-actions #new-project').count()==1;assert page.locator('.project-card-stats').count()==1;assert page.locator('#reconnect').count()==0
  page.locator('#new-project').click();page.locator('#project-name').fill('Original Flow');page.screenshot(path=str(root/'consumer-create.png'));expect(page.locator('.modal')).to_be_visible();expect(page.locator('#main-helper')).to_be_disabled();page.locator('[data-close]').click()
  page.locator('.app-settings-button').click();page.locator('#settings-sidebar-width').fill('270');assert page.locator('.home-grid').evaluate('(n)=>n.style.getPropertyValue("--participant-width")')=='270px';page.locator('[data-close]').click()
  page.locator('[data-enter]').click();page.locator('.work-body').wait_for();open_browser();expect(page.locator('[data-id="Example.ButtonGame::Score"]')).to_be_visible();page.locator('[data-id="Example.ButtonGame::Score"]').click();expect(page.locator('[data-schema-id]')).to_have_text('Example.ButtonGame::Score');page.screenshot(path=str(root/'consumer-schema.png'))
  page.locator('#chat-input').fill('Preserved project message');page.locator('#chat-input').blur();expect(page.locator('#status')).to_contain_text('전송 없음');page.locator('.brand').click();page.locator('[data-enter]').click();expect(page.locator('#chat-input')).to_have_value('Preserved project message',timeout=30000);assert not errors,errors
  ref=b.new_page(viewport={'width':1440,'height':1000});ref.goto('http://127.0.0.1:'+str(server.server_port));ref.evaluate('showHome()');ref.evaluate('document.fonts.ready');ref.screenshot(path=str(root/'original-home.png'));
  shape='n=>[n.tagName,n.className,[...n.children].map(c=>[c.tagName,c.className,[...c.children].map(x=>[x.tagName,x.className])])]'
  page.locator('.brand').click();page.locator('.home-grid').wait_for();
  # Home heading/actions migrated to v318; only unchanged card interiors retain v196 characterization.
  for region in ['.project-card-main','.project-card-stats']:
   assert page.locator(region).first.evaluate(shape)==ref.locator(region).first.evaluate(shape),region
  page.locator('#add-agent').click();page.get_by_role('dialog',name='사용할 AI',exact=True).get_by_role('button',name='OpenAI Responses',exact=True).click();expect(page.locator('[data-connection-field="model"]')).to_be_visible(timeout=60000);page.screenshot(path=str(root/'consumer-settings.png'));page.locator('[data-connection-cancel]').click();
  ref.evaluate("enterProject('demo')");ref.screenshot(path=str(root/'original-project.png'));ref.evaluate('showHome();createProject()');ref.screenshot(path=str(root/'original-create.png'))
  ref.locator('.modal [data-close]').click();ref.evaluate("enterProject('demo');toggleNav()");ref.screenshot(path=str(root/'original-navigation.png'));ref.evaluate('toggleNav()')
  for group in ['concept','feature','module']:
   ref.evaluate("openBrowser('"+group+"')");ref.screenshot(path=str(root/('original-browser-'+group+'.png')))
  ref.evaluate("closeWindow('browser');openEditor('monster')");ref.screenshot(path=str(root/'original-object.png'));ref.evaluate("closeWindow('object:monster');openSchema()");ref.screenshot(path=str(root/'original-schema.png'));ref.evaluate("closeWindow('schema');openReview('monster')");ref.screenshot(path=str(root/'original-review.png'));ref.evaluate("closeWindow('review:monster')")
  ref.locator('.home-side [data-helper="a"]').click();ref.wait_for_timeout(700);ref.screenshot(path=str(root/'original-helper.png'));ref.locator('.helper-window-pin').click();ref.screenshot(path=str(root/'original-helper-pinned.png'));ref.locator('.sd-close').click();ref.locator('.home-side [data-helper="a"]').click();ref.locator('.helper-window-settings').click();ref.screenshot(path=str(root/'original-helper-settings.png'));ref.locator('.modal [data-close]').click();ref.evaluate('openAugment()');ref.wait_for_timeout(700);ref.screenshot(path=str(root/'original-augment.png'));ref.locator('.augment-overlay [data-propose]').click();ref.locator('#augment-proposal').fill('Local retained direction');ref.screenshot(path=str(root/'original-augment-proposal.png'));ref.locator('.modal [data-close]').click();ref.locator('.augment-overlay [data-cancel]').click();ref.evaluate("project.yogis=[{id:'reference-capture',ey:[],lay:[],note:'',sealed:false}];openYogi('reference-capture')");ref.screenshot(path=str(root/'original-yogi.png'));ref.evaluate("project.yogis[0].ey=['monster'];openYogi('reference-capture')");ref.locator('.yogi-clipboard [data-confirm]').click();ref.screenshot(path=str(root/'original-yogi-package.png'))
  page.locator('.brand').click();page.locator('[data-enter]').filter(has_text='ButtonGame').click();page.locator('.app-settings-button').click();page.locator('#settings-sidebar-width').fill('180');page.locator('.modal [data-close]').click();page.locator('#nav').click();page.screenshot(path=str(root/'consumer-navigation.png'));page.locator('#nav').click();open_browser()
  for group in ['concept','feature','module']:
   page.locator('[data-tab="'+group+'"]').click();expect(page.locator('[data-tab="'+group+'"]')).to_have_class('selected');expect(page.locator('#nav')).to_be_enabled();page.screenshot(path=str(root/('consumer-browser-'+group+'.png')));ref.evaluate("openBrowser('"+group+"')");
   for region in ['.browser-tabs','.browser-tools','.browser-foot']:assert page.locator(region).evaluate(shape)==ref.locator(region).evaluate(shape),region
  page.locator('[data-tab="concept"]').click();expect(page.locator('#nav')).to_be_enabled(timeout=30000);page.locator('[data-id="Example.ButtonGame::Score"]').click();expect(page.locator('[data-schema-id]')).to_have_text('Example.ButtonGame::Score');page.locator('.window[data-key="browser"] .window-title').click(position={'x':50,'y':20});page.locator('.window[data-key="browser"] [data-close]').click();page.screenshot(path=str(root/'consumer-object.png'))
  field=page.locator('[data-schema-field="initial"]');field.fill('1');field.locator('..').get_by_role('button',name='Apply field',exact=True).click();expect(page.locator('[data-schema-field="initial"]')).to_have_value('1');page.locator('#semantic-review').click();expect(page.locator('#confirm')).to_be_enabled(timeout=60000);page.screenshot(path=str(root/'consumer-review.png'));page.locator('[data-reject]').click()
  field=page.locator('[data-schema-field="initial"]');field.fill('0');field.locator('..').get_by_role('button',name='Apply field',exact=True).click();expect(page.locator('[data-schema-field="initial"]')).to_have_value('0');page.locator('.window[data-key="schema"] [data-close]').click()
  page.locator('#add-helper').click();page.locator('[data-recruit="global"]').click();page.locator('#helper-list button').click();expect(page.locator('#helper-summary')).to_contain_text('main-helper',timeout=30000);expect(page.locator('.helper-local-settings')).to_contain_text('기억 대상: main-helper');page.locator('.modal [data-close]').click();page.locator('.window[data-key="schema"] [data-close]').click();page.locator('.home-side [data-helper]').filter(has_text='main-helper').click();expect(page.locator('.participant-expanded-card .messages')).to_contain_text('아직 받은 응답이 없습니다.');page.screenshot(path=str(root/'consumer-helper.png'));page.locator('.helper-window-pin').click();expect(page.locator('.helper-sd-panel')).to_be_visible();page.screenshot(path=str(root/'consumer-helper-pinned.png'));page.locator('.sd-close').click();page.locator('.home-side [data-helper]').filter(has_text='main-helper').click();page.locator('.helper-window-settings').click();page.screenshot(path=str(root/'consumer-helper-settings.png'));page.locator('.modal [data-close]').click()
  page.locator('#augment').click();expect(page.locator('.augment-overlay .augment-empty')).to_be_visible();assert page.locator('.augment-overlay .augment-card').count()==0;page.screenshot(path=str(root/'consumer-augment.png'));page.locator('.augment-overlay [data-propose]').click();page.locator('#augment-direction').fill('Local retained direction');page.screenshot(path=str(root/'consumer-augment-proposal.png'));page.locator('.modal [data-close]').click();page.locator('.augment-overlay [data-close]').click()
  open_browser();page.locator('[data-id="Example.ButtonGame::Score"]').click();page.locator('#yogi').click();expect(page.locator('#nav')).to_be_enabled();page.locator('[data-schema-field="initial"]').click();expect(page.locator('.yogi-clipboard')).to_be_visible();page.screenshot(path=str(root/'consumer-yogi.png'));page.locator('#yogi-seal').click();expect(page.locator('.yogi-package')).to_be_visible();page.screenshot(path=str(root/'consumer-yogi-package.png'));page.locator('.yogi-package').click();expect(page.locator('#yogi-seal')).to_be_enabled();page.locator('.yogi-clipboard [data-close]').click()
  open_browser();page.locator('[data-new]').click();page.locator('.context-menu button').filter(has_text='스키마 생성').click();page.locator('#new-declaration-name').fill('RestoredSchema');page.locator('#new-declaration').click();expect(page.locator('[data-schema-id]')).to_have_text('Example.ButtonGame::RestoredSchema');page.locator('.window[data-key="browser"] .window-title').click(position={'x':50,'y':20});page.locator('.window[data-key="browser"] [data-close]').click();page.locator('[data-add]').click();page.locator('[data-definition="name"]').fill('title');page.locator('[data-definition="type"]').last.fill('string');page.locator('[data-operation="definition-apply"]').last.click();expect(page.locator('#status')).to_contain_text('필드 정의가 공유 초안에 적용됨');page.screenshot(path=str(root/'consumer-schema.png'));assert not errors,errors
  print('PASS ordinary ProjectPack original Home/sidebar/create/settings/project/schema/chat retention; evidence '+str(root),flush=True);b.close()
except Exception:
 try:
  page.screenshot(path=str(root/'failure.png'),full_page=True)
  print('Home failure status:',page.locator('#status').inner_text(),flush=True)
  print('Home failure browser:',page.evaluate("()=>({selected:document.querySelector('[data-tab].selected')?.dataset.tab,ids:[...document.querySelectorAll('#objects [data-id]')].map(n=>n.dataset.id),navDisabled:document.querySelector('#nav')?.disabled})"),flush=True)
 except Exception:pass
 raise
finally:
 host.terminate()
 try:host.wait(timeout=15)
 except subprocess.TimeoutExpired:host.kill();host.wait()
 server.shutdown();log.close()
