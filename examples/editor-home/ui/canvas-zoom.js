// v666 presentation limits. These values never change source or execution state.
export const MIN_CANVAS_ZOOM=1/32,MAX_CANVAS_ZOOM=5;
export const CANVAS_ZOOM_PRESETS=Object.freeze([3.125,6.25,12.5,25,50,75,100,150,200,300,400,500]);
export const clampCanvasZoom=value=>Math.max(MIN_CANVAS_ZOOM,Math.min(MAX_CANVAS_ZOOM,Number.isFinite(value)?value:1));
export const canvasZoomPercent=value=>Number((value*100).toFixed(5));
export function createSteppedZoomWheel(){
 let accumulated=0,lastTime=0;
 const stops=[];for(let value=1;value<=MAX_CANVAS_ZOOM;value+=.25)stops.push(value);
 for(let upper=1;upper>=.0625;upper/=2)for(let part=4;part<8;part++)stops.push(upper*part/8);
 stops.sort((a,b)=>a-b);
 const step=(scale,event)=>{
  const delta=event.deltaY*(event.deltaMode===1?40:event.deltaMode===2?800:1),now=performance.now();
  if(!delta)return scale;
  if(now-lastTime>250||Math.sign(delta)!==Math.sign(accumulated))accumulated=0;
  lastTime=now;accumulated+=delta;const ticks=Math.floor(Math.abs(accumulated)/100);if(!ticks)return scale;
  const direction=Math.sign(accumulated);accumulated-=direction*ticks*100;let next=clampCanvasZoom(scale);
  for(let i=0;i<Math.min(ticks,stops.length);i++){const stop=direction>0?[...stops].reverse().find(value=>value<next-1e-7):stops.find(value=>value>next+1e-7);if(stop===undefined)break;next=stop;}
  return next;
 };
 step.reset=()=>{accumulated=0;lastTime=0};return step;
}

// Original v666 zoom popover; callbacks are bound to one currently owned view.
export function bindCanvasZoomMenu({button,signal,isCurrent,getScale,setScale,fit}){
 let menu=null,events=null,closed=false;
 const sync=()=>{if(!menu)return;const value=canvasZoomPercent(getScale());menu.querySelector('[data-zoom-slider]').value=value;const input=menu.querySelector('[data-zoom-value]');if(document.activeElement!==input)input.value=value;for(const item of menu.querySelectorAll('[data-zoom-preset]'))item.setAttribute('aria-pressed',String(Number(item.dataset.zoomPreset)===value));};
 const commit=()=>{if(!menu||!isCurrent())return;const input=menu.querySelector('[data-zoom-value]'),raw=input.value.trim(),value=Number(raw);if(raw&&Number.isFinite(value))setScale(clampCanvasZoom(value/100));input.value=canvasZoomPercent(getScale());sync();};
 const close=(apply=true)=>{if(!menu)return;if(apply)commit();menu.querySelector('[data-zoom-value]').onblur=null;events?.abort();events=null;menu.remove();menu=null;button.setAttribute('aria-expanded','false');};
 const open=event=>{
  event.stopPropagation();if(closed||!isCurrent())return;if(menu){close();return;}
  const id='bp-zoom-value-'+crypto.randomUUID();menu=document.createElement('section');menu.className='workspace-zoom-menu bp-zoom-menu';menu.setAttribute('role','dialog');menu.setAttribute('aria-label','노드 화면 배율');
  menu.innerHTML='<div class="workspace-zoom-controls"><label for="'+id+'">배율</label><label class="workspace-zoom-value" for="'+id+'"><input id="'+id+'" data-zoom-value type="text" inputmode="decimal" aria-label="화면 배율 직접 입력" autocomplete="off"><span aria-hidden="true">%</span></label><input data-zoom-slider type="range" min="3.125" max="500" step="any" aria-label="화면 배율 조절"></div><div class="workspace-zoom-presets">'+CANVAS_ZOOM_PRESETS.map(value=>'<button type="button" data-zoom-preset="'+value+'">'+value+'%</button>').join('')+'</div><button type="button" class="bp-fit-button" data-bp-fit>전체 보기</button>';
  document.body.append(menu);button.setAttribute('aria-expanded','true');sync();
  const position=()=>{if(!menu)return;if(!isCurrent()||!button.isConnected){close(false);return;}const rect=button.getBoundingClientRect();menu.style.left=Math.max(8,Math.min(rect.left,innerWidth-menu.offsetWidth-8))+'px';menu.style.top=Math.max(8,Math.min(rect.bottom+6,innerHeight-menu.offsetHeight-8))+'px';};position();if(!menu)return;
  const input=menu.querySelector('[data-zoom-value]');input.onfocus=()=>input.select();input.onblur=commit;input.onkeydown=event=>{if(event.key==='Enter'&&!event.isComposing){event.preventDefault();event.stopPropagation();commit();input.select();}};
  menu.querySelector('[data-zoom-slider]').oninput=event=>{if(isCurrent()){setScale(clampCanvasZoom(Number(event.target.value)/100));sync();}};
  for(const item of menu.querySelectorAll('[data-zoom-preset]'))item.onclick=()=>{if(isCurrent()){setScale(Number(item.dataset.zoomPreset)/100);sync();}};
  menu.querySelector('[data-bp-fit]').onclick=()=>{if(isCurrent()){fit();sync();}};
  events=new AbortController();document.addEventListener('pointerdown',event=>{if(!menu.contains(event.target)&&!button.contains(event.target))close();},{capture:true,signal:events.signal});document.addEventListener('keydown',event=>{if(event.key==='Escape'){event.preventDefault();event.stopImmediatePropagation();close(false);if(isCurrent())button.focus({preventScroll:true});}},{capture:true,signal:events.signal});window.addEventListener('resize',position,{signal:events.signal});input.focus({preventScroll:true});
 };
 button.setAttribute('aria-haspopup','dialog');button.setAttribute('aria-expanded','false');button.addEventListener('click',open,{signal});signal.addEventListener('abort',()=>{closed=true;close(false);},{once:true});
 return {sync,close};
}
