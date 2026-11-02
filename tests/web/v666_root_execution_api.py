"""Real API/checkpoint/Confirm and execution checks for bounded M12."""
import copy,json,subprocess,stat
import v666_root_execution_fixture as x
f=x.f
try:
 units={}
 for id,kind,path in [(x.feature,'function','Flow.celem'),(x.impl,'implementation','FlowBody.celem'),(x.graph,'blueprint','Flow.graph.json'),(x.graph+'/node:choose','blueprint-node','Flow.node.json'),(f.n+'Main','function','Main.celem'),(f.n+'MainBody','implementation','MainBody.celem'),(x.caller,'blueprint','Main.graph.json'),(x.caller+'/node:after','blueprint-node','After.node.json')]:units[id]={'kind':kind,'path':path,'draft':(f.project/path).read_text()}
 if x.compound_mode:units[x.other_feature]={'kind':'function','path':'Other.celem','draft':(f.project/'Other.celem').read_text()}
 pure=f.metadata('blueprintRootExecution',namespace='Owned.Elements',id=x.graph,units=units,plan=x.plan({'entry':x.root['entry'],'edges':x.root['edges']}));assert len(pure['group'])==x.expected_review_members
 import hashlib
 for id,unit in pure['units'].items():unit['baseline']=hashlib.sha256((f.project/unit['path']).read_bytes()).hexdigest()
 assert len(f.metadata('blueprintRootExecutionGuards',namespace='Owned.Elements',units=pure['units'])['checks'])==x.expected_review_members
 def reject_metadata(rows):
  result=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps({'operation':'blueprintRootExecutionGuards','namespace':'Owned.Elements','units':rows}),text=True,capture_output=True,env=f.env,check=True);reply=json.loads(result.stdout);assert reply['ok'] is False,reply
 def header_bytes(value):
  path=f.project/'Other.celem';path.chmod(0o600)
  try:path.write_bytes(value)
  finally:path.chmod(0o400)
 if x.compound_mode:
  assert pure['observedContracts']==[x.other_feature]
  bad=copy.deepcopy(pure['units']);bad.pop(x.other_feature);reject_metadata(bad)
  bad=copy.deepcopy(pure['units']);bad[x.other_feature]['original']=bad[x.other_feature]['draft'];bad[x.other_feature]['draft']+=' ';reject_metadata(bad)
 x.build('before',x.result_code,x.initial_stdout);f.start(0);d=x.read();assert d['rootExecution'],d.get('rootExecutionError');assert d['rootExecution']['callers'][0]['graph']==x.caller;before=x.checkpoint();req=x.request(d);x.original();f.checked('원래 sync void 원문·일반 호출 실행과 명시 호출자 후보를 확인한다')
 for field in ['missing-caller','unknown-branch','stale-proof','bad-id','changed-value']+(['changed-data','missing-data'] if x.nonvoid_mode else []):
  bad=copy.deepcopy(req)
  if field=='missing-caller':bad['edits'][0]['definition']['caller']['graph']=''
  elif field=='unknown-branch':bad['edits'][0]['definition']['exits']['yes']['executionBranch']='unknown'
  elif field=='stale-proof':bad['sourceProof']=bad['sourceProof'].replace(d['sources'][0]['hash'],'0'*64)
  elif field=='bad-id':bad['edits'][0]['definition']['branches'][0]['id']='../escape'
  elif field=='changed-data':bad['edits'][0]['definition']['exits']['yes']['value']={'constant':999}
  elif field=='missing-data':bad['edits'][0]['definition']['exits']['yes'].pop('value')
  else:bad['edits'][0]['definition']['branches'][0]['value']=0
  x.rpc('authorBatch',False,**bad);assert x.checkpoint()==before;x.original()
 f.checked('명시 호출자 누락·잘못된 분기/값·낡은 증거는 원자 거절하며 입력과 원본을 유지한다')
 source=f.project/'After.node.json';source.write_bytes(x.physical[source]+b' ');x.rpc('authorBatch',False,**req);source.write_bytes(x.physical[source]);assert x.checkpoint()==before;x.original();f.checked('다른 호출자 frame의 물리 원문 경합도 전체 저장 전 확인한다')
 if x.compound_mode:
  header=f.project/'Other.celem';header_bytes(x.physical[header]+b' ');x.rpc('authorBatch',False,**req);header_bytes(x.physical[header]);assert x.checkpoint()==before;x.original();f.checked('다른 import 헤더의 Save 전 물리 경합은 전체 후보를 거절하며 readonly 원본을 보존한다')
 result=x.rpc('authorBatch',**req);assert result['settled'] and result['checkpointSaved'];assert x.rpc('settledAuthorBatch',**req)['settled'];current=x.read();assert current['diagnostics']['state']=='source-ready';assert x.read(x.caller)['diagnostics']['state']=='source-ready';assert len(current['reviewIds'])>=8;x.original();saved=x.checkpoint();f.checked('루트 공개 분기·반환·직접 호출자 dispatch를 한 후보/checkpoint CAS와 완전 Review 그룹에 저장한다')
 if x.compound_mode:
  assert x.other_feature in current['reviewIds'];rows={u['id']:u for u in json.loads(next(iter(saved.values())))['changes']}
  for kind in ['header-draft','missing-receipt','tampered-hash']:
   bad=copy.deepcopy(rows)
   if kind=='header-draft':bad[x.other_feature]['draft']+=' '
   elif kind=='missing-receipt':bad[x.graph].pop('authorSaveReceipt')
   else:bad[x.graph]['authorSaveReceipt']['sources'][x.other_feature]['hash']='0'*64
   reject_metadata(bad)
  f.checked('추가 계약은 변경 없는 전체 Review 멤버이며 header draft·누락/변조 receipt는 실제 검증에서 거절한다')
 f.stop();f.start(1);assert x.checkpoint()==saved;assert x.read()['diagnostics']['state']=='source-ready';assert x.rpc('settledAuthorBatch',**req)['settled'];x.original();f.checked('재시작에서 같은 branch ID·호출자 receipt·원자 그룹을 복원하고 응답 재조회는 중복 저장하지 않는다')
 f.invoke('reviewGroup',{'ids':[x.graph]},False);x.original();ids=x.read()['reviewIds'];view=f.invoke('reviewGroup',{'ids':ids});assert not view['state']['review'].get('errors');x.original();f.checked('부분 Review를 거절하고 전체 Review 준비·취소는 원본을 쓰지 않는다')
 review_checkpoint=x.checkpoint();token=view['state']['review']['token'];source.write_bytes(x.physical[source]+b' ');failed=f.invoke('confirmGroup',{'ids':ids,'token':token})['result']['result'];assert failed['sourceConfirmed'] is False;source.write_bytes(x.physical[source]);x.original();assert x.checkpoint()==review_checkpoint;f.stop();f.start(2);f.checked('Review 뒤 호출자 변경은 최종 CAS에서 전부 미반영하고 저장된 후보를 유지한다')
 if x.compound_mode:
  ids=x.read()['reviewIds'];view=f.invoke('reviewGroup',{'ids':ids});header_review_checkpoint=x.checkpoint();header_bytes(x.physical[header]+b' ');failed=f.invoke('confirmGroup',{'ids':ids,'token':view['state']['review']['token']})['result']['result'];assert failed['sourceConfirmed'] is False;header_bytes(x.physical[header]);assert x.checkpoint()==header_review_checkpoint;x.original();f.checked('Review 뒤 다른 import 헤더 변경도 최종 CAS에서 전체 미반영한다')
 view=f.invoke('reviewGroup',{'ids':x.read()['reviewIds']});f.invoke('confirmGroup',{'ids':x.read()['reviewIds'],'token':view['state']['review']['token']});assert (f.project/'Flow.node.json').read_bytes()==x.physical[f.project/'Flow.node.json'];assert (f.project/'After.node.json').read_bytes()==x.physical[f.project/'After.node.json'];x.build('after');assert x.read(x.caller)['nodes'][0]['outputs']==x.expected_outputs;f.checked('Confirm 뒤 기존 C# 바이트·ordinary 계약을 보존하며 성공 분기는 직접 호출자의 반환 경로로 실제 실행한다')
 if x.out_mode:f.checked('기존 out/ref 계약과 출력 카드·소비 연결을 보존하고 분기 진입 전에 데이터를 발행해 실제 반환한다')
 if x.nonvoid_mode:
  saved_graph=json.loads((f.project/'Flow.graph.json').read_text())
  assert {key:v['value'] for key,v in saved_graph['exits'].items()}==x.root['exits']
  f.checked('기존 직접 종료점 값 연결과 export-return을 분기와 별도로 보존하며 native 반환 소비자를 유지한다')
 if x.compound_mode:
  for name in ['Other.celem','OtherBody.celem','Other.csbody']:assert stat.S_IMODE((f.project/name).stat().st_mode)==0o400
  dependency_path=f.project/('Flow.graph.json' if x.provider_import_mode else 'Main.graph.json');dependency_node='root_other' if x.provider_import_mode else 'other';assert next(n for n in json.loads(dependency_path.read_bytes())['nodes'] if n['id']==dependency_node)==next(n for n in json.loads(x.physical[dependency_path])['nodes'] if n['id']==dependency_node)
  caller_path=f.project/'Main.graph.json';confirmed=caller_path.read_bytes();caller_graph=json.loads(confirmed)
  caller_graph['edges']=[e for e in caller_graph['edges'] if not(e['from']=='invoke' and e['port'].startswith('case:'))];caller_path.write_text(json.dumps(caller_graph))
  try:x.build('unrouted-continuation',x.result_code,x.initial_stdout)
  finally:caller_path.write_bytes(confirmed)
  f.checked('다른 호출·C#·import와 readonly 모드를 유지하고 결과 분기 뒤 기존 다음 호출/데이터 소비를 실제 실행한다')
 if x.nonvoid_mode:
  caller_file=f.project/'Main.graph.json';saved_caller=caller_file.read_bytes();g=json.loads(saved_caller);g['edges']=[e for e in g['edges'] if not(e['from']=='invoke' and e['port'].startswith('case:'))];caller_file.write_text(json.dumps(g))
  try:x.build('native-continuation',x.result_code,x.initial_stdout)
  finally:caller_file.write_bytes(saved_caller)
  body_file=f.project/'MainBody.celem';saved_body=body_file.read_bytes();body_file.write_text('implementation '+f.n+'MainBody for '+f.n+'Main () -> int {import '+x.feature+' as Original (long,ref int,out long,out string) -> int;body common "Legacy.csbody";}');(f.project/'Legacy.csbody').write_text('int cell=41;int value=calls.Original.Invoke(1,ref cell,out long result,out string label);global::System.Console.WriteLine("legacy:"+value+":"+result+":"+label+":"+cell);return value;')
  try:x.build('native-ordinary',42,'callee:1\nlegacy:42:420:value:42:42')
  finally:body_file.write_bytes(saved_body)
  f.checked('분기 뒤 continuation의 원래 반환 소비와 기존 C# IInvoke 반환형/ref/out를 별도 실제 실행으로 보존한다')
 f.stop();f.start(3);assert x.read()['diagnostics']['state']=='source-ready';assert x.read(x.caller)['diagnostics']['state']=='source-ready';f.checked('최종 반영 후 cold 재시작에서 공개 분기와 연결을 다시 읽는다')
 print('M12_FIXTURE '+str(f.case),flush=True)
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
