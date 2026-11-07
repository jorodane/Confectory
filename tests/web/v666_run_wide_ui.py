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

def normal(browser):
 global page
 page.locator('#chat-input').fill('640 출력도 원본과 실행 계약 보존');w,key=open_run();row=start(w,key);frame=int(row['control']['frame']);m=menu(w);expect(m.locator('optgroup[label="PC · 가로"] option')).to_have_text('640 × 360');m.locator('[data-run-resolution]').select_option('640x360');expect(m.locator('[data-run-size-feedback]')).to_contain_text('다음 실제 출력');expect(m.locator('[data-run-size-feedback]')).to_be_visible();assert len(changes())==1;dimensions(w,64,36);assert int(f.run('read',row)['control']['frame'])==frame;step(w,m,640,360);f.checked('original PC 640x360 option sends one owned request and leaves paused frames unchanged; one explicit Step confirms exact new pixels')
 m=menu(w);fill(m,640,360,'가로 화면');expect(m.locator('[data-run-preset-save]')).to_be_enabled();m.locator('[data-run-preset-save]').click();wait_mode(m,'preset:');expect(m.locator('[data-run-size-feedback]')).to_contain_text('다음 실제 출력');assert registry()['items'][0]['width']==640;step(w,m,640,360);m=menu(w);fill(m,640,512,'초과 예산');expect(m.locator('[data-run-size-apply]')).to_be_disabled();expect(m.locator('[data-run-preset-save]')).to_be_disabled();n=len(changes());fill(m,640,409,'최대 너비');expect(m.locator('[data-run-size-apply]')).to_be_enabled();m.locator('[data-run-size-apply]').click();expect(m.locator('[data-run-size-feedback]')).to_contain_text('다음 실제 출력');assert len(changes())==n+1;step(w,m,640,409);m=menu(w);page.screenshot(path=str(f.root/'actual-wide-output.png'));m.locator('[data-dev-close]').click();flush_presentation(page);page.close();f.stop();f.start(1);page2=f.setup(browser);page=page2;expect(page2.locator('.window[data-key="'+key+'"] [data-run-play]')).to_be_enabled();assert registry()['items'][0]['width']==640;expect(page2.locator('#chat-input')).to_have_value('640 출력도 원본과 실행 계약 보존');assert not f.data(key)['handle'];f.checked('wide private registration survives cold; area-over-budget custom and registration are rejected without erasing input, valid maximum-axis area renders, no runtime command replay')
 w2=page2.locator('.window[data-key="'+key+'"]');start(w2,key);w2.locator('[data-run-developer]').click();m2=page2.get_by_role('dialog',name='실행 개발 메뉴',exact=True);page2.wait_for_function('(id)=>document.getElementById(id).querySelector(\"option[value=\\\"640x360\\\"]\").disabled===false',arg=m2.get_attribute('id'));m2.locator('[data-dev-close]').click();n=len(changes());page2.evaluate("""()=>{const base=fetch;globalThis.__legacyPackets=0;fetch=async(...args)=>{let b;try{b=JSON.parse(args[1]?.body||'{}')}catch{}const target=b?.op==='observe'&&b.endpoint==='runSurface';if(target){b.input.cursor='';args[1]={...args[1],body:JSON.stringify(b)};}const response=await base(...args);if(!target)return response;const p=await response.clone().json();if(p.ok&&p.result?.available){__legacyPackets++;p.result.runtime='e'.repeat(32);p.result.cursor=p.result.runtime+':'+p.result.revision;p.result.resize.max=512;delete p.result.resize.maxPixels;p.result.unchanged=false;}return new Response(JSON.stringify(p),{status:200,headers:{'Content-Type':'application/json'}});};}""");w2.locator('[data-run-developer]').click();page2.wait_for_function('(id)=>{const m=document.getElementById(id);return globalThis.__legacyPackets>0&&m.querySelector(\"option[value=\\\"640x360\\\"]\").disabled&&m.querySelector(\"optgroup[label=\\\"등록한 해상도\\\"] option\").disabled}',arg=m2.get_attribute('id'));m2.locator('[data-run-resolution]').select_option('custom');expect(m2.locator('[data-run-width]')).to_have_attribute('max','512');assert len(changes())==n;page2.close();f.checked('browser-only simulated validated legacy publisher replacement refreshes fixed/preset disabled options and form max512 without a size command; native legacy compatibility is tested separately')
def lifecycle(browser):
 global page
 page.locator('#chat-input').fill('가로 요청 중 늦은 새 입력');w,key=open_run();row=start(w,key);m=menu(w);page.evaluate("""()=>{const base=fetch,held=new Set();globalThis.__holdWide=true;globalThis.__heldWide=0;globalThis.__releaseWide=null;fetch=async(...args)=>{let b;try{b=JSON.parse(args[1]?.body||'{}')}catch{}if(b?.op==='invoke'&&b.endpoint==='runWindow'&&b.input.operation==='surface-size'&&__holdWide){__holdWide=false;held.add(b.requestId);}const response=await base(...args);if(b?.op==='update'){const p=await response.clone().json();let changed=false;for(const row of p.results||[])if(held.delete(row.requestId)){__heldWide++;await new Promise(r=>__releaseWide=r);row.ok=false;delete row.result;row.error={code:'transport-interrupted'};changed=true;}if(changed)return new Response(JSON.stringify(p),{status:200,headers:{'Content-Type':'application/json'}});}return response;};}""");m.locator('[data-run-resolution]').select_option('640x360');page.wait_for_function('()=>__heldWide===1');fill(m,600,400,'보존할 가로 이름');page.evaluate('()=>__releaseWide()');expect(w.locator('[data-run-retry]')).to_be_visible();expect(m.locator('[data-run-width]')).to_have_value('600');assert len(changes())==1;m.locator('[data-dev-close]').click();w.locator('[data-run-retry]').click();expect(w.locator('[data-run-retry]')).to_be_hidden();m=menu(w);expect(m.locator('[data-run-width]')).to_have_value('600');expect(m.locator('[data-run-preset-name]')).to_have_value('보존할 가로 이름');assert len(changes())==1;step(w,m,640,360);f.checked('lost accepted fixed-wide reply preserves late custom/name input; read-only recovery does not replay command and explicit Step applies captured640x360')
 # Foreign/stale/over-budget requests do not affect the accepted wide pixels.
 for request in [dict(publisher='f'*32,sizeSequence=1,width=640,height=360),dict(publisher=changes()[0]['input']['publisher'],sizeSequence=0,width=640,height=360),dict(publisher=changes()[0]['input']['publisher'],sizeSequence=1,width=640,height=410)]:f.run('surface-size',row,False,command='d'*32,**request)
 dimensions(w,640,360);m=menu(w);m.locator('[data-run-size-apply]').click();expect(m.locator('[data-run-size-feedback]')).to_contain_text('다음 실제 출력');m.locator('form').evaluate('(el)=>{globalThis.__oldWideForm=el;globalThis.__oldWideSubmit=el.onsubmit;}');m.locator('[data-dev-close]').click();page.locator('[data-window-tab-close="'+key+'"]').click();expect(w).to_be_hidden();assert f.run('read',row)['closed'];fresh,newkey=open_run();count=len(changes());page.evaluate('()=>__oldWideSubmit({preventDefault(){},currentTarget:__oldWideForm})');page.wait_for_timeout(500);assert len(changes())==count;flush_presentation(page);page.close();f.stop();f.start(1);page=f.setup(browser);expect(page.locator('.window[data-key="'+newkey+'"] [data-run-play]')).to_be_enabled();expect(page.locator('#chat-input')).to_have_value('가로 요청 중 늦은 새 입력');assert not f.data(newkey)['handle'];f.checked('wide stale/foreign/area requests rejected; close disposes pending size owner and old form cannot affect sibling/cold runtime or original input')
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
print('RUN_WIDE_UI',f.root,flush=True)
