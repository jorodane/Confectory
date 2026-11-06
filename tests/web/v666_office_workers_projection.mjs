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
console.log('PASS native public Worker identity/project/participant scope, eight factual statuses, no IO/name/target inference, immutable state independent of arrival, no execution timestamps or journal writes');
