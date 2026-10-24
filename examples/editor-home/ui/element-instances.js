import {createElementViewSave} from './element-view-save.js';
import {createElementEditors} from './elements.js';

// Reuse the reference element renderer; only its window, input and RPC owners differ.
export function createElementInstances(api){
 const instances=new Map();
 function instance(row){
  const owner=api.current.projectId,id=row.id,slot=row.view,key=owner+'|'+slot+'|'+id,panel='editor-'+slot;
  const previous=instances.get(key);if(previous?.authorBinding===row.authorBinding)return previous;
  const binding=()=>api.current.projectId===owner?api.current.editorViews.find(value=>value.view===slot&&value.id===id&&value.mode==='properties'&&value.authorBinding===row.authorBinding):null;
  const requireOwner=()=>{if(!binding())throw Error('편집창의 프로젝트나 대상이 바뀌었습니다. 입력은 유지됩니다.');};
  const local=owner+'|'+id+'|',wire=local+'view:'+slot+'|';
  const toWire=value=>value.startsWith(local+'element|')?wire+value.slice(local.length):value.startsWith(local+'primary|')?wire+value.slice((local+'primary|').length):null;
  const fromWire=value=>value.startsWith(wire+'element|')?local+value.slice(wire.length):value.startsWith(wire)?local+'primary|'+value.slice(wire.length):null;
  const inputs={get(value){const target=toWire(value);return target?api.base.inputs.get(target):undefined;},has(value){return this.get(value)!==undefined;},set(value,data){const target=toWire(value);if(!target)throw Error('독립 편집창의 입력 대상이 다릅니다.');api.base.inputs.set(target,data);return this;},delete(value){const target=toWire(value);return target?api.base.inputs.delete(target):false;},*entries(){for(const [key,value] of api.base.inputs){const name=fromWire(key);if(name)yield [name,value];}},*keys(){for(const [key] of this.entries())yield key;},*values(){for(const [,value] of this.entries())yield value;},[Symbol.iterator](){return this.entries();},get size(){return [...this.entries()].length;}};
  const windows={get(value){if(!binding())return undefined;const w=api.base.windows.get(value==='schema'?panel:value);return w?.key===panel&&w.meta.id===id?w:undefined;},*values(){const w=this.get(panel);if(w)yield w;}};
  const proxy={get generation(){return api.view.generation;},async update(){requireOwner();await api.view.update();requireOwner();},async call(endpoint,input={}){
   requireOwner();if(endpoint==='blueprint'&&['list','readFeature','createFeature','read','authorBatch','settledAuthorBatch','readOwnerEdits','settledSlots','applySlots','implementationSources','readImplementationCopy','readImplementation','readSlotRemoval','implementationCallables','discardImplementationCopies'].includes(input.action))return api.view.call(endpoint,{...input,...(input.action==='list'?{ownerHash:binding().schema.textHash,ownerRevision:binding().schema.revision}:{}),view:slot,viewBinding:binding().authorBinding,owner:id});if(input.id&&input.id!==id)throw Error('독립 편집창의 대상이 다릅니다. 입력은 유지됩니다.');
   if(endpoint==='schema'||endpoint==='select')return api.view.call('openEditorView',{view:slot,id,viewMode:'properties'});
   const aliases={editField:'editViewField',editDescription:'editViewDescription',editDeclaration:'editViewDeclaration',editObjectStructure:'editViewObjectStructure',saveDraft:'saveEditorView'};
   if(aliases[endpoint])return api.view.call(aliases[endpoint],{...input,view:slot,id});
   if(endpoint==='blueprint')return api.view.call(endpoint,{...input,view:slot,id});
   if(['editObjectStructure','readAppliedModules','readModuleInterface'].includes(endpoint))return api.view.call(endpoint,{...input,view:slot,id});
   if(endpoint==='moveBrowserFolders'||endpoint==='browserDrafts'&&Array.isArray(input.ids)&&input.ids.includes(id))return api.view.call(endpoint,{...input,view:slot,id});
   throw Error('이 독립 편집창에는 해당 작업이 아직 연결되지 않았어요. 입력은 유지됩니다.');
  }};
  const unavailable=()=>{throw Error('구현 복사 편집은 원래 요소 창에서 진행해 주세요. 이 창의 입력은 유지됩니다.');};
  const base=api.base,scoped={...base,inputs,windows,rawSlot:slot,get current(){const value=binding();return {...api.current,draft:value?.draft||null,schema:value?.schema||null};},get view(){return proxy;},get busy(){return base.busy;},get dirty(){return false;},
   openWindow(name,title,width,height,options){requireOwner();if(name!=='schema')throw Error('독립 편집창의 표시 대상이 다릅니다.');const w=base.openWindow(panel,title,width,height,options);w.meta.id=id;w.meta.view=slot;w.meta.mode='properties';return w;},
   open:target=>api.open(target),work:(fn,...args)=>base.work(async()=>{requireOwner();return fn();},...args),
   detachedFunctionRemoval:true,removeOwnFunction:(w,schema,method)=>{if(!binding()||schema.id!==id)return false;return base.removeOwnFunction(w,schema,method);},removeOwnImplementation:(w,schema,method)=>{if(!binding()||schema.id!==id)return false;return base.removeOwnImplementation(w,schema,method);},removeModuleImplementation:(w,schema,requirement)=>{if(!binding()||schema.id!==id)return false;return base.removeModuleImplementation(w,schema,requirement);},implementationArchive:()=>{requireOwner();return (api.current.retirements||[]).find(value=>value.owner===id&&[null,undefined,'implementation-only-v1','information-binding-v1'].includes(value.mode)&&['pending','restoring'].includes(value.state));},cancelImplementationArchive:async(w,schema,alive)=>{requireOwner();const receipt=scoped.implementationArchive();if(!receipt||base.classificationPending([id,receipt.function,...receipt.ids]))throw Error('구현과 관련된 다른 입력을 먼저 확인해 주세요. 입력은 유지됩니다.');const surface={view:slot,id,viewBinding:binding().authorBinding};await base.archiveAction(receipt,receipt.state==='pending'?'recover':'cancel',()=>!!binding()&&alive(),surface);requireOwner();await base.refreshClassification(id);},localDiscardOnly:true,detachedAuthoring:row.schema?.kind==='schema',hasOwnerAttempt:()=>false,discardOwnerAttemptInWork:unavailable,copyDrafts:()=>[],hasCopyAttempt:()=>false,copyDiscardSnapshot:()=>null,openSlotInWork:(info,context)=>{requireOwner();const schema=binding().schema;if(context.owner!==id||schema?.kind!=='schema'||!schema.ownFunctions?.some(method=>method.id===info.id&&method.origin===id&&method.writable)&&!schema.requirements?.some(method=>method.function===info.id))throw Error('독립 창의 직접 소유 기능을 다시 선택해 주세요. 입력은 유지됩니다.');return (schema.requirements?.some(method=>method.function===info.id)?base.moduleAuthor({slot,id}):base).openSlotInWork(info,{...context,view:slot,viewBinding:binding().authorBinding});},openCopyInWork:unavailable,saveCopiesInWork:unavailable,discardCopiesInWork:unavailable,
   review:async target=>{requireOwner();if(target!==id)throw Error('검토할 요소가 바뀌었습니다.');await api.review(id,requireOwner);}
  };
  Object.assign(scoped,{classificationInView:true,classificationPeers:()=>base.classificationPending([id],{map:base.inputs,cells:[...inputs].map(([k,v])=>[toWire(k),v])}),classify:async(moves,alive)=>{
   await base.whenIdle();return scoped.work(async()=>{const guard=()=>{requireOwner();if(!alive()||moves.length!==1||moves[0].id!==id)throw Error('분류할 창이나 대상이 바뀌었습니다. 입력은 유지됩니다.');if(base.classificationPending([id]))throw Error('이 정보의 입력을 먼저 저장하거나 취소해 주세요. 다른 입력은 유지됩니다.');};
    for(let attempt=0;attempt<3;attempt++){await proxy.update();guard();try{const result=await proxy.call('moveBrowserFolders',{moves});if(result.moved===false)return false;break;}catch(error){if(error.message!=='stale_revision'||attempt===2)throw error;}}
    await proxy.call('schema',{id});await base.refreshClassification();
   },'분류 위치를 변경했어요. 상속·참조·네임스페이스는 유지됩니다.');
  }});
  const saves=createElementViewSave({slot,owner:id,inputs,journals:base.ownerAuthorInputs,get current(){return scoped.current;},get view(){return proxy;},persist:base.persist,flush:base.persistOwnerInputs});
  Object.assign(scoped,{atomicOwnerEdits:true,hasOwnerAttempt:saves.has,recoverOwnerEditsInWork:saves.recover,saveOwnerEditsInWork:saves.save,discardOwnerAttemptInWork:saves.discard,otherPending:()=>false});
  const moduleAuthor=()=>{requireOwner();return base.moduleAuthor({slot,id});};
  Object.assign(scoped,{detachedModules:true,copyDrafts:(...args)=>moduleAuthor().copyDrafts(...args),hasCopyAttempt:(...args)=>moduleAuthor().hasCopyAttempt(...args),copyDiscardSnapshot:(...args)=>moduleAuthor().copyDiscardSnapshot(...args),validateCopyDiscard:(...args)=>moduleAuthor().validateCopyDiscard(...args),discardCopies:(...args)=>moduleAuthor().discardCopies(...args),discardCopiesInWork:(...args)=>moduleAuthor().discardCopiesInWork(...args),openCopyInWork:(...args)=>moduleAuthor().openCopyInWork(...args),saveCopiesInWork:(...args)=>moduleAuthor().saveCopiesInWork(...args),recoverCopiesInWork:(...args)=>moduleAuthor().recoverCopiesInWork(...args),otherPending:(ids,except)=>base.otherPending(ids,except?.map===inputs?{...except,map:base.inputs,cells:except.cells.map(([k,v])=>[toWire(k),v])}:except)});
  const editor=createElementEditors(scoped);editor.authorBinding=row.authorBinding;instances.set(key,editor);return editor;
 }
 return {show:row=>instance(row).show(row.schema),reopen(row,w){instance(row).retryStatus(w);},retire(row,w){const key=api.current.projectId+'|'+row.view+'|'+row.id;instances.get(key)?.reset(w);instances.delete(key);},refreshProjection:()=>{for(const editor of instances.values())editor.refreshProjection();},controls:blocked=>{for(const editor of instances.values())editor.controls(blocked);}};
}
