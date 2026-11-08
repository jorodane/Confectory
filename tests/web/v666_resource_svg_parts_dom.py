"""Actual bounded large SVG pixels and pre-XML security/complexity rejection."""
import pathlib,sys,tempfile,http.server,threading,json,base64,traceback
from functools import partial
from playwright.sync_api import sync_playwright
import v666_resource_svg_fixture as old
from v666_resource_svg_parts_fixture import geometry,alpha,padded
r=pathlib.Path(sys.argv[1]).resolve();case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-svg-parts-dom-'));values={};expected={}
raw,pixels=geometry();values['geometry']=raw;expected['geometry']=[400,200,base64.b64encode(pixels).decode()];values['maximum']=padded(raw,4194304);expected['maximum']=expected['geometry'];raw,pixels=alpha();values['alpha']=raw;expected['alpha']=[65,33,base64.b64encode(pixels).decode()]
pixels=bytes((240,10,20,255))*65*24+bytes((10,180,30,255))*65*9;values['medium']=padded(old.color,262145);expected['medium']=[65,33,base64.b64encode(pixels).decode()]
for name in ['dtd','entity','script','event','style','external','foreign','filter','recursive','invalid_ref','missing_ref','duplicate','deep','complex','malformed','unsupported','oversized']:
 values['reject-'+name]=padded(getattr(old,name),1048600)
values['reject-comments']=padded(old.svg('<!--x-->'*1025),1048600);values['reject-markup']=padded(old.svg('<rect/>'*5000),1048600);values['reject-invalid-utf8']=values['alpha'][:-10]+b'\xff'+values['alpha'][-9:];values['reject-malformed-comment']=padded(old.svg('<!-- a--b -->'),1048600);values['reject-characters']=old.svg(' '*1048600);values['reject-over4MiB']=padded(old.color,4194305)
values['reject-html']=b'<html><script>globalThis.rasterExecuted=true</script></html>'+b' '*1048600
values['reject-attribute']=padded(old.svg('<rect x="'+'0'*65537+'"/>'),1048600)
values['reject-numbers']=padded(old.svg(('<rect stroke-dasharray="'+' '.join(['1']*128)+'"/>')*257),1048600)
values['reject-elements']=padded(old.svg('<rect/>'*1024),1048600)
values['reject-title']=padded(old.svg('<title>'+'x'*65537+'</title>'),1048600)
values['reject-PI']=padded(b'<?xml-stylesheet href="https://must-not-load.invalid/x"?>'+old.color,1048600)
values['reject-encoding']=padded(b'<?xml version="1.0" encoding="utf-16"?>'+old.color,1048600)
values['reject-unclosed-comments']=b'<svg xmlns="http://www.w3.org/2000/svg">'+b'<!--'*262200
values['reject-many-markup']=b'<'*1048600
for name,data in values.items():(case/(name+'.svg')).write_bytes(data)
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(r/'examples/editor-home/ui')));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();errors=[];external=[]
try:
 with sync_playwright()as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page();page.on('pageerror',lambda e:errors.append(str(e)));origin='http://127.0.0.1:'+str(server.server_port);page.route('**/*',lambda route:route.continue_()if route.request.url.startswith(origin)else(external.append(route.request.url),route.abort())[-1]);page.goto(origin+'/resource-images.js')
  result=page.evaluate('''async({samples,expected})=>{const {resourceImageInfo,mountResourceImage}=await import('/resource-images.js'),create=URL.createObjectURL.bind(URL),revoke=URL.revokeObjectURL.bind(URL),parse=DOMParser.prototype.parseFromString,decode=s=>Uint8Array.from(atob(s),c=>c.charCodeAt(0));let created=0,revoked=0,parses=0;const live=new Set(),pixels={},rejected={};URL.createObjectURL=blob=>{const u=create(blob);live.add(u);created++;return u;};URL.revokeObjectURL=u=>{if(!live.delete(u))throw Error('double URL revoke');revoked++;revoke(u);};DOMParser.prototype.parseFromString=function(...a){parses++;return parse.apply(this,a);};
   for(const name of Object.keys(expected)){const bytes=decode(samples[name]),copy=bytes.slice(),preview=document.createElement('div'),[w,h,encoded]=expected[name];document.body.replaceChildren(preview);const info=resourceImageInfo(bytes);if(info.width!==w||info.height!==h||info.type!=='image/svg+xml')throw Error('info '+name);let failed=false;const dispose=mountResourceImage({preview,toolbar:{},status:{},bytes,item:{name:name+'.svg'},active:()=>true,onError:()=>failed=true});for(let n=0;n<1000&&!failed&&preview.getAttribute('aria-busy')!=='false';n++)await new Promise(r=>setTimeout(r,5));if(failed||preview.getAttribute('aria-busy')!=='false')throw Error('decode '+name);const img=preview.querySelector('img');if(img.naturalWidth!==w||img.naturalHeight!==h)throw Error('dimensions');const c=document.createElement('canvas');c.width=w;c.height=h;const x=c.getContext('2d');x.drawImage(img,0,0);const a=x.getImageData(0,0,w,h).data,b=decode(encoded);let color=0,alpha=0;for(let n=0;n<a.length;n+=4){alpha=Math.max(alpha,Math.abs(a[n+3]-b[n+3]));for(let k=0;k<3;k++)color=Math.max(color,Math.abs(Math.round(a[n+k]*a[n+3]/255)-Math.round(b[n+k]*b[n+3]/255)));}if(color>1||alpha>1)throw Error('pixels '+name+' '+color+'/'+alpha);pixels[name]={width:w,height:h,color,alpha,sha:[...new Uint8Array(await crypto.subtle.digest('SHA-256',a))].map(v=>v.toString(16).padStart(2,'0')).join('')};if(bytes.some((v,i)=>v!==copy[i]))throw Error('source changed');dispose();dispose();if(live.size)throw Error('leak');}
   for(const[name,value]of Object.entries(samples).filter(([k])=>k.startsWith('reject-'))){let refused=false;const before=parses,urls=created;try{if(!resourceImageInfo(decode(value)))refused=true;}catch{refused=true;}if(!refused||created!==urls)throw Error('admitted '+name);const pre=['dtd','entity','comments','markup','invalid-utf8','over4MiB','html','PI','encoding','unclosed-comments','many-markup'].some(k=>name==='reject-'+k);if(pre&&parses!==before)throw Error('parsed before refusal '+name);rejected[name]={parsed:parses-before,preParseRequired:pre};}
   const many=new TextEncoder().encode('<svg xmlns="http://www.w3.org/2000/svg" width="1" height="1">'+'<!--x-->'.repeat(1025)+'</svg>');if(resourceImageInfo(many).width!==1)throw Error('old small comment profile changed');
   if(created!==revoked||live.size||globalThis.rasterExecuted)throw Error('leak/execution');return{pixels,rejected,created,revoked,parses,smallProfilePreserved:true};}''',dict(samples={k:base64.b64encode(v).decode()for k,v in values.items()},expected=expected))
  assert not errors and not external,(errors,external);page.screenshot(path=str(case/'actual-svg-parts.png'));(case/'checks.json').write_text(json.dumps(result,indent=2));browser.close();print('PASS actual >1MiB verbose geometry/alpha, 256KiB+1 and exact4MiB comment pixels; full canvas SHA/source preservation; existing static restrictions and pre-XML DTD/entity/UTF8/comment/markup/byte rejection; no external requests or page insertion',flush=True)
except Exception as e:
 (case/'failure.json').write_text(json.dumps(dict(error=repr(e),traceback=traceback.format_exc(),errors=errors,external=external),indent=2));raise
finally:server.shutdown();server.server_close();thread.join()
print('RESOURCE_SVG_PARTS_DOM_FIXTURE',case,flush=True)
