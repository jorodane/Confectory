"""Fixed C# ABI/text/helpers and real nominal values survive root contract edits."""
import copy,json
import v666_retained_native_code_fixture as c
x,f=c.x,c.f
try:
 f.start(0);f.invoke('select',dict(id=c.owner));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();catalog=c.catalog();c.execute(30,'original');assert catalog['nativeFunctionEdit']['available'];req=c.request(catalog);path=f.project/c.code_path;raw=path.read_bytes();stat=path.stat();scope=req['declaration']['changes'][0]['nativeTypes']['$function:'+c.fn];assert '$code:'+c.code_id in scope['sources']
 graph_path=f.project/c.graph_path;graph_raw=graph_path.read_bytes()
 for field,value in [('implementationContext',{}),('postCall',{}),('async',True),('imports',[c.fn])]:
  graph=copy.deepcopy(c.graph);graph['nodes'][0][field]=value;graph_path.write_text(json.dumps(graph))
  try:
   try:projection=c.catalog()
   except AssertionError as error:assert "'code': 'consumer_error'"in str(error),error
   else:assert not projection['nativeFunctionEdit']['available']
   assert checkpoint.read_bytes()==before
  finally:graph_path.write_bytes(graph_raw)
 x.unchanged();f.checked('context/wrapper/async or self-import scope does not gain editing authority from a retained ordinary code node')
 for fault in ['missing-use','wrong-use','missing-output','missing-caller','stale-record']:
  bad=copy.deepcopy(req);edit=bad['declaration']['changes'][0]
  if fault=='missing-use':edit['mapping']['implementations'].clear()
  elif fault=='wrong-use':next(iter(edit['mapping']['implementations'].values()))['value']={'input':'missing'}
  elif fault=='missing-output':edit['mapping']['outputs'].clear()
  elif fault=='missing-caller':edit['mapping']['bodies'].clear()
  else:path.write_bytes(raw+b'\n ')
  try:f.invoke('blueprint',bad,False);assert checkpoint.read_bytes()==before
  finally:path.write_bytes(raw)
  x.unchanged()
 for fault in ['invalid-code','stale-definition']:
  record=copy.deepcopy(c.record)
  if fault=='invalid-code':record['source']='return 17;'
  else:record['definitionHash']='0'*64
  path.write_text(json.dumps(record))
  try:
   try:fresh=c.catalog()
   except AssertionError as error:assert "'code': 'consumer_error'"in str(error),error
   else:f.invoke('blueprint',c.request(fresh),False)
   assert checkpoint.read_bytes()==before
  finally:path.write_bytes(raw)
  x.unchanged()
 f.checked('missing input/output/caller plans, unknown source, stale code proof, invalid C# and stale definition receipt reject atomically without rewriting the retained code')
 req=c.request(c.catalog());f.invoke('blueprint',req);ids=c.verify(checkpoint);x.unchanged();f.stop();f.start(1);f.invoke('select',dict(id=c.owner));assert c.verify(checkpoint)==ids;f.invoke('reviewGroup',dict(ids=ids,target='portable'));review=f.state()['review'];assert review['status']=='ready',review;saved=checkpoint.read_bytes();peer=copy.deepcopy(c.record);peer['source']+='// peer comment\n';path.write_text(json.dumps(peer))
 try:out=f.invoke('confirmGroup',dict(ids=ids,token=review['token']))['result']['result'];assert out['sourceConfirmed']is False and checkpoint.read_bytes()==saved
 finally:path.write_bytes(raw)
 x.unchanged();f.checked('code source is a read dependency of the whole candidate; a semantically harmless code comment after Review rejects final CAS, preserving the checkpoint')
 f.stop();f.start(2);f.invoke('select',dict(id=c.owner));f.invoke('reviewGroup',dict(ids=ids,target='portable'));review=f.state()['review'];assert review['status']=='ready',review;before_stat=path.stat();out=f.invoke('confirmGroup',dict(ids=ids,token=review['token']))['result']['result'];assert out.get('sourceConfirmed')is not False,(out,f.state().get('logs'));assert path.read_bytes()==raw and path.stat().st_mtime_ns==before_stat.st_mtime_ns;x.unchanged(c.changes_allowed);c.execute(31,'selected');f.checked('explicit input rebind and writer/exit choice plus only the authored C# caller change execute31; the ordinary C# node signature, full record bytes/helpers and mtime remain unchanged')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
