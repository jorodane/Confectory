"""Real browser codec/pixels and URL lifecycle over generated WebP, independent of native tests."""
import pathlib,sys,tempfile,http.server,threading,json,base64,traceback
from functools import partial
from playwright.sync_api import sync_playwright
from v666_resource_webp_fixture import lossless,lossy,alpha_lossy,alpha_lossless,metadata,animated,broken,oversized,truncated
r=pathlib.Path(sys.argv[1]).resolve();case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-webp-dom-'))
values={'lossless':lossless,'lossy':lossy,'alphaLossy':alpha_lossy,'alphaLossless':alpha_lossless,'metadata':metadata,'animated':animated,'broken':broken,'oversized':oversized,'truncated':truncated}
for name,data in values.items():(case/(name+'.webp')).write_bytes(data)
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(r/'examples/editor-home/ui')));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();errors=[];external=[]
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page();page.on('pageerror',lambda e:errors.append(str(e)));origin='http://127.0.0.1:'+str(server.server_port);page.route('**/*',lambda route:route.continue_()if route.request.url.startswith(origin)else(external.append(route.request.url),route.abort())[-1]);page.goto(origin+'/resource-images.js')
  result=page.evaluate('''async samples=>{const {resourceImageInfo,mountResourceImage}=await import('/resource-images.js'),baseCreate=URL.createObjectURL.bind(URL),baseRevoke=URL.revokeObjectURL.bind(URL);let created=0,revoked=0,live=new Set();URL.createObjectURL=blob=>{const url=baseCreate(blob);created++;live.add(url);return url;};URL.revokeObjectURL=url=>{if(!live.delete(url))throw Error('duplicate URL revocation');revoked++;baseRevoke(url);};const decode=s=>Uint8Array.from(atob(s),c=>c.charCodeAt(0)),pixels={};
   for(const name of['lossless','lossy','alphaLossy','alphaLossless','metadata']){const bytes=decode(samples[name]),preview=document.createElement('div'),toolbar=document.createElement('div'),status=document.createElement('div');document.body.replaceChildren(preview,toolbar,status);if(resourceImageInfo(bytes).type!=='image/webp')throw Error('type');let failed=false;const dispose=mountResourceImage({preview,toolbar,status,bytes,item:{name:name+'.webp'},active:()=>true,onError:()=>failed=true});await new Promise((resolve,reject)=>{const start=performance.now();const poll=()=>{if(failed)return reject(Error('browser decode '+name));if(preview.getAttribute('aria-busy')==='false')return resolve();if(performance.now()-start>10000)return reject(Error('load timeout'));setTimeout(poll,5);};poll();});const image=preview.querySelector('img');if(image.naturalWidth!==64||image.naturalHeight!==32)throw Error('natural size');const canvas=document.createElement('canvas');canvas.width=64;canvas.height=32;const ctx=canvas.getContext('2d');ctx.drawImage(image,0,0);pixels[name]=[...ctx.getImageData(4,4,1,1).data];dispose();dispose();if(live.size)throw Error('live URL after close');}
   for(const name of['animated','oversized','truncated']){let refused=false;try{resourceImageInfo(decode(samples[name]));}catch{refused=true;}if(!refused)throw Error('metadata admitted '+name);}
   let error=false;const preview=document.createElement('div');document.body.replaceChildren(preview);const dispose=mountResourceImage({preview,toolbar:{},status:{},bytes:decode(samples.broken),item:{name:'broken.webp'},active:()=>true,onError:()=>error=true});await new Promise((resolve,reject)=>{const start=performance.now();const poll=()=>{if(error)return resolve();if(performance.now()-start>10000)return reject(Error('bad decoder did not fail'));setTimeout(poll,5);};poll();});dispose();if(live.size||created!==revoked)throw Error('decoder error leaked URL');return{pixels,created,revoked,metadataRejection:3,actualDecoderFailure:error};}''',{k:base64.b64encode(v).decode()for k,v in values.items()})
  expected={'lossless':[240,10,20,255],'lossy':[10,180,30,255],'alphaLossy':[20,50,230,128],'alphaLossless':[240,10,20,128],'metadata':[240,10,20,255]}
  for name,pixel in result['pixels'].items():assert all(abs(a-b)<=4 for a,b in zip(pixel,expected[name])),(name,pixel)
  assert not errors and not external,(errors,external);(case/'checks.json').write_text(json.dumps(result,indent=2));browser.close();print('PASS real Chromium lossy/lossless/extended alpha WebP pixels, inert metadata, animated/size/truncation rejection and actual decoder-failure URL cleanup',flush=True)
except Exception as e:
 (case/'failure.json').write_text(json.dumps(dict(error=repr(e),traceback=traceback.format_exc(),errors=errors,external=external),indent=2));raise
finally:server.shutdown();server.server_close();thread.join()
print('RESOURCE_WEBP_DOM_FIXTURE',case,flush=True)
