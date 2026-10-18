import {createWorkspaceLinks} from './workspace-links.js';
import {noteHtml,noteMarkup,bindNoteEditor,applyNoteTitle} from './notes.js';

// Common v318 presentation runtime. Window and decoration records share selection and drag ownership.
// Domain actions are explicit host callbacks; no prototype database or AI implementation lives here.
export function createWorkspaceRuntime(host){
 const state={windows:new Map(),z:10,shiftHeld:false,activeWorkspaceId:'root',visitedWorkspaceTabs:['root'],workspaceContextGuard:null,workspaceNodes:new Map(),selectedWorkspaceNodeKeys:new Set(),workspaceGrid:22,workspaceDot:11,workspaceInset:2,workspaceDragPayload:null,workspaceDragGhost:null,workspaceDragPlacement:null};
const linkRuntime=createWorkspaceLinks({state,owner:()=>workspaceRecord(),project:()=>host.project,canvas:()=>host.$('#workspace'),ready:()=>!host.isRestoring&&!state.gesture&&(!host.canNavigate||host.canNavigate()),before:host.beforePrivateLayout?()=>host.beforePrivateLayout():undefined,record:before=>host.recordPrivateLayout?.(before),save:()=>saveLayouts(),toast:host.toast,contextMenu:host.contextMenu});
function cancelInteractions(){linkRuntime.cancel();state.cancelDrag?.();}
function setupWorkspaceNavigation(){
 const canvas=host.$('#workspace');if(!canvas||!host.project)return;if(host.preserveLifecycle&&!canvas.querySelector('.workspace-world-layer')){const world=document.createElement('div');world.className='workspace-world-layer';canvas.append(world);}
 const view=host.project.workspaceView??={x:0,y:0,scale:1};
 view.x=Number.isFinite(view.x)?view.x:0;view.y=Number.isFinite(view.y)?view.y:0;
 view.scale=Number.isFinite(view.scale)?Math.max(.4,Math.min(3,view.scale)):1;host.project.workspaceView=view;
 const apply=()=>{canvas.style.setProperty('--canvas-grid-size',22*view.scale+'px');canvas.style.setProperty('--canvas-grid-x',view.x+'px');canvas.style.setProperty('--canvas-grid-y',view.y+'px');state.windows.forEach(w=>{if(w.placed)placeWindow(w)});positionWorkspaceDecorations();linkRuntime.schedule()};
 canvas.updateWorkspaceView=apply;apply();
 canvas.resetWorkspaceView=()=>{const origin=workspaceOrigin();view.x=origin?canvas.clientWidth/2-origin.x*view.scale:0;view.y=origin?canvas.clientHeight/2-origin.y*view.scale:0;apply();host.project.workspaceView=view;host.persist()};
 let drag=null,ignoreContextUntil=0,suppressDragContextUntil=0;
 if(state.workspaceContextGuard){document.removeEventListener('contextmenu',state.workspaceContextGuard.context,true);document.removeEventListener('pointerdown',state.workspaceContextGuard.pointer,true)}
 const guardContext=e=>{if(drag?.button===2||performance.now()<suppressDragContextUntil){e.preventDefault();e.stopImmediatePropagation();if(!drag)suppressDragContextUntil=0}};
 const resetContext=e=>{if(e.button===2&&!drag)suppressDragContextUntil=0};
 state.workspaceContextGuard={context:guardContext,pointer:resetContext};
 document.addEventListener('contextmenu',guardContext,true);document.addEventListener('pointerdown',resetContext,true);
 const openRightClickMenu=(target,x,y)=>{
  const line=target.closest?.('.workspace-link-line');if(line){const edge=linkRuntime.rows().find(edge=>edge.parent===line.dataset.parent&&edge.child===line.dataset.child);if(edge)host.contextMenu(x,y,[['연결 해제',()=>linkRuntime.disconnect(edge)]]);return;}
  const event={clientX:x,clientY:y},objectEl=target.closest?.('[data-object]'),windowEl=target.closest?.('.window');
  const treeButton=target.closest?.('.folder-tree-name');
  if(treeButton&&windowEl){const w=state.windows.get(windowEl.dataset.key);if(w)host.browserTreeCreateMenu(w,treeButton.dataset.treeId||null,event);return}
  if(objectEl&&windowEl){const object=host.project.objects.find(o=>o.id===objectEl.dataset.object),w=state.windows.get(windowEl.dataset.key);if(object&&w){if(!host.preserveLifecycle)host.selectObject(object.id);host.objectContext(event,object,w)}return}
  if(target.closest?.('.browser-folder-tree')&&windowEl){const w=state.windows.get(windowEl.dataset.key);if(w)host.browserTreeCreateMenu(w,w.meta.parent||w.meta.rootFolder||null,event);return}
  if(target.closest?.('.window-title')&&windowEl){const w=state.windows.get(windowEl.dataset.key);if(w)host.contextMenu(x,y,[...(host.openWindowDocument?[['탭으로 열기',()=>host.openWindowDocument(w)]]:[]),...linkRuntime.menu(w),...(host.privateHistoryMenu?.()||[]),[w.meta.mainWorkspace?'메인 작업창 지정 해제':'메인 작업창으로 지정',()=>setMainWorkspaceWindow(w)],...(!isProjectBrowserKey(w.key)&&isBrowserWindowKey(w.key)?[['같은 브라우저 새 창으로 열기',()=>host.duplicateChildBrowser(w)]]:[])]);return}
  if(target.closest?.('.browser-items')&&windowEl){const w=state.windows.get(windowEl.dataset.key);if(w)host.browserCreateMenu(w,event);return}
  if(!windowEl)showWorkspaceContextMenu(x,y,target);
 };
 canvas.onpointerdown=e=>{
  if(![1,2].includes(e.button)||e.target.closest?.('.tab-document'))return;
  if(e.button===2)ignoreContextUntil=0;
  if(e.button===2&&e.target.closest?.('.bubble-dock,.workspace-tabs,.tab-document'))return;
  ignoreContextUntil=0;e.preventDefault();
  drag={id:e.pointerId,x:e.clientX,y:e.clientY,startX:view.x,startY:view.y,button:e.button,moved:false,target:e.target};
  canvas.setPointerCapture(e.pointerId);canvas.classList.add('is-panning');
 };
 canvas.onpointermove=e=>{if(!drag||e.pointerId!==drag.id)return;drag.moved ||= Math.abs(e.clientX-drag.x)+Math.abs(e.clientY-drag.y)>3;view.x=drag.startX+e.clientX-drag.x;view.y=drag.startY+e.clientY-drag.y;apply()};
 const finish=e=>{
  if(!drag||e.pointerId!==drag.id)return;
  const completed=drag;drag=null;if(host.preserveLifecycle&&e.type==='pointercancel'){view.x=completed.startX;view.y=completed.startY;apply()}canvas.classList.remove('is-panning');
  if(canvas.hasPointerCapture(e.pointerId))canvas.releasePointerCapture(e.pointerId);
  host.project.workspaceView=view;host.persist();
  if(completed.button===2){ignoreContextUntil=performance.now()+(completed.moved?700:100);if(completed.moved)suppressDragContextUntil=performance.now()+700;if(e.type==='pointerup'&&!completed.moved)openRightClickMenu(completed.target,e.clientX,e.clientY)}
 };
 canvas.onpointerup=finish;canvas.onpointercancel=finish;
 canvas.addEventListener('contextmenu',e=>{
  if(drag?.button===2||performance.now()<ignoreContextUntil){e.preventDefault();e.stopPropagation();return}
  if(e.target.closest?.('.window,.bubble-dock,.workspace-tabs,.tab-document'))return;
  e.preventDefault();e.stopPropagation();showWorkspaceContextMenu(e.clientX,e.clientY,e.target)
 },true);
 canvas.addEventListener('dblclick',e=>{
  if(e.button!==0||e.target!==canvas||state.activeWorkspaceId==='root')return;
  returnToParentWorkspace();
 });
 canvas.onwheel=e=>{
  if(e.target.closest?.('.tab-document'))return;
  if(e.target!==canvas){const win=e.target.closest?.('.window');if(!win)return;for(let node=e.target;node&&node!==canvas;node=node.parentElement){if(node.matches?.('select,input[type=range],input[type=number]'))return;const style=getComputedStyle(node);const vertical=/auto|scroll/.test(style.overflowY),horizontal=/auto|scroll/.test(style.overflowX);if(vertical&&node.scrollHeight>node.clientHeight+1&&((e.deltaY<0&&node.scrollTop>0)||(e.deltaY>0&&node.scrollTop+node.clientHeight<node.scrollHeight-1)))return;if(horizontal&&node.scrollWidth>node.clientWidth+1&&((e.deltaX<0&&node.scrollLeft>0)||(e.deltaX>0&&node.scrollLeft+node.clientWidth<node.scrollWidth-1)))return}}
  e.preventDefault();const next=Math.max(.4,Math.min(3,view.scale*Math.exp(-e.deltaY*.001)));if(next===view.scale)return;
  const rect=canvas.getBoundingClientRect(),x=e.clientX-rect.left,y=e.clientY-rect.top,ratio=next/view.scale;
  view.x=x-(x-view.x)*ratio;view.y=y-(y-view.y)*ratio;view.scale=next;apply();host.project.workspaceView=view;host.persist()
 };
}

function openWindow(key,title,width=600,height=420,opts={}){if(state.windows.has(key)){const w=state.windows.get(key);if(!opts.refresh||!host.preserveLifecycle){if(host.preserveLifecycle){w.el.hidden=false;registerWorkspaceNode(w)}focusWindow(w);ensureWindowVisible(w)}return w}const retained=host.takeDetachedWindow?.(key);if(retained){const space=host.$('#workspace');let layer=space.querySelector('.workspace-window-layer');if(!layer){layer=document.createElement('div');layer.className='workspace-window-layer';(space.querySelector('.workspace-world-layer')||space).append(layer)}layer.append(retained.el);state.windows.set(key,retained);if(!retained.el.hidden)registerWorkspaceNode(retained);if(!opts.refresh){retained.el.hidden=false;registerWorkspaceNode(retained);focusWindow(retained);ensureWindowVisible(retained);saveLayouts()}return retained}const space=host.$('#workspace');if(!space)return;const n=state.windows.size;const initial=opts.initial;const rect=space.getBoundingClientRect();const x=opts.x??(initial?Math.min(750,Math.max(24,rect.width-28)):40+(n%5)*30),y=opts.y??(initial?115:85+(n%5)*22);const el=document.createElement('section');el.className='window';el.dataset.key=key;el.tabIndex=-1;el.setAttribute('aria-label',title);el.innerHTML=`<header class="window-title"><span class="caption"><span style="color:var(--accent)">◈</span><strong>${host.esc(title)}</strong></span><span class="row" style="gap:0"><button data-fold aria-label="창 접기">−</button><button data-close aria-label="창 닫기">×</button></span></header><div class="window-body"></div>${['n','ne','e','se','s','sw','w','nw'].map(edge=>`<div class="window-resize-handle resize-${edge}" data-resize="${edge}" role="button" tabindex="0" aria-label="${edge} 방향으로 창 크기 조절"></div>`).join('')}<div class="workspace-multi-drag-surface" aria-hidden="true"></div>`;let layer=space.querySelector('.workspace-window-layer');if(!layer){layer=document.createElement('div');layer.className='workspace-window-layer';(space.querySelector('.workspace-world-layer')||space).append(layer)}layer.append(el);const w={key,title,el,body:host.$('.window-body',el),x,y,width:Math.min(width,rect.width),height:Math.min(height,rect.height-20),folded:false,meta:opts.meta||{}};w.kind='window';if(host.preserveLifecycle){w.placed=true;const view=host.project.workspaceView;const screenX=Math.max(0,Math.min(w.x,rect.width-w.width*view.scale)),screenY=Math.max(38,Math.min(w.y,rect.height-w.height*view.scale));w.x=(screenX-view.x)/view.scale;w.y=(screenY-view.y)/view.scale;}w.position=()=>placeWindow(w);state.windows.set(key,w);registerWorkspaceNode(w);clampWindow(w);setWindowSelection([w]);focusWindow(w);host.$('[data-close]',el).onclick=()=>closeWindow(key);host.$('[data-fold]',el).onclick=()=>{w.folded=!w.folded;el.classList.toggle('folded',w.folded);host.$('[data-fold]',el).textContent=w.folded?'+':'−';clampWindow(w);saveLayouts()};el.addEventListener('pointerdown',e=>{if(e.target.closest('.window-title'))return;if(e.ctrlKey||e.metaKey||e.shiftKey)toggleWindowSelection(w);else if(!isWorkspaceNodeSelected(w.key))setWindowSelection([w]);focusWindow(w)});setupWindowDrag(w);host.$('.resize-se',el).onkeydown=e=>{if(e.key.startsWith('Arrow')){e.preventDefault();w.width+=e.key==='ArrowRight'?20:e.key==='ArrowLeft'?-20:0;w.height+=e.key==='ArrowDown'?20:e.key==='ArrowUp'?-20:0;clampWindow(w);saveLayouts()}};saveLayouts();return w}

function placeWindow(w){if(w.documentDocked)return;const v=host.project?.workspaceView||{x:0,y:0,scale:1},scale=w.placed?v.scale:1;Object.assign(w.el.style,{left:(w.placed?v.x+w.x*scale:w.x)+'px',top:(w.placed?v.y+w.y*scale:w.y)+'px',width:w.width+'px',height:w.height+'px',transform:w.placed?'scale('+scale+')':'',transformOrigin:'top left'});linkRuntime.schedule()}

function registerWorkspaceNode(node){if(node.documentDocked)return node;state.workspaceNodes.set(node.key,node);renderWorkspaceNodeSelection();linkRuntime.schedule();return node}

function unregisterWorkspaceNode(key){state.workspaceNodes.get(key)?.el.classList.remove('multi-selected','multi-drag-mode','active');state.workspaceNodes.delete(key);state.selectedWorkspaceNodeKeys.delete(key);renderWorkspaceNodeSelection();linkRuntime.schedule()}

function isWorkspaceNodeSelected(key){return state.selectedWorkspaceNodeKeys.has(key)}

function selectedWorkspaceNodes(){return [...state.selectedWorkspaceNodeKeys].map(key=>state.workspaceNodes.get(key)).filter(Boolean)}

function selectedWorkspaceWindows(){return selectedWorkspaceNodes().filter(node=>node.kind==='window')}

function renderWorkspaceNodeSelection(){
 const multiple=state.selectedWorkspaceNodeKeys.size>1;
 state.workspaceNodes.forEach(node=>{
  const selected=isWorkspaceNodeSelected(node.key);
  node.el.classList.toggle('multi-selected',selected);
  node.el.classList.toggle('multi-drag-mode',multiple&&selected);
  node.el.classList.toggle('active',selected&&!multiple);
 });
 if(multiple&&document.activeElement?.closest?.('.window,.workspace-decoration'))host.$('#workspace')?.focus({preventScroll:true});
}

function setWorkspaceNodeSelection(nodes){state.selectedWorkspaceNodeKeys.clear();nodes.forEach(node=>{if(state.workspaceNodes.get(node.key)===node)state.selectedWorkspaceNodeKeys.add(node.key)});renderWorkspaceNodeSelection()}

function toggleWorkspaceNodeSelection(node){const next=new Set(state.selectedWorkspaceNodeKeys);next.has(node.key)?next.delete(node.key):next.add(node.key);setWorkspaceNodeSelection([...next].map(key=>state.workspaceNodes.get(key)).filter(Boolean))}

function focusWorkspaceNode(node){node.el.style.zIndex=host.foregroundZ?.(node)??++state.z;if(!isWorkspaceNodeSelected(node.key))setWorkspaceNodeSelection([node]);else renderWorkspaceNodeSelection()}

function setWindowSelection(items){setWorkspaceNodeSelection(items)}

function toggleWindowSelection(w){toggleWorkspaceNodeSelection(w)}

function focusWindow(w){if(!w.documentDocked&&!w.el.hidden&&!w.overlay)registerWorkspaceNode(w);if(w.documentDocked){host.focusWindowDocument?.(w);return}host.revealWorkspaceForWindow?.(w);focusWorkspaceNode(w)}

function ensureWindowVisible(w){
 if(!host.preserveLifecycle||w.documentDocked||!w.placed||w.el.hidden||w.overlay)return;
 const canvas=host.$('#workspace'),bounds=canvas.getBoundingClientRect(),header=host.$('.window-title',w.el).getBoundingClientRect();
 if(header.top>=bounds.top+38&&header.bottom<=bounds.bottom&&header.left>=bounds.left&&header.right<=bounds.right)return;
 const view=host.project.workspaceView;
 // Reveal a reopened popup without moving the other retained windows offscreen.
 const x=Math.min(Math.max(12,view.x+w.x*view.scale),canvas.clientWidth-w.width*view.scale-12);
 const y=Math.max(46,Math.min(view.y+w.y*view.scale,canvas.clientHeight-57));
 w.x=(x-view.x)/view.scale;w.y=(y-view.y)/view.scale;placeWindow(w);saveLayouts();
}

function closeWindow(key){const w=state.windows.get(key);if(!w)return;state.cancelDrag?.();linkRuntime.remove([key]);if(w.documentDocked){host.closeWindowDocument?.(key);return}if(host.hideWindowOnClose?.(key)){w.el.hidden=true;unregisterWorkspaceNode(key);saveLayouts();return}host.detachWindow?.(w,'close');clearTimeout(w.helperBubbleTimer);host.referenceTooltipCleanup?.();w.el.remove();state.windows.delete(key);unregisterWorkspaceNode(key);if(key==='run'&&host.running){host.closeRun()}saveLayouts()}

function toggleWindow(key,fn){state.windows.has(key)?closeWindow(key):fn()}

function clampWindow(w){if(w.overlay||w.documentDocked)return;if(w.el.classList.contains('is-workspace-dragging')){placeWindow(w);return}const helper=w.key.startsWith('helper-');if(w.placed){w.width=Math.max(helper?150:260,w.width);w.height=Math.max(helper?190:172,w.height);placeWindow(w);return}const s=host.$('#workspace');if(!s)return;const width=s.clientWidth,height=s.clientHeight;w.width=Math.max(Math.min(helper?150:260,width),Math.min(w.width,width));w.height=Math.max(Math.min(helper?190:160,height),Math.min(w.height,height));w.x=Math.max(0,Math.min(w.x,width-w.width));w.y=Math.max(38,Math.min(w.y,Math.max(38,height-(w.folded?45:w.height))));placeWindow(w)}

function clampWindows(){state.windows.forEach(clampWindow)}

function trackWorkspaceDrag(e,handle,onMove,onEnd){
 const sx=e.clientX,sy=e.clientY;
 let moved=false,finished=false;
 handle.setPointerCapture(e.pointerId);
 const move=ev=>{
  if(ev.pointerId!==e.pointerId)return;
  if(!moved&&Math.hypot(ev.clientX-sx,ev.clientY-sy)<3)return;
  moved=true;onMove(ev,sx,sy);
 };
 const cancel=()=>end({pointerId:e.pointerId,type:'pointercancel'});
 const keydown=event=>{if(event.key==='Escape'){event.preventDefault();event.stopImmediatePropagation();cancel();}};
 const end=ev=>{
  if(finished||ev.pointerId!==e.pointerId)return;
  finished=true;document.removeEventListener('keydown',keydown,true);if(state.cancelDrag===cancel)state.cancelDrag=null;
  handle.removeEventListener('pointermove',move);
  handle.removeEventListener('pointerup',end);
  handle.removeEventListener('pointercancel',end);
  handle.removeEventListener('lostpointercapture',end);
  if(handle.hasPointerCapture(e.pointerId))handle.releasePointerCapture(e.pointerId);
  onEnd(ev,moved);
 };
 state.cancelDrag=cancel;document.addEventListener('keydown',keydown,true);
 handle.addEventListener('pointermove',move);
 handle.addEventListener('pointerup',end);
 handle.addEventListener('pointercancel',end);
 handle.addEventListener('lostpointercapture',end);
}

function beginWorkspaceNodeDrag(e,node,{edge='',onClick}={}){
 if(node.documentDocked)return;
 if((!edge&&e.target.closest('button,input,textarea,select,[contenteditable=true]'))||e.button!==0)return;
 state.cancelDrag?.();e.preventDefault();e.stopPropagation();
 if(!edge&&(e.ctrlKey||e.metaKey||e.shiftKey)){toggleWorkspaceNodeSelection(node);return}
 const wasSelected=isWorkspaceNodeSelected(node.key);
 if(!wasSelected)setWorkspaceNodeSelection([node]);
 const members=edge?[node]:selectedWorkspaceNodes(),starts=new Map(members.map(item=>[item,{x:item.x,y:item.y,width:item.width,height:item.height}]));
 members.filter(item=>item!==node).forEach(item=>item.el.style.zIndex=++state.z);
 focusWorkspaceNode(node);if(!edge&&state.selectedWorkspaceNodeKeys.size<2)node.el.focus({preventScroll:true});
 const companions=[];
 if(!edge){const moving=new Set(members);let changed=true;while(changed){changed=false;for(const group of [...moving].filter(item=>item.kind==='decoration'&&item.item.kind==='group'))for(const other of state.workspaceNodes.values())if(other.placed&&other!==group&&!moving.has(other)&&fullyInsideDecoration(other,group.item)){moving.add(other);changed=true;}for(const child of linkRuntime.descendants([...moving]))if(!moving.has(child)){moving.add(child);changed=true;}}for(const item of moving)if(!members.includes(item))companions.push(item);}
 const traveling=[...members,...companions];
 const companionStarts=new Map(companions.map(item=>[item,{x:item.x,y:item.y}]));
 const historyBefore=!edge?host.beforePrivateLayout?.():null;if(!edge&&host.beforePrivateLayout&&!historyBefore)return;
 const start=starts.get(node),handle=e.currentTarget;
 state.gesture={project:host.project,workspaceId:state.activeWorkspaceId,entries:traveling.map(item=>({key:item.key,itemId:item.item?.id,kind:item.kind,geometry:{...(starts.get(item)||companionStarts.get(item))}}))};
 trackWorkspaceDrag(e,handle,(ev,sx,sy)=>{
  const scale=node.placed?(host.project.workspaceView?.scale||1):1,dx=(ev.clientX-sx)/scale,dy=(ev.clientY-sy)/scale;
  if(edge){
   const minWidth=node.kind==='window'?260:node.item.kind==='note'?(typeof node.item.richText==='string'?240:160):180,minHeight=node.kind==='window'?(node.placed?172:160):node.item.kind==='note'?(typeof node.item.richText==='string'?180:100):130;
   let left=start.x,top=start.y,right=start.x+start.width,bottom=start.y+start.height;
   if(edge.includes('w'))left=Math.min(right-minWidth,start.x+dx);
   if(edge.includes('e'))right=Math.max(left+minWidth,start.x+start.width+dx);
   if(edge.includes('n'))top=Math.min(bottom-minHeight,start.y+dy);
   if(edge.includes('s'))bottom=Math.max(top+minHeight,start.y+start.height+dy);
   Object.assign(node,{x:left,y:top,width:right-left,height:bottom-top});if(node.kind==='window')clampWindow(node);else node.position();
  }else{
   for(const item of members){const initial=starts.get(item),itemScale=item.placed?(host.project.workspaceView?.scale||1):1;item.x=initial.x+(ev.clientX-sx)/itemScale;item.y=initial.y+(ev.clientY-sy)/itemScale;item.el.classList.add('is-workspace-dragging');item.position()}
   for(const item of companions){const initial=companionStarts.get(item),itemScale=item.placed?(host.project.workspaceView?.scale||1):1;item.x=initial.x+(ev.clientX-sx)/itemScale;item.y=initial.y+(ev.clientY-sy)/itemScale;item.position()}
   updateWorkspaceDropPreview(traveling.every(item=>item.kind==='window')?workspaceDropTargetAt(ev.clientX,ev.clientY):null,traveling);host.$('#workspace-tabs')?.classList.toggle('is-placement-target',!!host.windowDocumentDropAt?.(ev.clientX,ev.clientY)&&members.every(item=>item.kind==='window'));
  }
 },(ev,moved)=>{
  state.gesture=null;
  const target=moved&&!edge&&ev.type==='pointerup'&&traveling.every(item=>item.kind==='window')?workspaceDropTargetAt(ev.clientX,ev.clientY):null;
  updateWorkspaceDropPreview(null);host.$('#workspace-tabs')?.classList.remove('is-placement-target');
  const toTabs=moved&&!edge&&ev.type==='pointerup'&&members.every(item=>item.kind==='window')&&host.windowDocumentDropAt?.(ev.clientX,ev.clientY);
  if(ev.type!=='pointerup'||toTabs){
   members.forEach(item=>Object.assign(item,starts.get(item)));
   companions.forEach(item=>Object.assign(item,companionStarts.get(item)));
  }
  members.forEach(item=>{item.el.classList.remove('is-workspace-dragging');item.position()});
  companions.forEach(item=>item.position());
  if(moved&&ev.type==='pointerup'){if(toTabs){host.openWindowDocuments?.(members);saveLayouts();}else if(target){if(!moveWindowsToWorkspace(traveling,target.dataset.workspaceId,historyBefore)){members.forEach(item=>Object.assign(item,starts.get(item)));companions.forEach(item=>Object.assign(item,companionStarts.get(item)));traveling.forEach(item=>item.position());}}else{saveLayouts();if(!edge)host.recordPrivateLayout?.(historyBefore);}}
  else if(!moved&&ev.type==='pointerup')onClick?.(wasSelected);
 });
}

function setupWindowDrag(w){
 host.$('.window-title',w.el).onpointerdown=e=>beginWorkspaceNodeDrag(e,w);
 host.$('.workspace-multi-drag-surface',w.el).onpointerdown=e=>beginWorkspaceNodeDrag(e,w);
 host.$$('[data-resize]',w.el).forEach(el=>el.onpointerdown=e=>beginWorkspaceNodeDrag(e,w,{edge:el.dataset.resize}));
}

function setupWindowSelection(){
 const canvas=host.$('#workspace');canvas.tabIndex=0;
 canvas.addEventListener('selectstart',e=>{if(canvas.classList.contains('is-selecting-windows'))e.preventDefault()});
 canvas.addEventListener('pointerdown',e=>{
  if(e.button!==0||e.target.closest('.window,.bubble-dock,.workspace-tabs,.augment-overlay,.workspace-decoration,.tab-document'))return;
  e.preventDefault();
  canvas.classList.add('is-selecting-windows');
  globalThis.getSelection?.()?.removeAllRanges();
  const additive=e.ctrlKey||e.metaKey||e.shiftKey,previous=new Set(additive?selectedWorkspaceNodes():[]),rect=canvas.getBoundingClientRect(),startX=e.clientX-rect.left,startY=e.clientY-rect.top;
  let moved=false,finished=false,box=null;
  canvas.setPointerCapture(e.pointerId);
  const move=ev=>{
   if(ev.pointerId!==e.pointerId)return;
   const x=ev.clientX-rect.left,y=ev.clientY-rect.top;
   if(!moved&&Math.hypot(x-startX,y-startY)<3)return;
   moved=true;
   if(!box){box=document.createElement('div');box.className='workspace-selection-box';canvas.append(box)}
   const left=Math.min(startX,x),top=Math.min(startY,y),right=Math.max(startX,x),bottom=Math.max(startY,y);
   Object.assign(box.style,{left:left+'px',top:top+'px',width:right-left+'px',height:bottom-top+'px'});
   const next=new Set(previous);
   state.workspaceNodes.forEach(node=>{const r=node.el.getBoundingClientRect();if(r.right>rect.left+left&&r.left<rect.left+right&&r.bottom>rect.top+top&&r.top<rect.top+bottom)next.add(node)});
   setWorkspaceNodeSelection(next);
  };
  const end=ev=>{
   if(finished||ev.pointerId!==e.pointerId)return;
   finished=true;
   if(ev.type==='pointercancel'||ev.type==='lostpointercapture')setWorkspaceNodeSelection(previous);
   else if(!moved&&!additive)setWorkspaceNodeSelection([]);
   box?.remove();
   canvas.classList.remove('is-selecting-windows');
   canvas.removeEventListener('pointermove',move);canvas.removeEventListener('pointerup',end);canvas.removeEventListener('pointercancel',end);canvas.removeEventListener('lostpointercapture',end);
   if(canvas.hasPointerCapture(e.pointerId))canvas.releasePointerCapture(e.pointerId);if(ev.type==='pointerup')canvas.focus({preventScroll:true});
  };
  canvas.addEventListener('pointermove',move);canvas.addEventListener('pointerup',end);canvas.addEventListener('pointercancel',end);canvas.addEventListener('lostpointercapture',end);
 });
}

function snapWindow(w){const s=host.$('#workspace'),h=w.folded?45:w.height;const xs=[0,s.clientWidth-w.width],ys=[0,s.clientHeight-h];state.windows.forEach(other=>{if(other===w)return;const oh=other.folded?45:other.height;if(w.y<other.y+oh+16&&w.y+h>other.y-16)xs.push(other.x+other.width+8,other.x-w.width-8,other.x);if(w.x<other.x+other.width+16&&w.x+w.width>other.x-16)ys.push(other.y+oh+8,other.y-h-8,other.y)});const x=xs.find(x=>Math.abs(w.x-x)<14),y=ys.find(y=>Math.abs(w.y-y)<14);if(x!==undefined)w.x=x;if(y!==undefined)w.y=y}

function workspaceRecord(id=state.activeWorkspaceId){return id==='root'?host.project:host.project?.workspaces?.find(space=>space.id===id)}

function workspaceItems(){const owner=workspaceRecord();if(!owner)return [];const key=state.activeWorkspaceId==='root'?'workspaceItems':'items';return owner[key]??=[]}

function decorationNodeKey(id){return 'decoration:'+id}

function windowLayout(w){return {key:w.key,x:w.x,y:w.y,width:w.width,height:w.height,folded:w.folded,placed:!!w.placed,meta:host.layoutMetadata?host.layoutMetadata(w):structuredClone(w.meta||{}),...(host.preserveLifecycle?{hidden:w.el.hidden}: {})}}

function saveLayouts(){if(host.isRestoring)return;if(host.page!=='work'||!host.project)return;const owner=workspaceRecord();if(!owner)return;owner.layout=[...state.windows.values()].filter(w=>w.key!=='build-result'&&!w.documentDocked&&(!host.preserveLifecycle||!w.overlay)).map(windowLayout);if(state.activeWorkspaceId==='root')host.project.rootWorkspaceView={...host.project.workspaceView};else owner.view={...host.project.workspaceView};host.persist()}

function workspaceDropTargetAt(x,y){return host.$$('.workspace-portal,.workspace-parent-node').find(target=>{const rect=target.getBoundingClientRect();return x>=rect.left&&x<=rect.right&&y>=rect.top&&y<=rect.bottom})}

function updateWorkspaceDropPreview(target,members=[]){
 host.$$('.workspace-drop-target').forEach(el=>{if(el!==target)el.classList.remove('workspace-drop-target')});
 const hidden=new Set(target?members.map(w=>w.el):[]);
 host.$$('.window.is-drop-preview').forEach(el=>{if(!hidden.has(el))el.classList.remove('is-drop-preview')});
 if(!target)return;
 target.classList.add('workspace-drop-target');
 const hint=host.$('.workspace-drop-hint',target);if(hint)hint.textContent='여기에 '+(members.length||1)+'개 창 넣기';
 members.forEach(w=>w.el.classList.add('is-drop-preview'));
}

function moveWindowsToWorkspace(members,targetId,historyBefore=null){
 members=linkRuntime.descendants(members);if(!members.length||members.some(w=>w.kind!=='window'||w.documentDocked||w.overlay||state.windows.get(w.key)!==w))return false;
 const target=workspaceRecord(targetId);if(!target||targetId===state.activeWorkspaceId)return false;target.layout??=[];
 if(members.some(w=>target.layout.some(item=>item.key===w.key))){host.toast('대상 작업 공간에 같은 private 창이 있어 이동하지 않았습니다.');return false;}
 const keys=new Set(members.map(w=>w.key)),edges=linkRuntime.rows().filter(edge=>keys.has(edge.parent)&&keys.has(edge.child));if((target.links?.length||0)+edges.length>255){host.toast('대상 Workspace의 연결 한도를 넘어 이동하지 않았습니다.');return false;}
 const before=historyBefore||host.beforePrivateLayout?.();if(host.beforePrivateLayout&&!before)return false;
 const base=target.layout.length,left=Math.min(...members.map(w=>w.x)),top=Math.min(...members.map(w=>w.y)),moved=members.map(w=>({...windowLayout(w),x:70+base*34+w.x-left,y:90+base*30+w.y-top,placed:true}));
 linkRuntime.remove([...keys]);target.links??=[];target.links.push(...edges);
 members.forEach(w=>{host.detachWindow?.(w,'move');clearTimeout(w.helperBubbleTimer);w.el.remove();state.windows.delete(w.key);unregisterWorkspaceNode(w.key);});setWindowSelection([]);saveLayouts();target.layout.push(...moved);host.persist();host.recordPrivateLayout?.(before);renderWorkspaceDecorations();renderWorkspaceTabs();host.toast(members.length+'개 창을 '+target.name+'(으)로 옮겼어요.');return true;
}

function renderWorkspaceTabs(){const tabs=host.$('#workspace-tabs');if(!tabs)return;host.beforeRenderTabs?.(tabs);tabs.replaceChildren();const add=(id,label)=>{const button=document.createElement('button');button.type='button';button.className='workspace-home-tab'+(id===state.activeWorkspaceId?' is-current':'');button.id=id==='root'?'workspace-home-tab':'workspace-tab-'+id;button.setAttribute('role','tab');button.setAttribute('aria-selected',String(id===state.activeWorkspaceId));button.textContent=label;button.onclick=()=>{const documentWasOpen=host.activateWorkspaceView?.();if(id===state.activeWorkspaceId){if(!documentWasOpen)host.$('#workspace').resetWorkspaceView?.();return}switchWorkspace(id)};tabs.append(button);if(id!=='root'&&host.preserveLifecycle){const close=document.createElement('button');close.type='button';close.className='workspace-tab-close';close.setAttribute('aria-label',label+' 탭 닫기');close.textContent='×';close.onclick=()=>{if(state.activeWorkspaceId===id)returnToParentWorkspace();state.visitedWorkspaceTabs=state.visitedWorkspaceTabs.filter(item=>item!==id);renderWorkspaceTabs();host.persist()};tabs.append(close)}};add('root','Workspace');state.visitedWorkspaceTabs.filter(id=>id!=='root').forEach(id=>{const space=workspaceRecord(id);if(space)add(id,space.name)});host.renderDocumentTabs?.(tabs);}

function switchWorkspace(id){if(host.canNavigate&&!host.canNavigate()){host.toast('편집창을 복원하고 있습니다. 잠시 후 이동하세요.');return;}const target=workspaceRecord(id);if(!target||id===state.activeWorkspaceId)return;cancelInteractions();saveLayouts();const saved=(target.layout||[]).map(item=>structuredClone(item));state.windows.forEach(w=>{if(w.documentDocked)return;host.detachWindow?.(w,'navigate');clearTimeout(w.helperBubbleTimer);w.el.remove();state.windows.delete(w.key)});state.workspaceNodes.clear();setWorkspaceNodeSelection([]);state.activeWorkspaceId=id;if(!state.visitedWorkspaceTabs.includes(id))state.visitedWorkspaceTabs.push(id);Object.assign(host.project.workspaceView,(id==='root'?host.project.rootWorkspaceView:target.view)||{x:0,y:0,scale:1});host.$('#workspace').updateWorkspaceView?.();renderWorkspaceDecorations();renderWorkspaceTabs();saved.forEach(restoreWindow);host.afterSwitchWorkspace?.(id);saveLayouts();requestAnimationFrame(()=>clampWindows())}

function returnToParentWorkspace(){
 if(state.activeWorkspaceId==='root')return;
 const childId=state.activeWorkspaceId,parentId=workspaceRecord()?.parentId||'root';
 switchWorkspace(parentId);
 const portal=workspaceItems().find(item=>item.kind==='portal'&&item.id===childId);
 if(portal){workspaceCenterOn(portal.x+portal.width/2,portal.y+portal.height/2);saveLayouts()}
}

function positionWorkspaceDecorations(){if(!host.project)return;const view=host.project.workspaceView||{x:0,y:0,scale:1},items=workspaceItems();host.$$('.workspace-decoration').forEach(el=>{const item=items.find(entry=>entry.id===el.dataset.workspaceItem);if(!item)return;Object.assign(el.style,{left:(view.x+item.x*view.scale)+'px',top:(view.y+item.y*view.scale)+'px',width:item.width+'px',height:item.height+'px',transform:'scale('+view.scale+')',transformOrigin:'top left'})});const parent=host.$('.workspace-parent-node');if(parent)Object.assign(parent.style,{left:(view.x+24*view.scale)+'px',top:(view.y+72*view.scale)+'px',transform:'scale('+view.scale+')',transformOrigin:'top left'})}

function selectWorkspaceDecoration(id){const node=state.workspaceNodes.get(decorationNodeKey(id));if(node){setWorkspaceNodeSelection([node]);focusWorkspaceNode(node)}}

function decorationName(item){return item.kind==='portal'?(workspaceRecord(item.id)?.name||'Workspace'):(item.name||({note:'메모',group:'그룹'}[item.kind]))}

function renameWorkspaceDecoration(item){
 const el=host.$$('.workspace-decoration').find(node=>node.dataset.workspaceItem===item.id),label=el?.querySelector('.workspace-item-name');
 if(!label||el.querySelector('.workspace-name-editor'))return;
 selectWorkspaceDecoration(item.id);
 const input=document.createElement('input');input.className='workspace-name-editor';input.setAttribute('aria-label','이름 변경');input.maxLength=50;input.value=decorationName(item);
 label.replaceWith(input);input.focus();input.select();
 let done=false;
 const finish=save=>{
  if(done)return;done=true;
  if(save){const name=input.value.trim();if(name){if(item.kind==='portal'){workspaceRecord(item.id).name=name;const tab=host.$('#workspace-tab-'+item.id);if(tab)tab.textContent=name}else item.name=name;host.noteChanged?.(item,null);host.persist()}}
  label.textContent=decorationName(item);
  input.onblur=null;input.replaceWith(label);
 };
 input.onkeydown=e=>{if(e.key==='Enter'){e.preventDefault();finish(true)}else if(e.key==='Escape'){e.preventDefault();finish(false)}e.stopPropagation()};
 input.onblur=()=>finish(true);
}

function deleteWorkspaceNodes(nodes){
 const project=host.project,workspace=state.activeWorkspaceId;
 const current=nodes.filter(node=>(node.kind==='window'||node.kind==='decoration')&&state.workspaceNodes.get(node.key)===node);
 if(!current.length)return;
 const portals=current.filter(node=>node.kind==='decoration'&&node.item.kind==='portal');
 const perform=()=>{
  if(host.project!==project||state.activeWorkspaceId!==workspace||current.some(node=>state.workspaceNodes.get(node.key)!==node)){host.toast('작업 공간이 바뀌어 삭제를 중단했습니다.');return;}
  cancelInteractions();const before=host.beforePrivateDelete?.();if(host.beforePrivateDelete&&!before)return;
  linkRuntime.remove(current.map(node=>node.key));
  const removedWorkspaceIds=new Set(portals.map(node=>node.item.id));
  let changed=true;
  while(changed){changed=false;for(const child of host.project.workspaces||[])if(removedWorkspaceIds.has(child.parentId)&&!removedWorkspaceIds.has(child.id)){removedWorkspaceIds.add(child.id);changed=true}}
  const removedItemIds=new Set(current.filter(node=>node.kind==='decoration').map(node=>node.item.id));
  removedWorkspaceIds.forEach(id=>removedItemIds.add(id));
  const items=workspaceItems();for(let i=items.length-1;i>=0;i--)if(removedItemIds.has(items[i].id))items.splice(i,1);
  if(removedWorkspaceIds.size){
   host.beforeDeleteWorkspaces?.(removedWorkspaceIds);
   host.project.workspaces=host.project.workspaces.filter(child=>!removedWorkspaceIds.has(child.id));
   host.project.workspaceItems=host.project.workspaceItems.filter(item=>!removedItemIds.has(item.id));
   for(const child of host.project.workspaces)child.items=(child.items||[]).filter(item=>!removedItemIds.has(item.id));
   state.visitedWorkspaceTabs=state.visitedWorkspaceTabs.filter(id=>!removedWorkspaceIds.has(id));
  }
  setWorkspaceNodeSelection([]);
  current.filter(node=>node.kind==='window').forEach(node=>closeWindow(node.key));
  host.pruneNoteDocuments?.();renderWorkspaceDecorations();renderWorkspaceTabs();saveLayouts();host.recordPrivateDelete?.(before);
 };
 if(!portals.length){perform();return}
 const single=portals.length===1&&current.length===1,space=workspaceRecord(portals[0].item.id);
 host.modal(single?'하위 Workspace 삭제':'선택한 항목 삭제',`<p>${single?`<strong>${host.esc(space?.name||'하위 Workspace')}</strong>을(를) 삭제할까요?`:`선택한 ${current.length}개 항목을 삭제할까요?`}</p><p class="muted">${single?'이 Workspace':'선택한 하위 Workspace'} 안의 창과 하위 Workspace도 함께 삭제됩니다.</p>${host.preserveLifecycle?'<p class="muted">작업 공간 배치만 제거합니다. 실제 객체와 프로젝트 파일은 삭제하지 않으며 편집 입력은 보존됩니다.</p>':''}<div class="row" style="justify-content:flex-end"><button type="button" data-cancel>취소</button><button type="button" class="primary" data-confirm>삭제</button></div>`,(root,close)=>{
  host.$('[data-cancel]',root).onclick=close;
  host.$('[data-confirm]',root).onclick=()=>{close();perform()};
 });
}

function removeWorkspaceDecoration(item){const node=state.workspaceNodes.get(decorationNodeKey(item.id));if(node)deleteWorkspaceNodes([node])}

function confirmRemoveChildWorkspace(item){const node=state.workspaceNodes.get(decorationNodeKey(item.id));if(node)deleteWorkspaceNodes([node])}

function fullyInsideDecoration(entry,group){
 const height=entry.folded?45:entry.height;
 return entry.x>=group.x&&entry.y>=group.y&&entry.x+entry.width<=group.x+group.width&&entry.y+height<=group.y+group.height;
}

function renderWorkspaceDecorations(){
 const canvas=host.$('#workspace');if(!canvas||!host.project)return;
 let layer=host.$('.workspace-decoration-layer',canvas);
 if(!layer){layer=document.createElement('div');layer.className='workspace-decoration-layer';(canvas.querySelector('.workspace-world-layer')||canvas).append(layer)}
 layer.replaceChildren();
 for(const [key,node] of state.workspaceNodes)if(node.kind==='decoration')state.workspaceNodes.delete(key);
 for(const item of workspaceItems()){
  if(item.kind==='portal'){item.width=185;item.height=46}
  const el=document.createElement('article');el.className='workspace-decoration workspace-'+item.kind;
  el.dataset.workspaceItem=item.id;if(item.kind==='portal')el.dataset.workspaceId=item.id;
  el.tabIndex=0;

  const title=host.esc(decorationName(item));
  const resizeHandles=['n','ne','e','se','s','sw','w','nw'].map(edge=>'<span class="window-resize-handle resize-'+edge+'" data-decoration-resize="'+edge+'" role="button" tabindex="0" aria-label="'+edge+' 방향으로 '+(item.kind==='note'?'메모':'그룹')+' 크기 조절"></span>').join('');
  if(item.kind==='note')el.innerHTML='<header class="workspace-item-handle"><strong class="workspace-item-name">'+title+'</strong>'+(host.preserveLifecycle?'<button type="button" data-note-format aria-label="메모 서식 편집" title="메모 서식 편집">Aa</button>':'')+'<button type="button" data-remove aria-label="메모 삭제">×</button></header>'+(host.preserveLifecycle&&typeof item.richText==='string'?noteMarkup(item):'<textarea aria-label="메모 내용" placeholder="메모를 남겨보세요…">'+host.esc(item.text||'')+'</textarea>')+resizeHandles;
  else if(item.kind==='group')el.innerHTML='<header class="workspace-item-handle"><strong class="workspace-item-name">'+title+'</strong><button type="button" data-remove aria-label="그룹 삭제">×</button></header>'+resizeHandles;
  else if(item.kind==='portal')el.innerHTML='<header class="workspace-item-handle"><strong class="workspace-item-name">'+title+'</strong><button type="button" data-remove aria-label="하위 Workspace 삭제">×</button></header><span class="workspace-drop-hint" aria-live="polite"></span>';
  layer.append(el);
  el.insertAdjacentHTML('beforeend','<div class="workspace-multi-drag-surface" aria-hidden="true"></div>');
  const node=registerWorkspaceNode({key:decorationNodeKey(item.id),kind:'decoration',item,el,placed:true,get x(){return item.x},set x(v){item.x=v},get y(){return item.y},set y(v){item.y=v},get width(){return item.width},set width(v){item.width=v},get height(){return item.height},set height(v){item.height=v},position:positionWorkspaceDecorations});
  el.addEventListener('focus',()=>{if(!isWorkspaceNodeSelected(node.key))setWorkspaceNodeSelection([node])});
  el.addEventListener('pointerdown',e=>{if(e.target.closest('.workspace-item-handle,[data-decoration-resize]'))return;if(e.ctrlKey||e.metaKey||e.shiftKey)toggleWorkspaceNodeSelection(node);else if(!isWorkspaceNodeSelected(node.key))setWorkspaceNodeSelection([node]);focusWorkspaceNode(node)});
  el.addEventListener('keydown',e=>{if(e.key==='F2'){e.preventDefault();renameWorkspaceDecoration(item)}else if(item.kind==='portal'&&e.key==='Enter'&&!e.target.matches('input,button')){e.preventDefault();switchWorkspace(item.id)}});
  const name=host.$('.workspace-item-name',el);
  let renameTimer,ignoreNameClick=false;
  const activateName=wasSelected=>{
   el.focus({preventScroll:true});
   if(!wasSelected){selectWorkspaceDecoration(item.id);return}
   if(item.kind==='note'&&host.openNoteDocument){clearTimeout(renameTimer);renameTimer=setTimeout(()=>{if(el.isConnected&&!el.closest('[hidden]')&&isWorkspaceNodeSelected(node.key))renameWorkspaceDecoration(item)},260);return}
   if(item.kind!=='portal'){renameWorkspaceDecoration(item);return}
   clearTimeout(renameTimer);
   renameTimer=setTimeout(()=>{if(el.isConnected&&isWorkspaceNodeSelected(node.key))renameWorkspaceDecoration(item)},260);
  };
  name.onclick=e=>{e.stopPropagation();if(ignoreNameClick){ignoreNameClick=false;return}activateName(isWorkspaceNodeSelected(node.key))};
  name.ondblclick=e=>{e.stopPropagation();clearTimeout(renameTimer);if(item.kind==='portal')switchWorkspace(item.id);else if(item.kind==='note')host.openNoteDocument?.(item)};
  if(item.kind==='portal')el.ondblclick=e=>{if(e.target.closest('button,input'))return;clearTimeout(renameTimer);switchWorkspace(item.id)};
  const handle=host.$('.workspace-item-handle',el);
  if(host.preserveLifecycle&&item.kind==='note')handle.ondblclick=event=>{if(!event.target.closest('button,input,.workspace-item-name')){clearTimeout(renameTimer);host.openNoteDocument?.(item);}};
  handle.onpointerdown=e=>{
   if(e.button!==0||e.target.closest('button,input'))return;
   const onName=!!e.target.closest('.workspace-item-name');
   beginWorkspaceNodeDrag(e,node,{onClick:wasSelected=>{
    if(onName){ignoreNameClick=true;activateName(wasSelected);setTimeout(()=>{ignoreNameClick=false},0)}
   }});
  };
  host.$('.workspace-multi-drag-surface',el)?.addEventListener('pointerdown',e=>beginWorkspaceNodeDrag(e,node));
  if(host.preserveLifecycle)applyNoteTitle(el,item);
  if(item.kind==='note'){
   if(host.preserveLifecycle&&typeof item.richText==='string'){el.noteCanonicalHtml=noteHtml(item);el.noteBinding=bindNoteEditor(el,item,()=>{el.noteCanonicalHtml=noteHtml(item);host.noteChanged?.(item,el.querySelector('[data-note-editor]'));host.persist();},()=>workspaceItems().includes(item));}else host.$('textarea',el).oninput=e=>{item.text=e.target.value;host.noteChanged?.(item,e.target);host.persist()};
   host.$('[data-note-format]',el)?.addEventListener('click',event=>{event.stopPropagation();editWorkspaceNote(item);});
  }
  if(item.kind==='group'||item.kind==='note'){
   const minWidth=item.kind==='note'?(typeof item.richText==='string'?240:160):180,minHeight=item.kind==='note'?(typeof item.richText==='string'?180:100):130;
   host.$$('[data-decoration-resize]',el).forEach(resize=>{
    const edge=resize.dataset.decorationResize;
    resize.onpointerdown=e=>beginWorkspaceNodeDrag(e,node,{edge});
    if(edge==='se')resize.onkeydown=e=>{if(!e.key.startsWith('Arrow'))return;e.preventDefault();item.width=Math.max(minWidth,item.width+(e.key==='ArrowRight'?20:e.key==='ArrowLeft'?-20:0));item.height=Math.max(minHeight,item.height+(e.key==='ArrowDown'?20:e.key==='ArrowUp'?-20:0));positionWorkspaceDecorations();saveLayouts()};
   });
  }
  const remove=host.$('[data-remove]',el);
  if(remove)remove.onclick=e=>{e.stopPropagation();item.kind==='portal'?confirmRemoveChildWorkspace(item):removeWorkspaceDecoration(item)};
 }
 if(state.activeWorkspaceId!=='root'){
  const parentId=workspaceRecord()?.parentId||'root',parentName=parentId==='root'?'Workspace':workspaceRecord(parentId)?.name||'상위 Workspace';
  const node=document.createElement('div');node.className='workspace-parent-node';node.dataset.workspaceId=parentId;
  node.tabIndex=0;node.setAttribute('role','button');node.setAttribute('aria-label',parentName+'에 창 넣기 또는 두 번 클릭해 이동');
  node.title='창을 끌어 놓거나 두 번 클릭해 '+parentName+'로 이동';
  node.innerHTML='<span class="workspace-parent-symbol" aria-hidden="true">↖</span><small>상위</small><span class="workspace-drop-hint" aria-live="polite"></span>';
  node.ondblclick=e=>{e.stopPropagation();returnToParentWorkspace()};
  node.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();returnToParentWorkspace()}};
  layer.append(node);
 }
 positionWorkspaceDecorations();renderWorkspaceNodeSelection();host.refreshNoteDocuments?.();linkRuntime.schedule();
}

function createWorkspaceDecoration(kind,x,y){
 const point=workspaceWorldPoint(x,y),sizes={note:[230,165],group:[340,245],portal:[185,46]},[width,height]=sizes[kind],item={id:host.uid(),kind,x:point.x-width/2,y:point.y-height/2,width,height};
 if(kind==='note'){item.name='메모';item.text=''}
 if(kind==='group')item.name='그룹';
 if(kind==='portal'){host.project.workspaces??=[];host.project.workspaces.push({id:item.id,name:'Workspace '+(host.project.workspaces.length+1),parentId:state.activeWorkspaceId,layout:[],view:{x:0,y:0,scale:1},items:[]})}
 workspaceItems().push(item);renderWorkspaceDecorations();selectWorkspaceDecoration(item.id);saveLayouts();
 if(kind==='note')host.$('.workspace-note:last-child textarea')?.focus();
 return item;
}

function editWorkspaceNote(item){
 if(!workspaceItems().includes(item)||item.kind!=='note')return;
 if(typeof item.richText!=='string'){item.richText=noteHtml(item);item.width=Math.max(item.width,330);item.height=Math.max(item.height,260);renderWorkspaceDecorations();saveLayouts();}
 host.$$('.workspace-note').find(el=>el.dataset.workspaceItem===item.id)?.querySelector('[data-note-editor]')?.focus();
}
function editWorkspaceTitle(item,owns=()=>workspaceItems().includes(item),acrossWorkspaces=false){
 const scope=host.project,workspace=state.activeWorkspaceId,current=item.titleStyle,size=Number.isFinite(current?.size)?Math.min(72,Math.max(8,current.size)):13,color=/^#[0-9a-f]{6}$/i.test(current?.color||'')?current.color:'#e9d9b9';
 host.modal('제목 서식','<form class="stack" data-note-title-form><label>제목 크기<input type="number" min="8" max="72" step="1" data-title-size value="'+size+'"></label><label>제목 색상<input type="color" data-title-color value="'+color+'"></label><strong data-title-preview></strong><div class="actions"><button type="submit" data-title-apply>적용</button><button type="button" data-title-clear>직접 서식 지우기</button></div><p>Workspace 배치의 제목에만 적용합니다.</p></form>',(root,close)=>{
  const sizeInput=root.querySelector('[data-title-size]'),colorInput=root.querySelector('[data-title-color]'),preview=root.querySelector('[data-title-preview]');preview.textContent=decorationName(item);
  const draw=()=>{preview.style.fontSize=Math.min(72,Math.max(8,Number(sizeInput.value)||13))+'px';preview.style.color=colorInput.value;};sizeInput.oninput=colorInput.oninput=draw;draw();
  const valid=()=>host.project===scope&&(acrossWorkspaces||state.activeWorkspaceId===workspace)&&owns();
  root.querySelector('[data-title-clear]').onclick=()=>{if(!valid()){host.toast('제목의 작업 공간이 바뀌었습니다.');return;}delete item.titleStyle;host.$$('.workspace-decoration').filter(el=>el.dataset.workspaceItem===item.id).forEach(el=>applyNoteTitle(el,item));host.noteChanged?.(item,null);host.persist();close();};
  root.querySelector('form').onsubmit=event=>{event.preventDefault();if(!valid()){host.toast('제목의 작업 공간이 바뀌었습니다.');return;}const next=Number(sizeInput.value);if(!Number.isFinite(next)||next<8||next>72)return;item.titleStyle={size:next,color:colorInput.value};item.height=Math.max(item.height,next*1.25+(item.kind==='note'?150:50));host.$$('.workspace-decoration').filter(el=>el.dataset.workspaceItem===item.id).forEach(el=>applyNoteTitle(el,item));positionWorkspaceDecorations();host.noteChanged?.(item,null);host.persist();close();};
 });
}

function showWorkspaceContextMenu(x,y,target){
 const itemEl=target?.closest?.('.workspace-decoration');
 if(itemEl){
  const item=workspaceItems().find(entry=>entry.id===itemEl.dataset.workspaceItem);
  if(item){
   selectWorkspaceDecoration(item.id);
   const options=[];
   if(item.kind==='portal')options.push(['작업 공간 열기',()=>switchWorkspace(item.id)]);
   if(item.kind==='note'){options.push(['메모 편집',()=>itemEl.querySelector('[data-note-editor],textarea')?.focus()]);if(host.preserveLifecycle)options.push(['탭으로 열기',()=>host.openNoteDocument?.(item)],['메모 서식 편집',()=>editWorkspaceNote(item)]);}
   if(host.preserveLifecycle)options.push(['제목 서식',()=>editWorkspaceTitle(item)]);
   options.push(['이름 변경',()=>renameWorkspaceDecoration(item)]);
   options.push([item.kind==='portal'?'하위 Workspace 삭제':item.kind==='group'?'그룹 삭제':'메모 삭제',()=>itemEl.querySelector('[data-remove]')?.click()]);
   host.contextMenu(x,y,options);return;
  }
 }
 showWorkspaceSearchMenu(x,y);
}

function restoreWindow(l){if(host.restoreActualWindow){const w=host.restoreActualWindow(l);if(w){Object.assign(w,{x:l.x,y:l.y,width:l.width,height:l.height,folded:!!l.folded,placed:!!l.placed});w.el.hidden=!!l.hidden;w.el.classList.toggle('folded',w.folded);if(w.el.hidden)unregisterWorkspaceNode(w.key);else registerWorkspaceNode(w);clampWindow(w)}return w}let w;if(l.key==='browser'||l.key.startsWith('browser:')||l.key.startsWith('browser-tree:'))w=host.openBrowser(l.meta?.group||(l.key.startsWith('browser:')||l.key.startsWith('browser-tree:')?l.key.split(':')[1]:'concept'),null,true,l.key,l.meta?.rootFolder||null);else if(l.key.startsWith('object:'))w=host.openEditor(l.key.slice(7));else if(l.key==='map')w=host.openMap();else if(l.key==='schema')w=host.openSchema();else if(l.key==='issues')w=host.openIssues();else if(l.key==='run')w=host.openRunViewport();else if(l.key==='augment')w=host.openAugment();else if(l.key==='custom')w=host.openCustom();else if(l.key==='packs')w=host.openPacks();else if(l.key.startsWith('yogi:'))w=host.openYogi(l.key.slice(5));else if(l.key.startsWith('helper-')){host.helperChat(l.key.slice(7));w=state.windows.get(l.key)}if(w){Object.assign(w,{meta:l.meta||w.meta,x:l.x,y:l.y,width:l.key.startsWith('helper-')?150:l.width,height:l.key.startsWith('helper-')?210:l.height,folded:l.folded,placed:!!l.placed});w.el.classList.toggle('folded',!!l.folded);clampWindow(w);w.el.classList.toggle('workspace-main-window',!!w.meta.mainWorkspace);if(isBrowserWindowKey(w.key))host.renderBrowser(w)}}

function isBrowserWindowKey(key){return key==='browser'||key.startsWith('browser:')||key.startsWith('browser-tree:')}

function isProjectBrowserKey(key){return key==='browser'}

function browserInstanceKey(kind,group='concept',folder=null){const id=host.uid();return kind==='tree'?'browser-tree:'+group+':'+folder+':'+id:'browser:'+group+':'+id}

function browserInitialSize(key){return isProjectBrowserKey(key)?{width:678,height:458}:{width:502,height:348}}

function browserPlacementSize(key){const existing=state.windows.get(key);return existing?{width:existing.width,height:existing.height}:browserInitialSize(key)}

function startWorkspaceDrag(e,payload){endWorkspaceDrag();state.workspaceDragPayload=payload;state.workspaceDragPlacement={last:null,spot:null,preview:null};e.dataTransfer.setData('application/x-confectory-placement',JSON.stringify(payload));e.dataTransfer.effectAllowed='copy';state.workspaceDragGhost=document.createElement('canvas');state.workspaceDragGhost.width=state.workspaceDragGhost.height=1;Object.assign(state.workspaceDragGhost.style,{position:'fixed',left:'-100px',top:'-100px',pointerEvents:'none'});document.body.append(state.workspaceDragGhost);e.dataTransfer.setDragImage(state.workspaceDragGhost,0,0)}

function endWorkspaceDrag(){state.workspaceDragPlacement?.preview?.remove();updateWorkspaceDropPreview(null);state.workspaceDragPayload=null;state.workspaceDragPlacement=null;state.workspaceDragGhost?.remove();state.workspaceDragGhost=null}

function startObjectEditorDrag(e,o){startWorkspaceDrag(e,{kind:'object',key:'object:'+o.id,id:o.id,title:o.name+' · 데이터',width:405,height:475});e.dataTransfer.setData('application/x-semantic-object',o.id);e.dataTransfer.effectAllowed='copyMove'}

function workspaceDragSize(payload){const existing=state.windows.get(payload.key);return existing?{width:existing.width,height:workspaceWindowHeight(existing)}:{width:payload.width,height:payload.height}}

function workspaceDropSpot(e,payload){const pointer=workspaceWorldPoint(e.clientX,e.clientY),size=workspaceDragSize(payload);return{x:pointer.x-size.width/2,y:pointer.y-size.height/2}}

function setupHelperWorkspaceDrags(){host.$$('.home-side [data-helper]').forEach(tile=>{tile.draggable=true;tile.ondragstart=e=>{const id=tile.dataset.helper,h=host.helpers.find(item=>item.id===id);if(!h){e.preventDefault();return}startWorkspaceDrag(e,{kind:'helper',key:'helper-'+id,id,title:h.name+' 캐릭터',width:150,height:210})};tile.ondragend=endWorkspaceDrag})}

function setupBrowserDockDrag(){
 const dock=host.$('#nav'),canvas=host.$('#workspace');dock.draggable=true;dock.title='클릭하여 열기 · 드래그하여 Workspace에 배치';
 const payloadFor=e=>e.dataTransfer?.types.includes('application/x-confectory-placement')?state.workspaceDragPayload:null;
 canvas.addEventListener('dragover',e=>{
  const payload=payloadFor(e);if(!payload||!state.workspaceDragPlacement)return;
  e.preventDefault();
  const size=workspaceDragSize(payload),pointer=workspaceWorldPoint(e.clientX,e.clientY),desired={x:pointer.x-size.width/2,y:pointer.y-size.height/2};
  const spot=workspaceDropSpot(e,payload);state.workspaceDragPlacement.spot=spot;
  const target=workspaceDropTargetAt(e.clientX,e.clientY);
  updateWorkspaceDropPreview(target);
  if(target){state.workspaceDragPlacement.preview?.remove();state.workspaceDragPlacement.preview=null}
  else state.workspaceDragPlacement.preview=workspaceShowPlacement(state.workspaceDragPlacement.preview,spot,desired,size.width,size.height,payload.title);
  e.dataTransfer.dropEffect=spot?'copy':'none';
 });
 canvas.addEventListener('drop',e=>{
  const payload=payloadFor(e);if(!payload)return;e.preventDefault();
  const target=workspaceDropTargetAt(e.clientX,e.clientY),spot=workspaceDropSpot(e,payload),size=workspaceDragSize(payload);
  endWorkspaceDrag();
  if(!spot)return;
  let w;const center={x:e.clientX,y:e.clientY};
  if(payload.kind==='browser')w=host.openBrowser('concept',center,false,'browser',null,spot);
  else if(payload.kind==='tab')w=host.openBrowser(payload.group,center,false,payload.key,null,spot);
  else if(payload.kind==='tree')w=host.openBrowser(payload.group,center,false,payload.key,payload.parentId,spot);
  else if(payload.kind==='helper'){host.helperChat(payload.id,false);w=state.windows.get(payload.key)}
  else if(payload.kind==='issues')w=host.openIssues();
  else if(payload.kind==='run')w=host.openRunViewport();
  else if(payload.kind==='object')w=host.openEditor(payload.id);
  if(w){w.x=spot.x;w.y=spot.y;w.width=size.width;if(!w.folded)w.height=size.height;w.placed=true;placeWindow(w);if(target)moveWindowsToWorkspace([w],target.dataset.workspaceId);else saveLayouts()}
 });
 canvas.addEventListener('dragleave',e=>{if(!canvas.contains(e.relatedTarget)&&state.workspaceDragPlacement){state.workspaceDragPlacement.preview?.remove();state.workspaceDragPlacement.preview=null;state.workspaceDragPlacement.spot=null;state.workspaceDragPlacement.last=null;updateWorkspaceDropPreview(null)}});
 dock.ondragstart=e=>startWorkspaceDrag(e,{kind:'browser',key:'browser',title:'프로젝트 브라우저',width:678,height:458});dock.ondragend=endWorkspaceDrag;
 [['issues','issues','신문고',414,436],['run','run','실행창',502,348]].forEach(([id,kind,title,width,height])=>{const button=host.$('#'+id);if(!button)return;button.draggable=true;button.ondragstart=e=>startWorkspaceDrag(e,{kind,key:kind,title,width,height});button.ondragend=endWorkspaceDrag});
}

function workspaceSnapStart(n){return Math.round((n-state.workspaceDot-state.workspaceInset)/state.workspaceGrid)*state.workspaceGrid+state.workspaceDot+state.workspaceInset}

function workspaceSnapEnd(n){return Math.round((n-state.workspaceDot+state.workspaceInset)/state.workspaceGrid)*state.workspaceGrid+state.workspaceDot-state.workspaceInset}

function workspaceSpot(clientX,clientY,width=678,height=458){const canvas=host.$('#workspace'),r=canvas.getBoundingClientRect(),v=host.project.workspaceView||{x:0,y:0,scale:1},s=v.scale||1;return{x:workspaceSnapStart(((clientX??r.left+r.width/2)-r.left-v.x)/s-width/2),y:workspaceSnapStart(((clientY??r.top+r.height/2)-r.top-v.y)/s-height/2)}}

function workspaceWorldPoint(clientX,clientY){const rect=host.$('#workspace').getBoundingClientRect(),view=host.project.workspaceView;return{x:(clientX-rect.left-view.x)/view.scale,y:(clientY-rect.top-view.y)/view.scale}}

function workspaceWindowHeight(w){return w.folded?45:w.height}

function workspaceSnapFloor(n){return Math.floor((n-state.workspaceDot-state.workspaceInset)/state.workspaceGrid+1e-9)*state.workspaceGrid+state.workspaceDot+state.workspaceInset}

function workspaceSnapCeil(n){return Math.ceil((n-state.workspaceDot-state.workspaceInset)/state.workspaceGrid-1e-9)*state.workspaceGrid+state.workspaceDot+state.workspaceInset}

function workspacePointerBlocked(pointer,ignore){return [...state.windows.values()].some(w=>w!==ignore&&w.placed&&pointer.x>=w.x&&pointer.x<=w.x+w.width&&pointer.y>=w.y&&pointer.y<=w.y+workspaceWindowHeight(w))}

function workspaceVacant(x,y,width,height,ignore){const gap=state.workspaceInset*2;return [...state.windows.values()].every(w=>w===ignore||!w.placed||x+width<=w.x-gap+1e-7||w.x+w.width+gap<=x+1e-7||y+height<=w.y-gap+1e-7||w.y+workspaceWindowHeight(w)+gap<=y+1e-7)}

function workspaceResolveDrag(desired,width,height,pointer,ignore,state={last:null}){
 if(workspacePointerBlocked(pointer,ignore)){state.last=null;return null}
 const gap=state.workspaceInset*2,xs=new Map(),ys=new Map(),previous=state.last;
 const add=(axis,value,contact)=>{if(!axis.has(value))axis.set(value,new Set());if(contact)axis.get(value).add(contact)};
 add(xs,workspaceSnapFloor(desired.x));add(xs,workspaceSnapCeil(desired.x));
 add(ys,workspaceSnapFloor(desired.y));add(ys,workspaceSnapCeil(desired.y));
 // Every candidate stays under the cursor, so it cannot jump across a blocker.
 add(xs,workspaceSnapCeil(pointer.x-width));add(xs,workspaceSnapFloor(pointer.x));
 add(ys,workspaceSnapCeil(pointer.y-height));add(ys,workspaceSnapFloor(pointer.y));
 if(previous){add(xs,previous.x);add(ys,previous.y)}
 state.windows.forEach(w=>{
  if(w===ignore||!w.placed)return;
  add(xs,workspaceSnapFloor(w.x-gap-width),w.key+':left');
  add(xs,workspaceSnapCeil(w.x+w.width+gap),w.key+':right');
  add(ys,workspaceSnapFloor(w.y-gap-height),w.key+':top');
  add(ys,workspaceSnapCeil(w.y+workspaceWindowHeight(w)+gap),w.key+':bottom');
 });
 let best=null,stable=null,lastCell=null;
 for(const [x,xContacts] of xs){
  if(x>pointer.x+1e-7||x+width<pointer.x-1e-7)continue;
  for(const [y,yContacts] of ys){
   if(y>pointer.y+1e-7||y+height<pointer.y-1e-7||!workspaceVacant(x,y,width,height,ignore))continue;
   const candidate={x,y,contacts:[...xContacts,...yContacts],distance:Math.hypot(x-desired.x,y-desired.y)};
   if(!best||candidate.distance<best.distance-1e-7)best=candidate;
   if(previous?.contacts.some(contact=>candidate.contacts.includes(contact))&&(!stable||candidate.distance<stable.distance-1e-7))stable=candidate;
   if(previous&&x===previous.x&&y===previous.y)lastCell=candidate;
  }
 }
 if(!best){state.last=null;return null}
 // A small screen-space margin prevents cell and contact-side chatter at corners.
 const margin=8/(host.project.workspaceView.scale||1),nearestDistance=best.distance;
 if(stable&&stable.distance<=nearestDistance+margin)best=stable;
 if(lastCell&&lastCell.distance<=nearestDistance+margin)best=lastCell;
 state.last=best;return{x:best.x,y:best.y};
}

function workspaceShowPlacement(preview,spot,desired,width,height,title){
 if(!preview){preview=document.createElement('div');preview.className='workspace-placement-preview';preview.setAttribute('aria-hidden','true');host.$('#workspace').append(preview)}
 const view=host.project.workspaceView,at=spot||desired;
 preview.textContent=title;preview.classList.toggle('invalid',!spot);
 Object.assign(preview.style,{left:view.x+at.x*view.scale+'px',top:view.y+at.y*view.scale+'px',width:width*view.scale+'px',height:height*view.scale+'px'});
 return preview;
}

function workspaceFreeSpot(center,width,height){const canvas=host.$('#workspace'),rect=canvas.getBoundingClientRect();const point=workspaceWorldPoint(center?.x??rect.left+rect.width/2,center?.y??rect.top+rect.height/2);return{x:point.x-width/2,y:point.y-height/2}}

function workspaceMenuSpot(x,y,width,height){const spot=workspaceFreeSpot({x,y},width,height),canvas=host.$('#workspace'),view=host.project.workspaceView,left=-view.x/view.scale,top=(38-view.y)/view.scale,right=(canvas.clientWidth-view.x)/view.scale-width,bottom=(canvas.clientHeight-view.y)/view.scale-height;return{x:Math.max(left,Math.min(spot.x,Math.max(left,right))),y:Math.max(top,Math.min(spot.y,Math.max(top,bottom)))}}

function workspaceFindSpot(center,width,height,ignore=null){
 const base=workspaceSpot(center?.x,center?.y,width,height);if(workspaceVacant(base.x,base.y,width,height,ignore))return base;
 // Click-to-open placement retains the clockwise search, independent of dragging.
 const tryCell=(dx,dy)=>{const x=base.x+dx*state.workspaceGrid,y=base.y+dy*state.workspaceGrid;return workspaceVacant(x,y,width,height,ignore)?{x,y}:null};
 for(let ring=1;ring<80;ring++){
  for(let dx=-ring;dx<=ring;dx++){const spot=tryCell(dx,-ring);if(spot)return spot}
  for(let dy=-ring+1;dy<=ring;dy++){const spot=tryCell(ring,dy);if(spot)return spot}
  for(let dx=ring-1;dx>=-ring;dx--){const spot=tryCell(dx,ring);if(spot)return spot}
  for(let dy=ring-1;dy>-ring;dy--){const spot=tryCell(-ring,dy);if(spot)return spot}
 }
 return{x:workspaceSnapCeil(Math.max(...[...state.windows.values()].filter(w=>w!==ignore&&w.placed).map(w=>w.x+w.width))+state.workspaceInset*2),y:base.y};
}

function focusWorkspaceWindow(w){if(!w)return;setWindowSelection([w]);focusWindow(w);if(w.placed)workspaceCenterOn(w.x+w.width/2,w.y+w.height/2)}

function workspaceCenterOn(x,y){const canvas=host.$('#workspace'),v=host.project.workspaceView;v.x=canvas.clientWidth/2-x*v.scale;v.y=canvas.clientHeight/2-y*v.scale;canvas.updateWorkspaceView?.();host.persist()}

function workspaceOrigin(){const placed=[...state.windows.values()].filter(w=>w.placed);if(!placed.length)return null;const main=placed.find(w=>w.meta?.mainWorkspace);if(main)return{x:main.x+main.width/2,y:main.y+main.height/2};return{x:(Math.min(...placed.map(w=>w.x))+Math.max(...placed.map(w=>w.x+w.width)))/2,y:(Math.min(...placed.map(w=>w.y))+Math.max(...placed.map(w=>w.y+w.height)))/2}}

function setMainWorkspaceWindow(target){const enabled=!target.meta.mainWorkspace;state.windows.forEach(w=>{w.meta.mainWorkspace=enabled&&w===target;w.el.classList.toggle('workspace-main-window',w.meta.mainWorkspace)});saveLayouts()}

function showWorkspaceSearchMenu(x,y){
 document.querySelector('.workspace-search-menu')?._close?.();
 const menu=document.createElement('div');menu.className='workspace-search-menu';menu.setAttribute('role','dialog');menu.setAttribute('aria-label','작업 공간 창 검색');
 menu.innerHTML='<div class="workspace-search-head"><input type="search" aria-label="작업 공간 창 검색" placeholder="창이나 객체 검색..."></div><div class="workspace-search-path"></div><div class="workspace-search-results"></div>';
 document.body.append(menu);
 const search=menu.querySelector('input'),path=menu.querySelector('.workspace-search-path'),results=menu.querySelector('.workspace-search-results');
 let group=null,folder=null;
 const close=()=>{menu.remove();document.removeEventListener('pointerdown',dismiss,true);document.removeEventListener('keydown',onKey)};
 menu._close=close;
 const dismiss=e=>{if(!menu.contains(e.target))close()};
 const openGroup=()=>{const current=group,key=browserInstanceKey('tab',current),size=browserInitialSize(key);close();host.openBrowser(current,{x,y},false,key,null,workspaceMenuSpot(x,y,size.width,size.height))};
 const openItem=o=>{close();if(host.browserCanEnter(o)){const key=browserInstanceKey('tree',o.group,o.id),size=browserInitialSize(key);host.openBrowser(o.group,{x,y},false,key,o.id,workspaceMenuSpot(x,y,size.width,size.height));return}const key='object:'+o.id,existing=state.windows.get(key);if(existing){focusWorkspaceWindow(existing);return}const w=host.openEditor(o.id);if(!w)return;const spot=workspaceMenuSpot(x,y,w.width,w.height);Object.assign(w,{x:spot.x,y:spot.y,placed:true});placeWindow(w);saveLayouts()};
 const add=(label,detail,action,className='')=>{const b=document.createElement('button');b.type='button';b.className='workspace-search-entry '+className;const name=document.createElement('strong');name.textContent=label;b.append(name);if(detail){const sub=document.createElement('small');sub.textContent=detail;b.append(sub)}b.onclick=action;results.append(b);return b};
 const ancestry=o=>{const names=[],seen=new Set();let parent=host.project.objects.find(item=>item.id===host.browserHierarchyParent(o));while(parent&&!seen.has(parent.id)){seen.add(parent.id);names.unshift(parent.name);parent=host.project.objects.find(item=>item.id===host.browserHierarchyParent(parent))}return names.join(' / ')};
 const position=()=>{menu.style.left=Math.max(8,Math.min(x,innerWidth-menu.offsetWidth-8))+'px';menu.style.top=Math.max(8,Math.min(y,innerHeight-menu.offsetHeight-8))+'px'};
 const render=()=>{
  results.replaceChildren();path.replaceChildren();const query=search.value.trim().toLocaleLowerCase();
  if(group||folder){const back=document.createElement('button');back.type='button';back.textContent='‹  '+(folder?host.project.objects.find(o=>o.id===folder)?.name||host.groups[group]:host.groups[group]);back.onclick=()=>{if(folder){folder=host.browserHierarchyParent(host.project.objects.find(o=>o.id===folder))||null}else group=null;render()};path.append(back)}
  if(query){const matches=host.project.objects.filter(o=>(!group||o.group===group)&&(o.id+' '+o.name+' '+ancestry(o)).toLocaleLowerCase().includes(query)).slice(0,60);matches.forEach(o=>add(o.name,host.groups[o.group]+(ancestry(o)?' / '+ancestry(o):'')+(o.kind==='Category'?' · 브라우저':''),()=>openItem(o)));if(!matches.length)add('검색 결과가 없어요.','',()=>{},'empty');position();return}
  if(!group){[['메모 만들기','note'],['그룹 만들기','group'],['하위 Workspace 만들기','portal']].forEach(([name,kind])=>add(name,'',()=>{close();createWorkspaceDecoration(kind,x,y)}));for(const [name,action] of host.privateHistoryMenu?.()||[])add(name,'비공개 배치 이력',()=>{close();action();});Object.entries(host.groups).forEach(([key,name])=>add(name,'브라우저와 하위 계층 보기  ›',()=>{group=key;folder=null;render()}));position();return}
  if(!folder)add(host.groups[group]+' 브라우저','새 창으로 열기',openGroup,'open-browser');
  else{const current=host.project.objects.find(o=>o.id===folder);if(current)add(current.name+' 브라우저','이 분류를 새 창으로 열기',()=>openItem(current),'open-browser')}
  const children=host.project.objects.filter(o=>o.group===group&&(host.browserHierarchyParent(o)||null)===folder).sort((a,b)=>Number(b.kind==='Category')-Number(a.kind==='Category'));
  children.forEach(o=>{if(host.browserCanEnter(o))add(o.name,'하위 계층  ›',()=>{folder=o.id;render()},'category');else add(o.name,o.kind,()=>openItem(o))});
  if(!children.length)add('이 계층에는 항목이 없어요.','검색으로 다른 대상을 찾을 수 있어요.',()=>{},'empty');
  position();
 };
 const onKey=e=>{if(!menu.isConnected)return;if(e.key==='Escape'){e.preventDefault();close()}else if(e.key==='Enter'&&document.activeElement===search){e.preventDefault();results.querySelector('.workspace-search-entry:not(.empty)')?.click()}};
 search.oninput=render;document.addEventListener('pointerdown',dismiss,true);document.addEventListener('keydown',onKey);render();
 search.focus();
}
 return {state,links:linkRuntime,cancelInteractions,editWorkspaceTitle,setupWorkspaceNavigation,openWindow,placeWindow,registerWorkspaceNode,unregisterWorkspaceNode,isWorkspaceNodeSelected,selectedWorkspaceNodes,selectedWorkspaceWindows,renderWorkspaceNodeSelection,setWorkspaceNodeSelection,toggleWorkspaceNodeSelection,focusWorkspaceNode,setWindowSelection,toggleWindowSelection,focusWindow,ensureWindowVisible,closeWindow,toggleWindow,clampWindow,clampWindows,trackWorkspaceDrag,beginWorkspaceNodeDrag,setupWindowDrag,setupWindowSelection,snapWindow,workspaceRecord,workspaceItems,decorationNodeKey,windowLayout,saveLayouts,workspaceDropTargetAt,updateWorkspaceDropPreview,moveWindowsToWorkspace,renderWorkspaceTabs,switchWorkspace,returnToParentWorkspace,positionWorkspaceDecorations,selectWorkspaceDecoration,decorationName,renameWorkspaceDecoration,deleteWorkspaceNodes,removeWorkspaceDecoration,confirmRemoveChildWorkspace,fullyInsideDecoration,renderWorkspaceDecorations,createWorkspaceDecoration,showWorkspaceContextMenu,restoreWindow,isBrowserWindowKey,isProjectBrowserKey,browserInstanceKey,browserInitialSize,browserPlacementSize,startWorkspaceDrag,endWorkspaceDrag,startObjectEditorDrag,workspaceDragSize,workspaceDropSpot,setupHelperWorkspaceDrags,setupBrowserDockDrag,workspaceSnapStart,workspaceSnapEnd,workspaceSpot,workspaceWorldPoint,workspaceWindowHeight,workspaceSnapFloor,workspaceSnapCeil,workspacePointerBlocked,workspaceVacant,workspaceResolveDrag,workspaceShowPlacement,workspaceFreeSpot,workspaceMenuSpot,workspaceFindSpot,focusWorkspaceWindow,workspaceCenterOn,workspaceOrigin,setMainWorkspaceWindow,showWorkspaceSearchMenu};
}
