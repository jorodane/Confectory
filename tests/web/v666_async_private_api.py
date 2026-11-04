"""Actual private Task Save, cold restore and complete final-CAS failure."""
import json
import v666_async_private_fixture as x
f=x.f
try:
 x.build('original');f.start(0);f.invoke('select',dict(id=x.feature));f.invoke('saveDraft',{});x.original();assert x.read()['asyncTransition']['enabled']is False
 x.parent();d=x.read();assert d['asyncTransition']['enabled'];req=x.request(d,[dict(node='body',enabled=True)]);x.rpc('authorBatch',**req);assert x.rpc('settledAuthorBatch',**req)['settled'];assert x.read()['asyncTransition']['nodes'][0]['enabled'];x.original();before=x.checkpoint();f.stop();f.start(1);assert before==x.checkpoint();assert x.rpc('settledAuthorBatch',**req)['settled'];x.original();f.checked('명시 내부 Task·leaf 전환은 원문/공개 계약을 보존하고 전체 receipt를 cold 복원한다')
 d=x.read();ids=d['reviewIds'];f.invoke('reviewGroup',dict(ids=[x.leaf]),False);r=f.invoke('reviewGroup',dict(ids=ids))['state']['review'];assert not r.get('errors'),r;review_before=x.checkpoint();p=f.project/'Flow.node.json';old=p.read_bytes();p.write_bytes(old+b' ')
 try:
  v=f.invoke('confirmGroup',dict(ids=ids,token=r['token']))['result']['result'];assert not v['sourceConfirmed'];assert review_before==x.checkpoint()
 finally:p.write_bytes(old)
 x.original();f.checked('부분 Review와 Review 뒤 private 원문 충돌은 전체 저장을 거절하고 후보를 보존한다');f.stop();f.start(2);x.confirm();x.unchanged();x.build('confirmed');f.stop();f.start(3);assert x.read()['diagnostics']['state']=='source-ready';x.unchanged();f.checked('Confirm 뒤 원문/공개 계약/호출자/실행선을 유지하고 실제 Task와 확정 cold를 실행한다');print('ASYNC_PRIVATE_FIXTURE',f.case,flush=True)
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
