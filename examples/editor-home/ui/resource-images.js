import {resourceSvgInfo,resourceSvgSignature} from './resource-svg.js';
// Bounded image display of already SHA-verified project-copy bytes.
// This is metadata screening before the browser decoder, not a new image codec.
const FILE_BYTES=1048576,RASTER_BYTES=4194304,MAX_SIDE=16384,MAX_PIXELS=16777216,TOTAL_PIXELS=33554432;
function resourceAvifSignature(bytes){
 if(bytes.length<16||bytes[4]!==102||bytes[5]!==116||bytes[6]!==121||bytes[7]!==112)return false;
 const length=new DataView(bytes.buffer,bytes.byteOffset,bytes.byteLength).getUint32(0);
 if(length<16||length>76||length>bytes.length||(length-16)%4)return false;
 for(let at=8;at<length;at+=at===8?8:4)if(bytes[at]===97&&bytes[at+1]===118&&bytes[at+2]===105&&bytes[at+3]===102)return true;
 return false;
}
let leasedPixels=0;
export function resourceImageInfo(bytes){
 if(!(bytes instanceof Uint8Array)||bytes.length>RASTER_BYTES||bytes.length>FILE_BYTES&&!([137,80,78,71,13,10,26,10].every((v,i)=>bytes[i]===v)||bytes[0]===255&&bytes[1]===216&&bytes[2]===255||bytes[0]===66&&bytes[1]===77||bytes[0]===82&&bytes[1]===73&&bytes[2]===70&&bytes[3]===70&&bytes[8]===87&&bytes[9]===69&&bytes[10]===66&&bytes[11]===80||bytes[0]===71&&bytes[1]===73&&bytes[2]===70&&bytes[3]===56&&(bytes[4]===55||bytes[4]===57)&&bytes[5]===97||resourceAvifSignature(bytes)||resourceSvgSignature(bytes)))throw Error('resource_image_bytes');
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
 if(bytes.length>=6&&['GIF87a','GIF89a'].includes(tag(0,6))){
  if(bytes.length<13)throw Error('resource_image_gif_header');
  const info=size(view.getUint16(6,true),view.getUint16(8,true),'image/gif'),globalColors=bytes[10]&128?2<<(bytes[10]&7):0;
  let offset=13+globalColors*3,frames=0,control=null;if(offset>bytes.length||globalColors&&bytes[11]>=globalColors)throw Error('resource_image_gif_palette');
  const blocks=()=>{let length=0;for(;;){if(offset>=bytes.length)throw Error('resource_image_gif_blocks');const count=bytes[offset++];if(!count)return length;if(offset+count>bytes.length)throw Error('resource_image_gif_blocks');offset+=count;length+=count;}};
  while(offset<bytes.length){
   const kind=bytes[offset++];
   if(kind===59){if(offset!==bytes.length||!frames||control)throw Error('resource_image_gif_end');return {...info,pixels:info.pixels*frames,frames};}
   if(kind===33){
    if(offset>=bytes.length)throw Error('resource_image_gif_extension');const label=bytes[offset++];
    if(label===249){
     if(control||offset+6>bytes.length||bytes[offset]!==4||bytes[offset+5]!==0)throw Error('resource_image_gif_control');
     const flags=bytes[offset+1];if(flags&224||(flags>>2&7)>3||flags&2)throw Error('resource_image_gif_control');control={transparent:flags&1?bytes[offset+4]:null};offset+=6;
    }else if(label===254)blocks();
    else if(label===255){if(offset+12>bytes.length||bytes[offset++]!==11)throw Error('resource_image_gif_application');offset+=11;blocks();}
    else throw Error('resource_image_gif_extension');
    continue;
   }
   if(kind!==44||offset+9>bytes.length)throw Error('resource_image_gif_frame');
   const left=view.getUint16(offset,true),top=view.getUint16(offset+2,true),width=view.getUint16(offset+4,true),height=view.getUint16(offset+6,true),flags=bytes[offset+8],colors=flags&128?2<<(flags&7):globalColors;
   if(!width||!height||left+width>info.width||top+height>info.height||flags&24||!colors||control?.transparent!=null&&control.transparent>=colors)throw Error('resource_image_gif_frame');
   if(++frames>64||info.pixels*frames>MAX_PIXELS)throw Error('resource_image_gif_budget');offset+=9+(flags&128?colors*3:0);
   if(offset>=bytes.length||bytes[offset]<2||bytes[offset]>8)throw Error('resource_image_gif_codes');offset++;if(!blocks())throw Error('resource_image_gif_codes');control=null;
  }
  throw Error('resource_image_gif_end');
 }
 if(bytes.length>=12&&tag(4,4)==='ftyp'){
  let boxCount=0;const fail=()=>{throw Error('resource_image_avif_structure');};
  const boxes=(start,end)=>{const result=[];for(let at=start;at<end;){if(at+8>end||++boxCount>128)fail();const length=view.getUint32(at);if(length<8||at+length>end)fail();result.push({at,body:at+8,end:at+length,type:tag(at+4,4)});at+=length;}return result;};
  const only=(list,type)=>{const found=list.filter(row=>row.type===type);if(found.length!==1)fail();return found[0];},full=row=>{if(row.body+4>row.end||view.getUint32(row.body)!==0)fail();return row.body+4;};
  const top=boxes(0,bytes.length),ftyp=only(top,'ftyp');if(ftyp.at!==0||ftyp.end<16||ftyp.end>76||(ftyp.end-16)%4)fail();const brands=[tag(8,4)];for(let at=16;at<ftyp.end;at+=4)brands.push(tag(at,4));if(!brands.includes('avif'))return null;if(brands.includes('avis')||top.some(row=>!['ftyp','meta','mdat','free'].includes(row.type)))fail();
  const meta=only(top,'meta'),mdat=only(top,'mdat'),children=boxes(full(meta),meta.end);if(children.some(row=>!['hdlr','pitm','iloc','iinf','iprp','iref'].includes(row.type)))fail();
  const hdlr=only(children,'hdlr'),handler=full(hdlr);if(handler+21>hdlr.end||view.getUint32(handler)!==0||tag(handler+4,4)!=='pict'||bytes.subarray(handler+8,handler+20).some(value=>value!==0)||hdlr.end-handler>84||bytes[hdlr.end-1]!==0)fail();
  const pitm=only(children,'pitm'),primaryAt=full(pitm);if(primaryAt+2!==pitm.end)fail();const primary=view.getUint16(primaryAt);
  const iinf=only(children,'iinf'),infoAt=full(iinf);if(infoAt+2>iinf.end)fail();const count=view.getUint16(infoAt),entries=boxes(infoAt+2,iinf.end),ids=new Set();if(count<1||count>2||entries.length!==count)fail();
  for(const row of entries){const at=row.body;if(row.type!=='infe'||at+13>row.end||bytes[at]!==2||(view.getUint32(at)&0xffffff)>1||view.getUint16(at+6)!==0||tag(at+8,4)!=='av01'||row.end-at>268||bytes.indexOf(0,at+12)!==row.end-1)fail();const id=view.getUint16(at+4);if(!id||ids.has(id)||id===primary&&(view.getUint32(at)&1))fail();ids.add(id);}if(!ids.has(primary))fail();
  const iloc=only(children,'iloc');let at=full(iloc);if(at+4>iloc.end||bytes[at++]!==0x44||bytes[at++]!==0||view.getUint16(at)!==count)fail();at+=2;const locations=new Map();
  for(let n=0;n<count;n++){if(at+14>iloc.end)fail();const id=view.getUint16(at),reference=view.getUint16(at+2),extents=view.getUint16(at+4),offset=view.getUint32(at+6),length=view.getUint32(at+10);at+=14;if(!ids.has(id)||locations.has(id)||reference||extents!==1||!length||offset<mdat.body||offset+length>mdat.end)fail();locations.set(id,{offset,length});}if(at!==iloc.end)fail();let next=mdat.body;for(const row of [...locations.values()].sort((a,b)=>a.offset-b.offset)){if(row.offset!==next)fail();next+=row.length;}if(next!==mdat.end)fail();
  const iprp=only(children,'iprp'),propertyBoxes=boxes(iprp.body,iprp.end);if(propertyBoxes.length!==2)fail();const ipco=only(propertyBoxes,'ipco'),ipma=only(propertyBoxes,'ipma'),properties=boxes(ipco.body,ipco.end);if(properties.length<4||properties.length>16)fail();
  const parsed=properties.map(row=>{const at=row.body,length=row.end-at;
   if(row.type==='ispe'){if(full(row)+8!==row.end)fail();return {type:row.type,info:size(view.getUint32(at+4),view.getUint32(at+8),'image/avif')};}
   if(row.type==='pixi'){if(full(row)+1>row.end||![1,3].includes(bytes[at+4])||length!==5+bytes[at+4]||bytes.subarray(at+5,row.end).some(value=>value!==8))fail();return {type:row.type,channels:bytes[at+4]};}
   if(row.type==='av1C'){if(length!==4||bytes[at]!==129||bytes[at+1]>>5>1||bytes[at+2]&0xe0||bytes[at+3]!==0)fail();return {type:row.type,profile:bytes[at+1]>>5,level:bytes[at+1]&31,flags:bytes[at+2]};}
   if(row.type==='colr'){if(length!==11||tag(at,4)!=='nclx'||view.getUint16(at+4)!==1||![1,13].includes(view.getUint16(at+6))||![0,1,6].includes(view.getUint16(at+8))||bytes[at+10]&127)fail();return {type:row.type,primaries:1,transfer:view.getUint16(at+6),matrix:view.getUint16(at+8),range:bytes[at+10]>>7};}
   if(row.type==='auxC'){const start=full(row),urn='urn:mpeg:mpegB:cicp:systems:auxiliary:alpha\0';if(row.end-start!==urn.length||tag(start,urn.length)!==urn)fail();return {type:row.type};}
   fail();
  });
  at=full(ipma);if(at+4>ipma.end||view.getUint32(at)!==count)fail();at+=4;const associations=new Map(),used=new Set();
  for(let n=0;n<count;n++){if(at+3>ipma.end)fail();const id=view.getUint16(at),amount=bytes[at+2],rows=new Map();at+=3;if(!ids.has(id)||associations.has(id)||!amount||at+amount>ipma.end)fail();for(let j=0;j<amount;j++){const index=(bytes[at++]&127)-1;if(index<0||index>=parsed.length||rows.has(parsed[index].type))fail();rows.set(parsed[index].type,parsed[index]);used.add(index);}associations.set(id,rows);}if(at!==ipma.end||used.size!==parsed.length)fail();
  const primaryProperties=associations.get(primary),primaryInfo=primaryProperties?.get('ispe')?.info;if(!primaryInfo)fail();let pixels=0;
  // Resolve every declared item through its associations and local extent; no unassociated dimension guess.
  for(const[id,rows]of associations){const alpha=id!==primary,required=alpha?['ispe','pixi','av1C','auxC']:['ispe','pixi','av1C','colr'];if(rows.size!==4||required.some(type=>!rows.has(type))||rows.get('pixi').channels!==(alpha?1:3))fail();const info=rows.get('ispe').info;if(info.width!==primaryInfo.width||info.height!==primaryInfo.height||(pixels+=info.pixels)>MAX_PIXELS)fail();
   const location=locations.get(id),end=location.offset+location.length;let pos=location.offset,sequence=null,frame=false,delimiter=false;
   // A reduced still sequence and one frame keep all coded dimensions bounded before native decode.
   while(pos<end){const header=bytes[pos++],type=header>>3&15;if(header&0x85||!(header&2))fail();let length=0,multiplier=1,done=false;for(let n=0;n<8&&pos<end;n++){const value=bytes[pos++];length+=(value&127)*multiplier;if(!Number.isSafeInteger(length)||length>(type===6?RASTER_BYTES:FILE_BYTES))fail();if(!(value&128)){done=true;break;}multiplier*=128;}if(!done||pos+length>end)fail();const finish=pos+length;
    if(type===2){if(delimiter||sequence||frame||length)fail();delimiter=true;}
    else if(type===1){if(sequence||frame||!length)fail();let bit=pos*8;const read=amount=>{if(bit+amount>finish*8)fail();let value=0;while(amount--)value=value*2+(bytes[bit>>3]>>(7-(bit++&7))&1);return value;};const profile=read(3);if(profile>1||read(1)!==1||read(1)!==1)fail();const level=read(5),widthBits=read(4)+1,heightBits=read(4)+1,width=read(widthBits)+1,height=read(heightBits)+1;if(width!==info.width||height!==info.height)fail();read(6);if(read(1)!==0)fail();const mono=profile===1?0:read(1),described=read(1),primaries=described?read(8):2,transfer=described?read(8):2,matrix=described?read(8):2;let range,x,y,chroma=0;
     if(mono){range=read(1);x=y=1;}else{if(primaries===1&&transfer===13&&matrix===0){range=1;x=y=0;}else{range=read(1);x=y=profile===0?1:0;if(x&&y)chroma=read(2);}read(1);}read(1);if(read(1)!==1)fail();while(bit<finish*8)if(read(1)!==0)fail();sequence={profile,level,flags:mono<<4|x<<3|y<<2|chroma};if(mono!==(alpha?1:0))fail();const color=rows.get('colr');if(color&&(range!==color.range||described&&(primaries!==color.primaries||transfer!==color.transfer||matrix!==color.matrix)))fail();
    }else if(type===6){if(!sequence||frame||!length)fail();frame=true;}else fail();pos=finish;
   }
   const config=rows.get('av1C');if(!sequence||!frame||sequence.profile!==config.profile||sequence.level!==config.level||sequence.flags!==config.flags)fail();
  }
  const refs=children.filter(row=>row.type==='iref');if(count===1){if(refs.length)fail();}else{if(refs.length!==1)fail();const children=boxes(full(refs[0]),refs[0].end);if(children.length!==1||children[0].type!=='auxl'||children[0].end-children[0].body!==6)fail();const at=children[0].body,alpha=[...ids].find(id=>id!==primary);if(view.getUint16(at)!==alpha||view.getUint16(at+2)!==1||view.getUint16(at+4)!==primary)fail();}
  return {...primaryInfo,pixels};
 }
 return resourceSvgInfo(bytes);
}
export function mountResourceImage({preview,toolbar,status,bytes,item,active,onError,onDetached}){
 const info=resourceImageInfo(bytes);if(!info)return null;
 if(['image/webp','image/bmp','image/gif','image/avif'].includes(info.type)&&typeof createImageBitmap!=='function')throw Error('resource_image_decoder_unsupported');
 if(leasedPixels+info.pixels>TOTAL_PIXELS)throw Error('resource_image_total_budget');
 leasedPixels+=info.pixels;let disposed=false,url=null,image=null,observer=null,decoding=false,released=false;
 const release=()=>{if(!decoding&&!released){released=true;leasedPixels-=info.pixels;}};
 const dispose=()=>{if(disposed)return;disposed=true;observer?.disconnect();release();if(image){image.onload=null;image.onerror=null;image.removeAttribute('src');image.remove();}if(url){URL.revokeObjectURL(url);url=null;}};
 const failure=()=>{if(disposed)return;if(active()){dispose();onError();}else{dispose();onDetached?.();}};
 try{
  image=document.createElement('img');image.alt=item.name;image.dataset.resourceRaster='';image.decoding='async';image.referrerPolicy='no-referrer';
  image.onload=()=>{if(disposed||info.type==='image/svg+xml'&&decoding)return;if(!active()){dispose();onDetached?.();return;}const width=image.naturalWidth,height=image.naturalHeight;if(!((width===info.width&&height===info.height)||(!['image/gif','image/avif','image/svg+xml'].includes(info.type)&&width===info.height&&height===info.width))){failure();return;}preview.setAttribute('aria-busy','false');toolbar.textContent='그림 미리보기';status.textContent='읽기 전용 미리보기';};
  if(typeof MutationObserver==='function'&&document.body){observer=new MutationObserver(()=>{if(!disposed&&!active()){dispose();onDetached?.();}});observer.observe(document.body,{childList:true,subtree:true,attributes:true,attributeFilter:['hidden']});}
  image.onerror=failure;const blob=new Blob([info.displayBytes||bytes],{type:info.type}),display=()=>{if(disposed)return;if(!active()){dispose();onDetached?.();return;}url=URL.createObjectURL(blob);preview.replaceChildren(image);image.src=url;};preview.className='resource-preview is-image-preview';preview.setAttribute('aria-busy','true');
  if(info.type==='image/svg+xml'){
   // Chromium's bitmap decoder does not accept SVG blobs. Decode an isolated image instead;
   // the lease survives close until its actual decode promise settles, and the URL is revoked.
   if(typeof image.decode!=='function')throw Error('resource_svg_decoder_unsupported');
   url=URL.createObjectURL(blob);decoding=true;
   void(async()=>{let failed=false;try{image.src=url;await image.decode();if(image.naturalWidth!==info.width||image.naturalHeight!==info.height)failed=true;}catch{failed=true;}finally{decoding=false;}if(disposed){release();return;}if(failed){failure();return;}if(!active()){dispose();onDetached?.();return;}try{preview.replaceChildren(image);image.onload();}catch{failure();}})();
  }else if(['image/webp','image/bmp','image/gif','image/avif'].includes(info.type)){
   decoding=true;void(async()=>{let bitmap=null,failed=false;try{bitmap=await createImageBitmap(blob);if(!((bitmap.width===info.width&&bitmap.height===info.height)||(!['image/gif','image/avif','image/svg+xml'].includes(info.type)&&bitmap.width===info.height&&bitmap.height===info.width)))failed=true;}catch{failed=true;}finally{bitmap?.close();decoding=false;}if(disposed){release();return;}if(failed){failure();return;}try{display();}catch{failure();}})();
  }else display();return dispose;
 }catch(error){dispose();throw error;}
}
