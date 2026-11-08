"""Explicit HD UI, multipart lifetime and actual frames; generated projects only."""
import json,sys,time,traceback,hashlib
from playwright.sync_api import sync_playwright,expect
sys.argv.append('--resizable-output')
import v666_run_fullscreen_fixture as f
mode=sys.argv[3];page=None
for manifest in f.projects:
 p=manifest.parent/'MainBody.celem';p.write_text(p.read_text().replace('Confectory.RunSurface::Open as OpenSurface','Confectory.RunSurface::OpenHD as OpenSurface'))
 p=manifest.parent/'Main.csbody';p.write_text(p.read_text().replace('Thread.Sleep(16)','Thread.Sleep(50)'))
f.before={str(p):p.read_bytes()for m in f.projects for p in m.parent.rglob('*')if p.is_file()}


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
 page.locator('#chat-input').fill('HD와 별개인 입력');w,key=open_run();row=start(w,key);frame=int(row['control']['frame']);m=menu(w)
 for choice,width,height in [('1280x720',1280,720),('720x1280',720,1280),('1024x768',1024,768)]:
  count=len(changes());m.locator('[data-run-resolution]').select_option(choice);expect(m.locator('[data-run-size-feedback]')).to_contain_text('다음 실제 출력');assert len(changes())==count+1 and int(f.run('read',row)['control']['frame'])==frame;step(w,m,width,height);frame+=1
  canvas=w.locator('[data-run-pixels]');rgba=canvas.evaluate('c=>[...c.getContext("2d").getImageData(10,20,1,1).data]');assert rgba[1:]==[40,140,255],rgba;m=menu(w)
 f.checked('authored landscapeHD, portraitHD and4:3 presets request one actual bounded output without automatic Resume/Step; real generated pixels arrive coherently after one explicit Step each')
 fill(m,1280,720,'내 HD 화면');m.locator('[data-run-preset-save]').click();wait_mode(m,'preset:');assert registry()['items'][0]['width']==1280;step(w,m,1280,720);m=menu(w);fill(m,1280,721,'지우지 않을 초과 입력');expect(m.locator('[data-run-size-apply]')).to_be_disabled();expect(m.locator('[data-run-preset-save]')).to_be_disabled();expect(m.locator('[data-run-width]')).to_have_value('1280');expect(m.locator('[data-run-height]')).to_have_value('721');page.screenshot(path=str(f.root/'actual-hd-output.png'));m.locator('[data-dev-close]').click();flush_presentation(page);page.close();f.stop();f.start(1);page=f.setup(browser);w=page.locator('.window[data-key="'+key+'"]');expect(w.locator('[data-run-play]')).to_be_enabled();assert registry()['items'][0]['width']==1280 and not f.data(key)['handle'];expect(page.locator('#chat-input')).to_have_value('HD와 별개인 입력');f.checked('HD private registration survives cold while live lease/pixels/command do not; out-of-budget requests preserve input and do not mutate source or silently resize')

def parts(browser):
 global page
 page.locator('#chat-input').fill('조각 전송과 별개인 새 입력');w,key=open_run();row=start(w,key);m=menu(w);m.locator('[data-run-resolution]').select_option('1280x720');step(w,m,1280,720)
 page.evaluate("""()=>{const base=fetch;globalThis.__badHD=true;globalThis.__badHDCount=0;fetch=async(...args)=>{let q;try{q=JSON.parse(args[1]?.body||'{}')}catch{}const response=await base(...args);if(!__badHD||q?.op!=='observe'||q.endpoint!=='runSurface'||!q.input?.cursor?.startsWith('slice:'))return response;const value=await response.clone().json();if(value.ok&&value.result?.available){__badHDCount++;const old=value.result.pixels;value.result.pixels=(old[0]==='A'?'B':'A')+old.slice(1);return new Response(JSON.stringify(value),{status:200,headers:{'Content-Type':'application/json'}});}return response;};}""")
 f.control(f.run('read',row),'step');page.wait_for_function('()=>__badHDCount>0');expect(w.locator('[data-run-pixels]')).to_be_hidden();expect(w.locator('[data-run-step]')).to_be_enabled();frame=int(f.run('read',row)['control']['frame']);page.locator('#chat-input').fill('손상 조각 뒤 새 입력');page.evaluate('()=>__badHD=false');dimensions(w,1280,720);assert int(f.run('read',row)['control']['frame'])==frame;expect(page.locator('#chat-input')).to_have_value('손상 조각 뒤 새 입력');f.checked('browser-only corrupted cached HD slices fail overall SHA and hide stale pixels; read-only observation recovers the same paused frame without replaying Step or erasing late input')
 page.evaluate("""()=>{const base=fetch;globalThis.__holdHD=true;globalThis.__heldHD=0;globalThis.__sliceHD=[];fetch=async(...args)=>{let q;try{q=JSON.parse(args[1]?.body||'{}')}catch{}const response=await base(...args);if(q?.op!=='observe'||q.endpoint!=='runSurface'||!q.input?.cursor?.startsWith('slice:'))return response;__sliceHD.push(q.input.cursor);if(__holdHD){__holdHD=false;__heldHD++;await new Promise(resolve=>__releaseHD=resolve);}return response;};}""")
 # A new real frame forces parts again; hold its first browser slice after native acceptance.
 f.control(f.run('read',row),'step');page.wait_for_function('()=>__heldHD===1');w.locator('[data-close]').click();page.evaluate('()=>__releaseHD()');page.wait_for_function('(key)=>!document.querySelector(`.window[data-key="${key}"]:not([hidden])`)',arg=key);fresh,newkey=open_run();expect(fresh.locator('[data-run-play]')).to_be_enabled();expect(fresh.locator('[data-run-pixels]')).to_be_hidden();assert f.run('read',row)['closed'];expect(page.locator('#chat-input')).to_have_value('손상 조각 뒤 새 입력');f.checked('actual accepted HD transfer interrupted by close aborts remaining slice requests, retires canvas/cache and cannot paint a new view or execute another project; unrelated input survives')
 flush_presentation(page);page.close();f.stop();f.start(1);page=f.setup(browser);expect(page.locator('.window[data-key="'+newkey+'"] [data-run-play]')).to_be_enabled();assert not f.data(newkey)['handle'];f.checked('cold restart after an interrupted HD transfer restores only presentation and never resumes pixels, slices or execution')

def lifecycle(browser):
 global page
 page.locator('#chat-input').fill('가로 요청 중 늦은 새 입력');w,key=open_run();row=start(w,key);m=menu(w);page.evaluate("""()=>{const base=fetch,held=new Set();globalThis.__holdWide=true;globalThis.__heldWide=0;globalThis.__releaseWide=null;fetch=async(...args)=>{let b;try{b=JSON.parse(args[1]?.body||'{}')}catch{}if(b?.op==='invoke'&&b.endpoint==='runWindow'&&b.input.operation==='surface-size'&&__holdWide){__holdWide=false;held.add(b.requestId);}const response=await base(...args);if(b?.op==='update'){const p=await response.clone().json();let changed=false;for(const row of p.results||[])if(held.delete(row.requestId)){__heldWide++;await new Promise(r=>__releaseWide=r);row.ok=false;delete row.result;row.error={code:'transport-interrupted'};changed=true;}if(changed)return new Response(JSON.stringify(p),{status:200,headers:{'Content-Type':'application/json'}});}return response;};}""");m.locator('[data-run-resolution]').select_option('1280x720');page.wait_for_function('()=>__heldWide===1');fill(m,600,400,'보존할 가로 이름');page.evaluate('()=>__releaseWide()');expect(w.locator('[data-run-retry]')).to_be_visible();expect(m.locator('[data-run-width]')).to_have_value('600');assert len(changes())==1;m.locator('[data-dev-close]').click();w.locator('[data-run-retry]').click();expect(w.locator('[data-run-retry]')).to_be_hidden();m=menu(w);expect(m.locator('[data-run-width]')).to_have_value('600');expect(m.locator('[data-run-preset-name]')).to_have_value('보존할 가로 이름');assert len(changes())==1;step(w,m,1280,720);f.checked('lost accepted fixed-HD reply preserves late custom/name input; read-only recovery does not replay command and explicit Step applies captured1280x720')
 # Foreign/stale/over-budget requests do not affect the accepted HD pixels.
 for request in [dict(publisher='f'*32,sizeSequence=1,width=640,height=360),dict(publisher=changes()[0]['input']['publisher'],sizeSequence=0,width=640,height=360),dict(publisher=changes()[0]['input']['publisher'],sizeSequence=1,width=1280,height=721)]:f.run('surface-size',row,False,command='d'*32,**request)
 dimensions(w,1280,720);m=menu(w);m.locator('[data-run-size-apply]').click();expect(m.locator('[data-run-size-feedback]')).to_contain_text('다음 실제 출력');m.locator('form').evaluate('(el)=>{globalThis.__oldWideForm=el;globalThis.__oldWideSubmit=el.onsubmit;}');m.locator('[data-dev-close]').click();page.locator('[data-window-tab-close="'+key+'"]').click();expect(w).to_be_hidden();assert f.run('read',row)['closed'];fresh,newkey=open_run();count=len(changes());page.evaluate('()=>__oldWideSubmit({preventDefault(){},currentTarget:__oldWideForm})');page.wait_for_timeout(500);assert len(changes())==count;flush_presentation(page);page.close();f.stop();f.start(1);page=f.setup(browser);expect(page.locator('.window[data-key="'+newkey+'"] [data-run-play]')).to_be_enabled();expect(page.locator('#chat-input')).to_have_value('가로 요청 중 늦은 새 입력');assert not f.data(newkey)['handle'];f.checked('HD stale/foreign/area requests rejected; close disposes pending size owner and old form cannot affect sibling/cold runtime or original input')
try:
 f.start(0)
 with sync_playwright()as pw:
  expect.set_options(timeout=60000);browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=f.setup(browser)
  try:
   if mode=='normal':normal(browser)
   elif mode=='lifecycle':lifecycle(browser)
   else:parts(browser)
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
print('RUN_HD_UI',f.root,flush=True)
