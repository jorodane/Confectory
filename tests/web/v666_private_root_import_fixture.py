"""Original ordinary helper call/import in a private implementation, no ABI change."""
import copy,hashlib,json
import v666_private_return_import_fixture as _prior
for key in dir(_prior):
 if not key.startswith('_'):globals()[key]=getattr(_prior,key)

root_alias='fg_call_'+hashlib.sha256(helper.encode()).hexdigest()[:24];root_call='original-helper-result'
header=f.project/impl_path;header.write_bytes(header.read_bytes().replace(b'{',('{import '+helper+' as '+root_alias+' (long) -> long; // 원래 private 구현 import 😀\r\n').encode(),1));whole_header=header.read_bytes()
graph=json.loads(whole_flow)
graph['nodes'].append(dict(id=root_call,kind='call',control='next',intent='원래 helper 결과 보존',feature=helper,signature=dict(args=[dict(name='value',type='long')],**{'return':'long'}),arguments=dict(value=dict(node='inner')),x=779,y=127))
edge=next(row for row in graph['edges']if row['from']=='inner');assert edge['to']=='exit:return';edge['to']=root_call;graph['edges'].append(dict(**{'from':root_call},port='next',to='exit:return'));graph['exits']={'return':{'node':root_call}}
(f.project/graph_path).write_bytes((json.dumps(graph,ensure_ascii=False,indent=2)+'\r\n').encode());whole_flow=(f.project/graph_path).read_bytes()
# Authenticate the original source records against the resulting original graph.
defs=f.metadata('blueprintDescribeOwned',project=str(f.manifest),id=whole_implementation,text=whole_header.decode(),bodyTarget='common',graph=graph,definitionsOnly=True);assert defs['state']=='node-definitions',defs
for path,key in [(node_path,private_node),(extra_path,'preserve')]:
 record=json.loads((f.project/path).read_bytes());record['definitionHash']=next(row['definitionHash']for row in [*defs.get('nodes',[]),*defs.get('nestedNodes',[])]if row['id']==key);(f.project/path).write_bytes((json.dumps(record,ensure_ascii=False,indent=2)+'\r\n').encode())
whole_record=(f.project/node_path).read_bytes();extra_bytes=(f.project/extra_path).read_bytes();extra_mtime=(f.project/extra_path).stat().st_mtime_ns
snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts}
def sync():
 for module in [_prior,_prior._alias]:
  for name in ['snapshot','whole_header','whole_flow','whole_record','extra_bytes','extra_mtime','selected_helpers']:setattr(module,name,globals()[name])
  if 'accepted_description'in globals():module.accepted_description=accepted_description
sync()
def unchanged():sync();_prior.unchanged()
def request():sync();return _prior.request()
def verify_rows(rows):
 sync();_prior.verify_rows(rows);merged=rows.get(whole_graph,{}).get('draft',(f.project/graph_path).read_bytes().decode());assert merged==whole_flow.decode();assert json.loads(merged)==graph;assert(f.project/impl_path).read_bytes()==whole_header
def verify(checkpoint):
 sync();ids=_prior.verify(checkpoint);verify_rows({row['id']:row for row in json.loads(checkpoint.read_text())['changes']});return ids
def verify_live():
 sync();_prior.verify_live();verify_rows({});f.checked('original private implementation import and actual ordinary helper call, entire graph/layout/locals and ABI remain byte-identical while the two manual sources execute20')
def after_contract(index):sync();return _prior.after_contract(index)
