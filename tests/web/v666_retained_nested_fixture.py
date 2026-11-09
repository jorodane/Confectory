"""Unchanged owned private callers retain qualified code, locals and exact bytes."""
import copy,json,time
import v666_retained_callers_fixture as _prior
for _key in dir(_prior):
 if not _key.startswith('_'):globals()[_key]=getattr(_prior,_key)
_base=_prior._prior._base
_signature={'args':[{'name':'first','type':'long'},{'name':'second','type':'long'}],'return':'long'}
_bindings={name:{'input':name}for name in ['first','second']}
def _box(name,child):return {'id':name,'kind':'graph','control':'next','intent':'기존 내부 '+name,'signature':copy.deepcopy(_signature),'arguments':copy.deepcopy(_bindings),'graph':child}
def _frame(nodes,entry,exits):return {'schema':1,'profile':'sync-acyclic-nested-v1','nodes':nodes,'entry':entry,'edges':[{'from':entry,'port':'next','to':'exit:return'}],'exits':{'return':{'node':exits}},'locals':[{'id':'exact','name':'프레임별 정확한 지역값','type':'long','initial':{'constant':9223372036854775805}}]}
_inner={key:copy.deepcopy(graph[key])for key in ['schema','profile','nodes','entry','edges','exits','locals']};_inner['profile']='sync-acyclic-nested-v1'
_outer=_frame([_box('inner',_inner)],'inner','inner')
_sibling=copy.deepcopy(_inner);_sibling['nodes']=[copy.deepcopy(_inner['nodes'][-1])];_sibling['nodes'][0]['implementation']='sibling-code.node.json';_sibling['nodes'][0]['arguments']={'value':{'input':'first'},'bonus':{'constant':0}};_sibling['entry']='preserved_code';_sibling['edges']=[{'from':'preserved_code','port':'next','to':'exit:return'}];_sibling['exits']={'return':{'node':'preserved_code'}}
graph=copy.deepcopy(graph);graph.update(_frame([_box('outer',_outer),_box('sibling',_sibling)],'outer','outer'));graph['locals']=[];graph['edges']=[{'from':'outer','port':'next','to':'sibling'},{'from':'sibling','port':'next','to':'exit:return'}]
(f.project/retained_graph).write_bytes((json.dumps(graph,ensure_ascii=False,indent=2)+'\n').replace('\n','\r\n').encode())
_defs=f.metadata('blueprintDescribeOwned',project=str(f.manifest),id=n.caller+'Body',text=(f.project/retained_header).read_text(),bodyTarget='common',graph=graph,definitionsOnly=True);assert _defs['state']=='node-definitions',_defs
for _path,_key in [(retained_file,'outer/inner/preserved_code'),('sibling-code.node.json','sibling/preserved_code')]:
 _record=json.loads(snapshot[retained_file]);_record['definitionHash']=next(row['definitionHash']for row in _defs['nestedNodes']if row['id']==_key);(f.project/_path).write_bytes((json.dumps(_record,ensure_ascii=False,indent=2)+'\n').replace('\n','\r\n').encode())
snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts};_base.snapshot=snapshot;_base.graph=graph
def verify_rows(rows):
 merged={row['id']:{'draft':(f.project/row['path']).read_bytes().decode()}for row in f.metadata('describe',project=str(f.manifest))['units']}|rows
 assert json.loads(merged[n.caller+'Body/body:common']['draft'])==graph
 assert merged[n.caller+'Body/body:common']['draft']==snapshot[retained_graph].decode()
 assert merged[n.caller+'Body']['draft']==snapshot[retained_header].decode()
 for key,path in [(n.caller+'Body/body:common/node:outer/node:inner/node:preserved_code',retained_file),(n.caller+'Body/body:common/node:sibling/node:preserved_code','sibling-code.node.json')]:assert merged[key]['draft']==snapshot[path].decode(),key
 for fn in functions:
  assert n.canonical(f.metadata('inspect',text=merged[fn]['draft'])['signature'])==old
  assert merged[fn+'Body']['draft']==snapshot[fn.split('::')[1]+'Body.celem'].decode()
  assert merged[fn+'Body/body:common']['draft']==selected[fn]
_base.verify_rows=verify_rows
def verify(checkpoint):return _base.verify(checkpoint)
def verify_live():
 verify_rows({})
 if 'accepted_description'in globals():assert f.metadata('inspect',text=n.a.info.read_text())['description']==accepted_description
 for path,raw in snapshot.items():
  if path not in set(paths.values())|{'elements/'+fn.split('::')[1]+'.celem'for fn in functions}|{str(n.a.info.relative_to(f.project))}:assert(f.project/path).read_bytes()==raw,path
 execute(edited_result,'retained-private-caller');f.checked('qualified depth2 and sibling code records, CRLF Unicode bytes, local identities/exact64 and all contracts/routes remain unchanged; actual edited program21')
def caller_arguments(index):return copy.deepcopy(graph['nodes'][index]['arguments'])
def caller_exits():return copy.deepcopy(graph['exits'])
def after_contract(index):
 from playwright.sync_api import expect
 fn=functions[index];selector='[data-inline-method="'+fn+'"] [data-function-edit], [data-inline-method="'+fn+'"] [data-function-write-direct]';held=d.pending()
 def open_editor():
  f.owner().locator(selector).click();chooser=f.page.get_by_role('dialog',name='구현 선택',exact=True);expect(chooser).to_be_visible();chooser.locator('[data-information-body="'+fn+'Body/body:common"]').click();expect(chooser).to_have_count(0);dialog=f.page.locator('[role=dialog]:has([data-code-source])');expect(dialog).to_be_visible();return dialog
 def fill(dialog):
  field=dialog.locator('[data-code-source]');assert sources[fn]in field.input_value();field.evaluate('(el,text)=>{el.focus();const i=el.value.indexOf(text);if(i<0)throw Error("Original native body absent");el.setSelectionRange(i,i+text.length);}',sources[fn]);f.page.keyboard.insert_text(selected[fn]);f.idle()
 dialog=open_editor();fill(dialog);dialog.locator('[data-code-cancel]').click();assert d.pending()==held
 dialog=open_editor();fill(dialog);f.page.screenshot(path=str(f.case/('native-private-caller-'+str(index)+'.png')));dialog.locator('[data-code-save]').click();expect(dialog).to_have_count(0);f.idle();saved=d.pending();f.owner().locator('[data-own-functions-toggle]').press('Control+z');assert d.pending()==held;f.owner().locator('[data-own-functions-toggle]').press('Control+y');assert d.pending()==saved
 if index==1 and mode=='reproduce-ui':
  checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));baseline=checkpoint.read_bytes();mark=len(f.traffic);f.owner().locator('[data-element-action=save]').click();deadline=time.monotonic()+60
  while time.monotonic()<deadline:
   ids={row['invoke']['requestId']for row in f.traffic[mark:]if row.get('invoke',{}).get('endpoint')=='blueprint'and row['invoke']['input'].get('action')=='applySlots'};replies=[row['result']for row in f.traffic[mark:]if row.get('result',{}).get('requestId')in ids]
   if replies:assert replies[-1]['ok']is False;break
   f.page.wait_for_timeout(20)
  else:raise AssertionError('No observed joint native Save result')
  assert d.pending()==saved and checkpoint.read_bytes()==baseline;unchanged();f.checked('original chooser selects only each callee body while grouped same-contract Save rejects and retains both inputs and the unchanged nested caller');f.browser.close();raise SystemExit(0)
