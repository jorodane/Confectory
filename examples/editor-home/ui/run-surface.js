// Pixels are inert, bounded RGBA8 from the exact native execution. No source, media URL or commands.
export async function decodeRunSurface(packet,prior,handle,readPart){
 if(packet?.available!==true)return null;
 const {runtime,revision,cursor,format,encoding,width,height,sha256,unchanged}=packet;
 const uhd=packet.resize?.max===4096&&packet.resize?.maxPixels===8847360,qhd=packet.resize?.max===2560&&packet.resize?.maxPixels===3686400,fhd=packet.resize?.max===1920&&packet.resize?.maxPixels===2073600,hd=packet.resize?.max===1280&&packet.resize?.maxPixels===921600,maxAxis=uhd?4096:qhd?2560:fhd?1920:hd?1280:640,maxPixels=uhd?8847360:qhd?3686400:fhd?2073600:hd?921600:262144;
 if(typeof handle!=='string'||!handle||typeof runtime!=='string'||runtime.length!==32||!/^[a-f0-9]{32}$/.test(runtime)||typeof revision!=='string'||! /^(0|[1-9][0-9]{0,18})$/.test(revision)||BigInt(revision)<=0n||BigInt(revision)>9223372036854775807n||cursor!==runtime+':'+revision||format!=='rgba8'||!['base64url','base64url-parts-v1'].includes(encoding)||!Number.isInteger(width)||!Number.isInteger(height)||width<1||height<1||width>maxAxis||height>maxAxis||width*height>maxPixels||typeof sha256!=='string'||sha256.length!==64||!/^[a-f0-9]{64}$/.test(sha256)||typeof unchanged!=='boolean')throw Error('surface_invalid');
 const resize=decodeRunSize(packet.resize,prior?.handle===handle&&prior.runtime===runtime?prior.resize:null,width,height);
 const same=prior?.handle===handle&&prior.runtime===runtime;
 const renderRate=decodeRunRate(packet.renderRate,same?prior.renderRate:null,revision);
 const bounds=decodeRunBounds(packet.bounds,width,height);
 if(same&&revision===prior.revision&&JSON.stringify(bounds)!==JSON.stringify(prior.bounds))throw Error('bounds_changed');
 if(same&&BigInt(prior.revision)>BigInt(revision))throw Error('surface_stale');
 if(unchanged){if(encoding!=='base64url'||packet.part!==undefined||packet.parts!==undefined)throw Error('surface_invalid');if(!same||prior.cursor!==cursor||prior.width!==width||prior.height!==height||prior.sha256!==sha256||packet.pixels!==undefined)throw Error('surface_unobserved');return JSON.stringify(resize)===JSON.stringify(prior.resize)&&JSON.stringify(renderRate)===JSON.stringify(prior.renderRate)?prior:Object.freeze({...prior,resize,renderRate});}
 let pixels;
 const decode=value=>{if(typeof value!=='string'||value.length>1398102||! /^[A-Za-z0-9_-]+$/.test(value))throw Error('surface_invalid');const raw=atob(value.replaceAll('-','+').replaceAll('_','/'));if(btoa(raw).replaceAll('+','-').replaceAll('/','_').replace(/=+$/,'')!==value)throw Error('surface_invalid');return Uint8ClampedArray.from(raw,c=>c.charCodeAt(0));};
 if(encoding==='base64url-parts-v1'){
  const total=width*height*4,count=Math.ceil(total/786432);if((!hd&&!fhd&&!qhd&&!uhd)||total<=1048576||packet.part!==0||packet.parts!==count||typeof readPart!=='function')throw Error('surface_parts');pixels=new Uint8ClampedArray(total);
  const metadata=value=>{const copy={...value};delete copy.pixels;delete copy.part;return JSON.stringify(Object.keys(copy).sort().map(key=>[key,copy[key]]));},expected=metadata(packet);
  for(let index=0;index<count;index++){const piece=index===0?packet:await readPart('slice:'+cursor+':'+index);if(!piece||piece.part!==index||metadata(piece)!==expected)throw Error('surface_parts');const chunk=decode(piece.pixels),length=Math.min(786432,total-index*786432);if(chunk.length!==length)throw Error('surface_parts');pixels.set(chunk,index*786432);}
 }else{if(packet.part!==undefined||packet.parts!==undefined)throw Error('surface_parts');pixels=decode(packet.pixels);}
 if(pixels.length!==width*height*4)throw Error('surface_invalid');
 const actual=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',pixels)),b=>b.toString(16).padStart(2,'0')).join('');
 if(actual!==sha256||same&&revision===prior.revision&&(sha256!==prior.sha256||width!==prior.width||height!==prior.height))throw Error('surface_hash');
 return Object.freeze({handle,runtime,revision,cursor,width,height,sha256,pixels,resize,renderRate,bounds});
}

export function decodeRunBounds(value,width,height){
 if(value===undefined)return null;
 if(!value||typeof value!=='object'||Array.isArray(value)||value.space!=='rgba8-pixels-v1'||!Array.isArray(value.rectangles)||value.rectangles.length>64||value.rectangles.length%4!==0)throw Error('bounds_invalid');
 const rectangles=[...value.rectangles];
 for(let i=0;i<rectangles.length;i+=4){const[x,y,w,h]=rectangles.slice(i,i+4);if(![x,y,w,h].every(Number.isSafeInteger)||x<0||y<0||w<1||h<1||x+w>width||y+h>height)throw Error('bounds_invalid');}
 return Object.freeze({space:value.space,rectangles:Object.freeze(rectangles)});
}

// Successful producer publications over the actual 900..999 ms bucket window.
// This is neither the control frame counter nor the browser's polling cadence.
export function decodeRunRate(value,prior,revision){
 if(value===undefined){if(prior)throw Error('rate_capability_changed');return null;}
 if(!value||typeof value!=='object'||Array.isArray(value))throw Error('rate_invalid');
 const {basis,observation,ready,frames,windowMs}=value,decimal=n=>typeof n==='string'&&/^(0|[1-9][0-9]{0,18})$/.test(n)&&BigInt(n)<=9223372036854775807n;
 if(basis!=='software-present-v1'||!decimal(revision)||BigInt(revision)<=0n||!decimal(observation)||BigInt(observation)<=0n||!decimal(frames)||BigInt(frames)>BigInt(revision)||typeof ready!=='boolean'||!Number.isInteger(windowMs)||(ready?windowMs<900||windowMs>999:windowMs!==0||frames!=='0'))throw Error('rate_invalid');
 const result=Object.freeze({basis,observation,ready,frames,windowMs});
 if(prior&&(BigInt(observation)<BigInt(prior.observation)||prior.ready&&!ready||observation===prior.observation&&JSON.stringify(result)!==JSON.stringify(prior)))throw Error('rate_stale');
 return result;
}

// Size ACK is distinct from frame ACK and requires matching actual output pixels.
export function decodeRunSize(value,prior,width,height){
 if(value===undefined){if(prior)throw Error('size_capability_changed');return null;}
 if(!value||typeof value!=='object'||Array.isArray(value))throw Error('size_invalid');
 const {sequence,ack,command,width:requestedWidth,height:requestedHeight,min,max,maxPixels}=value;
 if(!Number.isInteger(sequence)||sequence<0||sequence>64||!Number.isInteger(ack)||ack<0||ack>sequence||sequence-ack>1||min!==240||![512,640,1280,1920,2560,4096].includes(max)||max===640&&maxPixels!==262144||max===1280&&maxPixels!==921600||max===1920&&maxPixels!==2073600||max===2560&&maxPixels!==3686400||max===4096&&maxPixels!==8847360||maxPixels!==undefined&&maxPixels!==(max===4096?8847360:max===2560?3686400:max===1920?2073600:max===1280?921600:262144)||width>max||height>max||requestedWidth*requestedHeight>(maxPixels??262144)||![requestedWidth,requestedHeight].every(n=>Number.isInteger(n)&&n>=1&&n<=max)||typeof command!=='string'||(sequence>0&&command.length!==32)||(sequence===0?command!=='':!/^[a-f0-9]{32}$/.test(command))||sequence>0&&(requestedWidth<min||requestedHeight<min)||ack===sequence&&(width!==requestedWidth||height!==requestedHeight))throw Error('size_invalid');
 if(prior&&(max!==prior.max||maxPixels!==prior.maxPixels||sequence<prior.sequence||ack<prior.ack||sequence===prior.sequence&&(command!==prior.command||requestedWidth!==prior.width||requestedHeight!==prior.height)))throw Error('size_stale');
 return Object.freeze({sequence,ack,command,width:requestedWidth,height:requestedHeight,min,max,...(maxPixels===undefined?{}:{maxPixels})});
}
