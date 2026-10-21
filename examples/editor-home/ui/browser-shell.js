// v508 browser chrome and title path; declarations remain owned by the existing adapter.
const steps=[0,20,40,60,80,100];
export function mountBrowserShell(w,api){
 w.browserCommitStatus=null;w.browserCommitStamp=null;updateBrowserCommitActions(w,null);
 const {esc,groups}=api,group=w.meta.group;w.el.classList.add('browser-view');w.meta.density=steps.reduce((best,value)=>Math.abs(value-w.meta.density)<Math.abs(best-w.meta.density)?value:best,40);
 w.el.querySelector('.browser-title-path')?.remove();
 w.body.innerHTML=`${api.projectBrowser?`<div class="browser-tabs">${Object.entries(groups).map(([key,name])=>`<button data-tab="${key}" class="${key===group?'selected':''}" draggable="true" title="끌어서 ${name} 브라우저 만들기">${name}</button>`).join('')}</div>`:''}<div class="browser-tools"><button type="button" class="secondary browser-hierarchy-toggle" data-browser-detail><svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path d="M5 4v14h6M5 9h6M12 7h7v4h-7ZM12 16h7v4h-7Z" fill="none" stroke="currentColor" stroke-width="1.7"/></svg></button><input id="object-query" class="search" aria-label="의미 객체 검색" placeholder="${groups[group]} 검색…" value="${esc(w.meta.queryInput??w.meta.query??'')}" style="min-width:60px"><button id="object-search" class="secondary" aria-label="검색 확정">검색</button><button id="browser-actions" class="secondary" aria-label="정렬 방법" title="정렬 방법"><svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M4 6h16M4 12h11M4 18h6" fill="none" stroke="currentColor" stroke-width="2"/></svg></button><button data-new class="secondary" aria-label="새 의미 객체">＋</button><div class="density-steps" role="group" aria-label="브라우저 표시 크기">${steps.map((value,i)=>`<button type="button" class="density-step ${w.meta.density===value?'selected':''}" data-density="${value}" aria-label="표시 크기 ${i+1}단계" aria-pressed="${w.meta.density===value}" title="${i===0?'Compact':i===5?'Data':'Preview · '+(i+1)+'단계'}"><span style="height:${7+i*3}px"></span></button>`).join('')}</div></div><div class="crumbs"><button data-root>ProjectPack</button></div><div class="browser-file-pane"><nav class="browser-folder-tree" aria-label="폴더 계층"></nav><div id="objects" class="browser-items" tabindex="0"></div></div><span id="density-label" hidden></span><span data-total hidden></span>`;
 setupBrowserTreeResize(w,w.body.querySelector('.browser-file-pane'),w.body.querySelector('.browser-folder-tree'),w.body.querySelector('.browser-items'),api);
 const density=w.body.querySelector('.density-steps'),pick=value=>{if(w.meta.density===value)return;w.meta.density=value;for(const b of density.querySelectorAll('[data-density]')){const active=Number(b.dataset.density)===value;b.classList.toggle('selected',active);b.setAttribute('aria-pressed',String(active));}api.density();};let suppress=false;
 density.onpointerdown=e=>{if(e.button!==0)return;e.preventDefault();suppress=true;density.setPointerCapture(e.pointerId);const choose=x=>{const box=density.getBoundingClientRect();pick(steps[Math.max(0,Math.min(5,Math.floor((x-box.left)/box.width*6)))]);};choose(e.clientX);density.onpointermove=ev=>{if(ev.pointerId===e.pointerId)choose(ev.clientX);};const finish=()=>{density.onpointermove=null;density.onpointerup=null;density.onpointercancel=null;if(density.hasPointerCapture(e.pointerId))density.releasePointerCapture(e.pointerId);setTimeout(()=>suppress=false,0);};density.onpointerup=density.onpointercancel=finish;};
 for(const b of density.querySelectorAll('[data-density]'))b.onclick=()=>{if(!suppress)pick(Number(b.dataset.density));};
 const toggle=w.body.querySelector('[data-browser-detail]');toggle.onclick=()=>{if(w.meta.treeWidth>0){w.meta.treeRestoreWidth=w.meta.treeWidth;w.setBrowserTreeWidth(0);}else w.setBrowserTreeWidth(w.meta.treeRestoreWidth||160);api.persist();};

}

export function mountBrowserCommitActions(w,api){
 const controls=w.el.querySelector('.window-title .row');if(!controls||controls.querySelector('[data-browser-save]'))return;
 const workers=document.createElement('span');workers.className='browser-title-workers';workers.dataset.browserWorkers='';controls.prepend(workers);
 for(const [key,label,title] of [['discard','변경 취소','현재 범위의 적용된 변경을 마지막 저장본으로 되돌리기'],['save','임시 저장','이 프로젝트의 작업 사본을 저장 · 최종 소스는 변경하지 않음'],['confirm','확정','현재 범위의 변경을 검토한 뒤 별도 확정']]){const b=document.createElement('button');b.type='button';b.className='window-commit-action';b.dataset['browser'+key[0].toUpperCase()+key.slice(1)]='';b.textContent=label;b.title=title;b.dataset.normalTitle=title;b.disabled=true;b.onclick=()=>api.action(w,key);controls.insertBefore(b,controls.querySelector('[data-fold],[data-close]'));}
}
export function updateBrowserCommitActions(w,status,blocked=false){
 for(const key of ['save','discard','confirm']){const button=w.el.querySelector('[data-browser-'+key+']');if(!button)continue;button.title=status?.state==='error'?'변경 상태 확인 실패 · 검색을 눌러 다시 확인해 주세요. [browser-draft-status]':button.dataset.normalTitle;button.disabled=blocked||status?.state!=='ready'||(key==='confirm'?!status.dirty:!status.unsaved)||(key==='discard'&&!status.canDiscard);}
}

export function updateBrowserTitlePath(w,api={}){
 const caption=w.el.querySelector(':scope>.window-title .caption'),path=w.el.querySelector('.crumbs');if(!caption||!path)return;
 w.pathObserver?.disconnect();caption.querySelector(':scope>strong')?.remove();
 const buttons=[...path.querySelectorAll('button')];if(!buttons.length)return;path.replaceChildren();const spans=buttons.map((button,index)=>{const step=document.createElement('span');step.className='browser-path-step';if(index){const separator=document.createElement('span');separator.textContent='/';separator.className='path-separator';step.append(separator);}button.title=button.title||button.textContent;if(!index)button.classList.add('browser-path-root');step.append(button);path.append(step);return step;});
 path.classList.add('browser-title-path');path.setAttribute('aria-label','현재 브라우저 경로');path.title=buttons.map(b=>b.textContent).join(' / ');caption.append(path);
 const ellipsis=document.createElement('span');ellipsis.className='browser-path-ellipsis';ellipsis.innerHTML='<span class="path-separator">/</span><button type="button" aria-label="생략된 경로 보기">…</button>';ellipsis.hidden=true;if(spans.length>1)spans[0].after(ellipsis);ellipsis.querySelector('button').onclick=e=>api.contextMenu?.(e.clientX,e.clientY,buttons.slice(1,-1).map(button=>[button.textContent,()=>button.click()]));
 const fit=()=>{if(!path.isConnected||!path.clientWidth)return;spans.forEach(s=>s.hidden=false);ellipsis.hidden=true;path.classList.remove('is-condensed');const width=spans.reduce((sum,s,i)=>sum+buttons[i].scrollWidth+(i?12:0),0)+Math.max(0,spans.length-1)*5;if(spans.length>2&&width>path.clientWidth){spans.slice(1,-1).forEach(s=>s.hidden=true);ellipsis.hidden=false;path.classList.add('is-condensed');}};w.pathObserver=new ResizeObserver(fit);w.pathObserver.observe(path);requestAnimationFrame(fit);
}

function setupBrowserTreeResize(w,pane,tree,items,api){
 const handle=document.createElement('div');handle.className='browser-tree-resizer';handle.tabIndex=0;
 handle.setAttribute('role','separator');handle.setAttribute('aria-orientation','vertical');
 handle.setAttribute('aria-label','계층 너비 조절, 클릭하여 접기 또는 펼치기');handle.title='드래그하여 너비 조절 · 클릭하여 접기 / 펼치기';
 tree.after(handle);
 const max=()=>pane.clientWidth?Math.max(80,pane.clientWidth-100):Math.max(160,w.meta.treeWidth||160);
 const apply=value=>{const width=Math.max(0,Math.min(max(),value));w.meta.hierarchyVisible=width>0;const toggle=w.body.querySelector("[data-browser-detail]");toggle?.setAttribute("aria-pressed",String(width>0));toggle?.setAttribute("aria-label",width>0?"폴더 계층 접기":"폴더 계층 펼치기");w.meta.treeWidth=width;pane.style.setProperty('--browser-tree-width',width+'px');pane.classList.toggle('tree-collapsed',width===0);handle.title=width===0?'계층구조 펼치기 · 드래그하여 너비 조절':'드래그하여 너비 조절 · 클릭하여 접기';tree.inert=width===0;handle.setAttribute('aria-valuemin','0');handle.setAttribute('aria-valuemax',String(max()));handle.setAttribute('aria-valuenow',String(Math.round(width)));return width};
 const toggle=()=>{if(w.meta.treeWidth>0){w.meta.treeRestoreWidth=w.meta.treeWidth;apply(0)}else apply(w.meta.treeRestoreWidth||160);api.persist()};
 w.setBrowserTreeWidth=apply;apply(w.meta.hierarchyVisible===false?0:w.meta.treeWidth??160);
 handle.onpointerdown=e=>{
  if(e.button!==0)return;e.preventDefault();e.stopPropagation();const start=w.meta.treeWidth,restore=w.meta.treeRestoreWidth;
  api.trackDrag(e,handle,(ev,sx)=>{const scale=w.documentDocked||!w.placed?1:api.scale();apply(start+(ev.clientX-sx)/scale)},(ev,moved)=>{
   if(ev.type!=='pointerup'){apply(start);w.meta.treeRestoreWidth=restore;return}
   if(!moved)toggle();else{if(w.meta.treeWidth>0)w.meta.treeRestoreWidth=w.meta.treeWidth;api.persist()}
  });
 };
 handle.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();toggle();return}if(!['ArrowLeft','ArrowRight','Home','End'].includes(e.key))return;e.preventDefault();apply(e.key==='Home'?0:e.key==='End'?max():w.meta.treeWidth+(e.key==='ArrowRight'?16:-16));if(w.meta.treeWidth>0)w.meta.treeRestoreWidth=w.meta.treeWidth;api.persist()};
}