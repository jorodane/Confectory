"""Explicit producer size request is acknowledged only by real new pixels. No implicit Step."""
import json,sys,time,traceback
from playwright.sync_api import sync_playwright,expect
sys.argv.append('--resizable-output')
import v666_run_fullscreen_fixture as f
mode=sys.argv[3];page=None

def open_run():
 page.get_by_role('tab',name='Workspace',exact=True).click();page.locator('#run').click();w=page.locator('.run-window:visible');expect(w.locator('[data-run-play]')).to_be_enabled();key=w.get_attribute('data-key');return page.locator('.window[data-key="'+key+'"]'),key

def menu(w):
 w.locator('[data-run-developer]').click();m=page.get_by_role('dialog',name='실행 개발 메뉴',exact=True);expect(m).to_be_visible();return m

def start(w,key):
 w.locator('[data-run-play]').click();expect(w.locator('.caption strong')).to_have_text('실행 중',timeout=180000);expect(w.locator('[data-run-pause]')).to_be_enabled();w.locator('[data-run-pause]').click();expect(w.locator('[data-run-step]')).to_be_enabled();expect(w.locator('[data-run-pixels]')).to_be_visible();return f.run('read',f.data(key))

def fill(m,width,height):
 m.locator('[data-run-width]').fill(str(width));m.locator('[data-run-height]').fill(str(height))
def dimensions(w,width,height):
 page.wait_for_function('(a)=>{const c=document.querySelector(`.window[data-key="${a.key}"] [data-run-pixels]`);return c&&!c.hidden&&c.width===a.width&&c.height===a.height}',arg={'key':w.get_attribute('data-key'),'width':width,'height':height})
def changes():return[x for x in f.requests if x['endpoint']=='runWindow'and x['input']['operation']=='surface-size']
def surface(row):
 v=f.mount()
 try:
  for _ in range(200):
   p=f.raw({'op':'observe','view':v['view'],'scope':v['scope'],'endpoint':'runSurface','input':{'view':row['view'],'lease':row['lease'],'handle':row['handle']}})
   if p.get('ok'):return p['result']
   assert p.get('error',{}).get('code')=='busy',p;time.sleep(.01)
  raise AssertionError(p)
 finally:f.raw({'op':'dispose','view':v['view']})

def normal():
 page.locator('#chat-input').fill('해상도는 명시적 출력 요청이며 작업 도착 조건이 아님');w,key=open_run();row=start(w,key);frame=int(row['control']['frame']);initial=surface(row);assert initial['resize']['sequence']==0;dimensions(w,64,36);m=menu(w);expect(m.locator('[data-run-resolution]')).to_be_enabled();m.locator('[data-run-resolution]').select_option('custom');fill(m,320,240);assert not changes();m.locator('[data-run-size-apply]').click();expect(m.locator('[data-run-size-feedback]')).to_contain_text('다음 실제 출력');expect(m.locator('[data-run-size-apply]')).to_be_disabled();page.wait_for_timeout(1000);dimensions(w,64,36);pending=surface(row);assert pending['resize']['sequence']==1 and pending['resize']['ack']==0;observed=f.run('read',row);assert int(observed['control']['frame'])==frame and observed['control']['ack']==row['control']['ack']and observed['control']['mode']=='paused',(frame,row['control'],observed['control']);f.checked('original custom form sends one owned request; paused output stays 64x36 with separate pending size receipt and unchanged frame/ACK, no automatic execution')
 # Old CAS and foreign ownership never reach another update.
 for values in [{'publisher':'f'*32,'sizeSequence':1,'width':320,'height':240},{'publisher':initial['runtime'],'sizeSequence':0,'width':320,'height':240},{'publisher':initial['runtime'],'sizeSequence':1,'width':513,'height':240}]:f.run('surface-size',row,False,command='c'*32,**values)
 assert surface(row)['resize']==pending['resize'];m.locator('[data-dev-close]').click();w.locator('[data-run-step]').click();expect(w.locator('[data-run-step]')).to_be_enabled();dimensions(w,320,240);actual=surface(row);assert actual['resize']['sequence']==actual['resize']['ack']==1 and int(f.run('read',row)['control']['frame'])==frame+1;f.checked('stale publisher/size CAS and out-of-budget native requests are rejected; one explicit Step renders and acknowledges actual 320x240 pixels')
 m=menu(w);expect(m.locator('[data-run-size-feedback]')).to_contain_text('출력을 확인');fill(m,239,240);n=len(changes());m.locator('[data-run-size-apply]').click();assert len(changes())==n;fill(m,512,512);m.locator('[data-run-size-apply]').click();expect(m.locator('[data-run-size-feedback]')).to_contain_text('다음 실제 출력');m.locator('[data-dev-close]').click();w.locator('[data-run-step]').click();expect(w.locator('[data-run-step]')).to_be_enabled();dimensions(w,512,512);maximal=surface(row);assert maximal['resize']['ack']==2;page.screenshot(path=str(f.root/'actual-resolution.png'));f.checked('HTML bounds do not dispatch invalid input; maximum 512x512 full-SHA image is acknowledged only after another real Step')
 m=menu(w);fill(m,350,280);m.locator('[data-dev-close]').click();other,otherkey=open_run();om=menu(other);expect(om.locator('[data-run-resolution]')).to_be_disabled();om.locator('[data-dev-close]').click();page.locator('[data-window-tab="'+key+'"]').click();m=menu(w);expect(m.locator('[data-run-width]')).to_have_value('350');expect(m.locator('[data-run-height]')).to_have_value('280');m.locator('[data-dev-close]').click();assert len(changes())==2;expect(page.locator('#chat-input')).to_have_value('해상도는 명시적 출력 요청이며 작업 도착 조건이 아님');w.locator('[data-run-play]').click();expect(w.locator('[data-run-pixels]')).to_be_hidden();fresh=start(w,key);assert fresh['handle']!=row['handle'];dimensions(w,64,36);assert surface(fresh)['resize']['sequence']==0;f.checked('unsubmitted fields survive sibling/menu round trips, never affect another Run; Stop/restart resets runtime size without replaying requests or rewriting source')

def lifecycle(browser):
 global page
 page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(f.projects[1]);f.start(-1);page=f.setup(browser);other_listing=f.state()['listingId'];page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(f.projects[0]);f.start(2);page=f.setup(browser);first_listing=f.state()['listingId']
 page.locator('#chat-input').fill('응답 유실·닫기 후 남겨둘 새 입력');w,key=open_run();row=start(w,key);frame=int(row['control']['frame']);m=menu(w);m.locator('[data-run-resolution]').select_option('custom');fill(m,320,240)
 page.evaluate('''()=>{const base=fetch,held=new Set();globalThis.__holdSize=true;globalThis.__heldSize=0;globalThis.__releasedSize=null;globalThis.__denyClose=false;fetch=async(...args)=>{let b;try{b=JSON.parse(args[1]?.body||'{}')}catch{}if(b?.op==='invoke'&&b.endpoint==='runWindow'){if(b.input.operation==='surface-size'&&__holdSize){__holdSize=false;held.add(b.requestId);}if(b.input.operation==='close'&&__denyClose){b.input.lease='f'.repeat(32);args[1]={...args[1],body:JSON.stringify(b)};}}const response=await base(...args);if(b?.op==='update'){const p=await response.clone().json();let changed=false;for(const row of p.results||[])if(held.delete(row.requestId)){__heldSize++;await new Promise(r=>__releasedSize=r);row.ok=false;delete row.result;row.error={code:'transport-interrupted'};changed=true;}if(changed)return new Response(JSON.stringify(p),{status:200,headers:{'Content-Type':'application/json'}});}return response;};}''')
 m.locator('[data-run-size-apply]').click();page.wait_for_function('()=>__heldSize===1');fill(m,480,256);page.evaluate('()=>__releasedSize()');expect(w.locator('[data-run-retry]')).to_be_visible();expect(m.locator('[data-run-size-feedback]')).to_contain_text('입력은 보존');expect(m.locator('[data-run-width]')).to_have_value('480');expect(m.locator('[data-run-height]')).to_have_value('256');assert len(changes())==1;pending=surface(row);assert pending['resize']['sequence']==1 and pending['resize']['ack']==0;assert int(f.run('read',row)['control']['frame'])==frame;m.locator('[data-dev-close]').click();w.locator('[data-run-retry]').click();expect(w.locator('[data-run-retry]')).to_be_hidden();assert len(changes())==1;m=menu(w);expect(m.locator('[data-run-width]')).to_have_value('480');expect(m.locator('[data-run-height]')).to_have_value('256');expect(m.locator('[data-run-size-feedback]')).to_contain_text('다음 실제 출력');m.locator('[data-dev-close]').click();w.locator('[data-run-step]').click();expect(w.locator('[data-run-step]')).to_be_enabled();dimensions(w,320,240);f.checked('lost accepted size reply preserves late fields; explicit read reconciles same pending receipt without replay or Step, actual next Step applies original request only')
 m=menu(w);m.locator('[data-run-size-apply]').click();expect(m.locator('[data-run-size-feedback]')).to_contain_text('다음 실제 출력');page.evaluate('()=>__denyClose=true');m.locator('[data-dev-close]').click();page.locator('[data-window-tab-close="'+key+'"]').click();expect(w.locator('[data-run-retry]')).to_be_visible();assert f.run('read',row)['state']=='running';w.locator('[data-run-retry]').click();expect(w.locator('[data-run-retry]')).to_be_hidden();m=menu(w);expect(m.locator('[data-run-width]')).to_have_value('480');expect(m.locator('[data-run-height]')).to_have_value('256');m.locator('form').evaluate('(form)=>{globalThis.__oldSizeForm=form;globalThis.__oldSizeSubmit=form.onsubmit;}');page.evaluate('()=>__denyClose=false');m.locator('[data-dev-close]').click();page.locator('[data-window-tab-close="'+key+'"]').click();expect(w).to_be_hidden();assert f.run('read',row)['closed'];fresh,newkey=open_run();expect(fresh.locator('[data-run-pixels]')).to_be_hidden();page.evaluate('()=>__oldSizeSubmit({preventDefault(){},currentTarget:__oldSizeForm})');assert len(changes())==2;page.evaluate('()=>confectoryFlushPresentation()');f.call('leaveProject',{});f.call('openProject',{'id':other_listing});page.reload();f.goto_editor(page,f.url);page.locator('.work-body').wait_for();f.run('surface-size',row,False,publisher=pending['runtime'],sizeSequence=1,command='d'*32,width=240,height=240);f.call('leaveProject',{});f.call('openProject',{'id':first_listing});page.reload();f.goto_editor(page,f.url);page.locator('.work-body').wait_for();expect(page.locator('#chat-input')).to_have_value('응답 유실·닫기 후 남겨둘 새 입력');f.checked('retired form cannot submit; another registered ProjectContext rejects the old publisher/view and preserves separate input');page.evaluate('()=>confectoryFlushPresentation()');page.close();f.stop();f.start(3);new=f.setup(browser);fresh=new.locator('.window[data-key="'+newkey+'"]');expect(fresh.locator('[data-run-play]')).to_be_enabled();expect(fresh.locator('[data-run-pixels]')).to_be_hidden();assert not f.data(newkey)['handle'];expect(new.locator('#chat-input')).to_have_value('응답 유실·닫기 후 남겨둘 새 입력');new.close();f.checked('denied close retains process/fields/input; actual close discards pending runtime request without implicit frame, cold restores layout/input with no command or process replay')
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
print('RUN_RESOLUTION_FIXTURE',f.root,flush=True)
