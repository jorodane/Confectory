"""Nominal Blueprint entry/writer/exit changes share caller review and final CAS."""
import copy,json,sys
import v666_blueprint_entry_fixture as c
x,f=c.x,c.f
try:
 f.start(0);f.invoke('select',dict(id=c.owner));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();catalog=c.catalog();c.execute(30,'original')
 if 'baseline'in sys.argv[4:]:assert not catalog['nativeFunctionEdit']['available'];x.unchanged();raise SystemExit(0)
 assert catalog['nativeFunctionEdit']['available']and catalog['nativeFunctionEdit']['blueprintImplementation'];req=c.request(catalog);raw_graph=(f.project/c.graph_path).read_bytes()
 for boundary in ['copy','opaque','async']:
  g=copy.deepcopy(c.graph)
  if boundary=='copy':g['copySource']={'owner':'not-owned'}
  elif boundary=='opaque':g['nodes']=[dict(id='native',kind='code',control='next',signature=c.old)]
  else:g['profile']='async-acyclic-switch-v1'
  (f.project/c.graph_path).write_text(json.dumps(g))
  try:
   v=f.metadata('effective',project=str(f.manifest),manifest=f.manifest.read_text(),id=c.owner,text=(f.project/'FreeInfo.celem').read_text(),nativeTypes=True,nativeFunction=c.fn,observeSources=True);assert v['status']=='available'and not v['nativeFunctionEdit']['available'],v
  finally:(f.project/c.graph_path).write_bytes(raw_graph)
 for fault in ['missing-writer','wrong-source','wrong-type','missing-caller','invalid-code','stale-graph','missing-proof']:
  bad=copy.deepcopy(req);edit=bad['declaration']['changes'][0];output=next(iter(edit['mapping']['outputs'].values()))
  if fault=='missing-writer':edit['mapping']['outputs'].clear()
  elif fault=='wrong-source':output['source']={'input':'unknown'}
  elif fault=='wrong-type':output['type']='int'
  elif fault=='missing-caller':edit['mapping']['bodies'].clear()
  elif fault=='invalid-code':edit['mapping']['bodies'][c.body_id]['text']=c.original
  elif fault=='missing-proof':edit['nativeTypes'].pop('$function:'+c.fn)
  else:(f.project/c.graph_path).write_bytes(raw_graph+b'\n ')
  try:f.invoke('blueprint',bad,False);assert checkpoint.read_bytes()==before
  finally:(f.project/c.graph_path).write_bytes(raw_graph)
  x.unchanged()
 f.checked('copy/opaque/async boundaries remain protected; missing writer/caller/type/scope plans, invalid C# and stale graph reject without checkpoint or original writes')
 f.invoke('blueprint',req);ids=c.verify(checkpoint);x.unchanged();f.stop();f.start(1);f.invoke('select',dict(id=c.owner));assert c.verify(checkpoint)==ids;f.invoke('reviewGroup',dict(ids=ids,target='portable'));review=f.state()['review'];assert review['status']=='ready',review;saved=checkpoint.read_bytes();path=f.project/c.graph_path;raw=path.read_bytes();path.write_bytes(raw+b'\n ')
 try:out=f.invoke('confirmGroup',dict(ids=ids,token=review['token']))['result']['result'];assert out['sourceConfirmed']is False and checkpoint.read_bytes()==saved
 finally:path.write_bytes(raw)
 x.unchanged();f.checked('candidate cold-restores; semantically identical whitespace change to the graph after Review rejects final CAS while exact original coordinates/IDs/routes remain protected')
 f.stop();f.start(2);f.invoke('select',dict(id=c.owner));f.invoke('reviewGroup',dict(ids=ids,target='portable'));review=f.state()['review'];assert review['status']=='ready',review;out=f.invoke('confirmGroup',dict(ids=ids,token=review['token']))['result']['result'];assert out.get('sourceConfirmed')is not False,(out,f.state().get('logs'));x.unchanged(c.changes_allowed);c.execute(31,'selected');f.checked('explicit Review/Confirm updates entry and return '+('exit'if c.use_exit else'writer')+' with only the authored C# caller adaptation; actual struct argument/return executes31')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
