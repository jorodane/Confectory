// Projection of already-public observations, never an assignment or permission source.
const states=Object.freeze({
 ready:['waiting','idle','배정 대기'],dispatching:['working','running','실행 준비 중'],
 running:['working','running','작업 중'],'awaiting-verification':['review','verification','완료 검증 대기'],
 completed:['done','done','완료'],cancelled:['idle','cancelled','취소됨'],
 interrupted:['error','interrupted','중단됨'],error:['error','error','오류']
});
export function projectOfficeWorkers(observation,objects){
 const project=observation?.projectId;if(typeof project!=='string'||!project)return [];
 const owned=new Map(objects.filter(row=>row.owned===true).map(row=>[row.id,row]));
 const helpers=new Map();for(const row of observation.participants||[])if(typeof row.id==='string'&&row.id&&!helpers.has(row.id))helpers.set(row.id,{id:row.id,name:String(row.name||row.id),workers:[]});
 const seen=new Set();for(const row of observation.workers||[]){
  if(row.projectId!==project||!helpers.has(row.ownerHelper)||!Object.hasOwn(states,row.status)||typeof row.id!=='string'||!/^[a-f0-9]{64}$/.test(row.id)||seen.has(row.id))continue;
  seen.add(row.id);const targets=new Set();
  for(const id of [row.assignedNode,...(Array.isArray(row.assignedSourceIds)?row.assignedSourceIds:[])])if(typeof id==='string'&&id){const at=id.indexOf('/body:');targets.add(at<0?id:id.slice(0,at));}
  // Multiple assignments or invisible targets do not select an execution target.
  const target=targets.size===1?[...targets][0]:null,objectId=target&&owned.has(target)?target:undefined;
  const [state,jobState,label]=states[row.status];
  helpers.get(row.ownerHelper).workers.push(Object.freeze({id:row.id,projectId:project,ownerHelper:row.ownerHelper,
   state,access:'idle',objectId,nativeStatus:row.status,jobState,
   jobLabel:row.needsCheck?'실행 확인 필요':label,needsCheck:row.needsCheck===true}));
 }
 for(const helper of helpers.values())helper.workers.sort((a,b)=>a.id.localeCompare(b.id));
 return [...helpers.values()];
}
