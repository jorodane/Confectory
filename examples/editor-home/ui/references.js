// References are scoped text preparation. Existing Apply/CAS and read-only definition gates remain authoritative.
export function createReferenceGestures(api){
 const mime='application/x-confectory-reference';
 const valid=id=>typeof id==='string'&&id.length<=512&&id===id.trim()&&!/[\r\n\0]/.test(id)&&id.split('::').length===2&&id.split('::').every(Boolean);
 function source(element,id){if(!valid(id))return;const scope=api.projectId;element.draggable=true;element.dataset.referenceDrag=id;element.addEventListener('pointerdown',event=>{if(event.button===0)event.stopPropagation();});element.addEventListener('dragstart',event=>{if(api.busy||api.projectId!==scope||!scope){event.preventDefault();return;}event.stopPropagation();event.dataTransfer.setData(mime,JSON.stringify({version:1,projectId:scope,id}));event.dataTransfer.effectAllowed='copy';});element.addEventListener('dragend',event=>event.stopPropagation());}
 function target(input,encode=id=>id){const scope=api.projectId;input.addEventListener('dragover',event=>{if(!input.disabled&&!input.readOnly&&!api.busy&&[...event.dataTransfer.types].includes(mime)){event.preventDefault();event.stopPropagation();event.dataTransfer.dropEffect='copy';}});input.addEventListener('drop',event=>{
  if(![...event.dataTransfer.types].includes(mime))return;event.preventDefault();event.stopPropagation();let value;try{value=JSON.parse(event.dataTransfer.getData(mime));}catch{}
  if(api.busy||input.disabled||input.readOnly||!input.isConnected||api.projectId!==scope||value?.version!==1||value.projectId!==scope||!valid(value.id)){api.toast('유효한 현재 프로젝트 참조가 아닙니다. 입력은 유지됩니다.');return;}
  input.value=encode(value.id);input.dispatchEvent(new Event('input',{bubbles:true}));input.focus({preventScroll:true});api.toast('참조 입력을 준비했습니다. 적용하려면 기존 Apply를 사용하세요.');
 });}
 function link(owner,id,attribute){if(!valid(id))return null;const button=document.createElement('button');button.type='button';button.dataset.operation='reference-link';button.dataset[attribute]=id;button.textContent='현재 참조 열기';button.title='확인한 현재 참조를 엽니다. 미적용 입력을 적용하지 않습니다.';button.onclick=()=>api.open(owner,id);source(button,id);return button;}
 return {source,target,link};
}

// v536 hover is declared inheritance, not generic project or account access.
export function createBrowserReferenceHover(api){
 let active=null,shift=false;
 function close(){active?.tip?.remove();active=null;}
 function draw(){
  if(!active)return;const {anchor,id,scope}=active;
  if(api.projectId!==scope||!anchor.isConnected||!anchor.getClientRects().length){close();return;}
  active.tip?.remove();const rows=api.projection.rows(),row=rows.find(row=>row.id===id),name=id=>rows.find(row=>row.id===id)?.title||id?.split('::').at(-1)||'Root';
  if(!row){close();return;}const refs=shift?api.projection.children(id):rows.filter(value=>value.id===api.projection.parent(id));
  const tip=document.createElement('div');tip.className='object-ref floating-object-ref';tip.setAttribute('role','tooltip');
  const title=document.createElement('strong');title.textContent=shift?'역참조 · Shift + Hover':'참조 · Hover';const info=document.createElement('small');info.textContent='분류: '+name(api.projection.folder(id))+' · ID: '+id.slice(0,12);
  tip.append(title,document.createElement('br'),document.createTextNode(refs.map(row=>name(row.id)).join(' · ')||'연결된 상속 참조 없음'),document.createElement('br'),info);document.body.append(tip);active.tip=tip;
  const r=anchor.getBoundingClientRect(),t=tip.getBoundingClientRect();tip.style.left=Math.max(8,Math.min(r.left,innerWidth-t.width-8))+'px';tip.style.top=Math.max(8,Math.min(r.top-t.height-8>=8?r.top-t.height-8:r.bottom+8,innerHeight-t.height-8))+'px';
 }
 for(const event of ['keydown','keyup'])document.addEventListener(event,e=>{if(shift!==e.shiftKey){shift=e.shiftKey;draw();}});
 window.addEventListener('blur',()=>{shift=false;close();});window.addEventListener('resize',close);document.addEventListener('scroll',close,true);document.addEventListener('pointerdown',close,true);
 function bind(root,items){
  if(active&&!active.anchor.isConnected)close();
  for(const row of root.querySelectorAll('[data-object]')){
   const id=row.dataset.object;if(!items.some(value=>value.id===id))continue;const anchor=row.querySelector('.browser-data-identity')||row;anchor.classList.add('reference-hover-target');
   anchor.onmouseenter=e=>{close();shift=e.shiftKey;active={anchor,id,scope:api.projectId};draw();};anchor.onmouseleave=close;
  }
 }
 return {bind,close};
}
