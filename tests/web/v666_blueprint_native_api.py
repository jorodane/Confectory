"""Nominal call inputs are explicit existing values, never JSON snapshots."""
import copy,json,sys
import v666_blueprint_native_fixture as c
x,f=c.x,c.f
try:
 f.start(0);f.invoke('select',dict(id=c.owner));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();catalog=c.catalog();c.execute(30,'original')
 if 'baseline'in sys.argv[4:]:assert not catalog['nativeFunctionEdit']['available'];x.unchanged();raise SystemExit(0)
 assert catalog['nativeFunctionEdit']['available'];req=c.request(catalog)
 # The source picker must retain existing non-owned/private/opaque boundaries.
 graph_path=f.project/c.caller_path;raw_graph=graph_path.read_bytes()
 for boundary in ['private-copy','opaque-code','async-frame']:
  graph=copy.deepcopy(c.graph)
  if boundary=='private-copy':graph['copySource']={'owner':'unreviewed'}
  elif boundary=='opaque-code':graph['nodes'][0]['kind']='code'
  else:graph['profile']='async-acyclic-switch-v1'
  graph_path.write_text(json.dumps(graph))
  try:
   projection=f.metadata('effective',project=str(f.manifest),manifest=f.manifest.read_text(),id=c.owner,text=(f.project/'FreeInfo.celem').read_text(),nativeTypes=True,nativeFunction=c.fn,observeSources=True);assert projection['status']=='available'and not projection['nativeFunctionEdit']['available'],projection
  finally:graph_path.write_bytes(raw_graph)
 assert checkpoint.read_bytes()==before;x.unchanged();f.checked('private copy, opaque code and async caller frames remain unavailable; source discovery grants no new editing ownership')
 for fault in ['missing-plan','unknown-source','wrong-type','self-result','raw-snapshot','missing-disconnect','stale-graph']:
  bad=copy.deepcopy(req);edit=bad['declaration']['changes'][0];call=edit['mapping']['callers'][c.caller_id+'#invoke'];raw=(f.project/c.caller_path).read_bytes()
  if fault=='missing-plan':edit['mapping']['bodies'].clear()
  elif fault=='unknown-source':call['inputs']['payload']={'binding':{'input':'missing'}}
  elif fault=='wrong-type':call['inputs']['payload']={'binding':{'input':'mode'}}
  elif fault=='self-result':call['inputs']['payload']={'binding':{'node':'invoke','output':'return'}}
  elif fault=='raw-snapshot':call['inputs']['payload']={'valueJson':'{"Value":{"Count":30}}'}
  elif fault=='missing-disconnect':call['disconnect'].clear()
  else:(f.project/c.caller_path).write_bytes(raw+b'\n')
  try:f.invoke('blueprint',bad,False);assert checkpoint.read_bytes()==before
  finally:(f.project/c.caller_path).write_bytes(raw)
  x.unchanged()
 f.checked('missing native adaptation, unknown/mistyped/self sources, nominal JSON snapshots, unreviewed disconnect and changed graph proofs reject atomically')
 f.invoke('blueprint',req);ids=c.verify(checkpoint);x.unchanged();f.stop();f.start(1);f.invoke('select',dict(id=c.owner));assert c.verify(checkpoint)==ids;f.invoke('reviewGroup',dict(ids=ids,target='portable'));review=f.state()['review'];assert review['status']=='ready',review;saved=checkpoint.read_bytes();path=f.project/c.caller_path;raw=path.read_bytes();path.write_bytes(raw+b'\n// peer graph\n')
 try:out=f.invoke('confirmGroup',dict(ids=ids,token=review['token']))['result']['result'];assert out['sourceConfirmed']is False and checkpoint.read_bytes()==saved
 finally:path.write_bytes(raw)
 x.unchanged();f.checked('complete candidate cold-restores; a Blueprint change after Review rejects final CAS and preserves caller IDs, flow and source bytes')
 f.stop();f.start(2);f.invoke('select',dict(id=c.owner));f.invoke('reviewGroup',dict(ids=ids,target='portable'));review=f.state()['review'];assert review['status']=='ready',review;out=f.invoke('confirmGroup',dict(ids=ids,token=review['token']))['result']['result'];assert out.get('sourceConfirmed')is not False,(out,f.state().get('logs'));x.unchanged(c.changes_allowed);c.execute(31,'selected');f.checked('new explicit Review/Confirm publishes exactly the selected C# adaptation and Blueprint import/bindings; existing struct/enum/interface-array inputs execute31 without rewriting the runtime caller')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
