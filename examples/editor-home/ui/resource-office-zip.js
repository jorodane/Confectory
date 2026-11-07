// Read only the bounded XML parts used by the authored Office previews.
// No filesystem extraction, ZIP64, encryption, vendor code or document scripts.
const SOURCE=1048576,ENTRY=2097152,TOTAL=4194304,COUNT=1024,PARTS=64;
export const officeExtensions=new Set(['docx','xlsx','pptx','odt']);
const wanted=(name,extension)=>extension==='docx'?name==='word/document.xml':extension==='odt'?name==='content.xml':extension==='pptx'?/^ppt\/slides\/slide\d+\.xml$/.test(name):/^xl\/(workbook\.xml|_rels\/workbook\.xml\.rels|sharedStrings\.xml|worksheets\/sheet\d+\.xml)$/.test(name);
const fail=code=>{throw Error('office_zip_'+code);};
const crcTable=Uint32Array.from({length:256},(_,i)=>{let c=i;for(let n=0;n<8;n++)c=c&1?0xedb88320^(c>>>1):c>>>1;return c>>>0;});
export function officeCRC(bytes){let crc=0xffffffff;for(const byte of bytes)crc=crcTable[(crc^byte)&255]^(crc>>>8);return (crc^0xffffffff)>>>0;}
export function officeDirectory(bytes,extension){
 if(!(bytes instanceof Uint8Array)||bytes.length<22||bytes.length>SOURCE||!officeExtensions.has(extension))fail('input');
 const view=new DataView(bytes.buffer,bytes.byteOffset,bytes.byteLength),range=(at,size,end=bytes.length)=>{if(!Number.isSafeInteger(at)||at<0||size<0||at+size>end)fail('bounds');},u16=at=>{range(at,2);return view.getUint16(at,true);},u32=at=>{range(at,4);return view.getUint32(at,true);};
 let end=-1;for(let at=bytes.length-22;at>=Math.max(0,bytes.length-65557);at--)if(u32(at)===0x06054b50&&at+22+u16(at+20)===bytes.length){end=at;break;}
 if(end<0||u16(end+4)||u16(end+6)||u16(end+8)!==u16(end+10))fail('directory');
 const count=u16(end+10),size=u32(end+12),start=u32(end+16);if(!count||count>COUNT||size===0xffffffff||start===0xffffffff||start+size!==end||u32(0)!==0x04034b50)fail('directory');
 const extra=(at,length)=>{const limit=at+length;range(at,length);while(at<limit){if(at+4>limit)fail('extra');const tag=u16(at),n=u16(at+2);at+=4;if(tag===1||at+n>limit)fail('zip64_or_extra');at+=n;}};
 const seen=new Set(),intervals=[],parts=[];let at=start,total=0;
 for(let index=0;index<count;index++){
  range(at,46,end);if(u32(at)!==0x02014b50)fail('entry');const flags=u16(at+8),method=u16(at+10),crc=u32(at+16),packed=u32(at+20),raw=u32(at+24),nameSize=u16(at+28),extraSize=u16(at+30),comment=u16(at+32),local=u32(at+42);
  if(flags&~0x080e||![0,8].includes(method)||u16(at+34)||[packed,raw,local].includes(0xffffffff)||!nameSize||nameSize>512||((u32(at+38)>>>16)&0xf000)===0xa000)fail('features');range(at+46,nameSize+extraSize+comment,end);
  const nameBytes=bytes.subarray(at+46,at+46+nameSize),name=flags&0x800?new TextDecoder('utf-8',{fatal:true}).decode(nameBytes):String.fromCharCode(...nameBytes);
  if(/[\0\\]/.test(name)||name.startsWith('/')||/^[a-z]:/i.test(name)||name.split('/').some(part=>part==='.'||part==='..')||seen.has(name))fail('name');seen.add(name);extra(at+46+nameSize,extraSize);
  range(local,30,start);if(u32(local)!==0x04034b50||u16(local+6)!==flags||u16(local+8)!==method||u16(local+26)!==nameSize)fail('local');const localExtra=u16(local+28),data=local+30+nameSize+localExtra;range(local+30,nameSize+localExtra,start);
  if(!nameBytes.every((byte,i)=>bytes[local+30+i]===byte))fail('local_name');extra(local+30+nameSize,localExtra);range(data,packed,start);let finish=data+packed;
  if(flags&8){for(const [field,value]of[[14,crc],[18,packed],[22,raw]])if(u32(local+field)!==0&&u32(local+field)!==value)fail('local_size');const descriptor=u32(finish)===0x08074b50?finish+4:finish;range(descriptor,12,start);if(u32(descriptor)!==crc||u32(descriptor+4)!==packed||u32(descriptor+8)!==raw)fail('descriptor');finish=descriptor+12;}
  else if(u32(local+14)!==crc||u32(local+18)!==packed||u32(local+22)!==raw)fail('local_size');
  if(method===0&&packed!==raw)fail('stored_size');intervals.push([local,finish]);
  if(wanted(name,extension)){total+=raw;if(raw>ENTRY||total>TOTAL||parts.length>=PARTS)fail('decoded_budget');parts.push({name,data,packed,raw,crc,method});}
  at+=46+nameSize+extraSize+comment;
 }
 if(at!==end||!parts.length)fail('parts');intervals.sort((a,b)=>a[0]-b[0]);for(let i=1;i<intervals.length;i++)if(intervals[i][0]<intervals[i-1][1])fail('overlap');return parts;
}
export async function extractOfficeFiles(bytes,extension){
 const parts=officeDirectory(bytes,extension),files=[];let total=0;
 for(const part of parts){
  let result;if(part.method===0)result=bytes.slice(part.data,part.data+part.packed);
  else{
   const reader=new Blob([bytes.subarray(part.data,part.data+part.packed)]).stream().pipeThrough(new DecompressionStream('deflate-raw')).getReader(),chunks=[];let length=0;
   try{for(;;){const {done,value}=await reader.read();if(done)break;length+=value.length;if(length>part.raw||total+length>TOTAL)fail('actual_budget');chunks.push(value);}if(length!==part.raw)fail('actual_size');result=new Uint8Array(length);let offset=0;for(const chunk of chunks){result.set(chunk,offset);offset+=chunk.length;}}
   catch(error){try{await reader.cancel();}catch{}throw error;}finally{reader.releaseLock();}
  }
  total+=result.length;if(result.length!==part.raw||total>TOTAL||officeCRC(result)!==part.crc)fail('integrity');files.push([part.name,result.buffer]);
 }
 return files;
}
