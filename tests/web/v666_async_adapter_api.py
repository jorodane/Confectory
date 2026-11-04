"""Result 없는 동작: 원문/출력 보존, 별도 선택과 전체 source CAS."""
import copy,json
import v666_async_adapter_fixture as x
f=x.f
try:
 x.build('initial',True);f.start(0);before=x.checkpoint();req=x.request(x.read());bad=copy.deepcopy(req);bad['sourceProof']='[]';x.rpc('authorBatch',False,**bad);assert x.checkpoint()==before;x.original()
 assert x.rpc('authorBatch',**req)['settled'];assert x.rpc('settledAuthorBatch',**req)['settled'];node=x.selected();marker=node['completionBranch'];assert node['completionAdapter']['source']=='return Result.None;' and node['signature']==x.signature and x.read()['edges']==x.initial_edges;x.original();f.checked('원문·native 반환/out·연결을 그대로 두고 별도 None 선택기를 저장한다')
 f.stop();f.start(1);assert x.selected()['completionBranch']==marker and x.rpc('settledAuthorBatch',**req)['settled'];x.confirm();x.code_unchanged();x.build('none');f.checked('cold/응답 재조회/최종 확정 뒤 None은 완료를 암묵 실행하지 않는다')
 req=x.edit(x.read(),x.selection());assert x.rpc('authorBatch',**req)['settled'];assert x.rpc('settledAuthorBatch',**req)['settled'];x.code_unchanged();ids=x.read()['reviewIds'];review=f.invoke('reviewGroup',{'ids':ids})['state']['review'];assert not review.get('errors'),review;before=x.checkpoint()
 path=f.project/'After.node.json';old=path.read_bytes();path.write_bytes(old+b' ')
 try:result=f.invoke('confirmGroup',{'ids':ids,'token':review['token']})['result']['result'];assert not result['sourceConfirmed'];assert x.checkpoint()==before
 finally:path.write_bytes(old)
 f.checked('확정 후 별도 선택기 편집도 다른 호출자 원문의 Review 이후 경합을 최종 CAS에서 거절한다')
 f.stop();f.start(2);x.confirm();x.build('explicit',True);x.code_unchanged();f.checked('readonly 출력/native 반환 snapshot으로 명시 선택한 완료만 다음 흐름 전에 실행한다')
 x.rpc('authorBatch',**x.edit(x.read(),'return Result.None;'));x.confirm();x.rpc('authorBatch',**x.request(x.read(),True));x.confirm();x.build('async-again',True);x.code_unchanged();assert x.selected()['completionBranch']['id']==marker['id'];f.checked('명시적 async 재전환은 같은 완료 ID와 원문·출력·다음 연결을 회복한다')
 print('ASYNC_ADAPTER_FIXTURE',f.case,flush=True)
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
