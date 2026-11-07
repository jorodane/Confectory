"""Actual GIF browser codec, animation/compositing pixels and bounded URL lifecycle."""
import pathlib,sys,tempfile,http.server,threading,json,base64,traceback,io,time
from PIL import Image
from functools import partial
from playwright.sync_api import sync_playwright
from v666_resource_gif_fixture import static87,local,animated,previous,corrupt,unsupported,interactive,oversized,truncated
r=pathlib.Path(sys.argv[1]).resolve();case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-gif-dom-'));values=dict(static87=static87,local=local,animated=animated,previous=previous,corrupt=corrupt,unsupported=unsupported,interactive=interactive,oversized=oversized,truncated=truncated)
for name,data in values.items():(case/(name+'.gif')).write_bytes(data)
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(r/'examples/editor-home/ui')));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();errors=[];external=[]
try:
 with sync_playwright()as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page();page.on('pageerror',lambda e:errors.append(str(e)));origin='http://127.0.0.1:'+str(server.server_port);page.route('**/*',lambda route:route.continue_()if route.request.url.startswith(origin)else(external.append(route.request.url),route.abort())[-1]);page.goto(origin+'/resource-images.js')
  result=page.evaluate('''async samples=>{const {resourceImageInfo,mountResourceImage}=await import('/resource-images.js'),baseCreate=URL.createObjectURL.bind(URL),baseRevoke=URL.revokeObjectURL.bind(URL),decode=s=>Uint8Array.from(atob(s),c=>c.charCodeAt(0));let created=0,revoked=0,live=new Set(),native=createImageBitmap,bitmaps=0,closed=0;URL.createObjectURL=blob=>{const url=baseCreate(blob);created++;live.add(url);return url;};URL.revokeObjectURL=url=>{if(!live.delete(url))throw Error('duplicate URL');revoked++;baseRevoke(url);};createImageBitmap=async blob=>{const bitmap=await native(blob);bitmaps++;return{width:bitmap.width,height:bitmap.height,close:()=>{closed++;bitmap.close();}};};const results={},pause=ms=>new Promise(r=>setTimeout(r,ms));
   for(const name of['static87','local','animated','previous','corrupt']){const bytes=decode(samples[name]),preview=document.createElement('div'),toolbar=document.createElement('div'),status=document.createElement('div');document.body.replaceChildren(preview,toolbar,status);let failed=false;const before=created,dispose=mountResourceImage({preview,toolbar,status,bytes,item:{name:name+'.gif'},active:()=>true,onError:()=>failed=true});for(let n=0;n<400&&!failed&&preview.getAttribute('aria-busy')!=='false';n++)await pause(5);
    if(name==='corrupt'){if(!failed||created!==before)throw Error('actual corrupt LZW not refused before URL');results[name]={decoderRejected:true};dispose();continue;}
    if(failed||preview.getAttribute('aria-busy')!=='false')throw Error('GIF decode '+name);const image=preview.querySelector('img');if(image.naturalWidth!==65||image.naturalHeight!==33)throw Error('natural canvas size');const canvas=document.createElement('canvas');canvas.width=65;canvas.height=33;const ctx=canvas.getContext('2d'),colors=new Set();let transparent=false;
    for(let n=0;n<(resourceImageInfo(bytes).frames>1?100:1);n++){ctx.clearRect(0,0,65,33);ctx.drawImage(image,0,0);colors.add([...ctx.getImageData(4,4,1,1).data].join(','));transparent||=ctx.getImageData(0,4,1,1).data[3]===0;if(name==='static87'||name==='local'){if([...ctx.getImageData(4,30,1,1).data].join(',')!=='10,180,30,255')throw Error('interlaced bottom pixel');}await pause(10);}
    results[name]={colors:[...colors],transparent,frames:resourceImageInfo(bytes).frames};dispose();dispose();if(live.size)throw Error('live GIF URL after close');}
   for(const name of['unsupported','interactive','oversized','truncated']){let refused=false;try{resourceImageInfo(decode(samples[name]));}catch{refused=true;}if(!refused)throw Error('admitted '+name);}
   if(live.size||created!==revoked||bitmaps!==closed)throw Error('GIF bitmap/URL leak');globalThis.__gifStatus=()=>({created,revoked,bitmaps,closed,live:live.size});return{results,created,revoked,bitmaps,closed};}''',{k:base64.b64encode(v).decode()for k,v in values.items()})
  for name in ['static87','local']:assert result['results'][name]['colors']==['240,10,20,255'],(name,result)
  assert result['results']['animated']['colors']==['240,10,20,255']and result['results']['animated']['transparent'],result
  # Canvas must use the animation's default/first image (HTML Standard); use actual compositor screenshots for motion.
  result['compositedAnimation']={}
  for name,wanted in [('animated',{(240,10,20),(10,180,30)}),('previous',{(240,10,20),(10,180,30),(10,30,220)})]:
   page.evaluate('''async sample=>{const {mountResourceImage}=await import('/resource-images.js');document.body.style.margin='0';const preview=document.createElement('div');document.body.replaceChildren(preview);let failed=false;globalThis.__gifDispose=mountResourceImage({preview,toolbar:{},status:{},bytes:Uint8Array.from(atob(sample),c=>c.charCodeAt(0)),item:{name:'actual animation.gif'},active:()=>true,onError:()=>failed=true});for(let n=0;n<400&&!failed&&preview.getAttribute('aria-busy')!=='false';n++)await new Promise(r=>setTimeout(r,5));if(failed||preview.getAttribute('aria-busy')!=='false')throw Error('animation load');}''',base64.b64encode(values[name]).decode())
   colors=set()
   for n in range(18):
    screenshot=page.screenshot(clip=dict(x=0,y=0,width=65,height=33));pixel=Image.open(io.BytesIO(screenshot)).convert('RGB').getpixel((4,4))
    if pixel not in colors:(case/(name+'-'+str(n)+'.png')).write_bytes(screenshot)
    colors.add(pixel);time.sleep(.06)
   assert colors==wanted,(name,colors);result['compositedAnimation'][name]=[list(x)for x in sorted(colors)];page.evaluate('()=>__gifDispose()')
  counters=page.evaluate('()=>__gifStatus()');assert counters['live']==0 and counters['created']==counters['revoked']and counters['bitmaps']==counters['closed'],counters
  result['finalCounters']=counters
  assert not errors and not external,(errors,external);(case/'checks.json').write_text(json.dumps(result,indent=2));browser.close();print('PASS real Chromium GIF87a/interlace/global/local palette pixels; native GIF89a transparency/two- and three-frame looping/disposal animation; actual corrupt LZW decoder refusal, structure guards and exact bitmap/URL cleanup',flush=True)
except Exception as e:
 (case/'failure.json').write_text(json.dumps(dict(error=repr(e),traceback=traceback.format_exc(),errors=errors,external=external),indent=2));raise
finally:server.shutdown();server.server_close();thread.join()
print('RESOURCE_GIF_DOM_FIXTURE',case,flush=True)
