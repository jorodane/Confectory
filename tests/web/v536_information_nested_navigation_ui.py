"""Original private breadcrumbs retain qualified source and unrelated window input."""
import json
from playwright.sync_api import sync_playwright,expect
import v536_information_nested_fixture as x
f,d=x.f,x.d

def author():return f.page.locator('.window[data-key=blueprint]')
def inspector():return f.page.locator('.bp-flow-inspector:not([hidden])')
def enter(node):
 f.idle();author().locator('[data-flow-node="'+node+'"]').click();inspector().locator('[data-flow-internal]').click();expect(author().locator('[data-flow-parent]')).to_be_visible();f.idle()
def source(name):
 author().locator('[data-flow-node=body]').click();inspector().locator('[data-flow-code]').click();dialog=f.page.locator('.bp-script-dialog')
 assert x.record_sources[name].replace('\r\n','\n') in dialog.locator('[data-code-source]').input_value();dialog.locator('[data-code-cancel]').click();inspector().locator('[data-flow-done]').click();f.idle()
try:
 f.start(0);f.invoke('select',{'id':x.owner});f.invoke('saveDraft',{})
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700});d.open_info();f.owner().locator('.object-title-description').fill('다른 정보 입력을 보존');held=d.pending()
  f.page.locator('#workspace').click(button='right',position={'x':1000,'y':300});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]');b.locator('[data-tab=feature]').click();b.locator('[data-object="'+x.caller+'"]').press('Enter');f.page.locator('.window[data-key=declaration] [data-function-write-direct]').click();expect(author().locator('[data-bp-node=left]')).to_be_visible();f.page.set_viewport_size({'width':390,'height':844});enter('left');source('left');assert d.pending()==held
  author().locator('[data-flow-parent]').click();expect(author().locator('[data-flow-node=right]')).to_be_visible();enter('right');enter('deep');source('right');assert d.pending()==held
  f.page.screenshot(path=str(f.case/'private-navigation.png'));f.pending();f.page.close();f.stop();f.start(1);f.page=f.setup();f.page.set_viewport_size({'width':390,'height':844});expect(author().locator('[data-flow-node=body]')).to_be_visible();f.idle();source('right');assert d.pending()==held
  author().locator('[data-flow-parent]').click();expect(author().locator('[data-flow-node=deep]')).to_be_visible();author().locator('[data-flow-parent]').click();expect(author().locator('[data-flow-node=left]')).to_be_visible();enter('left');source('left');assert d.pending()==held
  assert all((f.project/p).read_bytes()==v for p,v in x.snapshot.items());assert not f.errors and not f.external
  f.checked('원본 내부 흐름·상위/깊이2 재진입·폭 전환·cold는 동명 leaf source와 다른 정보 입력을 분리 보존한다');f.browser.close()
finally:
 f.stop();print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngineRenderer':True,'nativeWindowsOrMobile':False,'projectRun':False},ensure_ascii=False))
