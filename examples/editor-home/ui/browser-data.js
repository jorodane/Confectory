import {parseTypedJson} from './typed-json.js';
// Shared original Browser cells: private input receipts are never login/permission grants.
export function createBrowserDataCells(api){
 const {w,view,values,reads,name,currentWindow,alive,esc}=api;
 const persist=()=>api.persist(),fail=(_,error)=>api.fail(error);
 const enqueue=run=>api.enqueue(run);
 const cellKey=(id,column)=>JSON.stringify([id,column]),version=row=>({revision:row.revision,textHash:row.textHash,viewHash:row.viewHash}),proof=row=>({...version(row),contentHash:row.contentHash}),sameProof=(a,b)=>a.revision===b.revision&&a.textHash===b.textHash&&a.viewHash===b.viewHash;
 const dataOwner=()=>currentWindow()&&w.el.isConnected&&!w.el.hidden;
 function dataError(key,code){const text=code==='element-value-stale'?'값을 보는 동안 원본이나 정의가 바뀌었어요. 입력은 보관했어요. Esc로 입력을 취소하고 현재 값을 확인해 주세요.':'값을 적용하지 못했어요. 입력을 확인하고 Enter로 다시 시도해 주세요.';const record=view.meta.dataInputs[key];if(record)view.meta.dataInputs[key]={...record,error:text};if(currentWindow()){w.elementDataError={key,text};fail(w,Error(text));const input=[...w.el.querySelectorAll('[data-cell-key]')].find(input=>input.dataset.cellKey===key);input?.setAttribute('aria-invalid','true');if(input)input.title=text;api.persist();}}
 // A cell response stages source only. Keep its acknowledged intent until a verified
 // saved checkpoint contains it; cold startup never replays a write.
 const fieldRaw=field=>{if(!field)return null;const node=parseTypedJson(field.valueJson);return node.kind==='string'?node.value:node.raw??'';};
 function rememberProof(id,...rows){const history=view.meta.dataProofs[id]||[];for(const row of rows)if(!history.some(value=>sameProof(value,row)))history.push(proof(row));view.meta.dataProofs[id]=history.length>32?[history[0],...history.slice(-31)]:history;}
 function checkpointReceipt(row){for(const [key,record] of Object.entries(view.meta.dataInputs)){if(record.id!==row.id||record.ackRaw===undefined||record.raw!==record.ackRaw||!row.checkpointSaved)continue;const field=row.fields.find(field=>field.column===record.column);if(field?.writable&&fieldRaw(field)===record.raw)delete view.meta.dataInputs[key];}if(!Object.values(view.meta.dataInputs).some(record=>record.id===row.id))delete view.meta.dataProofs[row.id];}
 function commitCell(key){
  const record=view.meta.dataInputs[key];if(!record||api.jobs.has(key))return api.jobs.get(key)?.promise;const job={record,sent:false,cancelled:false};api.jobs.set(key,job);
  const run=async()=>{if(job.cancelled)return;let sent=job.record;try{if(!dataOwner())throw Error('element-cell-target-changed');
    const fresh=(await api.readElements([sent.id],dataOwner)).rows.find(row=>row.id===sent.id&&row.status==='available');if(job.cancelled)return;if(!fresh)throw Error('element-values-unavailable');const field=fresh.fields.find(field=>field.column===sent.column);if(!field?.writable)throw Error('element-value-stale');
    const sameContent=typeof sent.contentHash==='string'&&/^[a-f0-9]{64}$/.test(sent.contentHash)&&sent.textHash===fresh.textHash&&sent.contentHash===fresh.contentHash;
    if(!sameProof(fresh,sent)&&!sameContent&&!(view.meta.dataProofs[sent.id]||[]).some(value=>sameProof(value,fresh)))throw Error('element-value-stale');
    rememberProof(sent.id,sent,fresh);sent={...sent,...proof(fresh)};
    // An explicit retry may recover an exact content snapshot after revision counters reset.
    // The server still receives and atomically checks that fresh proof.
    const valueJson=api.valueJson({value:sent.raw,type:sent.inputKind==='boolean'?'checkbox':'text',checked:sent.raw==='true'},{inputKind:sent.inputKind,type:sent.type,kind:sent.kind,cardinality:'single'});let next=fresh;
    if(field.valueJson!==valueJson){job.sent=true;const result=await api.editElement({id:sent.id,column:sent.column,valueJson,version:version(sent)},dataOwner);if(!result.accepted)throw Error(result.code||'element-value-rejected');next=result.row;}
    rememberProof(sent.id,next);
    for(const [name,value] of Object.entries(view.meta.dataInputs)){if(value.id!==sent.id)continue;if(name===key)view.meta.dataInputs[name]={...value,...proof(next),ackRaw:sent.raw,error:undefined};else if(sameProof(value,job.record)||sameProof(value,sent))view.meta.dataInputs[name]={...value,...proof(next)};}
    for(const other of api.jobs.values())if(other!==job&&!other.sent&&other.record.id===sent.id&&sameProof(other.record,job.record))other.record={...other.record,...proof(next)};
    checkpointReceipt(next);
    if(currentWindow()){const current=api.activeView();current?.values?.set(next.id,next);if(w.elementDataError?.key===key){const message=w.el.querySelector('[data-element-error]');if(message?.textContent===w.elementDataError.text)message.textContent='';w.elementDataError=null;}api.persist();const focused=document.activeElement;if(!focused?.matches('[data-browser-value]')||!w.el.contains(focused))current?.render?.();else if(focused.dataset.cellKey===key){focused.removeAttribute('aria-invalid');}}
   }catch(error){dataError(key,error.message);}finally{if(api.jobs.get(key)===job)api.jobs.delete(key);}};
  job.promise=enqueue(run);return job.promise;
 }

 function dataFields(row){
  if(row.owned===false||row.kind!=='object')return '';const data=values.get(row.id);if(!data)return '<small role="status">값을 불러오는 중이에요.</small>';if(data.status!=='available')return '<button type="button" class="secondary" data-values-retry="'+esc(row.id)+'">값을 다시 읽기</button>';
  const all=data.fields||[],fields=all.filter(field=>!['value:"editorName"','value:"editorIcon"'].includes(field.column)&&field.kind!=='function'&&field.state==='present'&&!all.some(parent=>parent.path.length<field.path.length&&parent.path.every((part,i)=>field.path[i]===part)&&parent.cardinality==='multiple')&&!(field.kind==='compound'&&field.cardinality==='single'&&all.some(child=>child.path.length>field.path.length&&field.path.every((part,i)=>child.path[i]===part))));
  const priority=['hp','speed','attack','drop','description'],rank=field=>{const i=priority.indexOf(field.kind==='description'?'description':field.path[0]);return i<0?priority.length:i;};fields.sort((a,b)=>rank(a)-rank(b)||a.path.join('.').localeCompare(b.path.join('.'),'ko'));
  return fields.map(field=>{const label=field.kind==='description'?'설명':field.path.join('.'),key=cellKey(row.id,field.column),pending=view.meta.dataInputs[key];let node;try{node=parseTypedJson(field.valueJson);}catch{}const complex=field.cardinality==='multiple'||['compound','reference'].includes(field.kind)||node?.kind==='object'||node?.kind==='array';let control;
   if(complex)control='<button type="button" class="secondary" data-data-detail="'+esc(row.id)+'" data-detail-path="'+esc(JSON.stringify(field.path))+'">'+(field.cardinality==='multiple'?(node?.items?.length||0)+'개 값 · ':'')+'편집</button>';
   else{const boolean=node?.kind==='boolean',text=pending?.raw??(node?.kind==='string'?node.value:node?.raw??'');control='<input data-browser-value="'+esc(row.id)+'" data-cell-key="'+esc(key)+'" data-browser-column="'+esc(field.column)+'" aria-label="'+esc(name(row.id)+' '+label)+'" type="'+(boolean?'checkbox':node?.kind==='number'?'number':'text')+'" '+(boolean?(text==='true'?'checked ':'')+(field.writable?'':'disabled'):'value="'+esc(text)+'" '+(field.writable?'':'readonly'))+' aria-invalid="'+String(!!pending?.error)+'" title="'+esc(pending?.error||(field.writable?'Enter 또는 다른 곳을 눌러 변경을 적용해요.':'값 변경은 상세 편집에서 확인해 주세요.'))+'">';}
   return '<div class="browser-data-field"><span class="browser-property-label" title="'+esc(label)+'" aria-label="'+esc(label)+'">'+esc(label)+'</span>'+control+'</div>';
  }).join('');
 }
 function bindCells(list){
  for(const input of list.querySelectorAll('[data-browser-value]')){
   const key=input.dataset.cellKey,id=input.dataset.browserValue,column=input.dataset.browserColumn,data=values.get(id),field=data?.fields?.find(field=>field.column===column);if(!field?.writable)continue;
   input.oninput=()=>{if(!dataOwner())return;const old=view.meta.dataInputs[key],raw=input.type==='checkbox'?String(input.checked):input.value,baseline=parseTypedJson(field.valueJson),original=baseline.kind==='string'?baseline.value:baseline.raw??'';if(raw===original&&old?.ackRaw===undefined&&!api.jobs.has(key))delete view.meta.dataInputs[key];else view.meta.dataInputs[key]={...(old||{id,column,...proof(data),kind:field.kind,type:field.type,inputKind:field.inputKind}),raw,token:crypto.randomUUID(),error:undefined};input.removeAttribute('aria-invalid');api.persist();};
   input.onchange=()=>{const record=view.meta.dataInputs[key];if(record&&!record.error&&record.raw!==record.ackRaw)commitCell(key);};input.onkeydown=e=>{if(e.isComposing||e.keyCode===229)return;if(e.key==='Enter'){e.preventDefault();e.stopPropagation();commitCell(key);}else if(e.key==='Escape'){e.preventDefault();e.stopPropagation();const job=api.jobs.get(key);if(job&&!job.sent)job.cancelled=true;const record=view.meta.dataInputs[key];if(record?.ackRaw!==undefined&&record.raw!==record.ackRaw)view.meta.dataInputs[key]={...record,raw:record.ackRaw,token:crypto.randomUUID(),error:undefined};else if(job?.sent)view.meta.dataInputs[key]={...job.record,token:crypto.randomUUID()};else delete view.meta.dataInputs[key];input.onchange=null;input.blur();values.delete(id);api.persist();api.activeView()?.render?.();}};
  }
 }
 function readValues(items){
  const missing=items.filter(row=>row.owned!==false&&row.kind==='object'&&!values.has(row.id)&&!reads.has(row.id));if(!missing.length||!api.readElements)return;
  for(let i=0;i<missing.length;i+=8){const ids=missing.slice(i,i+8).map(row=>row.id);ids.forEach(id=>reads.add(id));const read=async()=>{if(!alive())return;return api.readElements(ids,alive);},promise=enqueue(read);promise.then(result=>{if(!alive()||!result)return;for(const id of ids){const row=result.rows.find(row=>row.id===id)||{id,status:'unavailable'};values.set(id,row);if(row.status==='available')checkpointReceipt(row);}api.persist();api.activeView()?.render?.();},()=>{if(!alive())return;for(const id of ids)values.set(id,{id,status:'unavailable'});api.activeView()?.render?.();}).finally(()=>ids.forEach(id=>reads.delete(id)));}
 }

 return {fields:dataFields,bind:bindCells,load:readValues,commit:commitCell};
}

let browserReads=Promise.resolve();
export function createStandaloneBrowserData(api){
 const name=id=>api.projection.rows().find(row=>row.id===id)?.title||id.split('::').at(-1);
 function render(w,root,items){
  const scope=api.current.projectId;
  if(!w.browserDataView||w.browserDataView.scope!==scope){
   w.meta.browserData??={dataInputs:{},dataProofs:{}};
   const view=w.browserDataView={scope,values:new Map(),reads:new Set(),items:[]};
   // Layout hydration may replace metadata; rendering, persistence and guards must
   // always read the same current private-input object, never a retired copy.
   Object.defineProperty(view,'meta',{get:()=>w.meta.browserData??={dataInputs:{},dataProofs:{}}});
   view.meta.dataInputs??={};view.meta.dataProofs??={};w.browserDataJobs??=new Map();
   const alive=()=>api.current.projectId===scope&&api.windows.get(w.key)===w&&w.browserDataView===view;
   view.cells=createBrowserDataCells(Object.create(api,Object.getOwnPropertyDescriptors({w,view,values:view.values,reads:view.reads,name,esc:api.esc,currentWindow:alive,alive,jobs:w.browserDataJobs,activeView:()=>w.browserDataView,fail:error=>api.toast(error.message),enqueue:run=>{const promise=browserReads.then(run,run);browserReads=promise.catch(()=>{});return promise;}})));
   view.render=()=>{if(alive())api.render(w.key);};
   view.saved=()=>{view.values.clear();view.stamp=null;view.render();};
  }
  const view=w.browserDataView;view.items=items;
  const stamp=JSON.stringify([items.map(row=>[row.id,row.kind,row.owned,row.title,row.revision,row.textHash]),[...view.values],view.meta.dataInputs]);
  if(view.stamp===stamp&&root.querySelector('.browser-data-list'))return;
  // Background reads must not replace text while the user is editing it.
  if(root.contains(document.activeElement)&&document.activeElement.matches('input,textarea,select'))return;
  view.stamp=stamp;
  const esc=api.esc;
  root.innerHTML='<div class="browser-data-list">'+items.map(row=>'<article class="object-data browser-data-row" data-object="'+esc(row.id)+'" data-id="'+esc(row.id)+'" tabindex="0"><div class="browser-data-identity"><span class="obj-icon">◇</span><button type="button" class="browser-data-name" data-inline-name="'+esc(row.id)+'">'+esc(name(row.id))+'</button></div><div class="browser-data-fields">'+view.cells.fields(row)+'</div><button type="button" class="browser-data-edit" data-data-detail="'+esc(row.id)+'" aria-label="'+esc(name(row.id))+' 편집">⋯</button></article>').join('')+'</div>';
  view.cells.bind(root);view.cells.load(items);
  for(const b of root.querySelectorAll('[data-values-retry]'))b.onclick=e=>{e.stopPropagation();view.values.delete(b.dataset.valuesRetry);view.stamp=null;view.render();};
  for(const b of root.querySelectorAll('[data-data-detail]'))b.onclick=async e=>{
   e.stopPropagation();if(b.disabled)return;b.disabled=true;
   try{
    const focused=document.activeElement;
    if(focused?.matches('[data-browser-value]')&&w.el.contains(focused))await view.cells.commit(focused.dataset.cellKey);
    await Promise.all([...w.browserDataJobs.values()].map(job=>job.promise));
    if(api.current.projectId!==scope||api.windows.get(w.key)!==w)return;
    const id=b.dataset.dataDetail;
    if(Object.values(view.meta.dataInputs).some(record=>record.id===id&&record.error))throw Error('보관된 입력을 확인하고 Enter로 적용하거나 Esc로 취소해 주세요.');
    if(!items.some(row=>row.id===id&&row.owned!==false&&row.kind==='object')){api.open(items.find(row=>row.id===id));return;}
    await api.detail(id,b.dataset.detailPath?JSON.parse(b.dataset.detailPath):[],()=>api.current.projectId===scope&&api.windows.get(w.key)===w);
   }catch(error){api.toast(error.message);}finally{b.disabled=false;}
  };
 }
 return {render,saved:()=>{for(const w of api.windows.values())if(w.browserDataView?.scope===api.current.projectId)w.browserDataView.saved();}};
}
