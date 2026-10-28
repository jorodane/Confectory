"""Existing object module UI under v536 navigation; real isolated engine, no run/account."""
import json
from playwright.sync_api import sync_playwright,expect
import v536_wide_mixed as f
owner=f.n+'Monster'
def pending():return [(k,v) for k,v in f.pending()['schema'] if '|'+owner+'|element|' in k]
def card(name):return f.owner().locator('[data-behavior-source="'+f.n+name+'"]')
try:
 f.start(0);f.invoke('select',{'id':owner});f.invoke('saveDraft',{})
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':1600,'height':1300});f.open_owner(owner);expect(card('Rules').locator('[data-module-method]')).to_have_count(2);before=f.state()['draft']['text'];f.originals()
  card('Rules').locator('[data-behavior-unlink]').click();expect(card('Rules')).to_have_count(0);assert pending()[0][1]['value']==[];f.owner().locator('[data-element-action=discard]').click();expect(card('Rules').locator('[data-module-method]')).to_have_count(2);assert not pending() and f.state()['draft']['text']==before;f.originals();f.checked('기존 객체 모듈 해제·취소는 두 기능 계약과 own provide/부모/typed 값을 복원한다')
  button=f.owner().locator('[data-module-link]');button.scroll_into_view_if_needed();f.page.evaluate('()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))');button.click();f.page.get_by_role('dialog',name='모듈 연결',exact=True).locator('[data-link-id="'+f.n+'Extra"]').click();expect(card('Extra')).to_be_visible();f.owner().locator('[data-own-functions-toggle]').focus();f.page.keyboard.press('Control+z');expect(card('Extra')).to_have_count(0);f.page.keyboard.press('Control+Shift+z');expect(card('Extra')).to_be_visible();f.checked('동일 원본 module picker의 객체 private Undo/Redo는 기존 Rules와 provider를 유지한다')
  f.owner().locator('[data-element-action=save]').click()
  for _ in range(240):
   if not pending() and not [v for _,v in f.pending()['blueprint'] if v.get('kind')=='owner-attempt' and v.get('owner')==owner]:break
   f.page.wait_for_timeout(100)
  else:raise AssertionError('object module save did not settle')
  f.originals();assert 'module '+f.n+'Extra;' in f.state()['draft']['text'];assert 'provide '+f.n+'Slot with '+f.n+'AliasBody;' in f.state()['draft']['text'];f.pending();f.page.close();f.stop();f.start(1);f.page=f.setup();expect(card('Extra')).to_be_visible();expect(card('Rules').locator('[data-module-method]')).to_have_count(2);f.page.wait_for_function('()=>typeof confectoryFlushPresentation==="function"');assert not pending();f.originals();f.checked('기존 객체의 원자적 Save/cold는 module 두 개와 provider를 보관하며 source를 자동 확정하지 않는다');assert not f.errors and not f.external,(f.errors,f.external);f.browser.close()
except Exception:
 try:f.page.screenshot(path=str(f.case/'object-module-regression-failure.png'))
 except Exception:pass
 print('EVIDENCE '+str(f.case),flush=True);raise
finally:f.stop()
print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngine':True,'nativeWindows':False,'accountOrInference':False},ensure_ascii=False))
