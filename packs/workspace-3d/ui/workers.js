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
  let lastToolIO=null,ioLabel='';const io=row.lastToolIO;
  if(!row.needsCheck&&row.status!=='ready'&&row.status!=='dispatching'&&io?.projectId===project&&typeof io.receipt==='string'&&/^[a-f0-9]{64}$/.test(io.receipt)&&Number.isInteger(io.ordinal)&&io.ordinal>=1&&io.ordinal<=256&&typeof io.targetId==='string'&&io.targetId.length>0&&io.targetId.length<=1024){
   const at=io.targetId.indexOf('/body:'),root=at<0?io.targetId:io.targetId.slice(0,at),assigned=[row.assignedNode,...(Array.isArray(row.assignedSourceIds)?row.assignedSourceIds:[])].includes(io.targetId);
   if(assigned&&owned.has(root))ioLabel=io.kind==='read'&&io.outcome==='completed'?'읽기 완료':io.kind==='draft-stage'&&io.outcome==='applied'?'초안 변경 확인':io.kind==='draft-stage'&&io.outcome==='unchanged'?'초안 동일 확인':'';
   if(ioLabel)lastToolIO=Object.freeze({receipt:io.receipt,ordinal:io.ordinal,kind:io.kind,outcome:io.outcome,targetId:io.targetId});
  }
  const [state,jobState,label]=states[row.status];
  helpers.get(row.ownerHelper).workers.push(Object.freeze({id:row.id,label:'Worker '+row.id.slice(0,12),projectId:project,ownerHelper:row.ownerHelper,
   state,access:'idle',objectId,nativeStatus:row.status,jobState,lastToolIO,ioLabel,
   jobLabel:row.needsCheck?'실행 확인 필요':label,needsCheck:row.needsCheck===true}));
 }
 for(const helper of helpers.values()){helper.workers.sort((a,b)=>a.id.localeCompare(b.id));helper.status='확인된 작업 '+helper.workers.length+'건';}
 return [...helpers.values()];
}
