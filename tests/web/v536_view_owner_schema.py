"""Detached schema display-name candidate, exact value and compiler group scope."""
import json
from playwright.sync_api import sync_playwright,expect
import v536_view_owner_ui as u
f=u.f
(f.project/'Local.celem').write_text('schema '+f.n+'Local {field Mana single general long;field Other single general string;}')
f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element Local schema "Local.celem";registry Confectory.Build.DotNet'))
p=f.project/'Slime.celem';p.write_text(p.read_text().replace('{','{use schema '+f.n+'Local;data Mana=9223372036854775806;data Other="남길 값";',1))
f.original={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file()}
def field(slot,path):return u.window(slot).locator('[data-property-path=\''+json.dumps(path,separators=(',',':'))+'\']')
try:
 f.start(0);f.invoke('select',{'id':f.id});f.invoke('saveDraft',{})
 with sync_playwright() as pw,u.cleanup():
  f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1400});expect.set_options(timeout=60000);u.open_two();name=field('1',['Mana']).locator('[data-property-name]');expect(name).to_be_editable();u.description('2').fill('다른 창 입력');held=u.cells('2');checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();name.fill(' ');u.rejected('1');assert checkpoint.read_bytes()==before and u.cells('2')==held;expect(field('1',['Mana']).locator('[data-property-name]')).to_have_value(' ');f.originals();f.checked('독립 창의 불완전 schema 이름 Save는 전체 미적용이며 원문/다른 창 입력을 보존한다')
  name=field('1',['Mana']).locator('[data-property-name]');name.press('Escape');name.fill('마나 한글');u.window('1').locator('[data-element-action=save]').click();u.saved();expect(field('1',['Mana']).locator('[data-property-name]')).to_have_value('마나 한글');expect(field('1',['Mana']).locator('[data-property-value]')).to_have_value('9223372036854775806');assert u.cells('2')==held;f.originals();u.restart(1);expect(field('1',['Mana']).locator('[data-property-name]')).to_have_value('마나 한글');expect(u.description('2')).to_have_value('다른 창 입력');f.checked('독립 창 schema-only Save/cold는 stable key/raw64와 다른 창 입력을 유지하고 자기 schema 이름만 보관한다')
  mark=len(f.traffic);u.window('1').locator('[data-element-action=confirm]').click();dialog=f.page.get_by_role('dialog',name='관련 변경 검토',exact=True);expect(dialog).to_be_visible();dialog.locator('#review-creation').click();expect(f.page.locator('#status')).to_contain_text('미적용 입력을 먼저 적용');assert u.cells('2')==held and not [t for t in f.traffic[mark:] if t.get('invoke',{}).get('endpoint')=='reviewGroup'];f.originals();dialog.get_by_role('button',name='닫기',exact=True).click();u.window('2').locator('[data-element-action=discard]').click();f.idle();assert not u.cells('2');expect(field('2',['Mana']).locator('[data-property-name]')).to_have_value('마나 한글');f.checked('같은 owner의 peer 미적용 입력은 공동 Review를 차단·보존하고 명시 local 취소는 저장된 schema를 되돌리지 않는다')
  r=u.review();r.locator('[data-reject]').click();expect(r).to_be_hidden();f.originals();r=u.review()
  if r.locator('[data-review-advanced]').count():
   r.locator('[data-review-advanced]').click()
   if r.locator('[data-advanced-reviewed]').count():r.locator('[data-advanced-reviewed]').check()
  r.locator('#confirm').click();expect(r).to_have_count(0,timeout=120000);f.idle();assert {k for k,v in f.original.items() if (f.project/k).read_bytes()!=v}=={'Local.celem'};u.restart(2);expect(field('1',['Mana']).locator('[data-property-name]')).to_have_value('마나 한글');expect(field('1',['Other']).locator('[data-property-value]')).to_have_value('남길 값');assert not u.cells('2');assert not f.errors and not f.external,(f.errors,f.external);f.checked('독립 창 schema-only Review취소/명시 compiler Confirm/cold는 schema 파일만 반영하고 owner/부모/다른 값을 보존한다')
except Exception:
 try:f.case.joinpath('view-schema-failure.json').write_text(json.dumps({'state':f.state(),'traffic':f.traffic[-50:]},ensure_ascii=False,indent=2))
 except Exception:pass
 print('EVIDENCE '+str(f.case),flush=True);raise
finally:f.stop()
print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngine':True,'renderer':True,'nativeWindows':False,'accountOrInference':False},ensure_ascii=False))
