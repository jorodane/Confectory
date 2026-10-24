"""Contained inline function Save boundaries with isolated engine/storage/transport fixtures."""
import json,sys,time
from playwright.sync_api import sync_playwright,expect
import v536_field_definitions_ui as d
f=d.f;owner=d.owner;mode=sys.argv[3]
def pending():return d.pending()
def method():return f.owner().locator('[data-inline-method]').last
def restart(i):
 f.pending();f.page.unroute_all(behavior='wait');f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':1700,'height':1300});expect(f.owner().locator('.object-title-name')).to_have_text('FreeInfo');f.idle()
def saved(name):
 deadline=time.monotonic()+60
 while time.monotonic()<deadline:
  if not pending() and any(v['name']==name for v in f.state()['schema'].get('ownFunctions',[])):f.idle();return
  f.page.wait_for_timeout(30)
 raise AssertionError((f.owner().locator('[data-element-error]').all_text_contents(),f.pending()))
try:
 f.start(0);f.invoke('select',{'id':owner});f.invoke('saveDraft',{})
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':1700,'height':1300});d.open_info();f.owner().locator('[data-function-add]').click();method().locator('[data-inline-name]').fill('원래 기능 입력');method().locator('[data-inline-description]').fill('설명 😀');d.field(['Power']).locator('[data-property-value]').fill('9223372036854775803');held=pending();fn=next(v['id'] for _,v in held if v['kind']=='function-add');checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
  if mode in ['storage','conflict']:
   if mode=='storage':checkpoint.chmod(0o400)
   else:
    s=f.state()['schema'];f.invoke('editDescription',{'id':owner,'revision':s['revision'],'hash':s['textHash'],'value':'다른 편집자 변경'});f.invoke('saveDraft',{});before=checkpoint.read_bytes()
   try:f.rejected_save();assert pending()==held and checkpoint.read_bytes()==before;f.originals();f.invoke('schema',{'id':owner});assert not any(v['id']==fn for v in f.state()['schema'].get('ownFunctions',[]));f.checked('저장 거절/실제 동료 변경은 정보 값·함수·등록을 전체 미적용하고 입력과 checkpoint를 보존한다')
   finally:
    if mode=='storage':checkpoint.chmod(0o600)
   restart(1);assert pending()==held
   if mode=='storage':f.owner().locator('[data-element-action=save]').click();saved('원래 기능 입력');assert len([v for v in json.loads(checkpoint.read_text())['changes'] if v['kind']=='function' and v.get('creationOwner')==owner])==1
   else:f.rejected_save();assert pending()==held and checkpoint.read_bytes()==before
   f.originals();f.checked('cold 뒤 새 명시적 재시도는 원래 기준 불변이면 한 번 저장하고 실제 변경이면 입력을 보존하며 거절한다')
  elif mode=='cancel':
   f.owner().locator('[data-element-action=discard]').click();expect(f.owner().locator('[data-inline-method]')).to_have_count(0);expect(d.field(['Power']).locator('[data-property-value]')).to_have_value('9223372036854775806');f.idle();assert not pending();assert checkpoint.read_bytes()==before;restart(1);assert not pending() and checkpoint.read_bytes()==before;f.originals();f.checked('새 자체 기능·기본값의 명시 취소/cold는 미저장 입력만 정리하고 원래 정보·등록을 보존한다')
  elif mode in ['loss','late']:
   applies=set();queries=set();lost={};missing=[]
   def intercept(route):
    body=route.request.post_data_json
    if body.get('op')=='invoke' and body.get('endpoint')=='blueprint':
     action=body.get('input',{}).get('action')
     if action=='applySlots':applies.add(body['requestId'])
     elif applies and action=='settledSlots':queries.add(body['requestId'])
    response=route.fetch();payload=response.json()
    if mode=='late' and not lost and any(v.get('requestId') in applies and v.get('ok') for v in payload.get('results',[])):lost.update(route=route,response=response,payload=payload);return
    for row in payload.get('results',[]):
     if row['requestId'] in applies|(queries if mode=='loss' else set()):rid=row['requestId'];missing.append(rid);row.clear();row.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
    route.fulfill(response=response,json=payload)
   f.page.route('**/api/request',intercept);f.owner().locator('[data-element-action=save]').click();deadline=time.monotonic()+60
   if mode=='late':
    while time.monotonic()<deadline and not lost:f.page.wait_for_timeout(30)
    assert lost;method().locator('[data-inline-name]').fill('응답 대기 중 새 이름');method().locator('[data-inline-description]').fill('새 설명 😀');payload=lost['payload']
    for v in payload['results']:
     if v.get('requestId') in applies:rid=v['requestId'];v.clear();v.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
    lost['route'].fulfill(response=lost['response'],json=payload)
    deadline=time.monotonic()+60
    while time.monotonic()<deadline:
     value=next((v for _,v in pending() if v.get('id')==fn),{})
     if value.get('kind')=='function-edit':break
     f.page.wait_for_timeout(30)
    assert value.get('kind')=='function-edit' and value['name']=='응답 대기 중 새 이름' and value['functionHash']==next(v['hash'] for v in f.state()['schema']['ownFunctions'] if v['id']==fn),value;f.originals();f.page.unroute_all(behavior='wait');f.checked('실제 적용 응답 유실 뒤 늦은 이름/설명은 새 함수의 확인된 hash에 묶인 후속 편집으로 남고 재생성하지 않는다');restart(1);expect(method().locator('[data-inline-name]')).to_have_value('응답 대기 중 새 이름');f.owner().locator('[data-element-action=save]').click();saved('응답 대기 중 새 이름');assert len([v for v in json.loads(checkpoint.read_text())['changes'] if v['kind']=='function' and v.get('creationOwner')==owner])==1;f.originals();f.checked('늦은 함수 입력은 cold 후 한 번의 다음 Save로 보존되고 기존 exact64 값과 원본은 유지된다')
   else:
    while time.monotonic()<deadline and not any(r in queries for r in missing):f.page.wait_for_timeout(30)
    assert len(applies)==1 and any(r in queries for r in missing);assert pending()==held;f.page.unroute_all(behavior='wait');mark=len(f.traffic);restart(1);f.owner().locator('[data-element-action=save]').click();saved('원래 기능 입력');assert not any(v.get('invoke',{}).get('input',{}).get('action')=='applySlots' for v in f.traffic[mark:]);assert len([v for v in json.loads(checkpoint.read_text())['changes'] if v['kind']=='function' and v.get('creationOwner')==owner])==1;f.originals();f.checked('성공/조회 응답 유실은 cold 후 receipt로 확인하며 정보·함수·등록 후보를 중복 적용하지 않는다')
  else:raise AssertionError(mode)
  assert not f.errors and not f.external,(f.errors,f.external);f.page.unroute_all(behavior='wait');f.browser.close()
except Exception:
 try:(f.case/'own-function-boundary-failure.json').write_text(json.dumps({'mode':mode,'traffic':f.traffic,'checks':f.checks,'errors':f.errors,'state':f.state()},ensure_ascii=False,indent=2));f.page.screenshot(path=str(f.case/'own-function-boundary-failure.png'))
 except Exception:pass
 print('EVIDENCE '+str(f.case),flush=True);raise
finally:f.stop()
print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngine':True,'renderer':True,'nativeWindows':False,'accountOrInference':False},ensure_ascii=False))
