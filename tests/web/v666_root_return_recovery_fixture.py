"""Existing root return terminal, with no export writer or contract changes."""
import copy,json
import v666_root_execution_fixture as x
f=x.f;graph=x.caller;feature=x.main_id;node='$exit:return';graph_file='Main.graph.json';source_file='After.node.json'
original_value=copy.deepcopy(x.cg['exits']['return']);definition=copy.deepcopy(x.cg)
def read():return x.read(graph)
def current():return json.loads(next(e for e in read()['exits']if e['name']=='return')['valueJson'])
