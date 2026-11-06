"""Authored Run developer menu over actual owned execution/ACKs; no renderer/audio simulation."""
import json,sys,time,traceback,re
from playwright.sync_api import sync_playwright,expect
import v666_run_fullscreen_fixture as f
mode=sys.argv[3];page=None

def open_run():
 page.get_by_role('tab',name='Workspace',exact=True).click();page.locator('#run').click();w=page.locator('.run-window:visible');expect(w.locator('[data-run-play]')).to_be_enabled(timeout=60000);key=w.get_attribute('data-key');return page.locator('.window[data-key="'+key+'"]'),key

def menu(w):
 w.locator('[data-run-developer]').click();m=page.get_by_role('dialog',name='실행 개발 메뉴',exact=True);expect(m).to_be_visible();return m

def output(w):return w.locator('.run-debug-info')
def starts():return[r for r in f.requests if r['endpoint']=='runWindow'and r['input']['operation']=='start']
def unsupported(m):
 for selector in ['[data-run-resolution]','[data-run-debug="bounds"]','[data-run-debug="grid"]','[data-run-sound]','[data-run-sound-test]']:expect(m.locator(selector)).to_be_disabled()
 expect(m).to_contain_text('현재 호스트는 내장 렌더 화면과 해상도 제어를 제공하지 않아요.');expect(m).to_contain_text('프로젝트 오디오 backend가 연결되지 않았어요.')

def normal():
 page.locator('#chat-input').fill('디버그 표시는 실행 권한이 아님 😀');w,key=open_run();n=len(f.requests);m=menu(w);unsupported(m);expect(output(w)).to_be_hidden();m.locator('[data-run-debug="info"]').check();expect(output(w)).to_be_visible();expect(output(w)).to_contain_text('상태: 실행 대기');expect(output(w)).to_contain_text('렌더 FPS: 미지원');expect(output(w)).to_contain_text('렌더 해상도: 미지원');expect(output(w)).to_contain_text('오디오: 미지원');assert not starts();m.locator('[data-dev-close]').click();f.checked('original developer popover/checkbox shows factual idle diagnostics; unsupported resolution/render/audio cannot execute or manufacture preview/FPS/sound')
 w.locator('[data-run-play]').click();expect(w.locator('.caption strong')).to_have_text('실행 중',timeout=180000);expect(w.locator('[data-run-pause]')).to_be_enabled();w.locator('[data-run-pause]').click();expect(w.locator('.caption strong')).to_have_text('일시 정지');expect(w.locator('[data-run-step]')).to_be_enabled();before=f.data(key);frame=int(before['control']['frame']);expect(output(w)).to_contain_text('프레임: '+str(frame));expect(output(w)).to_contain_text('제어: 일시 정지');w.locator('[data-run-step]').click();expect(output(w)).to_contain_text('프레임: '+str(frame+1));expect(w.locator('[data-run-step]')).to_be_enabled();after=f.data(key);assert int(after['control']['frame'])==frame+1 and after['handle']==before['handle'];expect(output(w)).to_contain_text('명령 확인: '+str(after['control']['ack'])+' / '+str(after['control']['sequence']));f.checked('actual owned runtime Pause/one Step ACK drives exact frame and command diagnostics, with no computed render FPS or automatic source Confirm')
 m=menu(w);unsupported(m);m.locator('[data-dev-close]').click();w.locator('[data-run-maximize]').click();expect(w).to_have_class(re.compile('is-run-fullscreen'));m=menu(w);unsupported(m);box=m.bounding_box();assert box['x']>=0 and box['y']>=0;m.press('Escape');expect(m).to_be_hidden();expect(w).to_have_class(re.compile('is-run-fullscreen'));page.keyboard.press('Escape');expect(w).not_to_have_class(re.compile('is-run-fullscreen'));expect(output(w)).to_be_visible();f.checked('authored popover remains accessible above fullscreen; Escape closes only the top menu before restoring the same Run window')
 # Keep the flag per actual view; hidden sibling windows cannot alter each other.
 second,other=open_run();m=menu(second);expect(m.locator('[data-run-debug="info"]')).not_to_be_checked();m.locator('[data-dev-close]').click();expect(output(second)).to_be_hidden();page.locator('[data-window-tab="'+key+'"]').click();expect(output(w)).to_be_visible();assert f.data(key)['handle']==before['handle'];expect(page.locator('#chat-input')).to_have_value('디버그 표시는 실행 권한이 아님 😀');f.checked('debug visibility belongs to the exact Run view; sibling tabs preserve separate choices and unchanged process/inputs')
 page.set_viewport_size({'width':390,'height':800});m=menu(w);unsupported(m);box=m.bounding_box();assert box['x']>=0 and box['x']+box['width']<=391 and box['y']>=0;page.screenshot(path=str(f.root/'developer-narrow.png'));m.locator('[data-dev-close]').click();w.locator('[data-run-play]').click();expect(w.locator('.caption strong')).to_have_text('실행 대기중',timeout=60000);expect(output(w)).to_contain_text('프레임 제어: 확인할 수 없음');assert len(starts())==1;f.checked('390px viewport fits original menu; explicit Stop clears current frame claims and preserves source/input')

def lifecycle(browser):
 global page
 page.locator('#chat-input').fill('응답 실패 후 남겨둘 입력');w,key=open_run();m=menu(w);m.locator('[data-run-debug="info"]').check();m.locator('[data-dev-close]').click();w.locator('[data-run-play]').click();expect(w.locator('.caption strong')).to_have_text('실행 중',timeout=180000);expect(w.locator('[data-run-pause]')).to_be_enabled();w.locator('[data-run-pause]').click();expect(w.locator('[data-run-step]')).to_be_enabled();owner=f.data(key)
 page.evaluate('''()=>{const base=fetch,lost=new Set();globalThis.__loseRead=true;globalThis.__readLossInjected=0;globalThis.__denyClose=false;fetch=async(...args)=>{let body;try{body=JSON.parse(args[1]?.body||'{}')}catch{}if(body?.op==='invoke'&&body.endpoint==='runWindow'){if(body.input.operation==='read'&&__loseRead){__loseRead=false;lost.add(body.requestId);}if(body.input.operation==='close'&&__denyClose){body.input.lease='f'.repeat(32);args[1]={...args[1],body:JSON.stringify(body)};}}const response=await base(...args);if(body?.op==='update'){const result=await response.clone().json();let changed=false;for(const row of result.results||[])if(lost.delete(row.requestId)){__readLossInjected++;row.ok=false;row.error={code:'transport-interrupted'};delete row.result;changed=true;}if(changed)return new Response(JSON.stringify(result),{status:200,headers:{'Content-Type':'application/json'}});}return response;};}''')
 page.wait_for_function('()=>__readLossInjected===1');page.wait_for_timeout(1200);expect(w.locator('[data-run-retry]')).to_be_visible(timeout=10000);expect(output(w)).to_contain_text('상태: 확인 필요');expect(output(w)).not_to_contain_text('프레임:');w.locator('[data-run-retry]').click();expect(w.locator('[data-run-retry]')).to_be_hidden();expect(output(w)).to_contain_text('제어: 일시 정지');assert f.data(key)['handle']==owner['handle']and len(starts())==1;f.checked('lost actual read reply withholds stale current counters; explicit retry recovers same handle/ACK without replaying Start')
 m=menu(w);m.locator('[data-run-debug="info"]').evaluate('(el)=>{globalThis.__oldDebug=el;globalThis.__oldChange=el.onchange;}');page.evaluate('()=>__denyClose=true');m.locator('[data-dev-close]').click();page.locator('[data-window-tab-close="'+key+'"]').click();expect(w.locator('[data-run-retry]')).to_be_visible();expect(w).to_be_visible();assert f.run('read',owner)['state']=='running';expect(output(w)).to_be_visible();expect(page.locator('#chat-input')).to_have_value('응답 실패 후 남겨둘 입력');page.evaluate('()=>__denyClose=false');w.locator('[data-run-retry]').click();expect(w.locator('[data-run-retry]')).to_be_hidden();m=menu(w);expect(m.locator('[data-run-debug="info"]')).to_be_checked();m.locator('[data-dev-close]').click();page.locator('[data-window-tab-close="'+key+'"]').click();expect(w).to_be_hidden(timeout=60000);expect(page.locator('.run-dev-menu')).to_have_count(0);assert f.run('read',owner)['closed'];f.checked('denied close retains debug choice/process/input; explicit retry closes owned Run and disposes exact popover/observers')
 fresh,newkey=open_run();m=menu(fresh);expect(m.locator('[data-run-debug="info"]')).not_to_be_checked();page.evaluate('()=>{__oldDebug.checked=true;__oldChange({currentTarget:__oldDebug});}');expect(m.locator('[data-run-debug="info"]')).not_to_be_checked();expect(output(fresh)).to_be_hidden();m.locator('[data-run-debug="info"]').check();m.locator('[data-dev-close]').click();page.evaluate('()=>confectoryFlushPresentation()');assert 'runDebugInfo'not in json.dumps(f.state()['presentation']);assert len(starts())==1;f.checked('retired debug callback cannot mutate a new view; debug observation is transient and never private execution/lease data')
 global_page=page;global_page.close();f.stop();f.start(3);newpage=f.setup(browser);page=newpage;fresh=newpage.locator('.window[data-key="'+newkey+'"]');expect(fresh.locator('[data-run-play]')).to_be_enabled();expect(output(fresh)).to_be_hidden();assert not f.data(newkey)['handle'];expect(newpage.locator('#chat-input')).to_have_value('응답 실패 후 남겨둘 입력');newpage.close();f.checked('cold engine restores private geometry/input with fresh idle Run owner, not debug checkbox/handle/lease/automatic execution')

try:
 f.start(0)
 with sync_playwright()as pw:
  expect.set_options(timeout=60000);browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=f.setup(browser)
  try:
   if mode=='normal':normal()
   else:lifecycle(browser)
   f.original();assert not f.errors and not f.external,(f.errors,f.external)
   if not page.is_closed():page.screenshot(path=str(f.root/('developer-'+mode+'.png')));page.close()
   browser.close()
  except Exception:
   if not page.is_closed():
    try:(f.root/'fault-injection.json').write_text(json.dumps(page.evaluate('()=>({readLossInjected:globalThis.__readLossInjected??0,loseRead:globalThis.__loseRead??null})')));page.screenshot(path=str(f.root/'failure.png'),timeout=5000);(f.root/'failure.html').write_text(page.content())
    except Exception:pass
   raise
except Exception as error:
 (f.root/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc(),errors=f.errors),ensure_ascii=False));raise
finally:f.save_evidence();f.stop()
print('RUN_DEVELOPER_FIXTURE',f.root,flush=True)
