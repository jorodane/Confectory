"""Production workspace/Pack Manager modules in Chromium with owned metadata.
No engine/provider/account execution. Full engine and restart checks are separate.
"""
import http.server,json,pathlib,re,sys,tempfile,threading,zipfile
from playwright.sync_api import sync_playwright,expect
repo=pathlib.Path(sys.argv[1]).resolve();out=pathlib.Path(tempfile.mkdtemp(prefix='confectory-v508-shell-'))
style='\n'.join((repo/'examples/editor-home/ui'/n).read_text() for n in ('style.css','consumer.css','runtime.css'));style=re.sub(r'@import\s+url\([^)]*\)\s*;','',style)
class Handler(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(repo),**kw)
 def log_message(self,*a):pass
 def do_GET(self):
  if self.path=='/fixture':self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.end_headers();self.wfile.write(('<style>'+style+'</style><main id="app"><div class="work"><main id="workspace" class="workspace" style="position:relative;width:1200px;height:760px"><div id="workspace-tabs" class="workspace-tabs" role="tablist"></div></main></div></main>').encode())
  else:super().do_GET()
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();url='http://127.0.0.1:'+str(server.server_port)
checks=[];errors=[]
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page(viewport={'width':1280,'height':850});page.on('pageerror',lambda e:errors.append(str(e)));page.goto(url+'/fixture')
  page.evaluate('''async()=>{
   const {createActualWorkspace}=await import('/examples/editor-home/ui/workspace-host.js'),{createPackManager}=await import('/examples/editor-home/ui/pack-manager.js');
   const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)],esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
   globalThis.calls=[];globalThis.saved=[];globalThis.toasts=[];globalThis.current={projectId:'OwnedA',editorViews:[],namespace:'Owned.A',units:[]};
   globalThis.catalog={status:'available',packs:[{namespace:'Owned.A',version:'1.0',description:'Owned project',owned:true,dependencies:{'Owned.Api':'1'}},{namespace:'Owned.Api',version:'1.0',description:'Owned dependency',dependencies:{}},{namespace:'Owned.Unused',version:'2.0',description:'Unused local registration',dependencies:{}}]};
   const manager=createPackManager({esc,canvas:()=>$('#workspace'),project:()=>shell.project,catalog:()=>catalog,load:()=>calls.push('load'),persist:()=>shell.schedule(),toast:t=>toasts.push(t)});
   const api={$, $$,esc,get current(){return current},get page(){return 'work'},isBusy:false,projection:{workspaceRows:()=>[]},showPackManager:active=>manager.show(active),createWorkspaceObject:(...a)=>calls.push(['create',...a]),createWorkspaceVariation:(...a)=>calls.push(['variation',...a]),openObjectTable:(...a)=>calls.push(['table',...a]),captureInputs:()=>({}),capturePanels:()=>[],captureYogi:()=>null,restoreInputs:()=>{},restorePanels:()=>{},restoreYogi:()=>{},clearPanels:()=>{},clearYogi:()=>{},setWorkspaceStatus:()=>{},toast:t=>toasts.push(t),contextMenu:()=>{},modal:()=>{},controls:()=>{},render:()=>{},save:async(v,scope)=>saved.push({v:structuredClone(v),scope}),renderObjects:()=>{},openBrowser:(...a)=>calls.push(['browser',...a]),openDeclaration:id=>calls.push(['editor',id])};
   globalThis.shell=createActualWorkspace(api);shell.attach(current);globalThis.manager=manager;
  }''')
  fixed=page.locator('.workspace-fixed-tabs');expect(fixed.get_by_role('tab')).to_have_count(2);expect(fixed.locator('.workspace-tab-close')).to_have_count(0);expect(page.locator('#workspace-home-tab')).to_have_attribute('aria-selected','true');checks.append('original fixed Workspace/Pack Manager tabs have no close control')
  page.locator('#workspace-pack-tab').click();expect(page.locator('#pack-manager-view')).to_be_visible();expect(page.locator('#workspace-pack-tab')).to_have_attribute('aria-selected','true');expect(page.locator('[data-pack]')).to_have_count(2);expect(page.locator('[data-pack="Owned.Unused"]')).to_have_count(0);page.screenshot(path=str(out/'pack-manager-installed.png'));checks.append('real module uses project dependency closure, excludes merely registered packs')
  page.locator('[data-pack-group="local"]').click();expect(page.locator('[data-pack]')).to_have_count(3);page.locator('[data-pack="Owned.Unused"]').click();page.locator('[data-pack-favorite]').click();page.locator('[data-pack-group="favorite"]').click();expect(page.locator('[data-pack]')).to_have_count(1);expect(page.locator('[data-pack="Owned.Unused"]')).to_have_count(1);checks.append('local metadata/favorite choice separated from installed project scope')
  before=page.evaluate('JSON.stringify(catalog)');page.locator('[data-pack-update]').click();assert page.evaluate('JSON.stringify(catalog)')==before;assert page.evaluate("toasts.at(-1).includes('지원하지')");checks.append('unsupported pack writes never forge metadata success')
  page.locator('#workspace-home-tab').click();expect(page.locator('#pack-manager-view')).to_be_hidden();expect(page.locator('#workspace-home-tab')).to_have_attribute('aria-selected','true')
  page.locator('[data-workspace-zoom]').click();expect(page.get_by_role('dialog',name='화면 배율')).to_be_visible();page.locator('[data-zoom-preset="3.125"]').click();expect(page.locator('[data-workspace-zoom]')).to_have_text('3.125%');assert page.evaluate('shell.project.workspaceView.scale')==.03125;page.locator('[data-zoom-value]').fill('87.5');page.locator('[data-zoom-value]').press('Enter');expect(page.locator('[data-workspace-zoom]')).to_have_text('87.5%');page.screenshot(path=str(out/'zoom-87.5.png'));page.locator('[data-zoom-value]').press('Escape');expect(page.locator('.workspace-zoom-menu')).to_have_count(0);checks.append('original zoom markup/presets/direct input update actual canvas scale')
  page.evaluate('()=>shell.runtime.showWorkspaceSearchMenu(420,200)');expect(page.locator('.workspace-search-results>button>strong')).to_have_text(['새로 만들어 배치','프로젝트 브라우저','개념','정보','기능','모듈']);page.screenshot(path=str(out/'workspace-menu.png'));page.locator('.workspace-create-menu').click();expect(page.locator('[data-workspace-create]')).to_have_count(5);expect(page.locator('[data-workspace-tool-create]')).to_have_count(4);page.screenshot(path=str(out/'workspace-create.png'));page.locator('.workspace-search-head input').press('Escape');expect(page.locator('.workspace-search-results>button')).to_have_count(6);checks.append('original context hierarchy/create grid/back navigation restored')
  page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();assert page.evaluate("calls.some(c=>c[0]==='browser'&&c[4].startsWith('browser:project:'))");checks.append('Project Browser action calls actual adapter, no fake source object')
  await_flush=page.evaluate('async()=>{await shell.flush();return saved.length>0;}');assert await_flush;assert not errors,errors;browser.close()
finally:server.shutdown()
record={'checks':checks,'pageErrors':errors,'actualEngine':False,'nativeWindows':False,'evidence':str(out)};(out/'evidence.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
