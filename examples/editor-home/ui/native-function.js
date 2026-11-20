// A standalone C# body over the existing owned draft, checkpoint and Review APIs.
// Never converts the definition into a graph or serializes generated preview code.
export function mountNativeFunction(root,api){
 const {esc}=api,events=new AbortController();let disposed=false,writing=false,data=api.data;
 const key=api.key,owns=()=>!disposed&&root.isConnected&&api.owns();
 const basis=value=>JSON.stringify(value.map(({id,hash,path,baseline})=>({id,hash,path,baseline})));
 const pending=()=>api.inputs.get(key);
 const matches=held=>held?.kind==='native-body'&&held.id===data.id&&basis(held.sources)===basis(data.sources);
 // Revision numbers are process-local. A cold read may rebind ONLY identical
 // complete source hashes, locators and original file baselines.
 if(matches(pending())){api.inputs.set(key,{...pending(),sources:structuredClone(data.sources),checkpointHash:data.checkpointHash});api.persist();}
 root.innerHTML='<div class="bp-toolbar"><strong>'+esc(api.name)+'</strong><div class="bp-save-group"><span class="bp-status" role="status"></span><button type="button" data-native-save>저장</button><button type="button" data-native-complete>기능 완성</button></div></div><nav class="fd-view-tabs" role="tablist" aria-label="기능 보기"><button role="tab" aria-selected="true">네이티브 코드</button></nav><section class="function-document native-function"><div class="fd-native-tools"><span>직접 선언한 C# 본문 · 초안 저장 후 검토에서 컴파일</span><div><button type="button" data-native-undo>실행 취소</button><button type="button" data-native-redo>다시 실행</button><button type="button" data-native-convert>블루프린트로 변환…</button></div></div><textarea data-native-source aria-label="네이티브 C# 본문" spellcheck="false"></textarea></section>';
 if(!document.head.querySelector('[data-function-document-style]')){const style=document.createElement('link');style.rel='stylesheet';style.href=new URL('./function-document.css',import.meta.url).href;style.dataset.functionDocumentStyle='';document.head.append(style);}
 const editor=root.querySelector('[data-native-source]'),status=root.querySelector('.bp-status');editor.value=pending()?.text??data.source;
 const message=text=>status.textContent=text??(pending()?(matches(pending())?'미저장 초안':'소스 변경 · 입력 보존 · 원본과 비교 필요'):'저장됨');message();
 editor.addEventListener('input',()=>{if(!owns())return;const old=pending();api.inputs.set(key,{kind:'native-body',id:data.id,text:editor.value,sources:old?.sources||structuredClone(data.sources),checkpointHash:old?.checkpointHash??data.checkpointHash});api.persist();message();},{signal:events.signal});
 async function refresh(captured=null){
  const fresh=await api.read();if(!owns())return;
  const held=pending();
  if(captured&&held&&JSON.stringify(held)!==JSON.stringify(captured)&&basis(held.sources)===basis(captured.sources)&&fresh.source===captured.text){
   const peers=value=>basis(value.filter(row=>row.id!==data.id));
   if(peers(fresh.sources)===peers(captured.sources))api.inputs.set(key,{...held,sources:structuredClone(fresh.sources),checkpointHash:fresh.checkpointHash});
  }
  data=fresh;if(!pending())editor.value=data.source;api.persist();message();
 }
 async function save(complete=false){
  if(!owns()||writing)return;writing=true;message('저장 중…');
  try{
   const held=pending(),captured=held&&structuredClone(held);
   if(captured){if(!matches(captured))throw Error('소스가 바뀌었습니다. 입력은 보존됩니다. 원본과 비교한 뒤 다시 열어 주세요.');const result=await api.save(captured);if(!owns())return;if(result.id!==data.id||result.checkpointSaved!==true)throw Error('저장 응답을 확인하지 못했습니다. 입력은 보존됩니다.');if(JSON.stringify(pending())===JSON.stringify(captured)){api.inputs.delete(key);api.persist();}await refresh(captured);}
   else await refresh();
   if(complete){if(pending())throw Error('저장 도중 추가한 입력은 유지됩니다. 먼저 새 입력을 저장해 주세요.');await api.review(data.reviewIds);}
  }catch(error){if(owns())message(error.message||'저장하지 못했습니다. 입력은 보존됩니다.');}finally{writing=false;}
 }
 async function history(redo){
  if(!owns()||writing)return;if(pending()){message('저장하지 않은 입력을 먼저 확인해 주세요. 텍스트 실행 취소는 편집기에서 사용할 수 있습니다.');return;}
  writing=true;try{await api.history(redo);await refresh();}catch(error){if(owns())message(error.message);}finally{writing=false;}
 }
 root.querySelector('[data-native-save]').onclick=()=>api.work(()=>save());root.querySelector('[data-native-complete]').onclick=()=>api.work(()=>save(true));
 root.querySelector('[data-native-convert]').onclick=()=>{if(!owns()||writing)return;if(pending()){message('입력을 먼저 저장해 주세요. 변환 전 원본은 유지됩니다.');return;}api.work(api.convert);};
 root.querySelector('[data-native-undo]').onclick=()=>api.work(()=>history(false));root.querySelector('[data-native-redo]').onclick=()=>api.work(()=>history(true));
 root.addEventListener('keydown',event=>{if(!owns()||event.isComposing||!(event.ctrlKey||event.metaKey))return;if(event.key.toLowerCase()==='s'){event.preventDefault();event.stopPropagation();api.work(()=>save());}},{signal:events.signal});
 return {refresh:()=>refresh(),destroy(){disposed=true;events.abort();}};
}
