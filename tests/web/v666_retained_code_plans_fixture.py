"""Every retained-context and independent-root source plan is explicitly selected."""
import copy,json,hashlib
import v666_whole_bodies_fixture as _base
for _key in dir(_base):
 if not _key.startswith('_'):globals()[_key]=getattr(_base,_key)
b=_base
code_path='paired-root.node.json';code_node=whole_graph+'/node:adjust';code_signature={'args':[{'name':'value','type':'long'},{'name':'sentinel','type':'long'},{'name':'total','type':'long','mode':'out'}],'return':'void'}
code_source='if(sentinel!=9223372036854775806L)throw new System.InvalidOperationException("exact local");total=Keep(value); // 독립 원문 😀\n'
code_selected='if(sentinel!=9223372036854775806L)throw new System.InvalidOperationException("exact local");total=Edit(value); // 명시 독립 편집 😀\n'
original_helpers='static long Keep(long value){return checked(value+1);} // 기존 helpers\n';selected_helpers='static long Edit(long value){return checked(value+2);} // 직접 편집 helpers\n'
graph=json.loads(whole_flow);graph['profile']='sync-acyclic-methods-v1';context=next(v for v in graph['nodes']if v.get('implementationContext')is not None);writer=next(v for v in graph['nodes']if v['kind']=='export')
code=dict(id='adjust',kind='code',control='next',intent='함께 명시 편집하는 독립 코드',signature=copy.deepcopy(code_signature),arguments={'value':{'node':context['id']},'sentinel':{'local':'kept'}},implementation=code_path,x=431,y=127)
graph['nodes'].insert(1,code);graph['locals']=[dict(id='kept',name='정확한 기존 지역값',type='long',initial={'constant':9223372036854775806})];graph['edges']=[{'from':context['id'],'port':'next','to':'adjust'},{'from':'adjust','port':'next','to':writer['id']}];writer['arguments']['value']={'node':'adjust','output':'total'}
(f.project/graph_path).write_bytes((json.dumps(graph,ensure_ascii=False,indent=2)+'\r\n').encode())
defs=f.metadata('blueprintDescribeOwned',project=str(f.manifest),id=whole_implementation,text=(f.project/impl_path).read_text(),bodyTarget='common',graph=graph,definitionsOnly=True);assert defs['state']=='node-definitions',defs
record=json.loads(whole_record);record['definitionHash']=next(v['definitionHash']for v in defs['nodes']if v['id']==context['id']);(f.project/node_path).write_bytes((json.dumps(record,ensure_ascii=False,indent=2)+'\r\n').encode())
code_record=dict(schema=1,node='adjust',definitionHash=next(v['definitionHash']for v in defs['nodes']if v['id']=='adjust'),source=code_source,helpers=original_helpers);(f.project/code_path).write_bytes((json.dumps(code_record,ensure_ascii=False,indent=2)+'\r\n').encode());code_bytes=(f.project/code_path).read_bytes()
whole_record=(f.project/node_path).read_bytes();whole_flow=(f.project/graph_path).read_bytes();extra_path='Main.csbody';extra_id=f.n+'MainBody/body:common';extra_bytes=(f.project/extra_path).read_bytes();extra_mtime=(f.project/extra_path).stat().st_mtime_ns;original_result=41;edited_result=22
snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts};b.snapshot=snapshot;b._prior.snapshot=snapshot

def unchanged():b.unchanged();assert(f.project/extra_path).read_bytes()==extra_bytes and(f.project/extra_path).stat().st_mtime_ns==extra_mtime
def request():
 r=n.request(copy.deepcopy(old),{'amount':'amount','count':'count'});fn=functions[1];r['changes'].append(dict(type='function-edit',id=fn,hash=hashlib.sha256(r['units'][fn]['draft'].encode()).hexdigest(),name=labels[1],description='',signature=copy.deepcopy(old)))
 for index,row in enumerate(r['changes']):
  row.update(name=labels[index],description='');catalog=f.metadata('informationFunctionBodies',**{k:r[k]for k in ['project','manifest','id','units']},function=row['id'],includeBlueprintTargets=True);key=whole_node if index==0 else row['id']+'Body/body:common';body=catalog[key]
  plan={k:body[k]for k in ['hash','path']}|dict(beforeSignature=copy.deepcopy(native),signature=copy.deepcopy(native),contract=copy.deepcopy(old),text=selected[row['id']]);bodies={key:plan}
  if index==0:
   assert body['sourceKind']=='whole-graph-csharp';plan.update(whole=copy.deepcopy(body['whole']),outputs={'return':'return'});unit=r['units'][code_node];independent=dict(hash=hashlib.sha256(unit['draft'].encode()).hexdigest(),path=unit['path'],beforeSignature=copy.deepcopy(code_signature),signature=copy.deepcopy(code_signature),contract=copy.deepcopy(old),text=code_selected,helpers=selected_helpers,whole=dict(graph=whole_graph,hash=hashlib.sha256(r['units'][whole_graph]['draft'].encode()).hexdigest(),node='adjust',returnNode=writer['id']))
   if mode not in ['reproduce','prior-ui']:assert catalog[code_node]['sourceKind']=='scoped-code-csharp'and catalog[code_node]['whole']==independent['whole']
   bodies[code_node]=independent
  row['mapping']=dict(before=copy.deepcopy(old),args={'amount':'amount','count':'count'},bodies=bodies)
  if index==0:
   uses=f.metadata('informationFunctionInputs',**{k:r[k]for k in ['project','manifest','id','units']},function=row['id']);row['mapping']['callers']={key:{k:value[k]for k in ['graph','node','hash']}|dict(inputs={a['name']:a['name']for a in old['args']},disconnect={})for key,value in uses.items()}
 return r
def verify_rows(rows):
 merged={v['id']:dict(draft=(f.project/v['path']).read_bytes().decode('utf-8-sig'))for v in f.metadata('describe',project=str(f.manifest))['units']}|rows
 assert json.loads(merged[whole_node]['draft'])==json.loads(whole_record)|{'source':selected[whole_function]};assert json.loads(merged[code_node]['draft'])==json.loads(code_bytes)|dict(source=code_selected,helpers=selected_helpers)
 assert merged[whole_graph]['draft']==whole_flow.decode();assert merged[whole_implementation]['draft']==whole_header.decode();assert merged[functions[1]+'Body/body:common']['draft']==selected[functions[1]];assert merged[n.caller+'Body/body:common']['draft']==snapshot[retained_graph].decode();assert merged[n.caller+'Body']['draft']==snapshot[retained_header].decode()
 for fn in functions:assert n.canonical(f.metadata('inspect',text=merged[fn]['draft'])['signature'])==old
 assert extra_id not in rows and(f.project/extra_path).read_bytes()==extra_bytes and(f.project/extra_path).stat().st_mtime_ns==extra_mtime
def verify(checkpoint):
 rows={v['id']:v for v in json.loads(checkpoint.read_text())['changes']};verify_rows(rows);unchanged();ids=rows[owner]['atomicEditGroup'];assert set([owner,*functions,whole_node,code_node,functions[1]+'Body/body:common'])<=set(ids);assert extra_id not in ids;return ids
def verify_live():
 verify_rows({});allowed={node_path,code_path,paths[functions[1]],str(n.a.info.relative_to(f.project)),*['elements/'+fn.split('::')[1]+'.celem'for fn in functions]}
 for path,raw in snapshot.items():
  if path not in allowed:assert(f.project/path).read_bytes()==raw,path
 execute(edited_result,'retained-code-plans');f.checked('all three manual sources execute22; retained/public/native/node ABIs, graph bytes/layout/exact64 and unselected source bytes+mtime remain exact')
def after_contract(index):
 if index==1:return b.after_contract(index)
 from playwright.sync_api import expect
 selector='[data-inline-method="'+functions[0]+'"] [data-function-edit], [data-inline-method="'+functions[0]+'"] [data-function-write-direct]';dialog=f.page.locator('[role=dialog]:has([data-code-source])')
 def open_source(key,source,text,helpers=None):
  f.owner().locator(selector).click();expect(f.page.locator('[role=dialog]:has([data-code-source]), [role=dialog]:has([data-information-body])')).to_be_visible();choice=f.page.locator('[data-information-body="'+key+'"]')
  if choice.count():choice.click()
  expect(dialog).to_be_visible();field=dialog.locator('[data-code-source]')
  if mode=='prior-ui'and key==code_node:
   checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));saved=checkpoint.read_bytes();assert choice.count()==0 and code_source not in field.input_value();dialog.locator('[data-code-cancel]').click();assert d.pending()==first and checkpoint.read_bytes()==saved;unchanged();(f.case/'prior-required-plans-ui.json').write_text(json.dumps(dict(traffic=f.traffic[-12:],rootCodeUnavailable=True,pendingPreserved=True,checkpointPreserved=True),ensure_ascii=False,indent=2));f.checked('prior retained editor preserves its explicit context plan but cannot select the independent root source; no input/source write');f.browser.close();raise SystemExit(0)
  assert source in field.input_value();field.evaluate('(el,text)=>{el.focus();const p=el.value.indexOf(text);el.setSelectionRange(p,p+text.length);}',source);f.page.keyboard.insert_text(text)
  if helpers is not None:field.evaluate('(el,text)=>{el.focus();const p=el.value.indexOf(text);if(p<0)throw Error("Helper source missing");el.setSelectionRange(p,p+text.length);}',original_helpers);f.page.keyboard.insert_text(helpers)
  f.idle()
 held=d.pending();open_source(whole_node,sources[whole_function],selected[whole_function]);dialog.locator('[data-code-cancel]').click();assert d.pending()==held
 open_source(whole_node,sources[whole_function],selected[whole_function]);dialog.locator('[data-code-save]').click();mapping=f.page.locator('[role=dialog]:has([data-abi-remap-accept])');expect(mapping).to_be_visible();mapping.locator('section[data-abi-target="native:'+whole_node+'"] [data-abi-output=return]').select_option('return');mapping.locator('[data-abi-remap-accept]').click();f.idle();first=d.pending()
 for _ in range(2):f.owner().locator('[data-own-functions-toggle]').press('Control+z')
 assert d.pending()==held
 for _ in range(2):f.owner().locator('[data-own-functions-toggle]').press('Control+y')
 assert d.pending()==first
 open_source(code_node,code_source,code_selected,selected_helpers);dialog.locator('[data-code-cancel]').click();assert d.pending()==first
 open_source(code_node,code_source,code_selected,selected_helpers);f.page.screenshot(path=str(f.case/'all-required-source-plans.png'));dialog.locator('[data-code-save]').click();f.idle();saved=d.pending();f.owner().locator('[data-own-functions-toggle]').press('Control+z');assert d.pending()==first;f.owner().locator('[data-own-functions-toggle]').press('Control+y');assert d.pending()==saved;f.checked('retained CSharp/output identity and independent code/helpers are explicitly edited; cancel and each Undo/Redo retain both mandatory source plans')
