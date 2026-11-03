"""Registered import receipt, immutable ownership, cold recovery and final raw CAS."""
import copy,json,hashlib
import v666_root_execution_imports_fixture as x
f=x.f
try:
 x.build('registered-import-before',x.x.result_code,x.x.initial_stdout);f.start(0);d=x.read();assert d['rootExecution'],d.get('rootExecutionError');assert len(d['rootExecutionDependencyHash'])==64
 assert all(not row['id'].startswith('External.Observed::') for row in d['sources'])
 req=x.request(d);before=x.checkpoint();x.original()
 for name in ['Value.celem','Scope.celem','Rules.celem','pack.cpack']:
  path=x.pack/name;x.mutate(path)
  try:x.rpc('authorBatch',False,**req)
  finally:x.restore(path)
  assert x.checkpoint()==before;x.original()
 path=x.pack/'pack.cpack';hidden=x.pack/'manifest temporarily absent';path.rename(hidden)
 try:x.rpc('authorBatch',False,**req)
 finally:hidden.rename(path)
 assert x.checkpoint()==before;x.original()
 f.checked('등록 함수·scope·manifest가 Save 전에 바뀌면 원래 dependency receipt로 전체 거절하며 외부 원본을 writable unit에 포함하지 않는다')
 saved=x.rpc('authorBatch',**req);assert saved['checkpointSaved'] and saved['settled'];assert x.rpc('settledAuthorBatch',**req)['settled'];x.original()
 checkpoint=x.checkpoint();rows={r['id']:r for r in json.loads(next(iter(checkpoint.values())))['changes']};receipt=rows[x.x.audit_impl]['rootExecutionImports'];assert set(receipt['headers'])>={x.foreign,x.scope,x.provider};assert all(not r['path'].endswith('.csbody') for r in receipt['observations']);assert all(r['hash'] for r in receipt['observations'])
 for kind in ['missing','text','path','raw','scope']:
  bad=copy.deepcopy(rows)
  if kind=='missing':bad[x.x.audit_impl].pop('rootExecutionImports')
  elif kind=='text':bad[x.x.audit_impl]['rootExecutionImports']['headers'][x.foreign]['text']+=' '
  elif kind=='path':bad[x.x.audit_impl]['rootExecutionImports']['headers'][x.foreign]['path']=str(x.pack/'Value.csbody')
  elif kind=='raw':bad[x.x.audit_impl]['rootExecutionImports']['observations'][0]['hash']='0'*64
  else:bad[x.x.audit_impl]['rootExecutionImports']['headers'].pop(x.scope)
  try:
   f.metadata('blueprintRootExecutionGuards',namespace=f.n[:-2],units=bad)
   f.metadata('blueprintOverrideContracts',action='verifyGroup',project=str(x.x.manifest),units=bad)
  except AssertionError:pass
  else:raise AssertionError('Registered receipt accepted '+kind)
 f.checked('외부 본문 읽기 없이 정확한 헤더·원시 관측을 저장하고 누락·본문경로 대체·text/raw 변조·scope 누락을 거절한다')
 f.stop();f.start(1);assert x.checkpoint()==checkpoint and x.rpc('settledAuthorBatch',**req)['settled'];d=x.read();assert d['rootExecution'];ids=d['reviewIds'];assert len(ids)==x.x.expected_review_members
 f.checked('cold 재시작 후 동일 외부 관측과 전체 후보를 복원하며 응답 재조회는 중복 저장하지 않는다')
 repeat=x.request(d);repeat['edits'][0]['definition']['branches'].reverse();repeat['edits'][0]['definition']['branches'][0]['name']='외부 관측 유지';x.rpc('authorBatch',**repeat);x.original()
 # Missing and changed current registrations must be rejected even after Review.
 for index,name in enumerate(['Value.celem','Scope.celem','Rules.celem','pack.cpack'],2):
  ids=x.read()['reviewIds'];review=f.invoke('reviewGroup',{'ids':ids});assert not review['state']['review'].get('errors'),review;checkpoint=x.checkpoint();path=x.pack/name;x.mutate(path)
  try:
   answer=f.invoke('confirmGroup',{'ids':ids,'token':review['state']['review']['token']})['result']['result'];assert answer['sourceConfirmed'] is False,answer
  finally:x.restore(path)
  assert x.checkpoint()==checkpoint;x.original();f.stop();f.start(index)
 f.checked('반복 이름·순서 편집을 보존하고 Review 뒤 함수·scope·manifest 경합은 최종 raw CAS에서 전체 미반영한다')
 ids=x.read()['reviewIds'];review=f.invoke('reviewGroup',{'ids':ids});assert not review['state']['review'].get('errors'),review;f.invoke('confirmGroup',{'ids':ids,'token':review['state']['review']['token']});x.build('registered-import-after');x.retained()
 f.stop();f.start(5);assert x.read()['rootExecution'];assert x.x.graph not in x.x.read(x.x.audit_graph)['reviewIds'];x.retained()
 f.checked('전체 Confirm과 실제 실행은 native/scoped import·out·legacy 의미와 readonly 원본을 보존하고 완료 receipt는 후속 편집을 잠그지 않는다')
 print('M12_IMPORTS_FIXTURE '+str(f.case),flush=True)
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
