// Authored v666 finder over already visible presentation and the existing
// permission-filtered declaration projection. No file reads, grants or writes.
export function createWorkspaceFinder(api){
 let active=null;
 const visible=el=>!!el?.isConnected&&!el.closest('[hidden]')&&el.getClientRects().length>0&&getComputedStyle(el).visibility!=='hidden';
 const labels={category:'카테고리',concept:'개념',object:'개념',schema:'정보',enum:'종류',function:'기능',implementation:'구현',module:'모듈'};
 const glyph=value=>typeof value==='string'&&value.length<=16&&!value.startsWith('data:')?value:'◇';
 function close({focus=false}={}){const state=active;if(!state)return;active=null;api.contentClose?.();state.events.abort();state.observer.disconnect();state.resize.disconnect();state.panel.remove();state.anchor.setAttribute('aria-expanded','false');if(focus&&state.valid())state.anchor.focus({preventScroll:true});}
 function candidates(mode,query){
  const found=[],objects=api.objects(),matches=value=>String(value??'').toLocaleLowerCase().includes(query),represented=new Set(),seen=new Set();
  const excerpt=value=>{const flat=String(value??'').replace(/\s+/g,' '),index=flat.toLocaleLowerCase().indexOf(query);return flat.slice(Math.max(0,index-28),Math.max(0,index)+95);};
  const nodes=[...api.nodes(),...api.windows()];
  for(const node of nodes){
   if(seen.has(node.key)||!visible(node.el)||node.placed===false&&!node.documentDocked)continue;seen.add(node.key);
   const declaration=objects.find(row=>row.id===node.meta?.id),item=node.item,kind=item?.kind;
   const title=kind?api.decorationName(item):node.el.querySelector('.window-title .caption strong,.object-title-name')?.textContent?.trim()||node.title||'이름 없는 창';
   const detail=kind?({note:'메모',group:'그룹 · 창과 요소 묶음',portal:'하위 Workspace · 이동'}[kind]||'작업 공간 항목'):node.kind==='parent'?'상위 Workspace · 이동':declaration?labels[declaration.kind]||declaration.kind:'열린 창';
   const content=mode==='text'?title+' '+api.text(node.el):title+' '+detail;
   if(declaration)represented.add(declaration.id);
   if(mode==='text'?!query||!matches(content):query&&!matches(content))continue;
   found.push({key:'node:'+node.key,id:node.key,kind:'node',title,detail:mode==='text'?detail+' · '+excerpt(content):detail,icon:kind==='note'?'▧':kind==='portal'?'↗':kind==='group'?'▱':glyph(declaration?.icon)});
  }
  // Only names/types already exposed by the current native projection qualify.
  // Do not recursively search raw metadata, source paths or unobserved parents.
  if(query)for(const row of objects){
   const title=row.name||row.title||row.id.split('::').at(-1),detail=labels[row.kind]||row.kind||'요소',owned=row.owned!==false&&row.id.startsWith((api.namespace?.()||'')+'::'),content=title+' '+detail+(mode==='text'&&owned?' '+(row.description||'')+' '+(api.contentRows?.().get(row.id)?.text||''):'');
   if(mode!=='text'&&represented.has(row.id)||!matches(content))continue;
   found.push({key:'object:'+row.id,id:row.id,kind:'object',title,detail:mode==='text'?detail+' · '+excerpt(content):detail,icon:glyph(row.icon)});
  }
  return found;
 }
 function open(){
  const context=api.context();if(!context||!api.ready())return;
  if(active?.valid()){active.input.focus();active.input.select();return;}
  close();api.beforeOpen();const {anchor,host,key}=context,panel=document.createElement('section');panel.id='workspace-find-panel';panel.className='workspace-find-panel';panel.setAttribute('role','dialog');panel.setAttribute('aria-label','검색');panel.dataset.office='false';
  panel.innerHTML='<header><strong>검색</strong><button type="button" data-find-close aria-label="검색 닫기">×</button></header><div class="workspace-find-modes" role="group" aria-label="검색 방식"><button type="button" data-find-mode="elements" aria-pressed="true">요소</button><button type="button" data-find-mode="text" aria-pressed="false">글자</button></div><input type="search" aria-label="검색어" maxlength="256" autocomplete="off"><div class="workspace-find-status" role="status"></div><div class="workspace-find-results"></div>';
  document.body.append(panel);anchor.setAttribute('aria-expanded','true');const input=panel.querySelector('input'),list=panel.querySelector('.workspace-find-results'),status=panel.querySelector('.workspace-find-status'),events=new AbortController();let mode='elements',activeIndex=0,stamp='',queued=false;
  const valid=()=>{const now=api.context();return !!now&&now.key===key&&now.anchor===anchor&&now.host===host&&visible(anchor);};
  const position=()=>{if(!valid()){close();return;}const box=anchor.getBoundingClientRect(),area=host.getBoundingClientRect(),right=Math.max(8,innerWidth-box.right),height=Math.max(180,Math.min(580,box.top-Math.max(8,area.top)-16));panel.style.right=Math.min(right,Math.max(8,innerWidth-panel.offsetWidth-8))+'px';panel.style.bottom=Math.max(8,innerHeight-box.top+8)+'px';panel.style.height=height+'px';};
  function render(reset=false){
   if(!valid()){close();return;}const query=input.value.trim().toLocaleLowerCase();api.contentEnsure?.(mode==='text'&&!!query);const content=api.contentStatus?.(),rows=candidates(mode,query),ready=api.ready()&&!['queued','loading'].includes(content?.phase),load=api.loadState?.(),next=JSON.stringify([mode,query,ready,load,content,rows]);if(!reset&&stamp===next){position();return;}const previous=list.querySelector('[data-active=true]')?.dataset.findKey;stamp=next;list.replaceChildren();input.placeholder=mode==='text'?'찾을 글자나 내용을 입력하십시오…':'배치된 창이나 요소 이름 검색…';
   status.textContent=load==='loading'?'프로젝트 요소 목록을 확인하고 있습니다.':load==='failed'?'프로젝트 요소 목록을 확인하지 못했어요. 열린 항목은 계속 찾을 수 있어요.':query?rows.length+'개 결과':mode==='text'?'찾을 글자를 입력해 주십시오.':'배치된 요소를 찾거나 이름을 입력해 주십시오.';
   if(load==='failed'){const retry=document.createElement('button');retry.type='button';retry.dataset.findRetry='';retry.textContent='다시 불러오기';retry.onclick=()=>api.load?.();status.append(retry);}
   if(mode==='text'&&query&&load!=='loading'&&load!=='failed'&&content){
    if(['queued','loading'].includes(content.phase))status.textContent='소유 객체의 정의·값 내용을 확인하고 있어요. '+content.loaded+'개 확인';
    else if(content.phase==='restricted')status.textContent='이 설정 프로젝트는 내용 조회를 허용하지 않아요. 이름·배치된 글자 찾기는 유지해요.';
    else if(content.phase==='failed')status.textContent='객체 내용을 확인하지 못했어요. 현재 결과는 일부일 수 있어요.';
    else if(content.phase==='partial')status.textContent=rows.length+'개 결과 · 정의·값 '+content.loaded+'개 확인 · '+(content.unsupported+content.unavailable)+'개 미지원/확인 불가';
    else if(content.phase==='ready')status.textContent=rows.length+'개 결과 · 정의·값 '+content.loaded+'개 확인';
    if(['ready','partial','failed'].includes(content.phase)){const refresh=document.createElement('button');refresh.type='button';refresh.dataset.findContentRefresh='';refresh.textContent=content.phase==='failed'?'내용 다시 불러오기':'내용 새로 확인';refresh.onclick=()=>api.contentRefresh?.();status.append(refresh);}
   }
   let section='';for(const row of rows.slice(0,80)){
    const group=mode==='text'?'글자 일치':row.kind==='node'?'열린 창·작업 공간 항목':'요소';if(section!==group){section=group;const heading=document.createElement('h3');heading.textContent=group;list.append(heading);}
    const button=document.createElement('button');button.type='button';button.className='workspace-find-result';button.dataset.findKey=row.key;button.disabled=!ready;const icon=document.createElement('span');icon.className='workspace-find-icon';icon.textContent=row.icon;const content=document.createElement('span'),title=document.createElement('strong'),detail=document.createElement('small');title.textContent=row.title;detail.textContent=row.detail;content.append(title,detail);button.append(icon,content);button.onclick=()=>{
     if(!valid()||!api.ready()||['queued','loading'].includes(api.contentStatus?.().phase))return;const current=candidates(mode,input.value.trim().toLocaleLowerCase()).find(item=>item.key===row.key);if(!current){render();return;}close();if(current.kind==='object')api.openObject(current.id);else api.focusNode(current.id);
    };list.append(button);
   }
   if(query&&!rows.length){const empty=document.createElement('p');empty.className='workspace-find-empty';empty.textContent='일치하는 결과가 없습니다.';list.append(empty);}
   const buttons=[...list.querySelectorAll('.workspace-find-result')];activeIndex=reset?0:Math.max(0,buttons.findIndex(button=>button.dataset.findKey===previous));if(buttons[activeIndex])buttons[activeIndex].dataset.active='true';position();
  }
  const update=()=>{if(queued)return;queued=true;queueMicrotask(()=>{queued=false;if(active?.panel===panel)render();});};
  const observer=new MutationObserver(update),resize=new ResizeObserver(position);observer.observe(document.body,{childList:true,subtree:true,characterData:true,attributes:true,attributeFilter:['hidden','aria-hidden']});resize.observe(host);
  input.oninput=()=>render(true);for(const button of panel.querySelectorAll('[data-find-mode]'))button.onclick=()=>{mode=button.dataset.findMode;for(const item of panel.querySelectorAll('[data-find-mode]'))item.setAttribute('aria-pressed',String(item===button));render(true);input.focus();};panel.querySelector('[data-find-close]').onclick=()=>close({focus:true});
  panel.onkeydown=event=>{event.stopPropagation();if(event.isComposing||event.keyCode===229)return;if(event.key==='Escape'){event.preventDefault();close({focus:true});return;}if((event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==='f'){event.preventDefault();input.focus();input.select();return;}if(event.target!==input)return;const buttons=[...list.querySelectorAll('.workspace-find-result')];if(['ArrowDown','ArrowUp'].includes(event.key)&&buttons.length){event.preventDefault();buttons[activeIndex]?.removeAttribute('data-active');activeIndex=(activeIndex+(event.key==='ArrowDown'?1:-1)+buttons.length)%buttons.length;buttons[activeIndex].dataset.active='true';buttons[activeIndex].scrollIntoView({block:'nearest'});}else if(event.key==='Enter'&&buttons.length){event.preventDefault();buttons[activeIndex]?.click();}};
  document.addEventListener('pointerdown',event=>{if(!panel.contains(event.target)&&!anchor.contains(event.target))close();},{capture:true,signal:events.signal});window.addEventListener('resize',position,{signal:events.signal});host.addEventListener('input',update,{signal:events.signal});host.addEventListener('change',update,{signal:events.signal});
  active={panel,input,anchor,events,observer,resize,valid,update};render();input.focus();api.load?.();
 }
 return {open,close,update:()=>active?.update()};
}
