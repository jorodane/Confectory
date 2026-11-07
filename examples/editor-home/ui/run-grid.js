// Same contain rectangle as the verified RGBA canvas; percentages are a view aid, not element bounds.
export function runGridBox(viewWidth,viewHeight,width,height){
 if(![viewWidth,viewHeight,width,height].every(n=>Number.isFinite(n)&&n>0)||![width,height].every(Number.isSafeInteger))return null;
 const scale=Math.min(viewWidth/width,viewHeight/height),w=width*scale,h=height*scale;
 if(![scale,w,h].every(n=>Number.isFinite(n)&&n>0))return null;
 return Object.freeze({left:(viewWidth-w)/2,top:(viewHeight-h)/2,width:w,height:h});
}
export function createRunGrid(screen){
 const element=document.createElement('div');element.className='run-debug-grid';element.dataset.runGrid='';element.setAttribute('aria-hidden','true');element.hidden=true;screen.append(element);let disposed=false;
 function hide(){element.hidden=true;screen.classList.remove('run-show-grid');}
 return {paint(enabled,frame,visible){if(disposed||!enabled||!visible||!frame){hide();return;}const box=runGridBox(screen.clientWidth,screen.clientHeight,frame.width,frame.height);if(!box){hide();return;}Object.assign(element.style,{inset:'auto',left:box.left+'px',top:box.top+'px',width:box.width+'px',height:box.height+'px'});element.hidden=false;screen.classList.add('run-show-grid');},hide,dispose(){if(disposed)return;disposed=true;hide();element.remove();}};
}
