"""Trace the ordinary existing integer property Save and explicit Run.

Run after editor_new_game_workflow.py on its disposable UI-created
Timing Puzzle evidence directory. No game source files are seeded or edited outside the editor.
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


from editor_new_game_workflow import browser as project_browser, confirm, stage_entry
from editor_logic_workflow import find_project_item
import subprocess,time
FEATURE='PlayTimingPuzzle'
ns=manifest.read_text().split()[1]
bindings=[('Confectory.Window::CreateSurfaces','Confectory.Window::CreateSurfacesBody'),('Confectory.RenderInput::Pump','Confectory.Window::PumpBody'),('Confectory.RenderInput::Draw','Confectory.Window::DrawBody'),('Confectory.Window::Close','Confectory.Window::CloseBody')]
import ctypes,io,re
from PIL import Image
from ctypes import c_void_p,c_int,c_uint,c_ulong


def activate(page):
 page.evaluate('async()=>await confectoryFlushPresentation()');tab=page.get_by_role('tab',name='Workspace',exact=True)
 if tab.get_attribute('aria-selected')!='true':tab.click();expect(tab).to_have_attribute('aria-selected','true')
 for key in ('targets','packs','blueprint','declaration','schema'):
  other=page.locator(f'.window[data-key={key}]')
  if other.is_visible():other.locator('[data-close]').first.click()

def rules(page):
 activate(page);find_project_item(page,ns+'::TimingRules','개념');window=page.locator('.window[data-key=schema]');expect(window.locator('.object-title-name')).to_have_text('TimingRules');return window

def add_field(page,window,name,value):
 window.locator('[data-schema-add]').click();row=window.locator('[data-definition-key]').last;row.locator('[data-property-name]').fill(name);row.locator('[data-property-type]').click();picker=page.get_by_role('dialog',name='속성 타입 선택',exact=True);picker.locator('[data-type="long"]').click();row.locator('[data-property-value]').fill(str(value))

def save_rules(page,window):
 window.locator('[data-element-action=confirm]').click()
 deadline=time.monotonic()+60
 while time.monotonic()<deadline:
  if page.locator('#review-creation').is_visible():
   page.locator('#review-creation').click();r=page.locator('.window[data-key=review]');expect(r).to_be_visible(timeout=120000)
   if r.locator('[data-review-advanced]').is_visible():r.locator('[data-review-advanced]').click()
   if r.locator('[data-advanced-reviewed]').count():r.locator('[data-advanced-reviewed]').check()
   r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);return
  if page.locator('#status').inner_text()=='저장했습니다.':return
  if '완료하지 못했습니다' in page.locator('#status').inner_text():raise AssertionError(window.locator('[data-element-error]').all_text_contents())
  page.wait_for_timeout(100)
 raise AssertionError(page.locator('#status').inner_text())

def connect(page):
 if 'dependency Confectory.RuntimeBase ' in manifest.read_text():return
 tab=page.get_by_role('tab',name='Pack Manager',exact=True);tab.click();expect(tab).to_have_attribute('aria-selected','true');expect(page.locator('#home-pack-connect')).to_be_enabled();page.locator('#home-pack-connect').click()
 d=page.get_by_role('dialog',name='설치된 팩 연결',exact=True);d.locator('[data-installed-pack-choice]').select_option('Confectory.RuntimeBase');d.locator('[data-installed-pack-review]').click()
 r=page.locator('.window[data-key=review]');expect(r).to_be_visible(timeout=120000)
 if r.locator('[data-review-advanced]').is_visible():r.locator('[data-review-advanced]').click()
 if r.locator('[data-advanced-reviewed]').count():r.locator('[data-advanced-reviewed]').check()
 r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000)

def prepare_fixture(page):
  window=rules(page);source=project/'elements/TimingRules.celem'
  if 'data PhaseMilliseconds' not in source.read_text():
   add_field(page,window,'PhaseMilliseconds',5000);save_rules(page,window)
  window.locator('[data-close]').first.click();connect(page);activate(page)
  find_project_item(page,ns+'::'+FEATURE,'기능');dec=page.locator('.window[data-key=declaration]');expect(dec.locator('.object-title-name')).to_have_text(FEATURE)
  if 'use object '+ns+'::TimingRules;' not in (project/'elements'/f'{FEATURE}.celem').read_text():
   dec.locator('[data-owned-object-use]').click();d=page.get_by_role('dialog',name='프로젝트 객체 참조',exact=True);d.locator('[data-owned-object-id]').fill(ns+'::TimingRules');d.locator('[data-owned-object-apply]').click();expect(d).to_be_hidden(timeout=30000);confirm(page,dec.locator('[data-feature-action=confirm]'));dec.locator('[data-close]').first.click();find_project_item(page,ns+'::'+FEATURE,'기능')
  dec.locator('[data-function-write-direct]').click();panel=page.locator('.window[data-key=blueprint]');doc=panel.locator('.function-document');expect(doc).to_be_visible()
  doc.locator('[data-document-code-import=body]').click();d=page.get_by_role('dialog',name='코드 기능 참조',exact=True);d.locator('[data-code-import-feature]').fill('Confectory.RuntimeBase::ReadDeclaredLong');d.locator('[data-code-import-apply]').click();expect(d).to_be_hidden(timeout=30000)
  read=doc.locator('[data-code-import-id="Confectory.RuntimeBase::ReadDeclaredLong"] [data-code-import-alias]').inner_text()
  import json
  marker=root/'data-save-result.txt';code=f'long phase={read}.Invoke("{ns}::TimingRules","PhaseMilliseconds");System.IO.File.WriteAllText({json.dumps(str(marker))},phase.ToString());return 0;'
  panel.locator('[data-document-code=body]').click();dialog=page.locator('.bp-script-dialog');src=dialog.locator('[data-code-source]');expect(src).to_be_visible();src.evaluate("""el=>{const p=[...el.closest('.bp-script-editor').querySelectorAll('[data-code-highlight]>span')];const i=p.findIndex(x=>x.dataset.codeRegion==='body');const n=p.slice(0,i).reduce((a,x)=>a+x.textContent.length,0);el.focus();el.setSelectionRange(n,n+p[i].textContent.length)}""")
  page.keyboard.insert_text(code);dialog.locator('[data-code-save]').click();expect(dialog).to_be_hidden();panel.locator('[data-bp-save]').click();expect(panel.locator('.bp-status')).to_have_text('저장됨',timeout=120000);confirm(page,panel.locator('[data-bp-complete]'));print('PASS fixture existing integer and ordinary declared-value caller confirmed',flush=True)

import json
trace=Path(sys.argv[4]);
def enable_trace():
 f.RUN=['strace','-D','-f','-ttt','-s','512','-e','trace=execve,openat,rename,renameat,renameat2','-o',str(trace),*f.RUN]
phases={}
def measured(name,action):
 start=time.time();result=action();end=time.time();phases[name]=[start,end];print(name,round((end-start)*1000,1),flush=True);return result
def run(page,expected):
 activate(page);page.evaluate('async()=>await confectoryFlushPresentation()');marker=root/'data-save-result.txt';marker.unlink(missing_ok=True);page.get_by_role('button',name='프로젝트 실행',exact=True).click();deadline=time.monotonic()+120
 while not marker.is_file() and time.monotonic()<deadline:page.wait_for_timeout(100)
 assert marker.is_file() and marker.read_text()==str(expected);expect(page.locator('.run-window:visible [data-run-frame]')).to_have_text('종료 코드 0',timeout=120000)
 key=page.locator('.run-window:visible').get_attribute('data-key');page.locator(f'[data-window-tab-close="{key}"]').click()
def measure_workflow(page):
  source=project/'elements/TimingRules.celem';import re
  impl=project/'elements'/f'{FEATURE}BlueprintBody.celem';graph=project/re.search(r'blueprint common "([^"]+)"',impl.read_text())[1];code=graph.parent/json.loads(graph.read_text())['nodes'][0]['implementation'];unchanged={p:p.read_bytes() for p in (impl,graph,code,project/'elements'/f'{FEATURE}.celem')}
  old=int(re.search(r'data PhaseMilliseconds = (\d+);',source.read_text())[1]);new=old+100
  run(page,old);w=measured('open',lambda:rules(page));value=w.get_by_label('PhaseMilliseconds 기본값',exact=True);expect(value).to_have_value(str(old))
  measured('edit',lambda:value.fill(str(new)))
  measured('save',lambda:save_rules(page,w));assert f'data PhaseMilliseconds = {new};' in source.read_text()
  w.locator('[data-close]').first.click();w=measured('reopen',lambda:rules(page));expect(w.get_by_label('PhaseMilliseconds 기본값',exact=True)).to_have_value(str(new));w.locator('[data-close]').first.click()
  assert all(p.read_bytes()==data for p,data in unchanged.items())
  measured('run',lambda:run(page,new));print('PASS normal reopen and explicit run uses saved value',flush=True)

def conflict_workflow(page):
  source=project/'elements/TimingRules.celem';original=source.read_bytes();import re
  old=int(re.search(rb'data PhaseMilliseconds = (\d+);',original)[1]);w=rules(page);value=w.get_by_label('PhaseMilliseconds 기본값',exact=True);expect(value).to_have_value(str(old));value.fill(str(old+100))
  changed=original.replace(str(old).encode(),str(old+200).encode());assert changed!=original
  try:
   source.write_bytes(changed) # competing edit only on disposable test project
   w.locator('[data-element-action=confirm]').click();expect(page.locator('#status')).to_contain_text('입력은 유지',timeout=60000);expect(value).to_have_value(str(old+100));assert source.read_bytes()==changed;print('PASS external integer conflict retained',flush=True)
  finally:source.write_bytes(original)

def schema_conflict_workflow(page):
  source=project/'elements/TimingRules.celem';original=source.read_bytes();import re
  old=int(re.search(rb'data PhaseMilliseconds = (\d+);',original)[1]);w=rules(page);value=w.get_by_label('PhaseMilliseconds 기본값',exact=True);value.fill(str(old+100))
  schema=project/'elements'/(re.search(rb'use schema [^:]+::([^;]+);',original)[1].decode()+'.celem');schema_original=schema.read_bytes();changed=schema_original.replace(b'general long',b'general int');assert changed!=schema_original
  try:
   schema.write_bytes(changed) # competing schema edit only on disposable fixture
   w.locator('[data-element-action=confirm]').click();expect(page.locator('#status')).to_contain_text('입력은 유지',timeout=60000);expect(value).to_have_value(str(old+100));assert source.read_bytes()==original and schema.read_bytes()==changed;print('PASS external schema change rejected and local integer input retained',flush=True)
  finally:schema.write_bytes(schema_original)

def summarize():
 import re
 rows=trace.read_text().splitlines();counts={}
 for name,(start,end) in phases.items():
  selected=[line for line in rows if (match:=re.match(r'\d+ (\d+\.\d+)',line)) and start<=float(match[1])<=end]
  compilers=sum('execve(' in line and 'csc.dll' in line for line in selected)
  project_dlls=[line for line in selected if 'openat(' in line and '.dll' in line and str(project/'.confectory') in line]
  counts[name]={'ms':round((end-start)*1000,1),'compiler_processes':compilers,'project_dll_opens':len(project_dlls),'project_dll_writes':sum(('O_WRONLY' in line or 'O_RDWR' in line or 'O_CREAT' in line) for line in project_dlls)}
 trace.with_suffix('.phases.json').write_text(json.dumps(phases,indent=2));print(json.dumps(counts,indent=2),flush=True)
 if '--baseline' not in sys.argv:
  for phase in ('open','edit','save','reopen'):assert counts[phase]['compiler_processes']==counts[phase]['project_dll_opens']==0,counts
  assert counts['run']['compiler_processes']>=1 and counts['run']['project_dll_opens']>0,counts

if not any(flag in sys.argv for flag in ('--setup-only','--guard-only','--schema-guard-only')):enable_trace()
with sync_playwright() as pw,pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']) as browser:
 if '--setup-only' in sys.argv:
  with f.web(browser,'data-save-setup') as page:prepare_fixture(page)
 elif '--guard-only' in sys.argv:
  with f.web(browser,'data-save-conflict') as page:conflict_workflow(page)
 elif '--schema-guard-only' in sys.argv:
  with f.web(browser,'data-save-schema-conflict') as page:schema_conflict_workflow(page)
 else:
  with f.web(browser,'data-save-trace') as page:measure_workflow(page)
  summarize()
