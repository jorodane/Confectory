"""The retained caller's own public input contract changes with its native callee."""
import copy,hashlib,json,subprocess
import v666_retained_callers_fixture as b
for key in dir(b):
 if not key.startswith('_'):globals()[key]=getattr(b,key)
caller_function,callee=functions;caller_impl=caller_function+'Body';caller_graph=caller_impl+'/body:common';caller_path='retained-owner.graph.json';code_path='retained-owner.node.json';code_id=caller_graph+'/node:preserved_code';header_path=caller_function.split('::')[1]+'Body.celem'
old_header=(f.project/header_path).read_text();lift=f.metadata('blueprintConversion',project=str(f.manifest),id=caller_impl,text=old_header,target='common',graphPath=caller_path,nodePath=code_path)
owned_graph=copy.deepcopy(graph);owned_graph['feature']=caller_function;owned_graph['contractHash']=lift['graph']['contractHash'];invoke=copy.deepcopy(owned_graph['nodes'][0]);invoke['feature']=callee;invoke['signature']=copy.deepcopy(old);invoke['arguments']={'amount':{'input':'amount'},'count':{'input':'count'}};invoke.update(x=172,y=84)
adjust=copy.deepcopy(owned_graph['nodes'][-1]);adjust['arguments']['value']={'node':'invoke'};adjust['implementation']=code_path;adjust.update(x=412,y=124);owned_graph['nodes']=[invoke,adjust];owned_graph['entry']='invoke';owned_graph['edges']=[{'from':'invoke','port':'next','to':'preserved_code'},{'from':'preserved_code','port':'next','to':'exit:return'}];owned_graph['exits']={'return':{'node':'preserved_code'}}
alias='fg_call_'+hashlib.sha256(callee.encode()).hexdigest()[:24];header='implementation '+caller_impl+' for '+caller_function+' (long amount,long count) -> long {import '+callee+' as '+alias+' (long,long) -> long;blueprint common "'+caller_path+'";}'
(f.project/header_path).write_bytes(header.encode());(f.project/caller_path).write_bytes((json.dumps(owned_graph,ensure_ascii=False,indent=2)+'\r\n').encode());defs=f.metadata('blueprintDescribeOwned',project=str(f.manifest),id=caller_impl,text=header,bodyTarget='common',graph=owned_graph,definitionsOnly=True);assert defs['state']=='node-definitions',defs
code=copy.deepcopy(record);code['definitionHash']=next(v['definitionHash']for v in defs['nodes']if v['id']=='preserved_code');(f.project/code_path).write_bytes((json.dumps(code,ensure_ascii=False,indent=2)+'\r\n').encode());code_bytes=(f.project/code_path).read_bytes();code_source=code['source'];nexts=copy.deepcopy(olds);nexts[0]['args'][0]['name']='leftAmount';nexts[1]['args'][0]['name']='rightAmount';original_result=42;edited_result=22
snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts};mtimes={p:(f.project/p).stat().st_mtime_ns for p in snapshot};changed_source_paths={paths[callee]};retained_file=code_path

def unchanged():assert all((f.project/p).read_bytes()==raw for p,raw in snapshot.items())
def request():
 r=n.request(copy.deepcopy(nexts[0]),{'amount':'leftAmount','count':'count'});r['changes'][0].update(name=labels[0],description='');fn=callee;unit=r['units'][fn];catalog=f.metadata('informationFunctionBodies',**{k:r[k]for k in ['project','manifest','id','units']},function=fn,includeBlueprintTargets=True);key=fn+'Body/body:common';body=catalog[key];plan={k:body[k]for k in ['hash','path']}|dict(beforeSignature=copy.deepcopy(native),signature=copy.deepcopy(native),contract=copy.deepcopy(nexts[1]),text=selected[fn]);r['changes'].append(dict(type='function-edit',id=fn,hash=hashlib.sha256(unit['draft'].encode()).hexdigest(),name=labels[1],description='',signature=copy.deepcopy(nexts[1]),mapping=dict(before=copy.deepcopy(old),args={'amount':'rightAmount','count':'count'},bodies={key:plan})));return r
def prepare(r,ok=True):
 p=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(dict(operation='informationDefinitions',**r)),env=f.env,text=True,capture_output=True,check=True);v=json.loads(p.stdout);assert bool(v['ok'])==ok,v;return v

def verify_rows(rows):
 merged={v['id']:dict(draft=(f.project/v['path']).read_bytes().decode('utf-8-sig'))for v in f.metadata('describe',project=str(f.manifest))['units']}|rows
 for index,fn in enumerate(functions):assert n.canonical(f.metadata('inspect',text=merged[fn]['draft'])['signature'])==nexts[index]
 expected=copy.deepcopy(owned_graph);expected['contractHash']=hashlib.sha256(json.dumps(dict(feature=caller_function,signature=nexts[0]),sort_keys=True,separators=(',',':')).encode()).hexdigest();expected['nodes'][0]['signature']=copy.deepcopy(nexts[1]);expected['nodes'][0]['arguments']={'rightAmount':{'input':'leftAmount'},'count':{'input':'count'}};assert json.loads(merged[caller_graph]['draft'])==expected
 expected=copy.deepcopy(graph)
 for index,node in enumerate(expected['nodes'][:2]):node['signature']=copy.deepcopy(nexts[index]);node['arguments']['leftAmount'if index==0 else'rightAmount']=node['arguments'].pop('amount')
 assert json.loads(merged[n.caller+'Body/body:common']['draft'])==expected;assert json.loads(merged[code_id]['draft'])==code;assert merged[callee+'Body/body:common']['draft']==selected[callee];assert merged[callee+'Body']['draft']==snapshot[callee.split('::')[1]+'Body.celem'].decode()
 for p in [code_path,retained_file,'retained-code.node.json',paths[caller_function]]:assert(f.project/p).read_bytes()==snapshot[p]and(f.project/p).stat().st_mtime_ns==mtimes[p]
def verify(checkpoint):
 rows={v['id']:v for v in json.loads(checkpoint.read_text())['changes']};verify_rows(rows);unchanged();ids=rows[owner]['atomicEditGroup'];assert set([owner,*functions,caller_impl,caller_graph,n.caller+'Body/body:common',callee+'Body/body:common'])<=set(ids);assert code_id not in ids;return ids
def verify_live():
 verify_rows({});allowed={str(n.a.info.relative_to(f.project)),header_path,caller_path,'CallerBody.celem','caller.graph.json',paths[callee],*['elements/'+fn.split('::')[1]+'.celem'for fn in functions]}
 for p,raw in snapshot.items():
  if p not in allowed:assert(f.project/p).read_bytes()==raw,p
 execute(edited_result,'retained-caller-contract');f.checked('explicit caller/callee public inputs and manual native callee body execute22; retained CSharp bytes, exact64 locals, layout and surrounding routes remain')
 if 'accepted_description'in globals():assert f.metadata('inspect',text=n.a.info.read_text())['description']==accepted_description

def edit_contract(popover,index):
 field=popover.locator('[data-signature-kind=inputs] [data-signature-id=arg0] [data-signature-name]');field.press('Shift+F10');f.page.locator('.context-menu').get_by_role('button',name='C# 이름 편집',exact=True).click();popover.locator('[data-signature-id=arg0] [data-signature-name]').fill(nexts[index]['args'][0]['name'])
def after_contract(index):
 if index==1:b.after_contract(index)
def validate_history():
 held=d.pending();trace=[held]
 for _ in range(3):f.owner().locator('[data-own-functions-toggle]').press('Control+z');trace.append(d.pending())
 assert not d.pending(),trace
 for _ in range(3):f.owner().locator('[data-own-functions-toggle]').press('Control+y')
 assert d.pending()==held
 (f.case/'retained-contract-history.json').write_text(json.dumps(trace,ensure_ascii=False,indent=2))
def caller_arguments(index):
 args=copy.deepcopy(graph['nodes'][index]['arguments']);args[nexts[index]['args'][0]['name']]=args.pop('amount');return args
def verify_pins(panel,index):
 from playwright.sync_api import expect
 method=panel.locator('[data-inline-method="'+functions[index]+'"]')
 for arg in nexts[index]['args']:expect(method.locator('[data-pin-side=inputs] [data-function-pin-name='+arg['name']+']')).to_have_count(1)
 expect(method.locator('[data-pin-side=outputs] [data-function-pin-name=결과]')).to_have_attribute('data-function-pin-type','정수')
