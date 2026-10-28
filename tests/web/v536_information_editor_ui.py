"""Original v536 information editor with actual schema/default atomic saves."""
import json,sys
from playwright.sync_api import sync_playwright,expect
import v536_wide_mixed as f
mode=sys.argv[3] if len(sys.argv)>3 else 'normal';owner=f.n+'Details'
extra={'InfoSub':'schema '+f.n+'InfoSub {field Count single general long;}','InfoNested':'schema '+f.n+'InfoNested {field Child single compound '+f.n+'InfoSub;}'}
for key,text in extra.items():(f.project/(key+'.celem')).write_text(text)
f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet',''.join('element '+key+' schema "'+key+'.celem";' for key in extra)+'registry Confectory.Build.DotNet'))
f.original={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file()}
def pending():return [(k,v) for k,v in f.pending()['schema'] if '|'+owner+('|view:1|element|' if mode=='view' else '|element|') in k]
def field(path):return f.owner().locator('[data-property-path=\''+json.dumps(path,separators=(',',':'))+'\']')
def open_info():
 f.page.locator('#workspace').click(button='right',position={'x':80,'y':100});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]');b.locator('[data-tab=info]').click();b.locator('[data-browser-control="object-query"]').fill('Details');b.locator('[data-browser-control="object-search"]').click();row=b.locator('[data-object="'+owner+'"]');expect(row).to_be_visible();expect(row).to_have_attribute('aria-disabled','false');row.click(button='right');f.page.locator('.context-menu').get_by_role('button',name='새 창으로 열기' if mode=='view' else '상세 편집',exact=True).click();expect(f.owner().locator('.object-title-name')).to_have_text('Details');b.locator('[data-close]').first.click();f.idle()
def restart(i):
 f.pending();f.page.unroute_all(behavior='wait');f.page.close();f.stop();f.start(i);f.page=f.setup();expect(field(['Power']).locator('[data-property-value]')).to_be_visible(timeout=60000);f.idle()
def saved():
 for _ in range(240):
  if not pending() and not [v for _,v in f.pending()['blueprint'] if v.get('kind') in ['owner-attempt','view-owner-attempt'] and v.get('owner')==owner]:f.idle();return
  f.page.wait_for_timeout(100)
 raise AssertionError((f.owner().locator('[data-element-error]').all_text_contents(),f.pending()))
def review():
 f.owner().locator('[data-element-action=confirm]').click();r=f.page.locator('.window[data-key=review]');f.page.wait_for_function('()=>document.querySelector("#review-creation")||[...document.querySelectorAll(".window[data-key=review]")].some(e=>!e.hidden&&e.getClientRects().length)')
 if f.page.locator('#review-creation').count():f.page.locator('#review-creation').click()
 expect(r).to_be_visible();return r
try:
 f.start(0);f.invoke('select',{'id':owner});f.invoke('saveDraft',{})
 with sync_playwright() as pw:
  f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();expect.set_options(timeout=60000);
  if mode=='view':f.owner=lambda:f.page.locator('.window[data-key=editor-1]')
  open_info();expect(f.owner().locator('.data-value-field,[data-schema-id]')).to_have_count(0);assert abs(f.owner().bounding_box()['width']-460)<1;field(['Power']).locator('[data-property-value]').fill('9223372036854775806');field(['Label']).locator('[data-property-value]').fill('정보 기본값 한글');field(['Power']).locator('[data-property-name]').fill('공격력');f.owner().locator('.object-title-description').fill('정보 자체 편집')
  f.owner().locator('[data-schema-add]').click();new=f.owner().locator('[data-definition-key]').last;new.locator('[data-property-name]').fill('상태 한글');new.locator('[data-property-type]').click();f.page.get_by_role('dialog',name='속성 타입 선택',exact=True).locator('[data-type=bool]').click();new.locator('[data-property-value]').check();f.owner().locator('[data-schema-add]').click();nested=f.owner().locator('[data-definition-key]').last;nested.locator('[data-property-name]').fill('중첩 정보');nested.locator('[data-property-type]').click();picker=f.page.get_by_role('dialog',name='속성 타입 선택',exact=True);assert picker.locator('[data-information="'+owner+'"]').count()==0;picker.locator('[data-information="'+f.n+'InfoNested"]').click();nested.locator('[aria-label="Count 기본값"]').fill('9223372036854775805');held=pending();assert len([v for _,v in held if v.get('nativeKey')])==2;checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();f.originals();f.checked('원본 정보 탭→460px 정보 카드에서 기존 기본값/표시 이름·한글 새 필드·중첩 기본값을 stable key와 exact long으로 보관한다')
  restart(1);assert pending()==held;expect(field(['Power']).locator('[data-property-value]')).to_have_value('9223372036854775806');f.originals();f.checked('저장 전 프로세스 재시작은 정보 자체 정의/기본값·source proof와 한글 원문을 복원한다')
  if mode=='cancel':
   f.owner().locator('[data-element-action=discard]').click();expect(f.owner().locator('[data-definition-key]')).to_have_count(0);restart(2);assert not pending() and checkpoint.read_bytes()==before;expect(field(['Power']).locator('[data-property-value]')).to_have_value('0');f.originals();f.checked('정보 편집 명시 취소/cold는 기존 저장본·객체 값·부모·원문을 보존하고 새 profile/필드를 만들지 않는다')
  elif mode=='conflict':
   source=f.project/'Details.celem';peer=source.read_bytes()+b'\n// isolated peer information source\n';source.write_bytes(peer);f.original['Details.celem']=peer;f.rejected_save();assert checkpoint.read_bytes()==before and pending()==held;f.originals();restart(2);assert pending()==held;f.rejected_save();assert pending()==held and checkpoint.read_bytes()==before;f.originals();f.checked('실제 정보 source 경합은 새 정의/기본값/설명을 전체 미적용하고 cold 재시도에도 원래 입력과 peer source를 보존한다')
  else:
   if mode=='reject':
    f.owner().get_by_label('Count 기본값',exact=True).fill('9223372036854775808');rejected=pending();f.rejected_save();assert checkpoint.read_bytes()==before and pending()==rejected;f.originals();restart(2);expect(f.owner().get_by_label('Count 기본값',exact=True)).to_have_value('9223372036854775808');f.owner().get_by_label('Count 기본값',exact=True).fill('9223372036854775805');f.checked('중첩 기본값 long 범위 거절은 전체 미적용·원문 cold 보존이며 명시 수정 뒤 같은 기준으로 재시도한다')
   if mode=='storage':
    checkpoint.chmod(0o400)
    try:f.rejected_save();assert checkpoint.read_bytes()==before and pending()==held;f.originals();f.checked('checkpoint 쓰기 실패는 정보 정의/기본값/설명을 전체 미적용하고 입력을 보존한다')
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
    assert len(applies)==1 and any(r in queries for r in lost);assert pending()==held;f.page.unroute_all(behavior='wait');mark=len(f.traffic);restart(2);f.owner().locator('[data-element-action=save]').click();saved();assert not any(r.get('invoke',{}).get('input',{}).get('action')=='applySlots' for r in f.traffic[mark:]);f.checked('정보 owner 저장 응답/조회 유실은 cold receipt 조회만으로 복구하며 새 정의를 중복 적용하지 않는다')
   else:f.owner().locator('[data-element-action=save]').click();saved()
   f.originals();restart(3);expect(field(['Power']).locator('[data-property-name]')).to_have_value('공격력');expect(f.owner().get_by_label('상태 한글 기본값',exact=True)).to_be_checked();expect(f.owner().get_by_label('Count 기본값',exact=True)).to_have_value('9223372036854775805');f.checked('한 후보 Save/cold는 정보 원본의 버전 표식/정의/default를 함께 보관하며 기존 객체 데이터는 바꾸지 않는다');r=review();r.locator('[data-reject]').click();expect(r).to_be_hidden();f.originals();r=review()
   if r.locator('[data-review-advanced]').count():
    r.locator('[data-review-advanced]').click()
    if r.locator('[data-advanced-reviewed]').count():r.locator('[data-advanced-reviewed]').check()
   r.locator('#confirm').click();expect(r).to_have_count(0,timeout=120000);f.idle();changed={k for k,v in f.original.items() if (f.project/k).read_bytes()!=v};assert changed=={'Details.celem'},changed;restart(4);expect(field(['Power']).locator('[data-property-value]')).to_have_value('9223372036854775806');expect(f.owner().get_by_label('Count 기본값',exact=True)).to_have_value('9223372036854775805');f.checked('Review 취소/명시 compiler Confirm/확정 후 cold는 정보 source만 반영하고 부모·객체·다른 target을 보존한다')
  f.page.screenshot(path=str(f.case/'information-editor-final.png'));assert not f.errors and not f.external,(f.errors,f.external);f.page.unroute_all(behavior='wait');f.browser.close()
except Exception:
 try:f.case.joinpath('info-editor-failure.json').write_text(json.dumps({'state':f.state(),'traffic':f.traffic[-70:],'errors':f.errors},ensure_ascii=False,indent=2));f.page.screenshot(path=str(f.case/'info-editor-failure.png'))
 except Exception:pass
 print('EVIDENCE '+str(f.case),flush=True);raise
finally:f.stop()
print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngine':True,'renderer':True,'nativeWindows':False,'accountOrInference':False},ensure_ascii=False))
