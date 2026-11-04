"""Existing owned private caller binds typed body input and its Task in one Save."""
import json,uuid
import v666_async_private_fixture as x
f=x.f
source='// explicit private Task input 😀\nawait global::System.Threading.Tasks.Task.Yield();\nreturn Twice(amount)+1;\n'
try:
 f.start(0);f.invoke('select',dict(id=x.feature));f.invoke('saveDraft',{});x.parent();d=x.read();before=x.checkpoint();request=x.request(d,nodes=[dict(node='body',enabled=True)]);request['edits']=[dict(action='source',node='body',text=source),dict(action='intent',node='body',text='명시 입력과 함께 전환'),*request['edits']]
 bad={**request,'attempt':uuid.uuid4().hex,'edits':[dict(action='source',node='absent',text=source),*request['edits'][1:]]};x.rpc('authorBatch',False,**bad);assert before==x.checkpoint();x.original();assert x.rpc('authorBatch',**request)['settled'];held=x.checkpoint();assert x.rpc('settledAuthorBatch',**request)['settled'];assert held==x.checkpoint();x.original();f.stop();f.start(1);assert held==x.checkpoint();assert next(n for n in x.read()['nodes']if n['id']=='body')['async'];f.checked('소유 내부 본문 입력과 Task를 한 후보에 묶고 없는 동작 거절·반복 조회·cold에서 원문/입출력과 checkpoint를 보존한다')
 ids=x.read()['reviewIds'];f.invoke('reviewGroup',dict(ids=[x.leaf]),False);r=f.invoke('reviewGroup',dict(ids=ids))['state']['review'];assert not r.get('errors'),r;review_before=x.checkpoint();p=f.project/'Flow.node.json';old=p.read_bytes();p.write_bytes(old+b' ')
 try:
  result=f.invoke('confirmGroup',dict(ids=ids,token=r['token']))['result']['result'];assert not result['sourceConfirmed']and x.checkpoint()==review_before,result
 finally:p.write_bytes(old)
 x.original();x.confirm();assert json.loads(p.read_text())['source']==source;assert json.loads(p.read_text())['helpers']==x.record['helpers'];assert(f.project/'Flow.celem').read_bytes()==x.public
 for path,data in x.physical.items():
  if path.name not in ['Flow.graph.json','Flow.node.json']:assert path.read_bytes()==data,path
 x.build('coupled-private');f.stop();f.start(2);assert next(n for n in x.read()['nodes']if n['id']=='body')['async'];assert json.loads(p.read_text())['source']==source;f.checked('부분 Review/원문 충돌 거절·Confirm·실제 private Task와 확정 cold는 공개 계약/기존 호출자/요청한 원문과 helper를 유지한다');print('ASYNC_COUPLED_PRIVATE_FIXTURE',f.case,flush=True)
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
