"""Trace normal UI creation of one inherited data object using an existing schema.

Run after project_runtime_configuration.py on its disposable UI-created
Timing Puzzle evidence directory. Only the disposable UI-created project is used. Pass a unique child name as argument 4.
Optional: --untraced --timeline --expect-combined|--expect-legacy-fallback --conflict|--schema-conflict|--permission|--lost-create-response|--proposal-failure. --run and --peer are optional native/runtime and isolation regressions.
For --proposal-failure, build tests/packs/fixtures/variation_proposal_failure/failure-proxy.csproj
and set CONFECTORY_TEST_AUTHORING_HOST to its DLL, CONFECTORY_REAL_AUTHOR to the real tool,
CONFECTORY_VARIATION_FAILURE_FIXTURE=1; use the disposable child name TimingRulesBatchCase.
"""
import sys,os,json,shutil,tempfile,subprocess
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
f.ENV.update(CONFECTORY_EDITOR_REPO=str(repo), CONFECTORY_ELEMENT_AUTHORING_HOST=os.environ.get('CONFECTORY_TEST_AUTHORING_HOST',str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')), CONFECTORY_PROJECT_EXECUTION_HOST=str(repo/'targets/project-execution-host/bin/Release/net10.0/Confectory.ProjectExecutionHost.dll'))
expect.set_options(timeout=30000)


from editor_navigation import open_workspace_menu
import time,re
ns=manifest.read_text().split()[1]

def activate(page):
 page.evaluate('async()=>await confectoryFlushPresentation()');tab=page.get_by_role('tab',name='Workspace',exact=True)
 if tab.get_attribute('aria-selected')!='true':tab.click();expect(tab).to_have_attribute('aria-selected','true')
 for key in ('targets','packs','blueprint','declaration','schema'):
  other=page.locator(f'.window[data-key={key}]')
  if other.is_visible():other.locator('[data-close]').first.click()

def find_creation_item(page,item,tab):
 browser=page.locator('.window[data-key^="browser:project:"]:visible').first
 if not browser.is_visible():
  open_workspace_menu(page).get_by_role('button',name='프로젝트 브라우저',exact=True).click()
 expect(browser).to_be_visible()
 browser.get_by_role('button',name=tab,exact=True).click()
 browser.locator('[data-browser-control=object-query]').fill(item.split('::')[-1])
 browser.locator('[data-browser-control=object-search]').click()
 browser.locator(f'[data-object="{item}"]').press('Enter')
 browser.locator('[data-close]').first.click()

def rules(page):
 activate(page);find_creation_item(page,ns+'::TimingRules','개념');window=page.locator('.window[data-key=schema]');expect(window.locator('.object-title-name')).to_have_text('TimingRules');return window

from editor_logic_workflow import review
from contextlib import contextmanager
name=sys.argv[4]
assert re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*',name)
trace=root/(name+'.strace')
if '--untraced' not in sys.argv:f.RUN=['strace','-D','-f','-ttt','-s','512','-e','trace=execve,openat,rename,renameat,renameat2','-o',str(trace),*f.RUN]
if '--timeline' in sys.argv:f.ENV.update(CONFECTORY_UI_TRACE='1',CONFECTORY_PERFORMANCE='1')
phases={}
@contextmanager
def phase(name):
 start=time.time()
 yield
 phases[name]=(start,time.time())
 print(name,round((phases[name][1]-start)*1000),flush=True)
child=project/'elements'/f'{name}.celem'
if '--peer' in sys.argv:
 peer_root=Path(tempfile.mkdtemp(prefix='confectory-local-first-'))
 peer_project=peer_root/'projects'/'Timing Puzzle'
 shutil.copytree(project,peer_project,ignore=shutil.ignore_patterns('.confectory','.build'))
 (peer_root/'profile').mkdir()
 (peer_root/'profile/projects.json').write_text((root/'profile/projects.json').read_text().replace(str(root),str(peer_root)))
 def peer_snapshot():return {str(p.relative_to(peer_project)):p.read_bytes() for p in peer_project.rglob('*') if p.is_file() and '.confectory' not in p.parts and '.build' not in p.parts}
 peer_before=peer_snapshot()
def run_at_offset(page,label,expected):
 import ctypes,io
 from PIL import Image
 from ctypes import c_void_p,c_int,c_uint,c_ulong
 activate(page);page.get_by_role('button',name='프로젝트 실행',exact=True).click();deadline=time.monotonic()+120
 while time.monotonic()<deadline:
  tree=subprocess.check_output(['xwininfo','-root','-tree'],text=True);found=re.search(r'(0x[0-9a-f]+) "Timing Puzzle Configured"',tree)
  if found:break
  if page.locator('.run-window:visible [data-run-frame]').count() and '종료 코드' in page.locator('.run-window:visible [data-run-frame]').inner_text():raise AssertionError(page.locator('.run-window:visible').inner_text())
  page.wait_for_timeout(80)
 else:raise AssertionError('Configured window not observed')
 wid=found[1];x=ctypes.CDLL('libX11.so.6');t=ctypes.CDLL('libXtst.so.6');x.XOpenDisplay.restype=c_void_p;x.XFlush.argtypes=[c_void_p];x.XCloseDisplay.argtypes=[c_void_p];t.XTestFakeMotionEvent.argtypes=[c_void_p,c_int,c_int,c_int,c_ulong];t.XTestFakeButtonEvent.argtypes=[c_void_p,c_uint,c_int,c_ulong]
 d=x.XOpenDisplay(None);assert d;geometry=subprocess.check_output(['xwininfo','-id',wid],text=True);sx=int(re.search(r'Absolute upper-left X:\s*(-?\d+)',geometry)[1]);sy=int(re.search(r'Absolute upper-left Y:\s*(-?\d+)',geometry)[1])
 def capture():return Image.open(io.BytesIO(subprocess.check_output(['import','-window',wid,'png:-']))).convert('RGB')
 try:
  deadline=time.monotonic()+3
  while time.monotonic()<deadline:
   image=capture()
   if image.getpixel((45,45))==(0,204,0):break
  else:raise AssertionError('Initial green not observed')
  start=time.monotonic();time.sleep(1.6);image=capture();assert image.getpixel((45,45))==expected,(label,image.getpixel((45,45)))
  t.XTestFakeMotionEvent(d,0,sx+80,sy+70,0);t.XTestFakeButtonEvent(d,1,1,0);t.XTestFakeButtonEvent(d,1,0,0);x.XFlush(d);time.sleep(.12);image=capture();assert image.getpixel((45,165))==expected,(label,image.getpixel((45,165)));image.save(root/f'config-{label}.png');print('PASS fixed click offset',label,round(time.monotonic()-start,2),expected,flush=True)
 finally:x.XCloseDisplay(d)
 expect(page.locator('.run-window:visible [data-run-frame]')).to_have_text('종료 코드 0',timeout=120000)


def exercise(page):
 with phase('open'):
  w=rules(page)
 original=manifest.read_bytes()
 parent=(project/'elements/TimingRules.celem').read_bytes()
 print('variation controls',w.locator('[data-create-variation]').count(),flush=True)
 with phase('begin_create'):
  if w.locator('[data-create-variation]').count():w.locator('[data-create-variation]').click()
  else:
   w.locator('.object-variations [data-new]').click();page.get_by_role('button',name='개념 생성',exact=True).click()
  entry=w.locator('.browser-create-draft input')
 with phase('duplicate'):
  entry.fill('TimingRules');entry.press('Enter')
  expect(entry).to_have_attribute('aria-invalid','true')
  assert not child.exists() and manifest.read_bytes()==original
 if '--proposal-failure' in sys.argv:
  entry.fill(name);entry.press('Enter');expect(entry).to_have_attribute('aria-invalid','true',timeout=120000)
  assert not child.exists() and manifest.read_bytes()==original
  entry.press('Escape');w.locator('[data-close]').first.click()
  from editor_navigation import open_workspace_menu
  open_workspace_menu(page).get_by_role('button',name='프로젝트 브라우저',exact=True).click()
  b=page.locator('.window[data-key^="browser:project:"]');b.get_by_role('button',name='개념',exact=True).click()
  b.locator('[data-browser-control=object-query]').fill(name);b.locator('[data-browser-control=object-search]').click()
  expect(b.locator(f'[data-object="{ns}::{name}"]')).to_have_count(0)
  assert not child.exists() and manifest.read_bytes()==original
  print('PASS failed combined proposal left neither staged child nor source registration',flush=True)
  return
 if '--lost-create-response' in sys.argv:
  admitted=[];masked=set()
  def lose_response(route):
   try:request=route.request.post_data_json
   except Exception:request=None
   if isinstance(request,dict) and request.get('endpoint')=='createVariation':admitted.append(request['requestId'])
   response=route.fetch();payload=response.json()
   for row in payload.get('results',[]):
    if row.get('requestId') in admitted:
     assert row.get('ok'),row
     masked.add(row['requestId']);rid=row['requestId'];row.clear();row.update(requestId=rid,ok=False,error={'code':'transport_lost'})
   route.fulfill(response=response,json=payload)
  page.route('**/api/request',lose_response)
  try:
   entry.fill(name);entry.press('Enter')
   expect(entry).to_have_attribute('aria-invalid','true',timeout=120000)
   assert len(admitted)==len(masked)==1,(admitted,masked)
   assert not child.exists() and manifest.read_bytes()==original
   entry.press('Escape')
  finally:page.unroute('**/api/request',lose_response)
  print('PASS lost creation response left source untouched; inspect complete draft in Review',flush=True)
 else:
  with phase('create'):
   entry.fill(name)
   entry.evaluate('''b=>{window.__variationReady=null;b.addEventListener('keydown',e=>{if(e.key!=='Enter')return;const start=performance.now();const check=()=>{if(!b.isConnected||!b.getClientRects().length){window.__variationReady=performance.now()-start;return;}if(performance.now()-start<120000)requestAnimationFrame(check);};requestAnimationFrame(check);},{capture:true,once:true});}''')
   entry.press('Enter');expect(entry).to_be_hidden(timeout=120000)
   page.wait_for_function('()=>window.__variationReady!==null');print('draft DOM ms',round(page.evaluate('()=>window.__variationReady')),flush=True)
   assert not child.exists() and manifest.read_bytes()==original
 with phase('open_child'):
  w.locator('[data-close]').first.click()
  find_creation_item(page,ns+'::'+name,'개념')
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
 if any(flag in sys.argv for flag in ('--conflict','--schema-conflict','--permission')):
  with phase('conflict'):
   permission='--permission' in sys.argv
   target=project/'elements'/('TimingRules_Properties_46768765afa8.celem') if '--schema-conflict' in sys.argv else manifest
   old_bytes=target.read_bytes();mode=target.stat().st_mode&0o777
   changed=old_bytes if permission else old_bytes.replace(b'general long',b'general bool') if target!=manifest else original+b'\n// competing manifest edit\n'
   assert permission or changed!=old_bytes
   try:
    if permission:target.chmod(0o400)
    else:target.write_bytes(changed)
    r.locator('#confirm').click()
    expect(page.locator('#status')).to_contain_text('최종 소스에 반영되지 않았습니다',timeout=120000)
    assert not child.exists() and target.read_bytes()==changed
    if target!=manifest:assert manifest.read_bytes()==original
    print('PASS external change or permission refused without partial registration',flush=True)
   finally:
    if permission:target.chmod(mode)
    else:target.write_bytes(old_bytes)
  return
 with phase('confirm'):
  r.locator('#confirm').evaluate('''b=>{window.__creationClose=null;b.addEventListener('click',()=>{const start=performance.now(),review=b.closest('.window[data-key=review]');const check=()=>{if(!review?.isConnected||!review.getClientRects().length){window.__creationClose=performance.now()-start;return;}if(performance.now()-start<120000)requestAnimationFrame(check);};requestAnimationFrame(check);},{capture:true,once:true});}''')
  started=time.monotonic();r.locator('#confirm').click();deadline=time.monotonic()+120
  while (not child.exists() or f'element {name} object' not in manifest.read_text()) and time.monotonic()<deadline:page.wait_for_timeout(25)
  print('durable creation ms',round((time.monotonic()-started)*1000),flush=True)
  expect(r).to_be_hidden(timeout=120000);page.wait_for_function('()=>window.__creationClose!==null');print('confirm DOM ms',round(page.evaluate('()=>window.__creationClose')),flush=True)
  assert child.exists() and f'element {name} object' in manifest.read_text(),page.locator('#status').inner_text()
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
 rows=trace.read_text().splitlines() if '--untraced' not in sys.argv else []
 if not any(flag in sys.argv for flag in ('--conflict','--schema-conflict','--permission','--proposal-failure')):
  with f.web(browser,'object-add-cold') as page:
   with phase('cold_reopen'):
    activate(page);find_creation_item(page,ns+'::'+name,'개념')
    w=page.locator('.window[data-key=schema]')
    expect(w.locator('.object-title-name')).to_have_text(name)
    expect(w.get_by_label('PhaseMilliseconds 기본값',exact=True)).to_have_value('5000')
   if '--run' in sys.argv:
    w.locator('[data-close]').first.click()
    run_at_offset(page,'after-creation',(204,0,0))
    print('PASS actual Run after inherited object creation',flush=True)
  print('PASS cold reopen',flush=True)
  if '--untraced' not in sys.argv:rows+=trace.read_text().splitlines()
 if '--peer' in sys.argv:
  assert peer_snapshot()==peer_before
  f.ROOT,f.PROFILE,f.PROJECTS=peer_root,peer_root/'profile',peer_root/'projects'
  f.ENV={key:str(value).replace(str(root),str(peer_root)) for key,value in f.ENV.items()}
  with f.web(browser,'peer') as page:
   from editor_navigation import open_workspace_menu
   activate(page);open_workspace_menu(page).get_by_role('button',name='프로젝트 브라우저',exact=True).click()
   b=page.locator('.window[data-key^="browser:project:"]');b.get_by_role('button',name='개념',exact=True).click()
   b.locator('[data-browser-control=object-query]').fill(name);b.locator('[data-browser-control=object-search]').click()
   expect(b.locator(f'[data-object="{ns}::{name}"]')).to_have_count(0)
   assert peer_snapshot()==peer_before
  print('PASS same-namespace peer has no staged or confirmed new object',flush=True)
for name,(start,end) in (phases.items() if '--untraced' not in sys.argv else []):
 selected=[line for line in rows if (match:=re.match(r'\d+ (\d+\.\d+)',line)) and start<=float(match[1])<=end]
 csc=[line for line in selected if 'execve(' in line and 'csc.dll' in line]
 dlls=[line for line in selected if 'openat(' in line and '.dll' in line and str(project/'.confectory') in line]
 print(name,'compiler',len(csc),'links',sum('/outputs/linux/' in l for l in csc),'DLL opens',len(dlls),'writes',sum('O_WRONLY' in l or 'O_RDWR' in l or 'O_CREAT' in l for l in dlls),flush=True)
 if '--baseline' not in sys.argv and name!='conflict':assert not csc and not dlls,(name,len(csc),len(dlls))

if '--timeline' in sys.argv:
 calls=[];pending=[]
 for line in (root/'object-add.log').read_text().splitlines():
  if not line.startswith('CONFECTORY_UI_TRACE '):continue
  row=json.loads(line.split(' ',1)[1])
  if row['stage']=='authoring-process':pending.append((row['operation'],row['elapsedMs']))
  if row['stage']=='consumer':
   if row.get('endpoint')=='createVariation':calls.append((row['elapsedMs'],pending))
   pending=[]
 print('create authoring calls',json.dumps(calls),flush=True)
 if '--expect-combined' in sys.argv:
  names=[name for name,_ in calls[-1][1]]
  assert names==['prepareExistingSchemaObjectVariation'],names
  print('PASS single combined authoring proposal',flush=True)
 if '--expect-legacy-fallback' in sys.argv:
  names=[name for name,_ in calls[-1][1]]
  assert names==['prepareExistingSchemaObjectVariation','inspect','create','editDeclaration','register'],names
  print('PASS old authoring tool fallback',flush=True)
