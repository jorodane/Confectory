"""Existing next edges plus stable output storage names; C# bytes never change."""
import copy,json
import v666_route_group_recovery_fixture as base
x=base.x;f=base.f;feature=base.feature;graph=base.graph;node='body';graph_file=base.graph_file
name='실행 결과 α 😀';late_name='나중 결과 β 🛡️';original=base.original;selected=base.selected;late=base.late
read=base.read;current=base.current;edits=base.edits;result=base.result
physical=x.physical.copy()
def checkpoint():return next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))
def aliases():return read().get('locals',[])
def physical_confirmed(wanted_name,routes,alias_id):
 expected=base.after(routes);expected['locals']=[dict(id=alias_id,name=wanted_name,type='int',source=dict(node=node,output='return'))];expected['exits']['return']=dict(local=alias_id)
 actual=json.loads((f.project/graph_file).read_text());key=lambda e:(e['from'],e['port'],e['to']);assert sorted(actual.pop('edges'),key=key)==sorted(expected.pop('edges'),key=key);assert actual==expected
 assert all(p.read_bytes()==raw for p,raw in physical.items()if p!=f.project/graph_file)
