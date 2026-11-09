"""An unchanged ordinary Blueprint caller retains its code, locals and exact source."""
import copy,json,sys
_requested=sys.argv[3]if len(sys.argv)>3 else'normal'
if len(sys.argv)>3:sys.argv[3]='leaf'
import v666_body_imports_fixture as _prior
if len(sys.argv)>3:sys.argv[3]=_requested
for _key in dir(_prior):
 if not _key.startswith('_'):globals()[_key]=getattr(_prior,_key)
mode=_requested;_prior._base.mode=mode
retained_header='CallerBody.celem';retained_file='retained-code.node.json';retained_graph='caller.graph.json';retained=n.caller
original_result=41;edited_result=21
original_graph=copy.deepcopy(graph);graph=copy.deepcopy(graph);graph['profile']='sync-acyclic-alias-locals-v1'
node={'id':'preserved_code','kind':'code','control':'next','intent':'소유 호출자의 기존 계산과 지역값','implementation':retained_file,'signature':{'args':[{'name':'value','type':'long'},{'name':'bonus','type':'long'}],'return':'long'},'arguments':{'value':{'node':'invoke_second'},'bonus':{'local':'bonus'}}}
graph['locals']=[{'id':'bonus','name':'기존 보정','type':'long','initial':{'constant':1}},{'id':'exact','name':'정확한 큰 지역값','type':'long','initial':{'constant':9223372036854775806}}];graph['nodes'].append(node);graph['edges']=[{'from':'invoke','port':'next','to':'invoke_second'},{'from':'invoke_second','port':'next','to':'preserved_code'},{'from':'preserved_code','port':'next','to':'exit:return'}];graph['exits']={'return':{'node':'preserved_code'}}
(f.project/retained_graph).write_text(json.dumps(graph,ensure_ascii=False));defs=f.metadata('blueprintDescribeOwned',project=str(f.manifest),id=n.caller+'Body',text=(f.project/retained_header).read_text(),bodyTarget='common',graph=graph,definitionsOnly=True);assert defs['state']=='node-definitions',defs
record=json.loads((f.project/'function.node.json').read_text());record.update(node='preserved_code',definitionHash=next(row['definitionHash']for row in defs['nodes']if row['id']=='preserved_code'),source='return checked(value+bonus); // 기존 계산 원문 · 9223372036854775806 😀\r\n');(f.project/retained_file).write_bytes(json.dumps(record,ensure_ascii=False,indent=2).encode())
snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts};_prior._base.snapshot=snapshot;_prior._base.graph=graph
verify_rows=_prior._base.verify_rows

def verify(checkpoint):return _prior._base.verify(checkpoint)
def verify_live():
 _prior._base.verify_live()
 if 'accepted_description'in globals():assert f.metadata('inspect',text=n.a.info.read_text())['description']==accepted_description
 for path,raw in snapshot.items():
  if path not in set(paths.values())|{'elements/'+fn.split('::')[1]+'.celem'for fn in functions}|{str(n.a.info.relative_to(f.project))}:assert(f.project/path).read_bytes()==raw,path
 execute(edited_result,'retained-ordinary-caller');f.checked('unchanged ordinary caller graph/code/local IDs, CRLF Unicode source, edges and exact64 local survive; actual edited program21')
def caller_arguments(index):return copy.deepcopy(graph['nodes'][index]['arguments'])
def caller_exits():return copy.deepcopy(graph['exits'])
