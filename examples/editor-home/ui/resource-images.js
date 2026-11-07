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
 return null;
}
export function mountResourceImage({preview,toolbar,status,bytes,item,active,onError,onDetached}){
 const info=resourceImageInfo(bytes);if(!info)return null;
 if(leasedPixels+info.pixels>TOTAL_PIXELS)throw Error('resource_image_total_budget');
 leasedPixels+=info.pixels;let disposed=false,url=null,image=null,observer=null;
 const dispose=()=>{if(disposed)return;disposed=true;observer?.disconnect();leasedPixels-=info.pixels;if(image){image.onload=null;image.onerror=null;image.removeAttribute('src');image.remove();}if(url){URL.revokeObjectURL(url);url=null;}};
 const failure=()=>{if(disposed)return;if(active()){dispose();onError();}else{dispose();onDetached?.();}};
 try{
  image=document.createElement('img');image.alt=item.name;image.dataset.resourceRaster='';image.decoding='async';image.referrerPolicy='no-referrer';
  image.onload=()=>{if(disposed)return;if(!active()){dispose();onDetached?.();return;}const width=image.naturalWidth,height=image.naturalHeight;if(!((width===info.width&&height===info.height)||(width===info.height&&height===info.width))){failure();return;}preview.setAttribute('aria-busy','false');toolbar.textContent='그림 미리보기';status.textContent='읽기 전용 미리보기';};
  if(typeof MutationObserver==='function'&&document.body){observer=new MutationObserver(()=>{if(!disposed&&!active()){dispose();onDetached?.();}});observer.observe(document.body,{childList:true,subtree:true,attributes:true,attributeFilter:['hidden']});}
  image.onerror=failure;url=URL.createObjectURL(new Blob([bytes],{type:info.type}));preview.className='resource-preview is-image-preview';preview.setAttribute('aria-busy','true');preview.replaceChildren(image);image.src=url;return dispose;
 }catch(error){dispose();throw error;}
}
