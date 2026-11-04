"""A new code node's signature, value, C# and Task share the first candidate."""
import copy,json,uuid
import v666_async_creating_fixture as x

f=x.f
try:
 f.start(0);f.invoke('select',dict(id=x.feature));f.invoke('saveDraft',{});d=x.read();before=x.checkpoint()
 source='await global::System.Threading.Tasks.Task.Yield();\nglobal::System.Console.WriteLine("work");\n'
 edits=[dict(action='source',node=x.node,text=source),dict(action='argument',node=x.node,name='input',valueJson='{"constant":3}'),dict(action='parameters',node=x.node,definition=dict(args=[dict(name='input',type='int')],remap={},returnType='void')),dict(action='createNode',node=x.node,definition=dict(kind='code',control='next',intent='새 Task',signature=dict(args=[],**{'return':'void'}))),dict(action='route',node=x.node,port='next',to='body'),dict(action='entry',node='$entry',to=x.node),dict(action='asyncTransition',node='$root',definition=dict(enabled=True,nodes=[dict(node=x.node,enabled=True)]))]
 request=x.request(d,edits)
 for kind in ['existing-node','missing-flag','ref']:
  bad=copy.deepcopy(request);bad['attempt']=uuid.uuid4().hex
  if kind=='existing-node':bad['edits'][3]['node']='body'
  elif kind=='missing-flag':bad['edits'][-1]['definition']['nodes'][0]['node']='unknown'
  else:bad['edits'][2]['definition']['args'][0]['mode']='ref'
  x.rpc('authorBatch',False,**bad);assert before==x.checkpoint();x.original();assert all(n['id']!=x.node for n in x.read()['nodes'])
 assert x.rpc('authorBatch',**request)['settled'];held=x.checkpoint();assert x.rpc('settledAuthorBatch',**request)['settled']and held==x.checkpoint();node=next(n for n in x.read()['nodes']if n['id']==x.node);assert node['async']and node['signature']['args'][0]['name']=='input';assert json.loads(x.draft_unit()['draft'])['source']==source;assert not x.path().exists();x.original();f.stop();f.start(1);assert held==x.checkpoint()and x.rpc('settledAuthorBatch',**request)['settled'];f.checked('새 동작 생성/핀/값/실행선/명시 C#/Task는 한 후보로 저장하고 중복 ID·없는 flag·ref는 전체 거절한다')
 ids=x.read()['reviewIds'];f.invoke('reviewGroup',dict(ids=[x.source_id(x.node)]),False);r=f.invoke('reviewGroup',dict(ids=ids))['state']['review'];assert not r.get('errors'),r;result=f.invoke('confirmGroup',dict(ids=ids,token=r['token']))['result']['result'];assert result['sourceConfirmed'],result;x.build('coupled-new-node',True);x.unchanged();assert json.loads(x.path().read_text())['source']==source;f.stop();f.start(2);assert next(n for n in x.read()['nodes']if n['id']==x.node)['async'];f.checked('전체 Review/Confirm·실제 await 실행·확정 cold는 기존 C#·계약/본문과 원래 다음 실행 순서를 보존한다');print('ASYNC_COUPLED_NODE_FIXTURE',f.case,flush=True)
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
