"""Actual explicitly opted-in software pixels; controlled packet faults are rejection tests only."""
import json,sys,time,traceback,hashlib,base64
from playwright.sync_api import sync_playwright,expect
sys.argv.append('--software-output')
import v666_run_fullscreen_fixture as f
mode=sys.argv[3];page=None

def open_run():
 page.get_by_role('tab',name='Workspace',exact=True).click();page.locator('#run').click();w=page.locator('.run-window:visible');expect(w.locator('[data-run-play]')).to_be_enabled();key=w.get_attribute('data-key');return page.locator('.window[data-key="'+key+'"]'),key

def pixels(w):return w.locator('[data-run-pixels]')
def snapshot(w):return pixels(w).evaluate('(c)=>({width:c.width,height:c.height,cursor:c.dataset.surfaceCursor,first:[...c.getContext("2d").getImageData(0,0,1,1).data],last:[...c.getContext("2d").getImageData(63,35,1,1).data]})')
def wait_pixel(w,n):
 expect(pixels(w)).to_be_visible();page.wait_for_function('(a)=>{const c=document.querySelector(`.window[data-key="${a.key}"] [data-run-pixels]`);return c&&!c.hidden&&c.getContext("2d").getImageData(0,0,1,1).data[0]===a.value}',arg={'key':w.get_attribute('data-key'),'value':n%256})
def start_pause(w,key):
 w.locator('[data-run-play]').click();expect(w.locator('.caption strong')).to_have_text('실행 중',timeout=180000);expect(w.locator('[data-run-pause]')).to_be_enabled();w.locator('[data-run-pause]').click();expect(w.locator('.caption strong')).to_have_text('일시 정지');expect(w.locator('[data-run-step]')).to_be_enabled();row=f.data(key);wait_pixel(w,int(row['control']['frame']));return row

def normal():
 page.locator('#chat-input').fill('영상 관찰은 권한이나 실행 조건이 아님 😀');w,key=open_run();expect(pixels(w)).to_be_hidden();row=start_pause(w,key);n=int(row['control']['frame']);s=snapshot(w);assert(s['width'],s['height'])==(64,36)and s['first']==[n%256,0,0,255]and s['last']==[n%256,252,245,255],s;f.checked('actual project-produced top-down RGBA reaches Run canvas with exact corner pixels and cooperative frame owner; no source rewrite')
 w.locator('[data-run-developer]').click();m=page.get_by_role('dialog',name='실행 개발 메뉴',exact=True);expect(m.locator('[data-run-resolution]')).to_be_disabled();expect(m.locator('[data-run-resolution]')).to_contain_text('64 × 36');expect(m.locator('[data-run-sound]')).to_be_disabled();m.locator('[data-run-debug="info"]').check();expect(w.locator('.run-debug-info')).to_contain_text('렌더 해상도: 64 × 36 px');expect(w.locator('.run-debug-info')).to_contain_text('렌더 FPS: 미지원');m.locator('[data-dev-close]').click();w.locator('[data-run-step]').click();expect(w.locator('[data-run-step]')).to_be_enabled();wait_pixel(w,n+1);assert f.data(key)['handle']==row['handle'];f.checked('Step publishes one actual output; readonly dimensions never invent render FPS/audio or change resolution/contract')
 # Repeat observations through one mounted view: bytes are never replayed by update.
 view=f.mount()
 try:
  def read(cursor=''):
   body={'op':'observe','view':view['view'],'scope':view['scope'],'endpoint':'runSurface','input':{'view':row['view'],'lease':row['lease'],'handle':row['handle'],'cursor':cursor}}
   for _ in range(200):
    p=f.raw(body)
    if p.get('error',{}).get('code')!='busy':return p
    time.sleep(.01)
   raise AssertionError(p)
  packet=read();assert packet['ok']and packet['result']['available'],packet;frame=packet['result'];raw=base64.urlsafe_b64decode(frame['pixels']+'='*((-len(frame['pixels']))%4));assert hashlib.sha256(raw).hexdigest()==frame['sha256']and len(raw)==64*36*4
  for _ in range(24):
   p=read(frame['cursor']);assert p['ok']and p['result']['unchanged']and'pixels'not in p['result'],p
   u=f.raw({'op':'update','view':view['view'],'scope':view['scope']});assert u.get('results',[])==[],u
  denied=f.raw({'op':'observe','view':view['view'],'scope':view['scope'],'endpoint':'runWindow','input':{'operation':'start'}});assert denied['error']['code']=='endpoint_denied';f.checked('24 unchanged reads omit image bytes and all retained request rows; same public read cannot invoke execution mutations')
 finally:f.raw({'op':'dispose','view':view['view']})
 w.locator('[data-run-maximize]').click();expect(pixels(w)).to_be_visible();page.keyboard.press('Escape');expect(pixels(w)).to_be_visible();second,other=open_run();expect(pixels(second)).to_be_hidden();page.locator('[data-window-tab="'+key+'"]').click();wait_pixel(w,n+1);assert f.data(key)['handle']==row['handle'];expect(page.locator('#chat-input')).to_have_value('영상 관찰은 권한이나 실행 조건이 아님 😀');f.checked('fullscreen and sibling tab lifecycle preserve exact owner and input without transferring pixels or starting another execution')
 w.locator('[data-run-play]').click();expect(w.locator('.caption strong')).to_have_text('실행 대기중');expect(pixels(w)).to_be_hidden();row2=start_pause(w,key);assert row2['handle']!=row['handle']and snapshot(w)['cursor'].split(':')[0]!=s['cursor'].split(':')[0];page.screenshot(path=str(f.root/'actual-software-pixels.png'));f.checked('Stop clears image; explicit restart creates a new handle and publisher epoch, never replays old pixels')

def lifecycle(browser):
 page.locator('#chat-input').fill('실패·닫기 후 남겨둘 입력');w,key=open_run();owner=start_pause(w,key)
 page.evaluate('''()=>{const base=fetch;globalThis.__corruptSurface=false;globalThis.__surfaceFaults=0;globalThis.__holdSurface=false;globalThis.__heldSurface=0;globalThis.__releaseSurface=null;fetch=async(...args)=>{let b;try{b=JSON.parse(args[1]?.body||'{}')}catch{}const response=await base(...args);if(b?.op==='observe'&&b.endpoint==='runSurface'){const p=await response.clone().json();if(p.ok&&p.result?.available){if(__corruptSurface){p.result.sha256='0'.repeat(64);__surfaceFaults++;return new Response(JSON.stringify(p),{status:200,headers:{'Content-Type':'application/json'}});}if(__holdSurface){__holdSurface=false;__heldSurface++;await new Promise(r=>__releaseSurface=r);}}}return response;};}''')
 page.evaluate('()=>__corruptSurface=true');page.wait_for_function('()=>__surfaceFaults>0');expect(pixels(w)).to_be_hidden();expect(w.locator('[data-run-step]')).to_be_enabled();page.evaluate('()=>__corruptSurface=false');wait_pixel(w,int(owner['control']['frame']));assert f.data(key)['handle']==owner['handle'];f.checked('malformed SHA response removes stale pixels but preserves actual execution/control; readonly retry recovers same owner')
 page.evaluate('()=>__holdSurface=true');page.wait_for_function('()=>__heldSurface===1');page.locator('[data-window-tab-close="'+key+'"]').click();expect(w).to_be_hidden(timeout=15000);fresh,newkey=open_run();expect(pixels(fresh)).to_be_hidden();page.evaluate('()=>__releaseSurface()');page.wait_for_timeout(700);expect(pixels(fresh)).to_be_hidden();assert f.run('read',owner)['closed'];expect(page.locator('#chat-input')).to_have_value('실패·닫기 후 남겨둘 입력');f.checked('close aborts held pixel delivery and stops owned process; retired response cannot paint a new Run or discard unrelated input')
 page.evaluate('()=>confectoryFlushPresentation()');presentation=json.dumps(f.state()['presentation']);assert'pixels'not in presentation and'surfaceCursor'not in presentation;page.close();f.stop();f.start(3);new=f.setup(browser);fresh=new.locator('.window[data-key="'+newkey+'"]');expect(fresh.locator('[data-run-play]')).to_be_enabled();expect(pixels(fresh)).to_be_hidden();assert not f.data(newkey)['handle'];expect(new.locator('#chat-input')).to_have_value('실패·닫기 후 남겨둘 입력');new.close();f.checked('cold engine restores layout/input with fresh idle owner, no transient pixels/cursor/lease or automatic execution')
try:
 f.start(0)
 with sync_playwright()as pw:
  expect.set_options(timeout=60000);browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=f.setup(browser)
  try:
   if mode=='normal':normal()
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
print('RUN_SURFACE_FIXTURE',f.root,flush=True)
