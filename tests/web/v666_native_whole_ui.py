"""Explicit whole-body node ABI and source plans through the existing editor."""
import json,time,sys
from playwright.sync_api import sync_playwright,expect
import v666_native_whole_fixture as c
e,x=c.e,c.x
f,d=x.f,x.d;mode=sys.argv[3]if len(sys.argv)>3 else'normal'
def pending():return d.pending()
def row():return f.owner().locator('[data-inline-method]').last
def detail():row().locator('.function-node-heading').press('Enter');p=f.page.locator('.function-detail-popover');expect(p).to_be_visible();assert abs(p.bounding_box()['width']-420)<1;return p
def pick(field,id,multi=False):
 field.locator('[data-signature-type]').click();p=f.page.get_by_role('dialog',name='속성 타입 선택',exact=True);expect(p).to_be_visible();p.get_by_label('여러 개 허용',exact=True).set_checked(multi);p.locator('[type=search]').fill(id.split('::')[-1]);p.locator('[data-native-type]').filter(has_text=id).click()
def save(ok=True):
 mark=len(f.traffic);f.owner().locator('[data-element-action=save]').click();deadline=time.monotonic()+90
 while time.monotonic()<deadline:
  ids={r['invoke']['requestId']for r in f.traffic[mark:]if r.get('invoke',{}).get('endpoint')=='blueprint'and r['invoke']['input'].get('action')=='applySlots'};preparation={r['invoke']['requestId']for r in f.traffic[mark:]if r.get('invoke',{}).get('endpoint')=='blueprint'and r['invoke']['input'].get('action')=='readOwnerEdits'};rows=[r['result']for r in f.traffic[mark:]if(r.get('result',{}).get('requestId')in ids or not ok and r.get('result',{}).get('requestId')in preparation and r['result'].get('ok')is False)and r['result'].get('error',{}).get('code')!='stale_revision']
  if rows:assert bool(rows[-1]['ok'])==ok,rows[-1];f.idle();return
  f.page.wait_for_timeout(25)
 raise AssertionError(dict(traffic=f.traffic[mark:],pending=pending()))
def restart(i):
 f.pending();f.page.unroute_all(behavior='wait');f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size(dict(width=2300,height=1700));expect(f.owner().locator('.object-title-name')).to_have_text('FreeInfo');f.idle()
try:
 f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
 with sync_playwright()as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size(dict(width=2300,height=1700));d.open_info();assert abs(f.owner().bounding_box()['width']-460)<1
  row().locator('[data-inline-name]').fill('정보 값 계약');held=pending();p=detail();field=p.locator('[data-signature-kind=inputs] .feature-io-row').first;field.locator('[data-signature-type]').click();picker=f.page.get_by_role('dialog',name='속성 타입 선택',exact=True);expect(picker.locator('[data-native-type]').filter(has_text='LegacyMood')).to_be_disabled();expect(picker.locator('[data-native-type]').filter(has_text='Hidden.Types::')).to_have_count(0);f.page.keyboard.press('Escape');p.locator('[data-detail-cancel]').click();assert pending()==held
  p=detail();pick(p.locator('[data-signature-kind=inputs] .feature-io-row').first,f.n+'Payload');pick(p.locator('[data-signature-id=return]'),f.n+'Payload');f.page.screenshot(path=str(f.case/'native-whole-detail.png'));p.locator('button[type=submit]').click();expect(p).to_have_count(0)
  held=pending();assert len(held)==1;value=held[0][1];signature=value['signature'];fn=value['id'];assert signature==c.new and len(value['nativeTypes'])==2 and value['kind']=='native-function-edit' and fn==e.fn
  texts={c.code_id:c.code_selected,c.body_id:c.selected}
  def source_plan(id,text,cancel=False,before_text=None):
   row().locator('[data-function-write-direct],[data-function-edit]').first.click();chooser=f.page.get_by_role('dialog',name='구현 선택',exact=True);expect(chooser).to_be_visible();chooser.locator('[data-information-body="'+id+'"]').click();dialog=f.page.locator('.bp-script-dialog');expect(dialog).to_be_visible();source=dialog.locator('[data-code-source]');old=(before_text if before_text is not None else c.original if id==c.body_id else c.code_original).replace('\r\n','\n').strip();current=source.input_value();assert old in current,(id,current);source.evaluate('(el,text)=>{el.focus();const i=el.value.indexOf(text);el.setSelectionRange(i,i+text.length)}',old);f.page.keyboard.insert_text(text.replace('\r\n','\n').strip());assert text.replace('\r\n','\n').strip()in source.input_value();dialog.locator('[data-code-cancel]'if cancel else'[data-code-save]').click();expect(dialog).to_have_count(0);f.idle()
  source_plan(c.code_id,texts[c.code_id]+'// cancelled draft',True);assert pending()==held
  for id,text in texts.items():source_plan(id,text)
  held=pending();assert set(held[0][1]['mapping']['bodies'])=={c.body_id,c.code_id};assert all(plan['text'].strip()==texts[id].replace('\r\n','\n').strip()for id,plan in held[0][1]['mapping']['bodies'].items());f.checked('original C# chooser retains cancelled text boundaries and stores explicit C# caller adaptation, whole-body signature/body and original return writer without changing any source')
  f.owner().locator('[data-own-functions-toggle]').press('Control+z');assert pending()!=held;f.owner().locator('[data-own-functions-toggle]').press('Control+y');assert pending()==held;restart(1);assert pending()==held;assert checkpoint.read_bytes()==before;x.unchanged();f.checked('original 460px card and detail search select Blueprint entry and return struct types with cancel, disabled boundaries, Undo/Redo and exact cold-restored source proofs')
  if mode=='cancel':
   f.owner().locator('[data-element-action=discard]').click();f.idle();assert not pending();restart(2);assert not pending()and checkpoint.read_bytes()==before;x.unchanged();f.checked('explicit discard and restart remove only the unsaved signature transition');f.browser.close();raise SystemExit(0)
  if mode=='conflict':
   original=e.path.read_bytes();e.path.write_bytes(original+b'\n// peer contract observation\n')
   try:
    mark=len(f.traffic);save(False);assert pending()==held and checkpoint.read_bytes()==before;assert not any(r.get('invoke',{}).get('input',{}).get('action')=='applySlots'for r in f.traffic[mark:])
   finally:e.path.write_bytes(original)
   x.unchanged();restart(2);assert pending()==held;f.checked('changed physical function source rejects UI Save without dropping the selected types; exact restoration and cold retry retain the original baseline')
  if mode=='storage':
   checkpoint.chmod(0o400)
   try:save(False);assert pending()==held and checkpoint.read_bytes()==before;x.unchanged()
   finally:checkpoint.chmod(0o600)
   f.checked('failed checkpoint storage retains exact types, explicit body plans and source proofs for retry')
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
   f.page.route('**/api/request',intercept);f.owner().locator('[data-element-action=save]').click();deadline=time.monotonic()+90
   while time.monotonic()<deadline and not queries&masked:f.page.wait_for_timeout(20)
   assert len(applies)==1 and queries&masked and pending();f.page.unroute_all(behavior='wait');all_held=f.pending();mark=len(f.traffic);restart(2);assert f.pending()==all_held;f.owner().locator('[data-element-action=save]').click();deadline=time.monotonic()+60
   while pending()and time.monotonic()<deadline:f.page.wait_for_timeout(20)
   assert not pending();assert not any(r.get('invoke',{}).get('input',{}).get('action')=='applySlots'for r in f.traffic[mark:]);c.verify(checkpoint,signature);x.unchanged();f.checked('lost apply and receipt responses cold-restore exact type proofs and recover the settled receipt without duplicate transition');f.browser.close();raise SystemExit(0)
  late_name='응답 대기 중 새 이름';injected=[]
  if mode=='late':
   applies=set()
   def intercept(route):
    body=route.request.post_data_json
    if body.get('op')=='invoke'and body.get('endpoint')=='blueprint'and body.get('input',{}).get('action')=='applySlots':applies.add(body['requestId'])
    response=route.fetch();payload=response.json()
    if not injected and any(r.get('ok')and r['requestId']in applies for r in payload.get('results',[])):
     row().locator('[data-inline-name]').fill(late_name);injected.append(True)
    route.fulfill(response=response,json=payload)
   f.page.route('**/api/request',intercept)
  save();deadline=time.monotonic()+30
  if mode=='late':
   f.page.unroute_all(behavior='wait');assert injected
   while time.monotonic()<deadline and(not pending()or pending()[0][1]['kind']!='function-edit'):f.page.wait_for_timeout(20)
   assert len(pending())==1 and pending()[0][1]['name']==late_name and pending()[0][1]['signature']==signature;ids=c.verify(checkpoint,signature);restart(2);assert pending()[0][1]['name']==late_name;save();f.checked('late name input survives native-transition receipt rebasing and cold restart; an explicit second Save retains the accepted nominal contract')
  deadline=time.monotonic()+30
  while pending()and time.monotonic()<deadline:f.page.wait_for_timeout(20)
  assert not pending();ids=c.verify(checkpoint,signature);x.unchanged();restart(2);assert c.verify(checkpoint,signature)==ids and not pending();expect(f.owner().locator('[data-element-action=save]')).to_be_disabled();assert not any('Confectory.Information.'in e.get_attribute('data-function-pin-type')for e in row().locator('[data-function-pin-unit]').all());f.checked('one typed Save atomically stores owner/function/implementation/caller sources and complete guards, then cold-restores with duplicate Save disabled')
  f.invoke('reviewGroup',dict(ids=ids,target='portable'));review=f.state()['review'];assert review['status']=='ready',review;f.invoke('confirmGroup',dict(ids=ids,token=review['token']));assert signature['return']in e.path.read_text();assert(f.project/c.native_path).read_bytes()==c.code_original.encode();x.unchanged(c.changes_allowed);c.execute(31,'ui-confirmed');f.checked('only explicit compiler Review/Confirm publishes the nominal signature and selected C# plans; unrelated originals survive and actual execution is31')
  if mode=='normal'and'view'not in sys.argv:
   restart(3);held_sources={p:(f.project/p).read_bytes()for p in c.changes_allowed};row().locator('[data-function-write-direct],[data-function-edit]').first.click();chooser=f.page.get_by_role('dialog',name='구현 선택',exact=True);chooser.locator('[data-information-body="'+c.code_id+'"]').click();dialog=f.page.locator('.bp-script-dialog');expect(dialog).to_be_visible();assert c.code_selected.replace('\r\n','\n').strip()in dialog.locator('[data-code-source]').input_value();f.page.screenshot(path=str(f.case/'accepted-native-whole.png'));dialog.locator('[data-code-cancel]').click();assert all((f.project/p).read_bytes()==raw for p,raw in held_sources.items());f.checked('the existing whole C# editor reopens its accepted struct signature/body while the archived original C# file and every physical source remain unchanged')
  assert not f.errors and not f.external,(f.errors,f.external);f.browser.close()
except Exception:
 try:(f.case/'failure-state.json').write_text(json.dumps(dict(state=f.state(),traffic=f.traffic[-40:],pending=pending()),ensure_ascii=False,indent=2));f.page.screenshot(path=str(f.case/'failure.png'))
 except Exception:pass
 raise
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
