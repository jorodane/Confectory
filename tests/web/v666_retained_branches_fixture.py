"""Existing execution choices remain read-only while two native bodies change."""
import copy,json,sys
import v666_retained_callers_fixture as _prior
for _key in dir(_prior):
 if not _key.startswith('_'):globals()[_key]=getattr(_prior,_key)
boolean='--boolean' in sys.argv
original_graph=copy.deepcopy(graph);graph=copy.deepcopy(graph)
selector_file='retained-selector.node.json'
selector={'id':'preserved_choice','kind':'code','control':'branch'if boolean else'switch','intent':'원래 호출자의 실행 선택','signature':{'args':[{'name':'value','type':'long'}],'return':'bool'if boolean else'void'},'arguments':{'value':{'node':'preserved_code'}},'implementation':selector_file}
if not boolean:selector['executionEnum']={'primary':'continue','members':[{'id':'continue','name':'Continue','value':0},{'id':'positive','name':'Positive','value':17},{'id':'negative','name':'Negative','value':-3}]}
graph['profile']='sync-acyclic-switch-v1';graph['nodes'].append(selector)
next(e for e in graph['edges']if e['from']=='preserved_code')['to']=selector['id']
graph['edges'] += [{'from':selector['id'],'port':'true'if boolean else'case:positive','to':'exit:return'},{'from':selector['id'],'port':'false'if boolean else'case:negative','to':'exit:alternate'}]
if not boolean:graph['edges'].append({'from':selector['id'],'port':'next','to':'exit:fallback'})
graph['exits']['alternate']={'binary':{'operator':'+','type':'long','operands':[{'node':'preserved_code'},{'constant':1}]}}
if not boolean:graph['exits']['fallback']={'constant':-7}
(f.project/retained_graph).write_text(json.dumps(graph,ensure_ascii=False))
defs=f.metadata('blueprintDescribeOwned',project=str(f.manifest),id=n.caller+'Body',text=(f.project/retained_header).read_text(),bodyTarget='common',graph=graph,definitionsOnly=True);assert defs['state']=='node-definitions',defs
for filename,node,source in [(retained_file,'preserved_code',None),(selector_file,selector['id'],'return value>30;'if boolean else'return value>30?Result.Positive:Result.Negative;')]:
 p=f.project/filename;record=json.loads(p.read_text())if p.exists()else{'schema':1,'node':node,'source':source+' // 분기 ID17/-3 · 원문 😀\r\n'}
 record['definitionHash']=next(row['definitionHash']for row in defs['nodes']if row['id']==node);p.write_bytes(json.dumps(record,ensure_ascii=False,indent=2).encode())
original_result=41;edited_result=22
snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts}
_prior.snapshot=snapshot;_prior.graph=graph;_prior.original_graph=original_graph
_prior._prior._base.snapshot=snapshot;_prior._prior._base.graph=graph
def verify_live():
 _prior._prior._base.verify_live()
 if 'accepted_description'in globals():assert f.metadata('inspect',text=n.a.info.read_text())['description']==accepted_description
 for path,raw in snapshot.items():
  if path not in set(paths.values())|{'elements/'+fn.split('::')[1]+'.celem'for fn in functions}|{str(n.a.info.relative_to(f.project))}:assert(f.project/path).read_bytes()==raw,path
 execute(edited_result,'retained-execution-choice');f.checked('unchanged execution selector source, enum IDs/values, paths and caller locals survive; edited callees route through the original alternate exit to22')
