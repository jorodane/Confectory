"""One already lifted whole CSharp body and one native body in the same owner."""
import copy,hashlib,json,subprocess,time
import v536_information_shared_bodies_fixture as _prior
for _key in dir(_prior):
 if not _key.startswith('_'):globals()[_key]=getattr(_prior,_key)
for fn in functions:
 p=f.project/('elements/'+fn.split('::')[1]+'.celem');text=p.read_text();assert 'provide 'not in text;p.write_text(text.replace('{','{provide '+fn+' with '+fn+'Body;',1))
(f.project/'MainBody.celem').write_text('implementation '+f.n+'MainBody for '+f.n+'Main () -> int {import '+n.caller+' as SharedCaller (long,long) -> long;body common \"Main.csbody\";}')
(f.project/'Main.csbody').write_text('int result=checked((int)calls.SharedCaller.Invoke(30,5));global::System.Console.WriteLine(result);return result;')
whole_function=functions[0];whole_implementation=whole_function+'Body';whole_graph=whole_implementation+'/body:common';graph_path='whole-group.graph.json';node_path='whole-group.node.json';original_path=paths[whole_function];impl_path=whole_function.split('::')[1]+'Body.celem';cpp=(f.project/impl_path).read_text();converted=f.metadata('blueprintConversion',project=str(f.manifest),id=whole_implementation,text=cpp,target='common',graphPath=graph_path,nodePath=node_path);assert 'graph'in converted and'node'in converted,converted
(f.project/impl_path).write_text(converted['implementation']);(f.project/graph_path).write_text(json.dumps(converted['graph'],ensure_ascii=False));(f.project/node_path).write_text(json.dumps(converted['node'],ensure_ascii=False));whole_node=whole_graph+'/node:'+next(v['id']for v in converted['graph']['nodes']if v.get('implementationContext')is not None);whole_record=(f.project/node_path).read_bytes();whole_flow=(f.project/graph_path).read_bytes();whole_header=(f.project/impl_path).read_bytes();snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts};_prior.snapshot=snapshot
original_result=40;edited_result=20;retained_header='CallerBody.celem';retained_graph='caller.graph.json';retained_file=graph_path

def unchanged():assert all((f.project/path).read_bytes()==raw for path,raw in snapshot.items())
def request():
 r=n.request(copy.deepcopy(old),{'amount':'amount','count':'count'});fn=functions[1];r['changes'].append(dict(type='function-edit',id=fn,hash=hashlib.sha256(r['units'][fn]['draft'].encode()).hexdigest(),name=labels[1],description='',signature=copy.deepcopy(old)))
 for index,row in enumerate(r['changes']):
  row.update(name=labels[index],description='');bodies=f.metadata('informationFunctionBodies',**{k:r[k]for k in ['project','manifest','id','units']},function=row['id'],includeBlueprintTargets=True);own={key:body for key,body in bodies.items()if not body['caller']};assert len(own)==1;key,body=next(iter(own.items()));assert body['sourceKind']==('whole-csharp'if index==0 else'csharp'),body
  plan={k:body[k]for k in ['hash','path']}|dict(beforeSignature=copy.deepcopy(native),signature=copy.deepcopy(native),contract=copy.deepcopy(old),text=selected[row['id']])
  if index==0:assert key==whole_node;plan['whole']=copy.deepcopy(body['whole'])
  row['mapping']=dict(before=copy.deepcopy(old),args={'amount':'amount','count':'count'},bodies={key:plan})
 return r

def verify_rows(rows):
 merged={row['id']:dict(draft=(f.project/row['path']).read_bytes().decode('utf-8-sig'))for row in f.metadata('describe',project=str(f.manifest))['units']}|rows
 assert json.loads(merged[whole_node]['draft'])==json.loads(whole_record)|{'source':selected[whole_function]};assert merged[whole_graph]['draft']==whole_flow.decode();assert merged[whole_implementation]['draft']==whole_header.decode();assert(f.project/original_path).read_bytes()==snapshot[original_path]
 fn=functions[1];assert merged[fn+'Body/body:common']['draft']==selected[fn];assert merged[n.caller+'Body/body:common']['draft']==snapshot[retained_graph].decode();assert merged[n.caller+'Body']['draft']==snapshot[retained_header].decode()
 for fn in functions:assert n.canonical(f.metadata('inspect',text=merged[fn]['draft'])['signature'])==old

def verify(checkpoint):
 rows={row['id']:row for row in json.loads(checkpoint.read_text())['changes']};verify_rows(rows);unchanged();ids=rows[owner]['atomicEditGroup'];assert set([owner,*functions,whole_node,functions[1]+'Body/body:common'])<=set(ids);return ids

def execute(expected,name):
 build=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),'build',str(f.manifest),'portable'],env=f.env,text=True,capture_output=True);(f.case/(name+'-build.log')).write_text(build.stdout+build.stderr);assert build.returncode==0,build.stdout[-2000:]+build.stderr[-2000:];out=subprocess.run(json.loads(build.stdout)['run'],env=f.env,text=True,capture_output=True);(f.case/(name+'-run.json')).write_text(json.dumps(dict(exit=out.returncode,stdout=out.stdout,stderr=out.stderr)));assert(out.returncode,out.stdout.strip())==(expected,str(expected)),(out.returncode,out.stdout,out.stderr)

def verify_live():
 verify_rows({});allowed={node_path,paths[functions[1]],str(n.a.info.relative_to(f.project)),*['elements/'+fn.split('::')[1]+'.celem'for fn in functions]}
 for path,raw in snapshot.items():
  if path not in allowed:assert(f.project/path).read_bytes()==raw,path
 if 'accepted_description'in globals():assert f.metadata('inspect',text=n.a.info.read_text())['description']==accepted_description
 execute(edited_result,'whole-native-group');f.checked('actual whole/native manual bodies execute20; original csbody, graph/header, callers/contracts, IDs/routes and outside files remain exact')
