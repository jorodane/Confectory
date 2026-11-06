// Authored auto mode measures CSS client pixels, never DPR or scaled canvas pixels.
export function runAutoDimensions(width,height){return Number.isInteger(width)&&Number.isInteger(height)&&width>=240&&width<=512&&height>=240&&height<=512?Object.freeze({width,height}):null;}
// One live publisher, one pending native receipt. Geometry notifications are not execution commands.
export function createRunAutoFit({read,measure,send,changed,delay=180}){
 let runtime=null,timer=null,disposed=false,sending=false,blocked=false,epoch=0;
 const cancel=()=>{if(timer!==null)clearTimeout(timer);timer=null;};
 function disable(){cancel();epoch++;runtime=null;blocked=false;}
 function activate(value){disable();if(!disposed&&value)runtime=value;notify();}
 function notify(){if(!disposed&&runtime&&timer===null)timer=setTimeout(pump,delay);}
 async function pump(){timer=null;if(disposed||!runtime)return;const s=read();if(s.runtime&&s.runtime!==runtime){disable();changed();return;}if(!s.visible||!s.ready||blocked||sending||s.runtime!==runtime)return;const dimensions=runAutoDimensions(...measure());if(!dimensions||s.width===dimensions.width&&s.height===dimensions.height)return;const captured=epoch;sending=true;try{if(!await send(dimensions)&&epoch===captured)blocked=true;}catch{if(epoch===captured)blocked=true;}finally{sending=false;if(!disposed)changed();}}
 return {activate,disable,notify,get runtime(){return runtime;},get blocked(){return blocked;},dispose(){disposed=true;disable();}};
}
