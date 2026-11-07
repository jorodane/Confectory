// Read-only navigation over this display pack's already permitted source/actors.
export function createOfficeFinder({engine,current,status}){
 const snapshot=()=>{if(!current()||!engine()?.active)return null;const view=engine();view.refreshSource();return view;};
 function actors(view){const rows=[];for(const helper of view.source.helpers||[]){const actor=view.helperActors.find(a=>a.helperId===helper.id);if(!actor)continue;const workers=[];for(const allowed of helper.workers||[]){const worker=actor.workers.find(a=>a.workerId===allowed.id);if(!worker)continue;workers.push({key:'office-worker:'+worker.id,id:worker.id,kind:'office-worker',parent:actor.id,title:worker.workerLabel,detail:view.jobAction(worker),target:view.objectsById.get(worker.activity.objectId)?.name||'',icon:'•'});}rows.push({key:'office-helper:'+actor.id,id:actor.id,kind:'office-helper',title:helper.name,detail:view.actorAction(actor),icon:'♙',workers});}return rows;}
 function rows(mode,query){const view=snapshot();if(!view)return [];const match=text=>String(text??'').toLocaleLowerCase().includes(query),result=[];
  for(const helper of actors(view)){const own=!query||match(helper.title+' '+helper.detail),workers=helper.workers.filter(w=>own||match(w.title+' '+w.detail+' '+w.target));if(mode==='workers'){if(own||workers.length)result.push({...helper,workers});}else if(mode==='text'&&query){if(match(helper.title+' '+helper.detail))result.push({...helper,workers:undefined});for(const worker of helper.workers)if(match(helper.title+' '+worker.title+' '+worker.detail+' '+worker.target))result.push({...worker,title:helper.title+' · '+worker.title});}}
  if(mode==='text'&&query)for(const room of view.rooms.values())if(match(room.category.name))result.push({key:'office-room:'+room.id,id:room.id,kind:'office-room',title:room.category.name,detail:'방 이름',icon:'▣'});
  return result;
 }
 function navigate(kind,id){const view=snapshot();if(!view)return false;
  if(kind==='office-zone'){if(!['__lobby','__concept','__info','__feature','__module'].includes(id)||!view.rooms.has(id))return false;view.focusRoom(id);return true;}
  if(kind==='object'){const object=view.source.objects.find(o=>o.id===id);if(!object)return false;const room=view.roomFor(object);if(!room)return false;view.focusRoom(room.id);if(object.kind!=='Category')view.select('station',id,false);return true;}
  if(kind==='office-room'){if(!view.rooms.has(id))return false;view.focusRoom(id);return true;}
  const helper=actors(view).find(h=>kind==='office-helper'?h.id===id:h.workers.some(w=>w.id===id));if(!helper)return false;const role=kind==='office-helper'?'helper':kind==='office-worker'?'worker':null;if(!role)return false;view.select(role,id);view.followActor(id);return true;
 }
 return Object.freeze({current,ready:()=>!!current()&&!!engine()?.active,rows,navigate,status:()=>current()?status():'unavailable'});
}
