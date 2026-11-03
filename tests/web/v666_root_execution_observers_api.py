"""Actual ordinary consumer compatibility, receipt-only updates and source CAS."""
import copy,hashlib,json,uuid
import v666_root_execution_observers_fixture as x
f=x.f
def change(name,value):
 p=f.project/name;mode=p.stat().st_mode&0o777;p.chmod(0o600)
 try:p.write_bytes(value)
 finally:p.chmod(mode)
def guards(rows):return f.metadata('blueprintRootExecutionGuards',namespace='Owned.Elements',units=rows)
try:
 x.build('observers-before',x.result_code,x.initial_stdout);f.start(0);d=x.read();assert d['rootExecution'],d.get('rootExecutionError')
 choices=d['rootExecution'];assert [(r['graph'],r['node']) for r in choices['callers']]==[(x.caller,'invoke')];assert set(choices['observers'])=={x.audit_graph,x.legacy_graph};assert choices['observedContracts']==[x.scope]
 units={r['id']:{'kind':r['kind'],'path':r['path'],'draft':(f.project/r['path']).read_text()} for r in d['sources']}
 pure=f.metadata('blueprintRootExecution',namespace='Owned.Elements',id=x.graph,units=units,plan=x.plan(d));assert len(pure['group'])==x.expected_review_members,pure['group']
 record=json.loads(pure['units'][x.audit_source_id]['draft']);x.preserved(record);assert record['definitionHash']!=x.audit_record['definitionHash']
 for unit in pure['units'].values():unit['baseline']=hashlib.sha256((f.project/unit['path']).read_bytes()).hexdigest()
 assert len(guards(pure['units'])['checks'])==x.expected_review_members
 f.checked('직접 public caller만 명시 대응하고 native/legacy ordinary 소비자는 전체 관측하며, C#·graph·IO·readonly 원본은 유지하고 생성 receipt만 갱신한다')
 for kind in ['stale-code','missing-code','missing-target','wrong-context','fake-public-wrapper']:
  bad=copy.deepcopy(units)
  if kind=='stale-code':
   node=json.loads(bad[x.audit_source_id]['draft']);node['definitionHash']='0'*64;bad[x.audit_source_id]['draft']=json.dumps(node)
  elif kind=='missing-code':bad.pop(x.audit_source_id)
  elif kind=='missing-target':bad.pop(x.audit_graph)
  elif kind=='wrong-context':
   body=json.loads(bad[x.audit_graph]['draft']);body['nodes'][0]['implementationContext']['implementation']=x.impl;bad[x.audit_graph]['draft']=json.dumps(body)
  else:
   body=json.loads(bad[x.legacy_graph]['draft']);body['nodes'][0]['publicExecution']='0'*64;bad[x.legacy_graph]['draft']=json.dumps(body)
  try:f.metadata('blueprintRootExecutionCandidates',id=x.graph,units=bad)
  except AssertionError:pass
  else:raise AssertionError('Implicit source repair or lost ordinary context accepted: '+kind)
 before=x.checkpoint();req=x.request(d);bad=copy.deepcopy(req);bad['edits'][0]['definition']['caller'].update(graph=x.legacy_graph,node='wrapped');x.rpc('authorBatch',False,**bad);assert x.checkpoint()==before;x.original()
 for name in ['Audit.node.json','AuditScope.celem']:
  change(name,x.physical[f.project/name]+b' ')
  try:x.rpc('authorBatch',False,**req)
  finally:change(name,x.physical[f.project/name])
  assert x.checkpoint()==before;x.original()
 f.checked('낡은 native receipt·누락 target/원문·다른 소유 문맥·legacy 자동 public 전환 및 Save 전 C#/scope 경합은 전체 거절한다')
 saved=x.rpc('authorBatch',**req);assert saved['settled'] and saved['checkpointSaved'];assert x.rpc('settledAuthorBatch',**req)['settled'];x.original();assert x.read(x.audit_graph)['diagnostics']['state']=='source-ready';assert x.read(x.legacy_graph)['diagnostics']['state']=='source-ready'
 saved=x.checkpoint();rows={row['id']:row for row in json.loads(next(iter(saved.values())))['changes']};stored=json.loads(rows[x.audit_source_id]['draft']);assert stored==record
 for kind in ['missing-observer','stale-native','missing-receipt','tampered-scope']:
  bad=copy.deepcopy(rows)
  if kind=='missing-observer':bad.pop(x.audit_graph)
  elif kind=='stale-native':
   node=json.loads(bad[x.audit_source_id]['draft']);node['definitionHash']='0'*64;bad[x.audit_source_id]['draft']=json.dumps(node)
  elif kind=='missing-receipt':bad[x.graph].pop('authorSaveReceipt')
  else:bad[x.graph]['authorSaveReceipt']['sources'][x.scope]['hash']='0'*64
  try:guards(bad)
  except AssertionError:pass
  else:raise AssertionError('Corrupt observed execution group accepted: '+kind)
 f.stop();f.start(1);assert x.checkpoint()==saved and x.rpc('settledAuthorBatch',**req)['settled'];assert len(x.read()['reviewIds'])==x.expected_review_members
 f.checked('전체 후보·관측 receipt·생성 hash를 한 checkpoint에 저장하고 missing/tampered 그룹을 거절하며 cold 재조회는 중복 저장하지 않는다')
 repeated=x.request(x.read());branches=repeated['edits'][0]['definition']['branches'];branches.reverse();branches[0]['name']='실패 이름';branches[1]['name']='성공 이름';x.rpc('authorBatch',**repeated);x.original();assert x.read(x.audit_graph)['diagnostics']['state']=='source-ready';assert x.read(x.legacy_graph)['diagnostics']['state']=='source-ready'
 f.invoke('reviewGroup',{'ids':[x.graph]},False);f.checked('반복 이름·순서 편집도 ordinary source를 유지하며 부분 Review는 거절한다')
 for index,name in enumerate(['Audit.node.json','AuditScope.celem'],2):
  ids=x.read()['reviewIds'];view=f.invoke('reviewGroup',{'ids':ids});assert not view['state']['review'].get('errors');checkpoint=x.checkpoint();change(name,x.physical[f.project/name]+b' ')
  try:answer=f.invoke('confirmGroup',{'ids':ids,'token':view['state']['review']['token']})['result']['result'];assert answer['sourceConfirmed'] is False
  finally:change(name,x.physical[f.project/name])
  assert x.checkpoint()==checkpoint;x.original();f.stop();f.start(index)
 f.checked('Review 뒤 native 원문과 readonly scope 경합을 최종 raw CAS에서 전체 미반영하고 재시작 입력을 보존한다')
 ids=x.read()['reviewIds'];view=f.invoke('reviewGroup',{'ids':ids});assert not view['state']['review'].get('errors');f.invoke('confirmGroup',{'ids':ids,'token':view['state']['review']['token']});x.build('observers-after')
 f.checked('실제 실행에서 native this/소스 위치·out20과 legacy NoBranch0·기존17/out30을 보존하며 선택한 public caller만 반환한다')
 f.stop();f.start(4);assert x.read()['diagnostics']['state']=='source-ready';native=x.read(x.audit_graph);assert native['diagnostics']['state']=='source-ready';assert x.graph not in native['reviewIds']
 # Acknowledge must retire the completed producer group. A later explicit
 # consumer source edit uses its own normal authoring boundary and can be undone.
 changed=x.audit_source+'// 명시적인 후속 입력\r\n';x.rpc('source',id=x.audit_graph,basis=native['basis'],node=x.audit_node,text=changed);f.invoke('saveDraft',{});f.stop();f.start(5)
 restored={row['id']:row for row in json.loads(next(iter(x.checkpoint().values())))['changes']};assert json.loads(restored[x.audit_source_id]['draft'])['source']==changed
 native=x.read(x.audit_graph);assert x.graph not in native['reviewIds'];x.rpc('source',id=x.audit_graph,basis=native['basis'],node=x.audit_node,text=x.audit_source);f.invoke('saveDraft',{});x.preserved(json.loads((f.project/'Audit.node.json').read_text()))
 f.checked('완료 그룹은 퇴역하여 후속 native 원문 입력을 독립 저장·cold 복원·명시 되돌림하며 원본은 추가 반영하지 않는다')
 print('M12_OBSERVERS_FIXTURE '+str(f.case),flush=True)
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
