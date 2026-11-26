"""Trace normal UI creation of one inherited data object using an existing schema.

Run after project_runtime_configuration.py on its disposable UI-created
Timing Puzzle evidence directory. Only the disposable UI-created project is used. Pass a unique child name as argument 4.
"""
import sys
from pathlib import Path
from playwright.sync_api import expect, sync_playwright
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'gui'))
import editor_local_first_workflow as f

repo = Path(sys.argv[2]).resolve()
root = Path(sys.argv[3]).resolve()
project = root / 'projects' / 'Timing Puzzle'
assert root.name.startswith('confectory-local-first-') and project.is_dir()
manifest = project / 'project.cproj'
old = f.ROOT
f.ROOT, f.PROFILE, f.PROJECTS, f.TITLE, f.repo = root, root/'profile', root/'projects', 'Timing Puzzle', repo
f.ENV = {key: str(value).replace(str(old), str(root)) for key, value in f.ENV.items()}
f.ENV.update(CONFECTORY_EDITOR_REPO=str(repo), CONFECTORY_ELEMENT_AUTHORING_HOST=str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll'), CONFECTORY_PROJECT_EXECUTION_HOST=str(repo/'targets/project-execution-host/bin/Release/net10.0/Confectory.ProjectExecutionHost.dll'))
expect.set_options(timeout=30000)


from editor_logic_workflow import find_project_item
import time,re
ns=manifest.read_text().split()[1]

def activate(page):
 page.evaluate('async()=>await confectoryFlushPresentation()');tab=page.get_by_role('tab',name='Workspace',exact=True)
 if tab.get_attribute('aria-selected')!='true':tab.click();expect(tab).to_have_attribute('aria-selected','true')
 for key in ('targets','packs','blueprint','declaration','schema'):
  other=page.locator(f'.window[data-key={key}]')
  if other.is_visible():other.locator('[data-close]').first.click()

def rules(page):
 activate(page);find_project_item(page,ns+'::TimingRules','개념');window=page.locator('.window[data-key=schema]');expect(window.locator('.object-title-name')).to_have_text('TimingRules');return window

from editor_logic_workflow import review
from contextlib import contextmanager
name=sys.argv[4]
assert re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*',name)
trace=root/(name+'.strace')
f.RUN=['strace','-D','-f','-ttt','-s','512','-e','trace=execve,openat,rename,renameat,renameat2','-o',str(trace),*f.RUN]
phases={}
@contextmanager
def phase(name):
 start=time.time()
 yield
 phases[name]=(start,time.time())
 print(name,round((phases[name][1]-start)*1000),flush=True)
child=project/'elements'/f'{name}.celem'
def exercise(page):
 with phase('open'):
  w=rules(page)
 original=manifest.read_bytes()
 parent=(project/'elements/TimingRules.celem').read_bytes()
 print('variation controls',w.locator('[data-create-variation]').count(),flush=True)
 with phase('create'):
  if w.locator('[data-create-variation]').count():w.locator('[data-create-variation]').click()
  else:
   w.locator('.object-variations [data-new]').click();page.get_by_role('button',name='개념 생성',exact=True).click()
  entry=w.locator('.browser-create-draft input')
  entry.fill('TimingRules');entry.press('Enter')
  expect(entry).to_have_attribute('aria-invalid','true')
  entry.fill(name);entry.press('Enter')
  expect(entry).to_be_hidden(timeout=120000)
  assert not child.exists() and manifest.read_bytes()==original
 with phase('open_child'):
  w.locator('[data-close]').first.click()
  find_project_item(page,ns+'::'+name,'개념')
  w=page.locator('.window[data-key=schema]')
  expect(w.locator('.object-title-name')).to_have_text(name)
  expect(w.get_by_label('PhaseMilliseconds 기본값',exact=True)).to_have_value('5000')
 with phase('review_cancel'):
  r=review(page,w.locator('[data-element-action=confirm]'))
  expect(r.locator('[data-review-unit]')).to_have_count(2)
  r.locator('[data-reject]').click();expect(r).to_be_hidden()
  assert not child.exists() and manifest.read_bytes()==original
 with phase('review'):
  r=review(page,w.locator('[data-element-action=confirm]'))
 if '--conflict' in sys.argv:
  with phase('conflict'):
   changed=original+b'\n// competing manifest edit\n'
   try:
    manifest.write_bytes(changed)
    r.locator('#confirm').click()
    expect(page.locator('#status')).to_contain_text('최종 소스에 반영되지 않았습니다',timeout=120000)
    assert not child.exists() and manifest.read_bytes()==changed
    print('PASS external manifest edit not overwritten',flush=True)
   finally:manifest.write_bytes(original)
  return
 with phase('confirm'):
  r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000)
  assert child.exists(),page.locator('#status').inner_text()
  assert 'extends '+ns+'::TimingRules' in child.read_text()
  assert (project/'elements/TimingRules.celem').read_bytes()==parent
 print('PASS duplicate, cancel, confirm and parent preserved',flush=True)
with sync_playwright() as pw,pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']) as browser:
 with f.web(browser,'object-add') as page:
  try:exercise(page)
  except Exception:
   page.screenshot(path=str(root/'object-add-error.png'),full_page=True)
   print(page.locator('body').inner_text()[-5000:],flush=True)
   raise
 rows=trace.read_text().splitlines()
 if '--conflict' not in sys.argv:
  with f.web(browser,'object-add-cold') as page:
   with phase('cold_reopen'):
    activate(page);find_project_item(page,ns+'::'+name,'개념')
    w=page.locator('.window[data-key=schema]')
    expect(w.locator('.object-title-name')).to_have_text(name)
    expect(w.get_by_label('PhaseMilliseconds 기본값',exact=True)).to_have_value('5000')
  print('PASS cold reopen',flush=True)
if '--conflict' not in sys.argv:rows+=trace.read_text().splitlines()
for name,(start,end) in phases.items():
 selected=[line for line in rows if (match:=re.match(r'\d+ (\d+\.\d+)',line)) and start<=float(match[1])<=end]
 csc=[line for line in selected if 'execve(' in line and 'csc.dll' in line]
 dlls=[line for line in selected if 'openat(' in line and '.dll' in line and str(project/'.confectory') in line]
 print(name,'compiler',len(csc),'links',sum('/outputs/linux/' in l for l in csc),'DLL opens',len(dlls),'writes',sum('O_WRONLY' in l or 'O_RDWR' in l or 'O_CREAT' in l for l in dlls),flush=True)
 if '--baseline' not in sys.argv and name!='conflict':assert not csc and not dlls,(name,len(csc),len(dlls))
