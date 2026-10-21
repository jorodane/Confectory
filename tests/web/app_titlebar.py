"""Shipped titlebar renderer vs v508 oracle; isolated native bridge and display profile.

This does not execute Win32/WebView2 windowing or any account/provider action.
"""
import http.server,json,pathlib,re,sys,tempfile,threading,zipfile
from playwright.sync_api import sync_playwright,expect

repo=pathlib.Path(sys.argv[1]).resolve();out=pathlib.Path(tempfile.mkdtemp(prefix='confectory-titlebar-ui-'))
ui=repo/'examples/editor-home/ui'
original=zipfile.ZipFile(repo/'reference/site-ui/Confectory-Editor-Prototype-v508.zip').read('Confectory-v508/dist/app.js').decode()
styles='\n'.join((ui/n).read_text() for n in ('style.css','consumer.css','runtime.css'))
styles=re.sub(r'@import\s+url\([^)]*\)\s*;','',styles)
icons=original[original.index('function appWindowIcon('):original.index('function syncAppWindowSize(')]
setup=original[original.index(" const group=document.createElement('div');group.className='app-window-controls'"):original.index(';syncAppWindowSize();',original.index('function setupAppWindowControls('))+1]
form=original[original.index('`<form id="my-info-form"'):original.index('`,(root,close)=>',original.index('function openMyInfo('))][1:]
base='''<header class="topbar"><button class="brand" data-window-no-drag><span class="mark">C</span><span class="brand-name">Confectory</span></button><div class="right"><button class="app-settings-button" aria-label="설정 열기"><svg viewBox="0 0 24 24"><path d="m9 3-.6 2.1-1.8 1L4.5 5.6 2 9.9l1.5 1.6v2L2 15.1l2.5 4.3 2.1-.5 1.8 1L9 22h6l.6-2.1 1.8-1 2.1.5 2.5-4.3-1.5-1.6v-2L22 9.9l-2.5-4.3-2.1.5-1.8-1L15 3Z"/><circle cx="12" cy="12.5" r="3.5"/></svg><span>설정</span></button></div></header>'''
bootstrap='''
globalThis.calls=[];globalThis.toasts=[];globalThis.hold=false;globalThis.held=[];globalThis.saveHold=false;globalThis.saveFail=false;globalThis.saves=0;
globalThis.nativeState={customCaption:false,state:'normal'};
globalThis.profile={status:'ready',revision:'missing',value:{version:1,name:'나',title:'',status:'',introduction:'',icon:'👤'}};
globalThis.listeners=[];globalThis.chrome={webview:{addEventListener:(n,cb)=>listeners.push(cb)}};
globalThis.eventState=(value)=>{nativeState={...nativeState,...value};for(const cb of listeners)cb({data:{type:'confectory-window-state',state:{...nativeState}}});};
globalThis.confectoryWebUI={windowChromeSupported:true,windowCommand:async(command,enabled)=>{calls.push({command,enabled});if(hold)await new Promise(r=>held.push(r));if(command==='chrome')nativeState.customCaption=enabled;if(command==='toggle-maximize')nativeState.state=nativeState.state==='maximized'?'normal':'maximized';if(command==='minimize')nativeState.state='minimized';return {ok:true,state:{...nativeState}};}};
globalThis.modal=(title,html,cb)=>{document.querySelector('#overlays').innerHTML='<div class="modal-shade"><section class="modal participant-create-dialog"><div class="modal-head"><h2>'+title+'</h2><button data-close>×</button></div>'+html+'</section></div>';const root=document.querySelector('.modal'),close=()=>root.parentElement.remove();root.querySelector('[data-close]').onclick=close;cb?.(root,close);};
globalThis.$=(s,r=document)=>r.querySelector(s);globalThis.esc=v=>{const d=document.createElement('div');d.textContent=String(v??'');return d.innerHTML;};
globalThis.api={$,esc,modal,toast:t=>toasts.push(t),loadProfile:async()=>structuredClone(profile),saveProfile:async input=>{saves++;if(saveHold)await new Promise(r=>globalThis.releaseSave=r);if(saveFail)return {status:'unavailable'};profile={status:'ready',revision:'saved-'+saves,value:input.value};return structuredClone(profile);}};
'''
class Handler(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(repo),**kw)
 def log_message(self,*a):pass
 def do_GET(self):
  if self.path=='/fixture':
   data=('<style>'+styles+'</style><main id="app"></main><div id="overlays"></div>').encode();self.send_response(200);self.end_headers();self.wfile.write(data)
  else:super().do_GET()
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();url='http://127.0.0.1:'+str(server.server_port)
checks=[];errors=[];geometry=[]
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page(viewport={'width':1280,'height':892});page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(url+'/fixture');page.add_script_tag(content=bootstrap)
  page.evaluate('html=>document.querySelector("#app").innerHTML=html',base)
  # Oracle executes only exact original DOM construction. Never old prototype window actions.
  page.add_script_tag(content=icons+'''const right=$('.topbar>.right');const mine=document.createElement('button');mine.className='app-my-info-button';mine.setAttribute('aria-label','내 정보 열기');mine.innerHTML='<span class="my-header-avatar" aria-hidden="true">👤</span><span>내 정보</span>';right.prepend(mine);'''+setup)
  rects="() => ['.topbar','.app-my-info-button','.app-settings-button','.app-window-controls','[data-app-minimize]','[data-app-maximize]','[data-app-close]'].map(s=>{const e=document.querySelector(s),r=e.getBoundingClientRect();return {selector:s,x:r.x,y:r.y,width:r.width,height:r.height,html:s==='.topbar'?undefined:e.innerHTML};})"
  oracle=page.evaluate(rects);page.screenshot(path=str(out/'v508-titlebar.png'))
  page.evaluate('html=>document.querySelector("#app").innerHTML=html',base)
  page.evaluate("async()=>{const {createAppTitlebar}=await import('/examples/editor-home/ui/app-titlebar.js');globalThis.titlebar=createAppTitlebar(api);}")
  page.wait_for_function("()=>document.documentElement.dataset.nativeCaption==='true'")
  actual=page.evaluate(rects);assert actual==oracle,(actual,oracle);geometry.append({'viewport':1280,'oracle':oracle,'actual':actual});checks.append('exact original DOM/icon geometry at1280x892');page.screenshot(path=str(out/'native-titlebar.png'))
  page.locator('[data-app-maximize]').click();expect(page.locator('[data-app-maximize]')).to_have_attribute('aria-pressed','true');page.locator('[data-app-maximize]').click();expect(page.locator('[data-app-maximize]')).to_have_attribute('aria-pressed','false')
  page.evaluate("()=>eventState({state:'maximized'})");expect(page.locator('[data-app-maximize]')).to_have_attribute('aria-pressed','true');page.locator('[data-app-minimize]').click();page.locator('[data-app-close]').click();assert page.locator('.topbar').count()==1 and page.evaluate('document.fullscreenElement===null');assert not page.locator('#app').get_attribute('class');checks.append('commands/events use host, no fake minimize/fullscreen/close navigation')
  page.locator('.app-my-info-button').click();expect(page.locator('#my-info-name')).to_have_value('나');assert page.locator('#my-info-form').evaluate('(e)=>{const c=e.cloneNode(true);c.querySelector("#my-info-avatar").innerHTML="";return c.innerHTML;}')==page.evaluate('(html)=>{const t=document.createElement("template");t.innerHTML=html;return t.content.firstChild.innerHTML}',form), 'original profile markup mismatch'
  page.screenshot(path=str(out/'my-info.png'));page.locator('#my-info-name').fill('표시 이름');page.evaluate('()=>saveHold=true');page.locator('button[type=submit]').click();page.evaluate('()=>{globalThis.flushed=false;globalThis.flushFailed=false;titlebar.flush().then(()=>flushed=true,()=>flushFailed=true);}')
  assert page.evaluate('saves===1&&!flushed&&!flushFailed');page.locator('button[type=submit]').evaluate('(b)=>b.click()');assert page.evaluate('saves===1');page.evaluate('()=>{saveHold=false;releaseSave();}');page.wait_for_function('()=>flushed');expect(page.locator('#my-info-form')).to_have_count(0);checks.append('pending explicit Save flush awaits commit; duplicate submits blocked')
  page.locator('.app-my-info-button').click();expect(page.locator('#my-info-name')).to_have_value('표시 이름');page.evaluate('()=>saveFail=true');page.locator('#my-info-name').fill('보존할 입력');page.locator('button[type=submit]').click();page.wait_for_function('()=>toasts.at(-1).includes("저장하지")');expect(page.locator('#my-info-name')).to_have_value('보존할 입력');assert page.evaluate('async()=>{try{await titlebar.flush();return false;}catch{return true;}}');page.locator('[data-close]').click();assert page.evaluate('async()=>await titlebar.flush()');checks.append('save failure retains input and blocks flush until explicit dismissal')
  page.evaluate('html=>{hold=true;document.querySelector("#app").innerHTML="";}',base);page.wait_for_function('()=>held.length===1');page.evaluate('html=>document.querySelector("#app").innerHTML=html',base);page.evaluate('()=>{hold=false;held.shift()();}');page.wait_for_function("()=>document.documentElement.dataset.nativeCaption==='true'&&document.querySelector('.topbar').style.visibility!=='hidden'");expect(page.locator('.app-window-controls')).to_have_count(1);expect(page.locator('.app-my-info-button')).to_have_count(1);checks.append('async no-header/replaced-header handoff converges without duplicate controls')
  page.locator('.app-window-controls').evaluate('(e)=>e.remove()');page.wait_for_function("()=>!!document.querySelector('.app-window-controls')");expect(page.locator('.app-my-info-button')).to_have_count(1);checks.append('partial header rerender idempotent')
  for width in (640,960):
   page.set_viewport_size({'width':width,'height':600});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');page.screenshot(path=str(out/f'titlebar-{width}.png'))
  checks.append('small viewports no horizontal overflow')
  rules=page.locator('style[data-native-caption-regions]').inner_text();assert all(x in rules for x in ('app-region:drag','app-region:no-drag','[role="tab"]','[role="tablist"]','input','button','[contenteditable="true"]'));checks.append('native drag declaration excludes interactive controls/tabs')
  page.evaluate('()=>{confectoryWebUI.windowChromeSupported=false;document.querySelector("#app").innerHTML="";}');page.evaluate('html=>document.querySelector("#app").innerHTML=html',base);expect(page.locator('.app-window-controls')).to_be_hidden();expect(page.locator('.topbar')).to_be_visible();checks.append('unsupported native/browser retains visible header without fake window controls')
  pending=browser.new_page();pending.goto(url+'/fixture');pending.add_script_tag(content=bootstrap);pending.evaluate('html=>document.querySelector("#app").innerHTML=html',base)
  pending.evaluate("async()=>{globalThis.loads=0;api.loadProfile=()=>{loads++;return new Promise(r=>globalThis.releaseLoad=()=>r(structuredClone(profile)));};const {createAppTitlebar}=await import('/examples/editor-home/ui/app-titlebar.js');globalThis.titlebar=createAppTitlebar(api);}")
  pending.wait_for_function('()=>loads===1');pending.locator('.app-my-info-button').click();pending.evaluate('()=>releaseLoad()');expect(pending.locator('#my-info-name')).to_have_value('나');assert pending.evaluate('loads===1');checks.append('click during initial profile load shares pending read and opens once');pending.close()
  assert not errors,errors;browser.close()
finally:server.shutdown()
record={'checks':checks,'geometry':geometry,'pageErrors':errors,'nativeWindowsExecuted':False,'evidence':str(out)};(out/'evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False,indent=2))
