"""Target disappearance keeps the existing locator refusal and exact recovery."""
import copy,json
import v666_multitarget_bodies_fixture as x
f=x.f
def rpc(action,**body):return f.invoke('blueprint',dict(action=action,**body))['result']['result']
def receipt():return next(row for row in json.loads(checkpoint.read_text())['changes']if row['id']==x.owner)['slotSaveReceipt']
try:
 f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});f.invoke('schema',dict(id=x.owner));s=f.state()['schema'];basis=rpc('readOwnerEdits',id=x.owner,hash=s['textHash']);reply=rpc('applySlots',id=x.owner,rows=[],basis=basis['basis'],declaration=dict(id=x.owner,hash=s['textHash'],changes=x.request()['changes']));assert reply['atomic']and reply['checkpointSaved'];checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));ids=x.verify(checkpoint);saved=copy.deepcopy(receipt());p=f.project/x.retained_header;original=p.read_bytes();removed='body linux "'+x.body_paths[x.functions[0]+'Body/body:linux']+'";';assert removed in original.decode();peer=original.decode().replace(removed,'',1).encode();p.write_bytes(peer);held=checkpoint.read_bytes();f.invoke('reviewGroup',dict(ids=ids,target='portable'),False);assert checkpoint.read_bytes()==held and receipt()==saved and p.read_bytes()==peer;f.checked('live Review rejects peer target removal without shrinking the saved native group')
 f.stop()
 try:f.start(1)
 except AssertionError:
  assert f.host.poll()is not None and'Project workspace unavailable'in(f.case/'host-1.log').read_text();f.stop()
 else:raise AssertionError('Forced project startup unexpectedly adopted the removed saved target locator')
 assert checkpoint.read_bytes()==held and p.read_bytes()==peer and all((f.project/path).read_bytes()==value for path,value in x.snapshot.items()if path!=x.retained_header);rows={row['id']:row for row in json.loads(checkpoint.read_text())['changes']}
 for key,text in x.body_edits.items():assert rows[key]['draft']==text
 f.checked('existing Restore locator ownership rule refuses forced cold project loading after a target disappears; all four saved edits and checkpoint bytes remain intact')
 p.write_bytes(original);f.start(2);f.invoke('select',dict(id=x.owner));assert x.verify(checkpoint)==ids and receipt()==saved;f.invoke('reviewGroup',dict(ids=ids,target='portable'));assert f.state()['review']['status']=='ready';f.checked('exact original header restoration restores cold project loading and permits fresh explicit Review of the complete four-body group')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
