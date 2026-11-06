"""General Blueprint readonly completion cannot undo an explicit window close."""
import json,sys,time,traceback
from playwright.sync_api import sync_playwright,expect
import v536_wide_mixed as f
mode=sys.argv[3];paused={};ids=set();reads=[];releases=[]
def open_native():
 f.page.locator('#workspace').click(button='right',position={'x':700,'y':300});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]');b.get_by_role('button',name='기능',exact=True).click();b.locator('[data-browser-control="object-query"]').fill('Slot');b.locator('[data-browser-control="object-search"]').click();f.idle();b.locator('[data-object="'+f.n+'Slot"]').click(button='right');f.page.get_by_role('button',name='기능 Blueprint',exact=True).click();expect(f.author().locator('.bp-scroll')).to_be_visible();b.locator('[data-close]').first.click();f.idle()
def hold(route):
 body=route.request.post_data_json
 if body.get('op')=='invoke'and body.get('endpoint')=='blueprint'and body.get('input',{}).get('action')=='read':ids.add(body['requestId']);reads.append(body)
 response=route.fetch();data=response.json()
 if not paused and any(row.get('requestId')in ids and row.get('ok')for row in data.get('results',[])):
  paused.update(route=route,response=response,data=data);return
 route.fulfill(response=response,json=data)
def release(failure=False):
 data=paused['data']
 if failure:
  for row in data.get('results',[]):
   if row.get('requestId')in ids:row['ok']=False;row['error']={'code':'transport-interrupted'};row.pop('result',None)
 paused['route'].fulfill(response=paused['response'],json=data);f.page.unroute('**/api/request',hold);releases.append({'failedReply':failure,'requests':len(reads)});paused.clear();ids.clear()
def close_during_read(failure=False):
 f.page.route('**/api/request',hold);f.author().locator('[data-bp-read]').click()
 end=time.monotonic()+20
 while not paused and time.monotonic()<end:f.page.wait_for_timeout(30)
 assert paused,'read completion was not held';f.author().locator('[data-close]').first.click();expect(f.author()).to_be_hidden();release(failure);f.idle()
 if mode=='baseline':
  expect(f.author()).to_be_visible();f.checked('published general Blueprint read completion reopens the floating window after the user explicitly closes it');return
 expect(f.author()).to_be_hidden();expect(f.page.locator('#chat-input')).to_have_value('읽기 중 닫아도 보존할 입력 😀');f.originals();f.checked('held '+('failed'if failure else'successful')+' read completion preserves explicit Close, private input and physical sources')
def guards():
 f.originals();assert not f.errors and not f.external,(f.errors,f.external)
 forbidden={'editDraft','saveDraft','reviewDraft','confirmDraft','confirm','confirmGroup','authorBatch','edit','runProject','startAI'}
 assert not forbidden.intersection(r.get('invoke',{}).get('endpoint')for r in f.traffic)
try:
 f.start(0)
 with sync_playwright()as p:
  try:
   expect.set_options(timeout=60000);f.browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':1600,'height':1100});open_native();f.page.locator('#chat-input').fill('읽기 중 닫아도 보존할 입력 😀');f.author().locator('[data-bp-percent]').click();dialog=f.page.get_by_role('dialog',name='노드 화면 배율',exact=True);dialog.locator('[data-zoom-preset="300"]').click();dialog.locator('[data-zoom-value]').press('Escape');f.page.evaluate('()=>confectoryFlushPresentation()')
   for i in range(1 if mode=='baseline'else 3):
    close_during_read(mode=='failure'and i!=1)
    if mode!='baseline':
     open_native();expect(f.author().locator('[data-bp-percent]')).to_have_text('300%');guards();f.checked('next explicit open of the retained hidden window reads the current source and restores the same accepted 300% camera')
   if mode!='baseline':
    f.page.evaluate('()=>confectoryFlushPresentation()');f.page.close();f.stop();f.start(1);f.page=f.setup();f.page.set_viewport_size({'width':1600,'height':1100});expect(f.author().locator('[data-bp-percent]')).to_have_text('300%');expect(f.author().locator('.bp-scroll')).to_have_count(0);expect(f.page.locator('#chat-input')).to_have_value('읽기 중 닫아도 보존할 입력 😀');f.author().locator('[data-bp-read]').click();expect(f.author().locator('.bp-scroll')).to_be_visible();expect(f.author().locator('[data-bp-percent]')).to_have_text('300%');f.checked('cold restores private layout/input without replaying the pending read; explicit source observation reconnects the same owned Blueprint')
   guards();f.page.screenshot(path=str(f.case/('native-read-close-'+mode+'.png')));f.browser.close()
  except Exception as e:
   try:f.page.screenshot(path=str(f.case/'failure.png'));(f.case/'failure.html').write_text(f.page.content())
   except Exception:pass
   (f.case/'failure.json').write_text(json.dumps(dict(error=repr(e),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:
 f.stop();(f.case/'native-read-close.json').write_text(json.dumps(dict(checks=f.checks,errors=f.errors,reads=reads,releases=releases,actualEngine=True,actualWindows=False,actualMobile=False),ensure_ascii=False,indent=2))
print('NATIVE_READ_CLOSE_FIXTURE',f.case,flush=True)
