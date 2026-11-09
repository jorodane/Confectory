"""Existing serial After and execution wrappers remain unchanged in a body group."""
import copy,json,time
import v666_retained_callers_fixture as _prior
for _key in dir(_prior):
 if not _key.startswith('_'):globals()[_key]=getattr(_prior,_key)
_base=_prior._prior._base
original_result=42;edited_result=29;retained_file='Main.csbody'
for fn in functions:
 p=f.project/('elements/'+fn.split('::')[1]+'.celem');p.write_text(p.read_text().replace('{','{value blueprintPublishedOutputs='+json.dumps(json.dumps(['return']))+';',1))
graph=copy.deepcopy(graph);graph['profile']='sync-acyclic-switch-v1';graph['locals']=[];graph['nodes']=graph['nodes'][:2]
_helpers='private static long Read(long value){return value;} // 원래 보조 함수 😀\r\n'
_first=f.metadata('blueprintCallAfter',functionText=(f.project/('elements/'+functions[0].split('::')[1]+'.celem')).read_text(),source='return Read(@context.@return)+2; // 원래 serial After\r\n',helpers=_helpers)
graph['nodes'][0]['postCall']={k:_first[k]for k in ['contractHash','source','helpers']}
_execution={'primary':'continue','members':[{'id':'continue','name':'Continue','value':0},{'id':'positive','name':'Positive','value':17},{'id':'negative','name':'Negative','value':-3}]}
_second=f.metadata('blueprintCallWrapper',functionText=(f.project/('elements/'+functions[1].split('::')[1]+'.celem')).read_text(),executionEnum=_execution,returnMapping='native-return-out-v1',source='if(@originalBranch!=OriginalResult.NoBranch)throw new global::System.InvalidOperationException();\r\nreturn Read(@context.@return)>30?Result.Positive:Result.Negative; // 원래 실행 선택\r\n',helpers=_helpers)
graph['nodes'][1].update(control='switch',executionEnum=copy.deepcopy(_execution),postCall={k:_second[k]for k in ['mode','contractHash','source','helpers','returnMapping']})
graph['edges']=[{'from':'invoke','port':'next','to':'invoke_second'},{'from':'invoke_second','port':'case:positive','to':'exit:return'},{'from':'invoke_second','port':'case:negative','to':'exit:alternate'},{'from':'invoke_second','port':'next','to':'exit:fallback'}]
graph['exits']={'return':{'node':'invoke_second'},'alternate':{'binary':{'operator':'+','type':'long','operands':[{'node':'invoke_second'},{'constant':7}]}},'fallback':{'constant':9223372036854775806}}
(f.project/retained_graph).write_text(json.dumps(graph,ensure_ascii=False,indent=2)+'\n')
snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts};_base.snapshot=snapshot;_base.graph=graph
verify_rows=_base.verify_rows
def verify(checkpoint):return _base.verify(checkpoint)
def verify_live():
 verify_rows({})
 if 'accepted_description'in globals():assert f.metadata('inspect',text=n.a.info.read_text())['description']==accepted_description
 for path,raw in snapshot.items():
  if path not in set(paths.values())|{'elements/'+fn.split('::')[1]+'.celem'for fn in functions}|{str(n.a.info.relative_to(f.project))}:assert(f.project/path).read_bytes()==raw,path
 for fn in functions:
  path='elements/'+fn.split('::')[1]+'.celem';before=f.metadata('inspect',text=snapshot[path].decode());after=f.metadata('inspect',text=(f.project/path).read_text());assert after['values']==before['values'] and after['relations']==before['relations'],fn
 execute(edited_result,'retained-post-call');f.checked('both original After/helpers, native-return snapshot mapping, OriginalResult.NoBranch and enum IDs17/-3/routes remain exact; edited program takes the original negative branch to29')
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
 dialog=open_editor();fill(dialog);f.page.screenshot(path=str(f.case/('native-wrapper-caller-'+str(index)+'.png')));dialog.locator('[data-code-save]').click();expect(dialog).to_have_count(0);f.idle();saved=d.pending();f.owner().locator('[data-own-functions-toggle]').press('Control+z');assert d.pending()==held;f.owner().locator('[data-own-functions-toggle]').press('Control+y');assert d.pending()==saved
 if index==1 and mode=='reproduce-ui':
  checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));baseline=checkpoint.read_bytes();mark=len(f.traffic);f.owner().locator('[data-element-action=save]').click();deadline=time.monotonic()+60
  while time.monotonic()<deadline:
   ids={row['invoke']['requestId']for row in f.traffic[mark:]if row.get('invoke',{}).get('endpoint')=='blueprint'and row['invoke']['input'].get('action')=='applySlots'};replies=[row['result']for row in f.traffic[mark:]if row.get('result',{}).get('requestId')in ids]
   if replies:assert replies[-1]['ok']is False;break
   f.page.wait_for_timeout(20)
  else:raise AssertionError('No observed joint native Save result')
  assert d.pending()==saved and checkpoint.read_bytes()==baseline;unchanged();f.checked('original chooser selects only each callee body while grouped same-contract Save rejects and retains both inputs and the unchanged post-call wrappers');f.browser.close();raise SystemExit(0)
