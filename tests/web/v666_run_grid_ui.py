"""Original named preset UI with real private storage and actual size receipts, never simulated pixels."""
import json,sys,time,traceback,hashlib
from playwright.sync_api import sync_playwright,expect
if sys.argv[3]!='unsupported':sys.argv.append('--resizable-output')
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

def grid(w):return w.locator('[data-run-grid]')
def mutating():return[x for x in f.requests if x['endpoint']=='runWindow'and x['input']['operation']not in ['open','read']]
def fits(w):
 page.wait_for_function("""key=>{const w=document.querySelector(`.window[data-key="${key}"]`),g=w.querySelector('[data-run-grid]'),c=w.querySelector('[data-run-pixels]');if(!g||g.hidden||!c||c.hidden)return false;const b=c.getBoundingClientRect(),v=g.getBoundingClientRect(),ratio=c.width/c.height,width=Math.min(b.width,b.height*ratio),height=width/ratio;return Math.abs(v.width-width)<.2&&Math.abs(v.height-height)<.2&&Math.abs(v.left-b.left-(b.width-width)/2)<.2&&Math.abs(v.top-b.top-(b.height-height)/2)<.2&&getComputedStyle(g).backgroundSize.split(',').every(value=>value.trim()==='10% 10%')&&getComputedStyle(g).pointerEvents==='none';}""",arg=w.get_attribute('data-key'))
def toggle(w,on=True):
 m=menu(w);expect(m.locator('[data-run-debug="bounds"]')).to_be_disabled();expect(m.locator('[data-run-debug="grid"]')).to_be_enabled();m.locator('[data-run-debug="grid"]').set_checked(on);m.locator('[data-dev-close]').click();return m

def floating(w,key):
 page.locator('#workspace-pack-tab').click();page.locator('[data-tab-order-key="window:'+key+'"]').drag_to(page.locator('#workspace'),target_position={'x':550,'y':210});expect(w).to_be_visible();assert w.evaluate('(el)=>el.parentElement.classList.contains("workspace-floating-window-layer")')

def normal(browser):
 global page
 page.locator('#chat-input').fill('실제 영상 위 그리드는 실행과 별개');w,key=open_run();m=menu(w);expect(m.locator('[data-run-debug="grid"]')).to_be_disabled();m.locator('[data-dev-close]').click();row=start(w,key);frame=int(row['control']['frame']);pixels=w.locator('[data-run-pixels]').evaluate('(el)=>el.toDataURL()');n=len(mutating());toggle(w);expect(grid(w)).to_be_visible();fits(w);assert grid(w).get_attribute('aria-hidden')=='true';assert grid(w).evaluate('(g)=>{const b=g.getBoundingClientRect();return document.elementFromPoint(b.left+b.width/2,b.top+b.height/2)!==g}');toggle(w,False);expect(grid(w)).to_be_hidden();toggle(w);fits(w);assert len(mutating())==n and w.locator('[data-run-pixels]').evaluate('(el)=>el.toDataURL()')==pixels and int(f.run('read',row)['control']['frame'])==frame;page.screenshot(path=str(f.root/'actual-run-grid.png'));f.checked('authored grid toggles over exact verified image contain box; transparent to pointer input, source pixels/frame/commands unchanged, element bounds remain unavailable')
 m=menu(w);fill(m,320,480,'변경하지 않을 이름');m.locator('[data-run-size-apply]').click();expect(m.locator('[data-run-size-feedback]')).to_contain_text('다음 실제 출력');fits(w);dimensions(w,64,36);step(w,m,320,480);fits(w);pixels=w.locator('[data-run-pixels]').evaluate('(el)=>el.toDataURL()');w.locator('[data-run-maximize]').click();expect(w.locator('[data-run-maximize]')).to_have_attribute('aria-pressed','true');fits(w);page.set_viewport_size({'width':390,'height':844});fits(w);page.set_viewport_size({'width':1440,'height':1000});fits(w);w.locator('[data-run-maximize]').click();fits(w);assert w.locator('[data-run-pixels]').evaluate('(el)=>el.toDataURL()')==pixels;f.checked('grid follows actual portrait pixels only after explicit Step and tracks maximize/restore/390px browser viewport without stretching pixels or claiming the requested size is already rendered')
 other,otherkey=open_run();expect(grid(w)).to_be_hidden();m=menu(other);expect(m.locator('[data-run-debug="grid"]')).not_to_be_checked();m.locator('[data-dev-close]').click();otherrow=start(other,otherkey);expect(grid(other)).to_be_hidden();page.locator('[data-window-tab="'+key+'"]').click();expect(grid(w)).to_be_visible();fits(w);m=menu(w);expect(m.locator('[data-run-debug="grid"]')).to_be_checked();m.locator('[data-run-debug="grid"]').evaluate('(el)=>{globalThis.__oldGrid=el;globalThis.__oldGridChange=el.onchange;}');m.locator('[data-dev-close]').click();page.locator('[data-window-tab-close="'+key+'"]').click();expect(grid(w)).to_have_count(0);page.evaluate('()=>{__oldGrid.checked=true;__oldGridChange({currentTarget:__oldGrid});}');expect(grid(other)).to_be_hidden();page.locator('[data-window-tab="'+otherkey+'"]').click();expect(other.locator('[data-run-pixels]')).to_be_visible();toggle(other);fits(other);flush_presentation(page);assert'runGridEnabled'not in json.dumps(f.state()['presentation']);page.close();f.stop();f.start(1);page=f.setup(browser);fresh=page.locator('.window[data-key="'+otherkey+'"]');expect(fresh.locator('[data-run-play]')).to_be_enabled();expect(grid(fresh)).to_be_hidden();m=menu(fresh);expect(m.locator('[data-run-debug="grid"]')).not_to_be_checked();expect(m.locator('[data-run-debug="grid"]')).to_be_disabled();expect(page.locator('#chat-input')).to_have_value('실제 영상 위 그리드는 실행과 별개');assert not f.data(otherkey)['handle'];f.checked('choice belongs to one live view; hidden sibling and retired callback cannot affect another, cold restores original input/layout without grid choice, process or lease replay')

def lifecycle(browser):
 page.locator('#chat-input').fill('그리드 오류와 새 입력 보존');w,key=open_run();row=start(w,key);toggle(w);fits(w);m=menu(w);fill(m,350,280,'실패 중 새 이름');m.locator('[data-dev-close]').click();n=len(mutating());page.evaluate("""()=>{const base=fetch;globalThis.__corruptGridSurface=true;globalThis.__denyGridClose=false;globalThis.__gridFaults=0;fetch=async(...args)=>{let b;try{b=JSON.parse(args[1]?.body||'{}')}catch{}if(b?.op==='invoke'&&b.endpoint==='runWindow'&&b.input.operation==='close'&&__denyGridClose){b.input.lease='f'.repeat(32);args[1]={...args[1],body:JSON.stringify(b)};}const response=await base(...args);if(b?.op==='observe'&&b.endpoint==='runSurface'&&__corruptGridSurface){const p=await response.clone().json();if(p.ok&&p.result?.available){__gridFaults++;p.result.sha256='0'.repeat(64);return new Response(JSON.stringify(p),{status:200,headers:{'Content-Type':'application/json'}});}}return response;};}""");page.wait_for_function('()=>__gridFaults>0');expect(grid(w)).to_be_hidden();expect(w.locator('[data-run-pixels]')).to_be_hidden();m=menu(w);expect(m.locator('[data-run-debug="grid"]')).to_be_checked();expect(m.locator('[data-run-debug="grid"]')).to_be_disabled();expect(m.locator('[data-run-width]')).to_have_value('350');expect(m.locator('[data-run-preset-name]')).to_have_value('실패 중 새 이름');m.locator('[data-dev-close]').click();assert len(mutating())==n and f.run('read',row)['handle']==row['handle'];page.evaluate('()=>__corruptGridSurface=false');expect(grid(w)).to_be_visible();fits(w);assert len(mutating())==n;f.checked('malformed image receipt hides grid with pixels while keeping per-view choice and late fields; normal existing observation recovers same live owner without executing or resizing anything')
 floating(w,key);w.locator('[data-fold]').click();page.wait_for_function('key=>document.querySelector(`.window[data-key="${key}"] [data-run-grid]`).hidden',arg=key);w.locator('[data-fold]').click();expect(grid(w)).to_be_visible();fits(w);page.evaluate('()=>__denyGridClose=true');w.locator('[data-close]').click();expect(w.locator('[data-run-retry]')).to_be_visible();expect(grid(w)).to_be_hidden();assert f.run('read',row)['state']=='running';page.evaluate('()=>__denyGridClose=false');w.locator('[data-run-retry]').click();expect(w.locator('[data-run-retry]')).to_be_hidden();expect(grid(w)).to_be_visible();fits(w);m=menu(w);expect(m.locator('[data-run-debug="grid"]')).to_be_checked();expect(m.locator('[data-run-width]')).to_have_value('350');expect(m.locator('[data-run-preset-name]')).to_have_value('실패 중 새 이름');m.locator('[data-dev-close]').click();w.locator('[data-close]').click();expect(grid(w)).to_have_count(0);assert f.run('read',row)['closed'];expect(page.locator('#chat-input')).to_have_value('그리드 오류와 새 입력 보존');f.checked('folding clears stale overlay; denied close preserves process/grid choice/input for explicit recovery; actual close disposes exact overlay and owner')

def unsupported(browser):
 w,key=open_run();m=menu(w);expect(m.locator('[data-run-debug="grid"]')).to_be_disabled();n=len(mutating());m.locator('[data-run-debug="grid"]').evaluate('(el)=>{el.disabled=false;el.checked=true;el.onchange({currentTarget:el});}');expect(m.locator('[data-run-debug="grid"]')).to_be_disabled();expect(m.locator('[data-run-debug="grid"]')).not_to_be_checked();expect(grid(w)).to_be_hidden();m.locator('[data-dev-close]').click();w.locator('[data-run-play]').click();expect(w.locator('.caption strong')).to_have_text('실행 중',timeout=180000);expect(w.locator('[data-run-pause]')).to_be_enabled();w.locator('[data-run-pause]').click();expect(w.locator('[data-run-step]')).to_be_enabled();m=menu(w);expect(m.locator('[data-run-debug="grid"]')).to_be_disabled();expect(m.locator('[data-run-debug="bounds"]')).to_be_disabled();assert len(mutating())==n+2;expect(grid(w)).to_be_hidden();f.checked('idle and actual frame-only project cannot manufacture a render grid; forged disabled DOM is reset without execution authority, element bounds stay unavailable')
try:
 f.start(0)
 with sync_playwright()as pw:
  expect.set_options(timeout=60000);browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=f.setup(browser)
  try:
   if mode=='normal':normal(browser)
   elif mode=='unsupported':unsupported(browser)
   else:lifecycle(browser)
   f.original();assert not f.errors and not f.external,(f.errors,f.external)
   if not page.is_closed():page.close()
   browser.close()
  except Exception:
   if not page.is_closed():
    try:page.screenshot(path=str(f.root/'failure.png'),timeout=5000);(f.root/'failure.html').write_text(page.content());(f.root/'grid-geometry.json').write_text(json.dumps(page.locator('[data-run-grid]').evaluate_all('(elements)=>elements.map(g=>({style:g.getAttribute(\"style\"),hidden:g.hidden,backgroundSize:getComputedStyle(g).backgroundSize,box:g.getBoundingClientRect().toJSON()}))'),indent=2))
    except Exception:pass
   raise
except Exception as error:
 (f.root/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc(),errors=f.errors),ensure_ascii=False));raise
finally:f.save_evidence();f.stop()
print('RUN_GRID_UI',f.root,flush=True)
