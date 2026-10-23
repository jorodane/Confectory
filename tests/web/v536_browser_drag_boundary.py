"""Isolated renderer routing checks only; no engine model, native drag or account proof."""
import http.server,threading,pathlib,sys,json,tempfile
from playwright.sync_api import sync_playwright
repo=pathlib.Path(sys.argv[1]).resolve();out=pathlib.Path(tempfile.mkdtemp(prefix='confectory-browser-drop-'))
class Handler(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(repo),**kwargs)
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page();page.goto('http://127.0.0.1:'+str(server.server_port));page.set_content('<main id="workspace" style="height:600px"><section class="browser-view"><button id="inside">child</button></section><div id="empty">Workspace</div></main>');errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  result=page.evaluate('''async()=>{const {createWorkspaceRuntime}=await import('/examples/editor-home/ui/workspace.js');let owner='project-a';const calls=[],notices=[],$=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];const host={$, $$,projectIdentity:()=>owner,project:{workspaceView:{x:0,y:0,scale:1}},placeObjects:(ids,spot)=>calls.push(ids),toast:t=>notices.push(t)},ui=createWorkspaceRuntime(host),transfer=new DataTransfer();ui.setupOwnedObjectDrop();const start=()=>ui.startObjectEditorDrag({dataTransfer:transfer},{id:'Owned::One',name:'One'},[{id:'Owned::One',name:'One'}],owner);const drop=target=>target.dispatchEvent(new DragEvent('drop',{dataTransfer:transfer,bubbles:true,cancelable:true,clientX:400,clientY:300}));start();drop($('#inside'));const blockedBrowser=calls.length===0&&notices.length===1;start();owner='project-b';drop($('#empty'));const blockedOwner=calls.length===0;owner='project-a';start();drop($('#empty'));return {blockedBrowser,blockedOwner,validOwned:calls.length===1&&calls[0][0]==='Owned::One',notices};}''');assert result['blockedBrowser'] and result['blockedOwner'] and result['validOwned'],result;assert not errors,errors;browser.close();(out/'evidence.json').write_text(json.dumps({'checks':result,'errors':errors,'actualEngine':False,'nativeWindows':False},ensure_ascii=False,indent=2));print(json.dumps({'checks':result,'evidence':str(out)},ensure_ascii=False))
finally:server.shutdown()
