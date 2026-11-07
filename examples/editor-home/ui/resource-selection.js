// Private browser selection only. It never grants access or writes project data.
export function createResourceSelection(api){
 const known=()=>new Set((api.catalogue()?.items||[]).map(row=>row.id));
 function ids(w){const source=Array.isArray(w.meta.resourceSelections)?w.meta.resourceSelections:w.meta.resourceSelected?[w.meta.resourceSelected]:[],allowed=known();return [...new Set(source.filter(id=>typeof id==='string'&&allowed.has(id)))].slice(0,128);}
 function paint(w){const selected=new Set(ids(w));for(const row of w.body.querySelectorAll('[data-resource-id]')){const chosen=selected.has(row.dataset.resourceId);row.classList.toggle('selected',chosen);row.setAttribute('aria-selected',String(chosen));}for(const row of w.body.querySelectorAll('[data-resource-tree-id]'))row.classList.toggle('is-object-selected',selected.has(row.dataset.resourceTreeId));}
 function set(w,values,anchor=null){w.meta.resourceSelections=[...new Set(values)].filter(id=>known().has(id)).slice(0,128);w.meta.resourceSelected=anchor;w.meta.resourceAnchor=anchor;paint(w);}
 function select(w,item,event={}){const rows=api.rows(w),selected=new Set(ids(w)),add=event.ctrlKey||event.metaKey;let anchor=w.meta.resourceAnchor;
  if(event.shiftKey&&anchor){const from=rows.findIndex(row=>row.id===anchor),to=rows.findIndex(row=>row.id===item.id);if(!add)selected.clear();if(from>=0&&to>=0)for(const row of rows.slice(Math.min(from,to),Math.max(from,to)+1))selected.add(row.id);else selected.add(item.id);}
  else if(add){if(selected.has(item.id))selected.delete(item.id);else selected.add(item.id);anchor=item.id;}
  else{selected.clear();selected.add(item.id);anchor=item.id;}
  set(w,[...selected],anchor);w.resourceUserSelection=(w.resourceUserSelection||0)+1;api.persist();
 }
 return {ids,paint,set,select};
}
