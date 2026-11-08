// The native reader verifies the whole owned copy. The browser verifies exactly
// the bounded prefix pinned to that observation; this is never editable content.
const digest=/^[a-f0-9]{64}$/,id=/^[a-f0-9]{32}$/;
const matches=(pattern,value)=>typeof value==='string'&&pattern.test(value);
const exact=(value,keys)=>value&&typeof value==='object'&&!Array.isArray(value)&&Object.keys(value).sort().join('|')===[...keys].sort().join('|');
const shape=value=>JSON.stringify(Object.keys(value).sort().map(key=>[key,value[key]]));
export function validateResourceTextPrefixHeader(header){
 const item=header?.item,cap=header?.preview;
 if(header?.status!=='ready'||!matches(id,header.project)||!matches(id,item?.id)||!matches(digest,item?.hash)||!matches(digest,item?.contentGeneration)||!matches(digest,header.displayRevision)||!Number.isInteger(item.size)||item.size<=1048576||item.size>4194304||header.encoding!=='unavailable'||header.reason!=='resource_preview_file_budget'||header.data!==undefined||!exact(cap,['encoding','bytes','total'])||cap.encoding!=='base64url-prefix-v1'||cap.bytes!==1048576||cap.total!==item.size)throw Error('resource_preview_descriptor');
}
export async function decodeResourceTextPrefix(header,reply){
 validateResourceTextPrefixHeader(header);
 const item=header.item,cap=header.preview;
 if(reply?.status!=='ready'||reply.project!==header.project||reply.displayRevision!==header.displayRevision||!reply.item||shape(reply.item)!==shape(item)||reply.encoding!=='base64url-prefix-v1'||reply.reason!==undefined||!exact(reply.preview,['bytes','total','sha256'])||reply.preview.bytes!==cap.bytes||reply.preview.total!==cap.total||!matches(digest,reply.preview.sha256)||typeof reply.data!=='string'||reply.data.length>1398104)throw Error('resource_preview_identity');
 const binary=atob(reply.data.replaceAll('-','+').replaceAll('_','/'));
 if(binary.length!==1048576||btoa(binary).replaceAll('+','-').replaceAll('/','_')!==reply.data)throw Error('resource_preview_bytes');
 const bytes=Uint8Array.from(binary,c=>c.charCodeAt(0)),hash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(v=>v.toString(16).padStart(2,'0')).join('');
 if(hash!==reply.preview.sha256)throw Error('resource_preview_hash');
 return bytes;
}
