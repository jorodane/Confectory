import {createElementViewSave} from './element-view-save.js';
import {createElementEditors} from './elements.js';

// Reuse the reference element renderer; only its window, input and RPC owners differ.
export function createElementInstances(api){
 const instances=new Map();
 function instance(row){
  const owner=api.current.projectId,id=row.id,slot=row.view,key=owner+'|'+slot+'|'+id,panel='editor-'+slot;
  if(instances.has(key))return instances.get(key);
  const binding=()=>api.current.projectId===owner?api.current.editorViews.find(value=>value.view===slot&&value.id===id&&value.mode==='properties'):null;
  const requireOwner=()=>{if(!binding())throw Error('편집창의 프로젝트나 대상이 바뀌었습니다. 입력은 유지됩니다.');};
  const local=owner+'|'+id+'|',wire=local+'view:'+slot+'|';
  const toWire=value=>value.startsWith(local+'element|')?wire+value.slice(local.length):value.startsWith(local+'primary|')?wire+value.slice((local+'primary|').length):null;
  const fromWire=value=>value.startsWith(wire+'element|')?local+value.slice(wire.length):value.startsWith(wire)?local+'primary|'+value.slice(wire.length):null;
  const inputs={get(value){const target=toWire(value);return target?api.base.inputs.get(target):undefined;},has(value){return this.get(value)!==undefined;},set(value,data){const target=toWire(value);if(!target)throw Error('독립 편집창의 입력 대상이 다릅니다.');api.base.inputs.set(target,data);return this;},delete(value){const target=toWire(value);return target?api.base.inputs.delete(target):false;},*entries(){for(const [key,value] of api.base.inputs){const name=fromWire(key);if(name)yield [name,value];}},*keys(){for(const [key] of this.entries())yield key;},*values(){for(const [,value] of this.entries())yield value;},[Symbol.iterator](){return this.entries();},get size(){return [...this.entries()].length;}};
  const windows={get(value){if(!binding())return undefined;const w=api.base.windows.get(value==='schema'?panel:value);return w?.key===panel&&w.meta.id===id?w:undefined;},*values(){const w=this.get(panel);if(w)yield w;}};
  const proxy={get generation(){return api.view.generation;},async update(){requireOwner();await api.view.update();requireOwner();},async call(endpoint,input={}){
   requireOwner();if(input.id&&input.id!==id)throw Error('독립 편집창의 대상이 다릅니다. 입력은 유지됩니다.');
   if(endpoint==='schema'||endpoint==='select')return api.view.call('openEditorView',{view:slot,id,viewMode:'properties'});
   const aliases={editField:'editViewField',editDescription:'editViewDescription',editDeclaration:'editViewDeclaration',editObjectStructure:'editViewObjectStructure',saveDraft:'saveEditorView'};
   if(aliases[endpoint])return api.view.call(aliases[endpoint],{...input,view:slot,id});
   if(endpoint==='blueprint')return api.view.call(endpoint,{...input,view:slot,id});
   if(['editObjectStructure','readAppliedModules','readModuleInterface'].includes(endpoint))return api.view.call(endpoint,{...input,view:slot,id});
   if(endpoint==='browserDrafts'&&Array.isArray(input.ids)&&input.ids.length===1&&input.ids[0]===id)return api.view.call(endpoint,{...input,view:slot,id});
   throw Error('이 독립 편집창에는 해당 작업이 아직 연결되지 않았어요. 입력은 유지됩니다.');
  }};
  const unavailable=()=>{throw Error('구현 복사 편집은 원래 요소 창에서 진행해 주세요. 이 창의 입력은 유지됩니다.');};
  const base=api.base,scoped={...base,inputs,windows,rawSlot:slot,get current(){const value=binding();return {...api.current,draft:value?.draft||null,schema:value?.schema||null};},get view(){return proxy;},get busy(){return base.busy;},get dirty(){return false;},
   openWindow(name,title,width,height,options){requireOwner();if(name!=='schema')throw Error('독립 편집창의 표시 대상이 다릅니다.');const w=base.openWindow(panel,title,width,height,options);w.meta.id=id;w.meta.view=slot;w.meta.mode='properties';return w;},
   open:target=>api.open(target),work:(fn,...args)=>base.work(async()=>{requireOwner();return fn();},...args),
   localDiscardOnly:true,hasOwnerAttempt:()=>false,discardOwnerAttemptInWork:unavailable,copyDrafts:()=>[],hasCopyAttempt:()=>false,copyDiscardSnapshot:()=>null,openSlotInWork:unavailable,openCopyInWork:unavailable,saveCopiesInWork:unavailable,discardCopiesInWork:unavailable,
   review:async target=>{requireOwner();if(target!==id)throw Error('검토할 요소가 바뀌었습니다.');await api.review(id,requireOwner);}
  };
  const saves=createElementViewSave({slot,owner:id,inputs,journals:base.ownerAuthorInputs,get current(){return scoped.current;},get view(){return proxy;},persist:base.persist,flush:base.persistOwnerInputs});
  Object.assign(scoped,{atomicOwnerEdits:true,hasOwnerAttempt:saves.has,recoverOwnerEditsInWork:saves.recover,saveOwnerEditsInWork:saves.save,discardOwnerAttemptInWork:saves.discard,otherPending:()=>false});
  const editor=createElementEditors(scoped);instances.set(key,editor);return editor;
 }
 return {show:row=>instance(row).show(row.schema),reopen(row,w){instance(row).retryStatus(w);},retire(row,w){const key=api.current.projectId+'|'+row.view+'|'+row.id;instances.get(key)?.reset(w);instances.delete(key);},refreshProjection:()=>{for(const editor of instances.values())editor.refreshProjection();},controls:blocked=>{for(const editor of instances.values())editor.controls(blocked);}};
}
