import json,os,pathlib,subprocess,tempfile,time,shutil,http.server,threading
from playwright.sync_api import sync_playwright,expect
import sys
repo=pathlib.Path(sys.argv[1]).resolve();report=json.load(open(sys.argv[2]));reference=pathlib.Path(sys.argv[3]).resolve()
root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-original-layout-'));env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_ENTRY_STORAGE=str(root/'storage'),CONFECTORY_HOME_STORAGE=str(root/'storage'),CONFECTORY_WEB_PROJECT=str(repo/'examples/button-game/project.cpack'),PATH=str(pathlib.Path(env.get('CONFECTORY_DOTNET','dotnet')).parent)+os.pathsep+env['PATH'])
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
  page.locator('.brand').click();page.locator('.home-grid').wait_for();page.wait_for_timeout(3600);page.screenshot(path=str(root/'consumer-home.png'));assert page.locator('.home-side').count()==1;assert page.locator('.project-add #new-project').count()==1;assert page.locator('.project-card-stats').count()==1;assert page.locator('.project-add small').first.evaluate('(n)=>getComputedStyle(n).display')=='block';assert page.locator('#reconnect').count()==0
  page.locator('#new-project').click();page.locator('#project-name').fill('Original Flow');page.screenshot(path=str(root/'consumer-create.png'));expect(page.locator('.modal')).to_be_visible();expect(page.locator('#main-helper')).to_be_disabled();page.locator('[data-close]').click()
  page.locator('.app-settings-button').click();page.locator('#settings-sidebar-width').fill('270');assert page.locator('.home-grid').evaluate('(n)=>n.style.getPropertyValue("--participant-width")')=='270px';page.locator('[data-close]').click()
  page.locator('[data-enter]').click();page.locator('.work-body').wait_for();page.locator('#nav').click();expect(page.locator('[data-id="Example.ButtonGame::Score"]')).to_be_visible();page.locator('[data-id="Example.ButtonGame::Score"]').click();expect(page.locator('[data-schema-id]')).to_have_text('Example.ButtonGame::Score');page.screenshot(path=str(root/'consumer-schema.png'))
  page.locator('#chat-input').fill('Preserved project message');page.locator('#chat-input').blur();expect(page.locator('#status')).to_contain_text('전송 없음');page.locator('.brand').click();page.locator('[data-enter]').click();expect(page.locator('#chat-input')).to_have_value('Preserved project message');assert not errors,errors
  ref=b.new_page(viewport={'width':1440,'height':1000});ref.goto('http://127.0.0.1:'+str(server.server_port));ref.evaluate('showHome()');ref.evaluate('document.fonts.ready');ref.screenshot(path=str(root/'original-home.png'));
  shape='n=>[n.tagName,n.className,[...n.children].map(c=>[c.tagName,c.className,[...c.children].map(x=>[x.tagName,x.className])])]'
  page.locator('.brand').click();page.locator('.home-grid').wait_for();
  for region in ['.home-heading','.project-add','.project-card-main','.project-card-stats']:
   assert page.locator(region).first.evaluate(shape)==ref.locator(region).first.evaluate(shape),region
  page.locator('#add-agent').click();page.locator('#connection-choice').select_option('Confectory.Agent.Responses::Connection');page.locator('#connection-edit').click();expect(page.locator('[data-schema-id]')).to_have_text('Confectory.AISettings::Settings',timeout=60000);page.screenshot(path=str(root/'consumer-settings.png'));
  ref.evaluate("enterProject('demo')");ref.screenshot(path=str(root/'original-project.png'));ref.evaluate('showHome();createProject()');ref.screenshot(path=str(root/'original-create.png'))
  print('PASS ordinary ProjectPack original Home/sidebar/create/settings/project/schema/chat retention; evidence '+str(root),flush=True);b.close()
finally:
 host.terminate()
 try:host.wait(timeout=15)
 except subprocess.TimeoutExpired:host.kill();host.wait()
 server.shutdown();log.close()
