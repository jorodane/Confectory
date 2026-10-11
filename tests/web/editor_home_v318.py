import json,os,pathlib,subprocess,tempfile,time,shutil,sys,http.server,threading,zipfile,signal
from playwright.sync_api import sync_playwright,expect
repo=pathlib.Path(sys.argv[1]).resolve();report=json.load(open(sys.argv[2]));root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-v318-home-'))
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
reference=root/'reference';zipfile.ZipFile(repo/'reference/site-ui/Confectory-Editor-Prototype-v318.zip').extractall(reference)
class Static(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(reference/'confectory-site'),**k)
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Static);threading.Thread(target=server.serve_forever,daemon=True).start()
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);errors=[]
 ref=browser.new_page(viewport={'width':1440,'height':1000});ref.goto('http://127.0.0.1:'+str(server.server_port));ref.evaluate('showHome()');ref.screenshot(path=str(root/'original-v318-home.png'))
 shape='n=>[n.tagName,n.className,[...n.children].map(c=>[c.tagName,c.className])]'

 try:
  for n in range(2):
   host,stream,url=start(n)
   try:
    page=browser.new_page(viewport={'width':1440,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)));page.goto(url);page.locator('.work-body').wait_for(timeout=30000);page.locator('.brand').click();page.locator('#home-projects').wait_for();expect(page.locator('[data-project]')).to_have_count(1);favorite=page.locator('[data-favorite]')
    if n==0:
     expect(favorite).to_have_attribute('aria-pressed','false');favorite.click();expect(page.locator('[data-favorite]')).to_have_attribute('aria-pressed','true');page.locator('#home-project-search').fill('no-such-project');expect(page.locator('[data-project]')).to_have_count(0);expect(page.locator('.project-empty')).to_have_text('검색 결과가 없습니다.');page.locator('#home-project-search').fill('');expect(page.locator('[data-project]')).to_have_count(1)
    else:expect(favorite).to_have_attribute('aria-pressed','true')
    for selector in ['.home-tabs','.home-project-controls','.home-project-actions','.project-card-main','.project-card-stats']:
     assert page.locator(selector).first.evaluate(shape)==ref.locator(selector).first.evaluate(shape),selector
    page.screenshot(path=str(root/f'home-{n}.png'));page.locator('[data-manage]').click();page.get_by_role('button',name='목록에서 삭제',exact=True).click();page.locator('.modal [data-close]').click();expect(page.locator('[data-project]')).to_have_count(1)
    if n==1:
     page.locator('[data-manage]').click();page.get_by_role('button',name='목록에서 삭제',exact=True).click();page.locator('#remove-project').click();expect(page.locator('[data-project]')).to_have_count(0);assert json.loads((root/'storage/projects.json').read_text())==[]
    else:
     page.locator('[data-enter]').click();page.locator('.work-body').wait_for(timeout=60000);expect(page.locator('#title')).to_contain_text('ButtonGame')
    assert not errors,errors
    page.close()
   except Exception as error:
    page.screenshot(path=str(root/f'failure-{n}.png'));(root/f'failure-{n}.html').write_text(page.content());raise AssertionError(str(error)+'\nPage errors: '+str(errors)+'\nStatus: '+str(page.locator('#toast').text_content())) from error
   finally:stop(host,stream)
 finally:
  browser.close();server.shutdown();server.server_close()
for name,data in before.items():assert (project/name).read_bytes()==data,name
print('PASS ordinary ProjectPack v318 Home search favorite process restart removal cancel and file preservation',root)
