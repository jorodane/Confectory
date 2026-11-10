"""Legacy v1 remains readable; guarded v2 cannot be downgraded silently."""
import json
import v666_function_types_fixture as x
f=x.f
try:
 f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));initial=checkpoint.read_bytes();assert json.loads(initial)['version']==1 and'nativeTypeProfile'not in json.loads(initial);request=x.request();row=request['declaration']['changes'][0];f.invoke('blueprint',request);ids=x.verify(checkpoint,row['id'],row['signature']);valid=checkpoint.read_bytes();x.unchanged();f.stop();f.checked('a legacy v1 draft loads unchanged and only a native-type-protected candidate exports v2 with its exact capability profile')
 for index,mode in enumerate(['downgrade','profile'],1):
  bad=json.loads(valid)
  if mode=='downgrade':bad['version']=1;bad.pop('nativeTypeProfile')
  else:bad['nativeTypeProfile']='unknown-reader-profile'
  data=json.dumps(bad,ensure_ascii=False).encode();checkpoint.write_bytes(data)
  try:f.start(index)
  except AssertionError as error:assert'Project workspace unavailable'in str(error),str(error)
  else:raise AssertionError('incompatible guarded checkpoint opened')
  finally:f.stop()
  assert checkpoint.read_bytes()==data;x.unchanged()
 f.checked('a forged v1 downgrade and an unknown v2 profile are rejected before restoring or writing sources; the incompatible checkpoint remains byte-identical')
 checkpoint.write_bytes(valid);f.start(3);f.invoke('select',dict(id=x.owner));assert x.verify(checkpoint,row['id'],row['signature'])==ids;f.invoke('schema',dict(id=x.owner));schema=f.state()['schema'];f.invoke('editDescription',dict(id=x.owner,revision=schema['revision'],hash=schema['textHash'],value='newer unsaved description'));status=f.invoke('browserDrafts',dict(action='status',ids=[x.owner]))['result']['result'];f.invoke('browserDrafts',dict(action='discard',ids=status['ids'],revisions=[r['revision']for r in status['rows']],hashes=[r['hash']for r in status['rows']],checkpointHash=status['checkpointHash'],ownerHash=status['ownerHash']));assert not(f.project/('elements/'+row['id'].split('::')[1]+'.celem')).exists();x.unchanged();f.stop();f.start(4);f.invoke('select',dict(id=x.owner));f.invoke('schema',dict(id=x.owner));assert any(v['id']==row['id']for v in f.state()['schema']['ownFunctions']);assert f.state()['schema']['description']!='newer unsaved description' and checkpoint.read_bytes()==valid;x.verify(checkpoint,row['id'],row['signature']);x.unchanged();f.checked('v2 creation-group discard removes only newer unsaved description input; the settled typed function and exact saved checkpoint survive cold restart without publishing sources')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
