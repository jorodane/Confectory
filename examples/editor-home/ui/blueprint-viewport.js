// Presentation only: coordinates, zoom and gestures never carry a source basis.
export const clampBlueprintZoom=value=>Math.max(.03125,Math.min(3,Number.isFinite(value)?value:1));
const finite=(value,fallback=0)=>Number.isFinite(value)&&Math.abs(value)<=1e7?value:fallback;
export function activateBlueprintView(w,data){
 if(!data)return;
 if(w.meta.blueprintGraph!==data.id){
  const saved=Object.hasOwn(w.meta.blueprintViews||{},data.id)?w.meta.blueprintViews[data.id]:null;
  w.meta.blueprintZoom=saved?.zoom??100;w.meta.blueprintCamera=saved?.camera??{x:0,y:0};w.meta.blueprintPositions=saved?.positions??{};w.meta.blueprintNode=saved?.node;
 }
 w.meta.blueprintGraph=data.id;
}
function wheelSteps(){
 let accumulated=0,lastTime=0;const stops=[1,1.25,1.5,1.75,2,2.25,2.5,2.75,3];
 for(let upper=1;upper>=.0625;upper/=2)for(let part=4;part<8;part++)stops.push(upper*part/8);stops.sort((a,b)=>a-b);
 return {reset(){accumulated=0;lastTime=0;},step(scale,event){const delta=event.deltaY*(event.deltaMode===1?40:event.deltaMode===2?800:1),now=performance.now();if(!delta)return scale;if(now-lastTime>250||Math.sign(delta)!==Math.sign(accumulated))accumulated=0;lastTime=now;accumulated+=delta;const ticks=Math.floor(Math.abs(accumulated)/100);if(!ticks)return scale;const direction=Math.sign(accumulated);accumulated-=direction*ticks*100;let next=scale;for(let i=0;i<Math.min(ticks,stops.length);i++){const stop=direction>0?[...stops].reverse().find(value=>value<next-1e-7):stops.find(value=>value>next+1e-7);if(stop===undefined)break;next=stop;}return next;}};
}
export function mountBlueprintViewport({w,data,$,$$,persist,isCurrent,hasWire,cancelWire}){
 const viewport=$('.bp-scroll',w.body),canvas=$('.bp-canvas',w.body),events=new AbortController(),wheel=wheelSteps();
 let scale=clampBlueprintZoom(Number(w.meta.blueprintZoom)/100),camera={x:finite(w.meta.blueprintCamera?.x),y:finite(w.meta.blueprintCamera?.y)},gesture=null,menu=null,menuEvents=null,closed=false;
 const positions=Object.create(null);for(const [i,node] of data.nodes.entries()){const saved=w.meta.blueprintPositions?.[node.id];positions[node.id]={x:Math.max(0,finite(saved?.x,40+i*290)),y:Math.max(0,finite(saved?.y,55+(i%2)*95))};}
 function save(){
  if(!isCurrent())return;const view={zoom:scale*100,camera:{...camera},positions:structuredClone(positions),node:w.meta.blueprintNode};
  Object.assign(w.meta,{blueprintZoom:view.zoom,blueprintCamera:view.camera,blueprintPositions:view.positions});
  const views=Object.assign(Object.create(null),w.meta.blueprintViews||{});views[data.id]=view;while(Object.keys(views).length>64)delete views[Object.keys(views).find(id=>id!==data.id)];w.meta.blueprintViews=views;persist();
 }
 function geometry(){const rect=viewport.getBoundingClientRect();return {rect,x:rect.width/viewport.offsetWidth||1,y:rect.height/viewport.offsetHeight||1};}
 function draw(){
  canvas.style.transform=`translate(${camera.x}px,${camera.y}px) scale(${scale})`;canvas.style.zoom='';
  for(const node of data.nodes){const el=$('[data-bp-node="'+CSS.escape(node.id)+'"]',w.body),p=positions[node.id];el.style.left=p.x+'px';el.style.top=p.y+'px';}
  const width=Math.max(700,...Object.values(positions).map(p=>p.x+300)),height=Math.max(390,...data.nodes.map(n=>positions[n.id].y+(n.control==='switch'?Math.max(280,$('[data-bp-node=\"'+CSS.escape(n.id)+'\"]',w.body).offsetHeight+30):280)));canvas.style.width=width+'px';canvas.style.height=height+'px';
  const svg=$('.bp-wires',w.body);svg.setAttribute('width',width);svg.setAttribute('height',height);svg.innerHTML=data.edges.filter(edge=>positions[edge.from]&&positions[edge.to]).map(edge=>{const origin=geometry(),outElement=$('[data-bp-exec-out="'+CSS.escape(edge.from)+'"][data-exec-port="'+CSS.escape(String(edge.port))+'"]',w.body),inputElement=$('[data-bp-exec-in="'+CSS.escape(edge.to)+'"]',w.body);if(!outElement||!inputElement)return '';const out=outElement.getBoundingClientRect(),input=inputElement.getBoundingClientRect(),x=((out.right-origin.rect.left)/origin.x-camera.x)/scale,y=((out.top+out.height/2-origin.rect.top)/origin.y-camera.y)/scale,tx=((input.left-origin.rect.left)/origin.x-camera.x)/scale,ty=((input.top+input.height/2-origin.rect.top)/origin.y-camera.y)/scale;return `<path d="M${x} ${y} C${x+35} ${y},${tx-35} ${ty},${tx} ${ty}"/>`;}).join('');
  if(data.profile==='sync-acyclic-switch-v1'){
   const safe=value=>String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
   for(const edge of data.diagnostics?.branchReturns||[]){
    const from=$('[data-bp-exec-out="'+CSS.escape(edge.from)+'"][data-exec-port="'+CSS.escape(edge.port)+'"]',w.body),to=$('[data-bp-exec-out="'+CSS.escape(edge.owner)+'"][data-exec-port="next"]',w.body);if(!from||!to)continue;
    const origin=geometry(),a=from.getBoundingClientRect(),b=to.getBoundingClientRect(),x=((a.right-origin.rect.left)/origin.x-camera.x)/scale,y=((a.top+a.height/2-origin.rect.top)/origin.y-camera.y)/scale,tx=((b.right-origin.rect.left)/origin.x-camera.x)/scale,ty=((b.top+b.height/2-origin.rect.top)/origin.y-camera.y)/scale,bend=Math.max(x,tx)+45;
    svg.insertAdjacentHTML('beforeend',`<path class="bp-return-wire" data-bp-return-wire="${safe(edge.from+'/'+edge.port)}" d="M${x} ${y} C${bend} ${y},${bend} ${ty},${tx} ${ty}"><title>${safe(edge.owner)} 메인 계속 포트로 복귀</title></path>`);
   }
  }
  const percent=Number((scale*100).toFixed(5));$('[data-bp-zoom]',w.body).value=percent;$('[data-bp-percent]',w.body).textContent=percent+'%';
  if(menu){$('[data-zoom-slider]',menu).value=percent;if(document.activeElement!==$('[data-zoom-value]',menu))$('[data-zoom-value]',menu).value=percent;for(const button of $$('[data-zoom-preset]',menu))button.setAttribute('aria-pressed',String(Number(button.dataset.zoomPreset)===percent));}
 }
 function zoomAt(next,x,y){const ratio=next/scale;camera.x=x-(x-camera.x)*ratio;camera.y=y-(y-camera.y)*ratio;scale=next;draw();save();}
 function setZoom(next){wheel.reset();zoomAt(clampBlueprintZoom(next),viewport.clientWidth/2,viewport.clientHeight/2);}
 function fit(){if(!data.nodes.length)return;wheel.reset();const left=Math.min(...Object.values(positions).map(p=>p.x)),top=Math.min(...Object.values(positions).map(p=>p.y)),right=Math.max(...data.nodes.map(n=>positions[n.id].x+$('[data-bp-node="'+CSS.escape(n.id)+'"]',w.body).offsetWidth)),bottom=Math.max(...data.nodes.map(n=>positions[n.id].y+$('[data-bp-node="'+CSS.escape(n.id)+'"]',w.body).offsetHeight));scale=Math.max(.05,Math.min(1,(viewport.clientWidth-40)/(right-left+40),(viewport.clientHeight-40)/(bottom-top+40)));camera={x:(viewport.clientWidth-(right-left)*scale)/2-left*scale,y:(viewport.clientHeight-(bottom-top)*scale)/2-top*scale};draw();save();}
 function closeMenu(commit=true){if(!menu)return;const old=menu;menu=null;$('[data-zoom-value]',old).onblur=null;if(commit){const input=$('[data-zoom-value]',old),raw=input.value.trim(),value=Number(raw);if(raw&&Number.isFinite(value))setZoom(value/100);}menuEvents?.abort();menuEvents=null;old.remove();$('[data-bp-percent]',w.body)?.setAttribute('aria-expanded','false');}
 $('[data-bp-percent]',w.body).onclick=()=>{
  if(menu){closeMenu();return;}menu=document.createElement('section');menu.className='bp-zoom-menu';menu.setAttribute('role','dialog');menu.setAttribute('aria-label','노드 화면 배율');menu.innerHTML='<label>배율 <input data-zoom-value type="text" inputmode="decimal" aria-label="화면 배율 직접 입력"> %</label><input data-zoom-slider type="range" min="3.125" max="300" step="any" aria-label="화면 배율 조절"><div>'+[3.125,6.25,12.5,25,50,75,100,150,200,300].map(value=>`<button data-zoom-preset="${value}">${value}%</button>`).join('')+'</div><button data-zoom-fit>전체 보기</button>';document.body.append(menu);menuEvents=new AbortController();
  const button=$('[data-bp-percent]',w.body),rect=button.getBoundingClientRect();Object.assign(menu.style,{left:Math.max(8,Math.min(rect.left,innerWidth-menu.offsetWidth-8))+'px',top:Math.max(8,Math.min(rect.bottom+6,innerHeight-menu.offsetHeight-8))+'px'});button.setAttribute('aria-expanded','true');draw();
  const input=$('[data-zoom-value]',menu),commit=()=>{const raw=input.value.trim(),value=Number(raw);if(raw&&Number.isFinite(value))setZoom(value/100);input.value=Number((scale*100).toFixed(5));};input.value=Number((scale*100).toFixed(5));input.onblur=commit;input.onkeydown=e=>{if(e.key==='Enter'){e.preventDefault();e.stopPropagation();commit();input.select();}};
  $('[data-zoom-slider]',menu).oninput=e=>setZoom(Number(e.target.value)/100);for(const b of $$('[data-zoom-preset]',menu))b.onclick=()=>setZoom(Number(b.dataset.zoomPreset)/100);$('[data-zoom-fit]',menu).onclick=()=>{fit();input.value=Number((scale*100).toFixed(5));};
  document.addEventListener('pointerdown',e=>{if(menu&&!menu.contains(e.target)&&!button.contains(e.target))closeMenu();},{capture:true,signal:menuEvents.signal});menu.addEventListener('keydown',e=>{if(e.key==='Escape'){e.preventDefault();e.stopPropagation();closeMenu(false);button.focus({preventScroll:true});}});input.focus({preventScroll:true});input.select();
 };
 $('[data-bp-zoom]',w.body).oninput=e=>setZoom(Number(e.target.value)/100);$('[data-bp-fit]',w.body).onclick=fit;
 function stopGesture(cancel=false){if(!gesture)return;const g=gesture;gesture=null;if(cancel)g.restore();g.owner.onpointermove=g.owner.onpointerup=g.owner.onpointercancel=null;if(g.owner.hasPointerCapture(g.id))g.owner.releasePointerCapture(g.id);viewport.classList.remove('is-panning');draw();save();}
 function startGesture(event,owner,move,restore){event.preventDefault();event.stopPropagation();stopGesture(true);owner.setPointerCapture(event.pointerId);gesture={id:event.pointerId,owner,restore};owner.onpointermove=e=>{if(e.pointerId===event.pointerId&&isCurrent()){move(e);draw();}};owner.onpointerup=e=>{if(e.pointerId===event.pointerId)stopGesture();};owner.onpointercancel=()=>stopGesture(true);}
 viewport.addEventListener('wheel',event=>{event.stopPropagation();const input=event.target.closest('textarea');if(input&&input.scrollHeight>input.clientHeight+1)return;event.preventDefault();if(!isCurrent())return;const next=wheel.step(scale,event);if(next===scale)return;const g=geometry();zoomAt(next,(event.clientX-g.rect.left)/g.x,(event.clientY-g.rect.top)/g.y);},{passive:false,signal:events.signal});
 viewport.addEventListener('pointerdown',event=>{if(![1,2].includes(event.button)||!isCurrent())return;cancelWire();const before={...camera},g=geometry(),start={x:event.clientX,y:event.clientY};startGesture(event,viewport,e=>{camera.x=before.x+(e.clientX-start.x)/g.x;camera.y=before.y+(e.clientY-start.y)/g.y;},()=>camera={...before});viewport.classList.add('is-panning');},{capture:true,signal:events.signal});
 viewport.addEventListener('contextmenu',e=>{e.preventDefault();e.stopPropagation();},{signal:events.signal});
 for(const header of $$('[data-bp-drag]',w.body))header.onpointerdown=event=>{if(event.button!==0||event.target.closest('button,input,textarea,select')||hasWire())return;const id=header.dataset.bpDrag,before={...positions[id]},g=geometry(),start={x:event.clientX,y:event.clientY};startGesture(event,header,e=>{positions[id]={x:Math.max(0,before.x+(e.clientX-start.x)/g.x/scale),y:Math.max(0,before.y+(e.clientY-start.y)/g.y/scale)};},()=>positions[id]={...before});};
 document.addEventListener('keydown',e=>{if(e.key==='Escape'&&(gesture||hasWire())){e.preventDefault();e.stopPropagation();stopGesture(true);cancelWire();}},{capture:true,signal:events.signal});
 const resize=new ResizeObserver(()=>{if(!closed&&isCurrent())draw();});resize.observe(viewport);
 const visibility=new MutationObserver(()=>{if(!isCurrent()){cancelWire();dispose();}else if(!w.el.isConnected||w.el.hidden){stopGesture(true);closeMenu(false);cancelWire();}});visibility.observe(document.body,{subtree:true,childList:true,attributes:true,attributeFilter:['hidden']});
 function dispose(){if(closed)return;stopGesture(true);closeMenu(false);save();closed=true;events.abort();resize.disconnect();visibility.disconnect();}
 draw();save();return {dispose,focusNode(id){if(!positions[id])return;const node=$('[data-bp-node="'+CSS.escape(id)+'"]',w.body);camera={x:viewport.clientWidth/2-(positions[id].x+node.offsetWidth/2)*scale,y:viewport.clientHeight/2-(positions[id].y+node.offsetHeight/2)*scale};draw();save();}};
}
