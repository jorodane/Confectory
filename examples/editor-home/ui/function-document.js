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
 const prior=Object.hasOwn(views,context)?views[context]:null,state={mode:['blueprint','native'].includes(prior?.mode)?prior.mode:'logic',cells:{...prior?.cells},groups:{...prior?.groups},tabs:{...prior?.tabs},scroll:Number.isFinite(prior?.scroll)?Math.max(0,prior.scroll):0};
 let destroyed=false,frame=0,activated=false,previewRequest=0,previewVersion=null;
 const owns=()=>!destroyed&&root.isConnected&&!api.view.el.hidden&&api.owns();
 const nav=document.createElement('nav');nav.className='fd-view-tabs';nav.setAttribute('role','tablist');nav.setAttribute('aria-label','기능 보기');
 nav.innerHTML='<button type="button" role="tab" data-function-view="logic">논리 코드</button><button type="button" role="tab" data-function-view="native">네이티브 미리보기</button><button type="button" role="tab" data-function-view="blueprint">블루프린트 보기</button>';
 root.querySelector('.bp-toolbar').after(nav);
 const host=document.createElement('section');host.className='function-document';host.tabIndex=-1;host.setAttribute('role','tabpanel');host.setAttribute('aria-label','논리 코드');root.append(host);
 const preview=document.createElement('section');preview.className='function-native-preview function-document';preview.hidden=true;preview.setAttribute('role','tabpanel');preview.setAttribute('aria-label','네이티브 미리보기');root.append(preview);
 root.classList.add('has-function-document');
 function persist(){
  if(!owns())return;
  views[context]=structuredClone(state);
  while(Object.keys(views).length>64)delete views[Object.keys(views).find(key=>key!==context)];
  api.view.meta.functionDocumentViews=views;api.persist();
 }
 const fieldLabel=field=>esc(field.name||field.id)+' <small>'+esc((field.type||field.nativeType||'')+(field.multi?'[]':''))+'</small>';
 function render(){
  if(!owns()||state.mode!=='logic')return;
  const model=api.model(),tree=functionDocumentTree(model);
  const fields=(node,side)=>{
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
   const {node,branches}=item,folded=state.cells[node.id]===true,selected=branches.some(branch=>branch.id===state.tabs[node.id])?state.tabs[node.id]:branches[0]?.id,groupFolded=state.groups[node.id]===true;
   return '<article class="fd-cell" data-document-cell="'+esc(node.id)+'"><header class="fd-cell-header"><button type="button" data-document-fold="'+esc(node.id)+'" aria-label="'+esc(node.name)+' '+(folded?'펼치기':'접기')+'" aria-expanded="'+!folded+'">'+(folded?'▸':'▾')+'</button>'+(node.readonly||node.id==='$entry'?'<strong class="fd-cell-title">'+esc(node.name)+'</strong>':'<input class="fd-cell-title" data-document-name="'+esc(node.id)+'" aria-label="동작 이름" value="'+esc(node.name)+'">')+'<span class="fd-cell-state">'+esc({entry:'입력',action:'동작',call:'참조',export:'출력',set:'저장',property:'속성'}[node.kind]||'동작')+'</span><button type="button" class="fd-cell-grip" disabled aria-label="셀 이동" title="실행 순서는 블루프린트 보기에서 연결하세요.">⠿</button></header><div class="fd-cell-content" '+(folded?'hidden':'')+'><div class="fd-cell-io"><section class="fd-inputs" aria-label="셀 입력">'+fields(node,'inputs')+'</section><section class="fd-outputs" aria-label="셀 출력">'+fields(node,'outputs')+'</section></div>'+(node.id!=='$entry'&&!node.terminal?'<div class="fd-cell-actions">'+(node.codeEditable?'<button type="button" data-document-code="'+esc(node.id)+'">네이티브 코드 편집</button>':'')+(node.internal?'<button type="button" data-document-internal="'+esc(node.id)+'">내부 흐름</button>':'')+(node.kind==='call'?'<button type="button" data-document-source="'+esc(node.id)+'">원본 열기</button>':'')+'</div>':'')+(branches.length?'<section class="fd-branches"><nav class="fd-branch-tabs" aria-label="실행 분기"><button type="button" data-document-group="'+esc(node.id)+'" aria-label="분기 내용 '+(groupFolded?'펼치기':'접기')+'" aria-expanded="'+!groupFolded+'">'+(groupFolded?'▸':'▾')+'</button>'+branches.map(branch=>'<button type="button" data-document-branch="'+esc(branch.id)+'" data-document-owner="'+esc(node.id)+'" aria-pressed="'+(branch.id===selected)+'">'+esc(branch.name)+'</button>').join('')+'</nav>'+branches.map(branch=>'<div class="fd-branch-panel" data-document-panel="'+esc(branch.id)+'" '+(groupFolded||branch.id!==selected?'hidden':'')+'>'+cells(branch.cells)+'</div>').join('')+'</section>':'')+'</div></article>';
  }).join('');
  const scroll=host.scrollTop;
  host.innerHTML='<div class="fd-document-title">'+esc(model.name)+'</div>'+cells(tree.cells)+(tree.detached.length?'<section class="fd-detached"><h3>별도 셀</h3>'+cells(tree.detached)+'</section>':'');
  host.scrollTop=scroll;
  for(const button of host.querySelectorAll('[data-document-fold]'))button.onclick=()=>{if(!owns()||api.closeValues('preserve')===false)return;const id=button.dataset.documentFold;state.cells[id]=state.cells[id]!==true;persist();render();};
  for(const button of host.querySelectorAll('[data-document-group]'))button.onclick=()=>{if(!owns()||api.closeValues('preserve')===false)return;const id=button.dataset.documentGroup;state.groups[id]=state.groups[id]!==true;persist();render();};
  for(const button of host.querySelectorAll('[data-document-branch]'))button.onclick=()=>{if(!owns()||api.closeValues('preserve')===false)return;state.tabs[button.dataset.documentOwner]=button.dataset.documentBranch;persist();render();};
  for(const input of host.querySelectorAll('[data-document-name]'))input.oninput=()=>{if(owns())api.write(input.dataset.documentName,'rename',input.value);};
  for(const button of host.querySelectorAll('[data-document-value]'))button.onclick=()=>{if(owns())api.editValue(button.dataset.documentValue,button.dataset.documentPort,button);};
  for(const button of host.querySelectorAll('[data-document-code]'))button.onclick=()=>{if(owns())api.code(button.dataset.documentCode);};
  for(const button of host.querySelectorAll('[data-document-internal]'))button.onclick=()=>{if(owns())api.internal(button.dataset.documentInternal);};
  for(const button of host.querySelectorAll('[data-document-source]'))button.onclick=()=>{if(owns())api.source(button.dataset.documentSource);};
 }
 async function generate(){
  const request=++previewRequest;previewVersion=api.nativeVersion?.();
  preview.innerHTML='<div class="fd-native-tools"><span role="status">생성 중…</span><button type="button" data-native-refresh>갱신</button></div><p class="fd-native-scope">현재 함수의 엔진 생성 C# 본문 · 읽기 전용 · 컴파일·실행 검증 전</p><pre data-native-body tabindex="0" aria-label="생성된 C# 본문"></pre><pre data-native-members tabindex="0" aria-label="생성된 C# 멤버" hidden></pre>';
  preview.querySelector('[data-native-refresh]').onclick=()=>{if(owns())generate();};
  try{
   const result=await api.previewNative();if(!owns()||state.mode!=='native'||request!==previewRequest)return;
   if(previewVersion!==api.nativeVersion?.())throw Error('소스가 바뀌어 결과가 오래됐습니다. 갱신해 주세요.');
   preview.querySelector('[data-native-body]').textContent=result.body;
   const members=preview.querySelector('[data-native-members]');members.textContent=result.members;members.hidden=!result.members;
   preview.querySelector('[role=status]').textContent='생성됨 · '+result.bodyHash;
  }catch(error){if(owns()&&state.mode==='native'&&request===previewRequest){preview.querySelector('[data-native-body]').textContent='';preview.querySelector('[data-native-members]').hidden=true;preview.querySelector('[role=status]').textContent=error.message||'생성하지 못했습니다. 원본과 입력은 유지됩니다.';}}
 }
 // openWindow may render while hidden. Set view DOM now and activate its
 // model/callbacks after the current owner becomes visible.
 function mode(next,initial=false){
  if(destroyed||!['logic','native','blueprint'].includes(next)||!initial&&(!owns()||api.closeValues('preserve')===false||!owns()))return;
  state.mode=next;host.hidden=next!=='logic';preview.hidden=next!=='native';root.classList.toggle('fd-logic',next!=='blueprint');previewRequest++;
  root.querySelector('.bp-layout').inert=next!=='blueprint';
  for(const button of nav.querySelectorAll('[data-function-view]'))button.setAttribute('aria-selected',String(button.dataset.functionView===next));
  if(owns()){activated=true;api.switchView?.(next);if(next==='logic'){render();host.scrollTop=state.scroll;}else if(next==='native')generate();else api.graph();}
  if(!initial)persist();
 }
 for(const button of nav.querySelectorAll('[data-function-view]:not(:disabled)'))button.onclick=()=>mode(button.dataset.functionView);
 host.addEventListener('scroll',()=>{if(owns()&&state.mode==='logic'){state.scroll=host.scrollTop;persist();}},{passive:true,signal:events.signal});
 host.addEventListener('keydown',event=>{
  if(!owns()||event.isComposing||event.keyCode===229||!(event.ctrlKey||event.metaKey))return;
  const key=event.key.toLowerCase();if(key==='s'){event.preventDefault();event.stopPropagation();if(api.closeValues()!==false)api.save();}
  else if(['z','y'].includes(key)&&!event.target.closest('input,textarea,select')){event.preventDefault();event.stopPropagation();api.undo(key==='y'||event.shiftKey);}
 },{signal:events.signal});
 mode(state.mode,true);
 return {get mode(){return state.mode;},refresh(){cancelAnimationFrame(frame);frame=requestAnimationFrame(()=>{if(!owns())return;if(!activated){mode(state.mode,true);return;}if(state.mode==='native'&&previewVersion!==api.nativeVersion?.()){previewRequest++;previewVersion=api.nativeVersion?.();preview.querySelector('[data-native-body]').textContent='';preview.querySelector('[data-native-members]').hidden=true;preview.querySelector('[role=status]').textContent='입력 또는 소스가 바뀌었습니다. 갱신해 주세요.';}if(state.mode==='logic'&&!host.querySelector('input:focus,textarea:focus')&&!document.querySelector('.bp-value-menu'))render();});},destroy(){destroyed=true;cancelAnimationFrame(frame);events.abort();nav.remove();host.remove();preview.remove();root.classList.remove('fd-logic','has-function-document');}};
}
