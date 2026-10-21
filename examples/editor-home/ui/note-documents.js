import {noteHtml,noteMarkup,bindNoteEditor,applyNoteTitle} from './notes.js';

// Documents are views of canonical private notes; they own no declaration or execution handle.
export function createNoteDocuments(api){
 let owner=null,canvas=null,layer=null,editing=null;const records=new Map();
 const notes=()=>{const p=api.project;return p?[...(p.workspaceItems||[]),...(p.workspaces||[]).flatMap(w=>w.items||[])].filter(item=>item.kind==='note'):[];};
 function resolve(id){const found=notes().filter(item=>item.id===id);return found.length===1?found[0]:null;}
 function ids(){return [...new Set(Array.isArray(api.project?.noteDocuments)?api.project.noteDocuments:[])].filter(id=>typeof id==='string'&&id.length>0&&id.length<=128&&resolve(id)).slice(0,64);}
 function activeId(){const id=api.project?.activeNoteDocument;return ids().includes(id)?id:null;}
 function reset(){layer?.remove();canvas?.classList.remove('has-note-document');const world=canvas?.querySelector('.workspace-world-layer');if(world)world.hidden=false;records.clear();layer=null;canvas=null;owner=null;}
 function synchronize(record,item,source){
  if(record.item!==item){
   record.item=item;record.el.innerHTML='<header class="note-document-heading"><strong class="workspace-item-name" data-note-document-title></strong><button type="button" data-note-document-style aria-label="메모 제목 서식">Aa</button></header>'+noteMarkup(item);
   record.editor=record.el.querySelector('[data-note-editor]');const project=api.project;
   const current=()=>api.project===project&&resolve(item.id)===item&&records.get(item.id)===record&&record.el.isConnected;
   record.binding=bindNoteEditor(record.el,item,()=>{changed(item,record.editor);api.persist();},current);
   record.el.querySelector('[data-note-document-style]').onclick=()=>{if(current())api.editTitle(item,current);};
  }
  record.el.querySelector('[data-note-document-title]').textContent=item.name||'메모';applyNoteTitle(record.el,item);
  const html=noteHtml(item);if(record.editor!==source&&record.canonicalHtml!==html){record.editor.innerHTML=html;record.binding.capture();}record.canonicalHtml=html;
 }
 function render(source=editing){
  const project=api.project,host=api.canvas();if(!project||!host){reset();return;}
  if(project!==owner||host!==canvas){reset();owner=project;canvas=host;}
  const open=ids();for(const [id,record] of records)if(!open.includes(id)){record.el.remove();records.delete(id);}
  if(open.length&&!layer){layer=document.createElement('div');layer.className='workspace-note-document-layer';canvas.append(layer);}
  for(const id of open){let record=records.get(id);if(!record){const el=document.createElement('section');el.className='workspace-note-document tab-document';el.dataset.noteDocument=id;el.tabIndex=0;el.setAttribute('role','region');record={el,item:null};records.set(id,record);layer.append(el);}synchronize(record,resolve(id),source);record.el.hidden=id!==activeId();record.el.setAttribute('aria-label',(record.item.name||'메모')+' · 메모 문서');}
  const active=activeId(),world=canvas.querySelector('.workspace-world-layer');if(world)world.hidden=!!active;canvas.classList.toggle('has-note-document',!!active);if(layer)layer.hidden=!active;api.renderTabs();
 }
 function changed(item,source){
  if(api.project!==owner||resolve(item.id)!==item)return;editing=source;
  try{
   let inline=[...canvas.querySelectorAll('.workspace-note')].find(el=>el.dataset.workspaceItem===item.id);
   if(inline&&typeof item.richText==='string'&&!inline.querySelector('[data-note-editor]')){item.width=Math.max(item.width,330);item.height=Math.max(item.height,260);api.renderDecorations();inline=[...canvas.querySelectorAll('.workspace-note')].find(el=>el.dataset.workspaceItem===item.id);}
   if(inline){const editor=inline.querySelector('[data-note-editor]');if(editor&&editor!==source&&inline.noteCanonicalHtml!==noteHtml(item)){editor.innerHTML=noteHtml(item);inline.noteBinding?.capture();}inline.noteCanonicalHtml=noteHtml(item);const plain=inline.querySelector('textarea');if(plain&&plain!==source&&plain.value!==item.text)plain.value=item.text||'';applyNoteTitle(inline,item);}
   render(source);
  }finally{editing=null;}
 }
 function activate(id){if(api.loading||!resolve(id)||!ids().includes(id))return;api.activateDocument?.();api.project.activeNoteDocument=id;api.project.activeWindowDocument=null;api.refreshWindows?.();render();api.persist();records.get(id)?.el.focus({preventScroll:true});}
 function open(item){if(api.loading||resolve(item.id)!==item)return;const open=ids();if(!open.includes(item.id)){if(open.length>=64){api.toast('메모 문서 탭은 최대 64개입니다.');return;}open.push(item.id);}api.project.noteDocuments=open;activate(item.id);}
 function close(id){if(!api.project)return;api.project.noteDocuments=ids().filter(value=>value!==id);if(api.project.activeNoteDocument===id)api.project.activeNoteDocument=null;render();api.persist();}
 function deactivate(){if(!activeId())return false;api.project.activeNoteDocument=null;render();api.persist();return true;}
 function prune(){if(!api.project||(!Array.isArray(api.project.noteDocuments)&&!api.project.activeNoteDocument))return;api.project.noteDocuments=ids();if(!ids().includes(api.project.activeNoteDocument))api.project.activeNoteDocument=null;render();}
 function renderTabs(tabs){
  const active=activeId();if(active)for(const tab of tabs.querySelectorAll('[role=tab]'))tab.setAttribute('aria-selected','false');
  for(const id of ids()){
   const item=resolve(id),label=item.name||'메모',tab=document.createElement('button');tab.type='button';tab.className='workspace-note-tab'+(active===id?' is-current':'');tab.dataset.noteTab=id;tab.setAttribute('role','tab');tab.setAttribute('aria-selected',String(active===id));tab.textContent=label;tab.onclick=()=>activate(id);tabs.append(tab);
   const button=document.createElement('button');button.type='button';button.className='workspace-tab-close';button.dataset.noteTabClose=id;button.setAttribute('aria-label',label+' 메모 탭 닫기');button.textContent='×';button.onclick=()=>close(id);tabs.append(button);
  }
 }
 function findContext(){
  const id=activeId(),record=records.get(id),project=api.project,item=resolve(id);if(!record||!item)return null;
  return {key:api.scope+'|note-document|'+id,host:record.el,title:'메모 본문에서 찾기',emptyMessage:'현재 메모 본문을 검색합니다.',placeholder:'메모 본문의 글자 찾기…',isCurrent:()=>api.project===project&&activeId()===id&&resolve(id)===item&&records.get(id)===record,items:()=>[{id,element:record.editor}],focus:()=>record.editor.scrollIntoView({block:'nearest',inline:'nearest'})};
 }
 return {open,close,activate,deactivate,render,renderTabs,changed,prune,detach:reset,findContext,get active(){return !!activeId();}};
}
