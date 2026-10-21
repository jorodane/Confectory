"""Compare original browser chrome to shipped adapter with identical empty data.
No prototype/domain mutation or account/provider calls; rendered geometry only.
"""
import http.server,json,pathlib,re,sys,tempfile,threading,zipfile
from playwright.sync_api import sync_playwright
repo=pathlib.Path(sys.argv[1]).resolve();out=pathlib.Path(tempfile.mkdtemp(prefix='confectory-browser-oracle-'));z=zipfile.ZipFile(repo/'reference/site-ui/Confectory-Editor-Prototype-v508.zip');original=z.read('Confectory-v508/dist/app.js').decode()
def fn(name):
 a=original.index('function '+name+'(');b=original.find('\nfunction ',a+1);s=original[a:b]
 if name=='setupBrowserTreeResize':s=s.split('\nlet activeWorkerCountClose=')[0]
 return s
source='\n'.join(fn(n) for n in ['renderBrowser','setupBrowserTree','setupBrowserTreeResize','setupBrowserActions','updateChildBrowserDetail','mountBrowserTitlePath','mountCollectionCommitActions','updateBrowserActions'])
styles='\n'.join((repo/'examples/editor-home/ui'/n).read_text() for n in ['style.css','consumer.css','runtime.css']);styles=re.sub(r'@import\s+url\([^)]*\)\s*;','',styles)
class Handler(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(repo),**kw)
 def log_message(self,*a):pass
 def do_GET(self):
  if self.path=='/fixture':
   self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.end_headers();self.wfile.write(('<style>'+styles+'</style><main id="workspace" class="workspace" style="position:relative;width:1200px;height:760px"><section class="window browser-view" style="left:40px;top:80px;width:678px;height:458px"><header class="window-title"><span class="caption"><span>◈</span><strong>프로젝트 브라우저</strong></span><span class="row"><button data-fold>−</button><button data-close>×</button></span></header><div class="window-body"></div></section></main>').encode())
  else:super().do_GET()
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();url='http://127.0.0.1:'+str(server.server_port);errors=[]
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page(viewport={'width':1280,'height':850});page.on('pageerror',lambda e:errors.append(str(e)));page.goto(url+'/fixture')
  page.add_script_tag(content="""const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)],esc=v=>String(v??'');const groups={concept:'개념',info:'정보',feature:'기능',module:'모듈'},project={objects:[],workspaceView:{scale:1}},openWorkspaceTabs=[],browserDensitySteps=[0,20,40,60,80,100];const browserDensityIndex=v=>browserDensitySteps.reduce((best,step,i)=>Math.abs(step-v)<Math.abs(browserDensitySteps[best]-v)?i:best,0);const isProjectBrowserKey=()=>true,browserRootLabel=()=> 'ProjectPack',setupBrowserObjectDrop=()=>{},renderBrowserItems=()=>{},saveLayouts=()=>{},browserFolderWorkers=()=>[],renderWorkspaceTabs=()=>{},endWorkspaceDrag=()=>{},browserPendingChanges=()=>[],updateBrowserHeaderWorkers=()=>{};globalThis.w={key:'browser:project:oracle',el:$('.window'),body:$('.window-body'),meta:{group:'concept',density:40,parent:null,query:''},title:'프로젝트 브라우저'};"""+source+'\nmountCollectionCommitActions(w);renderBrowser(w);')
  page.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
  rects="() => ['.browser-tabs','.browser-tools','.search','.density-steps','.browser-file-pane','.browser-folder-tree','.browser-tree-resizer','.browser-items','.browser-title-path','[data-browser-discard]','[data-browser-save]','[data-browser-confirm]'].map(s=>{const e=document.querySelector(s),r=e.getBoundingClientRect();return {selector:s,x:r.x,y:r.y,width:r.width,height:r.height};})"
  before=page.evaluate(rects);page.screenshot(path=str(out/'original-browser.png'))
  page.evaluate("async()=>{const {mountBrowserShell,updateBrowserTitlePath,mountBrowserCommitActions}=await import('/examples/editor-home/ui/browser-shell.js');const {createDeclarationTree}=await import('/examples/editor-home/ui/browser-tree.js');for(const e of w.el.querySelectorAll('.window-commit-action,.browser-title-workers'))e.remove();mountBrowserCommitActions(w,{action:()=>{}});mountBrowserShell(w,{esc,groups,projectBrowser:true,density:()=>{},persist:()=>{},trackDrag:()=>{},scale:()=>1});const tree=createDeclarationTree({$, $$,esc,current:{projectId:'Owned',inventory:{packs:[],status:'available'},namespace:'Owned'},projection:{snapshot:()=>({rows:[],children:new Map(),version:1}),group:()=>'',parent:()=>null},render:()=>{},persist:()=>{}},{originalChrome:true});tree.render(w);updateBrowserTitlePath(w);}")
  page.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))');after=page.evaluate(rects);page.screenshot(path=str(out/'adapted-browser.png'));assert before==after,(before,after);assert not errors,errors;browser.close()
finally:server.shutdown()
record={'pass':True,'original':before,'adapted':after,'pageErrors':errors,'scope':'empty-data browser chrome and original commit bar geometry, native/backend not executed','evidence':str(out)};(out/'evidence.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
