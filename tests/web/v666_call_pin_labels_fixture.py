"""Owned positional call pins keep their native IDs despite different callee names."""
import json,copy,sys
import v666_root_input_name_recovery_fixture as base
x=base.x;f=base.f;callee=base.feature;feature=f.n+'Main';graph=f.n+'MainBody/body:common';node='invoke';parameter='constructor'if sys.argv[3]=='plain-prototype'else'supplied';input_label='計算 수량 😀';return_label='계산 결과 β';labels={'amount':input_label}
function=base.function
prepared=f.metadata('functionPresentation',project=str(f.manifest),manifest=f.manifest.read_text(),id=callee,text=function,drafts=[],changes=[dict(type='function-argument-names',text=json.dumps(labels,ensure_ascii=False)),dict(type='function-return-name',text=return_label)])
function=prepared['text']
if sys.argv[3]=='invalid':function=base.function.rstrip()[:-1]+'value editorArgumentNames="null";}'
elif sys.argv[3]=='plain-prototype':function=base.function
(f.project/'Pair.celem').write_text(function)
main_text=(f.project/'Main.celem').read_text();prepared=f.metadata('blueprintPrepareFeature',id=feature,text='function '+feature+' () -> int {}',implementation=f.n+'MainBody',graphPath='Call.graph.json',nodePath='Unused.node.json')
sig=dict(args=[dict(name=parameter,type='int')],**{'return':'int'})
g=dict(schema=1,profile='sync-acyclic-methods-v1',feature=feature,contractHash=prepared['graph']['contractHash'],entry=node,nodes=[dict(id=node,kind='call',control='next',intent='원래 위치 기반 호출',feature=callee,signature=sig,arguments={parameter:{'constant':7}})],edges=[dict(**{'from':node,'port':'next','to':'exit:return'})],exits={'return':{'node':node,'output':'return'}})
(f.project/'MainBody.celem').write_text(prepared['implementation'].replace('{', '{import '+callee+' as Callee (int) -> int;',1));(f.project/'Call.graph.json').write_text(json.dumps(g,ensure_ascii=False))
before_definitions=f.metadata('featureBlueprintNodes',featureSource=main_text,graph=g,featureContracts={callee:function});assert before_definitions['state']=='node-definitions',before_definitions
canonical_alias=next(row['alias']for row in before_definitions['imports']if row['feature']==callee)
p=f.project/'MainBody.celem';p.write_text(p.read_text().replace(' as Callee ', ' as '+canonical_alias+' '))
x.physical={p:p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.parts}
def read():return f.invoke('blueprint',dict(action='read',id=graph))['result']['result']
def row():return next(r for r in read()['nodes']if r['id']==node)
