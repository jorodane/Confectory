"""원본 컨텍스트 메뉴에서 명시적으로 async 전환하고 checkpoint/Review로 확정한다."""
import copy,json,sys
from playwright.sync_api import sync_playwright,expect
import v666_async_information_fixture as x
f=x.f;mode=sys.argv[3] if len(sys.argv)>3 else 'normal'
def panel():return f.author()
def pending():return f.pending()['blueprint']
def retained(held):return all(dict(pending()).get(key)==value for key,value in held)
def open_graph(feature=x.feature,node=x.node):
 f.idle()
 if panel().is_visible() and panel().locator('[data-bp-node="'+node+'"]').count():return
 x.d.open_info();f.owner().locator('[data-inline-method="'+feature+'"]').locator('[data-function-edit],[data-function-write-direct]').click();expect(panel().locator('[data-bp-node="'+node+'"]')).to_be_visible()

def toggle(node=None):
 target=panel().locator('[data-bp-node="'+node+'"] .function-node-heading') if node else panel().locator('.bp-identity')
 panel().locator('[data-bp-overview-node="'+node+'"]').click() if node else None
 target.click(button='right');f.page.screenshot(path=str(f.case/('menu-'+(node or 'root')+'.png')));(f.case/'menu.html').write_text(f.page.content());f.page.locator('[data-bp-async="'+(node or '$root')+'"]').click()
def place_author():
 # Arrange the generated fixture through the same title drag a user uses,
 # before staging edits. Keep the authored card sizes and screen scale.
 f.page.locator('#workspace').click(position={'x':2200,'y':1100});before=panel().bounding_box();title=panel().locator(':scope > .window-title .caption').bounding_box();left=1730;start={'x':title['x']+8,'y':title['y']+8};f.page.mouse.move(**start);f.page.mouse.down();f.page.mouse.move(start['x']+left-before['x'],start['y'],steps=25);f.page.mouse.up();f.idle();after=panel().bounding_box();(f.case/'fixture-window-placement.json').write_text(json.dumps(dict(before=before,after=after)));f.page.screenshot(path=str(f.case/'fixture-window-placement.png'));assert abs(after['x']-left)<3,after
def front():panel().locator(':scope > .window-title .caption').click(position={'x':5,'y':8})
def activate_save():
 front();panel().locator('[data-bp-save]').click()
def save():
 activate_save();expect(panel().locator('.bp-status')).to_have_text('저장됨',timeout=90000);f.idle()
def restart(i):
 f.pending();f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':2600,'height':1800});f.idle();expect(panel()).to_be_visible();front()
def review():
 front();button=panel().locator('[data-bp-complete]');button.focus();button.press('Enter');f.page.locator('.window[data-key=review]:visible,.window[data-key=targets]:visible').first.wait_for(state='visible',timeout=90000);t=f.page.locator('.window[data-key=targets]')
 if t.is_visible():t.locator('[data-target-choice]').select_option('portable');t.locator('[data-close]').click();panel().locator('[data-bp-complete]').press('Enter')
 r=f.page.locator('.window[data-key=review]');expect(r).to_be_visible(timeout=90000);a=r.locator('[data-review-advanced]')
 if a.is_visible():a.click();r.locator('[data-advanced-reviewed]').check()
 return r
try:
 f.start(0);x.create();f.invoke('select',{'id':x.owner});f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':2600,'height':1800});open_graph();place_author();toggle();assert pending();panel().locator('.bp-viewport').press('Control+z');assert not pending();panel().locator('.bp-viewport').press('Control+y');assert pending();x.original();assert checkpoint.read_bytes()==before;assert not x.path().exists();f.checked('정보 함수의 Root async 메뉴와 Undo/Redo는 모든 새 파일과 등록 원본을 보존한다');toggle(x.node)
  held=copy.deepcopy(pending());restart(1);assert pending()==held;x.original();assert not x.path().exists();f.checked('새 파일이 없는 상태에서 명시 async 입력을 cold 복원한다')
  if mode=='storage':
   checkpoint.chmod(0o400)
   try:
    activate_save();f.idle();actual=pending();(f.case/'storage-proof.json').write_text(json.dumps(dict(held=held,actual=actual,checkpointSame=checkpoint.read_bytes()==before,status=panel().locator('.bp-status').inner_text()),ensure_ascii=False,indent=2));assert retained(held) and checkpoint.read_bytes()==before;x.original()
   finally:checkpoint.chmod(0o600)
   restart(2);f.checked('저장 권한 실패는 모든 입력과 원본을 보존한다')
  if mode=='conflict':
   p=x.path();p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'peer source')
   try:activate_save();f.idle();assert retained(held) and checkpoint.read_bytes()==before
   finally:p.unlink()
   x.original();f.checked('새 파일 경로의 상대 파일 충돌에서 전체 후보와 입력을 보존한다')
  if mode in ['loss','late']:
   requests=set();queries=set();paused={};lost=[]
   def interrupt(route):
    body=route.request.post_data_json
    if body.get('op')=='invoke' and body.get('endpoint')=='blueprint':
     action=body.get('input',{}).get('action')
     if action=='authorBatch':requests.add(body['requestId'])
     elif requests and action=='settledAuthorBatch':queries.add(body['requestId'])
    response=route.fetch();payload=response.json()
    if mode=='late' and not paused and any(r.get('ok') and r.get('requestId') in requests for r in payload.get('results',[])):paused.update(route=route,response=response);return
    if mode=='loss':
     for r in payload.get('results',[]):
      if r['requestId'] in requests|queries:rid=r['requestId'];lost.append(rid);r.clear();r.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
    route.fulfill(response=response,json=payload)
   f.page.route('**/api/request',interrupt);activate_save()
   for _ in range(1000):
    if paused or requests and any(r in queries for r in lost):break
    f.page.wait_for_timeout(30)
   assert len(requests)==1
   if mode=='late':
    assert paused;toggle(x.node);paused['route'].fulfill(response=paused['response']);f.page.unroute('**/api/request',interrupt);f.idle();assert pending();restart(3);mark=len(f.traffic);activate_save();f.idle();assert pending();assert not any(r.get('invoke',{}).get('input',{}).get('action')=='authorBatch'for r in f.traffic[mark:]);(f.case/'late-input-after-query.json').write_text(json.dumps(pending(),ensure_ascii=False,indent=2));save();applied=[r['invoke']['input']for r in f.traffic[mark:]if r.get('invoke',{}).get('input',{}).get('action')=='authorBatch'];assert len(applied)==1 and next(n for n in applied[0]['edits'][0]['definition']['nodes']if n['node']==x.node)['enabled'] is False;assert next(n for n in x.read()['asyncTransition']['nodes']if n['id']==x.node)['enabled'] is False;toggle(x.node);save();f.checked('늦은 명시 전환은 cold 뒤 이전 receipt만 조회하고 새 입력은 별도 Save로 보존한다')
   else:
    assert any(r in queries for r in lost) and pending();f.page.unroute_all(behavior='wait');restart(3);mark=len(f.traffic);save();assert not any(r.get('invoke',{}).get('input',{}).get('action')=='authorBatch' for r in f.traffic[mark:]);f.checked('응답 유실 뒤 cold 재조회는 동일 async 전환을 중복 저장하지 않는다')
  else:save()
  assert not pending();x.original();assert not x.path().exists();assert json.loads(x.draft_unit()['draft'])['source']=='';f.checked('첫 async Save는 기존 파일과 빈 사용자 C#을 보존하고 missing CAS를 유지한다')
  def editor():
   front();panel().locator('[data-bp-overview-node="'+x.node+'"]').press('Enter')
   panel().locator('[data-bp-node="'+x.node+'"] [data-internal-code]').press('Enter');d=f.page.locator('.bp-script-dialog');expect(d).to_be_visible();return d
  d=editor();assert 'Task' in d.locator('[data-code-source]').input_value();f.page.keyboard.insert_text(x.new_source);d.locator('[data-code-cancel]').click();assert not pending();assert json.loads(x.draft_unit()['draft'])['source']==''
  d=editor();f.page.keyboard.insert_text(x.new_source);d.locator('[data-code-save]').click();held=copy.deepcopy(pending());restart(4);assert retained(held);open_graph();save();assert json.loads(x.draft_unit()['draft'])['source']==x.new_source;x.original();assert not x.path().exists();f.checked('Task 고정 서명에서 명시 C#을 작성하고 취소·cold·저장을 거쳐도 기존 원문과 새 입력을 보존한다')
  r=review();r.locator('[data-reject]').click();expect(r).to_be_hidden();x.original();assert not x.path().exists();r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();x.build_new('async-ui');x.run(f.project,'preserved-main-ui',7,'');x.unchanged();assert json.loads(x.path().read_text())['source']==x.new_source
  f.checked('전체 Review 취소/Confirm에서 처음으로 파일을 생성하고 실제 await 뒤 다음 동작을 실행한다');restart(5);assert x.read()['diagnostics']['state']=='source-ready'and x.path().is_file();x.unchanged();f.checked('확정 cold는 새 async 동작·ID·실행선을 복원한다');assert not f.errors and not f.external,(f.errors,f.external);f.page.screenshot(path=str(f.case/'async-final.png'),full_page=True);f.browser.close()
except Exception:
 (f.case/'failure-details.json').write_text(json.dumps({'errors':f.errors,'checks':f.checks},ensure_ascii=False,indent=2))
 try:f.page.screenshot(path=str(f.case/'async-failure.png'),timeout=5000);(f.case/'failure.html').write_text(f.page.content())
 except Exception:pass
 raise
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2));f.stop()
print('ASYNC_INFORMATION_FIXTURE '+str(f.case),flush=True)
