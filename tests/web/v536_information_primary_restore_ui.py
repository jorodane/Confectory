"""A stale primary property layout is presentation, not a failed schema read."""
import json
from playwright.sync_api import sync_playwright,expect
import v536_information_nested_fixture as x
f,d=x.f,x.d
try:
 f.start(0);f.invoke('select',{'id':x.owner});f.invoke('saveDraft',{})
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700});d.open_info();f.owner().locator('.object-title-description').fill('복원 뒤 정보 입력');held=d.pending()
  f.page.locator('#workspace').click(button='right',position={'x':900,'y':400});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]');b.locator('[data-tab=feature]').click();b.locator('[data-object="'+x.caller+'"]').press('Enter');f.idle();f.page.locator('.window[data-key=declaration] [data-function-write-direct]').click();f.idle();assert f.state()['draft']['id']==x.caller;f.pending();f.page.close();f.stop();f.start(1);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700});f.idle()
  status=f.page.locator('#status').text_content();(f.case/'primary-restore-observation.json').write_text(json.dumps({'status':status,'selection':f.state()['draft']['id'],'schema':f.state().get('schema'),'pendingPreserved':d.pending()==held},ensure_ascii=False,indent=2));assert status!='Schema unavailable',status
  assert f.state()['draft']['id']==x.caller and d.pending()==held;expect(f.page.locator('.window[data-key=blueprint] [data-bp-node=left]')).to_be_visible()
  f.page.get_by_role('tab',name='Workspace',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]');expect(b).to_have_count(1);b.locator('[data-tab=info]').click();b.locator('[data-browser-control=object-query]').fill('FreeInfo');b.locator('[data-browser-control=object-search]').click();b.locator('[data-object="'+x.owner+'"]').press('Enter');expect(f.owner().locator('.object-title-description')).to_have_value('복원 뒤 정보 입력');assert d.pending()==held;assert all((f.project/p).read_bytes()==v for p,v in x.snapshot.items());assert not f.errors and not f.external
  f.checked('없는 primary schema를 배경 복원 성공/실패로 표시하지 않고 현재 함수와 입력을 유지하며 정보 재열기로 원래 입력을 복원한다');f.page.screenshot(path=str(f.case/'primary-restored.png'));f.browser.close()
except Exception:
 try:(f.case/'failure.json').write_text(json.dumps({'traffic':f.traffic[-40:],'state':f.state()},ensure_ascii=False,indent=2));f.page.screenshot(path=str(f.case/'primary-failure.png'))
 except Exception:pass
 raise
finally:
 f.stop();print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngineRenderer':True,'nativeWindows':False},ensure_ascii=False))
