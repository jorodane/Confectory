"""완료의 일반 Result 복귀: 실제 저장/복원/CAS와 실행 의미를 분리한다."""
import copy,json
import v666_async_completion_fixture as x
f=x.f
try:
 x.build('initial',10,'callee:1\ncompleted:10\nafter:10');f.start(0);d=x.read();before=x.checkpoint();req=x.request(d);x.original()
 bad=copy.deepcopy(req);bad['sourceProof']='[]';x.rpc('authorBatch',False,**bad);assert x.checkpoint()==before;x.original();f.checked('완료 복귀에서도 낡은 전체 source proof는 원자 거절한다')
 result=x.rpc('authorBatch',**req);assert result['settled'];assert x.rpc('settledAuthorBatch',**req)['settled'];marker=x.check_demoted();x.original();f.checked('연결된 completion 키/목적지와 기존 Result ID/값·out·본문을 그대로 저장한다')
 saved=x.checkpoint();f.stop();f.start(1);assert x.checkpoint()==saved and x.check_demoted()==marker;assert x.rpc('settledAuthorBatch',**req)['settled'];x.original();f.checked('cold 복원과 응답 재조회는 같은 완료 ID/숫자/label과 후보를 유지한다')
 ids=x.read()['reviewIds'];f.invoke('reviewGroup',{'ids':[x.graph]},False);v=f.invoke('reviewGroup',{'ids':ids});assert not v['state']['review'].get('errors');x.original();review_checkpoint=x.checkpoint()
 other=f.project/'After.node.json';prior=other.read_bytes();other.write_bytes(prior+b' ')
 try:failed=f.invoke('confirmGroup',{'ids':ids,'token':v['state']['review']['token']})['result']['result'];assert not failed['sourceConfirmed'];assert x.checkpoint()==review_checkpoint
 finally:other.write_bytes(prior)
 x.original();f.stop();f.start(2);ids=x.read()['reviewIds'];v=f.invoke('reviewGroup',{'ids':ids});f.invoke('confirmGroup',{'ids':ids,'token':v['state']['review']['token']});x.run('ordinary-not-selected');x.run('ordinary-selected',True);f.checked('최종 CAS 뒤 기존 C#은 일반 완료 분기를 자동 실행하지 않고 명시 Result 선택만 그 줄을 실행한다')
 current=x.read();req=x.request(current,True);assert x.rpc('authorBatch',**req)['settled'];ids=x.read()['reviewIds'];v=f.invoke('reviewGroup',{'ids':ids});f.invoke('confirmGroup',{'ids':ids,'token':v['state']['review']['token']});x.code_unchanged();x.build('re-enabled',10,'callee:1\ncompleted:10\nafter:10');f.checked('같은 완료 연결을 async로 다시 전환하면 원문 재작성 없이 완료→결과→다음 순서를 회복한다')
 print('ASYNC_COMPLETION_FIXTURE',f.case,flush=True)
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
