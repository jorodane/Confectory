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
