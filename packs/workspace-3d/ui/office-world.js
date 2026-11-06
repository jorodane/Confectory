import * as THREE from './assets/three.module-0.160.1.js';

export const zones={
 concept:{name:'개념 연구실',short:'연구실',color:'#dce9e6',floor:['#c2cdca','#d5ddda'],wall:'#b9c8c5',axis:'z',sign:-1,read:'표본 관찰',write:'배양 제어'},
 info:{name:'정보 사무실',short:'사무실',color:'#d6b992',floor:['#544e46','#5b554b'],wall:'#797367',axis:'x',sign:-1,read:'서류 열람',write:'서류 작성'},
 feature:{name:'기능 공장',short:'공장',color:'#dfa665',floor:['#41484a','#474e50'],wall:'#637073',axis:'x',sign:1,read:'부품 검사',write:'납땜'},
 module:{name:'모듈 조립실',short:'조립실',color:'#a5c49c',floor:['#404d48','#48554d'],wall:'#657970',axis:'x',sign:1,read:'부품틀 확인',write:'조립'},
 resource:{name:'자료실',short:'자료실',color:'#b7b8d4',floor:['#737b83','#839099'],wall:'#aab4bc',axis:'x',sign:-1,read:'자료 열람',write:'자료 정리'}
};
const loungeTheme={floor:['#bfc2bb','#d2d4cd'],wall:'#bcc3b9'};
const cafeTheme={floor:['#8d765b','#9b8264'],wall:'#b9ae9a'};
const roadThemes={
 lounge:{base:'#4b5654',surface:'#59635e',edge:'#b8aa8c',mark:'#dbc59e'},
 cafe:{base:'#514b43',surface:'#75644f',edge:'#d1b487',mark:'#ebd4a5'},
 concept:{base:'#40545c',surface:'#537078',edge:'#a7cbd0',mark:'#91bcc9'},
 info:{base:'#504a43',surface:'#716659',edge:'#c8b89a',mark:'#d7c5a0'},
 feature:{base:'#50463f',surface:'#735746',edge:'#e3a05c',mark:'#f2b873'},
 module:{base:'#414c44',surface:'#59705a',edge:'#a5be8f',mark:'#c0d3a4'}
};
const clamp=(n,a,b)=>Math.max(a,Math.min(b,n));
const hash=value=>[...String(value)].reduce((n,c)=>(n*31+c.charCodeAt(0))>>>0,0);
export const zoneOf=object=>Object.hasOwn(zones,object?.group)?object.group:'concept';
const point=(axis,forward,lateral)=>axis==='x'?{x:forward,z:lateral}:{x:lateral,z:forward};

export function makeFloorplan(objects){
 const categories=objects.filter(o=>o.kind==='Category'),byId=new Map(categories.map(o=>[o.id,o])),parents=new Map(),plans=new Map(),forests={};
 // Break physical cycles without changing category ownership or inheritance.
 for(const category of categories){let parent=byId.get(category.parent),p=parent,seen=new Set([category.id]);while(p&&!seen.has(p.id)){seen.add(p.id);p=byId.get(p.parent)}if(p||parent&&zoneOf(parent)!==zoneOf(category))parent=null;parents.set(category.id,parent?.id||'__'+zoneOf(category))}
 for(const key of Object.keys(zones)){
  const members=categories.filter(o=>zoneOf(o)===key),roots=members.filter(o=>parents.get(o.id)==='__'+key),tree=new Map(),seen=new Set();let cursor=0;
  const walk=(node,depth)=>{if(seen.has(node.id))return;seen.add(node.id);const children=members.filter(o=>parents.get(o.id)===node.id);children.forEach(c=>walk(c,depth+1));const leaves=children.map(c=>tree.get(c.id)).filter(Boolean),lane=leaves.length?leaves.reduce((n,p)=>n+p.lane,0)/leaves.length:cursor++;tree.set(node.id,{depth,lane})};roots.forEach(o=>walk(o,1));members.forEach(o=>{if(!seen.has(o.id)){parents.set(o.id,'__'+key);walk(o,1)}});forests[key]={tree,leaves:Math.max(1,cursor)};
 }
 const widest=Math.max(forests.concept.leaves,forests.info.leaves,forests.feature.leaves+forests.module.leaves),laneStep=13,levelStep=15,distance=26+Math.max(0,widest-2)*3;
 plans.set('__lobby',{id:'__lobby',zone:'lounge',parent:null,x:0,z:0,w:24,d:21,category:{id:'__lobby',name:'중앙 라운지',kind:'Lobby'}});
 plans.set('__cafe',{id:'__cafe',zone:'lounge',parent:'__lobby',x:-8,z:-19,w:12,d:8,category:{id:'__cafe',name:'카페 · 라운지',kind:'Lounge'}});
 for(const [key,theme] of Object.entries(zones)){
  if(key==='resource')continue;
  const forest=forests[key],industrialOffset=key==='feature'?-(forests.module.leaves+1)*laneStep/2:key==='module'?(forests.feature.leaves+1)*laneStep/2:0;
  // The café is fixed beside the concept wing; empty projects still need room and corridor clearance.
  const cafe=plans.get('__cafe'),zoneDistance=key==='concept'?Math.max(distance,Math.ceil(Math.abs(cafe.z)+cafe.d/2+4.5+4)):distance;
  const center=point(theme.axis,theme.sign*zoneDistance,industrialOffset),foyerId='__'+key;plans.set(foyerId,{id:foyerId,zone:key,parent:'__lobby',...center,w:10,d:9,category:{id:foyerId,name:theme.name,kind:'Zone',group:key}});
  for(const category of categories.filter(o=>zoneOf(o)===key)){const position=forest.tree.get(category.id),lateral=(position.lane-(forest.leaves-1)/2)*laneStep+industrialOffset;plans.set(category.id,{id:category.id,zone:key,parent:parents.get(category.id),...point(theme.axis,theme.sign*(zoneDistance+position.depth*levelStep),lateral),w:10,d:9,category})}
 }
 const office=plans.get('__info');plans.set('__resources',{id:'__resources',zone:'resource',parent:'__info',x:office.x,z:office.z+16,w:10,d:9,category:{id:'__resources',name:'자료실',kind:'ResourceLibrary',group:'resource'}});
 return plans;
}

class MinHeap{
 constructor(){this.data=[]}
 push(value){let i=this.data.length;this.data.push(value);while(i){const p=(i-1)>>1;if(this.data[p].score<=value.score)break;this.data[i]=this.data[p];i=p}this.data[i]=value}
 pop(){const top=this.data[0],last=this.data.pop();if(this.data.length){let i=0;while(i*2+1<this.data.length){let child=i*2+1;if(child+1<this.data.length&&this.data[child+1].score<this.data[child].score)child++;if(this.data[child].score>=last.score)break;this.data[i]=this.data[child];i=child}this.data[i]=last}return top}
 get length(){return this.data.length}
}

export class FloorNavigation{
 constructor(){this.step=1;this.cells=new Set();this.obstacles=[]}
 key(x,z){return x+','+z}
 addRect(x,z,w,d){const s=this.step;for(let ix=Math.ceil((x-w/2)/s);ix<=Math.floor((x+w/2)/s);ix++)for(let iz=Math.ceil((z-d/2)/s);iz<=Math.floor((z+d/2)/s);iz++)this.cells.add(this.key(ix,iz))}
 block(x,z,w,d){this.obstacles.push({x,z,w:w+.55,d:d+.55})}
 finish(){for(const key of this.cells){const [x,z]=key.split(',').map(Number);if(this.obstacles.some(o=>Math.abs(x*this.step-o.x)<o.w/2&&Math.abs(z*this.step-o.z)<o.d/2))this.cells.delete(key)}}
 nearest(p){const x=Math.round(p.x/this.step),z=Math.round(p.z/this.step);if(this.cells.has(this.key(x,z)))return {x,z};for(let r=1;r<=20;r++){let best=null,distance=Infinity;for(let dx=-r;dx<=r;dx++)for(const dz of [-r,r])if(this.cells.has(this.key(x+dx,z+dz))&&dx*dx+dz*dz<distance){best={x:x+dx,z:z+dz};distance=dx*dx+dz*dz}for(let dz=-r+1;dz<r;dz++)for(const dx of [-r,r])if(this.cells.has(this.key(x+dx,z+dz))&&dx*dx+dz*dz<distance){best={x:x+dx,z:z+dz};distance=dx*dx+dz*dz}if(best)return best}return null}
 path(from,to,diagonal=false){
  const start=this.nearest(from),end=this.nearest(to);if(!start||!end)return null;const startKey=this.key(start.x,start.z),endKey=this.key(end.x,end.z),heap=new MinHeap(),cost=new Map([[startKey,0]]),came=new Map(),closed=new Set(),heuristic=(x,z)=>Math.hypot(x-end.x,z-end.z);heap.push({...start,key:startKey,score:heuristic(start.x,start.z)});
  while(heap.length&&closed.size<40000){const current=heap.pop();if(closed.has(current.key))continue;if(current.key===endKey){const result=[];let key=endKey;while(key!==startKey){const [x,z]=key.split(',').map(Number);result.push({x:x*this.step,z:z*this.step});key=came.get(key)}result.reverse();return result.filter((p,i)=>!i||i===result.length-1||Math.sign(p.x-result[i-1].x)!==Math.sign(result[i+1].x-p.x)||Math.sign(p.z-result[i-1].z)!==Math.sign(result[i+1].z-p.z))}closed.add(current.key);
   for(const [dx,dz] of [[1,0],[-1,0],[0,1],[0,-1],[1,1],[1,-1],[-1,1],[-1,-1]]){if(!diagonal&&dx&&dz)continue;const x=current.x+dx,z=current.z+dz,key=this.key(x,z);if(!this.cells.has(key)||closed.has(key)||dx&&dz&&(!this.cells.has(this.key(current.x+dx,current.z))||!this.cells.has(this.key(current.x,current.z+dz))))continue;const next=cost.get(current.key)+Math.hypot(dx,dz);if(next>=(cost.get(key)??Infinity))continue;cost.set(key,next);came.set(key,current.key);heap.push({x,z,key,score:next+heuristic(x,z)})}
  }return null;
 }
}

export class OfficeWorld{
 constructor(office){this.o=office;this.nav=new FloorNavigation();this.assets=[];this.iconCache=new Map();this.cubeIconCache=new Map();this.conceptCubes=new Map();this.decorations=new Map();this.animated=[];this.gates=[];this.restSpots=[];this.chairs=[];this.workClaims=new Map();this.restClaims=new Map();this.interactionClaims=new Map();this.connections=[];this.signs=new Map();this.wallSegments=[];this.dirt=[];this.cleaners=[];this.activityTraces=new Map();this.coverageCache=new Map();this.cleanerProvisionTimer=0;this.nextCleanerId=0;this.dirtSerial=0;this.disposed=false}
 box(parent,x,y,z,w,h,d,color,pick){return this.o.box(parent,x,y,z,w,h,d,color,pick)}
 local(room,x,z){return {x:room.group.position.x+x,z:room.group.position.z+z}}
 obstacle(room,x,z,w,d){const p=this.local(room,x,z);this.nav.block(p.x,p.z,w,d)}
 shape(parent,x,y,z,w,h,d,color,type='cylinder'){this.geometry??={};const geometry=this.geometry[type]??=type==='cylinder'?new THREE.CylinderGeometry(1,1,1,16):new THREE.IcosahedronGeometry(1,0),mesh=new THREE.Mesh(geometry,this.o.mat(color));mesh.position.set(x,y,z);mesh.scale.set(w,h,d);parent.add(mesh);return mesh}
 glass(color='#a8dce1',opacity=.25){const material=new THREE.MeshLambertMaterial({color,transparent:true,opacity,depthWrite:false});this.assets.push(material);return material}
 text(parent,text,x,y,z,width=2.4,color='#f4e3bd',background='#273337',overlay=false){
  const key=[text,color,background,overlay].join('|');let material=this.iconCache.get(key);if(!material){const canvas=document.createElement('canvas');canvas.width=512;canvas.height=128;const ctx=canvas.getContext('2d');ctx.fillStyle=background;ctx.fillRect(0,0,512,128);ctx.strokeStyle=color;ctx.lineWidth=4;ctx.strokeRect(5,5,502,118);ctx.fillStyle=color;ctx.font='bold 42px sans-serif';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(String(text).slice(0,30),256,66,480);const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace;material=new THREE.SpriteMaterial({map:texture,depthWrite:false,depthTest:!overlay});this.assets.push(texture,material);this.iconCache.set(key,material)}const sprite=new THREE.Sprite(material);sprite.position.set(x,y,z);sprite.scale.set(width,width/4,1);parent.add(sprite);return sprite;
 }
 icon(parent,object,x,y,z,size=.65){const symbol=String(object?.icon||object?.name?.charAt(0)||'◇').slice(0,3);return this.text(parent,symbol,x,y,z,size,'#d3eef0','#344c58')}
 conceptCube(parent,object,x,y,z,size=.5,pick=null){
  const colors=['#88bfc1','#a5d3c9','#b5c4dd','#9cc9d4','#b8d0a4','#c2b9d6'],color=colors[hash(object?.id||object?.name||'concept')%colors.length],group=new THREE.Group();group.position.set(x,y,z);parent.add(group);
  this.box(group,0,0,0,size,size,size,color,pick);this.box(group,0,size*.5+.012,0,size*.84,.024,size*.84,'#e2eee2',pick);this.box(group,0,-size*.04,size*.5+.012,size*.52,size*.52,.024,'#405c62',pick);
  const symbol=String(object?.icon||object?.name?.charAt(0)||'◇').slice(0,2);let material=this.cubeIconCache.get(symbol);
  if(!material){const canvas=document.createElement('canvas');canvas.width=128;canvas.height=128;const ctx=canvas.getContext('2d');ctx.fillStyle='#e6f6ee';ctx.font='bold 94px sans-serif';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(symbol,64,68,112);const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace;material=new THREE.MeshBasicMaterial({map:texture,transparent:true,depthWrite:false,side:THREE.DoubleSide});this.assets.push(texture,material);this.cubeIconCache.set(symbol,material)}
  this.geometry??={};const badge=new THREE.Mesh(this.geometry.cubeBadgePlane??=new THREE.PlaneGeometry(1,1),material);badge.position.set(0,-size*.04,size*.5+.03);badge.scale.set(size*.5,size*.5,1);group.add(badge);
  return group;
 }
 sign(parent,text,x,y,z,width,color,background,rotation=0,mountY=2.3,key=null,label='간판'){
  const id='sign:'+(key??this.signs.size),saved=this.o.layout.signs[id]||{},displayText=String(saved.text||text).slice(0,40),accent=saved.color||color,style=saved.style||0,backing=style===1?'#604833':style===2?'#203d43':background;
  const lines=displayText.split('\n').slice(0,2),height=lines.length>1?1.3:Math.max(.7,width*.19),group=new THREE.Group();group.name='office-sign';group.userData.signText=displayText;group.position.set(saved.x??x,y,saved.z??z);group.rotation.y=saved.rotation??rotation;group.scale.setScalar(saved.scale||1);parent.add(group);
  const pick={kind:'sign',id},room=[...this.o.rooms.values()].find(value=>value.group===parent);this.signs.set(id,{id,text:displayText,label,room,roomId:room?.id,group,defaults:{x,z,rotation,scale:1,style:0,text,color}});
  const rim=.07,innerWidth=width-2*rim,innerHeight=height-2*rim;
  // The backing fits inside the frame; side rails meet the top/bottom rails without overlapping exterior faces.
  this.box(group,0,0,0,innerWidth,innerHeight,.26,'#344247',pick);
  for(const side of [-1,1]){this.box(group,0,side*(height-rim)/2,0,width,rim,.34,style===1?'#b99364':accent,pick);this.box(group,side*(width-rim)/2,0,0,rim,innerHeight,.34,style===1?'#b99364':accent,pick)}
  const bottom=y-height/2,support=bottom-mountY;for(const side of [-1,1]){const sx=side*Math.min(1.25,width*.32);if(support>0)this.box(group,sx,-height/2-support/2,0,.1,support,.12,'#89958c');this.box(group,sx,-height/2-support,0,.3,.08,.24,'#58655e')}
  const canvas=document.createElement('canvas');canvas.width=1024;canvas.height=Math.round(1024*(height-.16)/(width-.16));const ctx=canvas.getContext('2d');ctx.fillStyle=backing;ctx.fillRect(0,0,canvas.width,canvas.height);ctx.fillStyle=accent;ctx.textAlign='center';ctx.textBaseline='middle';ctx.font=(style===2?'700 ':'600 ')+Math.min(90,Math.floor(canvas.height/(lines.length+1)*.9))+'px sans-serif';lines.forEach((line,index)=>ctx.fillText(line,512,canvas.height*(index+.5)/lines.length,960));
  const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace;const material=new THREE.MeshBasicMaterial({map:texture}),geometry=new THREE.PlaneGeometry(width-.16,height-.16);this.assets.push(texture,material,geometry);
  for(const side of [-1,1]){const face=new THREE.Mesh(geometry,material);face.position.z=side*.15;face.rotation.y=side<0?Math.PI:0;face.userData.pick=pick;group.add(face);this.o.pickables.push(face)}
  return group;
 }
 build(){
  const o=this.o,plans=makeFloorplan(o.source.objects);this.plans=plans;
  const office=o.layout.rooms.__info,library=plans.get('__resources');if(office){library.x=office.x??library.x;library.z=(office.z??0)+16}
  for(const plan of plans.values()){
   const saved=o.layout.rooms[plan.id],group=new THREE.Group(),extra=Math.max(0,Math.min(4,Math.round(saved?.size||0)));
   group.position.set(Math.round(saved?.x??plan.x),0,Math.round(saved?.z??plan.z));o.model.add(group);
   o.rooms.set(plan.id,{...plan,w:plan.w+extra,d:plan.d+extra,group,color:saved?.color|| (plan.id==='__cafe'?'#e8c58e':zones[plan.zone]?.color||'#e3ddcd'),objects:[],workSpots:[],doorways:new Map(),portals:new Map()})
  }
  this.links=[];
  for(const room of o.rooms.values())if(room.id!=='__lobby'){
   const parent=o.rooms.get(room.parent)||o.rooms.get('__'+room.zone);
   if(parent&&parent!==room)this.planConnection(parent,room)
  }
  for(const object of o.source.objects.filter(o=>o.kind!=='Category'))o.roomFor(object)?.objects.push(object);
  for(const room of o.rooms.values()){
   room.origin={x:room.group.position.x,z:room.group.position.z};this.shell(room);
   if(room.id==='__lobby')this.lounge(room);else if(room.id==='__cafe')this.cafe(room);else if(room.id==='__resources')this.resourceLibrary(room);else{this.workbench(room);room.storages=[];const count=Math.max(1,Math.min(5,Math.ceil(room.objects.length/10))),buckets=Array.from({length:count},()=>[]);room.objects.forEach((object,index)=>buckets[Math.floor(index/10)%count].push(object));buckets.forEach((items,index)=>this.storage(room,index,items));const link=this.links.find(item=>item.to===room.id),face=link?.toFace||'z+',offset=link?.toOffset||0,x=face[0]==='x'?(face[1]==='+'?room.w/2:-room.w/2):offset,z=face[0]==='z'?(face[1]==='+'?room.d/2:-room.d/2):offset;this.sign(room.group,room.category.name,x,3.05,z,Math.min(6,Math.max(3.4,room.category.name.length*.62)),room.color,'#293b3f',face[0]==='x'?Math.PI/2:0,2.4)}
   o.label(room.category.name,'room',room.id,()=>new THREE.Vector3(room.group.position.x,.25,room.group.position.z));
  }
  for(const link of this.links){this.connections.push(link);for(let i=1;i<link.route.length;i++)this.corridor(link.route[i-1],link.route[i],link.zone,link.width)}
  this.renderJunctions();
  for(const prop of o.layout.props){const room=o.rooms.get(prop.roomId);if(room)o.addPropModel(prop,room)}
  this.nav.finish();for(const room of o.rooms.values())this.pack(room.group);
 }
 shell(room){
  const {group,w,d}=room,theme=room.id==='__cafe'?cafeTheme:room.zone==='lounge'?loungeTheme:zones[room.zone],pick={kind:'room',id:room.id},floor=theme.floor;this.box(group,0,-.32,0,w+.25,.55,d+.25,'#202b30',pick);this.box(group,0,-.04,0,w+.1,.08,d+.1,room.color);
  const nx=Math.ceil(w),nz=Math.ceil(d),tiles=new THREE.InstancedMesh(this.o.boxGeometry,this.o.mat('#ffffff'),nx*nz),matrix=new THREE.Matrix4(),color=new THREE.Color();let index=0;for(let x=0;x<nx;x++)for(let z=0;z<nz;z++){matrix.compose(new THREE.Vector3((x+.5)*w/nx-w/2,.025,(z+.5)*d/nz-d/2),new THREE.Quaternion(),new THREE.Vector3(w/nx-.03,.08,d/nz-.03));tiles.setMatrixAt(index,matrix);tiles.setColorAt(index,color.set(floor[(x+z)%2]));index++}tiles.userData.pick=pick;group.add(tiles);this.o.pickables.push(tiles);this.nav.addRect(group.position.x,group.position.z,w-.45,d-.45);
  for(const face of ['x-','x+','z-','z+']){
   const axis=face[0],sign=face[1]==='+'?1:-1,length=axis==='x'?d:w,height=sign>0?.32:1.45;
   const requested=[...(room.doorways.get(face)||[]),...(room.id==='__lobby'&&face==='z+'?[[-3,3]]:[])].sort((a,b)=>a[0]-b[0]),openings=[];
   for(const [start,end] of requested){const previous=openings.at(-1);if(previous&&start<=previous[1]+.1)previous[1]=Math.max(previous[1],end);else openings.push([start,end])}
   const ranges=[];let edge=-length/2;for(const [a,b] of openings){if(a>edge)ranges.push([edge,a]);edge=b}if(edge<length/2)ranges.push([edge,length/2]);
   for(const [a,b] of ranges){this.wallSegments.push({roomId:room.id,face,a,b,height});const center=(a+b)/2,size=b-a,x=axis==='x'?sign*w/2:center,z=axis==='z'?sign*d/2:center;this.box(group,x,height/2,z,axis==='x'?.18:size,height,axis==='z'?.18:size,theme.wall,pick);this.box(group,x,height+.04,z,axis==='x'?.23:size+.05,.1,axis==='z'?.23:size+.05,room.color);this.obstacle(room,x,z,axis==='x'?.18:size,axis==='z'?.18:size)}
   for(const [a,b] of openings){const center=(a+b)/2,gap=b-a;for(const end of [a,b])this.box(group,axis==='x'?sign*w/2:end+(end<center?-.12:.12),1.15,axis==='z'?sign*d/2:end+(end<center?-.12:.12),.24,2.3,.24,room.color);this.box(group,axis==='x'?sign*w/2:center,2.3,axis==='z'?sign*d/2:center,axis==='x'?.25:gap+.5,.18,axis==='z'?.25:gap+.5,room.color)}
  }
 }
 door(room,face,offset=0){return this.local(room,face==='x-'?-room.w/2:face==='x+'?room.w/2:face[0]==='z'?offset:0,face==='z-'?-room.d/2:face==='z+'?room.d/2:offset)}
 doorOffset(room,face,other,width){const limit=(face[0]==='x'?room.d:room.w)/2-width/2-1,target=face[0]==='x'?other.group.position.z-room.group.position.z:other.group.position.x-room.group.position.x;return Math.round(clamp(target,-limit,limit))}
 doorExclusions(room,face){
  if(room.id!=='__lobby')return [];
  if(face==='z+')return [[-room.w/2,room.w/2]];
  // Side doors must end before the staff gate plane.
  if(face==='x-'||face==='x+')return [[room.d/2-3.3,room.d/2]];
  return []
 }
 portalAllowed(room,face,offset,width){return this.doorExclusions(room,face).every(([start,end])=>offset+width/2<=start||offset-width/2>=end)}
 portalChoice(room,face,other,width){
  // Ordinary rooms share one doorway per wall; the lounge may have several
  // wherever its door exclusion ranges leave space.
  const allowed=portal=>this.portalAllowed(room,face,portal.offset,portal.width),list=(room.portals.get(face)||[]).filter(allowed),hall=room.id==='__lobby',length=face[0]==='x'?room.d:room.w;
  if(this.doorExclusions(room,face).some(([start,end])=>start<=-length/2&&end>=length/2))return null;
  if(!hall)return list[0]||{face,offset:0,width};
  const desired=this.doorOffset(room,face,other,width),closest=[...list].sort((a,b)=>Math.abs(a.offset-desired)-Math.abs(b.offset-desired))[0];
  if(closest&&Math.abs(closest.offset-desired)<=Math.max(4,width+1))return closest;
  const capacity=Math.min(3,Math.max(1,Math.floor(length/6)));
  if(list.length>=capacity)return closest;
  const limit=Math.max(0,Math.floor(length/2-width/2-1)),slots=Array.from({length:limit*2+1},(_,i)=>i-limit).sort((a,b)=>Math.abs(a-desired)-Math.abs(b-desired));
  const offset=slots.find(slot=>this.portalAllowed(room,face,slot,width)&&list.every(portal=>Math.abs(portal.offset-slot)>=(portal.width+width)/2+1));
  return offset===undefined?closest||null:{face,offset,width};
 }
 commitPortal(room,portal){
  const list=room.portals.get(portal.face)||[];
  if(list.some(item=>item.offset===portal.offset))return;
  list.push(portal);room.portals.set(portal.face,list);
  const entries=room.doorways.get(portal.face)||[];entries.push([portal.offset-portal.width/2,portal.offset+portal.width/2]);room.doorways.set(portal.face,entries)
 }
 outsideDoor(point,face,other,otherFace){
  const axis=face[0],sign=face[1]==='+'?1:-1,gap=axis===otherFace[0]&&face!==otherFace?Math.abs(other[axis]-point[axis]):Infinity,distance=Math.min(3,Math.max(2,gap/2-.5));
  return axis==='x'?{x:Math.round(point.x+sign*distance),z:point.z}:{x:point.x,z:Math.round(point.z+sign*distance)}
 }
 planConnection(parent,room){
  const dx=room.group.position.x-parent.group.position.x,dz=room.group.position.z-parent.group.position.z,axes=[{axis:'x',delta:dx,strength:Math.abs(dx)/((parent.w+room.w)/2)},{axis:'z',delta:dz,strength:Math.abs(dz)/((parent.d+room.d)/2)}].sort((a,b)=>b.strength-a.strength),nav=this.corridorNavigation(),width=room.id==='__cafe'?4:3;
  // The center-to-center quadrant determines the preferred parallel walls.
  // Try the other axis and then reverse-facing parallel walls only if blocked.
  const pairs=[...axes.map(({axis,delta})=>[axis+(delta>=0?'+':'-'),axis+(delta>=0?'-':'+')]),...axes.map(({axis,delta})=>[axis+(delta>=0?'-':'+'),axis+(delta>=0?'+':'-')])];
  let best=null;
  for(const [fromFace,toFace] of pairs){
   const fromPortal=this.portalChoice(parent,fromFace,room,width),toPortal=this.portalChoice(room,toFace,parent,width);
   if(!fromPortal||!toPortal)continue;
   const from=this.door(parent,fromFace,fromPortal.offset),to=this.door(room,toFace,toPortal.offset),start=this.outsideDoor(from,fromFace,to,toFace),end=this.outsideDoor(to,toFace,from,fromFace);
   if(!nav.cells.has(nav.key(start.x,start.z))||!nav.cells.has(nav.key(end.x,end.z)))continue;
   const planned=this.lowTurnPath(nav,start,end,fromFace,toFace);
   if(!planned)continue;
   const route=[from,...planned.path,to].filter((point,index,list)=>!index||point.x!==list[index-1].x||point.z!==list[index-1].z);
   best={from:parent.id,to:room.id,fromFace,toFace,fromOffset:fromPortal.offset,toOffset:toPortal.offset,fromPortal,toPortal,route,zone:room.id==='__cafe'?'cafe':room.zone,width:Math.max(fromPortal.width,toPortal.width),turns:planned.turns,fallback:false};
   break;
  }
  if(!best){
   // Preserve a connection even after an unusual manual room arrangement.
   const fallback=pairs.map(([fromFace,toFace])=>({fromFace,toFace,fromPortal:this.portalChoice(parent,fromFace,room,width),toPortal:this.portalChoice(room,toFace,parent,width)})).find(choice=>choice.fromPortal&&choice.toPortal);if(!fallback)return;
   const {fromFace,toFace,fromPortal,toPortal}=fallback,from=this.door(parent,fromFace,fromPortal.offset),to=this.door(room,toFace,toPortal.offset),start=this.outsideDoor(from,fromFace,to,toFace),end=this.outsideDoor(to,toFace,from,fromFace);
   best={from:parent.id,to:room.id,fromFace,toFace,fromOffset:fromPortal.offset,toOffset:toPortal.offset,fromPortal,toPortal,route:[from,start,{x:end.x,z:start.z},end,to],zone:room.id==='__cafe'?'cafe':room.zone,width,turns:2,fallback:true}
  }
  this.commitPortal(parent,best.fromPortal);this.commitPortal(room,best.toPortal);this.links.push(best);this.recordRoad(best)
 }
 lowTurnPath(nav,start,end,fromFace,toFace){
  const dirs=[[1,0,'x+'],[-1,0,'x-'],[0,1,'z+'],[0,-1,'z-']],initial=dirs.findIndex(dir=>dir[2]===fromFace),arrival=dirs.findIndex(dir=>dir[2]===toFace[0]+(toFace[1]==='+'?'-':'+')),turnCost=nav.cells.size*4+1,key=(x,z,dir)=>x+','+z+','+dir,origin=key(start.x,start.z,initial),heap=new MinHeap(),cost=new Map([[origin,0]]),previous=new Map(),heuristic=(x,z)=>.8*(Math.abs(x-end.x)+Math.abs(z-end.z));
  heap.push({x:start.x,z:start.z,dir:initial,key:origin,cost:0,score:heuristic(start.x,start.z)});
  let goal=null,goalCost=Infinity,visited=0;
  while(heap.length&&visited++<Math.max(120000,nav.cells.size*4)){
   const current=heap.pop();if(current.cost!==cost.get(current.key))continue;if(current.score>=goalCost)break;
   if(current.x===end.x&&current.z===end.z){const total=current.cost+(current.dir===arrival?0:turnCost);if(total<goalCost){goal=current;goalCost=total}continue}
   for(let dir=0;dir<4;dir++){
    const x=current.x+dirs[dir][0],z=current.z+dirs[dir][1],cell=nav.key(x,z);
    if(!nav.cells.has(cell))continue;
    const next=current.cost+(dir===current.dir?0:turnCost)+(this.roadCells?.has(cell) ? .8 : 1),nextKey=key(x,z,dir);
    if(next>=(cost.get(nextKey)??Infinity))continue;
    cost.set(nextKey,next);previous.set(nextKey,current.key);heap.push({x,z,dir,key:nextKey,cost:next,score:next+heuristic(x,z)})
   }
  }
  if(!goal)return null;
  const raw=[];for(let cursor=goal.key;cursor;cursor=previous.get(cursor)){const [x,z]=cursor.split(',').map(Number);raw.push({x,z})}raw.reverse();
  const path=raw.filter((point,index)=>index===0||index===raw.length-1||(point.x-raw[index-1].x)!==(raw[index+1].x-point.x)||(point.z-raw[index-1].z)!==(raw[index+1].z-point.z));
  const turns=Math.floor(goalCost/turnCost);return {path,turns}
 }
 recordRoad(link){
  this.roadGraph??=new Map();this.roadCells??=new Set();
  const node=(x,z)=>{const key=x+','+z;if(!this.roadGraph.has(key))this.roadGraph.set(key,{x,z,zone:link.zone,neighbors:new Set()});this.roadCells.add(key);return this.roadGraph.get(key)};
  for(let i=1;i<link.route.length;i++){
   const a=link.route[i-1],b=link.route[i],axis=a.x!==b.x?'x':'z',other=axis==='x'?'z':'x';if(a[other]!==b[other]||!Number.isInteger(a[other]))continue;
   const lo=Math.ceil(Math.min(a[axis],b[axis])),hi=Math.floor(Math.max(a[axis],b[axis]));let prior=null;
   for(let value=lo;value<=hi;value++){const current=node(axis==='x'?value:a.x,axis==='z'?value:a.z);if(prior&&Math.abs(current[axis]-prior[axis])===1){current.neighbors.add(prior.x+','+prior.z);prior.neighbors.add(current.x+','+current.z)}prior=current}
  }
 }
 renderJunctions(){
  this.junctions=[];
  for(const node of this.roadGraph?.values()||[]){if(node.neighbors.size<3)continue;
   const theme=roadThemes[node.zone]||roadThemes.lounge,group=new THREE.Group();group.name='office-route-junction';group.position.set(node.x,0,node.z);this.o.model.add(group);
   this.box(group,0,-.02,0,3.05,.045,3.05,theme.surface);
   for(const edge of [-1.5,-.5,.5,1.5]){this.box(group,edge,.007,0,.025,.012,2.9,theme.edge);this.box(group,0,.008,edge,2.9,.012,.025,theme.edge)}
   this.box(group,0,.015,0,.55,.016,.55,theme.mark);this.junctions.push({x:node.x,z:node.z,degree:node.neighbors.size})
  }
 }
 corridorNavigation(){if(this.routingNav)return this.routingNav;const nav=new FloorNavigation(),rooms=[...this.o.rooms.values()];nav.step=1;const minX=Math.min(...rooms.map(r=>r.group.position.x-r.w/2))-10,maxX=Math.max(...rooms.map(r=>r.group.position.x+r.w/2))+10,minZ=Math.min(...rooms.map(r=>r.group.position.z-r.d/2))-10,maxZ=Math.max(...rooms.map(r=>r.group.position.z+r.d/2))+10;nav.addRect((minX+maxX)/2,(minZ+maxZ)/2,maxX-minX,maxZ-minZ);for(const r of rooms)nav.block(r.group.position.x,r.group.position.z,r.w+2,r.d+2);nav.finish();this.routingNav=nav;return nav}
 corridor(a,b,zone,width=2.8){const dx=b.x-a.x,dz=b.z-a.z,length=Math.hypot(dx,dz);if(length<.01)return;this.corridorKeys??=new Set();const key=[a.x,a.z,b.x,b.z].join(',');if(this.corridorKeys.has(key))return;this.corridorKeys.add(key);const theme=roadThemes[zone]||roadThemes.lounge,road=new THREE.Group();road.name='office-corridor-'+zone;road.position.set((a.x+b.x)/2,0,(a.z+b.z)/2);road.rotation.y=-Math.atan2(dz,dx);this.o.model.add(road);
  this.box(road,0,-.16,0,length+width,.18,width,theme.base);this.box(road,0,-.055,0,length+.2,.036,width-.28,theme.surface);
  const first=dx?Math.min(a.x,b.x):Math.min(a.z,b.z),last=dx?Math.max(a.x,b.x):Math.max(a.z,b.z),middle=(first+last)/2,direction=Math.sign(dx||dz);
  for(let cell=Math.ceil(first);cell<last;cell++)this.box(road,(cell-middle)*direction,-.029,0,.025,.012,width-.32,theme.edge);
  for(let lane=-width/2+1;lane<width/2-.1;lane++)this.box(road,0,-.028,lane,length+.15,.012,.025,theme.edge);
  for(const side of [-1,1])this.box(road,0,-.027,side*(width/2-.13),length+.14,.014,.065,theme.edge);
  if(zone==='feature'||zone==='cafe')this.box(road,0,-.025,0,length,.012,.055,theme.mark);
  else if(zone==='module')for(const side of [-1,1])this.box(road,0,-.025,side*.38,length,.012,.045,theme.mark);
  else for(let i=0;i<Math.min(32,Math.floor(length/2.5));i++){const offset=-length/2+1.25+i*2.5;this.box(road,offset,-.024,0,.07,.012,zone==='info'?width*.7:width*.32,theme.mark)}
  const steps=Math.ceil(length/(this.nav.step*.8));for(let i=0;i<=steps;i++)this.nav.addRect(a.x+dx*i/steps,a.z+dz*i/steps,width-.2,width-.2);
 }
 storage(room,index,items){
  const o=this.o,id=room.id+'#'+index,saved=o.layout.storages[id]??={},slots=[[-3.2,-3.8,0],[3.2,-3.8,0],[-4.3,2.2,Math.PI/2],[4.3,2.2,-Math.PI/2],[-2.7,3.8,Math.PI]],slot=slots[index],group=new THREE.Group();
  if(!Number.isInteger(saved.style)||saved.style<0||saved.style>2){saved.style=Math.floor(Math.random()*3);this.createdStyles=true}o.layout.storages[id]=saved;
  group.position.set(clamp(saved.x??slot[0],-room.w/2+.7,room.w/2-.7),0,clamp(saved.z??slot[1],-room.d/2+.7,room.d/2-.7));const hasPosition=saved.x!=null||saved.z!=null,rotation=saved.rotation??(hasPosition?(room.w/2-Math.abs(group.position.x)<room.d/2-Math.abs(group.position.z)?group.position.x<0?Math.PI/2:-Math.PI/2:group.position.z<0?0:Math.PI):slot[2]),scale=saved.scale||1;group.rotation.y=rotation;group.scale.set(.72*scale,scale,.75*scale);room.group.add(group);
  const front={x:Math.sin(rotation),z:Math.cos(rotation)},pick={kind:'storage',id},station={id,index,group,room,front,rotation,contents:items};room.storages.push(station);room.storage??=station;o.stationGroups.set(id,station);
  for(const object of items)o.objectStations.set(object.id,station);if(!index&&room.category.kind==='Category')o.objectStations.set(room.id,station);
  this.obstacle(room,group.position.x,group.position.z,(Math.abs(front.x)>.5?.85:1.9)*scale,(Math.abs(front.x)>.5?1.9:.85)*scale);
  if(room.zone==='info'){
   this.box(group,0,1,0,2.6,2,1,saved?.color||'#b2aa94',pick);
   for(const y of [.35,.88,1.42])for(const x of [-.65,.65]){this.box(group,x,y,.54,1.18,.45,.07,'#d4c8ac',pick);this.box(group,x,y,.61,.36,.06,.08,'#747c72')}
   station.drawer=this.box(group,0,.36,.6,2.4,.28,.15,'#e5d7ba',pick);station.drawer.userData.dynamic=true;
  }else if(room.zone==='feature'){
   this.box(group,0,.27,0,2.6,.54,1.1,saved?.color||'#6c7268',pick);
   for(const [x,y,z] of [[-.85,.72,.1],[-.1,.72,.1],[.65,.72,.1],[-.5,1.08,-.05],[.3,1.08,-.05]]){this.box(group,x,y,z,.62,.35,.62,'#b79768',pick);this.box(group,x,y+.22,z,.24,.12,.25,'#90b5b4')}
  }else if(room.zone==='module'){
   this.box(group,0,1,0,2.6,2,.85,saved?.color||'#54665c',pick);
   for(const y of [.3,.95,1.6]){this.box(group,0,y-.1,.1,2.7,.1,.95,'#a8b391');for(const x of [-.82,0,.82]){this.box(group,x,y+.1,.47,.6,.45,.12,'#c4ceb0',pick);this.box(group,x,y+.1,.55,.4,.27,.08,'#405a50')}}
  }else{
   this.box(group,0,.4,0,2.6,.8,1.1,saved?.color||'#657c83',pick);this.box(group,0,.85,0,2.7,.1,1.2,'#b4d0d3');
   const displayed=items.length?items:this.o.source.objects.filter(object=>object.parent===room.id);
   for(const [index,object] of displayed.slice(0,6).entries()){
    const x=(index%3-1)*.8,z=index<3?-.26:.26,cube=this.conceptCube(group,object,x,1.19,z,.48,{kind:'station',id:object.id});this.conceptCubes.set(object.id,cube)
   }
  }
  if(saved.style===1){this.box(group,0,2.13,0,2.85,.18,1.18,saved.color||'#d1b584',pick);for(const side of [-1,1])this.box(group,side*1.3,1,0,.14,1.9,1.13,'#d0b992',pick)}
  if(saved.style===2){this.box(group,0,2.08,0,2.8,.14,1.08,'#344b4e',pick);for(const side of [-1,1]){this.box(group,side*1.25,1.07,.48,.12,1.8,.12,'#7eb2a9',pick);this.box(group,side*.6,1.95,.56,.7,.08,.06,'#b9dbc9',pick)}}
 }
 interactionPoint(id,key,room,candidates){
  const claimKey=id+'|'+key,current=this.interactionClaims.get(claimKey);if(current)return current;
  const occupied=[...this.interactionClaims.entries()].filter(([owner])=>!owner.startsWith(id+'|')).map(([,spot])=>spot)
   .concat([...this.workClaims.entries()].filter(([owner])=>owner!==id).map(([,spot])=>spot),[...this.restClaims.entries()].filter(([owner])=>owner!==id).map(([,spot])=>spot));
  const unique=new Map();for(const candidate of candidates){const node=this.nav.nearest(candidate);if(!node)continue;const spot={...candidate,x:node.x*this.nav.step,z:node.z*this.nav.step};if(Math.hypot(spot.x-candidate.x,spot.z-candidate.z)>1.55||Math.abs(spot.x-room.group.position.x)>room.w/2+1.2||Math.abs(spot.z-room.group.position.z)>room.d/2+1.2)continue;unique.set(this.nav.key(node.x,node.z),spot)}
  const options=[...unique.values()],rank=spot=>{const distance=occupied.length?Math.min(...occupied.map(other=>Math.hypot(spot.x-other.x,spot.z-other.z))):3;return Math.min(distance,3)-(spot.priority||0)*.35};
  options.sort((a,b)=>rank(b)-rank(a)||hash(id+':'+key+':'+a.x+':'+a.z)-hash(id+':'+key+':'+b.x+':'+b.z));
  const chosen=options[0]||{...this.local(room,0,0),rotation:0,seated:false};this.interactionClaims.set(claimKey,chosen);return chosen;
 }
 stationPoint(station,id){
  const {room,rotation}=station,candidates=[];for(const distance of [1.35,2.15,3])for(const side of [0,-.9,.9,-1.8,1.8,-2.7,2.7,-3.6,3.6]){
   candidates.push({...this.local(room,station.group.position.x+station.front.x*distance+Math.cos(rotation)*side,station.group.position.z+station.front.z*distance-Math.sin(rotation)*side),rotation:rotation+Math.PI,seated:false,priority:distance>2?.25:0});
  }
  return this.interactionPoint(id,'station:'+station.id,room,candidates);
 }
 planterPoint(id,room,planter){
  const candidates=[],rotation=planter.rotation||0;for(const side of [1,-1])for(const offset of [0,-.9,.9,-1.8,1.8,-2.6,2.6]){
   const x=planter.x+Math.cos(rotation)*offset+Math.sin(rotation)*side*1.5,z=planter.z-Math.sin(rotation)*offset+Math.cos(rotation)*side*1.5,point=this.local(room,x,z);
   candidates.push({...point,rotation:Math.atan2(room.group.position.x+planter.x-point.x,room.group.position.z+planter.z-point.z),seated:false,priority:Math.abs(offset)>1.8?.2:0});
  }
  return this.interactionPoint(id,'planter:'+planter.x+':'+planter.z,room,candidates);
 }
 coffeePoint(id){
  const room=this.o.rooms.get('__cafe'),candidates=[];
  // Use the actual café counter, relative to its saved room position.
  for(const x of [-4,-3,-2,-1,0,1,2,3,4])candidates.push({...this.local(room,x,-1),rotation:Math.PI,seated:false,roomId:room.id});
  for(const x of [-4,-1,1,4])candidates.push({...this.local(room,x,3),rotation:Math.PI,seated:false,roomId:room.id,priority:1});
  return this.interactionPoint(id,'coffee',room,candidates);
 }
 resourceStorageSlots(room){
  const candidates=[[-room.w/2+1.65,-room.d/2+.85,0],[room.w/2-1.65,-room.d/2+.85,0],[-room.w/2+.85,0,Math.PI/2],[room.w/2-.85,0,-Math.PI/2],[-room.w/2+1.65,room.d/2-.85,Math.PI],[room.w/2-1.65,room.d/2-.85,Math.PI]],chosen=[];
  for(const [x,z,rotation] of candidates){
   const w=Math.abs(Math.cos(rotation))*2.8+Math.abs(Math.sin(rotation)),d=Math.abs(Math.sin(rotation))*2.8+Math.abs(Math.cos(rotation));
   const blocksDoor=[...room.doorways].some(([face,ranges])=>ranges.some(([start,end])=>face[0]==='z'?x+w/2>start-.3&&x-w/2<end+.3&&(face==='z-'?z-d/2<-room.d/2+2.1:z+d/2>room.d/2-2.1):z+d/2>start-.3&&z-d/2<end+.3&&(face==='x-'?x-w/2<-room.w/2+2.1:x+w/2>room.w/2-2.1)));
   if(blocksDoor||chosen.some(slot=>Math.abs(x-slot.x)<(w+slot.w)/2+.4&&Math.abs(z-slot.z)<(d+slot.d)/2+.4))continue;
   chosen.push({x,z,rotation,w,d});if(chosen.length===2)break;
  }
  return chosen;
 }
 resourceLibrary(room){
  const g=room.group,files=(this.o.source.resources||[]).filter(item=>item.kind!=='folder');room.storages=[];room.resourceCount=files.length;
  const slots=this.resourceStorageSlots(room);
  for(const [index,x] of [-2.8,1].entries()){
   const id=room.id+'#'+index,saved=this.o.layout.storages[id]||{},legacy=(saved.x??x)===x&&(saved.z??-3)===-3&&(saved.rotation??0)===0&&(saved.scale??1)===1,slot=slots[index]||{x:index?-3.35:3.35,z:3.65,rotation:Math.PI};
   if(legacy&&(saved.x!=null||saved.z!=null)){Object.assign(saved,{x:slot.x,z:slot.z,rotation:slot.rotation});this.createdStyles=true}
   const group=new THREE.Group(),rotation=saved.rotation??(legacy?slot.rotation:0),scale=saved.scale??1,pick={kind:'storage',id};group.position.set(saved.x??(legacy?slot.x:x),0,saved.z??(legacy?slot.z:-3));group.rotation.y=rotation;group.scale.set(.72*scale,scale,.75*scale);g.add(group);
   const style=saved.style||0,body=saved.color||(style===1?'#98744f':style===2?'#36535f':'#536674'),shelf=style===2?'#8ebcbe':'#d9cbb0',box=(x,y,z,w,h,d,color)=>this.box(group,x/.72,y,z/.75,w/.72,h,d/.75,color,pick);
   box(0,1.05,-.15,2.7,2.1,.55,body);for(const y of [.3,.95,1.6]){box(0,y,.2,2.75,.1,.8,shelf);for(let i=0;i<5;i++){box(-1+i*.48,y+.27,.28,.34,.43,.32,['#c7b385','#93bdb5','#b1a3be'][i%3]);box(-1+i*.48,y+.28,.46,.19,.1,.02,'#e9e3cd')}}
   if(style===1)for(const side of [-1,1])box(side*1.33,1.08,.2,.1,2.14,.8,body);if(style===2)box(0,2.15,.25,2.75,.09,.85,'#b2d9cd');
   const station={id,index,group,room,name:'자료 보관함 '+(index+1),front:{x:Math.sin(rotation),z:Math.cos(rotation)},rotation,contents:files.filter((_,i)=>i%2===index)};room.storages.push(station);room.storage??=station;this.o.stationGroups.set(id,station);for(const file of station.contents)this.o.objectStations.set(file.id,station);
   this.obstacle(room,group.position.x,group.position.z,(Math.abs(Math.cos(rotation))*2.8+Math.abs(Math.sin(rotation)))*scale,(Math.abs(Math.sin(rotation))*2.8+Math.abs(Math.cos(rotation)))*scale);
  }
  const id='built:'+room.id+':workbench',saved=this.o.layout.decorations[id]||{},prop={id,roomId:room.id,kind:'workbench',x:saved.x??0,z:saved.z??.6,rotation:saved.rotation??0,scale:saved.scale??1,style:saved.style??0,color:saved.color},table=new THREE.Group(),surface=prop.color||(prop.style===1?'#a98051':prop.style===2?'#6f919a':'#ccb996');table.position.set(prop.x,0,prop.z);table.rotation.y=prop.rotation;table.scale.setScalar(prop.scale);g.add(table);
  this.box(table,0,.69,0,4.8,.15,2,surface);for(const x of [-2,2])for(const z of [-.7,.7])this.box(table,x,.3,z,prop.style===1?.22:.15,.6,.15,prop.style===1?'#8b6a48':'#5c6c70');if(prop.style===2)this.box(table,0,.78,-.9,4.6,.06,.08,'#b8dcd1');
  room.terminals=[];room.workSpots=[];
  const spots=[[-1.1,-1.85,0],[1.1,-1.85,0],[-1.1,1.85,Math.PI],[1.1,1.85,Math.PI],[-3.1,0,Math.PI/2],[3.1,0,-Math.PI/2]],transform=(x,z)=>this.local(room,prop.x+(Math.cos(prop.rotation)*x+Math.sin(prop.rotation)*z)*prop.scale,prop.z+(-Math.sin(prop.rotation)*x+Math.cos(prop.rotation)*z)*prop.scale);
  spots.forEach(([x,z,rotation],index)=>{
   const spot=this.chair(room,x,z,rotation,false,.65);table.add(spot.chair);Object.assign(spot,transform(x,z),{index,roomId:room.id,rotation:rotation+prop.rotation,seatHeight:spot.seatHeight*prop.scale});room.workSpots.push(spot);
   const terminal=new THREE.Group(),payload=new THREE.Group();terminal.position.set(x+Math.sin(rotation)*.8,0,z+Math.cos(rotation)*.8);table.add(terminal);payload.position.y=.84;terminal.add(payload);room.terminals.push({index,group:terminal,payload,owner:null,objectId:null,room});
  });
  const angle=prop.rotation;this.obstacle(room,prop.x,prop.z,(Math.abs(Math.cos(angle))*4.8+Math.abs(Math.sin(angle))*2)*prop.scale,(Math.abs(Math.sin(angle))*4.8+Math.abs(Math.cos(angle))*2)*prop.scale);this.nav.obstacles.at(-1).fixtureId=id;this.registerDecoration(table,'자료 열람대',room,prop);
  const link=this.links.find(item=>item.to===room.id),face=link?.toFace||'z-',offset=link?.toOffset||0,x=face[0]==='x'?(face[1]==='+'?room.w/2:-room.w/2):offset,z=face[0]==='z'?(face[1]==='+'?room.d/2:-room.d/2):offset;
  this.sign(g,'자료실 · RESOURCES',x,2.8,z,5.3,'#d9d5ed','#42566a',face[0]==='x'?Math.PI/2:0,2.1);
 }
 pollutionLimit(){return 2*this.o.source.helpers.reduce((count,helper)=>count+1+this.o.workerRows(helper).length,0)}
 floorPoint(position,maxDistance=1.5){const node=this.nav.nearest(position);return node&&Math.hypot(node.x*this.nav.step-position.x,node.z*this.nav.step-position.z)<=maxDistance?{x:node.x*this.nav.step,z:node.z*this.nav.step}:null}
 cleaningAnchor(position){const room=[...this.o.rooms.values()].find(room=>Math.abs(position.x-room.group.position.x)<room.w/2&&Math.abs(position.z-room.group.position.z)<room.d/2);return room?{id:room.id,x:position.x-room.group.position.x,z:position.z-room.group.position.z}:null}
 takeCleaningState(){
  const state={cleaners:this.cleaners,dirt:this.dirt,traces:this.activityTraces,nextId:this.nextCleanerId,serial:this.dirtSerial,provisionTimer:this.cleanerProvisionTimer};
  for(const item of [...state.cleaners,...state.dirt]){item.anchor=this.cleaningAnchor(item.group.position);item.group.removeFromParent()}
  for(const cleaner of state.cleaners)cleaner.homeAnchor=this.cleaningAnchor(cleaner.home);
  this.cleaners=[];this.dirt=[];this.activityTraces=new Map();return state;
 }
 restoreCleaningState(state){
  const remap=(position,anchor)=>{const room=this.o.rooms.get(anchor?.id);return room?this.local(room,anchor.x,anchor.z):position};
  if(state){
   this.cleaners=state.cleaners;this.dirt=state.dirt;this.activityTraces=state.traces;this.nextCleanerId=state.nextId;this.dirtSerial=state.serial;this.cleanerProvisionTimer=state.provisionTimer;
   for(const item of [...this.cleaners,...this.dirt]){const p=remap(item.group.position,item.anchor),floor=this.floorPoint(p,Infinity),blocked=this.nav.obstacles.some(obstacle=>Math.abs(p.x-obstacle.x)<obstacle.w/2&&Math.abs(p.z-obstacle.z)<obstacle.d/2),next=!blocked&&Math.hypot((floor?.x??Infinity)-p.x,(floor?.z??Infinity)-p.z)<.8?p:floor;if(next){item.group.position.x=next.x;item.group.position.z=next.z}this.o.model.add(item.group)}
   for(const cleaner of this.cleaners){cleaner.home=this.floorPoint(remap(cleaner.home,cleaner.homeAnchor),Infinity);cleaner.path=this.nav.path(cleaner.group.position,cleaner.target?.group.position||cleaner.home)||[];cleaner.retry=0;this.applyCleanerAppearance(cleaner);this.registerCleanerPick(cleaner)}
  }
  if(!this.cleaners.length){const lobby=this.o.rooms.get('__lobby');this.createCleaner(this.floorPoint(this.local(lobby,-8,7),Infinity))}
  this.enforcePollutionLimit();
 }
 createCleaner(home){
   if(!home)return null;
   const group=new THREE.Group(),bodyGeometry=new THREE.CylinderGeometry(1,1,1,24),puddleGeometry=new THREE.CircleGeometry(1,12),brushes=[];
   const disk=(radius,height,y,color)=>{const mesh=new THREE.Mesh(bodyGeometry,this.o.mat(color));mesh.scale.set(radius,height,radius);mesh.position.y=y;group.add(mesh);return mesh};
   const id=this.nextCleanerId++,roundBase=disk(.4,.13,.12,'#3a4d4a'),rim=disk(.37,.07,.22,'#d8d8bd'),cap=disk(.32,.015,.263,'#91b9ac'),sensor=disk(.12,.06,.29,'#526e66'),square=this.box(group,0,.14,0,.78,.2,.76,'#3a4d4a'),squareCap=this.box(group,0,.25,0,.7,.035,.68,'#91b9ac'),antenna=this.box(group,-.2,.38,-.12,.045,.22,.045,'#d8d8bd'),antennaTip=this.box(group,-.2,.5,-.12,.08,.07,.08,'#e6c88d');
   const light=this.box(group,0,.22,.345,.19,.055,.025,'#9cebd4');for(const side of [-1,1]){this.box(group,side*.11,.18,.365,.055,.045,.025,'#263b38');const brush=new THREE.Group();brush.position.set(side*.3,.035,.22);group.add(brush);for(const angle of [0,Math.PI/3,-Math.PI/3]){const arm=this.box(brush,0,0,0,.35,.025,.035,'#d7bd80');arm.rotation.y=angle}brushes.push(brush)}
   group.name='office-robot-vacuum';group.position.set(home.x,0,home.z);const cleaner={id,group,brushes,light,roundBase,rim,cap,sensor,square,squareCap,antenna,antennaTip,resources:[bodyGeometry,puddleGeometry],puddleGeometry,home,path:[],target:null,mode:'idle',routeKind:'returning',retry:0,idleFor:0,patrolIndex:0};this.cleaners.push(cleaner);this.o.model.add(group);this.applyCleanerAppearance(cleaner);this.registerCleanerPick(cleaner);return cleaner;
 }
 registerCleanerPick(cleaner){const pick={kind:'cleaner',id:String(cleaner.id)};cleaner.group.traverse(mesh=>{if(mesh.isMesh){mesh.userData.pick=pick;this.o.pickables.push(mesh)}})}
 applyCleanerAppearance(cleaner){
  const appearance=this.o.layout.cleaners?.[cleaner.id]||{},style=appearance.style||0,color=appearance.color||['#91b9ac','#b8af8b','#99aebf','#b4a1b9'][cleaner.id%4];
  cleaner.roundBase.visible=cleaner.rim.visible=cleaner.cap.visible=style!==1;cleaner.square.visible=cleaner.squareCap.visible=style===1;cleaner.antenna.visible=cleaner.antennaTip.visible=style===2;cleaner.sensor.scale.set(style===2?.16:.12,style===2?.11:.06,style===2?.16:.12);cleaner.cap.material=cleaner.squareCap.material=this.o.mat(color);
 }
 spillCoffee(actor){
  const cleaner=this.cleaners[0];if(!cleaner||this.dirt.length>=this.pollutionLimit())return;
  const group=new THREE.Group(),scale=actor.role==='worker'?.65:1,rotation=actor.group.rotation.y,materials=[],puddles=[],drops=[];
  group.name='office-coffee-spill';group.position.set(actor.group.position.x+Math.sin(rotation)*.3,0,actor.group.position.z+Math.cos(rotation)*.3);
  const coffee=new THREE.MeshBasicMaterial({color:'#704527',transparent:true,opacity:.8,depthWrite:false});materials.push({material:coffee,opacity:.8});
  for(const [x,z,r] of [[0,0,.42],[.25,.1,.26],[-.2,.14,.24],[.06,-.23,.22]]){const mesh=new THREE.Mesh(cleaner.puddleGeometry,coffee);mesh.rotation.x=-Math.PI/2;mesh.position.set(x*scale,.024,z*scale);group.add(mesh);puddles.push({mesh,r:r*scale})}
  for(let i=0;i<6;i++){const angle=i*Math.PI/3,mesh=this.box(group,0,0,0,.065*scale,.075*scale,.065*scale,coffee);drops.push({mesh,dx:Math.cos(angle)*scale,dz:Math.sin(angle)*scale})}
  const cup=actor.props.cup.clone(true),copies=new Map();cup.traverse(mesh=>{if(!mesh.isMesh)return;delete mesh.userData.pick;const source=mesh.material;let material=copies.get(source);if(!material){material=source.clone();material.transparent=true;copies.set(source,material);materials.push({material,opacity:source.opacity})}mesh.material=material});cup.visible=true;cup.scale.setScalar(actor.role==='worker'?.5:1);cup.position.set(0,.75*scale,0);cup.rotation.y=rotation;group.add(cup);this.o.model.add(group);
  this.registerDirt({kind:'coffee',group,cup,materials,puddles,drops,scale});
 }
 registerDirt(item){item.serial=this.dirtSerial++;item.age=0;item.cleaned=0;this.dirt.push(item);for(const cleaner of this.cleaners)cleaner.retry=0;return item}
 removeDirt(item){item.group.removeFromParent();for(const {material} of item.materials)material.dispose();this.dirt=this.dirt.filter(next=>next!==item);for(const cleaner of this.cleaners)if(cleaner.target===item){cleaner.target=null;cleaner.path=[];cleaner.retry=0}}
 enforcePollutionLimit(){const limit=this.pollutionLimit();while(this.dirt.length>limit){const item=this.dirt.find(item=>!this.cleaners.some(cleaner=>cleaner.target===item))||this.dirt[0];this.removeDirt(item)}}
 dropActivityDirt(actor,kind,rotation=actor.group.rotation.y){
  if(this.dirt.length>=this.pollutionLimit())return null;
  const p=actor.group.position,angles=kind==='footprint'?[rotation+Math.PI]:[rotation+1.4,rotation-1.4,rotation+Math.PI,rotation],distances=kind==='footprint'?[.7]:[.7,1.3,1.9];let point;
  for(const distance of distances){for(const angle of angles){const candidate=this.floorPoint({x:p.x+Math.sin(angle)*distance,z:p.z+Math.cos(angle)*distance});if(candidate&&!this.dirt.some(item=>Math.hypot(item.group.position.x-candidate.x,item.group.position.z-candidate.z)<.85)){point=candidate;break}}if(point)break}if(!point)return null;
  const group=new THREE.Group(),zone=this.o.rooms.get(actor.roomId)?.zone,color=kind==='footprint'?'#6c604c':{info:'#ece3cb',concept:'#92ccd0',feature:'#b6a17e',module:'#a5bd98'}[zone]||'#ded3b6',opacity=kind==='footprint'?.48:.95,material=new THREE.MeshBasicMaterial({color,transparent:true,opacity,depthWrite:false}),scale=actor.role==='worker'?.8:1;
  group.name='office-'+kind;group.position.set(point.x,0,point.z);group.rotation.y=rotation;
  if(kind==='footprint')for(const side of [-1,1]){this.box(group,side*.12*scale,.026,side*.13*scale,.13*scale,.012,.22*scale,material);this.box(group,side*.12*scale,.026,(side*.13-.18)*scale,.1*scale,.012,.08*scale,material)}
  else for(let i=0;i<3;i++){const mesh=this.box(group,(i-1)*.16,.035+i*.012,(i%2-.5)*.16,zone==='info'?.24:.13,.025,zone==='info'?.19:.11,material);mesh.rotation.y=(i-1)*.6+(this.dirtSerial%5)*.17}
  this.o.model.add(group);return this.registerDirt({kind,group,materials:[{material,opacity}]});
 }
 emitActivityDirt(dt,actors){
  const liveIds=new Set();for(const actor of actors){liveIds.add(actor.id);const p=actor.group.position,seed=hash(actor.id),trace=this.activityTraces.get(actor.id)||{x:p.x,z:p.z,walked:seed%8,working:0};this.activityTraces.set(actor.id,trace);const dx=p.x-trace.x,dz=p.z-trace.z,distance=Math.hypot(dx,dz);trace.x=p.x;trace.z=p.z;
   if(this.o.edit||actor.suspended||!actor.group.visible||actor.arriving)continue;
   if(distance>.02&&distance<3){trace.walked+=distance;const stride=12+seed%7;if(trace.walked>=stride){trace.walked%=stride;this.dropActivityDirt(actor,'footprint',Math.atan2(dx,dz))}}
   const working=actor.role==='worker'&&!actor.path.length&&!actor.blocked&&['work','read','collect','deposit'].includes(actor.task?.kind);trace.working=working?trace.working+dt:0;if(trace.working>=5+seed%5){trace.working=0;this.dropActivityDirt(actor,'scrap')}
  }
  for(const id of this.activityTraces.keys())if(!liveIds.has(id))this.activityTraces.delete(id);
 }
 routeLength(from,path){if(path===null)return Infinity;let distance=0,previous=from;for(const point of path){distance+=Math.hypot(point.x-previous.x,point.z-previous.z);previous=point}return distance}
 coverageDistance(cleaner,item){const p=item.group.position,region=this.cleaningAnchor(p)?.id||Math.floor(p.x/8)+':'+Math.floor(p.z/8),key=cleaner.id+'|'+region;if(!this.coverageCache.has(key))this.coverageCache.set(key,this.routeLength(cleaner.home,this.nav.path(cleaner.home,p)));return this.coverageCache.get(key)}
 cleanerDock(point){
  const rooms=[...this.o.rooms.values()].sort((a,b)=>Math.hypot(a.group.position.x-point.x,a.group.position.z-point.z)-Math.hypot(b.group.position.x-point.x,b.group.position.z-point.z));
  for(const room of rooms.slice(0,2)){const candidates=[[-1,-1],[-1,1],[1,-1],[1,1],[0,1],[1,0],[-1,0]].map(([x,z])=>this.floorPoint(this.local(room,x*(room.w/2-1.3),z*(room.d/2-1.3)))).filter(Boolean).sort((a,b)=>Math.hypot(a.x-point.x,a.z-point.z)-Math.hypot(b.x-point.x,b.z-point.z));for(const home of candidates){const route=this.nav.path(home,point);if(route===null||this.routeLength(home,route)>24)continue;if(this.cleaners.some(cleaner=>this.routeLength(cleaner.home,this.nav.path(cleaner.home,home))<24))continue;return home}}
  return null;
 }
 provisionCleaners(dt){
  this.cleanerProvisionTimer-=dt;if(this.cleanerProvisionTimer>0)return;this.cleanerProvisionTimer=4;
  if(!this.dirt.length||this.cleaners.length>=Math.max(1,Math.min(this.pollutionLimit(),this.o.rooms.size)))return;
  const regions=new Map();for(const item of this.dirt){const p=item.group.position,key=this.cleaningAnchor(p)?.id||Math.floor(p.x/8)+':'+Math.floor(p.z/8);const region=regions.get(key)||{item,count:0};region.count++;regions.set(key,region)}
  const demand=[...regions.values()].map(region=>({...region,distance:Math.min(...this.cleaners.map(cleaner=>this.coverageDistance(cleaner,region.item)))})).filter(region=>region.distance>38||region.distance>26&&region.distance/3.6+region.count*1.4>20).sort((a,b)=>b.distance-a.distance||b.count-a.count);
  for(const region of demand){const home=this.cleanerDock(region.item.group.position);if(!home)continue;const added=this.createCleaner(home);for(const cleaner of this.cleaners)if(cleaner!==added&&cleaner.target&&cleaner.mode!=='cleaning'){const p=cleaner.target.group.position,nearby=this.routeLength(home,this.nav.path(home,p));if(nearby+8<this.routeLength(cleaner.group.position,cleaner.path)){cleaner.target=null;cleaner.path=[];cleaner.retry=0}}break}
 }
 assignCleaningTargets(){
  const claimed=new Set(this.cleaners.map(cleaner=>cleaner.target).filter(Boolean)),pending=()=>this.dirt.filter(item=>!claimed.has(item)),nearest=cleaner=>Math.min(...pending().map(item=>cleaner.group.position.distanceToSquared(item.group.position)));
  for(const cleaner of this.cleaners.filter(cleaner=>!cleaner.target&&!cleaner.retry).sort((a,b)=>nearest(a)-nearest(b))){cleaner.retry=1;const score=item=>cleaner.group.position.distanceToSquared(item.group.position)-Math.min(item.age,90)*5;for(const item of pending().sort((a,b)=>score(a)-score(b))){const point=this.floorPoint(item.group.position);if(!point)continue;const route=this.nav.path(cleaner.group.position,point);if(route!==null){cleaner.target=item;cleaner.path=route;cleaner.idleFor=0;claimed.add(item);break}}}
 }
 tickCleaning(time,dt,actors){
  this.enforcePollutionLimit();this.emitActivityDirt(dt,actors);
  for(const item of this.dirt){item.age+=dt;if(item.kind==='coffee'){const fall=Math.min(1,item.age/.45),spread=Math.min(1,item.age/.4);item.cup.position.y=(.75*(1-fall)+.13*fall)*item.scale;item.cup.rotation.z=fall*Math.PI*.47;item.cup.position.x=fall*.2*item.scale;for(const {mesh,r} of item.puddles)mesh.scale.setScalar(r*(.1+spread*.9));for(const {mesh,dx,dz} of item.drops){mesh.visible=item.age<.65;const t=Math.min(.65,item.age);mesh.position.set(dx*t,Math.max(.025,(.2+1.8*t-3*t*t)*item.scale),dz*t)}}for(const {material,opacity} of item.materials)material.opacity=opacity*(1-item.cleaned)}
  this.provisionCleaners(dt);for(const cleaner of this.cleaners)cleaner.retry=Math.max(0,cleaner.retry-dt);this.assignCleaningTargets();
  for(const cleaner of this.cleaners){
   if(cleaner.target&&!cleaner.path.length&&cleaner.group.position.distanceTo(cleaner.target.group.position)>1.5){const route=this.nav.path(cleaner.group.position,cleaner.target.group.position);if(route?.length)cleaner.path=route;else{cleaner.target=null;cleaner.retry=1}}
   if(cleaner.target&&!cleaner.path.length){cleaner.mode='cleaning';cleaner.target.cleaned=Math.min(1,cleaner.target.cleaned+dt/(cleaner.target.kind==='coffee'?2.4:1.2));if(cleaner.target.cleaned>=1)this.removeDirt(cleaner.target)}
   if(!cleaner.target&&!cleaner.path.length){const p=cleaner.group.position;if(Math.hypot(p.x-cleaner.home.x,p.z-cleaner.home.z)>.1){cleaner.path=this.nav.path(p,cleaner.home)||[];cleaner.routeKind='returning'}else{cleaner.idleFor+=dt;if(cleaner.idleFor>6+cleaner.id%4){cleaner.idleFor=0;const angle=(cleaner.patrolIndex++%8)*Math.PI/4,point=this.floorPoint({x:cleaner.home.x+Math.sin(angle)*4,z:cleaner.home.z+Math.cos(angle)*4});if(point){const route=this.nav.path(p,point),length=this.routeLength(p,route);if(length>=2&&length<=12){cleaner.path=route;cleaner.routeKind='patrolling'}}}}}
   if(cleaner.path.length){cleaner.mode=cleaner.target?'moving':cleaner.routeKind;const p=cleaner.group.position,target=cleaner.path[0],dx=target.x-p.x,dz=target.z-p.z,distance=Math.hypot(dx,dz),step=dt*3.6;cleaner.group.rotation.y=Math.atan2(dx,dz);if(distance<=step){p.x=target.x;p.z=target.z;cleaner.path.shift()}else{p.x+=dx/distance*step;p.z+=dz/distance*step}cleaner.idleFor=0}else if(!cleaner.target)cleaner.mode='idle';
   if(cleaner.mode!=='idle')for(const brush of cleaner.brushes)brush.rotation.y+=dt*(cleaner.mode==='cleaning'?14:8);cleaner.light.material=this.o.mat(cleaner.mode==='cleaning'?'#9cebd4':cleaner.mode==='idle'?'#88a9a3':'#ffdc8e');
  }
 }
 chair(room,x,z,rotation=0,rest=false,scale=1){
  const group=new THREE.Group(),back=.34;group.position.set(x,0,z);group.rotation.y=rotation;group.scale.setScalar(scale);room.group.add(group);
  this.box(group,0,.49,0,.68,.15,.65,'#748e83');this.box(group,0,.84,-back,.72,.72,.14,'#708a80');
  for(const side of [-1,1]){this.box(group,side*.28,.23,0,.08,.46,.5,'#465450');this.box(group,side*.38,.65,0,.1,.11,.6,'#9fb2a0')}
  const spot={...this.local(room,x,z),rotation,seated:true,seatHeight:.565*scale,id:room.id+':'+x+':'+z,chair:group};this.chairs.push({group,rotation});if(rest)this.restSpots.push(spot);return spot;
 }
 bench(room,x,z,rotation){
  const id='built:'+room.id+':bench:'+x+':'+z,saved=this.o.layout.decorations[id]||{};if(saved.deleted)return;const prop={id,roomId:room.id,kind:'bench',x:saved.x??x,z:saved.z??z,rotation:saved.rotation??rotation,scale:saved.scale??1,color:saved.color},group=new THREE.Group();group.position.set(prop.x,0,prop.z);group.rotation.y=prop.rotation;group.scale.setScalar(prop.scale);room.group.add(group);
  this.box(group,0,.48,0,2.5,.17,.76,prop.color||'#bea57b');this.box(group,0,.83,-.36,2.5,.7,.14,'#9e8262');
  for(const side of [-1,1]){this.box(group,side*1.05,.24,0,.14,.48,.6,'#6d766c');this.box(group,side*1.16,.67,0,.12,.12,.76,'#d3be98')}
  for(const offset of [-.58,.58])this.restSpots.push({...this.local(room,prop.x+Math.cos(prop.rotation)*offset*prop.scale,prop.z-Math.sin(prop.rotation)*offset*prop.scale),rotation:prop.rotation,seated:true,seatHeight:.565*prop.scale,id:id+':'+offset});
  this.registerDecoration(group,'벤치',room,prop);
 }
 registerDecoration(group,name,room,prop){const id=prop.id,pick={kind:'decor',id};group.name='office-decor-'+name;this.decorations.set(id,{name,room,group,prop});group.traverse(mesh=>{if(mesh.isMesh&&!mesh.userData.pick){mesh.userData.pick=pick;this.o.pickables.push(mesh)}})}
 builtInProp(room,kind,x,z,name,rotation=0){const id='built:'+room.id+':'+kind+':'+x+':'+z,saved=this.o.layout.decorations[id]||{};if(saved.deleted)return;const prop={id,roomId:room.id,kind,x:saved.x??x,z:saved.z??z,rotation:saved.rotation??rotation,scale:saved.scale??1,color:saved.color},group=this.o.addPropModel(prop,room,false);this.registerDecoration(group,name,room,prop)}
 planter(room,x,z,rotation=0,defaults=null){
  const id='built:'+room.id+':planter:'+x+':'+z,saved=this.o.layout.decorations[id]||{};if(saved.deleted)return;const prop={id,roomId:room.id,kind:'planter',x:saved.x??defaults?.x??x,z:saved.z??defaults?.z??z,rotation:saved.rotation??defaults?.rotation??rotation,scale:saved.scale??1,color:saved.color},group=new THREE.Group(),length=4.4;group.position.set(prop.x,0,prop.z);group.rotation.y=prop.rotation;group.scale.setScalar(prop.scale);room.group.add(group);
  this.box(group,0,.34,0,length,.68,1.05,prop.color||'#8d7256');this.box(group,0,.71,0,length-.18,.11,.88,'#554d3e');
  for(const u of [-1.7,-.85,0,.85,1.7]){this.box(group,u,.97,0,.14,.52,.14,'#648662');this.box(group,u,1.24,0,.62,.56,.56,u%2?'#719267':'#7c9d70');this.box(group,u+.12,1.5,-.08,.32,.25,.3,'#a1b98a')}
  this.obstacle(room,prop.x,prop.z,(Math.abs(Math.sin(prop.rotation))>.5?1.1:length)*prop.scale,(Math.abs(Math.sin(prop.rotation))>.5?length:1.1)*prop.scale);this.registerDecoration(group,'긴 화단',room,prop);
 }
 lounge(room){
  const g=room.group;
  this.builtInProp(room,'fountain',0,-1.5,'분수대');
  this.bench(room,-5,-1.5,Math.PI/2);this.bench(room,5,-1.5,-Math.PI/2);
  this.bench(room,-10,-2.7,Math.PI/2);this.bench(room,10,-2.7,-Math.PI/2);this.bench(room,5,-8.1,0);
  // Keep the original ID so saved user placements still override the revised default.
  this.planter(room,-10,3.35,Math.PI/2);this.planter(room,10,3.35,Math.PI/2,{x:-5,z:-8,rotation:0});
  for(const [x,z] of [[-10,-5],[10,-5]])this.builtInProp(room,'plant',x,z,'화분');
  const security=room.d/2-3.3;for(const x of [-3,-1,1,3]){this.box(g,x,.6,security,.38,1.2,.9,'#707d7c');this.box(g,x,1.26,security+.18,.4,.12,.5,'#b8c9c4');this.box(g,x,1.34,security+.32,.24,.035,.2,'#334c50');this.obstacle(room,x,security,.38,.9)}for(const side of [-1,1]){this.box(g,side*7.5,.88,security,8.6,1.5,.1,this.glass('#bad9d8',.3));this.obstacle(room,side*7.5,security,8.6,.1)}
  for(let lane=0;lane<3;lane++){const x=(lane-1)*2,flap=this.box(g,x,1.01,security,1.55,.65,.08,this.glass('#8dd6ce',.52));flap.userData.dynamic=true;const light=this.box(g,x-.75,1.35,security+.4,.16,.06,.12,'#b4d3a0');light.userData.dynamic=true;this.gates.push({lane,flap,light,open:0,badge:this.local(room,x-.5,security+1.1),inside:this.local(room,x,security-1.6),outside:this.local(room,x,room.d/2+3.6)})}
  this.box(g,0,-.14,room.d/2+3.1,6.2,.24,6.5,'#435458');this.nav.addRect(room.group.position.x,room.group.position.z+room.d/2+3.1,5.8,6.5);this.sign(g,'STAFF ENTRANCE',0,3.15,room.d/2,5.6,'#edd9b2','#3b494a',0,2.3,'entrance','입구 간판');
  for(const [key,text] of [['concept','개념 · CONCEPT LAB'],['info','정보 · OFFICE'],['feature','기능 · FACTORY'],['module','모듈 · ASSEMBLY']]){const link=this.links.find(item=>item.from===room.id&&item.to==='__'+key);if(!link)continue;const face=link.fromFace,p=this.door(room,face,link.fromOffset),local={x:p.x-room.group.position.x,z:p.z-room.group.position.z};this.sign(g,text,local.x,3.1,local.z,4.8,zones[key].color,'#293d43',face[0]==='x'?Math.PI/2:0,2.3,'way:'+key,zones[key].name+' 간판')}
 }
 cafe(room){
  const g=room.group,pick={kind:'room',id:room.id};
  this.box(g,0,.58,-2.45,8.5,1.16,1.4,'#92765a',pick);this.box(g,0,1.2,-2.45,8.8,.14,1.6,'#dbc198',pick);this.obstacle(room,0,-2.45,8.8,1.6);
  this.box(g,-2.8,1.61,-2.5,1.25,.68,.6,'#394747');this.box(g,-2.8,1.63,-2.16,.9,.24,.1,'#b1c9ba');
  for(const x of [-.5,.3,1.1])this.shape(g,x,1.39,-2.1,.14,.28,.14,'#eadcbe');
  this.sign(g,'CAFÉ · LOUNGE',0,2.7,-3.5,5.3,'#f2d49e','#514737',0,1.3,'cafe','카페 간판');
  for(const x of [-2.9,2.9]){
   const z=.9;this.builtInProp(room,'cafeTable',x,z,'카페 테이블');
   this.builtInProp(room,'chair',x,z-1.45,'의자');this.builtInProp(room,'chair',x,z+1.45,'의자',Math.PI);
  }
  this.bench(room,-5,1.1,Math.PI/2);
  for(const x of [-5.1,5.1])this.builtInProp(room,'plant',x,-2.5,'화분');
 }
 workbench(room){
  const id='built:'+room.id+':workbench',saved=this.o.layout.decorations[id]??={};if(!Number.isInteger(saved.style)||saved.style<0||saved.style>2){saved.style=Math.floor(Math.random()*3);this.createdStyles=true}this.o.layout.decorations[id]=saved;
  const prop={id,roomId:room.id,kind:'workbench',x:saved.x??0,z:saved.z??0,rotation:saved.rotation??0,scale:1,style:saved.style,color:saved.color},g=new THREE.Group(),c=room.color,theme=room.zone,angle=prop.rotation;
  g.position.set(prop.x,0,prop.z);g.rotation.y=angle;room.group.add(g);
  const transform=(x,z)=>({x:prop.x+Math.cos(angle)*x+Math.sin(angle)*z,z:prop.z-Math.sin(angle)*x+Math.cos(angle)*z});
  room.terminals=[];room.workSpots=[];const fixtureObstacleStart=this.nav.obstacles.length;
  if(theme==='concept'){
   this.box(g,0,.13,0,3.5,.26,2.1,prop.color||'#718c91');this.box(g,0,.42,0,3.15,.35,1.75,this.glass('#67bac7',.4));
   for(const x of [-1.73,1.73]){this.box(g,x,.5,0,.1,.65,2.1,this.glass('#b9e4e5',.24));this.box(g,x,.83,0,.12,.08,2.15,c)}
   for(const z of [-1.03,1.03]){this.box(g,0,.5,z,3.5,.65,.1,this.glass('#b9e4e5',.24));this.box(g,0,.83,z,3.6,.08,.12,c)}
   this.obstacle(room,prop.x,prop.z,Math.abs(Math.sin(angle))>.5?2.1:3.5,Math.abs(Math.sin(angle))>.5?3.5:2.1);room.openTop=true;
   for(let i=0;i<8;i++){const bubble=this.shape(g,Math.sin(i)*1.3,.4,Math.cos(i)*.65,.04,.04,.04,'#b1e8e7','sphere');this.animated.push({kind:'bubble',mesh:bubble,phase:i/8})}
  }else{
   this.box(g,0,.28,0,4.4,.55,2.4,prop.color||(theme==='info'?'#9a896f':'#4d605b'));this.box(g,0,.6,0,4.55,.12,2.5,theme==='info'?'#d2bc95':theme==='feature'?'#a99470':'#97ad87');this.obstacle(room,prop.x,prop.z,Math.abs(Math.sin(angle))>.5?2.5:4.55,Math.abs(Math.sin(angle))>.5?4.55:2.5);room.openTop=true;
   if(theme==='module')for(let i=0;i<11;i++)this.box(g,-2+i*.4,.67,0,.012,.015,2.35,'#7b9a7a');
  }
  if(prop.style===1){for(const side of [-1,1]){this.box(g,side*2.08,.26,0,.18,.52,2.55,'#c7ab7c');this.box(g,0,.69,side*1.22,4.6,.1,.12,'#e1c78e')}}
  if(prop.style===2){for(const side of [-1,1]){this.box(g,side*2.13,.58,0,.13,.12,2.5,'#80b4aa');this.box(g,0,.62,side*1.2,4.5,.06,.1,'#b1ddd1')}this.box(g,0,.71,0,3.7,.035,1.65,'#526d6b')}
  const spots=[[-1.1,-2.05,0],[1.1,-2.05,0],[-1.1,2.05,Math.PI],[1.1,2.05,Math.PI],[-2.95,0,Math.PI/2],[2.95,0,-Math.PI/2]];
  spots.forEach(([x,z,rotation],index)=>{
   const spot=theme==='info'?this.chair(room,x,z,rotation,false,.65):{...this.local(room,x,z),rotation,seated:false},location=transform(x,z);if(spot.chair)g.add(spot.chair);Object.assign(spot,this.local(room,location.x,location.z),{rotation:rotation+angle});spot.index=index;spot.roomId=room.id;room.workSpots.push(spot);
   const front={x:Math.sin(rotation),z:Math.cos(rotation)},offset=['feature','module'].includes(theme)?1.2:.63,cx=x+front.x*offset,cz=z+front.z*offset,terminal=new THREE.Group();terminal.position.set(cx,0,cz);terminal.rotation.y=rotation;g.add(terminal);
   if(theme==='concept'){
    this.box(terminal,0,.5,0,.9,.12,.46,'#a0b4b0');this.box(terminal,0,.79,.03,.68,.44,.06,'#263d48');this.box(terminal,0,.79,.07,.57,.32,.02,'#79b5c3');this.box(terminal,0,.58,-.16,.6,.035,.13,'#d0dfd3');
    const terminalLocation=transform(cx,cz),side=Math.abs(Math.sin(rotation+angle))>.5;this.obstacle(room,terminalLocation.x,terminalLocation.z,side?.46:.9,side?.9:.46);
    this.box(terminal,0,.12,.35,.07,.09,.7,c);
   }else if(theme==='feature'){
    this.box(terminal,0,.68,0,.75,.06,.5,'#799e8c');this.box(terminal,.3,.8,-.1,.18,.28,.2,'#46565a');
   }else if(theme==='module'){
    this.box(terminal,0,.68,0,.8,.035,.55,'#4f8074');for(let j=0;j<3;j++)this.box(terminal,-.25+j*.25,.71,0,.012,.01,.5,'#a1c7ad');
   }
   const payload=new THREE.Group();payload.position.set(theme==='concept'?(index%2?1:-1)*.9:cx,theme==='concept'?.53:theme==='info'?.68:.78,theme==='concept'?(index<2?-.48:index<4?.48:0):cz);g.add(payload);
   room.terminals.push({index,group:terminal,payload,owner:null,objectId:null,room});
  });
  for(const obstacle of this.nav.obstacles.slice(fixtureObstacleStart))obstacle.fixtureId=id;
  this.registerDecoration(g,'중앙 작업대',room,prop);
  if(theme==='feature'){
   const beltGroup=room.group,beltX=2.2,beltZ=3.7,beltLength=4.25,half=beltLength/2;this.box(beltGroup,beltX,.39,beltZ,beltLength,.65,.8,'#566164');this.box(beltGroup,beltX,.76,beltZ,beltLength+.08,.1,.7,'#243b3c');this.obstacle(room,beltX,beltZ,beltLength+.1,.8);
   for(const side of [-1,1]){const portal=new THREE.Group();portal.position.set(beltX+side*(half-.08),0,beltZ);beltGroup.add(portal);this.box(portal,side*.17,1.01,0,.12,.55,.57,'#152728');for(const z of [-.4,.4])this.box(portal,0,1.02,z,.48,.72,.12,'#788984');this.box(portal,0,1.44,0,.48,.13,.92,'#849590');this.box(portal,side*.1,.82,0,.42,.08,.75,'#374a4a')}
   for(let i=0;i<5;i++){const group=new THREE.Group();beltGroup.add(group);this.box(group,0,0,0,.3,.25,.28,i%2?'#c8a878':'#96b1b7',{kind:'storage',id:room.id+'#0'});this.animated.push({kind:'belt',mesh:group,x:beltX,z:beltZ,phase:i/5,length:beltLength-.18,roomId:room.id})}
  }
 }
 coordinationPoint(room,index=0){return {...this.local(room,index%2?-3.7:3.7,-1.65),rotation:index%2?Math.PI/2:-Math.PI/2,seated:false}}
 observationPoint(id,room){
  const key='observe:'+room.id,claimed=[...this.workClaims.entries()].filter(([,spot])=>spot.roomId===room.id),working=claimed.filter(([owner])=>{const actor=this.o.actors.find(a=>a.id===owner);return actor?.task?.kind==='work'&&!actor.path.length}),pool=working.length?working:claimed,candidates=[];
  for(const [ownerId,spot] of pool){const owner=this.o.actors.find(a=>a.id===ownerId),sin=Math.sin(spot.rotation),cos=Math.cos(spot.rotation);for(const behind of [1.2,2.1])for(const side of [0,-1,1,-2,2])candidates.push({x:spot.x-sin*behind+cos*side,z:spot.z-cos*behind-sin*side,rotation:spot.rotation,seated:false,roomId:room.id,index:spot.index,ownerId,objectId:owner?.activity.objectId,priority:behind>2?.15:0})}
  if(!candidates.length)for(const z of [2.5,3.5,-2.5])for(const x of [-3,-1,1,3])candidates.push({...this.local(room,x,z),rotation:Math.PI,seated:false,roomId:room.id});
  const claim=this.interactionClaims.get(id+'|'+key);if(claim?.ownerId&&!pool.some(([owner])=>owner===claim.ownerId))this.interactionClaims.delete(id+'|'+key);
  const result=this.interactionPoint(id,key,room,candidates);this.observerClaims??=new Map();this.observerClaims.set(id,result);return result;
 }
 meetingPoint(id,index){const seats=[0,2,8,6],spot=this.restSpots[seats[index%seats.length]];this.restClaims.set(id,spot);return spot}
 workPoint(id,room,preferred){
  if(this.workClaims.has(id))return this.workClaims.get(id);
  const used=new Set([...this.workClaims.values()].filter(p=>p.roomId===room.id).map(p=>p.index)),spot=room.workSpots.find(p=>p.index===preferred&&!used.has(p.index))||room.workSpots.find(p=>!used.has(p.index));
  if(!spot)return null;this.observerClaims?.delete(id);this.interactionClaims.delete(id+'|observe:'+room.id);this.workClaims.set(id,spot);return spot;
 }
 clearPayload(group){group.traverse(mesh=>{const at=this.o.pickables.indexOf(mesh);if(at>=0)this.o.pickables.splice(at,1)});group.clear()}
 releaseWork(id){const spot=this.workClaims.get(id);if(!spot)return;const room=this.o.rooms.get(spot.roomId),terminal=room?.terminals[spot.index];if(terminal){terminal.owner=null;terminal.objectId=null;this.clearPayload(terminal.payload)}this.workClaims.delete(id)}
 showTerminal(id,room,object){const spot=this.workClaims.get(id);if(!spot)return;const terminal=room.terminals[spot.index];if(terminal.owner===id&&terminal.objectId===object?.id)return;terminal.owner=id;terminal.objectId=object?.id;this.clearPayload(terminal.payload);
  if(room.zone==='resource'){
   const color=object?.kind==='image'?'#a1c9bc':object?.kind==='mesh'?'#ae9bc5':'#eee2ca';this.box(terminal.payload,0,object?.kind==='mesh'?.16:0,0,object?.kind==='mesh'?.35:.65,object?.kind==='mesh'?.32:.025,.42,color);
   if(object?.kind==='image')this.box(terminal.payload,0,.02,0,.43,.012,.27,'#628f89');else if(object?.kind!=='mesh')for(let i=0;i<3;i++)this.box(terminal.payload,0,.02,-.12+i*.1,.43,.008,.012,'#879990');
  }
  else if(room.zone==='info'){this.box(terminal.payload,0,0,0,.7,.018,.48,'#eee2ca');for(let i=0;i<4;i++)this.box(terminal.payload,0,.012,-.14+i*.09,.47,.005,.015,'#879990')}
  else if(room.zone==='concept')this.conceptCube(terminal.payload,object,0,.18,0,.42);
  else this.icon(terminal.payload,object,0,0,0,.4);
  if(room.zone==='module'){for(const x of [-.22,.22])this.box(terminal.payload,x,0,0,.06,.14,.4,'#c2cbac')}
  else if(room.zone==='feature')this.box(terminal.payload,0,-.05,0,.3,.1,.25,'#b6c8a6');
  if(object?.id){const pick={kind:'station',id:object.id};terminal.payload.traverse(mesh=>{if(mesh.isMesh||mesh.isSprite){mesh.userData.pick=pick;this.o.pickables.push(mesh)}})}
 }
 restPoint(id,loungeOnly=false){
  if(this.restClaims.has(id))return this.restClaims.get(id);
  const claimed=[...this.restClaims.values()],used=new Set(claimed.map(p=>p.id)),seats=loungeOnly?this.restSpots.filter(p=>p.id.includes('__lobby')):this.restSpots,free=seats.filter(p=>!used.has(p.id)),pool=free.length?free:seats;
  const spot=[...pool].sort((a,b)=>{
   const spacing=p=>claimed.length?Math.min(...claimed.map(other=>Math.hypot(p.x-other.x,p.z-other.z))):0;
   return spacing(b)-spacing(a)||hash(id+':'+a.id)-hash(id+':'+b.id);
  })[0]||{...this.local(this.o.rooms.get('__lobby'),-4,4),rotation:0,seated:false};
  this.restClaims.set(id,spot);return spot
 }
 tick(time,dt,actors){
  this.tickCleaning(time,dt,actors);
  for(const item of this.animated){const t=time*.001;if(item.kind==='water'){const progress=(t*.72+item.phase)%1,radius=.07+progress*.6;item.mesh.position.set(item.x+Math.cos(item.angle)*radius,1.83+.3*progress-.85*progress*progress,item.z+Math.sin(item.angle)*radius);item.mesh.scale.y=.08+progress*.03}else if(item.kind==='bubble')item.mesh.position.y=.3+(t*.16+item.phase)% .4;else if(item.kind==='belt'){const progress=(t*.2+item.phase)%1,edge=Math.min(1,progress/.12,(1-progress)/.12);item.mesh.position.set(item.x+(progress-.5)*item.length,.52+edge*.43,item.z)}}
  for(const station of this.o.stationGroups.values())if(station.drawer){const open=actors.some(a=>a.role==='worker'&&a.roomId===station.room.id&&a.task?.kind==='collect'&&!a.path.length);station.drawer.position.z+=((open?.9:.6)-station.drawer.position.z)*Math.min(1,dt*8)}
  for(const gate of this.gates){const open=actors.some(a=>a.role==='helper'&&a.arriving&&a.gateLane===gate.lane&&['badge','enter'].includes(a.arrivalPhase));gate.open+=(Number(open)-gate.open)*Math.min(1,dt*7);gate.flap.scale.x=1.55*Math.max(.06,1-gate.open);gate.light.material=this.o.mat(open?'#a9e1ab':'#d3b374')}
 }
 pack(group){for(const child of [...group.children])if(child.isGroup)this.pack(child);const groups=new Map();for(const mesh of group.children)if(mesh.isMesh&&mesh.geometry===this.o.boxGeometry&&!mesh.userData.dynamic){let list=groups.get(mesh.material);if(!list)groups.set(mesh.material,list=[]);list.push(mesh)}for(const [material,list] of groups){if(list.length<3)continue;const instanced=new THREE.InstancedMesh(this.o.boxGeometry,material,list.length);instanced.userData.picks=[];list.forEach((mesh,index)=>{mesh.updateMatrix();instanced.setMatrixAt(index,mesh.matrix);instanced.userData.picks[index]=mesh.userData.pick;group.remove(mesh);const at=this.o.pickables.indexOf(mesh);if(at>=0)this.o.pickables.splice(at,1)});group.add(instanced);if(instanced.userData.picks.some(Boolean))this.o.pickables.push(instanced)}}
 dispose(){this.disposed=true;for(const item of [...this.dirt])this.removeDirt(item);for(const cleaner of this.cleaners){cleaner.group.removeFromParent();for(const resource of cleaner.resources)resource.dispose()}this.cleaners=[];for(const asset of this.assets)asset.dispose();for(const geometry of Object.values(this.geometry||{}))geometry.dispose()}
}
