"""Immutable full original renderer comparison. Rectangle match does not imply controls/plug functionality parity."""
import pathlib,sys,http.server,threading,tempfile,zipfile,json
from playwright.sync_api import sync_playwright
repo=pathlib.Path(sys.argv[1]).resolve();case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-feature-full-scene-'))
with zipfile.ZipFile(repo/'reference/site-ui/Confectory-Editor-Prototype-v508.zip') as z:
 for n in z.namelist():
  marker='Confectory-v508/dist/'
  if n.startswith(marker) and not n.endswith('/'):
   f=case/n[len(marker):];f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(z.read(n))
class H(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(case),**kw)
 def log_message(self,*a):pass
 def translate_path(self,path):
  if path.startswith('/engine/'):
   target=(repo/path[len('/engine/'):]).resolve()
   if target.is_relative_to(repo):return str(target)
   return str(case/'missing')
  return super().translate_path(path)

server=http.server.ThreadingHTTPServer(('127.0.0.1',0),H);threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page(viewport={'width':1280,'height':900});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto('http://127.0.0.1:'+str(server.server_port));page.wait_for_function('typeof db!=="undefined"');
  page.evaluate("enterProject(db.projects[0].id)");
  page.evaluate('''()=>{const definition={name:'Serial',description:'직렬 연결 검증',inputs:[{id:'seed',name:'seed',type:'정수'},{id:'other',name:'other',type:'정수'},{id:'narrow',name:'narrow',type:'정수'}],outputs:[{id:'return',name:'결과',type:'정수'}],executionOutputs:[]},graph={version:2,implicitEnd:true,entryWall:{width:132},internalFunctions:true,outputNodes:true,localVariables:[],nodes:[{id:'$entry',kind:'entry',x:0,y:0},{id:'first',kind:'action',x:172,y:0,definition:{name:'첫 기능',description:'',inputs:[{id:'n',name:'n',type:'정수'}],outputs:[{id:'return',name:'결과',type:'정수'}],executionOutputs:[]}},{id:'second',kind:'action',x:602,y:0,definition:{name:'둘째 기능',description:'',inputs:[{id:'n',name:'n',type:'정수'}],outputs:[{id:'return',name:'결과',type:'정수'}],executionOutputs:[]}},{id:'$exit:return',kind:'export',outputId:'return',x:1032,y:0}],links:[{id:'entry',from:'$entry',port:'next',to:'first'},{id:'route:first',from:'first',port:'next',to:'second'},{id:'route:second',from:'second',port:'next',to:'$exit:return'}]},object={id:'owned',name:'Serial',kind:'Feature',group:'feature',description:definition.description,functionDefinition:definition};project.objects.push(object);const view=openWindow('feature-author:owned','Serial · 노드 작성',1100,700,{forceWindow:true,meta:{objectId:'owned',authorDraft:definition,graphDraft:graph,graphDirty:false,graphView:{x:0,y:0,scale:1}}});view.el.classList.add('feature-author-document');globalThis.probeView=view;renderFunctionBlueprint(view,object);Object.assign(view.el.style,{left:'40px',top:'40px'});}''');
  page.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))');page.screenshot(path=str(case/'original.png'))
  selectors=['.blueprint-editor','.bp-toolbar','.bp-tools','.bp-layout','.bp-navigation','.bp-overview','.bp-viewport','.bp-entry-wall','.bp-entry-wall>.bp-node-header','[data-bp-signature]','[data-signature-id=seed]','[data-bp-node=first]','.function-node-heading','.function-node-flow','.bp-output-sidebar','.bp-output-heading','.bp-output-entry','.bp-output-item','[data-bp-node="\\$exit:return"]']
  measure='selectors=>Object.fromEntries(selectors.map(s=>{const e=probeView.body.querySelector(s);if(!e)return [s,null];const r=e.getBoundingClientRect();return [s,{x:r.x,y:r.y,width:r.width,height:r.height}]}))'
  before=page.evaluate(measure,selectors);original_plugs=page.evaluate("[...probeView.body.querySelectorAll('.bp-pin-plug')].map(e=>e.outerHTML)")
  page.evaluate("""async()=>{
   probeView.blueprintCleanup?.();for(const file of ['consumer.css','runtime.css']){const link=document.createElement('link');link.rel='stylesheet';link.href='/engine/examples/editor-home/ui/'+file;document.head.append(link);await new Promise((resolve,reject)=>{link.onload=resolve;link.onerror=reject;});}
   const w=probeView,info={id:'Owned::Serial',kind:'function',description:'직렬 연결 검증',signature:{args:[{name:'seed',type:'long'},{name:'other',type:'long'},{name:'narrow',type:'int'}],return:'long'}},data={id:'Owned::Impl/body:common',feature:info.id,signature:info.signature,featureDefinition:info,entry:'first',profile:'sync-acyclic-v1',nodes:[{id:'first',displayName:'첫 기능',kind:'code',control:'next',intent:'',signature:{args:[{name:'n',type:'long'}],return:'long'},arguments:[{name:'n',type:'long',valueJson:'null'}],source:''},{id:'second',displayName:'둘째 기능',kind:'code',control:'next',intent:'',signature:{args:[{name:'n',type:'long'}],return:'long'},arguments:[{name:'n',type:'long',valueJson:'null'}],source:''}],edges:[{from:'first',port:'next',to:'second'},{from:'second',port:'next',to:'exit:return'}],exits:[{name:'return',valueJson:'null'}],sources:[],diagnostics:{state:'needs-implementation'}};
   w.meta={id:info.id};const windows=new Map([[w.key,w]]),api={$, $$,esc,authorInputs:new Map(),current:{projectId:'owned'},windows,view:{update:async()=>{},call:async(e,i)=>i.action==='list'?{rows:[{id:data.id}]}:structuredClone(data)},openWindow:()=>w,focus:()=>{},persist:()=>{},controls:()=>{},work:()=>{},toast:()=>{}};const {createFeatureAuthoring}=await import('/engine/examples/editor-home/ui/feature-authoring.js');await createFeatureAuthoring(api).openInWork(info);
  }""")
  page.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))');page.screenshot(path=str(case/'adapted.png'));after=page.evaluate(measure,selectors);differences=[{'selector':s,'original':before[s],'adapted':after[s]} for s in selectors if before[s]!=after[s]]
  record={'originalPlugs':original_plugs,'original':before,'adapted':after,'differences':differences,'measuredMatch':not differences,'knownUnmatchedBehavior':['root/borrowed/ref/out contracts protected; plain internal contracts supported','binary expression operators and local alias editing incomplete','serial-only branch slot deliberately disabled','full function-call integration, module import and other node kinds pending'],'errors':errors,'scope':'Full immutable original renderFunctionBlueprint vs actual author renderer at same viewport/frame/scene; read-only controls and value plugs differences are not excluded','evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,indent=2));print(json.dumps({'rectangles':len(selectors),'differences':differences,'measuredMatch':not differences,'knownUnmatchedBehavior':['root/borrowed/ref/out contracts protected; plain internal contracts supported','binary expression operators and local alias editing incomplete','serial-only branch slot deliberately disabled','full function-call integration, module import and other node kinds pending'],'errors':errors,'evidence':str(case)},indent=2));assert not errors,errors;assert not differences,differences;browser.close()
finally:server.shutdown()
