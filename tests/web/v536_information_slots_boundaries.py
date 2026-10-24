"""Schema-owner copy/default Save boundaries through the real v536 renderer.
All source changes, storage faults and transport loss use an isolated fixture.
"""
import json,shutil,sys,time
from playwright.sync_api import sync_playwright,expect
import v536_field_definitions_ui as d
f=d.f;owner=d.owner;mode=sys.argv[3]
info=f.project/'FreeInfo.celem'
info.write_text(info.read_text().replace('FreeInfo {','FreeInfo {module '+f.n+'Rules;',1))
f.original={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file()}
peer_inputs=None
if mode=='projects':
 b_root=f.case/'other root'/'owned project';shutil.copytree(f.project,b_root);original_b={str(p.relative_to(b_root)):p.read_bytes() for p in b_root.rglob('*') if p.is_file()}
def slot():return f.owner().locator('[data-module-method="'+f.n+'Slot"]')
def verify_peer():
 if peer_inputs is None:return
 w=f.page.locator('.window[data-key=editor-1]');expect(w.locator('.object-title-name')).to_have_text('RefTarget');expect(w.locator('.object-title-description')).to_have_value('다른 창 입력 보존');assert [(k,v) for k,v in f.pending()['schema'] if '|'+f.n+'RefTarget|view:1|element|' in k]==peer_inputs
def open_peer():
 global peer_inputs
 f.page.locator('#workspace').click(button='right',position={'x':80,'y':100});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]');b.locator('[data-tab=concept]').click();b.locator('[data-browser-control="object-query"]').fill('RefTarget');b.locator('[data-browser-control="object-search"]').click();row=b.locator('[data-object="'+f.n+'RefTarget"]');expect(row).to_have_attribute('aria-disabled','false');row.click(button='right');f.page.locator('.context-menu').get_by_role('button',name='새 창으로 열기',exact=True).click();w=f.page.locator('.window[data-key=editor-1]');expect(w.locator('.object-title-name')).to_have_text('RefTarget');b.locator('[data-close]').first.click();head=w.locator('.object-title-name').bounding_box();box=w.bounding_box();f.page.mouse.move(head['x']+5,head['y']+5);f.page.mouse.down();f.page.mouse.move(1700+head['x']-box['x']+5,120+head['y']-box['y']+5,steps=10);f.page.mouse.up();w.locator('.object-title-description').fill('다른 창 입력 보존');w.get_by_label('Count 기본값',exact=True).fill('9223372036854775802');peer_inputs=[(k,v) for k,v in f.pending()['schema'] if '|'+f.n+'RefTarget|view:1|element|' in k];assert len(peer_inputs)==2;d.open_info();verify_peer()
def pending_owner():
 rows=f.pending();return {key:[(k,v) for k,v in rows[key] if '|'+owner+'|' in k or v.get('copy',{}).get('owner')==owner or v.get('owner')==owner] for key in ['schema','blueprint']}
def retained(held):
 now=pending_owner()
 assert all(dict(now[group]).get(key)==value for group,rows in held.items() for key,value in rows),(held,now)
 return now
def ready():
 expect(f.owner().locator('.object-title-name')).to_have_text('FreeInfo');expect(slot()).to_be_visible();verify_peer();f.idle()
def restart(i):
 f.pending();f.page.unroute_all(behavior='wait');f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1600});ready();f.originals()
def saved(implementation):
 deadline=time.monotonic()+90
 while time.monotonic()<deadline:
  pending=pending_owner()
  if not any(pending.values()):
   f.idle();f.invoke('schema',{'id':owner});schema=f.state().get('schema') or {}
   if schema.get('id')==owner and any(row['function']==f.n+'Slot' and row['implementation']==implementation and row['contract']['status']=='valid' for row in schema.get('providers',[])):
    verify_peer();return
  f.page.wait_for_timeout(30)
 raise AssertionError((f.owner().locator('[data-element-error]').all_text_contents(),pending))
def seed():
 slot().locator('[data-function-write-direct]').click();picker=f.page.locator('.feature-import-dialog');expect(picker).to_be_visible();picker.locator('[data-copy-source="'+f.n+'SlotBody"][data-copy-target=common]').click();expect(f.author().locator('[data-bp-node=body]')).to_be_visible();f.edit_region(f.author().locator('[data-bp-node=body] [data-internal-code]'),f.body,'slotCount=amount+7;slotReady=true;return amount+9;');f.close_author();d.field(['Power']).locator('[data-property-value]').fill('9223372036854775804');copy=next(v['copy'] for _,v in f.pending()['blueprint'] if v.get('kind')=='copy-selection' and v.get('copy',{}).get('owner')==owner);return copy['implementation']
try:
 f.start(0);f.invoke('select',{'id':owner});f.invoke('saveDraft',{})
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1600});d.open_info();open_peer();implementation=seed();held=pending_owner();checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();f.originals();verify_peer()
  if mode=='projects':
   a=f.state();alist=a['listingId'];peer_a=peer_inputs;checkpoint_a=checkpoint;before_a=before;implementation_a=implementation;held_a=held;f.pending();f.page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(b_root/'project.cproj');f.start(1);f.invoke('select',{'id':owner});f.invoke('saveDraft',{});f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1600});d.open_info();open_peer();peer=f.page.locator('.window[data-key=editor-1]');peer.get_by_label('Count 기본값',exact=True).fill('9223372036854775803');peer_inputs=[(k,v) for k,v in f.pending()['schema'] if '|'+f.n+'RefTarget|view:1|element|' in k];peer_b=peer_inputs;implementation_b=seed();f.owner().locator('[data-element-action=save]').click();saved(implementation_b);b=f.state();assert a['projectId']!=b['projectId'] and implementation_a!=implementation_b;blist=b['listingId'];checkpoint_b=next(b_root.glob('.confectory/edit-workspaces/*/draft.json'));saved_b=checkpoint_b.read_bytes();f.checked('같은 이름/요소 ID의 다른 실제 프로젝트는 서로 다른 copy와 exact64·peer 입력을 독립적으로 저장한다')
   def enter(listing,peer):
    global peer_inputs
    peer_inputs=peer;f.page.locator('.brand').click();expect(f.page.locator('.home-grid')).to_be_visible();f.page.locator('[data-enter="'+listing+'"]').click();expect(f.page.locator('.work-body')).to_be_visible();ready()
   enter(alist,peer_a);assert pending_owner()==held_a and checkpoint_a.read_bytes()==before_a;row=f.owner().locator('[data-module-method="'+f.n+'Slot2"]');row.locator('[data-function-import]').click();picker=f.page.locator('.feature-import-dialog');expect(picker).to_be_visible();picker.locator('[data-feature-import-search]').fill('Donor');option=picker.locator('[data-feature-import="'+f.n+'Donor"]');expect(option).to_be_visible();option.evaluate('el=>globalThis.retiredInformationImport=el.onclick');f.page.keyboard.press('Escape');enter(blist,peer_b);mark=len(f.traffic);f.page.evaluate('async()=>await retiredInformationImport()');f.idle();assert not any(r.get('invoke',{}).get('endpoint')=='blueprint' and r['invoke']['input'].get('action') in ['readImplementation','applySlots'] for r in f.traffic[mark:]);assert checkpoint_a.read_bytes()==before_a and checkpoint_b.read_bytes()==saved_b;f.checked('실제 Home A→B 전환 후 은퇴한 A 기능 선택은 B의 copy/본문/등록이나 입력을 변경하지 않는다')
   enter(alist,peer_a);assert pending_owner()==held_a;f.owner().locator('[data-element-action=save]').click();saved(implementation_a);assert checkpoint_b.read_bytes()==saved_b;peer_inputs=peer_b;restart(2);assert any(v['implementation']==implementation_b for v in f.state()['schema']['providers']);enter(alist,peer_a);assert any(v['implementation']==implementation_a for v in f.state()['schema']['providers']);f.originals();assert all((b_root/k).read_bytes()==v for k,v in original_b.items());f.checked('양방향 재진입·A 저장·실제 cold는 두 프로젝트의 copy와 private peer 입력을 분리 복원하고 양쪽 원본을 유지한다')
  elif mode in ['storage','conflict']:
   if mode=='storage':checkpoint.chmod(0o400)
   else:
    f.invoke('schema',{'id':owner});schema=f.state()['schema'];f.invoke('editDescription',{'id':owner,'revision':schema['revision'],'hash':schema['textHash'],'value':'다른 편집자의 저장'});f.invoke('saveDraft',{});before=checkpoint.read_bytes()
   try:f.rejected_save();retained(held);assert checkpoint.read_bytes()==before,'checkpoint changed on rejected Save';f.originals();verify_peer();f.checked('실제 저장 거절/다른 편집자 CAS 충돌은 정보 값·copy·본문·등록 전부 미적용이고 private/다른 창 입력을 보존한다')
   finally:
    if mode=='storage':checkpoint.chmod(0o600)
   restart(1);retained(held);verify_peer()
   if mode=='storage':f.owner().locator('[data-element-action=save]').click();saved(implementation);f.originals();f.checked('실패 cold 뒤 새 명시적 Save는 copy와 exact64 기본값을 함께 적용하고 다른 창 입력·원본을 보존한다')
   else:f.rejected_save();retained(held);assert checkpoint.read_bytes()==before;f.originals();f.checked('실제 source/CAS 변경 뒤 cold 재시도도 오래된 후보 전체를 거절하며 동료 checkpoint를 덮지 않는다')
  elif mode=='cancel':
   f.owner().locator('[data-element-action=discard]').click();expect(d.field(['Power']).locator('[data-property-value]')).to_have_value('9223372036854775806');f.idle();assert not any(pending_owner().values()),pending_owner();cancelled=json.loads(checkpoint.read_text());assert cancelled['changes']==json.loads(before)['changes'] and not cancelled['privateCopies'];verify_peer();f.originals();restart(1);assert not any(pending_owner().values());cancelled=json.loads(checkpoint.read_text());assert cancelled['changes']==json.loads(before)['changes'] and not cancelled['privateCopies'];verify_peer();f.checked('명시 취소와 cold는 정보의 미저장 copy snapshot/본문/값만 정리하고 다른 창 입력·원본·등록·기존 source 초안을 보존한다')
  elif mode=='loss':
   applies=set();queries=set();lost=[]
   def intercept(route):
    body=route.request.post_data_json
    if body.get('op')=='invoke' and body.get('endpoint')=='blueprint':
     action=body.get('input',{}).get('action')
     if action=='applySlots':applies.add(body['requestId'])
     elif applies and action=='settledSlots':queries.add(body['requestId'])
    response=route.fetch();payload=response.json()
    for row in payload.get('results',[]):
     if row['requestId'] in applies|queries:rid=row['requestId'];lost.append(rid);row.clear();row.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
    route.fulfill(response=response,json=payload)
   f.page.route('**/api/request',intercept);f.owner().locator('[data-element-action=save]').click()
   deadline=time.monotonic()+60
   while time.monotonic()<deadline and not any(r in queries for r in lost):f.page.wait_for_timeout(30)
   assert len(applies)==1 and any(r in queries for r in lost);retained(held);verify_peer();f.page.unroute_all(behavior='wait');mark=len(f.traffic);restart(1);saved(implementation);expect(f.owner().locator('[data-element-action=save]')).to_be_disabled();assert any(row.get('invoke',{}).get('input',{}).get('action')=='settledSlots' for row in f.traffic[mark:]);assert not any(row.get('invoke',{}).get('input',{}).get('action')=='applySlots' for row in f.traffic[mark:]);draft=json.loads(checkpoint.read_text());assert len([v for v in draft['changes'] if v.get('creationOwner')==owner and v['kind']=='implementation'])==1;f.originals();verify_peer();f.checked('실제 성공·조회 응답 유실 후 cold receipt 확인은 정보/copy를 중복 저장하지 않고 원래 private 근거·다른 창 입력을 보존한다')
  else:raise AssertionError(mode)
  assert not f.errors and not f.external,(f.errors,f.external);f.page.unroute_all(behavior='wait');f.browser.close()
except Exception:
 (f.case/'information-slot-boundary-failure.json').write_text(json.dumps({'mode':mode,'traffic':f.traffic,'checks':f.checks,'errors':f.errors},ensure_ascii=False,indent=2))
 print('EVIDENCE '+str(f.case),flush=True);raise
finally:f.stop()
print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngine':True,'renderer':True,'nativeWindows':False,'accountOrInference':False},ensure_ascii=False))
