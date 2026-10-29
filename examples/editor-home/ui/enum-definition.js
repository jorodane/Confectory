import {browserIconMarkup} from './browser-data.js';
import {openGlyphPopover} from './glyph-popover.js';

// Original information choices: order is presentation; the selected value is an
// opaque item id. This does not edit Blueprint execution-enum ports or C# values.
export function renderEnumDefinition({api,w,info,header}){
 const {esc}=api,root=document.createElement('section');root.className='object-schema';root.dataset.enumDefinition='';w.body.querySelector('[data-declaration-properties]').after(root);
 const read=()=>JSON.parse(header.value('enum-values')||'[]'),alive=()=>root.isConnected&&header.owns(),write=(items,options)=>header.edit('enum-values',JSON.stringify(items),options);
 let dragged=null;
 function render(){
  if(!root.isConnected)return;
  let items;try{items=read();if(!Array.isArray(items))throw Error();}catch{root.textContent='보관한 종류 정의를 읽지 못했어요. 원본과 입력을 유지합니다.';return;}
  root.innerHTML='<div class="object-section-heading"><strong>종류 항목</strong><button type="button" class="secondary" data-enum-add '+(!info.editable?'disabled':'')+'>＋ 항목</button></div><div class="enum-values">'+items.map((item,index)=>'<div class="enum-value-row" data-enum-value="'+esc(item.id)+'"><span class="enum-value-index" title="행을 드래그해서 순서 변경">'+(index+1)+'</span><button type="button" class="property-icon-edit enum-icon-edit" data-enum-icon aria-label="'+esc(item.name)+' 종류 아이콘 편집" '+(!info.editable?'disabled':'')+'>'+browserIconMarkup({kind:'schema',icon:item.icon||'◇'},esc)+'</button><input data-enum-name maxlength="60" aria-label="종류 항목 이름" value="'+esc(item.name)+'" '+(!info.editable?'readonly':'')+'><button type="button" class="property-remove" data-enum-remove="'+esc(item.id)+'" aria-label="'+esc(item.name)+' 제거" '+(!info.editable?'disabled':'')+'>×</button></div>').join('')+'</div>';
  root.querySelector('[data-enum-add]').onclick=()=>{if(!alive())return;const next=read();if(next.length>=256)return api.toast('종류 항목 수가 저장 예산을 넘었어요. 기존 항목은 유지됩니다.');let name='새 항목',n=2;while(next.some(item=>item.name===name))name='새 항목 '+n++;next.push({id:crypto.randomUUID(),name});write(next);root.querySelector('.enum-value-row:last-child input')?.focus();};
  for(const row of root.querySelectorAll('[data-enum-value]')){
   const id=row.dataset.enumValue,input=row.querySelector('[data-enum-name]'),button=row.querySelector('[data-enum-icon]');let before=null;input.setAttribute('aria-invalid',String(!input.value.trim()||items.some(item=>item.id!==id&&item.name===input.value)));
   input.onfocus=()=>{before=header.snapshot();};
   input.oninput=()=>{if(!alive())return;const next=read(),item=next.find(item=>item.id===id);if(!item)return;item.name=input.value;write(next,{transient:true,paint:false});};
   input.onchange=()=>{if(!alive())return;const next=read(),item=next.find(item=>item.id===id);if(!item)return;const name=input.value.trim();if(name&&!next.some(item=>item.id!==id&&item.name===name))item.name=name;write(next,{before:before??header.snapshot()});};
   input.onkeydown=e=>{e.stopPropagation();if(e.isComposing)return;if(e.key==='Enter'){e.preventDefault();input.blur();}};
   button.onclick=()=>{if(!alive())return;const item=read().find(item=>item.id===id);if(!item)return;openGlyphPopover({api,w,anchor:button,title:item.name+' 종류',value:item.icon||'◇',allowEmpty:true,allowImage:true,alive:()=>alive()&&button.isConnected,onApply:icon=>{if(!alive())return;const next=read(),item=next.find(item=>item.id===id);if(!item)return;if(icon)item.icon=icon;else delete item.icon;write(next);}});};
   row.querySelector('[data-enum-remove]').onclick=()=>{if(alive())write(read().filter(item=>item.id!==id));};
   row.draggable=info.editable===true;row.ondragstart=e=>{if(!alive()||e.target.closest('input,button'))return e.preventDefault();dragged=id;e.dataTransfer.effectAllowed='move';e.dataTransfer.setData('application/x-enum-order',id);};
   row.ondragover=e=>{if(alive()&&dragged&&dragged!==id)e.preventDefault();};
   row.ondrop=e=>{if(!alive()||!dragged||dragged===id)return;e.preventDefault();const next=read(),from=next.findIndex(item=>item.id===dragged),to=next.findIndex(item=>item.id===id);dragged=null;if(from<0||to<0)return;const [item]=next.splice(from,1);next.splice(to,0,item);write(next);};
   row.ondragend=()=>{dragged=null;};
  }
 }
 header.validate(()=>{const names=new Set();for(const item of read()){if(!item.name?.trim()||item.name!==item.name.trim()||names.has(item.name))throw Error('종류 항목 이름은 비어 있거나 중복될 수 없어요. 입력은 유지됩니다.');names.add(item.name);}});
 header.observe(render);
}
