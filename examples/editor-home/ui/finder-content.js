// Transient index of the existing owned Browser Data read representation.
// No raw source paths, external IDs, grants, edits or persistent search state.
export function createFinderContent(api){
 const supported=new Set(['object','schema','function','implementation','module','category','concept','enum']);
 const skipped=new Set(['image','bustImage','voxelCharacter','thumbnail','blob','dataUrl','editorIcon']);
 let enabled=false,identity='',epoch=0,job=null,timer=null,phase='idle',rows=new Map(),unsupported=0,unavailable=0;
 const context=()=>api.context();
 function changed(){api.changed();}
 function reset(){++epoch;clearTimeout(timer);timer=null;job=null;rows=new Map();phase='idle';unsupported=unavailable=0;identity='';}
 function ensure(wanted){
  if(!wanted){if(enabled){enabled=false;reset();changed();}return;}
  enabled=true;const own=context();if(!own){reset();return;}
  const mark=own.key+'|'+own.basis;if(identity!==mark){reset();identity=mark;}
  if(phase!=='idle'||job||timer||!api.ready())return;
  // One source snapshot serves the current text query; typing never replays a
  // navigation or launches overlapping reads. A real source-basis change retires it.
  const serial=epoch;phase='queued';changed();timer=setTimeout(()=>{timer=null;if(enabled&&epoch===serial)void load(own,serial);},180);
 }
 function text(row){
  let size=0,incomplete=row.incomplete===true;const parts=[];const add=value=>{const flat=String(value??'').replace(/\s+/g,' ').trim();if(!flat||/^data:/i.test(flat))return;if(size>=20000){incomplete=true;return;}if(flat.length>20000-size)incomplete=true;const part=flat.slice(0,20000-size);parts.push(part);size+=part.length;};
  if(!Array.isArray(row.fields))throw Error('finder-content-fields');
  for(const field of row.fields){
   if(typeof field.name!=='string')throw Error('finder-content-field');if(skipped.has(field.name))continue;add(field.name);if(field.state!=='present'){incomplete=true;continue;}if(typeof field.valueJson!=='string')throw Error('finder-content-value');JSON.parse(field.valueJson);
   // Walk validated JSON tokens: retain exact numeric lexemes, decode Unicode,
   // and omit image payloads even inside compounds. Never round via Number.
   const tokens=field.valueJson.match(/"(?:\\.|[^"\\])*"|[{}\[\],:]|true|false|null|-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?/g);let index=0;
   const visit=(depth,allowed)=>{const token=tokens[index++];if(token==='{'){while(tokens[index]!=='}'){const key=JSON.parse(tokens[index++]);index++;const include=allowed&&!skipped.has(key);if(include&&depth<4)add(key);visit(depth+1,include);if(tokens[index]===',')index++;}index++;}else if(token==='['){while(tokens[index]!==']'){visit(depth+1,allowed);if(tokens[index]===',')index++;}index++;}else if(allowed&&depth<=4)add(token[0]==='"'?JSON.parse(token):token);};visit(0,true);
  }
  const bodies=[];if(row.bodies!==undefined&&!Array.isArray(row.bodies))throw Error('finder-body-rows');
  for(const body of row.bodies||[]){if(typeof body.target!=='string'||!body.target||body.id!==row.id+'/body:'+body.target||typeof body.text!=='string'||body.text.length>1048576||!/^\d+$/.test(body.revision)||!/^\d+$/.test(body.ownerRevision)||body.ownerHash!==row.textHash||!/^[0-9a-f]{64}$/.test(body.textHash)){incomplete=true;continue;}incomplete||=body.truncated===true;bodies.push({id:body.id,target:body.target,text:body.text.replace(/\s+/g,' ').trim(),revision:body.revision,ownerRevision:body.ownerRevision,ownerHash:body.ownerHash,textHash:body.textHash});}
  return {text:parts.join(' · '),bodies,incomplete};
 }
 async function load(own,serial){
  const token={};job=token;const alive=()=>enabled&&job===token&&epoch===serial&&context()?.key===own.key&&context()?.basis===own.basis;
  try{
   const all=api.objects().filter(row=>row.owned!==false&&row.id.startsWith(own.namespace+'::'));
   const selected=all.filter(row=>supported.has(row.kind));unsupported=all.length-selected.length;
   if(own.namespace==='Confectory.AISettings'){unsupported=all.length;phase='restricted';changed();return;}
   phase='loading';changed();
   const batches=[];let batch=[];for(const row of selected){if(row.kind==='implementation'){if(batch.length){batches.push(batch);batch=[];}batches.push([row.id]);}else{batch.push(row.id);if(batch.length===64){batches.push(batch);batch=[];}}}if(batch.length)batches.push(batch);
   for(const ids of batches){
    if(!alive())return;const reply=await api.read(ids,alive);if(!alive())return;
    if(reply?.projectId!==own.projectId||!Array.isArray(reply.rows)||reply.rows.length!==ids.length||new Set(reply.rows.map(row=>row.id)).size!==ids.length||reply.rows.some(row=>!ids.includes(row.id)))throw Error('finder-content-owner');
    for(const row of reply.rows){if(row.status!=='available'){++unavailable;continue;}try{const value=text(row);if(value.incomplete)++unavailable;rows.set(row.id,{id:row.id,text:value.text,bodies:value.bodies,revision:row.revision,textHash:row.textHash,viewHash:row.viewHash,contentHash:row.contentHash});}catch{++unavailable;}}
    changed();
   }
   if(alive()){phase=unavailable||unsupported?'partial':'ready';changed();}
  }catch(error){if(alive()){phase='failed';changed();}}
  finally{if(job===token){job=null;changed();}}
 }
 function refresh(){if(!enabled)return;reset();changed();ensure(true);}
 function close(){if(!enabled&&!job&&!timer&&!rows.size)return;enabled=false;reset();changed();}
 return {ensure,refresh,close,get rows(){return rows},get status(){return {phase,loaded:rows.size,unsupported,unavailable};}};
}
