"""Whole-body node ABI/source edits keep exact original/context CAS boundaries."""
import copy,json
import v666_native_retained_fixture as c
x,f=c.x,c.f
try:
 f.start(0);f.invoke('select',dict(id=c.owner));f.invoke('saveDraft',{});cp=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=cp.read_bytes();catalog=c.catalog();extra_time=(f.project/c.extra_path).stat().st_mtime_ns;assert catalog['nativeFunctionEdit']['available'];c.execute(30,'original');r=c.request(catalog)
 if c.consumer:
  row=catalog['functionBodies'][c.code_id];assert len(row['outputConsumers']['return'])==2;f.invoke('blueprint',r,False);assert cp.read_bytes()==before;x.unchanged();f.checked('unmapped old output still used by independent code rejects despite an explicit writer replacement; no source or checkpoint writes');raise SystemExit(0)
 for fault in ['body','caller','receipt','signature','return','compile','context','output','writer']:
  bad=copy.deepcopy(r);m=bad['declaration']['changes'][0]['mapping'];p=m['bodies'][c.code_id]
  if fault=='body':m['bodies'].pop(c.code_id)
  elif fault=='caller':m['bodies'].pop(c.body_id)
  elif fault=='receipt':p['whole']['hash']='0'*64
  elif fault=='signature':p['signature']['args'][0]['type']='int'
  elif fault=='return':p['whole']['returnNode']=c.node['id']
  elif fault=='compile':p['text']='return 17;'
  elif fault=='output':p['outputs']['return']='return'
  elif fault=='writer':m['outputs'].clear()
  else:p['whole']['node']='other'
  f.invoke('blueprint',bad,False);assert cp.read_bytes()==before;x.unchanged()
 f.checked('missing manual bodies, stale whole/context/return receipts, wrong native ABI and invalid C# reject atomically; original C# file and every route/ID survive')
 f.invoke('blueprint',r);ids=c.verify(cp);x.unchanged();f.stop();f.start(1);f.invoke('select',dict(id=c.owner));assert c.verify(cp)==ids;f.invoke('reviewGroup',dict(ids=ids,target='portable'));v=f.state()['review'];assert v['status']=='ready',v;path=f.project/c.code_path;raw=path.read_bytes();saved=cp.read_bytes();path.write_bytes(raw+b'\n ')
 try:assert f.invoke('confirmGroup',dict(ids=ids,token=v['token']))['result']['result']['sourceConfirmed']is False;assert cp.read_bytes()==saved
 finally:path.write_bytes(raw)
 f.checked('cold-restored whole-body candidate compiles with generated struct types and rejects even whitespace source change after Review')
 f.stop();f.start(2);f.invoke('select',dict(id=c.owner));f.invoke('reviewGroup',dict(ids=ids,target='portable'));v=f.state()['review'];assert v['status']=='ready',v;out=f.invoke('confirmGroup',dict(ids=ids,token=v['token']))['result']['result'];assert out.get('sourceConfirmed')is not False;assert(f.project/c.native_path).read_bytes()==c.code_original.encode();assert(f.project/c.extra_path).read_bytes()==c.extra_bytes and(f.project/c.extra_path).stat().st_mtime_ns==extra_time;x.unchanged(c.changes_allowed);c.execute(31,'selected');f.checked('only explicit retained context ABI/text/writer and caller plans change the owned node ABI; independent code/helper bytes/mtime, exact local, original .csbody and native names/IDs/layout survive; actual execution30→31')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
