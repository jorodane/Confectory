"""Primary information module implementation UI over the real isolated engine.
Existing v536 layout, native copy/import/body, exact defaults and explicit compiler Confirm.
"""
import json,re,time
from playwright.sync_api import sync_playwright,expect
import v536_field_definitions_ui as d
f=d.f;owner=d.owner;info=f.project/'FreeInfo.celem'
info.write_text(info.read_text().replace('FreeInfo {','FreeInfo {module '+f.n+'Rules;',1))
main=f.project/'MainBody.celem';main.write_text(main.read_text().replace(' in '+f.n+'Slime;',' in '+owner+';'))
f.original={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file()}
def place_info():
 if not d.is_view:return
 w=f.owner();head=w.locator('.object-title-name').bounding_box();box=w.bounding_box();f.page.mouse.move(head['x']+5,head['y']+5);f.page.mouse.down();f.page.mouse.move(1780+head['x']-box['x']+5,80+head['y']-box['y']+5,steps=12);f.page.mouse.up()
def slot(name):return f.owner().locator('[data-module-method="'+f.n+name+'"]')
def copy_input():return next(v['copy'] for _,v in f.pending()['blueprint'] if v.get('kind')=='copy-selection' and v.get('copy',{}).get('owner')==owner)
def saved(feature,implementation):
 deadline=time.monotonic()+90
 while time.monotonic()<deadline:
  inputs=f.pending();state=f.state();s=next(r['schema'] for r in state['editorViews'] if r['view']=='1') if d.is_view else state['schema'];providers=s.get('providers',[]) if s.get('id')==owner else []
  if any(v['function']==f.n+feature and v['implementation']==implementation and v['contract']['status']=='valid' for v in providers) and not d.pending() and not [v for key,v in inputs['blueprint'] if v.get('owner')==owner or v.get('copy',{}).get('owner')==owner or '|slot:'+owner+':' in key]:f.idle();return
  f.page.wait_for_timeout(30)
 raise AssertionError((f.owner().locator('[data-element-error]').all_text_contents(),f.pending()))
def save(feature,implementation):f.owner().locator('[data-element-action=save]').click();saved(feature,implementation);f.originals()
def copy(name,source,text,before=f.body):
 slot(name).locator('[data-function-write-direct]').click();picker=f.page.locator('.feature-import-dialog');expect(picker).to_be_visible();picker.locator('[data-copy-source="'+f.n+source+'"][data-copy-target=common]').click();expect(f.author().locator('[data-bp-node=body]')).to_be_visible();f.edit_region(f.author().locator('[data-bp-node=body] [data-internal-code]'),before,text);f.close_author();return copy_input()['implementation']
def restart(i):
 f.pending();f.page.unroute_all(behavior='wait');f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':2300 if d.is_view else 1800,'height':1500});expect(f.owner().locator('.object-title-name')).to_have_text('FreeInfo');place_info();f.idle();expect(slot('Slot')).to_be_visible();expect(slot('Slot2')).to_be_visible();f.originals()
try:
 f.start(0);f.invoke('select',{'id':owner});f.invoke('saveDraft',{});f.invoke('select',{'id':f.id})
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':2300 if d.is_view else 1800,'height':1500});d.open_info();place_info();expect(slot('Slot').locator('[data-function-write-description]')).to_be_disabled()
  first=copy('Slot','SlotBody','slotCount=amount+7;slotReady=true;return amount+9;');d.field(['Power']).locator('[data-property-value]').fill('9223372036854775804');held=f.pending();f.originals();restart(1);assert f.pending()==held;save('Slot',first);expect(d.field(['Power']).locator('[data-property-value]')).to_have_value('9223372036854775804');f.checked('원본 정보 카드의 직접 작성은 Blueprint 기본 구현을 private copy로 열고 본문·exact64 기본값을 같은 후보로 Save/cold 복원하며 원본은 보존한다')
  slot('Slot2').locator('[data-function-import]').click();picker=f.page.locator('.feature-import-dialog');expect(picker).to_be_visible();picker.locator('[data-feature-import-search]').fill('Donor');picker.locator('[data-feature-import="'+f.n+'Donor"]').click();selected=next(v for _,v in d.pending() if v['kind']=='implementation');second=selected['implementation'];checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();d.field(['Power']).locator('[data-property-value]').fill('9223372036854775803');mixed=f.pending();f.rejected_save();assert f.pending()==mixed and checkpoint.read_bytes()==before;d.field(['Power']).locator('[data-property-value]').fill('9223372036854775804');save('Slot2',second);expect(slot('Slot2').locator('[data-imported-feature-open]')).to_have_text('Donor');f.checked('같은 계약의 명시적 기능 가져오기는 정보 provide/import/본문/등록을 저장하며 아직 지원하지 않는 선택+값 혼합은 전부 미적용·입력 보존한다')
  slot('Slot').locator('[data-function-edit]').click();expect(f.author().locator('[data-bp-node=body]')).to_be_visible();f.edit_region(f.author().locator('[data-bp-node=body] [data-internal-code]'),'slotCount=amount+7;slotReady=true;return amount+9;','slotCount=amount+8;slotReady=false;return amount+10;');f.author().locator('[data-bp-save]').click();expect(f.author().locator('.bp-status')).to_have_text('복사본 · FreeInfo · common');f.close_author();f.originals();restart(2);slot('Slot').locator('[data-function-edit]').click();expect(f.author().locator('[data-bp-node=body]')).to_be_visible();f.author().locator('[data-bp-node=body] [data-internal-code]').click();dialog=f.page.locator('.bp-script-dialog');expect(dialog.locator('[data-code-source]')).to_have_value(re.compile(re.escape('slotCount=amount+8;slotReady=false;return amount+10;')));dialog.locator('[data-code-cancel]').click();f.close_author();f.checked('정보가 독점 소유하는 저장 copy 편집은 원래 body만 저장·재시작하며 donor/부모/다른 target을 쓰지 않는다')
  review=d.review();review.locator('[data-reject]').click();expect(review).to_be_hidden();f.originals();review=d.review()
  if review.locator('[data-review-advanced]').count():
   review.locator('[data-review-advanced]').click()
   if review.locator('[data-advanced-reviewed]').count():review.locator('[data-advanced-reviewed]').check()
  review.locator('#confirm').click();expect(review).to_have_count(0,timeout=120000);f.idle();assert {k for k,v in f.original.items() if (f.project/k).read_bytes()!=v}=={'FreeInfo.celem','project.cproj'};assert 'provide '+f.n+'Slot with '+first in info.read_text() and 'provide '+f.n+'Slot2 with '+second in info.read_text();assert not any(v.get('invoke',{}).get('endpoint') in ['run','runProject','startProject'] for v in f.traffic);f.checked('Review 취소와 새 명시적 compiler Confirm은 정보/등록/새 copy/import만 반영하고 원래 함수/모듈/본문/계정/실행 권한을 보존한다');f.page.screenshot(path=str(f.case/'information-slots-final.png'));assert not f.errors and not f.external,(f.errors,f.external);f.browser.close()
except Exception:
 try:(f.case/'information-slots-ui-failure.json').write_text(json.dumps({'state':f.state(),'traffic':f.traffic[-70:],'errors':f.errors},ensure_ascii=False,indent=2))
 except Exception:pass
 print('EVIDENCE '+str(f.case),flush=True);raise
finally:f.stop()
print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngine':True,'renderer':True,'detachedView':d.is_view,'nativeWindows':False,'accountOrInference':False},ensure_ascii=False))
