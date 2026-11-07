import {runGridBox} from './run-grid.js';
// Visible producer-reported rectangles in the same contain box as RGBA pixels.
export function runBoundsGeometry(viewWidth,viewHeight,frame){
 const box=frame?.bounds&&runGridBox(viewWidth,viewHeight,frame.width,frame.height);if(!box)return null;
 const rectangles=[];for(let i=0;i<frame.bounds.rectangles.length;i+=4){const[x,y,w,h]=frame.bounds.rectangles.slice(i,i+4);rectangles.push(Object.freeze({left:box.left+x*box.width/frame.width,top:box.top+y*box.height/frame.height,width:w*box.width/frame.width,height:h*box.height/frame.height}));}
 return Object.freeze({box,rectangles:Object.freeze(rectangles)});
}
export function createRunBounds(screen){
 const element=document.createElement('div');element.className='run-output-bounds';element.dataset.runBounds='';element.setAttribute('aria-hidden','true');element.hidden=true;screen.append(element);let disposed=false,stamp='';
 const hide=()=>{element.hidden=true;element.replaceChildren();stamp='';};
 return {paint(enabled,frame,visible){if(disposed||!enabled||!visible){hide();return;}const layout=runBoundsGeometry(screen.clientWidth,screen.clientHeight,frame);if(!layout){hide();return;}const next=JSON.stringify([frame.cursor,frame.bounds,layout.box]);if(stamp===next){element.hidden=false;return;}stamp=next;Object.assign(element.style,{left:layout.box.left+'px',top:layout.box.top+'px',width:layout.box.width+'px',height:layout.box.height+'px'});element.replaceChildren();for(const rectangle of layout.rectangles){const child=document.createElement('span');Object.assign(child.style,{left:rectangle.left-layout.box.left+'px',top:rectangle.top-layout.box.top+'px',width:rectangle.width+'px',height:rectangle.height+'px'});element.append(child);}element.hidden=false;},hide,dispose(){if(disposed)return;disposed=true;hide();element.remove();}};
}
