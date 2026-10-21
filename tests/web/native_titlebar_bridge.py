"""Execute exact injected bridge in top documents and prohibited frame contexts.
Browser simulation only: host admission and Win32 execution are separate checks.
"""
import json,pathlib,re,sys
from playwright.sync_api import sync_playwright
repo=pathlib.Path(sys.argv[1]).resolve();source=(repo/'targets/webview-windows/Program.cs').read_text()
injected=source.split('await core.AddScriptToExecuteOnDocumentCreatedAsync("""',1)[1].split('""".Replace',1)[0]
origin='https://owned-titlebar.invalid';injected=injected.replace('__WINDOW_CHROME__','true').replace('__WINDOW_ORIGIN__',json.dumps(origin))
fake="""globalThis.posts=[];globalThis.handlers=[];globalThis.chrome={webview:{addEventListener:(kind,cb)=>handlers.push(cb),postMessage:m=>{posts.push(m);queueMicrotask(()=>handlers.forEach(cb=>cb({data:{id:m.id,reply:{ok:true}}})));}}};"""
checks=[]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);context=browser.new_context();context.add_init_script(fake+'\n'+injected)
 context.route('**/*',lambda r:r.fulfill(content_type='text/html',body='<main>owned fixture</main>'))
 page=context.new_page();page.goto(origin+'/');assert page.evaluate('Object.isFrozen(confectoryWebUI)&&confectoryWebUI.windowChromeSupported');assert page.evaluate("async()=>{await confectoryWebUI.windowCommand('chrome',true);return JSON.stringify(posts[0]);}")==json.dumps({'id':'1','envelope':{'command':'chrome','enabled':True},'native':'window'},separators=(',',':'));checks.append('exact owner top-frame bridge installs frozen transport and bounded window envelope')
 page.evaluate("() => {for(const src of ['/frame','https://remote-titlebar.invalid/frame']){const f=document.createElement('iframe');f.src=src;document.body.append(f);}}")
 page.wait_for_function('()=>document.querySelectorAll("iframe").length===2&&[...document.querySelectorAll("iframe")].every(f=>f.contentWindow)')
 for frame in page.frames[1:]:
  frame.wait_for_load_state();assert frame.evaluate('typeof confectoryWebUI')=='undefined'
 checks.append('same-origin and remote iframe document receives no injected bridge')
 page.goto('https://remote-titlebar.invalid/');assert page.evaluate('typeof confectoryWebUI')=='undefined';checks.append('remote top document receives no bridge')
 browser.close()
# Production prohibits even same-origin frame navigation, and receives only main-frame messages.
assert 'core.FrameNavigationStarting += (_, e) => e.Cancel = true;' in source
assert 'AreHostObjectsAllowed = false' in source
assert "frame-src 'none'" in source
assert '.FrameCreated' not in source and '.WebMessageReceived' in source
assert '!Owned(e.Source) || !Owned(core.Source)' in source and 'new Uri(e.Source).AbsolutePath is not ("/" or "/index.html")' in source and 'new Uri(core.Source).AbsolutePath is not ("/" or "/index.html")' in source
checks.append('source audit: native admission checks sender/current owned root document; frames blocked, host objects off')
print(json.dumps({'checks':checks,'nativeWindowsExecuted':False},indent=2))
