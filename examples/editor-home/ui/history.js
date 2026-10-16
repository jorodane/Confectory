// Transaction metadata comes from the shared draft owner; source text is not presentation.
export function createDraftHistory(api){
 const {$,$$,esc}=api;
 const reasons={EMPTY:'해당 이력이 없습니다.',SOURCE_CHANGED:'현재 소스가 이력의 내용과 다릅니다. 입력과 초안을 유지했습니다.',HISTORY_CHANGED:'읽은 뒤 이력이나 소스가 바뀌었습니다. 다시 읽고 선택하세요.',OWNERSHIP_CHANGED:'생성·등록부 변경으로 이전 소스 편집 이력을 정리했습니다.',CONFLICT_REBASED:'충돌 기준을 새로 선택해 이전 편집 이력을 정리했습니다.',ENTRY_BUDGET:'최근 편집은 전체 이력 저장 예산을 초과했습니다. 해당 초안은 유지됩니다.'};
 const label=value=>value==='batch-edit'?'묶음 편집':'소스 편집';
 function show(data=null,meta={}){
  const scope=api.current.projectId,w=api.openWindow('history','의미 편집 이력',720,390,{refresh:true});Object.assign(w.meta,meta);w.historyData=data;
  w.body.innerHTML=`<div class="window-content draft-history"><div class="actions"><button data-operation data-history-read>현재 이력 읽기</button><button data-operation data-history-move="undo">되돌리기</button><button data-operation data-history-move="redo">다시 실행</button></div><p class="small">공유 초안의 새 편집으로 적용합니다. Save와 새 Review/Confirm은 별도 동작입니다.</p><p class="small" data-history-status></p><div class="draft-history-current">${['undo','redo'].map(direction=>{const item=data?.[direction];return `<section data-history-tip="${direction}"><strong>${direction==='undo'?'되돌릴 편집':'다시 실행할 편집'}</strong><p>${item?.id?esc(label(item.label)+' · '+item.units.length+'개 소스'):'—'}</p>${(item?.units||[]).map(unit=>`<div class="small">${esc(unit.id)}</div>`).join('')}</section>`;}).join('')}</div><div class="draft-history-list">${(data?.entries||[]).map(entry=>`<div data-history-entry="${esc(entry.id)}"><strong>${entry.direction==='undo'?'적용됨':'되돌림'} · ${esc(label(entry.label))}</strong><span>${entry.ids.map(esc).join(', ')}</span></div>`).join('')}</div></div>`;
  $('[data-history-status]',w.body).textContent=w.historyError||(data?.code?reasons[data.code]||data.code:data?.boundary?reasons[data.boundary]||data.boundary:data?`되돌리기 ${data.undoCount} · 다시 실행 ${data.redoCount}`:'복원 후 현재 이력을 다시 읽으세요.');
  $('[data-history-read]',w.body).onclick=()=>open();
  for(const button of $$('[data-history-move]',w.body)){
   const direction=button.dataset.historyMove,item=data?.[direction];button.dataset.supported=String(item?.available===true);
   button.onclick=()=>api.work(async()=>{
    if(api.current.projectId!==scope||!item?.available)throw Error('현재 프로젝트 이력을 다시 읽으세요.');
    if(api.pending(item.units.map(unit=>unit.id)))throw Error('이 소스의 미적용 입력을 먼저 처리하세요. 입력은 유지됩니다.');
    const result=await api.view.call('draftHistory',{action:direction,token:item.token});
    if(api.current.projectId!==scope)throw Error('프로젝트가 바뀌었습니다.');
    if(api.windows.get('history')===w&&w.el.isConnected)show(result,w.meta);
    if(result.accepted!==true)throw Error(reasons[result.code]||'현재 이력을 다시 확인하세요.');
   },direction==='undo'?'공유 초안 편집을 되돌렸습니다.':'공유 초안 편집을 다시 실행했습니다.');
  }
  api.controls();return w;
 }
 function open(){const scope=api.current.projectId,prior=api.windows.get('history');return api.work(async()=>{const result=await api.view.call('draftHistory',{action:'inspect'});if(api.current.projectId!==scope)throw Error('프로젝트가 바뀌었습니다.');if(prior&&(!prior.el.isConnected||api.windows.get('history')!==prior))return false;api.reveal('history');api.focus(show(result));api.persist();},'공유 초안의 실제 편집 이력');}
 return {open,restore:meta=>show(null,meta)};
}
