"""First-save branch insertion, output-before-routing and final atomic CAS."""
import copy,json,shutil,subprocess,uuid
import v666_async_branch_creation_fixture as x
f=x.f
def unselected_result():
 # A generated execution copy selects the other authored result. The original
 # caller, contracts and source files remain byte-for-byte unchanged.
 project=f.case/'other-result-execution';shutil.copytree(f.project,project,ignore=shutil.ignore_patterns('.confectory'))
 path=project/'Main.graph.json';caller=json.loads(path.read_text());next(n for n in caller['nodes']if n['id']=='invoke')['arguments']['amount']={'constant':0};path.write_text(json.dumps(caller))
 built=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),'build',str(project/'project.cproj'),'portable'],env=f.env,text=True,capture_output=True);(f.case/'other-result-build.log').write_text(built.stdout+built.stderr);assert built.returncode==0,built.stderr+built.stdout[-2500:]
 result=subprocess.run(json.loads(built.stdout)['run'],env=f.env,text=True,capture_output=True);(f.case/'other-result-run.json').write_text(json.dumps(dict(exit=result.returncode,stdout=result.stdout,stderr=result.stderr)))
 expected='callee:0\n'+('work:0\n'if x.port=='completion'else'')+'completed:0\nafter:0';assert (result.returncode,result.stdout.strip())==(0,expected),(result.returncode,result.stdout,result.stderr);x.unchanged()
try:
 f.start(0);f.invoke('select',dict(id=x.feature));f.invoke('saveDraft',{});d=x.read();before=x.checkpoint();destination=next(e['to']for e in x.base.initial_edges if e['from']=='choose'and e['port']==x.port)
 edits=[dict(action='createNode',node=x.node,definition=dict(kind='code',control='next',intent='명시적 분기선 Task',branchOwner='choose',signature=dict(args=[dict(name='value',type='int')],**{'return':'void'}))),dict(action='argument',node=x.node,name='value',valueJson='{"node":"choose","output":"result"}'),dict(action='route',node=x.node,port='next',to=destination),dict(action='route',node='choose',port=x.port,to=x.node),dict(action='source',node=x.node,text=x.new_source),dict(action='asyncTransition',node='$root',definition=dict(enabled=True,nodes=[dict(node=x.node,enabled=True)]))]
 request=x.request(d,edits)
 for kind in ['unknown-port','cross-region','unknown-owner','unknown-flag','ref']:
  bad=copy.deepcopy(request);bad['attempt']=uuid.uuid4().hex
  if kind=='unknown-port':bad['edits'][3]['port']='case:deleted'
  elif kind=='cross-region':bad['edits'][3]['to']='choose'
  elif kind=='unknown-owner':bad['edits'][0]['definition']['branchOwner']='missing'
  elif kind=='unknown-flag':bad['edits'][-1]['definition']['nodes'][0]['node']='missing'
  else:bad['edits'][0]['definition']['signature']['args'][0]['mode']='ref'
  x.rpc('authorBatch',False,**bad);assert x.checkpoint()==before;x.original();assert all(n['id']!=x.node for n in x.read()['nodes'])
 f.checked('없는 분기·다른 영역·소유자 위조·없는 Task·ref는 전체 후보를 거절하고 원본과 checkpoint를 보존한다')
 assert x.rpc('authorBatch',**request)['settled'];saved=x.checkpoint();assert x.rpc('settledAuthorBatch',**request)['settled']and x.checkpoint()==saved
 current=x.read();fresh=next(n for n in current['nodes']if n['id']==x.node);assert fresh['async']and fresh['branchOwner']=='choose';assert json.loads(x.draft_unit()['draft'])['source']==x.new_source;assert not x.path().exists();x.original()
 expected=[{**e,'to':x.node}if e['from']=='choose'and e['port']==x.port else e for e in x.base.initial_edges]+[dict(**{'from':x.node},port='next',to=destination)]
 assert sorted(current['edges'],key=json.dumps)==sorted(expected,key=json.dumps)
 f.stop();f.start(1);assert x.checkpoint()==saved and x.rpc('settledAuthorBatch',**request)['settled'];x.original();f.checked('분기선 생성·기존 출력 연결·명시 원문·Task는 첫 Save 한 후보이고 반복 조회/cold에서 중복 저장하지 않는다')
 ids=x.read()['reviewIds'];f.invoke('reviewGroup',dict(ids=[x.source_id(x.node)]),False)
 for target in ['manifest','source']:
  review=f.invoke('reviewGroup',dict(ids=ids))['state']['review'];assert not review.get('errors'),review;held=x.checkpoint()
  p=f.project/('project.cproj'if target=='manifest'else'Flow.node.json');old=p.read_bytes();p.write_bytes(old+b' ')
  try:
   result=f.invoke('confirmGroup',dict(ids=ids,token=review['token']))['result']['result'];assert not result['sourceConfirmed'],result;assert x.checkpoint()==held,'Confirm changed the reviewed checkpoint';assert p.read_bytes()==old+b' '
  finally:p.write_bytes(old)
  x.original()
 review=f.invoke('reviewGroup',dict(ids=ids))['state']['review'];assert not review.get('errors'),review;assert f.invoke('confirmGroup',dict(ids=ids,token=review['token']))['result']['result']['sourceConfirmed'];x.unchanged();assert json.loads(x.path().read_text())['source']==x.new_source;x.build('branch-task-execution',True);unselected_result()
 f.stop();f.start(2);assert next(n for n in x.read()['nodes']if n['id']==x.node)['async'];x.unchanged();f.checked('부분 Review·최종 CAS 거절/명시 재시도·확정 cold와 실제 await 실행은 출력→완료→결과→연속 순서를 보존한다');print('ASYNC_BRANCH_CREATION_FIXTURE',f.case,flush=True)
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
