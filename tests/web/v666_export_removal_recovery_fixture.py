"""Two existing exports; delete one using unchanged native rewiring/default-out rules."""
import copy,json
import v666_export_binding_recovery_fixture as base
x=base.x;f=x.f
feature=base.feature;graph=base.graph;node=base.node;graph_file=base.graph_file;source_file=base.source_file;original_source=base.original_source
signature=base.signature;definition=copy.deepcopy(base.definition)
keep=copy.deepcopy(definition['nodes'][1]);keep.update(id='keep',intent='남길 출력 발행',output='right');keep['arguments']['value']={'constant':23};definition['nodes'].append(keep)
definition['edges'][-1]['to']='keep';definition['edges'].append(dict(**{'from':'keep','port':'next','to':'exit:return'}))
(f.project/graph_file).write_text(json.dumps(definition,ensure_ascii=False))
x.physical={p:p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.parts}
def read():return base.read()
def current():return any(n['id']==node for n in read()['nodes'])
def expected(value=23,removed=True):return(2 if removed else 1,'body\n'+('0'if removed else'17')+':'+str(value)+':0:False')
def after(value=23):
 out=copy.deepcopy(definition);out['nodes']=[n for n in out['nodes']if n['id']!=node];out['edges']=[e for e in out['edges']if e['from']!=node]
 for e in out['edges']:
  if e['to']==node:e['to']='keep'
 next(n for n in out['nodes']if n['id']=='keep')['arguments']['value']={'constant':value}
 return out
