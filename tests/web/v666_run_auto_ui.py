"""Original named preset UI with real private storage and actual size receipts, never simulated pixels."""
import json,sys,time,traceback,hashlib
from playwright.sync_api import sync_playwright,expect
sys.argv.append('--resizable-output')
import v666_run_fullscreen_fixture as f
mode=sys.argv[3];page=None

def open_run():
 page.get_by_role('tab',name='Workspace',exact=True).click();page.locator('#run').click();w=page.locator('.run-window:visible');expect(w.locator('[data-run-play]')).to_be_enabled();key=w.get_attribute('data-key');return page.locator('.window[data-key="'+key+'"]'),key

def menu(w):
 w.locator('[data-run-developer]').click();m=page.get_by_role('dialog',name='실행 개발 메뉴',exact=True);expect(m).to_be_visible();expect(m.locator('[data-run-preset-refresh]')).to_be_enabled();return m

def start(w,key):
 w.locator('[data-run-play]').click();expect(w.locator('.caption strong')).to_have_text('실행 중',timeout=180000);expect(w.locator('[data-run-pause]')).to_be_enabled();w.locator('[data-run-pause]').click();expect(w.locator('[data-run-step]')).to_be_enabled();expect(w.locator('[data-run-pixels]')).to_be_visible();return f.run('read',f.data(key))

def fill(m,width,height,name):
 m.locator('[data-run-resolution]').select_option('custom');m.locator('[data-run-width]').fill(str(width));m.locator('[data-run-height]').fill(str(height));m.locator('[data-run-preset-name]').fill(name)
def dimensions(w,width,height):page.wait_for_function('(a)=>{const c=document.querySelector(`.window[data-key="${a.key}"] [data-run-pixels]`);return c&&!c.hidden&&c.width===a.width&&c.height===a.height}',arg={'key':w.get_attribute('data-key'),'width':width,'height':height})
def changes():return[x for x in f.requests if x['endpoint']=='runWindow'and x['input']['operation']=='surface-size']
def writes():return[x for x in f.requests if x['endpoint']=='runPresets']
def registry():
 v=f.mount()
 try:
  for _ in range(200):
   p=f.raw({'op':'observe','view':v['view'],'scope':v['scope'],'endpoint':'runPresetRead','input':{}})
   if p.get('ok'):return p['result']
   assert p.get('error',{}).get('code')=='busy',p;time.sleep(.01)
  raise AssertionError(p)
 finally:f.raw({'op':'dispose','view':v['view']})
def wait_mode(m,prefix):page.wait_for_function('(a)=>document.getElementById(a.id).querySelector("[data-run-resolution]").value.startsWith(a.prefix)',arg={'id':m.get_attribute('id'),'prefix':prefix})
def flush_presentation(p):
 p.wait_for_function("()=>typeof globalThis.confectoryFlushPresentation==='function'");p.evaluate('()=>confectoryFlushPresentation()')
def step(w,m,width,height):
 m.locator('[data-dev-close]').click();w.locator('[data-run-step]').click();expect(w.locator('[data-run-step]')).to_be_enabled();dimensions(w,width,height)

def floating(w,key):
 page.locator('#workspace-pack-tab').click();page.locator('[data-tab-order-key="window:'+key+'"]').drag_to(page.locator('#workspace'),target_position={'x':550,'y':210});expect(w).to_be_visible();assert w.evaluate('(el)=>el.parentElement.classList.contains("workspace-floating-window-layer")')
def screen_size(w):return w.locator('.run-screen').evaluate('(el)=>[el.clientWidth,el.clientHeight]')
def resize(w,width,height):
 before=screen_size(w);h=w.locator('[data-resize="se"]').bounding_box();page.mouse.move(h['x']+h['width']/2,h['y']+h['height']/2);page.mouse.down();page.mouse.move(h['x']+h['width']/2+width-before[0],h['y']+h['height']/2+height-before[1],steps=8);page.mouse.up();page.wait_for_function('(a)=>{const e=document.querySelector(`.window[data-key="${a.key}"] .run-screen`);return e.clientWidth===a.width&&e.clientHeight===a.height}',arg={'key':w.get_attribute('data-key'),'width':width,'height':height})
def pending(m):expect(m.locator('[data-run-size-feedback]')).to_contain_text('다음 실제 출력');expect(m.locator('[data-run-size-feedback]')).to_be_visible()
def count(n):page.wait_for_function('(n)=>globalThis.__sizeRequests===n',arg=n)
def instrument():
 page.evaluate("""()=>{const base=fetch,held=new Set();globalThis.__sizeRequests=0;globalThis.__holdSize=false;globalThis.__heldSize=0;globalThis.__releaseSize=null;fetch=async(...args)=>{let b;try{b=JSON.parse(args[1]?.body||'{}')}catch{}if(b?.op==='invoke'&&b.endpoint==='runWindow'&&b.input.operation==='surface-size'){__sizeRequests++;if(__holdSize){__holdSize=false;held.add(b.requestId);}}const response=await base(...args);if(b?.op==='update'){const p=await response.clone().json();let changed=false;for(const row of p.results||[])if(held.delete(row.requestId)){__heldSize++;await new Promise(r=>__releaseSize=r);row.ok=false;delete row.result;row.error={code:'transport-interrupted'};changed=true;}if(changed)return new Response(JSON.stringify(p),{status:200,headers:{'Content-Type':'application/json'}});}return response;};}""")
def normal(browser):
 page.locator('#chat-input').fill('자동 맞춤은 실제 출력이며 실행 조건이 아님');w,key=open_run();row=start(w,key);frame=int(row['control']['frame']);floating(w,key);resize(w,360,280);instrument();m=menu(w);m.locator('[data-run-resolution]').select_option('auto');pending(m);count(1);dimensions(w,64,36);assert int(f.run('read',row)['control']['frame'])==frame;assert changes()[0]['input']['width']==360 and changes()[0]['input']['height']==280;m.locator('[data-dev-close]').click();resize(w,390,290);resize(w,410,300);page.wait_for_timeout(650);count(1);w.locator('[data-run-step]').click();dimensions(w,360,280);count(2);assert changes()[-1]['input']['width']==410 and changes()[-1]['input']['height']==300;page.wait_for_timeout(500);count(2);w.locator('[data-run-step]').click();dimensions(w,410,300);page.wait_for_timeout(650);count(2);f.checked('authored exact CSS auto fit queues one pending actual receipt, never advances paused frames, coalesces latest real resize only after ACK and does not repeat unchanged geometry')
 m=menu(w);m.locator('[data-run-resolution]').select_option('current');m.locator('[data-dev-close]').click();resize(w,430,320);page.wait_for_timeout(600);count(2);resize(w,650,330);m=menu(w);m.locator('[data-run-resolution]').select_option('auto');expect(m.locator('.run-resolution-form>small')).to_contain_text('범위 밖');page.wait_for_timeout(500);count(2);m.locator('[data-dev-close]').click();resize(w,440,310);count(3);w.locator('[data-run-step]').click();dimensions(w,440,310);f.checked('leaving auto cancels future geometry work; over-budget viewport is not clamped or sent, returning to supported dimensions produces real new pixels')
 m=menu(w);expect(m.locator('[data-run-size-feedback]')).to_contain_text('출력을 확인');page.screenshot(path=str(f.root/'actual-auto-fit.png'));m.locator('[data-dev-close]').click();w.locator('[data-run-play]').click();expect(w.locator('[data-run-play]')).to_have_text('▶');row2=start(w,key);assert row2['handle']!=row['handle'];page.wait_for_timeout(650);count(3);m=menu(w);expect(m.locator('[data-run-resolution]')).to_have_value('current');m.locator('[data-dev-close]').click();dimensions(w,64,36);expect(page.locator('#chat-input')).to_have_value('자동 맞춤은 실제 출력이며 실행 조건이 아님');f.checked('Stop/new runtime disables prior auto publisher rather than replaying geometry or original commands; source/chat/layout retained')
def lifecycle(browser):
 global page
 page.locator('#chat-input').fill('자동 맞춤 중 늦은 입력 보존');w,key=open_run();row=start(w,key);floating(w,key);resize(w,360,280);instrument();m=menu(w);page.evaluate('()=>__holdSize=true');m.locator('[data-run-resolution]').select_option('auto');page.wait_for_function('()=>__heldSize===1');m.locator('[data-run-resolution]').select_option('custom');fill(m,480,256,'보존할 이름');page.evaluate('()=>__releaseSize()');expect(w.locator('[data-run-retry]')).to_be_visible();expect(m.locator('[data-run-width]')).to_have_value('480');m.locator('[data-dev-close]').click();resize(w,420,300);page.wait_for_timeout(600);count(1);w.locator('[data-run-retry]').click();expect(w.locator('[data-run-retry]')).to_be_hidden();m=menu(w);expect(m.locator('[data-run-resolution]')).to_have_value('custom');expect(m.locator('[data-run-width]')).to_have_value('480');expect(m.locator('[data-run-preset-name]')).to_have_value('보존할 이름');pending(m);step(w,m,360,280);page.wait_for_timeout(500);count(1);f.checked('accepted auto reply loss and late custom input do not replay size commands; explicit read recovers receipt, explicit Step applies original captured target only')
 m=menu(w);m.locator('[data-run-resolution]').select_option('auto');pending(m);count(2);m.locator('[data-run-resolution]').select_option('current');m.locator('[data-dev-close]').click();resize(w,440,310);page.wait_for_timeout(600);count(2);w.locator('[data-run-step]').click();dimensions(w,420,300);page.wait_for_timeout(500);count(2);f.checked('leaving auto during pending receipt preserves that request but cancels queued geometry and leaves Step/ACK independent')
 m=menu(w);page.evaluate('()=>__holdSize=true');m.locator('[data-run-resolution]').select_option('auto');page.wait_for_function('()=>__heldSize===2');page.evaluate('()=>__releaseSize()');expect(w.locator('[data-run-retry]')).to_be_visible();m.locator('[data-dev-close]').click();resize(w,460,330);w.locator('[data-run-retry]').click();expect(w.locator('[data-run-retry]')).to_be_hidden();w.locator('[data-run-step]').click();dimensions(w,440,310);page.wait_for_timeout(600);count(3);m=menu(w);expect(m.locator('.run-resolution-form>small')).to_contain_text('자동 맞춤을 멈췄어요');m.locator('[data-run-resolution]').select_option('current');m.locator('[data-run-resolution]').select_option('auto');pending(m);count(4);f.checked('uncertain auto result latches even after receipt read and ACK; new geometry needs explicit reselection, no implicit command retry');m.locator('[data-run-resolution]').evaluate('(el)=>{globalThis.__oldAutoChange=el.onchange;globalThis.__oldAutoSelect=el;}');m.locator('[data-dev-close]').click();w.locator('[data-close]').click();expect(w).to_be_hidden();assert f.run('read',row)['closed'];fresh,newkey=open_run();page.evaluate('()=>{__oldAutoSelect.value="auto";__oldAutoChange();}');page.wait_for_timeout(500);count(4);flush_presentation(page);page.close();f.stop();f.start(1);page=f.setup(browser);expect(page.locator('.window[data-key="'+newkey+'"] [data-run-play]')).to_be_enabled();expect(page.locator('#chat-input')).to_have_value('자동 맞춤 중 늦은 입력 보존');assert not f.data(newkey)['handle'];assert not[x for x in f.requests if x['endpoint']=='runWindow'and x['input']['operation']=='surface-size'][4:];f.checked('close disposes observer and old selection handlers; fresh sibling/cold restores input and layout without a process, auto mode or runtime command replay')
try:
 f.start(0)
 with sync_playwright()as pw:
  expect.set_options(timeout=60000);browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=f.setup(browser)
  try:
   if mode=='normal':normal(browser)
   else:lifecycle(browser)
   f.original();assert not f.errors and not f.external,(f.errors,f.external)
   if not page.is_closed():page.close()
   browser.close()
  except Exception:
   if not page.is_closed():
    try:page.screenshot(path=str(f.root/'failure.png'),timeout=5000);(f.root/'failure.html').write_text(page.content())
    except Exception:pass
   raise
except Exception as error:
 (f.root/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc(),errors=f.errors),ensure_ascii=False));raise
finally:f.save_evidence();f.stop()
print('RUN_AUTO_UI',f.root,flush=True)
