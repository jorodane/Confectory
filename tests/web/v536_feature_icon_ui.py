"""Visible standalone function header glyph, real owner transaction and compiler Confirm."""
import ast,json,pathlib,re,sys,time,zipfile
from playwright.sync_api import sync_playwright,expect
import v536_wide_mixed as f
mode=sys.argv[3] if len(sys.argv)>3 else 'normal';owner=f.n+'Donor';leaf='Donor';file=f.project/'Donor.celem';is_property=is_function=is_new=False;new_label=''
# The same original-popup geometry oracle used by existing element glyph acceptance.
p=pathlib.Path(__file__).with_name('v536_element_icon_ui.py');tree=ast.parse(p.read_text());node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='compare');exec(compile(ast.Module(body=[node],type_ignores=[]),str(p),'exec'))
original_fn=file.read_text().replace('{','{ // preserve feature glyph comment\n',1);file.write_text(original_fn);f.original[file.name]=file.read_bytes();baseline_signature=f.metadata('inspect',text=original_fn)['signature']
def surface():return f.page.locator('.window[data-key=declaration]')
def icon():return surface().locator('.object-icon-control>.obj-icon')
def pending():return [(k,v) for k,v in f.pending()['schema'] if '|'+owner+'|element|' in k]
def popup():surface().locator('.object-icon-edit').click();p=f.page.get_by_role('dialog',name='Donor 아이콘 편집',exact=True);expect(p).to_be_visible();return p
def open_card(target=owner):
 f.page.locator('#workspace').click(button='right',position={'x':80,'y':100});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]');b.locator('[data-tab=feature]').click();b.locator('[data-object="'+target+'"]').press('F2');expect(surface().locator('.object-title-name')).to_have_text(target.split('::')[-1]);f.idle();b.locator('[data-close]').first.click()
def saved():
 for _ in range(600):
  now=f.pending();journal=[v for _,v in now['blueprint'] if v.get('kind')=='owner-attempt' and v.get('owner')==owner]
  if not pending() and not journal:f.idle();return
  if surface().locator('[data-feature-error]').inner_text():raise AssertionError(surface().locator('[data-feature-error]').inner_text())
  f.page.wait_for_timeout(100)
 raise AssertionError((pending(),journal))
def save(ok=True):
 surface().locator('[data-feature-action=save]').click()
 if ok:saved()
 else:expect(surface().locator('[data-feature-error]')).not_to_have_text('',timeout=60000);f.idle();assert pending()
def restart(i):
 f.pending();f.page.unroute_all(behavior='wait');f.page.close();f.stop();f.start(i);f.page=f.setup();expect(surface().locator('.object-title-name')).to_have_text('Donor',timeout=60000);f.idle()
def review():
 surface().locator('[data-feature-action=confirm]').click();f.page.wait_for_function('()=>document.querySelector("#review-creation")||[...document.querySelectorAll(".window[data-key=review]")].some(e=>!e.hidden&&e.getClientRects().length)')
 if f.page.locator('#review-creation').count():f.page.locator('#review-creation').click()
 r=f.page.locator('.window[data-key=review]');expect(r).to_be_visible(timeout=120000);return r
def unchanged():f.originals();assert f.metadata('inspect',text=f.state()['draft']['text'])['signature']==baseline_signature
try:
 f.start(0);f.invoke('select',{'id':owner});f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();open_card();default=icon().inner_text();p=popup();compare(p);p.locator('[data-icon-choice="🔥"]').click();p.locator('[data-cancel]').click();assert not pending();expect(icon()).to_have_text(default);p=popup();p.get_by_label('기호나 이모지',exact=True).fill('ab');p.get_by_role('button',name='적용',exact=True).click();expect(p).to_be_visible();p.get_by_label('기호나 이모지',exact=True).press('Escape');assert not pending();f.checked('원본 기능 헤더 팝오버 취소·Escape·잘못된 glyph는 계약·입력·원본을 유지하고 초점을 복원한다')
  p=popup();p.locator('[data-icon-choice="★"]').click();p.get_by_role('button',name='적용',exact=True).click();surface().locator('.object-icon-edit').focus();f.page.keyboard.press('Control+z');expect(icon()).to_have_text(default);assert not pending();f.page.keyboard.press('Control+y');expect(icon()).to_have_text('★');p=popup();p.locator('[data-icon-choice="🛡️"]').click();p.get_by_role('button',name='적용',exact=True).click();surface().get_by_label('기능 설명',exact=True).fill('아이콘과 설명 원자 저장');surface().locator('.object-icon-edit').focus();f.page.keyboard.press('Control+z');expect(icon()).to_have_text('★');expect(surface().get_by_label('기능 설명',exact=True)).to_have_value('아이콘과 설명 원자 저장');f.page.keyboard.press('Control+y');expect(icon()).to_have_text('🛡️');expect(surface().get_by_label('기능 설명',exact=True)).to_have_value('아이콘과 설명 원자 저장');held=pending();assert len(held)==2;unchanged();assert checkpoint.read_bytes()==before
  if mode=='contexts':
   stale=[]
   def admission(route):
    data=route.request.post_data_json
    if data and data.get('op')=='invoke' and data.get('endpoint')=='select' and data.get('input',{}).get('id')==f.n+'Native' and not stale:stale.append(data['requestId']);data['expectedRevision']=0;route.continue_(post_data=json.dumps(data));return
    route.continue_()
   f.page.route('**/api/request',admission);open_card(f.n+'Native');assert stale;f.page.unroute_all(behavior='wait');surface().locator('.object-icon-edit').focus();f.page.keyboard.press('Control+z');assert pending()==held;assert not [(k,v) for k,v in f.pending()['schema'] if '|'+f.n+'Native|element|' in k];open_card();expect(icon()).to_have_text('🛡️');expect(surface().get_by_label('기능 설명',exact=True)).to_have_value('아이콘과 설명 원자 저장');assert pending()==held;f.checked('F2 선택의 실제 stale admission을 재시도하고 다른 함수의 Undo는 원래 glyph/설명·재진입 입력을 보존한다')
  restart(1);assert pending()==held;expect(icon()).to_have_text('🛡️');f.checked('적용·Undo/Redo·설명 결합·미저장 재시작은 glyph와 원래 함수/typed caller·C#·정확한 값을 보존한다')
  if mode=='conflict':
   peer=file.read_bytes()+b'\n// fixture concurrent source\n';file.write_bytes(peer);f.original[file.name]=peer;save(False);assert pending()==held and checkpoint.read_bytes()==before;unchanged();restart(2);save(False);assert pending()==held and checkpoint.read_bytes()==before;unchanged();f.checked('실제 함수 source 변경은 전체 후보 미적용·입력 보존이며 재시작에도 원래 기준을 자동 교체하지 않는다')
  elif mode=='cancel':
   surface().locator('[data-feature-action=discard]').click();saved();restart(2);assert not pending() and checkpoint.read_bytes()==before;expect(icon()).to_have_text(default);unchanged();f.checked('명시적 변경 취소/cold는 glyph·설명만 취소하고 원본·부모·typed 참조·C#을 보존한다')
  else:
   if mode=='storage':
    checkpoint.chmod(0o400)
    try:save(False);assert pending()==held and checkpoint.read_bytes()==before;unchanged()
    finally:checkpoint.chmod(0o600)
    restart(2);assert pending()==held;f.checked('실제 checkpoint 쓰기 실패는 glyph/설명을 부분 적용하지 않고 원문·저장 기록·재시작 입력을 보존한다')
   if mode=='loss':
    lost=[]
    def intercept(route):
     data=route.request.post_data_json if route.request.method=='POST' else None
     if data and data.get('op')=='update':
      response=route.fetch();payload=response.json();matches=[r for r in payload.get('results',[]) if r.get('ok') and any(t.get('invoke',{}).get('endpoint')=='blueprint' and t['invoke']['input'].get('action')=='applySlots' and t['invoke']['requestId']==r['requestId'] for t in f.traffic)]
      if matches and not lost:lost.extend(r['requestId'] for r in matches);route.abort();return
      route.fulfill(response=response);return
     route.continue_()
    f.page.route('**/api/request',intercept)
   if mode=='late':
    parked=[]
    def intercept(route):
     data=route.request.post_data_json
     if data and data.get('op')=='invoke' and data.get('endpoint')=='blueprint' and data.get('input',{}).get('action')=='applySlots' and not parked:parked.append(route);return
     route.continue_()
    f.page.route('**/api/request',intercept);surface().locator('[data-feature-action=save]').click()
    for _ in range(600):
     if parked:break
     f.page.wait_for_timeout(20)
    assert parked;surface().get_by_label('기능 설명',exact=True).fill('저장 응답 대기 중 새 설명');parked[0].continue_();expect(surface().locator('[data-feature-error]')).to_contain_text('새 입력',timeout=60000);f.page.unroute_all(behavior='wait');restart(3);expect(icon()).to_have_text('🛡️');expect(surface().get_by_label('기능 설명',exact=True)).to_have_value('저장 응답 대기 중 새 설명');assert pending();save();f.checked('응답 대기 중 새 설명은 수락 결과 조회 뒤 별도 입력으로 cold 보존하고 새 명시적 Save만 적용한다')
   else:save()
   if mode=='loss':assert lost;f.page.unroute_all(behavior='wait');f.checked('적용 응답 유실은 기존 요청 결과 조회로 복구하며 입력을 추측 삭제하거나 중복 적용하지 않는다')
   unchanged();restart(4);assert not pending();expect(icon()).to_have_text('🛡️');expected_description='저장 응답 대기 중 새 설명' if mode=='late' else '아이콘과 설명 원자 저장';expect(surface().get_by_label('기능 설명',exact=True)).to_have_value(expected_description);f.checked('한 owner 후보/CAS Save와 cold는 glyph·설명을 함께 저장하고 함수 계약·typed import·구현 C#·부모·다른 값을 유지한다')
   r=review();r.locator('[data-reject]').click();expect(r).to_be_hidden();unchanged();r=review()
   for cb in r.locator('[data-review-id]').all():cb.check()
   if r.locator('[data-review-advanced]').count():
    r.locator('[data-review-advanced]').click()
    if r.locator('[data-advanced-reviewed]').count():r.locator('[data-advanced-reviewed]').check()
   r.locator('#confirm').click();expect(r).to_have_count(0,timeout=120000);f.idle();assert {k for k,v in f.original.items() if (f.project/k).read_bytes()!=v}=={'Donor.celem'};assert 'preserve feature glyph comment' in file.read_text();assert f.metadata('inspect',text=file.read_text())['signature']==baseline_signature;f.checked('Review 취소 뒤 새 명시적 compiler Confirm만 함수 glyph·설명을 반영하며 원문·구현·typed caller·다른 파일·권한을 보존한다')
  assert not f.errors and not f.external,(f.errors,f.external);f.browser.close()
except Exception:
 try:(f.case/'feature-icon-failure.json').write_text(json.dumps({'state':f.state(),'traffic':f.traffic[-90:],'errors':f.errors},ensure_ascii=False,indent=2))
 except Exception:pass
 print('EVIDENCE '+str(f.case),flush=True);raise
finally:f.stop()
print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngine':True,'renderer':True,'nativeWindows':False,'actualMobile':False,'accountOrInference':False},ensure_ascii=False))
