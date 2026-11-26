"""Trace real Chromium retirement of one previously UI-created pure data object.

Run with BUILD_REPORT OVERLAY UI_CREATED_EVIDENCE_ROOT [--always|--conflict|--late-reference|--permission] [--baseline] [--untraced] [--timeline] [--expect-retirement-only-proof] [--recover] [--run].
Each run creates isolated source copies and fresh profiles; requires strace unless --untraced.
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
if '--timeline' in sys.argv:
 (root/'data').mkdir();env.update(CONFECTORY_UI_TRACE='1',CONFECTORY_PERFORMANCE='1',XDG_DATA_HOME=str(root/'data'))
phases={};traces=[]
@contextmanager
def phase(name):
 start=time.time();yield;phases[name]=(start,time.time());print(name,round((phases[name][1]-start)*1000),flush=True);(root/'phases.json').write_text(json.dumps(phases))
@contextmanager
def web(browser,label):
 trace=root/(label+'.strace')
 if '--untraced' not in sys.argv:traces.append(trace)
 with (root/(label+'.log')).open('w') as log:
  host=subprocess.Popen(run if '--untraced' in sys.argv else ['strace','-D','-f','-ttt','-s','512','-e','trace=execve,openat,rename,renameat,renameat2','-o',str(trace),*run],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
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
 start=time.monotonic();b.locator('[data-browser-confirm]').click();r=page.locator('.window[data-key=review]');expect(r).to_be_visible(timeout=120000);print('review visible ms',round((time.monotonic()-start)*1000),flush=True)
 if r.locator('[data-review-advanced]').is_visible():r.locator('[data-review-advanced]').click()
 if r.locator('[data-advanced-reviewed]').count():r.locator('[data-advanced-reviewed]').check()
 expect(r.locator('#confirm')).to_be_enabled(timeout=120000);print('review ready ms',round((time.monotonic()-start)*1000),flush=True)
 return r
def unchanged():assert snapshot(project)==original and snapshot(peer)==peer_original
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


def activate(page):
 page.wait_for_function('()=>typeof confectoryFlushPresentation==="function"')
 page.evaluate('()=>confectoryFlushPresentation()')
 tab=page.get_by_role('tab',name='Workspace',exact=True)
 if tab.get_attribute('aria-selected')!='true':tab.click();expect(tab).to_have_attribute('aria-selected','true')
with sync_playwright() as pw,pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']) as browser:
 with web(browser,'stage') as page:
  b=browser_panel(page)
  with phase('referenced'):
   d=delete(page,b,'TimingRules');expect(d).to_contain_text('참조하는 항목');assert not d.locator('#delete-object').count();d.get_by_role('button',name='닫기',exact=True).click();unchanged()
  with phase('cancel'):
   d=delete(page,b,name);expect(d.locator('#delete-object')).to_be_visible();d.get_by_role('button',name='닫기',exact=True).click();unchanged()
  with phase('plan'):
   d=delete(page,b,name)
  with phase('stage'):
   d.locator('#delete-object').click();expect(d).to_be_hidden(timeout=120000);expect(filter(b,name)).to_have_count(0,timeout=120000);unchanged()
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
  elif '--late-reference' in sys.argv or '--permission' in sys.argv:
   permission='--permission' in sys.argv
   target=manifest if permission else project/'elements/TimingRulesVariantTrace.celem'
   prior=target.read_bytes();mode=target.stat().st_mode&0o777
   changed=prior if permission else prior.replace(b'::TimingRules {',('::'+name+' {').encode())
   assert permission or changed!=prior
   try:
    if permission:target.chmod(0o400)
    else:target.write_bytes(changed)
    with phase('late_guard'):
     r.locator('#confirm').click()
     expect(page.locator('#status')).to_contain_text('최종 소스에 반영되지 않았습니다',timeout=120000)
     assert target.read_bytes()==changed and f'element {name} object' in manifest.read_text()
     assert child.read_bytes()==original[f'elements/{name}.celem'] and snapshot(peer)==peer_original
     if permission:assert target.stat().st_mode&0o222==0
     print('PASS late permission/reference change refused without unregister',flush=True)
   finally:
    if permission:target.chmod(mode)
  elif '--always' in sys.argv:
   with phase('always_reference'):
    r.locator('#confirm').click()
    expect(page.locator('#status')).to_contain_text('최종 소스에 반영되지 않았습니다',timeout=120000)
    unchanged()
    print('PASS manifest always reference blocks final confirmation despite stage success',flush=True)
  else:
   with phase('confirm'):
    # Observe actual modal disappearance in the page; Playwright's wait polling
    # can otherwise add a substantial delay to the reported UI-completion time.
    r.locator('#confirm').evaluate('''b=>{window.__retirementUIClose=null;b.addEventListener('click',()=>{const start=performance.now(),review=b.closest('.window[data-key=review]');const check=()=>{if(!review?.isConnected||!review.getClientRects().length){window.__retirementUIClose=performance.now()-start;return;}if(performance.now()-start<120000)requestAnimationFrame(check);};requestAnimationFrame(check);},{capture:true,once:true});}''')
    next_start=time.time()
    r.locator('#confirm').click();deadline=time.monotonic()+120
    while f'element {name} object' in manifest.read_text() and time.monotonic()<deadline:page.wait_for_timeout(25)
    print('durable unregister ms',round((time.time()-next_start)*1000),flush=True)
    assert f'element {name} object' not in manifest.read_text();expect(r).to_be_hidden(timeout=120000);assert child.read_bytes()==original[f'elements/{name}.celem']
    page.wait_for_function('()=>window.__retirementUIClose!==null');print('ui close observed ms',round(page.evaluate('()=>window.__retirementUIClose')),flush=True)
    assert all(snapshot(project)[k]==v for k,v in original.items() if k!='project.cproj');assert snapshot(peer)==peer_original
   with phase('ui_stable'):
    expect(filter(b,name)).to_have_count(0,timeout=120000)
  page.wait_for_function('()=>typeof confectoryFlushPresentation==="function"');page.evaluate('()=>confectoryFlushPresentation()')
 if not any(x in sys.argv for x in ('--always','--conflict','--late-reference','--permission')):
  with web(browser,'cold') as page:
   with phase('cold_reopen'):
    b=browser_panel(page);expect(filter(b,name)).to_have_count(0);assert child.exists();assert snapshot(peer)==peer_original
  if '--run' in sys.argv:
   with web(browser,'run-after-retirement') as page:
    assert f'element {name} object' not in manifest.read_text()
    run_at_offset(page,'after-retirement',(204,0,0))
    print('PASS explicit Run after retire uses original TimingRules configuration',flush=True)
  if '--recover' in sys.argv:
   with web(browser,'recover-check') as page:
    b=browser_panel(page);expect(filter(b,name)).to_have_count(0);retained=child.read_bytes()
    b.locator('[data-browser-control="browser-actions"]').click()
    page.get_by_role('button',name='삭제 항목 복구',exact=True).click()
    page.locator('.context-menu').get_by_role('button',name=name,exact=True).click()
    expect(filter(b,name)).to_have_count(1,timeout=120000)
    assert f'element {name} object' not in manifest.read_text() and child.read_bytes()==retained
    r=review(page,b);r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000)
    assert f'element {name} object' in manifest.read_text() and child.read_bytes()==retained
    print('PASS existing recovery UI restores registration and original bytes',flush=True)
  env.update(CONFECTORY_WEB_PROJECT=str(peer/'project.cproj'),CONFECTORY_HOME_STORAGE=str(root/'peer-profile'),CONFECTORY_ENTRY_STORAGE=str(root/'peer-profile'))
  with web(browser,'peer') as page:
   b=browser_panel(page);expect(filter(b,name)).to_be_visible();assert snapshot(peer)==peer_original
   print('PASS same-ID peer still present in actual editor',flush=True)
rows=[line for trace in traces for line in trace.read_text().splitlines()]
for label,(start,end) in (phases.items() if traces else []):
 selected=[line for line in rows if (m:=re.match(r'\d+ (\d+\.\d+)',line)) and start<=float(m[1])<=end]
 csc=[line for line in selected if 'execve(' in line and 'csc.dll' in line]
 dll=[line for line in selected if 'openat(' in line and '.dll' in line and str(project/'.confectory') in line]
 print(label,'csc',len(csc),'link',sum('/outputs/linux/' in l for l in csc),'dll',len(dll),'writes',sum('O_WRONLY' in l or 'O_RDWR' in l or 'O_CREAT' in l for l in dll),flush=True)
 if '--baseline' not in sys.argv:assert not csc and not dll,(label,len(csc),len(dll))
if '--timeline' in sys.argv:
 calls=[];pending=[]
 for line in (root/'confirm.log').read_text().splitlines():
  if not line.startswith('CONFECTORY_UI_TRACE '):continue
  row=json.loads(line.split(' ',1)[1])
  if row['stage']=='authoring-process':pending.append((row['operation'],row['elapsedMs']))
  if row['stage']=='consumer':
   if row.get('endpoint')=='confirmGroup':calls.append(pending)
   pending=[]
 print('confirm authoring calls',json.dumps(calls),flush=True)
 if '--expect-retirement-only-proof' in sys.argv:
  assert len(calls)==1,calls
  names=[name for name,_ in calls[0]]
  assert names.count('validateExistingSchemaObjectRetirement')==1 and 'validateExistingSchemaObjectCreation' not in names,names
  print('PASS no inapplicable creation proof; full retirement proof invoked',flush=True)
elif '--expect-retirement-only-proof' in sys.argv:
 raise AssertionError('--expect-retirement-only-proof requires --timeline')
print('PASS actual retirement scenario',flush=True)
