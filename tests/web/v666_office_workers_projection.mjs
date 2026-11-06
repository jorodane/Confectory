import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
const root=process.argv[2];
const {projectOfficeWorkers:project}=await import(pathToFileURL(root+'/packs/workspace-3d/ui/workers.js'));
globalThis.window={};const {actorMethods}=await import(pathToFileURL(root+'/packs/workspace-3d/ui/office-actors.js'));
const id='a'.repeat(64),objects=[{id:'Own::Impl',owned:true},{id:'Own::Other',owned:true},{id:'External::Fn',owned:false}];
const task=(extra={})=>({id,projectId:'p',ownerHelper:'h',status:'ready',assignedNode:'Own::Impl/body:common/node:n',assignedSourceIds:[],...extra});
const observation=workers=>({projectId:'p',participants:[{id:'h',name:'실제 도우미'},{id:'idle',name:'유휴 도우미'}],workers});
const original=JSON.stringify(observation([task()]));let result=project(JSON.parse(original),objects);
assert.equal(JSON.stringify(observation([task()])),original);assert.equal(result.length,2);assert.equal(result[0].workers[0].objectId,'Own::Impl');assert.equal(result[0].workers[0].access,'idle');assert(Object.isFrozen(result[0].workers[0]));
assert.equal(result[0].workers[0].id,id);assert.equal(result[0].workers[0].label,'Worker '+id.slice(0,12));assert.equal(result[0].status,'확인된 작업 1건');assert.equal(result[1].status,'확인된 작업 0건');
const expected={ready:['idle','배정 대기'],dispatching:['running','실행 준비 중'],running:['running','작업 중'],'awaiting-verification':['verification','완료 검증 대기'],completed:['done','완료'],cancelled:['cancelled','취소됨'],interrupted:['interrupted','중단됨'],error:['error','오류']};
const context={bridge:{observedOnly:true,canInspectTask:()=>true},source:{id:'p'},objectsById:new Map(objects.filter(o=>o.owned).map(o=>[o.id,o])),roomFor:()=>({id:'room'})};
for(const [status,[state,label]]of Object.entries(expected)){
 const raw=project(observation([task({status})]),objects)[0].workers[0];
 const activity=actorMethods.workerActivity.call(context,{id:'h'},{raw},0),actor={activity,group:{position:{x:-999,z:-999}},path:[{x:1,z:2}],host:{arriving:true}};
 const job=actorMethods.createWorkerJob.call(context,actor,{job:{state:'running',startedAt:123}});actor.job=job;
 assert.equal(job.state,state);assert.equal(job.nativeStatus,status);assert.equal(job.startedAt,null);assert.equal(job.finishedAt,null);assert.equal(actorMethods.jobAction.call(context,actor),label);assert.equal(activity.access,'idle');assert(Object.isFrozen(job));
}
assert.equal(project(observation([task({status:'interrupted',needsCheck:true})]),objects)[0].workers[0].jobLabel,'실행 확인 필요');
for(const extra of [{projectId:'other'},{ownerHelper:'private'},{status:'unknown'},{status:'toString'},{id:'invalid'}])assert.equal(project(observation([task(extra)]),objects)[0].workers.length,0);
assert.equal(project({...observation([task()]),projectId:''},objects).length,0);
assert.equal(project({...observation([task()]),participants:[]},objects).length,0);
assert.equal(project(observation([task(),task()]),objects)[0].workers.length,1);
for(const extra of [{assignedSourceIds:['Own::Other']},{assignedNode:'External::Fn'},{assignedNode:'Missing::Unknown'}])assert.equal(project(observation([task(extra)]),objects)[0].workers[0].objectId,undefined);
assert.equal(project(observation([task({assignedSourceIds:['Own::Impl']})]),objects)[0].workers[0].objectId,'Own::Impl');
assert.equal(project({...observation([]),workers:undefined,actionWorkers:[task()]},objects)[0].workers.length,0);
// Only the already-authorized, explicitly assigned, completed tool receipt is displayed.
const io={projectId:'p',receipt:'b'.repeat(64),ordinal:2,targetId:'Own::Impl/body:common/node:n',kind:'read',outcome:'completed'};
const withIO=(extra={},row={})=>project(observation([task({status:'running',...row,lastToolIO:{...io,...extra}})]),objects)[0].workers[0];
for(const [kind,outcome,label]of [['read','completed','읽기 완료'],['draft-stage','applied','초안 변경 확인'],['draft-stage','unchanged','초안 동일 확인']]){
 const raw=withIO({kind,outcome});assert.equal(raw.ioLabel,label);assert(Object.isFrozen(raw.lastToolIO));assert.equal(raw.access,'idle');
 const activity=actorMethods.workerActivity.call(context,{id:'h'},{raw},0),actor={activity};actor.job=actorMethods.createWorkerJob.call(context,actor,{});
 assert.equal(actorMethods.jobAction.call(context,actor),'작업 중 · 최근 '+label);assert.equal(actor.job.startedAt,null);assert.equal(actor.job.finishedAt,null);
}
for(const bad of [{projectId:'other'},{receipt:'capability'},{ordinal:0},{ordinal:257},{ordinal:1.5},{targetId:''},{targetId:'Own::Other'},{targetId:'External::Fn'},{kind:'writing'},{kind:'read',outcome:'applied'},{kind:'draft-stage',outcome:'conflict'}])assert.equal(withIO(bad).lastToolIO,null);
for(const row of [{needsCheck:true},{status:'ready'},{status:'dispatching'}])assert.equal(withIO({},row).lastToolIO,null);
const multiple=withIO({},{assignedSourceIds:['Own::Other']});assert.equal(multiple.objectId,undefined);assert.equal(multiple.ioLabel,'읽기 완료');
assert.equal(project(observation([task({status:'running',changedIds:['Own::Impl'],access:'write'})]),objects)[0].workers[0].lastToolIO,null);
console.log('PASS native public Worker identity/project/participant scope, eight factual statuses, completed assigned IO only; no phase/name/target inference, immutable state independent of arrival, no execution timestamps or journal writes');
