import copy,json,pathlib,sys,uuid
import v666_root_execution_fixture as x
f=x.f
try:
 x.build('initial',x.result_code,x.initial_stdout);f.start(0)
 d=x.read();assert d.get('asyncTransition') is not None,d.get('asyncError');f.checked('직접 소유한 기존 함수의 전환 후보와 원래 target을 확인한다')
 def convert(graph,nodes):
  d=x.read(graph);req=dict(id=graph,attempt=uuid.uuid4().hex,checkpointHash=d['checkpointHash'],sourceProof=x.proof(d),edits=[dict(action='asyncTransition',node='$root',definition=dict(enabled=True,nodes=nodes))]);r=x.rpc('authorBatch',**req);assert r['settled'] and r['checkpointSaved'],r;assert x.rpc('settledAuthorBatch',**req)['settled'];x.original();return req
 before=x.checkpoint();initial=x.read();bad=dict(id=x.graph,attempt=uuid.uuid4().hex,checkpointHash=initial['checkpointHash'],sourceProof=x.proof(initial),edits=[dict(action='asyncTransition',node='$root',definition=dict(enabled=True,nodes=[dict(node='unknown',enabled=True)]))]);x.rpc('authorBatch',False,**bad);assert x.checkpoint()==before;x.original()
 first=convert(x.graph,[dict(node='choose',enabled=True)]);f.checked('명시 함수와 동작 전환은 원본 C#과 동기 호출자를 바꾸지 않고 checkpoint에 저장한다')
 d=x.read(x.caller);assert d.get('asyncTransition') is not None,d.get('asyncError');assert d['diagnostics']['state']=='invalid',d['diagnostics'];assert 'GRAPH_ASYNC_CALLER_REQUIRED' in json.dumps(d['diagnostics']),d['diagnostics'];f.checked('남은 동기 호출자는 자동 전환 없이 실제 호환 오류로 표시한다')
 saved=x.checkpoint();f.stop();f.start(1);assert x.checkpoint()==saved;assert x.rpc('settledAuthorBatch',**first)['settled'];f.checked('cold 재시작에서 전환 후보와 응답 조회를 복원한다')
 second=convert(x.caller,[]);d=x.read(x.graph);code=next(n for n in d['nodes'] if n['id']=='choose');body=dict(executionEnum=code['executionEnum'],source=code['source'],helpers=code.get('helpers') or '');request=dict(id=x.graph,attempt=uuid.uuid4().hex,checkpointHash=d['checkpointHash'],sourceProof=x.proof(d),edits=[dict(action='enumCode',node='choose',definition=body)]);assert x.rpc('authorBatch',**request)['settled'];x.original();f.checked('저장된 async 그래프의 기존 enum C# 편집 경로가 원문과 완료 계약을 유지한다');d=x.read(x.graph);x.rpc('route',id=x.graph,node='choose',basis=d['basis'],port='completion',to='return:choose');f.invoke('saveDraft',{});assert any(e['port']=='completion' for e in x.read()['edges']);f.checked('완료 연결을 원래 분기 소유자의 continuation으로 저장한다');d=x.read(x.graph);ids=d['reviewIds'];assert len(ids)>4,ids
 f.invoke('reviewGroup',{'ids':[x.graph]},False);v=f.invoke('reviewGroup',{'ids':ids});assert not v['state']['review'].get('errors'),v['state']['review'];x.original();f.checked('명시 호출자 전환의 완전 원자 그룹만 Review하고 원본을 보존한다')
 review_before=x.checkpoint();observed=f.project/'Native.celem';old=observed.read_bytes();observed.write_bytes(old+b' ')
 try:
  failed=f.invoke('confirmGroup',{'ids':ids,'token':v['state']['review']['token']})['result']['result'];assert not failed['sourceConfirmed'];assert x.checkpoint()==review_before
 finally:observed.write_bytes(old)
 x.original();f.stop();f.start(2);ids=x.read()['reviewIds'];v=f.invoke('reviewGroup',{'ids':ids});assert not v['state']['review'].get('errors');f.checked('Review 뒤 관측 헤더 변경은 최종 CAS에서 전체 미반영하고 재시도 후보를 유지한다')
 f.invoke('confirmGroup',{'ids':ids,'token':v['state']['review']['token']});x.build('async-confirmed',x.result_code,x.initial_stdout)
 for name in ['Flow.node.json','After.node.json']:assert json.loads((f.project/name).read_text())['source']==json.loads(x.physical[f.project/name])['source']
 f.checked('Confirm 뒤 원래 C#과 출력/분기를 유지하며 실제 Task 호출을 실행한다')
 print('ASYNC_FIXTURE',f.case,flush=True)
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
