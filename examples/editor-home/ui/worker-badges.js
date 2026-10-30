// Read projection only: task ownership/approval/dispatch remain in their packs.
export function assignedWorkerProjection(current,projection){
 const result=new Map(),project=current?.projectId;if(!project)return result;
 const rows=new Map(projection.rows().filter(row=>row.owned!==false).map(row=>[row.id,row]));
 const helpers=new Set((current.helpers||[]).map(row=>row.id));
 const declaration=id=>{if(typeof id!=='string')return null;const marker=id.indexOf('/body:');const root=marker<0?id:id.slice(0,marker);return rows.has(root)?root:null;};
 const add=(id,task,reason)=>{const owner=declaration(id);if(!owner)return;const targets=new Set([owner]);
  // A registered implementation's provide edge explicitly identifies its
  // function. Do not infer callers from strings, aliases, display names or C#.
  if(rows.get(owner).kind==='implementation')for(const edge of projection.snapshot?.()?.edges||current.relationsMap?.edges||[])if(edge.target===owner&&edge.role==='provide'&&rows.get(edge.source)?.kind==='function'&&(edge.function==null||edge.function===edge.source))targets.add(edge.source);
  for(const target of targets){if(!result.has(target))result.set(target,new Map());const badge=result.get(target);if(!badge.has(task.ownerHelper))badge.set(task.ownerHelper,{helper:task.ownerHelper,tasks:new Set(),states:new Set(),reasons:new Set()});const row=badge.get(task.ownerHelper);row.tasks.add(task.id);row.states.add(task.status);row.reasons.add(reason);}
 };
 for(const task of current.assignmentWorkers||[]){if(task.projectId!==project||!helpers.has(task.ownerHelper))continue;
  if(['ready','dispatching','running','awaiting-verification'].includes(task.status)||task.needsCheck)for(const id of [task.assignedNode,...(task.assignedSourceIds||[])])add(id,task,task.needsCheck?'배정 확인 필요':'배정');
  // These are recorded dirty contributions, not arbitrary user edits. A
  // supporting draft is deliberately labelled separately from authorship.
  for(const id of task.changedIds||[])add(id,task,'미반영 변경');
  if(['ready','dispatching','running','awaiting-verification'].includes(task.status))for(const id of task.supportingDraftIds||[])add(id,task,'지원 초안');
 }
 return result;
}

export function createWorkerBadges(api){
 let queued=false,closePopup=null,lastScope=null,lastWorkers=null;
 const helpers=()=>new Map(api.helpers().map(h=>[h.id,h]));
 const combine=rows=>{const out=new Map();for(const map of rows)for(const [id,row] of map||[]){if(!out.has(id))out.set(id,{helper:id,tasks:new Set(),states:new Set(),reasons:new Set()});const target=out.get(id);for(const key of ['tasks','states','reasons'])for(const value of row[key])target[key].add(value);}return out;};
 const empty=()=>new Map();
 function refresh(){
  const current=api.current(),scope=current?.projectId||'',workerKey=JSON.stringify([scope,current?.assignmentWorkers,current?.helpers]);
  if(scope!==lastScope||workerKey!==lastWorkers){closePopup?.();lastScope=scope;lastWorkers=workerKey;}
  const data=assignedWorkerProjection(current,api.projection),rows=new Map(api.projection.rows().filter(row=>row.owned!==false).map(row=>[row.id,row])),known=helpers();
  const within=(id,parent)=>{const seen=new Set();for(let at=id;at&&!seen.has(at);at=api.projection.browserParent(at)){if(at===parent)return true;seen.add(at);}return false;};
  const subtree=id=>combine([...data].filter(([source])=>!id||within(source,id)).map(([,value])=>value));
  const summary=row=>[...row.reasons].join(' · ')+' · '+[...row.states].join(' · ');
  const portrait=row=>{const h=known.get(row.helper);return h?'<button type="button" class="collaborator worker-portrait" data-assigned-helper="'+api.esc(h.id)+'" title="'+api.esc(h.name+' · '+summary(row))+'" aria-label="'+api.esc(h.name+' · '+summary(row))+'">'+api.avatar(h)+'</button>':'';};
  function bind(root){for(const b of root.querySelectorAll('[data-assigned-helper]'))b.onclick=e=>{e.stopPropagation();const id=b.dataset.assignedHelper;if(api.current()?.projectId===scope&&known.has(id))api.open(known.get(id));};}
  function paint(slot,badges,count=false){
   const values=[...badges.values()].filter(row=>known.has(row.helper)).sort((a,b)=>a.helper.localeCompare(b.helper));
   const stamp=JSON.stringify([scope,count,values.map(row=>[row.helper,[...row.tasks],[...row.states],[...row.reasons],known.get(row.helper)?.name,known.get(row.helper)?.presentation])]);if(slot._badgeStamp===stamp)return;
   closePopup?.();slot._badgeStamp=stamp;slot.dataset.assignedWorkers=scope;slot.hidden=!values.length;
   slot.innerHTML=count&&values.length>1?'<button type="button" class="worker-count" aria-label="'+values.length+'명의 작업자" title="'+values.length+'명의 작업자" aria-haspopup="dialog" aria-expanded="false">'+values.length+'</button>':values.map(portrait).join('');bind(slot);
   const counter=slot.querySelector('.worker-count');if(!counter)return;
   counter.onkeydown=e=>{if(e.key!=='Escape')e.stopPropagation();};counter.onclick=e=>{e.stopPropagation();if(counter.getAttribute('aria-expanded')==='true'){closePopup?.();return;}closePopup?.();counter.focus({preventScroll:true});counter.setAttribute('aria-expanded','true');
    const popup=document.createElement('div');popup.className='worker-count-popover floating-worker-count';popup.setAttribute('role','dialog');popup.setAttribute('aria-label',values.length+'명의 작업자');popup.innerHTML=values.map(portrait).join('');document.body.append(popup);bind(popup);const r=counter.getBoundingClientRect();popup.style.left=Math.max(4,Math.min(innerWidth-popup.offsetWidth-4,r.right-popup.offsetWidth))+'px';popup.style.top=(r.top>popup.offsetHeight+8?r.top-popup.offsetHeight-5:r.bottom+5)+'px';
    const events=new AbortController(),options={capture:true,signal:events.signal},owns=target=>target===counter||popup.contains(target);const close=()=>{events.abort();popup.remove();counter.setAttribute('aria-expanded','false');if(closePopup===close)closePopup=null;};closePopup=close;
    document.addEventListener('pointerdown',event=>{if(!owns(event.target))close();},options);document.addEventListener('focusin',event=>{if(!owns(event.target))close();},options);document.addEventListener('keydown',event=>{if(event.key==='Escape'){event.preventDefault();event.stopPropagation();close();counter.focus({preventScroll:true});}},options);window.addEventListener('resize',close,{signal:events.signal});slot.closest('.browser-folder-tree,.window-content,.browser-items')?.addEventListener('scroll',close,{signal:events.signal});
   };
  }
  const slot=(root,selector,kind)=>{let node=root.querySelector(selector);if(!node){node=document.createElement('span');node.className=kind;node.dataset.workerBadgeSlot='';root.append(node);}return node;};
  for(const w of api.windows().values()){
   if(!w.el.isConnected)continue;
   for(const element of w.el.querySelectorAll('[data-object]')){const id=element.dataset.object,owner=element.querySelector('.browser-data-identity')||element;let node=slot(owner,':scope>[data-worker-badge-slot]','folder-workers');if(element.classList.contains('object-card'))Object.assign(node.style,{position:'absolute',right:'3px',top:'3px'});paint(node,data.get(id)||empty(),true);}
   for(const line of w.el.querySelectorAll('.folder-tree-row')){const button=line.querySelector('[data-tree-id],[data-namespace]');if(!button)continue;const id=button.dataset.treeId,namespace=button.dataset.namespace,badges=id?subtree(id):combine([...data].filter(([source])=>rows.get(source)?.group===w.meta.group&&(!namespace||source.startsWith(namespace+'::'))).map(([,v])=>v));paint(slot(line,':scope>[data-worker-badge-slot]','folder-workers'),badges,true);}
   const browser=w.el.querySelector('[data-browser-workers]');if(browser){const badges=combine([...data].filter(([id])=>rows.get(id)?.group===w.meta.group&&(!w.meta.namespace||id.startsWith(w.meta.namespace+'::'))&&(!w.meta.parent||within(id,w.meta.parent))).map(([,v])=>v));paint(browser,badges);}
   const header=w.el.querySelector(':scope>.object-header>.row')||(['declaration','properties'].includes(w.meta.mode)?w.el.querySelector(':scope>.window-title>.row'):null);if(header){const id=w.elementSchema?.id||w.meta.id;let target=header.querySelector('[data-object-workers]');if(!target){target=document.createElement('span');target.className='browser-title-workers';target.dataset.objectWorkers='';header.prepend(target);}paint(target,data.get(id)||empty());}
  }
  if(closePopup&&!document.querySelector('.worker-count[aria-expanded=true]'))closePopup();
 }
 const schedule=()=>{if(queued)return;queued=true;requestAnimationFrame(()=>{queued=false;refresh();});};
 new MutationObserver(schedule).observe(document.body,{childList:true,subtree:true});
 return {refresh:schedule};
}
