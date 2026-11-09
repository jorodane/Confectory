"""One authored information Save: owner presentation and unchanged native bodies."""
import copy,json,time
import v666_native_callers_fixture as _prior
for _key in dir(_prior):
 if not _key.startswith('_'):globals()[_key]=getattr(_prior,_key)
description='정보 설명 · 두 본문과 함께 저장 9223372036854775806 😀'
icon='▣'
def request():
 r=_prior.request();r['changes'].insert(1,dict(type='description',text=description));r['changes'].append(dict(type='icon',text=icon));return r
def verify_presentation(text):
 info=f.metadata('inspect',text=text);assert info['description']==description and info['values']['editorIcon']==icon,info
def verify_rows(rows):
 _prior.verify_rows(rows);verify_presentation(rows[owner]['draft'])
def verify(checkpoint):
 group=_prior.verify(checkpoint);rows={r['id']:r for r in json.loads(checkpoint.read_text())['changes']};verify_presentation(rows[owner]['draft']);return group
def verify_live():
 _prior.verify_live();path=next(row['path']for row in f.metadata('describe',project=str(f.manifest))['units']if row['id']==owner);verify_presentation((f.project/path).read_text());f.checked('owner description/icon and both explicit C# bodies confirm together; original caller bytes/contracts/exact64 remain intact')
def after_contract(index):
 _prior.after_contract(index)
 if index==0:
  from playwright.sync_api import expect
  f.owner().locator('.object-title-description').fill(description);f.idle();held=d.pending()
  f.owner().locator('.object-icon-edit').click();dialog=f.page.locator('.object-icon-popover');expect(dialog).to_be_visible();dialog.locator('[data-icon-choice="'+icon+'"]').click();dialog.locator('[type=submit]').click();expect(dialog).to_have_count(0);f.idle();saved=d.pending();assert len(saved)==3 and len(held)==2
  f.owner().locator('.object-icon-edit').press('Control+z');assert d.pending()==held
  f.owner().locator('.object-icon-edit').press('Control+y');assert d.pending()==saved
  f.page.screenshot(path=str(f.case/'owner-presentation-and-bodies.png'));f.checked('original 460px header description and icon join explicit body drafts; icon Undo/Redo retains all unrelated input')
 if index==1 and mode=='reproduce-header-ui':
  saved=d.pending();assert len(saved)==4
  checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));baseline=checkpoint.read_bytes();mark=len(f.traffic);f.owner().locator('[data-element-action=save]').click();deadline=time.monotonic()+60
  while time.monotonic()<deadline:
   ids={row['invoke']['requestId']for row in f.traffic[mark:]if row.get('invoke',{}).get('endpoint')=='blueprint'and row['invoke']['input'].get('action')=='applySlots'};replies=[row['result']for row in f.traffic[mark:]if row.get('result',{}).get('requestId')in ids]
   if replies:assert replies[-1]['ok']is False;break
   f.page.wait_for_timeout(20)
  else:raise AssertionError('No observed mixed applySlots response')
  assert d.pending()==saved and checkpoint.read_bytes()==baseline;unchanged();f.checked('published single Save rejects header presentation with two valid native bodies; all four inputs and original checkpoint/source retained');f.browser.close();raise SystemExit(0)
