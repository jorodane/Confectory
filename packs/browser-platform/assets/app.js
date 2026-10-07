import {dotnet} from './_framework/dotnet.js';
const surface=document.getElementById('surface'),canvas=document.querySelector('canvas'),ctx=canvas.getContext('2d'),overlay=document.getElementById('fields');
const events=[],hosts=new Map(),closedHosts=new Set(),loops=new Set();let bridge,serial=1,picker=null,presented=0;
function font(){ctx.font='14px sans-serif';ctx.textBaseline='top';}font();
function size(){const w=Math.max(1,surface.clientWidth),h=Math.max(1,surface.clientHeight);if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h;font();}return[w,h];}
function key(e){if(typeof e.key!=='string')return 0;return({Tab:0xff09,Enter:0xff0d,Escape:0xff1b,ArrowLeft:0xff51,ArrowUp:0xff52,ArrowRight:0xff53,ArrowDown:0xff54,Backspace:0xff08,Delete:0xffff})[e.key]??(e.key.length===1?e.key.charCodeAt(0):0);}
function record(list,id,type,e){const b=canvas.getBoundingClientRect();list.push(id,type,Math.round((e.clientX??b.x)-b.x),Math.round((e.clientY??b.y)-b.y),key(e),(e.repeat?1:0)|(e.ctrlKey?2:0)|(e.shiftKey?4:0)|(e.altKey?8:0));}
for(const [name,type] of [['pointerdown',1],['pointerup',2],['pointermove',3],['keydown',5],['keyup',6]])canvas.addEventListener(name,e=>{record(events,0,type,e);if(name==='keydown')e.preventDefault();});canvas.tabIndex=0;
function snapshot(row){const el=row.el;return {...row.args,value:el.value,caret:el.selectionEnd??0,anchor:el.selectionStart??0,focus:document.activeElement===el,provider:'browser-dom',nativeHandle:row.key,deferredExternal:row.composing,composing:row.composing};}
function native(a){let h=hosts.get(a.host),p=JSON.parse(a.payload);if(a.operation==='create'){const token='browser-field-owner-'+serial++;hosts.set(token,{fields:new Map(),events:[],picker:null});return token;}if(!h){if(a.operation==='close'&&closedHosts.has(a.host))return{};throw Error('Unknown browser native owner');}
 switch(a.operation){
 case 'configure':{const k=p.id+':'+p.binding;let row=h.fields.get(k);if(!row){const el=document.createElement(p.mode==='singleline'?'input':'textarea');el.dataset.control=p.id;el.dataset.binding=p.binding;row={key:k,el,args:p,composing:false};h.fields.set(k,row);overlay.append(el);el.addEventListener('compositionstart',()=>row.composing=true);el.addEventListener('compositionend',()=>row.composing=false);for(const [n,t] of [['keydown',5],['keyup',6]])el.addEventListener(n,e=>{record(h.events,p.id,t,e);if(e.key==='Tab')e.preventDefault();});}
 const el=row.el;if(!row.composing&&el.value!==p.value){el.value=p.value;el.setSelectionRange(Math.min(p.anchor,p.caret),Math.max(p.anchor,p.caret));}row.args=p;el.placeholder=p.hint;el.disabled=!p.enabled;el.readOnly=p.readonly;el.style.display=p.visible?'block':'none';const [x,y,w,z]=p.bounds;Object.assign(el.style,{left:x+'px',top:y+'px',width:w+'px',height:z+'px'});return snapshot(row);}
 case 'snapshot':return [...h.fields.values()].map(snapshot);
 case 'events':return h.events.splice(0);
 case 'frame':for(const row of h.fields.values())if(!p.shown.includes(row.key)){row.args.visible=false;row.el.style.display='none';}return{};
 case 'focus':{const row=[...h.fields.values()].find(r=>r.args.id===p.id&&r.args.visible);if(row)row.el.focus();else document.activeElement?.blur();return{};}
 case 'clip':{const row=h.fields.get(p.key);if(row){const[x,y,w,z]=row.args.bounds;row.el.style.clipPath=p.regions.length===0?'inset(100%)':`path('${p.regions.reduce((s,v,i,r)=>i%4?s:s+`M${r[i]-x} ${r[i+1]-y}h${r[i+2]}v${r[i+3]}h-${r[i+2]}Z`,'')}')`;}return{};}
 case 'commands':return{};
 case 'close':for(const row of h.fields.values())row.el.remove();hosts.delete(a.host);closedHosts.add(a.host);return{};
 case 'folder-begin':{h.picker={state:'pending'};const input=document.createElement('input');input.type='file';input.multiple=true;input.webkitdirectory=true;input.style.display='none';document.body.append(input);picker=input;input.addEventListener('cancel',()=>{h.picker={state:'cancelled'};input.remove();});input.addEventListener('change',async()=>{try{const files=[...input.files];if(!files.length){h.picker={state:'cancelled'};return;}const names=files.map(f=>f.webkitRelativePath||f.name),texts=await Promise.all(files.map(f=>f.text()));const base=bridge.ImportFiles(JSON.stringify(names),JSON.stringify(texts));h.picker={state:'selected',path:base+'/'+names[0].split('/')[0]};}catch(e){h.picker={state:'error',error:e.message};}finally{input.remove();}});input.click();return{};}
 case 'folder-poll':{const p=h.picker??{state:'idle'};if(p.state!=='pending')h.picker=null;return p;}
 case 'folder-cancel':if(picker)picker.remove();h.picker={state:'cancelled'};return{};
 case 'open-folder':throw Error('Browser cannot launch OS file manager; selected files remain virtual');
 default:throw Error('Unsupported NativeUI operation '+a.operation);
 }}
function request(operation,payload){const a=JSON.parse(payload);let result={};switch(operation){
 case 'create':if(a.titles.length!==1)throw Error('Browser supports one document surface');size();result=[1,1];break;
 case 'dimensions':result=size();break;
 case 'pump':result=events.splice(0);break;
 case 'draw':presented++;size();for(let i=0;i<a.rectangles.length;i+=5){const[x,y,w,h,c]=a.rectangles.slice(i,i+5);ctx.fillStyle='#'+c.toString(16).padStart(6,'0');ctx.fillRect(x,y,w,h);}break;
 case 'drawText':font();ctx.fillStyle='#dceaf2';for(let i=0;i<a.labels.length;i++){const[x,y,w,h]=a.clips.slice(i*4,i*4+4),[ox,oy]=a.origins.slice(i*2,i*2+2);ctx.save();ctx.beginPath();ctx.rect(x,y,w,h);ctx.clip();ctx.fillText(a.labels[i],ox,oy);ctx.restore();}break;
 case 'measure':font();{let start=0;const lines=a.text.split('\n').map(text=>{const positions=Array.from({length:text.length+1},(_,i)=>i>0&&i<text.length&&/[\uD800-\uDBFF]/.test(text[i-1])&&/[\uDC00-\uDFFF]/.test(text[i])?-1:Math.round(ctx.measureText(text.slice(0,i)).width));const row={start,text,positions};start+=text.length+1;return row;});result={text:a.text,insetX:10,insetY:4,ascent:14,height:17,lineHeight:21,lines};}break;
 case 'native':result=native(a);break;
 case 'close':events.length=0;ctx.clearRect(0,0,canvas.width,canvas.height);break;
 default:throw Error('Unsupported platform operation '+operation);
 }return typeof result==='string'?result:JSON.stringify(result);}
const runtime=await dotnet.create();runtime.setModuleImports('confectory.browser.platform',{request,run:token=>{loops.add(token);requestAnimationFrame(function tick(){if(!loops.has(token))return;try{if(bridge.Step(token))requestAnimationFrame(tick);else loops.delete(token);}catch(e){loops.delete(token);console.error(e);}});}});runtime.setModuleImports('confectory.browser.dom',{render:()=>{throw Error('Alternate demo rendering is not a same-editor provider');}});const config=runtime.getConfig(),exports=await runtime.getAssemblyExports(config.mainAssemblyName);bridge=exports.Confectory.Browser.Bridge;const result=bridge.Initialize();globalThis.confectoryPlatform={bridge,events,hosts,loops,canvas,request,result,get presented(){return presented}};addEventListener('pagehide',()=>bridge.Close());
