"""An explicit native value-to-out plan beside exact-ABI private C#/helpers."""
import copy,hashlib,json,re,subprocess
import v666_private_body_group_fixture as _private
for _key in dir(_private):
 if not _key.startswith('_'):globals()[_key]=getattr(_private,_key)
nexts=[copy.deepcopy(old),copy.deepcopy(old)];nexts[1]['args'][1]['mode']='out'
native_after=copy.deepcopy(native);native_after['args'][1]['mode']='out'
selected[functions[1]]='nativeCount=5;return checked(nativeAmount-nativeCount); // 명시 out 할당 · 😀\n'
(f.project/'Main.csbody').write_text('int result=checked((int)calls.SharedCaller.Invoke(30,5));bool changed=result==20;var binding=calls.SharedCaller.GetType();var importsType=binding.Assembly.GetType(binding.FullName+"Imports")!;var imports=System.Activator.CreateInstance(importsType,true)!;var properties=importsType.GetProperties();if(properties.Length!=2)throw new System.Exception("two original imports required");int outs=0;foreach(var property in properties){var invoke=property.PropertyType.GetMethod("Invoke")!;var parameters=invoke.GetParameters();if(invoke.ReturnType!=typeof(long)||parameters.Length!=2||parameters[0].ParameterType!=typeof(long)||parameters[0].IsOut||parameters[0].ParameterType.IsByRef)throw new System.Exception("wrong original ABI");if(parameters[1].IsOut){outs++;if(!changed||parameters[1].ParameterType!=typeof(long).MakeByRefType())throw new System.Exception("unexpected out ABI");object?[] arguments=new object?[]{30L,99L};var value=invoke.Invoke(property.GetValue(imports),arguments);if(!object.Equals(value,25L)||!object.Equals(arguments[1],5L))throw new System.Exception("out assignment/return lost");}else if(parameters[1].ParameterType!=typeof(long))throw new System.Exception("original value ABI lost");}if(outs!=(changed?1:0))throw new System.Exception("explicit out transition missing");System.Console.WriteLine(result);return result;')
caller_flow=json.loads((f.project/retained_graph).read_text());caller_flow['profile']='sync-acyclic-implicit-out-v1';(f.project/retained_graph).write_bytes((json.dumps(caller_flow,ensure_ascii=False,indent=2)+'\r\n').encode())
snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts}
def unchanged():
 assert all((f.project/path).read_bytes()==raw for path,raw in snapshot.items());assert(f.project/extra_path).stat().st_mtime_ns==extra_mtime

def request():
 r=_private.request();row=r['changes'][1];row['signature']=copy.deepcopy(nexts[1])
 for plan in row['mapping']['bodies'].values():plan.update(signature=copy.deepcopy(native_after),contract=copy.deepcopy(nexts[1]),text=selected[functions[1]])
 callers=f.metadata('informationFunctionInputs',**{k:r[k]for k in ['project','manifest','id','units']},function=functions[1]);assert len(callers)==1
 row['mapping']['callers']={key:{k:plan[k]for k in ['graph','node','hash']}|dict(inputs={'amount':'amount'},disconnect={'count':plan['bindings']['count']},outputs={'return':'return'})for key,plan in callers.items()}
 return r

def prepare(r,ok=True):
 p=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(dict(operation='informationDefinitions',**r)),env=f.env,text=True,capture_output=True,check=True);v=json.loads(p.stdout);assert bool(v['ok'])==ok,v;return v

def verify_rows(rows):
 merged={v['id']:dict(draft=(f.project/v['path']).read_bytes().decode('utf-8-sig'))for v in f.metadata('describe',project=str(f.manifest))['units']}|rows
 assert json.loads(merged[whole_node]['draft'])==json.loads(whole_record)|dict(source=selected[whole_function],helpers=selected_helpers)
 assert merged[whole_graph]['draft']==whole_flow.decode()and merged[whole_implementation]['draft']==whole_header.decode()
 assert(f.project/original_path).read_bytes()==snapshot[original_path]and(f.project/extra_path).read_bytes()==extra_bytes and(f.project/extra_path).stat().st_mtime_ns==extra_mtime
 assert extra_id not in rows;fn=functions[1];assert merged[fn+'Body/body:common']['draft']==selected[fn]
 for index,fn in enumerate(functions):assert n.canonical(f.metadata('inspect',text=merged[fn]['draft'])['signature'])==nexts[index]
 assert n.canonical(f.metadata('inspect',text=merged[functions[1]+'Body']['draft'])['signature'])==native_after
 expected=json.loads(snapshot[retained_graph]);node=next(v for v in expected['nodes']if v.get('feature')==functions[1]);node['signature']=copy.deepcopy(nexts[1]);node['arguments'].pop('count');assert json.loads(merged[n.caller+'Body/body:common']['draft'])==expected
 pattern=r'(import\s+'+re.escape(functions[1])+r'\s+as\s+\w+\s*)\(([^)]*)\)';matches=list(re.finditer(pattern,merged[n.caller+'Body']['draft']));assert len(matches)==1 and re.sub(r'\s+','',matches[0][2])=='long,outlong'
 assert re.sub(pattern,lambda m:m[1]+'(<explicit role>)',merged[n.caller+'Body']['draft'])==re.sub(pattern,lambda m:m[1]+'(<explicit role>)',snapshot[retained_header].decode())

def caller_arguments(index):
 value=copy.deepcopy(json.loads(snapshot[retained_graph])['nodes'][index]['arguments'])
 if index==1:value.pop('count')
 return value

def verify(checkpoint):
 document=json.loads(checkpoint.read_text());assert document['version']==1 and 'nativeTypeProfile'not in document;rows={v['id']:v for v in document['changes']};verify_rows(rows);unchanged();receipt=rows[owner]['slotSaveReceipt'];assert len(receipt['nativeBodyContexts'])==2 and 'nativeTypeProofs'not in receipt and 'nativeTypeReads'not in receipt
 assert {graph_path,node_path,retained_graph,retained_header,extra_path}<=set(receipt['readGuards']);ids=rows[owner]['atomicEditGroup'];assert set([owner,*functions,whole_node,functions[1]+'Body',functions[1]+'Body/body:common',n.caller+'Body',n.caller+'Body/body:common'])<=set(ids)and extra_id not in ids;return ids

def verify_live():
 verify_rows({});allowed={node_path,paths[functions[1]],str(n.a.info.relative_to(f.project)),retained_header,retained_graph,functions[1].split('::')[1]+'Body.celem',*['elements/'+fn.split('::')[1]+'.celem'for fn in functions]}
 for path,raw in snapshot.items():
  if path not in allowed:assert(f.project/path).read_bytes()==raw,path
 if 'accepted_description'in globals():assert f.metadata('inspect',text=n.a.info.read_text())['description']==accepted_description
 execute(20,'private-value-out');f.checked('actual shared caller20 and unique native IInvoke out ABI/value5/direct return25; private ABI/helpers, aliases, graph/layout/locals and independent source bytes/mtime retained')
undo_steps=2
def edit_contract(popover,index):pass
def after_contract(index):
 if index==0:return _private.after_contract(index)
 from playwright.sync_api import expect
 held=d.pending();selector='[data-inline-method="'+functions[index]+'"] [data-function-edit], [data-inline-method="'+functions[index]+'"] [data-function-write-direct]';dialog=f.page.locator('[role=dialog]:has([data-code-source])')
 def fill():
  field=dialog.locator('[data-code-source]');assert sources[functions[index]]in field.input_value();field.evaluate("el=>{el.focus();el.setSelectionRange(el.value.indexOf('(')+1,el.value.indexOf(')'));}");f.page.keyboard.insert_text('long nativeAmount, out long nativeCount');field.evaluate('(el,text)=>{el.focus();const i=el.value.indexOf(text);if(i<0)throw Error("Original native body missing");el.setSelectionRange(i,i+text.length);}',sources[functions[index]]);f.page.keyboard.insert_text(selected[functions[index]]);f.idle()
 f.owner().locator(selector).click();expect(dialog).to_be_visible();fill();dialog.locator('[data-code-cancel]').click();assert d.pending()==held
 f.owner().locator(selector).click();expect(dialog).to_be_visible();fill();f.page.screenshot(path=str(f.case/'private-native-value-out-source.png'));dialog.locator('[data-code-save]').click();expect(dialog).to_have_count(0)
 remap=f.page.get_by_role('dialog',name='호출 계약 갱신',exact=True);expect(remap).to_be_visible();assert remap.locator('section[data-abi-target]').count()==1;remap.locator('[data-abi-input=amount]').select_option('pin:amount');remap.locator('[data-abi-disconnect=count]').select_option('disconnect');remap.locator('[data-abi-output=return]').select_option('return');f.page.screenshot(path=str(f.case/'private-value-out-caller.png'));remap.locator('[data-abi-remap-accept]').click();expect(remap).to_have_count(0);f.idle();saved=d.pending()
 for _ in range(2):f.owner().locator('[data-own-functions-toggle]').press('Control+z')
 assert d.pending()==held
 for _ in range(2):f.owner().locator('[data-own-functions-toggle]').press('Control+y')
 assert d.pending()==saved;f.checked('original native parameter/source editor explicitly changes one value to out, assigns it, acknowledges old caller removal and preserves original return; cancel and two-step Undo/Redo retain private plan')
def verify_pins(panel,index):
 from playwright.sync_api import expect
 method=panel.locator('[data-inline-method="'+functions[index]+'"]');expect(method.locator('[data-pin-side=inputs] [data-function-pin-name=amount]')).to_have_count(1)
 if index==1:
  expect(method.locator('[data-pin-side=inputs] [data-function-pin-name=count]')).to_have_count(0);expect(method.locator('[data-pin-side=outputs] [data-function-pin-name=count]')).to_have_attribute('data-function-pin-type','정수')
 else:expect(method.locator('[data-pin-side=inputs] [data-function-pin-name=count]')).to_have_count(1)
