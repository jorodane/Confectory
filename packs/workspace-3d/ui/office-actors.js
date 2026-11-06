import * as THREE from './assets/three.module-0.160.1.js';
import {createCharacter} from './voxel-character.js';
import {zones} from './office-world.js';

const hash=value=>[...String(value)].reduce((n,c)=>(n*31+c.charCodeAt(0))>>>0,0);
const rank={conflict:9,error:8,working:7,writing:7,review:6,reading:6,waiting:1,idle:1,done:0};
const accessFor=state=>['working','writing'].includes(state)?'write':['review','reading'].includes(state)?'read':'idle';
const active=activity=>activity.nativeStatus&&['running','verification'].includes(activity.jobState)||['read','write'].includes(activity.access)||['conflict','error'].includes(activity.state);
const keyFor=activity=>JSON.stringify([activity.state,activity.access,activity.objectId,activity.peerHelperId]);

// Helpers coordinate; only their half-size Workers handle objects and terminals.
export const actorMethods={
 workerKey(helperId,workerId){return JSON.stringify([helperId,String(workerId)])},
 workerRows(helper){
  const counts=new Map(),rows=(helper.workers||[]).map((raw,index)=>{
   const id=String((Array.isArray(raw)?raw[0]:raw.id??raw.workerId)??index+1),count=counts.get(id)||0;counts.set(id,count+1);
   return {raw,workerId:count?id+' ('+(count+1)+')':id};
  });
  for(const entry of this.workerOverrides.values())if(entry.helperId===helper.id&&!rows.some(row=>row.workerId===String(entry.workerId)))rows.push({raw:{id:entry.workerId},workerId:String(entry.workerId)});
  const override=this.activityOverrides.get(helper.id);
  if(override&&!rows.length&&active(override))rows.push({raw:{id:override.workerId||'A'},workerId:String(override.workerId||'A')});
  return rows;
 },
 workerActivity(helper,row,index){
  if(this.bridge.observedOnly){
   const raw=row.raw,allowed=raw.projectId===this.source.id&&raw.ownerHelper===helper.id&&this.bridge.canInspectTask?.(helper,raw)===true;
   return {state:raw.state,access:'idle',nativeStatus:raw.nativeStatus,jobState:raw.jobState,jobLabel:raw.jobLabel,
    objectId:allowed&&this.objectsById.has(raw.objectId)?raw.objectId:undefined,text:raw.jobLabel};
  }
  const raw=row.raw,meta=Array.isArray(raw)?raw[4]||{}:raw,legacy=this.activityOverrides.get(helper.id),override=this.workerOverrides.get(this.workerKey(helper.id,row.workerId))||(legacy&&(legacy.workerId?String(legacy.workerId)===row.workerId:index===0)?legacy:null),state=override?.state||(Array.isArray(raw)?raw[1]:raw.state)||'waiting',location=(Array.isArray(raw)?raw[3]:raw.location)||'';
  const targetId=override?.objectId||meta.objectId,object=targetId?this.objectsById.get(targetId):[...this.objectsById.values()].filter(o=>o.kind!=='folder'&&o.name&&location.includes(o.name)).sort((a,b)=>location.lastIndexOf(b.name)-location.lastIndexOf(a.name)||b.name.length-a.name.length)[0]||this.source.objects.find(o=>o.helper===helper.id);
  const access=override?.access||meta.access,hiddenTarget=!!meta.hiddenTarget||this.bridge.canInspectTask?.(helper,{...meta,objectId:targetId||object?.id})===false;
  if(hiddenTarget)return {state,access:['read','write','idle'].includes(access)?access:accessFor(state),objectId:undefined,text:'작업 중',hiddenTarget:true};
  return {state,access:['read','write','idle'].includes(access)?access:accessFor(state),objectId:object?.id||override?.objectId||meta.objectId,text:String(override?.text||(Array.isArray(raw)?raw[2]:raw.text)||''),peerHelperId:override?.peerHelperId||meta.peerHelperId};
 },
 createWorkerJob(actor,old){
  if(this.bridge.observedOnly){const a=actor.activity,o=this.objectsById.get(a.objectId);return Object.freeze({
   key:JSON.stringify([a.nativeStatus,a.objectId]),state:a.jobState,objectId:a.objectId,access:'idle',
   nativeStatus:a.nativeStatus,label:a.jobLabel,roomId:o?this.roomFor(o).id:'__lobby',startedAt:null,finishedAt:null});}
  const activity=actor.activity,state=['error','conflict','done'].includes(activity.state)?activity.state:['read','write'].includes(activity.access)?'running':'idle',key=JSON.stringify([activity.objectId,activity.access,state]),prior=old?.job,now=performance.now(),sameTarget=prior?.objectId===activity.objectId,object=this.objectsById.get(activity.objectId);
  // This snapshot follows Worker signals. Walking, reporting and seat availability never advance it.
  return Object.freeze({key,state,objectId:activity.objectId,access:activity.access,roomId:object?this.roomFor(object).id:'__lobby',startedAt:state==='running'?prior?.key===key?prior.startedAt:now:sameTarget?prior?.startedAt??null:null,finishedAt:state==='done'?prior?.key===key?prior.finishedAt:now:null});
 },
 captureActors(sameWorkspace){
  return new Map((sameWorkspace?this.actors:[]).map(actor=>{
   const p=actor.group.position,anchor=actor.arriving?this.rooms.get('__lobby'):[...this.rooms.values()].find(r=>r.origin&&Math.abs(p.x-r.origin.x)<r.w/2&&Math.abs(p.z-r.origin.z)<r.d/2);
   return [actor.id,{x:p.x,z:p.z,rotation:actor.group.rotation.y,coffeeCarry:!!actor.coffeeCarry,anchor:anchor?.id,localX:anchor?p.x-anchor.origin.x:0,localZ:anchor?p.z-anchor.origin.z:0,arriving:actor.arriving,arrivalPhase:actor.arrivalPhase,arrivalOrder:actor.arrivalOrder,arrivalUntil:actor.arrivalUntil,gateLane:actor.gateLane,taskKind:actor.task?.kind,activityKey:keyFor(actor.activity),terminalIndex:actor.terminal?.index,job:actor.job}];
  }));
 },
 buildActor(helper,id,role,workerId,workerLabel=workerId){
  const rig=createCharacter(helper,this.source.skins[helper.id]||helper.voxelCharacter),actor={...rig,id,role,helper,helperId:helper.id,workerId,workerLabel,path:[],speed:role==='worker'?7.2:3.1,carrying:false,taskStarted:null};
  actor.group.scale.setScalar(role==='worker'?.5:1);this.model.add(actor.group);this.actorProps(actor);
  const pick={kind:role,id};actor.group.traverse(mesh=>{if(mesh.isMesh){mesh.userData.pick=pick;this.pickables.push(mesh)}});
  actor.shadow=new THREE.Mesh(this.shadowGeometry,this.shadowMaterial);actor.shadow.rotation.x=-Math.PI/2;actor.shadow.position.y=.08;actor.group.add(actor.shadow);
  this.label(role==='worker'?helper.name+' · '+workerLabel:helper.name,role,id,()=>actor.group.position.clone().add(new THREE.Vector3(0,role==='worker'?1.42:2.8,0)),'준비 중',role==='helper'?helper.image:'');this.actors.push(actor);return actor;
 },
 placeActor(actor,old,fallback){
  let start=fallback;
  if(old){const anchor=this.rooms.get(old.anchor);start=anchor?this.world.local(anchor,old.localX,old.localZ):old.anchor?this.world.gates[0].inside:old}
  const nearest=this.world.nav.nearest(start)||this.world.nav.nearest(fallback)||this.world.nav.nearest(this.world.gates[0].inside);
  actor.group.position.set(nearest.x*this.world.nav.step,0,nearest.z*this.world.nav.step);
  if(old){actor.coffeeCarry=!!old.coffeeCarry;if(Number.isFinite(old.rotation))actor.group.rotation.y=old.rotation}
 },
 buildCast(previous){
  this.helperActors=[];this.workerActors=[];
  this.source.helpers.forEach((helper,index)=>{
   const actor=this.buildActor(helper,helper.id,'helper'),old=previous.get(actor.id);this.helperActors.push(actor);
   actor.arriving=old?.arriving??!this.layout.seenHelpers.includes(helper.id);actor.arrivalPhase=old?.arrivalPhase||'queue';actor.arrivalOrder=old?.arrivalOrder??performance.now()+index;actor.arrivalUntil=old?.arrivalUntil||0;actor.gateLane=old?.gateLane??index%this.world.gates.length;
   this.placeActor(actor,old,actor.arriving?this.world.gates[actor.gateLane].outside:this.world.local(this.rooms.get('__lobby'),-3+index,4));
  });
  for(const host of this.helperActors){
   const rows=this.workerRows(host.helper);host.workers=[];
   rows.forEach((row,index)=>{
    const id='worker:'+this.workerKey(host.id,row.workerId),actor=this.buildActor(host.helper,id,'worker',row.workerId,row.raw.label||row.workerId),old=previous.get(id);
    actor.host=host;actor.activity=this.workerActivity(host.helper,row,index);actor.job=this.createWorkerJob(actor,old);actor.suspended=!this.bridge.observedOnly&&host.arriving;actor.group.visible=!actor.suspended;
    this.placeActor(actor,old,{x:host.group.position.x+(index%3-1)*.7,z:host.group.position.z+.8});actor.old=old;host.workers.push(actor);this.workerActors.push(actor);
   });
   host.activity=[...host.workers].sort((a,b)=>(rank[b.activity.state]||0)-(rank[a.activity.state]||0))[0]?.activity||{state:'waiting',access:'idle',text:'다음 작업을 기다리고 있습니다'};
  }
  const meetings=new Set();
  for(const host of this.helperActors)if(host.workers.some(w=>w.activity.state==='conflict')){
   const issue=host.workers.find(w=>w.activity.state==='conflict').activity,object=this.objectsById.get(issue.objectId),room=object&&this.roomFor(object),peer=this.helperActors.find(h=>h.id===issue.peerHelperId&&h!==host)||this.helperActors.find(h=>h!==host&&h.workers.some(w=>{const o=this.objectsById.get(w.activity.objectId);return o&&this.roomFor(o)===room}))||this.helperActors.find(h=>h!==host);
   if(peer){meetings.add(host.id);meetings.add(peer.id);host.peerId=peer.id;peer.peerId=host.id}
  }
  let meetingIndex=0;for(const host of this.helperActors)if(meetings.has(host.id))host.meeting=this.world.meetingPoint(host.id,meetingIndex++);
  const roomUse=new Map();
  for(const host of this.helperActors){
   if(host.meeting){host.roomId='__lobby';host.tasks=[{kind:'discuss',...host.meeting}]}
   else{
    const worker=[...host.workers].filter(w=>active(w.activity)).sort((a,b)=>(rank[b.activity.state]||0)-(rank[a.activity.state]||0))[0],object=worker&&this.objectsById.get(worker.activity.objectId),room=object?this.roomFor(object):this.rooms.get('__lobby');
    if(!worker){host.roomId='__lobby';host.tasks=this.loungeLeisureTasks(host.id)}
    else{const index=roomUse.get(room.id)||0;roomUse.set(room.id,index+1);host.roomId=room.id;host.tasks=[{kind:'supervise',...this.world.coordinationPoint(room,index)}]}
   }
   host.taskIndex=0;this.routeActor(host);
  }
  for(const worker of this.workerActors){const old=worker.old;this.planWorker(worker,old?.activityKey===keyFor(worker.activity)?old:null);delete worker.old}
  this.workerJobs=new Map(this.workerActors.map(actor=>[actor.id,actor.job]));
  for(const room of this.rooms.values()){room.jobs=this.workerActors.filter(actor=>actor.job.roomId===room.id);const running=room.jobs.filter(actor=>actor.job.state==='running').length,label=this.labelItems.find(label=>label.kind==='room'&&label.id===room.id),small=label?.el.querySelector('small');if(small&&running)small.textContent+=' · '+running+'건 진행'}
 },
 handoffPoint(actor,standby=false){
  const host=actor.host,target=host.arriving?this.world.gates[host.gateLane].outside:host.tasks[0],index=host.workers.indexOf(actor),side=(index-(host.workers.length-1)/2)*1.45,rotation=target.rotation||0;
  return {x:target.x+Math.sin(rotation)*1.9+Math.cos(rotation)*side,z:target.z+Math.cos(rotation)*1.9-Math.sin(rotation)*side,rotation:rotation+Math.PI,seated:false};
 },
 loungeLeisureTasks(id){
  const room=this.rooms.get('__lobby'),at=(x,z)=>{const point=this.world.local(room,x,z),node=this.world.nav.nearest(point);return node?{x:node.x*this.world.nav.step,z:node.z*this.world.nav.step}:point};
  const planter=this.world.decorations.get('built:__lobby:planter:10:3.35')?.prop||this.world.decorations.get('built:__lobby:planter:-10:3.35')?.prop||{x:-10,z:3.35};
  const view=this.world.planterPoint(id,room,planter),coffee=this.world.coffeePoint(id),walks=[[-5,3],[3,-6],[6,3],[-3,-4]],index=hash(id)%walks.length,seat=this.world.restPoint(id,true);
  const tasks=[
   {kind:'wander',leisure:true,duration:1.4,...at(...walks[index])},
   {kind:'coffee',leisure:true,duration:9+hash(id)%4,...coffee},
   {kind:'admire',leisure:true,duration:5.5,...view},
   {kind:'sit',leisure:true,duration:8,...seat},
   {kind:'wander',leisure:true,duration:1.4,...at(...walks[(index+2)%walks.length])}
  ];
  const start=hash(id+':leisure')%tasks.length;return [...tasks.slice(start),...tasks.slice(0,start)];
 },
 planWorker(actor,old){
  const object=this.objectsById.get(actor.activity.objectId),room=object?this.roomFor(object):this.rooms.get('__lobby'),station=this.objectStations.get(object?.id),access=actor.activity.access;
  actor.roomId=room.id;actor.carrying=false;actor.terminal=null;actor.preferredTerminal=old?.terminalIndex;
  // Terminals illustrate already-running work, even while the character is elsewhere.
  if(actor.job.state==='running'&&(access==='write'||room.zone==='resource')&&station){actor.terminal=this.world.workPoint(actor.id,room,actor.preferredTerminal);if(actor.terminal&&room.zone!=='resource')this.world.showTerminal(actor.id,room,object)}
  if(object&&room.zone==='concept')this.world.conceptCube(actor.props.specimen,object,0,0,.21,.32);
  if(['error','conflict'].includes(actor.activity.state))actor.tasks=[{kind:'report',duration:2.4},{kind:'awaitReply',duration:8}];
  else if(['idle','done'].includes(actor.job.state))actor.tasks=this.loungeLeisureTasks(actor.id);
  else if(actor.job.state!=='running'||!station||this.bridge.observedOnly)actor.tasks=[{kind:'standby'}];
  else{
   actor.tasks=[{kind:'receive',duration:1.1},{kind:'collect',duration:.85,...this.world.stationPoint(station,actor.id)}];
   if(access==='read'){if(room.zone==='resource')actor.tasks.push({kind:'observe'});actor.tasks.push({kind:'read',duration:9+hash(actor.id)%5,...(room.zone==='resource'?{}:this.world.stationPoint(station,actor.id))})}
   else{actor.tasks.push({kind:'observe'});if(room.zone==='concept')actor.tasks.push({kind:'deposit',duration:1.1});actor.tasks.push({kind:'work',duration:15+hash(actor.id)%8})}
   actor.tasks.push({kind:'report',duration:1.25});
  }
  actor.taskIndex=Math.max(0,actor.tasks.findIndex(task=>task.kind===old?.taskKind));actor.carrying=['read','work','deposit','report'].includes(actor.tasks[actor.taskIndex].kind)&&active(actor.activity);this.routeActor(actor);
 },
 routeActor(actor){
  let task;
  if(actor.role==='helper'&&actor.arriving){const gate=this.world.gates[actor.gateLane],phase=actor.arrivalPhase;task={kind:phase,...(phase==='enter'?gate.inside:phase==='queue'?gate.outside:gate.badge)}}
  else{
   task={...actor.tasks[actor.taskIndex]};
   if(actor.role==='worker'){
    if(['receive','report','standby','awaitReply'].includes(task.kind))Object.assign(task,this.handoffPoint(actor,['standby','awaitReply'].includes(task.kind)));
    if(['observe','deposit','work'].includes(task.kind)||task.kind==='read'&&this.rooms.get(actor.roomId)?.zone==='resource'){
     const room=this.rooms.get(actor.roomId),spot=this.world.workPoint(actor.id,room,actor.preferredTerminal);actor.terminal=spot;
     if(!spot){task={kind:'observe',...this.world.observationPoint(actor.id,room)}}
     else if(task.kind==='observe'){actor.taskIndex++;return this.routeActor(actor)}
     else{Object.assign(task,spot);if(task.kind==='work'&&room.zone!=='resource')this.world.showTerminal(actor.id,room,this.objectsById.get(actor.activity.objectId))}
    }
   }
  }
  if(actor.coffeeCarry&&!task.leisure){this.world.spillCoffee(actor);actor.coffeeCarry=false}
  actor.task=task;actor.goal={x:task.x,z:task.z};const path=this.world.nav.path(actor.group.position,actor.goal);actor.blocked=path===null;actor.path=path||[];actor.taskStarted=null;
 },
 advanceWorker(actor){
  const kind=actor.task.kind;
  if(kind==='collect')actor.carrying=true;
  if(kind==='deposit'){actor.carrying=false;this.world.showTerminal(actor.id,this.rooms.get(actor.roomId),this.objectsById.get(actor.activity.objectId))}
  if(['read','work'].includes(kind)&&this.rooms.get(actor.roomId)?.zone==='resource'){this.world.releaseWork(actor.id);actor.terminal=null;actor.carrying=true}
  if(kind==='report')actor.carrying=false;
  actor.taskIndex=(actor.taskIndex+1)%actor.tasks.length;this.routeActor(actor);
 },
 jobAction(actor){
  if(this.bridge.observedOnly)return actor.job?.label||'';
  if(actor.activity?.hiddenTarget)return '작업 중';const job=actor.job;if(!job)return '';
  if(job.state==='done')return '작업 완료';if(job.state==='error')return '오류 / 중단';if(job.state==='conflict')return '협의 필요';if(job.state==='idle')return '작업 대기';
  const theme=zones[this.rooms.get(job.roomId)?.zone];return (job.access==='read'?theme?.read||'읽기':theme?.write||'쓰기')+' 중';
 },
 actorAction(actor){
  if(actor.activity?.hiddenTarget||actor.role==='helper'&&actor.workers?.some(worker=>worker.activity.hiddenTarget))return '작업 중';const visual=this.visualAction(actor);
  if(actor.role==='helper'){const running=actor.workers.filter(worker=>worker.job.state==='running').length;return running?'작업 '+running+'건 진행 · '+visual:visual}
  if(actor.job.state==='idle')return visual;
  const job=this.jobAction(actor);return !actor.path.length&&['work','read'].includes(actor.task.kind)?job:job+' · '+visual;
 },
 visualAction(actor){
  if(actor.blocked)return '이동 멈춤';
  if(actor.task?.leisure){
   if(actor.coffeeCarry&&actor.task.kind!=='coffee')return actor.path.length?'커피 들고 이동 중':actor.task.kind==='sit'?'커피 들고 휴식 중':actor.task.kind==='admire'?'커피 들고 화단 구경 중':'커피 들고 산책 중';
   if(actor.path.length)return actor.task.kind==='coffee'?'카페로 이동 중':actor.task.kind==='wander'?'라운지 산책 중':'라운지에서 이동 중';
   return {wander:'라운지 산책',coffee:'커피 마시는 중',sit:'라운지에 앉아 휴식',admire:'화단 구경 중'}[actor.task.kind]||'라운지 휴식';
  }
  if(actor.role==='helper'){
   if(actor.arriving)return actor.arrivalPhase==='badge'?'사원증 확인':actor.arrivalPhase==='queue'?'입장 대기':'출근 중';
   if(actor.path.length)return '이동 중';
   if(actor.commanding)return actor.commanding.task.kind==='report'?'워커 보고 받는 중':'워커에게 지시 중';
   if(actor.task.kind==='discuss')return (this.helperActors.find(a=>a.id===actor.peerId)?.helper.name||'도우미')+'와 협의';
   return actor.task.kind==='rest'?'라운지 휴식':'워커 '+actor.workers.length+'명 지휘';
  }
  if(actor.suspended)return '소환 대기';if(actor.path.length)return '이동 중';
  const kind=actor.task.kind,theme=zones[this.rooms.get(actor.roomId)?.zone];
  return kind==='receive'?'지시 확인 중':kind==='report'?['error','conflict'].includes(actor.activity.state)?'문제 보고':'진행 보고':kind==='awaitReply'?'도우미 응답 대기':kind==='standby'?'도우미 곁에서 대기':kind==='observe'?'작업 구경 중':kind==='read'?theme.read:kind==='collect'?theme===zones.resource?'자료 꺼내기':theme===zones.info?'서류 꺼내기':theme===zones.concept?'표본 꺼내기':'부품 꺼내기':kind==='deposit'?'수조에 표본 투입':kind==='work'?theme.write:'대기';
 },
 updateActors(time,dt){
  if(this.edit){this.world.tick(time,dt,this.actors);return}
  const firstArrival=this.helperActors.filter(a=>a.arriving).sort((a,b)=>a.arrivalOrder-b.arrivalOrder)[0];
  for(const host of this.helperActors)host.commanding=this.workerActors.find(w=>w.host===host&&!w.path.length&&['receive','report'].includes(w.task.kind)&&Math.hypot(w.group.position.x-host.group.position.x,w.group.position.z-host.group.position.z)<2.3);
  for(const chair of this.world.chairs)chair.group.rotation.y=chair.rotation;
  for(const actor of this.actors){
   if(actor.role==='worker'&&actor.host.arriving&&!this.bridge.observedOnly){actor.group.visible=false;actor.suspended=true;continue}
   if(actor.suspended){actor.suspended=false;actor.group.visible=true;this.placeActor(actor,null,{x:actor.host.group.position.x+.8,z:actor.host.group.position.z});this.routeActor(actor)}
   if(actor.role==='helper'&&actor.arriving&&actor.arrivalPhase==='queue'&&actor===firstArrival){actor.arrivalPhase='approach';this.routeActor(actor)}
   const moving=actor.path.length>0&&!actor.blocked;
   if(moving){const p=actor.group.position,target=actor.path[0],dx=target.x-p.x,dz=target.z-p.z,distance=Math.hypot(dx,dz),step=dt*actor.speed;if(distance<=step){p.x=target.x;p.z=target.z;actor.path.shift()}else{p.x+=dx/distance*step;p.z+=dz/distance*step;actor.group.rotation.y=Math.atan2(dx,dz)}}
   if(!actor.path.length&&!actor.blocked){
    const p=actor.group.position,goal=actor.goal;if(Math.hypot(p.x-goal.x,p.z-goal.z)<.4&&!this.world.nav.obstacles.some(o=>Math.abs(goal.x-o.x)<o.w/2&&Math.abs(goal.z-o.z)<o.d/2)){p.x=goal.x;p.z=goal.z}
    actor.taskStarted??=time;let elapsed=(time-actor.taskStarted)/1000;
    if(actor.role==='helper'&&actor.arriving){
     if(actor.arrivalPhase==='approach'){actor.arrivalPhase='badge';actor.arrivalUntil=time+1050;this.routeActor(actor)}
     else if(actor.arrivalPhase==='badge'&&time>=actor.arrivalUntil){actor.arrivalPhase='enter';this.routeActor(actor)}
     else if(actor.arrivalPhase==='enter'){actor.arriving=false;if(!this.layout.seenHelpers.includes(actor.id)){this.layout.seenHelpers.push(actor.id);this.bridge.save()}this.routeActor(actor)}
    }else if(actor.task.leisure){
     if(actor.task.kind==='coffee')actor.coffeeCarry=true;
     if(actor.task.duration&&elapsed>=actor.task.duration){actor.taskIndex=(actor.taskIndex+1)%actor.tasks.length;this.routeActor(actor)}
    }else if(actor.role==='worker'){
     if(['read','work'].includes(actor.task.kind)&&this.rooms.get(actor.roomId)?.zone==='resource')this.world.showTerminal(actor.id,this.rooms.get(actor.roomId),this.objectsById.get(actor.activity.objectId));
     if(['receive','report'].includes(actor.task.kind)&&(actor.host.path.length||Math.hypot(p.x-actor.host.group.position.x,p.z-actor.host.group.position.z)>2.3)){actor.taskStarted=time;elapsed=0}
     if(actor.task.kind==='observe'){if(time-(actor.observationCheck||0)>450){actor.observationCheck=time;this.routeActor(actor)}}
     else if(actor.task.duration&&elapsed>=actor.task.duration)this.advanceWorker(actor);
    }
   }
   this.poseActor(actor,time,dt,moving);
  }
  this.world.tick(time,dt,this.actors);
 },
 poseActor(actor,time,dt,moving){
  const still=!actor.path.length&&!actor.blocked,kind=actor.task.kind,worker=actor.role==='worker',theme=this.rooms.get(actor.roomId)?.zone,work=worker&&still&&kind==='work',read=worker&&still&&kind==='read',rest=!worker&&still&&kind==='rest',coffee=still&&kind==='coffee',admire=still&&kind==='admire',sitting=still&&kind==='sit',badge=!worker&&still&&actor.arriving&&actor.arrivalPhase==='badge';
  if(still&&Number.isFinite(actor.task.rotation))actor.group.rotation.y=actor.task.rotation;else if(badge)actor.group.rotation.y=Math.PI;
  let facing=null;if(!worker&&still&&actor.commanding)facing=actor.commanding;else if(!worker&&still&&kind==='discuss')facing=this.helperActors.find(a=>a.id===actor.peerId);else if(worker&&still&&['receive','report','standby','awaitReply'].includes(kind))facing=actor.host;
  if(worker&&still&&kind==='observe')facing=this.actors.find(a=>a.id===actor.task.ownerId)||null;
  const look=facing?Math.atan2(facing.group.position.x-actor.group.position.x,facing.group.position.z-actor.group.position.z):actor.group.rotation.y;
  const relative=Math.atan2(Math.sin(look-actor.group.rotation.y),Math.cos(look-actor.group.rotation.y));
  actor.head.rotation.y+=(Math.max(-.7,Math.min(.7,relative))-actor.head.rotation.y)*Math.min(1,dt*8);
  const rightArm=actor.limbs[0],leftArm=actor.limbs[1],rightX=rightArm.rotation.x,rightZ=rightArm.rotation.z,leftX=leftArm.rotation.x,leftZ=leftArm.rotation.z,elbowX=actor.elbows.map(joint=>joint.rotation.x);
  for(const limb of actor.limbs)limb.rotation.set(0,0,0);
  actor.elbows[0].rotation.x=actor.elbows[1].rotation.x=-.2;actor.knees[0].rotation.x=actor.knees[1].rotation.x=0;
  const stride=moving?Math.sin(time*(worker?.016:.01)):0,armSwing=stride*(worker?.32:.25),legSwing=stride*(worker?.65:.5);
  actor.limbs[0].rotation.x=armSwing;actor.limbs[1].rotation.x=-armSwing;actor.limbs[2].rotation.x=-legSwing;actor.limbs[3].rotation.x=legSwing;
  if(worker&&still&&['read','collect','deposit','report'].includes(kind)){
   actor.limbs[0].rotation.x=-.14;
   actor.limbs[1].rotation.x=(kind==='collect'||kind==='deposit'?-.48:kind==='read'?-.42:-.3)+Math.sin(time*.004)*.04;
   actor.elbows[1].rotation.x=kind==='report'?-.45:-.7;
  }
  if(work){const frequency=theme==='feature'?.026:theme==='module'?.009:.016,motion=Math.sin(time*frequency);actor.limbs[0].rotation.x=-.22+motion*.05;actor.limbs[1].rotation.x=-.42-motion*.08;actor.elbows[1].rotation.x=-.58-motion*.12}
  if(!worker&&still&&!actor.task.leisure&&(actor.commanding||kind==='discuss')){actor.limbs[0].rotation.x=-.1;actor.limbs[1].rotation.x=-.3+Math.sin(time*.003)*.08;actor.elbows[1].rotation.x=-.8;actor.limbs[1].rotation.z=.12}
  actor.body.rotation.x=worker&&still&&kind==='observe'?.08:0;
  if(rest||sitting){actor.limbs[0].rotation.x=-.22;actor.limbs[1].rotation.x=rest?-.35+Math.sin(time*.001)*.04:-.22;actor.elbows[0].rotation.x=-.45;actor.elbows[1].rotation.x=-.55}
  if(coffee){const sip=(1+Math.sin(time*.002+hash(actor.id)))/2;actor.limbs[0].rotation.x=-.08;actor.limbs[1].rotation.x=-.4-sip*.75;actor.elbows[1].rotation.x=-.75-sip*.4;actor.limbs[1].rotation.z=.08}
  else if(actor.coffeeCarry){actor.limbs[1].rotation.x=-.25+(moving?stride*.025:0);actor.elbows[1].rotation.x=-.85;actor.limbs[1].rotation.z=.07}
  if(admire){actor.limbs[0].rotation.x=-.12;actor.head.rotation.x=.12+Math.sin(time*.0015)*.05}
  else actor.head.rotation.x=0;
  if(badge){actor.limbs[1].rotation.x=-1;actor.elbows[1].rotation.x=-.85}
  const armEase=1-Math.exp(-Math.max(0,dt)*10);
  rightArm.rotation.x=rightX+(rightArm.rotation.x-rightX)*armEase;rightArm.rotation.z=rightZ+(rightArm.rotation.z-rightZ)*armEase;
  leftArm.rotation.x=leftX+(leftArm.rotation.x-leftX)*armEase;leftArm.rotation.z=leftZ+(leftArm.rotation.z-leftZ)*armEase;
  actor.elbows.forEach((joint,index)=>{joint.rotation.x=elbowX[index]+(joint.rotation.x-elbowX[index])*armEase});
  const seated=still&&actor.task.seated,targetY=seated?(actor.task.seatHeight??.565)-(worker?.42:.84):0;actor.group.position.y+=(targetY-actor.group.position.y)*Math.min(1,dt*9);if(seated){actor.limbs[2].rotation.x=actor.limbs[3].rotation.x=-1.25;actor.knees[0].rotation.x=actor.knees[1].rotation.x=1.1;if(actor.task.chair)actor.task.chair.rotation.y=actor.group.rotation.y}
  actor.shadow.position.y=(.08-actor.group.position.y)/(worker?.5:1);actor.body.position.y=moving?Math.abs(Math.sin(time*(worker?.022:.01)))*.035:Math.sin(time*.002+hash(actor.id))*.008;
  for(const prop of Object.values(actor.props))prop.visible=false;
  if(worker&&kind!=='observe'&&(actor.carrying||read||still&&kind==='deposit'||still&&kind==='collect'&&(time-(actor.taskStarted??time))>500)&&!(work&&theme==='info')&&!(theme==='resource'&&still&&(work||read))){const prop=theme==='resource'?(this.objectsById.get(actor.activity.objectId)?.kind==='mesh'?actor.props.frame:actor.props.paper):theme==='info'?actor.props.paper:theme==='feature'?actor.props.part:theme==='module'?actor.props.frame:actor.props.specimen;prop.visible=true}
  actor.props.pen.visible=work&&['info','feature','resource'].includes(theme);actor.props.frame.visible||=work&&theme==='module';actor.props.badge.visible=badge;actor.props.cup.visible=rest||coffee||!!actor.coffeeCarry;actor.props.sparks.visible=work&&theme==='feature'&&Math.sin(time*.035)>-.25;if(actor.props.sparks.visible)actor.props.sparks.rotation.y=time*.004;
 }
};
