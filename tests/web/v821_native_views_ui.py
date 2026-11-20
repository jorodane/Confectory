"""Actual Linux engine views: generated C# is read-only; native source uses owned drafts.
No Windows, physical device or mockup visual-equivalence claim.
"""
import json,sys,time,traceback
from playwright.sync_api import sync_playwright,expect
import v666_node_names_recovery_fixture as t
f=t.f;x=t.x
mode=sys.argv[3] if len(sys.argv)>3 else 'preview'
feature=t.feature if mode=='preview' else f.n+'Native'

def panel():return f.page.locator('.window[data-key=blueprint]')
def open_function():
 f.idle();f.page.locator('#workspace').click(button='right',position={'x':1300,'y':300});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click()
 b=f.page.locator('.window[data-key^="browser:project:"]');b.get_by_role('button',name='기능',exact=True).click();b.locator('[data-browser-control=object-query]').fill(feature.split('::')[-1]);b.locator('[data-browser-control=object-search]').click();b.locator('[data-object="'+feature+'"]').press('Enter');b.locator('[data-close]').first.click();f.idle();f.page.locator('[data-operation=feature-author-open]').first.click()
 expect(panel()).to_be_visible()
def restart(index):
 f.pending();f.page.close();f.stop();f.start(index);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});f.idle()
 if not panel().is_visible():open_function()
def read_native():return f.invoke('blueprint',dict(action='readNative',feature=feature,id=f.n+'NativeBody/body:common'))['result']['result']
def saved(text):
 panel().locator('[data-native-source]').fill(text);panel().locator('[data-native-save]').click();f.idle();expect(panel().locator('.bp-status')).to_have_text('저장됨',timeout=90000);assert read_native()['source']==text

def review():
 panel().locator('[data-native-complete]').click();f.idle();targets=f.page.locator('.window[data-key=targets]')
 if targets.is_visible():targets.locator('[data-target-choice]').select_option('portable');targets.locator('[data-close]').click();panel().locator('[data-native-complete]').click();f.idle()
 r=f.page.locator('.window[data-key=review]');expect(r).to_be_visible(timeout=90000)
 if r.locator('[data-review-advanced]').is_visible():r.locator('[data-review-advanced]').click()
 if r.locator('[data-advanced-reviewed]').count():r.locator('[data-advanced-reviewed]').check()
 return r
try:
 f.start(0);f.invoke('select',{'id':feature});f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
 with sync_playwright() as pw:
  expect.set_options(timeout=45000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});open_function()
  if mode=='preview':
   baseline=t.read();expected=f.invoke('blueprint',dict(action='nativePreview',id=t.graph))['result']['result']['diagnostics'];assert expected['state']=='source-assembled',expected
   panel().get_by_role('tab',name='네이티브 미리보기',exact=True).click();view=panel().locator('.function-native-preview');expect(view.locator('[role=status]')).to_contain_text('생성됨',timeout=90000)
   assert view.locator('[data-native-body]').text_content()==expected['body'];assert not view.locator('textarea,input,[contenteditable=true]').count();assert 'body' in expected['body'] and 'after' in expected['body'];x.original();assert checkpoint.read_bytes()==before;assert not f.pending()['blueprint']
   f.checked('logical native preview equals the real source-assembled engine body and hash; read-only tab writes neither graph nor checkpoint')
   panel().get_by_role('tab',name='블루프린트 보기',exact=True).click();expect(panel().locator('.bp-viewport')).to_be_visible();panel().get_by_role('tab',name='논리 코드',exact=True).click();panel().locator('[data-document-name=body]').fill('未保存 한글');held=f.pending()['blueprint']
   panel().get_by_role('tab',name='네이티브 미리보기',exact=True).click();expect(view.locator('[role=status]')).to_contain_text('저장하지 않은 입력');assert not view.locator('[data-native-body]').text_content();assert f.pending()['blueprint']==held;assert t.read()['nodes']==baseline['nodes'];x.original()
   restart(1);view=panel().locator('.function-native-preview');expect(view).to_be_visible();expect(view.locator('[role=status]')).to_contain_text('저장하지 않은 입력');assert f.pending()['blueprint']==held;x.original()
   x.build('preview-no-write',10,'body\nafter\n10');f.checked('unsaved and cold-restored logical inputs refuse stale preview, preserve exact private text, legacy view and actual execution')
  else:
   editor=panel().locator('[data-native-source]');expect(editor).to_be_visible();assert panel().get_by_role('tab').all_text_contents()==['네이티브 코드'];assert editor.input_value()=='return input+3;';assert not panel().locator('.bp-layout').count();x.original()
   candidate='// 직접 네이티브 편집 α 😀\nreturn input+8;';editor.fill(candidate);held=f.pending()['blueprint'];checkpoint.chmod(0o400)
   try:
    panel().locator('[data-native-save]').click();f.idle();expect(panel().locator('.bp-status')).not_to_have_text('저장 중…',timeout=90000);assert f.pending()['blueprint']==held;assert read_native()['source']=='return input+3;';assert checkpoint.read_bytes()==before;x.original()
   finally:checkpoint.chmod(0o600)
   restart(1);editor=panel().locator('[data-native-source]');expect(editor).to_have_value(candidate);assert read_native()['source']=='return input+3;';x.original();f.checked('pure native definitions have only the native-code surface; failed checkpoint Save preserves live draft, file bytes and cold input')
   panel().locator('[data-native-save]').click();f.idle();expect(panel().locator('.bp-status')).to_have_text('저장됨',timeout=90000);assert read_native()['source']==candidate;x.original();assert not f.pending()['blueprint']
   panel().locator('[data-native-undo]').click();f.idle();expect(editor).to_have_value('return input+3;');panel().locator('[data-native-redo]').click();f.idle();expect(editor).to_have_value(candidate);x.original()
   restart(2);editor=panel().locator('[data-native-source]');expect(editor).to_have_value(candidate);assert read_native()['source']==candidate;x.original();f.checked('native Save stages one exact body and source history; shared Undo/Redo and cold checkpoint retain source without graph conversion or original writes')
   stale=read_native();stale['sources'][0]['hash']='0'*64
   f.invoke('blueprint',dict(action='saveNative',feature=feature,id=stale['id'],sources=stale['sources'],checkpointHash=stale['checkpointHash'],text='return 999;'),False);assert read_native()['source']==candidate;x.original();f.checked('native direct Save rejects forged/stale source closure without mutation')
   saved('return MissingNativeSymbol;');r=review();r.locator('#confirm').click();expect(r.locator('#confirm')).to_be_disabled(timeout=120000);f.idle();assert f.state()['review']['status']=='invalid';assert read_native()['source']=='return MissingNativeSymbol;';x.original();r.locator('[data-reject]').click();saved(candidate);f.checked('native compiler failure rejects Confirm and retains the invalid draft and all originals for explicit correction')
   r=review();r.locator('[data-reject]').click();x.original();assert read_native()['source']==candidate
   r=review();native_file=f.project/'Native.csbody';original=native_file.read_bytes();native_file.write_bytes(original+b'\n// peer change')
   r.locator('#confirm').click();f.idle();assert native_file.read_bytes()==original+b'\n// peer change';assert read_native()['source']==candidate;native_file.write_bytes(original);
   if r.is_visible():r.locator('[data-reject]').click()
   f.checked('native Review cancellation and final file CAS preserve the draft and peer edits')
   r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();assert native_file.read_text()==candidate;assert all(p.read_bytes()==raw for p,raw in x.physical.items()if p!=native_file)
   restart(3);expect(panel().locator('[data-native-source]')).to_have_value(candidate)
   # Execute this actual native function through an independently rebuilt caller.
   (f.project/'MainBody.celem').write_text('implementation '+f.n+'MainBody for '+f.n+'Main () -> int {import '+feature+' as Native (long) -> long;body common "Main.csbody";}');(f.project/'Main.csbody').write_text('return checked((int)calls.Native.Invoke(7));')
   x.build('native-confirmed',15,'');f.checked('fresh native Review/Confirm writes only the selected original body, reopens correctly and rebuilt native execution returns 15')
  f.page.screenshot(path=str(f.case/('native-'+mode+'.png')),full_page=True)
  assert not f.errors and not f.external,(f.errors,f.external)
  f.browser.close()
 print(json.dumps(dict(checks=f.checks,actualLinuxEngine=True,actualWindows=False,fullUI=False,mockupVisualCompared=False,evidence=str(f.case)),ensure_ascii=False))
except BaseException:
 (f.case/'native-failure.txt').write_text(traceback.format_exc());raise
finally:f.stop()
