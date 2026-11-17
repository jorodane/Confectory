"""Original ordinary call to the second selected function; both ABIs retained."""
import copy,hashlib,json,subprocess
import v666_private_body_group_fixture as _base
for key in dir(_base):
 if not key.startswith('_'):globals()[key]=getattr(_base,key)

callee=functions[1];root_alias='fg_call_'+hashlib.sha256(callee.encode()).hexdigest()[:24];root_call='original-selected-result'
header=f.project/impl_path;header.write_bytes(header.read_bytes().replace(b'{',('{import '+callee+' as '+root_alias+' (long,long) -> long; // 원래 선택 함수 호출 😀\r\n').encode(),1));whole_header=header.read_bytes()
graph=json.loads(whole_flow)
graph['nodes'].append(dict(id=root_call,kind='call',control='next',intent='원래 선택 함수 호출',feature=callee,signature=copy.deepcopy(old),arguments=dict(amount=dict(node='inner'),count=dict(constant=0)),x=779,y=127))
edge=next(row for row in graph['edges']if row['from']=='inner');assert edge['to']=='exit:return';edge['to']=root_call;graph['edges'].append(dict(**{'from':root_call},port='next',to='exit:return'));graph['exits']={'return':{'node':root_call}}
(f.project/graph_path).write_bytes((json.dumps(graph,ensure_ascii=False,indent=2)+'\r\n').encode());whole_flow=(f.project/graph_path).read_bytes()
defs=f.metadata('blueprintDescribeOwned',project=str(f.manifest),id=whole_implementation,text=whole_header.decode(),bodyTarget='common',graph=graph,definitionsOnly=True);assert defs['state']=='node-definitions',defs
for path,key in [(node_path,private_node),(extra_path,'preserve')]:
 record=json.loads((f.project/path).read_bytes());record['definitionHash']=next(row['definitionHash']for row in [*defs.get('nodes',[]),*defs.get('nestedNodes',[])]if row['id']==key);(f.project/path).write_bytes((json.dumps(record,ensure_ascii=False,indent=2)+'\r\n').encode())
whole_record=(f.project/node_path).read_bytes();extra_bytes=(f.project/extra_path).read_bytes();extra_mtime=(f.project/extra_path).stat().st_mtime_ns
snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts}
def sync():
 for module in [_base,_base.b,_base.b._prior]:
  for name in ['snapshot','whole_header','whole_flow','whole_record','extra_bytes','extra_mtime','selected_helpers']:setattr(module,name,globals()[name])
  if 'accepted_description'in globals():module.accepted_description=accepted_description
sync()
def unchanged():sync();_base.unchanged()
def request():sync();return _base.request()
def prepare(r,ok=True):
 p=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(dict(operation='informationDefinitions',**r)),env=f.env,text=True,capture_output=True,check=True);v=json.loads(p.stdout);assert bool(v['ok'])==ok,v;return v
def verify_rows(rows):
 sync();_base.verify_rows(rows);assert json.loads(rows.get(whole_graph,{}).get('draft',whole_flow.decode()))==graph
def verify(checkpoint):
 sync();ids=_base.verify(checkpoint);doc=json.loads(checkpoint.read_text());receipt=next(row for row in doc['changes']if row['id']==owner)['slotSaveReceipt'];assert receipt['version']==3 and len(receipt['nativeBodyContexts'])==2;assert {impl_path,graph_path,paths[callee],callee.split('::')[1]+'Body.celem','elements/'+callee.split('::')[1]+'.celem'}<=set(receipt['readGuards']);return ids
def verify_live():
 sync();_base.verify_live();verify_rows({})
 if 'accepted_description'in globals():assert f.metadata('inspect',text=n.a.info.read_text())['description']==accepted_description
 f.checked('actual original call invokes the selected callee within the unchanged private graph; both explicit source edits execute20 with original public/native/private ABI, aliases, coordinates, exact locals and bytes outside the selected source group retained')
def after_contract(index):
 sync()
 if index==0:return _base.after_contract(index)
 from playwright.sync_api import expect
 held=d.pending();dialog=f.page.locator('[role=dialog]:has([data-code-source])');selector='[data-inline-method="'+functions[index]+'"] [data-function-edit], [data-inline-method="'+functions[index]+'"] [data-function-write-direct]'
 def open_edit():
  f.owner().locator(selector).click();choice=f.page.locator('[data-information-body="'+callee+'Body/body:common"]');expect(choice).to_be_visible();choice.click();expect(dialog).to_be_visible();field=dialog.locator('[data-code-source]');assert sources[callee]in field.input_value();field.evaluate('(el,text)=>{el.focus();const i=el.value.indexOf(text);el.setSelectionRange(i,i+text.length);}',sources[callee]);f.page.keyboard.insert_text(selected[callee]);f.idle()
 open_edit();dialog.locator('[data-code-cancel]').click();assert d.pending()==held
 open_edit();f.page.screenshot(path=str(f.case/'selected-callee-source.png'));dialog.locator('[data-code-save]').click();expect(dialog).to_have_count(0);f.idle();saved=d.pending();assert saved!=held
 f.owner().locator('[data-own-functions-toggle]').press('Control+z');assert d.pending()==held
 f.owner().locator('[data-own-functions-toggle]').press('Control+y');assert d.pending()==saved;f.checked('existing implementation picker explicitly selects the callee own CSharp body among its caller sources; cancel and Undo/Redo preserve manual input')
 if index!=1 or mode!='reproduce-ui':return
 import time
 from playwright.sync_api import expect
 checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();pending=d.pending();mark=len(f.traffic)
 f.page.evaluate('()=>{globalThis.selectedSaveClicks=[];document.addEventListener("click",e=>{if(e.target.closest("[data-element-action=save]"))selectedSaveClicks.push({trusted:e.isTrusted});},true)}');button=f.owner().locator('[data-element-action=save]');expect(button).to_be_enabled();button.click();deadline=time.monotonic()+60
 while time.monotonic()<deadline:
  ids={v['invoke']['requestId']for v in f.traffic[mark:]if v.get('invoke',{}).get('input',{}).get('action')=='applySlots'};replies=[v['result']for v in f.traffic[mark:]if v.get('result',{}).get('requestId')in ids]
  if replies:assert replies[-1]['ok']is False;break
  f.page.wait_for_timeout(25)
 else:raise AssertionError('Prior selected-callee Save response missing')
 clicks=f.page.evaluate('()=>selectedSaveClicks');assert clicks and all(v['trusted']for v in clicks);assert checkpoint.read_bytes()==before and d.pending()==pending;unchanged();f.page.screenshot(path=str(f.case/'prior-selected-import-save.png'));(f.case/'prior-selected-import-save.json').write_text(json.dumps(dict(replies=replies,clicks=clicks,inputRetained=True,checkpointRetained=True),ensure_ascii=False,indent=2));f.checked('intact published package rejects one trusted selected-callee/private Save while preserving both manual inputs, checkpoint and original source bytes');f.browser.close();raise SystemExit(0)
