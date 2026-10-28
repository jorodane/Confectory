"""Original information picker and nested values through isolated real engine/renderer."""
import contextlib,json,pathlib,sys,time
from playwright.sync_api import sync_playwright,expect
import v536_wide_mixed as f
mode=sys.argv[3] if len(sys.argv)>3 else 'normal'
(f.project/'Nested.celem').write_text('schema '+f.n+'Nested {field Child single compound '+f.n+'Details;field Counts multiple general long;}')
f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element Nested schema "Nested.celem";registry Confectory.Build.DotNet'))
f.original={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file()}
def draft():return f.owner().locator('[data-definition-key]')
def field(path):return f.owner().locator('[data-property-path=\''+json.dumps(path,separators=(',',':'))+'\']')
def own_inputs():return [(k,v) for k,v in f.pending()['schema'] if '|'+f.id+'|' in k and '|element|' in k]
def restart(i):
 f.pending();f.page.unroute_all(behavior='wait');f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':2300 if mode=='view' else 1600,'height':1400 if mode=='view' else 1100});expect(f.owner().locator('[aria-label="HP 기본값"]')).to_be_visible(timeout=60000);f.idle()
def saved():
 for _ in range(240):
  if not own_inputs() and not [v for k,v in f.pending()['blueprint'] if v.get('kind') in ['owner-attempt','view-owner-attempt']]:f.idle();return
  f.page.wait_for_timeout(100)
 raise AssertionError((f.owner().locator('[data-element-error]').all_text_contents(),f.pending()))
def review():
 f.owner().locator('[data-element-action=confirm]').click();r=f.page.locator('.window[data-key=review]');f.page.wait_for_function('()=>document.querySelector("#review-creation")||[...document.querySelectorAll(".window[data-key=review]")].some(e=>!e.hidden&&e.getClientRects().length)')
 if f.page.locator('#review-creation').count():f.page.locator('#review-creation').click()
 expect(r).to_be_visible();return r
try:
 f.start(0);f.invoke('select',{'id':f.id});f.invoke('saveDraft',{})
 with sync_playwright() as pw:
  f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':2300 if mode=='view' else 1600,'height':1400 if mode=='view' else 1100});expect.set_options(timeout=60000);f.open_owner()
  if mode=='view':
   import v536_view_owner_ui as u
   u.open_two();f.owner=lambda:f.page.locator('.window[data-key="editor-1"]')
  f.owner().locator('[data-schema-add]').click();draft().locator('[data-property-name]').fill('Stats');draft().locator('[data-property-type]').click();picker=f.page.get_by_role('dialog',name='속성 타입 선택',exact=True);expect(picker).to_be_visible();picker.locator('[aria-label="타입 검색"]').fill('Nested');picker.locator('[data-information="'+f.n+'Nested"]').click();expect(draft().locator('[data-property-type]').first).to_have_text('Nested');f.idle();undo=f.owner().locator('[data-own-properties-toggle]');expect(undo).to_be_enabled();undo.focus();expect(undo).to_be_focused()
  f.pending();before_history=f.state()['presentation'].get('privateHistory');f.page.keyboard.press('Control+z')
  expect(draft().locator('[data-property-type]')).to_have_text('글자');f.pending();assert f.state()['presentation'].get('privateHistory')==before_history;draft().locator('[data-property-type]').click();f.page.get_by_role('dialog',name='속성 타입 선택',exact=True).locator('[data-information="'+f.n+'Nested"]').click();expect(field(['Stats','Child','Power']).locator('[data-property-value]')).to_have_value('0');field(['Stats','Child','Power']).locator('[data-property-value]').fill('9223372036854775806');field(['Stats','Child','Label']).locator('[data-property-value]').fill('새 중첩 한글');f.owner().locator('.object-title-description').fill('정보와 한 후보');held=own_inputs();before=next(f.project.glob('.confectory/edit-workspaces/*/draft.json')).read_bytes();f.originals();f.checked('원본 새 속성→정보 검색/선택은 중첩 기본값·multiple 첫 항목을 표시하고 정확한 long/한글을 한 private 정의로 보관한다')
  restart(1);expect(field(['Stats','Child','Power']).locator('[data-property-value]')).to_have_value('9223372036854775806');assert own_inputs()==held;f.originals();f.checked('저장 전 실제 프로세스 재시작은 정보 선택 source proof와 중첩 raw64/한글 입력을 복원한다')
  if mode=='cancel':
   f.owner().locator('[data-element-action=discard]').click();expect(draft()).to_have_count(0);restart(2);assert not own_inputs();assert next(f.project.glob('.confectory/edit-workspaces/*/draft.json')).read_bytes()==before;f.originals();f.checked('명시 취소/cold는 새 정보 속성과 설명 입력만 해제하고 재사용 정의/원본/checkpoint를 보존한다')
  elif mode=='conflict':
   source=f.project/'Details.celem';peer=source.read_bytes()+b'\n// isolated peer definition change\n';source.write_bytes(peer);f.original['Details.celem']=peer;f.rejected_save();assert own_inputs()==held and next(f.project.glob('.confectory/edit-workspaces/*/draft.json')).read_bytes()==before;f.originals();restart(2);assert own_inputs()==held;f.rejected_save();assert own_inputs()==held and source.read_bytes()==peer;f.originals();f.checked('선택 후 실제 재사용 정보 source 변경은 새 정의/등록/설명을 전체 거절하며 cold/재시도에도 원래 proof와 원문/동료 source를 보존한다')
  else:
   if mode=='reject':
    field(['Stats','Child','Power']).locator('[data-property-value]').fill('9223372036854775808');rejected=own_inputs();f.rejected_save();assert own_inputs()==rejected and next(f.project.glob('.confectory/edit-workspaces/*/draft.json')).read_bytes()==before;f.originals();restart(2);expect(field(['Stats','Child','Power']).locator('[data-property-value]')).to_have_value('9223372036854775808');field(['Stats','Child','Power']).locator('[data-property-value]').fill('9223372036854775806');f.checked('중첩 long 범위 오류는 설명/schema/등록 전체 미적용·원문 cold 보존이며 명시 수정 재시도를 준비한다')
   if mode=='storage':
    checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));checkpoint.chmod(0o400)
    try:f.rejected_save();assert checkpoint.read_bytes()==before and own_inputs()==held;f.originals();f.checked('실제 checkpoint 쓰기 실패는 새 schema/등록/owner 전체 미적용이며 중첩 입력을 보존한다')
    finally:checkpoint.chmod(0o600)
    restart(2)
   if mode=='loss':
    applies=set();queries=set();lost=[]
    def intercept(route):
     body=route.request.post_data_json
     if body.get('op')=='invoke' and body.get('endpoint')=='blueprint':
      action=body.get('input',{}).get('action')
      if action=='applySlots':applies.add(body['requestId'])
      elif applies and action=='settledSlots':queries.add(body['requestId'])
     response=route.fetch();payload=response.json()
     for r in payload.get('results',[]):
      if r['requestId'] in applies|queries:rid=r['requestId'];lost.append(rid);r.clear();r.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
     route.fulfill(response=response,json=payload)
    f.page.route('**/api/request',intercept);f.owner().locator('[data-element-action=save]').click()
    for _ in range(300):
     if applies and any(r in queries for r in lost):break
     f.page.wait_for_timeout(100)
    assert len(applies)==1 and any(r in queries for r in lost);assert own_inputs()==held;f.page.unroute_all(behavior='wait');mark=len(f.traffic);restart(2);f.owner().locator('[data-element-action=save]').click();saved();assert not any(r.get('invoke',{}).get('input',{}).get('action')=='applySlots' for r in f.traffic[mark:]);f.checked('정보 정의 저장 응답/조회 유실 뒤 cold receipt 조회만으로 복구하며 schema/등록을 중복 생성하지 않는다')
   else:f.owner().locator('[data-element-action=save]').click();saved()
   f.originals();restart(3);expect(field(['Stats','Child','Power']).locator('[data-property-value]')).to_have_value('9223372036854775806');expect(field(['Stats','Child','Label']).locator('[data-property-value]')).to_have_value('새 중첩 한글');expect(field(['Stats']).locator('[data-property-type]').first).to_have_text('Nested');f.checked('한 후보 Save/cold는 새 compound 정의·등록·값·설명을 함께 보관하고 정보 원본/부모를 바꾸지 않는다');r=review();r.locator('[data-reject]').click();expect(r).to_be_hidden();f.originals();r=review()
   if r.locator('[data-review-advanced]').count():
    r.locator('[data-review-advanced]').click()
    if r.locator('[data-advanced-reviewed]').count():r.locator('[data-advanced-reviewed]').check()
   r.locator('#confirm').click();expect(r).to_have_count(0,timeout=120000);f.idle();changed={k for k,v in f.original.items() if (f.project/k).read_bytes()!=v};assert changed=={'Slime.celem','project.cproj'},changed;restart(4);expect(field(['Stats','Child','Power']).locator('[data-property-value]')).to_have_value('9223372036854775806');f.checked('명시 Review취소/compiler Confirm/cold는 새 schema와 선택 owner/등록만 반영하고 정보/부모/다른 target 원문을 보존한다')
  if mode=='view':
   h=f.pending();history=f.state()['presentation']['privateHistory'];assert history['undo'];sources={p:p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.parts};f.page.locator('#workspace').click(position={'x':2000,'y':750});assert not f.page.evaluate('()=>!!document.activeElement.closest(".object-schema")');f.page.keyboard.press('Control+z');f.pending();undone=f.state()['presentation']['privateHistory'];assert len(undone['undo'])==len(history['undo'])-1 and len(undone['redo'])==len(history['redo'])+1;f.page.keyboard.press('Control+Shift+z');f.pending();redone=f.state()['presentation']['privateHistory'];assert len(redone['undo'])==len(history['undo']) and len(redone['redo'])==len(history['redo']);assert all(p.read_bytes()==data for p,data in sources.items());expect(field(['Stats','Child','Power']).locator('[data-property-value]')).to_have_value('9223372036854775806');f.checked('객체 폼 local Undo는 Workspace 이력을 소비하지 않고, 폼 밖 Workspace Undo/Redo는 동작하며 확정 소스/값을 바꾸지 않는다')
  visible=field(['Stats'])
  if visible.count():visible.scroll_into_view_if_needed()
  f.page.screenshot(path=str(f.case/'information-final.png'));assert not f.errors and not f.external,(f.errors,f.external);f.page.unroute_all(behavior='wait');f.browser.close()
except Exception:
 try:f.case.joinpath('information-failure.json').write_text(json.dumps({'state':f.state(),'traffic':f.traffic[-60:],'errors':f.errors},ensure_ascii=False,indent=2));f.page.screenshot(path=str(f.case/'information-failure.png'))
 except Exception:pass
 print('EVIDENCE '+str(f.case),flush=True);raise
finally:f.stop()
print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngine':True,'renderer':True,'nativeWindows':False,'accountOrInference':False},ensure_ascii=False))
