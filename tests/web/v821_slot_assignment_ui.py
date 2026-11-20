"""Actual owned object slot replacement; immutable existing implementations.

Uses the original card, existing provide semantics and original Save/Confirm.
No inference, account, conversion, source creation or hidden provider fallback.
"""
import copy,json,re,stat,sys,time
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
import v666_export_binding_recovery_fixture as t

f=t.f;x=t.x;owner=f.n+'Monster';feature=f.n+'Slot';selected=f.n+'AssignedBody'
mode=sys.argv[3] if len(sys.argv)>3 else 'normal'
signature='(long amount,out long slotCount,out bool slotReady) -> long'
extra={
 'AssignedBody':('implementation','implementation '+selected+' for '+feature+' '+signature+' {description "기존 구현 선택";body common "Assigned.csbody";}'),
 'BoundBody':('implementation','implementation '+f.n+'BoundBody for '+feature+' '+signature+' {body common "Bound.csbody";}'),
 'ReadOnlyBody':('implementation','implementation '+f.n+'ReadOnlyBody for '+feature+' '+signature+' {body common "ReadOnly.csbody";}'),
 'PeerOwner':('object','object '+f.n+'PeerOwner {module '+f.n+'Rules;provide '+feature+' with '+f.n+'BoundBody;}')}
for name,(kind,text) in extra.items():
 (f.project/(name+'.celem')).write_text(text)
 f.manifest=f.project/'project.cproj';f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element '+name+' '+kind+' "'+name+'.celem";registry Confectory.Build.DotNet',1))
for name in ['Assigned','Bound','ReadOnly']:
 (f.project/(name+'.csbody')).write_text('slotCount=amount+50;slotReady=true;return amount+40; // 원본 유지\r\n')
(f.project/'ReadOnlyBody.celem').chmod(0o400)
if mode=='contract':
 p=f.project/'AssignedBody.celem';p.write_text(p.read_text().replace('out long slotCount','ref long slotCount'))
(f.project/'MainBody.celem').write_text('implementation '+f.n+'MainBody for '+f.n+'Main () -> int {import '+feature+' as Slot (long,out long,out bool) -> long in '+owner+';body common "Main.csbody";}')
(f.project/'Main.csbody').write_text('long result=calls.Slot.Invoke(5,out long count,out bool ready);global::System.Console.WriteLine($"{result}:{count}:{ready}");return checked((int)result);')
f.original={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file()}
modes={p:stat.S_IMODE((f.project/p).stat().st_mode) for p in f.original}
(f.case/'slot-assignment-originals.json').write_text(json.dumps(dict(ownerText=f.original['Monster.celem'].decode(),files={p:dict(sha256=__import__('hashlib').sha256(raw).hexdigest(),mode=modes[p])for p,raw in f.original.items()}),ensure_ascii=False,indent=2))
peer=[]
def original():
 f.originals();assert all(stat.S_IMODE((f.project/p).stat().st_mode)==m for p,m in modes.items())
def schema():
 f.invoke('schema',dict(id=owner));return f.state()['schema']
def base():
 s=schema();return dict(id=owner,function=feature,previous=f.n+'AliasBody',revision=s['revision'],hash=s['textHash'])
def rpc(action,success=True,**kw):return f.invoke('blueprint',dict(action=action,**kw),success)['result'].get('result')
def slot():return f.owner().locator('[data-module-method="'+feature+'"]')
def pending():return [(k,v) for k,v in f.pending()['schema'] if '|'+owner+'|element|' in k]
def peer_kept():assert [(k,v) for k,v in f.pending()['schema'] if '|'+f.n+'Target1|element|' in k]==peer
def ready():
 expect(f.owner().locator('.object-title-name')).to_have_text('Monster');expect(slot().locator('[data-function-assignment]')).to_be_visible();f.idle()
def restart(i,flush=True):
 if flush:f.pending()
 f.page.unroute_all(behavior='ignore');f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size(dict(width=1800,height=1450));ready();peer_kept();original()
def rejected(held,checkpoint,raw):
 f.rejected_save();assert pending()==held and checkpoint.read_bytes()==raw;peer_kept();original()
def review():
 f.owner().locator('[data-element-action=confirm]').click();r=f.page.locator('.window[data-key=review]');expect(r).to_be_visible(timeout=120000)
 for check in r.locator('[data-review-id]').all():check.check()
 if r.locator('[data-review-advanced]').count():
  r.locator('[data-review-advanced]').click()
  if r.locator('[data-advanced-reviewed]').count():r.locator('[data-advanced-reviewed]').check()
 return r
try:
 f.start(0);f.invoke('select',dict(id=owner));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();b=base()
 catalog=rpc('slotAssignments',**b,query='',page=0)
 if mode=='contract':
  assert not catalog['rows'],catalog;rpc('readSlotAssignment',False,**b,implementation=selected);assert checkpoint.read_bytes()==before;original()
 else:
  assert [r['implementation']for r in catalog['rows']]==[selected],catalog
  prepared=rpc('readSlotAssignment',**b,implementation=selected);row=dict(function=feature,implementation=selected,fingerprint=prepared['fingerprint'],basis=prepared['basis'])
  for target in [f.n+'BoundBody',f.n+'ReadOnlyBody',f.n+'DonorBody','Other.Pack::Body']:
   rpc('readSlotAssignment',False,**b,implementation=target);assert checkpoint.read_bytes()==before;original()
  for mutation in ['owner','implementation','fingerprint','unmarked','duplicate','edits','declaration','stale']:
   q=dict(id=owner,rows=[copy.deepcopy(row)])
   if mutation=='owner':q['id']=f.n+'Slime'
   elif mutation=='implementation':q['rows'][0]['implementation']=f.n+'BoundBody'
   elif mutation=='fingerprint':q['rows'][0]['fingerprint']='0'*64
   elif mutation=='unmarked':q['rows'][0].pop('fingerprint')
   elif mutation=='duplicate':q['rows']*=2
   elif mutation=='edits':q['rows'][0]['edits']=[dict(action='source',node='body',text='return 0;')]
   elif mutation=='declaration':q['declaration']=dict(id=owner,hash=b['hash'],changes=[])
   else:q['rows'][0]['basis']='stale-slot-token'
   rpc('applySlots',False,**q);assert checkpoint.read_bytes()==before;original()
  f.checked('server catalog/selection binds one current direct object provider; other owners/defaults, read-only headers, wrong function and forged/mixed/stale plans refuse without mutation')
 with sync_playwright()as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size(dict(width=1800,height=1450));f.open_owner(f.n+'Target1');f.owner().locator('.object-title-description').fill('다른 객체 입력 보존 α');peer=[(k,v)for k,v in f.pending()['schema']if '|'+f.n+'Target1|element|'in k];assert peer;f.open_owner(owner);ready()
  slot().locator('[data-function-assignment]').click();picker=f.page.locator('.feature-import-dialog');expect(picker).to_be_visible()
  if mode=='contract':
   expect(picker.locator('.feature-import-empty')).to_contain_text('없습니다');assert pending()==[];peer_kept();original();picker.locator('[data-close]').first.click() if picker.locator('[data-close]').count()else f.page.keyboard.press('Escape');restart(1);assert pending()==[];original();f.checked('out/ref contract mismatch is absent from the actual picker and rejected by server; unrelated input and originals survive cold')
  else:
   picker.locator('[data-slot-assignment="'+selected+'"]').click();expect(picker).to_be_hidden();held=pending();assert len(held)==1 and held[0][1]['kind']=='slot-assignment';expect(slot().locator('[data-slot-assignment-current]')).to_contain_text('AssignedBody');assert checkpoint.read_bytes()==before;original();peer_kept()
   slot().locator('.function-node-name').click();f.page.keyboard.press('Control+z');assert pending()==[];slot().locator('.function-node-name').click();f.page.keyboard.press('Control+y');assert pending()==held;restart(1);assert pending()==held
   f.checked('original object card stages the chosen existing implementation, supports private Undo/Redo and cold selection recovery without changing the original provider or other object input')
   if mode=='conflict':
    s=schema();f.invoke('editDescription',dict(id=owner,revision=s['revision'],hash=s['textHash'],value='동시 저장된 설명'));f.invoke('saveDraft',{});peer_checkpoint=checkpoint.read_bytes();rejected(held,checkpoint,peer_checkpoint);assert schema()['description']=='동시 저장된 설명';restart(2);assert pending()==held;rejected(held,checkpoint,peer_checkpoint);f.checked('peer owner Save refuses the stale selection without rebasing and preserves peer checkpoint, original provider and all private inputs through cold')
   else:
    for file in ['Assigned.csbody','PeerOwner.celem']:
     p=f.project/file;raw=p.read_bytes();p.write_bytes(raw+b' ')
     try:f.rejected_save();assert pending()==held and checkpoint.read_bytes()==before and p.read_bytes()==raw+b' ';peer_kept()
     finally:p.write_bytes(raw)
     original()
    for file in [f.project/'Monster.celem',f.project/'AssignedBody.celem',checkpoint]:
     old_mode=stat.S_IMODE(file.stat().st_mode);file.chmod(0o400)
     try:f.rejected_save();assert pending()==held and checkpoint.read_bytes()==before;f.originals();peer_kept()
     finally:file.chmod(old_mode)
     original()
    restart(2);assert pending()==held
    # Lose an actual successful Save response; receipt reconciliation must survive cold.
    ids=set();lost={}
    def intercept(route):
     body=route.request.post_data_json
     if body.get('op')=='invoke'and body.get('endpoint')=='blueprint'and body.get('input',{}).get('action')=='applySlots':ids.add(body['requestId'])
     response=route.fetch();payload=response.json()
     if not lost and body.get('op')=='update'and any(r.get('requestId')in ids for r in payload.get('results',[])):
      assert all(r.get('ok')for r in payload['results']if r.get('requestId')in ids),payload;lost.update(accepted=True);payload['results']=[dict(requestId=r['requestId'],ok=False,error=dict(code='transport-interrupted'))if r.get('requestId')in ids else r for r in payload['results']];route.fulfill(response=response,json=payload);return
     route.fulfill(response=response)
    f.page.route('**/api/request',intercept);f.owner().locator('[data-element-action=save]').click();deadline=time.monotonic()+120
    while not lost and time.monotonic()<deadline:f.page.wait_for_timeout(50)
    assert lost,'no successful assignment response observed';saved=checkpoint.read_bytes();assert saved!=before and len(ids)==1;f.idle();(f.case/'slot-assignment-loss.json').write_text(json.dumps(dict(actualServerSuccess=True,saveRequests=len(ids),pendingBeforeCold=pending()),ensure_ascii=False));original();restart(3,False);deadline=time.monotonic()+90
    while pending()and time.monotonic()<deadline:f.page.wait_for_timeout(50)
    assert not pending()and checkpoint.read_bytes()==saved;peer_kept();s=schema();assert next(r for r in s['providers']if r['function']==feature)['implementation']==selected;original()
    history=f.invoke('draftHistory',dict(action='inspect'))['result']['result'];assert history['boundary']=='OWNERSHIP_CHANGED'and not history['undo']['available']and not history['redo']['available'];denied=[f.invoke('draftHistory',dict(action=direction,token='stale-slot-token'))['result']['result']for direction in ['undo','redo']];assert all(not value['accepted']and not value['changed']for value in denied);assert checkpoint.read_bytes()==saved;restart(4);assert not pending();original()
    f.checked('physical source/permission/checkpoint faults preserve exact selection; accepted response loss reconciles without duplicate Save through cold, and shared Undo/Redo retain the existing OWNERSHIP_CHANGED boundary')
    r=review();r.locator('[data-reject]').click();original();r=review();review_checkpoint=checkpoint.read_bytes();(f.case/'slot-assignment-before-cas.json').write_bytes(review_checkpoint);p=f.project/'Assigned.csbody';raw=p.read_bytes();p.write_bytes(raw+b' ')
    try:r.locator('#confirm').click();f.idle();(f.case/'slot-assignment-after-cas.json').write_bytes(checkpoint.read_bytes());assert p.read_bytes()==raw+b' 'and checkpoint.read_bytes()==review_checkpoint;assert(f.project/'Monster.celem').read_bytes()==f.original['Monster.celem']
    finally:p.write_bytes(raw)
    if r.is_visible():r.locator('[data-reject]').click()
    r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();x.build('slot-existing-assignment',45,'45:55:True');assert {k for k,v in f.original.items()if(f.project/k).read_bytes()!=v}=={'Monster.celem'};assert all(stat.S_IMODE((f.project/p).stat().st_mode)==m for p,m in modes.items());assert 'provide '+feature+' with '+selected in(f.project/'Monster.celem').read_text();peer_kept()
    f.checked('Review cancel and final dependency CAS preserve originals/peer changes; fresh Confirm changes only the object provide mapping and real unchanged native execution returns 45 with out values 55/true')
    f.original={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.parts};restart(5);assert next(r for r in schema()['providers']if r['function']==feature)['implementation']==selected;expect(slot().locator('[data-slot-assignment-current]')).to_contain_text('AssignedBody');assert not pending();original();f.checked('confirmed existing provider reopens from physical sources with the same assignment, unchanged bodies and peer input')
  slot().scroll_into_view_if_needed();f.page.screenshot(path=str(f.case/('slot-assignment-'+mode+'.png')),full_page=True);assert not f.errors and not f.external,(f.errors,f.external);f.browser.close()
except BaseException:
 if getattr(f,'page',None):
  try:(f.case/'slot-assignment-failure.html').write_text(f.page.content());f.page.screenshot(path=str(f.case/'slot-assignment-failure.png'),timeout=10000)
  except Exception:pass
 raise
finally:
 (f.case/'slot-assignment-traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False));(f.case/'slot-assignment-checks.json').write_text(json.dumps(f.checks,ensure_ascii=False));f.stop()
print('V821_SLOT_ASSIGNMENT',mode,f.case,flush=True)
