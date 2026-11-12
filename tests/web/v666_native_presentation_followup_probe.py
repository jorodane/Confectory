"""Diagnose a four-row presentation Save after a native ABI group; never Confirm."""
import copy,hashlib,json,sys
import v666_native_header_contracts_fixture as x
f=x.f;proof={};peer_path=f.project/x.retained_file;peer_original=None

def rpc(action,**body):return f.invoke('blueprint',dict(action=action,**body))['result']['result']
def prepare(changes):
 f.invoke('schema',dict(id=x.owner));sc=f.state()['schema'];basis=rpc('readOwnerEdits',id=x.owner,hash=sc['textHash']);return dict(id=x.owner,rows=[],basis=basis['basis'],declaration=dict(id=x.owner,hash=sc['textHash'],changes=changes))
def receipt():return next(row for row in json.loads(checkpoint.read_text())['changes']if row['id']==x.owner)['slotSaveReceipt']
try:
 f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));first=rpc('applySlots',**prepare(x.request()['changes']));assert first['atomic']and first['checkpointSaved'];ids=x.verify(checkpoint);before=copy.deepcopy(receipt());assert before['readGuards']and x.retained_file in before['readGuards'];proof['beforeGuards']=before['readGuards'];proof['beforeReceipt']=before;original_checkpoint=checkpoint.read_bytes();rows={row['id']:row for row in json.loads(original_checkpoint)['changes']};changes=[dict(type='description',text='한 Save의 후속 정보 설명'),dict(type='icon',text='★')]
 for index,fn in enumerate(x.functions):
  changes.append(dict(type='function-edit',id=fn,hash=hashlib.sha256(rows[fn]['draft'].encode()).hexdigest(),name=x.labels[index],description='후속 함수 설명 '+str(index),signature=copy.deepcopy(x.nexts[index])))
 proof['followupChanges']=changes
 try:reply=rpc('applySlots',**prepare(changes))
 except AssertionError as ex:
  proof.update(metadataAccepted=False,rejection=str(ex),checkpointUnchanged=checkpoint.read_bytes()==original_checkpoint);x.unchanged();f.checked('published four-row followup presentation is rejected while the original saved group/source remains intact')
 else:
  after=copy.deepcopy(receipt());proof.update(metadataAccepted=True,reply=reply,afterGuards=after.get('readGuards'),afterReceipt=after,guardScopePreserved=after.get('readGuards')==before['readGuards']);x.unchanged();peer_original=peer_path.read_bytes();peer_path.write_bytes(peer_original+b'\n// peer helper after metadata Save before Review\n')
  try:
   try:f.invoke('reviewGroup',dict(ids=ids,target='portable'))
   except AssertionError as ex:proof.update(peerReviewAccepted=False,peerReviewRejection=str(ex))
   else:proof.update(peerReviewAccepted=True,review=f.state().get('review'))
  finally:peer_path.write_bytes(peer_original);peer_original=None
  x.unchanged();f.checked('four-row followup observed guard preservation='+str(proof['guardScopePreserved'])+', peer Review accepted='+str(proof['peerReviewAccepted'])+'; no Confirm and original bytes restored')
 if '--expect=safe'in sys.argv:assert proof.get('metadataAccepted')and proof.get('guardScopePreserved')and proof.get('peerReviewAccepted')is False,proof
finally:
 if peer_original is not None:peer_path.write_bytes(peer_original)
 (f.case/'presentation-followup-probe.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2));(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
