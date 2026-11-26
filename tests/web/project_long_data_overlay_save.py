"""Measure one existing long setting through the normal Chromium Save.

Arguments: BUILD_REPORT OVERLAY UI_CREATED_EVIDENCE_ROOT [--trace] [--baseline]
[--assets] [--legacy-finalization] [--legacy-settlement] [--lost-owner-response] [--guard-object|--guard-schema|--guard-final-object|--guard-final-schema] [--run] [--timeline] [--context-batch|--context-baseline]. Every invocation makes a disposable copy.
The final guards introduce external changes only after the normal UI has checkpointed the candidate.
The optional assets are 32 MiB of inert synthetic files, never real user data.
"""
import os,sys,shutil,tempfile,subprocess,signal,time,json,re
from pathlib import Path
from contextlib import contextmanager
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"gui"))
expect.set_options(timeout=30000)
repo=Path(sys.argv[2]).resolve();source=Path(sys.argv[3]).resolve()/'projects'/'Timing Puzzle'
assert source.parent.parent.name.startswith('confectory-local-first-')
root=Path(tempfile.mkdtemp(prefix='confectory-data-value-copy-'));print('fixture',root,flush=True)
project=root/'project';peer=root/'peer'
for dest in (project,peer):shutil.copytree(source,dest,ignore=shutil.ignore_patterns('.confectory','.build'))
manifest=project/'project.cproj';ns=manifest.read_text().split()[1]
if '--assets' in sys.argv:
 folder=project/'assets';folder.mkdir()
 for i in range(128):(folder/f'fixture-{i:03}.txt').write_bytes(bytes([65+i%26])*262144)
print('source files',sum(1 for p in project.rglob('*') if p.is_file()),'bytes',sum(p.stat().st_size for p in project.rglob('*') if p.is_file()),flush=True)
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
 trace=root/(label+'.strace');traces.append(trace)
 with (root/(label+'.log')).open('w') as log:
  host=subprocess.Popen((['strace','-D','-f','-ttt','-s','512','-e','trace=execve,openat,mkdir,mkdirat,rename,renameat,renameat2,copy_file_range,sendfile','-o',str(trace)]+run) if '--trace' in sys.argv else run,cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
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

from editor_logic_workflow import find_project_item
def save_existing_rule(page,window,new):
 # Only an already confirmed object value may use this single direct Save.
 button=window.locator('[data-element-action=confirm]');expect(button).to_have_text('저장')
 calls=[];all_calls=[];blueprint_calls=[]
 if '--timeline' in sys.argv:page.evaluate('()=>globalThis.confectoryWebUITrace=[]')
 def observe(request):
  if request.method!='POST':return
  try:payload=request.post_data_json
  except Exception:return
  if isinstance(payload,dict) and payload.get('op')=='invoke':
   endpoint=payload.get('endpoint');all_calls.append(endpoint)
   if endpoint=='blueprint':blueprint_calls.append(payload.get('input',{}).get('action'))
   if endpoint in ('reviewGroup','confirmGroup','directPropertyConfirm'):calls.append(endpoint)
 page.on('request',observe)
 page.evaluate("""()=>{window.__directRuleReviewSeen=false;const visible=()=>[...document.querySelectorAll('#review-creation,.window[data-key=review]')].some(e=>e.getClientRects().length>0);const check=()=>{if(visible())window.__directRuleReviewSeen=true};check();window.__directRuleObserver=new MutationObserver(check);window.__directRuleObserver.observe(document.body,{subtree:true,childList:true,attributes:true});}""")
 try:
  started=time.monotonic();button.click()
  deadline=time.monotonic()+120
  while time.monotonic()<deadline and (not any(c in calls for c in ('confirmGroup','directPropertyConfirm')) or f'data OpenMilliseconds = {new};' not in source_file.read_text()):page.wait_for_timeout(50)
  print('durable ms',round((time.monotonic()-started)*1000),flush=True)
  expect(page.locator('#status')).to_have_text('저장했습니다.',timeout=120000)
  expect(page.locator('#review-creation')).to_be_hidden();expect(page.locator('.window[data-key=review]')).to_be_hidden()
  assert not page.evaluate('()=>window.__directRuleReviewSeen'), 'A Review was displayed during direct Save'
  expected=['reviewGroup','confirmGroup'] if '--legacy-finalization' in sys.argv or '--baseline' in sys.argv else ['directPropertyConfirm']
  assert calls==expected,calls
  expected_owner=['readOwnerEdits','applySlots','settledSlots','settledSlots'] if any(flag in sys.argv for flag in ('--legacy-settlement','--legacy-finalization','--baseline')) else ['readOwnerEdits','applySlots']
  assert [action for action in blueprint_calls if action in ('readOwnerEdits','applySlots','settledSlots')]==expected_owner,blueprint_calls
  print('owner requests',blueprint_calls,flush=True)
  from collections import Counter
  print('finalization requests',calls,'total invokes',len(all_calls),dict(Counter(all_calls)),flush=True)
 finally:
  page.remove_listener('request',observe);page.evaluate('()=>window.__directRuleObserver?.disconnect()')
  if '--timeline' in sys.argv:print('RENDERER',json.dumps(page.evaluate('()=>globalThis.confectoryWebUITrace')),flush=True)


def rules(page):
 page.evaluate('()=>confectoryFlushPresentation()')
 for key in ('schema','blueprint','declaration','targets','packs'):
  other=page.locator(f'.window[data-key={key}]')
  if other.is_visible():other.locator('[data-close]').first.click()
 find_project_item(page,ns+'::TimingRules','개념')
 w=page.locator('.window[data-key=schema]');expect(w.locator('.object-title-name')).to_have_text('TimingRules');return w
source_file=project/'elements/TimingRules.celem'
import ctypes,io
from PIL import Image
from ctypes import c_void_p,c_int,c_uint,c_ulong
def run_at_offset(page,label,expected):
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
 page.evaluate('()=>confectoryFlushPresentation()')
 tab=page.get_by_role('tab',name='Workspace',exact=True)
 if tab.get_attribute('aria-selected')!='true':tab.click();expect(tab).to_have_attribute('aria-selected','true')
with sync_playwright() as pw,pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']) as browser:
 with web(browser,'value-save') as page:
  w=rules(page)
  if '--lost-owner-response' in sys.argv:
   value=w.get_by_label('OpenMilliseconds 기본값',exact=True);expect(value).to_have_value('1000');value.fill('2000')
   applies=[];queries=[];masked=[]
   def lose_response(route):
    try:body=route.request.post_data_json
    except Exception:body=None
    if isinstance(body,dict) and body.get('endpoint')=='blueprint':
     action=body.get('input',{}).get('action')
     if action=='applySlots':applies.append(body['requestId'])
     elif action=='settledSlots' and applies:queries.append(body['requestId'])
    response=route.fetch();payload=response.json()
    for row in payload.get('results',[]):
     rid=row.get('requestId')
     if rid not in applies+queries:continue
     if rid in applies:assert row.get('ok') and row.get('result',{}).get('ownerSettled') is True,row
     masked.append(rid);row.clear();row.update(requestId=rid,ok=False,error={'code':'transport_lost'})
    route.fulfill(response=response,json=payload)
   page.route('**/api/request',lose_response)
   w.locator('[data-element-action=confirm]').click()
   expect(page.locator('#status')).to_have_text('transport_lost',timeout=120000)
   assert len(applies)==1 and queries and len(masked)>=2
   assert source_file.read_bytes()==original['elements/TimingRules.celem']
   checkpoint=next((project/'.confectory/edit-workspaces').glob('*/draft.json'));held=checkpoint.read_bytes()
   assert b'OpenMilliseconds = 2000;' in held
   def journals():
    return [v for file in (root/'profile/presentations').glob('*.json') for _,v in json.loads(file.read_text()).get('inputs',{}).get('blueprint',[]) if v.get('kind')=='owner-attempt']
   assert len(journals())==1
   page.unroute_all(behavior='wait')
   print('PASS apply checkpoint persisted with reply lost and journal retained',flush=True)
  elif '--guard-final-object' in sys.argv or '--guard-final-schema' in sys.argv:
   value=w.get_by_label('OpenMilliseconds 기본값',exact=True);expect(value).to_have_value('1000');value.fill('2000')
   target=source_file if '--guard-final-object' in sys.argv else project/'elements'/(re.search(r'use schema [^:]+::([^;]+);',source_file.read_text())[1]+'.celem')
   before=target.read_bytes()
   changed=before.replace(b'OpenMilliseconds = 1000',b'OpenMilliseconds = 3000') if target==source_file else before.replace(b'general long',b'general bool')
   assert changed!=before
   observed=[]
   def before_finalize(route):
    try:payload=route.request.post_data_json
    except Exception:payload=None
    if isinstance(payload,dict) and payload.get('endpoint')==('confirmGroup' if '--legacy-finalization' in sys.argv or '--baseline' in sys.argv else 'directPropertyConfirm') and not observed:
     assert source_file.read_bytes()==original['elements/TimingRules.celem']
     target.write_bytes(changed);observed.append(True)
    route.fallback()
   page.route('**/*',before_finalize)
   w.locator('[data-element-action=confirm]').click()
   expect(page.locator('#status')).to_contain_text('유지',timeout=120000)
   assert observed and target.read_bytes()==changed
   assert all(snapshot(project)[k]==v for k,v in original.items() if k!=str(target.relative_to(project)))
   assert snapshot(peer)==peer_original
   drafts=list((project/'.confectory/edit-workspaces').glob('*/draft.json'))
   assert any('OpenMilliseconds = 2000;' in draft.read_text() for draft in drafts), 'Checkpoint did not retain the attempted value'
   print('PASS external change at finalization and durable draft retained',flush=True)
  elif '--guard-object' in sys.argv or '--guard-schema' in sys.argv:
   value=w.get_by_label('OpenMilliseconds 기본값',exact=True);expect(value).to_have_value('1000');value.fill('2000')
   target=source_file if '--guard-object' in sys.argv else project/'elements'/(re.search(r'use schema [^:]+::([^;]+);',source_file.read_text())[1]+'.celem')
   before=target.read_bytes()
   changed=before.replace(b'OpenMilliseconds = 1000',b'OpenMilliseconds = 3000') if target==source_file else before.replace(b'general long',b'general int')
   assert changed!=before;target.write_bytes(changed)
   w.locator('[data-element-action=confirm]').click();expect(page.locator('#status')).to_contain_text('입력은 유지',timeout=120000)
   expect(value).to_have_value('2000');assert target.read_bytes()==changed
   assert all(snapshot(project)[k]==v for k,v in original.items() if k!=str(target.relative_to(project)))
   assert snapshot(peer)==peer_original;print('PASS external edit and private input preserved',flush=True)
  else:
   for i in range(3):
    previous=int(re.search(r'data OpenMilliseconds = (\d+);',source_file.read_text())[1]);new=3500 if previous==1000 else 1000
    value=w.get_by_label('OpenMilliseconds 기본값',exact=True);expect(value).to_have_value(str(previous));value.fill(str(new))
    with phase(f'save{i+1}'):save_existing_rule(page,w,new)
    assert f'data OpenMilliseconds = {new};' in source_file.read_text()
    assert all(snapshot(project)[k]==v for k,v in original.items() if k!='elements/TimingRules.celem')
    assert snapshot(peer)==peer_original
    w=rules(page);expect(w.get_by_label('OpenMilliseconds 기본값',exact=True)).to_have_value(str(new))
   print('PASS three direct saves/reopen and sources preserved',flush=True)
 if '--lost-owner-response' in sys.argv:
  with web(browser,'cold-recovery') as page:
   w=rules(page);expect(w.get_by_label('OpenMilliseconds 기본값',exact=True)).to_have_value('2000')
   assert len(journals())==1 and checkpoint.read_bytes()==held
   recovered=[]
   def observe_recovery(request):
    try:body=request.post_data_json
    except Exception:return
    if isinstance(body,dict) and body.get('endpoint')=='blueprint':recovered.append(body.get('input',{}).get('action'))
   page.on('request',observe_recovery)
   w.locator('[data-element-action=save]').click()
   deadline=time.monotonic()+120
   while journals() and time.monotonic()<deadline:page.wait_for_timeout(50)
   assert not journals() and 'settledSlots' in recovered and 'applySlots' not in recovered,recovered
   assert checkpoint.read_bytes()==held and source_file.read_bytes()==original['elements/TimingRules.celem']
   assert snapshot(peer)==peer_original
   print('PASS cold recovery settled without repeating write; checkpoint identical',recovered,flush=True)
   w.locator('[data-element-action=confirm]').click()
   review=page.locator('.window[data-key=review]')
   creation=page.locator('#review-creation')
   deadline=time.monotonic()+120
   while not (review.is_visible() or creation.is_visible()) and time.monotonic()<deadline:page.wait_for_timeout(50)
   if creation.is_visible():creation.click()
   expect(review).to_be_visible(timeout=120000)
   if review.locator('[data-review-advanced]').is_visible():review.locator('[data-review-advanced]').click()
   if review.locator('[data-advanced-reviewed]').count():review.locator('[data-advanced-reviewed]').check()
   review.locator('#confirm').click();expect(review).to_be_hidden(timeout=120000)
   assert 'data OpenMilliseconds = 2000;' in source_file.read_text()
   assert all(snapshot(project)[k]==v for k,v in original.items() if k!='elements/TimingRules.celem')
   assert snapshot(peer)==peer_original
   print('PASS recovered draft explicit finalization once',flush=True)
 if '--run' in sys.argv:
  with web(browser,'cold-run') as page:
   w=rules(page);expect(w.get_by_label('OpenMilliseconds 기본값',exact=True)).to_have_value('3500');w.locator('[data-close]').first.click()
   run_at_offset(page,'after-overlay',(0,204,0));print('PASS cold explicit Run uses value',flush=True)
if phases:
 from statistics import median
 print('Save median ms',round(median((end-start)*1000 for start,end in phases.values()),1),flush=True)
if '--trace' in sys.argv:
 rows=[line for trace in traces for line in trace.read_text().splitlines()]
 for label,(start,end) in phases.items():
  selected=[line for line in rows if (m:=re.match(r'\d+ (\d+\.\d+)',line)) and start<=float(m[1])<=end]
  csc=[line for line in selected if 'execve(' in line and 'csc.dll' in line]
  dll=[line for line in selected if 'openat(' in line and '.dll' in line and str(project/'.confectory') in line]
  candidate=[line for line in selected if str(project/'.confectory/candidates') in line]
  starts=[line for line in candidate if 'mkdir(' in line or 'mkdirat(' in line]
  renames=[line for line in candidate if 'rename(' in line or 'renameat' in line]
  copied=[line for line in candidate if 'openat(' in line and 'O_CREAT' in line]
  print(label,'csc',len(csc),'DLL',len(dll),'candidate syscalls',len(candidate),'candidate file creates',len(copied),flush=True)
  if starts and renames:
   t=lambda l:float(l.split()[1])
   print('candidate first mkdir to first rename (copy+write) ms',round((t(renames[0])-t(starts[0]))*1000,2),flush=True)
  assert not csc and not dll
  if '--baseline' not in sys.argv:assert not candidate,(label,len(candidate))

if '--timeline' in sys.argv and phases:
 groups=[];group=[];reviews=[]
 for line in (root/'value-save.log').read_text().splitlines():
  if not line.startswith('CONFECTORY_UI_TRACE '):continue
  row=json.loads(line.split(' ',1)[1])
  if row['stage']=='authoring-process':group.append(row)
  if row['stage']=='consumer':
   mixed=[item['elapsedMs'] for item in group if item.get('operation')=='mixedOwnerCopyEdits']
   if row.get('endpoint')=='blueprint' and mixed:groups.append({'consumerMs':row['elapsedMs'],'mixedPreparationMs':mixed,'effectiveMs':[item['elapsedMs'] for item in group if item.get('operation')=='effective']})
   if row.get('endpoint') in ('reviewGroup','confirmGroup','directPropertyConfirm'):reviews.append({'endpoint':row['endpoint'],'consumerMs':row['elapsedMs'],'propertyObservationsMs':[item['elapsedMs'] for item in group if item.get('operation')=='blueprintPropertyObservations'],'overlayMs':[item['elapsedMs'] for item in group if item.get('operation')=='validateLongDataOverlay']})
   group=[]
 print('OWNER PREPARATION',json.dumps(groups),flush=True)
 print('REVIEW CONFIRM',json.dumps(reviews),flush=True)
 assert len(groups)==len(phases),groups
 assert all(len(group['mixedPreparationMs'])==(2 if '--baseline' in sys.argv else 1) for group in groups),groups

 if '--context-batch' in sys.argv or '--context-baseline' in sys.argv:
  assert all(len(group['effectiveMs'])==(1 if '--context-batch' in sys.argv else 4) for group in groups),groups
