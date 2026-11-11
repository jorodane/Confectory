"""Existing private/After/slot views retain exact original native callee/caller IDs and C#."""
import copy,json,sys
import v666_call_pin_labels_fixture as base
x=base.x;f=base.f;callee=base.callee;feature=base.feature;root=base.graph;graph=root+'/graph:inside';node=base.node;parameter=base.parameter;input_label=base.input_label;return_label=base.return_label
child=copy.deepcopy(base.g);child.pop('feature');child.pop('contractHash')
g=copy.deepcopy(base.g);g.update(profile='sync-acyclic-methods-v1',entry='inside',nodes=[dict(id='inside',kind='graph',control='next',intent='원래 내부 호출',signature=dict(args=[],**{'return':'int'}),arguments={},graph=child)],edges=[dict(**{'from':'inside','port':'next','to':'exit:return'})],exits={'return':{'node':'inside','output':'return'}})
context=next((v for v in sys.argv[4:]if v in ['after','slot']),'private');owner=None
if context=='after':
 graph=root;parameter='amount';g=copy.deepcopy(base.g);g['nodes'][0]['signature']['args'][0]['name']=parameter;g['nodes'][0]['arguments']={parameter:{'constant':7}};after=f.metadata('blueprintCallAfter',functionText=base.function);g['nodes'][0]['postCall']={k:after[k]for k in ['contractHash','source','helpers']}
elif context=='slot':
 owner=f.n+'Unit';p=f.project/'Unit.celem';p.write_text(p.read_text().rstrip()[:-1]+'provide '+feature+' with '+f.n+'MainBody;}')
(f.project/'Call.graph.json').write_text(json.dumps(g,ensure_ascii=False))
definitions=f.metadata('blueprintDescribeOwned',project=str(f.manifest),id=f.n+'MainBody',text=(f.project/'MainBody.celem').read_text(),bodyTarget='common',graph=g,definitionsOnly=True);assert definitions['state']=='node-definitions',definitions
x.physical={p:p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.parts}
def read():
 slot={}
 if owner:
  info=f.invoke('schema',dict(id=owner))['state']['schema'];slot=dict(owner=owner,ownerHash=info['textHash'],ownerRevision=info['revision'])
 return f.invoke('blueprint',dict(action='read',id=graph,**slot))['result']['result']
def row():return next(r for r in read()['nodes']if r['id']==node)
