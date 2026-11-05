"""Existing outputs/serial graph; one explicit new export and two next connections."""
import copy,json
import v666_export_removal_recovery_fixture as base
x=base.x;f=x.f
feature=base.feature;graph=base.graph;graph_file=base.graph_file;source_file=base.source_file;original_source=base.original_source;definition=copy.deepcopy(base.definition);signature=base.signature
from_node='body';to_node='publish';output='spare';node='export_new'
def read():return base.read()
def current(node):return next((n for n in read()['nodes']if n['id']==node),None)
def current_value(node):return json.loads(current(node)['arguments'][0]['valueJson'])
def edits(node,value=37):return[dict(kind='create',node=node,output=output),dict(kind='value',node=node,valueJson=json.dumps({'constant':value},separators=(',',':'))),dict(kind='route',node=from_node,to=node),dict(kind='route',node=node,to=to_node)]
def after(node,value=37):
 out=copy.deepcopy(definition);out['nodes'].append(dict(id=node,kind='export',control='next',intent='Assign spare',output=output,signature=dict(args=[dict(name='value',type='int')],**{'return':'void'}),arguments=dict(value={'constant':value})));out['edges']=[e for e in out['edges']if e['from']!=from_node]+[dict(**{'from':from_node,'port':'next','to':node}),dict(**{'from':node,'port':'next','to':to_node})];return out
def expected(value=0):return(1,'body\n17:23:'+str(value)+':False')
