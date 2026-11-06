"""Existing general Blueprint viewport over an actual generated-project engine."""
import json,sys,traceback
from playwright.sync_api import sync_playwright,expect
import v536_wide_mixed as f
mode=sys.argv[3];reads=[];injections=0
def route(request):
 global injections
 body=request.request.post_data_json if request.request.method=='POST'else None
 if isinstance(body,dict)and body.get('op')=='invoke'and body.get('endpoint')=='blueprint'and body.get('input',{}).get('action')in ['list','read']:
  reads.append(body)
  if mode!='baseline'and injections<(3 if mode=='exhausted'else 2):
   injections+=1;body['expectedRevision']-=1;request.continue_(post_data=json.dumps(body));return
 f.route(request)
dialog=lambda:f.page.get_by_role('dialog',name='노드 화면 배율',exact=True)
def popup():
 f.author().locator('[data-bp-percent]').click();expect(dialog()).to_be_visible();return dialog()
def at(n):expect(f.author().locator('[data-bp-percent]')).to_have_text(str(n)+'%')
def set_zoom(n):
 popup().locator('[data-zoom-preset="'+str(n)+'"]').click();at(n);dialog().locator('[data-zoom-value]').press('Escape')
def capture():
 dialog().evaluate('''m=>{const input=m.querySelector('[data-zoom-value]'),slider=m.querySelector('[data-zoom-slider]'),preset=m.querySelector('[data-zoom-preset="400"]'),fit=m.querySelector('[data-zoom-fit]');globalThis.__nativeRetired={menu:m,input,slider,slide:slider.oninput,click:preset.onclick,fit:fit.onclick,blur:input.onblur,enter:input.onkeydown,open:document.querySelector('[data-bp-percent]').onclick};}''')
def late():
 f.page.evaluate('''()=>{const r=__nativeRetired;r.input.value='425';r.slider.value='200';r.slide({target:r.slider});r.click();r.fit();r.blur();r.enter({key:'Enter',preventDefault(){},stopPropagation(){}});r.menu.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}));}''')
def guards():
 f.originals();assert not f.errors and not f.external,(f.errors,f.external)
 forbidden={'editDraft','saveDraft','reviewDraft','confirmDraft','confirm','confirmGroup','authorBatch','edit','runProject','startAI'}
 assert not forbidden.intersection(r.get('invoke',{}).get('endpoint')for r in f.traffic)
def open_native():
 f.page.locator('#workspace').click(button='right',position={'x':700,'y':300});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]');b.get_by_role('button',name='기능',exact=True).click();b.locator('[data-browser-control="object-query"]').fill('Slot');b.locator('[data-browser-control="object-search"]').click();f.idle()
 if mode=='exhausted':
  b.locator('[data-object="'+f.n+'Slot"]').click(button='right');f.page.get_by_role('button',name='기능 Blueprint',exact=True).click();expect(f.page.locator('#toast')).to_contain_text('stale_revision');f.idle();assert injections==3 and len(reads)==3;expect(f.author()).to_have_count(0);f.checked('three actual pre-admission stale read rejections exhaust the bounded entry retry; no source or partial Blueprint is created before the next explicit open')
 for attempt in range(3 if mode=='baseline'else 1):
  b.locator('[data-object="'+f.n+'Slot"]').click(button='right');f.page.get_by_role('button',name='기능 Blueprint',exact=True).click()
  try:expect(f.author().locator('.bp-scroll')).to_be_visible(timeout=10000);break
  except AssertionError:
   assert mode=='baseline'and attempt<2 and 'stale_revision'in f.page.locator('#toast').inner_text();f.idle();f.checked('published Blueprint entry rejects a concurrent revision; baseline explicitly retries the read-only UI request')
 b.locator('[data-close]').first.click();f.idle()
try:
 f.start(0)
 with sync_playwright()as p:
  expect.set_options(timeout=60000);f.browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.route('**/*',route);f.page.set_viewport_size({'width':1600,'height':1100});open_native()
  if mode!='baseline':assert injections==(3 if mode=='exhausted'else 2)and len(reads)>=(5 if mode=='exhausted'else 4),(injections,len(reads));f.checked('general Blueprint opens after bounded readonly re-observation, with no repeated mutation or automatic source conversion')
  f.page.locator('#chat-input').fill('일반 Blueprint 확대 중 보존할 입력 😀');set_zoom(500);popup();capture();dialog().locator('[data-zoom-value]').press('Escape');popup()
  f.page.evaluate("()=>{const r=__nativeRetired;r.slider.value='200';r.slide({target:r.slider});}")
  if mode=='baseline':
   at(200);f.checked('published general Blueprint retired slider mutates the reopened viewport from 500% to 200% through the actual engine presentation path')
  else:
   at(500);dialog().locator('[data-zoom-value]').fill('300');late();at(500);expect(dialog().locator('[data-zoom-value]')).to_have_value('300');dialog().locator('[data-zoom-value]').press('Enter');at(300);dialog().locator('[data-zoom-value]').press('Escape')
   for _ in range(3):
    popup();capture();dialog().locator('[data-zoom-value]').fill('100');dialog().locator('[data-zoom-value]').press('Escape');late();at(300);expect(dialog()).to_have_count(0)
   set_zoom(400);f.page.evaluate('()=>confectoryFlushPresentation()');guards();f.checked('actual general Blueprint rejects retired slider/preset/fit/blur/Enter on reopen and repeated cancellation, while current Enter/presets preserve private input and physical sources')
   f.page.close();f.stop();f.start(1);f.page=f.setup();f.page.set_viewport_size({'width':1600,'height':1100});at(400);expect(f.page.locator('#chat-input')).to_have_value('일반 Blueprint 확대 중 보존할 입력 😀');expect(dialog()).to_have_count(0);popup();capture();f.author().locator('[data-close]').first.evaluate('el=>el.click()');expect(f.author()).to_be_hidden();expect(dialog()).to_have_count(0);f.page.evaluate('()=>__nativeRetired.open()');expect(dialog()).to_have_count(0);late();expect(dialog()).to_have_count(0);f.checked('cold restores only accepted 400% and private input; closing the real general Blueprint retires its popup and retained open/input callbacks')
  guards();f.page.screenshot(path=str(f.case/('native-zoom-lifetime-'+mode+'.png')));f.browser.close()
except Exception as e:
 try:f.page.screenshot(path=str(f.case/'failure.png'));(f.case/'failure.html').write_text(f.page.content())
 except Exception:pass
 (f.case/'failure.json').write_text(json.dumps(dict(error=repr(e),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:
 f.stop();(f.case/'native-zoom-lifetime.json').write_text(json.dumps(dict(checks=f.checks,errors=f.errors,reads=reads,injectedPreAdmissionStales=injections,actualEngine=True,actualWindows=False,actualMobile=False),ensure_ascii=False,indent=2))
print('NATIVE_ZOOM_LIFETIME_FIXTURE',f.case,flush=True)
