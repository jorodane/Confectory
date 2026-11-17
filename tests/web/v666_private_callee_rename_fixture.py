"""Explicit public pin correspondence on an original selected ordinary callee."""
import copy,hashlib,json
import v666_private_selected_import_fixture as _selected
for key in dir(_selected):
 if not key.startswith('_'):globals()[key]=getattr(_selected,key)
nexts=[copy.deepcopy(old),copy.deepcopy(old)];nexts[1]['args'][0]['name']='receivedAmount';undo_steps=2
def sync():
 _selected.selected_helpers=selected_helpers
 if 'accepted_description'in globals():_selected.accepted_description=accepted_description
 _selected.sync()
def unchanged():sync();_selected.unchanged()
def request():
 sync();r=_selected.request();row=r['changes'][1];row['signature']=copy.deepcopy(nexts[1]);row['mapping']['args']={'amount':'receivedAmount','count':'count'}
 for plan in row['mapping']['bodies'].values():plan['contract']=copy.deepcopy(nexts[1])
 return r
def current_whole(rows):
 r=request();r['units'].update(copy.deepcopy(rows));bodies=f.metadata('informationFunctionBodies',**{k:r[k]for k in ['project','manifest','id','units']},function=whole_function,includeBlueprintTargets=True);return bodies[whole_node]['whole']
def expected_graph(raw):
 result=json.loads(raw)
 for node in result['nodes']:
  if node.get('feature')==callee:node['signature']=copy.deepcopy(nexts[1]);node['arguments']['receivedAmount']=node['arguments'].pop('amount')
 return result
def verify_rows(rows):
 sync();merged={v['id']:dict(draft=(f.project/v['path']).read_bytes().decode('utf-8-sig'))for v in f.metadata('describe',project=str(f.manifest))['units']}|rows
 assert json.loads(merged[whole_node]['draft'])==json.loads(whole_record)|dict(source=selected[whole_function],helpers=selected_helpers)
 assert json.loads(merged[whole_graph]['draft'])==expected_graph(whole_flow);assert merged[whole_implementation]['draft']==whole_header.decode()
 assert(f.project/original_path).read_bytes()==snapshot[original_path]and(f.project/extra_path).read_bytes()==extra_bytes and(f.project/extra_path).stat().st_mtime_ns==extra_mtime
 assert extra_id not in rows;assert merged[callee+'Body/body:common']['draft']==selected[callee];assert merged[callee+'Body']['draft']==snapshot[callee.split('::')[1]+'Body.celem'].decode()
 for index,fn in enumerate(functions):assert n.canonical(f.metadata('inspect',text=merged[fn]['draft'])['signature'])==nexts[index]
 assert json.loads(merged[n.caller+'Body/body:common']['draft'])==expected_graph(snapshot[retained_graph]);assert merged[n.caller+'Body']['draft']==snapshot[retained_header].decode()
def verify(checkpoint):
 document=json.loads(checkpoint.read_text());assert document['version']==1;rows={v['id']:v for v in document['changes']};verify_rows(rows);unchanged();receipt=rows[owner]['slotSaveReceipt'];assert receipt['version']==3 and len(receipt['nativeBodyContexts'])==2
 assert {impl_path,graph_path,paths[callee],callee.split('::')[1]+'Body.celem','elements/'+callee.split('::')[1]+'.celem',retained_header,retained_graph}<=set(receipt['readGuards']);ids=rows[owner]['atomicEditGroup'];assert {owner,*functions,whole_node,whole_graph,callee+'Body/body:common',n.caller+'Body/body:common'}<=set(ids)and extra_id not in ids;return ids
def verify_live():
 verify_rows({});allowed={node_path,graph_path,paths[callee],str(n.a.info.relative_to(f.project)),retained_graph,*['elements/'+fn.split('::')[1]+'.celem'for fn in functions]}
 for path,raw in snapshot.items():
  if path not in allowed:assert(f.project/path).read_bytes()==raw,path
 if 'accepted_description'in globals():assert f.metadata('inspect',text=n.a.info.read_text())['description']==accepted_description
 execute(20,'private-callee-rename');f.checked('actual private call and shared caller retain their exact bindings under one explicit public pin rename and execute20; native/private ABI, fixed import aliases, outputs, coordinates, exact locals and unselected source bytes retained')
def edit_contract(popover,index):
 if index==1:popover.locator('[data-signature-id=arg0] [data-signature-name]').fill('receivedAmount')
def caller_arguments(index):
 return copy.deepcopy(expected_graph(snapshot[retained_graph])['nodes'][index]['arguments'])
def verify_pins(panel,index):
 from playwright.sync_api import expect
 method=panel.locator('[data-inline-method="'+functions[index]+'"]')
 for arg in nexts[index]['args']:expect(method.locator('[data-pin-side=inputs] [data-function-pin-name='+arg['name']+']')).to_have_count(1)
def after_contract(index):sync();return _selected.after_contract(index)

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
