"""Original v666 canvas edits a free node's observed nominal ABI, never the root contract."""
import json,sys,time
from playwright.sync_api import sync_playwright,expect
import v666_native_parameters_fixture as c
f,d=c.f,c.x.d;mode=sys.argv[3]if len(sys.argv)>3 else'normal'
assert mode in ['normal','storage','conflict','cancel','loss','late']
def held():return[(k,v)for k,v in f.pending()['blueprint']if'|v508-author|'in k]
def node():return f.author().locator('[data-bp-node=transform]')
def unit(name):return node().locator('[data-action-field="'+name+'"][data-action-side=inputs]')
def restart(i):
 f.pending();f.page.unroute_all(behavior='wait');f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size(dict(width=2300,height=1700));expect(node()).to_be_visible();f.idle()
def require(value,why):
 if value:return
 (f.case/'assertion-state.json').write_text(json.dumps(dict(why=why,state=f.state(),traffic=f.traffic[-40:],pending=f.pending()),ensure_ascii=False,indent=2));f.page.screenshot(path=str(f.case/'assertion.png'));raise AssertionError(why)
def save(ok=True):
 mark=len(f.traffic);f.author().locator('[data-bp-save]').click();deadline=time.monotonic()+120
 while time.monotonic()<deadline:
  invokes=[r['invoke']for r in f.traffic[mark:]if r.get('invoke',{}).get('endpoint')in['blueprint','saveDraft']];ids={r['requestId']for r in invokes};rows=[r['result']for r in f.traffic[mark:]if r.get('result',{}).get('requestId')in ids and r['result'].get('error',{}).get('code')!='stale_revision']
  if not ok and any(not row['ok']for row in rows):f.idle();return
  if ok and not held():f.idle();return
  f.page.wait_for_timeout(25)
 raise AssertionError(dict(pending=held(),traffic=f.traffic[mark:]))
try:
 f.start(0);f.invoke('select',dict(id=c.x.owner));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));baseline=checkpoint.read_bytes();c.execute(31,'before-parameter-edit')
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size(dict(width=2300,height=1700));d.open_info()
  if c.private:
   f.page.locator('#workspace').click(button='right',position={'x':1000,'y':300});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();browser=f.page.locator('.window[data-key^="browser:project:"]');browser.locator('[data-tab=feature]').click();browser.locator('[data-object="'+c.c.fn+'"]').press('Enter');f.page.locator('.window[data-key=declaration] [data-function-write-direct]').click()
  else:f.owner().locator('[data-inline-method]').last.locator('[data-function-write-direct],[data-function-edit]').first.click()
  if c.private:
   f.page.set_viewport_size(dict(width=390,height=844));f.author().locator('[data-flow-node=private]').click();f.page.locator('.bp-flow-inspector:not([hidden]) [data-flow-internal]').click();expect(f.author().locator('[data-flow-parent]')).to_be_visible();f.page.set_viewport_size(dict(width=2300,height=1700));f.idle()
  expect(node()).to_be_visible();before_reject=held();node().locator('.bp-pin-plug[data-side=in][data-port="field:data"] .bp-value-dropdown').click();f.page.get_by_role('button',name='자료형 선택…',exact=True).click();f.page.get_by_role('dialog',name='속성 타입 선택',exact=True).locator('[data-type=int]').click();f.idle();require(held()==before_reject,"connected nominal input must reject an implicit type change");name=unit('data').locator('[data-action-field-name]');name.fill('received');name.press('Enter');f.idle();expect(unit('received')).to_be_visible();node().locator('[data-action-field-add=inputs]').click();f.idle()
  node().locator('.bp-pin-plug[data-side=in][data-port="field:input1"] .bp-value-dropdown').click();f.page.get_by_role('button',name='자료형 선택…',exact=True).click();picker=f.page.get_by_role('dialog',name='속성 타입 선택',exact=True);expect(picker.locator('[data-type="'+c.payload+'"]')).to_be_visible();assert picker.locator('[data-type^="Confectory.Information."]').count()==(1 if c.private else 3);before_cancel=held();f.page.keyboard.press('Escape');assert held()==before_cancel
  node().locator('.bp-pin-plug[data-side=in][data-port="field:input1"] .bp-value-dropdown').click();f.page.get_by_role('button',name='자료형 선택…',exact=True).click();picker=f.page.get_by_role('dialog',name='속성 타입 선택',exact=True);picker.locator('[data-type="'+c.payload+'"]').click();f.idle()
  contract_held=held();f.author().locator('.bp-viewport').press('Control+z');require(held()!=contract_held,"canvas Undo did not change the typed binding");f.author().locator('.bp-viewport').press('Control+y');require(held()==contract_held,"Redo changed the typed binding");f.checked('Undo/Redo preserves the selected nominal parameter ABI and explicit source binding before independent body input')
  node().locator('.bp-pin-plug[data-side=in][data-port="field:input1"] .bp-value-dropdown').click();f.page.get_by_role('button',name='입력 · data',exact=True).click();f.idle()
  plan=next(json.loads(v['text'])for k,v in held()if v['type']=='parameters');assert plan['args']==[dict(name='received',type=c.payload),dict(name='input1',type=c.payload)] and plan['remap']=={'data':'received'} and plan['returnType']==c.payload
  cancel_held=held();node().locator('[data-internal-code]').click();cancelled=f.page.locator('.bp-script-dialog');field=cancelled.locator('[data-code-source]');old_body=c.c.code_source.replace('\r\n','\n').strip();field.evaluate('(el,text)=>{el.focus();const i=el.value.indexOf(text);el.setSelectionRange(i,i+text.length);}',old_body);f.page.keyboard.insert_text('return received; // cancelled manual source');cancelled.locator('[data-code-cancel]').click();require(held()==cancel_held,'cancelling C# must retain the exact typed parameter plan and binding')
  if mode=='cancel':
   captured=held();restart(1);require(held()==captured,'cancelled source and incomplete ABI must survive restart');assert checkpoint.read_bytes()==baseline;c.unchanged();f.checked('C# cancel and restart keep the explicit incomplete nominal ABI without rewriting or publishing the original source');f.browser.close();raise SystemExit(0)
  node().locator('[data-internal-code]').click();dialog=f.page.locator('.bp-script-dialog');field=dialog.locator('[data-code-source]');old=c.c.code_source.replace('\r\n','\n').strip();assert old in field.input_value();field.evaluate('(el,text)=>{el.focus();const i=el.value.indexOf(text);el.setSelectionRange(i,i+text.length);}',old);f.page.keyboard.insert_text(c.body.replace('\r\n','\n').strip());dialog.locator('[data-code-save]').click();f.idle();captured=held();assert checkpoint.read_bytes()==baseline;c.unchanged();f.checked('original canvas selects only observed frame types, retains cancelled picker state and explicit parameter remap/body/binding without source writes')
  f.author().locator('.bp-viewport').press('Control+z');require(held()==captured,"Undo must retain newer independent binding and body input");restart(1);require(held()==captured,"retained plan changed during restart");c.unchanged();f.page.screenshot(path=str(f.case/'nominal-node-parameters.png'));f.checked('nominal node ABI, bindings and manual C# survive cold restart with root contract, parent and original helpers intact')
  if mode=='conflict':
   leaf=f.project/'Leaf.celem';raw=leaf.read_bytes();leaf.write_bytes(raw+b'\n// another editor\n')
   try:save(False);require(held()==captured,'stale observed type source must retain all pending edits');assert checkpoint.read_bytes()==baseline
   finally:leaf.write_bytes(raw)
   c.unchanged();f.checked('changed observed type source rejects Save without dropping nominal parameters, bindings or body input')
  if mode=='storage':
   checkpoint.chmod(0o400)
   try:save(False);require(held()==captured,"failed storage must retain the complete plan");assert checkpoint.read_bytes()==baseline;c.unchanged()
   finally:checkpoint.chmod(0o600)
   f.checked('checkpoint storage failure retains all nominal node inputs for explicit retry')
  if mode=='loss':
   applies,queries,masked=set(),set(),set()
   def intercept(route):
    body=route.request.post_data_json
    if body.get('op')=='invoke'and body.get('endpoint')=='blueprint':
     action=body.get('input',{}).get('action')
     if action=='authorBatch':applies.add(body['requestId'])
     elif applies and action=='settledAuthorBatch':queries.add(body['requestId'])
    response=route.fetch();payload=response.json()
    for result in payload.get('results',[]):
     if result['requestId']in applies|queries:
      rid=result['requestId'];masked.add(rid);result.clear();result.update(requestId=rid,ok=False,error={'code':'transport_lost'})
    route.fulfill(response=response,json=payload)
   f.page.route('**/api/request',intercept);f.author().locator('[data-bp-save]').click();deadline=time.monotonic()+120
   while time.monotonic()<deadline and not queries&masked:f.page.wait_for_timeout(20)
   require(len(applies)==1 and queries&masked and held(),'retain the uncertain atomic Save');f.page.unroute_all(behavior='wait');captured_all=f.pending();mark=len(f.traffic);restart(2);require(f.pending()==captured_all,'cold restart changed uncertain Save');f.author().locator('[data-bp-save]').click();deadline=time.monotonic()+90
   while held()and time.monotonic()<deadline:f.page.wait_for_timeout(20)
   require(not held(),'settled Save recovery did not finish');assert not any(r.get('invoke',{}).get('input',{}).get('action')=='authorBatch'for r in f.traffic[mark:]);c.verify(checkpoint);c.unchanged();f.checked('lost apply/receipt responses cold-restore exact node ABI/body/bindings and recover the settled receipt without a second atomic apply');f.browser.close();raise SystemExit(0)
  late_intent='Save 응답 중 새 설명';injected=[]
  if mode=='late':
   applies=set()
   def intercept(route):
    body=route.request.post_data_json
    if body.get('op')=='invoke'and body.get('endpoint')=='blueprint'and body.get('input',{}).get('action')=='authorBatch':applies.add(body['requestId'])
    response=route.fetch();payload=response.json()
    if not injected and any(r.get('ok')and r['requestId']in applies for r in payload.get('results',[])):
     node().locator('[data-inline-description]').fill(late_intent);injected.append(True)
    route.fulfill(response=response,json=payload)
   f.page.route('**/api/request',intercept);f.author().locator('[data-bp-save]').click();deadline=time.monotonic()+120
   while time.monotonic()<deadline and not(injected and len(held())==1 and held()[0][1]['type']=='intent'):f.page.wait_for_timeout(20)
   f.page.unroute_all(behavior='wait');require(injected and len(held())==1 and held()[0][1]['text']==late_intent,'late description was lost or not separated from the accepted ABI');c.verify(checkpoint);restart(2);require(len(held())==1 and held()[0][1]['text']==late_intent,'late description did not restore');save();c.verify(checkpoint,late_intent);c.unchanged();f.checked('late node description survives accepted nominal ABI receipt and restart; a second explicit Save retains the contract and typed body');f.browser.close();raise SystemExit(0)
  save();ids=c.verify(checkpoint);c.unchanged();restart(2);assert not held();assert c.verify(checkpoint)==ids
  if mode in ['storage','conflict']:
   f.checked('successful retry atomically saves the complete node candidate and cold-restores it without changing original sources');f.browser.close();raise SystemExit(0)
  f.invoke('reviewGroup',dict(ids=ids,target='portable'));review=f.state()['review'];assert review['status']=='ready',review
  raw=(f.project/c.code_path).read_bytes();(f.project/c.code_path).write_bytes(raw+b'\n ')
  try:out=f.invoke('confirmGroup',dict(ids=ids,token=review['token']))['result']['result'];assert out.get('sourceConfirmed')is False
  finally:(f.project/c.code_path).write_bytes(raw)
  c.unchanged();f.checked('Review never grants a changed physical node source; final CAS rejects while preserving the saved nominal candidate')
  f.invoke('reviewGroup',dict(ids=ids,target='portable'));review=f.state()['review'];assert review['status']=='ready',review;out=f.invoke('confirmGroup',dict(ids=ids,token=review['token']))['result']['result'];assert out.get('sourceConfirmed')is not False; c.unchanged({c.c.graph_path,c.code_path});c.execute(61,'after-parameter-edit');assert not f.errors and not f.external;f.checked('explicit compiler Review/Confirm executes61 through the new nominal ABI while public function, caller, helpers and unrelated originals retain exact contracts/bytes');f.browser.close()
except Exception:
 try:f.page.screenshot(path=str(f.case/'failure.png'));(f.case/'failure-dom.html').write_text(f.page.content())
 except Exception as error:(f.case/'capture-error.txt').write_text(str(error))
 try:(f.case/'failure-state.json').write_text(json.dumps(dict(state=f.state(),traffic=f.traffic[-40:],pending=f.pending()),ensure_ascii=False,indent=2))
 except Exception as error:(f.case/'state-capture-error.txt').write_text(str(error))
 raise
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
