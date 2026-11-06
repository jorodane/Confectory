"""One existing owned ordinary node: its three authored text fields, no contract change."""
import copy,json
import v666_text_pair_recovery_fixture as base
x=base.x;f=base.f;feature=base.feature;graph=base.graph;node=base.node;graph_file=base.graph_file;source_file=base.source_file
original_source=base.original_source;original_name=base.original_name;name=base.name;late_name=base.late_name;text=base.text;late=base.late
original_intent=next(n for n in base.base.definition['nodes']if n['id']==node)['intent'];intent='기존 계약으로 계산한 값을 반환합니다 α 😀';late_intent='늦게 수정한 계산 설명 β 🛡️'
def read():return base.read()
def current():return base.current()
def checkpoint():return base.checkpoint()
def physical_confirmed(wanted_name,wanted_source,wanted_intent):
 expected=copy.deepcopy(base.base.definition);row=next(n for n in expected['nodes']if n['id']==node);row.update(displayName=wanted_name,intent=wanted_intent)
 assert json.loads((f.project/graph_file).read_text())==expected
 defs=f.metadata('featureBlueprintNodes',featureSource=base.base.function,graph=expected);record=json.loads(x.physical[f.project/source_file]);record.update(source=wanted_source,definitionHash=next(n for n in defs['nodes']if n['id']==node)['definitionHash'])
 assert json.loads((f.project/source_file).read_text())==record
 assert all(p.read_bytes()==raw for p,raw in x.physical.items()if p.name not in (graph_file,source_file))
