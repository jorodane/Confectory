// Real source snapshots are ephemeral; only the user's unapplied candidate is presentation.
export function createSourceConflicts(api){
 const {$,$$,esc,inputs}=api;
 const key=(scope,id)=>scope+'|'+id;
 const same=(record,data)=>!!record&&record.revision===data?.revision&&record.draftHash===data?.draftHash&&record.fileHash===data?.fileHash;
 const binding=data=>({revision:data.revision,draftHash:data.draftHash,fileHash:data.fileHash});
 const reasons={PREVIEW_BUDGET:'이 파일은 전체 비교 표시 예산을 초과했습니다.',CREATION_WORKFLOW_REQUIRED:'새 선언은 생성과 등록부 검토 흐름에서 처리하세요.',FILE_MISSING:'현재 파일이 없습니다. 공유 초안은 유지했습니다.',SOURCE_KIND:'이 소스 종류의 충돌 해결은 지원하지 않습니다.',SOURCE_VERSION_CHANGED:'파일 또는 공유 초안이 바뀌었습니다. 입력은 유지했습니다. 다시 읽고 비교 기준을 선택하세요.',DRAFT_CHANGED_DURING_READ:'읽는 동안 공유 초안이 바뀌었습니다. 다시 읽으세요.',FILE_CHANGED_DURING_READ:'읽는 동안 파일이 바뀌었습니다. 다시 읽으세요.'};
 function show(id,data=null,meta={}){
  const scope=api.current.projectId,k=key(scope,id),w=api.openWindow('conflict','소스 비교 · '+id.split('::').at(-1),880,430,{refresh:true});Object.assign(w.meta,meta,{conflictSourceId:id});w.title='소스 비교 · '+id.split('::').at(-1);$('.caption strong',w.el).textContent=w.title;w.el.setAttribute('aria-label',w.title);w.conflictData=data;
  const raw=api.sourceInput();if(raw.dirty&&raw.id===id&&!inputs.has(k))inputs.set(k,{text:raw.text,revision:raw.revision,draftHash:null,fileHash:null,rawOrigin:{text:raw.text,revision:raw.revision}});
  const record=inputs.get(k),available=data&&['baseText','fileText','draftText'].every(name=>typeof data[name]==='string');
  w.body.innerHTML=`<div class="window-content source-conflict"><div class="source-conflict-heading"><strong data-conflict-id>${esc(id)}</strong><button data-operation data-conflict-read>현재 값 다시 읽기</button></div><p class="small" data-conflict-status>${!data?'프로세스 복원 후 비교 값은 다시 읽어야 합니다. 미적용 입력은 유지됩니다.':data.code?esc(reasons[data.code]||data.code):data.status==='conflict'?'기준 이후에 현재 파일이 바뀌었습니다.':'마지막으로 읽은 파일과 공유 초안입니다.'}</p>${available?'<div class="source-conflict-versions">'+[['baseText','기준 파일'],['fileText','현재 파일'],['draftText','공유 초안']].map(([name,label])=>`<label>${label}<button data-operation data-conflict-use="${name}">이 내용 사용</button><textarea data-conflict-version="${name}" readonly spellcheck="false"></textarea></label>`).join('')+'</div>':''}<label class="source-conflict-candidate">합칠 내용 · 공유 초안에 적용<textarea data-conflict-candidate maxlength="262144" spellcheck="false"></textarea></label><p class="small" data-conflict-notice></p><div class="actions"><button data-operation data-conflict-bind>입력 유지하고 현재 기준 선택</button><button data-operation data-conflict-apply>공유 초안에 합치기</button><button data-operation data-conflict-save>Save</button><button data-operation data-conflict-review>Review…</button></div><details class="small"><summary>리비전과 내용 해시</summary><pre data-conflict-proof></pre></details></div>`;
  const candidate=$('[data-conflict-candidate]',w.body);candidate.value=record?.text??(available?data.draftText:'');
  if(available)for(const area of $$('[data-conflict-version]',w.body))area.value=data[area.dataset.conflictVersion];
  $('[data-conflict-proof]',w.body).textContent=data?JSON.stringify({revision:data.revision,baselineHash:data.baselineHash,draftHash:data.draftHash,fileHash:data.fileHash},null,2):'비교 값을 아직 읽지 않았습니다.';
  const notice=()=>{
   const local=inputs.get(k),stale=!!local&&!same(local,data),live=api.current.draft,changed=live?.id===id&&data&&live.revision!==data.revision;
   $('[data-conflict-notice]',w.body).textContent=w.conflictError||((stale||changed)?'비교 대상이 바뀌었습니다. 입력은 유지됩니다. 다시 읽고 현재 기준을 명시적으로 선택하세요.':'합치기는 공유 초안 편집입니다. Save 후 새 Review/Confirm으로 최종 반영하세요.');
   $('[data-conflict-apply]',w.body).dataset.supported=String(!!available&&data.canResolve===true&&!stale&&!changed);
   $('[data-conflict-bind]',w.body).dataset.supported=String(!!available&&data.canResolve===true&&!!local&&stale&&!changed);
   $('[data-conflict-save]',w.body).dataset.supported=String(api.current.draft?.id===id);
   $('[data-conflict-review]',w.body).dataset.supported=String(api.current.draft?.id===id&&!local);
   api.controls();
  };w.conflictNotice=notice;
  candidate.oninput=()=>{const old=inputs.get(k);inputs.set(k,{...(old|| (data?binding(data):{revision:null,draftHash:null,fileHash:null})),text:candidate.value});w.conflictError=null;api.persist();notice();};
  for(const button of $$('[data-conflict-use]',w.body))button.onclick=()=>{inputs.set(k,{...(inputs.get(k)||{}),...binding(data),text:data[button.dataset.conflictUse]});candidate.value=inputs.get(k).text;w.conflictError=null;api.persist();notice();};
  $('[data-conflict-bind]',w.body).onclick=()=>{if(!data?.canResolve||!inputs.has(k))return;inputs.set(k,{...inputs.get(k),...binding(data),text:candidate.value});w.conflictError=null;api.persist();notice();};
  $('[data-conflict-read]',w.body).onclick=()=>open(id);
  $('[data-conflict-apply]',w.body).onclick=()=>api.work(async()=>{
   if(api.current.projectId!==scope||api.current.draft?.id!==id)throw Error('비교할 소스 선택이 바뀌었습니다. 입력은 유지됩니다.');
   const local=inputs.get(k);if(!available||!data.canResolve||(local&&!same(local,data)))throw Error('현재 비교 기준을 다시 확인하세요.');
   const submitted=JSON.stringify(local),raw=api.sourceInput(),text=candidate.value;
   const result=await api.view.call('resolveSourceConflict',{id,text,...binding(data)});
   if(result.accepted!==true){w.conflictError=reasons[result.code]||'파일 또는 초안이 바뀌었습니다. 다시 비교하세요.';notice();return false;}
   if(api.current.projectId!==scope)throw Error('프로젝트가 바뀌었습니다.');
   if(JSON.stringify(inputs.get(k))===submitted)inputs.delete(k);
   api.acceptSource(id,raw,local?.rawOrigin);api.persist();
   const fresh=await api.view.call('inspectSourceConflict',{id});if(api.current.projectId!==scope)throw Error('프로젝트가 바뀌었습니다.');if(api.windows.get('conflict')===w&&w.el.isConnected)show(id,fresh,w.meta);
  },'공유 초안에 합쳤습니다. 최종 파일은 변경하지 않았습니다.');
  $('[data-conflict-save]',w.body).onclick=()=>api.work(async()=>{if(inputs.has(k))throw Error('미적용 합치기 입력을 먼저 처리하세요.');if(api.current.projectId!==scope||api.current.draft?.id!==id)throw Error('소스 선택이 바뀌었습니다.');await api.view.call('saveDraft',{});},'Draft saved; final sources unchanged');
  $('[data-conflict-review]',w.body).onclick=()=>{if(inputs.has(k)){api.toast('미적용 합치기 입력을 먼저 처리하세요.');return;}api.review(id);};notice();return w;
 }
 function open(id=api.current.draft?.id){
  const scope=api.current.projectId,prior=api.windows.get('conflict');return api.work(async()=>{
   if(!id||api.current.projectId!==scope)throw Error('소스를 먼저 선택하세요.');const raw=api.sourceInput();
   if(raw.dirty&&raw.id!==id)throw Error('현재 소스의 미적용 입력을 먼저 처리하세요.');
   if(api.current.draft?.id!==id)await api.view.call('select',{id});
   const data=await api.view.call('inspectSourceConflict',{id});if(api.current.projectId!==scope)throw Error('프로젝트가 바뀌었습니다.');
   const k=key(scope,id);if(raw.dirty&&!inputs.has(k))inputs.set(k,{text:raw.text,revision:raw.revision,draftHash:null,fileHash:null,rawOrigin:{text:raw.text,revision:raw.revision}});
   if(prior&&(!prior.el.isConnected||api.windows.get('conflict')!==prior))return false;api.reveal('conflict');const w=show(id,data);api.focus(w);api.persist();
  },'현재 파일과 공유 초안 비교');
 }
 function restore(meta){const id=meta.conflictSourceId;if(!id)return null;return show(id,null,meta);}
 function update(){const w=api.windows.get('conflict');w?.conflictNotice?.();}
 return {open,restore,update};
}
