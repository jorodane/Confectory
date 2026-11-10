"""Existing authored body editor with array fields and actual slot receipt lifecycle."""
import json,time
from playwright.sync_api import sync_playwright,expect
import v666_information_arrays_fixture as arrays
x=arrays.x
f,d=x.f,x.d
mode=__import__('sys').argv[3]if len(__import__('sys').argv)>3 else'normal'
assert mode in ['normal','cancel','storage','loss','late','guards']
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
  if mode=='loss':
   applies,queries,masked=set(),set(),set()
   def intercept(route):
    body=route.request.post_data_json
    if body.get('op')=='invoke'and body.get('endpoint')=='blueprint':
     action=body.get('input',{}).get('action')
     if action=='applySlots':applies.add(body['requestId'])
     elif applies and action=='settledSlots':queries.add(body['requestId'])
    response=route.fetch();payload=response.json()
    for result in payload.get('results',[]):
     if result['requestId']in applies|queries:
      rid=result['requestId'];masked.add(rid);result.clear();result.update(requestId=rid,ok=False,error={'code':'transport_lost'})
    route.fulfill(response=response,json=payload)
   f.page.route('**/api/request',intercept);f.owner().locator('[data-element-action=save]').click();deadline=time.monotonic()+120
   while time.monotonic()<deadline and not queries&masked:f.page.wait_for_timeout(20)
   assert len(applies)==1 and queries&masked and pending();f.page.unroute_all(behavior='wait');all_held=f.pending();mark=len(f.traffic);restart(2);assert f.pending()==all_held;f.owner().locator('[data-element-action=save]').click();deadline=time.monotonic()+90
   while pending()and time.monotonic()<deadline:f.page.wait_for_timeout(20)
   assert not pending();assert not any(r.get('invoke',{}).get('input',{}).get('action')=='applySlots'for r in f.traffic[mark:]);x.verify(checkpoint);x.unchanged();f.checked('lost array-body apply and receipt responses cold-restore exact input/source proofs and settle without a duplicate apply');f.browser.close();raise SystemExit(0)
  late_name='Save 응답 중 새 이름';injected=[]
  if mode=='late':
   applies=set()
   def intercept(route):
    body=route.request.post_data_json
    if body.get('op')=='invoke'and body.get('endpoint')=='blueprint'and body.get('input',{}).get('action')=='applySlots':applies.add(body['requestId'])
    response=route.fetch();payload=response.json()
    if not injected and any(result.get('ok')and result['requestId']in applies for result in payload.get('results',[])):
     f.owner().locator('[data-inline-method="'+x.fn+'"] [data-inline-name]').fill(late_name);injected.append(True)
    route.fulfill(response=response,json=payload)
   f.page.route('**/api/request',intercept)
  save();deadline=time.monotonic()+30
  if mode=='late':
   f.page.unroute_all(behavior='wait');assert injected
   while time.monotonic()<deadline and(not pending()or pending()[0][1].get('kind')!='function-edit'):f.page.wait_for_timeout(20)
   assert len(pending())==1 and pending()[0][1]['name']==late_name and pending()[0][1]['signature']==x.signature;x.verify(checkpoint);restart(2);assert pending()[0][1]['name']==late_name;save();f.checked('a late name survives array-body receipt rebasing and restart; explicit follow-up Save retains the accepted C# and array contract')
  while pending()and time.monotonic()<deadline:f.page.wait_for_timeout(20)
  assert not pending();ids,receipt=x.verify(checkpoint);x.unchanged();restart(3 if mode=='late' else 2);assert x.verify(checkpoint)==(ids,receipt);assert not pending();
  if mode=='late':expect(f.owner().locator('[data-inline-method="'+x.fn+'"] [data-inline-name]')).to_have_value(late_name)
  f.checked('one existing Save stores the typed body and exact schema read proof atomically, then restores both after a cold restart')
  # With no new input the existing UI prevents a duplicate Save.
  saved=checkpoint.read_bytes();expect(f.owner().locator('[data-element-action=save]')).to_be_disabled();assert checkpoint.read_bytes()==saved and not pending()
  if mode=='guards':
   f.pending();f.page.close();f.stop()
   for i,kind in enumerate(['missing','extra','proof'],4):
    document=json.loads(saved);row=next(row for row in document['changes']if'slotSaveReceipt'in row);proof=row['slotSaveReceipt']
    if kind=='missing':del proof['readGuards']['registered/Leaf.celem']
    elif kind=='extra':proof['readGuards']['unobserved.txt']={'path':'unobserved.txt','hash':'0'*64}
    else:proof['nativeTypeReads'][0]['hash']='0'*64
    checkpoint.write_text(json.dumps(document,ensure_ascii=False));tampered=checkpoint.read_bytes();f.start(i);f.invoke('reviewGroup',dict(ids=ids,target='portable'),False);assert checkpoint.read_bytes()==tampered;x.unchanged();f.stop()
   checkpoint.write_bytes(saved);f.start(7);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700});f.idle();assert x.verify(checkpoint)==(ids,receipt)
   f.checked('cold Review rejects a missing registered guard, an unobserved extra guard and a tampered native type read proof while retaining the complete saved candidate and originals')
   f.invoke('reviewGroup',dict(ids=ids,target='portable'));review=f.state()['review'];assert review['status']=='ready';peer=f.project/'registered/Leaf.celem';original_peer=peer.read_bytes();peer.write_bytes(original_peer+b'\n// peer\n');before_confirm=checkpoint.read_bytes();outcome=f.invoke('confirmGroup',dict(ids=ids,token=review['token']))['result']['result'];assert outcome['sourceConfirmed']is False,outcome;assert peer.read_bytes()==original_peer+b'\n// peer\n'and checkpoint.read_bytes()==before_confirm;x.unchanged({'registered/Leaf.celem'});peer.write_bytes(original_peer);f.checked('a registered native usage source change after Review rejects Confirm, preserving peer bytes and the exact saved candidate')
  f.invoke('reviewGroup',dict(ids=ids,target='portable'));review=f.state()['review'];assert review['status']=='ready',review;f.invoke('confirmGroup',dict(ids=ids,token=review['token']));assert(f.project/x.body_path).read_bytes()==x.selected.encode();x.unchanged({x.body_path,x.function_path});x.execute();f.checked('the no-input duplicate Save stays disabled and explicit compiler Review/Confirm executes the struct value input and result31')
  assert not f.errors and not f.external,(f.errors,f.external);f.browser.close()
except Exception:
 failure={'traffic':f.traffic[-50:]}
 try:failure['state']=f.state()
 except Exception as error:failure['stateError']=str(error)
 try:failure['pending']=pending()
 except Exception as error:failure['pendingError']=str(error)
 (f.case/'failure-state.json').write_text(json.dumps(failure,ensure_ascii=False,indent=2))
 try:f.page.screenshot(path=str(f.case/'failure.png'))
 except Exception:pass
 raise
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
