"""Actual authored native runtime input and render loop.

Run after project_installed_pack_registration.py on its disposable UI-created
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

def verify_clicks(window_id):
 x=ctypes.CDLL('libX11.so.6');t=ctypes.CDLL('libXtst.so.6');x.XOpenDisplay.restype=c_void_p;x.XFlush.argtypes=[c_void_p];x.XCloseDisplay.argtypes=[c_void_p];t.XTestFakeMotionEvent.argtypes=[c_void_p,c_int,c_int,c_int,c_ulong];t.XTestFakeButtonEvent.argtypes=[c_void_p,c_uint,c_int,c_ulong]
 d=x.XOpenDisplay(None);assert d
 geometry=subprocess.check_output(['xwininfo','-id',window_id],text=True)
 sx=int(re.search(r'Absolute upper-left X:\s*(-?\d+)',geometry)[1]);sy=int(re.search(r'Absolute upper-left Y:\s*(-?\d+)',geometry)[1])
 def capture():return Image.open(io.BytesIO(subprocess.check_output(['import','-window',window_id,'png:-']))).convert('RGB')
 try:
  for label,expected in [('success',(0,204,0)),('failure',(204,0,0))]:
   deadline=time.monotonic()+6
   while time.monotonic()<deadline:
    im=capture();pixel=im.getpixel((45,45))
    if pixel==expected:
     t.XTestFakeMotionEvent(d,0,sx+80,sy+70,0);t.XTestFakeButtonEvent(d,1,1,0);t.XTestFakeButtonEvent(d,1,0,0);x.XFlush(d);time.sleep(.15);im=capture()
     if im.getpixel((45,165))==expected:break
   else:raise AssertionError((label,pixel,im.getpixel((45,165))))
   im.save(root/f'timing-{label}.png');print('PASS actual pointer',label,im.getpixel((45,165)),flush=True)
 finally:x.XCloseDisplay(d)

def run_and_click(page):
 page.evaluate('async()=>await confectoryFlushPresentation()');tab=page.get_by_role('tab',name='Workspace',exact=True)
 if tab.get_attribute('aria-selected')!='true':tab.click();expect(tab).to_have_attribute('aria-selected','true')
 page.get_by_role('button',name='프로젝트 실행',exact=True).click();deadline=time.monotonic()+120
 while time.monotonic()<deadline:
  tree=subprocess.check_output(['xwininfo','-root','-tree'],text=True);found=re.search(r'(0x[0-9a-f]+) "Timing Puzzle Interactive"',tree)
  if found:verify_clicks(found[1]);break
  page.wait_for_timeout(100)
 else:raise AssertionError('No native window')
 expect(page.locator('.run-window:visible [data-run-frame]')).to_have_text('종료 코드 0',timeout=120000)

def guard_code_imports(page):
 page.evaluate('async()=>await confectoryFlushPresentation()');tab=page.get_by_role('tab',name='Workspace',exact=True)
 if tab.get_attribute('aria-selected')!='true':tab.click();expect(tab).to_have_attribute('aria-selected','true')
 for key in ('targets','packs','blueprint','declaration'):
  other=page.locator(f'.window[data-key={key}]')
  if other.is_visible():other.locator('[data-close]').first.click()
 find_project_item(page,ns+'::'+FEATURE,'기능');dec=page.locator('.window[data-key=declaration]');expect(dec.locator('.object-title-name')).to_have_text(FEATURE)
 dec.locator('[data-function-write-direct]').click();panel=page.locator('.window[data-key=blueprint]');doc=panel.locator('.function-document');expect(doc).to_be_visible()
 for feature,_ in bindings:expect(doc.locator(f'[data-code-import-id="{feature}"] [data-code-import-alias]')).to_contain_text('fg_call_')
 source=project/'elements'/f'{FEATURE}BlueprintBody.celem';before=source.read_bytes()
 def reject(feature):
  doc.locator('[data-document-code-import=body]').click();dialog=page.get_by_role('dialog',name='코드 기능 참조',exact=True);dialog.locator('[data-code-import-feature]').fill(feature);dialog.locator('[data-code-import-apply]').click();expect(dialog.locator('[data-code-import-error]')).not_to_have_text('');expect(dialog.locator('[data-code-import-feature]')).to_have_value(feature);dialog.locator('[data-close]').click()
 reject(bindings[0][0]);assert source.read_bytes()==before
 # Only a disposable fixture is changed to emulate a competing editor, not to author the game.
 graph=project/re.search(r'blueprint common "([^"]+)"',before.decode())[1];original=graph.read_bytes();changed=original+b'\n'
 try:
  graph.write_bytes(changed);reject('Confectory.Window::TextStyle');assert graph.read_bytes()==changed and source.read_bytes()==before
 finally:graph.write_bytes(original)
 print('PASS duplicate and competing external graph rejected; native sources preserved',flush=True)

with sync_playwright() as pw, pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox']) as browser:
    if "--cold-only" not in sys.argv and "--guard-only" not in sys.argv:
        with f.web(browser, 'code-import-runtime') as page:
            page.evaluate('async()=>await confectoryFlushPresentation()')
            page.get_by_role('tab',name='Workspace',exact=True).click()
            for key in ('targets','packs','blueprint','declaration'):
                other=page.locator(f'.window[data-key={key}]')
                if other.is_visible():other.locator('[data-close]').first.click()
            if not (project/'elements'/f'{FEATURE}.celem').exists():
                b=project_browser(page);b.get_by_role('button',name='기능',exact=True).click();b.locator('[data-new]').click()
                page.get_by_role('button',name='기능 생성',exact=True).click()
                d=page.get_by_role('dialog',name='새 기능 만들기',exact=True)
                d.locator('#object-name').fill(FEATURE);d.get_by_role('button',name='생성',exact=True).click();expect(d).to_be_hidden()
                dec=page.locator('.window[data-key=declaration]');expect(dec.locator('.object-title-name')).to_have_text(FEATURE)
                dec.locator('[data-function-write-direct]').click();panel=page.locator('.window[data-key=blueprint]');expect(panel.locator('.function-document')).to_be_visible()
                panel.locator('[data-document-code=body]').click();dialog=page.locator('.bp-script-dialog');src=dialog.locator('[data-code-source]');expect(src).to_be_visible()
                src.evaluate("""el=>{const p=[...el.closest('.bp-script-editor').querySelectorAll('[data-code-highlight]>span')];const i=p.findIndex(x=>x.dataset.codeRegion==='body');const n=p.slice(0,i).reduce((a,x)=>a+x.textContent.length,0);el.focus();el.setSelectionRange(n,n+p[i].textContent.length)}""")
                page.keyboard.insert_text('return 0; // Window entry');dialog.locator('[data-code-save]').click();expect(dialog).to_be_hidden()
                panel.locator('[data-bp-save]').click();expect(panel.locator('.bp-status')).to_have_text('저장됨',timeout=120000);confirm(page,panel.locator('[data-bp-complete]'))
                panel.locator('[data-close]').first.click()
                if b.is_visible():b.locator('[data-close]').first.click()
                if dec.is_visible():dec.locator('[data-close]').first.click()
            find_project_item(page,ns+'::'+FEATURE,'기능')
            dec=page.locator('.window[data-key=declaration]');expect(dec.locator('.object-title-name')).to_have_text(FEATURE)
            page.evaluate('async()=>await confectoryFlushPresentation()')
            source=project/'elements'/f'{FEATURE}.celem'
            for function,implementation in bindings:
                if f'provide {function} with {implementation};' in source.read_text():continue
                dec.locator('[data-registered-provider]').click();d=page.get_by_role('dialog',name='등록 팩 구현 지정',exact=True)
                d.locator('[data-provider-function]').fill(function);d.locator('[data-provider-implementation]').fill(implementation);d.locator('[data-provider-apply]').click();expect(d).to_be_hidden(timeout=30000)
                confirm(page,dec.locator('[data-feature-action=confirm]'));print('PASS binding',function,flush=True)
                page.evaluate('async()=>await confectoryFlushPresentation()')
                dec.locator('[data-close]').first.click();find_project_item(page,ns+'::'+FEATURE,'기능');expect(dec.locator('.object-title-name')).to_have_text(FEATURE)
            dec.locator('[data-function-write-direct]').click();panel=page.locator('.window[data-key=blueprint]');doc=panel.locator('.function-document');expect(doc).to_be_visible()
            for function,_ in bindings:
                doc.locator('[data-document-code-import=body]').click();d=page.get_by_role('dialog',name='코드 기능 참조',exact=True);d.locator('[data-code-import-feature]').fill(function);d.locator('[data-code-import-apply]').click();expect(d).to_be_hidden(timeout=30000);print('PASS import',function,flush=True)
            aliases=[doc.locator(f'[data-code-import-id="{fn}"] [data-code-import-alias]').inner_text() for fn,_ in bindings]
            create,pump,draw,close=aliases
            code=f"""var surfaces={create}.Invoke(new[]{{"Timing Puzzle Interactive"}},420,260);
try {{
 var watch=System.Diagnostics.Stopwatch.StartNew();int result=0;
 while(watch.ElapsedMilliseconds<18000) {{
  bool green=(watch.ElapsedMilliseconds/1500)%2==0;
  var events={pump}.Invoke(surfaces);
  for(int i=0;i+5<events.Length;i+=6) {{
   if(events[i+1]==8)return 0;
   if(events[i+1]==1&&events[i+2]>=40&&events[i+2]<200&&events[i+3]>=40&&events[i+3]<120)result=green?1:2;
  }}
  {draw}.Invoke(surfaces,0,new[]{{0,0,420,260,0xeeeeee,40,40,160,80,green?0x00cc00:0xcc0000,40,160,160,60,result==1?0x00cc00:result==2?0xcc0000:0x777777}},new[]{{"Timing Puzzle",green?"Click now":"Wait",result==1?"Success":result==2?"Failure":"No attempt"}});
  System.Threading.Thread.Sleep(25);
 }}
 return 0;
}} finally {{ {close}.Invoke(surfaces,-1); }}"""
            panel.locator('[data-document-code=body]').click();dialog=page.locator('.bp-script-dialog');src=dialog.locator('[data-code-source]');expect(src).to_be_visible()
            src.evaluate("""el=>{const p=[...el.closest('.bp-script-editor').querySelectorAll('[data-code-highlight]>span')];const i=p.findIndex(x=>x.dataset.codeRegion==='body');const n=p.slice(0,i).reduce((a,x)=>a+x.textContent.length,0);el.focus();el.setSelectionRange(n,n+p[i].textContent.length)}""")
            page.keyboard.insert_text(code);dialog.locator('[data-code-save]').click();expect(dialog).to_be_hidden()
            panel.locator('[data-bp-save]').click();expect(panel.locator('.bp-status')).to_have_text('저장됨',timeout=120000);confirm(page,panel.locator('[data-bp-complete]'));print('PASS compiled interactive code',flush=True)
            panel.locator('[data-close]').first.click()
            if dec.is_visible():dec.locator('[data-close]').first.click()
            r,w=stage_entry(page,ns+'::'+FEATURE);r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);w.locator('[data-close]').click()
            run_and_click(page)
    with f.web(browser,'cold-interactive-input') as page:
        assert f'entry {ns}::{FEATURE};' in manifest.read_text()
        if '--guard-only' in sys.argv:guard_code_imports(page)
        else:
            run_and_click(page)
            print('PASS cold UI native input + render + exit',flush=True)
