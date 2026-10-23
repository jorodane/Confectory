"""Real renderer, controlled transport: preflight/retirement/late-input races, no accounts."""
import http.server,pathlib,sys,tempfile,threading,json
from playwright.sync_api import sync_playwright
repo=pathlib.Path(sys.argv[1]).resolve();case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-slot-batch-renderer-'));checks=[]
class Handler(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(repo),**kw)
 def log_message(self,*a):pass
 def do_GET(self):
  if self.path=='/fixture':self.send_response(200);self.end_headers();self.wfile.write(b'<main id="workspace"></main>')
  else:super().do_GET()
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page();page.goto('http://127.0.0.1:'+str(server.server_port)+'/fixture')
  results=page.evaluate('''async()=>{
   const {createElementFunctions}=await import('/examples/editor-home/ui/element-functions.js');const results=[];
   for(const mode of ['retire-before-apply','new-input-before-apply','cancel-before-apply','retire-after-accepted','replacement-after-accepted']){
    const el=document.createElement('section');document.body.append(el);const signature={args:[{type:'long',name:'n'}],return:'long'},schema={id:'Owned::Owner',revision:1,textHash:'h',requirements:['A','B'].map(n=>({function:'Owned::'+n,signature}))},w={key:'schema',el,elementScope:'project',elementSchema:schema},inputs=new Map(),windows=new Map([['schema',w]]),current={projectId:'project',schema},calls=[];let release,entered,step=0;const held=new Promise(resolve=>release=resolve),arrival=new Promise(resolve=>entered=resolve);
    for(const n of ['A','B'])inputs.set('project|Owned::Owner|element|implementation:Owned::'+n,{kind:'implementation',function:'Owned::'+n,reference:'Owned::Donor',implementation:'Owned::Impl_'+n,signature,fingerprint:n});
    const captured=[...inputs],api={inputs,windows,current,$:()=>null,$$:()=>[],esc:String,persist:()=>{},otherPending:()=>false,view:{update:async()=>{},call:async(endpoint,input)=>{calls.push(input.action||endpoint);if(input.action==='readImplementation'){if(++step===2&&mode.endsWith('before-apply')){entered();await held;}return {basis:input.function,contractFingerprint:input.function.split('::')[1]};}if(input.action==='applySlots'){if(mode.endsWith('after-accepted')){entered();await held;}return {atomic:true};}return {};}}};const feature=createElementFunctions(api);const alive=()=>windows.get('schema')===w&&el.isConnected;const result=feature.flush(w,schema,alive).then(()=>null,e=>e.message);await arrival;
    if(mode==='retire-before-apply'||mode==='retire-after-accepted'){windows.delete('schema');el.remove();}
    if(mode==='new-input-before-apply')inputs.set('project|Owned::Owner|element|description',{kind:'description',text:'new typing'});
    if(mode==='cancel-before-apply')for(const [key,value] of captured)inputs.delete(key);
    if(mode==='replacement-after-accepted')inputs.set(captured[0][0],{...captured[0][1],implementation:'Owned::Replacement'});
    release();const error=await result,applied=calls.filter(c=>c==='applySlots').length;
    if(mode.endsWith('before-apply')){if(applied!==0||!error)throw Error('Unexpected mutation '+mode);if(mode==='cancel-before-apply'&&inputs.size!==0)throw Error('Canceled inputs replayed');if(mode==='retire-before-apply'&&inputs.size!==2)throw Error('Retired input lost');if(mode==='new-input-before-apply'&&inputs.size!==3)throw Error('Late typing lost');}
    else {if(applied!==1)throw Error('Missing accepted batch');if(mode==='retire-after-accepted'&&inputs.size!==0)throw Error('Accepted retired choices retained');if(mode==='replacement-after-accepted'&&(inputs.size!==1||inputs.get(captured[0][0]).implementation!=='Owned::Replacement'))throw Error('Late replacement deleted');}
    el.remove();results.push(mode);
   }return results;
  }''')
  checks.extend(results);browser.close()
finally:server.shutdown()
record={'checks':checks,'actualBackend':False,'realRenderer':True,'controlledTransport':True,'nativeWindows':False,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
