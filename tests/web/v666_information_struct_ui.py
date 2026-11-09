"""Existing native body editor with a real nominal information value contract."""
import json,time
from playwright.sync_api import sync_playwright,expect
import v666_information_struct_fixture as x
f,d=x.f,x.d
mode=__import__('sys').argv[3]if len(__import__('sys').argv)>3 else'normal'
def pending():return d.pending()
def body_dialog():
 f.owner().locator('[data-inline-method="'+x.fn+'"] [data-function-edit], [data-inline-method="'+x.fn+'"] [data-function-write-direct]').click()
 f.page.wait_for_function('()=>document.querySelector("[data-information-body]")||document.querySelector("[data-code-source]")')
 chooser=f.page.locator('[data-information-body="'+x.body_id+'"]')
 if chooser.count():chooser.click()
 dialog=f.page.locator('[role=dialog]:has([data-code-source])');expect(dialog).to_be_visible();return dialog
def edit(dialog,text):
 field=dialog.locator('[data-code-source]');before=x.original.removesuffix('\r\n');assert before in field.input_value()
 # The DOM has LF offsets; leave the original trailing CRLF outside the edit.
 field.evaluate('(el,text)=>{el.focus();const i=el.value.indexOf(text);if(i<0)throw Error("Original body absent");el.setSelectionRange(i,i+text.length)}',before);f.page.keyboard.insert_text(text.removesuffix('\r\n'));f.idle()
def save(ok=True):
 mark=len(f.traffic);f.owner().locator('[data-element-action=save]').click();deadline=time.monotonic()+90
 while time.monotonic()<deadline:
  ids={r['invoke']['requestId']for r in f.traffic[mark:]if r.get('invoke',{}).get('endpoint')=='blueprint'and r['invoke']['input'].get('action')=='applySlots'}
  rows=[r['result']for r in f.traffic[mark:]if r.get('result',{}).get('requestId')in ids and r['result'].get('error',{}).get('code')!='stale_revision']
  if rows:assert bool(rows[-1]['ok'])==ok,rows[-1];f.idle();return
  f.page.wait_for_timeout(20)
 raise AssertionError(dict(reason='no observed applySlots response',traffic=f.traffic[mark:],pending=pending()))
def restart(i):
 f.pending();f.page.unroute_all(behavior='wait');f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700});expect(f.owner().locator('.object-title-name')).to_have_text('FreeInfo');f.idle()
try:
 f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
 with sync_playwright()as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700});d.open_info()
  assert abs(f.owner().bounding_box()['width']-460)<1
  dialog=body_dialog();edit(dialog,x.selected);dialog.locator('[data-code-cancel]').click();assert not pending()and checkpoint.read_bytes()==before;x.unchanged()
  dialog=body_dialog();edit(dialog,x.selected);f.page.screenshot(path=str(f.case/'typed-body.png'));dialog.locator('[data-code-save]').click();expect(dialog).to_have_count(0);held=pending();assert len(held)==1
  f.owner().locator('[data-own-functions-toggle]').press('Control+z');assert not pending();f.owner().locator('[data-own-functions-toggle]').press('Control+y');assert pending()==held
  restart(1);assert pending()==held and checkpoint.read_bytes()==before;x.unchanged();f.checked('the authored 460px native body editor keeps the struct contract, cancel, Undo/Redo and unsaved cold restoration without rewriting any source')
  if mode=='cancel':
   f.owner().locator('[data-element-action=discard]').click();f.idle();assert not pending()and checkpoint.read_bytes()==before;restart(2);assert not pending();x.unchanged();f.checked('explicit discard and cold restart remove only the selected typed-body input');f.browser.close();raise SystemExit(0)
  if mode=='storage':
   checkpoint.chmod(0o400)
   try:save(False);assert pending()==held and checkpoint.read_bytes()==before;x.unchanged()
   finally:checkpoint.chmod(0o600)
   f.checked('failed checkpoint storage retains the exact typed body input and original C# and information definition')
  save();deadline=time.monotonic()+30
  while pending()and time.monotonic()<deadline:f.page.wait_for_timeout(20)
  assert not pending();ids,receipt=x.verify(checkpoint);x.unchanged();restart(2);assert x.verify(checkpoint)==(ids,receipt);assert not pending();f.checked('one existing Save stores the typed body and exact schema read proof atomically, then restores both after a cold restart')
  # With no new input the existing UI prevents a duplicate Save.
  saved=checkpoint.read_bytes();expect(f.owner().locator('[data-element-action=save]')).to_be_disabled();assert checkpoint.read_bytes()==saved and not pending()
  f.invoke('reviewGroup',dict(ids=ids,target='portable'));review=f.state()['review'];assert review['status']=='ready',review;f.invoke('confirmGroup',dict(ids=ids,token=review['token']));assert(f.project/x.body_path).read_bytes()==x.selected.encode();x.unchanged({x.body_path,x.function_path});x.execute();f.checked('the no-input duplicate Save stays disabled and explicit compiler Review/Confirm executes the struct value input and result31')
  assert not f.errors and not f.external,(f.errors,f.external);f.browser.close()
except Exception:
 try:(f.case/'failure-state.json').write_text(json.dumps(dict(state=f.state(),traffic=f.traffic[-50:],pending=pending()),ensure_ascii=False,indent=2));f.page.screenshot(path=str(f.case/'failure.png'))
 except Exception:pass
 raise
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
