"""Two existing ordinary nodes: display names only, source/contracts/edges unchanged."""
import copy,json
import v666_root_input_name_recovery_fixture as base
x=base.x;f=base.f;feature=base.feature;graph=base.graph;graph_file=base.graph_file
nodes=['body','after'];original={node:node for node in nodes};selected={'body':'계산 이름 α 😀','after':'후속 이름 β 🛡️'};late={'body':'늦은 계산 γ','after':'늦은 후속 δ'}
definition=copy.deepcopy(base.definition);definition['nodes'].append(dict(id='after',kind='code',control='next',intent='기존 후속 C#',signature=dict(args=[],**{'return':'void'}),arguments={},implementation='Pair.after.node.json'))
definition['edges']=[dict(**{'from':'body','port':'next','to':'after'}),dict(**{'from':'after','port':'next','to':'exit:return'})]
defs=f.metadata('featureBlueprintNodes',featureSource=base.function,graph=definition);assert defs['state']=='node-definitions',defs
sources={'body':base.original_source,'after':'// 두 번째 원문 보존 😀\r\nglobal::System.Console.WriteLine("after");\r\n'}
for node,path in [('body',base.source_file),('after','Pair.after.node.json')]:
 (f.project/path).write_text(json.dumps(dict(schema=1,node=node,definitionHash=next(n['definitionHash']for n in defs['nodes']if n['id']==node),source=sources[node]),ensure_ascii=False))
(f.project/graph_file).write_text(json.dumps(definition,ensure_ascii=False));x.physical={p:p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.parts}
def read():return base.read()
def current():return {n['id']:n.get('displayName',n['id'])for n in read()['nodes']if n['id']in nodes}
def edits(names):return [dict(action='rename',node=node,text=names[node])for node in nodes]
def checkpoint():return next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))
def confirmed(names):
 expected=copy.deepcopy(definition)
 for row in expected['nodes']:
  if row['id']in names:row['displayName']=names[row['id']]
 assert json.loads((f.project/graph_file).read_text())==expected
 assert all(p.read_bytes()==raw for p,raw in x.physical.items()if p.name!=graph_file)
expected=(10,'body\nafter\n10')
