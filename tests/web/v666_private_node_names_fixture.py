"""Explicit own private-code parameter name, unchanged enclosing frames and public ABI."""
import copy,json,hashlib,subprocess
import v666_private_body_group_fixture as _base
for key in dir(_base):
 if not key.startswith('_'):globals()[key]=getattr(_base,key)
renamed=copy.deepcopy(code_signature);renamed['args'][0]['name']='deltaNative'
selected[whole_function]='return Edit(deltaNative-secondNative); // 명시 노드 인자명과 본문 😀\n'
def sync():
 for module in [_base,_base.b,_base.b._prior]:
  module.selected=selected;module.selected_helpers=selected_helpers
  if 'accepted_description'in globals():module.accepted_description=accepted_description
def unchanged():_base.unchanged()
def request():
 sync();r=_base.request();next(iter(r['changes'][0]['mapping']['bodies'].values()))['signature']=copy.deepcopy(renamed);return r
def prepare(r,ok=True):
 p=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(dict(operation='informationDefinitions',**r)),env=f.env,text=True,capture_output=True,check=True);v=json.loads(p.stdout);assert bool(v['ok'])==ok,v;return v
def expected_graph():
 g=json.loads(whole_flow);node=g['nodes'][1]['graph']['nodes'][0];node['signature']=copy.deepcopy(renamed);node['arguments']={'deltaNative':node['arguments']['firstNative'],'secondNative':node['arguments']['secondNative']};return g
def verify_rows(rows):
 sync();merged={v['id']:dict(draft=(f.project/v['path']).read_bytes().decode('utf-8-sig'))for v in f.metadata('describe',project=str(f.manifest))['units']}|rows
 assert json.loads(merged[whole_graph]['draft'])==expected_graph()
 record=json.loads(merged[whole_node]['draft']);original=json.loads(whole_record);assert record['definitionHash']!=original['definitionHash'];assert record==original|dict(source=selected[whole_function],helpers=selected_helpers,definitionHash=record['definitionHash'])
 assert merged[whole_implementation]['draft']==whole_header.decode();assert merged[functions[1]+'Body/body:common']['draft']==selected[functions[1]]
 assert merged[n.caller+'Body/body:common']['draft']==snapshot[retained_graph].decode();assert merged[n.caller+'Body']['draft']==snapshot[retained_header].decode()
 for fn in functions:assert n.canonical(f.metadata('inspect',text=merged[fn]['draft'])['signature'])==old
 assert extra_id not in rows and(f.project/extra_path).read_bytes()==extra_bytes and(f.project/extra_path).stat().st_mtime_ns==extra_mtime
def verify(checkpoint):
 document=json.loads(checkpoint.read_text());assert document['version']==1;rows={v['id']:v for v in document['changes']};verify_rows(rows);unchanged();receipt=rows[owner]['slotSaveReceipt'];assert receipt['version']==3 and len(receipt['nativeBodyContexts'])==2
 assert {graph_path,node_path,extra_path,retained_graph,retained_header}<=set(receipt['readGuards']);ids=rows[owner]['atomicEditGroup'];assert {owner,*functions,whole_node,whole_graph,functions[1]+'Body/body:common'}<=set(ids)and extra_id not in ids;return ids
def verify_live():
 verify_rows({});allowed={node_path,graph_path,paths[functions[1]],str(n.a.info.relative_to(f.project)),*['elements/'+fn.split('::')[1]+'.celem'for fn in functions]}
 for path,raw in snapshot.items():
  if path not in allowed:assert(f.project/path).read_bytes()==raw,path
 if 'accepted_description'in globals():assert f.metadata('inspect',text=n.a.info.read_text())['description']==accepted_description
 execute(20,'private-node-names');f.checked('actual own private-code name/body/helper and native body execute20; original40, parent/public/native ABIs, frame bindings, exact locals, authored layout and independent source bytes+mtime retained')
def current_whole(rows):
 r=_base.request();r['units'].update(copy.deepcopy(rows));bodies=f.metadata('informationFunctionBodies',**{k:r[k]for k in ['project','manifest','id','units']},function=whole_function,includeBlueprintTargets=True);return bodies[whole_node]['whole']
def after_contract(index):
 sync()
 if index==1:return _base.after_contract(index)
 from playwright.sync_api import expect
 held=d.pending();dialog=f.page.locator('[role=dialog]:has([data-code-source])');selector='[data-inline-method="'+whole_function+'"] [data-function-edit], [data-inline-method="'+whole_function+'"] [data-function-write-direct]'
 def open_edit():
  f.owner().locator(selector).click();expect(f.page.locator('[role=dialog]:has([data-code-source]), [role=dialog]:has([data-information-body])')).to_be_visible();choice=f.page.locator('[data-information-body="'+whole_node+'"]')
  if choice.count():choice.click()
  expect(dialog).to_be_visible();return dialog.locator('[data-code-source]')
 field=open_edit()
 if mode=='reproduce-ui':
  assert dialog.locator('[data-code-region=parameters]').count()==0
  before=field.input_value();field.evaluate("el=>{el.focus();const i=el.value.indexOf('firstNative');el.setSelectionRange(i,i+11);}");f.page.keyboard.insert_text('deltaNative');assert field.input_value()==before;assert d.pending()==held;unchanged();f.page.screenshot(path=str(f.case/'prior-node-parameters-readonly.png'));f.checked('intact published private-node editor protects the signature header and cannot select an own parameter name; original input/bytes retained');dialog.locator('[data-code-cancel]').click();f.browser.close();raise SystemExit(0)
 expect(dialog.locator('[data-code-region=parameters]')).to_have_count(1);dialog.locator('[data-code-cancel]').click();assert d.pending()==held
 field=open_edit()
 def replace(old_text,new_text):
  field.evaluate('(el,text)=>{el.focus();const i=el.value.indexOf(text);if(i<0)throw Error("Expected original text absent");el.setSelectionRange(i,i+text.length);}',old_text);f.page.keyboard.insert_text(new_text)
 replace('long firstNative, long secondNative','long deltaNative, long secondNative');replace(sources[whole_function],selected[whole_function]);replace(original_helpers,selected_helpers);f.idle();f.page.screenshot(path=str(f.case/'private-node-parameter-name.png'));dialog.locator('[data-code-save]').click();expect(dialog).to_have_count(0);f.idle();saved=d.pending();assert saved!=held
 plan=next(iter(next(row for _,row in saved if row.get('id')==whole_function)['mapping']['bodies'].values()));assert plan['signature']==renamed and plan['beforeSignature']==code_signature and plan['contract']==old and plan['helpers']==selected_helpers
 f.owner().locator('[data-own-functions-toggle]').press('Control+z');assert d.pending()==held;f.owner().locator('[data-own-functions-toggle]').press('Control+y');assert d.pending()==saved;f.checked('original C# editor explicitly selects own parameter name and source/helpers, preserves public contract and supports Cancel/Undo/Redo')
