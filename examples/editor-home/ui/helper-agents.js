// Registered provider configuration, Helper identity and global conversation are separate owners.
export function createHelperAgentsUI(api){
 const {$,$$,esc}=api,loaded=new Set();let creation=null;
 const state=()=>api.current?.helperAgents||{agents:[],assignments:{},turns:{}};
 const agents=()=>state().agents||[],assigned=id=>state().assignments?.[id]||'';
 const title=id=>api.connectionTitle((api.current.connections||[]).find(row=>row.id===id)||{id});
 const supported=()=>api.current.globalHelperSupported===true&&!state().errorCode;
 const invoke=(action,payload={})=>api.view.call('helperGlobal',{action,...payload});
 const options=(selected='',empty='나중에 배정')=>`<option value="">${empty}</option>`+agents().map(agent=>`<option value="${esc(agent.id)}" ${agent.id===selected?'selected':''}>${esc(title(agent.id))} · ${esc(agent.model)}</option>`).join('');
 const status=id=>{const row=state().turns?.[id];return row?.state==='running'?'전역 응답을 기다리는 중':row?.state==='completed'?(row.answerReceived?'전역 응답 수신':'응답 내용 없음'):row?.state==='error'?'전역 요청 실패':row?.state==='cancelled'?'전역 요청 취소됨':row?.state==='prepared'?'전역 전송 전 검토':assigned(id)?'전역 대화 준비':'Agent를 배정하세요.';};
 function create(agent=''){
  creation??={creationId:crypto.randomUUID().replaceAll('-',''),name:'',personality:'',speciality:'',agent};
  const input=creation;
  api.modal('Helper 추가',`<form class="stack" data-helper-create><p>성격과 전문성을 정해 새 Helper를 만들거나 기본 Helper를 가져오세요.</p><label>이름<input id="participant-name" data-new-helper-name maxlength="80" required value="${esc(input.name)}"></label><label>간단 설명 · 전문성<input id="participant-short-description" data-new-helper-speciality maxlength="160" required value="${esc(input.speciality)}"></label><label>성격과 역할<textarea id="participant-description" data-new-helper-personality rows="4" maxlength="2048" required>${esc(input.personality)}</textarea></label><label>사용할 Agent<select data-new-helper-agent aria-label="사용할 Agent 선택">${options(input.agent)}</select></label><p class="small">${agents().length?'등록한 설정을 선택합니다. 실제 전송은 별도 검토합니다.':'등록한 Agent가 없습니다. Helper를 먼저 만들고 나중에 배정할 수 있습니다.'}</p><div class="actions"><button type="button" data-open-agent-settings>Agent 연결·등록</button><button class="primary" data-operation type="submit" data-helper-create-submit data-supported="${supported()}">Helper 만들기</button></div></form><section class="helper-import"><h3>기존 Helper 가져오기</h3><p>기본 Main Helper의 성격과 전문성을 가져옵니다. 기존 기억과 표시 프로필은 보존합니다.</p><button type="button" data-operation data-recruit="global" data-supported="${supported()}">Main Helper 가져오기</button>${api.current.projectId?'<button type="button" data-operation data-recruit="project">기존 프로젝트 Helper 모집</button>':''}</section>`,(root,close)=>{
   root.classList.add('helper-create-modal');root.dataset.helperCreator='true';
   for(const [selector,key] of [['[data-new-helper-name]','name'],['[data-new-helper-personality]','personality'],['[data-new-helper-speciality]','speciality'],['[data-new-helper-agent]','agent']])$(selector,root).oninput=e=>input[key]=e.target.value;
   $('[data-open-agent-settings]',root).onclick=()=>{close();api.settings();};
   $('form',root).onsubmit=e=>{e.preventDefault();api.action(async()=>{const result=await invoke('create',input);creation=null;close();api.openHelper(result.helper);},'Helper 생성됨 · 전송 없음');};
   $('[data-recruit="global"]',root).onclick=()=>api.action(async()=>{await invoke('import',{agent:input.agent});close();api.list();},'기본 Helper 가져옴 · 전송 없음');
   $('[data-recruit="project"]',root)?.addEventListener('click',()=>api.action(async()=>{await api.view.call('helperRecruit',{kind:'project'});close();api.list();},'프로젝트 Helper 모집됨 · 전송 없음'));
  });
 }
 function mountAssignment(root,helper){
  root.innerHTML=`<label>사용할 Agent<select data-helper-agent-select aria-label="사용할 Agent 선택" ${helper&&supported()?'':'disabled'}>${options(helper?assigned(helper.id):'','미배정')}</select></label><button type="button" data-helper-agent-settings>Agent 연결·등록</button>`;
  $('[data-helper-agent-settings]',root).onclick=()=>api.settings();
  const select=$('select',root);select.onchange=()=>{const next=select.value,prior=assigned(helper.id);api.action(async()=>{await invoke(next?'assign':'unbind',{helper:helper.id,agent:next});},'Helper의 Agent 배정 저장됨 · 전송 없음').then(result=>{if(result===false&&select.isConnected)select.value=prior;});};
 }
 function approval(preview){
  api.modal('전역 대화 전송 전 검토',`<section data-global-approval><p><strong>${esc(title(preview.connection))} · ${esc(preview.model)}</strong></p><p>Helper: ${esc(preview.helper)} · 전역 대화</p><h3>이번 메시지</h3><pre class="consumer-output">${esc(preview.message)}</pre><details><summary>전송할 Helper·기억·대화 기록</summary><pre class="consumer-output">${esc(JSON.stringify(preview.context,null,2))}</pre></details><p>현재 프로젝트의 파일·참조·기억은 보내지 않습니다. 이 대화에는 프로젝트 편집 도구가 없습니다.</p><div data-global-permissions>${(preview.policy.requirements||[]).map(row=>`<label class="check"><input type="checkbox" data-global-permission="${esc(row.id)}"> ${esc(row.label||row.id)}</label>`).join('')}</div>${preview.canStart?'':'<p role="status">'+esc(preview.policy.blockedReason||'연결 설정에서 사전 확인을 완료한 뒤 다시 검토하세요.')+'</p>'}<p class="small">요청은 사용량이나 비용을 발생시킬 수 있습니다. 초안과 기록 저장은 AI 응답 수신과 별개입니다.</p><div class="actions"><button class="primary" data-operation data-global-start data-supported="false">승인한 내용으로 전송</button><button data-global-review-cancel>취소 · 입력 보관</button></div></section>`,(root,close)=>{
   const start=$('[data-global-start]',root),requirements=preview.policy.requirements||[];
   const ready=()=>{const ok=preview.canStart===true&&api.current.helperAgents?.preview?.token===preview.token&&requirements.every(row=>$('[data-global-permission="'+CSS.escape(row.id)+'"]',root)?.checked);start.dataset.supported=String(ok);start.disabled=!ok||api.busy;};
   for(const checkbox of $$('[data-global-permission]',root))checkbox.onchange=ready;
   start.onclick=()=>api.action(async()=>{const approvals=Object.fromEntries($$('[data-global-permission]',root).map(input=>[input.dataset.globalPermission,input.checked]));await invoke('start',{helper:preview.helper,token:preview.token,approvals});close();},'전역 요청 시작됨');
   const cancel=()=>api.action(async()=>{await invoke('cancel-preview');close();},'검토 취소됨 · 입력 보관');
   $('[data-global-review-cancel]',root).onclick=$('[data-close]',root).onclick=cancel;
   const keys=root.onkeydown;root.onkeydown=e=>{if(e.key==='Escape'){e.preventDefault();cancel();}else keys(e);};root.parentElement.onclick=e=>{if(e.target===root.parentElement)cancel();};ready();
  });
 }
 function renderGlobal(root,helper){
  const draft=api.draft(helper);root.dataset.conversationMode='global';root.dataset.globalHelper=helper.id;
  root.innerHTML=`<div class="window-content global-helper-conversation"><h3>전역 대화</h3><p class="small" data-global-agent></p><div class="global-helper-messages" aria-live="polite"></div><div class="actions global-history-navigation"><button type="button" data-operation data-global-history-older data-supported="false">이전 기록</button><small data-global-history-page></small><button type="button" data-operation data-global-history-newer data-supported="false">최근 기록</button></div><p role="status" data-global-status></p><form class="stack" data-global-draft><textarea rows="3" maxlength="8192" aria-label="전역 Helper 대화 입력">${esc(draft.value.globalDraft)}</textarea><label class="check"><input type="checkbox" data-global-common> 이번 전송에 공통 기억 포함</label><div class="actions"><button type="submit" class="primary" data-operation data-global-prepare data-supported="false">보내기 전 검토</button><button type="button" data-operation data-global-save data-supported="${!!draft.revision}">전역 입력 보관</button><button type="button" data-global-discard>입력 버리기 · 저장본 다시 읽기</button></div></form><div class="actions"><button type="button" data-global-agent-settings>Agent 배정·설정</button><button type="button" data-operation data-global-stop data-supported="false">이 전역 요청 중지</button></div><p class="small">전역 입력과 대화 기록은 이 컴퓨터에 보관합니다. 받은 응답만 대화 결과로 표시합니다.</p></div>`;
  $('textarea',root).oninput=e=>{const draft=api.draft(helper);draft.value.globalDraft=e.target.value;draft.dirty=true;};
  $('form',root).onsubmit=e=>{e.preventDefault();const message=$('textarea',root).value,includeCommon=$('[data-global-common]',root).checked;api.action(async()=>{const preview=await invoke('prepare',{helper:helper.id,message,includeCommon});approval(preview);},'전역 전송 전 검토 · 아직 전송 없음');};
  $('[data-global-save]',root).onclick=()=>api.action(()=>api.save(helper),'전역 입력이 로컬에 보관됨 · 전송 없음');
  $('[data-global-discard]',root).onclick=()=>{api.discard(helper);renderGlobal(root,helper);};
  $('[data-global-agent-settings]',root).onclick=()=>api.openHelper(helper.id);
  $('[data-global-stop]',root).onclick=()=>{const requestId=state().turns?.[helper.id]?.requestId;api.action(()=>invoke('cancel',{helper:helper.id,requestId}),'원래 전역 요청에 중지 요청됨');};
  for(const [selector,direction] of [['[data-global-history-older]',1],['[data-global-history-newer]',-1]])$(selector,root).onclick=()=>api.action(()=>invoke('conversation',{helper:helper.id,page:(state().turns?.[helper.id]?.historyPage||0)+direction}),'보관한 전역 기록 조회 · 전송 없음');
  update(root);
  if(!loaded.has(helper.id)){
   const load=()=>{if(!root.isConnected)return;if(api.busy){setTimeout(load,50);return;}loaded.add(helper.id);api.action(()=>invoke('conversation',{helper:helper.id}),'').then(result=>{if(result===false)loaded.delete(helper.id);});};setTimeout(load,0);
  }
 }
 function update(root){
  const id=root.dataset.globalHelper;if(!id||root.dataset.conversationMode!=='global')return;
  const card=root.closest('.participant-expanded-card');if(card){const top=Math.max(112,Math.min(parseFloat(card.style.top)||225,innerHeight-360));card.style.top=top+'px';card.style.maxHeight=Math.max(180,innerHeight-top-12)+'px';}
  const row=state().turns?.[id],agent=agents().find(agent=>agent.id===assigned(id));
  $('[data-global-agent]',root).textContent=agent?title(agent.id)+' · '+agent.model+' · 설정 등록됨':'Agent 미배정 · 설정을 등록하고 이 Helper에 배정하세요.';
  $('[data-global-status]',root).textContent=status(id)+(row?.errorCode?' · '+row.errorCode:'')+(row?.historyError?' · 응답은 유지되지만 기록 저장을 확인해야 합니다.':'');
  $('[data-global-history-page]',root).textContent=`보관 기록 ${row?.recordCount||0}개 · ${(row?.historyPage||0)+1} / ${row?.historyPages||1}`;
  for(const [selector,ok] of [['[data-global-history-older]',(row?.historyPage||0)+1<(row?.historyPages||1)],['[data-global-history-newer]',(row?.historyPage||0)>0]]){const button=$(selector,root);button.dataset.supported=String(ok);button.disabled=api.busy||!ok;}
  const stamp=JSON.stringify([row?.records,row?.requestId,row?.state,row?.output,row?.historyError]);const box=$('.global-helper-messages',root);
  if(box.dataset.stamp!==stamp){box.dataset.stamp=stamp;box.innerHTML=(row?.records||[]).map(record=>`<article class="global-helper-turn" data-global-record="${esc(record.requestId)}"><p class="global-user-message">${esc(record.message)}</p><p class="small">${esc(({completed:'응답 수신',error:'요청 실패',cancelled:'취소됨',interrupted:'이전 실행 중단',running:'응답 대기'})[record.state]||record.state)}</p>${record.output?'<pre class="global-assistant-message">'+esc(record.output)+'</pre>':''}</article>`).join('');if(row?.output&&(row.state==='running'||row.historyError))box.insertAdjacentHTML('beforeend',(row.historyError?'<p class="small">이번 요청에서 받은 응답 · 기록 저장 실패</p>':'')+'<pre class="global-assistant-message" data-current-global-output>'+esc(row.output)+'</pre>');if(!box.childNodes.length)box.innerHTML='<p class="muted">아직 받은 전역 응답이 없습니다.</p>';}
  const prepare=$('[data-global-prepare]',root),stop=$('[data-global-stop]',root);prepare.dataset.supported=String(supported()&&!!agent&&row?.state!=='running');prepare.disabled=api.busy||prepare.dataset.supported==='false';stop.dataset.supported=String(row?.state==='running');stop.disabled=api.busy||stop.dataset.supported==='false';
 }
 return {create,mountAssignment,renderGlobal,update,status,assigned,agents};
}
