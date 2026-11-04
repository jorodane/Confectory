"""Real missing-source creation, blank transition, source edit and final creation CAS."""
import json
import v666_async_creating_fixture as x
f=x.f
try:
 x.build('original');f.start(0);x.create();assert not x.path().exists();unit=x.draft_unit();assert unit['baseline']=='missing'and unit['original']=='';d=x.read();assert d.get('asyncTransition'),d.get('asyncError');assert any(n['id']==x.node for n in d['asyncTransition']['nodes']);x.original();f.checked('기존 생성 API의 새 record는 첫 Confirm 전 물리 파일 없이 직접 소유 Root에 남는다')
 req=x.transition(d);assert x.rpc('authorBatch',**req)['settled'];assert x.rpc('settledAuthorBatch',**req)['settled'];unit=x.draft_unit();r=json.loads(unit['draft']);assert r['source']==''and r['definitionHash']!='0'*64;assert not x.path().exists();saved=x.checkpoint();f.stop();f.start(1);assert saved==x.checkpoint();assert x.rpc('settledAuthorBatch',**req)['settled'];x.original();f.checked('빈 새 동작의 명시 async 전환은 코드 자동 작성 없이 missing CAS와 영수증을 cold 복원한다')
 d=x.read();x.rpc('source',id=x.graph,node=x.node,text=x.new_source,basis=d['basis']);f.invoke('saveDraft',{});unit=x.draft_unit();assert unit['baseline']=='missing'and json.loads(unit['draft'])['source']==x.new_source;ids=x.read()['reviewIds'];f.invoke('reviewGroup',{'ids':[x.graph]},False);review=f.invoke('reviewGroup',{'ids':ids})['state']['review'];assert not review.get('errors'),review;before=x.checkpoint();p=x.path();p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'peer source that must survive')
 try:
  failed=f.invoke('confirmGroup',{'ids':ids,'token':review['token']})['result']['result'];(f.case/'new-file-conflict.json').write_text(json.dumps(failed,ensure_ascii=False,indent=2));assert not failed['sourceConfirmed'];assert p.read_bytes()==b'peer source that must survive';assert x.checkpoint()==before;x.original()
 finally:p.unlink()
 f.checked('새 파일 경로에 Review 후 원본이 나타나면 final CAS가 전체 Confirm을 거절하고 상대 파일·입력을 보존한다')
 f.stop();f.start(2);ids=x.read()['reviewIds'];review=f.invoke('reviewGroup',{'ids':ids})['state']['review'];assert not review.get('errors'),review;result=f.invoke('confirmGroup',{'ids':ids,'token':review['token']})['result']['result'];assert result['sourceConfirmed'];x.unchanged();assert json.loads(x.path().read_text())['source']==x.new_source;x.build('new-confirmed',True);f.stop();f.start(3);assert x.read()['diagnostics']['state']=='source-ready';assert x.path().is_file();x.unchanged();f.checked('명시 새 C#을 확정한 뒤 실제 await→다음 실행과 새 파일/기존 원문·ID·함수 계약을 cold에서 복원한다');print('ASYNC_CREATING_FIXTURE',f.case,flush=True)
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
