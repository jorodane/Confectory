"""Existing authored function detail picker through a real editor engine."""
import json,time,sys,shutil
from playwright.sync_api import sync_playwright,expect
import v666_native_type_group_fixture as x
c,e=x.c,x.c.e
f,d=x.f,x.c.x.d;mode=sys.argv[3]if len(sys.argv)>3 else'normal'
def pending():return d.pending()
fn=x.second
def row():return f.owner().locator('[data-inline-method="'+fn+'"]')
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
  planned=x.request()['changes']
  for fn,plan in zip(x.functions,planned):
   row().locator('[data-inline-name]').fill(plan['name']);held=pending();p=detail();field=p.locator('[data-signature-kind=inputs] .feature-io-row').first;pick(field,f.n+'Payload');p.locator('[data-detail-cancel]').click();assert pending()==held
   p=detail();field=p.locator('[data-signature-kind=inputs] .feature-io-row').first;pick(field,f.n+'Payload');p.locator('button[type=submit]').click();expect(p).to_have_count(0);held=pending()
   def source_plan(id,text,cancel=False):
    row().locator('[data-function-write-direct],[data-function-edit]').first.click();chooser=f.page.locator('[data-information-body="'+id+'"]');expect(chooser).to_be_visible();chooser.click();dialog=f.page.locator('.bp-script-dialog');expect(dialog).to_be_visible();source=dialog.locator('[data-code-source]');old=x.sources[id].replace('\r\n','\n').strip();assert old in source.input_value();source.evaluate('(el,text)=>{el.focus();const i=el.value.indexOf(text);el.setSelectionRange(i,i+text.length)}',old);f.page.keyboard.insert_text(text.replace('\r\n','\n').strip());dialog.locator('[data-code-cancel]'if cancel else'[data-code-save]').click();expect(dialog).to_have_count(0);f.idle()
   body=plan['mapping']['bodies'];source_plan(x.bodies[fn],body[x.bodies[fn]]['text']+'// cancelled text',True);assert pending()==held
   for id,source in body.items():source_plan(id,source['text'])
  held=pending();assert len(held)==2 and {v['id']for _,v in held}==set(x.functions);assert all(len(v['nativeTypes'])==2 and len(v['mapping']['bodies'])==2 for _,v in held);f.checked('two original type pickers and own C# choosers retain explicit nominal selections and four authored body plans without changing source')
  signature=planned[-1]['signature'];f.owner().locator('[data-own-functions-toggle]').press('Control+z');assert pending()!=held;f.owner().locator('[data-own-functions-toggle]').press('Control+y');assert pending()==held;restart(1);assert pending()==held and checkpoint.read_bytes()==before;x.unchanged();f.checked('original card layout, cancel, Undo/Redo and cold restart preserve both nominal scopes and exact source plans')
  if mode=='prior-ui':
   saved=checkpoint.read_bytes();held=pending();save(False);assert pending()==held and checkpoint.read_bytes()==saved;x.unchanged();f.checked('prior intact UI rejects the two-scope nominal Save and preserves both source plans, checkpoint and originals');f.browser.close();raise SystemExit(0)
  if mode=='projects':
   first=f.state()['listingId'];f.page.close();f.stop();other=f.case/'other project';shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory'));f.env['CONFECTORY_WEB_PROJECT']=str(other/'project.cproj');f.start(2);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});second=f.state()['listingId'];peer_checkpoint=next(other.glob('.confectory/edit-workspaces/*/draft.json'));peer_saved=peer_checkpoint.read_bytes();f.page=f.setup();f.page.set_viewport_size(dict(width=2300,height=1700))
   def enter(listing):
    f.page.locator('.brand').click();expect(f.page.locator('.home-grid')).to_be_visible();f.page.locator('[data-enter="'+listing+'"]').click();expect(f.page.locator('.work-body')).to_be_visible();f.idle()
   enter(first);assert pending()==held;p=detail();p.locator('form').evaluate('el=>globalThis.staleNativeTypeForm=el');enter(second);d.open_info();assert not pending();f.page.evaluate("()=>staleNativeTypeForm.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}))");assert not pending()and checkpoint.read_bytes()==before and peer_checkpoint.read_bytes()==peer_saved;enter(first);assert pending()==held;x.unchanged();f.checked('same-namespace project roundtrip preserves both nominal inputs in A and refuses stale form submission into B');f.browser.close();raise SystemExit(0)
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
   assert not pending();assert not any(r.get('invoke',{}).get('input',{}).get('action')=='applySlots'for r in f.traffic[mark:]);x.verify(checkpoint);x.unchanged();f.checked('lost apply and receipt responses cold-restore exact type proofs and recover the settled receipt without duplicate transition');f.browser.close();raise SystemExit(0)
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
   assert len(pending())==1 and pending()[0][1]['name']==late_name and pending()[0][1]['signature']==signature;ids=x.verify(checkpoint);restart(2);assert pending()[0][1]['name']==late_name;save();f.checked('late name input survives native-transition receipt rebasing and cold restart; an explicit second Save retains the accepted nominal contract')
  deadline=time.monotonic()+30
  while pending()and time.monotonic()<deadline:f.page.wait_for_timeout(20)
  assert not pending();ids=x.verify(checkpoint);x.unchanged();restart(2);assert x.verify(checkpoint)==ids and not pending();expect(f.owner().locator('[data-element-action=save]')).to_be_disabled();assert not any('Confectory.Information.'in e.get_attribute('data-function-pin-type')for e in row().locator('[data-function-pin-unit]').all());f.checked('one typed Save atomically stores owner/function/implementation/caller sources and complete guards, then cold-restores with duplicate Save disabled')
  f.invoke('reviewGroup',dict(ids=ids,target='portable'));review=f.state()['review'];assert review['status']=='ready',review;out=f.invoke('confirmGroup',dict(ids=ids,token=review['token']))['result']['result'];assert out['sourceConfirmed'],(out,f.state().get('logs'));x.verify_live();f.checked('only explicit Review/Confirm publishes both nominal signatures and four selected C# bodies; actual execution is73')
  assert not f.errors and not f.external,(f.errors,f.external);f.browser.close()
except Exception:
 try:(f.case/'failure-state.json').write_text(json.dumps(dict(state=f.state(),traffic=f.traffic[-40:],pending=pending()),ensure_ascii=False,indent=2));f.page.screenshot(path=str(f.case/'failure.png'))
 except Exception:pass
 raise
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
