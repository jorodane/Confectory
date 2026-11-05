"""A saved, clean root contract group followed by ordinary owned source editing."""
import json
import v666_root_input_name_recovery_fixture as base
x=base.x;f=x.f;feature=base.feature;graph=base.graph;graph_file=base.graph_file;source_file=base.source_file
original_name=base.original_name;original_source=base.original_source.replace('\r\n','\n')
p=f.project/source_file;record=json.loads(p.read_text());record['source']=original_source;p.write_text(json.dumps(record,ensure_ascii=False))
p=f.project/graph_file;p.write_text(json.dumps(base.definition,separators=(',',':'),ensure_ascii=True))
x.physical={p:p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.parts}
text=original_source+'\n// 직접 입력한 후속 본문 α 😀';late=original_source+'\n// 저장 중 새로 입력한 후속 본문 β'
def read():return base.read()
def current():return next(row['source']for row in read()['nodes']if row['id']=='body')
def root_plan():return base.plan(original_name)
def checkpoint():return next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))
def complete_group():
 d=json.loads(checkpoint().read_text());g=next(u for u in d['changes']if u['id']==graph);assert set(g['rootContractGroup'])=={feature,f.n+'PairBody',graph};assert set(g['rootContractGroup'])<={u['id']for u in d['changes']};return d,g
expected=base.expected
