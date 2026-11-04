"""Contained creation, binding, async execution and final owner/manifest CAS."""
import json
import v666_async_information_fixture as x
f=x.f
try:
 x.run(f.project,'original-main',7,'');f.start(0);x.create();d=x.read();assert d.get('asyncTransition'),d.get('asyncError');before=x.checkpoint();x.original();f.checked('정보 자체 함수와 첫 구현은 기존 contain/provide 생성 그룹을 유지하며 async 메뉴를 제공한다')
 req=x.request(d);assert x.rpc('authorBatch',**req)['settled'];assert x.rpc('settledAuthorBatch',**req)['settled'];assert x.read()['asyncTransition']['enabled'];saved=x.checkpoint();f.stop();f.start(1);assert saved==x.checkpoint();assert x.rpc('settledAuthorBatch',**req)['settled'];x.original();assert not any(p.exists()for p in x.paths.values());f.checked('정보 owner·배정·첫 계약과 새 파일 부재 조건/receipt를 cold 복원한다')
 d=x.read();x.rpc('source',id=x.graph,node='body',text=x.new_source,basis=d['basis']);f.invoke('saveDraft',{});ids=x.read()['reviewIds'];assert x.owner in ids and x.feature in ids and x.graph in ids;f.invoke('reviewGroup',{'ids':[x.graph]},False)
 for name in ['FreeInfo.celem','project.cproj']:
  r=f.invoke('reviewGroup',{'ids':ids})['state']['review'];assert not r.get('errors'),r;p=f.project/name;old=p.read_bytes();before=x.checkpoint();p.write_bytes(old+b' ')
  try:
   result=f.invoke('confirmGroup',{'ids':ids,'token':r['token']})['result']['result'];assert not result['sourceConfirmed'];assert before==x.checkpoint();assert not any(p.exists()for p in x.paths.values())
  finally:p.write_bytes(old)
  x.original();f.checked('Review 뒤 '+name+' 변경은 전체 생성/비동기 저장을 final CAS에서 거절한다')
 f.stop();f.start(2);ids=x.read()['reviewIds'];r=f.invoke('reviewGroup',{'ids':ids})['state']['review'];result=f.invoke('confirmGroup',{'ids':ids,'token':r['token']})['result']['result'];assert result['sourceConfirmed'],result;x.unchanged();assert all(p.exists()for p in x.paths.values());assert json.loads(x.paths[x.graph+'/node:body'].read_text())['source']==x.new_source;x.build_new('owned-scope-entry');x.reject_sync('sync-scope-rejection');x.run(f.project,'unchanged-entry',7,'');f.stop();f.start(3);assert x.read()['diagnostics']['state']=='source-ready';x.unchanged();f.checked('동일 정보 scope의 명시 async caller는 실제 await 뒤 실행하고 원래 진입/C#과 다른 데이터는 유지하며 미전환 동기 호출자는 오류로 거절한다');print('ASYNC_INFORMATION_FIXTURE',f.case,flush=True)
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
