"""Explicit native value input addition retains all original inputs and output consumers."""
import copy,hashlib,json,subprocess,sys
import v536_information_shared_bodies_fixture as _editor
for _key in dir(_editor):
 if not _key.startswith('_'):globals()[_key]=getattr(_editor,_key)
old={'args':[{'name':'amount','type':'long'},{'name':'real','type':'double'}],'return':'long'}
olds=[copy.deepcopy(old),copy.deepcopy(old)];nexts=copy.deepcopy(olds)
for sig in nexts:sig['args'].append({'name':'step','type':'long'})
new=nexts[0];native={'args':[{'name':'nativeAmount','type':'long'},{'name':'nativeReal','type':'double'}],'return':'long'}
native_after=copy.deepcopy(native);native_after['args'].append({'name':'step','type':'long'})
undo_steps=3;original_result=38;edited_result=46;helper=f.n+'StableReturnHelper';helper_body='stable-return-helper.csbody';retained_header='StableReturnHelperBody.celem';retained_file=helper_body;retained_graph='caller.graph.json';sources={};selected={};paths={}
for name,kind,text in [('StableReturnHelper','function','function '+helper+' (long value) -> long {provide '+helper+' with '+helper+'Body;}'),('StableReturnHelperBody','implementation','implementation '+helper+'Body for '+helper+' (long value) -> long {body common "'+helper_body+'";}')]:
 (f.project/(name+'.celem')).write_text(text);f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element '+name+' '+kind+' "'+name+'.celem";registry Confectory.Build.DotNet',1))
(f.project/helper_body).write_bytes('// 原래 읽기 원문 😀\r\nreturn checked(value+3);\r\n'.encode())
for index,fn in enumerate(functions):
 path=('function'if index==0 else'second')+'-native.csbody';paths[fn]=path
 (f.project/('elements/'+fn.split('::')[1]+'.celem')).write_text('function '+fn+' (long amount,double real) -> long {provide '+fn+' with '+fn+'Body;value editorName='+json.dumps(labels[index],ensure_ascii=False)+';}')
 (f.project/(fn.split('::')[1]+'Body.celem')).write_text('implementation '+fn+'Body for '+fn+' (long nativeAmount,double nativeReal) -> long {import '+helper+' as StableHelper (long) -> long;body common "'+path+'";}')
 sources[fn]='return calls.StableHelper.Invoke(checked(nativeAmount+1)); // 原래 별도 native 이름 😀\n'
 selected[fn]='return calls.StableHelper.Invoke(checked(nativeAmount+step)); // 직접 선택한 long 입력 사용 · 😀\n'
 (f.project/path).write_bytes(sources[fn].encode())
prepared=f.metadata('blueprintPrepareFeature',id=n.caller,text=n.caller_source,implementation=n.caller+'Body',graphPath='caller.graph.json',nodePath='unused.node.json')
graph=prepared['graph'];graph.update(profile='sync-acyclic-implicit-out-v1',nodes=[],entry='',edges=[],exits={'return':None});header=prepared['implementation']
for fn,node in zip(functions,['invoke','invoke_second']):
 linked=f.metadata('blueprintPrepareCall',id=n.caller+'Body',text=header,targetText=(f.project/('elements/'+fn.split('::')[1]+'.celem')).read_text(),graph=graph,definition={'id':node,'feature':fn,'intent':'원래 out/return 소비 · '+node,'control':'next'});header,graph=linked['implementation'],linked['graph']
graph['nodes'][0]['arguments']={'amount':{'input':'first'},'real':{'constant':1.25}}
graph['nodes'][1]['arguments']={'amount':{'node':'invoke'},'real':{'constant':2.5}}
graph.update(entry='invoke',edges=[{'from':'invoke','port':'next','to':'invoke_second'},{'from':'invoke_second','port':'next','to':'exit:return'}],exits={'return':{'node':'invoke_second'}})
(f.project/'Caller.celem').write_text(prepared['function']);(f.project/'CallerBody.celem').write_text(header);(f.project/'caller.graph.json').write_bytes((json.dumps(graph,ensure_ascii=False,indent=2)+'\n').replace('\n','\r\n').encode())
(f.project/'MainBody.celem').write_text('implementation '+f.n+'MainBody for '+f.n+'Main () -> int {import '+n.caller+' as SharedCaller (long,long) -> long;body common "Main.csbody";}')
(f.project/'Main.csbody').write_text('// Fixture-only native argument and execution probe; unchanged by Save.\nvar binding=calls.SharedCaller.GetType();\nvar importsType=binding.Assembly.GetType(binding.FullName+"Imports")!;\nvar imports=global::System.Activator.CreateInstance(importsType,true)!;\nvar properties=importsType.GetProperties();\nif(properties.Length!=2)throw new global::System.Exception("two native imports required");\nbool changed=global::System.Environment.GetEnvironmentVariable("CONFECTORY_INPUT_ADDITION_PROBE")=="added";\nforeach(var property in properties){\n var invoke=property.PropertyType.GetMethod("Invoke")!;var p=invoke.GetParameters();\n if(invoke.ReturnType!=typeof(long)||p.Length!=(changed?3:2)||p[0].ParameterType!=typeof(long)||p[1].ParameterType!=typeof(double)||global::System.Linq.Enumerable.Any(p,x=>x.ParameterType.IsByRef)||changed&&p[2].ParameterType!=typeof(long))throw new global::System.Exception("wrong value argument ABI");\n object?[] args=changed?new object?[]{30L,1.25,5L}:new object?[]{30L,1.25};object? resultValue=invoke.Invoke(property.GetValue(imports),args);\n if(!global::System.Object.Equals(resultValue,changed?38L:34L)||!global::System.Object.Equals(args[0],30L)||!global::System.Object.Equals(args[1],1.25)||changed&&!global::System.Object.Equals(args[2],5L))throw new global::System.Exception("new argument or original values changed");\n}\nint result=checked((int)calls.SharedCaller.Invoke(30,5));global::System.Console.WriteLine(result);return result;\n')

snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts}
def unchanged():assert all((f.project/path).read_bytes()==raw for path,raw in snapshot.items())
def request():
 r=n.request(copy.deepcopy(nexts[0]),{a['name']:a['name']for a in old['args']});fn=functions[1];r['changes'].append(dict(type='function-edit',id=fn,hash=hashlib.sha256(r['units'][fn]['draft'].encode()).hexdigest(),name=labels[1],description='',signature=copy.deepcopy(nexts[1])))
 for index,row in enumerate(r['changes']):
  args={k:r[k]for k in ['project','manifest','id','units']};bodies=f.metadata('informationFunctionBodies',**args,function=row['id'],includeBlueprintTargets=True);own={key:body for key,body in bodies.items()if not body['caller']};assert len(own)==1 and all(body['sourceKind']=='csharp'for body in own.values())
  callers=f.metadata('informationFunctionInputs',**args,function=row['id']);row.update(name=labels[index],description='')
  row['mapping']={'before':copy.deepcopy(old),'args':{a['name']:a['name']for a in old['args']},'bodies':{key:{k:body[k]for k in ['hash','path']}|dict(beforeSignature=copy.deepcopy(native),signature=copy.deepcopy(native_after),contract=copy.deepcopy(nexts[index]),text=selected[row['id']])for key,body in own.items()},'callers':{key:{k:plan[k]for k in ['graph','node','hash']}|dict(inputs={'amount':'amount','real':'real','step':{'valueJson':'5'}},disconnect={})for key,plan in callers.items()}}
 return r

def expected_graph():
 expected=copy.deepcopy(graph)
 for index,node in enumerate(expected['nodes']):node['signature']=copy.deepcopy(nexts[index]);node['arguments']['step']={'constant':5}
 expected['nodes'][1]['arguments']['amount']={'node':'invoke'};expected['exits']={'return':{'node':'invoke_second'}};return expected
def caller_arguments(index):return copy.deepcopy(expected_graph()['nodes'][index]['arguments'])
def caller_exits():return copy.deepcopy(expected_graph()['exits'])
def verify_rows(rows):
 merged={row['id']:{'draft':(f.project/row['path']).read_bytes().decode('utf-8-sig')}for row in f.metadata('describe',project=str(f.manifest))['units']}|rows
 assert json.loads(merged[n.caller+'Body/body:common']['draft'])==expected_graph()
 assert n.canonical(f.metadata('inspect',text=merged[n.caller+'Body']['draft'])['signature'])==n.canonical(f.metadata('inspect',text=snapshot['CallerBody.celem'].decode())['signature'])
 for index,fn in enumerate(functions):
  assert n.canonical(f.metadata('inspect',text=merged[fn]['draft'])['signature'])==nexts[index]
  assert n.canonical(f.metadata('inspect',text=merged[fn+'Body']['draft'])['signature'])==native_after
  assert merged[fn+'Body/body:common']['draft']==selected[fn]
def verify(checkpoint):
 rows={row['id']:row for row in json.loads(checkpoint.read_text())['changes']};verify_rows(rows);unchanged();ids=rows[owner]['atomicEditGroup'];assert set(functions+[fn+'Body'for fn in functions]+[fn+'Body/body:common'for fn in functions]+[owner,n.caller+'Body',n.caller+'Body/body:common'])<=set(ids);return ids

def execute(expected,name):
 result=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),'build',str(f.manifest),'portable'],env=f.env,text=True,capture_output=True);(f.case/(name+'-build.log')).write_text(result.stdout+result.stderr);assert result.returncode==0,result.stdout[-3000:]+result.stderr[-1000:];report=json.loads(result.stdout);run=subprocess.run(report['run'],env=f.env|{'CONFECTORY_INPUT_ADDITION_PROBE':'original'if name.startswith('original')else'added'},text=True,capture_output=True);(f.case/(name+'-run.json')).write_text(json.dumps(dict(exit=run.returncode,stdout=run.stdout,stderr=run.stderr)));assert(run.returncode,run.stdout.strip())==(expected,str(expected)),(run.returncode,run.stdout,run.stderr)
def verify_live():
 verify_rows({})
 if 'accepted_description'in globals():assert f.metadata('inspect',text=n.a.info.read_text())['description']==accepted_description
 allowed=set(paths.values())|{'elements/'+fn.split('::')[1]+'.celem'for fn in functions}|{fn.split('::')[1]+'Body.celem'for fn in functions}|{str(n.a.info.relative_to(f.project)),'CallerBody.celem','caller.graph.json'}
 for path,raw in snapshot.items():
  if path not in allowed:assert(f.project/path).read_bytes()==raw,path
 execute(edited_result,'native-return-execution');f.checked('actual IInvoke appends value long step and receives explicit5; providers return34 to38 and caller38 to46 through the explicitly authored body; nativeAmount/nativeReal aliases, old bindings, caller ABI, helper, IDs and routes preserved')

def edit_contract(popover,index):
 from playwright.sync_api import expect
 before=popover.locator('[data-signature-id]').evaluate_all('(rows)=>rows.map(row=>row.dataset.signatureId)');popover.locator('[data-signature-add=inputs]').click();field=popover.locator('[data-signature-kind=inputs] .feature-io-row').last
 observed=field.evaluate('(row)=>({id:row.dataset.signatureId,name:row.querySelector("[data-signature-name]").value,readonly:row.querySelector("[data-signature-name]").readOnly})');assert observed['id']not in before and not observed['readonly'];(f.case/('new-input-row-'+str(index)+'.json')).write_text(json.dumps(dict(before=before,created=observed),ensure_ascii=False))
 field.locator('[data-signature-name]').fill('step');field.locator('[data-signature-type]').click();f.page.get_by_role('dialog',name='속성 타입 선택',exact=True).locator('[data-type=long]').click()
def has_mapping_dialog(index):return False
def after_contract(index):
 from playwright.sync_api import expect
 dialog=f.page.get_by_role('dialog',name='호출 계약 갱신',exact=True);expect(dialog).to_be_visible();dialog.locator('[data-abi-input=amount]').select_option('pin:amount');dialog.locator('[data-abi-input=real]').select_option('pin:real');dialog.locator('[data-abi-input=step]').select_option('value');dialog.locator('[data-abi-value=step]').fill('5');dialog.locator('[data-abi-remap-accept]').click();expect(dialog).to_have_count(0);f.idle()
 _editor.sources=sources;_editor.selected=selected;_editor.after_contract(index)
def verify_pins(panel,index):
 from playwright.sync_api import expect
 method=panel.locator('[data-inline-method="'+functions[index]+'"]');
 expect(method.locator('[data-pin-side=outputs] [data-function-pin-name=결과]')).to_have_attribute('data-function-pin-type','정수');expect(method.locator('[data-pin-side=inputs] [data-function-pin-name=step]')).to_have_attribute('data-function-pin-type','정수')
