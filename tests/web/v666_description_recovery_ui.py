"""Real owned node/function description saving, entry, failure and receipt recovery."""
import ast,copy,json,pathlib,sys
from playwright.sync_api import sync_playwright,expect
import v666_root_execution_fixture as x
f=x.f;target=sys.argv[3];mode=sys.argv[4];text='확인한 설명 α 😀';late='늦게 입력한 설명 β 🛡️';helper=f.repo/'tests/web/v666_async_transition_ui.py'
names={'panel','open_graph'}
exec(compile(ast.Module(body=[n for n in ast.parse(helper.read_text()).body if isinstance(n,ast.FunctionDef)and n.name in names],type_ignores=[]),str(helper),'exec'))
def private():
 value=f.pending();return {key:value.get(key)for key in ['blueprint','declarations','schema']}
def has(value):return value in json.dumps(private(),ensure_ascii=False)
def declaration():return f.page.locator('.window[data-key=declaration]')
def control():
 if target=='node':return panel().locator('[data-bp-node=choose] [data-inline-description]')
 return declaration().locator('[data-inline-description]')
def show():
 if target=='node':
  open_graph();panel().locator('.window-title').click(position={'x':190,'y':16});panel().locator('[data-bp-overview-node=choose]').click()
 else:
  if panel().is_visible():panel().locator('[data-close]').first.click()
  expect(declaration()).to_be_visible();declaration().locator('.window-title').click(position={'x':150,'y':16})
 expect(control()).to_be_visible()
def save():
 show();(panel().locator('[data-bp-save]')if target=='node'else declaration().locator('[data-feature-action=save]')).click();f.idle()
def saved():
 save();assert not has(text)and not has(late),private();x.original()
def restart(i):
 f.pending();f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});f.idle();show()
def stage(value):control().fill(value);f.pending();assert has(value)
def review():
 show();(panel().locator('[data-bp-complete]')if target=='node'else declaration().locator('[data-feature-action=confirm]')).click();f.idle()
 if f.page.locator('#review-creation').is_visible():f.page.locator('#review-creation').click();f.idle()
 f.page.locator('.window[data-key=review]:visible,.window[data-key=targets]:visible').first.wait_for(state='visible',timeout=90000);t=f.page.locator('.window[data-key=targets]')
 if t.is_visible():
  t.locator('[data-target-choice]').select_option('portable');t.locator('[data-close]').click();(panel().locator('[data-bp-complete]')if target=='node'else declaration().locator('[data-feature-action=confirm]')).click()
 r=f.page.locator('.window[data-key=review]');expect(r).to_be_visible(timeout=90000)
 if r.locator('[data-review-advanced]').is_visible():r.locator('[data-review-advanced]').click();r.locator('[data-advanced-reviewed]').check()
 return r
def history(direction):
 state=f.invoke('draftHistory',{'action':'inspect'})['result']['result'];assert state[direction]['available'];result=f.invoke('draftHistory',{'action':direction,'token':state[direction]['token']})['result']['result'];assert result['accepted'];x.original()
def current_text():
 if target=='node':return next(n['intent']for n in x.read()['nodes']if n['id']=='choose')
 return f.invoke('inspectDeclaration',{'id':x.feature})['state']['declaration']['description']
def main():
 open_graph();show();old=control().input_value();control().press('Control+a');f.page.keyboard.insert_text(text);control().press('Control+z');expect(control()).to_have_value(old);control().press('Control+Shift+z');expect(control()).to_have_value(text);assert has(text);x.original();held=copy.deepcopy(private());assert checkpoint.read_bytes()==before;restart(1);expect(control()).to_have_value(text);assert has(text);f.checked(target+': text Undo/Redo and cold retain exact pending description before any Save')
 if mode=='conflict':
  if target=='node':data=x.read();f.invoke('blueprint',{'action':'intent','id':x.graph,'basis':data['basis'],'node':'choose','text':'동료의 새 설명'})
  else:
   info=f.invoke('inspectDeclaration',{'id':x.feature})['state']['declaration'];f.invoke('editFunctionContract',{'id':x.feature,'revision':info['revision'],'hash':info['textHash'],'edit':{'description':'동료의 새 설명'}})
  f.invoke('saveDraft',{});peer=checkpoint.read_bytes();save();assert has(text)and checkpoint.read_bytes()==peer;x.original();restart(2);assert has(text)and checkpoint.read_bytes()==peer;x.original();f.checked(target+': stale pending description cannot overwrite a peer checkpoint or silently rebase after cold');return
 if mode in ['storage','storage-new','entry']:
  checkpoint.chmod(0o400)
  try:
   if mode=='entry':assert target=='function';declaration().locator('[data-function-write-direct]').click();f.idle()
   else:save()
   assert has(text)and checkpoint.read_bytes()==before;x.original();(f.case/'retained-after-storage-failure.json').write_text(json.dumps(private(),ensure_ascii=False))
  finally:checkpoint.chmod(0o600)
  if mode=='storage-new':stage(late)
  restart(2);expect(control()).to_have_value(late if mode=='storage-new'else text);assert has(late if mode=='storage-new'else text);x.original();f.checked(target+': failed checkpoint/entry and cold retain the original description input and checkpoint')
  if mode=='entry':declaration().locator('[data-function-write-direct]').click();f.idle();expect(panel()).to_be_visible();assert checkpoint.read_bytes()!=before and not has(text);x.original();show();f.checked('function: explicit editor entry durably saves the description before opening the existing body')
 if mode in ['loss','late']:
  action='authorBatch'if target=='node'else'applySlots';query='settledAuthorBatch'if target=='node'else'settledSlots';requests=set();queries=set();paused={};lost=[]
  def interrupt(route):
   body=route.request.post_data_json
   if body.get('op')=='invoke'and body.get('endpoint')=='blueprint':
    op=body.get('input',{}).get('action')
    if op==action:requests.add(body['requestId'])
    elif requests and op==query:queries.add(body['requestId'])
   response=route.fetch();payload=response.json()
   if mode=='late'and not paused and any(row.get('ok')and row.get('requestId')in requests for row in payload.get('results',[])):paused.update(route=route,response=response);return
   if mode=='loss':
    for row in payload.get('results',[]):
     if row['requestId']in requests|queries:rid=row['requestId'];lost.append(rid);row.clear();row.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
   route.fulfill(response=response,json=payload)
  f.page.route('**/api/request',interrupt);(panel().locator('[data-bp-save]')if target=='node'else declaration().locator('[data-feature-action=save]')).click()
  for _ in range(1000):
   if paused or requests and any(r in queries for r in lost):break
   f.page.wait_for_timeout(30)
  assert len(requests)==1
  if mode=='late':assert paused;stage(late);paused['route'].fulfill(response=paused['response']);f.page.unroute('**/api/request',interrupt);f.idle();assert has(late)
  else:assert any(r in queries for r in lost);f.page.unroute_all(behavior='wait');f.idle();assert has(text)
  restart(3);wanted=late if mode=='late'else text;assert has(wanted);mark=len(f.traffic);save()
  if has(wanted):save()
  assert not has(wanted)and current_text()==wanted
  writes=[row['invoke']['input']for row in f.traffic[mark:]if row.get('invoke',{}).get('endpoint')=='blueprint'and row['invoke']['input'].get('action')==action]
  if mode=='loss':assert not writes,writes
  else:
   for write in writes:
    changes=write['edits']if target=='node'else write['declaration']['changes'];assert text not in json.dumps(changes,ensure_ascii=False)
  f.checked(target+': '+mode+' recovery separates confirmed receipt/new text without replaying old edits')
 else:saved()
 assert not has(text)and not has(late);value=late if mode in ['late','storage-new']else text;assert current_text()==value;x.original();history('undo');assert current_text()==(text if mode=='late'else old);history('redo');assert current_text()==value;f.invoke('saveDraft',{});restart(4);expect(control()).to_have_value(value);assert not has(value);f.checked(target+': durable metadata supports shared draft Undo/Redo and cold without changing C#/contracts')
 if target=='node':
  assert x.read()['diagnostics']['state']=='needs-implementation';panel().locator('[data-bp-node=choose] [data-internal-code]').click();editor=f.page.locator('.bp-script-dialog');expect(editor).to_be_visible();assert editor.locator('[data-code-region=body]').text_content()==x.original_source.replace('\r\n','\n');editor.locator('[data-code-save]').click();save();assert x.read()['diagnostics']['state']=='source-ready';x.original();f.checked('node intent still invalidates the old implementation; explicit unchanged-C# review restores readiness without rewriting original bytes')
 r=review();r.locator('[data-reject]').click();x.original();r=review();p=f.project/('Flow.graph.json'if target=='node'else'Flow.celem');physical=p.read_bytes();held=checkpoint.read_bytes();p.write_bytes(physical+b' ')
 try:r.locator('#confirm').click();f.idle();assert p.read_bytes()==physical+b' 'and checkpoint.read_bytes()==held;assert all(path.read_bytes()==original for path,original in x.physical.items()if path!=p)
 finally:p.write_bytes(physical)
 if r.is_visible():r.locator('[data-reject]').click()
 r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();assert all(path.read_bytes()==original for path,original in x.physical.items()if path.name not in ({'Flow.graph.json','Flow.node.json'}if target=='node'else{'Flow.celem'}))
 if target=='node':assert json.loads((f.project/'Flow.node.json').read_text())['source'].encode()==x.original_source.encode();g=json.loads(p.read_text());assert g['edges']==x.root['edges']and g['profile']==x.root['profile']and next(n['intent']for n in g['nodes']if n['id']=='choose')==value
 else:assert p.read_bytes()!=physical and current_text()==value
 x.build('description-execution',10,'callee:1\nafter:10');restart(5);expect(control()).to_have_value(value);assert not has(value);assert not f.errors and not f.external,(f.errors,f.external);f.page.screenshot(path=str(f.case/'description-final.png'),timeout=5000,full_page=True);f.checked(target+': Review cancel/final CAS refusal/new Confirm/real execution/cold preserve original code and connections')
try:
 f.start(0);f.invoke('select',dict(id=x.feature));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
 with sync_playwright()as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400})
  try:main()
  except Exception:
   (f.case/'failure-inputs.json').write_text(json.dumps(private(),ensure_ascii=False));f.page.screenshot(path=str(f.case/'failure.png'),timeout=5000);raise
  f.browser.close()
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False));f.stop()
print('DESCRIPTION_RECOVERY_FIXTURE',f.case,flush=True)
