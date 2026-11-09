"""One owned root, existing output storage alias and an explicitly edited C# body."""
import copy,json
import v666_text_pair_recovery_fixture as base
x=base.x;f=base.f;feature=base.feature;graph=base.graph;node=base.node;graph_file=base.graph_file;source_file=base.source_file
original_source=base.original_source;text=base.text;late=base.late;name='계산한 결과 α 😀';late_name='나중 결과 β 🛡️'
def read():return base.read()
def current():return base.current()
def checkpoint():return base.checkpoint()
def aliases():return read().get('locals',[])
def physical_confirmed(wanted_name,wanted_source,alias_id):
 expected=copy.deepcopy(base.base.definition);expected['locals']=[dict(id=alias_id,name=wanted_name,type='int',source=dict(node=node,output='return'))];expected['exits']['return']=dict(local=alias_id)
 assert json.loads((f.project/graph_file).read_text())==expected
 record=json.loads(x.physical[f.project/source_file]);record['source']=wanted_source
 assert json.loads((f.project/source_file).read_text())==record
 assert all(p.read_bytes()==raw for p,raw in x.physical.items()if p.name not in(graph_file,source_file))
