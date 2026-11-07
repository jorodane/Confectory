import {officeDirectory,extractOfficeFiles,officeCRC} from './resource-office-zip.js';
const limit=1048576;
export async function readEditableOfficeArchive(bytes,extension='docx'){
 const parts=officeDirectory(bytes,extension,true),ordered=[...parts].sort((a,b)=>a.local-b.local),view=new DataView(bytes.buffer,bytes.byteOffset,bytes.byteLength);
 if(parts.some(p=>/^_xmlsignatures\//i.test(p.name)||/(?:^|\/)vbaProject\.bin$/i.test(p.name)))throw Error('docx_signed_or_macro');
 let at=0;for(const p of ordered){if(p.local!==at)throw Error('docx_opaque_records');at=p.finish;}if(at!==Math.min(...parts.map(p=>p.central)))throw Error('docx_opaque_records');
 const files=await extractOfficeFiles(bytes,extension,true),xml=files.find(([name])=>name==='word/document.xml')?.[1];if(extension==='docx'&&(!xml||xml.byteLength>2097152))throw Error('docx_document');return {parts,view,xml,files};
}
export const readDocxArchive=bytes=>readEditableOfficeArchive(bytes,'docx');
export const rewriteDocxArchive=(bytes,xml)=>rewriteOfficeArchive(bytes,new Map([['word/document.xml',xml]]),'docx');
export async function rewriteOfficeArchive(bytes,replacements,extension){
 const {parts,view}=await readEditableOfficeArchive(bytes,extension),packed=new Map();
 for(const [name,xml]of replacements){
  if(!parts.some(part=>part.name===name)||!(xml instanceof Uint8Array)||xml.length>2097152)throw Error('docx_xml_budget');
  const reader=new Blob([xml]).stream().pipeThrough(new CompressionStream('deflate-raw')).getReader(),chunks=[];let size=0;
  try{for(;;){const{done,value}=await reader.read();if(done)break;if((size+=value.length)>limit)throw Error('docx_output_budget');chunks.push(value);}}catch(e){try{await reader.cancel();}catch{}throw e;}finally{reader.releaseLock();}
  packed.set(name,{chunks,size,raw:xml.length,crc:officeCRC(xml)});
 }
 const chunks=[],offsets=new Map();let length=0;const append=data=>{if((length+=data.length)>limit)throw Error('docx_output_budget');chunks.push(data);};
 for(const part of [...parts].sort((a,b)=>a.local-b.local)){offsets.set(part.name,length);const changed=packed.get(part.name);if(!changed){append(bytes.subarray(part.local,part.finish));continue;}const header=bytes.slice(part.local,part.data),h=new DataView(header.buffer);h.setUint16(4,20,true);h.setUint16(6,view.getUint16(part.local+6,true)&0x800,true);h.setUint16(8,8,true);h.setUint32(14,changed.crc,true);h.setUint32(18,changed.size,true);h.setUint32(22,changed.raw,true);append(header);for(const chunk of changed.chunks)append(chunk);}
 const start=length;for(const part of parts){const header=bytes.slice(part.central,part.central+part.centralSize),h=new DataView(header.buffer);h.setUint32(42,offsets.get(part.name),true);const changed=packed.get(part.name);if(changed){h.setUint16(6,20,true);h.setUint16(8,view.getUint16(part.central+8,true)&0x800,true);h.setUint16(10,8,true);h.setUint32(16,changed.crc,true);h.setUint32(20,changed.size,true);h.setUint32(24,changed.raw,true);}append(header);}
 const end=parts.at(-1).central+parts.at(-1).centralSize,eocd=bytes.slice(end),e=new DataView(eocd.buffer);e.setUint32(12,length-start,true);e.setUint32(16,start,true);append(eocd);const output=new Uint8Array(length);let at=0;for(const chunk of chunks){output.set(chunk,at);at+=chunk.length;}return output;
}
