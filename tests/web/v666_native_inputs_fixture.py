"""Two explicit native value-input replacements compose a direct shared caller."""
import copy,json,sys
_requested=sys.argv[3] if len(sys.argv)>3 else 'normal'
if len(sys.argv)>3:sys.argv[3]='leaf'
import v666_body_imports_fixture as _prior
if len(sys.argv)>3:sys.argv[3]=_requested
for key in dir(_prior):
 if not key.startswith('_'):globals()[key]=getattr(_prior,key)
mode=_requested;nexts=copy.deepcopy(olds)
for sig in nexts:sig['args'][0]['type']='string'
undo_steps=3
texts=['첫째😀','second'];original_result=70;edited_result=21
selected={fn:'return checked(amount.Length'+('' if index==0 else '*2')+'+count); // 명시 새 string 본문 😀\n' for index,fn in enumerate(functions)}
graph=copy.deepcopy(graph);graph['nodes'][1]['arguments']['count']={'node':'invoke'}
(f.project/'caller.graph.json').write_bytes((json.dumps(graph,ensure_ascii=False,indent=2)+'\n').replace('\n','\r\n').encode())
snapshot={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory'not in p.relative_to(f.project).parts}
retained_header='StableBodyHelperBody.celem';retained_file='stable-helper.csbody';retained_graph='caller.graph.json'
def unchanged():assert all((f.project/path).read_bytes()==raw for path,raw in snapshot.items())
def request():
 result=_prior.request()
 for index,row in enumerate(result['changes']):
  row['signature']=copy.deepcopy(nexts[index]);mapping=row['mapping'];mapping['args']={'amount':None,'count':'count'}
  for plan in mapping['bodies'].values():plan.update(signature=copy.deepcopy(nexts[index]),contract=copy.deepcopy(nexts[index]),text=selected[row['id']])
  callers=f.metadata('informationFunctionInputs',**{k:result[k] for k in ['project','manifest','id','units']},function=row['id'])
  mapping['callers']={key:{k:plan[k] for k in ['graph','node','hash']}|{'inputs':{'amount':{'valueJson':json.dumps(texts[index],ensure_ascii=False)},'count':'count'},'disconnect':{'amount':plan['bindings']['amount']}} for key,plan in callers.items()}
 return result

def expected_graph():
 expected=copy.deepcopy(graph)
 for index,node in enumerate(expected['nodes']):node['signature']=copy.deepcopy(nexts[index]);node['arguments']['amount']={'constant':texts[index]}
 return expected

def caller_arguments(index):return copy.deepcopy(expected_graph()['nodes'][index]['arguments'])
def caller_exits():return copy.deepcopy(graph['exits'])

def verify_rows(rows):
 merged={row['id']:{'draft':(f.project/row['path']).read_bytes().decode('utf-8-sig')} for row in f.metadata('describe',project=str(f.manifest))['units']}|rows
 assert json.loads(merged[n.caller+'Body/body:common']['draft'])==expected_graph()
 caller=f.metadata('inspect',text=merged[n.caller+'Body']['draft']);assert n.canonical(caller['signature'])==n.canonical(f.metadata('inspect',text=snapshot['CallerBody.celem'].decode())['signature'])
 for index,fn in enumerate(functions):
  assert n.canonical(f.metadata('inspect',text=merged[fn]['draft'])['signature'])==nexts[index]
  assert n.canonical(f.metadata('inspect',text=merged[fn+'Body']['draft'])['signature'])==nexts[index]
  assert merged[fn+'Body/body:common']['draft']==selected[fn]
def verify(checkpoint):
 rows={row['id']:row for row in json.loads(checkpoint.read_text())['changes']};verify_rows(rows);unchanged();ids=rows[owner]['atomicEditGroup'];assert set(functions+[fn+'Body'for fn in functions]+[fn+'Body/body:common'for fn in functions]+[owner,n.caller+'Body',n.caller+'Body/body:common'])<=set(ids);return ids

def verify_live():
 verify_rows({})
 if 'accepted_description'in globals():assert f.metadata('inspect',text=n.a.info.read_text())['description']==accepted_description
 allowed=set(paths.values())|{'elements/'+fn.split('::')[1]+'.celem'for fn in functions}|{fn.split('::')[1]+'Body.celem'for fn in functions}|{str(n.a.info.relative_to(f.project)),'CallerBody.celem','caller.graph.json'}
 for path,raw in snapshot.items():
  if path not in allowed:assert(f.project/path).read_bytes()==raw,path
 execute(edited_result,'native-input-type-execution');f.checked('actual two native string bodies execute result21 through explicitly replaced caller values; retained count consumes first result and original C# outside selected bodies remains exact')

def edit_contract(popover,index):
 from playwright.sync_api import expect
 popover.locator('[data-signature-id=arg0] [data-signature-type]').click();f.page.get_by_role('dialog',name='속성 타입 선택',exact=True).locator('[data-type=string]').click()
def has_mapping_dialog(index):return False
def after_contract(index):
 from playwright.sync_api import expect
 dialog=f.page.get_by_role('dialog',name='호출 계약 갱신',exact=True);expect(dialog).to_be_visible()
 for target in dialog.locator('section[data-abi-target]').all():target.locator('[data-abi-input=amount]').select_option('value');target.locator('[data-abi-value=amount]').fill(texts[index])
 dialog.locator('[data-abi-disconnect=amount]').select_option('disconnect');dialog.locator('[data-abi-remap-accept]').click();expect(dialog).to_have_count(0);f.idle()
 # Existing C# body editor displays the explicitly selected new native header.
 _prior.after_contract.__globals__['selected']=selected;_prior.after_contract(index)

def verify_pins(panel,index):
 from playwright.sync_api import expect
 method=panel.locator('[data-inline-method="'+functions[index]+'"]');expect(method.locator('[data-pin-side=inputs] [data-function-pin-name=amount]')).to_have_attribute('data-function-pin-type','글자')
