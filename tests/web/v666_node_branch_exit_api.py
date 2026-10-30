"""명시 종료 선택·연결·원자 저장과 기존 반환/저장소의 실제 실행."""
import copy,json,uuid,sys,subprocess
import v666_node_branch_exit_fixture as e
n=e.n;x=e.x;f=e.f
try:
 n.build('before');f.start(0);e.wrap();before=x.checkpoint();x.original()
 cases=[]
 for kind in ['missing','deleted','unconnected','orphan','empty','unrepresented']:
  bad=e.plan()
  if kind=='missing':bad['exits']['finish']={'executionBranch':''}
  if kind=='deleted':bad['exits']['finish']={'executionBranch':'deleted'}
  if kind=='unconnected':bad['edges']=bad['edges'][1:]
  if kind=='orphan':bad['exits']['unused']={'executionBranch':'next'}
  if kind=='empty':bad['exits']={};bad['edges']=[]
  if kind=='unrepresented':del bad['exits']['finish'];bad['edges']=bad['edges'][:1]
  invalid=e.native(bad);wanted='GRAPH_EXECUTION_EXIT_BRANCH' if kind in ['missing','deleted'] else 'GRAPH_EXECUTION_EXIT_DISCONNECTED' if kind=='orphan' else 'GRAPH_EXECUTION_EXIT_COVERAGE' if kind=='unrepresented' else 'GRAPH_EXECUTION_EXIT_INCOMPLETE';assert invalid['state']=='invalid' and invalid['diagnostics'][0]['code']==wanted,(kind,invalid)
  e.batch(bad,False);assert x.checkpoint()==before;x.original();cases.append(kind)
 f.checked('누락/삭제된 분기·미연결/고립 종료점·빈 계획은 기본 분기를 추정하지 않고 전체 거절한다')
 native=e.native(e.plan());assert native['state'] in ['source-ready','source-assembled'],native
 protected=f.project/'Flow.node.json';protected.write_bytes(x.physical[protected]+b' ');e.batch(e.plan(),False);assert x.checkpoint()==before and protected.read_bytes()==x.physical[protected]+b' ';protected.write_bytes(x.physical[protected]);f.checked('미확정 래핑의 원래 C# guard 경합은 종료점 Save 전에 거절하고 입력/체크포인트/외부 수정을 보존한다')
 e.batch(e.plan());saved=x.checkpoint();d=e.read();assert d['executionExitMode'] and d['executionEnum']==n.execution and d['diagnostics']['state']=='source-ready';x.original();f.stop();f.start(1);assert x.checkpoint()==saved and e.read()['executionExitMode'];f.checked('기존 ID의 종료점과 모든 실행선을 한 후보/CAS로 저장하고 cold에서 복원한다')
 ids,token=e.review();p=f.project/'Flow.node.json';p.write_bytes(x.physical[p]+b' ');failed,_=x.any_invoke('confirmGroup',{'token':token,'ids':ids});assert not failed.get('result',{}).get('sourceConfirmed');assert (f.project/'Flow.graph.json').read_bytes()==x.physical[f.project/'Flow.graph.json'];p.write_bytes(x.physical[p]);f.stop();f.start(2);e.confirm();e.run('explicit-exits');f.checked('최종 원문 CAS는 충돌을 거절하고 명시 복구 뒤 종료점의 ID만 바깥 분기로 반환한다')
 published=json.loads((f.project/'Flow.graph.json').read_text());outer=next(r for r in n.at(published)['nodes'] if r['id']=='calculate');assert n.at(published)['edges']==n.at(n.graph)['edges'] and outer['executionEnum']==n.execution and outer['retainedCode']['definition']==next(r for r in n.at(n.graph)['nodes'] if r['id']=='calculate');body=outer['graph']['nodes'][0];record=json.loads((f.project/body['implementation']).read_text());assert record['source']==n.source and record['helpers']==n.helpers and (f.project/'Flow.node.json').read_bytes()==x.physical[f.project/'Flow.node.json'];f.checked('공개 계약·분기 ID/순서·바깥 실행선·C# 원문/helpers와 원본 record를 보존한다')
 e.batch(e.plan(True));e.confirm();e.run('changed-exit-selection',True);f.checked('C# Result 계산을 바꾸지 않고 종료점에서 선택한 기존 ID만 명시 변경한다')
 if not n.refs:
  early={'entry':'exit:proceed','exits':{'proceed':{'executionBranch':'alternate'}},'edges':[]};e.batch(early);e.confirm();e.run('explicit-early-exit',swapped=True,early=True);f.checked('직접 진입한 종료점은 선택기를 실행하지 않고 명시 반환하며 기존 미할당 out 정책을 유지한다')
 if any(a.startswith('--legacy-cli=') for a in sys.argv):
  legacy=next(a.split('=',1)[1] for a in sys.argv if a.startswith('--legacy-cli='));protected={p:p.read_bytes() for p in f.project.iterdir() if p.is_file()};failed=subprocess.run([f.env['CONFECTORY_DOTNET'],legacy,'build',str(x.manifest),'portable'],capture_output=True,text=True,env=f.env);(f.case/'legacy-refusal.log').write_text(failed.stdout+failed.stderr);assert failed.returncode!=0 and ('Private graph contract is owned' in failed.stdout+failed.stderr or 'GRAPH_SCHEMA' in failed.stdout+failed.stderr),(failed.returncode,failed.stdout[-3000:]);assert all(p.read_bytes()==value for p,value in protected.items());f.checked('이전 정상 실행 파일은 새 종료점 형식을 명시 거절하며 원문/데이터를 쓰거나 다른 분기로 실행하지 않는다')
 f.stop();f.start(3);assert e.read()['diagnostics']['state']=='source-ready';print('M11_BRANCH_EXIT_FIXTURE '+str(f.case),flush=True)
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
