"""An original private callee changes ref to out; both caller ref ABIs stay intact."""
import copy,hashlib,json,re,subprocess
import v666_private_body_group_fixture as _role
for key in dir(_role):
 if not key.startswith('_'):globals()[key]=getattr(_role,key)
old=copy.deepcopy(old);old['args'][1]['mode']='ref';olds=[copy.deepcopy(old),copy.deepcopy(old)];nexts=copy.deepcopy(olds);nexts[1]['args'][1]['mode']='out'
native=copy.deepcopy(native);native['args'][1]['mode']='ref';native_before=copy.deepcopy(native);native_after=copy.deepcopy(native);native_after['args'][1]['mode']='out'
callee=functions[1];root_alias='fg_call_'+hashlib.sha256(callee.encode()).hexdigest()[:24];root_call='original-selected-value';private_alias='fg_call_'+hashlib.sha256(functions[0].encode()).hexdigest()[:24]
for index,fn in enumerate(functions):
 (f.project/('elements/'+fn.split('::')[1]+'.celem')).write_text('function '+fn+' (long amount,ref long count) -> long {provide '+fn+' with '+fn+'Body;value editorName='+json.dumps(labels[index],ensure_ascii=False)+';}')
(f.project/impl_path).write_bytes((f.project/impl_path).read_bytes().replace(b'long count)',b'ref long count)').replace(b'{',('{import '+callee+' as '+root_alias+' (long,ref long) -> long; // 원래 ref 저장소 호출 😀\r\n').encode(),1))
(f.project/(callee.split('::')[1]+'Body.celem')).write_text('implementation '+callee+'Body for '+callee+' (long nativeAmount,ref long nativeCount) -> long {body common "'+paths[callee]+'";}')
sources[callee]='nativeCount=40;return checked(nativeAmount+nativeCount); // 원래 ref 쓰기 · 😀\n';selected[callee]='nativeCount=6;return checked(nativeAmount-nativeCount); // 명시 out 할당 · 😀\n';(f.project/paths[callee]).write_text(sources[callee])
whole_header=(f.project/impl_path).read_bytes();graph=json.loads(whole_flow)
initial=f.metadata('blueprintPrepareFeature',id=whole_function,text='function '+whole_function+' (long amount,ref long count) -> long {}',implementation=whole_implementation,graphPath=graph_path,nodePath='unused-ref-root.node.json')
graph['contractHash']=initial['graph']['contractHash'];graph['nodes'].append(dict(id=root_call,kind='call',control='next',intent='원래 선택 ref 호출',feature=callee,signature=copy.deepcopy(olds[1]),arguments=dict(amount=dict(node='inner'),count=dict(input='count')),x=779,y=127))
edge=next(row for row in graph['edges']if row['from']=='inner');assert edge['to']=='exit:return';edge['to']=root_call;graph['edges'].append(dict(**{'from':root_call},port='next',to='exit:return'));graph['exits']={'return':{'node':root_call}}
(f.project/graph_path).write_bytes((json.dumps(graph,ensure_ascii=False,indent=2)+'\r\n').encode());whole_flow=(f.project/graph_path).read_bytes()
defs=f.metadata('blueprintDescribeOwned',project=str(f.manifest),id=whole_implementation,text=whole_header.decode(),bodyTarget='common',graph=graph,definitionsOnly=True);assert defs['state']=='node-definitions',defs
for path,key in [(node_path,private_node),(extra_path,'preserve')]:
 record=json.loads((f.project/path).read_bytes());record['definitionHash']=next(row['definitionHash']for row in [*defs.get('nodes',[]),*defs.get('nestedNodes',[])]if row['id']==key);(f.project/path).write_bytes((json.dumps(record,ensure_ascii=False,indent=2)+'\r\n').encode())
whole_record=(f.project/node_path).read_bytes();extra_bytes=(f.project/extra_path).read_bytes();extra_mtime=(f.project/extra_path).stat().st_mtime_ns
prepared=f.metadata('blueprintPrepareFeature',id=n.caller,text=n.caller_source.replace('long second','ref long second'),implementation=n.caller+'Body',graphPath=retained_graph,nodePath='unused-ref-caller.node.json');caller=prepared['graph'];caller.update(profile='sync-acyclic-ref-v1',nodes=[],entry='',edges=[],exits={'return':None});header=prepared['implementation']
for fn,node in zip(functions,['invoke','invoke_second']):
 linked=f.metadata('blueprintPrepareCall',id=n.caller+'Body',text=header,targetText=(f.project/('elements/'+fn.split('::')[1]+'.celem')).read_text(),graph=caller,definition=dict(id=node,feature=fn,intent='원래 ref 저장소 호출 · '+node,control='next'));header,caller=linked['implementation'],linked['graph']
caller['nodes'][0]['arguments']={'amount':{'input':'first'},'count':{'input':'second'}};caller['nodes'][1]['arguments']={'amount':{'node':'invoke'},'count':{'input':'second'}};caller.update(entry='invoke',edges=[{'from':'invoke','port':'next','to':'invoke_second'},{'from':'invoke_second','port':'next','to':'exit:return'}],exits={'return':{'node':'invoke_second'}})
(f.project/'Caller.celem').write_text(prepared['function']);(f.project/retained_header).write_text(header);(f.project/retained_graph).write_bytes((json.dumps(caller,ensure_ascii=False,indent=2)+'\r\n').encode())
(f.project/'MainBody.celem').write_text('implementation '+f.n+'MainBody for '+f.n+'Main () -> int {import '+n.caller+' as SharedCaller (long,ref long) -> long;body common "Main.csbody";}')
main='// Fixture-only direct ref/out and original storage probe; Save preserves this source.\nvar binding=calls.SharedCaller.GetType();var importsType=binding.Assembly.GetType(binding.FullName+"Imports")!;var imports=System.Activator.CreateInstance(importsType,true)!;var properties=importsType.GetProperties();if(properties.Length!=2)throw new System.Exception("two original imports required");\nbool changed=importsType.GetProperty("CALLEE")!.PropertyType.GetMethod("Invoke")!.GetParameters()[1].IsOut;\nlong second=5;int result=checked((int)calls.SharedCaller.Invoke(30,ref second));if(result!=(changed?13:115)||second!=(changed?5:40))throw new System.Exception("original caller ref storage changed");\nforeach(var property in properties){bool callee=property.Name=="CALLEE";if(!callee&&property.Name!="PRIVATE")throw new System.Exception("unexpected original import");var invoke=property.PropertyType.GetMethod("Invoke")!;var p=invoke.GetParameters();bool byRef=true;if(invoke.ReturnType!=typeof(long)||p.Length!=2||p[0].ParameterType!=typeof(long)||p[1].IsOut!=(callee&&changed)||p[1].ParameterType!=(byRef?typeof(long).MakeByRefType():typeof(long)))throw new System.Exception("wrong ref/out ABI");object?[] arguments=new object?[]{30L,5L};var value=invoke.Invoke(property.GetValue(imports),arguments);long expected=changed?(callee?24L:19L):(callee?70L:75L);if(!object.Equals(value,expected)||!object.Equals(arguments[1],changed?(callee?6L:5L):40L))throw new System.Exception("ref/out copy or explicit source lost");}\nSystem.Console.WriteLine(result);return result;\n'.replace('CALLEE',root_alias).replace('PRIVATE',private_alias)
(f.project/'Main.csbody').write_text(main);original_result=115;edited_result=13
snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts}
def sync():
 for module in [_role,_role.b,_role.b._prior]:
  for name in ['snapshot','whole_header','whole_flow','whole_record','extra_bytes','extra_mtime','selected_helpers','old','native']:setattr(module,name,globals()[name])
  if 'accepted_description'in globals():module.accepted_description=accepted_description
sync()
def unchanged():sync();_role.unchanged()
def request():
 sync();r=_role.request();row=r['changes'][1];row['signature']=copy.deepcopy(nexts[1]);row['mapping']['before']=copy.deepcopy(olds[1])
 for plan in row['mapping']['bodies'].values():plan.update(beforeSignature=copy.deepcopy(native_before),signature=copy.deepcopy(native_after),contract=copy.deepcopy(nexts[1]),text=selected[callee])
 callers=f.metadata('informationFunctionInputs',**{k:r[k]for k in ['project','manifest','id','units']},function=callee);assert len(callers)==2,callers
 row['mapping']['callers']={key:{k:plan[k]for k in ['graph','node','hash']}|dict(inputs={'amount':'amount'},disconnect={'count':plan['bindings']['count']},outputs={'return':'return'})for key,plan in callers.items()};return r
def prepare(r,ok=True):
 p=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(dict(operation='informationDefinitions',**r)),env=f.env,text=True,capture_output=True,check=True);v=json.loads(p.stdout);assert bool(v['ok'])==ok,v;return v
def current_whole(rows):
 r=request();r['units'].update(copy.deepcopy(rows));bodies=f.metadata('informationFunctionBodies',**{k:r[k]for k in ['project','manifest','id','units']},function=whole_function,includeBlueprintTargets=True);return bodies[whole_node]['whole']
def expected_graph(raw):
 result=json.loads(raw)
 for node in result['nodes']:
  if node.get('feature')==callee:node['signature']=copy.deepcopy(nexts[1]);node['arguments'].pop('count');result['exits']={'return':{'node':node['id']}}
 return result
root_pattern=r'(import\s+'+re.escape(callee)+r'\s+as\s+'+root_alias+r'\s*)\(([^)]*)\)'
pattern=r'(import\s+'+re.escape(callee)+r'\s+as\s+\w+\s*)\(([^)]*)\)'
def verify_header(text,raw,pattern):
 matches=list(re.finditer(pattern,text));assert len(matches)==1 and re.sub(r'\s+','',matches[0][2])=='long,outlong'
 assert re.sub(pattern,lambda m:m[1]+'(<explicit role>)',text)==re.sub(pattern,lambda m:m[1]+'(<explicit role>)',raw.decode())
def verify_rows(rows):
 sync();merged={v['id']:dict(draft=(f.project/v['path']).read_bytes().decode('utf-8-sig'))for v in f.metadata('describe',project=str(f.manifest))['units']}|rows
 assert json.loads(merged[whole_node]['draft'])==json.loads(whole_record)|dict(source=selected[whole_function],helpers=selected_helpers)
 assert json.loads(merged[whole_graph]['draft'])==expected_graph(whole_flow);verify_header(merged[whole_implementation]['draft'],whole_header,root_pattern)
 assert(f.project/original_path).read_bytes()==snapshot[original_path]and(f.project/extra_path).read_bytes()==extra_bytes and(f.project/extra_path).stat().st_mtime_ns==extra_mtime;assert extra_id not in rows
 assert merged[callee+'Body/body:common']['draft']==selected[callee]
 assert n.canonical(f.metadata('inspect',text=merged[callee+'Body']['draft'])['signature'])==native_after
 for index,fn in enumerate(functions):assert n.canonical(f.metadata('inspect',text=merged[fn]['draft'])['signature'])==nexts[index]
 assert json.loads(merged[n.caller+'Body/body:common']['draft'])==expected_graph(snapshot[retained_graph]);verify_header(merged[n.caller+'Body']['draft'],snapshot[retained_header],pattern)
def verify(checkpoint):
 document=json.loads(checkpoint.read_text());assert document['version']==1;rows={v['id']:v for v in document['changes']};verify_rows(rows);unchanged();receipt=rows[owner]['slotSaveReceipt'];assert receipt['version']==3 and len(receipt['nativeBodyContexts'])==2
 assert {impl_path,graph_path,paths[callee],callee.split('::')[1]+'Body.celem','elements/'+callee.split('::')[1]+'.celem',retained_header,retained_graph}<=set(receipt['readGuards']);ids=rows[owner]['atomicEditGroup'];assert {owner,*functions,whole_node,whole_graph,whole_implementation,callee+'Body',callee+'Body/body:common',n.caller+'Body',n.caller+'Body/body:common'}<=set(ids)and extra_id not in ids;return ids
def verify_live():
 verify_rows({});allowed={node_path,graph_path,impl_path,paths[callee],str(n.a.info.relative_to(f.project)),retained_graph,retained_header,callee.split('::')[1]+'Body.celem',*['elements/'+fn.split('::')[1]+'.celem'for fn in functions]}
 for path,raw in snapshot.items():
  if path not in allowed:assert(f.project/path).read_bytes()==raw,path
 if 'accepted_description'in globals():assert f.metadata('inspect',text=n.a.info.read_text())['description']==accepted_description
 execute(13,'private-callee-ref-out');f.checked('actual private and shared callers execute13 through two explicit original ref-input disconnections; direct native long24/out6 and private19/ref5 with caller ref5 unchanged; the new out stays separate, other input/return/private ABI, aliases, routes, coordinates, exact locals and unselected source bytes retained')
def caller_arguments(index):return copy.deepcopy(expected_graph(snapshot[retained_graph])['nodes'][index]['arguments'])
def caller_exits():return copy.deepcopy(expected_graph(snapshot[retained_graph])['exits'])
def after_contract(index):
 sync()
 if index==0:return _role.after_contract(index)
 from playwright.sync_api import expect
 held=d.pending();dialog=f.page.locator('[role=dialog]:has([data-code-source])');selector='[data-inline-method="'+callee+'"] [data-function-edit], [data-inline-method="'+callee+'"] [data-function-write-direct]'
 def open_edit():
  f.owner().locator(selector).click();choice=f.page.locator('[data-information-body="'+callee+'Body/body:common"]');expect(choice).to_be_visible();choice.click();expect(dialog).to_be_visible();return dialog.locator('[data-code-source]')
 field=open_edit()
 if mode=='reproduce-ui':
  text=field.input_value();assert re.match(r'public long Invoke\(long nativeAmount, ref long nativeCount\)',text);assert dialog.locator('[data-code-region=parameters]').count()==1
  field.evaluate("el=>{el.focus();el.setSelectionRange(el.value.indexOf('(')+1,el.value.indexOf(')'));}");f.page.keyboard.insert_text('long nativeAmount, out long nativeCount');dialog.locator('[data-code-save]').click();expect(dialog.locator('[data-code-error]')).to_be_visible();f.idle();(f.case/'baseline-rejection-diagnostic.json').write_text(json.dumps(dict(text=field.input_value(),pending=d.pending(),held=held,error=dialog.locator('[data-code-error]').inner_text()),ensure_ascii=False,indent=2));assert 'out long nativeCount'in field.input_value();rejected=d.pending();assert [v for v in rejected if v[1].get('id')!=callee]==held;rejected_row=next(v for _,v in rejected if v.get('id')==callee);assert rejected_row['signature']==old and 'bodies'not in rejected_row['mapping'];assert next(iter(rejected_row['bodyDrafts'].values()))['parameters']=='long nativeAmount, out long nativeCount';unchanged();f.page.screenshot(path=str(f.case/'prior-ref-out-rejected.png'));(f.case/'prior-role-editor.json').write_text(json.dumps(dict(headerRegionEditable=True,roleSaveRejected=True,inputRetained=True,originalsRetained=True,error=dialog.locator('[data-code-error]').inner_text()),ensure_ascii=False,indent=2));dialog.locator('[data-code-cancel]').click();assert d.pending()==held;f.checked('intact published scoped editor rejects ref-to-out Save while retaining explicit input and original sources');f.browser.close();raise SystemExit(0)
 dialog.locator('[data-code-cancel]').click();assert d.pending()==held
 field=open_edit();original=sources[callee].replace('\r\n','\n');assert original in field.input_value()
 field.evaluate("el=>{el.focus();el.setSelectionRange(el.value.indexOf('(')+1,el.value.indexOf(')'));}");f.page.keyboard.insert_text('long nativeAmount, out long nativeCount');field.evaluate('(el,text)=>{const i=el.value.indexOf(text);el.setSelectionRange(i,i+text.length);}',original);f.page.keyboard.insert_text(selected[callee]);f.idle();f.page.screenshot(path=str(f.case/'selected-callee-ref-out-source.png'));dialog.locator('[data-code-save]').click();expect(dialog).to_have_count(0)
 remap=f.page.get_by_role('dialog',name='호출 계약 갱신',exact=True);expect(remap).to_be_visible();targets=remap.locator('section[data-abi-target]');assert targets.count()==2
 for target in targets.all():target.locator('[data-abi-input=amount]').select_option('pin:amount');remap.locator('[data-abi-disconnect-target="'+target.get_attribute('data-abi-target')+'"][data-abi-disconnect=count]').select_option('disconnect');target.locator('[data-abi-output=return]').select_option('return')
 f.page.screenshot(path=str(f.case/'two-explicit-input-disconnections.png'));remap.locator('[data-abi-remap-accept]').click();expect(remap).to_have_count(0);f.idle();saved=d.pending();entry=next(value for _,value in saved if value.get('id')==callee);plan=next(iter(entry['mapping']['bodies'].values()));assert plan['beforeSignature']==native_before and plan['signature']==native_after
 field=open_edit();assert re.match(r'public long Invoke\(long nativeAmount, out long nativeCount\)',field.input_value());dialog.locator('[data-code-save]').click();expect(dialog).to_have_count(0);f.idle();assert d.pending()==saved;f.checked('before first owner Save, own Code Save reentry retains the exact native aliases, out role, source and both explicit original input disconnections and return identities')
 for _ in range(2):f.owner().locator('[data-own-functions-toggle]').press('Control+z')
 assert d.pending()==held
 for _ in range(2):f.owner().locator('[data-own-functions-toggle]').press('Control+y')
 assert d.pending()==saved;f.checked('own native editor explicitly changes ref to out and assigns it; both original callers explicitly disconnect both original count bindings and retain amount/return; cancel and Undo/Redo preserve private plan')

def edit_contract(popover,index):pass

# Role and source are two explicit owner history entries.
undo_steps=2

def verify_pins(panel,index):
 from playwright.sync_api import expect
 method=panel.locator('[data-inline-method="'+functions[index]+'"]');expected=['amount']if index==1 else['amount','count']
 assert method.locator('[data-pin-side=inputs] [data-function-pin-name]').evaluate_all('(els)=>els.map(e=>e.dataset.functionPinName)')==expected
 expect(method.locator('[data-pin-side=inputs] [data-function-pin-name=amount]')).to_have_attribute('data-function-pin-type','정수')
 expect(method.locator('[data-pin-side=inputs] [data-function-pin-name=count]')).to_have_count(0 if index==1 else 1)
 expect(method.locator('[data-pin-side=outputs] [data-function-pin-name=count]')).to_have_attribute('data-function-pin-type','정수')
 expect(method.locator('[data-pin-side=outputs] [data-function-pin-name=결과]')).to_have_attribute('data-function-pin-type','정수')
