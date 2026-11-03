"""M12: qualified private caller; same local leaf ID in a readonly peer frame."""
import copy,json,re,sys
import v666_root_execution_fixture as base
f=base.f
feature=base.feature;impl=base.impl;graph=base.graph;caller=base.caller
caller_node='frame/invoke';frame_id=caller+'/graph:frame';peer_id=caller+'/node:peer/node:after'
root=base.root;function=base.function;manifest=base.manifest
edge=base.edge
nested_mode=True;out_mode=True;result_code=10
initial_stdout='callee:1\nafter:10\nroot-after:10';final_stdout='callee:1\nroot-after:10'
inner=copy.deepcopy(base.cg);inner.pop('feature');inner.pop('contractHash')
inner['nodes'][-1]['implementation']='NestedAfter.node.json'
outer=copy.deepcopy(base.cg)
outer['nodes']=[{'id':'frame','kind':'graph','control':'next','intent':'보존할 소유 private frame','signature':{'args':[],'return':'int'},'arguments':{},'graph':inner}, {'id':'root_after','kind':'code','control':'next','intent':'private 반환 뒤 기존 다음 줄','signature':{'args':[{'type':'int','name':'value'}],'return':'void'},'arguments':{'value':{'node':'frame','output':'return'}},'implementation':'RootAfter.node.json'}]
outer.update(entry='frame',edges=[edge('frame','root_after'),edge('root_after','exit:return')],exits={'return':{'node':'frame','output':'return'}})
peer={'schema':1,'profile':'sync-acyclic-switch-v1','entry':'after','nodes':[{'id':'after','kind':'code','control':'next','intent':'같은 local ID의 보존할 형제','signature':{'args':[],'return':'int'},'arguments':{},'implementation':'PeerAfter.node.json'}],'edges':[edge('after','exit:return')],'exits':{'return':{'node':'after','output':'return'}}}
outer['nodes'].append({'id':'peer','kind':'graph','control':'next','intent':'실행하지 않는 보존할 형제','signature':{'args':[],'return':'int'},'arguments':{},'graph':peer})
(f.project/'Main.graph.json').write_text(json.dumps(outer,ensure_ascii=False))
context={'implementation':f.n+'MainBody','feature':f.n+'Main','signature':{'args':[],'return':'int'},'imports':{base.alias:{'feature':feature,'scope':None,'signature':base.call_sig}}}
defs=f.metadata('featureBlueprintNodes',featureSource=base.main,implementationContext=context,bodyTarget='common',graph=outer,featureContracts={feature:function});assert defs['state']=='node-definitions',defs
for key,file,source in [('root_after','RootAfter.node.json','global::System.Console.WriteLine("root-after:"+value);'),('frame/after','NestedAfter.node.json','global::System.Console.WriteLine("after:"+value);'),('peer/after','PeerAfter.node.json','return 999;')]:
 row=next(n for n in [*defs['nodes'],*defs['nestedNodes']] if n['id']==key)
 (f.project/file).write_text(json.dumps({'schema':1,'node':key.split('/')[-1],'definitionHash':row['definitionHash'],'source':source},ensure_ascii=False))
(f.project/'PeerAfter.node.json').chmod(0o400)
manifest.write_text(re.sub(r'element (\w+) \w+ "[^"]+";',lambda m:m.group() if m[1] in {'Main','MainBody','Flow','FlowBody'} else '',manifest.read_text()))
physical={p:p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.parts};base.physical=physical
original=base.original;read=base.read;rpc=base.rpc;checkpoint=base.checkpoint;proof=base.proof

def build(*args,**kwargs):
 base.build(*args,**kwargs)
 for p,value in physical.items():
  if p.name.endswith('.node.json'):assert p.read_bytes()==value,p

def plan(data):
 result=base.plan(data);result['caller']['node']=caller_node;return result

def request(data,selected=None):return base.request(data,selected or plan(data))
