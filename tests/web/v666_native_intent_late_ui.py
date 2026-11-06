"""Queued input during existing native intent Apply; controls remain disabled."""
import json,sys,time,traceback
from playwright.sync_api import sync_playwright,expect
import v536_wide_mixed as f
mode=sys.argv[3];graph=f.n+'SlotBody/body:common';paused={};ids=set();requests=[];base=None
field=lambda:f.author().locator('[data-bp-intent]')
def open_native():
 f.page.locator('#workspace').click(button='right',position={'x':700,'y':300});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]');b.get_by_role('button',name='기능',exact=True).click();b.locator('[data-browser-control="object-query"]').fill('Slot');b.locator('[data-browser-control="object-search"]').click();f.idle();b.locator('[data-object="'+f.n+'Slot"]').click(button='right');f.page.get_by_role('button',name='기능 Blueprint',exact=True).click();expect(f.author().locator('.bp-scroll')).to_be_visible();b.locator('[data-close]').first.click();f.idle();f.author().locator('[data-bp-select="body"]').click();expect(field()).to_be_visible();f.idle()
def private():return [(k,v)for k,v in f.pending()['blueprint']if '|'+graph+'|intent|'in k]
def shared():return next(n['intent']for n in f.invoke('blueprint',{'action':'read','id':graph})['result']['result']['nodes']if n['id']=='body')
def button(name):return field().locator('..').locator('[data-'+name+']')
def hold(route):
 body=route.request.post_data_json
 if body.get('op')=='invoke'and body.get('endpoint')=='blueprint'and body.get('input',{}).get('action')=='intent':ids.add(body['requestId']);requests.append(body)
 response=route.fetch();data=response.json()
 if not paused and any(row.get('requestId')in ids and row.get('ok')for row in data.get('results',[])):paused.update(route=route,response=response,data=data);return
 route.fulfill(response=response,json=data)
def release(failure=False):
 data=paused['data']
 if failure:
  for row in data.get('results',[]):
   if row.get('requestId')in ids:row['ok']=False;row['error']={'code':'transport-interrupted'};row.pop('result',None)
 paused['route'].fulfill(response=paused['response'],json=data);f.page.unroute('**/api/request',hold);paused.clear();ids.clear();f.idle()
def guards():
 f.originals();assert not f.errors and not f.external,(f.errors,f.external)
 forbidden={'editDraft','saveDraft','confirmDraft','confirm','confirmGroup','reviewGroup','runProject','startAI'}
 assert not forbidden.intersection(row.get('invoke',{}).get('endpoint')for row in f.traffic)
def history(action):
 state=f.invoke('draftHistory',{'action':'inspect'})['result']['result'];assert state[action]['available'];assert f.invoke('draftHistory',{'action':action,'token':state[action]['token']})['result']['result']['accepted'];f.originals()
try:
 f.start(0)
 with sync_playwright()as p:
  try:
   expect.set_options(timeout=60000);f.browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1300});open_native();base=field().input_value();assert shared()==base;submitted=base+' 새 설명 제출 😀';field().fill(submitted);assert private()[0][1]['text']==submitted
   f.page.route('**/api/request',hold);button('apply').click();end=time.monotonic()+20
   while not paused and time.monotonic()<end:f.page.wait_for_timeout(30)
   assert paused;expect(field()).to_be_disabled()
   if mode=='normal':
    field().evaluate('el=>globalThis.__intentBeforeRemount=el');f.author().locator('[data-bp-select="body"]').evaluate('el=>el.click()');assert field().evaluate('el=>el!==__intentBeforeRemount');expect(field()).to_be_disabled()
   field().evaluate('el=>globalThis.__retiredIntent={el,input:el.oninput}')
   wanted=submitted if mode=='aba'else base
   field().evaluate('''(el,values)=>{for(const value of values){el.value=value;el.dispatchEvent(new InputEvent('input',{bubbles:true,inputType:'insertReplacementText'}));}}''',['중간 입력',wanted]);expect(field()).to_have_value(wanted)
   release(mode=='failure')
   if mode=='baseline':
    expect(field()).to_have_value(submitted);assert not private();assert shared()==submitted;f.checked('published native Apply overwrites a queued return-to-original intent with the older submitted value and drops its private entry')
   else:
    expect(field()).to_have_value(wanted);assert private()[0][1]['text']==wanted;assert shared()==submitted;assert len(requests)==1;guards();f.checked('queued '+('same-text ABA'if mode=='aba'else'return-to-original')+' input survives '+('lost success reply'if mode=='failure'else'accepted Apply')+'; source applies exactly the submitted intent once, controls stay blocked during the request')
    if mode=='normal':
     held=private();f.page.evaluate("()=>{__retiredIntent.el.value='RetiredMustNotReplace';__retiredIntent.input();}");expect(field()).to_have_value(wanted);assert private()==held;f.checked('controlled same-source selection remount retains the pending attempt; old disconnected input callbacks cannot replace the newer private intent')
    if mode=='cold':
     f.pending();f.page.close();f.stop();f.start(1);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1300});expect(f.author().locator('.bp-scroll')).to_have_count(0);f.author().locator('[data-bp-read]').click();expect(field()).to_be_visible();expect(field()).to_have_value(wanted);assert private()[0][1]['text']==wanted;before=shared();button('apply').click();f.idle();expect(field()).to_have_value(wanted);assert private()[0][1]['text']==wanted and shared()==before;button('reset').click();assert not private();f.checked('cold retains the queued text without source authority; Apply before explicit basis re-observation is refused and explicit Reset alone discards the private entry')
    elif mode=='aba':
     button('reset').click();assert not private();expect(field()).to_have_value(submitted);f.checked('same-text newer intent is retained until explicit Reset even when the accepted draft has the same display text')
    else:
     button('apply').click();f.idle();expect(field()).to_have_value(wanted);assert private()[0][1]['text']==wanted and shared()==submitted;f.checked('existing source basis/CAS refuses implicit rebase of the newer private intent after accepted Apply or lost response')
     if mode=='failure':f.author().locator('[data-bp-read]').click();expect(field()).to_have_value(wanted)
     button('rebase').click();button('apply').click();f.idle();expect(field()).to_have_value(wanted);assert not private()and shared()==wanted;history('undo');assert shared()==submitted;history('redo');assert shared()==wanted;f.checked('explicit basis review and Apply commit only the chosen intent; shared Undo/Redo retain original IDs/contracts and physical source bytes')
   guards();f.page.screenshot(path=str(f.case/('native-intent-late-'+mode+'.png')));f.browser.close()
  except Exception as e:
   try:f.page.screenshot(path=str(f.case/'failure.png'));(f.case/'failure.html').write_text(f.page.content())
   except Exception:pass
   (f.case/'failure.json').write_text(json.dumps(dict(error=repr(e),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:
 f.stop();(f.case/'native-intent-late.json').write_text(json.dumps(dict(checks=f.checks,errors=f.errors,applyRequests=requests,originalIntent=base,actualEngine=True,queuedCallbackSimulation=True,actualWindows=False,actualMobile=False),ensure_ascii=False,indent=2))
print('NATIVE_INTENT_LATE_FIXTURE',f.case,flush=True)
