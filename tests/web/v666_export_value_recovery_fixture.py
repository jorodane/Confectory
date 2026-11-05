"""Existing owned export assignment; original public contract and C# stay intact."""
import copy,json
import v666_root_execution_fixture as x
f=x.f
node='publish_return';graph=x.caller;feature=x.main_id;graph_file='Main.graph.json';source_file='After.node.json'
original_value={'node':'invoke','output':'result'}
x.cg['nodes'].append(dict(id=node,kind='export',control='next',intent='기존 반환 출력 발행',output='return',signature=dict(args=[dict(name='value',type='int')],**{'return':'void'}),arguments=dict(value=copy.deepcopy(original_value))))
next(e for e in x.cg['edges']if e['from']=='after')['to']=node
x.cg['edges'].append(x.edge(node,'exit:return'));x.cg['exits']['return']=None
(f.project/graph_file).write_text(json.dumps(x.cg,ensure_ascii=False))
definition=copy.deepcopy(x.cg)
x.physical={p:p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.parts}
def read():return x.read(graph)
def current():
 return json.loads(next(n for n in read()['nodes']if n['id']==node)['arguments'][0]['valueJson'])
