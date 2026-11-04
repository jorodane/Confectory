"""Bounded owned-root argument checkpoint admission and unchanged rejection fences."""
import copy,json,sys,uuid
import v666_root_execution_fixture as x
f=x.f
try:
 f.start(0);f.invoke('select',dict(id=x.feature));f.invoke('saveDraft',{});original=x.read();before=x.checkpoint()
 def request():return {'action':'authorBatch','id':x.graph,'attempt':uuid.uuid4().hex,'checkpointHash':original['checkpointHash'],'sourceProof':x.proof(original),'edits':[{'action':'argument','node':'choose','name':'amount','valueJson':'{"constant":2}'}]}
 def rejected(name,change):
  body=request();change(body);v=f.invoke('blueprint',body,False);assert not v['result']['ok'];assert x.checkpoint()==before;x.original();assert x.read()['sources']==original['sources'];f.checked(name)
 rejected('stale checkpoint cannot publish a value candidate',lambda q:q.update(checkpointHash='0'*64))
 def tamper(q):
  rows=json.loads(q['sourceProof']);rows[0][2]='0'*64;q['sourceProof']=json.dumps(rows)
 rejected('tampered source closure cannot publish a value candidate',tamper)
 rejected('unknown node cannot borrow owned argument admission',lambda q:q['edits'][0].update(node='missing'))
 rejected('export nodes cannot borrow code-argument admission',lambda q:q['edits'][0].update(node='publish_yes',name='value'))
 rejected('out-only declaration cannot become an input',lambda q:q['edits'][0].update(name='result'))
 rejected('owner/slot context is not granted by value admission',lambda q:q.update(owner=f.id,ownerHash='0'*64,ownerRevision=0))
 rejected('private frame is not granted by value admission',lambda q:q['edits'][0].update(frame=x.graph+'/graph:missing'))
 rejected('mixed route editing is not granted by argument-only admission',lambda q:q['edits'].append({'action':'route','node':'choose','to':'exit:yes'}))
 graph=f.project/'Flow.graph.json';raw=graph.read_bytes();graph.write_bytes(raw+b' ')
 try:
  body=request();v=f.invoke('blueprint',body);assert v['result']['result']['checkpointSaved']and graph.read_bytes()==raw+b' ';assert all(p.read_bytes()==value for p,value in x.physical.items()if p!=graph)
 finally:graph.write_bytes(raw)
 f.checked('private Save preserves a physical source change; physical publication stays behind final Confirm CAS')
 result=v['result']['result'];assert result['checkpointSaved']and result['sourceWritten']is False;x.original();saved=x.checkpoint();after=x.read();assert next(a['valueJson']for n in after['nodes']if n['id']=='choose'for a in n['arguments']if a['name']=='amount')=='{"constant":2}'
 repeat=f.invoke('blueprint',body)['result']['result'];assert repeat['checkpointSaved']and x.checkpoint()==saved;x.original();f.stop();f.start(1);assert x.checkpoint()==saved;after=x.read();assert next(a['valueJson']for n in after['nodes']if n['id']=='choose'for a in n['arguments']if a['name']=='amount')=='{"constant":2}';x.original();f.checked('one explicit owned value candidate is durable/idempotent across restart without physical source publication')
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
print('VALUE_GUIDANCE_API_FIXTURE',f.case,flush=True)
