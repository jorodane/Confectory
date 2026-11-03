"""직접 소유 함수·원래 public 완료 연결과 원문을 가진 생성 테스트 자료."""
import copy,hashlib,json,uuid
import v666_async_completion_fixture as previous
f=previous.f;feature,impl,graph,caller=previous.feature,previous.impl,previous.graph,previous.caller
_stop=f.stop
def stop():
 _stop()
 if f.host is not None:f.host.wait(timeout=15)
f.stop=stop
# Demote only the local Result node first; its function remains explicitly async.
units={}
for id,old in previous.units.items():
 text=(f.project/old['path']).read_text();units[id]=dict(kind=old['kind'],path=old['path'],original=text,draft=text,baseline=hashlib.sha256(text.encode()).hexdigest(),revision=0)
prepared=f.metadata('blueprintAsyncTransition',namespace='Owned.Elements',id=graph,units=units,plan=dict(enabled=True,nodes=[dict(node='choose',enabled=False)]));units.update(prepared['units'])
for unit in units.values():(f.project/unit['path']).write_text(unit['draft'])
g=json.loads((f.project/'Main.graph.json').read_text());g['nodes'].append(dict(id='publicDone',kind='code',control='next',intent='기존 공개 완료 작업',branchOwner='invoke',signature={'args':[{'name':'value','type':'int'}],'return':'void'},arguments={'value':{'node':'invoke','output':'result'}},implementation='PublicDone.node.json'));g['edges'] += [dict(from_='invoke',port='completion',to='publicDone'),dict(from_='publicDone',port='next',to='return:invoke')]
for edge in g['edges']:
 if 'from_'in edge:edge['from']=edge.pop('from_')
defs=f.metadata('featureBlueprintNodes',featureSource=(f.project/'Main.celem').read_text(),graph=g,featureContracts={feature:(f.project/'Flow.celem').read_text()});record=dict(schema=1,node='publicDone',definitionHash=next(n['definitionHash']for n in defs['nodes']if n['id']=='publicDone'),source='global::System.Console.WriteLine("public:"+value);')
(f.project/'PublicDone.node.json').write_text(json.dumps(record));(f.project/'Main.graph.json').write_text(json.dumps(g));physical={p:p.read_bytes()for p in f.project.rglob('*')if p.is_file()and '.confectory'not in p.parts};code={p:json.loads(v)['source']for p,v in physical.items()if p.name.endswith('.node.json')};original_edges=copy.deepcopy(g['edges']);local_graph=json.loads((f.project/'Flow.graph.json').read_text());local_nodes=copy.deepcopy(local_graph['nodes'])
read,rpc,proof,checkpoint,build=previous.read,previous.rpc,previous.proof,previous.checkpoint,previous.build

def original():assert all(p.read_bytes()==v for p,v in physical.items())
def code_unchanged():
 for p,text in code.items():assert json.loads(p.read_text())['source']==text,p

def request(data,enabled=False):return dict(id=graph,attempt=uuid.uuid4().hex,checkpointHash=data['checkpointHash'],sourceProof=proof(data),edits=[dict(action='asyncTransition',node='$root',definition=dict(enabled=enabled,nodes=[]))])
def marker():
 d=read();values=d['featureDefinition']['values'];raw=values.get('blueprintFunctionCompletion');assert raw,values
 return json.loads(raw)if isinstance(raw,str)else raw

def check_demoted():
 d=read();m=marker();assert not d['asyncTransition']['enabled'];assert any(b==m for b in d['publicExecutionBranches']);assert json.loads((f.project/'Flow.graph.json').read_text())['nodes']==local_nodes
 c=read(caller);assert c['edges']==original_edges;call=next(n for n in c['nodes']if n['id']=='invoke');assert not call.get('async') and call['completionBranch']['id']==m['id'];assert call['publicExecution'];return m

def root_plan(data,choice='none',name=None):
 branches=copy.deepcopy(data['rootExecution']['branches']);m=marker()
 if name is not None:next(b for b in branches if b['id']==m['id'])['name']=name
 return dict(branches=branches,entry=data['entry'],edges=copy.deepcopy(data['edges']),exits={e['name']:{'executionBranch':choice}for e in data['exits']},caller=dict(graph=caller,node='invoke',routes=[]))
def public_select(choice='none',name=None):
 d=read();plan=root_plan(d,choice,name);return rpc('authorBatch',id=graph,attempt=uuid.uuid4().hex,checkpointHash=d['checkpointHash'],sourceProof=proof(d),edits=[dict(action='rootExecution',node='$root',definition=plan)])
def confirm():
 d=read();ids=d['reviewIds'];v=f.invoke('reviewGroup',dict(ids=ids));assert not v['state']['review'].get('errors'),v['state']['review'];result=f.invoke('confirmGroup',dict(ids=ids,token=v['state']['review']['token']))['result']['result'];assert result['sourceConfirmed'],result
