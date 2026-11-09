"""A header-only followup must retain every target and its exact source proof."""
import copy,json
import v666_multitarget_bodies_fixture as x
f=x.f;description='플랫폼별 본문 검토 후 설명'
def rpc(action,**body):return f.invoke('blueprint',dict(action=action,**body))['result']['result']
def save(changes):
 f.invoke('schema',dict(id=x.owner));s=f.state()['schema'];basis=rpc('readOwnerEdits',id=x.owner,hash=s['textHash']);return rpc('applySlots',id=x.owner,rows=[],basis=basis['basis'],declaration=dict(id=x.owner,hash=s['textHash'],changes=changes))
try:
 f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});assert save(x.request()['changes'])['checkpointSaved'];checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));first=json.loads(checkpoint.read_text());before=next(row for row in first['changes']if row['id']==x.owner)['slotSaveReceipt'];assert save([dict(type='description',text=description)])['checkpointSaved'];ids=x.verify(checkpoint);original=checkpoint.read_bytes();data=json.loads(original);owner=next(row for row in data['changes']if row['id']==x.owner);receipt=owner['slotSaveReceipt'];assert receipt['readGuards']==before['readGuards']and set(x.body_paths)<=set(receipt['sources']);key=x.functions[0]+'Body/body:linux';f.checked('header-only followup Save keeps all four reviewed native targets, the exact read guards and complete eight-member group')
 for number,fault in enumerate(['missing-body-proof','missing-body-and-guards','body-kind','body-path','group-member']):
  tampered=copy.deepcopy(data);record=next(row for row in tampered['changes']if row['id']==x.owner);proof=record['slotSaveReceipt']['sources']
  if fault=='missing-body-proof':del proof[key]
  elif fault=='missing-body-and-guards':
   del proof[key];del record['slotSaveReceipt']['readGuards'][x.retained_header];del record['slotSaveReceipt']['readGuards'][x.body_paths[key]]
  elif fault=='body-kind':proof[key]['kind']='function'
  elif fault=='body-path':proof[key]['path']+='-other'
  else:record['atomicEditGroup'].remove(key)
  checkpoint.write_text(json.dumps(tampered,ensure_ascii=False));held=checkpoint.read_bytes();f.stop()
  try:f.start(number+1)
  except AssertionError:
   assert f.host.poll()is not None and'Project workspace unavailable'in(f.case/('host-'+str(number+1)+'.log')).read_text();f.stop();rejected='existing cold restore'
  else:
   f.invoke('select',dict(id=x.owner));f.invoke('reviewGroup',dict(ids=ids,target='portable'),False);rejected='Review'
  assert checkpoint.read_bytes()==held;x.unchanged();rows={row['id']:row for row in json.loads(checkpoint.read_text())['changes']}
  for body,text in x.body_edits.items():assert rows[body]['draft']==text
  f.checked(rejected+' rejects '+fault+' without losing a platform edit or writing source');checkpoint.write_bytes(original)
 f.stop();f.start(6);f.invoke('select',dict(id=x.owner));assert x.verify(checkpoint)==ids;f.invoke('reviewGroup',dict(ids=ids,target='portable'));review=f.state()['review'];assert review['status']=='ready';f.invoke('confirmGroup',dict(ids=ids,token=review['token']));x.accepted_description=description;x.verify_live();f.checked('exact receipt restoration permits fresh explicit Confirm of the later header and both platform programs20/24')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
