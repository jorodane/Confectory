"""Explicit private parameter order with the original simple bindings retained by name."""
import copy,json,hashlib,subprocess
import v666_private_body_group_fixture as _base
for key in dir(_base):
 if not key.startswith('_'):globals()[key]=getattr(_base,key)
selected_signature=copy.deepcopy(code_signature);selected_signature['args'].reverse()
selected[whole_function]='return Edit(firstNative-secondNative); // 직접 선택한 인자 순서와 본문 😀\n'
selected_helpers='static long Edit(long value){return checked(value);} // 직접 작성한 보조 함수 · 😀\n'
graph=json.loads(whole_flow);graph['nodes'][1]['graph']['nodes'][0]['arguments']['secondNative']={'constant':5}
if mode=='typed-literal-original':graph['nodes'][1]['graph']['nodes'][0]['arguments']['secondNative']={'constant':5,'type':'long'}
if mode=='local-original':graph['nodes'][1]['graph']['nodes'][0]['arguments']['secondNative']={'local':'inner_exact'}
if mode=='wide-original':graph['nodes'][1]['graph']['nodes'][0]['arguments']['secondNative']={'constant':9007199254740993}
main='long value=calls.SharedCaller.Invoke(30,5);string? observed=null;\nforeach(var type in global::System.Reflection.Assembly.GetExecutingAssembly().GetTypes())foreach(var method in type.GetMethods(global::System.Reflection.BindingFlags.Public|global::System.Reflection.BindingFlags.NonPublic|global::System.Reflection.BindingFlags.Static|global::System.Reflection.BindingFlags.Instance|global::System.Reflection.BindingFlags.DeclaredOnly)){\n var parameters=method.GetParameters();if(parameters.Length!=2||!global::System.Linq.Enumerable.Any(parameters,p=>p.Name=="firstNative")||!global::System.Linq.Enumerable.Any(parameters,p=>p.Name=="secondNative"))continue;\n if(parameters[0].ParameterType!=typeof(long)||parameters[1].ParameterType!=typeof(long)||method.ReturnType!=typeof(long))throw new System.Exception("actual private types");string order=parameters[0].Name+","+parameters[1].Name;if(observed!=null&&observed!=order)throw new System.Exception("private orders differ");observed=order;}\nif(observed==null)throw new System.Exception("private method metadata missing");global::System.Console.Error.WriteLine("private-order:"+observed);global::System.Console.WriteLine(value);return checked((int)value);'
if mode in ['wide-original','local-original']:
 exact=9007199254740993 if mode=='wide-original'else 9223372036854775806
 main=main.replace('calls.SharedCaller.Invoke(30,5)','calls.SharedCaller.Invoke(0,0)').replace('global::System.Console.WriteLine(value);return checked((int)value);','if(value!='+str(exact)+'L)throw new System.Exception("original exact value");global::System.Console.WriteLine(0);return 0;')
if mode=='preserved-source':selected[whole_function]=sources[whole_function];selected_helpers=original_helpers;selected[functions[1]]=sources[functions[1]]
(f.project/'Main.csbody').write_text(main)
(f.project/graph_path).write_bytes((json.dumps(graph,ensure_ascii=False,indent=2)+'\r\n').encode());whole_flow=(f.project/graph_path).read_bytes()
defs=f.metadata('blueprintDescribeOwned',project=str(f.manifest),id=whole_implementation,text=whole_header.decode(),bodyTarget='common',graph=graph,definitionsOnly=True);assert defs['state']=='node-definitions',defs
for path,key in [(node_path,private_node),(extra_path,'preserve')]:
 record=json.loads((f.project/path).read_bytes());record['definitionHash']=next(v['definitionHash']for v in [*defs['nodes'],*defs.get('nestedNodes',[])]if v['id']==key);(f.project/path).write_bytes((json.dumps(record,ensure_ascii=False,indent=2)+'\r\n').encode())
whole_record=(f.project/node_path).read_bytes();extra_bytes=(f.project/extra_path).read_bytes();extra_mtime=(f.project/extra_path).stat().st_mtime_ns
snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts}
for module in [_base,_base.b,_base.b._prior]:
 for name in ['whole_flow','whole_record','extra_bytes','extra_mtime','snapshot']:setattr(module,name,globals()[name])

def sync():
 for module in [_base,_base.b,_base.b._prior]:
  module.selected=selected;module.selected_helpers=selected_helpers
  if 'accepted_description'in globals():module.accepted_description=accepted_description
def unchanged():_base.unchanged()
def request():
 sync();r=_base.request();next(iter(r['changes'][0]['mapping']['bodies'].values()))['signature']=copy.deepcopy(selected_signature);return r
def prepare(r,ok=True):
 p=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(dict(operation='informationDefinitions',**r)),env=f.env,text=True,capture_output=True,check=True);v=json.loads(p.stdout);assert bool(v['ok'])==ok,v;return v
def expected_graph():
 g=json.loads(whole_flow);node=g['nodes'][1]['graph']['nodes'][0];node['signature']=copy.deepcopy(selected_signature);return g
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
 execute(40 if mode=='preserved-source'else 20,'private-node-order',ordered=True);f.checked('actual private order secondNative,firstNative retains name-bound values, parent/public/native ABIs, frame bindings, exact locals, authored layout and independent source bytes+mtime; unchanged bodies execute40, separately manually edited bodies execute20')
def execute(expected,name,ordered=None):
 build=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),'build',str(f.manifest),'portable'],env=f.env,text=True,capture_output=True);(f.case/(name+'-build.log')).write_text(build.stdout+build.stderr);assert build.returncode==0,build.stdout[-2000:]+build.stderr[-2000:]
 out=subprocess.run(json.loads(build.stdout)['run'],env=f.env,text=True,capture_output=True);(f.case/(name+'-run.json')).write_text(json.dumps(dict(exit=out.returncode,stdout=out.stdout,stderr=out.stderr)));swapped=expected==20 if ordered is None else ordered;marker='private-order:'+('secondNative,firstNative'if swapped else'firstNative,secondNative');assert(out.returncode,out.stdout.strip(),out.stderr.strip())==(expected,str(expected),marker),(out.returncode,out.stdout,out.stderr)
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
  expect(dialog.locator('[data-code-region=parameters]')).to_have_count(1);field.evaluate("el=>{el.focus();el.setSelectionRange(el.value.indexOf('(')+1,el.value.indexOf(')'));}");f.page.keyboard.insert_text('long secondNative, long firstNative');dialog.locator('[data-code-save]').click();expect(dialog.locator('[data-code-error]')).to_be_visible();assert field.input_value().startswith('public long Invoke(long secondNative, long firstNative)')
  unchanged();f.page.screenshot(path=str(f.case/'prior-node-order-rejected.png'));(f.case/'prior-order-editor.json').write_text(json.dumps(dict(orderRejected=True,inputRetained=True,originalsRetained=True,error=dialog.locator('[data-code-error]').inner_text()),ensure_ascii=False,indent=2));f.checked('intact published editor rejects own parameter order while retaining explicit declaration and originals');dialog.locator('[data-code-cancel]').click();assert d.pending()==held;f.browser.close();raise SystemExit(0)
 expect(dialog.locator('[data-code-region=parameters]')).to_have_count(1);dialog.locator('[data-code-cancel]').click();assert d.pending()==held
 field=open_edit()
 def replace(old_text,new_text):
  field.evaluate('(el,text)=>{el.focus();const i=el.value.indexOf(text);if(i<0)throw Error("Expected original text absent");el.setSelectionRange(i,i+text.length);}',old_text);f.page.keyboard.insert_text(new_text)
 replace('long firstNative, long secondNative','long secondNative, long firstNative');replace(sources[whole_function],selected[whole_function]);replace(original_helpers,selected_helpers);f.idle();f.page.screenshot(path=str(f.case/'private-node-parameter-order.png'));dialog.locator('[data-code-save]').click();expect(dialog).to_have_count(0);f.idle();saved=d.pending();assert saved!=held
 plan=next(iter(next(row for _,row in saved if row.get('id')==whole_function)['mapping']['bodies'].values()));assert plan['signature']==selected_signature and plan['beforeSignature']==code_signature and plan['contract']==old and plan['helpers']==selected_helpers
 f.owner().locator('[data-own-functions-toggle]').press('Control+z');assert d.pending()==held;f.owner().locator('[data-own-functions-toggle]').press('Control+y');assert d.pending()==saved;f.checked('original C# editor explicitly selects own parameter order and source/helpers, preserves public contract and supports Cancel/Undo/Redo')
