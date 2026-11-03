"""callee contract update inside an existing private forwarded execution frame."""
import copy,hashlib,json,stat
import v666_root_execution_forwarding_fixture as x
f=x.f
try:
 x.build('forward-before',x.result_code,x.initial_stdout);f.start(0);d=x.read();assert d['rootExecution'],d.get('rootExecutionError');assert [(r['graph'],r['node']) for r in d['rootExecution']['callers']]==[(x.caller,x.caller_node)]
 units={r['id']:{'kind':r['kind'],'path':r['path'],'draft':(f.project/r['path']).read_text()} for r in d['sources']}
 pure=f.metadata('blueprintRootExecution',namespace='Owned.Elements',id=x.graph,units=units,plan=x.plan(d));assert len(pure['group'])==x.expected_review_members,pure['group']
 for u in pure['units'].values():u['baseline']=hashlib.sha256((f.project/u['path']).read_bytes()).hexdigest()
 assert len(f.metadata('blueprintRootExecutionGuards',namespace='Owned.Elements',units=pure['units'])['checks'])==x.expected_review_members
 before=x.checkpoint();req=x.request(d)
 for kind in ['source','enum','signature','coverage','branch-owner','legacy-profile']:
  bad=copy.deepcopy(units);body=json.loads(bad[x.caller]['draft']);frame=next(n for n in body['nodes'] if n['id']=='frame');child=frame['graph']
  if kind=='source':frame['executionSource']='invoke'
  elif kind=='enum':frame['executionEnum']['members'][1]['value']=18
  elif kind=='signature':frame['signature']['args'][0]['type']='int'
  elif kind=='coverage':child['exits']['return']['executionBranch']='next'
  elif kind=='branch-owner':next(n for n in child['nodes'] if n['id']=='invoke')['branchOwner']='missing'
  else:child['profile']='sync-acyclic-methods-v1'
  bad[x.caller]['draft']=json.dumps(body)
  try:f.metadata('blueprintRootExecutionCandidates',id=x.graph,units=bad)
  except AssertionError:pass
  else:raise AssertionError('Invalid private forwarding contract accepted: '+kind)
 for kind in ['unqualified','parent-target','foreign-branch','stale']:
  bad=copy.deepcopy(req)
  if kind=='unqualified':bad['edits'][0]['definition']['caller']['node']='invoke'
  elif kind=='parent-target':bad['edits'][0]['definition']['caller']['routes'][0]['to']='root_after'
  elif kind=='foreign-branch':bad['edits'][0]['definition']['exits']['yes']['executionBranch']='done'
  else:bad['sourceProof']=bad['sourceProof'].replace(d['sources'][0]['hash'],'0'*64)
  x.rpc('authorBatch',False,**bad);assert x.checkpoint()==before;x.original()
 source=f.project/'Select.node.json';source.write_bytes(x.physical[source]+b' ')
 try:x.rpc('authorBatch',False,**req)
 finally:source.write_bytes(x.physical[source])
 assert x.checkpoint()==before;x.original();f.checked('기존 private source·enum·서명·종료점 coverage와 local 경로를 검증하고 Save 전 원문 경합을 전체 거절한다')
 saved=x.rpc('authorBatch',**req);assert saved['settled'] and saved['checkpointSaved'];assert x.rpc('settledAuthorBatch',**req)['settled'];assert len(x.read()['reviewIds'])==x.expected_review_members;x.original();checkpoint=x.checkpoint();f.stop();f.start(1);assert x.checkpoint()==checkpoint and x.rpc('settledAuthorBatch',**req)['settled'];assert x.read()['diagnostics']['state']=='source-ready'
 f.checked('callee 공개 계약·private call·selector·형제 원문을 한 checkpoint에 보존하고 cold receipt는 중복 적용하지 않는다')
 # A repeated explicit update changes only the callee's names/order, preserving allocated IDs/values.
 repeat=x.request(x.read());repeat['edits'][0]['definition']['branches'].reverse();repeat['edits'][0]['definition']['branches'][0]['name']='실패 이름';repeat['edits'][0]['definition']['branches'][1]['name']='성공 이름';x.rpc('authorBatch',**repeat);x.original();assert x.read(x.caller)['diagnostics']['state']=='source-ready'
 f.checked('반복 이름·순서 갱신도 피호출자의 기존 ID/값만 사용하고 private 분기17·입출력 계약은 바꾸지 않는다')
 f.invoke('reviewGroup',{'ids':[x.graph]},False);ids=x.read()['reviewIds'];review=f.invoke('reviewGroup',{'ids':ids});assert not review['state']['review'].get('errors');checkpoint=x.checkpoint();peer=f.project/'PeerAfter.node.json';peer.chmod(0o600)
 try:
  peer.write_bytes(x.physical[peer]+b' ');answer=f.invoke('confirmGroup',{'ids':ids,'token':review['state']['review']['token']})['result']['result'];assert answer['sourceConfirmed'] is False
 finally:peer.write_bytes(x.physical[peer]);peer.chmod(0o400)
 assert x.checkpoint()==checkpoint;x.original();f.stop();f.start(2);f.checked('부분 Review 및 Review 뒤 readonly 형제 경합을 최종 CAS에서 전체 거절하며 저장 입력을 복원한다')
 ids=x.read()['reviewIds'];review=f.invoke('reviewGroup',{'ids':ids});f.invoke('confirmGroup',{'ids':ids,'token':review['state']['review']['token']});x.build('forward-after',x.result_code,x.final_stdout)
 assert stat.S_IMODE(peer.stat().st_mode)==0o400
 f.checked('callee 성공은 현재 private frame만 반환하며 원래 분기17·out10·부모 분기/다음 줄·ID·C# 바이트를 실제 실행으로 보존한다')
 body=f.project/'Flow.graph.json';saved=body.read_bytes()
 try:
  for selected in ['failure','none']:
   current=json.loads(saved);current['exits']['yes']['executionBranch']=selected;body.write_text(json.dumps(current));x.build('forward-'+selected,x.result_code,x.initial_stdout)
 finally:body.write_bytes(saved)
 f.checked('callee 실패·None의 미연결 dispatch는 원래 private 다음 줄을 계속하며 private 분기17·부모 출력은 보존한다')
 f.stop();f.start(3);assert x.read()['diagnostics']['state']=='source-ready';assert x.read(x.caller)['diagnostics']['state']=='source-ready';print('M12_FORWARD_FIXTURE '+str(f.case),flush=True)
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
