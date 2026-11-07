import {officeDirectory,extractOfficeFiles,officeCRC} from './resource-office-zip.js';
const limit=1048576;
export async function readDocxArchive(bytes){
 const parts=officeDirectory(bytes,'docx',true),ordered=[...parts].sort((a,b)=>a.local-b.local),view=new DataView(bytes.buffer,bytes.byteOffset,bytes.byteLength);
 if(parts.some(p=>/^_xmlsignatures\//i.test(p.name)||/(?:^|\/)vbaProject\.bin$/i.test(p.name)))throw Error('docx_signed_or_macro');
 let at=0;for(const p of ordered){if(p.local!==at)throw Error('docx_opaque_records');at=p.finish;}if(at!==Math.min(...parts.map(p=>p.central)))throw Error('docx_opaque_records');
 const files=await extractOfficeFiles(bytes,'docx',true),xml=files.find(([name])=>name==='word/document.xml')?.[1];if(!xml||xml.byteLength>2097152)throw Error('docx_document');return {parts,view,xml};
}
export async function rewriteDocxArchive(bytes,xml){
 if(!(xml instanceof Uint8Array)||xml.length>2097152)throw Error('docx_xml_budget');const {parts,view}=await readDocxArchive(bytes),reader=new Blob([xml]).stream().pipeThrough(new CompressionStream('deflate-raw')).getReader(),compressed=[];let packedSize=0;
 try{for(;;){const{done,value}=await reader.read();if(done)break;if((packedSize+=value.length)>limit)throw Error('docx_output_budget');compressed.push(value);}}catch(e){try{await reader.cancel();}catch{}throw e;}finally{reader.releaseLock();}
 const chunks=[],offsets=new Map(),crc=officeCRC(xml);let length=0;const append=data=>{if((length+=data.length)>limit)throw Error('docx_output_budget');chunks.push(data);};
 for(const part of [...parts].sort((a,b)=>a.local-b.local)){offsets.set(part.name,length);if(part.name!=='word/document.xml'){append(bytes.subarray(part.local,part.finish));continue;}const header=bytes.slice(part.local,part.data),h=new DataView(header.buffer);h.setUint16(4,20,true);h.setUint16(6,view.getUint16(part.local+6,true)&0x800,true);h.setUint16(8,8,true);h.setUint32(14,crc,true);h.setUint32(18,packedSize,true);h.setUint32(22,xml.length,true);append(header);for(const chunk of compressed)append(chunk);}
 const start=length;for(const part of parts){const header=bytes.slice(part.central,part.central+part.centralSize),h=new DataView(header.buffer);h.setUint32(42,offsets.get(part.name),true);if(part.name==='word/document.xml'){h.setUint16(6,20,true);h.setUint16(8,view.getUint16(part.central+8,true)&0x800,true);h.setUint16(10,8,true);h.setUint32(16,crc,true);h.setUint32(20,packedSize,true);h.setUint32(24,xml.length,true);}append(header);}
 const end=parts.at(-1).central+parts.at(-1).centralSize,eocd=bytes.slice(end),e=new DataView(eocd.buffer);e.setUint32(12,length-start,true);e.setUint32(16,start,true);append(eocd);const output=new Uint8Array(length);let at=0;for(const chunk of chunks){output.set(chunk,at);at+=chunk.length;}return output;
}
