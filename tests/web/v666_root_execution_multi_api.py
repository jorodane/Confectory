"""Real multi-caller/target candidate, source CAS, cold and execution checks."""
import copy,hashlib,json
import v666_root_execution_multi_fixture as x
f=x.f
try:
 x.build('before',x.result_code,x.initial_stdout)
 f.start(0);d=x.read();assert d['rootExecution'],d.get('rootExecutionError');choices=d['rootExecution'];expected_calls=0 if x.no_callers else (3 if x.single else 5);assert len(choices['callers'])==expected_calls;assert len(choices['targets'])==(4 if x.providers_mode else 1 if x.single else 2)
 units={r['id']:{'kind':r['kind'],'path':r['path'],'draft':(f.project/r['path']).read_text()} for r in d['sources']}
 pure=f.metadata('blueprintRootExecution',namespace='Owned.Elements',id=x.graph,units=units,plan=x.plan(d));expected_group=4+(0 if x.single else 2)+(0 if x.no_callers else 8+(0 if x.single else 2))+(6 if x.providers_mode else 0);assert len(pure['group'])==expected_group,(pure['group'],expected_group)
 for unit in pure['units'].values():unit['baseline']=hashlib.sha256((f.project/unit['path']).read_bytes()).hexdigest()
 assert len(f.metadata('blueprintRootExecutionGuards',namespace='Owned.Elements',units=pure['units'])['checks'])==expected_group
 if x.providers_mode:
  assert pure['observedContracts']==[x.support]
  assert len({t['name'] for t in choices['targets']})==4
  restored=copy.deepcopy(pure['units']);restored.pop(x.alternative+'/body:linux')
  try:f.metadata('blueprintRootExecutionGuards',namespace='Owned.Elements',units=restored)
  except AssertionError as error:assert 'Complete owned execution branch review group' in str(error),error
  else:raise AssertionError('Missing provider accepted in restored group')
  for mutation in ['opaque','override','aliased-graph']:
   bad=copy.deepcopy(units)
   if mutation=='opaque':bad[x.alternative]['draft']=bad[x.alternative]['draft'].replace('blueprint common "Alternativecommon.graph.json"','body common "Original.csbody"')
   elif mutation=='override':bad[x.alternative]['draft']=bad[x.alternative]['draft'].replace(' -> void {',' -> void extends '+x.impl+' {')
   else:
    bad[x.alternative]['draft']=bad[x.alternative]['draft'].replace('Alternativecommon.graph.json','./Flow.graph.json');bad[x.alternative+'/body:common']['path']='./Flow.graph.json'
   try:f.metadata('blueprintRootExecutionCandidates',id=x.graph,units=bad)
   except AssertionError as error:
    assert {'opaque':'preserve opaque sources','override':'Override contracts','aliased-graph':'Aliased target files'}[mutation] in str(error),error
   else:raise AssertionError('Unsafe provider accepted: '+mutation)
  f.checked('다른 provider의 import도 readonly 관측하며 opaque·override·같은 물리 그래프는 자동 변환 없이 거절한다')
 before=x.checkpoint();req=x.request(d);x.original();f.checked('여러 호출 위치/target을 원래 ID와 out 계약의 명시 대응 후보로 관측하며 자동 선택하지 않는다')
 negative=['missing-caller','extra-target','stale-proof','bad-branch']
 if expected_calls:negative+=['duplicate-caller']
 if not x.single:negative+=['missing-target','invalid-last-target']
 for kind in negative:
  bad=copy.deepcopy(req);plan=bad['edits'][0]['definition']
  if kind=='missing-caller':
   if plan['callers']:plan['callers'].pop()
   else:plan['callers'].append({'graph':x.caller,'node':'invoke'})
  elif kind=='duplicate-caller':plan['callers'].append(copy.deepcopy(plan['callers'][0]))
  elif kind=='extra-target':plan['targets'].append({'graph':'Owned.Elements::Unknown/body:common','entry':'','edges':[],'exits':{}})
  elif kind=='missing-target':plan['targets'].pop()
  elif kind=='invalid-last-target':plan['targets'][-1]['exits']['yes']={'executionBranch':'missing'}
  elif kind=='bad-branch':plan['branches'][0]['id']='../escape'
  else:bad['sourceProof']=bad['sourceProof'].replace(d['sources'][0]['hash'],'0'*64)
  x.rpc('authorBatch',False,**bad);assert x.checkpoint()==before;x.original()
 f.checked('호출 누락/중복·target 누락/추가·마지막 target 오류·낡은 증거는 모두 미적용하고 입력과 원본을 보존한다')
 conflict=f.project/('Flow.node.json' if x.no_callers else 'PeerAfter.node.json');conflict.write_bytes(x.physical[conflict]+b' ');x.rpc('authorBatch',False,**req);conflict.write_bytes(x.physical[conflict]);assert x.checkpoint()==before;x.original();f.checked('다른 호출자/target의 물리 원문 경합도 전체 후보 저장 전에 거절한다')
 saved=x.rpc('authorBatch',**req);assert saved['settled'] and saved['checkpointSaved'];assert x.rpc('settledAuthorBatch',**req)['settled'];assert len(x.read()['reviewIds'])>=expected_group;x.original();checkpoint=x.checkpoint()
 f.stop();f.start(1);assert x.checkpoint()==checkpoint;assert x.rpc('settledAuthorBatch',**req)['settled'];assert x.read()['diagnostics']['state']=='source-ready';x.original();f.checked('전체 후보는 한 checkpoint CAS와 완전 Review 그룹이며 cold/receipt 재시도가 부분 저장이나 중복 저장을 만들지 않는다')
 f.invoke('reviewGroup',{'ids':[x.graph]},False);ids=x.read()['reviewIds'];review=f.invoke('reviewGroup',{'ids':ids,'target':'portable'});assert not review['state']['review'].get('errors');x.original();checkpoint=x.checkpoint();conflict=f.project/('Alternativecommon.node.json' if x.providers_mode else 'Flow.node.json' if x.single else 'FlowLinux.node.json');conflict.write_bytes(x.physical[conflict]+b' ');result=f.invoke('confirmGroup',{'ids':ids,'token':review['state']['review']['token']})['result']['result'];assert result['sourceConfirmed'] is False;conflict.write_bytes(x.physical[conflict]);assert x.checkpoint()==checkpoint;x.original();f.checked('부분 Review와 Review 뒤 다른 target의 원문 변경을 최종 CAS에서 거절하고 전체 저장 입력을 유지한다')
 if x.providers_mode:
  f.stop();f.start(11);ids=x.read()['reviewIds'];review=f.invoke('reviewGroup',{'ids':ids,'target':'portable'});checkpoint=x.checkpoint();support=f.project/'Support.celem';support.chmod(0o600)
  try:
   support.write_bytes(x.physical[support]+b' ');result=f.invoke('confirmGroup',{'ids':ids,'token':review['state']['review']['token']})['result']['result'];assert result['sourceConfirmed'] is False
  finally:support.write_bytes(x.physical[support]);support.chmod(0o400)
  assert x.checkpoint()==checkpoint;x.original();f.checked('다른 provider만 관측하는 readonly import도 Review 뒤 변경을 최종 CAS에서 전체 거절한다')
 f.stop();f.start(2);ids=x.read()['reviewIds'];review=f.invoke('reviewGroup',{'ids':ids,'target':'portable'});f.invoke('confirmGroup',{'ids':ids,'token':review['state']['review']['token']})
 records={p:v for p,v in x.physical.items() if p.suffix=='.csbody' or p.name.endswith('.node.json')}
 def original_records():assert all(p.read_bytes()==v for p,v in records.items())
 original_records();x.build('common-after')
 if not x.single:x.build('linux-after',target='linux')
 if not x.no_callers:
  x.build('peer-after',entry='Peer')
  if not x.single:x.build('peer-linux-after',entry='Peer',target='linux')
 f.checked('명시 Confirm 뒤 각 target과 서로 다른 호출자에서 공개 분기와 out을 실제 실행하고 원래 C# 및 기존 IInvoke를 보존한다')
 if x.providers_mode:
  assert (f.project/'Peer.celem').read_bytes()==x.physical[f.project/'Peer.celem']
  assert (f.project/'Support.celem').read_bytes()==x.physical[f.project/'Support.celem']
  f.checked('기존 scoped 배정으로 선택한 두 provider를 각 target에서 실행하며 임의 provider 선택·배정 변경을 하지 않는다')
 f.stop();f.start(3);d=x.read(x.alternative+'/body:linux' if x.providers_mode else x.graph if x.single else x.linux);follow=x.plan(d);follow['branches'].reverse();next(b for b in follow['branches'] if b['id']=='success')['name']='성공 이름 변경';before_files={p:p.read_bytes() for p in x.physical};repeat_units={r['id']:{'kind':r['kind'],'path':r['path'],'draft':(f.project/r['path']).read_text()} for r in d['sources']};f.metadata('blueprintRootExecution',namespace='Owned.Elements',id=d['id'],units=repeat_units,plan=follow);(f.case/'repeat-request.json').write_text(json.dumps(x.request(d,follow),ensure_ascii=False,indent=2));x.rpc('authorBatch',**x.request(d,follow));assert all(p.read_bytes()==v for p,v in before_files.items());assert [b['id'] for b in x.read()['rootExecution']['branches']]==['failure','success'];f.stop();f.start(4);ids=x.read()['reviewIds'];review=f.invoke('reviewGroup',{'ids':ids,'target':'portable'});f.invoke('confirmGroup',{'ids':ids,'token':review['state']['review']['token']});original_records();x.build('renamed-after');f.checked('반복 편집·이름/순서 변경도 기존 ID/값·모든 호출/target 대응·C# 바이트를 유지해 한 후보로 재저장·재시작·실행한다')
 print('M12_MULTI_FIXTURE '+str(f.case),flush=True)
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
