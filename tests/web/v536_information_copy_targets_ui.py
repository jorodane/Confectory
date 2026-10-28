"""Original function/body selectors join two explicitly selected target copies."""
import json,time,shutil
from playwright.sync_api import sync_playwright,expect
import v536_information_copy_targets_fixture as x
f,d,owner,fn,mode=x.f,x.d,x.owner,x.fn,x.mode
x.expected_text={k:v.replace('\r\n','\n') for k,v in x.expected_text.items()}

def pending():return [(k,v) for k,v in d.pending() if v['kind']=='function-edit']
def preserved():
 x.unchanged();expect(f.owner().get_by_label('Power 기본값',exact=True)).to_have_value('9223372036854775806');assert not f.page.locator('#app').evaluate('e=>e.inert')
def restart(i):
 held=f.pending();f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700})
 if d.is_view:f.owner=lambda:f.page.locator('.window[data-key=editor-1]')
 expect(f.owner().locator('.object-title-name')).to_have_text('FreeInfo');f.idle();return held

def wait(endpoint,mark,action=None,ok=True):
 until=time.monotonic()+120
 while time.monotonic()<until:
  ids={r['invoke']['requestId'] for r in f.traffic[mark:] if r.get('invoke',{}).get('endpoint')==endpoint and (action is None or r['invoke']['input'].get('action')==action)}
  rows=[r['result'] for r in f.traffic[mark:] if r.get('result',{}).get('requestId') in ids and r['result'].get('error',{}).get('code')!='stale_revision']
  if rows:assert bool(rows[-1]['ok'])==ok,rows[-1];f.idle();return rows[-1]
  f.page.wait_for_timeout(20)
 raise AssertionError((endpoint,action,str(f.case)))

def body(id):
 f.owner().locator('[data-inline-method="'+fn+'"] [data-function-edit], [data-inline-method="'+fn+'"] [data-function-write-direct]').click();picker=f.page.get_by_role('dialog',name='구현 선택',exact=True);expect(picker).to_be_visible();picker.locator('[data-information-body="'+id+'"]').click();dialog=f.page.locator('[role=dialog]:has([data-code-source])');expect(dialog).to_be_visible();return dialog

def fill(dialog,text):
 field=dialog.locator('[data-code-source]');field.evaluate(r"e=>{e.focus();e.setSelectionRange(e.value.indexOf('\n{\n')+3,e.value.lastIndexOf('\n}'));}");f.page.keyboard.insert_text(text)
def store(id,text=None):
 dialog=body(id)
 if text is not None:fill(dialog,text)
 dialog.locator('[data-code-save]').click();expect(dialog).to_be_hidden();f.idle()

def save():
 mark=len(f.traffic);f.owner().locator('[data-element-action=save]').click();wait('blueprint',mark,'applySlots')
 for _ in range(600):
  if not pending():return
  f.page.wait_for_timeout(30)
 raise AssertionError(f.owner().locator('[data-element-error]').all_text_contents())

try:
 f.start(0);f.invoke('select',{'id':owner});f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));baseline=checkpoint.read_bytes()
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700});d.open_info()
  f.owner().locator('[data-inline-method="'+fn+'"] > .function-node-heading').dblclick(position={'x':190,'y':3});popup=f.page.locator('.function-detail-popover');expect(popup).to_be_visible();popup.locator('[data-signature-id=arg0] [data-signature-name]').fill('renamed');popup.get_by_role('button',name='저장',exact=True).click();f.idle()
  for key in [x.first.c.body_id,x.first.donor_id,x.donor_windows]:store(key)
  store(x.first.body_id,x.expected_text[x.first.body_id]);initial=pending()[0][1]
  dialog=body(x.second_body);assert 'long first, long second' in dialog.locator('[data-code-source]').input_value();fill(dialog,x.expected_text[x.second_body]+'incomplete');held=restart(1);assert f.pending()==held
  dialog=body(x.second_body);assert 'incomplete' in dialog.locator('[data-code-source]').input_value();dialog.locator('[data-code-cancel]').click();after_cancel=pending()[0][1];assert after_cancel['mapping']==initial['mapping'] and x.second_body not in after_cancel['mapping'].get('bodies',{});assert 'incomplete' in after_cancel['bodyDrafts'][x.second_body]['text']
  store(x.second_body,x.expected_text[x.second_body]);value=pending()[0][1];assert value['signature']==x.new;assert set(value['mapping']['copies'])==set(x.graphs)
  for key in x.body_ids:assert value['mapping']['bodies'][key]['text']==x.expected_text[key]
  f.owner().locator('[data-own-functions-toggle]').press('Control+z');assert x.second_body not in pending()[0][1]['mapping']['bodies'];f.owner().locator('[data-own-functions-toggle]').press('Control+y');assert pending()[0][1]==value
  held=restart(2);assert f.pending()==held and pending()[0][1]==value;preserved();f.page.screenshot(path=str(f.case/'explicit-two-copy-targets.png'));f.checked('원래 구현 선택에서 명시한 common/windows copy의 본문·배정·정확한 값은 취소·불완전 입력 cold·Undo/Redo에 보존된다')
  if mode=='projects':
   listing=f.state()['listingId'];held=f.pending();f.page.close();f.stop();other=f.case/'other root'/'owned project';shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory'));f.env['CONFECTORY_WEB_PROJECT']=str(other/'project.cproj');f.start(6);f.invoke('select',{'id':owner});f.invoke('saveDraft',{});other_listing=f.state()['listingId'];other_checkpoint=next(other.glob('.confectory/edit-workspaces/*/draft.json'));other_saved=other_checkpoint.read_bytes();f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700})
   def enter(id):
    f.page.locator('.brand').click();expect(f.page.locator('.home-grid')).to_be_visible();f.page.locator('[data-enter="'+id+'"]').click();expect(f.page.locator('.work-body')).to_be_visible();f.idle()
   enter(listing);assert f.pending()==held and pending()[0][1]==value;dialog=body(x.second_body);dialog.locator('[data-code-save]').evaluate('e=>globalThis.staleCopySave=e');dialog.locator('[data-code-cancel]').click();enter(other_listing);d.open_info();assert not pending();f.page.evaluate('()=>staleCopySave.click()');assert not pending() and checkpoint.read_bytes()==baseline and other_checkpoint.read_bytes()==other_saved;enter(listing);assert pending()[0][1]==value;f.env['CONFECTORY_WEB_PROJECT']=str(f.manifest);preserved();f.checked('동일 namespace 프로젝트 전환은 명시 copy 대상과 창 입력을 분리하고 닫힌 C# 저장의 교차 적용을 막는다')
  if mode=='cancel':
   f.owner().locator('[data-element-action=discard]').click();f.idle();assert not pending();assert checkpoint.read_bytes()==baseline;preserved();restart(3);assert not pending();preserved();f.checked('변경 취소·cold는 copy 생성/배정과 원본을 유지하고 이번 callee/본문 입력만 취소한다')
  elif mode=='conflict':
   s=f.state()['schema'];f.invoke('editDescription',{'id':owner,'revision':s['revision'],'hash':s['textHash'],'value':'동료 입력 보존'});f.invoke('saveDraft',{});peer=checkpoint.read_bytes();f.rejected_save();assert pending()[0][1]==value and checkpoint.read_bytes()==peer;preserved();held=restart(3);assert f.pending()==held and pending()[0][1]==value;assert checkpoint.read_bytes()==peer;f.checked('동료 소스/CP 경합은 두 copy·callee를 전부 미적용하고 상대 저장과 원래 입력을 cold에 유지한다')
  else:
   if mode=='last-invalid':
    store(x.second_body,'return unknown;');bad=pending()[0][1];f.rejected_save();assert checkpoint.read_bytes()==baseline and pending()[0][1]==bad;preserved();f.owner().locator('[data-own-functions-toggle]').press('Control+z');assert pending()[0][1]==value;f.checked('마지막 copy의 실제 잘못된 C#은 앞선 copy·callee를 남기지 않고 Undo 후 명시 재시도를 허용한다')
   if mode=='storage-loss':
    checkpoint.chmod(0o400)
    try:f.rejected_save();assert checkpoint.read_bytes()==baseline and pending()[0][1]==value;preserved()
    finally:checkpoint.chmod(0o600)
    f.checked('실제 CP 쓰기 실패는 두 copy·callee 전체 미적용과 모든 원문/입력을 유지한다')
    applies=set();queries=set();masked=set()
    def intercept(route):
     request=route.request.post_data_json
     if request.get('op')=='invoke' and request.get('endpoint')=='blueprint':
      action=request.get('input',{}).get('action')
      if action=='applySlots':applies.add(request['requestId'])
      elif applies and action=='settledSlots':queries.add(request['requestId'])
     response=route.fetch();payload=response.json()
     for row in payload.get('results',[]):
      if row['requestId'] in applies|queries:
       rid=row['requestId'];masked.add(rid);row.clear();row.update(requestId=rid,ok=False,error={'code':'transport_lost'})
     route.fulfill(response=response,json=payload)
    f.page.route('**/api/request',intercept);f.owner().locator('[data-element-action=save]').click();until=time.monotonic()+90
    while time.monotonic()<until and not queries&masked:f.page.wait_for_timeout(20)
    assert len(applies)==1 and queries&masked and pending();f.page.unroute_all(behavior='wait');held=restart(3);assert f.pending()==held;mark=len(f.traffic);f.owner().locator('[data-element-action=save]').click();wait('blueprint',mark,'settledSlots');assert not any(r.get('invoke',{}).get('input',{}).get('action')=='applySlots' for r in f.traffic[mark:]);assert not pending();f.checked('저장 응답/결과 조회 유실 후 cold 재시도는 조회로 전체 적용을 확인하고 두 copy를 중복 저장하지 않는다')
   else:save()
   ids=x.verify(checkpoint);preserved();restart(4);assert x.verify(checkpoint)==ids;preserved();f.checked('하나의 실제 후보/CAS·cold 저장은 두 target copy 본문과 callee만 결합하고 원본·다른 target·배정을 보존한다')
   review=d.review();expect(review).to_be_visible();assert f.state()['review']['status']=='ready';review.locator('[data-reject]').click();preserved();review=d.review()
   if mode in ['ownership-cas','record-cas']:
    before_confirm=checkpoint.read_bytes();peer_path='WindowsHost.celem' if mode=='ownership-cas' else x.second_path;file=f.project/peer_path
    if mode=='ownership-cas':file.write_text(file.read_text().replace(x.second_copy,x.first.donor_impl))
    else:
     record=json.loads(file.read_text());record['source']='return first; // 동료의 먼저 저장된 원문';file.write_text(json.dumps(record))
    x.snapshot[peer_path]=file.read_bytes()
   if review.locator('[data-review-advanced]').count():
    review.locator('[data-review-advanced]').click()
    if review.locator('[data-advanced-reviewed]').count():review.locator('[data-advanced-reviewed]').check()
   mark=len(f.traffic);review.locator('#confirm').click();result=wait('confirmGroup',mark)
   if mode in ['ownership-cas','record-cas']:
    assert result['result']['sourceConfirmed'] is False,{'result':result,'logs':f.state().get('logs')};assert checkpoint.read_bytes()==before_confirm;preserved();held=restart(5);assert f.pending()==held and checkpoint.read_bytes()==before_confirm;x.verify(checkpoint);preserved();f.checked('Confirm 직전의 두 번째 copy 배정/본문 실제 경합은 모든 source를 미적용하고 상대 원문과 저장 초안을 cold에 보존한다')
   else:
    assert result['result']['sourceConfirmed'],{'review':f.state().get('review',{}).get('status'),'logs':f.state().get('logs')};expect(review).to_have_count(0)
   if mode not in ['ownership-cas','record-cas']:
    for key,path in [(x.first.body_id,x.first.body_path),(x.second_body,x.second_path)]:assert json.loads((f.project/path).read_text())['source']==x.expected_text[key]
    for path in [x.first.donor_path,x.first.donor_body_path,'whole-caller-windows.csbody','CallerHost.celem','WindowsHost.celem','project.cproj']:assert (f.project/path).read_bytes()==x.snapshot[path]
    f.checked('원래 Review 취소·재검토·명시 compiler Confirm은 두 copy를 함께 반영하고 donor/두 배정 및 공개 copy 계약을 보존한다')
  assert not f.errors and not f.external,(f.errors,f.external);f.browser.close()
except Exception:
 try:
  (f.case/'failure.json').write_text(json.dumps({'checks':f.checks,'state':f.state(),'traffic':f.traffic[-50:]},ensure_ascii=False,indent=2))
 except Exception:pass
 raise
finally:f.stop();print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngine':True,'nativeWindows':False,'projectRun':False},ensure_ascii=False))
