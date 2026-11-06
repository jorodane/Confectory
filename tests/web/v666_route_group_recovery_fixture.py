"""Three existing next edges; explicit reordering preserves all node/source/data identities."""
import copy,json
import v666_root_input_name_recovery_fixture as base
x=base.x;f=base.f;n=base.n;feature=base.feature;graph=base.graph;graph_file=base.graph_file
function=base.function;definition=copy.deepcopy(base.definition)
original={'first':'second','body':'first','second':'third'}
selected={'first':'third','body':'second','second':'first'}
late=original
for node in ['first','second','third']:
 definition['nodes'].append(dict(id=node,kind='code',control='next',intent='기존 '+node,signature=dict(args=[],**{'return':'void'}),arguments={},implementation='Pair.'+node+'.node.json'))
definition['edges']=[dict(**{'from':node,'port':'next','to':target})for node,target in [('body','first'),('first','second'),('second','third'),('third','exit:return')]]
(f.project/graph_file).write_text(json.dumps(definition,ensure_ascii=False))
defs=f.metadata('featureBlueprintNodes',featureSource=function,graph=definition);assert defs['state']=='node-definitions',defs
for node in ['first','second','third']:
 (f.project/('Pair.'+node+'.node.json')).write_text(json.dumps(dict(schema=1,node=node,definitionHash=next(row['definitionHash']for row in defs['nodes']if row['id']==node),source='// 원문·줄바꿈 보존 😀\r\nglobal::System.Console.WriteLine("'+node+'");\r\n'),ensure_ascii=False))
x.physical={p:p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.parts}
def read():return base.read()
def current():return {node:next((e['to']for e in read()['edges']if e['from']==node and e['port']=='next'),'')for node in original}
def edits(routes):return [dict(action='route',node=node,port='next',to=target)for node,target in routes.items()]
def after(routes):
 doc=copy.deepcopy(definition)
 for edge in doc['edges']:
  if edge['from']in routes and edge['port']=='next':edge['to']=routes[edge['from']]
 return doc
expected=(10,'body\nfirst\nsecond\nthird\n10')
def result(routes):return (10,'body\nsecond\nfirst\nthird\n10')if routes==selected else expected
