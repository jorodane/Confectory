// A declared item is discoverable independently of the host's finite typed routes.
export function createContextActions(api){
 let generation=0;
 const scope=()=>api.current?.projectId,selection=()=>api.current?.draft?.id||'';
 async function open(event,unit,builtins){
  const serial=++generation,projectId=scope(),selected=selection(),x=event.clientX,y=event.clientY;
  api.contextMenu(x,y,[...builtins,['등록 기능 조회 중…',()=>{}]]);
  const loadingMenu=document.querySelector('.context-menu');
  const owns=()=>generation===serial&&scope()===projectId&&selection()===selected;
  try{
   const data=await api.view.call('contextActions',{operation:'list',projectId,id:unit.id,target:api.target()});
   if(data.status==='failed')throw Error(data.message);
   if(!owns()||!loadingMenu?.isConnected)return;
   const actions=data.actions.map(action=>[action.available?'등록 기능 · '+action.title:'등록 기능 · '+action.title+' · 미지원',()=>action.available?form(data,action,owns):api.toast(action.reason)]);
   api.contextMenu(x,y,[...builtins,...(actions.length?actions:[['등록된 기능 없음',()=>{}]])]);
  }catch(error){if(owns()&&loadingMenu?.isConnected)api.contextMenu(x,y,[...builtins,['등록 기능 조회 실패 · 다시 여세요',()=>api.toast(error.message)]]);}
 }
 function form(data,action,owns){
  if(!owns())return api.toast('메뉴를 연 객체나 프로젝트가 바뀌었습니다. 다시 여세요.');
  api.modal(action.title,'<p data-action-context></p><p class="small">현재 공유 초안의 선언을 사용합니다. 반환값은 변경안이며 적용·저장하지 않습니다.</p><p data-action-function></p><form><label>필드<input data-action-field maxlength="128" required></label><label>JSON 값<input data-action-value maxlength="8192" required></label><div class="actions"><button type="submit" data-action-invoke>함수 호출</button><button type="button" data-action-cancel>취소</button></div></form><pre class="consumer-output" data-action-result></pre>',(root,close)=>{
   root.querySelector('[data-action-context]').textContent=data.object+' · revision '+data.revision;
   root.querySelector('[data-action-function]').textContent=action.function+' → '+action.implementation;
   const button=root.querySelector('[data-action-invoke]'),output=root.querySelector('[data-action-result]');let pending=null,retired=false,finished=false;
   const retire=()=>{if(retired)return;retired=true;observer.disconnect();if(pending)api.view.cancel(pending.requestId).catch(()=>{});else if(!finished)api.view.call('contextActions',{operation:'cancel',projectId:data.projectId,token:data.token}).catch(()=>{});};
   const observer=new MutationObserver(()=>{if(!root.isConnected)retire();});observer.observe(document.querySelector('#overlays'),{childList:true,subtree:true});
   root.querySelector('[data-action-cancel]').onclick=()=>{retire();close();};
   root.querySelector('form').onsubmit=event=>{event.preventDefault();if(pending||finished||retired||api.busy)return;
    if(!owns()){output.textContent='메뉴를 연 객체나 프로젝트가 바뀌었습니다. 다시 여세요.';button.disabled=true;return;}
    const field=root.querySelector('[data-action-field]').value,value=root.querySelector('[data-action-value]').value;button.disabled=true;
    api.work(async()=>{
     if(!owns()||retired)throw Error('현재 객체 컨텍스트를 다시 확인하세요.');
     pending=api.view.call('contextActions',{operation:'invoke',projectId:data.projectId,token:data.token,actionId:action.id,field,value});
     try{const result=await pending;if(retired||!root.isConnected)return false;finished=true;
      if(!owns()){output.textContent='프로젝트나 선택이 바뀌어 반환값을 표시하지 않았습니다.';return false;}
      output.textContent=result.status==='completed'?result.output:(result.status+' · '+result.message);root.dataset.actionStatus=result.status;
      if(result.status!=='completed')throw Error(result.message||'함수 호출 실패');return false;
     }finally{pending=null;if(!finished&&!retired)button.disabled=false;}
    },'',{flushWorkspace:false});
   };
  });
 }
 return {open};
}
