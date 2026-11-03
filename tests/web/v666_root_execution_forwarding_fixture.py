"""An existing private enum/out contract stays independent of callee branches."""
import copy,json,re
import v666_root_execution_fixture as base
f=base.f
feature=base.feature;impl=base.impl;graph=base.graph;caller=base.caller
caller_node='frame/invoke';frame_id=caller+'/graph:frame';peer_id=caller+'/node:peer/node:after'
root=base.root;function=base.function;manifest=base.manifest;edge=base.edge
nested_mode=True;forward_caller_mode=True;out_mode=True;data_mode=True;result_code=10;expected_review_members=12
initial_stdout='callee:1\nafter:10\nprivate:17:10\nroot-after:10';final_stdout='callee:1\nprivate:17:10\nroot-after:10'
execution={'primary':'next','members':[{'id':'next','name':'Continue','value':0},{'id':'done','name':'Done','value':17}]}
signature={'args':[{'type':'long','name':'amount'},{'type':'int','name':'result','mode':'out'}],'return':'void'}
select={'id':'select','kind':'code','control':'switch','intent':'원래 private 실행 선택','signature':copy.deepcopy(signature),'arguments':{'amount':{'input':'amount'}},'forwardCallerStorage':True,'executionEnum':copy.deepcopy(execution),'implementation':'Select.node.json'}
inner=copy.deepcopy(base.cg);inner.pop('feature');inner.pop('contractHash')
invoke=inner['nodes'][0];invoke['arguments']['amount']={'input':'amount'};invoke['forwardCallerStorage']=True;invoke['branchOwner']='select';inner['nodes'][1]['branchOwner']='select';inner['edges'][-1]['to']='return:select'
inner.update(schema=2,executionExitMode=True,entry='select',nodes=[select,*inner['nodes']],edges=[edge('select','exit:return'),edge('select','invoke','case:done'),edge('select','exit:proceed','case:next'),*inner['edges']],exits={'return':{'executionBranch':'done'},'proceed':{'executionBranch':'next'}})
frame={'id':'frame','kind':'graph','control':'switch','intent':'기존 private 분기17·out 계약','signature':copy.deepcopy(signature),'arguments':{'amount':{'constant':1}},'executionSource':'select','executionEnum':copy.deepcopy(execution),'graph':inner}
def code(id,file):return {'id':id,'kind':'code','control':'next','intent':id,'signature':{'args':[{'type':'int','name':'value'}],'return':'void'},'arguments':{'value':{'node':'frame','output':'result'}},'implementation':file}
branch=code('private_branch','PrivateBranch.node.json');branch['branchOwner']='frame'
outer=copy.deepcopy(base.cg)
outer.update(entry='frame',nodes=[frame,code('root_after','RootAfter.node.json'),branch],edges=[edge('frame','root_after'),edge('frame','private_branch','case:done'),edge('private_branch','return:frame'),edge('root_after','exit:return')],exits={'return':{'node':'frame','output':'result'}})
peer={'schema':1,'profile':'sync-acyclic-switch-v1','entry':'after','nodes':[{'id':'after','kind':'code','control':'next','intent':'같은 local ID의 보존할 형제','signature':{'args':[],'return':'int'},'arguments':{},'implementation':'PeerAfter.node.json'}],'edges':[edge('after','exit:return')],'exits':{'return':{'node':'after','output':'return'}}}
outer['nodes'].append({'id':'peer','kind':'graph','control':'next','intent':'실행하지 않는 보존할 형제','signature':{'args':[],'return':'int'},'arguments':{},'graph':peer})
(f.project/'Main.graph.json').write_text(json.dumps(outer,ensure_ascii=False))
context={'implementation':f.n+'MainBody','feature':f.n+'Main','signature':{'args':[],'return':'int'},'imports':{base.alias:{'feature':feature,'scope':None,'signature':base.call_sig}}}
defs=f.metadata('featureBlueprintNodes',featureSource=base.main,implementationContext=context,bodyTarget='common',graph=outer,featureContracts={feature:function});assert defs['state']=='node-definitions',defs
for key,file,source in [('frame/select','Select.node.json','// private enum과 출력 원문 보존 😀\r\nresult=-5;return Result.Done;\r\n'),('frame/after','After.node.json','global::System.Console.WriteLine("after:"+value);'),('root_after','RootAfter.node.json','global::System.Console.WriteLine("root-after:"+value);'),('private_branch','PrivateBranch.node.json','global::System.Console.WriteLine("private:17:"+value);'),('peer/after','PeerAfter.node.json','return 999;')]:
 row=next(n for n in [*defs['nodes'],*defs['nestedNodes']] if n['id']==key)
 (f.project/file).write_text(json.dumps({'schema':1,'node':key.split('/')[-1],'definitionHash':row['definitionHash'],'source':source},ensure_ascii=False))
(f.project/'PeerAfter.node.json').chmod(0o400)
manifest.write_text(re.sub(r'element (\w+) \w+ "[^\"]+";',lambda m:m.group() if m[1] in {'Main','MainBody','Flow','FlowBody'} else '',manifest.read_text()))
physical={p:p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.parts};base.physical=physical
original=base.original;read=base.read;rpc=base.rpc;checkpoint=base.checkpoint;proof=base.proof
def build(name,code=None,stdout=None):
 base.build(name,result_code if code is None else code,final_stdout if stdout is None else stdout)
 g=json.loads((f.project/'Main.graph.json').read_text());node=next(n for n in g['nodes'] if n['id']=='frame');child=node['graph']
 for key in ['id','control','signature','executionSource','executionEnum']:assert node[key]==frame[key],key
 assert child['schema']==2 and child['executionExitMode'] is True and child['exits']==inner['exits']
 for p,value in physical.items():
  if p.name.endswith('.node.json'):assert p.read_bytes()==value,p
def plan(data):
 result=base.plan(data);result['caller']['node']=caller_node;return result
def request(data,selected=None):return base.request(data,selected or plan(data))
def __getattr__(name):return getattr(base,name)
