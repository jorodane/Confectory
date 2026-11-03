"""Qualified frame candidate/CAS/restore and frame-local branch return execution."""
import copy,hashlib,json,stat
import v666_root_execution_nested_fixture as x
f=x.f
try:
 x.build('nested-before',x.result_code,x.initial_stdout);f.start(0);d=x.read();assert d['rootExecution'],d.get('rootExecutionError');assert [(r['graph'],r['node']) for r in d['rootExecution']['callers']]==[(x.caller,x.caller_node)]
 units={r['id']:{'kind':r['kind'],'path':r['path'],'draft':(f.project/r['path']).read_text()} for r in d['sources']}
 pure=f.metadata('blueprintRootExecution',namespace='Owned.Elements',id=x.graph,units=units,plan=x.plan(d));assert len(pure['group'])==10,pure['group'];assert x.peer_id in pure['group'] and x.caller+'/node:frame/node:after' in pure['group'];assert x.caller+'/node:after' not in pure['group']
 for u in pure['units'].values():u['baseline']=hashlib.sha256((f.project/u['path']).read_bytes()).hexdigest()
 assert len(f.metadata('blueprintRootExecutionGuards',namespace='Owned.Elements',units=pure['units'])['checks'])==10
 before=x.checkpoint();req=x.request(d)
 for kind in ['unqualified','other-frame','stale','legacy-profile']:
  bad=copy.deepcopy(req)
  if kind=='unqualified':bad['edits'][0]['definition']['caller']['node']='invoke'
  elif kind=='other-frame':bad['edits'][0]['definition']['caller']['routes'][0]['to']='root_after'
  elif kind=='stale':bad['sourceProof']=bad['sourceProof'].replace(d['sources'][0]['hash'],'0'*64)
  else:
   changed=copy.deepcopy(units);g=json.loads(changed[x.caller]['draft']);g['nodes'][0]['graph']['profile']='sync-acyclic-methods-v1';changed[x.caller]['draft']=json.dumps(g)
   try:f.metadata('blueprintRootExecutionCandidates',id=x.graph,units=changed)
   except AssertionError as e:assert 'switch-profile caller frames' in str(e),e
   else:raise AssertionError('Implicit private profile migration accepted')
   continue
  x.rpc('authorBatch',False,**bad);assert x.checkpoint()==before;x.original()
 f.checked('중첩 경로와 같은 local ID를 분리하고 잘못된 frame·낡은 증거·암묵적 profile 전환을 원자 거절한다')
 saved=x.rpc('authorBatch',**req);assert saved['settled'] and saved['checkpointSaved'];assert x.rpc('settledAuthorBatch',**req)['settled'];assert len(x.read()['reviewIds'])==10;x.original();checkpoint=x.checkpoint();f.stop();f.start(1);assert x.checkpoint()==checkpoint and x.rpc('settledAuthorBatch',**req)['settled'];assert x.read()['diagnostics']['state']=='source-ready'
 f.checked('공개 계약·private call·모든 leaf 관측을 한 checkpoint CAS에 저장하고 cold/receipt를 중복 없이 복원한다')
 f.invoke('reviewGroup',{'ids':[x.graph]},False);ids=x.read()['reviewIds'];review=f.invoke('reviewGroup',{'ids':ids});assert not review['state']['review'].get('errors');checkpoint=x.checkpoint();peer=f.project/'PeerAfter.node.json';peer.chmod(0o600)
 try:
  peer.write_bytes(x.physical[peer]+b' ');answer=f.invoke('confirmGroup',{'ids':ids,'token':review['state']['review']['token']})['result']['result'];assert answer['sourceConfirmed'] is False
 finally:peer.write_bytes(x.physical[peer]);peer.chmod(0o400)
 assert x.checkpoint()==checkpoint;x.original();f.checked('Review 뒤 같은 local ID 형제의 원문 경합도 최종 CAS에서 전체 거절하고 입력을 보존한다')
 f.stop();f.start(2);ids=x.read()['reviewIds'];review=f.invoke('reviewGroup',{'ids':ids});f.invoke('confirmGroup',{'ids':ids,'token':review['state']['review']['token']});x.build('nested-after',x.result_code,x.final_stdout)
 published=json.loads((f.project/'Main.graph.json').read_text());assert published['nodes'][2]==x.outer['nodes'][2];assert published['exits']==x.outer['exits'];assert published['nodes'][0]['graph']['exits']==x.inner['exits']
 for p,value in x.physical.items():
  if p.name.endswith('.node.json'):assert p.read_bytes()==value,p
 assert stat.S_IMODE(peer.stat().st_mode)==0o400
 f.checked('private 반환은 해당 frame만 끝내며 부모 다음 줄·값·ID·형제·C# 바이트와 readonly mode를 실제 실행으로 보존한다')
 f.stop();f.start(3);assert x.read()['diagnostics']['state']=='source-ready';assert x.read(x.caller)['diagnostics']['state']=='source-ready';print('M12_NESTED_FIXTURE '+str(f.case),flush=True)
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
