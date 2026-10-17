"""Real pointer/click cancellation and invalid-target preservation within existing route contracts."""
from playwright.sync_api import expect

def verify_pin_gestures(page,panel,read):
 root=panel();root.locator('[data-bp-fit]').click();baseline=read()['sources'];issues=[]
 def choose():
  panel().locator('[data-bp-select="selector"]').click()
  return panel().locator('[data-bp-route="case:next"]')
 def port():return panel().locator('[data-bp-exec-out="selector"][data-exec-port="case:next"]')
 def reset(field):field.locator('..').locator('[data-reset]').click()
 # A drag dropped on unused canvas is cancelled. A click still starts click-to-connect.
 choose();a=port().bounding_box();viewport=panel().locator('.bp-scroll');blank=viewport.bounding_box();x=blank['x']+blank['width']-15;y=blank['y']+blank['height']-15
 assert viewport.evaluate('(el)=>{const r=el.getBoundingClientRect();return !document.elementFromPoint(r.right-15,r.bottom-15)?.closest("[data-bp-exec-target]")}')
 page.mouse.move(a['x']+a['width']/2,a['y']+a['height']/2);page.mouse.down();page.mouse.move(x,y,steps=10);page.mouse.up()
 if port().get_attribute('aria-pressed')!='false' or panel().locator('.bp-wire-preview').count():issues.append('blank drag retained a pending execution wire')
 page.keyboard.press('Escape')
 # A branch clause cannot target the main region. Do not turn rejection into unlink.
 field=choose();expect(field).to_have_value('case_work');port().click();panel().locator('[data-bp-exec-in="condition"]').click()
 if field.input_value()!='case_work':issues.append('invalid branch target replaced existing route input with empty value')
 reset(field);page.keyboard.press('Escape')
 field=choose();field.select_option('return:selector');port().click();panel().locator('[data-bp-exec-in="condition"]').click()
 if field.input_value()!='return:selector':issues.append('invalid target destroyed retained unsubmitted route input')
 reset(field);page.keyboard.press('Escape')
 # The same rule protects the function entry from a branch-only target.
 entry=panel().locator('[data-bp-entry]');expect(entry).to_have_value('selector');panel().locator('[data-bp-exec-start]').click();panel().locator('[data-bp-exec-in="case_work"]').click()
 if entry.input_value()!='selector':issues.append('invalid entry target became an empty start connection')
 reset(entry);page.keyboard.press('Escape')
 assert read()['sources']==baseline,'pointer-only checks changed shared source'
 if issues:
  page.screenshot(path='/tmp/confectory-v480-pin-gestures-before.png',full_page=True)
  raise AssertionError('; '.join(issues))
 # Valid click/drag staging and explicit Apply remain available after a refusal.
 field=choose();field.select_option('return:selector');port().click();panel().locator('[data-bp-exec-in="condition"]').click();expect(field).to_have_value('return:selector');expect(port()).to_have_attribute('aria-pressed','true');panel().locator('[data-bp-exec-in="case_work"]').click();expect(field).to_have_value('case_work');expect(port()).to_have_attribute('aria-pressed','false');reset(field)
 entry=panel().locator('[data-bp-entry]');panel().locator('[data-bp-exec-start]').click();panel().locator('[data-bp-exec-in="case_work"]').click();expect(entry).to_have_value('selector');panel().locator('[data-bp-exec-in="condition"]').click();expect(entry).to_have_value('condition');reset(entry)
 field=choose();port().click();panel().locator('[data-bp-exec-in="case_work"]').click();expect(field).to_have_value('case_work');reset(field)
 source=panel().locator('[data-bp-exec-out="selector"][data-exec-port="next"]');source.drag_to(panel().locator('[data-bp-exec-in="condition"]'));field=panel().locator('[data-bp-route="next"]');expect(field).to_have_value('condition');reset(field)
 assert read()['sources']==baseline;page.keyboard.press('Escape');expect(panel().locator('.bp-wire-preview')).to_have_count(0)
 page.screenshot(path='/tmp/confectory-v480-pin-gestures.png',full_page=True)
 print('PASS actual v480 pin blank-drop cancellation, invalid case/entry target and retained input preservation; valid click/drag unchanged',flush=True)

def verify_output_sidebar(page,panel,meta,read):
 baseline=read()['sources'];separator=panel().get_by_role('separator',name='출력 영역 너비',exact=True);toggle=panel().get_by_role('button',name='출력 사이드바 접기',exact=True);expect(separator).to_have_count(1)
 separator.press('Home');expect(separator).to_have_attribute('aria-valuenow','120');separator.press('ArrowLeft');expect(separator).to_have_attribute('aria-valuenow','136');separator.press('End');assert 120<=float(separator.get_attribute('aria-valuenow'))<=420
 separator.press('Home');width=120;outer=panel().locator('.bp-output').evaluate('el=>el.getBoundingClientRect().width/el.offsetWidth');box=separator.bounding_box();x=box['x']+box['width']/2;y=box['y']+box['height']/2
 page.mouse.move(x,y);page.mouse.down();page.mouse.move(x-48,y,steps=6);page.mouse.up();expected=min(float(separator.get_attribute('aria-valuemax')),width+48/outer);assert abs(float(separator.get_attribute('aria-valuenow'))-expected)<1
 before=meta()['blueprintOutputWidth'];box=separator.bounding_box();x=box['x']+box['width']/2;y=box['y']+box['height']/2;page.mouse.move(x,y);page.mouse.down();page.mouse.move(x-25,y,steps=4);page.keyboard.press('Escape');page.mouse.up();assert abs(meta()['blueprintOutputWidth']-before)<.01
 separator.press('Home')
 for _ in range(9):separator.press('ArrowLeft')
 expect(separator).to_have_attribute('aria-valuenow','264');exit_field=panel().locator('[data-bp-exit="fallback"]');original=exit_field.input_value();exit_field.fill('{"constant":77}');toggle.click();expect(panel().locator('.bp-output-content')).to_be_hidden();assert panel().locator('.bp-output').evaluate('el=>el.offsetWidth')==36;assert meta()['blueprintOutputCollapsed'] is True
 panel().get_by_role('button',name='출력 사이드바 펼치기',exact=True).click();expect(exit_field).to_have_value('{"constant":77}');exit_field.locator('..').locator('[data-reset]').click();expect(exit_field).to_have_value(original);assert meta()['blueprintOutputWidth']==264 and meta()['blueprintOutputCollapsed'] is False
 assert read()['sources']==baseline;page.screenshot(path='/tmp/confectory-v480-output-sidebar.png',full_page=True)
 print('PASS actual v480 output sidebar pointer/keyboard bounds, outer zoom, Escape and retained hidden input; source unchanged',flush=True)
