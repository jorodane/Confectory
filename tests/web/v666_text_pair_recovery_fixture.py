"""One existing directly owned root code node: display name and C# body together."""
import copy,json
import v666_root_input_name_recovery_fixture as base
x=base.x;f=base.f;feature=base.feature;graph=base.graph;node='body';graph_file=base.graph_file;source_file=base.source_file
original_source=base.original_source;original_name='body';name='직접 계산 α 😀';late_name='늦은 계산 β 😀'
text=original_source.replace('amount+3','amount+4');late=original_source.replace('amount+3','amount+5')
def read():return base.read()
def current():return next(n for n in read()['nodes']if n['id']==node)
def checkpoint():return next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))
def physical_confirmed(wanted_name,wanted_source):
 expected=copy.deepcopy(base.definition);next(n for n in expected['nodes']if n['id']==node)['displayName']=wanted_name
 assert json.loads((f.project/graph_file).read_text())==expected
 record=json.loads(x.physical[f.project/source_file]);record['source']=wanted_source
 assert json.loads((f.project/source_file).read_text())==record
 assert all(p.read_bytes()==raw for p,raw in x.physical.items()if p.name not in (graph_file,source_file))
