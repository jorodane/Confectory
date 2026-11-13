"""A new draft field keeps its stable identity during consecutive type Undo/Redo."""
import json
from playwright.sync_api import sync_playwright,expect
import v536_field_definitions_ui as d
f=d.f;owner=d.owner;trace=[]
def focus():return f.page.evaluate('({tag:document.activeElement?.tagName,window:document.activeElement?.closest(".window")?.dataset.key,draft:document.activeElement?.closest("[data-definition-key]")?.dataset.definitionKey,type:document.activeElement?.matches("[data-property-type]")})')
try:
 f.start(0);f.invoke('select',dict(id=owner));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));baseline=checkpoint.read_bytes()
 with sync_playwright()as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size(dict(width=2300,height=1700));d.open_info();assert not d.pending();f.owner().locator('[data-schema-add]').click();row=f.owner().locator('[data-definition-key]').last;key=row.get_attribute('data-definition-key');row.locator('[data-property-name]').fill('연속 타입 😀');row.locator('[data-property-value]').fill('7');before=d.pending();assert len(before)==1
  d.choose(row.locator('[data-property-type]'),'general','double');planned=d.pending();assert len(planned)==1 and before!=planned;host=f.owner().get_attribute('data-key');row=f.owner().locator('[data-definition-key]').filter(has=f.page.locator('[data-property-name]')).last;button=row.locator('[data-property-type]');button.focus()
  for undo,redo in [('Control+z','Control+y'),('Control+z','Control+Shift+z'),('Control+z','Control+y')]:
   f.page.keyboard.press(undo);assert d.pending()==before;one=focus();f.page.keyboard.press(redo);two=focus();trace.append(dict(undo=one,redo=two,keys=[undo,redo]));(f.case/'draft-focus-chain.json').write_text(json.dumps(dict(key=key,before=before,planned=planned,trace=trace),ensure_ascii=False,indent=2))
   if d.mode=='reproduce-focus':assert one['tag']=='BODY'and two['tag']=='BODY'and d.pending()==before;f.originals();assert checkpoint.read_bytes()==baseline;f.checked('published draft type Undo loses focus and consecutive Redo cannot restore the original draft selection; source/checkpoint retained');f.browser.close();raise SystemExit(0)
   assert d.pending()==planned
   for current in [one,two]:assert current['type']and current['window']==host and current['draft']==key,current
   expect(button).to_be_focused()
  f.checked('draft field type Undo/Redo restores its exact stable definition key and same owner without another pointer/focus action; name/default/native identity preserved')
  f.owner().locator('[data-element-action=discard]').click();expect(f.owner().locator('[data-definition-key]')).to_have_count(0);assert not d.pending()and checkpoint.read_bytes()==baseline;f.originals();f.page.unroute_all(behavior='wait');f.page.close();f.stop();f.start(1);f.page=f.setup();f.page.set_viewport_size(dict(width=2300,height=1700));d.open_info();assert not d.pending()and checkpoint.read_bytes()==baseline;f.originals();f.checked('explicit draft cancellation and cold reopen preserve the original fields/defaults/source and do not restore the cancelled draft');f.browser.close()
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
