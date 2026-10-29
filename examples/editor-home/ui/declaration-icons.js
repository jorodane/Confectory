import {browserIconMarkup,localIconImage} from './browser-data.js';
import {openGlyphPopover} from './glyph-popover.js';
import {createElementAuthorSurface} from './element-author-surface.js';

// Exposed category/concept/module headers use the existing owner receipt/CAS.
// Generic declaration contracts and legacy properties keep their own Apply path.
export function createDeclarationIcons(api,features){
 const {$,$$,esc,inputs}=api,kinds=['category','concept','module'];
 const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
 function reset(w){
  if(!w?.declarationHeader)return;
  w.elementClosePopover?.();w.declarationIconEvents?.abort();
  const header=w.el.querySelector(':scope>.object-header'),row=header?.querySelector('.row');
  for(const b of header?.querySelectorAll('[data-declaration-header-action]')||[])b.remove();
  if(row)w.declarationHeader.append(row);header?.replaceWith(w.declarationHeader);
  w.declarationHeader=null;w.declarationIconInfo=null;w.declarationIconGeneration=(w.declarationIconGeneration||0)+1;w.declarationIconContext=null;w.el.classList.remove('object-editor');api.setupWindowDrag?.(w);
 }
 function bind(w,info,row,refresh,notice){
  if(!kinds.includes(info.kind)){reset(w);return null;}
  const scope=api.current.projectId,id=info.id,cacheKey=scope+'|'+(row?.view||'primary')+'|'+id;
  const scoped=row?createElementAuthorSurface(api,{scope,slot:row.view,id,mode:'declaration'}):api;
  const author=row?features.moduleAuthor({slot:row.view,id,mode:'declaration'}):features;
  const start=scope+'|'+id+'|element|',cells=()=>[...scoped.ownerInputs].filter(([k])=>k.startsWith(start));
  if(w.declarationIconContext!==cacheKey){w.declarationIconUndo=[];w.declarationIconRedo=[];w.declarationIconContext=cacheKey;w.declarationIconGeneration=(w.declarationIconGeneration||0)+1;}
  const generation=w.declarationIconGeneration,owns=()=>api.current.projectId===scope&&api.windows.get(w.key)===w&&w.meta.id===id&&w.declarationIconGeneration===generation&&(row||api.current.draft?.id===id)&&info.editable===true&&(!row||api.current.editorViews?.some(r=>r.view===row.view&&r.id===id&&r.mode==='declaration'&&r.authorBinding===row.authorBinding));
  w.declarationIconEvents?.abort();w.declarationIconInfo=info;
  if(!w.declarationHeader){
   w.declarationHeader=w.el.querySelector(':scope>.window-title');
   const header=document.createElement('div');header.className='object-header window-title has-object-parent';
   header.innerHTML='<div class="object-icon-control"><span class="obj-icon"></span><button type="button" class="object-icon-edit" aria-label="아이콘 편집">편집</button></div><div class="object-title-info"></div>';
   header.append(w.declarationHeader.querySelector('.row'));w.declarationHeader.replaceWith(header);w.el.classList.add('object-editor');api.setupWindowDrag?.(w);
  }
  const header=w.el.querySelector(':scope>.object-header'),icon=header.querySelector('.object-icon-control>.obj-icon'),button=header.querySelector('.object-icon-edit');
  const pending=()=>inputs.get(cacheKey)||{},has=()=>cells().length>0||author.hasOwnerAttempt(id);
  const value=kind=>scoped.ownerInputs.get(start+kind)?.text??pending().properties?.value?.[kind]??(kind==='icon'?info.values?.editorIcon:info.description);
  const draw=()=>{icon.innerHTML=browserIconMarkup({kind:info.kind,icon:value('icon')},esc);const raw=$('[data-decl-property=icon]',w.body);if(raw){raw.value=localIconImage(value('icon'))?'':value('icon')||'';raw.placeholder=localIconImage(value('icon'))?'로컬 이미지 선택됨':'';}notice();};
  header.querySelector('.object-title-info').innerHTML='<div class="object-parent-reference"><small>부모</small><span>'+esc(info.parent?.split('::').at(-1)||'Root')+'</span></div><div class="object-title-name-line"><h2 class="object-title-name">'+esc(info.values?.editorName||id.split('::').at(-1))+'</h2></div>';
  const record=(kind,text)=>{const prior=scoped.ownerInputs.get(start+kind);scoped.ownerInputs.set(start+kind,{kind,text,revision:prior?.revision??info.revision,hash:prior?.hash??info.textHash});api.persist();};
  function migrate(){
   const cache=pending();if(Object.keys(cache).some(k=>k!=='properties')||cache.properties&&Object.keys(cache.properties.value).some(k=>!['icon','description'].includes(k)))throw Error('다른 선언 입력을 먼저 적용해 주세요. 모든 입력은 유지됩니다.');
   if(cache.properties){for(const [kind,text] of Object.entries(cache.properties.value)){if(!scoped.ownerInputs.has(start+kind))scoped.ownerInputs.set(start+kind,{kind,text,revision:cache.properties.revision,hash:cache.properties.hash});}delete cache.properties;if(!Object.keys(cache).length)inputs.delete(cacheKey);}
  }
  const snapshot=()=>({cells:structuredClone(cells()),legacy:structuredClone(inputs.get(cacheKey))});
  function restore(target,expected){
   const from=new Map(expected.cells),to=new Map(target.cells),changed=[...new Set([...from.keys(),...to.keys()])].filter(k=>!same(from.get(k),to.get(k))),legacy=!same(target.legacy,expected.legacy);
   if(changed.some(k=>!same(scoped.ownerInputs.get(k),from.get(k)))||legacy&&!same(inputs.get(cacheKey),expected.legacy))throw Error('이후 입력이 바뀌었어요. 현재 입력은 유지됩니다.');
   for(const k of changed)if(to.has(k))scoped.ownerInputs.set(k,to.get(k));else scoped.ownerInputs.delete(k);
   if(legacy){if(target.legacy)inputs.set(cacheKey,target.legacy);else inputs.delete(cacheKey);}api.persist();draw();
  }
  button.disabled=info.editable!==true;button.onpointerdown=e=>e.stopPropagation();
  button.onclick=()=>{if(!owns()||w.el.hidden)return;openGlyphPopover({api,w,anchor:button,title:info.values?.editorName||id.split('::').at(-1),value:value('icon')||icon.textContent,allowImage:true,alive:()=>owns()&&w.declarationIconInfo?.textHash===info.textHash&&!w.el.hidden&&button.isConnected,onApply:text=>{try{const before=snapshot();let deferred=null;try{migrate();}catch(error){deferred=error;}record('icon',text);w.declarationIconUndo??=[];w.declarationIconUndo.push({before,after:snapshot(),hash:info.textHash});w.declarationIconRedo=[];draw();if(deferred)api.toast(deferred.message+' 선택한 아이콘도 보존했습니다.');}catch(error){api.toast(error.message);}}});};
  const events=new AbortController();w.declarationIconEvents=events;
  w.el.addEventListener('keydown',e=>{if(!owns()||e.isComposing||!(e.ctrlKey||e.metaKey)||!['z','y'].includes(e.key.toLowerCase())||e.target.closest('input,textarea,[role=dialog]')||author.hasOwnerAttempt(id))return;const redo=e.shiftKey||e.key.toLowerCase()==='y',from=redo?w.declarationIconRedo:w.declarationIconUndo,to=redo?(w.declarationIconUndo??=[]):(w.declarationIconRedo??=[]),step=from?.at(-1);if(!step||step.hash!==info.textHash)return;try{restore(redo?step.after:step.before,redo?step.before:step.after);from.pop();to.push(step);e.preventDefault();e.stopPropagation();button.focus({preventScroll:true});}catch(error){api.toast(error.message);}},{signal:events.signal});
  function check(){if(!owns())throw Error('헤더 편집 대상이 바뀌었습니다. 입력은 유지됩니다.');if(api.dirty&&!row)throw Error('소스 입력을 먼저 적용해 주세요. 헤더 입력은 유지됩니다.');}
  async function save(complete=false){
   check();migrate();let recovered=false;
   if(author.hasOwnerAttempt(id))recovered=(await author.recoverOwnerEditsInWork(id,owns))?.settled===true;
   if(!recovered&&cells().length){const submitted=cells();if(submitted.some(([,v])=>!['icon','description'].includes(v.kind)||v.hash!==info.textHash))throw Error('헤더 원본이 바뀌었습니다. 입력은 유지됩니다.');await author.saveOwnerEditsInWork(id,{request:{id,hash:info.textHash,changes:submitted.map(([,v])=>({type:v.kind,text:v.text}))},cells:submitted},owns);}
   await scoped.view.call('inspectDeclaration',{id});w.declarationIconUndo=[];w.declarationIconRedo=[];refresh();
   if(cells().length)throw Error('저장 중 새 입력은 보존했습니다. 다음 저장으로 확인해 주세요.');
   if(complete){const draft=scoped.current.draft;if(draft?.id!==id)throw Error('검토할 선언을 다시 확인해 주세요.');await api.reviewAuthor(draft.creationReviewIds?.length?draft.creationReviewIds:[id]);}
  }
  async function discard(){
   check();const held=cells(),legacy=structuredClone(inputs.get(cacheKey));await author.discardOwnerAttemptInWork(id,owns);
   const status=await api.view.call('browserDrafts',{action:'status',ids:[id]});check();
   if(status.rows?.find(r=>r.id===id)?.hash!==info.textHash||status.rows?.find(r=>r.id===id)?.revision!==info.revision)throw Error('취소할 원본이 바뀌었습니다. 입력은 유지됩니다.');
   if(status.unsaved&&scoped.otherPending?.(status.ids,{map:scoped.ownerInputs,cells:held}))throw Error('같은 선언의 다른 입력을 먼저 확인해 주세요. 입력은 유지됩니다.');
   if(status.unsaved)await api.view.call('browserDrafts',{action:'discard',ids:status.ids,revisions:status.rows.map(r=>r.revision),hashes:status.rows.map(r=>r.hash),checkpointHash:status.checkpointHash,ownerHash:status.ownerHash});
   for(const [k,v] of held)if(scoped.ownerInputs.get(k)===v)scoped.ownerInputs.delete(k);
   const current=inputs.get(cacheKey);for(const kind of ['icon','description'])if(legacy?.properties&&Object.hasOwn(legacy.properties.value,kind)&&same(current?.properties?.value?.[kind],legacy.properties.value[kind]))delete current.properties.value[kind];if(current?.properties&&!Object.keys(current.properties.value).length)delete current.properties;if(current&&!Object.keys(current).length)inputs.delete(cacheKey);api.persist();await scoped.view.call('inspectDeclaration',{id});w.declarationIconUndo=[];w.declarationIconRedo=[];refresh();
  }
  for(const b of header.querySelectorAll('[data-declaration-header-action]'))b.remove();
  for(const [action,label] of [['discard','변경 취소'],['save','임시 저장'],['confirm','확정']]){const b=document.createElement('button');b.type='button';b.className='secondary window-commit-action';b.dataset.declarationHeaderAction=action;b.dataset.operation='declaration-header-'+action;b.textContent=label;b.disabled=info.editable!==true;header.querySelector('.row').insertBefore(b,header.querySelector('[data-fold]'));b.onclick=()=>api.work(()=>action==='discard'?discard():save(action==='confirm'),'');}
  draw();return {has,save,discard,record,draw,value,stale:()=>cells().some(([,v])=>v.hash!==info.textHash)};
 }
 return {reset,bind};
}
