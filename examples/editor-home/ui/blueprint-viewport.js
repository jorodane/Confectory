// Presentation only: coordinates, zoom and gestures never carry a source basis.
export const clampBlueprintZoom=value=>Math.max(.03125,Math.min(3,Number.isFinite(value)?value:1));
const finite=(value,fallback=0)=>Number.isFinite(value)&&Math.abs(value)<=1e7?value:fallback;
// A world position up to 1e7 at 300% zoom needs a larger private camera range.
const finiteCamera=value=>Number.isFinite(value)&&Math.abs(value)<=4e7?value:0;
export function activateBlueprintView(w,data){
 if(!data)return;
 if(w.meta.blueprintGraph!==data.id){
  const saved=Object.hasOwn(w.meta.blueprintViews||{},data.id)?w.meta.blueprintViews[data.id]:null;
  w.meta.blueprintZoom=saved?.zoom??100;w.meta.blueprintCamera=saved?.camera??{x:0,y:0};w.meta.blueprintPositions=saved?.positions??{};w.meta.blueprintNode=saved?.node;
  w.meta.blueprintOutputWidth=saved?.outputWidth??165;w.meta.blueprintOutputCollapsed=saved?.outputCollapsed===true;
 }
 w.meta.blueprintGraph=data.id;
}
function wheelSteps(){
 let accumulated=0,lastTime=0;const stops=[1,1.25,1.5,1.75,2,2.25,2.5,2.75,3];
 for(let upper=1;upper>=.0625;upper/=2)for(let part=4;part<8;part++)stops.push(upper*part/8);stops.sort((a,b)=>a-b);
 return {reset(){accumulated=0;lastTime=0;},step(scale,event){const delta=event.deltaY*(event.deltaMode===1?40:event.deltaMode===2?800:1),now=performance.now();if(!delta)return scale;if(now-lastTime>250||Math.sign(delta)!==Math.sign(accumulated))accumulated=0;lastTime=now;accumulated+=delta;const ticks=Math.floor(Math.abs(accumulated)/100);if(!ticks)return scale;const direction=Math.sign(accumulated);accumulated-=direction*ticks*100;let next=scale;for(let i=0;i<Math.min(ticks,stops.length);i++){const stop=direction>0?[...stops].reverse().find(value=>value<next-1e-7):stops.find(value=>value>next+1e-7);if(stop===undefined)break;next=stop;}return next;}};
}
export function mountBlueprintViewport({w,data,$,$$,persist,isCurrent,hasWire,cancelWire,headerClick}){
 const viewport=$('.bp-scroll',w.body),canvas=$('.bp-canvas',w.body),events=new AbortController(),wheel=wheelSteps();
 let scale=clampBlueprintZoom(Number(w.meta.blueprintZoom)/100),camera={x:finiteCamera(w.meta.blueprintCamera?.x),y:finiteCamera(w.meta.blueprintCamera?.y)},gesture=null,menu=null,menuEvents=null,closed=false;
 let outputWidth=finite(w.meta.blueprintOutputWidth,165),outputCollapsed=w.meta.blueprintOutputCollapsed===true;
 const output=$('.bp-output',w.body),outputResize=$('[data-bp-output-resize]',w.body),outputToggle=$('[data-bp-output-toggle]',w.body),maxOutputWidth=()=>Math.max(120,Math.min(420,Math.floor(output.parentElement.clientWidth*.55))),clampOutputWidth=value=>Math.max(120,Math.min(maxOutputWidth(),value));
 function applyOutputSidebar(){const width=clampOutputWidth(outputWidth);output.style.flexBasis=(outputCollapsed?36:width)+'px';output.classList.toggle('is-collapsed',outputCollapsed);outputResize.hidden=outputCollapsed;outputToggle.textContent=outputCollapsed?'‹':'›';outputToggle.setAttribute('aria-expanded',String(!outputCollapsed));outputToggle.setAttribute('aria-label',outputCollapsed?'출력 사이드바 펼치기':'출력 사이드바 접기');outputResize.setAttribute('aria-valuemin','120');outputResize.setAttribute('aria-valuemax',String(maxOutputWidth()));outputResize.setAttribute('aria-valuenow',String(width));}
 const overview=$('[data-bp-overview]',w.body),overviewSvg=overview?.querySelector('svg'),overviewStatus=$('[data-bp-overview-status]',w.body);let overviewMap=null;
 const elementFor=id=>typeof id==='string'?$('[data-bp-node="'+CSS.escape(id)+'"]',w.body):null;
 const active=()=>!closed&&isCurrent()&&w.el.isConnected&&!w.el.hidden&&viewport.isConnected;
 const positions=Object.create(null);for(const [i,node] of data.nodes.entries()){if(typeof node.id!=='string'||!node.id.length||node.id.length>512||Object.hasOwn(positions,node.id))continue;const saved=w.meta.blueprintPositions?.[node.id];positions[node.id]={x:Math.max(0,finite(saved?.x,40+i*290)),y:Math.max(0,finite(saved?.y,55+(i%2)*95))};}
 function save(){
  if(!isCurrent())return;const view={zoom:scale*100,camera:{...camera},positions:structuredClone(positions),node:w.meta.blueprintNode,outputWidth,outputCollapsed};
  Object.assign(w.meta,{blueprintZoom:view.zoom,blueprintCamera:view.camera,blueprintPositions:view.positions,blueprintOutputWidth:outputWidth,blueprintOutputCollapsed:outputCollapsed});
  const views=Object.assign(Object.create(null),w.meta.blueprintViews||{});views[data.id]=view;while(Object.keys(views).length>64)delete views[Object.keys(views).find(id=>id!==data.id)];w.meta.blueprintViews=views;persist();
 }
 function geometry(){const rect=viewport.getBoundingClientRect();return {rect,x:rect.width/viewport.offsetWidth||1,y:rect.height/viewport.offsetHeight||1};}
 // Read actual, currently mounted nodes. Old saved IDs and missing DOM never
 // create glyphs or authority; source order and stable IDs are left untouched.
 function sceneBounds(){
  const boxes=[],seen=new Set();let right=700,bottom=390;
  for(const node of data.nodes){const p=positions[node.id],el=elementFor(node.id);if(!p||!el||!el.isConnected||seen.has(node.id))continue;seen.add(node.id);const width=el.offsetWidth,height=el.offsetHeight;if(!(width>0&&height>0&&width<=1e7&&height<=1e7))continue;const box={id:node.id,x:p.x,y:p.y,width,height};boxes.push(box);right=Math.max(right,p.x+Math.max(300,width)+32);bottom=Math.max(bottom,p.y+Math.max(280,height)+32);}
  return {boxes,right,bottom};
 }
 function drawOverview(scene){
  if(!overviewSvg)return;const width=overview.clientWidth,height=overview.clientHeight;overviewSvg.replaceChildren();overviewMap=null;
  overview.setAttribute('aria-disabled',String(!scene.boxes.length));if(width<8||height<8||!scene.boxes.length){overviewStatus.textContent='표시할 노드 없음';return;}
  const pad=3,sx=(width-2*pad)/scene.right,sy=(height-2*pad)/scene.bottom,ox=pad,oy=pad;
  if(!(sx>0&&sy>0&&Number.isFinite(sx)&&Number.isFinite(sy)))return;overviewMap={...scene,sx,sy,ox,oy};overviewSvg.setAttribute('viewBox',`0 0 ${width} ${height}`);
  const make=(tag,attributes,title)=>{const el=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const [name,value]of Object.entries(attributes))el.setAttribute(name,String(value));if(title){const text=document.createElementNS(el.namespaceURI,'title');text.textContent=title;el.append(text);}overviewSvg.append(el);return el;},byId=new Map(scene.boxes.map(b=>[b.id,b]));
  const line=(from,to,cls,title)=>{const a=byId.get(from),b=byId.get(to);if(!a||!b)return;make('line',{x1:ox+(a.x+a.width/2)*sx,y1:oy+(a.y+a.height/2)*sy,x2:ox+(b.x+b.width/2)*sx,y2:oy+(b.y+b.height/2)*sy,class:cls},title);};
  for(const edge of data.edges)line(edge.from,edge.to,'bp-map-edge',`${edge.from} ${edge.port} → ${edge.to}`);
  for(const edge of data.diagnostics?.branchReturns||[])line(edge.from,edge.owner,'bp-map-edge bp-map-return',`${edge.from} → ${edge.owner} 메인 계속 복귀`);
  for(const b of scene.boxes)make('rect',{x:ox+b.x*sx,y:oy+b.y*sy,width:Math.max(2,b.width*sx),height:Math.max(2,b.height*sy),class:'bp-map-node'+(w.meta.blueprintNode===b.id?' is-selected':''),'data-bp-overview-node':b.id},b.id);
  const left=Math.max(0,Math.min(scene.right,-camera.x/scale)),top=Math.max(0,Math.min(scene.bottom,-camera.y/scale)),right=Math.max(left,Math.min(scene.right,(viewport.clientWidth-camera.x)/scale)),bottom=Math.max(top,Math.min(scene.bottom,(viewport.clientHeight-camera.y)/scale));
  make('rect',{x:ox+left*sx,y:oy+top*sy,width:(right-left)*sx,height:(bottom-top)*sy,class:'bp-map-visible','data-bp-overview-visible':''});
  overviewStatus.textContent=`노드 ${scene.boxes.length}개 · 방향키로 이동 · Shift: 크게 · Home/End · Escape: 드래그 취소`;
 }
 function centerOverview(x,y){if(!overviewMap)return;const cx=Math.max(0,Math.min(overviewMap.right,x)),cy=Math.max(0,Math.min(overviewMap.bottom,y));camera={x:viewport.clientWidth/2-cx*scale,y:viewport.clientHeight/2-cy*scale};}

 function resetDOMScroll(){if(viewport.scrollLeft||viewport.scrollTop){viewport.scrollLeft=0;viewport.scrollTop=0;}}
 function draw(){
  resetDOMScroll();applyOutputSidebar();
  canvas.style.transform=`translate(${camera.x}px,${camera.y}px) scale(${scale})`;canvas.style.zoom='';
  for(const node of data.nodes){const el=elementFor(node.id),p=positions[node.id];if(!el||!p)continue;el.style.left=p.x+'px';el.style.top=p.y+'px';}
  const scene=sceneBounds(),width=scene.right,height=scene.bottom;canvas.style.width=width+'px';canvas.style.height=height+'px';
  const svg=$('.bp-wires',w.body);svg.setAttribute('width',width);svg.setAttribute('height',height);svg.innerHTML=data.edges.filter(edge=>positions[edge.from]&&positions[edge.to]).map(edge=>{const origin=geometry(),outElement=$('[data-bp-exec-out="'+CSS.escape(edge.from)+'"][data-exec-port="'+CSS.escape(String(edge.port))+'"]',w.body),inputElement=$('[data-bp-exec-in="'+CSS.escape(edge.to)+'"]',w.body);if(!outElement||!inputElement)return '';const out=outElement.getBoundingClientRect(),input=inputElement.getBoundingClientRect(),x=((out.right-origin.rect.left)/origin.x-camera.x)/scale,y=((out.top+out.height/2-origin.rect.top)/origin.y-camera.y)/scale,tx=((input.left-origin.rect.left)/origin.x-camera.x)/scale,ty=((input.top+input.height/2-origin.rect.top)/origin.y-camera.y)/scale;return `<path d="M${x} ${y} C${x+35} ${y},${tx-35} ${ty},${tx} ${ty}"/>`;}).join('');
  if(['sync-acyclic-switch-v1','sync-acyclic-property-set-v1','sync-acyclic-property-ref-v1'].includes(data.profile)){
   const safe=value=>String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
   for(const edge of data.diagnostics?.branchReturns||[]){
    const from=$('[data-bp-exec-out="'+CSS.escape(edge.from)+'"][data-exec-port="'+CSS.escape(edge.port)+'"]',w.body),to=$('[data-bp-exec-out="'+CSS.escape(edge.owner)+'"][data-exec-port="next"]',w.body);if(!from||!to)continue;
    const origin=geometry(),a=from.getBoundingClientRect(),b=to.getBoundingClientRect(),x=((a.right-origin.rect.left)/origin.x-camera.x)/scale,y=((a.top+a.height/2-origin.rect.top)/origin.y-camera.y)/scale,tx=((b.right-origin.rect.left)/origin.x-camera.x)/scale,ty=((b.top+b.height/2-origin.rect.top)/origin.y-camera.y)/scale,bend=Math.max(x,tx)+45;
    svg.insertAdjacentHTML('beforeend',`<path class="bp-return-wire" data-bp-return-wire="${safe(edge.from+'/'+edge.port)}" d="M${x} ${y} C${bend} ${y},${bend} ${ty},${tx} ${ty}"><title>${safe(edge.owner)} 메인 계속 포트로 복귀</title></path>`);
   }
  }
  drawOverview(scene);
  const percent=Number((scale*100).toFixed(5));$('[data-bp-zoom]',w.body).value=percent;$('[data-bp-percent]',w.body).textContent=percent+'%';
  if(menu){$('[data-zoom-slider]',menu).value=percent;if(document.activeElement!==$('[data-zoom-value]',menu))$('[data-zoom-value]',menu).value=percent;for(const button of $$('[data-zoom-preset]',menu))button.setAttribute('aria-pressed',String(Number(button.dataset.zoomPreset)===percent));}
 }
 function zoomAt(next,x,y){const ratio=next/scale;camera.x=x-(x-camera.x)*ratio;camera.y=y-(y-camera.y)*ratio;scale=next;draw();save();}
 function setZoom(next){wheel.reset();zoomAt(clampBlueprintZoom(next),viewport.clientWidth/2,viewport.clientHeight/2);}
 function fit(){const boxes=sceneBounds().boxes;if(!boxes.length)return;wheel.reset();const left=Math.min(...boxes.map(b=>b.x)),top=Math.min(...boxes.map(b=>b.y)),right=Math.max(...boxes.map(b=>b.x+b.width)),bottom=Math.max(...boxes.map(b=>b.y+b.height));scale=Math.max(.05,Math.min(1,(viewport.clientWidth-40)/(right-left+40),(viewport.clientHeight-40)/(bottom-top+40)));camera={x:(viewport.clientWidth-(right-left)*scale)/2-left*scale,y:(viewport.clientHeight-(bottom-top)*scale)/2-top*scale};draw();save();}
 function closeMenu(commit=true){if(!menu)return;const old=menu;menu=null;$('[data-zoom-value]',old).onblur=null;if(commit){const input=$('[data-zoom-value]',old),raw=input.value.trim(),value=Number(raw);if(raw&&Number.isFinite(value))setZoom(value/100);}menuEvents?.abort();menuEvents=null;old.remove();$('[data-bp-percent]',w.body)?.setAttribute('aria-expanded','false');}
 $('[data-bp-percent]',w.body).onclick=()=>{
  if(menu){closeMenu();return;}menu=document.createElement('section');menu.className='bp-zoom-menu';menu.setAttribute('role','dialog');menu.setAttribute('aria-label','노드 화면 배율');menu.innerHTML='<label>배율 <input data-zoom-value type="text" inputmode="decimal" aria-label="화면 배율 직접 입력"> %</label><input data-zoom-slider type="range" min="3.125" max="300" step="any" aria-label="화면 배율 조절"><div>'+[3.125,6.25,12.5,25,50,75,100,150,200,300].map(value=>`<button data-zoom-preset="${value}">${value}%</button>`).join('')+'</div><button data-zoom-fit>전체 보기</button>';document.body.append(menu);menuEvents=new AbortController();
  const button=$('[data-bp-percent]',w.body),rect=button.getBoundingClientRect();Object.assign(menu.style,{left:Math.max(8,Math.min(rect.left,innerWidth-menu.offsetWidth-8))+'px',top:Math.max(8,Math.min(rect.bottom+6,innerHeight-menu.offsetHeight-8))+'px'});button.setAttribute('aria-expanded','true');draw();
  const input=$('[data-zoom-value]',menu),commit=()=>{const raw=input.value.trim(),value=Number(raw);if(raw&&Number.isFinite(value))setZoom(value/100);input.value=Number((scale*100).toFixed(5));};input.value=Number((scale*100).toFixed(5));input.onblur=commit;input.onkeydown=e=>{if(e.key==='Enter'){e.preventDefault();e.stopPropagation();commit();input.select();}};
  $('[data-zoom-slider]',menu).oninput=e=>setZoom(Number(e.target.value)/100);for(const b of $$('[data-zoom-preset]',menu))b.onclick=()=>setZoom(Number(b.dataset.zoomPreset)/100);$('[data-zoom-fit]',menu).onclick=()=>{fit();input.value=Number((scale*100).toFixed(5));};
  document.addEventListener('pointerdown',e=>{if(menu&&!menu.contains(e.target)&&!button.contains(e.target))closeMenu();},{capture:true,signal:menuEvents.signal});menu.addEventListener('keydown',e=>{if(e.key==='Escape'){e.preventDefault();e.stopPropagation();closeMenu(false);button.focus({preventScroll:true});}});input.focus({preventScroll:true});input.select();
 };
 $('[data-bp-zoom]',w.body).oninput=e=>setZoom(Number(e.target.value)/100);$('[data-bp-fit]',w.body).onclick=fit;
 function stopGesture(cancel=false){if(!gesture)return;const g=gesture;gesture=null;if(cancel)g.restore();g.owner.onpointermove=g.owner.onpointerup=g.owner.onpointercancel=g.owner.onlostpointercapture=null;if(g.owner.hasPointerCapture(g.id))g.owner.releasePointerCapture(g.id);viewport.classList.remove('is-panning');overview?.classList.remove('is-dragging');draw();save();g.complete?.(!cancel&&active());}
 function startGesture(event,owner,move,restore,complete=null){event.preventDefault();event.stopPropagation();stopGesture(true);owner.setPointerCapture(event.pointerId);gesture={id:event.pointerId,owner,restore,complete};owner.onpointermove=e=>{if(e.pointerId===event.pointerId){if(!active()){stopGesture(true);return;}move(e);draw();}};owner.onpointerup=e=>{if(e.pointerId===event.pointerId)stopGesture(!active());};owner.onpointercancel=owner.onlostpointercapture=()=>stopGesture(true);}
 if(overview){
  overview.onpointerdown=event=>{if(event.button!==0||!active()||!overviewMap)return;overview.focus({preventScroll:true});cancelWire();const before={...camera},map={...overviewMap};const move=e=>{const r=overview.getBoundingClientRect(),x=(e.clientX-r.left)/(r.width/overview.clientWidth||1),y=(e.clientY-r.top)/(r.height/overview.clientHeight||1);centerOverview((x-map.ox)/map.sx,(y-map.oy)/map.sy);};startGesture(event,overview,move,()=>camera={...before});overview.classList.add('is-dragging');move(event);draw();};
  overview.onkeydown=event=>{if(!active()||!overviewMap||!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','Home','End','PageUp','PageDown'].includes(event.key))return;event.preventDefault();event.stopPropagation();stopGesture(true);cancelWire();const x=(viewport.clientWidth/2-camera.x)/scale,y=(viewport.clientHeight/2-camera.y)/scale,k=event.shiftKey?.5:.1,dx=viewport.clientWidth/scale*k,dy=viewport.clientHeight/scale*k;
   if(event.key==='Home')centerOverview(0,0);else if(event.key==='End')centerOverview(overviewMap.right,overviewMap.bottom);else centerOverview(x+(event.key==='ArrowLeft'?-dx:event.key==='ArrowRight'?dx:0),y+(event.key==='ArrowUp'?-dy:event.key==='ArrowDown'?dy:event.key==='PageUp'?-viewport.clientHeight/scale*.9:event.key==='PageDown'?viewport.clientHeight/scale*.9:0));draw();save();};
 }

 outputResize.onpointerdown=event=>{if(event.button!==0||!isCurrent())return;cancelWire();const x=event.clientX,before=outputWidth,width=clampOutputWidth(outputWidth),outer=output.getBoundingClientRect().width/output.offsetWidth||1;startGesture(event,outputResize,e=>outputWidth=clampOutputWidth(width+(x-e.clientX)/outer),()=>outputWidth=before);};
 outputResize.onkeydown=event=>{if(!isCurrent()||!['ArrowLeft','ArrowRight','Home','End'].includes(event.key))return;event.preventDefault();event.stopPropagation();outputWidth=event.key==='Home'?120:event.key==='End'?maxOutputWidth():clampOutputWidth(clampOutputWidth(outputWidth)+(event.key==='ArrowLeft'?16:-16));draw();save();};
 outputToggle.onclick=()=>{if(!isCurrent())return;stopGesture(true);cancelWire();outputCollapsed=!outputCollapsed;draw();save();};
 viewport.addEventListener('scroll',()=>{if(active())resetDOMScroll();},{passive:true,signal:events.signal});
 viewport.addEventListener('wheel',event=>{event.stopPropagation();const input=event.target.closest('textarea');if(input&&input.scrollHeight>input.clientHeight+1)return;event.preventDefault();if(!isCurrent())return;const next=wheel.step(scale,event);if(next===scale)return;const g=geometry();zoomAt(next,(event.clientX-g.rect.left)/g.x,(event.clientY-g.rect.top)/g.y);},{passive:false,signal:events.signal});
 viewport.addEventListener('pointerdown',event=>{if(![1,2].includes(event.button)||!isCurrent())return;cancelWire();const before={...camera},g=geometry(),start={x:event.clientX,y:event.clientY};startGesture(event,viewport,e=>{camera.x=before.x+(e.clientX-start.x)/g.x;camera.y=before.y+(e.clientY-start.y)/g.y;},()=>camera={...before});viewport.classList.add('is-panning');},{capture:true,signal:events.signal});
 viewport.addEventListener('contextmenu',e=>{e.preventDefault();e.stopPropagation();},{signal:events.signal});
 for(const header of $$('[data-bp-drag]',w.body))header.onpointerdown=event=>{if(event.button!==0||!active()||event.target.closest('button,input,textarea,select')||hasWire())return;const id=header.dataset.bpDrag;if(!positions[id]||!elementFor(id))return;const before={...positions[id]},g=geometry(),start={x:event.clientX,y:event.clientY};let moved=false;startGesture(event,header,e=>{if(Math.hypot(e.clientX-start.x,e.clientY-start.y)>4)moved=true;positions[id]={x:Math.max(0,before.x+(e.clientX-start.x)/g.x/scale),y:Math.max(0,before.y+(e.clientY-start.y)/g.y/scale)};},()=>positions[id]={...before},ok=>{if(ok)headerClick?.(id,moved,!!event.target.closest('[data-bp-name]'));});};
 document.addEventListener('keydown',e=>{if(e.key==='Escape'&&(gesture||hasWire())){e.preventDefault();e.stopPropagation();stopGesture(true);cancelWire();}},{capture:true,signal:events.signal});
 const resize=new ResizeObserver(()=>{if(active())draw();});resize.observe(viewport);if(overview)resize.observe(overview);for(const node of data.nodes){const el=elementFor(node.id);if(el)resize.observe(el);}
 const sceneChanges=new MutationObserver(()=>{if(active())draw();});sceneChanges.observe(canvas,{childList:true});
 window.addEventListener('blur',()=>stopGesture(true),{signal:events.signal});
 const visibility=new MutationObserver(()=>{if(!isCurrent()){cancelWire();dispose();}else if(!w.el.isConnected||w.el.hidden){stopGesture(true);closeMenu(false);cancelWire();}});visibility.observe(document.body,{subtree:true,childList:true,attributes:true,attributeFilter:['hidden']});
 function dispose(){if(closed)return;stopGesture(true);closeMenu(false);save();closed=true;events.abort();resize.disconnect();visibility.disconnect();sceneChanges.disconnect();}
 draw();save();return {dispose,focusNode(id){if(!active()||!Object.hasOwn(positions,id))return;const node=elementFor(id);if(!node)return;camera={x:viewport.clientWidth/2-(positions[id].x+node.offsetWidth/2)*scale,y:viewport.clientHeight/2-(positions[id].y+node.offsetHeight/2)*scale};draw();save();}};
}
