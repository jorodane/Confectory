"""One public pin rename beside an explicit private body/helper edit."""
import copy,hashlib,json
import v666_private_body_group_fixture as _private
for _key in dir(_private):
 if not _key.startswith('_'):globals()[_key]=getattr(_private,_key)
nexts=[copy.deepcopy(old),copy.deepcopy(old)];nexts[1]['args'][0]['name']='receivedAmount'
undo_steps=2
def request():
 r=_private.request();row=r['changes'][1];row['signature']=copy.deepcopy(nexts[1]);row['mapping']['args']={'amount':'receivedAmount','count':'count'}
 for plan in row['mapping']['bodies'].values():plan['contract']=copy.deepcopy(nexts[1])
 return r
def unchanged():_private.unchanged()
def verify_rows(rows):
 merged={v['id']:dict(draft=(f.project/v['path']).read_bytes().decode('utf-8-sig'))for v in f.metadata('describe',project=str(f.manifest))['units']}|rows
 assert json.loads(merged[whole_node]['draft'])==json.loads(whole_record)|dict(source=selected[whole_function],helpers=selected_helpers)
 assert merged[whole_graph]['draft']==whole_flow.decode() and merged[whole_implementation]['draft']==whole_header.decode()
 assert(f.project/original_path).read_bytes()==snapshot[original_path]
 assert extra_id not in rows and(f.project/extra_path).read_bytes()==extra_bytes and(f.project/extra_path).stat().st_mtime_ns==extra_mtime
 fn=functions[1];assert merged[fn+'Body/body:common']['draft']==selected[fn]
 assert merged[fn+'Body']['draft']==snapshot[fn.split('::')[1]+'Body.celem'].decode()
 for index,fn in enumerate(functions):assert n.canonical(f.metadata('inspect',text=merged[fn]['draft'])['signature'])==nexts[index]
 prior=json.loads(snapshot[retained_graph]);expected=copy.deepcopy(prior)
 for node in expected['nodes']:
  if node.get('feature')==functions[1]:node['signature']=copy.deepcopy(nexts[1]);node['arguments']['receivedAmount']=node['arguments'].pop('amount')
 assert json.loads(merged[n.caller+'Body/body:common']['draft'])==expected
 assert merged[n.caller+'Body']['draft']==snapshot[retained_header].decode()
def verify(checkpoint):
 rows={v['id']:v for v in json.loads(checkpoint.read_text())['changes']};verify_rows(rows);unchanged();ids=rows[owner]['atomicEditGroup']
 assert set([owner,*functions,whole_node,functions[1]+'Body/body:common',n.caller+'Body/body:common'])<=set(ids) and extra_id not in ids
 return ids
def verify_live():
 verify_rows({});allowed={node_path,paths[functions[1]],str(n.a.info.relative_to(f.project)),retained_header,retained_graph,*['elements/'+fn.split('::')[1]+'.celem'for fn in functions]}
 for path,raw in snapshot.items():
  if path not in allowed:assert(f.project/path).read_bytes()==raw,path
 execute(edited_result,'private-pin-rename');f.checked('explicit private/helper edit and public pin rename execute20; native aliases, frame ABI, exact caller bindings, independent graph/code/local bytes and permissions retained')
def edit_contract(popover,index):
 if index==1:popover.locator('[data-signature-id=arg0] [data-signature-name]').fill('receivedAmount')
def caller_arguments(index):
 result=copy.deepcopy(json.loads(snapshot[retained_graph])['nodes'][index]['arguments'])
 if index==1:result['receivedAmount']=result.pop('amount')
 return result
def validate_history():
 held=d.pending();a=next(row for row in held if row[1]['id']==functions[0]);trace=[held]
 f.owner().locator('[data-own-functions-toggle]').press('Control+z');renamed=d.pending();trace.append(renamed)
 assert len(renamed)==2 and next(row for row in renamed if row[1]['id']==functions[0])==a
 native=next(value for _,value in renamed if value['id']==functions[1]);assert native['signature']==nexts[1] and not native.get('mapping',{}).get('bodies') and not native.get('bodyDrafts')
 f.owner().locator('[data-own-functions-toggle]').press('Control+z');trace.append(d.pending());assert d.pending()==[a]
 f.owner().locator('[data-own-functions-toggle]').press('Control+y');trace.append(d.pending());assert d.pending()==renamed
 f.owner().locator('[data-own-functions-toggle]').press('Control+y');trace.append(d.pending());assert d.pending()==held
 (f.case/'shared-function-undo-trace.json').write_text(json.dumps(trace,ensure_ascii=False,indent=2))
 f.checked('source Undo retains the independent public rename; second Undo removes that rename only; two Redos restore both exact plans')
def verify_pins(panel,index):
 from playwright.sync_api import expect
 method=panel.locator('[data-inline-method="'+functions[index]+'"]')
 for arg in nexts[index]['args']:expect(method.locator('[data-pin-side=inputs] [data-function-pin-name='+arg['name']+']')).to_have_count(1)
def after_contract(index):_private.after_contract(index)
