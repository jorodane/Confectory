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
def wait_mode(m,prefix):page.wait_for_function('(p)=>document.querySelector(\'[role="dialog"][aria-label="실행 개발 메뉴"] [data-run-resolution]\').value.startsWith(p)',arg=prefix)
def step(w,m,width,height):
 m.locator('[data-dev-close]').click();w.locator('[data-run-step]').click();expect(w.locator('[data-run-step]')).to_be_enabled();dimensions(w,width,height)

def normal(browser):
 page.locator('#chat-input').fill('등록 해상도와 실제 실행·원본은 독립');w,key=open_run();row=start(w,key);frame=int(row['control']['frame']);m=menu(w);fill(m,320,240,'내 화면 <safe>');m.locator('[data-run-preset-save]').click();wait_mode(m,'preset:');saved=registry();assert len(saved['items'])==1;item=saved['items'][0];assert item['name']=='내 화면 <safe>';expect(m.locator('[data-run-preset-name]')).to_have_value('');expect(m.locator('[data-run-size-feedback]')).to_contain_text('다음 실제 출력');assert len(changes())==1 and len(writes())==1;dimensions(w,64,36);assert int(f.run('read',row)['control']['frame'])==frame;f.checked('original register saves one project-private stable ID then sends one separate size request; paused frame/ACK and 64x36 actual pixels do not advance automatically')
 step(w,m,320,240);m=menu(w);expect(m.locator('optgroup[label="등록한 해상도"] option')).to_have_text('내 화면 <safe> · 320 × 240');fill(m,400,256,'내 화면 <safe>');m.locator('[data-run-preset-save]').click();expect(m.locator('[data-run-preset-retry]')).to_be_visible();expect(m.locator('[data-run-preset-name]')).to_have_value('내 화면 <safe>');expect(m.locator('[data-run-width]')).to_have_value('400');assert registry()['revision']==saved['revision']and len(changes())==1;m.locator('[data-run-preset-refresh]').click();expect(m.locator('[data-run-preset-save]')).to_be_enabled();fill(m,320,240,'내 화면 <safe>');m.locator('[data-run-preset-save]').click();wait_mode(m,'preset:');assert registry()['revision']==saved['revision']and len(registry()['items'])==1;expect(m.locator('[data-run-size-feedback]')).to_contain_text('다음 실제 출력');assert len(changes())==2;step(w,m,320,240);f.checked('name/dimension conflict preserves typed input and committed list; explicit refresh then same-name/same-size registration selects the original ID without rewriting storage')
 other,otherkey=open_run();otherrow=start(other,otherkey);om=menu(other);om.locator('[data-run-resolution]').select_option('preset:'+item['id']);expect(om.locator('[data-run-size-feedback]')).to_contain_text('다음 실제 출력');assert len(changes())==3 and changes()[-1]['input']['view']==otherrow['view'];om.locator('[data-dev-close]').click();page.locator('[data-window-tab="'+key+'"]').click();m=menu(w);m.locator('[data-run-preset-remove]').click();expect(m.locator('[data-run-preset-feedback]')).to_contain_text('삭제했어요');assert not registry()['items']and len(changes())==3;dimensions(w,320,240);m.locator('[data-dev-close]').click();page.locator('[data-window-tab="'+otherkey+'"]').click();om=menu(other);expect(om.locator('[data-run-resolution]')).to_have_value('custom');expect(om.locator('[data-run-width]')).to_have_value('320');step(other,om,320,240);f.checked('registered list is shared by actual sibling Run views in one private project; delete preserves applied and pending outputs, remaining view keeps target dimensions and actual Step still acknowledges them')
 om=menu(other);fill(om,350,280,'복원할 화면');om.locator('[data-run-preset-save]').click();wait_mode(om,'preset:');committed=registry();assert len(committed['items'])==1;page.screenshot(path=str(f.root/'actual-presets.png'));om.locator('[data-dev-close]').click();page.evaluate('()=>confectoryFlushPresentation()');page.close();f.stop();f.start(1);fresh=f.setup(browser);fresh.locator('.work-body').wait_for();assert registry()['items']==committed['items'];expect(fresh.locator('#chat-input')).to_have_value('등록 해상도와 실제 실행·원본은 독립');assert not f.data(otherkey)['handle'];fresh.close();f.checked('cold restores committed project registrations and original chat/layout, with no process or runtime size command replay')

def lifecycle(browser):
 global page
 page.locator('#chat-input').fill('저장 실패와 늦은 새 입력 보존');w,key=open_run();row=start(w,key);m=menu(w);fill(m,320,240,'처음 등록');page.evaluate('''()=>{const base=fetch,held=new Set();globalThis.__holdPreset=true;globalThis.__heldPreset=0;globalThis.__releasePreset=null;fetch=async(...args)=>{let b;try{b=JSON.parse(args[1]?.body||'{}')}catch{}if(b?.op==='invoke'&&b.endpoint==='runPresets'&&__holdPreset){__holdPreset=false;held.add(b.requestId);}const response=await base(...args);if(b?.op==='update'){const p=await response.clone().json();let changed=false;for(const row of p.results||[])if(held.delete(row.requestId)){__heldPreset++;await new Promise(r=>__releasePreset=r);row.ok=false;delete row.result;row.error={code:'transport-interrupted'};changed=true;}if(changed)return new Response(JSON.stringify(p),{status:200,headers:{'Content-Type':'application/json'}});}return response;};}''');m.locator('[data-run-preset-save]').click();page.wait_for_function('()=>__heldPreset===1');m.locator('[data-run-width]').fill('480');m.locator('[data-run-height]').fill('256');m.locator('[data-run-preset-name]').fill('늦은 새 이름');page.evaluate('()=>__releasePreset()');expect(m.locator('[data-run-preset-retry]')).to_be_visible();expect(m.locator('[data-run-preset-name]')).to_have_value('늦은 새 이름');accepted=registry();assert len(accepted['items'])==1 and not changes();m.locator('[data-run-preset-retry]').click();expect(m.locator('[data-run-preset-retry]')).to_be_hidden();expect(m.locator('[data-run-preset-feedback]')).to_contain_text('새 입력은 유지');expect(m.locator('[data-run-width]')).to_have_value('480');assert registry()['revision']==accepted['revision']and len(writes())==2 and writes()[0]['input']['command']==writes()[1]['input']['command']and not changes();f.checked('lost accepted registration reply preserves late name/size; explicit same-command receipt recovery does not duplicate registration, rewrite storage or apply stale captured dimensions')
 m.locator('[data-run-preset-save]').click();wait_mode(m,'preset:');second=registry();assert len(second['items'])==2 and len(changes())==1;page.evaluate('()=>__holdPreset=true');m.locator('[data-run-preset-remove]').click();page.wait_for_function('()=>__heldPreset===2');m.locator('[data-run-resolution]').select_option('custom');m.locator('[data-run-width]').fill('350');m.locator('[data-run-height]').fill('280');m.locator('[data-run-preset-name]').fill('삭제 뒤 새 입력');page.evaluate('()=>__releasePreset()');expect(m.locator('[data-run-preset-retry]')).to_be_visible();removed=registry();assert len(removed['items'])==1;m.locator('[data-run-preset-retry]').click();expect(m.locator('[data-run-preset-retry]')).to_be_hidden();assert registry()['revision']==removed['revision']and len(changes())==1;expect(m.locator('[data-run-width]')).to_have_value('350');expect(m.locator('[data-run-preset-name]')).to_have_value('삭제 뒤 새 입력');step(w,m,480,256);f.checked('lost accepted delete replays only its receipt; late fields remain and previously pending runtime output applies unchanged on one explicit Step')
 m=menu(w);fill(m,350,280,'닫기 전 등록');page.evaluate('()=>__holdPreset=true');m.locator('[data-run-preset-save]').click();page.wait_for_function('()=>__heldPreset===3');m.locator('[data-run-preset-save]').evaluate('(button)=>{globalThis.__oldPresetSave=button.onclick;}');m.locator('[data-dev-close]').click();page.locator('[data-window-tab-close="'+key+'"]').click();page.evaluate('()=>__releasePreset()');expect(w).to_be_hidden();count=len(writes());fresh,newkey=open_run();page.evaluate('()=>__oldPresetSave()');page.wait_for_timeout(600);assert len(writes())==count and len(changes())==1;committed=registry();assert len(committed['items'])==2;expect(page.locator('#chat-input')).to_have_value('저장 실패와 늦은 새 입력 보존');page.evaluate('()=>confectoryFlushPresentation()');page.close();f.stop();f.start(1);page=f.setup(browser);expect(page.locator('#chat-input')).to_have_value('저장 실패와 늦은 새 입력 보존');assert registry()['items']==committed['items']and not f.data(newkey)['handle'];f.checked('close during accepted preference save cannot resize a retired Run; old handler cannot mutate sibling; cold keeps committed registrations/input without old runtime command replay')
 page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(f.projects[1]);f.start(2);page=f.setup(browser);other=registry();assert not other['items'];other_listing=f.state()['listingId'];page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(f.projects[0]);f.start(3);page=f.setup(browser);first_listing=f.state()['listingId'];assert registry()['items']==committed['items'];page.evaluate('()=>confectoryFlushPresentation()');f.call('leaveProject',{});f.call('openProject',{'id':other_listing});page.reload();f.goto_editor(page,f.url);page.locator('.work-body').wait_for();assert not registry()['items'];f.call('leaveProject',{});f.call('openProject',{'id':first_listing});page.reload();f.goto_editor(page,f.url);page.locator('.work-body').wait_for();assert registry()['items']==committed['items'];expect(page.locator('#chat-input')).to_have_value('저장 실패와 늦은 새 입력 보존');f.checked('actual registered ProjectContext round trip isolates private preset files and original input; selection never creates a grant or automatic size request')
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
print('RUN_PRESETS_UI',f.root,flush=True)
