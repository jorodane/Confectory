"""Explicit public input naming and native body edits share an existing caller."""
import copy,hashlib,json,sys
_requested=sys.argv[3]if len(sys.argv)>3 else'normal'
if len(sys.argv)>3:sys.argv[3]='normal'if'--imports-boundary'in sys.argv else'leaf'
import v666_body_imports_fixture as _prior
if len(sys.argv)>3:sys.argv[3]=_requested
for key in dir(_prior):
 if not key.startswith('_'):globals()[key]=getattr(_prior,key)
mode=_requested;nexts=copy.deepcopy(olds);nexts[0]['args'][0]['name']='leftAmount'
changed_source_paths=set(paths.values())
original_result=46 if'--imports-boundary'in sys.argv else 40;edited_result=26 if'--imports-boundary'in sys.argv else 20;retained_file=paths[functions[1]];retained_graph="caller.graph.json"

def request():
 result=_prior.request()
 for index,row in enumerate(result['changes']):
  row['signature']=copy.deepcopy(nexts[index]);row['mapping']['args']={a['name']:b['name']for a,b in zip(olds[index]['args'],nexts[index]['args'])}
  for body in row['mapping']['bodies'].values():body['contract']=copy.deepcopy(nexts[index])
 return result

def unchanged():assert all((f.project/path).read_bytes()==raw for path,raw in snapshot.items())
def caller_arguments(index):return {a['name']:copy.deepcopy(graph['nodes'][index]['arguments'][b['name']])for a,b in zip(nexts[index]['args'],olds[index]['args'])}
def verify_rows(rows):
 merged={row['id']:{'draft':(f.project/row['path']).read_text()}for row in f.metadata('describe',project=str(f.manifest))['units']}|rows
 expected=copy.deepcopy(graph)
 for index,node in enumerate(expected['nodes']):node.update(signature=nexts[index],arguments=caller_arguments(index))
 assert json.loads(merged[n.caller+'Body/body:common']['draft'])==expected
 assert merged[n.caller+'Body']['draft']==snapshot['CallerBody.celem'].decode()
 for index,fn in enumerate(functions):
  assert n.canonical(f.metadata('inspect',text=merged[fn]['draft'])['signature'])==nexts[index]
  assert merged[fn+'Body']['draft']==snapshot[fn.split('::')[1]+'Body.celem'].decode()
  assert merged[fn+'Body/body:common']['draft']==selected[fn]

def verify(checkpoint):
 rows={row['id']:row for row in json.loads(checkpoint.read_text())['changes']};verify_rows(rows);unchanged();group=rows[owner]['atomicEditGroup'];assert set(functions+[fn+'Body/body:common'for fn in functions]+[n.caller+'Body/body:common',owner])<=set(group);return group

def verify_live():
 verify_rows({})
 if 'accepted_description'in globals():assert f.metadata('inspect',text=n.a.info.read_text())['description']==accepted_description
 allowed=changed_source_paths|{'elements/'+fn.split('::')[1]+'.celem'for fn in functions}|{str(n.a.info.relative_to(f.project)),'caller.graph.json'}
 for path,raw in snapshot.items():
  if path not in allowed:assert(f.project/path).read_bytes()==raw,path
 execute(edited_result,'named-body-group-execution');f.checked('actual program20 uses the explicit public rename and two edited bodies; native declarations, other C#, caller edges and IDs remain exact')

def edit_contract(popover,index):
 if index==0:
  field=popover.locator('[data-signature-kind=inputs] [data-signature-id=arg0] [data-signature-name]');field.press('Shift+F10');f.page.locator('.context-menu').get_by_role('button',name='C# 이름 편집',exact=True).click();popover.locator('[data-signature-id=arg0] [data-signature-name]').fill('leftAmount')

def verify_pins(panel,index):
 from playwright.sync_api import expect
 method=panel.locator('[data-inline-method="'+functions[index]+'"]')
 for arg in nexts[index]['args']:expect(method.locator('[data-pin-side=inputs] [data-function-pin-name='+arg['name']+']')).to_have_count(1)
 expect(method.locator('[data-pin-side=outputs] [data-function-pin-name=결과]')).to_have_attribute('data-function-pin-type','정수')
