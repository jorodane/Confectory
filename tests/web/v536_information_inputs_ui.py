"""Original detail/ABI picker over real isolated API, renderer and compiler."""
import json,time,shutil
from playwright.sync_api import sync_playwright,expect
import v536_information_inputs_fixture as x
f,d,n,owner,fn=x.f,x.d,x.n,x.owner,x.fn
mode=x.mode

def pending():return [(k,v) for k,v in d.pending() if v['kind']=='function-edit']
def schema():
 s=f.state();return next(r['schema'] for r in s['editorViews'] if r['view']=='1') if d.is_view else s['schema']
def popup():
 f.owner().locator('[data-inline-method="'+fn+'"] > .function-node-heading').dblclick(position={'x':190,'y':3})
 p=f.page.locator('.function-detail-popover');expect(p).to_be_visible();return p
def wait(endpoint,start,ok=True,action=None):
 deadline=time.monotonic()+120
 while time.monotonic()<deadline:
  ids={r['invoke']['requestId'] for r in f.traffic[start:] if r.get('invoke',{}).get('endpoint')==endpoint and (action is None or r['invoke']['input'].get('action')==action)}
  rows=[r['result'] for r in f.traffic[start:] if r.get('result',{}).get('requestId') in ids and r['result'].get('error',{}).get('code')!='stale_revision']
  if rows:assert bool(rows[-1]['ok'])==ok,rows[-1];f.idle();return
  f.page.wait_for_timeout(20)
 raise AssertionError({'endpoint':endpoint,'action':action,'case':str(f.case)})
def preserved():
 expect(f.owner().get_by_label('Power 기본값',exact=True)).to_have_value('9223372036854775806')
 assert all((f.project/p).read_bytes()==b for p,b in x.snapshot.items())
 assert not f.page.locator('#app').evaluate('e=>e.inert')
def restart(i):
 f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700})
 if d.is_view:f.owner=lambda:f.page.locator('.window[data-key=editor-1]')
 expect(f.owner().locator('.object-title-name')).to_have_text('FreeInfo');f.idle()
def picker():
 p=f.page.get_by_role('dialog',name='호출 계약 갱신',exact=True);expect(p).to_be_visible();return p
def select():
 m=picker()
 if mode.startswith('delete'):m.locator('[data-abi-disconnect]').select_option('disconnect')
 elif mode=='binding':
  m.locator('[data-abi-input=count]').select_option('value');m.locator('[data-abi-value=count]').fill('7');m.locator('[data-abi-input=extra]').select_option('pin:count')
 else:
  m.locator('[data-abi-input=extra]').select_option('value');m.locator('[data-abi-value=extra]').fill('9223372036854775806')
 if mode=='binding':
  f.page.set_viewport_size({'width':640,'height':500});assert m.evaluate('e=>e.getBoundingClientRect().width<=innerWidth');f.page.screenshot(path=str(f.case/'input-picker-small.png'))
 m.locator('[data-abi-remap-accept]').click();expect(m).to_have_count(0);f.idle();f.page.set_viewport_size({'width':2300,'height':1700})
def verify():
 rows={r['id']:r for r in json.loads(checkpoint.read_text())['changes']}
 call=json.loads(rows[n.caller+'Body/body:common']['draft'])['nodes'][0]
 assert call['signature']==x.new
 assert call['arguments']==({'amount':{'input':'first'},'count':{'constant':7},'extra':{'input':'second'}} if mode=='binding' else {'amount':{'input':'first'},'count':{'input':'second'}}|({} if mode.startswith('delete') else {'extra':{'constant':9223372036854775806}}))
 assert json.loads(rows[fn+'Body/body:common/node:body']['draft'])['source']==n.record['source']
 return rows
try:
 f.start(0);f.invoke('select',{'id':owner});f.invoke('saveDraft',{})
 checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700});d.open_info()
  p=popup()
  if mode.startswith('delete'):p.locator('[data-signature-id=arg2] [data-signature-remove]').click()
  else:
   p.locator('[data-signature-add=inputs]').click();row=p.locator('[data-signature-kind=inputs] [data-signature-id]').last;row.locator('[data-signature-name]').fill('extra');row.locator('[data-signature-type]').click();f.page.get_by_role('dialog',name='속성 타입 선택',exact=True).locator('[data-type=long]').click()
  p.get_by_role('button',name='저장',exact=True).click();m=picker()
  if mode=='output-guard':
   m.locator('[data-abi-input=extra]').select_option('value');m.locator('[data-abi-value=extra]').fill('4');m.locator('[data-abi-output=return]').select_option('');m.locator('[data-abi-remap-accept]').click();expect(m).to_be_visible(timeout=2000);expect(m.locator('[data-abi-error]')).to_be_visible();assert not pending()[0][1]['mapping'].get('callers');m.locator('[data-abi-output=return]').select_option('return');f.checked('새 입력 대응 중 기존 출력 연결의 모순된 선택을 무시하지 않고 거절한다');m.locator('[data-abi-input=extra]').select_option('')
  m.locator('[data-abi-remap-accept]').click();expect(m.locator('[data-abi-error]')).to_be_visible()
  if not mode.startswith('delete'):
   m.locator('[data-abi-input=extra]').select_option('value');m.locator('[data-abi-value=extra]').fill('9223372036854775806')
  m.locator('[data-abi-remap-cancel]').click();assert pending() and checkpoint.read_bytes()==before;preserved()
  p=popup();p.get_by_role('button',name='저장',exact=True).click();select()
  value=pending()[0][1];assert value['mapping']['callers']
  for selection in value['mapping']['callers'].values():
   if mode.startswith('delete'):assert selection['disconnect']['extra']=='{"constant":9223372036854775806}'
   elif mode=='binding':assert selection['inputs']['extra']=='count' and selection['inputs']['count']=={'valueJson':'7'}
   else:assert selection['inputs']['extra']=={'valueJson':'9223372036854775806'}
  for _ in range(2):f.owner().locator('[data-own-functions-toggle]').press('Control+z')
  assert not pending()
  for _ in range(2):f.owner().locator('[data-own-functions-toggle]').press('Control+y')
  assert pending()[0][1]==value
  held=f.pending();restart(1);assert f.pending()==held;preserved()
  f.checked('원본 상세 입력 추가/삭제·명시 caller 선택·선택취소·Undo/Redo·cold 입력/정확64값 보존')
  if mode=='projects':
   alist=f.state()['listingId'];f.page.close();f.stop();other=f.case/'other root'/'owned project';shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory'));f.env['CONFECTORY_WEB_PROJECT']=str(other/'project.cproj');f.start(2);f.invoke('select',{'id':owner});f.invoke('saveDraft',{});blist=f.state()['listingId'];bcheckpoint=next(other.glob('.confectory/edit-workspaces/*/draft.json'));bsaved=bcheckpoint.read_bytes();f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700})
   def enter(listing):
    f.page.locator('.brand').click();expect(f.page.locator('.home-grid')).to_be_visible();f.page.locator('[data-enter="'+listing+'"]').click();expect(f.page.locator('.work-body')).to_be_visible();f.idle()
   enter(alist);assert pending()[0][1]['mapping']==value['mapping'];p=popup();p.locator('form').evaluate('el=>globalThis.staleInputForm=el');enter(blist);d.open_info();assert not pending();f.page.evaluate("()=>staleInputForm.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}))");assert not pending() and checkpoint.read_bytes()==before and bcheckpoint.read_bytes()==bsaved;enter(alist);assert pending()[0][1]['mapping']==value['mapping'];preserved();f.checked('같은 namespace/요소 ID의 다른 프로젝트 전환·오래된 form 제출은 입력을 분리하고 caller/source를 변경하지 않는다');f.browser.close();raise SystemExit(0)
  if mode=='loss':
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
   f.page.route('**/api/request',intercept);f.owner().locator('[data-element-action=save]').click()
   deadline=time.monotonic()+90
   while not queries&masked and time.monotonic()<deadline:f.page.wait_for_timeout(20)
   assert len(applies)==1 and queries&masked and pending();f.page.unroute_all(behavior='wait');held=f.pending();mark=len(f.traffic);restart(2);assert f.pending()==held
   f.owner().locator('[data-element-action=save]').click();wait('blueprint',mark,True,'settledSlots')
   deadline=time.monotonic()+60
   while pending() and time.monotonic()<deadline:f.page.wait_for_timeout(20)
   assert not pending();verify();preserved()
   assert not any(r.get('invoke',{}).get('input',{}).get('action')=='applySlots' for r in f.traffic[mark:])
   f.checked('저장·조회 응답 유실 뒤 cold receipt 확인으로 중복적용 없이 전체 후보 복원')
   f.browser.close();raise SystemExit(0)
  if mode=='storage':
   checkpoint.chmod(0o400)
   try:
    start=len(f.traffic);f.owner().locator('[data-element-action=save]').click();wait('blueprint',start,False,'applySlots');assert pending()[0][1]==value and checkpoint.read_bytes()==before;preserved()
   finally:checkpoint.chmod(0o600)
   f.checked('실제 화면 쓰기 실패는 전체 미적용 및 원래 입력·기존 checkpoint 보존')
  start=len(f.traffic);f.owner().locator('[data-element-action=save]').click();wait('blueprint',start,True,'applySlots')
  deadline=time.monotonic()+60
  while pending() and time.monotonic()<deadline:f.page.wait_for_timeout(20)
  assert not pending();verify();preserved();restart(3);assert not pending();preserved()
  review=d.review();review.locator('[data-reject]').click();preserved();review=d.review()
  if review.locator('[data-review-advanced]').count():
   review.locator('[data-review-advanced]').click()
   if review.locator('[data-advanced-reviewed]').count():review.locator('[data-advanced-reviewed]').check()
  start=len(f.traffic);review.locator('#confirm').click();wait('confirmGroup',start);expect(review).to_have_count(0);restart(4)
  assert n.canonical(next(r for r in schema()['ownFunctions'] if r['id']==fn)['signature'])==x.new
  assert json.loads((f.project/'function.node.json').read_text())['source']==n.record['source']
  f.checked('실제 UI Save·Review취소·Confirm·cold는 함수/구현/호출 전체 그룹만 반영')
  f.page.screenshot(path=str(f.case/'information-inputs.png'));assert not f.errors and not f.external,(f.errors,f.external);f.browser.close()
except Exception:
 try:(f.case/'input-ui-failure.json').write_text(json.dumps({'state':f.state(),'pending':f.pending(),'traffic':f.traffic[-45:]},ensure_ascii=False,indent=2))
 except Exception:pass
 raise
finally:
 print(json.dumps({'checks':f.checks,'mode':mode,'view':d.is_view,'evidence':str(f.case)},ensure_ascii=False));f.stop()
