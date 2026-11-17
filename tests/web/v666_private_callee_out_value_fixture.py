"""An original private ordinary callee changes one out to value with two explicit literal/output choices."""
import copy,hashlib,json,re,subprocess
import v666_private_out_value_fixture as _role
for key in dir(_role):
 if not key.startswith('_'):globals()[key]=getattr(_role,key)
callee=functions[1];root_alias='fg_call_'+hashlib.sha256(callee.encode()).hexdigest()[:24];root_call='original-selected-value'
header=f.project/impl_path;header.write_bytes(header.read_bytes().replace(b'{',('{import '+callee+' as '+root_alias+' (long,out long) -> long; // 원래 out 반환 호출 😀\r\n').encode(),1));whole_header=header.read_bytes()
graph=json.loads(whole_flow)
graph['nodes'].append(dict(id=root_call,kind='call',control='next',intent='원래 선택 반환 호출',feature=callee,signature=copy.deepcopy(olds[1]),arguments=dict(amount=dict(node='inner')),x=779,y=127))
edge=next(row for row in graph['edges']if row['from']=='inner');assert edge['to']=='exit:return';edge['to']=root_call;graph['edges'].append(dict(**{'from':root_call},port='next',to='exit:return'));graph['exits']={'return':{'node':root_call,'output':'count'}}
(f.project/graph_path).write_bytes((json.dumps(graph,ensure_ascii=False,indent=2)+'\r\n').encode());whole_flow=(f.project/graph_path).read_bytes()
defs=f.metadata('blueprintDescribeOwned',project=str(f.manifest),id=whole_implementation,text=whole_header.decode(),bodyTarget='common',graph=graph,definitionsOnly=True);assert defs['state']=='node-definitions',defs
for path,key in [(node_path,private_node),(extra_path,'preserve')]:
 record=json.loads((f.project/path).read_bytes());record['definitionHash']=next(row['definitionHash']for row in [*defs.get('nodes',[]),*defs.get('nestedNodes',[])]if row['id']==key);(f.project/path).write_bytes((json.dumps(record,ensure_ascii=False,indent=2)+'\r\n').encode())
whole_record=(f.project/node_path).read_bytes();extra_bytes=(f.project/extra_path).read_bytes();extra_mtime=(f.project/extra_path).stat().st_mtime_ns
p=f.project/'Main.csbody';main=p.read_text().replace('bool changed=result==20;','bool changed=result==15;')
# This original private function now invokes the selected callee itself. Its
# direct result is20, while the selected native callee directly returns25.
private_alias='fg_call_'+hashlib.sha256(functions[0].encode()).hexdigest()[:24]
assert main.count('if(!object.Equals(value,25L)')==1
main=main.replace('foreach(var property in properties){','foreach(var property in properties){if(property.Name!='+json.dumps(private_alias)+'&&property.Name!='+json.dumps(root_alias)+')throw new System.Exception("unexpected original import");')
main=main.replace('if(!object.Equals(value,25L)','if(!object.Equals(value,property.Name=='+json.dumps(root_alias)+'?25L:20L)')
p.write_text(main);original_result=40;edited_result=15
snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts}
def sync():
 for module in [_role,_role._private,_role._private.b,_role._private.b._prior]:
  for name in ['snapshot','whole_header','whole_flow','whole_record','extra_bytes','extra_mtime','selected_helpers']:setattr(module,name,globals()[name])
  if 'accepted_description'in globals():module.accepted_description=accepted_description
sync()
def unchanged():sync();_role.unchanged()
def request():
 sync();r=_role._private.request();row=r['changes'][1];row['signature']=copy.deepcopy(nexts[1]);row['mapping']['before']=copy.deepcopy(olds[1])
 for plan in row['mapping']['bodies'].values():plan.update(beforeSignature=copy.deepcopy(native_before),signature=copy.deepcopy(native_after),contract=copy.deepcopy(nexts[1]),text=selected[callee])
 callers=f.metadata('informationFunctionInputs',**{k:r[k]for k in ['project','manifest','id','units']},function=callee);assert len(callers)==2,callers
 row['mapping']['callers']={key:{k:plan[k]for k in ['graph','node','hash']}|dict(inputs={'amount':'amount','count':{'valueJson':'5'}},disconnect={},outputs={'return':'return','count':'return'})for key,plan in callers.items()};return r
def prepare(r,ok=True):
 p=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(dict(operation='informationDefinitions',**r)),env=f.env,text=True,capture_output=True,check=True);v=json.loads(p.stdout);assert bool(v['ok'])==ok,v;return v
def current_whole(rows):
 r=request();r['units'].update(copy.deepcopy(rows));bodies=f.metadata('informationFunctionBodies',**{k:r[k]for k in ['project','manifest','id','units']},function=whole_function,includeBlueprintTargets=True);return bodies[whole_node]['whole']
def expected_graph(raw):
 result=json.loads(raw)
 for node in result['nodes']:
  if node.get('feature')==callee:node['signature']=copy.deepcopy(nexts[1]);node['arguments']['count']={'constant':5};result['exits']={'return':{'node':node['id']}}
 return result
root_pattern=r'(import\s+'+re.escape(callee)+r'\s+as\s+'+root_alias+r'\s*)\(([^)]*)\)'
pattern=r'(import\s+'+re.escape(callee)+r'\s+as\s+\w+\s*)\(([^)]*)\)'
def verify_header(text,raw,pattern):
 matches=list(re.finditer(pattern,text));assert len(matches)==1 and re.sub(r'\s+','',matches[0][2])=='long,long'
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
 execute(15,'private-callee-out-value');f.checked('actual private and shared callers execute15 through two explicit new literal5 inputs and old-out-to-return choices; direct native long25 with value5 unchanged, other input/return/private ABI, aliases, routes, coordinates, exact locals and unselected source bytes retained')
def caller_arguments(index):return copy.deepcopy(expected_graph(snapshot[retained_graph])['nodes'][index]['arguments'])
def caller_exits():return copy.deepcopy(expected_graph(snapshot[retained_graph])['exits'])
def after_contract(index):
 sync()
 if index==0:return _role._private.after_contract(index)
 from playwright.sync_api import expect
 held=d.pending();dialog=f.page.locator('[role=dialog]:has([data-code-source])');selector='[data-inline-method="'+callee+'"] [data-function-edit], [data-inline-method="'+callee+'"] [data-function-write-direct]'
 def open_edit():
  f.owner().locator(selector).click();choice=f.page.locator('[data-information-body="'+callee+'Body/body:common"]');expect(choice).to_be_visible();choice.click();expect(dialog).to_be_visible();return dialog.locator('[data-code-source]')
 field=open_edit()
 if mode=='reproduce-ui':
  text=field.input_value();assert re.match(r'public long Invoke\(long nativeAmount, out long nativeCount\)',text);assert dialog.locator('[data-code-region=parameters]').count()==0
  field.evaluate("el=>{el.focus();el.setSelectionRange(el.value.indexOf('(')+1,el.value.indexOf(')'));}");f.page.keyboard.insert_text('long nativeAmount, long nativeCount');assert field.input_value()==text and d.pending()==held;unchanged();f.page.screenshot(path=str(f.case/'prior-readonly-native-role.png'));(f.case/'prior-role-editor.json').write_text(json.dumps(dict(protectedHeader=True,roleInputRejected=True,inputRetained=True,originalsRetained=True,header=text.split('\n')[0]),ensure_ascii=False,indent=2));dialog.locator('[data-code-cancel]').click();assert d.pending()==held;f.checked('intact published UI keeps the callee native parameters read-only for an original scoped caller; trusted role edit is rejected without source/input loss');f.browser.close();raise SystemExit(0)
 dialog.locator('[data-code-cancel]').click();assert d.pending()==held
 field=open_edit();original=sources[callee].replace('\r\n','\n');assert original in field.input_value()
 field.evaluate("el=>{el.focus();el.setSelectionRange(el.value.indexOf('(')+1,el.value.indexOf(')'));}");f.page.keyboard.insert_text('long nativeAmount, long nativeCount');field.evaluate('(el,text)=>{const i=el.value.indexOf(text);el.setSelectionRange(i,i+text.length);}',original);f.page.keyboard.insert_text(selected[callee]);f.idle();f.page.screenshot(path=str(f.case/'selected-callee-value-out-source.png'));dialog.locator('[data-code-save]').click();expect(dialog).to_have_count(0)
 remap=f.page.get_by_role('dialog',name='호출 계약 갱신',exact=True);expect(remap).to_be_visible();targets=remap.locator('section[data-abi-target]');assert targets.count()==2
 for target in targets.all():target.locator('[data-abi-input=amount]').select_option('pin:amount');target.locator('[data-abi-input=count]').select_option('value');target.locator('[data-abi-value=count]').fill('5');target.locator('[data-abi-output=count]').select_option('return');target.locator('[data-abi-output=return]').select_option('return')
 f.page.screenshot(path=str(f.case/'two-explicit-input-disconnections.png'));remap.locator('[data-abi-remap-accept]').click();expect(remap).to_have_count(0);f.idle();saved=d.pending();entry=next(value for _,value in saved if value.get('id')==callee);plan=next(iter(entry['mapping']['bodies'].values()));assert plan['beforeSignature']==native_before and plan['signature']==native_after
 field=open_edit();assert re.match(r'public long Invoke\(long nativeAmount, long nativeCount\)',field.input_value());dialog.locator('[data-code-save]').click();expect(dialog).to_have_count(0);f.idle();assert d.pending()==saved;f.checked('before first owner Save, own Code Save reentry retains the exact native aliases, value role, source and both explicit literal/output choices')
 for _ in range(2):f.owner().locator('[data-own-functions-toggle]').press('Control+z')
 assert d.pending()==held
 for _ in range(2):f.owner().locator('[data-own-functions-toggle]').press('Control+y')
 assert d.pending()==saved;f.checked('own native editor explicitly changes out to value and assigns it; both original callers explicitly select literal5 and map the old out to the original return; cancel and Undo/Redo preserve private plan')
