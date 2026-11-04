"""Whole-body root transition: native member identity and final source CAS."""
import copy,json
import v666_async_context_fixture as x
f=x.f
try:
 x.build('original');f.start(0);d=x.read();assert d.get('asyncTransition'),d.get('asyncError');assert not any(n['id']=='body'for n in d['asyncTransition']['nodes']);before=x.checkpoint()
 bad=x.request(d,nodes=[{'node':'body','enabled':True}]);x.rpc('authorBatch',False,**bad);assert x.checkpoint()==before;x.original();f.checked('native Invoke를 async 본문으로 묵시 변환하지 않고 함수 전체 전환만 명시한다')
 req=x.request(d);assert x.rpc('authorBatch',**req)['settled'];assert x.rpc('settledAuthorBatch',**req)['settled'];x.original();d=x.read(x.caller);assert 'GRAPH_ASYNC_CALLER_REQUIRED'in json.dumps(d['diagnostics']),d;f.checked('whole-body의 원문/문맥을 보존한 함수 전환은 동기 호출자를 자동 변경하지 않고 오류로 표시한다')
 demote=x.request(x.read(),enabled=False);assert x.rpc('authorBatch',**demote)['settled'];assert not x.read()['asyncTransition']['enabled'];promote=x.request(x.read());assert x.rpc('authorBatch',**promote)['settled'];assert x.read()['asyncTransition']['enabled'];x.original();d=x.read(x.caller);assert 'GRAPH_ASYNC_CALLER_REQUIRED'in json.dumps(d['diagnostics']),d;f.checked('호출자를 동기로 둔 채 같은 whole-body를 sync/async 왕복하며 명시 호출자 전환 오류를 유지한다');blocked_ids=x.read()['reviewIds'];rejected=f.invoke('reviewGroup',{'ids':blocked_ids})['state']['review'];unchanged=x.checkpoint();blocked=f.invoke('confirmGroup',{'ids':blocked_ids,'token':rejected['token']})['result']['result'];assert not blocked['sourceConfirmed'],blocked;assert x.checkpoint()==unchanged;x.original();d=x.read(x.caller);f.checked('미전환 동기 호출자의 후보는 저장되지만 Confirm의 실제 컴파일은 계속 거절한다')
 req2=x.request(d,x.caller);assert x.rpc('authorBatch',**req2)['settled'];saved=x.checkpoint();f.stop();f.start(1);assert saved==x.checkpoint();assert not x.rpc('settledAuthorBatch',**promote)['settled'];assert x.rpc('settledAuthorBatch',**req2)['settled'];x.original();ids=x.read()['reviewIds'];f.invoke('reviewGroup',{'ids':[x.graph]},False);review=f.invoke('reviewGroup',{'ids':ids})['state']['review'];assert not review.get('errors'),review;f.checked('명시한 호출자와 모든 target/원문 관측만 한 후보로 cold 복원·전체 Review한다')
 before=x.checkpoint();path=f.project/'CtxScope.celem';old=path.read_bytes();path.write_bytes(old+b' ')
 try:r=f.invoke('confirmGroup',{'ids':ids,'token':review['token']})['result']['result'];assert not r['sourceConfirmed'];assert x.checkpoint()==before
 finally:path.write_bytes(old)
 x.original();f.stop();f.start(2);ids=x.read()['reviewIds'];r=f.invoke('reviewGroup',{'ids':ids})['state']['review'];assert not r.get('errors'),r;f.invoke('confirmGroup',{'ids':ids,'token':r['token']});x.unchanged();x.build('async-confirmed');f.checked('scoped provider의 Review 이후 경합은 최종 CAS에서 거절하며 재시도 뒤 this/재귀/타입/원문 위치·CRLF·out/native를 실제 실행한다')
 f.stop();f.start(3);assert x.read()['diagnostics']['state']=='source-ready';assert x.read()['edges']==x.initial_edges;x.unchanged();f.checked('확정 cold는 원래 active Invoke와 ID/연결·scoped import를 복원한다');print('ASYNC_CONTEXT_FIXTURE',f.case,flush=True)
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
