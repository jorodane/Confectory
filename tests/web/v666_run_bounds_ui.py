"""Actual bounded output + authored checkbox, resize and interrupted read lifecycle."""
import json,sys,time,traceback
from playwright.sync_api import sync_playwright,expect
sys.argv.append('--bounds-output')
import v666_run_fullscreen_fixture as f
mode=sys.argv[3];page=None
def open_run():
 page.get_by_role('tab',name='Workspace',exact=True).click();page.locator('#run').click();w=page.locator('.run-window:visible');expect(w.locator('[data-run-play]')).to_be_enabled();key=w.get_attribute('data-key');return page.locator('.window[data-key="'+key+'"]'),key
def menu(w):w.locator('[data-run-developer]').click();return page.get_by_role('dialog',name='실행 개발 메뉴',exact=True)
def geometry(w):
 page.wait_for_function('''key=>{const w=document.querySelector(`.window[data-key="${key}"]`),s=w.querySelector('.run-screen'),b=w.querySelector('[data-run-bounds]');if(!b||b.hidden||b.children.length!==2)return false;const box=b.getBoundingClientRect(),origin=s.getBoundingClientRect(),scale=Math.min(s.clientWidth/64,s.clientHeight/36),rects=[[4,4,16,12],[32,8,24,20]];if(Math.abs(box.width-64*scale)>1||Math.abs(box.height-36*scale)>1||Math.abs(box.left-origin.left-s.clientLeft-(s.clientWidth-64*scale)/2)>1||Math.abs(box.top-origin.top-s.clientTop-(s.clientHeight-36*scale)/2)>1)return false;return [...b.children].every((child,i)=>{const r=child.getBoundingClientRect(),p=rects[i];return Math.abs(r.left-box.left-p[0]*scale)<1&&Math.abs(r.top-box.top-p[1]*scale)<1&&Math.abs(r.width-p[2]*scale)<1&&Math.abs(r.height-p[3]*scale)<1&&getComputedStyle(child).outlineStyle==='dashed'&&getComputedStyle(b).pointerEvents==='none'});}''',arg=w.get_attribute('data-key'))
def starts():return [r for r in f.requests if r['endpoint']=='runWindow'and r['input']['operation']=='start']
def guard():
 f.original();assert not f.errors and not f.external,(f.errors,f.external)
 assert not {'editDraft','saveDraft','confirmDraft','startAI','prepareWorker','reviewDraft'}.intersection(r.get('endpoint')for r in f.requests)
try:
 f.start(0)
 with sync_playwright()as pw:
  expect.set_options(timeout=60000);browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=f.setup(browser)
  try:
   page.locator('#chat-input').fill('경계 표시는 실행 권한과 분리');w,key=open_run();m=menu(w);expect(m.locator('[data-run-debug="bounds"]')).to_be_disabled();m.locator('[data-dev-close]').click();w.locator('[data-run-play]').click();expect(w.locator('.caption strong')).to_have_text('실행 중',timeout=180000);w.locator('[data-run-pause]').click();expect(w.locator('[data-run-step]')).to_be_enabled();expect(w.locator('[data-run-pixels]')).to_be_visible();row=f.data(key);frame=row['control']['frame'];m=menu(w);expect(m.locator('[data-run-debug="bounds"]')).to_be_enabled();m.locator('[data-run-debug="bounds"]').check();m.locator('[data-dev-close]').click();geometry(w);assert f.run('read',row)['control']['frame']==frame;assert len(starts())==1;guard();page.screenshot(path=str(f.root/'actual-bounds.png'));f.checked('original bounds checkbox displays only producer rectangles aligned to exact rendered pixels; dashed accent/contain/click-through overlay never executes or acknowledges a frame')
   m=menu(w);m.locator('[data-run-debug="bounds"]').uncheck();expect(w.locator('[data-run-bounds]')).to_be_hidden();m.locator('[data-run-debug="bounds"]').check();m.locator('[data-dev-close]').click();geometry(w);page.set_viewport_size(dict(width=390,height=800));geometry(w);page.set_viewport_size(dict(width=1440,height=1000));geometry(w);guard();f.checked('repeat Off/On and narrow/wide viewport resize preserve the same pixel-space geometry and original input')
   if mode=='lifecycle':
    page.evaluate('''()=>{const base=fetch;globalThis.__badBounds=true;globalThis.__badBoundsPackets=0;globalThis.__holdBounds=false;globalThis.__heldBounds=false;globalThis.__releaseBounds=null;fetch=async(...args)=>{let q;try{q=JSON.parse(args[1]?.body||'{}')}catch{}const response=await base(...args);if(q?.op!=='observe'||q.endpoint!=='runSurface')return response;const p=await response.clone().json();if(!p.ok||!p.result?.available)return response;if(__badBounds){__badBoundsPackets++;p.result.bounds.rectangles[2]=999;return new Response(JSON.stringify(p),{status:200,headers:{'Content-Type':'application/json'}});}if(__holdBounds){__holdBounds=false;__heldBounds=true;await new Promise(resolve=>__releaseBounds=resolve);}return response;};}''');page.wait_for_function('()=>__badBoundsPackets>0');expect(w.locator('[data-run-bounds]')).to_be_hidden();expect(w.locator('[data-run-pixels]')).to_be_hidden();assert f.run('read',row)['control']['frame']==frame;page.locator('#chat-input').fill('거절 뒤 남길 새 입력');page.evaluate('()=>__badBounds=false');geometry(w);expect(page.locator('#chat-input')).to_have_value('거절 뒤 남길 새 입력');assert len(starts())==1;guard();f.checked('browser-only invalid coordinates remove stale bounds/pixels without mutating the real running owner; valid observation recovers and preserves newer input')
    page.evaluate('()=>{__holdBounds=true;__heldBounds=false;}');page.wait_for_function('()=>__heldBounds');page.locator('[data-window-tab-close="'+key+'"]').click();expect(w).to_be_hidden();fresh,newkey=open_run();page.evaluate('()=>__releaseBounds()');m=menu(fresh);expect(m.locator('[data-run-debug="bounds"]')).to_be_disabled();expect(m.locator('[data-run-debug="bounds"]')).not_to_be_checked();m.locator('[data-dev-close]').click();expect(fresh.locator('[data-run-bounds]')).to_be_hidden();assert not f.data(newkey)['handle'];assert len(starts())==1;guard();f.checked('late real read after close cannot draw in a sibling, revive the retired publisher or replay Start')
   else:
    sibling,other=open_run();m=menu(sibling);expect(m.locator('[data-run-debug="bounds"]')).not_to_be_checked();expect(m.locator('[data-run-debug="bounds"]')).to_be_disabled();m.locator('[data-dev-close]').click();page.locator('[data-window-tab="'+key+'"]').click();geometry(w);w.locator('[data-run-step]').click();expect(w.locator('[data-run-step]')).to_be_enabled();geometry(w);assert int(f.run('read',row)['control']['frame'])==int(frame)+1;assert len(starts())==1;w.locator('[data-run-play]').click();expect(w.locator('[data-run-bounds]')).to_be_hidden();guard();f.checked('sibling choices are isolated; explicit Step replaces one coherent frame and Stop removes all retired geometry')
   page.evaluate('()=>confectoryFlushPresentation()');wanted=page.locator('#chat-input').input_value();page.close();f.stop();f.start(1);page=f.setup(browser);expect(page.locator('#chat-input')).to_have_value(wanted)
   for node in page.locator('[data-run-bounds]').all():expect(node).to_be_hidden()
   for p in(f.root/'profile').rglob('*.json'):
    if p.parent.name=='presentations':assert 'rgba8-pixels-v1'not in p.read_text()and'runBoundsEnabled'not in p.read_text()
   guard();f.checked('cold restores private input/windows only, without geometry/publisher/checkbox replay or automatic execution');browser.close()
  except Exception:
   if page and not page.is_closed():
    try:page.screenshot(path=str(f.root/'failure.png'));(f.root/'failure.html').write_text(page.content())
    except Exception:pass
   raise
except Exception as error:
 (f.root/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:f.save_evidence();f.stop()
print('RUN_BOUNDS_UI',f.root,flush=True)
