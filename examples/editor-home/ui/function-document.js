// A second view of the checked graph and the existing private input model.
// View folds never enter authorInputs, source plans, or the source Undo stack.
export function functionDocumentTree(model){
 const byId=new Map(model.nodes.map(node=>[node.id,node])),visited=new Set(),main=new Set();
 const next=(id,port='next')=>model.links.find(link=>link.from===id&&link.port===port)?.to;
 for(let id='$entry';byId.has(id)&&!main.has(id);id=next(id))main.add(id);
 function sequence(id,branch=false){
  const result=[];
  while(byId.has(id)){
   const node=byId.get(id);
   if(visited.has(id)||branch&&main.has(id)){result.push({reference:node});break;}
   visited.add(id);
   result.push({node,branches:(node.branches||[]).map(port=>({...port,cells:sequence(next(id,port.id),true)}))});
   if(node.terminal)break;
   id=next(id);
  }
  return result;
 }
 const cells=sequence('$entry'),detached=[];
 for(const node of model.nodes)if(!visited.has(node.id))detached.push(...sequence(node.id));
 return {cells,detached};
}

export function mountFunctionDocument(root,api){
 // An unconverted native body is still the explicit legacy conversion surface.
 // It is never relabelled as a logical definition or silently converted here.
 if(api.nativeDefinition)return null;
 if(!document.head.querySelector('[data-function-document-style]')){
  const style=document.createElement('link');style.rel='stylesheet';style.href=new URL('./function-document.css',import.meta.url).href;style.dataset.functionDocumentStyle='';document.head.append(style);
 }
 const esc=api.esc,events=new AbortController(),context=api.context,views=Object.assign(Object.create(null),api.view.meta.functionDocumentViews||{});
 const prior=Object.hasOwn(views,context)?views[context]:null,state={mode:['logic','blueprint','native'].includes(prior?.mode)?prior.mode:api.initialMode==='blueprint'?'blueprint':'logic',cells:{...prior?.cells},groups:{...prior?.groups},tabs:{...prior?.tabs},scroll:Number.isFinite(prior?.scroll)?Math.max(0,prior.scroll):0};
 let destroyed=false,frame=0,activated=false,previewRequest=0,previewVersion=null,drag=null,pointerType=null;
 const owns=()=>!destroyed&&root.isConnected&&!api.view.el.hidden&&api.owns();
 const nav=document.createElement('nav');nav.className='fd-view-tabs';nav.setAttribute('role','tablist');nav.setAttribute('aria-label','기능 보기');
 nav.innerHTML='<button type="button" role="tab" data-function-view="logic">논리 코드</button><button type="button" role="tab" data-function-view="native">네이티브 미리보기</button><button type="button" role="tab" data-function-view="blueprint">블루프린트 보기</button>';
 root.querySelector('.bp-toolbar').after(nav);
 const host=document.createElement('section');host.className='function-document';host.tabIndex=-1;host.setAttribute('role','tabpanel');host.setAttribute('aria-label','논리 코드');root.append(host);
 const preview=document.createElement('section');preview.className='function-native-preview';preview.hidden=true;preview.setAttribute('role','tabpanel');preview.setAttribute('aria-label','네이티브 미리보기');root.append(preview);
 root.classList.add('has-function-document');
 function persist(){
  if(!owns())return;
  views[context]=structuredClone(state);
  while(Object.keys(views).length>64)delete views[Object.keys(views).find(key=>key!==context)];
  api.view.meta.functionDocumentViews=views;api.persist();
 }
 const dragType='application/x-confectory-document-cell',marker=document.createElement('div');marker.className='fd-cell-drop-marker';marker.setAttribute('aria-label','셀 배치 위치');marker.innerHTML='<span>여기에 놓기</span>';
 const clearDrop=()=>{marker.remove();if(drag)drag.slot=null;};
 const cancelDrag=()=>{clearDrop();drag=null;pointerType=null;host.classList.remove('fd-cell-dragging');};
 const currentDrag=()=>{const now=drag&&api.cellDrag?.(drag.id);return !!now&&owns()&&state.mode==='logic'&&now.scope===drag.binding.scope&&now.version===drag.binding.version;};
 const fieldLabel=field=>esc(field.name||field.id)+' <small>'+esc((field.type||field.nativeType||'')+(field.multi?'[]':''))+'</small>';
 const dragTitle=actions=>{
  if(!actions?.drag)return '현재 입력과 편집 문맥에서는 드래그할 수 없습니다. 기존 입력은 유지됩니다.';
  if(actions.cross&&actions.transfer)return '주 흐름이나 열린 분기의 셀 앞뒤에 놓아 실행 위치를 옮깁니다. 다른 분기의 탭에 놓으면 그 분기 끝으로 이동합니다.';
  if(actions.cross)return '주 흐름이나 열린 분기의 셀 앞뒤에 놓아 실행 위치를 옮깁니다.';
  if(actions.transfer)return '다른 분기 탭에 놓으면 그 분기 끝으로 이동합니다. 같은 분기는 Alt+↑/↓로 이동할 수 있습니다.';
  return '같은 흐름 안에서 끌어 이동 · Alt+↑/↓';
 };
 // Keep the active text/caret while pending input changes action eligibility.
 function syncActions(){
  for(const button of host.querySelectorAll('[data-document-up],[data-document-down],[data-document-add]')){
   const kind=button.hasAttribute('data-document-up')?'up':button.hasAttribute('data-document-down')?'down':'add',id=button.dataset.documentUp||button.dataset.documentDown||button.dataset.documentAdd,actions=api.cellActions?.(id);button.disabled=actions?.[kind]!==true;button.title=button.disabled?actions?.reason||'기존 입력과 현재 실행 범위를 먼저 확인해 주세요.':'';
  }
  for(const button of host.querySelectorAll('[data-document-remove]'))button.disabled=api.cellActions?.(button.dataset.documentRemove)?.remove!==true;
  for(const button of host.querySelectorAll('[data-document-drag]')){const actions=api.cellActions?.(button.dataset.documentDrag);button.disabled=!actions?.drag;button.draggable=!!actions?.drag;button.title=dragTitle(actions);}
  for(const button of host.querySelectorAll('[data-document-branch-add]'))button.disabled=api.branchActions?.(button.dataset.documentOwner,button.dataset.documentBranchAdd)?.add!==true;
 }
 function render(){
  if(!owns()||state.mode!=='logic')return;if(pointerType==='mouse'&&!drag)return;if(drag){if(currentDrag())return;cancelDrag();}
  const model=api.model(),tree=functionDocumentTree(model);
  const fields=(node,side)=>{
   if(side==='inputs'&&node.branchExitChoice!==undefined)return '<div class="fd-pin"><span>반환할 분기</span><button type="button" data-document-branch-exit="'+esc(node.id)+'" aria-haspopup="listbox" aria-expanded="false">'+esc(node.branchExitChoice)+'</button></div>';
   const values=side==='inputs'?api.values(node.id):[];
   const declared=node.id==='$entry'?(side==='inputs'?model.inputs:model.outputs):side==='inputs'?node.inputs:node.outputs;
   if(side==='inputs'&&node.kind==='export')return values.map(field=>'<div class="fd-pin"><span>'+fieldLabel(field)+'</span><button type="button" data-document-value="'+esc(node.id)+'" data-document-port="'+esc(field.port)+'">'+esc(field.text||'값 선택')+'</button></div>').join('');
   return (declared||[]).map(field=>{
    const value=values.find(value=>value.port==='field:'+field.id);
    return '<div class="fd-pin"><span>'+fieldLabel(field)+'</span>'+(value?'<button type="button" data-document-value="'+esc(node.id)+'" data-document-port="'+esc(value.port)+'">'+esc(value.text||'값 선택')+'</button>':'')+'</div>';
   }).join('')||'<span class="fd-empty">'+(side==='inputs'?'입력 없음':'출력 없음')+'</span>';
  };
  const cells=items=>items.map(item=>{
   if(item.reference)return '<div class="fd-reference">↪ '+esc(item.reference.name)+'</div>';
   const {node,branches}=item,actions=api.cellActions?.(node.id),folded=state.cells[node.id]===true,selected=branches.some(branch=>branch.id===state.tabs[node.id])?state.tabs[node.id]:branches[0]?.id,groupFolded=state.groups[node.id]===true;
   const cellState=node.contractReviewRequired?'계약 확인 필요':({entry:'입력',action:'동작',call:'참조',export:'출력','branch-exit':'분기 반환',set:'저장',property:'속성'}[node.kind]||'동작');
   const addAtStart=node.id==='$entry'&&actions?.showAdd?'<div class="fd-cell-actions"><button type="button" data-document-add="$entry" '+(actions.add?'':'disabled title="기존 입력과 현재 실행 범위를 먼저 확인해 주세요."')+'>이 아래에 동작 추가</button></div>':'';
   const setTarget=api.hasSetTarget?.(node.id)?'<label class="bp-set-target">저장 대상<select aria-label="저장 대상" data-document-set-target="'+esc(node.id)+'"></select></label>':'';
   return '<article class="fd-cell" data-document-cell="'+esc(node.id)+'"><header class="fd-cell-header"><button type="button" data-document-fold="'+esc(node.id)+'" aria-label="'+esc(node.name)+' '+(folded?'펼치기':'접기')+'" aria-expanded="'+!folded+'">'+(folded?'▸':'▾')+'</button>'+(node.readonly||node.id==='$entry'?'<strong class="fd-cell-title">'+esc(node.name)+'</strong>':'<input class="fd-cell-title" data-document-name="'+esc(node.id)+'" aria-label="동작 이름" value="'+esc(node.name)+'">')+'<span class="fd-cell-state"'+(node.contractReviewRequired?' title="원본 기능의 입출력 계약이 바뀌었습니다."':'')+'>'+esc(cellState)+'</span><button type="button" class="fd-cell-grip" data-document-drag="'+esc(node.id)+'" '+(actions?.drag?'draggable="true"':'disabled')+' aria-label="'+esc(node.name)+' 셀 이동" title="'+esc(dragTitle(actions))+'">⠿</button>'+(actions?.remove?'<button type="button" data-document-remove="'+esc(node.id)+'" aria-label="'+esc(node.name)+' 셀 삭제" title="실행 흐름에서 셀 삭제 · C# 원본 유지 · Ctrl+Z로 취소">×</button>':'')+'</header><div class="fd-cell-content" '+(folded?'hidden':'')+'><div class="fd-cell-io"><section class="fd-inputs" aria-label="셀 입력">'+fields(node,'inputs')+'</section><section class="fd-outputs" aria-label="셀 출력">'+fields(node,'outputs')+'</section></div>'+setTarget+addAtStart+(node.id!=='$entry'&&!node.terminal?'<div class="fd-cell-actions">'+(actions?'<button type="button" data-document-up="'+esc(node.id)+'" '+(actions.up?'':'disabled title="'+esc(actions.reason||'현재 분기의 첫 셀입니다.')+'"')+'>위로</button><button type="button" data-document-down="'+esc(node.id)+'" '+(actions.down?'':'disabled title="'+esc(actions.reason||'현재 분기의 마지막 셀입니다.')+'"')+'>아래로</button><button type="button" data-document-add="'+esc(node.id)+'" '+(actions.add?'':'disabled title="'+esc(actions.reason||'현재 문맥의 추가는 지원하지 않습니다.')+'"')+'>이 아래에 동작 추가</button>':'')+(node.codeEditable?'<button type="button" data-document-code="'+esc(node.id)+'">네이티브 코드 편집</button>':'')+(node.internal?'<button type="button" data-document-internal="'+esc(node.id)+'">내부 흐름</button>':'')+(node.kind==='call'?'<button type="button" data-document-source="'+esc(node.id)+'">원본 열기</button>':'')+'</div>':'')+(branches.length?'<section class="fd-branches"><nav class="fd-branch-tabs" aria-label="실행 분기"><button type="button" data-document-group="'+esc(node.id)+'" aria-label="분기 내용 '+(groupFolded?'펼치기':'접기')+'" aria-expanded="'+!groupFolded+'">'+(groupFolded?'▸':'▾')+'</button>'+branches.map(branch=>'<button type="button" data-document-branch="'+esc(branch.id)+'" data-document-owner="'+esc(node.id)+'" aria-pressed="'+(branch.id===selected)+'">'+esc(branch.name)+'</button>').join('')+'</nav>'+branches.map(branch=>'<div class="fd-branch-panel" data-document-panel="'+esc(branch.id)+'" '+(groupFolded||branch.id!==selected?'hidden':'')+'>'+('<button type="button" data-document-branch-add="'+esc(branch.id)+'" data-document-owner="'+esc(node.id)+'" '+(api.branchActions?.(node.id,branch.id)?.add?'':'disabled title="미저장 입력을 먼저 저장하거나 기존 분기·공유·소유 범위를 확인해 주세요."')+'>이 분기에 동작 추가</button>')+cells(branch.cells)+'</div>').join('')+'</section>':'')+'</div></article>';
  }).join('');
  const scroll=host.scrollTop;
  host.innerHTML='<div class="fd-document-title">'+esc(model.name)+'</div>'+cells(tree.cells)+(tree.detached.length?'<section class="fd-detached"><h3>별도 셀</h3>'+cells(tree.detached)+'</section>':'');
  host.scrollTop=scroll;
  for(const button of host.querySelectorAll('[data-document-fold]'))button.onclick=()=>{if(!owns()||api.closeValues('preserve')===false)return;const id=button.dataset.documentFold;state.cells[id]=state.cells[id]!==true;persist();render();};
  for(const button of host.querySelectorAll('[data-document-group]'))button.onclick=()=>{if(!owns()||api.closeValues('preserve')===false)return;const id=button.dataset.documentGroup;state.groups[id]=state.groups[id]!==true;persist();render();};
  for(const button of host.querySelectorAll('[data-document-branch]'))button.onclick=()=>{if(!owns()||api.closeValues('preserve')===false)return;state.tabs[button.dataset.documentOwner]=button.dataset.documentBranch;persist();render();};
  for(const input of host.querySelectorAll('[data-document-name]'))input.oninput=()=>{if(owns()){api.write(input.dataset.documentName,'rename',input.value);syncActions();}};
  for(const control of host.querySelectorAll('[data-document-set-target]'))api.mountSetTarget(control.dataset.documentSetTarget,control);
  for(const button of host.querySelectorAll('[data-document-value]'))button.onclick=()=>{if(owns())api.editValue(button.dataset.documentValue,button.dataset.documentPort,button);};
  for(const button of host.querySelectorAll('[data-document-branch-exit]'))button.onclick=()=>{if(owns())api.pickBranchExit(button.dataset.documentBranchExit,button);};
  for(const button of host.querySelectorAll('[data-document-code]'))button.onclick=()=>{if(owns())api.code(button.dataset.documentCode);};
  for(const button of host.querySelectorAll('[data-document-internal]'))button.onclick=()=>{if(owns())api.internal(button.dataset.documentInternal);};
  for(const button of host.querySelectorAll('[data-document-drag]')){
   button.onpointerdown=event=>{event.stopPropagation();pointerType=event.pointerType;};
   button.ondragstart=event=>{
    if(pointerType!=='mouse'||!owns()||api.closeValues('preserve')===false){event.preventDefault();return;}
    const id=button.dataset.documentDrag,binding=api.cellDrag?.(id);if(!binding){event.preventDefault();return;}
    event.stopPropagation();cancelDrag();drag={id,binding,parent:button.closest('[data-document-cell]').parentElement,token:crypto.randomUUID(),slot:null};host.classList.add('fd-cell-dragging');event.dataTransfer.effectAllowed='move';event.dataTransfer.setData(dragType,drag.token);
   };
   button.ondragend=()=>{cancelDrag();render();};
   button.onkeydown=event=>{if(!event.isComposing&&event.altKey&&['ArrowUp','ArrowDown'].includes(event.key)){event.preventDefault();event.stopPropagation();cancelDrag();if(owns())api.moveCell(button.dataset.documentDrag,event.key==='ArrowUp'?-1:1,button);}};
  }
  for(const button of host.querySelectorAll('[data-document-remove]'))button.onclick=()=>{if(owns())api.removeCell(button.dataset.documentRemove,button);};
  for(const button of host.querySelectorAll('[data-document-up]'))button.onclick=()=>{if(owns())api.moveCell(button.dataset.documentUp,-1);};
  for(const button of host.querySelectorAll('[data-document-down]'))button.onclick=()=>{if(owns())api.moveCell(button.dataset.documentDown,1);};
  for(const button of host.querySelectorAll('[data-document-add]'))button.onclick=()=>{if(owns())api.addCell(button.dataset.documentAdd);};
  for(const button of host.querySelectorAll('[data-document-branch-add]'))button.onclick=()=>{if(owns())api.addBranch(button.dataset.documentOwner,button.dataset.documentBranchAdd);};
  for(const button of host.querySelectorAll('[data-document-source]'))button.onclick=()=>{if(owns())api.source(button.dataset.documentSource);};
 }
 function dropPosition(event){
  if(!currentDrag()){cancelDrag();return null;}
  const tab=event.target.closest('[data-document-branch]');
  if(tab){
   const transfer=drag.binding.transfer;
   if(!transfer||tab.dataset.documentBranch!==transfer.port||tab.dataset.documentOwner!==transfer.owner)return null;
   if(!api.canDropCell?.(drag.id,null,drag.binding,transfer))return null;
   const rect=tab.getBoundingClientRect(),bounds=host.getBoundingClientRect();
   if(rect.bottom>bounds.bottom||rect.bottom<bounds.top||rect.left<bounds.left||rect.right>bounds.right)return null;
   return {slot:null,transfer,x:rect.left,y:rect.bottom,width:rect.width};
  }
  const target=event.target.closest('[data-document-cell]'),parent=drag.parent;
  const empty=event.target.closest('[data-document-branch-add]');
  const area=empty?.parentElement||target?.parentElement;
  if(drag.binding.cross&&area&&area!==parent){
   const {owner,lanes}=drag.binding.cross,anchor=empty?'$empty':target.dataset.documentCell;
   const panel=area.dataset.documentPanel,box=(empty||target).getBoundingClientRect();
   const side=empty||event.clientY<box.top+box.height/2?'before':'after';
   let lane;
   if(panel&&area.closest('[data-document-cell]')?.dataset.documentCell===owner){
    lane=lanes.find(row=>row.id===panel&&(row.order.includes(anchor)||empty&&!row.order.length));
   }else if(area===host){
    lane=lanes.find(row=>row.order.includes(anchor)||row.id==='root-before'&&anchor===owner&&side==='before'
     &&event.target.closest('.fd-cell-header')?.parentElement===target
     ||row.id==='root-after'&&anchor===row.anchor&&side==='after');
   }
   if(lane){
    const transfer={lane:lane.id,anchor,side};
    if(!api.canDropCell?.(drag.id,null,drag.binding,transfer))return null;
    const bounds=host.getBoundingClientRect(),y=side==='before'?box.top-3:box.bottom+3;
    if(y<bounds.top+3||y>bounds.bottom-3)return null;
    return {slot:null,transfer,x:Math.max(bounds.left+5,box.left),y,width:Math.min(bounds.right-5,box.right)-Math.max(bounds.left+5,box.left)};
   }
  }
  if(!parent.isConnected||target&&target.parentElement!==parent||!target&&!parent.contains(event.target))return null;
  if(target&&!drag.binding.order.includes(target.dataset.documentCell)&&!(parent===host&&['$entry','$'+drag.binding.exit].includes(target.dataset.documentCell)))return null;
  const cells=drag.binding.order.map(id=>Array.from(parent.children).find(el=>el.dataset.documentCell===id));if(cells.some(el=>!el))return null;
  let slot=cells.findIndex(el=>{const r=el.getBoundingClientRect();return event.clientY<r.top+r.height/2;});if(slot<0)slot=cells.length;
  if(!api.canDropCell?.(drag.id,slot,drag.binding))return null;
  const anchor=cells[Math.min(slot,cells.length-1)],rect=anchor.getBoundingClientRect(),bounds=host.getBoundingClientRect(),y=slot<cells.length?rect.top-5:rect.bottom+5;
  if(event.clientX<rect.left||event.clientX>rect.right||y<bounds.top+3||y>bounds.bottom-3)return null;
  return {slot,x:Math.max(rect.left,bounds.left+5),y,width:Math.min(rect.right,bounds.right-5)-Math.max(rect.left,bounds.left+5)};
 }
 host.addEventListener('dragover',event=>{
  if(!drag||!Array.from(event.dataTransfer.types).includes(dragType))return;event.preventDefault();event.stopPropagation();clearDrop();const target=dropPosition(event);event.dataTransfer.dropEffect=target?'move':'none';if(!target)return;drag.slot=target.slot;
  const lane=target.transfer?.lane,branch=lane?.startsWith('case:');
  marker.toggleAttribute('data-branch-transfer',!!target.transfer&&!lane);
  if(lane)marker.dataset.scopeTransfer=branch?'case':'root';else delete marker.dataset.scopeTransfer;
  marker.firstElementChild.textContent=lane?(branch?'분기 안에 놓기':'주 흐름에 놓기'):target.transfer?'분기 끝에 놓기':'여기에 놓기';
  Object.assign(marker.style,{left:target.x+'px',top:target.y+'px',width:target.width+'px'});document.body.append(marker);
 },{signal:events.signal});
 host.addEventListener('drop',event=>{
  if(!drag||!Array.from(event.dataTransfer.types).includes(dragType))return;event.preventDefault();event.stopPropagation();const token=event.dataTransfer.getData(dragType),target=dropPosition(event),moving=drag;cancelDrag();if(target&&token===moving?.token)api.dropCell?.(moving.id,target.slot,moving.binding,target.transfer);else render();
 },{signal:events.signal});
 host.addEventListener('dragleave',event=>{if(drag&&!host.contains(event.relatedTarget))clearDrop();},{signal:events.signal});
 window.addEventListener('keydown',event=>{if(drag&&event.key==='Escape'){event.preventDefault();event.stopPropagation();cancelDrag();render();}},{capture:true,signal:events.signal});
 window.addEventListener('pointerup',()=>{if(pointerType!==null){pointerType=null;if(!drag)render();}},{signal:events.signal});
 window.addEventListener('pointercancel',()=>{if(!drag&&pointerType!==null){cancelDrag();render();}},{signal:events.signal});
 window.addEventListener('blur',()=>{if(drag||pointerType!==null){cancelDrag();render();}},{signal:events.signal});
 async function generate(){
  const request=++previewRequest;previewVersion=api.nativeVersion?.();
  preview.innerHTML='<div class="fd-native-tools"><span role="status">생성 중…</span><button type="button" data-native-refresh>갱신</button></div><p class="fd-native-scope">'+esc(api.nativeScope?.()||'선택한 함수의 C# 본문·멤버 스냅샷 · 읽기 전용 · 컴파일·실행 검증 전')+'</p><pre data-native-body tabindex="0" aria-label="생성된 C# 본문"></pre><pre data-native-members tabindex="0" aria-label="생성된 C# 멤버" hidden></pre>';
  preview.querySelector('[data-native-refresh]').onclick=()=>{if(owns())generate();};
  try{
   const result=await api.previewNative();if(!owns()||state.mode!=='native'||request!==previewRequest)return;
   if(previewVersion!==api.nativeVersion?.())throw Error('소스가 바뀌어 결과가 오래됐습니다. 갱신해 주세요.');
   preview.querySelector('[data-native-body]').textContent=result.body;
   const members=preview.querySelector('[data-native-members]');members.textContent=result.members;members.hidden=!result.members;
   preview.querySelector('[role=status]').textContent='생성됨 · '+result.bodyHash;
  }catch(error){if(owns()&&state.mode==='native'&&request===previewRequest){preview.querySelector('[data-native-body]').textContent='';preview.querySelector('[data-native-members]').textContent='';preview.querySelector('[data-native-members]').hidden=true;preview.querySelector('[role=status]').textContent=error.message==='consumer_error'?'네이티브 생성에 실패했습니다. 소스 충돌과 지원 문맥을 확인해 주세요. 원본과 입력은 유지됩니다.':error.message||'생성하지 못했습니다. 원본과 입력은 유지됩니다.';}}
 }
 // openWindow may render while hidden. Set view DOM now and activate its
 // model/callbacks after the current owner becomes visible.
 function mode(next,initial=false){
  cancelDrag();
  if(destroyed||!['logic','native','blueprint'].includes(next)||!initial&&(!owns()||api.closeValues('preserve')===false||!owns()))return;
  state.mode=next;host.hidden=next!=='logic';preview.hidden=next!=='native';root.classList.toggle('fd-logic',next!=='blueprint');previewRequest++;
  root.querySelector('.bp-layout').inert=next!=='blueprint';
  for(const button of nav.querySelectorAll('[data-function-view]'))button.setAttribute('aria-selected',String(button.dataset.functionView===next));
  if(owns()){activated=true;api.switchView?.(next);if(next==='logic'){render();host.scrollTop=state.scroll;}else if(next==='native')generate();else api.graph();}
  if(!initial)persist();
 }
 for(const button of nav.querySelectorAll('[data-function-view]:not(:disabled)'))button.onclick=()=>mode(button.dataset.functionView);
 host.addEventListener('scroll',()=>{if(drag)clearDrop();if(owns()&&state.mode==='logic'){state.scroll=host.scrollTop;persist();}},{passive:true,signal:events.signal});
 host.addEventListener('keydown',event=>{
  if(!owns()||event.isComposing||event.keyCode===229||!(event.ctrlKey||event.metaKey))return;
  const key=event.key.toLowerCase();if(key==='s'){event.preventDefault();event.stopPropagation();if(api.closeValues()!==false)api.save();}
  else if(['z','y'].includes(key)&&!event.target.closest('input,textarea,select')){event.preventDefault();event.stopPropagation();api.undo(key==='y'||event.shiftKey);}
 },{signal:events.signal});
 root.addEventListener('input',()=>{if(owns()&&state.mode==='native'&&preview.querySelector('[data-native-body]')&&previewVersion!==api.nativeVersion?.()){previewRequest++;previewVersion=api.nativeVersion?.();preview.querySelector('[data-native-body]').textContent='';preview.querySelector('[data-native-members]').textContent='';preview.querySelector('[data-native-members]').hidden=true;preview.querySelector('[role=status]').textContent='입력 또는 소스가 바뀌었습니다. 갱신해 주세요.';}},{signal:events.signal});
 mode(state.mode,true);
 return {get mode(){return state.mode;},remember(){
  if(!owns())return;
  if(state.mode==='logic')state.scroll=host.scrollTop;
  persist();
 },focusDocument(){
  if(owns()&&state.mode==='logic')host.focus({preventScroll:true});
 },focusGrip(id){
  if(!owns()||state.mode!=='logic')return;
  syncActions();
  host.querySelector('[data-document-drag="'+CSS.escape(id)+'"]:enabled')?.focus();
 },refresh(){cancelAnimationFrame(frame);frame=requestAnimationFrame(()=>{if(!owns())return;if(!activated){mode(state.mode,true);return;}if(state.mode==='native'&&previewVersion!==api.nativeVersion?.()){previewRequest++;previewVersion=api.nativeVersion?.();preview.querySelector('[data-native-body]').textContent='';preview.querySelector('[data-native-members]').textContent='';preview.querySelector('[data-native-members]').hidden=true;preview.querySelector('[role=status]').textContent='입력 또는 소스가 바뀌었습니다. 갱신해 주세요.';}if(state.mode==='logic'){syncActions();if(!host.querySelector('input:focus,textarea:focus,button:focus')&&!document.querySelector('.bp-value-menu'))render();}});},destroy(){cancelDrag();destroyed=true;cancelAnimationFrame(frame);events.abort();nav.remove();host.remove();preview.remove();root.classList.remove('fd-logic','has-function-document');}};
}
