// Keep the runtime's owner/lifetime intact. Retrying means a new document,
// never evaluating the partially initialized runtime a second time in this one.
let retired=false;
const retire=()=>{retired=true;};
window.addEventListener('pagehide',retire,{once:true});
try{
 await import('./v508-runtime.js');
}catch{
 if(!retired){
  // Exception text may contain paths/session URLs and cannot establish a
  // project/schema compatibility error.
  console.error('[Confectory] editor_bootstrap_failed');
  const app=document.getElementById('app');
  if(app&&!app.hasChildNodes()){
   const panel=document.createElement('main');panel.className='welcome';panel.dataset.bootstrapFailure='empty';panel.setAttribute('role','alert');
   const content=document.createElement('div');content.className='welcome-inner';
   const title=document.createElement('h1');title.textContent='작업실을 불러오지 못했어요';
   const message=document.createElement('p');message.textContent='연결과 앱 버전을 확인한 뒤 다시 불러와 주세요.';
   const actions=document.createElement('div');actions.className='row';
   const retry=document.createElement('button');retry.type='button';retry.className='primary';retry.textContent='다시 불러오기';
   retry.addEventListener('click',()=>{if(retired||retry.disabled)return;retry.disabled=true;window.location.reload();});
   actions.append(retry);content.append(title,message,actions);panel.append(content);app.append(panel);
  }else{
   // Initialization may already have rendered an owner or accepted input.
   // Leave that DOM alone; a bootstrap failure is not permission to reset it.
   const status=document.getElementById('status'),toast=document.getElementById('toast');
   if(status&&toast){status.dataset.bootstrapFailure='partial';status.textContent='화면 초기화를 마치지 못했어요. 입력을 확인한 뒤 창을 새로고침해 주세요.';toast.classList.add('show');}
  }
 }
}finally{
 window.removeEventListener('pagehide',retire);
}
