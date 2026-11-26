"""Trace real Chromium retirement of one previously UI-created pure data object.

Run with BUILD_REPORT OVERLAY UI_CREATED_EVIDENCE_ROOT [--always|--conflict] [--baseline].
Each run creates isolated source copies and fresh profiles; requires strace.
"""
import os,sys,shutil,tempfile,subprocess,signal,time,json,re
from pathlib import Path
from contextlib import contextmanager
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor,open_workspace_menu
expect.set_options(timeout=30000)
repo=Path(sys.argv[2]).resolve();source=Path(sys.argv[3]).resolve()/'projects'/'Timing Puzzle'
assert source.parent.parent.name.startswith('confectory-local-first-')
root=Path(tempfile.mkdtemp(prefix='confectory-data-delete-'));print('fixture',root,flush=True)
project=root/'project';peer=root/'peer'
for dest in (project,peer):shutil.copytree(source,dest,ignore=shutil.ignore_patterns('.confectory','.build'))
manifest=project/'project.cproj';ns=manifest.read_text().split()[1]
name='TimingRulesVariantCandidate';child=project/'elements'/f'{name}.celem'
if '--always' in sys.argv:
 manifest.write_text(manifest.read_text().replace('standalone true;','standalone true;\nalways '+ns+'::'+name+';'))
def snapshot(folder):return {str(p.relative_to(folder)):p.read_bytes() for p in folder.rglob('*') if p.is_file() and '.confectory' not in p.parts}
original=snapshot(project);peer_original=snapshot(peer)
run=json.loads(Path(sys.argv[1]).read_text())['run']
env=dict(os.environ,CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(root/'profile'),CONFECTORY_ENTRY_STORAGE=str(root/'profile'),CONFECTORY_MCP_DIRECTORY=str(root/'instances'),CONFECTORY_WEB_PROJECT=str(manifest),CONFECTORY_ELEMENT_AUTHORING_HOST=str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll'),CONFECTORY_PROJECT_EXECUTION_HOST=str(repo/'targets/project-execution-host/bin/Release/net10.0/Confectory.ProjectExecutionHost.dll'))
env['PATH']=str(Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH']
phases={};traces=[]
@contextmanager
def phase(name):
 start=time.time();yield;phases[name]=(start,time.time());print(name,round((phases[name][1]-start)*1000),flush=True);(root/'phases.json').write_text(json.dumps(phases))
@contextmanager
def web(browser,label):
 trace=root/(label+'.strace');traces.append(trace)
 with (root/(label+'.log')).open('w') as log:
  host=subprocess.Popen(['strace','-D','-f','-ttt','-s','512','-e','trace=execve,openat,rename,renameat,renameat2','-o',str(trace),*run],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  page=browser.new_page(viewport={'width':1800,'height':1200})
  try:
   deadline=time.monotonic()+45
   while time.monotonic()<deadline:
    urls=[l.split(' ',1)[1] for l in Path(log.name).read_text().splitlines() if l.startswith('CONFECTORY_WEB_UI ')]
    if urls:break
    assert host.poll() is None
    time.sleep(.05)
   assert urls
   origin=urls[-1].split('/#')[0];page.route('**/*',lambda r:r.continue_() if r.request.url.startswith(origin+'/') else r.abort())
   goto_editor(page,urls[-1])
   if page.locator('.home-grid').is_visible():
    page.locator('#home-projects [data-enter]').first.click()
   expect(page.locator('.work-body')).to_be_visible()
   page.wait_for_function('()=>typeof confectoryFlushPresentation==="function"');page.evaluate('()=>confectoryFlushPresentation()')
   tab=page.get_by_role('tab',name='Workspace',exact=True)
   if tab.get_attribute('aria-selected')!='true':tab.click();expect(tab).to_have_attribute('aria-selected','true')
   yield page
  except Exception:
   page.screenshot(path=str(root/(label+'-error.png')),full_page=True);print(page.locator('body').inner_text()[-5000:],flush=True);raise
  finally:
   page.close()
   if host.poll() is None:os.killpg(host.pid,signal.SIGTERM)
   host.wait(timeout=30)
def browser_panel(page):
 b=page.locator('.window[data-key^="browser:project:"]')
 if not b.is_visible():
  open_workspace_menu(page).get_by_role('button',name='프로젝트 브라우저',exact=True).click()
 expect(b).to_be_visible();b.get_by_role('button',name='개념',exact=True).click();return b
def filter(b,name):
 q=b.locator('[data-browser-control=object-query]');q.fill(name);b.locator('[data-browser-control=object-search]').click();return b.locator(f'[data-object="{ns}::{name}"]')
def delete(page,b,name):
 row=filter(b,name);expect(row).to_be_visible();row.click(button='right');page.get_by_role('button',name='삭제',exact=True).click()
 dlg=page.get_by_role('dialog',name='의미 객체 삭제',exact=True);expect(dlg).to_be_visible();return dlg
def review(page,b):
 b.locator('[data-browser-confirm]').click();r=page.locator('.window[data-key=review]');expect(r).to_be_visible(timeout=120000)
 if r.locator('[data-review-advanced]').is_visible():r.locator('[data-review-advanced]').click()
 if r.locator('[data-advanced-reviewed]').count():r.locator('[data-advanced-reviewed]').check()
 return r
def unchanged():assert snapshot(project)==original and snapshot(peer)==peer_original
with sync_playwright() as pw,pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']) as browser:
 with web(browser,'stage') as page:
  b=browser_panel(page)
  with phase('referenced'):
   d=delete(page,b,'TimingRules');expect(d).to_contain_text('참조하는 항목');assert not d.locator('#delete-object').count();d.get_by_role('button',name='닫기',exact=True).click();unchanged()
  with phase('cancel'):
   d=delete(page,b,name);expect(d.locator('#delete-object')).to_be_visible();d.get_by_role('button',name='닫기',exact=True).click();unchanged()
  with phase('stage'):
   d=delete(page,b,name);d.locator('#delete-object').click();expect(d).to_be_hidden(timeout=120000);expect(filter(b,name)).to_have_count(0,timeout=120000);unchanged()
  page.wait_for_function('()=>typeof confectoryFlushPresentation==="function"');page.evaluate('()=>confectoryFlushPresentation()')
 with web(browser,'confirm') as page:
  b=browser_panel(page);expect(filter(b,name)).to_have_count(0);unchanged()
  with phase('review_cancel'):
   r=review(page,b);r.locator('[data-reject]').click();expect(r).to_be_hidden();unchanged()
  with phase('review'):
   r=review(page,b)
  if '--conflict' in sys.argv:
   with phase('conflict'):
    changed=original['project.cproj']+b'\n// external manifest edit\n'
    manifest.write_bytes(changed)
    r.locator('#confirm').click()
    expect(page.locator('#status')).to_contain_text('최종 소스에 반영되지 않았습니다',timeout=120000)
    assert manifest.read_bytes()==changed and child.exists() and snapshot(peer)==peer_original
    print('PASS external manifest not overwritten',flush=True)
  elif '--always' in sys.argv:
   with phase('always_reference'):
    r.locator('#confirm').click()
    expect(page.locator('#status')).to_contain_text('최종 소스에 반영되지 않았습니다',timeout=120000)
    unchanged()
    print('PASS manifest always reference blocks final confirmation despite stage success',flush=True)
  else:
   with phase('confirm'):
    r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);assert f'element {name} object' not in manifest.read_text();assert child.read_bytes()==original[f'elements/{name}.celem']
    assert all(snapshot(project)[k]==v for k,v in original.items() if k!='project.cproj');assert snapshot(peer)==peer_original
  page.wait_for_function('()=>typeof confectoryFlushPresentation==="function"');page.evaluate('()=>confectoryFlushPresentation()')
 if not any(x in sys.argv for x in ('--always','--conflict')):
  with web(browser,'cold') as page:
   with phase('cold_reopen'):
    b=browser_panel(page);expect(filter(b,name)).to_have_count(0);assert child.exists();assert snapshot(peer)==peer_original
  env.update(CONFECTORY_WEB_PROJECT=str(peer/'project.cproj'),CONFECTORY_HOME_STORAGE=str(root/'peer-profile'),CONFECTORY_ENTRY_STORAGE=str(root/'peer-profile'))
  with web(browser,'peer') as page:
   b=browser_panel(page);expect(filter(b,name)).to_be_visible();assert snapshot(peer)==peer_original
   print('PASS same-ID peer still present in actual editor',flush=True)
rows=[line for trace in traces for line in trace.read_text().splitlines()]
for label,(start,end) in phases.items():
 selected=[line for line in rows if (m:=re.match(r'\d+ (\d+\.\d+)',line)) and start<=float(m[1])<=end]
 csc=[line for line in selected if 'execve(' in line and 'csc.dll' in line]
 dll=[line for line in selected if 'openat(' in line and '.dll' in line and str(project/'.confectory') in line]
 print(label,'csc',len(csc),'link',sum('/outputs/linux/' in l for l in csc),'dll',len(dll),'writes',sum('O_WRONLY' in l or 'O_RDWR' in l or 'O_CREAT' in l for l in dll),flush=True)
 if '--baseline' not in sys.argv:assert not csc and not dll,(label,len(csc),len(dll))
print('PASS actual retirement scenario',flush=True)
