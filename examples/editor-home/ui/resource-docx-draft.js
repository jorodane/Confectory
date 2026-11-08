// Owned DOCX private bytes only; no project write or command replay in observation.
const digest=/^[a-f0-9]{64}$/,identity=/^[a-f0-9]{32}$/;
export const docxHash=async bytes=>[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(v=>v.toString(16).padStart(2,'0')).join('');
export const docxBase64=bytes=>{let text='';for(let i=0;i<bytes.length;i+=8192)text+=String.fromCharCode(...bytes.subarray(i,i+8192));return btoa(text).replaceAll('+','-').replaceAll('/','_');};
export async function storeDocxDraft(input,request,active,project,receipt){
 const bytes=new TextEncoder().encode(JSON.stringify(input));if(bytes.length<1||bytes.length>7340032||input.value?.encoding!=='docx-parts-v1')throw Error('resource_docx_draft_budget');
 const id=crypto.randomUUID().replaceAll('-',''),hash=await docxHash(bytes);let committing=false;if(!active())throw Error('scope_changed');
 const check=(row,offset)=>{if(!active())throw Error('scope_changed');if(row?.status!=='receiving'||row.project!==project||row.id!==id||row.length!==bytes.length||row.offset!==offset)throw Error('resource_docx_upload_owner');};
 try{check(await request('upload-begin',{id,target:'draft-docx',length:bytes.length,hash}),0);for(let offset=0;offset<bytes.length;offset+=1048576){const piece=bytes.subarray(offset,Math.min(offset+1048576,bytes.length));if(!active())throw Error('scope_changed');check(await request('upload-chunk',{id,offset,data:docxBase64(piece)}),offset+piece.length);}if(!active())throw Error('scope_changed');committing=true;return await request('upload-commit',{id});}
 catch(error){if(committing){const proof={id:input.id,upload:id,hash,basis:input.revision};error.docxDraftReceipt=proof;if(active())try{const result=await receipt(proof);if(result.status==='confirmed'&&result.project===project&&result.id===input.id&&digest.test(result.revision))return result;}catch{}}throw error;}
 finally{if(active())try{await request('upload-cancel',{id});}catch{}}
}
export async function loadDocxDraft(saved,observe,active,project,id){
 if(saved?.project!==project||saved.id!==id)throw Error('resource_draft_owner');if(!saved.transfer)return saved;
 const t=saved.transfer,value=saved.value;if(!identity.test(id)||!digest.test(saved.revision)||value?.encoding!=='docx-parts-v1'||value.data!==undefined||t.encoding!=='base64url-docx-draft-parts-v1'||t.partBytes!==1048576||!Number.isInteger(t.total)||t.total<1||t.total>4194304||!digest.test(t.sha256))throw Error('resource_draft_manifest');
 const bytes=new Uint8Array(t.total),count=Math.ceil(t.total/1048576);
 for(let part=0;part<count;part++){
  if(!active())throw Error('scope_changed');const q=await observe({project,id,revision:saved.revision,hash:t.sha256,part});if(!active())throw Error('scope_changed');
  const offset=part*1048576,length=Math.min(1048576,t.total-offset);if(q?.project!==project||q.id!==id||q.revision!==saved.revision||q.hash!==t.sha256||q.total!==t.total||q.part!==part||q.parts!==count||q.encoding!=='base64url-docx-draft-part-v1'||typeof q.data!=='string'||q.data.length!==Math.ceil(length/3)*4||!digest.test(q.sha256))throw Error('resource_draft_part');
  const raw=Uint8Array.from(atob(q.data.replaceAll('-','+').replaceAll('_','/')),c=>c.charCodeAt(0));if(raw.length!==length||docxBase64(raw)!==q.data||await docxHash(raw)!==q.sha256||!active())throw Error('resource_draft_integrity');bytes.set(raw,offset);
 }
 if(await docxHash(bytes)!==t.sha256||!active())throw Error('resource_draft_integrity');const result=structuredClone(saved);result.value.data=docxBase64(bytes);return result;
}
