// A restored window retains user input and selection, never an execution grant.
export function createNodeTasks(api){
 const {$,$$,esc}=api;
 function show(data=null,plan=null,meta={}){
  const scope=api.current.projectId,w=api.openWindow('node-tasks','Blueprint 노드 Task',760,450,{refresh:true});Object.assign(w.meta,meta);w.nodeTaskData=data;w.nodeTaskPlan=plan;
  const selected=w.meta.nodeTaskNode||'',rows=data?.rows||[];
  w.body.innerHTML=`<div class="window-content node-tasks"><div class="actions"><button data-operation data-node-task-read>현재 목록 읽기</button><button data-operation data-node-task-inspect>선택 노드 검토</button><button data-operation data-node-task-assign>이 범위로 Task 배정</button></div><p class="small">배정은 로컬 계획입니다. 실제 모델 전송은 Worker 창에서 내용·사용량을 별도로 승인합니다.</p><label class="small">노드 검색 <input data-node-task-query maxlength="256" value="${esc(w.meta.nodeTaskQuery||'')}"></label><div class="node-task-list">${rows.map(row=>`<button data-operation data-node-task-id="${esc(row.id)}" class="${row.id===selected?'selected':''}">${esc(row.id)}${row.dirty?' · 초안 변경':''}</button>`).join('')}</div><p class="small" data-node-task-status>${data?`${data.total}개 노드 · ${data.page+1}페이지`:'현재 목록과 노드 정의를 다시 읽으세요. 이전 권한은 복원하지 않습니다.'}</p><div class="actions"><button data-operation data-node-task-page="-1">이전</button><button data-operation data-node-task-page="1">다음</button></div><pre class="consumer-output" data-node-task-plan></pre><label>배정 이유<textarea data-node-task-reason maxlength="4096" placeholder="이 노드를 구현하려는 이유">${esc(w.meta.nodeTaskReason||'')}</textarea></label></div>`;
  $('[data-node-task-plan]',w.body).textContent=plan?JSON.stringify({node:plan.assignment.id,definition:plan.definition,imports:plan.imports,sourceRevision:plan.sourceRevision,assignmentHash:plan.assignmentHash},null,2):selected?'선택: '+selected+'\n현재 정의와 초안 해시를 검토한 뒤 배정하세요.':'구현할 실제 코드 노드를 선택하세요.';
  $('[data-node-task-query]',w.body).oninput=e=>{w.meta.nodeTaskQuery=e.target.value;api.persist();};
  $('[data-node-task-reason]',w.body).oninput=e=>{w.meta.nodeTaskReason=e.target.value;api.persist();};
  $('[data-node-task-read]',w.body).onclick=()=>open(0);
  for(const b of $$('[data-node-task-id]',w.body))b.onclick=()=>{show(data,null,{...w.meta,nodeTaskNode:b.dataset.nodeTaskId});api.persist();};
  for(const b of $$('[data-node-task-page]',w.body)){
   const next=(data?.page||0)+Number(b.dataset.nodeTaskPage);b.dataset.supported=String(!!data&&next>=0&&next*32<data.total);b.onclick=()=>open(next);
  }
  $('[data-node-task-inspect]',w.body).dataset.supported=String(!!selected);
  $('[data-node-task-inspect]',w.body).onclick=()=>api.work(async()=>{
   if(api.current.projectId!==scope||!selected)throw Error('현재 프로젝트의 노드를 선택하세요.');
   if(api.pending(selected))throw Error('이 노드의 미적용 입력을 먼저 처리하세요. 입력은 유지됩니다.');
   const result=await api.view.call('nodeTask',{action:'inspect',node:selected});
   if(api.current.projectId!==scope)throw Error('프로젝트가 바뀌었습니다.');
   if(api.windows.get(w.key)===w&&w.el.isConnected)show(data,result,w.meta);
  },'실제 노드 정의·소스 해시 검토 · 전송 없음');
  $('[data-node-task-assign]',w.body).dataset.supported=String(!!plan&&plan.assignment.id===selected);
  $('[data-node-task-assign]',w.body).onclick=()=>api.work(async()=>{
   if(api.current.projectId!==scope||!plan||plan.assignment.id!==selected)throw Error('현재 노드 정의를 다시 검토하세요.');
   if(api.pending(selected))throw Error('이 노드의 미적용 입력을 먼저 처리하세요. 입력은 유지됩니다.');
   const rationale=$('[data-node-task-reason]',w.body).value;if(!rationale.trim())throw Error('배정 이유를 입력하세요.');
   const result=await api.view.call('nodeTask',{action:'assign',node:selected,assignmentHash:plan.assignmentHash,commandID:crypto.randomUUID(),rationale});
   if(api.current.projectId!==scope)throw Error('프로젝트가 바뀌었습니다.');
   if(api.windows.get(w.key)===w&&w.el.isConnected)show(data,null,w.meta);
   api.worker(result.task);
  },'노드 Task 배정됨 · 모델 실행·원본 변경 없음');
  api.controls();return w;
 }
 function open(page=0,node=null){const scope=api.current.projectId,prior=api.windows.get('node-tasks'),meta={...(prior?.meta||{}),nodeTaskPage:page,...(node?{nodeTaskNode:node,nodeTaskQuery:node}: {})};return api.work(async()=>{
  const result=await api.view.call('nodeTask',{action:'list',page,query:meta.nodeTaskQuery||''});if(api.current.projectId!==scope)throw Error('프로젝트가 바뀌었습니다.');
  if(prior&&(!prior.el.isConnected||api.windows.get('node-tasks')!==prior))return false;
  api.reveal('node-tasks');api.focus(show(result,null,meta));api.persist();
 },'소유 Blueprint 코드 노드 · 모델 실행 없음');}
 return {open,restore:meta=>show(null,null,meta)};
}
