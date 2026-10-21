"""Shipped startup/modal/animation code with controlled readiness snapshots.
No backend, account, login or model call. Actual engine coverage is separate.
"""
import json,pathlib,re,sys,tempfile
from playwright.sync_api import sync_playwright,expect
repo=pathlib.Path(sys.argv[1]).resolve();out=pathlib.Path(tempfile.mkdtemp(prefix='confectory-intro-transition-'))
source=(repo/'examples/editor-home/ui/v508-views.js').read_text().replace('export function createV508Views','function createV508Views',1)
css='\n'.join((repo/'examples/editor-home/ui'/n).read_text() for n in ('style.css','consumer.css','runtime.css'));css=re.sub(r'@import\s+url\([^)]*\)\s*;','',css)
ready={'id':'Confectory.Agent.Codex::Connection','state':'ready','readiness':{'state':'ready'},'accountMetadataVerified':True,'accountIdentity':{'fingerprint':'a'*64}}
script=source+'''
const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)],esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
globalThis.homeCalls=0;globalThis.openCalls=0;globalThis.flights=0;globalThis.errors=[];globalThis.active=true;globalThis.state={projectId:null,helperAgents:{agents:[]}};globalThis.dialog=null;globalThis.onHome=null;let scene='home';
new MutationObserver(rows=>{for(const row of rows)for(const node of row.addedNodes)if(node.nodeType===1&&node.matches('.startup-flight-layer'))flights++;}).observe(document.body,{childList:true});
globalThis.views=createV508Views({$,$$,esc,ready:Promise.resolve(),get current(){return state},get preferences(){return{}},get helpers(){return[]},get page(){return scene},startupActive:()=>active,connectionTitle:a=>a.id,toast:message=>errors.push(message),
 enterHome:()=>{homeCalls++;scene='home';$('#app').innerHTML='<header class="topbar">'+views.brand()+'</header><main class="home-grid"><button id="owned-project-list">프로젝트 목록</button></main>';onHome?.();},
 openAgent:options=>{openCalls++;views.modal('Agent 연결','<button id="owned-cancel">닫기</button>',(root,close)=>{dialog={...options,root,close};$('#owned-cancel',root).onclick=()=>{options.intro.cancel();close();};});}});
globalThis.update=(rows,projectId=null)=>{state={projectId,helperAgents:{agents:rows}};views.startupStateChanged();};
globalThis.finish=async()=>{const chosen=dialog;chosen.close();return await chosen.intro.complete('Confectory.Agent.Codex::Connection');};
views.start();
'''
checks=[];errors=[]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page(viewport={'width':1280,'height':900});page.emulate_media(reduced_motion='reduce');page.on('pageerror',lambda e:errors.append(str(e)))
 page.route('**/*',lambda r:r.fulfill(body=(repo/'examples/editor-home/ui/ConfectoryIcon.svg').read_bytes(),content_type='image/svg+xml') if r.request.url.endswith('/ConfectoryIcon.svg') else r.abort())
 def start(rows=None):
  page.goto('about:blank');page.set_content('<base href="http://owned.fixture/"><style>'+css+'</style><div id="app"></div><div id="overlays"></div>');page.add_script_tag(content=script)
  if rows:page.evaluate('v=>update(v)',rows)
 def intro():expect(page.locator('.welcome #connect')).to_be_enabled()
 def home():expect(page.locator('.home-grid')).to_be_visible();page.wait_for_function("() => !document.querySelector('.startup-flight-layer')");assert not page.locator('#app').evaluate('e=>e.inert');assert page.evaluate('homeCalls')==1 and page.evaluate('flights')==1
 start();intro();assert page.evaluate('homeCalls')==0;page.screenshot(path=str(out/'initial.png'))
 for phase in ('configured','checking','blocked','offline','unverified'):
  row={**ready,'state':phase,'readiness':{'state':phase}};page.evaluate('v=>update(v)',[row]);assert page.evaluate('homeCalls')==0
 checks.append('configuration/progress/failure/offline/unverified not success')
 page.evaluate('()=>{state.codexOnboarding={state:"login-complete"};views.startupStateChanged();}');assert page.evaluate('homeCalls')==0;checks.append('authentication-only completion not success')
 page.evaluate('v=>{update(v);views.startupStateChanged();views.startupStateChanged();}',[ready]);home();checks.append('existing verified connection completes once');assert page.locator('.brand').evaluate('e=>e===document.activeElement')
 start();intro();page.locator('#connect').evaluate('e=>{e.click();e.click();}');expect(page.locator('.modal')).to_have_count(1);assert page.evaluate('openCalls')==1;page.evaluate('v=>update(v)',[ready]);assert page.evaluate('homeCalls')==0;page.evaluate('finish()');home();expect(page.locator('.modal')).to_have_count(0);checks.append('intro success after modal cleanup, duplicate events one transition');page.screenshot(path=str(out/'connected-home.png'))
 start();intro();page.locator('#connect').click();page.locator('#owned-cancel').click();page.evaluate('v=>update(v)',[ready]);assert page.evaluate('homeCalls')==0;intro();page.locator('#connect').click();page.evaluate('finish()');home();checks.append('cancel suppresses late readiness, explicit reopen can complete')
 start();intro();page.locator('#connect').click();page.evaluate('()=>{dialog.intro.cancel();dialog.close();}');page.evaluate('v=>update(v,"owned-project")',[ready]);assert page.evaluate('dialog.intro.complete("Confectory.Agent.Codex::Connection")') is False;assert page.evaluate('homeCalls')==0;checks.append('navigation invalidates old intro callback')
 start();intro();page.locator('#connect').click();page.evaluate('()=>{globalThis.old=dialog.intro;dialog.close();views.start();}');intro();page.evaluate('v=>{state.helperAgents.agents=v;}',[ready]);assert page.evaluate('old.complete("Confectory.Agent.Codex::Connection")') is False;assert page.evaluate('homeCalls')==0;checks.append('stale startup generation cannot complete')
 start();intro();page.evaluate('active=false');page.evaluate('v=>update(v)',[ready]);assert page.evaluate('homeCalls')==0;checks.append('disposed view ignores late connection')
 start();intro();page.locator('#later').click();home();page.evaluate('v=>update(v)',[ready]);assert page.evaluate('homeCalls')==1;checks.append('Later works without connection and ignores later updates')
 start();intro();page.evaluate('()=>{onHome=()=>views.modal("New modal","<button id=owned-new>새 작업</button>",()=>{});}');page.evaluate('v=>update(v)',[ready]);expect(page.locator('.home-grid')).to_be_visible();page.wait_for_function("() => !document.querySelector('.startup-flight-layer')");assert page.locator('#app').evaluate('e=>e.inert');assert page.locator('.modal').evaluate('e=>e.contains(document.activeElement)');page.evaluate('views.dismissModal()');assert not page.locator('#app').evaluate('e=>e.inert');checks.append('transition preserves new modal inert/focus, its close releases inert')
 start();intro();page.emulate_media(reduced_motion='no-preference');page.evaluate('v=>update(v)',[ready]);home();checks.append('original animated transition still completes')
 assert not errors and not page.evaluate('errors'),(errors,page.evaluate('errors'));browser.close()
record={'checks':checks,'count':len(checks),'pageErrors':errors,'actualBackendAccountOrInference':False,'evidence':str(out)};(out/'evidence.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2));print('PASS shipped intro transition, modal cleanup and readiness fences')
