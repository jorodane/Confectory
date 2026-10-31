"""Real API/checkpoint/Confirm and execution checks for bounded M12."""
import copy,json
import v666_root_execution_fixture as x
f=x.f
try:
 units={}
 for id,kind,path in [(x.feature,'function','Flow.celem'),(x.impl,'implementation','FlowBody.celem'),(x.graph,'blueprint','Flow.graph.json'),(x.graph+'/node:choose','blueprint-node','Flow.node.json'),(f.n+'Main','function','Main.celem'),(f.n+'MainBody','implementation','MainBody.celem'),(x.caller,'blueprint','Main.graph.json'),(x.caller+'/node:after','blueprint-node','After.node.json')]:units[id]={'kind':kind,'path':path,'draft':(f.project/path).read_text()}
 pure=f.metadata('blueprintRootExecution',namespace='Owned.Elements',id=x.graph,units=units,plan=x.plan({'entry':x.root['entry'],'edges':x.root['edges']}));assert len(pure['group'])==8
 import hashlib
 for id,unit in pure['units'].items():unit['baseline']=hashlib.sha256((f.project/unit['path']).read_bytes()).hexdigest()
 assert len(f.metadata('blueprintRootExecutionGuards',namespace='Owned.Elements',units=pure['units'])['checks'])==8
 x.build('before',x.result_code,x.initial_stdout);f.start(0);d=x.read();assert d['rootExecution'],d.get('rootExecutionError');assert d['rootExecution']['callers'][0]['graph']==x.caller;before=x.checkpoint();req=x.request(d);x.original();f.checked('원래 sync void 원문·일반 호출 실행과 명시 호출자 후보를 확인한다')
 for field in ['missing-caller','unknown-branch','stale-proof','bad-id','changed-value']:
  bad=copy.deepcopy(req)
  if field=='missing-caller':bad['edits'][0]['definition']['caller']['graph']=''
  elif field=='unknown-branch':bad['edits'][0]['definition']['exits']['yes']['executionBranch']='unknown'
  elif field=='stale-proof':bad['sourceProof']=bad['sourceProof'].replace(d['sources'][0]['hash'],'0'*64)
  elif field=='bad-id':bad['edits'][0]['definition']['branches'][0]['id']='../escape'
  else:bad['edits'][0]['definition']['branches'][0]['value']=0
  x.rpc('authorBatch',False,**bad);assert x.checkpoint()==before;x.original()
 f.checked('명시 호출자 누락·잘못된 분기/값·낡은 증거는 원자 거절하며 입력과 원본을 유지한다')
 source=f.project/'After.node.json';source.write_bytes(x.physical[source]+b' ');x.rpc('authorBatch',False,**req);source.write_bytes(x.physical[source]);assert x.checkpoint()==before;x.original();f.checked('다른 호출자 frame의 물리 원문 경합도 전체 저장 전 확인한다')
 result=x.rpc('authorBatch',**req);assert result['settled'] and result['checkpointSaved'];assert x.rpc('settledAuthorBatch',**req)['settled'];current=x.read();assert current['diagnostics']['state']=='source-ready';assert x.read(x.caller)['diagnostics']['state']=='source-ready';assert len(current['reviewIds'])>=8;x.original();saved=x.checkpoint();f.checked('루트 공개 분기·반환·직접 호출자 dispatch를 한 후보/checkpoint CAS와 완전 Review 그룹에 저장한다')
 f.stop();f.start(1);assert x.checkpoint()==saved;assert x.read()['diagnostics']['state']=='source-ready';assert x.rpc('settledAuthorBatch',**req)['settled'];x.original();f.checked('재시작에서 같은 branch ID·호출자 receipt·원자 그룹을 복원하고 응답 재조회는 중복 저장하지 않는다')
 f.invoke('reviewGroup',{'ids':[x.graph]},False);x.original();ids=x.read()['reviewIds'];view=f.invoke('reviewGroup',{'ids':ids});assert not view['state']['review'].get('errors');x.original();f.checked('부분 Review를 거절하고 전체 Review 준비·취소는 원본을 쓰지 않는다')
 review_checkpoint=x.checkpoint();token=view['state']['review']['token'];source.write_bytes(x.physical[source]+b' ');failed=f.invoke('confirmGroup',{'ids':ids,'token':token})['result']['result'];assert failed['sourceConfirmed'] is False;source.write_bytes(x.physical[source]);x.original();assert x.checkpoint()==review_checkpoint;f.stop();f.start(2);f.checked('Review 뒤 호출자 변경은 최종 CAS에서 전부 미반영하고 저장된 후보를 유지한다')
 view=f.invoke('reviewGroup',{'ids':x.read()['reviewIds']});f.invoke('confirmGroup',{'ids':x.read()['reviewIds'],'token':view['state']['review']['token']});assert (f.project/'Flow.node.json').read_bytes()==x.physical[f.project/'Flow.node.json'];assert (f.project/'After.node.json').read_bytes()==x.physical[f.project/'After.node.json'];x.build('after');assert not x.out_mode or x.read(x.caller)['nodes'][0]['outputs']==[{'name':'result','type':'int'}];f.checked('Confirm 뒤 기존 C# 바이트·ordinary 계약을 보존하며 성공 분기는 직접 호출자의 반환 경로로 실제 실행한다')
 if x.out_mode:f.checked('정수 out의 기존 호출 계약과 출력 카드·소비 연결을 보존하고 분기 반환 시 데이터 10을 먼저 발행해 실제 반환한다')
 f.stop();f.start(3);assert x.read()['diagnostics']['state']=='source-ready';assert x.read(x.caller)['diagnostics']['state']=='source-ready';f.checked('최종 반영 후 cold 재시작에서 공개 분기와 연결을 다시 읽는다')
 print('M12_FIXTURE '+str(f.case),flush=True)
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
