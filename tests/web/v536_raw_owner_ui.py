"""Real source/properties windows share an explicit atomic owner save."""
import json,sys
from playwright.sync_api import sync_playwright,expect
import v536_wide_mixed as f
mode=sys.argv[3] if len(sys.argv)>3 else 'normal'
def win(slot):return f.page.locator('.window[data-key="editor-'+slot+'"]')
def number(path):return win('2').locator('[data-property-path=\''+json.dumps(path,separators=(',',':'))+'\'] [data-property-value]')
def raw_input():return win('1').locator('[data-editor-source]')
def pending():return f.pending()
def cells():return [(k,v) for k,v in pending()['schema'] if '|'+f.id+'|view:2|element|' in k]
def raws():return [(k,v) for k,v in pending()['views'] if k.endswith('|1|'+f.id)]
def journals():return [(k,v) for k,v in pending()['blueprint'] if k.endswith('|v536-raw-owner-attempt|'+f.id)]
def move(slot,x,y):
 w=win(slot);h=w.locator('.object-title-name') if w.locator('.object-title-name').count() else w.locator('.caption');head=h.bounding_box();box=w.bounding_box();f.page.mouse.move(head['x']+6,head['y']+8);f.page.mouse.down();f.page.mouse.move(x+head['x']-box['x']+6,y+head['y']-box['y']+8,steps=10);f.page.mouse.up();f.idle()
def restart(i):
 pending();f.page.unroute_all(behavior='wait');f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1400});expect(raw_input()).to_be_visible(timeout=60000);expect(number(['HP'])).to_be_visible();f.idle();move('3',1500,730) if mode=='peer' else None
def save():win('2').locator('[data-element-action=save]').click()
def saved():
 for _ in range(240):
  if not cells() and not raws() and not journals():f.idle();return
  f.page.wait_for_timeout(100)
 raise AssertionError((win('2').locator('[data-element-error]').all_text_contents(),pending()))
def reject():
 f.page.evaluate('''()=>{globalThis.rawMessages=[];globalThis.rawObserver=new MutationObserver(()=>{for(const el of document.querySelectorAll('[data-element-error],#status'))if(el.textContent&&!rawMessages.includes(el.textContent))rawMessages.push(el.textContent)});rawObserver.observe(document.body,{subtree:true,childList:true,characterData:true})}''');save();f.page.wait_for_function('()=>rawMessages.some(s=>/입력.*유지|보존|바뀌|consumer_error|거절|확인|미적용|원문/.test(s))');f.page.evaluate('()=>rawObserver.disconnect()');f.idle()
def review():
 win('2').locator('[data-element-action=confirm]').click();r=f.page.locator('.window[data-key=review]');f.page.wait_for_function('()=>document.querySelector("#review-creation")||[...document.querySelectorAll(".window[data-key=review]")].some(e=>!e.hidden&&e.getClientRects().length)')
 if f.page.locator('#review-creation').count():f.page.locator('#review-creation').click()
 expect(r).to_be_visible();return r
try:
 f.start(0);f.invoke('select',{'id':f.id});f.invoke('saveDraft',{});f.invoke('openEditorView',{'view':'1','id':f.id,'viewMode':'source'});f.invoke('openEditorView',{'view':'2','id':f.id,'viewMode':'properties'});f.invoke('select',{'id':f.n+'Unit'})
 if mode=='peer':f.invoke('openEditorView',{'view':'3','id':f.n+'Unit','viewMode':'properties'})
 with sync_playwright() as pw:
  f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1400});expect.set_options(timeout=60000);expect(raw_input()).to_be_visible();expect(number(['HP'])).to_be_visible();move('3',1500,730) if mode=='peer' else None;move('1',40,130);move('2',920,130)
  if mode=='peer':win('3').locator('[aria-label="HP 기본값"]').fill('9007199254740997');peer=[(k,v) for k,v in pending()['schema'] if '|'+f.n+'Unit|view:3|element|' in k];assert len(peer)==1
  before_native=next(r for r in f.state()['editorViews'] if r['view']=='1')['draft']['text'];raw=raw_input().input_value().replace('{','{\n// raw 소스 한글 😀\n description "소스 창 설명";\n',1);raw_input().fill(raw);number(['HP']).fill('9223372036854775806');held=pending();assert len(raws())==1 and len(cells())==1;checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();f.originals();f.checked('기존 실제 source/properties 두 창은 raw 원문/주석과 exact long을 서로 다른 기준 입력으로 보관하며 primary 다른 owner를 유지한다')
  restart(1);expect(raw_input()).to_have_value(raw);expect(number(['HP'])).to_have_value('9223372036854775806');assert raws()==[(k,v) for k,v in held['views']] and all(v.get('basis',{}).get('sourceIdentity') for _,v in raws());f.checked('저장 전 cold는 원래 raw source 위치 증거·텍스트·창별 typed 입력을 복원한다')
  if mode=='late':
   applies=set();late=raw+'\n// 저장 중 추가 한글 😀\n';inserted=[]
   def intercept(route):
    body=route.request.post_data_json
    if body.get('op')=='invoke' and body.get('endpoint')=='blueprint' and body.get('input',{}).get('action')=='applySlots':applies.add(body['requestId'])
    response=route.fetch();payload=response.json()
    if not inserted and any(r['requestId'] in applies and r.get('ok') for r in payload.get('results',[])):
     f.page.evaluate('text=>{const raw=document.querySelector(\'.window[data-key="editor-1"] [data-editor-source]\');raw.value=text;raw.dispatchEvent(new Event(\'input\',{bubbles:true}));const field=document.querySelector(\'.window[data-key="editor-2"] [aria-label="HP 기본값"]\');field.value=\'777\';field.dispatchEvent(new Event(\'input\',{bubbles:true}));}',late);inserted.append(True)
    route.fulfill(response=response,json=payload)
   f.page.route('**/api/request',intercept);save()
   for _ in range(300):
    if inserted and not journals():break
    f.page.wait_for_timeout(100)
   assert inserted and not journals();f.page.unroute_all(behavior='wait');expect(raw_input()).to_have_value(late);expect(number(['HP'])).to_have_value('777');assert raws() and cells();stored=next(r for r in f.state()['editorViews'] if r['view']=='1')['draft']['text'];assert stored==raw.replace('data HP=101;','data HP=9223372036854775806;');restart(2);expect(raw_input()).to_have_value(late);expect(number(['HP'])).to_have_value('777');f.originals();f.checked('Save 응답 이전에 새로 입력한 raw/typed 값은 늦은 receipt가 지우거나 적용하지 않고 cold에도 원래 기준과 함께 보존한다')
  elif mode=='cancel':
   win('2').locator('[data-element-action=discard]').click();f.idle();assert not cells() and raws();expect(raw_input()).to_have_value(raw);move('2',1500,130);win('1').locator('[data-editor-reset]').click();f.idle();assert not raws() and checkpoint.read_bytes()==before;restart(2);expect(raw_input()).to_have_value(before_native);f.originals();f.checked('속성 창 local 취소는 다른 raw 창 입력을 보존하며 source reset/cold만 자기 원문을 취소하고 checkpoint를 바꾸지 않는다')
  elif mode=='conflict':
   p=f.project/'Slime.celem';p.write_bytes(p.read_bytes()+b'\n// isolated peer source\n');f.original['Slime.celem']=p.read_bytes();held=pending();reject();assert checkpoint.read_bytes()==before;f.retained(held);restart(2);reject();f.retained(held);f.originals();f.checked('실제 source 변경은 raw/typed 전체 미적용·peer 파일/원래 원문과 cold 재시도 입력 보존으로 거절한다')
  else:
   if mode in ['undo','cancel-race']:
    move('2',1500,130);raw_input().evaluate("el=>{const i=el.value.indexOf('data HP=101;')+8;el.focus();el.setSelectionRange(i,i+3)}");f.page.keyboard.insert_text('102');bad=pending();reject();assert checkpoint.read_bytes()==before and journals();f.retained(bad)
    if mode=='undo':
     raw_input().focus();f.page.keyboard.press('Control+z');expect(raw_input()).to_have_value(raw);assert cells() and journals();f.originals();f.checked('raw/typed 중복 변경 거절 뒤 실제 textarea Undo는 원래 raw 기준을 복원하며 명시 재시도만 새 후보로 만든다')
    else:
     moved=raw_input().input_value()+'\n// 취소 중 새 입력\n';queries=set();injected=[]
     def intercept(route):
      body=route.request.post_data_json
      if body.get('op')=='invoke' and body.get('endpoint')=='blueprint' and body.get('input',{}).get('action')=='settledSlots':queries.add(body['requestId'])
      response=route.fetch();payload=response.json()
      if not injected and any(r['requestId'] in queries for r in payload.get('results',[])):
       raw_input().evaluate("(el,text)=>{el.value=text;el.dispatchEvent(new Event('input',{bubbles:true}))}",moved);injected.append(True)
      route.fulfill(response=response,json=payload)
     f.page.route('**/api/request',intercept);win('1').locator('[data-editor-reset]').click();f.page.wait_for_function("()=>document.querySelector('.brand:not([disabled])')");assert injected;f.page.unroute_all(behavior='wait');expect(raw_input()).to_have_value(moved);assert raws() and cells() and checkpoint.read_bytes()==before;restart(2);expect(raw_input()).to_have_value(moved);f.originals();f.checked('늦은 source Reset 결과가 취소 중 새 raw 입력과 다른 속성 창 입력을 삭제하지 않는다');f.page.screenshot(path=str(f.case/'raw-owner-final.png'));f.browser.close();f.stop();print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngine':True,'renderer':True,'nativeWindows':False,'accountOrInference':False},ensure_ascii=False));sys.exit(0)
   if mode=='reject':
    number(['HP']).fill('9223372036854775808');bad=pending();reject();assert checkpoint.read_bytes()==before;f.retained(bad);restart(2);expect(number(['HP'])).to_have_value('9223372036854775808');number(['HP']).fill('9223372036854775806');f.checked('잘못된 typed 값은 raw 설명까지 전체 미적용이며 cold 원문 보존 뒤 명시 수정 재시도를 허용한다')
   if mode=='storage':
    checkpoint.chmod(0o400)
    try:held=pending();reject();assert checkpoint.read_bytes()==before and next(r for r in f.state()['editorViews'] if r['view']=='1')['draft']['text']==before_native;f.retained(held);f.originals();f.checked('checkpoint 쓰기 실패는 raw/typed 어느 쪽도 적용하지 않고 원문·창별 입력을 보존한다')
    finally:checkpoint.chmod(0o600)
    restart(2)
   if mode=='loss':
    applies=set();queries=set();lost=[]
    def intercept(route):
     body=route.request.post_data_json
     if body.get('op')=='invoke' and body.get('endpoint')=='blueprint':
      action=body.get('input',{}).get('action')
      if action=='applySlots':applies.add(body['requestId'])
      elif applies and action=='settledSlots':queries.add(body['requestId'])
     response=route.fetch();payload=response.json()
     for r in payload.get('results',[]):
      if r['requestId'] in applies|queries:rid=r['requestId'];lost.append(rid);r.clear();r.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
     route.fulfill(response=response,json=payload)
    f.page.route('**/api/request',intercept);save()
    for _ in range(300):
     if applies and any(r in queries for r in lost):break
     f.page.wait_for_timeout(100)
    assert len(applies)==1 and any(r in queries for r in lost);assert raws() and cells() and journals();f.page.unroute_all(behavior='wait');mark=len(f.traffic);restart(2);save();saved();assert not any(r.get('invoke',{}).get('input',{}).get('action')=='applySlots' for r in f.traffic[mark:]);f.checked('적용/조회 응답 유실은 cold receipt 조회로만 복구하며 raw 후보를 중복 적용하지 않는다')
   else:
    if mode=='source-save':move('2',1500,130);win('1').locator('[data-editor-save]').click()
    else:save()
    saved()
   expected=raw.replace('data HP=101;','data HP=9223372036854775806;');expect(raw_input()).to_have_value(expected);assert f.state()['draft']['id']==f.n+'Unit';f.originals();restart(3);expect(raw_input()).to_have_value(expected);expect(number(['HP'])).to_have_value('9223372036854775806');f.checked('한 후보 Save/cold는 raw 주석/공백/정확한 값·원래 참조를 함께 보관하며 primary 선택·부모·다른 source를 바꾸지 않는다')
   if mode=='peer':
    assert [(k,v) for k,v in pending()['schema'] if '|'+f.n+'Unit|view:3|element|' in k]==peer;expect(win('3').locator('[aria-label="HP 기본값"]')).to_have_value('9007199254740997');win('3').locator('[data-element-action=discard]').click();f.idle();assert not [(k,v) for k,v in pending()['schema'] if '|'+f.n+'Unit|view:3|element|' in k];f.originals();f.checked('다른 owner 창의 미저장 exact 값은 raw Save/cold에 그대로 남으며 해당 창의 명시 취소만 그 입력을 정리한다')
   r=review();r.locator('[data-reject]').click();expect(r).to_be_hidden();f.originals();r=review()
   if r.locator('[data-review-advanced]').count():
    r.locator('[data-review-advanced]').click()
    if r.locator('[data-advanced-reviewed]').count():r.locator('[data-advanced-reviewed]').check()
   r.locator('#confirm').click();expect(r).to_have_count(0,timeout=120000);f.idle();assert {k for k,v in f.original.items() if (f.project/k).read_bytes()!=v}=={'Slime.celem'};assert (f.project/'Slime.celem').read_text()==expected;restart(4);expect(raw_input()).to_have_value(expected);f.checked('명시 Review 취소/compiler Confirm/cold는 결합한 source만 원문 그대로 최종 반영한다')
  f.page.screenshot(path=str(f.case/'raw-owner-final.png'));assert not f.errors and not f.external,(f.errors,f.external);f.page.unroute_all(behavior='wait');f.browser.close()
except Exception:
 try:f.case.joinpath('raw-ui-failure.json').write_text(json.dumps({'state':f.state(),'traffic':f.traffic[-90:],'errors':f.errors},ensure_ascii=False,indent=2));f.page.screenshot(path=str(f.case/'raw-ui-failure.png'))
 except Exception:pass
 print('EVIDENCE '+str(f.case),flush=True);raise
finally:f.stop()
print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngine':True,'renderer':True,'nativeWindows':False,'accountOrInference':False},ensure_ascii=False))
