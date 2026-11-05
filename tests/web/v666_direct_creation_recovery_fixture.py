"""One new owned void action inserted after an existing ordinary C# action."""
import uuid
import v666_root_followup_recovery_fixture as base
x=base.x;f=x.f;feature=base.feature;graph=base.graph;graph_file=base.graph_file;source_file=base.source_file
def read():return base.read()
text='global::System.Console.WriteLine("placed");'
late='global::System.Console.WriteLine("placed-late");'
intent='직접 배치한 동작';name='내부 기능'
def edits(node,source=text):return [dict(action='createNode',node=node,definition=dict(kind='code',control='next',intent=intent,signature=dict(args=[],**{'return':'void'}))),dict(action='rename',node=node,text=name),dict(action='intent',node=node,text=intent),dict(action='source',node=node,text=source),dict(action='route',node='body',port='next',to=node),dict(action='route',node=node,port='next',to='exit:return')]
def request(node,source=text):
 d=read();return dict(action='authorBatch',id=graph,attempt=uuid.uuid4().hex,checkpointHash=d['checkpointHash'],sourceProof=x.proof(d),edits=edits(node,source))
def current(node):return next((n for n in read()['nodes']if n['id']==node),None)
def checkpoint():return base.checkpoint()
_paths={}
def path(node):
 import json
 if node not in _paths:
  doc=json.loads(checkpoint().read_text());_paths[node]=f.project/next(u['path']for u in doc['changes']if u['id']==graph+'/node:'+node)
 return _paths[node]
def physical_confirmed(node,source):
 import copy,json
 p=path(node);assert json.loads(p.read_text())['source']==source
 assert all(k.read_bytes()==v for k,v in x.physical.items()if k.name!=graph_file)
 observed=json.loads((f.project/graph_file).read_text());before=copy.deepcopy(base.base.definition);added=next(n for n in observed['nodes']if n['id']==node);assert added['kind']=='code'and added['control']=='next'and added['signature']==dict(args=[],**{'return':'void'})
 assert [n for n in observed['nodes']if n['id']!=node]==before['nodes']
 edges=[dict(e)for e in before['edges']if not(e['from']=='body'and e['port']=='next')]+[{'from':'body','port':'next','to':node},{'from':node,'port':'next','to':'exit:return'}]
 assert sorted(observed['edges'],key=str)==sorted(edges,key=str)
 before['nodes']=observed['nodes'];before['edges']=observed['edges'];assert observed==before
 return p
