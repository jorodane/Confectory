// Bounded Home display state belongs to the host, separately from each project's presentation.
export function createHomePreferences(api){
 let value=null,revision=0,saved=0,timer=null,saving=null,status='ready';
 function hydrate(remote){if(value)return;value=structuredClone(remote.value);status=remote.status;render();}
 function render(){const label=api.$('#home-save-state'),retry=api.$('#home-save-retry');if(label)label.textContent=status==='unavailable'?'Home 보기 저장 자료를 읽지 못했습니다. 기존 파일을 유지합니다.':status==='failed'?'Home 보기 저장 실패 · 입력을 유지했습니다.':saving?'Home 보기 저장 중…':revision>saved?'Home 보기 변경 있음':'Home 보기 저장됨';if(retry){retry.hidden=status!=='failed';retry.disabled=!!saving;retry.onclick=()=>flush();}}
 function schedule(){clearTimeout(timer);timer=setTimeout(()=>{if(!api.canSave()){schedule();return;}flush();},250);}
 function changed(){revision++;render();schedule();}
 async function flush(){
  clearTimeout(timer);if(!value||saved===revision)return true;if(saving){await saving;if(saved<revision&&status!=='failed')return flush();return status==='ready';}
  const at=revision,candidate=structuredClone(value);
  saving=(async()=>{try{await api.save(candidate);saved=at;status='ready';return true;}catch{status='failed';return false;}})();render();const result=await saving;saving=null;render();if(result&&saved<revision)schedule();return result;
 }
 return {hydrate,changed,flush,render,get value(){return value}};
}
