"""Private sync demotion retains connected completion and native return data."""
import copy,json
import v666_async_private_returns_fixture as x
f=x.f
try:
 x.build('original-async',True);f.start(0);f.invoke('select',dict(id=x.feature));f.invoke('saveDraft',{});d=x.read();assert d['asyncTransition']['enabled'];preview=d['asyncTransition']['rootCompletion'];assert preview==next(n for n in x.read(x.graph)['asyncTransition']['nodes']if n['id']=='task')['demotion'];req=x.request(x.read(),enabled=False);x.rpc('authorBatch',**req);assert x.rpc('settledAuthorBatch',**req)['settled'];m=x.marker();assert m==preview;assert any(v['id']==m['id']for v in x.read()['executionEnum']['members']);assert not x.read()['asyncTransition']['enabled'];assert x.read(x.graph)['edges']==x.original_edges;assert json.loads(next(e['valueJson']for e in x.read()['exits']if e['name']=='done'))==dict(executionBranch='none',value=x.original_value);x.original();before=x.checkpoint();f.stop();f.start(1);assert x.checkpoint()==before and x.marker()==m;f.checked('내부 동기 복귀는 완료 실행선/분기 ID·native 반환·공개 계약·원문과 영수증을 보존한다')
 ids=x.read()['reviewIds'];f.invoke('reviewGroup',dict(ids=[x.leaf]),False);r=f.invoke('reviewGroup',dict(ids=ids))['state']['review'];assert not r.get('errors'),r;held=x.checkpoint();p=f.project/'Flow.node.json';old=p.read_bytes();p.write_bytes(old+b' ')
 try:v=f.invoke('confirmGroup',dict(ids=ids,token=r['token']))['result']['result'];assert not v['sourceConfirmed']and x.checkpoint()==held
 finally:p.write_bytes(old)
 x.original();x.confirm();x.unchanged();x.build('sync-none-is-not-completion',False);f.checked('부분 Review/최종 CAS 거절과 재시도 뒤 None은 완료 분기를 묵시적으로 선택하지 않는다')
 held=x.checkpoint()
 for invalid in ['native','branch']:
  bad=x.selection(m['id']);choice=bad['edits'][0]['definition']['exits']['done'];choice['value'if invalid=='native'else'executionBranch']={'constant':99}if invalid=='native'else'missing_branch';x.rpc('authorBatch',False,**bad);assert held==x.checkpoint();x.unchanged()
 f.checked('일반 완료 결과 편집에서 native 값 교체와 없는 분기는 거절하고 checkpoint/원문을 보존한다')
 x.select(m['id']);x.confirm();x.unchanged();x.build('explicit-ordinary-completion',True);f.stop();f.start(2);assert x.marker()==m and not x.read()['asyncTransition']['enabled'];assert x.read(x.graph)['edges']==x.original_edges;x.unchanged();f.checked('기존 반환 노드에서 일반 완료 결과를 명시 선택하면 같은 실행선이 같은 native 값으로 한 번 실행되고 cold 복원한다')
 held=x.checkpoint();x.rpc('authorBatch',False,**x.request(x.read(),enabled=True));assert held==x.checkpoint();x.select('none');x.rpc('authorBatch',**x.request(x.read(),enabled=True));x.confirm();x.unchanged();x.build('explicit-task-again',True);assert x.read(x.graph)['edges']==x.original_edges;f.checked('기존 반환 선택을 암묵 치환하지 않으며 명시 None 선택 후 같은 Task 완료선으로 재전환한다');print('ASYNC_PRIVATE_RETURNS_FIXTURE',f.case,flush=True)
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
