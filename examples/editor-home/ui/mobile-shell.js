// v536 compact shell. Panels reuse the live desktop DOM and its existing input owners.
export const mobileEditorQuery='(max-width: 1100px) and (any-pointer: coarse), (max-width: 760px)';
export function createMobileShell(api){
 const media=matchMedia(mobileEditorQuery);let header=null,nav=null,frame=0,baseline=null;
 const closePanels=()=>{document.body.classList.remove('mobile-participants-open','mobile-chat-open');nav?.querySelectorAll('[aria-expanded]').forEach(b=>b.setAttribute('aria-expanded','false'));};
 function install(){
  const next=document.querySelector('#app .topbar'),right=next?.querySelector(':scope>.right');
  if(next===header&&nav?.isConnected)return;
  closePanels();header=next;nav=null;if(!right)return;
  nav=document.createElement('nav');nav.className='mobile-workspace-actions';nav.setAttribute('aria-label','모바일 작업 도구');
  nav.innerHTML='<button type="button" data-mobile-people aria-expanded="false">작업자</button><button type="button" data-mobile-files>목록</button><button type="button" data-mobile-chat aria-expanded="false">채팅</button><button type="button" data-mobile-more aria-label="작업 메뉴">⋯</button>';right.prepend(nav);
  for(const [name,cls] of [['people','mobile-participants-open'],['chat','mobile-chat-open']])nav.querySelector('[data-mobile-'+name+']').onclick=()=>{const open=!document.body.classList.contains(cls);closePanels();document.body.classList.toggle(cls,open);nav.querySelector('[data-mobile-'+name+']').setAttribute('aria-expanded',String(open));};
  nav.querySelector('[data-mobile-files]').onclick=()=>{closePanels();if(api.page()==='work'&&!api.blocked())api.files();};
  nav.querySelector('[data-mobile-more]').onclick=event=>{closePanels();api.menu(event,[['모바일 조작 안내',api.help],...api.actions()]);};
  const work=document.querySelector('#app .work');if(work){const shade=document.createElement('button');shade.className='mobile-panel-dismiss';shade.setAttribute('aria-label','열린 패널 닫기');shade.onclick=closePanels;work.append(shade);}
 }
 function sync(){
  const mobile=media.matches,visual=window.visualViewport,height=visual?.height||innerHeight;
  document.body.classList.toggle('is-mobile-editor',mobile);
  document.documentElement.style.setProperty('--mobile-height',height+'px');document.documentElement.style.setProperty('--mobile-top',(visual?.offsetTop||0)+'px');
  if(!baseline||Math.abs(baseline.width-innerWidth)>60)baseline={width:innerWidth,height};else baseline.height=Math.max(baseline.height,height);
  const editing=document.activeElement?.matches('input,textarea,[contenteditable=true]');document.body.classList.toggle('is-mobile-keyboard',!!(mobile&&(innerHeight-height>100||editing&&baseline.height-height>100)));
  if(!mobile)closePanels();install();if(nav)nav.querySelectorAll('[data-mobile-files],[data-mobile-more]').forEach(button=>button.disabled=api.blocked());
 }
 const schedule=()=>{cancelAnimationFrame(frame);frame=requestAnimationFrame(sync);};
 window.addEventListener('resize',schedule);window.visualViewport?.addEventListener('resize',schedule);window.visualViewport?.addEventListener('scroll',schedule);media.addEventListener('change',schedule);
 new MutationObserver(()=>{if(document.querySelector('#app .topbar')!==header||header&&!nav?.isConnected)schedule();}).observe(document.querySelector('#app'),{childList:true,subtree:true});
 // Do not intercept modal Escape, IME or browser history. Their existing owner handles Back/close.
 document.addEventListener('keydown',event=>{if(event.key!=='Escape'||event.isComposing||event.defaultPrevented||event.target.closest?.('.modal,[role=dialog]')||document.querySelector('.modal-shade,.floating-dialog-host,.context-menu'))return;if(document.body.matches('.mobile-participants-open,.mobile-chat-open')){event.preventDefault();closePanels();nav?.querySelector('[data-mobile-people]')?.focus({preventScroll:true});}});
 sync();return {refresh:sync,closePanels};
}
