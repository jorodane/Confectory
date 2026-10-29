import {browserIconMarkup} from './browser-data.js';

let active=null;

// The prototype's information-choice dropdown. Item ids are the value; labels
// and icons are display metadata. Fresh choices never silently replace a value.
export function bindInformationEnum({api,w,anchor,row,value,items,choices,alive,pick,activate}){
 const {esc}=api,icon=item=>'<span class="property-label-icon" aria-hidden="true">'+(item?.icon?browserIconMarkup({kind:'schema',icon:item.icon},esc):'<span class="icon-placeholder">·</span>')+'</span>';
 const selected=items.find(item=>item.id===value);
 anchor.classList.add('enum-dropdown');anchor.setAttribute('aria-haspopup','listbox');anchor.setAttribute('aria-expanded','false');
 anchor.innerHTML=icon(selected)+'<span class="enum-value-name">'+esc(selected?.name||'선택…')+'</span><span class="enum-dropdown-arrow" aria-hidden="true">▾</span>';
 let loading=false;
 async function open(){
  if(loading)return;if(active){const same=active.anchor===anchor;active.close();if(same)return;}
  if(!alive()||activate?.()===false)return;loading=true;
  try{
   const current=await choices();if(!alive()||!anchor.isConnected)return;
   const root=document.createElement('div'),controller=new AbortController();root.className='enum-value-popover';root.setAttribute('role','listbox');root.setAttribute('aria-label',row.name+' 종류 선택');
   root.innerHTML=current.length?current.map(item=>'<button type="button" role="option" data-enum-choice="'+esc(item.id)+'" aria-selected="'+String(item.id===value)+'">'+icon(item)+'<span>'+esc(item.name)+'</span></button>').join(''):'<p class="small">종류 항목이 없습니다.</p>';
   document.body.append(root);anchor.setAttribute('aria-expanded','true');let closed=false;
   const close=()=>{if(closed)return;closed=true;controller.abort();observer.disconnect();root.remove();anchor.setAttribute('aria-expanded','false');if(active?.root===root)active=null;if(w.elementClosePopover===close)w.elementClosePopover=null;};
   const observer=new MutationObserver(()=>{if(!alive()||!anchor.isConnected)close();});observer.observe(document.body,{childList:true,subtree:true});active={root,anchor,close};w.elementClosePopover?.();w.elementClosePopover=close;
   const position=()=>{if(!alive()||!anchor.isConnected||!anchor.getClientRects().length){close();return;}const rect=anchor.getBoundingClientRect(),width=Math.min(Math.max(170,rect.width),340,innerWidth-16);root.style.width=width+'px';root.style.maxHeight=Math.min(300,innerHeight-16)+'px';root.style.left=Math.max(8,Math.min(rect.left,innerWidth-width-8))+'px';root.style.top=Math.max(8,Math.min(rect.bottom+4+root.offsetHeight<=innerHeight-8?rect.bottom+4:rect.top-root.offsetHeight-4,innerHeight-root.offsetHeight-8))+'px';};position();
   const buttons=[...root.querySelectorAll('[data-enum-choice]')];for(const button of buttons){button.tabIndex=-1;button.onclick=()=>{if(!alive()){close();return;}const id=button.dataset.enumChoice;close();pick(id);if(anchor.isConnected)anchor.focus({preventScroll:true});};}
   root.onkeydown=e=>{const index=buttons.indexOf(document.activeElement);if(['ArrowDown','ArrowUp','Home','End'].includes(e.key)&&buttons.length){e.preventDefault();buttons[e.key==='Home'?0:e.key==='End'?buttons.length-1:Math.max(0,Math.min(buttons.length-1,(index<0?0:index)+(e.key==='ArrowDown'?1:-1)))].focus();}else if(e.key==='Tab'){close();anchor.focus({preventScroll:true});}};
   document.addEventListener('keydown',e=>{if(e.key==='Escape'){e.preventDefault();e.stopImmediatePropagation();close();anchor.focus({preventScroll:true});}},{capture:true,signal:controller.signal});document.addEventListener('pointerdown',e=>{if(!root.contains(e.target)&&!anchor.contains(e.target))close();},{capture:true,signal:controller.signal});document.addEventListener('scroll',e=>{if(!root.contains(e.target))position();},{capture:true,signal:controller.signal});window.addEventListener('resize',position,{signal:controller.signal});(buttons.find(button=>button.dataset.enumChoice===value)||buttons[0])?.focus({preventScroll:true});
  }catch(error){api.fail(w,error);}finally{loading=false;}
 }
 anchor.onclick=open;anchor.onkeydown=e=>{if(['ArrowDown','ArrowUp'].includes(e.key)){e.preventDefault();open();}};
}
