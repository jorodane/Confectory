"""Delete one existing export: durable intent, native rewiring and late-input separation."""
import ast,copy,json,pathlib,sys
from playwright.sync_api import sync_playwright,expect
import v666_export_removal_recovery_fixture as t
x=t.x;f=x.f;mode=sys.argv[3];late='{"constant":29}'
helper=pathlib.Path(__file__).with_name('v666_async_transition_ui.py');names={'panel','open_graph'}
exec(compile(ast.Module(body=[n for n in ast.parse(helper.read_text()).body if isinstance(n,ast.FunctionDef)and n.name in names],type_ignores=[]),str(helper),'exec'))
def private():return f.pending()['blueprint']
def removed():return any(v.get('type')=='export-remove'and v.get('node')==t.node for _,v in private())
def haslate():return any(v.get('node')=='keep'and v.get('type')=='argument:value'and v.get('text')==late for _,v in private())
def show():open_graph(t.feature,'body')
def stage():
 show();panel().locator('[data-bp-overview-node=publish]').click();panel().locator('[data-bp-node=publish] [data-bp-remove]').click();assert removed()
def stage_late(verify=True):
 panel().locator('[data-bp-overview-node=keep]').click();panel().locator('[data-bp-node=keep] [data-exit-value]').click();q=f.page.get_by_role('dialog',name='핀 값 선택').get_by_role('searchbox',name='값 검색');q.fill('29');q.press('Enter')
 if verify:assert haslate()
def save():show();panel().locator('[data-bp-save]').click();f.idle()
def restart(i):
 f.pending();f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});f.idle();show()
def history(direction):
 state=f.invoke('draftHistory',{'action':'inspect'})['result']['result'];assert state[direction]['available'];assert f.invoke('draftHistory',{'action':direction,'token':state[direction]['token']})['result']['result']['accepted'];x.original()
def review():
 show();panel().locator('[data-bp-complete]').click();f.idle()
 if f.page.locator('#review-creation').is_visible():f.page.locator('#review-creation').click();f.idle()
 f.page.locator('.window[data-key=review]:visible,.window[data-key=targets]:visible').first.wait_for(state='visible',timeout=90000);targets=f.page.locator('.window[data-key=targets]')
 if targets.is_visible():targets.locator('[data-target-choice]').select_option('portable');targets.locator('[data-close]').click();panel().locator('[data-bp-complete]').click();f.idle()
 r=f.page.locator('.window[data-key=review]');expect(r).to_be_visible(timeout=90000)
 if r.locator('[data-review-advanced]').is_visible():r.locator('[data-review-advanced]').click()
 if r.locator('[data-advanced-reviewed]').count():r.locator('[data-advanced-reviewed]').check()
 return r
def main():
 stage();canvas=panel().locator('.bp-viewport');canvas.focus();canvas.press('Control+z');assert not removed()and t.current();canvas=panel().locator('.bp-viewport');canvas.focus();canvas.press('Control+y');assert removed()and t.current();x.original();assert checkpoint.read_bytes()==before;restart(1);assert removed()and t.current();f.checked('existing export delete can be cancelled/redone locally and exact deletion intent survives cold without physical writes')
 if mode=='conflict':
  data=t.read();f.invoke('blueprint',dict(action='outputNodes',id=t.graph,basis=data['basis'],edits=[dict(kind='value',node='keep',valueJson=late)]));f.invoke('saveDraft',{});held=checkpoint.read_bytes();save();assert removed()and checkpoint.read_bytes()==held and t.current();x.original();restart(2);save();assert removed()and t.current()and checkpoint.read_bytes()==held;x.original();f.checked('stale export deletion never overwrites another value checkpoint across retry/restart');return
 if mode in ['storage','unapplied-new']:
  checkpoint.chmod(0o400)
  try:save();assert removed()and checkpoint.read_bytes()==before and t.current();x.original();(f.case/'storage-failure-inputs.json').write_text(json.dumps(private(),ensure_ascii=False))
  finally:checkpoint.chmod(0o600)
  if mode=='unapplied-new':
   stage_late();held=checkpoint.read_bytes();mark=len(f.traffic);save();assert removed()and haslate()and checkpoint.read_bytes()==held and t.current();assert not any(r.get('invoke',{}).get('endpoint')=='blueprint'and r['invoke']['input'].get('action')=='outputNodes'for r in f.traffic[mark:]);restart(2);save();assert removed()and haslate()and t.current()and checkpoint.read_bytes()==held;x.original();f.checked('unapplied deletion receipt with a new unrelated value fails closed, retains both across cold and never falls back to live structural writes');return
  restart(2);assert removed()and t.current();f.checked('failed deletion checkpoint preserves live graph/physical originals and exact intent for cold retry')
 if mode in ['loss','late']:
  requests=set();queries=set();paused={};lost=[]
  def interrupt(route):
   body=route.request.post_data_json
   if body.get('op')=='invoke'and body.get('endpoint')=='blueprint':
    op=body.get('input',{}).get('action')
    if op=='authorBatch':requests.add(body['requestId'])
    elif requests and op=='settledAuthorBatch':queries.add(body['requestId'])
   response=route.fetch();payload=response.json()
   if mode=='late'and not paused and any(r.get('ok')and r.get('requestId')in requests for r in payload.get('results',[])):paused.update(route=route,response=response);return
   if mode=='loss':
    for row in payload.get('results',[]):
     if row['requestId']in requests|queries:rid=row['requestId'];lost.append(rid);row.clear();row.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
   route.fulfill(response=response,json=payload)
  f.page.route('**/api/request',interrupt);panel().locator('[data-bp-save]').click()
  for _ in range(1000):
   if paused or requests and any(r in queries for r in lost):break
   f.page.wait_for_timeout(30)
  assert len(requests)==1
  if mode=='late':assert paused;stage_late(False);paused['route'].fulfill(response=paused['response']);f.page.unroute('**/api/request',interrupt);f.idle();assert haslate()and not removed()
  else:assert any(r in queries for r in lost);f.page.unroute_all(behavior='wait');f.idle();assert removed()
  restart(3);assert haslate()if mode=='late'else removed();mark=len(f.traffic);save()
  if removed()or haslate():save()
  assert not removed()and not haslate()and not t.current()
  writes=[r['invoke']['input']for r in f.traffic[mark:]if r.get('invoke',{}).get('endpoint')=='blueprint'and r['invoke']['input'].get('action')=='authorBatch']
  if mode=='loss':assert not writes,writes
  else:assert writes and all(e['definition']['edits']==[dict(kind='value',node='keep',valueJson=late)]for w in writes for e in w['edits'])
  f.checked('export deletion '+mode+': settled receipt verifies absent node; late value is preserved separately without replaying removal')
 else:save();assert not removed()and not t.current();x.original()
 value=29 if mode=='late'else 23;history('undo');assert t.current()is(mode!='late');history('redo');assert not t.current();f.invoke('saveDraft',{});restart(4);assert not removed()and not haslate()and not t.current();x.original();f.checked('shared Undo/Redo/cold restore preserve remaining nodes, outputs and original C#')
 r=review();r.locator('[data-reject]').click();x.original();r=review();p=f.project/t.graph_file;physical=p.read_bytes();held=checkpoint.read_bytes();p.write_bytes(physical+b' ')
 try:r.locator('#confirm').click();f.idle();assert p.read_bytes()==physical+b' 'and checkpoint.read_bytes()==held;assert all(path.read_bytes()==raw for path,raw in x.physical.items()if path!=p)
 finally:p.write_bytes(physical)
 if r.is_visible():r.locator('[data-reject]').click()
 r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();assert json.loads(p.read_text())==t.after(value);assert all(path.read_bytes()==raw for path,raw in x.physical.items()if path!=p);x.build('ordinary-export-removal-execution',*t.expected(value));restart(5);assert not private()and not t.current()and not f.errors and not f.external,(private(),f.errors,f.external);f.page.screenshot(path=str(f.case/'export-removal-final.png'),timeout=5000,full_page=True);f.checked('Review cancel/final physical CAS/new Confirm/actual .NET execution/cold preserve contracts, native line bypass, default-out rules and source bytes')
try:
 f.start(0);f.invoke('select',dict(id=t.feature));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
 with sync_playwright()as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400})
  try:main()
  except Exception:
   (f.case/'failure-inputs.json').write_text(json.dumps(private(),ensure_ascii=False));f.page.screenshot(path=str(f.case/'failure.png'),timeout=5000);raise
  f.browser.close()
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False));f.stop()
print('EXPORT_REMOVAL_RECOVERY_FIXTURE',f.case,flush=True)
