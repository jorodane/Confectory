"""New owned public IO, authored C# and explicit Task share one first candidate."""
import copy,json,shutil,uuid
import v666_async_new_function_fixture as x
f=x.f
try:
 f.start(0);x.create();d=x.read();before=x.checkpoint();source=x.new_source
 plan=dict(args=[dict(name='seed',type='int'),dict(name='reply',type='int',mode='out')],returnType=d['signature']['return'],remap={},outputCreates=[dict(node='publish_reply',output='reply',valueJson='{"input":"seed"}')],outputEntry='before',outputRoutes=[dict(node='publish_reply',to='body')])
 edits=[dict(action='createNode',node='before',definition=dict(kind='code',control='next',intent='원래 입력을 읽는 새 직렬 동작',signature=dict(args=[dict(name='seed',type='int')],**{'return':'void'}))),dict(action='argument',node='before',name='seed',valueJson='{"input":"seed"}'),dict(action='route',node='before',port='next',to='publish_reply'),dict(action='source',node='before',text='global::System.Console.WriteLine("before:"+seed);'),dict(action='rootParameters',node='$root',definition=plan),dict(action='source',node='body',text=source),dict(action='asyncTransition',node='$root',definition=dict(enabled=True,nodes=[dict(node='body',enabled=True)]))]
 request={**x.request(d),'edits':edits}
 for kind in ['ref','duplicate-contract','unknown-remap']:
  bad=copy.deepcopy(request);bad['attempt']=uuid.uuid4().hex
  if kind=='ref':next(e for e in bad['edits']if e['action']=='rootParameters')['definition']['args'][0]['mode']='ref'
  elif kind=='duplicate-contract':bad['edits'].insert(0,copy.deepcopy(next(e for e in bad['edits']if e['action']=='rootParameters')))
  else:next(e for e in bad['edits']if e['action']=='rootParameters')['definition']['remap']['unknown']='seed'
  x.rpc('authorBatch',False,**bad);assert before==x.checkpoint();x.original();assert x.read()['signature']==d['signature']
 assert x.rpc('authorBatch',**request)['settled'];held=x.checkpoint();assert x.rpc('settledAuthorBatch',**request)['settled']and held==x.checkpoint();current=x.read();assert current['signature']['args']==plan['args']and current['asyncTransition']['enabled'];assert json.loads(x.draft_unit()['draft'])['source']==source;x.original();assert not any(p.exists()for p in x.paths.values());f.stop();f.start(1);assert held==x.checkpoint()and x.rpc('settledAuthorBatch',**request)['settled'];f.checked('새 공개 입력/출력·명시 원문·Task는 같은 후보에 저장하며 ref/중복 계약/잘못된 대응은 전체 거절하고 cold에서 복구한다')
 current=x.read();renamed=copy.deepcopy(plan['args']);renamed[0]['name']='origin';revised=dict(args=renamed,returnType=plan['returnType'],remap=dict(seed='origin',reply='reply'));x.rpc('rootParameters',id=x.graph,basis=current['basis'],plan=json.dumps(revised));f.invoke('saveDraft',{});f.stop();f.start(2);assert x.read()['signature']['args']==renamed;assert json.loads(x.draft_unit()['draft'])['source']==source;before_unit=next(u for u in x.units()if u['id']==x.graph+'/node:before');before_path=f.project/before_unit['path'];assert json.loads(before_unit['draft'])['source']=='global::System.Console.WriteLine("before:"+seed);';assert next(n for n in x.read()['nodes']if n['id']=='before')['arguments'][0]['valueJson']=='{"input":"origin"}';f.checked('첫 Save 뒤 Confirm 전 공개 IO 재편집은 새 계약의 명시 대응으로만 원자 그룹/원문을 보존하고 cold 복구한다')
 ids=x.read()['reviewIds'];f.invoke('reviewGroup',dict(ids=[x.graph]),False)
 for collision in ['new-destination','manifest']:
  v=f.invoke('reviewGroup',dict(ids=ids));assert not v['state']['review'].get('errors'),v['state']['review'];saved=x.checkpoint();path=x.paths[x.feature]if collision=='new-destination'else f.project/'project.cproj';old=path.read_bytes()if path.exists()else None;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((old or b'')+b' collision')
  try:
   r=f.invoke('confirmGroup',dict(ids=ids,token=v['state']['review']['token']))['result']['result'];assert not r['sourceConfirmed'],r;assert x.checkpoint()==saved;assert path.read_bytes()==(old or b'')+b' collision'
  finally:
   if old is None:path.unlink()
   else:path.write_bytes(old)
  x.original()
 f.checked('부분 Review와 Review 뒤 새 목적지/manifest 충돌은 전체 미확정하고 원문·입력·checkpoint와 충돌 자료를 보존한다')
 v=f.invoke('reviewGroup',dict(ids=ids));assert not v['state']['review'].get('errors'),v['state']['review'];r=f.invoke('confirmGroup',dict(ids=ids,token=v['state']['review']['token']))['result']['result'];assert r['sourceConfirmed'],r;x.unchanged();assert json.loads(x.path().read_text())['source']==source;assert json.loads(before_path.read_text())['source']=='global::System.Console.WriteLine("before:"+seed);'
 # Only this generated execution copy gets an explicitly authored async caller.
 destination=f.case/'explicit-async-caller';shutil.copytree(f.project,destination,ignore=shutil.ignore_patterns('.confectory'))
 metadata=json.dumps(json.dumps(dict(schema=1,completion='main_complete'),separators=(',',':')))
 main=f.n+'Main';implementation=f.n+'MainBody';main_source='function '+main+' () -> int {value blueprintAsync = '+metadata+';}'
 prepared=f.metadata('blueprintPrepareFeature',id=main,text=main_source,implementation=implementation,graphPath='Main.graph.json',nodePath='Main.node.json');caller=prepared['graph']
 call=dict(id='call',kind='call',control='next',intent='명시적으로 기다리는 테스트 호출자',feature=x.feature,signature=dict(args=renamed,**{'return':plan['returnType']}),arguments=dict(origin=dict(constant=3)))
 body=dict(id='body',kind='code',control='next',intent='입출력 실제 전달 확인',signature=dict(args=[dict(name='result',type='int'),dict(name='reply',type='int')],**{'return':'int'}),arguments=dict(result=dict(node='call'),reply=dict(node='call',output='reply')),implementation='Main.node.json')
 caller.update(entry='call',nodes=[call,body],edges=[dict(**{'from':'call'},port='next',to='body'),dict(**{'from':'body'},port='next',to='exit:return')],exits=dict(**{'return':dict(node='body')}))
 contracts={x.feature:x.paths[x.feature].read_text()};definitions=f.metadata('featureBlueprintNodes',featureSource=prepared['function'],graph=caller,featureContracts=contracts);assert definitions['state']=='node-definitions',definitions
 record=dict(schema=1,node='body',definitionHash=next(n for n in definitions['nodes']if n['id']=='body')['definitionHash'],source='global::System.Console.WriteLine("reply:"+reply);return result;')
 import hashlib
 alias='fg_call_'+hashlib.sha256(x.feature.encode()).hexdigest()[:24]
 for name,text in [('Main.celem',prepared['function']),('MainBody.celem',prepared['implementation'].replace('{','{ import '+x.feature+' as '+alias+' (int,out int) -> int;',1)),('Main.graph.json',json.dumps(caller)),('Main.node.json',json.dumps(record,ensure_ascii=False))]:(destination/name).write_text(text)
 x.run(destination,'root-io-execution',11,'before:3\nfresh\nreply:3');x.unchanged();f.stop();f.start(3);assert x.read()['signature']['args']==renamed;f.checked('전체 Review/Confirm과 실제 명시 async 호출자는 입력 3·출력 3·반환 11을 전달하며 원문/기존 진입과 확정 cold를 보존한다')
 print('ASYNC_ROOT_IO_FIXTURE',f.case,flush=True)
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
