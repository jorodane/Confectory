"""Original detached object windows use one candidate; peer input is never cancelled."""
import contextlib,json,pathlib,sys,time
from playwright.sync_api import sync_playwright,expect
import v536_wide_mixed as f
mode=sys.argv[3] if len(sys.argv)>3 else 'normal'
def window(slot):return f.page.locator('.window[data-key="editor-'+slot+'"]')
def power(slot):return window(slot).locator('[data-property-path=\'["Combat","Power"]\'] [data-property-value]')
def description(slot):return window(slot).locator('.object-title-description')
def pending():return f.pending()
def cells(slot):return [(k,v) for k,v in pending()['schema'] if '|'+f.id+'|view:'+slot+'|element|' in k]
def journal(slot):return [(k,v) for k,v in pending()['blueprint'] if k.endswith('|v536-view-owner-attempt|'+slot+'|'+f.id)]
def saved():
 for _ in range(180):
  if not cells('1') and not journal('1'):f.idle();return
  f.page.wait_for_timeout(100)
 raise AssertionError((window('1').locator('[data-element-error]').all_text_contents(),pending()))
def restart(i):
 pending();f.page.unroute_all(behavior='wait');f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1400});expect(power('1')).to_be_visible(timeout=60000);expect(power('2')).to_be_visible();f.idle()
def rejected(slot):
 f.page.evaluate('''()=>{globalThis.boundaryMessages=[];globalThis.boundaryObserver=new MutationObserver(()=>{for(const e of document.querySelectorAll('[data-element-error],#status'))if(e.textContent&&!boundaryMessages.includes(e.textContent))boundaryMessages.push(e.textContent)});boundaryObserver.observe(document.body,{subtree:true,childList:true,characterData:true})}''');window(slot).locator('[data-element-action=save]').click();f.page.wait_for_function('()=>boundaryMessages.some(s=>/입력.*유지|바뀌|실패|완료하지|consumer_error|stale|changed|형식/.test(s))');f.page.evaluate('()=>boundaryObserver.disconnect()');f.idle()
def open_two():
 f.page.locator('#workspace').click(button='right',position={'x':80,'y':100});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]');b.locator('[data-browser-control="object-query"]').fill('Slime');b.locator('[data-browser-control="object-search"]').click();row=b.locator('[data-object="'+f.id+'"]');expect(row).to_be_visible()
 for slot,x in [('1',900),('2',1400)]:
  row.click(button='right',position={'x':8,'y':8});f.page.locator('.context-menu').get_by_role('button',name='새 창으로 열기',exact=True).click();w=window(slot);expect(w.locator('.object-title-name')).to_have_text('Slime');head=w.locator('.object-title-name').bounding_box();box=w.bounding_box();f.page.mouse.move(head['x']+5,head['y']+5);f.page.mouse.down();f.page.mouse.move(x+head['x']-box['x']+5,140+head['y']-box['y']+5,steps=12);f.page.mouse.up();f.idle()
 b.locator('[data-close]').first.click();f.idle()
def view(slot):return next(r for r in f.state()['editorViews'] if r['view']==slot)
def verify_peer():expect(power('2')).to_have_value('9223372036854775806');expect(description('2')).to_have_value('둘째 창 입력')
@contextlib.contextmanager
def cleanup():
 try:yield
 finally:
  if getattr(f,'page',None) and not f.page.is_closed():f.page.unroute_all(behavior='wait')
  if getattr(f,'browser',None):f.browser.close()
def review():
 window('1').locator('[data-element-action=confirm]').click();r=f.page.locator('.window[data-key=review]');f.page.wait_for_function('()=>document.querySelector("#review-creation")||[...document.querySelectorAll(".window[data-key=review]")].some(e=>!e.hidden&&e.getClientRects().length)')
 if f.page.locator('#review-creation').count():f.page.locator('#review-creation').click()
 expect(r).to_be_visible();return r
def main():
 try:
  f.start(0);f.invoke('select',{'id':f.id});f.invoke('saveDraft',{})
  with sync_playwright() as pw,cleanup():
   f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1400});expect.set_options(timeout=60000);open_two();description('1').fill('첫 창 원자 저장');power('1').fill('9223372036854775805');description('2').fill('둘째 창 입력');power('2').fill('9223372036854775806');held=cells('2');before_native=view('1')['draft']['text'];checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();f.originals();f.checked('원본 새 창 메뉴의 두 실제 요소 창에 한글/정확한 raw64 입력을 독립 보관한다')
   if mode=='cancel':
    d=f.state()['schema'];f.invoke('schema',{'id':f.id});d=f.state()['schema'];f.invoke('editDescription',{'id':f.id,'revision':d['revision'],'hash':d['textHash'],'value':'다른 편집자의 미저장 변경'});native=view('1')['draft']['text'];window('1').locator('[data-element-action=discard]').click();f.idle();assert view('1')['draft']['text']==native and checkpoint.read_bytes()==before;verify_peer();assert cells('2')==held;f.originals();restart(1);verify_peer();assert not cells('1');f.checked('창의 명시 취소는 peer의 공유 미저장 변경과 다른 창 입력을 되돌리지 않으며 cold에 취소 입력을 되살리지 않는다')
   else:
    if mode=='storage':
     checkpoint.chmod(0o400)
     try:rejected('1');assert view('1')['draft']['text']==before_native and checkpoint.read_bytes()==before;expect(power('1')).to_have_value('9223372036854775805');verify_peer();assert cells('2')==held;f.originals();f.checked('독립 창의 checkpoint 쓰기 실패는 앞 설명/복합 값 전체 미적용이며 모든 창 입력을 보존한다')
     finally:checkpoint.chmod(0o600)
     restart(1);verify_peer()
    if mode=='loss':
     applies=set();queries=set();lost=[]
     def intercept(route):
      body=route.request.post_data_json
      if body.get('op')=='invoke' and body.get('endpoint')=='blueprint' and body.get('input',{}).get('view')=='1':
       action=body['input'].get('action')
       if action=='applySlots':applies.add(body['requestId'])
       elif applies and action=='settledSlots':queries.add(body['requestId'])
      response=route.fetch();payload=response.json()
      for r in payload.get('results',[]):
       if r['requestId'] in applies|queries:rid=r['requestId'];lost.append(rid);r.clear();r.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
      route.fulfill(response=response,json=payload)
     f.page.route('**/api/request',intercept);window('1').locator('[data-element-action=save]').click()
     for _ in range(300):
      if applies and any(r in queries for r in lost):break
      f.page.wait_for_timeout(100)
     assert len(applies)==1 and any(r in queries for r in lost);f.idle();assert cells('1') and journal('1');verify_peer();f.page.unroute_all(behavior='wait');mark=len(f.traffic);restart(1);window('1').locator('[data-element-action=save]').click();saved();assert not any(r.get('invoke',{}).get('input',{}).get('action')=='applySlots' for r in f.traffic[mark:]);f.checked('응답/조회 유실은 창별 시도를 보관하고 cold receipt 조회만으로 복구하며 중복 저장하지 않는다')
    else:window('1').locator('[data-element-action=save]').click();saved()
    assert view('1')['schema']['description']=='첫 창 원자 저장';verify_peer();f.originals();restart(2);expect(power('1')).to_have_value('9223372036854775805');verify_peer();f.checked('한 후보 Save/cold는 저장한 창 입력만 정리하고 peer 입력과 원본 파일을 보존한다')
    accepted=checkpoint.read_bytes();rejected('2');assert checkpoint.read_bytes()==accepted;verify_peer();window('2').locator('[data-element-action=discard]').click();expect(power('2')).to_have_value('9223372036854775805');expect(description('2')).to_have_value('첫 창 원자 저장');f.originals();f.checked('실제 오래된 두 번째 창 저장은 CAS로 거절하며 그 창의 명시 취소만 최신 공유 값을 읽는다')
    r=review();r.locator('[data-reject]').click();expect(r).to_be_hidden();f.originals();r=review()
    if r.locator('[data-review-advanced]').count():
     r.locator('[data-review-advanced]').click()
     if r.locator('[data-advanced-reviewed]').count():r.locator('[data-advanced-reviewed]').check()
    r.locator('#confirm').click();expect(r).to_have_count(0,timeout=120000);f.idle();assert {k for k,v in f.original.items() if (f.project/k).read_bytes()!=v}=={'Slime.celem'};restart(3);expect(power('1')).to_have_value('9223372036854775805');f.checked('명시 Review 취소/실제 compiler Confirm 후 cold까지 원래 객체만 반영하고 부모/다른 target을 보존한다')
   f.page.screenshot(path=str(f.case/'view-owner-final.png'));assert not f.errors and not f.external,(f.errors,f.external)
 except Exception:
  try:f.case.joinpath('view-failure.json').write_text(json.dumps({'state':f.state(),'traffic':f.traffic[-60:],'errors':f.errors},ensure_ascii=False,indent=2));f.page.screenshot(path=str(f.case/'view-failure.png'))
  except Exception:pass
  print('EVIDENCE '+str(f.case),flush=True);raise
 finally:f.stop()
 print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngine':True,'renderer':True,'nativeWindows':False,'accountOrInference':False},ensure_ascii=False))

if __name__=='__main__':main()
