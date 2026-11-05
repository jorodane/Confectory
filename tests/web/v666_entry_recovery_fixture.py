"""Two authored, initially detached start nodes; original execution is unchanged."""
import json
import v666_root_execution_fixture as x
f=x.f
for node,label in [('lead','lead'),('lateLead','late')]:
 x.cg['nodes'].append(dict(id=node,kind='code',control='next',intent='기존 시작 동작 '+label,signature=dict(args=[],**{'return':'void'}),arguments={},implementation=node+'.node.json'))
 x.cg['edges'].append(x.edge(node,'invoke'))
(f.project/'Main.graph.json').write_text(json.dumps(x.cg,ensure_ascii=False))
defs=f.metadata('featureBlueprintNodes',featureSource=(f.project/'Main.celem').read_text(),graph=x.cg,featureContracts={x.feature:(f.project/'Flow.celem').read_text()});assert defs['state']=='node-definitions',defs
for node,label in [('lead','lead'),('lateLead','late')]:
 (f.project/(node+'.node.json')).write_text(json.dumps(dict(schema=1,node=node,definitionHash=next(n['definitionHash']for n in defs['nodes']if n['id']==node),source='global::System.Console.WriteLine("'+label+'");'),ensure_ascii=False))
x.physical={p:p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.parts}
def current():return x.read(x.caller)['entry']
