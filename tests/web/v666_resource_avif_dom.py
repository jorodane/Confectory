"""Real browser AVIF pixels and URL/bitmap lifetime over generated project-copy data."""
import pathlib,sys,tempfile,http.server,threading,json,base64,traceback
from functools import partial
from playwright.sync_api import sync_playwright
from v666_resource_avif_fixture import color,subsampled,alpha,corrupt,oversized,mismatch,unsupported,truncated,animated
r=pathlib.Path(sys.argv[1]).resolve();case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-avif-dom-'));values=dict(color=color,subsampled=subsampled,alpha=alpha,corrupt=corrupt,oversized=oversized,mismatch=mismatch,unsupported=unsupported,truncated=truncated,animated=animated)
for name,data in values.items():(case/(name+'.avif')).write_bytes(data)
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(r/'examples/editor-home/ui')));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();errors=[];external=[]
try:
 with sync_playwright()as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page();page.on('pageerror',lambda e:errors.append(str(e)));origin='http://127.0.0.1:'+str(server.server_port);page.route('**/*',lambda route:route.continue_()if route.request.url.startswith(origin)else(external.append(route.request.url),route.abort())[-1]);page.goto(origin+'/resource-images.js')
  result=page.evaluate('''async samples=>{const {resourceImageInfo,mountResourceImage}=await import('/resource-images.js'),create=URL.createObjectURL.bind(URL),revoke=URL.revokeObjectURL.bind(URL),native=createImageBitmap,decode=s=>Uint8Array.from(atob(s),c=>c.charCodeAt(0));let created=0,revoked=0,bitmaps=0,closed=0,live=new Set();URL.createObjectURL=blob=>{const url=create(blob);created++;live.add(url);return url;};URL.revokeObjectURL=url=>{if(!live.delete(url))throw Error('double URL revoke');revoked++;revoke(url);};createImageBitmap=async blob=>{const bitmap=await native(blob);bitmaps++;return{width:bitmap.width,height:bitmap.height,close:()=>{closed++;bitmap.close();}};};const pixels={};
   for(const name of['color','subsampled','alpha','corrupt']){const bytes=decode(samples[name]),preview=document.createElement('div');document.body.replaceChildren(preview);let failed=false;const before=created,dispose=mountResourceImage({preview,toolbar:{},status:{},bytes,item:{name:name+'.avif'},active:()=>true,onError:()=>failed=true});for(let n=0;n<400&&!failed&&preview.getAttribute('aria-busy')!=='false';n++)await new Promise(r=>setTimeout(r,5));
    if(name==='corrupt'){if(!failed||created!==before)throw Error('corrupt AV1 frame not rejected before URL');dispose();continue;}if(failed||preview.getAttribute('aria-busy')!=='false')throw Error('AVIF decode '+name);const image=preview.querySelector('img');if(image.naturalWidth!==65||image.naturalHeight!==33)throw Error('natural dimensions');const canvas=document.createElement('canvas');canvas.width=65;canvas.height=33;const ctx=canvas.getContext('2d');ctx.drawImage(image,0,0);pixels[name]=[...ctx.getImageData(4,4,1,1).data,...ctx.getImageData(4,30,1,1).data,...ctx.getImageData(20,4,1,1).data,...ctx.getImageData(40,4,1,1).data];dispose();dispose();if(live.size)throw Error('live URL after close');}
   for(const name of['oversized','mismatch','unsupported','truncated','animated']){let refused=false;try{resourceImageInfo(decode(samples[name]));}catch{refused=true;}if(!refused)throw Error('metadata admitted '+name);}
   if(created!==revoked||live.size||bitmaps!==closed)throw Error('AVIF resource leak');return{pixels,created,revoked,bitmaps,closed,actualCorruptDecoderRejected:true};}''',{k:base64.b64encode(v).decode()for k,v in values.items()})
  def near(actual,expected,tolerance=4):assert all(abs(x-y)<=tolerance for x,y in zip(actual,expected)),(actual,expected)
  for name in ['color','subsampled']:
   near(result['pixels'][name][:4],[240,10,20,255]);near(result['pixels'][name][4:8],[10,180,30,255]);near(result['pixels'][name][12:16],[240,10,20,255])
  assert result['pixels']['alpha'][3]==0 and result['pixels']['alpha'][7]==0;near(result['pixels']['alpha'][8:12],[240,10,20,128],6);near(result['pixels']['alpha'][12:16],[240,10,20,255])
  assert not errors and not external,(errors,external);(case/'checks.json').write_text(json.dumps(result,indent=2));browser.close();print('PASS actual Chromium SDR8 AVIF444/420 RGB pixels and auxiliary alpha0/128/255, corrupt AV1 decoder refusal, container/sequence/size rejection and bitmap/URL cleanup',flush=True)
except Exception as e:
 (case/'failure.json').write_text(json.dumps(dict(error=repr(e),traceback=traceback.format_exc(),errors=errors,external=external),indent=2));raise
finally:server.shutdown();server.server_close();thread.join()
print('RESOURCE_AVIF_DOM_FIXTURE',case,flush=True)
