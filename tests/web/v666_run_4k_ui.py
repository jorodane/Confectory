"""Explicit 4K UI, multipart lifetime and actual frames; generated projects only."""
import json,sys,time,traceback,hashlib
from playwright.sync_api import sync_playwright,expect
sys.argv.append('--resizable-output')
import v666_run_fullscreen_fixture as f
mode=sys.argv[3];page=None
for manifest in f.projects:
 p=manifest.parent/'MainBody.celem';p.write_text(p.read_text().replace('Confectory.RunSurface::Open as OpenSurface','Confectory.RunSurface::Open4K as OpenSurface'))
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
def cold_row(key,previous):
 # A restored Play button can precede dispatch of the fresh native open reply.
 # Require a new native lease and idle receipt, never the last pre-restart row.
 observations=[]
 for attempt in range(600):
  rows=[row for row in f.traffic if row['view']==key[13:]];row=rows[-1]if rows else None
  if row and row['lease']!=previous:
   assert row['state']=='idle'and not row['handle']and not row.get('lastCommand'),row
   (f.root/('cold-'+key[13:]+'.json')).write_text(json.dumps(dict(previousLease=previous,row=row,waits=attempt),indent=2));return row
  if attempt%50==0:observations.append(row)
  page.wait_for_timeout(20)
 raise AssertionError(dict(reason='fresh cold native lease not observed',observations=observations))
def flush_presentation(p):
 p.wait_for_function("()=>typeof globalThis.confectoryFlushPresentation==='function'");p.evaluate('()=>confectoryFlushPresentation()')
def step(w,m,width,height):
 m.locator('[data-dev-close]').click();w.locator('[data-run-step]').click();expect(w.locator('[data-run-step]')).to_be_enabled();dimensions(w,width,height)

def normal(browser):
 global page
 page.locator('#chat-input').fill('4K와 별개인 입력');w,key=open_run();row=start(w,key);frame=int(row['control']['frame']);m=menu(w)
 assert m.locator('optgroup:not([label="등록한 해상도"]) option').count()==15 and m.locator('optgroup:not([label="등록한 해상도"]) option:disabled').count()==0
 for choice,width,height in [('3840x2160',3840,2160),('4096x2160',4096,2160),('1290x2796',1290,2796),('1440x3200',1440,3200)]:
  count=len(changes());m.locator('[data-run-resolution]').select_option(choice);expect(m.locator('[data-run-size-feedback]')).to_contain_text('다음 실제 출력');assert len(changes())==count+1 and int(f.run('read',row)['control']['frame'])==frame;step(w,m,width,height);frame+=1
  canvas=w.locator('[data-run-pixels]');rgba=canvas.evaluate('c=>[...c.getContext("2d").getImageData(10,20,1,1).data]');assert rgba[1:]==[40,140,255],rgba;m=menu(w)
 f.checked('authored UHD/DCI4K and two large portrait choices request one actual bounded output without automatic Resume/Step; real generated pixels arrive coherently after one explicit Step each')
 fill(m,4096,2160,'내 4K 화면');m.locator('[data-run-preset-save]').click();wait_mode(m,'preset:');assert registry()['items'][0]['width']==4096;step(w,m,4096,2160);m=menu(w);fill(m,4096,2161,'지우지 않을 초과 입력');expect(m.locator('[data-run-size-apply]')).to_be_disabled();expect(m.locator('[data-run-preset-save]')).to_be_disabled();expect(m.locator('[data-run-width]')).to_have_value('4096');expect(m.locator('[data-run-height]')).to_have_value('2161');page.screenshot(path=str(f.root/'actual-4k-output.png'));m.locator('[data-dev-close]').click();previous=f.data(key)['lease'];flush_presentation(page);page.close();f.stop();f.start(1);page=f.setup(browser);w=page.locator('.window[data-key="'+key+'"]');expect(w.locator('[data-run-play]')).to_be_enabled();cold_row(key,previous);assert registry()['items'][0]['width']==4096;expect(page.locator('#chat-input')).to_have_value('4K와 별개인 입력');f.checked('4K private registration survives cold while live lease/pixels/command do not; out-of-budget requests preserve input and do not mutate source or silently resize')

def parts(browser):
 global page
 page.locator('#chat-input').fill('조각 전송과 별개인 새 입력');w,key=open_run();row=start(w,key);m=menu(w);m.locator('[data-run-resolution]').select_option('4096x2160');step(w,m,4096,2160)
 page.evaluate("""()=>{const base=fetch;globalThis.__bad4K=true;globalThis.__bad4KCount=0;fetch=async(...args)=>{let q;try{q=JSON.parse(args[1]?.body||'{}')}catch{}const response=await base(...args);if(!__bad4K||q?.op!=='observe'||q.endpoint!=='runSurface'||!q.input?.cursor?.startsWith('slice:'))return response;const value=await response.clone().json();if(value.ok&&value.result?.available){__bad4KCount++;const old=value.result.pixels;value.result.pixels=(old[0]==='A'?'B':'A')+old.slice(1);return new Response(JSON.stringify(value),{status:200,headers:{'Content-Type':'application/json'}});}return response;};}""")
 f.control(f.run('read',row),'step');page.wait_for_function('()=>__bad4KCount>0');expect(w.locator('[data-run-pixels]')).to_be_hidden();expect(w.locator('[data-run-step]')).to_be_enabled();frame=int(f.run('read',row)['control']['frame']);page.locator('#chat-input').fill('손상 조각 뒤 새 입력');page.evaluate('()=>__bad4K=false');dimensions(w,4096,2160);assert int(f.run('read',row)['control']['frame'])==frame;expect(page.locator('#chat-input')).to_have_value('손상 조각 뒤 새 입력');f.checked('browser-only corrupted cached 4K slices fail overall SHA and hide stale pixels; read-only observation recovers the same paused frame without replaying Step or erasing late input')
 page.evaluate("""()=>{const base=fetch;globalThis.__hold4K=true;globalThis.__held4K=0;globalThis.__slice4K=[];fetch=async(...args)=>{let q;try{q=JSON.parse(args[1]?.body||'{}')}catch{}const response=await base(...args);if(q?.op!=='observe'||q.endpoint!=='runSurface'||!q.input?.cursor?.startsWith('slice:'))return response;__slice4K.push(q.input.cursor);if(__hold4K){__hold4K=false;__held4K++;await new Promise(resolve=>__release4K=resolve);}return response;};}""")
 # A new real frame forces parts again; hold its first browser slice after native acceptance.
 f.control(f.run('read',row),'step');page.wait_for_function('()=>__held4K===1');page.locator('[data-window-tab-close="'+key+'"]').click();page.evaluate('()=>__release4K()');page.wait_for_function('(key)=>!document.querySelector(`.window[data-key="${key}"]:not([hidden])`)',arg=key);fresh,newkey=open_run();expect(fresh.locator('[data-run-play]')).to_be_enabled();expect(fresh.locator('[data-run-pixels]')).to_be_hidden();assert f.run('read',row)['closed'];expect(page.locator('#chat-input')).to_have_value('손상 조각 뒤 새 입력');f.checked('actual accepted 4K transfer interrupted by close aborts remaining slice requests, retires canvas/cache and cannot paint a new view or execute another project; unrelated input survives')
 previous=f.data(newkey)['lease'];flush_presentation(page);page.close();f.stop();f.start(1);page=f.setup(browser);expect(page.locator('.window[data-key="'+newkey+'"] [data-run-play]')).to_be_enabled();cold_row(newkey,previous);f.checked('cold restart after an interrupted 4K transfer restores only presentation and never resumes pixels, slices or execution')

def lifecycle(browser):
 global page
 page.locator('#chat-input').fill('가로 요청 중 늦은 새 입력');w,key=open_run();row=start(w,key);m=menu(w);page.evaluate("""()=>{const base=fetch,held=new Set();globalThis.__holdWide=true;globalThis.__heldWide=0;globalThis.__releaseWide=null;fetch=async(...args)=>{let b;try{b=JSON.parse(args[1]?.body||'{}')}catch{}if(b?.op==='invoke'&&b.endpoint==='runWindow'&&b.input.operation==='surface-size'&&__holdWide){__holdWide=false;held.add(b.requestId);}const response=await base(...args);if(b?.op==='update'){const p=await response.clone().json();let changed=false;for(const row of p.results||[])if(held.delete(row.requestId)){__heldWide++;await new Promise(r=>__releaseWide=r);row.ok=false;delete row.result;row.error={code:'transport-interrupted'};changed=true;}if(changed)return new Response(JSON.stringify(p),{status:200,headers:{'Content-Type':'application/json'}});}return response;};}""");m.locator('[data-run-resolution]').select_option('4096x2160');page.wait_for_function('()=>__heldWide===1');fill(m,600,400,'보존할 가로 이름');page.evaluate('()=>__releaseWide()');expect(w.locator('[data-run-retry]')).to_be_visible();expect(m.locator('[data-run-width]')).to_have_value('600');assert len(changes())==1;m.locator('[data-dev-close]').click();w.locator('[data-run-retry]').click();expect(w.locator('[data-run-retry]')).to_be_hidden();m=menu(w);expect(m.locator('[data-run-width]')).to_have_value('600');expect(m.locator('[data-run-preset-name]')).to_have_value('보존할 가로 이름');assert len(changes())==1;step(w,m,4096,2160);f.checked('lost accepted fixed-4K reply preserves late custom/name input; read-only recovery does not replay command and explicit Step applies captured4096x2160')
 # Foreign/stale/over-budget requests do not affect the accepted 4K pixels.
 for request in [dict(publisher='f'*32,sizeSequence=1,width=640,height=360),dict(publisher=changes()[0]['input']['publisher'],sizeSequence=0,width=640,height=360),dict(publisher=changes()[0]['input']['publisher'],sizeSequence=1,width=4096,height=2161)]:f.run('surface-size',row,False,command='d'*32,**request)
 dimensions(w,4096,2160);m=menu(w);m.locator('[data-run-size-apply]').click();expect(m.locator('[data-run-size-feedback]')).to_contain_text('다음 실제 출력');m.locator('form').evaluate('(el)=>{globalThis.__oldWideForm=el;globalThis.__oldWideSubmit=el.onsubmit;}');m.locator('[data-dev-close]').click();page.locator('[data-window-tab-close="'+key+'"]').click();expect(w).to_be_hidden();assert f.run('read',row)['closed'];fresh,newkey=open_run();count=len(changes());page.evaluate('()=>__oldWideSubmit({preventDefault(){},currentTarget:__oldWideForm})');page.wait_for_timeout(500);assert len(changes())==count;previous=f.data(newkey)['lease'];flush_presentation(page);page.close();f.stop();f.start(1);page=f.setup(browser);expect(page.locator('.window[data-key="'+newkey+'"] [data-run-play]')).to_be_enabled();cold_row(newkey,previous);expect(page.locator('#chat-input')).to_have_value('가로 요청 중 늦은 새 입력');f.checked('4K stale/foreign/area requests rejected; close disposes pending size owner and old form cannot affect sibling/cold runtime or original input')
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
print('RUN_4K_UI',f.root,flush=True)
