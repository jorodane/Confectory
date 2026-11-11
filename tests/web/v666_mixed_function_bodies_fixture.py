"""One ordinary Blueprint name contract and one explicit native body share Save."""
import copy,json,sys,hashlib
import v666_named_body_group_fixture as _prior
for _key in dir(_prior):
 if not _key.startswith('_'):globals()[_key]=getattr(_prior,_key)
mode=sys.argv[3]if len(sys.argv)>3 else'normal';blueprint_function=functions[0];body_function=functions[1]
function_path='elements/'+blueprint_function.split('::')[1]+'.celem';impl_path=blueprint_function.split('::')[1]+'Body.celem';graph_path='function.graph.json';record_path='function.node.json'
text='function '+blueprint_function+' (long amount,long count) -> long {value editorName='+json.dumps(labels[0],ensure_ascii=False)+';}'
prepared=f.metadata('blueprintPrepareFeature',id=blueprint_function,text=text,implementation=blueprint_function+'Body',graphPath=graph_path,nodePath=record_path)
(f.project/function_path).write_text(prepared['function']);(f.project/impl_path).write_text(prepared['implementation']);blueprint_graph=prepared['graph'];record=prepared['node'];defs=f.metadata('featureBlueprintNodes',featureSource=prepared['function'],graph=blueprint_graph);record['definitionHash']=next(row['definitionHash']for row in defs['nodes']if row['id']=='body');record['source']='return checked(amount+count); // 기존 Blueprint C# · 9223372036854775806 😀'+chr(13)+chr(10);(f.project/graph_path).write_text(json.dumps(blueprint_graph,ensure_ascii=False));(f.project/record_path).write_text(json.dumps(record,ensure_ascii=False,indent=2))
if '--boundary'in sys.argv:
 graph=copy.deepcopy(graph);graph['profile']='sync-acyclic-alias-locals-v1';graph['locals']=[dict(id='preserved',name='기존 지역값',type='long',initial={'constant':1})];(f.project/'caller.graph.json').write_text(json.dumps(graph,ensure_ascii=False))
snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.parts};original_result=40;edited_result=30

def request():
 result=n.request(copy.deepcopy(nexts[0]),{'amount':'leftAmount','count':'count'});result['changes'][0].update(name=labels[0],description='')
 fn=body_function;row=dict(type='function-edit',id=fn,hash=hashlib.sha256(result['units'][fn]['draft'].encode()).hexdigest(),name=labels[1],description='',signature=copy.deepcopy(olds[1]),mapping=dict(before=copy.deepcopy(olds[1]),args={'amount':'amount','count':'count'}))
 args={k:result[k]for k in ['project','manifest','id','units']};bodies=f.metadata('informationFunctionBodies',**args,function=fn,includeBlueprintTargets=True);rows={key:body for key,body in bodies.items()if not body['caller']};assert len(rows)==1 and all(body['sourceKind']=='csharp'for body in rows.values()),rows
 row['mapping']['bodies']={key:{k:body[k]for k in ['hash','path']}|dict(beforeSignature=copy.deepcopy(body['signature']),signature=copy.deepcopy(body['signature']),contract=copy.deepcopy(olds[1]),text=selected[fn])for key,body in rows.items()};result['changes'].append(row);return result

def unchanged():assert all((f.project/path).read_bytes()==raw for path,raw in snapshot.items())
def caller_arguments(index):return {a['name']:copy.deepcopy(graph['nodes'][index]['arguments'][b['name']])for a,b in zip(nexts[index]['args'],olds[index]['args'])}
def verify_rows(rows):
 merged={row['id']:{'draft':(f.project/row['path']).read_text()}for row in f.metadata('describe',project=str(f.manifest))['units']}|rows
 caller=copy.deepcopy(graph)
 for index,node in enumerate(caller['nodes']):node.update(signature=nexts[index],arguments=caller_arguments(index))
 assert json.loads(merged[n.caller+'Body/body:common']['draft'])==caller and merged[n.caller+'Body']['draft']==snapshot['CallerBody.celem'].decode()
 for index,fn in enumerate(functions):assert n.canonical(f.metadata('inspect',text=merged[fn]['draft'])['signature'])==nexts[index]
 assert merged[body_function+'Body']['draft']==snapshot[body_function.split('::')[1]+'Body.celem'].decode()and merged[body_function+'Body/body:common']['draft']==selected[body_function]
 assert n.canonical(f.metadata('inspect',text=merged[blueprint_function+'Body']['draft'])['signature'])==nexts[0]
 actual=json.loads(merged[blueprint_function+'Body/body:common']['draft']);expected=copy.deepcopy(blueprint_graph);expected['nodes'][0]['arguments']['amount']={'input':'leftAmount'};defs=f.metadata('featureBlueprintNodes',featureSource=merged[blueprint_function]['draft'],graph=actual);assert defs['state']=='node-definitions',defs;expected['contractHash']=defs['contractHash'];assert actual==expected
 code=json.loads(merged[blueprint_function+'Body/body:common/node:body']['draft']);assert code['source']==record['source'];assert{key:value for key,value in code.items()if key!='definitionHash'}=={key:value for key,value in record.items()if key!='definitionHash'}

def verify(checkpoint):
 rows={row['id']:row for row in json.loads(checkpoint.read_text())['changes']};verify_rows(rows);unchanged();ids=rows[owner]['atomicEditGroup'];assert set([owner,*functions,blueprint_function+'Body',blueprint_function+'Body/body:common',body_function+'Body/body:common',n.caller+'Body/body:common'])<=set(ids);return ids

def verify_live():
 verify_rows({})
 if 'accepted_description'in globals():assert f.metadata('inspect',text=n.a.info.read_text())['description']==accepted_description
 allowed={paths[body_function],function_path,'elements/'+body_function.split('::')[1]+'.celem',impl_path,graph_path,record_path,str(n.a.info.relative_to(f.project)),'caller.graph.json'}
 for path,raw in snapshot.items():
  if path not in allowed:assert(f.project/path).read_bytes()==raw,path
 execute(edited_result,'mixed-function-bodies-execution');f.checked('actual program30 combines the explicit Blueprint root input remap and native body; original Blueprint C#, native declaration, other C#, caller edges and IDs remain exact')

def after_contract(index):
 if index==1:_prior.after_contract(index)
