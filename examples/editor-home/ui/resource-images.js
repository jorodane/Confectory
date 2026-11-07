// Bounded, static raster display of already SHA-verified project-copy bytes.
// This is metadata screening before the browser decoder, not a new image codec.
const FILE_BYTES=1048576,MAX_SIDE=16384,MAX_PIXELS=16777216,TOTAL_PIXELS=33554432;
let leasedPixels=0;
export function resourceImageInfo(bytes){
 if(!(bytes instanceof Uint8Array)||bytes.length>FILE_BYTES)throw Error('resource_image_bytes');
 const view=new DataView(bytes.buffer,bytes.byteOffset,bytes.byteLength),tag=(at,n)=>String.fromCharCode(...bytes.subarray(at,at+n));
 const size=(width,height,type)=>{if(!width||!height||width>MAX_SIDE||height>MAX_SIDE||width*height>MAX_PIXELS)throw Error('resource_image_dimensions');return {width,height,type,pixels:width*height};};
 if(bytes.length>=8&&[137,80,78,71,13,10,26,10].every((v,i)=>bytes[i]===v)){
  let offset=8,info=null,data=false,ended=false;
  while(offset+12<=bytes.length){const length=view.getUint32(offset),kind=tag(offset+4,4),next=offset+12+length;if(next>bytes.length)throw Error('resource_image_png_chunk');
   if(offset===8&&kind!=='IHDR')throw Error('resource_image_png_header');
   if(kind==='IHDR'){if(info||length!==13)throw Error('resource_image_png_header');info=size(view.getUint32(offset+8),view.getUint32(offset+12),'image/png');}
   if(['acTL','fcTL','fdAT'].includes(kind))throw Error('resource_image_animation_unsupported');
   if(kind==='IDAT')data=true;
   if(kind==='IEND'){if(length!==0||next!==bytes.length)throw Error('resource_image_png_end');ended=true;break;}
   offset=next;
  }
  if(!info||!data||!ended)throw Error('resource_image_png_incomplete');return info;
 }
 if(bytes.length>=4&&bytes[0]===255&&bytes[1]===216){
  let offset=2,info=null;
  while(offset<bytes.length){if(bytes[offset++]!==255)throw Error('resource_image_jpeg_marker');while(bytes[offset]===255)offset++;const marker=bytes[offset++];if(!marker||marker===216||marker===217||marker===1||marker>=208&&marker<=215||offset+2>bytes.length)throw Error('resource_image_jpeg_marker');const length=view.getUint16(offset);if(length<2||offset+length>bytes.length)throw Error('resource_image_jpeg_segment');
   if(marker===192||marker===194){if(info||length<8||bytes[offset+2]!==8||![1,3,4].includes(bytes[offset+7])||length!==8+3*bytes[offset+7])throw Error('resource_image_jpeg_frame');info=size(view.getUint16(offset+5),view.getUint16(offset+3),'image/jpeg');}
   else if(marker>=192&&marker<=207&&![196,200,204].includes(marker))throw Error('resource_image_jpeg_process_unsupported');
   if(marker===218){if(!info||bytes.at(-2)!==255||bytes.at(-1)!==217)throw Error('resource_image_jpeg_incomplete');return info;}
   offset+=length;
  }
  throw Error('resource_image_jpeg_incomplete');
 }
 if(bytes.length>=12&&tag(0,4)==='RIFF'&&tag(8,4)==='WEBP'){
  if(view.getUint32(4,true)+8!==bytes.length)throw Error('resource_image_webp_size');
  let offset=12,canvas=null,info=null,frame=null,alpha=false,flags=0;
  const u24=at=>bytes[at]|bytes[at+1]<<8|bytes[at+2]<<16;
  while(offset<bytes.length){
   if(offset+8>bytes.length)throw Error('resource_image_webp_chunk');const kind=tag(offset,4),length=view.getUint32(offset+4,true),data=offset+8,next=data+length+(length&1);
   if(next>bytes.length||(length&1)&&bytes[data+length]!==0)throw Error('resource_image_webp_chunk');
   if(kind==='ANIM'||kind==='ANMF')throw Error('resource_image_animation_unsupported');
   if(kind==='VP8X'){
    if(offset!==12||canvas||length!==10)throw Error('resource_image_webp_header');flags=bytes[data];if(flags&2)throw Error('resource_image_animation_unsupported');if(flags&0xc1||u24(data+1))throw Error('resource_image_webp_features');canvas=size(u24(data+4)+1,u24(data+7)+1,'image/webp');
   }else if(kind==='ALPH'){
    if(!canvas||!(flags&16)||alpha||frame||!length)throw Error('resource_image_webp_alpha');alpha=true;
   }else if(kind==='VP8 '){
    if(frame||length<10)throw Error('resource_image_webp_frame');const header=u24(data),partition=header>>>5;if(header&1||(header>>>1&7)>3||!(header&16)||!partition||partition+10>length||tag(data+3,3)!=='\x9d\x01\x2a')throw Error('resource_image_webp_frame');info=size(view.getUint16(data+6,true)&0x3fff,view.getUint16(data+8,true)&0x3fff,'image/webp');frame=kind;
   }else if(kind==='VP8L'){
    if(frame||alpha||length<5||bytes[data]!==47)throw Error('resource_image_webp_frame');const header=view.getUint32(data+1,true);if(header>>>29)throw Error('resource_image_webp_features');info=size((header&0x3fff)+1,(header>>>14&0x3fff)+1,'image/webp');frame=kind;
   }
   offset=next;
  }
  if(!info||offset!==bytes.length||canvas&&(info.width!==canvas.width||info.height!==canvas.height)||alpha&&frame!=='VP8 ')throw Error('resource_image_webp_incomplete');return info;
 }
 if(bytes.length>=2&&tag(0,2)==='BM'){
  if(bytes.length<54||view.getUint32(2,true)!==bytes.length||view.getUint32(6,true)!==0||view.getUint32(10,true)!==54||view.getUint32(14,true)!==40)throw Error('resource_image_bmp_header');
  const width=view.getInt32(18,true),signedHeight=view.getInt32(22,true),depth=view.getUint16(28,true);
  if(width<=0||signedHeight===0||view.getUint16(26,true)!==1||![24,32].includes(depth)||view.getUint32(30,true)!==0||view.getUint32(46,true)!==0||view.getUint32(50,true)!==0)throw Error('resource_image_bmp_format');
  const info=size(width,Math.abs(signedHeight),'image/bmp'),length=Math.ceil(width*depth/32)*4*info.height,declared=view.getUint32(34,true);
  if(length+54!==bytes.length||declared!==0&&declared!==length)throw Error('resource_image_bmp_pixels');return info;
 }
 return null;
}
export function mountResourceImage({preview,toolbar,status,bytes,item,active,onError,onDetached}){
 const info=resourceImageInfo(bytes);if(!info)return null;
 if(['image/webp','image/bmp'].includes(info.type)&&typeof createImageBitmap!=='function')throw Error('resource_image_decoder_unsupported');
 if(leasedPixels+info.pixels>TOTAL_PIXELS)throw Error('resource_image_total_budget');
 leasedPixels+=info.pixels;let disposed=false,url=null,image=null,observer=null,decoding=false,released=false;
 const release=()=>{if(!decoding&&!released){released=true;leasedPixels-=info.pixels;}};
 const dispose=()=>{if(disposed)return;disposed=true;observer?.disconnect();release();if(image){image.onload=null;image.onerror=null;image.removeAttribute('src');image.remove();}if(url){URL.revokeObjectURL(url);url=null;}};
 const failure=()=>{if(disposed)return;if(active()){dispose();onError();}else{dispose();onDetached?.();}};
 try{
  image=document.createElement('img');image.alt=item.name;image.dataset.resourceRaster='';image.decoding='async';image.referrerPolicy='no-referrer';
  image.onload=()=>{if(disposed)return;if(!active()){dispose();onDetached?.();return;}const width=image.naturalWidth,height=image.naturalHeight;if(!((width===info.width&&height===info.height)||(width===info.height&&height===info.width))){failure();return;}preview.setAttribute('aria-busy','false');toolbar.textContent='그림 미리보기';status.textContent='읽기 전용 미리보기';};
  if(typeof MutationObserver==='function'&&document.body){observer=new MutationObserver(()=>{if(!disposed&&!active()){dispose();onDetached?.();}});observer.observe(document.body,{childList:true,subtree:true,attributes:true,attributeFilter:['hidden']});}
  image.onerror=failure;const blob=new Blob([bytes],{type:info.type}),display=()=>{if(disposed)return;if(!active()){dispose();onDetached?.();return;}url=URL.createObjectURL(blob);preview.replaceChildren(image);image.src=url;};preview.className='resource-preview is-image-preview';preview.setAttribute('aria-busy','true');
  if(['image/webp','image/bmp'].includes(info.type)){
   decoding=true;void(async()=>{let bitmap=null,failed=false;try{bitmap=await createImageBitmap(blob);if(!((bitmap.width===info.width&&bitmap.height===info.height)||(bitmap.width===info.height&&bitmap.height===info.width)))failed=true;}catch{failed=true;}finally{bitmap?.close();decoding=false;}if(disposed){release();return;}if(failed){failure();return;}try{display();}catch{failure();}})();
  }else display();return dispose;
 }catch(error){dispose();throw error;}
}
