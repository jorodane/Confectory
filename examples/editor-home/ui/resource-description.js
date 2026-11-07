// Display metadata only. The exact private pending request survives a lost reply;
// no automatic rebasing over another writer or a reused resource identity.
const id=/^[a-f0-9]{32}$/,hash=/^[a-f0-9]{64}$/;
export function createResourceDescriptions(api){
 const bindings=new Map(),running=new WeakSet();
 const scope=()=>api.current?.projectId||'';
 const draft=w=>w.meta.resourceDescriptionDraft;
 const valid=d=>d&&d.owner===scope()&&id.test(d.id)&&hash.test(d.generation)&&hash.test(d.revision)&&typeof d.value==='string'&&d.value.length<=1000&&typeof d.original==='string'&&d.original.length<=1000;
 const pending=w=>!!draft(w);
 function paint(w){for(const b of bindings.get(w)||[]){if(!b.field.isConnected)continue;const d=draft(w),owns=valid(d)&&d.id===b.item.id&&d.generation===b.item.descriptionGeneration;b.field.readOnly=!!d&&!owns;b.field.value=owns?d.value:b.item.description||'';b.output.textContent=d&&!owns?'다른 자료의 설명 입력을 먼저 확인해 주세요.':owns?(d.message||(running.has(w)?'설명을 저장하고 있습니다…':d.pending?'저장 결과를 확인하지 못했어요. 같은 요청으로 확인하거나 입력만 취소할 수 있어요.':'설명 변경 있음')):'';b.retry.hidden=!owns||!d.pending;b.retry.disabled=running.has(w);b.cancel.hidden=!owns;b.cancel.disabled=running.has(w);}}
 async function call(owner,action,input,active){for(let n=0;n<3;n++){if(scope()!==owner||!active())throw Error('scope_changed');await api.view.update();if(scope()!==owner||!active())throw Error('scope_changed');try{return await api.view.call('projectResourceLayout',{project:owner,action,...input});}catch(e){if(e.message!=='stale_revision'||n===2)throw e;}}}
 async function save(w,b){const d=draft(w);if(!valid(d)||d.id!==b.item.id||d.generation!==b.item.descriptionGeneration||running.has(w)||!b.active())return;
  if(!d.pending&&d.value===d.original){delete w.meta.resourceDescriptionDraft;api.persist();paint(w);return;}
  d.pending??={revision:d.revision,command:crypto.randomUUID().replaceAll('-',''),id:d.id,generation:d.generation,value:d.value};const input=structuredClone(d.pending),owner=d.owner;running.add(w);delete d.message;paint(w);api.persist();
  await api.work(async()=>{try{
   await api.flush();if(draft(w)!==d||!b.active()||scope()!==owner)throw Error('scope_changed');
   const reply=await call(owner,'describe',input,b.active);if(draft(w)!==d||!b.active()||scope()!==owner)throw Error('scope_changed');
   const row=reply?.items?.find(row=>row.id===d.id);if(reply.project!==owner||reply.command!==input.command||!hash.test(reply.revision)||row?.descriptionGeneration!==d.generation||row.description!==input.value)throw Error('resource_description_receipt');
   delete d.pending;d.original=input.value;d.revision=reply.revision;for(const other of bindings.get(w)||[])if(other.item.id===d.id){other.item=row;other.revision=reply.revision;}
   if(d.value===input.value)delete w.meta.resourceDescriptionDraft;else d.message='저장한 뒤 입력한 설명은 유지됩니다. 입력란을 벗어나면 이어서 저장할 수 있어요.';
   api.accept(reply);api.persist();await api.flush();
  }catch(e){if(draft(w)===d)d.message='설명 저장 결과를 확인하지 못했어요. 입력은 유지됩니다. 같은 요청으로 다시 확인하거나 입력만 취소할 수 있어요.';throw e;}
  finally{running.delete(w);paint(w);}},null,{flushWorkspace:false});
 }
 async function cancel(w,b,closeAfter=false){const d=draft(w);if(!valid(d)||running.has(w)||!b.active())return;running.add(w);paint(w);
  await api.work(async()=>{try{const reply=await call(d.owner,'load',{},b.active);if(draft(w)!==d||!b.active()||scope()!==d.owner)throw Error('scope_changed');delete w.meta.resourceDescriptionDraft;api.persist();await api.flush();api.accept(reply);paint(w);if(closeAfter)api.close(w);}catch(e){if(!draft(w))w.meta.resourceDescriptionDraft=d;d.message='현재 보관본을 확인하지 못했어요. 설명 입력은 유지됩니다.';throw e;}finally{running.delete(w);paint(w);}},null,{flushWorkspace:false});
 }
 function bind({w,field,item,revision,active}){
  const output=document.createElement('small');output.dataset.resourceDescriptionStatus='';output.setAttribute('aria-live','polite');const actions=document.createElement('span'),retry=document.createElement('button'),cancelButton=document.createElement('button');retry.type=cancelButton.type='button';retry.textContent='설명 다시 확인';retry.dataset.resourceDescriptionRetry='';cancelButton.textContent='설명 입력 취소';cancelButton.dataset.resourceDescriptionCancel='';actions.append(retry,cancelButton);field.after(output,actions);
  const b={field,item,revision,active,output,retry,cancel:cancelButton};if(!bindings.has(w))bindings.set(w,new Set());bindings.get(w).add(b);field.maxLength=1000;
  const stop=e=>e.stopPropagation();for(const event of ['click','dblclick','pointerdown','dragstart'])field.addEventListener(event,stop);
  field.oninput=()=>{if(!active())return;let d=draft(w);if(d&&(!valid(d)||d.id!==item.id||d.generation!==item.descriptionGeneration)){paint(w);return;}if(!d){d={owner:scope(),id:item.id,generation:item.descriptionGeneration,revision:b.revision,original:b.item.description||'',value:field.value};w.meta.resourceDescriptionDraft=d;}d.value=field.value;delete d.message;api.persist();paint(w);};
  field.onchange=()=>{if(active())void save(w,b);};field.onkeydown=e=>{e.stopPropagation();if(e.key==='Escape'){e.preventDefault();void cancel(w,b);}else if(e.key==='Enter'&&field.tagName==='INPUT'||e.key==='s'&&(e.ctrlKey||e.metaKey)){e.preventDefault();void save(w,b);}};
  retry.onclick=()=>void save(w,b);cancelButton.onclick=()=>void cancel(w,b);w.resourceDescriptionBeforeClose=()=>{
   if(!draft(w))return false;if(running.has(w))return true;
   api.modal('저장하지 않은 설명','<p>설명 입력만 취소하고 창을 닫으시겠습니까? 이미 저장한 설명은 되돌리지 않습니다.</p><div class="row end"><button class="secondary" data-keep>계속 편집</button><button class="primary" data-discard>입력 취소</button></div>',(root,close)=>{root.querySelector('[data-keep]').onclick=close;root.querySelector('[data-discard]').onclick=()=>{close();void cancel(w,b,true);};});return true;};paint(w);
  return ()=>{bindings.get(w)?.delete(b);if(!bindings.get(w)?.size){bindings.delete(w);w.resourceDescriptionBeforeClose=null;}output.remove();actions.remove();};
 }
 function metadata(w,item,revision){for(const b of bindings.get(w)||[])if(b.item.id===item.id){b.item=item;b.revision=revision||b.revision;}paint(w);}
 return {bind,metadata,pending,active:w=>!!draft(w)&&bindings.has(w),beforeClose:w=>w.resourceDescriptionBeforeClose?.()||false};
}
