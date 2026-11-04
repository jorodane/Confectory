"""New declaration/registration/header/graph/code transition remains one CAS."""
import json
import v666_async_new_function_fixture as x
f=x.f
try:
 x.run(f.project,'original-main',7,'');f.start(0);x.create();d=x.read();assert d.get('asyncTransition'),d.get('asyncError');before=x.checkpoint();x.original();f.checked('기존 생성 API의 새 함수/구현/graph/코드는 파일 없이 등록 초안에서 async 메뉴를 제공한다')
 req=x.request(d);assert x.rpc('authorBatch',**req)['settled'];assert x.rpc('settledAuthorBatch',**req)['settled'];assert x.read()['asyncTransition']['enabled'];saved=x.checkpoint();f.stop();f.start(1);assert saved==x.checkpoint();assert x.rpc('settledAuthorBatch',**req)['settled'];x.original();assert not any(p.exists()for p in x.paths.values());f.checked('새 함수의 첫 전환 계약/등록/파일 부재 조건과 영수증을 cold 복원한다')
 ids=x.read()['reviewIds'];f.invoke('reviewGroup',{'ids':[x.graph]},False);r=f.invoke('reviewGroup',{'ids':ids})['state']['review'];before=x.checkpoint();failed=f.invoke('confirmGroup',{'ids':ids,'token':r['token']})['result']['result'];assert not failed['sourceConfirmed'];assert before==x.checkpoint();x.original();assert not any(p.exists()for p in x.paths.values());f.checked('int 본문이 아직 비어 있으면 실제 compiler Confirm을 거절하고 새 파일과 기존 진입 원문을 보존한다')
 d=x.read();x.rpc('source',id=x.graph,node='body',text=x.new_source,basis=d['basis']);f.invoke('saveDraft',{});ids=x.read()['reviewIds'];r=f.invoke('reviewGroup',{'ids':ids})['state']['review'];assert not r.get('errors'),r;p=f.project/'project.cproj';old=p.read_bytes();before=x.checkpoint();p.write_bytes(old+b' ')
 try:result=f.invoke('confirmGroup',{'ids':ids,'token':r['token']})['result']['result'];assert not result['sourceConfirmed'];assert before==x.checkpoint();assert not any(p.exists()for p in x.paths.values())
 finally:p.write_bytes(old)
 x.original();f.checked('Review 뒤 기존 프로젝트 등록이 바뀌면 모든 새 헤더/graph/코드 파일을 final CAS에서 거절한다')
 f.stop();f.start(2);ids=x.read()['reviewIds'];r=f.invoke('reviewGroup',{'ids':ids})['state']['review'];result=f.invoke('confirmGroup',{'ids':ids,'token':r['token']})['result']['result'];assert result['sourceConfirmed'],result;x.unchanged();assert all(p.exists()for p in x.paths.values());assert json.loads(x.paths[x.graph+'/node:body'].read_text())['source']==x.new_source;x.build_new('new-entry');x.run(f.project,'unchanged-entry',7,'');f.stop();f.start(3);assert x.read()['diagnostics']['state']=='source-ready';x.unchanged();f.checked('확정한 새 async 기능을 명시 Entry 복사본에서 실제 실행하고 원래 프로젝트의 진입/원문/실행도 보존한다');print('ASYNC_NEW_FUNCTION_FIXTURE',f.case,flush=True)
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
