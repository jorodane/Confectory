"""An original private ordinary callee changes return with explicit old-out choices."""
import copy,hashlib,json,re,subprocess
import v666_private_return_alias_fixture as _scalar
for key in dir(_scalar):
 if not key.startswith('_'):globals()[key]=getattr(_scalar,key)
callee=functions[1];root_alias='fg_call_'+hashlib.sha256(callee.encode()).hexdigest()[:24];root_call='original-selected-return'
header=f.project/impl_path;header.write_bytes(header.read_bytes().replace(b'{',('{import '+callee+' as '+root_alias+' (long,out long) -> long; // 원래 반환·out 호출 😀\r\n').encode(),1));whole_header=header.read_bytes()
graph=json.loads(whole_flow)
graph['nodes'].append(dict(id=root_call,kind='call',control='next',intent='원래 선택 반환 호출',feature=callee,signature=copy.deepcopy(olds[1]),arguments=dict(amount=dict(node='inner')),x=779,y=127))
edge=next(row for row in graph['edges']if row['from']=='inner');assert edge['to']=='exit:return';edge['to']=root_call;graph['edges'].append(dict(**{'from':root_call},port='next',to='exit:return'));graph['exits']={'return':{'node':root_call}}
(f.project/graph_path).write_bytes((json.dumps(graph,ensure_ascii=False,indent=2)+'\r\n').encode());whole_flow=(f.project/graph_path).read_bytes()
defs=f.metadata('blueprintDescribeOwned',project=str(f.manifest),id=whole_implementation,text=whole_header.decode(),bodyTarget='common',graph=graph,definitionsOnly=True);assert defs['state']=='node-definitions',defs
for path,key in [(node_path,private_node),(extra_path,'preserve')]:
 record=json.loads((f.project/path).read_bytes());record['definitionHash']=next(row['definitionHash']for row in [*defs.get('nodes',[]),*defs.get('nestedNodes',[])]if row['id']==key);(f.project/path).write_bytes((json.dumps(record,ensure_ascii=False,indent=2)+'\r\n').encode())
whole_record=(f.project/node_path).read_bytes();extra_bytes=(f.project/extra_path).read_bytes();extra_mtime=(f.project/extra_path).stat().st_mtime_ns
p=f.project/'Main.csbody';p.write_text(p.read_text().replace('bool changed=result==20;','bool changed=result==15;'));original_result=45;edited_result=15
snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts}
def sync():
 for module in [_scalar,_scalar._private,_scalar._private.b,_scalar._private.b._prior]:
  for name in ['snapshot','whole_header','whole_flow','whole_record','extra_bytes','extra_mtime','selected_helpers']:setattr(module,name,globals()[name])
  if 'accepted_description'in globals():module.accepted_description=accepted_description
sync()
def unchanged():sync();_scalar.unchanged()
def request():
 sync();r=_scalar._private.request();row=r['changes'][1];row['signature']=copy.deepcopy(nexts[1]);row['mapping']['before']=copy.deepcopy(olds[1])
 for plan in row['mapping']['bodies'].values():plan.update(beforeSignature=copy.deepcopy(native_before),signature=copy.deepcopy(native_after),contract=copy.deepcopy(nexts[1]),text=selected[callee])
 callers=f.metadata('informationFunctionInputs',**{k:r[k]for k in ['project','manifest','id','units']},function=callee);assert len(callers)==2,callers
 row['mapping']['callers']={key:{k:plan[k]for k in ['graph','node','hash']}|dict(inputs={'amount':'amount'},disconnect={},outputs={'return':'count','count':'count'})for key,plan in callers.items()};return r
def prepare(r,ok=True):
 p=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(dict(operation='informationDefinitions',**r)),env=f.env,text=True,capture_output=True,check=True);v=json.loads(p.stdout);assert bool(v['ok'])==ok,v;return v
def current_whole(rows):
 r=request();r['units'].update(copy.deepcopy(rows));bodies=f.metadata('informationFunctionBodies',**{k:r[k]for k in ['project','manifest','id','units']},function=whole_function,includeBlueprintTargets=True);return bodies[whole_node]['whole']
def expected_graph(raw):
 result=json.loads(raw)
 for node in result['nodes']:
  if node.get('feature')==callee:node['signature']=copy.deepcopy(nexts[1]);result['exits']={'return':{'node':node['id'],'output':'count'}}
 return result
root_pattern=r'(import\s+'+re.escape(callee)+r'\s+as\s+'+root_alias+r'\s*\([^)]*\)\s*->\s*)(long)'
def verify_rows(rows):
 sync();merged={v['id']:dict(draft=(f.project/v['path']).read_bytes().decode('utf-8-sig'))for v in f.metadata('describe',project=str(f.manifest))['units']}|rows
 assert json.loads(merged[whole_node]['draft'])==json.loads(whole_record)|dict(source=selected[whole_function],helpers=selected_helpers)
 assert json.loads(merged[whole_graph]['draft'])==expected_graph(whole_flow);assert merged[whole_implementation]['draft']==re.sub(root_pattern,lambda m:m[1]+'double',whole_header.decode())
 assert(f.project/original_path).read_bytes()==snapshot[original_path]and(f.project/extra_path).read_bytes()==extra_bytes and(f.project/extra_path).stat().st_mtime_ns==extra_mtime;assert extra_id not in rows
 assert merged[callee+'Body/body:common']['draft']==selected[callee]
 assert n.canonical(f.metadata('inspect',text=merged[callee+'Body']['draft'])['signature'])==native_after
 for index,fn in enumerate(functions):assert n.canonical(f.metadata('inspect',text=merged[fn]['draft'])['signature'])==nexts[index]
 assert json.loads(merged[n.caller+'Body/body:common']['draft'])==expected_graph(snapshot[retained_graph])
 matches=list(re.finditer(pattern,merged[n.caller+'Body']['draft']));assert len(matches)==1 and re.sub(r'\s+','',matches[0][2])=='long,outlong'and matches[0][4]=='double'
 assert re.sub(pattern,lambda m:m[1]+'('+re.sub(r'\s+','',m[2])+')'+m[3]+'<explicit return>',merged[n.caller+'Body']['draft'])==re.sub(pattern,lambda m:m[1]+'('+re.sub(r'\s+','',m[2])+')'+m[3]+'<explicit return>',snapshot[retained_header].decode())
def verify(checkpoint):
 document=json.loads(checkpoint.read_text());assert document['version']==1;rows={v['id']:v for v in document['changes']};verify_rows(rows);unchanged();receipt=rows[owner]['slotSaveReceipt'];assert receipt['version']==3 and len(receipt['nativeBodyContexts'])==2
 assert {impl_path,graph_path,paths[callee],callee.split('::')[1]+'Body.celem','elements/'+callee.split('::')[1]+'.celem',retained_header,retained_graph}<=set(receipt['readGuards']);ids=rows[owner]['atomicEditGroup'];assert {owner,*functions,whole_node,whole_graph,whole_implementation,callee+'Body',callee+'Body/body:common',n.caller+'Body',n.caller+'Body/body:common'}<=set(ids)and extra_id not in ids;return ids
def verify_live():
 verify_rows({});allowed={node_path,graph_path,impl_path,paths[callee],str(n.a.info.relative_to(f.project)),retained_graph,retained_header,callee.split('::')[1]+'Body.celem',*['elements/'+fn.split('::')[1]+'.celem'for fn in functions]}
 for path,raw in snapshot.items():
  if path not in allowed:assert(f.project/path).read_bytes()==raw,path
 if 'accepted_description'in globals():assert f.metadata('inspect',text=n.a.info.read_text())['description']==accepted_description
 execute(15,'private-callee-return');f.checked('actual private and shared callers execute15 through two explicit old-return-to-original-out choices; direct native double25.5/out25, input/private ABI, aliases, routes, coordinates, exact locals and unselected source bytes retained')
def caller_arguments(index):return copy.deepcopy(expected_graph(snapshot[retained_graph])['nodes'][index]['arguments'])
def caller_exits():return copy.deepcopy(expected_graph(snapshot[retained_graph])['exits'])
def after_contract(index):
 sync()
 if index==0:return _scalar._private.after_contract(index)
 from playwright.sync_api import expect
 remap=f.page.get_by_role('dialog',name='호출 계약 갱신',exact=True);expect(remap).to_be_visible();targets=remap.locator('section[data-abi-target]');assert targets.count()==2
 for target in targets.all():target.locator('[data-abi-input=amount]').select_option('pin:amount');target.locator('[data-abi-output=count]').select_option('count');target.locator('[data-abi-output=return]').select_option('count')
 f.page.screenshot(path=str(f.case/'two-explicit-return-choices.png'));remap.locator('[data-abi-remap-accept]').click();expect(remap).to_have_count(0);f.idle()
 original=sources[callee].replace('\r\n','\n');held=d.pending();dialog=f.page.locator('[role=dialog]:has([data-code-source])');selector='[data-inline-method="'+callee+'"] [data-function-edit], [data-inline-method="'+callee+'"] [data-function-write-direct]'
 def open_edit():
  f.owner().locator(selector).click();choice=f.page.locator('[data-information-body="'+callee+'Body/body:common"]');expect(choice).to_be_visible();choice.click();expect(dialog).to_be_visible();field=dialog.locator('[data-code-source]');assert original in field.input_value();header=re.match(r'public double Invoke\(([^)]*)\)',field.input_value());assert header,field.input_value()[:300];assert re.sub(r'\s+','',header[1])==('longamount,outlongcount'if mode=='reproduce-ui'else'longnativeAmount,outlongnativeCount'),header[1];field.evaluate('(el,text)=>{el.focus();const i=el.value.indexOf(text);el.setSelectionRange(i,i+text.length);}',original);f.page.keyboard.insert_text(selected[callee]);f.idle()
 open_edit();dialog.locator('[data-code-cancel]').click();assert d.pending()==held
 open_edit();f.page.screenshot(path=str(f.case/'selected-callee-return-source.png'));dialog.locator('[data-code-save]').click();expect(dialog).to_have_count(0);f.idle();saved=d.pending();assert saved!=held;entry=next(value for _,value in saved if value.get('id')==callee);plan=next(iter(entry['mapping']['bodies'].values()));assert plan['beforeSignature']==native_before;assert (plan['signature']!=native_after if mode=='reproduce-ui'else plan['signature']==native_after)
 f.owner().locator('[data-own-functions-toggle]').press('Control+z');assert d.pending()==held
 f.owner().locator('[data-own-functions-toggle]').press('Control+y');assert d.pending()==saved;f.checked('two explicit original return/out choices, own source selection, cancel and Undo/Redo; '+('prior legacy public-header alias fallback reproduced'if mode=='reproduce-ui'else'original native aliases retained'))
 if mode!='reproduce-ui':return
 import time
 checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();pending=d.pending();mark=len(f.traffic)
 f.page.evaluate('()=>{globalThis.returnSaveClicks=[];document.addEventListener("click",e=>{if(e.target.closest("[data-element-action=save]"))returnSaveClicks.push({trusted:e.isTrusted});},true)}');button=f.owner().locator('[data-element-action=save]');expect(button).to_be_enabled();button.click();deadline=time.monotonic()+60
 while time.monotonic()<deadline:
  ids={v['invoke']['requestId']for v in f.traffic[mark:]if v.get('invoke',{}).get('input',{}).get('action')=='applySlots'};replies=[v['result']for v in f.traffic[mark:]if v.get('result',{}).get('requestId')in ids]
  if replies:assert replies[-1]['ok']is False;break
  f.page.wait_for_timeout(25)
 else:raise AssertionError('Prior callee return Save response missing')
 clicks=f.page.evaluate('()=>returnSaveClicks');assert clicks and all(v['trusted']for v in clicks);assert checkpoint.read_bytes()==before and d.pending()==pending;unchanged();f.page.screenshot(path=str(f.case/'prior-callee-return-save.png'));(f.case/'prior-selected-import-save.json').write_text(json.dumps(dict(replies=replies,clicks=clicks,inputRetained=True,checkpointRetained=True,legacyPublicHeader=True,selectedSignature=plan['signature'],expectedNativeSignature=native_after),ensure_ascii=False,indent=2));f.checked('intact published package rejects one trusted callee return/private Save while preserving both sources, explicit return choices, checkpoint and originals');f.browser.close();raise SystemExit(0)
