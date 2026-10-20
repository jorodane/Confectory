// Registered provider configuration, Helper identity and global conversation are separate owners.
export function createHelperAgentsUI(api){
 const {$,$$,esc}=api,loaded=new Set(),drafts=new Map(),pending=new Set(),uncertain=new Map(),history=new Map(),loadingHistory=new Set(),recoveredDrafts=new Set(),notices=new Set();let saveTimer=null,saving=null,conflictOpen=false;
 const state=()=>api.current?.helperAgents||{agents:[],assignments:{},turns:{}};
 const agents=()=>state().agents||[],assigned=id=>state().assignments?.[id]||'';
 const title=id=>api.connectionTitle((api.current.connections||[]).find(row=>row.id===id)||{id});
 const supported=()=>api.current.globalHelperSupported===true&&!state().errorCode;
 const invoke=(action,payload={})=>api.view.call('helperGlobal',{action,...payload});

 const status=id=>{const row=state().turns?.[id];return row?.state==='running'?'전역 응답을 기다리는 중':row?.state==='completed'?(row.answerReceived?'전역 응답 수신':'응답 내용 없음'):row?.state==='error'?'전역 요청 실패':row?.state==='cancelled'?'전역 요청 취소됨':row?.state==='prepared'?'전역 전송 전 검토':assigned(id)?'전역 대화 준비':'Agent를 배정하세요.';};
 function approval(preview,generation){
  api.modal('전역 대화 전송 전 검토',`<section data-global-approval><p><strong>${esc(title(preview.connection))} · ${esc(preview.model)}</strong></p><p>Helper: ${esc(preview.helper)} · 전역 대화</p><h3>이번 메시지</h3><pre class="consumer-output">${esc(preview.message)}</pre><details><summary>전송할 Helper·기억·대화 기록</summary><pre class="consumer-output">${esc(JSON.stringify(preview.context,null,2))}</pre></details><p>현재 프로젝트의 파일·참조·기억은 보내지 않습니다. 이 대화에는 프로젝트 편집 도구가 없습니다.</p><div data-global-permissions>${(preview.policy.requirements||[]).map(row=>`<label class="check"><input type="checkbox" data-global-permission="${esc(row.id)}"> ${esc(row.label||row.id)}</label>`).join('')}</div>${preview.canStart?'':'<p role="status">'+esc(preview.policy.blockedReason||'연결 설정에서 사전 확인을 완료한 뒤 다시 검토하세요.')+'</p>'}<p class="small">요청은 사용량이나 비용을 발생시킬 수 있습니다. 초안과 기록 저장은 AI 응답 수신과 별개입니다.</p><div class="actions"><button class="primary" data-operation data-global-start data-supported="false">승인한 내용으로 전송</button><button data-global-review-cancel>취소 · 입력 보관</button></div></section>`,(root,close)=>{
   const start=$('[data-global-start]',root),requirements=preview.policy.requirements||[];
   const ready=()=>{const ok=preview.canStart===true&&api.current.helperAgents?.preview?.token===preview.token&&requirements.every(row=>$('[data-global-permission="'+CSS.escape(row.id)+'"]',root)?.checked);start.dataset.supported=String(ok);start.disabled=!ok||api.busy;};
   for(const checkbox of $$('[data-global-permission]',root))checkbox.onchange=ready;
   start.onclick=()=>api.action(async()=>{const approvals=Object.fromEntries($$('[data-global-permission]',root).map(input=>[input.dataset.globalPermission,input.checked]));await invoke('start',{helper:preview.helper,token:preview.token,approvals});await accepted({id:preview.helper},preview.message,generation);close();},'전역 요청 시작됨');
   const cancel=()=>api.action(async()=>{await invoke('cancel-preview');close();},'검토 취소됨 · 입력 보관');
   $('[data-global-review-cancel]',root).onclick=$('[data-close]',root).onclick=cancel;
   const keys=root.onkeydown;root.onkeydown=e=>{if(e.key==='Escape'){e.preventDefault();cancel();}else keys(e);};root.parentElement.onclick=e=>{if(e.target===root.parentElement)cancel();};ready();
  });
 }
 // Match the original v508 helperChat content; behavior changes do not add layout.
 function remember(helper,text){const draft=api.draft(helper);draft.value.globalDraft=text;draft.dirty=true;draft.editGeneration=(draft.editGeneration||0)+1;drafts.set(helper.id,helper);clearTimeout(saveTimer);saveTimer=setTimeout(()=>flushDrafts().catch(draftFailure),180);}
 function draftFailure(error){
  if(error.message!=='helper_draft_changed'){api.toast('입력을 아직 보관하지 못했어요. 입력은 유지됩니다. 다시 시도하세요.');return;}
  if(conflictOpen)return;conflictOpen=true;const saved=error.saved,helper=drafts.get(saved?.value?.helper);if(!helper||!saved){conflictOpen=false;return;}
  api.modal('보관된 입력이 바뀌었어요',`<p>저장된 입력과 현재 입력을 함께 유지하고 있어요. 사용할 입력을 선택하세요.</p><div class="actions"><button data-keep-saved>저장된 입력 사용</button><button class="primary" data-keep-mine>내 입력 보관</button><button data-later>나중에</button></div>`,(root,close)=>{
   const finish=()=>{conflictOpen=false;close();};$('[data-later]',root).onclick=$('[data-close]',root).onclick=finish;const keys=root.onkeydown;root.onkeydown=e=>{if(e.key==='Escape'){e.preventDefault();finish();}else keys?.(e);};root.parentElement.onclick=e=>{if(e.target===root.parentElement)finish();};
   $('[data-keep-saved]',root).onclick=()=>{const draft=api.draft(helper);Object.assign(draft,{revision:saved.revision,draftRevision:saved.draftRevision,value:saved.value,dirty:false});drafts.delete(helper.id);for(const card of $$('[data-global-helper="'+CSS.escape(helper.id)+'"]'))$('textarea',card).value=saved.value.globalDraft;finish();};
   $('[data-keep-mine]',root).onclick=()=>{api.draft(helper).draftRevision=saved.draftRevision;finish();flushDrafts().catch(draftFailure);};
  });
 }
 async function flushDrafts(){
  clearTimeout(saveTimer);if(saving){await saving;return flushDrafts();}
  saving=(async()=>{for(const [id,helper] of drafts){while(api.draft(helper).dirty)await api.saveDraft(helper);drafts.delete(id);}})();try{await saving;}finally{saving=null;}
 }
 addEventListener('beforeunload',e=>{if([...drafts.values()].some(h=>api.draft(h).dirty)){void flushDrafts().catch(()=>{});e.preventDefault();e.returnValue='';}});
 document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='hidden')void flushDrafts().catch(draftFailure);});
 const baseline=new Set(['contentApproved','usageApproved','processApproved','managedCredentialApproved','managedConfigurationApproved','managedStorageApproved']);
 async function ensureReady(helper){
  const initial=agents().find(row=>row.id===assigned(helper.id));if(initial?.id!=='Confectory.Agent.Codex::Connection')return;
  const basis=JSON.stringify([initial.id,initial.configFingerprint,initial.accountIdentity?.fingerprint]);
  const unchanged=()=>{const current=agents().find(row=>row.id===assigned(helper.id));if(!current||current.state==='offline'||JSON.stringify([current.id,current.configFingerprint,current.accountIdentity?.fingerprint])!==basis)throw Error('확인 중인 Agent 설정이 바뀌었어요. 다시 보내세요. [codex-readiness-changed]');};
  const call=async payload=>{for(let retry=0;;retry++){try{return await invoke('readiness',{helper:helper.id,...payload});}catch(error){if(error.message!=='stale_revision'||retry===2)throw error;await api.view.update();unchanged();}}};
  unchanged();let result=await call({begin:true});const deadline=Date.now()+95000;
  while(result.state==='checking'){if(Date.now()>deadline)throw Error('등록한 Agent의 연결 확인이 지연되고 있어요. Codex에서 상태를 확인하세요. [codex-readiness-timeout]');await new Promise(resolve=>setTimeout(resolve,100));unchanged();result=await call({token:result.token});}
  unchanged();if(result.state!=='ready')throw Error((result.message||'Codex에서 연결 상태를 확인하세요.')+' ['+(/^[a-z][a-z0-9_-]{0,79}$/.test(result.code||'')?result.code:'codex-readiness-failed')+']');
 }
 async function send(helper,message,generation){
  await flushDrafts();let preview=uncertain.get(helper.id);
  if(!preview)await ensureReady(helper);
  if(preview){await api.view.update();const row=state().turns?.[helper.id];if(row?.requestId===preview.token&&row.state!=='prepared'){uncertain.delete(helper.id);return preview.token;}if(api.current.helperAgents?.preview?.token!==preview.token)throw Error('전송 상태를 확인하지 못했어요. 연결을 확인한 뒤 다시 시도하세요.');}
  else for(let attempt=0;;attempt++){try{preview=await invoke('prepare',{helper:helper.id,message,includeCommon:false});break;}catch(error){if(error.message!=='stale_revision'||attempt===2)throw error;await api.view.update();}}
  const binding=agents().find(row=>row.id===assigned(helper.id));if(!binding||binding.state==='offline'||preview.connection!==binding.id||preview.model!==binding.model)throw Error('Helper의 Agent가 바뀌었어요. 연결을 확인한 뒤 다시 보내세요.');
  // A persisted registration outlives the session-only readiness proof. Missing or
  // expired evidence cannot establish a changed account and never permits start.
  if(!preview.canStart)throw Error(preview.policy?.blockedReason||'Agent 연결 상태를 다시 확인한 뒤 보내세요. [connection-verification-required]');
  const pinned=binding.accountIdentity?.fingerprint,observed=preview.policy?.verification?.accountIdentity?.fingerprint;
  if(pinned&&!observed)throw Error('현재 계정 확인 정보를 확인하지 못했어요. Codex에서 연결 상태를 다시 확인하세요. [codex-account-unverified]');
  if(pinned&&pinned!==observed)throw Error('연결한 계정의 확인 정보가 바뀌었어요. Codex에서 사용할 계정을 다시 확인하세요. [codex-account-mismatch]');
  const context=preview.context,scope=preview.policy?.contentScope;
  if(context?.projectId!==''||context?.membership?.kind!=='global'||scope?.kind!=='helper-global'||scope.helperId!==helper.id||scope.conversationId!==context.conversationId)throw Error('전역 대화 범위를 확인하지 못했어요.');
  if((preview.context.memory||[]).length>0||(preview.policy.requirements||[]).some(row=>!baseline.has(row.id))){approval(preview,generation);return false;}
  // Explicit Send authorizes this displayed message and its existing global-only Agent scope.
  // Unknown permissions still require the separate conditional approval; provider gates remain.
  uncertain.set(helper.id,preview);
  try{await invoke('start',{helper:helper.id,token:preview.token,approvals:Object.fromEntries(preview.policy.requirements.map(row=>[row.id,true]))});uncertain.delete(helper.id);return preview.token;}
  catch(error){await api.view.update().catch(()=>{});const row=state().turns?.[helper.id];if(row?.requestId===preview.token&&row.state!=='prepared'){uncertain.delete(helper.id);return preview.token;}throw error;}
 }
 async function accepted(helper,message,generation){
  const draft=api.draft(helper);if((draft.value.globalDraft!==message&&draft.value.globalDraft!=='')||(draft.editGeneration||0)!==generation)return;
  remember(helper,'');
  for(const card of $$('[data-global-helper="'+CSS.escape(helper.id)+'"]')){const input=$('textarea',card);if(input.value===message)input.value='';}await flushDrafts();
 }
 function renderGlobal(root,helper){
  const draft=api.draft(helper);root.dataset.conversationMode='global';root.dataset.globalHelper=helper.id;
  root.innerHTML=`<div class="window-content"><div class="messages" style="max-height:180px;margin:16px 0" aria-live="polite"></div><form class="helper-chat-compose" data-global-draft><div class="yogi-attachments"></div><textarea rows="1" maxlength="8192" placeholder="Helper에게 이야기하기…" aria-label="Helper 대화 입력">${esc(draft.value.globalDraft)}</textarea><button class="primary" type="submit" data-global-send data-operation data-supported="false">보내기</button></form></div>`;
  const input=$('textarea',root),form=$('form',root);let composing=false;
  input.addEventListener('compositionstart',()=>{composing=true;});input.addEventListener('compositionend',()=>{composing=false;remember(helper,input.value);});
  input.oninput=()=>{remember(helper,input.value);if(composing)clearTimeout(saveTimer);update(root);};
  input.onkeydown=e=>{if(e.key!=='Enter'||e.shiftKey||composing||e.isComposing||e.keyCode===229)return;e.preventDefault();if(!e.repeat&&!pending.has(helper.id)&&state().turns?.[helper.id]?.state!=='running')form.requestSubmit();};
  form.onsubmit=e=>{e.preventDefault();if(composing||e.isComposing||pending.has(helper.id))return;
   const row=state().turns?.[helper.id];if(row?.state==='running'){api.action(()=>invoke('cancel',{helper:helper.id,requestId:row.requestId}),'');return;}
   const message=input.value.trim()?input.value:retryRecord(helper.id)?.message;if(!message?.trim())return;const generation=api.draft(helper).editGeneration||0;pending.add(helper.id);update(root);
   api.action(async()=>{const token=await send(helper,message,generation);if(token)await accepted(helper,message,generation);},'').finally(()=>{pending.delete(helper.id);update(root);});
  };
  const box=$('.messages',root);box.onscroll=()=>{if(box.scrollTop<=0)older(root,helper);};box.addEventListener('wheel',e=>{if(e.deltaY<0&&box.scrollTop<=0)older(root,helper);},{passive:true});update(root);
  if(!loaded.has(helper.id)){const load=()=>{if(!root.isConnected)return;if(api.busy){setTimeout(load,50);return;}loaded.add(helper.id);api.action(()=>invoke('conversation',{helper:helper.id}),'').then(result=>{if(result===false)loaded.delete(helper.id);if(root.isConnected)update(root);});};setTimeout(load,0);}
 }
 function older(root,helper){const row=state().turns?.[helper.id];if(loadingHistory.has(helper.id)||api.busy||!row||(row.historyPage||0)+1>=(row.historyPages||1))return;loadingHistory.add(helper.id);api.action(()=>invoke('conversation',{helper:helper.id,page:(row.historyPage||0)+1}),'').finally(()=>loadingHistory.delete(helper.id));}
 const latest=id=>[...(history.get(id)?.values()||[])].sort((a,b)=>a.index-b.index).at(-1);
 const retryRecord=id=>{const last=latest(id);return last&&['error','cancelled','interrupted'].includes(last.state)?last:null;};
 function failureDetails(record,row){
  const code=record.errorCode||(row?.requestId===record.requestId?row.errorCode:'');if(!/^provider-[a-z-]{1,64}$/.test(code||''))return '';
  const info=record.errorDiagnostics||(row?.requestId===record.requestId?row.errorDiagnostics:null),parts=[code];
  if(['storage','process-start','initialize','account-read','configuration-read','runtime-features','requirements-read','policy-check','model-list','verification-check','thread-start','turn-start','response-events'].includes(info?.stage))parts.push(info.stage);
  if(['Win32Exception','UnauthorizedAccessException','IOException','JsonException','DecoderFallbackException','PlatformNotSupportedException','ArgumentException','InvalidOperationException','Other'].includes(info?.errorType))parts.push(info.errorType);
  if(['contextWindowExceeded','sessionBudgetExceeded','usageLimitExceeded','rateLimitExceeded','flexUnavailable','serverOverloaded','cyberPolicy','misalignmentPolicyViolation','internalServerError','unauthorized','badRequest','threadRollbackFailed','sandboxError','other','unknown','httpConnectionFailed','responseStreamConnectionFailed','responseStreamDisconnected','responseTooManyFailedAttempts'].includes(info?.providerErrorKind))parts.push(info.providerErrorKind);
  if(['frame-read','frame-parse','event-handle','rpc-response'].includes(info?.readPhase))parts.push(info.readPhase);
  if(['error','item/started','item/completed','item/agentMessage/delta','turn/started','turn/completed','other'].includes(info?.protocolEvent))parts.push(info.protocolEvent);
  for(const field of ['rpcErrorCode','nativeErrorCode','exitCode','httpStatusCode'])if(Number.isInteger(info?.[field]))parts.push(field+'='+info[field]);
  return ' ['+parts.join(' · ')+']';
 }
 function update(root){
  const id=root?.dataset.globalHelper;if(!id||root.dataset.conversationMode!=='global')return;
  const row=state().turns?.[id],agent=agents().find(agent=>agent.id===assigned(id));if(row?.historyError&&!notices.has(row.requestId)){notices.add(row.requestId);api.toast('받은 응답은 유지하지만 대화 기록을 보관하지 못했어요. 저장 상태를 확인하세요.');}let records=history.get(id);if(!records){records=new Map();history.set(id,records);}
  const offset=Math.max(0,(row?.recordCount||0)-(row?.historyPage||0)*2-(row?.records||[]).length);
  (row?.records||[]).forEach((record,index)=>records.set(record.requestId,{...record,index:offset+index}));
  if(row?.requestId&&records.has(row.requestId)){const record=records.get(row.requestId);if(row.state!=='prepared')Object.assign(record,{output:row.output||record.output,state:row.state,errorCode:row.errorCode,errorDiagnostics:row.errorDiagnostics});}
  const saved=api.draft({id}),last=latest(id);
  if(!recoveredDrafts.has(id)&&row?.recordCount){recoveredDrafts.add(id);if(last?.state==='interrupted'&&saved.value.globalDraft===''){$('textarea',root).value=last.message;remember({id},last.message);}}
  const list=[...records.values()].sort((a,b)=>a.index-b.index),box=$('.messages',root),stamp=JSON.stringify(list);
  if(box.dataset.stamp!==stamp){const bottom=box.scrollHeight-box.scrollTop-box.clientHeight<20,height=box.scrollHeight,top=box.scrollTop;box.innerHTML=list.map(record=>`<p><strong>나</strong> · ${esc(record.message).replace(/\n/g,'<br>')}</p><p><strong>${esc(api.draft({id}).value.name||id)}</strong> · ${esc((record.output||(record.state==='running'?'응답을 기다리고 있어요…':record.state==='error'?'응답을 받지 못했어요. 재시도로 다시 보낼 수 있어요.':record.state==='cancelled'?'응답을 중지했어요.':record.state==='interrupted'?'이전 응답이 중단됐어요.':''))+(record.state==='error'?failureDetails(record,row):'')).replace(/\n/g,'<br>')}</p>`).join('')||'<p class="muted">아직 대화가 없어요.</p>';box.dataset.stamp=stamp;box.scrollTop=loadingHistory.has(id)?top+box.scrollHeight-height:bottom?box.scrollHeight:top;}
  const button=$('[data-global-send]',root);if(!button.dataset.width)button.dataset.width=String(button.getBoundingClientRect().width);button.style.width=button.dataset.width+'px';const retry=!$('textarea',root).value.trim()&&retryRecord(id);button.textContent=row?.state==='running'?'중지':retry?'재시도':'보내기';button.setAttribute('aria-label',row?.state==='running'?'응답 중지':retry?'이전 메시지 다시 보내기':'메시지 보내기');button.dataset.supported=String(!pending.has(id)&&supported()&&!!agent&&agent.state!=='offline');button.disabled=api.busy||button.dataset.supported==='false';
 }
 return {renderGlobal,update,status,assigned,agents,ensureReady,flushDrafts:async()=>{try{await flushDrafts();}catch(error){draftFailure(error);throw error;}}};
}
