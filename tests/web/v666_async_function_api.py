"""공개 완료의 일반 결과·연결과 원래 IO/C#·후보/CAS를 함께 보존한다."""
import copy,json
import v666_async_function_fixture as x
f=x.f
try:
 x.build('initial-public-completion',10,'callee:1\npublic:10\nafter:10');f.start(0);data=x.read();assert data['asyncTransition']['rootCompletion'];before=x.checkpoint();request=x.request(data);bad=copy.deepcopy(request);bad['sourceProof']='[]';x.rpc('authorBatch',False,**bad);assert x.checkpoint()==before;x.original();f.checked('공개 완료 동기 복귀도 전체 관측 source proof를 요구한다')
 result=x.rpc('authorBatch',**request);assert result['settled'];m=x.check_demoted();assert x.rpc('settledAuthorBatch',**request)['settled'];x.original();f.checked('공개 완료 ID/정수값과 literal 완료 연결·기존 local Result·원문을 한 후보로 보존한다')
 f.stop();f.start(1);assert x.check_demoted()==m and x.rpc('settledAuthorBatch',**request)['settled'];x.original();f.checked('cold/같은 응답 재조회는 공개 분기나 호출자 후보를 중복 생성하지 않는다')
 ids=x.read()['reviewIds'];f.invoke('reviewGroup',dict(ids=[x.graph]),False);v=f.invoke('reviewGroup',dict(ids=ids));assert not v['state']['review'].get('errors');saved=x.checkpoint();path=f.project/'PublicDone.node.json';source=path.read_bytes();path.write_bytes(source+b' ')
 try:r=f.invoke('confirmGroup',dict(ids=ids,token=v['state']['review']['token']))['result']['result'];assert not r['sourceConfirmed'];assert x.checkpoint()==saved
 finally:path.write_bytes(source)
 x.original();f.stop();f.start(2);x.confirm();x.code_unchanged();x.build('ordinary-not-selected',10,'callee:1\nafter:10');f.checked('부분 Review/Review 뒤 호출자 경합은 거절하고 기존 C#은 일반 완료를 자동 선택하지 않는다')
 assert x.public_select(m['id'],name='공개 완료')['settled'];x.confirm();x.code_unchanged();x.build('ordinary-selected',10,'callee:1\npublic:10\nafter:10');renamed=x.marker();assert renamed['id']==m['id']and renamed['value']==m['value']and renamed['name']=='공개 완료';f.checked('기존 Root 반환 편집의 명시 선택·이름 변경만 같은 public 완료 줄을 실행한다')
 d=x.read();saved=x.checkpoint();x.rpc('authorBatch',False,**x.request(d,True));assert x.checkpoint()==saved;x.code_unchanged();f.checked('일반 완료 반환이 남은 재활성화는 묵시적 None 변환 없이 입력을 보존한다')
 assert x.public_select()['settled'];x.confirm();d=x.read();r=x.request(d,True);assert x.rpc('authorBatch',**r)['settled'];x.confirm();x.code_unchanged();x.build('async-restored',10,'callee:1\npublic:10\nafter:10');assert x.marker()['id']==m['id'];f.checked('명시 반환 선택 해제 후 async 재활성화는 원래 완료 실행/IO와 같은 예약 ID를 복원한다')
 d=x.read();assert x.rpc('authorBatch',**x.request(d))['settled'];assert x.check_demoted()['id']==m['id'];x.confirm();x.code_unchanged();x.build('ordinary-repeat',10,'callee:1\nafter:10');f.checked('반복 전체 전환은 같은 public/local 분기와 원문을 유지한다')
 print(json.dumps({'checks':f.checks,'actualEngine':True,'actualWindows':False,'evidence':str(f.case)},ensure_ascii=False))
finally:f.stop()
