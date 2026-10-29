"""Workspace's original Enum creation, registration Review, cold and explicit Confirm."""
import json,pathlib,sys
from playwright.sync_api import sync_playwright,expect
import v536_wide_mixed as f
mode=sys.argv[3] if len(sys.argv)>3 else 'normal';owner=f.n+'NewMood';file=f.project/'elements/NewMood.celem';snapshot={p:p.read_bytes() for p in f.project.rglob('*') if p.is_file()}
def original():assert not file.exists() and all(p.read_bytes()==v for p,v in snapshot.items())
def panel():return f.page.locator('.window[data-key=declaration]')
def reopen():
 f.idle()
 if panel().locator('[data-enum-definition]').is_visible():return
 f.page.locator('#workspace').click(button='right',position={'x':1300,'y':200});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]');b.locator('[data-tab=info]').click();b.locator('[data-browser-control=object-query]').fill('NewMood');b.locator('[data-browser-control=object-search]').click();b.locator('[data-object="'+owner+'"]').press('F2');b.locator('[data-close]').first.click();expect(panel().locator('[data-enum-definition]')).to_be_visible()
try:
 f.start(0);f.invoke('select',dict(id=f.id));f.invoke('saveDraft',{})
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size(dict(width=1900,height=1400))
  f.page.locator('#workspace').click(button='right',position={'x':1300,'y':200});f.page.locator('[data-workspace-create-menu]').click();f.page.locator('[data-workspace-create=Enum]').click();d=f.page.get_by_role('dialog',name='새 종류 만들기',exact=True);expect(d).to_be_visible();d.locator('#new-declaration-name').fill('NewMood');d.locator('#new-declaration').click();f.idle();expect(panel().locator('[data-enum-definition]')).to_be_visible();assert f.state()['draft']['kind']=='enum';original();f.checked('원본 작업실 종류 만들기는 별도 enum 정의와 프로젝트 등록 초안을 만들고 실행 enum이나 파일을 생성하지 않는다')
  panel().locator('[data-enum-add]').click();r=panel().locator('[data-enum-value]').first;id=r.get_attribute('data-enum-value');r.locator('[data-enum-name]').fill('새 종류 선택');r.locator('[data-enum-name]').press('Tab');panel().locator('[data-declaration-header-action=save]').click();f.idle();original();f.pending();f.page.close();f.stop();f.start(1);f.page=f.setup();f.page.set_viewport_size(dict(width=1900,height=1400));reopen();r=panel().locator('[data-enum-value="'+id+'"]');expect(r.locator('[data-enum-name]')).to_have_value('새 종류 선택');original();f.checked('새 종류·항목의 Save와 재시작은 동일한 정의·항목 ID·등록 그룹을 보존하며 Confirm 전 원본을 유지한다')
  if mode=='cancel':
   mark=len(f.traffic);panel().locator('[data-declaration-header-action=discard]').click();f.idle();original();assert all(u['id']!=owner for u in f.state()['units']);assert not [v['result'] for v in f.traffic[mark:] if 'result' in v and not v['result'].get('ok')];f.checked('새 종류 변경 취소는 미확정 항목과 등록 그룹을 함께 되돌리고 기존 원본을 유지한다');f.browser.close();raise SystemExit(0)
  panel().locator('[data-declaration-header-action=confirm]').click();review=f.page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=120000);review.locator('[data-reject]').click();expect(review).to_be_hidden();original();panel().locator('[data-declaration-header-action=confirm]').click();expect(review).to_be_visible(timeout=120000)
  if review.locator('[data-review-advanced]').count():
   review.locator('[data-review-advanced]').click()
   if review.locator('[data-advanced-reviewed]').count():review.locator('[data-advanced-reviewed]').check()
  expect(review.locator('#confirm')).to_be_enabled(timeout=120000);review.locator('#confirm').click();expect(review).to_be_hidden(timeout=120000);f.idle();assert file.exists() and file.read_text().startswith('enum '+owner);assert {p.name for p,v in snapshot.items() if p.read_bytes()!=v}=={'project.cproj'};assert not f.errors and not f.external;f.checked('명시 compiler Confirm은 새 종류 파일과 대응 등록만 함께 반영하고 기존 함수·본문·원본을 보존한다');f.page.screenshot(path=str(f.case/'information-enum-created.png'));f.browser.close()
except Exception:
 try:(f.case/'enum-create-failure.json').write_text(json.dumps(dict(state=f.state(),traffic=f.traffic[-90:],errors=f.errors),ensure_ascii=False,indent=2)+'\n')
 except Exception:pass
 try:f.page.screenshot(path=str(f.case/'enum-create-failure.png'),timeout=5000)
 except Exception:pass
 raise
finally:
 f.stop();(f.case/'information-enum-create-evidence.json').write_text(json.dumps(dict(checks=f.checks,actualWindows=False,actualMobile=False),ensure_ascii=False,indent=2)+'\n')
print('EVIDENCE',f.case,flush=True)
