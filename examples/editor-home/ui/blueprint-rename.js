// Labels are source metadata; editing never changes a stable node or callable ID.
export function mountBlueprintRename({w,data,api,select,applied}){
 const events=new AbortController(),scope=w.blueprintScope,inputs=api.inputs;
 const current=()=>api.current.projectId===scope&&w.blueprintData===data&&api.windows.get('blueprint')===w&&w.el.isConnected&&!w.el.hidden;
 const key=id=>scope+'|'+data.id+'|displayName|'+id;
 let editor=null,menu=null,submitting=false,press=null;
 const nodeFor=id=>data.nodes.find(n=>n.id===id&&n.renameable);
 const hostFor=id=>w.body.querySelector('[data-bp-name="'+CSS.escape(id)+'"]');
 function closeMenu(){menu?.remove();menu=null;}
 function resetLabel(){if(!editor)return;const {host,node}=editor;host.textContent='⚙ '+(node.displayName||node.id);host.classList.remove('is-renaming');editor=null;}
 function cancel(){if(!editor)return;inputs.delete(key(editor.node.id));resetLabel();api.persist();}
 function begin(id){
  if(!current()||submitting)return;const node=nodeFor(id),host=hostFor(id);if(!node||!host)return;
  closeMenu();if(editor?.node.id===id){editor.input.focus({preventScroll:true});return;}resetLabel();w.meta.blueprintNode=id;
  const input=document.createElement('input'),buttons=document.createElement('span');input.dataset.bpRename='';input.dataset.operation='blueprint-input';input.maxLength=256;input.setAttribute('aria-label','내부 함수 표시 이름');input.value=inputs.get(key(id))?.text??node.displayName??node.id;
  buttons.className='bp-rename-actions';
  const button=(text,title,action)=>{const el=document.createElement('button');el.type='button';el.textContent=text;el.title=title;el.setAttribute('aria-label',title);el.dataset.operation='';el.onclick=action;buttons.append(el);return el;};
  const remember=()=>{if(!current())return;const k=key(id);if(input.value===(node.displayName||node.id))inputs.delete(k);else inputs.set(k,{text:input.value,basis:inputs.has(k)?inputs.get(k).basis:data.basis});api.persist();};
  input.oninput=remember;
  const submit=()=>{if(submitting||!current())return;const text=input.value.trim();if(!text||text===(node.displayName||node.id)){cancel();return;}input.value=text;remember();submitting=true;
   api.work(async()=>{
    const root=data.rootId||data.id,prefix=scope+'|'+root,own=key(id);
    if(!current()||api.otherPending(data.sources.map(s=>s.id))||[...inputs.keys()].some(k=>(k.startsWith(prefix+'|')||k.startsWith(prefix+'/graph:'))&&k!==own))throw Error('다른 미적용 입력을 먼저 처리하세요. 표시 이름 입력은 유지됩니다.');
    const captured=inputs.get(own);if(!captured?.basis)throw Error('복원한 표시 이름은 현재 원본을 읽고 기준 재검토를 선택하세요. 입력은 유지됩니다.');
    await api.view.call('blueprint',{action:'rename',id:data.id,node:id,text,basis:captured.basis});
    if(inputs.get(own)?.text===text)inputs.delete(own);
    if(current())await applied(id);api.persist();
   },'표시 이름을 공유 초안에 적용했습니다. 프로젝트 저장은 초안 저장을 사용하세요.').finally(()=>submitting=false);
  };
  input.onkeydown=event=>{if(event.isComposing||event.keyCode===229)return;if(event.key==='Enter'){event.preventDefault();event.stopPropagation();submit();}else if(event.key==='Escape'){event.preventDefault();event.stopPropagation();cancel();host.focus({preventScroll:true});}};
  button('✓','표시 이름 적용',submit);button('×','표시 이름 입력 취소',cancel);button('↻','표시 이름 기준 재검토',()=>{const item=inputs.get(key(id));if(item)item.basis=data.basis;api.persist();api.toast('현재 읽은 원본을 기준으로 표시 이름을 재검토했습니다.');});
  editor={node,host,input};host.classList.add('is-renaming');host.replaceChildren(input,buttons);api.controls();input.focus({preventScroll:true});input.select();api.persist();
 }
 w.body.addEventListener('pointerdown',event=>{const header=event.target.closest('[data-bp-drag]');if(header)press={id:header.dataset.bpDrag,selected:w.meta.blueprintNode===header.dataset.bpDrag,active:w.el.classList.contains('active')};},{capture:true,signal:events.signal});
 w.body.addEventListener('contextmenu',event=>{
  const target=document.elementFromPoint(event.clientX,event.clientY)||event.target,header=target.closest('[data-bp-drag]'),node=nodeFor(header?.dataset.bpDrag);if(!node||!w.body.contains(header)||target.closest('input,button')||!current())return;
  event.preventDefault();event.stopPropagation();closeMenu();w.meta.blueprintNode=node.id;api.focus(w);api.persist();
  menu=document.createElement('div');menu.className='bp-rename-menu';menu.setAttribute('role','menu');const button=document.createElement('button');button.type='button';button.textContent='Rename · F2';button.setAttribute('role','menuitem');button.onclick=()=>begin(node.id);menu.append(button);document.body.append(menu);
  Object.assign(menu.style,{left:Math.max(8,Math.min(event.clientX,innerWidth-menu.offsetWidth-8))+'px',top:Math.max(8,Math.min(event.clientY,innerHeight-menu.offsetHeight-8))+'px'});button.focus({preventScroll:true});
 },{capture:true,signal:events.signal});
 document.addEventListener('pointerdown',event=>{if(menu&&!menu.contains(event.target))closeMenu();},{capture:true,signal:events.signal});
 document.addEventListener('keydown',event=>{
  if(!current()||!w.el.classList.contains('active')||event.isComposing||event.keyCode===229)return;
  if(event.key==='Escape'&&menu){event.preventDefault();closeMenu();return;}
  if(event.key==='F2'&&!event.target.closest('input,textarea,select,[contenteditable=true]')&&nodeFor(w.meta.blueprintNode)){event.preventDefault();event.stopPropagation();begin(w.meta.blueprintNode);}
 },{signal:events.signal});
 for(const host of w.body.querySelectorAll('[data-bp-name]'))host.onkeydown=event=>{if(event.key==='Enter'&&event.target===host){event.preventDefault();begin(host.dataset.bpName);}};
 return {activate(id,moved,onName){if(!current())return;if(!moved&&onName&&press?.id===id&&press.selected&&press.active&&nodeFor(id))begin(id);else select(id);},dispose(){closeMenu();resetLabel();events.abort();}};
}
