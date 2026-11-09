"""Legacy leaf groups with only ordinary Blueprint callers keep their empty read receipt."""
import json
import v666_body_imports_fixture as x
f=x.f
def rpc(action,**body):return f.invoke('blueprint',dict(action=action,**body))['result']['result']
try:
 assert x.mode=='leaf';f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});f.invoke('schema',dict(id=x.owner));s=f.state()['schema'];basis=rpc('readOwnerEdits',id=x.owner,hash=s['textHash']);reply=rpc('applySlots',id=x.owner,rows=[],basis=basis['basis'],declaration=dict(id=x.owner,hash=s['textHash'],changes=x.request()['changes']));assert reply['atomic']and reply['checkpointSaved'];checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));ids=x.verify(checkpoint);owner=next(r for r in json.loads(checkpoint.read_text())['changes']if r['id']==x.owner);assert owner['slotSaveReceipt']['readGuards']=={};f.stop();f.start(1);f.invoke('select',dict(id=x.owner));assert x.verify(checkpoint)==ids;f.invoke('reviewGroup',dict(ids=ids,target='portable'));review=f.state()['review'];assert review['status']=='ready';f.invoke('confirmGroup',dict(ids=ids,token=review['token']));x._base.verify_live();x.execute(20,'legacy-leaf');f.checked('legacy leaf/ordinary Blueprint caller empty-readGuards group remains valid through cold/Review/Confirm and execution20')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
