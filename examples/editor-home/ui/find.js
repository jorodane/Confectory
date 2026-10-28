// Transient text search over already placed presentation; no source reads or commands.
export function createPlacedTextFind(api){
 let active=null,lastHost=null;
 const visible=el=>!!el?.isConnected&&!el.closest('[hidden]')&&el.getClientRects().length>0&&getComputedStyle(el).visibility!=='hidden';
 function placedText(el){
  const parts=[],walker=document.createTreeWalker(el,NodeFilter.SHOW_TEXT);let node;
  while(node=walker.nextNode()){const parent=node.parentElement;if(parent&&!parent.closest('input,textarea,select,script,style,template,[hidden],[aria-hidden="true"]')&&visible(parent))parts.push(node.textContent);}
  for(const input of el.querySelectorAll('input,textarea,select')){
   const identity=[input.type,input.id,input.name,input.autocomplete,...[...input.attributes].filter(a=>a.name.startsWith('data-')).map(a=>a.name+' '+a.value)].join(' ');
   if(visible(input)&&input.type!=='hidden'&&!/password|secret|token|api[-_]?key/i.test(identity))parts.push(input.value);
  }
  return parts.join(' ').replace(/\s+/g,' ').trim();
 }
 function close(){active?.close();}
 function open(context=api.context(lastHost)){
  if(!context||!visible(context.host)||!context.isCurrent())return;
  if(active?.context.key===context.key&&active.context.host===context.host){active.input.focus();active.input.select();return;}
  close();const panel=document.createElement('section');panel.className='placed-text-find';panel.setAttribute('role','dialog');panel.setAttribute('aria-label',context.title);
  panel.innerHTML='<header><strong></strong><button type="button" data-find-close aria-label="찾기 닫기">×</button></header><div class="placed-find-row"><input type="search" maxlength="256" aria-label="배치된 노드에서 찾기" placeholder="배치된 노드의 글자 찾기…"><span data-find-count role="status"></span><button type="button" data-find-prev aria-label="이전 결과">↑</button><button type="button" data-find-next aria-label="다음 결과">↓</button></div><p data-find-result></p>';
  panel.querySelector('strong').textContent=context.title;document.body.append(panel);
  const input=panel.querySelector('input'),events=new AbortController();input.placeholder=context.placeholder||input.placeholder;let results=[],index=-1,marked=null;
  function valid(){return visible(context.host)&&context.isCurrent();}
  function clear(){marked?.classList.remove('is-placed-find-match');marked=null;}
  function position(){if(!valid()){dispose();return;}const rect=context.host.getBoundingClientRect();panel.style.left=Math.max(8,Math.min(innerWidth-panel.offsetWidth-8,rect.right-panel.offsetWidth-12))+'px';panel.style.top=Math.max(8,Math.min(innerHeight-panel.offsetHeight-8,rect.top+(context.host.matches('.window')?52:12)))+'px';}
  function show(focus=true){
   clear();const item=results[index],term=input.value.trim().toLocaleLowerCase();panel.querySelector('[data-find-count]').textContent=item?(index+1)+' / '+results.length:'0 / 0';
   const start=item?Math.max(0,item.text.toLocaleLowerCase().indexOf(term)-20):0;panel.querySelector('[data-find-result]').textContent=!term?(context.emptyMessage||'현재 화면에 배치된 노드를 검색합니다.'):item?item.text.slice(start,start+160):'일치하는 노드가 없습니다.';
   panel.querySelectorAll('[data-find-prev],[data-find-next]').forEach(b=>b.disabled=!item);
   if(item){if(focus)context.focus(item);marked=item.element;marked.classList.add('is-placed-find-match');}
  }
  function search(reset=true,focus=true){
   if(!valid()){dispose();return;}const previous=results[index]?.id,term=input.value.trim().toLocaleLowerCase();results=term?context.items().filter(item=>visible(item.element)).map(item=>({...item,text:placedText(item.element)})).filter(item=>item.text.toLocaleLowerCase().includes(term)):[];
   index=results.length?(reset?0:Math.max(0,results.findIndex(item=>item.id===previous))):-1;show(focus);
  }
  function step(delta){search(false,false);if(results.length){index=(index+delta+results.length)%results.length;show();}}
  function dispose(){clear();events.abort();hostObserver.disconnect();pageObserver.disconnect();resize.disconnect();panel.remove();if(active?.panel===panel)active=null;}
  const hostObserver=new MutationObserver(()=>search(false,false)),pageObserver=new MutationObserver(()=>{if(!valid())dispose();}),resize=new ResizeObserver(position);
  hostObserver.observe(context.host,{childList:true,subtree:true,characterData:true,attributes:true,attributeFilter:['hidden','aria-hidden']});pageObserver.observe(document.body,{childList:true,subtree:true});resize.observe(context.host);
  context.host.addEventListener('click',()=>queueMicrotask(()=>{if(panel.isConnected)search(false,false);}),{signal:events.signal});context.host.addEventListener('input',()=>search(false,false),{signal:events.signal});context.host.addEventListener('change',()=>search(false,false),{signal:events.signal});window.addEventListener('resize',position,{signal:events.signal});
  input.oninput=()=>search();panel.querySelector('[data-find-prev]').onclick=()=>step(-1);panel.querySelector('[data-find-next]').onclick=()=>step(1);panel.querySelector('[data-find-close]').onclick=dispose;
  panel.onkeydown=event=>{event.stopPropagation();if(event.isComposing||event.keyCode===229)return;if(event.key==='Escape'){event.preventDefault();dispose();context.host.focus({preventScroll:true});}else if(event.key==='Enter'){event.preventDefault();step(event.shiftKey?-1:1);}else if((event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==='f'){event.preventDefault();input.select();}};
  active={panel,input,context,close:dispose};position();search();input.focus();
 }
 function track(event){if(event.target.closest?.('.placed-text-find,.nav-menu'))return;lastHost=event.target.closest?.('.window,.tab-document')||null;}
 document.addEventListener('pointerdown',track,true);document.addEventListener('focusin',track,true);
 document.addEventListener('keydown',event=>{if(event.isComposing||event.keyCode===229||event.defaultPrevented||!(event.ctrlKey||event.metaKey)||event.key.toLowerCase()!=='f')return;const context=api.context(lastHost);if(!context)return;event.preventDefault();open(context);});
 return {open,close};
}
