"""Continue only an owned fake CLI fixture: placement visibility and private drafts.
No login, model turn, user credentials or real account grant.
"""
import hashlib,json,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();fixture=pathlib.Path(sys.argv[2]).resolve();assert fixture.parent==pathlib.Path('/tmp') and fixture.name.startswith('confectory-cli-flow-')
source=fixture/'agent-common';assert (source/'agent-common-evidence.json').is_file();case=pathlib.Path(tempfile.mkdtemp(prefix='visibility-',dir=fixture));storage=case/'profile';shutil.copytree(source/'profile',storage);shutil.copy2(source/'control.json',case/'control.json');control=json.loads((case/'control.json').read_text());control.update(holdAccount=False,readEmail='');(case/'control.json').write_text(json.dumps(control));(fixture/'active.json').write_text(json.dumps({'case':str(case)}))
projectA=next((fixture/'projects/one').glob('*/project.cproj'));projectB=next((fixture/'projects/two').glob('*/project.cproj'));report=json.loads((fixture/'build-phase2.json').read_text());checks=[];errors=[];external=[];host=None;log=None;initial_global=None
env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(storage),CONFECTORY_ENTRY_STORAGE=str(storage),CONFECTORY_MCP_DIRECTORY=str(case/'instances'),CONFECTORY_WEB_PROJECT=str(projectA),CONFECTORY_DOTNET=env.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet'));env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH']
def stop():
 global host,log
 if host and host.poll() is None:os.killpg(host.pid,signal.SIGTERM)
 if host:host.wait(timeout=15)
 if log:log.close()
def start(n):
 global host,log,origin,token,url
 file=case/f'host-{n}.log';log=file.open('w');host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 for _ in range(700):
  found=[line.split(' ',1)[1] for line in file.read_text().splitlines() if line.startswith('CONFECTORY_WEB_UI ')]
  if found:url=found[-1];origin,token=url.split('/#');return
  assert host.poll() is None,file.read_text()[-1500:];time.sleep(.05)
 raise AssertionError('owned startup timeout')
def state():
 for _ in range(300):
  request=urllib.request.Request(origin+'/api/request',data=b'{"op":"mount"}',headers={'Content-Type':'application/json','X-Confectory-Session':token});v=json.load(urllib.request.urlopen(request,timeout=20))
  if v.get('error',{}).get('code')=='busy':page.wait_for_timeout(20);continue
  assert v['ok'],v
  try:return v['state']
  finally:
   req=urllib.request.Request(origin+'/api/request',data=json.dumps({'op':'dispose','view':v['view']}).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':token});urllib.request.urlopen(req,timeout=20).close()
 raise AssertionError('owned state busy')
def page_setup():
 p=browser.new_page(viewport={'width':1280,'height':892});p.on('pageerror',lambda e:errors.append(str(e)));p.route('**/*',lambda r:r.continue_() if r.request.url.startswith(origin) else (external.append(r.request.url),r.abort()));goto_editor(p,url);return p
def placement():
 page.locator('#add-helper').click();return page.get_by_role('dialog',name='프로젝트 도우미 배치',exact=True)
def apply(d):d.locator('button[type=submit]').click();expect(d).to_have_count(0)
def enter(path):
 key=hashlib.sha256(str(path.resolve()).encode()).hexdigest().upper()[:32];page.locator('[data-enter="'+key+'"]').click();expect(page.locator('.work-body')).to_be_visible(timeout=30000)
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(0);page=page_setup();expect(page.locator('.home-side [data-helper]')).to_have_count(0)
  page.locator('#add-agent').click();d=page.get_by_role('dialog',name='Agent 추가',exact=True);d.get_by_role('button',name='Codex',exact=True).click();accept=d.locator('[data-agent-use-accept]');expect(accept).to_be_enabled(timeout=40000);accept.click();expect(d.locator('[data-agent-use-revoke]')).to_be_enabled();d.locator('[data-close]').click();expect(d).to_have_count(0)
  helpers=state()['helpers'];assert len(helpers)==3;first,second,third=[h['id'] for h in helpers];d=placement();expect(d.locator('[data-project-helper]')).to_have_count(3);d.locator('[data-project-helper="'+first+'"]').click();d.locator('[data-project-helper="'+second+'"]').click();apply(d);expect(page.locator('.home-side [data-helper]')).to_have_count(2)
  page.locator('.home-side [data-helper="'+first+'"]').click();card=page.locator('.participant-expanded-card[data-helper-id="'+first+'"]');
  if 'helper-sd-companion' in (card.get_attribute('class') or ''):
   # v508 hides sd-info (including sd-close); original keyboard closes compose, then companion.
   character=card.locator('.sd-character');expect(character).to_be_visible();character.press('Escape')
   if card.count():character.press('Escape')
   expect(card).to_have_count(0);page.locator('.home-side [data-helper="'+first+'"]').click()
  card.locator('#global-chat textarea').fill('Owned restart draft 한글');card.locator('.helper-window-pin').click();page.evaluate('async()=>{await confectoryFlushPresentation();}');d=placement();d.locator('[data-remove-helper="'+first+'"]').click();apply(d);expect(card).to_be_hidden();expect(page.locator('.home-side [data-helper]')).to_have_count(1);page.evaluate('async()=>{await confectoryFlushPresentation();}');checks.append('placement candidates preserved; unassignment hides retained pinned draft');page.close();stop()
  start(1);page=page_setup();expect(page.locator('.home-side [data-helper]')).to_have_count(1);card=page.locator('.participant-expanded-card[data-helper-id="'+first+'"]');expect(card).to_have_count(1);expect(card).to_be_hidden();expect(card.locator('#global-chat textarea')).to_have_value('Owned restart draft 한글');d=placement();expect(d.locator('[data-project-helper="'+third+'"]')).to_be_visible();d.locator('[data-project-helper="'+first+'"]').click();apply(d);expect(card).to_be_visible();expect(card.locator('#global-chat textarea')).to_have_value('Owned restart draft 한글');checks.append('restart restores hidden unplaced panel and pending draft; reassignment reveals same draft')
  page.locator('.brand').click();expect(page.locator('.home-grid')).to_be_visible();expect(page.locator('.home-side [data-helper]')).to_have_count(3);enter(projectB);expect(page.locator('.home-side [data-helper]')).to_have_count(0);page.locator('.brand').click();expect(page.locator('.home-grid')).to_be_visible();enter(projectA);expect(page.locator('.home-side [data-helper]')).to_have_count(2);card=page.locator('.participant-expanded-card[data-helper-id="'+first+'"]');expect(card).to_be_visible();expect(card.locator('#global-chat textarea')).to_have_value('Owned restart draft 한글');page.screenshot(path=str(case/'restored-placed-draft.png'));checks.append('same-name project B has no A participants; returning A restores input; outside keeps all globals')
  requests=[json.loads(line) for line in (case/'requests.jsonl').read_text().splitlines()];assert not [row for row in requests if row['method'] in ('account/login/start','turn/start')];assert not errors and not external,(errors,external);page.close();stop();browser.close()
finally:stop()
record={'checks':checks,'pageErrors':errors,'external':external,'actualEngine':True,'fixtureAccountOnly':True,'loginOrInference':False,'nativeWindows':False,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
