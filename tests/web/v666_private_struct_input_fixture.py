"""An existing caller struct value is explicitly selected for one native input."""
import copy,hashlib,json,re,subprocess
import v666_private_body_group_fixture as _private
for _key in dir(_private):
 if not _key.startswith('_'):globals()[_key]=getattr(_private,_key)
schema=f.n+'PrivateInputValue';schema_path='PrivateInputValue.celem';assert not(f.project/schema_path).exists()
(f.project/schema_path).write_bytes(('schema '+schema+' {field HP single general long;}\r\n').encode())
f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element PrivateInputValue schema "'+schema_path+'";registry Confectory.Build.DotNet',1))
packet=f.metadata('informationStruct',project=str(f.manifest),id=schema)['clrType']
caller_path=f.project/next(v['path']for v in f.metadata('describe',project=str(f.manifest))['units']if v['id']==n.caller);caller_path.write_text(caller_path.read_text().replace('(long first, long second)','(long first, long second, '+packet+' packet)').replace('(long first,long second)','(long first,long second,'+packet+' packet)'))
caller_header=f.project/retained_header;caller_header.write_text(caller_header.read_text().replace('(long first, long second)','(long first, long second, '+packet+' packet)').replace('(long first,long second)','(long first,long second,'+packet+' packet)'))
initial=f.metadata('blueprintPrepareFeature',id=n.caller,text='function '+n.caller+' (long first,long second,'+packet+' packet) -> long {}',implementation=n.caller+'Body',graphPath=retained_graph,nodePath='unused-initial-caller.node.json')
caller_flow=json.loads((f.project/retained_graph).read_text());caller_flow['contractHash']=initial['graph']['contractHash'];(f.project/retained_graph).write_text(json.dumps(caller_flow,ensure_ascii=False))
(f.project/'MainBody.celem').write_text('implementation '+f.n+'MainBody for '+f.n+'Main () -> int {import '+n.caller+' as SharedCaller (long,long,'+packet+') -> long;body common "Main.csbody";}')
(f.project/'Main.csbody').write_text('var packet=new '+packet+' {HP=25};int result=checked((int)calls.SharedCaller.Invoke(30,5,packet));if(packet.HP!=25)throw new System.Exception("caller value copy lost");System.Console.WriteLine(result);return result;')
nexts=[copy.deepcopy(old),copy.deepcopy(old)];nexts[1]['args'][0]['type']=packet
next_native=copy.deepcopy(native);next_native['args'][0]['type']=packet
selected[functions[1]]='long result=checked(nativeAmount.HP-nativeCount);nativeAmount.HP=999;return result; // 명시 value copy · 😀\n'
snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts}
assert packet in caller_path.read_text() and packet in caller_header.read_text()
def unchanged():
 assert all((f.project/path).read_bytes()==raw for path,raw in snapshot.items())
 assert(f.project/extra_path).stat().st_mtime_ns==extra_mtime
def catalog():
 f.invoke('schema',dict(id=owner));state=f.state()['schema'];return f.invoke('blueprint',dict(action='readOwnerEdits',id=owner,hash=state['textHash'],includeNativeTypes=True,nativeFunction=functions[1],includeFunctionInputs=functions[1],includeFunctionBodies=True))['result']['result']
def request(cat=None):
 cat=cat or catalog();r=_private.request();row=r['changes'][1];choice=next(v for v in cat['nativeTypes']if v['id']==schema);assert choice['available']and choice['clrType']==packet
 row['signature']=copy.deepcopy(nexts[1]);row['nativeTypes']={packet:copy.deepcopy(choice['proof']),'$function:'+functions[1]:copy.deepcopy(cat['nativeFunctionEdit']['proof'])};row['mapping']['args']={'amount':None,'count':'count'}
 for plan in row['mapping']['bodies'].values():plan.update(signature=copy.deepcopy(next_native),contract=copy.deepcopy(nexts[1]),text=selected[functions[1]])
 inputs=cat['functionInputs'];assert len(inputs)==1,inputs
 key,entry=next(iter(inputs.items()));assert any(v['type']==packet and v['source']=={'input':'packet'}for v in entry['sources']),entry
 row['mapping']['callers']={key:{k:copy.deepcopy(entry[k])for k in ['graph','node','hash']}|dict(inputs={'amount':{'binding':{'input':'packet'}},'count':'count'},disconnect={'amount':entry['bindings']['amount']})}
 return r
def prepare(r,ok=True):
 p=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(dict(operation='informationDefinitions',**r)),env=f.env,text=True,capture_output=True,check=True);v=json.loads(p.stdout);assert bool(v['ok'])==ok,v;return v
def verify_rows(rows):
 merged={v['id']:dict(draft=(f.project/v['path']).read_bytes().decode('utf-8-sig'))for v in f.metadata('describe',project=str(f.manifest))['units']}|rows
 assert json.loads(merged[whole_node]['draft'])==json.loads(whole_record)|dict(source=selected[whole_function],helpers=selected_helpers)
 assert merged[whole_graph]['draft']==whole_flow.decode() and merged[whole_implementation]['draft']==whole_header.decode()
 assert(f.project/original_path).read_bytes()==snapshot[original_path]and(f.project/extra_path).read_bytes()==extra_bytes and(f.project/extra_path).stat().st_mtime_ns==extra_mtime
 assert extra_id not in rows;fn=functions[1];assert merged[fn+'Body/body:common']['draft']==selected[fn]
 for index,fn in enumerate(functions):assert n.canonical(f.metadata('inspect',text=merged[fn]['draft'])['signature'])==nexts[index]
 assert n.canonical(f.metadata('inspect',text=merged[functions[1]+'Body']['draft'])['signature'])==next_native
 expected=json.loads(snapshot[retained_graph]);node=next(v for v in expected['nodes']if v.get('feature')==functions[1]);node['signature']=copy.deepcopy(nexts[1]);node['arguments']['amount']={'input':'packet'}
 assert json.loads(merged[n.caller+'Body/body:common']['draft'])==expected
 assert merged[schema]['draft']==snapshot[schema_path].decode()
 verify_caller_header(merged[n.caller+'Body']['draft'])
def verify_caller_header(text):
 pattern=r'(import\s+'+re.escape(functions[1])+r'\s+as\s+\w+\s*)\(([^)]*)\)';matches=list(re.finditer(pattern,text));assert len(matches)==1
 assert re.sub(r'\s+','',matches[0][2])==packet+',long'
 assert re.sub(pattern,lambda m:m[1]+'(<selected input type>)',text)==re.sub(pattern,lambda m:m[1]+'(<selected input type>)',snapshot[retained_header].decode())
def caller_arguments(index):
 value=copy.deepcopy(json.loads(snapshot[retained_graph])['nodes'][index]['arguments'])
 if index==1:value['amount']={'input':'packet'}
 return value
def verify(checkpoint):
 document=json.loads(checkpoint.read_text());rows={v['id']:v for v in document['changes']};verify_rows(rows);unchanged();receipt=rows[owner]['slotSaveReceipt'];assert document['nativeTypeProfile']=='native-type-source-guards-v1'
 assert set(receipt['nativeTypeProofs'])=={packet,'$function:'+functions[1]} and len(receipt['nativeBodyContexts'])==2 and receipt['nativeTypeReads']
 assert {schema_path,graph_path,node_path,retained_graph,retained_header,extra_path}<=set(receipt['readGuards'])
 assert set([owner,*functions,whole_node,functions[1]+'Body/body:common',n.caller+'Body/body:common'])<=set(rows[owner]['atomicEditGroup'])
 assert schema not in rows[owner]['atomicEditGroup'] and extra_id not in rows
 return rows[owner]['atomicEditGroup']
def verify_live():
 verify_rows({});allowed={node_path,paths[functions[1]],str(n.a.info.relative_to(f.project)),retained_header,retained_graph,functions[1].split('::')[1]+'Body.celem',*['elements/'+fn.split('::')[1]+'.celem'for fn in functions]}
 for path,raw in snapshot.items():
  if path not in allowed:assert(f.project/path).read_bytes()==raw,path
 execute(20,'private-struct-input');f.checked('explicit private/helper and existing caller struct input execute20; value-copy mutation leaves caller packet25 and private ABI/native aliases/source ownership intact')
 if 'accepted_description'in globals():assert f.metadata('inspect',text=n.a.info.read_text())['description']==accepted_description
undo_steps=3
def edit_contract(popover,index):
 if index!=1:return
 from playwright.sync_api import expect
 popover.locator('[data-signature-id=arg0] [data-signature-type]').click();picker=f.page.get_by_role('dialog',name='속성 타입 선택',exact=True);expect(picker).to_be_visible();picker.get_by_label('여러 개 허용',exact=True).set_checked(False);picker.locator('[type=search]').fill(schema.split('::')[-1]);picker.locator('[data-native-type]').filter(has_text=schema).click()
def after_contract(index):
 if index==1:
  from playwright.sync_api import expect
  dialog=f.page.get_by_role('dialog',name='호출 계약 갱신',exact=True);expect(dialog).to_be_visible();targets=dialog.locator('section[data-abi-target]');assert targets.count()==1
  select=targets.locator('[data-abi-input=amount]');options=select.locator('option').evaluate_all('(els)=>els.map(e=>({value:e.value,text:e.textContent}))');values=[v['value']for v in options if v['value'].startswith('pin:$source:')and'packet'in v['text']];assert len(values)==1,options;select.select_option(values[0]);dialog.locator('[data-abi-disconnect=amount]').select_option('disconnect');dialog.locator('[data-abi-remap-accept]').click();expect(dialog).to_have_count(0);f.idle()
 _private.after_contract(index)
def verify_pins(panel,index):
 from playwright.sync_api import expect
 method=panel.locator('[data-inline-method="'+functions[index]+'"]')
 for arg in nexts[index]['args']:expect(method.locator('[data-pin-side=inputs] [data-function-pin-name='+arg['name']+']')).to_have_count(1)
