// Adapt the existing module implementation editor to one properties-window lifetime.
// Copy/authoring transactions remain the same server candidates; only the UI owner differs.
export function createElementAuthorSurface(api,{scope,slot,id,mode='properties'}){
 let epoch=null;
 const row=()=>api.current.projectId===scope?api.current.editorViews?.find(r=>r.view===slot&&r.id===id&&r.mode===mode):null;
 epoch=row()?.authorBinding||null;
 const requireOwner=()=>{const r=row();if(!r?.authorBinding||epoch&&r.authorBinding!==epoch)throw Error('독립 창의 모듈 편집 대상이 바뀌었습니다. 입력은 유지됩니다.');epoch??=r.authorBinding;return r;};
 const local=scope+'|'+id+'|element|',wire=scope+'|'+id+'|view:'+slot+'|element|';
 const toWire=k=>k.startsWith(local)?wire+k.slice(local.length):null;
 const ownerInputs={get(k){const key=toWire(k);return key?api.ownerInputs.get(key):undefined;},has(k){return this.get(k)!==undefined;},set(k,v){const key=toWire(k);if(!key)throw Error('독립 창 입력 범위가 다릅니다.');api.ownerInputs.set(key,v);return this;},delete(k){const key=toWire(k);return key?api.ownerInputs.delete(key):false;},*[Symbol.iterator](){for(const [k,v] of api.ownerInputs)if(k.startsWith(wire))yield [local+k.slice(wire.length),v];}};
 const view={get generation(){return api.view.generation;},async update(){requireOwner();await api.view.update();requireOwner();},async call(endpoint,input={}){
  if(endpoint==='openEditorView'){
   if(input.view!==slot||input.id!==id||input.viewMode!==mode||api.current.projectId!==scope)throw Error('복원할 정보 창의 대상이 다릅니다.');
   if(epoch)requireOwner();const result=await api.view.call(endpoint,input);requireOwner();return result;
  }
  const r=requireOwner();
  if(endpoint==='inspectDeclaration'||endpoint==='schema')return api.view.call('openEditorView',{view:slot,id,viewMode:mode});
  if(endpoint==='saveDraft'||endpoint==='saveEditorView')return api.view.call('saveEditorView',{view:slot,id});
  if(endpoint!=='blueprint')throw Error('독립 창 모듈에는 이 작업이 연결되지 않았어요. 입력은 유지됩니다.');
  if(mode==='declaration'&&!['readOwnerEdits','settledSlots','applySlots'].includes(input.action))throw Error('이 선언창은 헤더 표시만 저장합니다.');
  return api.view.call(endpoint,{...input,view:slot,viewBinding:r.authorBinding,owner:id});
 }};
 return {...api,authorSurface:slot,authorOwner:id,raw:null,ownerInputs,get current(){const r=row(),value=mode==='declaration'?r?.declaration:r?.schema;return {...api.current,draft:r?.draft||null,schema:value||null,declaration:value||null};},get view(){return view;},get dirty(){return false;},otherPending:(ids,except)=>api.otherPending?.(ids,except?.map===ownerInputs?{...except,map:api.ownerInputs,cells:except.cells.map(([k,v])=>[toWire(k),v])}:except),copyChanged:owner=>mode==='properties'?api.copyChanged?.(owner,slot):api.controls()};
}
