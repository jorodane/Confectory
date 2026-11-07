import {mountBrowserShell,updateBrowserTitlePath} from './browser-shell.js';

function fitResourceFileNames(root){
 for(const label of root.querySelectorAll('[data-resource-full-name]')){
  if(!label.clientWidth)continue;const full=label.dataset.resourceFullName,match=label.dataset.resourceKind!=='folder'&&full.match(/^(.+)(\.[^.\s]+)$/u),stem=match?match[1]:full,extension=match?match[2]:'',parts=typeof Intl.Segmenter==='function'?[...new Intl.Segmenter(undefined,{granularity:'grapheme'}).segment(stem)].map(part=>part.segment):Array.from(stem),lines=label.closest('.object-card')?2:1,style=getComputedStyle(label),lineHeight=parseFloat(style.lineHeight)||parseFloat(style.fontSize)*1.5;
  const write=count=>{const shortened=count<parts.length,prefix=parts.slice(0,shortened?count:Math.max(0,count-1)).join('').trimEnd(),tail=document.createElement('span');tail.className='resource-filename-tail';tail.textContent=(shortened?'…':parts.at(-1)||'')+extension;label.replaceChildren(document.createTextNode(prefix),tail)};
  const overflows=()=>label.scrollWidth>label.clientWidth+1||label.scrollHeight>Math.ceil(lineHeight*lines)+1;
  write(parts.length);if(!overflows())continue;let low=0,high=parts.length-1;while(low<high){const middle=Math.ceil((low+high)/2);write(middle);if(overflows())high=middle-1;else low=middle}write(low);
 }
}
function bindResourceFileNames(root){
 let frame=0,active=true;const fit=()=>{frame=0;if(active&&root.isConnected)fitResourceFileNames(root)};
 const observer=new ResizeObserver(()=>{if(!frame)frame=requestAnimationFrame(fit)});observer.observe(root);fit();return ()=>{active=false;observer.disconnect();if(frame)cancelAnimationFrame(frame)};
}

function resourceSize(bytes){if(bytes<1024)return bytes+' B';if(bytes<1048576)return (bytes/1024).toFixed(1)+' KB';return (bytes/1048576).toFixed(1)+' MB'}

// Authored resource browser chrome; actual bytes live in the active project's
// native store. File objects/commands are volatile and never presentation data.
export function createResourceBrowser(api){
 const groups={concept:'개념',info:'정보',feature:'기능',module:'모듈',resource:'자료'},labels={image:'그림',document:'문서',mesh:'메시',file:'파일'},icons={image:'▧',document:'▤',mesh:'⬡',file:'▱'};
 const catalogues=new Map(),inputs=new Map();
 const scope=()=>api.current?.projectId||'';
 const state=w=>{const key=scope()+'|'+w.key;if(!inputs.has(key))inputs.set(key,{job:null,message:'',reading:false});return inputs.get(key);};
 const catalogue=owner=>{if(!catalogues.has(owner))catalogues.set(owner,{phase:'empty',value:null});return catalogues.get(owner);};
 const alive=(w,owner,token=w.resourceLifetime)=>!!token&&token===w.resourceLifetime&&token.generation===api.view.generation&&scope()===owner&&api.windows.get(w.key)===w&&w.meta.group==='resource'&&w.resourceScope===owner&&w.el.isConnected&&!w.el.closest('[hidden]')&&w.el.getClientRects().length>0;
 function accept(owner,result){if(result?.status!=='ready'||result.project!==owner||!Array.isArray(result.items)||result.items.length>64||result.items.some(row=>!/^[a-f0-9]{32}$/.test(row.id)||typeof row.name!=='string'||row.name.length>180||!labels[row.kind]||!/^[a-f0-9]{64}$/.test(row.hash)))throw Error('자료 목록의 프로젝트와 식별자를 확인하지 못했어요.');const c=catalogue(owner);c.value=result;c.phase='ready';}
 function update(){for(const w of api.windows.values())if(w.meta.group==='resource'&&w.resourceScope===scope())render(w);}
 function rows(w){const c=catalogue(scope()),query=(w.meta.query||'').toLocaleLowerCase();return [...(c.value?.items||[])].filter(row=>!query||row.name.toLocaleLowerCase().includes(query)).sort((a,b)=>w.meta.sort==='name'?a.name.localeCompare(b.name,'ko',{numeric:true}):w.meta.sort==='name-desc'?b.name.localeCompare(a.name,'ko',{numeric:true}):w.meta.sort==='newest'?b.createdAt.localeCompare(a.createdAt):0);}
 async function request(w,owner,action,input,token){
  for(let attempt=0;attempt<3;attempt++){if(!alive(w,owner,token))throw Error('scope_changed');await api.view.update();if(!alive(w,owner,token))throw Error('scope_changed');try{const result=await api.view.call('projectResources',{action,project:owner,...input});if(!alive(w,owner,token))throw Error('scope_changed');return result;}catch(error){if(error.message!=='stale_revision'||attempt===2)throw error;}}
 }
 function load(w,token=w.resourceLifetime){const owner=scope(),c=catalogue(owner),local=state(w);if(c.phase==='loading')return;c.phase='loading';update();
  (async()=>{await api.idle();if(!alive(w,owner,token)){c.phase=c.value?'ready':'empty';return;}await api.work(async()=>{try{accept(owner,await request(w,owner,'load',{},token));}catch(error){if(!alive(w,owner,token)){c.phase=c.value?'ready':'empty';return;}c.phase='failed';local.message='자료를 확인하지 못했어요. 기존 보관본은 그대로예요.';throw error;}finally{if(scope()===owner)update();}},null,{flushWorkspace:false});})();
 }
 function send(w,owner,local,job,token){if(job.inFlight)return;job.inFlight=true;local.message='파일을 보관하고 있습니다…';update();
  (async()=>{await api.idle();if(!alive(w,owner,token)||local.job!==job){job.inFlight=false;return;}await api.work(async()=>{try{
   if(local.job!==job)throw Error('scope_changed');const result=await request(w,owner,'import',job.input,token);accept(owner,result);
   if(local.job===job){local.job=null;local.message='자료 사본을 보관했어요. 원본 파일은 바뀌지 않았어요.';api.toast(local.message);w.meta.resourceSelected=result.selected;api.persist();}
  }catch(error){if(local.job===job)local.message='보관 결과를 확인하지 못했어요. 선택한 파일은 유지됩니다. 같은 요청으로 다시 확인하거나 선택 입력만 취소할 수 있어요.';if(alive(w,owner,token))throw error;}
  finally{job.inFlight=false;if(scope()===owner)update();}},null,{flushWorkspace:false});})();
 }
 async function choose(w,files,owner,token){if(!alive(w,owner,token))return;const local=state(w),c=catalogue(owner),selected=[...files];if(!selected.length)return;
  if(local.job||local.reading){api.toast('선택한 파일을 먼저 보관하거나 취소해 주세요. 입력은 유지됩니다.');return;}
  if(selected.length!==1||c.phase!=='ready'||selected[0].size>c.value.limits.fileBytes){api.toast('현재 보관 기능은 한 번에 1개, 파일당 1MiB까지 지원해요. 기존 자료는 유지됩니다.');return;}
  const file=selected[0],basis=c.value.revision,job={file,input:null,inFlight:false};local.job=job;local.reading=true;local.message='선택한 파일을 확인하고 있습니다…';update();
  try{const bytes=new Uint8Array(await file.arrayBuffer()),hash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(v=>v.toString(16).padStart(2,'0')).join('');let binary='';for(let n=0;n<bytes.length;n+=8192)binary+=String.fromCharCode(...bytes.subarray(n,n+8192));
   if(local.job!==job)return;job.input={revision:basis,command:crypto.randomUUID().replaceAll('-',''),item:{id:crypto.randomUUID().replaceAll('-',''),name:file.name,type:file.type,size:bytes.length,hash,modifiedAt:file.lastModified,data:btoa(binary).replaceAll('+','-').replaceAll('/','_')}};
   if(alive(w,owner,token))send(w,owner,local,job,token);
  }catch{if(local.job===job)local.message='선택한 파일을 읽지 못했어요. 원본 파일과 기존 보관본은 바뀌지 않았어요.';}
  finally{local.reading=false;if(scope()===owner)update();}
 }
 function mount(w){const owner=scope(),local=state(w),token={generation:api.view.generation};w.resourceLifetime=token;w.resourceGeneration=token.generation;const cache=catalogue(owner);if(cache.generation!==token.generation){cache.generation=token.generation;cache.phase='empty';}w.resourceScope=owner;w.browserScope=owner;w.resourceNameCleanup?.();w.resourceStamp=null;w.resourceStatusStamp=null;
  mountBrowserShell(w,{esc:api.esc,groups,projectBrowser:api.projectBrowser(w.key),trackDrag:api.trackDrag,scale:api.scale,density:()=>{render(w);api.persist();},persist:api.persist});
  for(const element of w.body.querySelectorAll('button,[role=separator],.density-steps'))for(const key of ['onclick','onpointerdown','onkeydown']){const handler=element[key];if(typeof handler==='function')element[key]=function(...args){if(alive(w,owner,token))return handler.apply(this,args);};}
  for(const node of w.body.querySelectorAll('[id]')){node.dataset.browserControl=node.id;node.removeAttribute('id');}
  const query=w.body.querySelector('[data-browser-control=object-query]');query.setAttribute('aria-label','자료 검색');query.placeholder='자료 검색…';
  const search=()=>{if(!alive(w,owner,token))return;w.meta.query=query.value;api.persist();render(w);};query.oninput=()=>{if(alive(w,owner,token)){w.meta.queryInput=query.value;api.persist();}};query.onkeydown=event=>{if(event.key==='Enter')search();};w.body.querySelector('[data-browser-control=object-search]').onclick=search;
  for(const button of w.body.querySelectorAll('[data-tab]'))button.onclick=()=>{if(alive(w,owner,token))api.switchGroup(w,button.dataset.tab);};
  const picker=document.createElement('input');picker.type='file';picker.hidden=true;picker.dataset.resourceFiles='';w.body.append(picker);picker.onchange=()=>{const files=[...picker.files];picker.value='';choose(w,files,owner,token);};
  const add=w.body.querySelector('[data-new]');add.setAttribute('aria-label','자료 추가');add.title='선택한 파일의 사본 보관 · 한 번에 1개, 파일당 1MiB';add.onclick=()=>{if(alive(w,owner,token)&&!local.job)picker.click();};
  w.body.querySelector('[data-browser-control=browser-actions]').onclick=event=>{if(!alive(w,owner,token))return;api.contextMenu(event.clientX,event.clientY,[['기본 순서',()=>sort('original')],['이름 오름차순',()=>sort('name')],['이름 내림차순',()=>sort('name-desc')],['최근 생성순',()=>sort('newest')]]);};function sort(value){if(alive(w,owner,token)){w.meta.sort=value;api.persist();render(w);}}
  const root=w.body.querySelector('[data-root]');root.onclick=()=>{if(alive(w,owner,token)){w.meta.query=w.meta.queryInput='';query.value='';api.persist();render(w);}};updateBrowserTitlePath(w,{contextMenu:api.contextMenu});
  const tree=w.body.querySelector('.browser-folder-tree');tree.innerHTML='<div class="folder-tree-row"><button class="folder-tree-name" aria-current="location">ProjectPack</button></div>';tree.querySelector('button').onclick=root.onclick;
  const output=document.createElement('output');output.className='resource-browser-status';output.dataset.resourceStatus='';output.setAttribute('aria-live','polite');w.body.append(output);const recovery=document.createElement('div');recovery.className='window-content';recovery.dataset.resourceRecovery='';recovery.hidden=true;w.body.append(recovery);
  w.body.ondragover=event=>{if(alive(w,owner,token)&&event.dataTransfer.types.includes('Files')){event.preventDefault();event.stopPropagation();event.dataTransfer.dropEffect='copy';}};
  w.body.ondrop=event=>{if(!alive(w,owner,token)||!event.dataTransfer.files.length)return;event.preventDefault();event.stopPropagation();choose(w,event.dataTransfer.files,owner,token);};
  render(w);const c=catalogue(owner);if(c.phase==='empty')load(w,token);return w;
 }
 function render(w){const owner=scope(),token=w.resourceLifetime;if(!alive(w,owner,token)||w.resourceScope!==owner)return;const c=catalogue(owner),local=state(w),root=w.body.querySelector('[data-browser-control=objects]'),output=w.body.querySelector('[data-resource-status]');if(!root||!output)return;if(c.phase==='empty'&&!api.busy&&!api.restoring)queueMicrotask(()=>{if(alive(w,owner,token)&&catalogue(owner).phase==='empty')load(w,token);});const recovery=w.body.querySelector('[data-resource-recovery]');
  const items=rows(w),selected=w.meta.resourceSelected,mode=w.meta.density<=0?'Compact':w.meta.density>=100?'Data':'Preview',stamp=JSON.stringify([c.phase,c.value?.revision,w.meta.query,w.meta.sort,w.meta.density,selected]);
  const add=w.body.querySelector('[data-new]');add.dataset.supported=String(c.phase==='ready'&&!local.job);add.disabled=c.phase!=='ready'||!!local.job||api.busy;
  const statusStamp=JSON.stringify([c.phase,local.message,local.job?.input?.command,local.job?.file.name,local.job?.inFlight,local.reading]);if(w.resourceStatusStamp!==statusStamp){w.resourceStatusStamp=statusStamp;output.replaceChildren();recovery.replaceChildren();recovery.hidden=c.phase!=='failed'&&(!local.job||local.job.inFlight||local.reading);const message=document.createElement('span');message.textContent=local.message||(c.phase==='loading'?'파일 목록을 확인하고 있습니다…':c.phase==='failed'?'자료를 확인하지 못했어요. 기존 보관본은 그대로예요.':items.length+'개 항목');output.append(message);if(!recovery.hidden){const copy=message.cloneNode(true);recovery.append(copy);}
  const reload=document.createElement('button');reload.type='button';reload.textContent='다시 확인';reload.dataset.resourceReload='';reload.disabled=c.phase==='loading'||!!local.job?.inFlight;reload.onclick=()=>{if(alive(w,owner,token))load(w,token);};recovery.append(reload);
  if(local.job){const job=local.job,label=document.createElement('small');label.textContent='선택한 파일: '+job.file.name;recovery.append(label);for(const [key,title]of[['retry','보관 다시 확인'],['cancel','선택 입력 취소']]){const button=document.createElement('button');button.type='button';button.dataset.resourcePending=key;button.textContent=title;button.disabled=job.inFlight||local.reading||key==='retry'&&!job.input;button.onclick=()=>{if(!alive(w,owner,token)||local.job!==job||job.inFlight)return;if(key==='retry')send(w,owner,local,job,token);else{local.job=null;local.message='선택한 파일 입력만 취소했어요. 이미 보관된 사본은 삭제하지 않아요.';update();}};recovery.append(button);}}
  }
  if(w.resourceStamp===stamp)return;w.resourceStamp=stamp;w.resourceNameCleanup?.();root.replaceChildren();root.style.setProperty('--browser-icon-size',(24+Math.max(0,Math.min(98,w.meta.density-1))*24/98)+'px');root.style.setProperty('--browser-tile-size',(80+w.meta.density/4)+'px');
  const list=document.createElement('div');list.className=mode==='Compact'?'compact-list':mode==='Data'?'browser-data-list':'object-grid';root.append(list);
  if(!items.length){const empty=document.createElement('div');empty.className='empty';empty.dataset.resourceEmpty='';empty.textContent=c.phase==='loading'?'자료를 확인하고 있습니다…':c.phase==='failed'?'파일 목록을 다시 확인해 주세요.':w.meta.query?'검색 결과가 없습니다.':'자료가 없습니다. 파일을 끌어 놓거나 자료 추가를 눌러 추가할 수 있습니다.';root.append(empty);}
  for(const row of items){const card=document.createElement('div');card.className=mode==='Compact'?'object-row':mode==='Data'?'object-data browser-data-row':'object-card concept-tile concept-file';card.dataset.resourceId=row.id;card.tabIndex=0;card.classList.toggle('selected',selected===row.id);card.setAttribute('aria-selected',String(selected===row.id));
   const icon=document.createElement('span');icon.className='obj-icon';icon.textContent=icons[row.kind];const name=document.createElement(mode==='Compact'?'strong':'span');name.className='name';name.title=row.name;const filename=document.createElement('span');filename.className='resource-filename';filename.dataset.resourceFullName=row.name;filename.dataset.resourceKind=row.kind;filename.textContent=row.name;name.append(filename);const detail=document.createElement('small');detail.textContent=labels[row.kind]+' · '+resourceSize(row.size);card.append(icon,name,detail);
   const select=()=>{if(!alive(w,owner,token)||!rows(w).some(item=>item.id===row.id&&item.hash===row.hash))return;w.meta.resourceSelected=row.id;api.persist();render(w);};card.onclick=select;card.onkeydown=event=>{if(['Enter',' '].includes(event.key)){event.preventDefault();select();}};card.ondblclick=()=>{if(alive(w,owner,token))api.toast('자료 사본은 보관되어 있어요. 내용 미리보기·편집은 아직 연결되지 않았어요.');};list.append(card);
  }
  w.resourceNameCleanup=bindResourceFileNames(root);
 }
 function retire(w){w.resourceNameCleanup?.();w.resourceNameCleanup=null;w.resourceLifetime=null;w.resourceGeneration=null;}
 return {mount,render,update,groups,retire,retireAll:()=>{for(const w of api.windows.values())retire(w);const c=catalogues.get(scope());if(c){c.generation=null;c.phase='empty';}}};
}
