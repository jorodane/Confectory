"""Existing detail/connection picker, actual engine and isolated source data."""
import json,time
from playwright.sync_api import sync_playwright,expect
import v536_information_input_replacements_fixture as x
f,d,n,owner,fn=x.f,x.d,x.n,x.owner,x.fn

def pending():return [(k,v) for k,v in d.pending() if v['kind']=='function-edit']
def schema():
 s=f.state();return next(r['schema'] for r in s['editorViews'] if r['view']=='1') if d.is_view else s['schema']
def popup():
 f.owner().locator('[data-inline-method="'+fn+'"] > .function-node-heading').dblclick(position={'x':190,'y':3});p=f.page.locator('.function-detail-popover');expect(p).to_be_visible();return p
def wait(endpoint,start,ok=True,action=None):
 deadline=time.monotonic()+120
 while time.monotonic()<deadline:
  ids={r['invoke']['requestId'] for r in f.traffic[start:] if r.get('invoke',{}).get('endpoint')==endpoint and (action is None or r['invoke']['input'].get('action')==action)}
  rows=[r['result'] for r in f.traffic[start:] if r.get('result',{}).get('requestId') in ids and r['result'].get('error',{}).get('code')!='stale_revision']
  if rows:assert bool(rows[-1]['ok'])==ok,rows[-1];f.idle();return
  f.page.wait_for_timeout(20)
 raise AssertionError({'endpoint':endpoint,'case':str(f.case)})
def preserved():
 expect(f.owner().get_by_label('Power 기본값',exact=True)).to_have_value('9223372036854775806');assert all((f.project/p).read_bytes()==b for p,b in x.snapshot.items());assert not f.page.locator('#app').evaluate('e=>e.inert')
def restart(i):
 f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700})
 if d.is_view:f.owner=lambda:f.page.locator('.window[data-key=editor-1]')
 expect(f.owner().locator('.object-title-name')).to_have_text('FreeInfo');f.idle()
def picker():
 m=f.page.get_by_role('dialog',name='입력 연결 갱신',exact=True);expect(m).to_be_visible();return m
def select():
 m=picker()
 for target in m.locator('section[data-abi-target]').all():
  if target.get_attribute('data-abi-target').startswith('use:'):
   select=target.locator('[data-abi-input=amount]')
   if x.kind=='delete':select.select_option('value');target.locator('[data-abi-value=amount]').fill('9223372036854775806')
   else:select.select_option('pin:count' if x.kind=='type' else 'pin:fresh')
  elif x.kind=='type':target.locator('[data-abi-input=amount]').select_option('value');target.locator('[data-abi-value=amount]').fill('새 한글 값')
  elif x.kind=='mixed':target.locator('[data-abi-input=fresh]').select_option('pin:amount')
 if x.kind!='mixed':m.locator('[data-abi-disconnect=amount]').select_option('disconnect')
 else:
  m.locator('[data-abi-disconnect=amount]').select_option('disconnect');m.locator('[data-abi-remap-accept]').click();expect(m).to_be_visible();expect(m.locator('[data-abi-error]')).to_contain_text('사용하는 기존 연결');m.locator('[data-abi-disconnect=amount]').select_option('')
 f.page.screenshot(path=str(f.case/'replacement-picker.png'));m.locator('[data-abi-remap-accept]').click();expect(m).to_have_count(0);f.idle()
try:
 f.start(0);f.invoke('select',{'id':owner});f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));baseline=checkpoint.read_bytes()
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700});d.open_info();p=popup()
  if x.kind=='type':p.locator('[data-signature-id=arg0] [data-signature-type]').click();f.page.get_by_role('dialog',name='속성 타입 선택',exact=True).locator('[data-type=string]').click()
  else:
   p.locator('[data-signature-id=arg0] [data-signature-remove]').click()
   if x.kind=='mixed':
    p.locator('[data-signature-add=inputs]').click();row=p.locator('[data-signature-kind=inputs] [data-signature-id]').last;row.locator('[data-signature-name]').fill('fresh');row.locator('[data-signature-type]').click();f.page.get_by_role('dialog',name='속성 타입 선택',exact=True).locator('[data-type=long]').click()
  p.get_by_role('button',name='저장',exact=True).click();m=picker();m.locator('[data-abi-remap-accept]').click();expect(m.locator('[data-abi-error]')).to_be_visible();m.locator('[data-abi-remap-cancel]').click();assert pending() and checkpoint.read_bytes()==baseline;preserved()
  p=popup();p.get_by_role('button',name='저장',exact=True).click();select();value=pending()[0][1];assert value['mapping']['args']==x.mapping['args'] and value['mapping']['implementations']
  for _ in range(2):f.owner().locator('[data-own-functions-toggle]').press('Control+z')
  assert not pending()
  for _ in range(2):f.owner().locator('[data-own-functions-toggle]').press('Control+y')
  assert pending()[0][1]==value;held=f.pending();restart(1);assert f.pending()==held;preserved();f.checked('원본 입력 삭제/타입/혼합 선택은 callee·caller를 명시하며 취소·Undo/Redo·미저장 cold 입력/원문 보존')
  if x.mode.endswith('cancel'):
   f.owner().locator('[data-element-action=discard]').click();f.idle();assert not pending() and checkpoint.read_bytes()==baseline;preserved();restart(2);assert not pending() and checkpoint.read_bytes()==baseline;preserved();f.checked('명시 변경 취소·cold는 계약/양쪽 연결 선택만 취소하고 원문·다른 값 보존');f.browser.close();raise SystemExit(0)
  if x.mode.endswith('conflict'):
   s=schema();f.invoke('editDescription',{'id':owner,'hash':s['textHash'],'revision':s['revision'],'value':'다른 편집자의 입력'});start=len(f.traffic);f.rejected_save();assert pending()[0][1]==value and checkpoint.read_bytes()==baseline;assert not any(r.get('invoke',{}).get('input',{}).get('action')=='applySlots' for r in f.traffic[start:]);preserved();f.checked('화면 동시 변경은 원래 후보 저장 전에 거절하고 peer/선택 입력 보존');f.browser.close();raise SystemExit(0)
  if x.mode.endswith('loss'):
   applies=set();queries=set();masked=set()
   def intercept(route):
    body=route.request.post_data_json
    if body.get('op')=='invoke' and body.get('endpoint')=='blueprint':
     action=body.get('input',{}).get('action')
     if action=='applySlots':applies.add(body['requestId'])
     elif applies and action=='settledSlots':queries.add(body['requestId'])
    response=route.fetch();payload=response.json()
    for row in payload.get('results',[]):
     if row['requestId'] in applies|queries:
      rid=row['requestId'];masked.add(rid);row.clear();row.update(requestId=rid,ok=False,error={'code':'transport_lost'})
    route.fulfill(response=response,json=payload)
   f.page.route('**/api/request',intercept);f.owner().locator('[data-element-action=save]').click();deadline=time.monotonic()+90
   while not queries&masked and time.monotonic()<deadline:f.page.wait_for_timeout(20)
   assert len(applies)==1 and queries&masked and pending();f.page.unroute_all(behavior='wait');held=f.pending();mark=len(f.traffic);restart(2);assert f.pending()==held;f.owner().locator('[data-element-action=save]').click();wait('blueprint',mark,True,'settledSlots');deadline=time.monotonic()+60
   while pending() and time.monotonic()<deadline:f.page.wait_for_timeout(20)
   assert not pending();x.verify(checkpoint);preserved();assert not any(r.get('invoke',{}).get('input',{}).get('action')=='applySlots' for r in f.traffic[mark:]);f.checked('callee/caller 저장·조회 응답 유실/cold는 전체 receipt를 조회하며 중복/부분 적용하지 않는다');f.browser.close();raise SystemExit(0)
  if x.mode.endswith('storage'):
   checkpoint.chmod(0o400)
   try:
    start=len(f.traffic);f.owner().locator('[data-element-action=save]').click();wait('blueprint',start,False,'applySlots');assert pending()[0][1]==value and checkpoint.read_bytes()==baseline;preserved()
   finally:checkpoint.chmod(0o600)
   f.checked('화면 쓰기 실패는 정의·callee·caller 전체 미적용과 원래 선택 입력 보존')
  start=len(f.traffic);f.owner().locator('[data-element-action=save]').click();wait('blueprint',start,True,'applySlots');deadline=time.monotonic()+60
  while pending() and time.monotonic()<deadline:f.page.wait_for_timeout(20)
  assert not pending();x.verify(checkpoint);preserved();restart(3);assert not pending();preserved();review=d.review();review.locator('[data-reject]').click();preserved();review=d.review()
  if review.locator('[data-review-advanced]').count():
   review.locator('[data-review-advanced]').click()
   if review.locator('[data-advanced-reviewed]').count():review.locator('[data-advanced-reviewed]').check()
  start=len(f.traffic);review.locator('#confirm').click();wait('confirmGroup',start);expect(review).to_have_count(0);restart(4);assert n.canonical(next(m for m in schema()['ownFunctions'] if m['id']==fn)['signature'])==x.new;assert json.loads((f.project/'function.node.json').read_text())['source']==n.record['source'];f.checked('실제 화면 Save·Review취소·compiler Confirm·cold는 전체 후보만 반영하고 C# 시그니처/본문과 다른 원문 보존');assert not f.errors and not f.external,(f.errors,f.external);f.page.screenshot(path=str(f.case/'replacement-saved.png'));f.browser.close()
except Exception:
 try:(f.case/'replacement-ui-failure.json').write_text(json.dumps({'state':f.state(),'pending':f.pending(),'traffic':f.traffic[-45:]},ensure_ascii=False,indent=2))
 except Exception:pass
 raise
finally:
 print(json.dumps({'checks':f.checks,'mode':x.mode,'view':d.is_view,'evidence':str(f.case),'nativeWindows':False},ensure_ascii=False));f.stop()
