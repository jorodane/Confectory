"""Actual software output rate with read-only fault/late-response UI boundaries."""
import json,sys,time,traceback,re
from playwright.sync_api import sync_playwright,expect
sys.argv.append('--software-output')
import v666_run_fullscreen_fixture as f
mode=sys.argv[3];page=None
def open_run():
 page.get_by_role('tab',name='Workspace',exact=True).click();page.locator('#run').click();w=page.locator('.run-window:visible');expect(w.locator('[data-run-play]')).to_be_enabled();key=w.get_attribute('data-key');return page.locator('.window[data-key="'+key+'"]'),key
def show_info(w):
 w.locator('[data-run-developer]').click();m=page.get_by_role('dialog',name='실행 개발 메뉴',exact=True);m.locator('[data-run-debug="info"]').check();m.locator('[data-dev-close]').click()
def fps(w,positive=False):
 pattern=r'소프트웨어 출력 FPS: '+(r'[1-9]\d*\.\d'if positive else r'0\.0')+r' fps'
 expect(w.locator('.run-debug-info')).to_contain_text(re.compile(pattern),timeout=20000)
def starts():return [r for r in f.requests if r['endpoint']=='runWindow'and r['input']['operation']=='start']
def guard():
 f.original();assert not f.errors and not f.external,(f.errors,f.external)
 assert not {'editDraft','saveDraft','confirmDraft','startAI','prepareWorker','reviewDraft'}.intersection(r.get('endpoint')for r in f.requests)
try:
 f.start(0)
 with sync_playwright()as pw:
  expect.set_options(timeout=60000);browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=f.setup(browser)
  try:
   page.locator('#chat-input').fill('실제 출력 집계와 분리할 입력 😀');w,key=open_run();show_info(w);expect(w.locator('.run-debug-info')).to_contain_text('렌더 FPS: 미지원');w.locator('[data-run-play]').click();expect(w.locator('.caption strong')).to_have_text('실행 중',timeout=180000);expect(w.locator('[data-run-pixels]')).to_be_visible();fps(w,True);guard();page.screenshot(path=str(f.root/'actual-rate.png'));f.checked('actual authenticated producer publication FPS appears in the authored developer info; not a browser clock/poll count or cooperative frame counter')
   w.locator('[data-run-pause]').click();expect(w.locator('[data-run-step]')).to_be_enabled();fps(w);row=f.run('read',f.data(key));frame=row['control']['frame'];cursor=w.locator('[data-run-pixels]').get_attribute('data-surface-cursor');page.evaluate("()=>{const base=CanvasRenderingContext2D.prototype.putImageData;globalThis.__ratePixelPaints=0;CanvasRenderingContext2D.prototype.putImageData=function(...a){__ratePixelPaints++;return base.apply(this,a)}}")
   page.wait_for_timeout(1200);fps(w);assert f.run('read',row)['control']['frame']==frame;assert w.locator('[data-run-pixels]').get_attribute('data-surface-cursor')==cursor;assert page.evaluate('__ratePixelPaints')==0;guard();f.checked('paused rate decays to zero from real idle time; metadata-only observations preserve pixels without canvas redraw, heartbeat/ACK or automatic Step')
   w.locator('[data-run-step]').click();expect(w.locator('[data-run-step]')).to_be_enabled();fps(w,True);fps(w);assert int(f.run('read',row)['control']['frame'])==int(frame)+1;assert len(starts())==1;guard();f.checked('one explicit Step publishes one real frame and a temporary measured rate then returns to zero without automatic execution')
   if mode=='lifecycle':
    page.evaluate('''()=>{const base=fetch;globalThis.__badRate=true;globalThis.__badRatePackets=0;globalThis.__holdRate=false;globalThis.__heldRate=false;globalThis.__releaseRate=null;fetch=async(...args)=>{let q;try{q=JSON.parse(args[1]?.body||'{}')}catch{}const response=await base(...args);if(q?.op!=='observe'||q.endpoint!=='runSurface')return response;const p=await response.clone().json();if(!p.ok||!p.result?.available)return response;if(__badRate){__badRatePackets++;p.result.renderRate.frames='-1';return new Response(JSON.stringify(p),{status:200,headers:{'Content-Type':'application/json'}});}if(__holdRate){__holdRate=false;__heldRate=true;await new Promise(resolve=>__releaseRate=resolve);}return response;};}''')
    page.wait_for_function('()=>__badRatePackets>0');expect(w.locator('[data-run-pixels]')).to_be_hidden();expect(w.locator('.run-debug-info')).to_contain_text('렌더 FPS: 미지원');assert f.run('read',row)['control']['frame']==str(int(frame)+1);assert len(starts())==1;page.locator('#chat-input').fill('거절 뒤 새로 보존할 입력');page.evaluate('()=>__badRate=false');expect(w.locator('[data-run-pixels]')).to_be_visible();fps(w);expect(page.locator('#chat-input')).to_have_value('거절 뒤 새로 보존할 입력');guard();f.checked('browser-only malformed-rate rejection removes stale numeric display and pixels without stopping/restarting the real owner; next valid observation recovers and preserves newer input')
    page.evaluate('()=>{__holdRate=true;__heldRate=false;}');page.wait_for_function('()=>__heldRate');page.locator('[data-window-tab-close="'+key+'"]').click();expect(w).to_be_hidden();fresh,newkey=open_run();show_info(fresh);page.evaluate('()=>__releaseRate()');page.wait_for_timeout(500);expect(fresh.locator('.run-debug-info')).to_contain_text('렌더 FPS: 미지원');assert not f.data(newkey)['handle'];assert len(starts())==1;guard();f.checked('late actual read response is fenced after close and cannot populate sibling owner diagnostics or replay Start')
   else:
    w.locator('[data-run-play]').click();expect(w.locator('.caption strong')).to_have_text('실행 대기중');expect(w.locator('.run-debug-info')).to_contain_text('렌더 FPS: 미지원');expect(w.locator('[data-run-pixels]')).to_be_hidden();w.locator('[data-run-play]').click();expect(w.locator('.caption strong')).to_have_text('실행 중',timeout=180000);fps(w,True);assert f.data(key)['handle']!=row['handle'];assert len(starts())==2;guard();f.checked('explicit Stop clears the retired rate and a new Start observes only its new publisher; no restored software clock')
   page.evaluate('()=>confectoryFlushPresentation()');wanted=page.locator('#chat-input').input_value();page.close();f.stop();f.start(1);page=f.setup(browser);expect(page.locator('#chat-input')).to_have_value(wanted)
   for candidate in page.locator('.run-window').all():expect(candidate.locator('.run-debug-info')).to_have_count(1);assert '소프트웨어 출력 FPS:'not in candidate.locator('.run-debug-info').inner_text()
   for p in(f.root/'profile').rglob('*.json'):
    if p.parent.name=='presentations':assert 'renderRate'not in p.read_text()and'software-present-v1'not in p.read_text()
   guard();f.checked('cold restores private windows/input only, never rate samples, publisher identity or automatic execution');browser.close()
  except Exception:
   if page and not page.is_closed():
    try:page.screenshot(path=str(f.root/'failure.png'));(f.root/'failure.html').write_text(page.content())
    except Exception:pass
   raise
except Exception as error:
 (f.root/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:f.save_evidence();f.stop()
print('RUN_RATE_UI',f.root,flush=True)
