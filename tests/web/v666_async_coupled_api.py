"""One first author Save binds original body input and explicit async flags."""
import copy,json,uuid,sys
if '--information'in sys.argv:import v666_async_information_fixture as x
else:import v666_async_new_function_fixture as x
f=x.f
try:
 f.start(0)
 if '--defer'in sys.argv:
  f.invoke('select',dict(id=x.owner));owner=x.owner_proof();basis=x.rpc('readOwnerEdits',id=x.owner,hash=owner['ownerHash']);x.rpc('applySlots',id=x.owner,rows=[],basis=basis['basis'],declaration=dict(id=x.owner,hash=owner['ownerHash'],changes=[dict(type='function-add',id=x.feature,name='첫 결합 함수',description='직접 소유 함수')]));f.invoke('schema',dict(id=x.owner));row=next(v for v in f.state()['schema']['ownFunctions']if v['id']==x.feature);preview=x.rpc('readFeature',id=x.feature,hash=row['hash'],revision=row['revision'],**x.owner_proof());held=x.checkpoint();created=x.rpc('createFeature',id=x.feature,basis=preview['basis'],deferCheckpoint=True);assert not created['checkpointSaved']and x.checkpoint()==held;x.graph=created['id'];x.impl=x.graph.split('/body:')[0];sources=x.read()['sources'];x.paths={u['id']:f.project/u['path']for u in sources if u['id']in[x.feature,x.impl,x.graph,x.graph+'/node:body']};assert len(x.paths)==4;x.owner_proof();unit=f.state()['draft'];assert unit['id']==x.owner;x.owner_draft=unit['text']
 else:x.create()
 f.invoke('select',dict(id=x.feature));d=x.read();before=x.checkpoint();edits=[dict(action='source',node=x.node,text=x.new_source),dict(action='intent',node=x.node,text='한 번의 첫 저장'),dict(action='icon',node=x.node,text='★'),*x.request(d)['edits']];request={**x.request(d),'edits':edits}
 for kind in ['wrong-order','duplicate','unsupported']:
  bad=copy.deepcopy(request);bad['attempt']=uuid.uuid4().hex
  if kind=='wrong-order':bad['edits']=[edits[-1],*edits[:-1]]
  elif kind=='duplicate':bad['edits'].append(copy.deepcopy(edits[-1]))
  else:bad['edits'].insert(0,dict(action='removeNode',node='body'))
  x.rpc('authorBatch',False,**bad);assert x.checkpoint()==before;x.original()
 f.checked('잘못된 전환 순서·중복 전환·다른 구조 입력은 첫 후보 전체를 거절하고 원본/초안을 보존한다')
 assert x.rpc('authorBatch',**request)['settled'];saved=x.checkpoint();unit=x.draft_unit();assert json.loads(unit['draft'])['source']==x.new_source and unit['baseline']=='missing';assert x.read()['asyncTransition']['enabled'];assert next(n for n in x.read()['nodes']if n['id']==x.node)['async'];assert x.rpc('settledAuthorBatch',**request)['settled'];assert x.checkpoint()==saved;x.original();assert not any(p.exists()for p in x.paths.values());f.stop();f.start(1);assert x.checkpoint()==saved and x.rpc('settledAuthorBatch',**request)['settled'];f.checked('첫 Save는 원문/표시 입력과 명시 함수·동작 async를 한 checkpoint로 묶고 반복 결과 조회/cold에서 중복 저장하지 않는다')
 ids=x.read()['reviewIds'];f.invoke('reviewGroup',dict(ids=[x.graph]),False);review=f.invoke('reviewGroup',dict(ids=ids))['state']['review'];assert not review.get('errors'),review;old=(f.project/'project.cproj').read_bytes();held=x.checkpoint();(f.project/'project.cproj').write_bytes(old+b' ')
 try:
  result=f.invoke('confirmGroup',dict(ids=ids,token=review['token']))['result']['result'];assert not result['sourceConfirmed']and x.checkpoint()==held
 finally:(f.project/'project.cproj').write_bytes(old)
 x.original();review=f.invoke('reviewGroup',dict(ids=ids))['state']['review'];result=f.invoke('confirmGroup',dict(ids=ids,token=review['token']))['result']['result'];assert result['sourceConfirmed'];x.unchanged();assert json.loads(x.path().read_text())['source']==x.new_source;x.build_new('coupled-execution');f.stop();f.start(2);assert x.read()['asyncTransition']['enabled'];x.unchanged();f.checked('부분 Review/최종 CAS 거절과 재시도는 생성 전체를 보존하고 명시 Task 원문을 실제 실행·확정 cold 복원한다');print('ASYNC_COUPLED_FIXTURE',f.case,flush=True)
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
