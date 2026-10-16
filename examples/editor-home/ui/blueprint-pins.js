// Pin gestures prepare existing form inputs; Apply retains the ordinary CAS path.
export function mountBlueprintPins({w,data,api,show,list}){
 const {$,$$,esc}=api,events=new AbortController();let wire=null,menu=null,menuEvents=null,preview=null,gesture=null,skipClick=false;
 const current=()=>api.current.projectId===w.blueprintScope&&w.blueprintData===data&&w.el.isConnected&&!w.el.hidden;
 function closeMenu(){menuEvents?.abort();menuEvents=null;menu?.remove();menu=null;}
 function clear(){closeMenu();if(gesture){const g=gesture;gesture=null;g.owner.onpointermove=g.owner.onpointerup=g.owner.onpointercancel=null;if(g.owner.hasPointerCapture(g.id))g.owner.releasePointerCapture(g.id);}wire=null;preview?.remove();preview=null;for(const el of $$('[aria-pressed="true"][data-bp-exec-out],[aria-pressed="true"][data-bp-exec-start]',w.body))el.setAttribute('aria-pressed','false');}
 function selected(id,method,...args){if(!current())return;if(w.meta.blueprintNode!==id){w.meta.blueprintNode=id;show(data,w.meta,list);return w.blueprintPins[method](...args);}return false;}
 function stage(kind,node,name,value){
  if(!current())return;if(node&&w.meta.blueprintNode!==node){selected(node,'stage',kind,node,name,value);return;}
  const selector=kind==='entry'?'[data-bp-entry]':kind==='route'?'[data-bp-route="'+CSS.escape(name)+'"]':'[data-bp-argument="'+CSS.escape(name)+'"]';
  const input=$(selector,w.body);if(!input)return;input.value=value;input.oninput();input.focus({preventScroll:true});api.toast('연결 값을 입력에 준비했습니다. 적용과 검토는 별도입니다.');
 }
 function popup(anchor,title,rows){
  closeMenu();menu=document.createElement('section');menu.className='bp-pin-menu';menu.setAttribute('role','dialog');menu.setAttribute('aria-label',title);menu.innerHTML='<strong>'+esc(title)+'</strong><p>기존 계약의 값을 선택해 입력에 준비합니다. 적용·검토는 별도입니다.</p>'+rows.map((row,i)=>'<button type="button" data-pin-choice="'+i+'">'+esc(row.label)+'</button>').join('')+'<button type="button" data-pin-close>취소</button>';document.body.append(menu);const rect=anchor.getBoundingClientRect();Object.assign(menu.style,{left:Math.max(8,Math.min(rect.left,innerWidth-menu.offsetWidth-8))+'px',top:Math.max(8,Math.min(rect.bottom+6,innerHeight-menu.offsetHeight-8))+'px'});menuEvents=new AbortController();
  for(const button of $$('[data-pin-choice]',menu))button.onclick=()=>{if(!current()){closeMenu();return;}const row=rows[Number(button.dataset.pinChoice)];closeMenu();row.choose();};$('[data-pin-close]',menu).onclick=closeMenu;
  document.addEventListener('pointerdown',e=>{if(menu&&!menu.contains(e.target)&&!anchor.contains(e.target))closeMenu();},{capture:true,signal:menuEvents.signal});menu.addEventListener('keydown',e=>{if(e.key==='Escape'){e.preventDefault();e.stopPropagation();closeMenu();anchor.focus({preventScroll:true});}});$('[data-pin-choice],[data-pin-close]',menu).focus({preventScroll:true});
 }
 function pickInput(nodeId,name){
  if(w.meta.blueprintNode!==nodeId){selected(nodeId,'pickInput',nodeId,name);return;}
  const node=data.nodes.find(n=>n.id===nodeId),arg=node?.signature.args.find(a=>a.name===name);if(!arg)return;clear();
  const rows=[...data.signature.args.filter(a=>a.type===arg.type).map(a=>({label:'입력 '+a.name+' · '+a.type,choose:()=>stage('argument',nodeId,name,JSON.stringify({input:a.name}))})),...data.nodes.filter(n=>n.id!==nodeId&&n.signature.return===arg.type).map(n=>({label:n.id+' 결과 · '+arg.type,choose:()=>stage('argument',nodeId,name,JSON.stringify({node:n.id}))})),{label:'직접 JSON 입력 · 현재 값 유지',choose:()=>{$('[data-bp-argument="'+CSS.escape(name)+'"]',w.body)?.focus({preventScroll:true});}}];
  popup($('[data-bp-input-pin="'+CSS.escape(nodeId)+'"][data-pin-name="'+CSS.escape(name)+'"]',w.body),name+' 입력 값',rows);
 }
 function output(anchor,value,type){clear();const rows=data.nodes.flatMap(n=>value.node===n.id?[]:n.signature.args.filter(a=>a.type===type).map(a=>({label:n.id+' · '+a.name+' 입력',choose:()=>stage('argument',n.id,a.name,JSON.stringify(value))})));popup(anchor,'결과를 연결할 입력',rows.length?rows:[{label:'같은 타입의 다른 입력이 없습니다',choose:()=>{}}]);}
 function start(from,port){
  if(!current())return;if(from&&w.meta.blueprintNode!==from){selected(from,'start',from,port);return;}
  closeMenu();if(wire?.from===from&&wire?.port===port){clear();return;}clear();wire={from,port};const button=from?$('[data-bp-exec-out="'+CSS.escape(from)+'"][data-exec-port="'+port+'"]',w.body):$('[data-bp-exec-start]',w.body);button?.setAttribute('aria-pressed','true');api.toast('실행을 연결할 상단바 또는 기존 반환 경로를 선택하세요. Escape로 취소합니다.');
 }
 function connect(to){if(!wire||!current())return;if(wire.from===to){api.toast('현재 profile에서는 같은 노드로 되돌아가는 실행선을 만들 수 없습니다.');return;}const from=wire.from,port=wire.port;clear();if(from)stage('route',from,port,to);else stage('entry',null,'',to);}
 function begin(event,from,port){
  if(event.button!==0||!current())return;event.preventDefault();event.stopPropagation();
  if(from&&w.meta.blueprintNode!==from){selected(from,'begin',event,from,port);return;}
  start(from,port);skipClick=true;const owner=from?$('[data-bp-exec-out="'+CSS.escape(from)+'"][data-exec-port="'+port+'"]',w.body):$('[data-bp-exec-start]',w.body);if(!wire){setTimeout(()=>skipClick=false,0);return;}owner.setPointerCapture(event.pointerId);gesture={owner,id:event.pointerId};
  owner.onpointerup=e=>{if(e.pointerId!==event.pointerId)return;const target=document.elementFromPoint(e.clientX,e.clientY),exit=target?.closest('[data-bp-exec-exit]'),header=target?.closest('[data-bp-exec-target]'),g=gesture;gesture=null;owner.onpointerup=owner.onpointercancel=null;if(g&&owner.hasPointerCapture(g.id))owner.releasePointerCapture(g.id);if(exit&&w.body.contains(exit))connect('exit:'+exit.dataset.bpExecExit);else if(header&&w.body.contains(header)&&header.dataset.bpExecTarget!==from)connect(header.dataset.bpExecTarget);setTimeout(()=>skipClick=false,0);};
  owner.onpointercancel=()=>{clear();skipClick=false;};
 }
 for(const button of $$('[data-bp-exec-out]',w.body)){button.onpointerdown=e=>begin(e,button.dataset.bpExecOut,button.dataset.execPort);button.onclick=e=>{e.stopPropagation();if(!skipClick)start(button.dataset.bpExecOut,button.dataset.execPort);};}
 $('[data-bp-exec-start]',w.body).onpointerdown=e=>begin(e,null,'next');$('[data-bp-exec-start]',w.body).onclick=e=>{e.stopPropagation();if(!skipClick)start(null,'next');};
 for(const header of $$('[data-bp-exec-target]',w.body))header.onclick=e=>{if(wire&&!e.target.closest('button,input,textarea,select')){e.preventDefault();e.stopPropagation();connect(header.dataset.bpExecTarget);}};
 for(const button of $$('[data-bp-exec-in],[data-bp-exec-exit]',w.body))button.onclick=e=>{e.stopPropagation();if(wire)connect(button.dataset.bpExecIn||'exit:'+button.dataset.bpExecExit);else api.toast('먼저 실행 출력 핀을 선택하세요.');};
 for(const button of $$('[data-bp-input-pin]',w.body))button.onclick=e=>{e.stopPropagation();pickInput(button.dataset.bpInputPin,button.dataset.pinName);};
 for(const button of $$('[data-bp-output-pin]',w.body))button.onclick=e=>{e.stopPropagation();const node=data.nodes.find(n=>n.id===button.dataset.bpOutputPin);output(button,{node:node.id},node.signature.return);};
 for(const button of $$('[data-bp-feature-pin]',w.body))button.onclick=e=>{e.stopPropagation();const arg=data.signature.args.find(a=>a.name===button.dataset.bpFeaturePin);output(button,{input:arg.name},arg.type);};
 const viewport=$('.bp-scroll',w.body);viewport.addEventListener('pointermove',e=>{if(!wire||!current())return;const source=wire.from?$('[data-bp-exec-out="'+CSS.escape(wire.from)+'"][data-exec-port="'+wire.port+'"]',w.body):$('[data-bp-exec-start]',w.body);if(!preview){preview=document.createElementNS('http://www.w3.org/2000/svg','svg');preview.classList.add('bp-wire-preview');preview.innerHTML='<path/>';viewport.append(preview);}const r=viewport.getBoundingClientRect(),s=source.getBoundingClientRect(),fx=r.width/viewport.offsetWidth||1,fy=r.height/viewport.offsetHeight||1,x=(s.right-r.left)/fx,y=(s.top+s.height/2-r.top)/fy,tx=(e.clientX-r.left)/fx,ty=(e.clientY-r.top)/fy;preview.querySelector('path').setAttribute('d',`M${x} ${y} C${x+35} ${y},${tx-35} ${ty},${tx} ${ty}`);},{signal:events.signal});
 return {begin,start,stage,pickInput,hasWire:()=>!!wire,clear,dispose(){clear();closeMenu();events.abort();}};
}
