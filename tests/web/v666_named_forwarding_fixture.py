"""Explicit public value-name/native text edits preserve private forwarded storage."""
import copy,json
import v666_named_nested_fixture as _prior
for _key in dir(_prior):
 if not _key.startswith('_'):globals()[_key]=getattr(_prior,_key)
graph=copy.deepcopy(graph);inner=graph['nodes'][0]['graph']['nodes'][0]['graph']
for index in range(2):
 original=copy.deepcopy(inner['nodes'][index]);call=copy.deepcopy(original);call.update(id='forwarded',forwardCallerStorage=True,arguments={a['name']:{'input':a['name']}for a in olds[index]['args']})
 child={'schema':1,'profile':'sync-acyclic-nested-v1','nodes':[call],'entry':'forwarded','edges':[{'from':'forwarded','port':'next','to':'exit:return'}],'exits':{'return':{'node':'forwarded'}},'locals':[{'id':'exact','name':'원래 전달 저장 프레임 값','type':'long','initial':{'constant':9223372036854775804}}]}
 if index==1:
  forwarded={'id':'inner','kind':'graph','control':'next','intent':'기존 두 번째 전달 계층','signature':copy.deepcopy(olds[index]),'arguments':{a['name']:{'input':a['name']}for a in olds[index]['args']},'forwardCallerStorage':True,'graph':child}
  child={'schema':1,'profile':'sync-acyclic-nested-v1','nodes':[forwarded],'entry':'inner','edges':[{'from':'inner','port':'next','to':'exit:return'}],'exits':{'return':{'node':'inner'}}}
 inner['nodes'][index]={'id':original['id'],'kind':'graph','control':'next','intent':'원래 전달 호출 '+str(index),'signature':copy.deepcopy(olds[index]),'arguments':copy.deepcopy(original['arguments']),'graph':child}
(f.project/retained_graph).write_bytes((json.dumps(graph,ensure_ascii=False,indent=2)+'\n').replace('\n','\r\n').encode())
defs=f.metadata('blueprintDescribeOwned',project=str(f.manifest),id=n.caller+'Body',text=(f.project/retained_header).read_text(),bodyTarget='common',graph=graph,definitionsOnly=True);assert defs['state']=='node-definitions',defs
for path,key in [(retained_file,'outer/inner/preserved_code'),('sibling-code.node.json','sibling/preserved_code')]:
 record=json.loads((f.project/path).read_text());record['definitionHash']=next(row['definitionHash']for row in defs['nestedNodes']if row['id']==key);(f.project/path).write_bytes((json.dumps(record,ensure_ascii=False,indent=2)+'\n').replace('\n','\r\n').encode())
snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts}
def unchanged():assert all((f.project/path).read_bytes()==raw for path,raw in snapshot.items())
def expected_graph():
 expected=copy.deepcopy(graph);frames=expected['nodes'][0]['graph']['nodes'][0]['graph']['nodes']
 for index in range(2):
  child=frames[index]['graph'];call=child['nodes'][0]
  if index==1:call=call['graph']['nodes'][0]
  before=copy.deepcopy(call['arguments']);call.update(signature=copy.deepcopy(nexts[index]),arguments={a['name']:before[b['name']]for a,b in zip(nexts[index]['args'],olds[index]['args'])})
 return expected
def verify_rows(rows):
 entries=f.metadata('describe',project=str(f.manifest))['units'];merged={row['id']:{'draft':(f.project/row['path']).read_bytes().decode('utf-8-sig')}for row in entries}|rows
 assert json.loads(merged[n.caller+'Body/body:common']['draft'])==expected_graph()
 assert merged[n.caller+'Body']['draft']==snapshot[retained_header].decode()
 for path in [retained_file,'sibling-code.node.json']:
  key=next(row['id']for row in entries if row['path']==path);assert merged[key]['draft']==snapshot[path].decode(),path
 for index,fn in enumerate(functions):
  assert n.canonical(f.metadata('inspect',text=merged[fn]['draft'])['signature'])==nexts[index]
  assert merged[fn+'Body']['draft']==snapshot[fn.split('::')[1]+'Body.celem'].decode()
  assert merged[fn+'Body/body:common']['draft']==selected[fn]
def verify(checkpoint):
 rows={row['id']:row for row in json.loads(checkpoint.read_text())['changes']};verify_rows(rows);unchanged();ids=rows[owner]['atomicEditGroup'];assert set(functions+[fn+'Body/body:common'for fn in functions]+[owner,n.caller+'Body/body:common'])<=set(ids);return ids
def verify_live():
 verify_rows({})
 if 'accepted_description'in globals():assert f.metadata('inspect',text=n.a.info.read_text())['description']==accepted_description
 allowed=set(paths.values())|{'elements/'+fn.split('::')[1]+'.celem'for fn in functions}|{str(n.a.info.relative_to(f.project)),retained_graph}
 for path,raw in snapshot.items():
  if path not in allowed:assert(f.project/path).read_bytes()==raw,path
 execute(edited_result,'named-forwarded-caller');f.checked('actual program21 retains both forwarded private storage chains, parent bindings/contracts/locals, qualified C# bytes, IDs/routes and native parameters while explicitly remapping the public input name')
