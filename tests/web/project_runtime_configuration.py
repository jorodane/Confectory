"""Actual published configuration values consumed by native timing loop.

Run after project_runtime_input.py on its disposable UI-created
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
FEATURE='PlayInteractiveTiming'
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

def save_existing_rule(page,window):
 # Only an already confirmed object value may use this single direct Save.
 button=window.locator('[data-element-action=confirm]');expect(button).to_have_text('저장')
 calls=[]
 def observe(request):
  if request.method!='POST':return
  try:payload=request.post_data_json
  except Exception:return
  if isinstance(payload,dict) and payload.get('op')=='invoke' and payload.get('endpoint') in ('reviewGroup','confirmGroup'):calls.append(payload['endpoint'])
 page.on('request',observe)
 page.evaluate("""()=>{window.__directRuleReviewSeen=false;const visible=()=>[...document.querySelectorAll('#review-creation,.window[data-key=review]')].some(e=>e.getClientRects().length>0);const check=()=>{if(visible())window.__directRuleReviewSeen=true};check();window.__directRuleObserver=new MutationObserver(check);window.__directRuleObserver.observe(document.body,{subtree:true,childList:true,attributes:true});}""")
 try:
  button.click();expect(page.locator('#status')).to_have_text('저장했습니다.',timeout=120000)
  expect(page.locator('#review-creation')).to_be_hidden();expect(page.locator('.window[data-key=review]')).to_be_hidden()
  assert not page.evaluate('()=>window.__directRuleReviewSeen'), 'A Review was displayed during direct Save'
  assert calls.count('reviewGroup')==calls.count('confirmGroup')==1,calls
 finally:
  page.remove_listener('request',observe);page.evaluate('()=>window.__directRuleObserver?.disconnect()')

def connect(page):
 if 'dependency Confectory.RuntimeBase ' in manifest.read_text():return
 tab=page.get_by_role('tab',name='Pack Manager',exact=True);tab.click();expect(tab).to_have_attribute('aria-selected','true');expect(page.locator('#home-pack-connect')).to_be_enabled();page.locator('#home-pack-connect').click()
 d=page.get_by_role('dialog',name='설치된 팩 연결',exact=True);d.locator('[data-installed-pack-choice]').select_option('Confectory.RuntimeBase');d.locator('[data-installed-pack-review]').click()
 r=page.locator('.window[data-key=review]');expect(r).to_be_visible(timeout=120000)
 if r.locator('[data-review-advanced]').is_visible():r.locator('[data-review-advanced]').click()
 if r.locator('[data-advanced-reviewed]').count():r.locator('[data-advanced-reviewed]').check()
 r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000)

def author_configuration(page):
  window=rules(page);source=project/'elements/TimingRules.celem'
  assert 'data PhaseMilliseconds' not in source.read_text() and not window.locator('[data-definition-key]').count()
  add_field(page,window,'PhaseMilliseconds',5000);add_field(page,window,'OpenMilliseconds',3500);save_rules(page,window)
  assert 'data PhaseMilliseconds = 5000;' in source.read_text() and 'data OpenMilliseconds = 3500;' in source.read_text()
  print('PASS two typed settings confirmed through UI',flush=True)
  window.locator('[data-close]').first.click();connect(page);activate(page)
  find_project_item(page,ns+'::'+FEATURE,'기능');dec=page.locator('.window[data-key=declaration]');expect(dec.locator('.object-title-name')).to_have_text(FEATURE)
  if 'use object '+ns+'::TimingRules;' not in (project/'elements'/f'{FEATURE}.celem').read_text():
   dec.locator('[data-owned-object-use]').click();d=page.get_by_role('dialog',name='프로젝트 객체 참조',exact=True);d.locator('[data-owned-object-id]').fill(ns+'::TimingRules');d.locator('[data-owned-object-apply]').click();expect(d).to_be_hidden(timeout=30000);confirm(page,dec.locator('[data-feature-action=confirm]'));print('PASS linked object',flush=True)
   dec.locator('[data-close]').first.click();find_project_item(page,ns+'::'+FEATURE,'기능');expect(dec.locator('.object-title-name')).to_have_text(FEATURE)
  dec.locator('[data-function-write-direct]').click();panel=page.locator('.window[data-key=blueprint]');doc=panel.locator('.function-document');expect(doc).to_be_visible()
  doc.locator('[data-document-code-import=body]').click();d=page.get_by_role('dialog',name='코드 기능 참조',exact=True);d.locator('[data-code-import-feature]').fill('Confectory.RuntimeBase::ReadDeclaredLong');d.locator('[data-code-import-apply]').click();expect(d).to_be_hidden(timeout=30000)
  print('PASS config import',flush=True)
  aliases=[doc.locator(f'[data-code-import-id="{fn}"] [data-code-import-alias]').inner_text() for fn,_ in bindings];create,pump,draw,close=aliases
  read=doc.locator('[data-code-import-id="Confectory.RuntimeBase::ReadDeclaredLong"] [data-code-import-alias]').inner_text()
  code=f"""long phase={read}.Invoke("{ns}::TimingRules","PhaseMilliseconds"), open={read}.Invoke("{ns}::TimingRules","OpenMilliseconds");
if(phase<=0||open<=0||open>=phase)return 2;
var surfaces={create}.Invoke(new[]{{"Timing Puzzle Configured"}},420,260);
try {{
 var watch=System.Diagnostics.Stopwatch.StartNew();int result=0;
 while(watch.ElapsedMilliseconds<10000) {{
  bool green=watch.ElapsedMilliseconds%phase<open;
  var events={pump}.Invoke(surfaces);
  for(int i=0;i+5<events.Length;i+=6) {{
   if(events[i+1]==8)return 0;
   if(events[i+1]==1&&events[i+2]>=40&&events[i+2]<200&&events[i+3]>=40&&events[i+3]<120)result=green?1:2;
  }}
  {draw}.Invoke(surfaces,0,new[]{{0,0,420,260,0xeeeeee,40,40,160,80,green?0x00cc00:0xcc0000,40,160,160,60,result==1?0x00cc00:result==2?0xcc0000:0x777777}},new[]{{$"Timing Puzzle {{phase}} / {{open}}",green?"Click now":"Wait",result==1?"Success":result==2?"Failure":"No attempt"}});
  System.Threading.Thread.Sleep(25);
 }}
 return 0;
}} finally {{ {close}.Invoke(surfaces,-1); }}"""
  panel.locator('[data-document-code=body]').click();dialog=page.locator('.bp-script-dialog');src=dialog.locator('[data-code-source]');expect(src).to_be_visible()
  src.evaluate("""el=>{const p=[...el.closest('.bp-script-editor').querySelectorAll('[data-code-highlight]>span')];const i=p.findIndex(x=>x.dataset.codeRegion==='body');const n=p.slice(0,i).reduce((a,x)=>a+x.textContent.length,0);el.focus();el.setSelectionRange(n,n+p[i].textContent.length)}""")
  page.keyboard.insert_text(code);dialog.locator('[data-code-save]').click();expect(dialog).to_be_hidden();panel.locator('[data-bp-save]').click();expect(panel.locator('.bp-status')).to_have_text('저장됨',timeout=120000);confirm(page,panel.locator('[data-bp-complete]'));print('PASS config code confirmed',flush=True)

import json

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

def code_proof():
 implementation=project/'elements'/f'{FEATURE}BlueprintBody.celem';graph=project/re.search(r'blueprint common "([^"]+)"',implementation.read_text())[1];code=graph.parent/json.loads(graph.read_text())['nodes'][0]['implementation']
 return {path:path.read_bytes() for path in (implementation,graph,code,project/'elements'/f'{FEATURE}.celem')}

def conflict_test(page):
 before=code_proof();window=rules(page);value=window.get_by_label('OpenMilliseconds 기본값',exact=True);expect(value).to_have_value('1000');value.fill('2000')
 target=project/'elements/TimingRules.celem';original=target.read_bytes();changed=original.replace(b'OpenMilliseconds = 1000',b'OpenMilliseconds = 3000');assert changed!=original
 try:
  target.write_bytes(changed) # competing edit of the disposable fixture only
  window.locator('[data-element-action=confirm]').click();expect(page.locator('#status')).to_contain_text('입력은 유지',timeout=60000)
  expect(value).to_have_value('2000');assert target.read_bytes()==changed and all(p.read_bytes()==data for p,data in before.items());print('PASS external configuration change preserved and local value retained',flush=True)
 finally:target.write_bytes(original)

with sync_playwright() as pw,pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']) as browser:
 if '--guard-only' in sys.argv:
  with f.web(browser,'config-conflict') as page:conflict_test(page)
 elif '--isolation-only' in sys.argv:
  with f.web(browser,'config-isolation') as page:
   assert 'data PhaseMilliseconds = 5000;' in (project/'elements/TimingRules.celem').read_text()
   run_at_offset(page,'isolated-wide',(0,204,0));print('PASS independent same-ID project unchanged and still success',flush=True)
 else:
  if '--ready-only' not in sys.argv:
   with f.web(browser,'config-author') as page:author_configuration(page)
  if '--setup-only' not in sys.argv:
   before=code_proof()
   with f.web(browser,'config-run-initial') as page:
    run_at_offset(page,'wide',(0,204,0))
    window=rules(page);expect(window.get_by_label('PhaseMilliseconds 기본값',exact=True)).to_have_value('5000');window.get_by_label('OpenMilliseconds 기본값',exact=True).fill('1000');save_existing_rule(page,window)
    assert 'data PhaseMilliseconds = 5000;' in (project/'elements/TimingRules.celem').read_text()
    assert 'data OpenMilliseconds = 1000;' in (project/'elements/TimingRules.celem').read_text()
    assert all(p.read_bytes()==data for p,data in before.items());print('PASS one existing value directly saved once, no Review; game source byte-identical',flush=True)
    run_at_offset(page,'narrow',(204,0,0))
   with f.web(browser,'config-run-cold') as page:
    assert all(p.read_bytes()==data for p,data in before.items());run_at_offset(page,'cold',(204,0,0));print('PASS cold config runtime',flush=True)
