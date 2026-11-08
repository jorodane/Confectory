// A whole, verified Office is required before allocating a document Worker.
// Native observations pin every part to the same owned import and display basis.
const chunkBytes=1048576,maximumBytes=4194304,id=/^[a-f0-9]{32}$/,hash=/^[a-f0-9]{64}$/;
export const resourceOfficeFormat=item=>{const mime=item?.type||'';return mime.includes('wordprocessingml')?'docx':mime.includes('spreadsheetml')?'xlsx':mime.includes('presentationml')?'pptx':mime.includes('opendocument.text')?'odt':String(item?.name).split('.').at(-1).toLowerCase();};
const matches=(pattern,value)=>typeof value==='string'&&pattern.test(value);
const exact=(value,keys)=>value&&typeof value==='object'&&!Array.isArray(value)&&Object.keys(value).sort().join('|')===[...keys].sort().join('|');
const shape=value=>JSON.stringify(Object.keys(value).sort().map(key=>[key,value[key]]));
const sha=async bytes=>[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(v=>v.toString(16).padStart(2,'0')).join('');
export function validateResourceOfficePartsHeader(header){
 const item=header?.item,cap=header?.officePreview;
 if(header?.status!=='ready'||!matches(id,header.project)||!matches(id,item?.id)||item.kind!=='document'||!['docx','xlsx','pptx','odt'].includes(resourceOfficeFormat(item))||!matches(hash,item.hash)||!matches(hash,item.contentGeneration)||!matches(hash,header.displayRevision)||!Number.isInteger(item.size)||item.size<=chunkBytes||item.size>maximumBytes||header.encoding!=='unavailable'||header.reason!=='resource_preview_file_budget'||header.data!==undefined||header.preview!==undefined||header.imagePreview!==undefined||header.pdfPreview!==undefined||!exact(cap,['encoding','partBytes','total','extension'])||cap.encoding!=='base64url-office-parts-v1'||cap.extension!==resourceOfficeFormat(item)||cap.partBytes!==chunkBytes||cap.total!==item.size)throw Error('resource_office_descriptor');
}
export async function readResourceOfficeParts(header,observe,active){
 validateResourceOfficePartsHeader(header);
 const current=()=>{if(!active())throw Error('scope_changed');};current();
 const item=header.item,bytes=new Uint8Array(item.size),basis={project:header.project,id:item.id,hash:item.hash,generation:item.contentGeneration,revision:header.displayRevision};
 for(let part=0;part<Math.ceil(item.size/chunkBytes);part++){
  current();let reply;
  for(let attempt=0;attempt<3;attempt++){try{reply=await observe({...basis,part});break;}catch(error){current();if(error.message!=='busy'||attempt===2)throw error;await new Promise(resolve=>setTimeout(resolve,50));current();}}
  current();const offset=part*chunkBytes,length=Math.min(chunkBytes,item.size-offset),meta=reply?.preview;
  if(reply?.status!=='ready'||reply.project!==header.project||reply.displayRevision!==header.displayRevision||!reply.item||shape(reply.item)!==shape(item)||reply.encoding!=='base64url-office-part-v1'||reply.reason!==undefined||!exact(meta,['part','offset','bytes','total','sha256'])||meta.part!==part||meta.offset!==offset||meta.bytes!==length||meta.total!==item.size||!matches(hash,meta.sha256)||typeof reply.data!=='string'||reply.data.length>1398104)throw Error('resource_office_part_identity');
  const binary=atob(reply.data.replaceAll('-','+').replaceAll('_','/'));
  if(binary.length!==length||btoa(binary).replaceAll('+','-').replaceAll('/','_')!==reply.data)throw Error('resource_office_part_bytes');
  const decoded=Uint8Array.from(binary,c=>c.charCodeAt(0));if(await sha(decoded)!==meta.sha256)throw Error('resource_office_part_hash');current();bytes.set(decoded,offset);
 }
 if(await sha(bytes)!==item.hash)throw Error('resource_office_whole_hash');current();return bytes;
}
