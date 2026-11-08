"""Authored fixed choices against real producer limits and frames; generated projects only."""
import json,sys,time,traceback
from playwright.sync_api import sync_playwright,expect
sys.argv.append('--resizable-output')
import v666_run_fullscreen_fixture as f
mode=sys.argv[3];page=None;profile=mode if mode in ['hd','fhd']else'qhd';symbol={'hd':'OpenHD','fhd':'OpenFHD','qhd':'OpenQHD'}[profile];limits={'hd':(1280,921600),'fhd':(1920,2073600),'qhd':(2560,3686400)}[profile]
for manifest in f.projects:
 p=manifest.parent/'MainBody.celem';p.write_text(p.read_text().replace('Confectory.RunSurface::Open as OpenSurface','Confectory.RunSurface::'+symbol+' as OpenSurface'))
 p=manifest.parent/'Main.csbody';p.write_text(p.read_text().replace('Thread.Sleep(16)','Thread.Sleep(50)'))
f.before={str(p):p.read_bytes()for m in f.projects for p in m.parent.rglob('*')if p.is_file()}
choices=[('PC · 가로',[('640x360','640 × 360'),('1280x720','HD · 1280 × 720'),('1920x1080','FHD · 1920 × 1080'),('2560x1440','QHD / 2K · 2560 × 1440'),('3840x2160','4K UHD · 3840 × 2160'),('1024x768','4:3 · 1024 × 768')]),('시네마',[('2048x1080','DCI 2K · 2048 × 1080'),('4096x2160','DCI 4K · 4096 × 2160')]),('휴대폰 · 세로',[('720x1280','HD · 720 × 1280'),('1080x1920','FHD · 1080 × 1920'),('1080x2340','FHD+ · 1080 × 2340'),('1080x2400','FHD+ · 1080 × 2400'),('1179x2556','1179 × 2556'),('1290x2796','1290 × 2796'),('1440x3200','QHD+ · 1440 × 3200')])]
def open_run():
 page.get_by_role('tab',name='Workspace',exact=True).click();page.locator('#run').click();w=page.locator('.run-window:visible');expect(w.locator('[data-run-play]')).to_be_enabled();key=w.get_attribute('data-key');return page.locator('.window[data-key="'+key+'"]'),key
def menu(w):
 w.locator('[data-run-developer]').click();m=page.get_by_role('dialog',name='실행 개발 메뉴',exact=True);expect(m).to_be_visible();expect(m.locator('[data-run-preset-refresh]')).to_be_enabled();return m
def start(w,key):
 w.locator('[data-run-play]').click();expect(w.locator('.caption strong')).to_have_text('실행 중',timeout=180000);expect(w.locator('[data-run-pause]')).to_be_enabled();w.locator('[data-run-pause]').click();expect(w.locator('[data-run-step]')).to_be_enabled();expect(w.locator('[data-run-pixels]')).to_be_visible();return f.run('read',f.data(key))
def changes():return[x for x in f.requests if x['endpoint']=='runWindow'and x['input']['operation']=='surface-size']
def dimensions(w,width,height):page.wait_for_function('(a)=>{const c=document.querySelector(`.window[data-key="${a.key}"] [data-run-pixels]`);return c&&!c.hidden&&c.width===a.width&&c.height===a.height}',arg={'key':w.get_attribute('data-key'),'width':width,'height':height})
def step(w,m,width,height):
 m.locator('[data-dev-close]').click();w.locator('[data-run-step]').click();expect(w.locator('[data-run-step]')).to_be_enabled();dimensions(w,width,height)
def flush():page.wait_for_function("()=>typeof globalThis.confectoryFlushPresentation==='function'");page.evaluate('()=>confectoryFlushPresentation()')
def assert_menu(m):
 observed=m.locator('[data-run-resolution] optgroup').evaluate_all('(groups)=>groups.map(g=>[g.label,[...g.children].map(o=>[o.value,o.textContent,o.disabled])])');assert len(observed)==3,observed
 for (label,items),(actual,rows)in zip(choices,observed):
  assert actual==label and len(rows)==len(items),(label,rows)
  for (value,title),(v,t,disabled)in zip(items,rows):
   width,height=map(int,value.split('x'));assert(v,t)==(value,title)and disabled==(width>limits[0]or height>limits[0]or width*height>limits[1]),(profile,value,disabled)
 f.checked(profile+' exact authored15 option/group/order/text and actual max-axis/max-pixel availability; no invented resolution or silent lower-profile enlargement')
def normal(browser):
 global page
 page.locator('#chat-input').fill('메뉴 변경과 별개인 입력');w,key=open_run();row=start(w,key);frame=int(row['control']['frame']);m=menu(w);assert_menu(m)
 for value in (['2048x1080','1080x2340','1080x2400','1179x2556','2048x1080']if profile=='qhd'else['1280x720']if profile=='hd'else['1080x1920']):
  width,height=map(int,value.split('x'));count=len(changes());m.locator('[data-run-resolution]').select_option(value);expect(m.locator('[data-run-size-feedback]')).to_contain_text('다음 실제 출력');assert len(changes())==count+1 and int(f.run('read',row)['control']['frame'])==frame
  # Even a forced disabled change while the prior command waits cannot enqueue another request.
  m.locator('[data-run-resolution]').evaluate('(s)=>{s.value="1080x2400";s.dispatchEvent(new Event("change"));}');assert len(changes())==count+1;step(w,m,width,height);frame+=1
  rgba=w.locator('[data-run-pixels]').evaluate('c=>[...c.getContext("2d").getImageData(10,20,1,1).data]');assert rgba[1:]==[40,140,255],rgba;m=menu(w)
 f.checked(profile+' real producer frames match accepted fixed dimensions/color and ACK after explicit Step only; pending duplicate refused and repeat after ACK works')
 for value in [value for _,items in choices for value,_ in items if (lambda d:d[0]>limits[0]or d[1]>limits[0]or d[0]*d[1]>limits[1])(tuple(map(int,value.split('x'))))]:
  count=len(changes());m.locator('[data-run-resolution]').evaluate('(s,v)=>{s.value=v;s.dispatchEvent(new Event("change"));}',value);assert len(changes())==count
 assert int(f.run('read',row)['control']['frame'])==frame;expect(page.locator('#chat-input')).to_have_value('메뉴 변경과 별개인 입력');page.screenshot(path=str(f.root/('fixed-menu-'+profile+'.png')));m.locator('[data-dev-close]').click();flush();page.close();f.stop();f.start(1);page=f.setup(browser);w=page.locator('.window[data-key="'+key+'"]');expect(w.locator('[data-run-play]')).to_be_enabled();expect(w.locator('[data-run-pixels]')).to_be_hidden();assert not f.data(key)['handle'];expect(page.locator('#chat-input')).to_have_value('메뉴 변경과 별개인 입력');f.checked('unsupported fixed choices remain disabled and forced events issue no command; cold restores presentation/input without live frame, lease or auto execution')
def lifecycle(browser):
 global page
 page.locator('#chat-input').fill('응답 유실과 별개인 입력');w,key=open_run();row=start(w,key);m=menu(w)
 page.evaluate("""()=>{const base=fetch,held=new Set();globalThis.__holdSize=true;globalThis.__heldSize=0;fetch=async(...args)=>{let q;try{q=JSON.parse(args[1]?.body||'{}')}catch{}if(q?.op==='invoke'&&q.endpoint==='runWindow'&&q.input.operation==='surface-size'&&__holdSize){__holdSize=false;held.add(q.requestId);}const response=await base(...args);if(q?.op==='update'){const p=await response.clone().json();let changed=false;for(const row of p.results||[])if(held.delete(row.requestId)){__heldSize++;await new Promise(resolve=>__releaseSize=resolve);row.ok=false;delete row.result;row.error={code:'transport-interrupted'};changed=true;}if(changed)return new Response(JSON.stringify(p),{status:200,headers:{'Content-Type':'application/json'}});}return response;};}""")
 m.locator('[data-run-resolution]').select_option('2048x1080');page.wait_for_function('()=>__heldSize===1');m.locator('[data-run-resolution]').select_option('custom');m.locator('[data-run-width]').fill('600');m.locator('[data-run-height]').fill('400');m.locator('[data-run-preset-name]').fill('늦은 입력 보존');page.evaluate('()=>__releaseSize()');expect(w.locator('[data-run-retry]')).to_be_visible();assert len(changes())==1;m.locator('[data-dev-close]').click();w.locator('[data-run-retry]').click();expect(w.locator('[data-run-retry]')).to_be_hidden();m=menu(w);expect(m.locator('[data-run-width]')).to_have_value('600');expect(m.locator('[data-run-height]')).to_have_value('400');expect(m.locator('[data-run-preset-name]')).to_have_value('늦은 입력 보존');assert len(changes())==1;step(w,m,2048,1080);f.checked('new cinema choice accepted before lost reply preserves late custom/name input; explicit read-only recovery never repeats command and one Step consumes captured2048x1080')
 m=menu(w);m.locator('[data-run-resolution]').select_option('1179x2556');expect(m.locator('[data-run-size-feedback]')).to_contain_text('다음 실제 출력');m.locator('[data-run-resolution]').evaluate('(s)=>{globalThis.__oldChoice=s;globalThis.__oldChange=s.onchange;}');m.locator('[data-dev-close]').click();page.locator('[data-window-tab-close="'+key+'"]').click();expect(w).to_be_hidden();assert f.run('read',row)['closed'];fresh,newkey=open_run();count=len(changes());page.evaluate('()=>{__oldChoice.value="1080x2400";__oldChange();}');page.wait_for_timeout(350);assert len(changes())==count;expect(fresh.locator('[data-run-pixels]')).to_be_hidden();flush();page.close();f.stop();f.start(1);page=f.setup(browser);expect(page.locator('.window[data-key="'+newkey+'"] [data-run-play]')).to_be_enabled();assert not f.data(newkey)['handle'];expect(page.locator('#chat-input')).to_have_value('응답 유실과 별개인 입력');f.checked('closing pending new portrait choice retires owner; stale selection handler cannot affect sibling, project or cold execution; unrelated input/source preserved')
try:
 f.start(0)
 with sync_playwright()as pw:
  expect.set_options(timeout=60000);browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=f.setup(browser)
  try:
   lifecycle(browser)if mode=='lifecycle'else normal(browser)
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
print('RUN_RESOLUTIONS_UI',f.root,flush=True)
