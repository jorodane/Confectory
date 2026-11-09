"""Owned native bodies retain an actual unchanged C# caller and its native aliases."""
import copy,hashlib,json,subprocess
import v666_body_imports_fixture as _prior
for _key in dir(_prior):
 if not _key.startswith('_'):globals()[_key]=getattr(_prior,_key)
retained=f.n+'NativeBodyCaller';retained_header='NativeBodyCallerBody.celem';retained_file='native-caller.csbody'
for name,kind,text in [('NativeBodyCaller','function','function '+retained+' (long amount,long count) -> long {provide '+retained+' with '+retained+'Body;}'),('NativeBodyCallerBody','implementation','implementation '+retained+'Body for '+retained+' (long left,long right) -> long {import '+functions[0]+' as First (long,long) -> long;import '+functions[1]+' as Second (long,long) -> long;body common "'+retained_file+'";}')]:
 (f.project/(name+'.celem')).write_bytes(text.encode());f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element '+name+' '+kind+' "'+name+'.celem";registry Confectory.Build.DotNet',1))
(f.project/retained_file).write_bytes('// 保持 · 호출자 원문 9223372036854775806 😀\r\nlong first=calls.First.Invoke(left,right);\r\nreturn calls.Second.Invoke(first,right);\r\n'.encode())
(f.project/'MainBody.celem').write_text('implementation '+f.n+'MainBody for '+f.n+'Main () -> int {import '+retained+' as NativeCaller (long,long) -> long;body common "Main.csbody";}')
(f.project/'Main.csbody').write_text('int result=checked((int)calls.NativeCaller.Invoke(30,5));global::System.Console.WriteLine(result);return result;')
snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts};_prior.snapshot=snapshot;_prior._base.snapshot=snapshot
original_result=40 if mode=='leaf'else 46;edited_result=20 if mode=='leaf'else 26
_base_verify_rows=_prior.verify_rows

def verify_rows(rows):
 _base_verify_rows(rows)
 for id,path in [(retained,'NativeBodyCaller.celem'),(retained+'Body',retained_header),(retained+'Body/body:common',retained_file)]:
  assert (rows[id]['draft'] if id in rows else (f.project/path).read_bytes().decode())==snapshot[path].decode(),id

def verify_live():
 verify_rows({});execute(edited_result,'retained-native-caller');f.checked('actual unchanged native caller keeps aliases/CRLF/C# bytes and executes edited callees: result'+str(edited_result))

# Shared checkpointer and browser driver call these hooks through their original module.
_prior._base.verify_rows=verify_rows

def after_contract(index):
 from playwright.sync_api import expect
 import time
 selector='[data-inline-method="'+functions[index]+'"] [data-function-edit], [data-inline-method="'+functions[index]+'"] [data-function-write-direct]'
 held=d.pending()
 def open_editor():
  f.owner().locator(selector).click();chooser=f.page.get_by_role('dialog',name='구현 선택',exact=True);expect(chooser).to_be_visible();expect(chooser.locator('[data-information-body="'+retained+'Body/body:common"]')).to_be_visible();chooser.locator('[data-information-body="'+functions[index]+'Body/body:common"]').click();expect(chooser).to_have_count(0)
  dialog=f.page.locator('[role=dialog]:has([data-code-source])');expect(dialog).to_be_visible();return dialog
 def fill(dialog):
  field=dialog.locator('[data-code-source]');assert sources[functions[index]]in field.input_value();field.evaluate('(el,text)=>{el.focus();const i=el.value.indexOf(text);if(i<0)throw Error("Original body absent");el.setSelectionRange(i,i+text.length);}',sources[functions[index]]);f.page.keyboard.insert_text(selected[functions[index]]);f.idle()
 dialog=open_editor();fill(dialog);dialog.locator('[data-code-cancel]').click();assert d.pending()==held
 dialog=open_editor();fill(dialog);f.page.screenshot(path=str(f.case/('native-caller-body-'+str(index)+'.png')));dialog.locator('[data-code-save]').click();expect(dialog).to_have_count(0);f.idle();saved=d.pending();f.owner().locator('[data-own-functions-toggle]').press('Control+z');assert d.pending()==held;f.owner().locator('[data-own-functions-toggle]').press('Control+y');assert d.pending()==saved
 if index==1 and mode=='reproduce-ui':
  checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));baseline=checkpoint.read_bytes();mark=len(f.traffic);f.owner().locator('[data-element-action=save]').click();deadline=time.monotonic()+60
  while time.monotonic()<deadline:
   ids={row['invoke']['requestId']for row in f.traffic[mark:]if row.get('invoke',{}).get('endpoint')=='blueprint'and row['invoke']['input'].get('action')=='applySlots'};replies=[row['result']for row in f.traffic[mark:]if row.get('result',{}).get('requestId')in ids]
   if replies:assert replies[-1]['ok']is False;break
   f.page.wait_for_timeout(20)
  else:raise AssertionError('No observed applySlots result')
  assert d.pending()==saved and checkpoint.read_bytes()==baseline;unchanged();f.checked('published authored chooser/editor preserves native caller but rejects grouped Save, retaining both body inputs/checkpoint');f.browser.close();raise SystemExit(0)
