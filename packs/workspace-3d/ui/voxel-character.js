import * as THREE from './assets/three.module-0.160.1.js';

const clamp=(n,a,b)=>Math.max(a,Math.min(b,n));
const safeColor=(value,fallback)=>/^#[a-f\d]{6}$/i.test(value||'')?value:fallback;
const hash=value=>[...String(value)].reduce((n,c)=>(n*31+c.charCodeAt(0))>>>0,0);
const palettes={
 lumi:{skin:'#edc7b4',hair:'#e1edf0',eyes:'#70b8ca',cloth:'#edf4f4',accent:'#83d7e5',dark:'#586781'},
 tori:{skin:'#e3b794',hair:'#80553e',eyes:'#a9bb75',cloth:'#cfb781',accent:'#e5bd6b',dark:'#544739'},
 vex:{skin:'#d6aa91',hair:'#2c2c3b',eyes:'#c88d88',cloth:'#4b475d',accent:'#ad8eaf',dark:'#252333'},
 frost:{skin:'#f0d4cd',hair:'#eef5fd',eyes:'#98bde9',cloth:'#f1f5fb',accent:'#8ee1e8',dark:'#8a9ac1'},
 obsidian:{skin:'#e6c2ba',hair:'#242333',eyes:'#b5a1cb',cloth:'#302e43',accent:'#8e7d9d',dark:'#191923'},
 forest:{skin:'#e5bd98',hair:'#5a483c',eyes:'#8aae77',cloth:'#6e8871',accent:'#d7ba79',dark:'#3c4d45'}
};
const presetStyles={lumi:['long','jacket','ribbon'],tori:['short','uniform','glasses'],vex:['short','jacket','none'],frost:['twin','robe','ribbon'],obsidian:['long','robe','horns'],forest:['short','hoodie','ears']};
const colorNames={skin:'피부',hair:'머리카락',eyes:'눈',cloth:'의상',accent:'포인트',dark:'그림자·신발'};
const texBoxes={head:[0,0,8,8,8],body:[16,16,8,12,4],rightArm:[40,16,4,12,4],leftArm:[32,48,4,12,4],rightLeg:[0,16,4,12,4],leftLeg:[16,48,4,12,4],hat:[32,0,8,8,8],jacket:[16,32,8,12,4],rightSleeve:[40,32,4,12,4],leftSleeve:[48,48,4,12,4],rightPants:[0,32,4,12,4],leftPants:[0,48,4,12,4]};
function textureBox(name,model){const box=texBoxes[name];return model==='slim'&&/Arm|Sleeve/.test(name)?[box[0],box[1],3,12,4]:box}
function faces(box){const [u,v,w,h,d]=box;return {right:[u,v+d,d,h],front:[u+d,v+d,w,h],left:[u+d+w,v+d,d,h],back:[u+d+w+d,v+d,w,h],top:[u+d,v,w,d],bottom:[u+d+w,v,w,d]}}
const skinParts=Object.keys(texBoxes),faceOrder=['left','right','top','bottom','front','back'],atlasColumns=8,atlasCell=16,atlasPadding=2,atlasWidth=atlasColumns*atlasCell,atlasHeight=Math.ceil(skinParts.length*6/atlasColumns)*atlasCell;
function atlasFace(part,index){const cell=skinParts.indexOf(part)*6+index;return {x:cell%atlasColumns*atlasCell,y:Math.floor(cell/atlasColumns)*atlasCell}}
function drawSkinAtlas(canvas,image,model){
 // Extrude every face's edge texels into a separate cell. Multisample edge
 // fragments can then sample past the face without picking up scalp/skin.
 // This atlas is only for rendering; imported and exported PNGs stay intact.
 const scale=image.width===128?2:1,source=document.createElement('canvas');source.width=source.height=64*scale;const ctx=source.getContext('2d');ctx.imageSmoothingEnabled=false;ctx.drawImage(image,0,0,source.width,source.height);const pixels=ctx.getImageData(0,0,source.width,source.height).data;
 canvas.width=atlasWidth*scale;canvas.height=atlasHeight*scale;const target=canvas.getContext('2d'),output=target.createImageData(canvas.width,canvas.height),data=output.data,cellSize=atlasCell*scale,padding=atlasPadding*scale;
 for(const part of skinParts){const regions=faces(textureBox(part,model));faceOrder.forEach((side,index)=>{const [sx,sy,w,h]=regions[side],tile=atlasFace(part,index);for(let y=0;y<cellSize;y++)for(let x=0;x<cellSize;x++){const sourceX=sx*scale+clamp(x-padding,0,w*scale-1),sourceY=sy*scale+clamp(y-padding,0,h*scale-1),from=(sourceY*source.width+sourceX)*4,to=((tile.y*scale+y)*canvas.width+tile.x*scale+x)*4;data[to]=pixels[from];data[to+1]=pixels[from+1];data[to+2]=pixels[from+2];data[to+3]=pixels[from+3]}})}
 target.putImageData(output,0,0);
}
function shade(hex,amount){const c=new THREE.Color(hex);c.multiplyScalar(amount);return '#'+c.getHexString(THREE.SRGBColorSpace)}
export function defaultCharacter(helper={}){
 const image=String(helper.image||''),preset=helper.id==='a'||image.includes('tori')?'tori':helper.id==='b'||image.includes('vex')?'vex':'lumi';
 const [hairStyle,outfit,accessory]=presetStyles[preset];
 return {version:1,source:'generated',model:'classic',preset,colors:{...palettes[preset]},hairStyle,outfit,accessory,variant:hash(helper.id||helper.name||'helper')%97,showOuter:true,showDetails:true};
}
function normalize(value,helper){const base=defaultCharacter(helper),next={...base,...value};next.colors=Object.fromEntries(Object.entries(base.colors).map(([key,color])=>[key,safeColor(value?.colors?.[key],color)]));next.model=next.model==='slim'?'slim':'classic';next.variant=Number.isFinite(next.variant)?next.variant:0;next.showOuter=next.showOuter!==false;next.showDetails=next.showDetails!==false;return next}

export function generateSkin(value,helper){
 const config=normalize(value,helper),c=document.createElement('canvas');c.width=c.height=64;const ctx=c.getContext('2d'),p=config.colors,variant=config.variant;
 const rect=(box,x,y,w,h,color)=>{const [u,v]=box;ctx.fillStyle=color;ctx.fillRect(u+x,v+y,w,h)};
 const fill=(name,color)=>{const f=faces(textureBox(name,config.model));for(const [side,box] of Object.entries(f)){rect(box,0,0,box[2],box[3],shade(color,side==='top'?1.05:side==='right'?.83:side==='back'?.91:1));}return f};
 const noise=(box,color,count=8)=>{for(let i=0;i<count;i++){const x=(i*7+variant*3)%box[2],y=(i*3+variant)%box[3];rect(box,x,y,1,1,color)}};
 const head=fill('head',p.skin);for(const side of ['top','back'])rect(head[side],0,0,8,8,p.hair);
 for(const side of ['left','right']){rect(head[side],0,0,8,3,p.hair);rect(head[side],0,0,2,7,p.hair)}
 rect(head.front,0,0,8,2,p.hair);rect(head.front,variant%2?1:5,1,2,2,p.hair);
 for(const x of [1,5]){rect(head.front,x,4,2,2,'#f5f0eb');rect(head.front,x+1,4,1,2,p.eyes);rect(head.front,x+1,4,1,1,shade(p.eyes,.56));rect(head.front,x,3,2,1,shade(p.hair,.85));}
 rect(head.front,3,7,2,1,shade(p.skin,.79));rect(head.front,0,6,1,1,shade(p.skin,.94));rect(head.front,7,6,1,1,shade(p.skin,.94));
 const body=fill('body',p.cloth);for(const side of ['front','back']){noise(body[side],shade(p.cloth,.96),7);rect(body[side],0,10,8,2,p.dark);rect(body[side],3,0,2,1,p.skin)}
 rect(body.front,3,1,2,9,p.accent);rect(body.front,3,10,2,1,p.accent);rect(body.front,0,2,2,1,shade(p.accent,.9));rect(body.front,6,2,2,1,shade(p.accent,.9));
 for(const name of ['rightArm','leftArm']){const arm=fill(name,p.cloth);for(const [side,box] of Object.entries(arm)){if(!['top','bottom'].includes(side)){rect(box,0,9,box[2],1,p.accent);rect(box,0,10,box[2],2,p.skin)}else if(side==='bottom')rect(box,0,0,box[2],box[3],p.skin)}}
 for(const name of ['rightLeg','leftLeg']){const leg=fill(name,p.dark);for(const [side,box] of Object.entries(leg)){if(!['top','bottom'].includes(side)){rect(box,0,0,4,8,shade(p.cloth,.72));rect(box,0,8,4,1,p.accent);rect(box,0,11,4,1,shade(p.dark,.8));if(side==='front')rect(box,name==='rightLeg'?3:0,1,1,7,shade(p.accent,.78))}}}
 // Transparent overlays use the standard 64 × 64 second-layer UV areas.
 const hat=faces(texBoxes.hat);for(const side of ['top','back','left','right']){const box=hat[side];rect(box,0,0,box[2],box[3],p.hair);noise(box,shade(p.hair,1.09),10)}
 rect(hat.front,0,0,8,2,p.hair);rect(hat.front,0,2,1,4,p.hair);rect(hat.front,7,2,1,4,p.hair);for(let x=1;x<7;x++)if((x+variant)%3!==0)rect(hat.front,x,2,1,1+(x+variant)%2,p.hair);
 const jacket=faces(texBoxes.jacket);for(const side of ['back','left','right']){const b=jacket[side];rect(b,0,0,b[2],b[3],shade(p.cloth,1.025));noise(b,shade(p.cloth,.94))}
 for(const x of [0,5]){rect(jacket.front,x,1,3,10,p.cloth);rect(jacket.front,x===0?2:5,2,1,8,p.accent)}
 rect(jacket.front,0,1,2,2,p.accent);rect(jacket.front,6,1,2,2,p.accent);if(config.outfit==='uniform'){for(const y of [4,7,9])rect(jacket.front,4,y,1,1,p.accent)}
 if(config.outfit==='hoodie'){rect(jacket.front,1,0,6,2,p.accent);rect(jacket.front,2,7,4,3,shade(p.cloth,.86));rect(hat.front,0,0,8,1,p.accent)}
 for(const name of ['rightSleeve','leftSleeve']){const sleeve=faces(textureBox(name,config.model));for(const [side,b] of Object.entries(sleeve)){if(side==='bottom')continue;rect(b,0,0,b[2],side==='top'?b[3]:10,p.cloth);if(side!=='top'){rect(b,0,8,b[2],2,p.accent);rect(b,0,1,1,6,shade(p.cloth,1.08))}}}
 for(const name of ['rightPants','leftPants']){const pants=faces(texBoxes[name]);for(const side of ['front','back','left','right']){const b=pants[side];rect(b,0,9,4,2,p.dark);rect(b,0,8,4,1,p.accent)}}
 return {...config,source:'generated',skin:c.toDataURL('image/png'),width:64,height:64};
}

function skinGeometry(part,model,w,h,d,segment){
 const geometry=new THREE.BoxGeometry(w,h,d),uv=geometry.attributes.uv,regions=faces(textureBox(part,model));
 faceOrder.forEach((side,index)=>{const tile=atlasFace(part,index),[, ,rw,faceHeight]=regions[side],vertical=segment&& !['top','bottom'].includes(side),rh=vertical?segment.length:faceHeight,x=tile.x+atlasPadding,y=tile.y+atlasPadding+(vertical?segment.start:0),u0=x/atlasWidth,u1=(x+rw)/atlasWidth,v0=1-y/atlasHeight,v1=1-(y+rh)/atlasHeight;uv.setXY(index*4,u0,v0);uv.setXY(index*4+1,u1,v0);uv.setXY(index*4+2,u0,v1);uv.setXY(index*4+3,u1,v1)});uv.needsUpdate=true;return geometry;
}

export function createCharacter(helper={},saved){
 const config=normalize(saved||helper.voxelCharacter,helper),data=/^data:image\/png;base64,[A-Za-z\d+/=]+$/.test(config.skin||'')?config:generateSkin(config,helper);
 const pixelScale=data.width===128?2:1,canvas=document.createElement('canvas');canvas.width=atlasWidth*pixelScale;canvas.height=atlasHeight*pixelScale;const ctx=canvas.getContext('2d');ctx.fillStyle=data.colors.cloth;ctx.fillRect(0,0,canvas.width,canvas.height);
 const texture=new THREE.CanvasTexture(canvas);texture.magFilter=texture.minFilter=THREE.NearestFilter;texture.generateMipmaps=false;texture.colorSpace=THREE.SRGBColorSpace;
 const image=new Image();let disposed=false;image.onload=()=>{if(disposed)return;const width=canvas.width,height=canvas.height;drawSkinAtlas(canvas,image,data.model);if(canvas.width!==width||canvas.height!==height)texture.dispose();texture.needsUpdate=true};image.src=data.skin;
 const baseMaterial=new THREE.MeshLambertMaterial({map:texture,alphaTest:.5}),outerMaterial=new THREE.MeshLambertMaterial({map:texture,alphaTest:.5,side:THREE.DoubleSide}),materials=[baseMaterial,outerMaterial],geometries=[],group=new THREE.Group(),body=new THREE.Group(),limbs=[],elbows=[],knees=[],outer=[],details=[];group.add(body);
 const unit=.07,arm=data.model==='slim'?3:4;
 const add=(parent,name,x,y,z,w,h,d,overlay=false,segment=null)=>{const geometry=skinGeometry(name,data.model,w*unit,h*unit,d*unit,segment);geometries.push(geometry);const mesh=new THREE.Mesh(geometry,overlay?outerMaterial:baseMaterial);mesh.position.set(x*unit,y*unit,z*unit);parent.add(mesh);if(overlay)outer.push(mesh);return mesh};
 const hairSize=9.6,head=new THREE.Group(); // Pivot at the neck so looking around does not turn the torso.
 head.position.y=24*unit;body.add(head);
 add(head,'head',0,4,0,8,8,8);add(head,'hat',0,4,0,hairSize,hairSize,hairSize,true);add(body,'body',0,18,0,8,12,4);add(body,'jacket',0,18,0,8.6,12.6,4.6,true);
 for(const [side,x] of [['right',-(4+arm/2)],['left',4+arm/2]]){const limb=new THREE.Group(),elbow=new THREE.Group();limb.position.set(x*unit,24*unit,0);elbow.position.y=-6*unit;body.add(limb);limb.add(elbow);add(limb,side+'Arm',0,-3,0,arm,6,4,false,{start:0,length:6});add(elbow,side+'Arm',0,-3,0,arm,6,4,false,{start:6,length:6});add(limb,side+'Sleeve',0,-3,0,arm+.5,6.12,4.5,true,{start:0,length:6});add(elbow,side+'Sleeve',0,-3,0,arm+.5,6.12,4.5,true,{start:6,length:6});limbs.push(limb);elbows.push(elbow)}
 for(const [side,x] of [['right',-2],['left',2]]){const limb=new THREE.Group(),knee=new THREE.Group();limb.position.set(x*unit,12*unit,0);knee.position.y=-6*unit;body.add(limb);limb.add(knee);add(limb,side+'Leg',0,-3,0,4,6,4,false,{start:0,length:6});add(knee,side+'Leg',0,-3,0,4,6,4,false,{start:6,length:6});add(limb,side+'Pants',0,-3,0,4.5,6.12,4.5,true,{start:0,length:6});add(knee,side+'Pants',0,-3,0,4.5,6.12,4.5,true,{start:6,length:6});limbs.push(limb);knees.push(knee)}
 const detailMaterials=new Map(),pixelGeometry=new THREE.BoxGeometry(1,1,1);geometries.push(pixelGeometry);
 const pixel=(parent,x,y,z,w,h,d,color)=>{if(!detailMaterials.has(color)){const material=new THREE.MeshLambertMaterial({color});detailMaterials.set(color,material);materials.push(material)}const mesh=new THREE.Mesh(pixelGeometry,detailMaterials.get(color));mesh.position.set(x*unit,y*unit,z*unit);mesh.scale.set(w*unit,h*unit,d*unit);parent.add(mesh);details.push(mesh);return mesh};
 const p=data.colors;
 if(data.source==='generated'){
  if(['long','twin'].includes(data.hairStyle)){for(const s of [-1,1]){pixel(body,s*4,21.5,-2.7,2,10,2,p.hair);pixel(body,s*4,16.5,-2.7,1.7,2,1.8,shade(p.hair,.9));if(data.hairStyle==='twin'){pixel(head,s*5.2,1,-2.5,2,3,2,p.accent);pixel(body,s*5.5,20,-2.5,2.5,8,2.5,p.hair)}}pixel(head,0,-2,-4,6,8,1,p.hair)}
  if(data.outfit==='robe'){for(let i=0;i<2;i++){const limb=limbs[2+i],knee=knees[i],sign=i===0?-1:1;pixel(limb,sign*.3,-3,-.1,4.8,6,5,p.cloth);pixel(knee,sign*.3,-3,-.1,4.9,1,5.1,p.accent);pixel(limb,sign*2.2,-3,.1,.6,5,5.2,shade(p.cloth,.9))}}
  if(data.accessory==='ears')for(const s of [-1,1]){pixel(head,s*3.3,9.5,0,2.5,3,2,p.hair);pixel(head,s*3.3,11.3,0,1.5,1,1.5,p.hair);pixel(head,s*3.3,9.5,1.05,1.3,1.8,.2,p.accent)}
  if(data.accessory==='horns')for(const s of [-1,1]){pixel(head,s*4,8.5,-1,2,2,2,p.accent);pixel(head,s*4.8,10,-1,1.4,2,1.4,shade(p.accent,1.1));pixel(head,s*4.2,11.3,-1,1,1,1,p.accent)}
  if(data.accessory==='ribbon')for(const s of [-1,1]){pixel(head,s*4.3,6.5,.5,1.8,2.3,2,p.accent);pixel(head,s*4.3,4.6,1,1,1.5,1,p.accent);pixel(head,s*3.2,8.5,-1,1.5,1,2.2,shade(p.accent,1.15))}
  if(data.accessory==='glasses'){const z=hairSize/2+.35;for(const s of [-1,1]){for(const y of [3,5])pixel(head,s*2,y,z,3,.4,.4,p.dark);for(const x of [s*2-1.4,s*2+1.4])pixel(head,x,4,z,.4,2,.4,p.dark)}pixel(head,0,4,z,1.2,.4,.4,p.dark)}
 }
 outer.forEach(mesh=>mesh.visible=data.showOuter);details.forEach(mesh=>mesh.visible=data.showDetails);
 return {group,body,head,limbs,elbows,knees,outer,details,color:p.accent,config:data,dispose(){if(disposed)return;disposed=true;image.onload=null;for(const g of geometries)g.dispose();for(const m of materials)m.dispose();texture.dispose()}};
}

export class CharacterPreview{
 constructor(host,helper){
  this.host=host;this.helper=helper;this.disposed=false;this.visible=true;this.pose='idle';this.yaw=-.18;this.pitch=.2;this.zoom=1;this.frame=0;this.events=new AbortController();this.scene=new THREE.Scene();this.scene.background=new THREE.Color('#202327');this.camera=new THREE.OrthographicCamera(-1.4,1.4,1.6,-1.6,.1,30);
  this.canvas=document.createElement('canvas');this.canvas.tabIndex=0;this.canvas.setAttribute('aria-label','복셀 캐릭터 3D 미리보기. 드래그 또는 좌우 화살표로 회전합니다.');host.append(this.canvas);
  this.renderer=new THREE.WebGLRenderer({canvas:this.canvas,antialias:true,powerPreference:'low-power'});this.renderer.setPixelRatio(Math.min(devicePixelRatio||1,1.5));this.renderer.outputColorSpace=THREE.SRGBColorSpace;this.scene.add(new THREE.HemisphereLight('#fff5ea','#697181',2.2));const light=new THREE.DirectionalLight('#fff2d6',2.3);light.position.set(-3,6,5);this.scene.add(light);
  this.floorGeometry=new THREE.CylinderGeometry(.88,.88,.08,48);this.floorMaterial=new THREE.MeshLambertMaterial({color:'#394044'});const floor=new THREE.Mesh(this.floorGeometry,this.floorMaterial);floor.position.y=-.09;this.scene.add(floor);
  const signal=this.events.signal;let drag=null;this.canvas.addEventListener('pointerdown',event=>{if(event.button!==0)return;event.preventDefault();this.canvas.focus({preventScroll:true});this.canvas.setPointerCapture(event.pointerId);drag={id:event.pointerId,x:event.clientX,y:event.clientY,yaw:this.yaw,pitch:this.pitch}},{signal});this.canvas.addEventListener('pointermove',event=>{if(!drag||event.pointerId!==drag.id)return;this.yaw=drag.yaw+(event.clientX-drag.x)*.012;this.pitch=clamp(drag.pitch+(event.clientY-drag.y)*.005,-.15,.75)},{signal});for(const type of ['pointerup','pointercancel','lostpointercapture'])this.canvas.addEventListener(type,event=>{if(drag?.id===event.pointerId)drag=null},{signal});this.canvas.addEventListener('wheel',event=>{event.preventDefault();this.zoom=clamp(this.zoom*Math.exp(-event.deltaY*.001),.6,1.6);this.resize()},{passive:false,signal});this.canvas.addEventListener('keydown',event=>{if(['ArrowLeft','ArrowRight'].includes(event.key)){event.preventDefault();this.yaw+=(event.key==='ArrowLeft'?-1:1)*Math.PI/8}},{signal});
  this.observer=new ResizeObserver(()=>this.resize());this.observer.observe(host);this.intersection=new IntersectionObserver(entries=>{this.visible=entries[0].isIntersecting;if(this.visible)this.start();else this.stop()});this.intersection.observe(host);document.addEventListener('visibilitychange',()=>{if(document.hidden)this.stop();else this.start()},{signal});this.resize();this.start();
 }
 set(config){const old=this.actor;this.actor=createCharacter(this.helper,config);if(old){this.scene.remove(old.group);old.dispose()}this.scene.add(this.actor.group);this.render(performance.now())}
 resize(){const w=this.host.clientWidth,h=this.host.clientHeight;if(!w||!h)return;this.renderer.setSize(w,h,false);this.camera.left=-1.65*w/h;this.camera.right=1.65*w/h;this.camera.top=1.65;this.camera.bottom=-1.65;this.camera.zoom=this.zoom;this.camera.updateProjectionMatrix()}
 render(time){if(!this.actor)return;const a=this.actor;a.group.rotation.y=this.yaw;const stride=this.pose==='walk'?Math.sin(time*.007):0;a.limbs[0].rotation.x=stride*.24;a.limbs[1].rotation.x=-stride*.24;a.limbs[2].rotation.x=-stride*.6;a.limbs[3].rotation.x=stride*.6;a.elbows[0].rotation.x=-.13;a.elbows[1].rotation.x=-.13;a.knees[0].rotation.x=a.knees[1].rotation.x=0;if(this.pose==='work'){const motion=Math.sin(time*.013);a.limbs[0].rotation.x=-.22+motion*.05;a.limbs[1].rotation.x=-.45-motion*.08;a.elbows[1].rotation.x=-.55-motion*.12}a.body.position.y=this.pose==='walk'?Math.abs(Math.sin(time*.007))*.025:Math.sin(time*.002)*.008;this.camera.position.set(1.2,2.05+this.pitch*3,6);this.camera.lookAt(0,1.2,0);this.renderer.render(this.scene,this.camera)}
 start(){if(this.frame||this.disposed||!this.visible||document.hidden)return;let last=0;const tick=t=>{this.frame=0;if(this.disposed||!this.visible||document.hidden)return;if(t-last>1000/30){this.render(t);last=t}this.frame=requestAnimationFrame(tick)};this.frame=requestAnimationFrame(tick)}
 stop(){cancelAnimationFrame(this.frame);this.frame=0}
 dispose(){if(this.disposed)return;this.disposed=true;this.stop();this.events.abort();this.observer?.disconnect();this.intersection?.disconnect();this.actor?.dispose();this.floorGeometry.dispose();this.floorMaterial.dispose();this.renderer.dispose();this.renderer.forceContextLoss();this.canvas.remove()}
}

async function importSkin(file){
 if(file.size>2*1024*1024)throw new Error('PNG 파일은 2MB 이하로 넣어 주십시오.');
 const bytes=new Uint8Array(await file.slice(0,8).arrayBuffer());if([137,80,78,71,13,10,26,10].some((n,i)=>bytes[i]!==n))throw new Error('마크 스킨 형식의 PNG 파일을 선택해 주십시오.');
 const bitmap=await createImageBitmap(file);try{if(![64,128].includes(bitmap.width)||bitmap.width!==bitmap.height)throw new Error('64×64 또는 128×128 PNG 스킨을 선택해 주십시오.');const canvas=document.createElement('canvas');canvas.width=canvas.height=bitmap.width;const ctx=canvas.getContext('2d');ctx.drawImage(bitmap,0,0);return {skin:canvas.toDataURL('image/png'),width:bitmap.width,height:bitmap.height}}finally{bitmap.close()}
}

export function mountCharacterEditor(host,{helper={},portrait=()=>helper.image}={}){
 let draft=helper.voxelCharacter?normalize(structuredClone(helper.voxelCharacter),helper):null,design=normalize(draft,helper),preview=null,disposed=false,importing=false;
 const htmlOptions=(items,current)=>items.map(([key,name])=>'<option value="'+key+'"'+(key===current?' selected':'')+'>'+name+'</option>').join('');
 host.classList.add('helper-voxel-section');host.innerHTML=`<header><div><h3>복셀 캐릭터</h3><p>픽셀 스킨에 머리카락과 의상을 겹쳐 나만의 도우미를 만듭니다.</p></div><span class="voxel-skin-badge">기본 + 외피</span></header><div class="voxel-editor-grid"><div class="voxel-preview-panel"><div class="voxel-character-preview"></div><div class="voxel-preview-actions"><button type="button" data-voxel-turn="0" aria-label="캐릭터 앞모습">앞</button><button type="button" data-voxel-turn="3.141592653589793" aria-label="캐릭터 뒷모습">뒤</button><label><span class="sr-only">미리보기 동작</span><select data-voxel-pose aria-label="미리보기 동작"><option value="idle">대기</option><option value="walk">걷기</option><option value="work">작업</option></select></label></div><small>드래그로 회전 · 휠로 확대</small></div><div class="voxel-design"><div class="voxel-fields"><label>스타일<select data-voxel-field="preset">${htmlOptions([['lumi','도우미 · 루미'],['tori','도우미 · 토리'],['vex','도우미 · 벡스'],['frost','서리빛'],['obsidian','흑요석'],['forest','숲의 모험가']],design.preset)}</select></label><label>체형<select data-voxel-model>${htmlOptions([['classic','기본 · 4픽셀 팔'],['slim','슬림 · 3픽셀 팔']],design.model)}</select></label><label>머리<select data-voxel-field="hairStyle">${htmlOptions([['short','짧은 머리'],['long','긴 머리'],['twin','트윈테일']],design.hairStyle)}</select></label><label>의상<select data-voxel-field="outfit">${htmlOptions([['jacket','재킷'],['robe','롱 코트'],['uniform','유니폼'],['hoodie','후디']],design.outfit)}</select></label><label>입체 장식<select data-voxel-field="accessory">${htmlOptions([['none','없음'],['ribbon','리본'],['ears','동물 귀'],['horns','뿔'],['glasses','안경']],design.accessory)}</select></label></div><div class="voxel-colors">${Object.entries(colorNames).map(([key,label])=>'<label><input type="color" data-voxel-color="'+key+'" aria-label="복셀 '+label+' 색상" value="'+design.colors[key]+'"><span>'+label+'</span></label>').join('')}</div><div class="voxel-layer-options"><label><input type="checkbox" data-voxel-outer ${design.showOuter?'checked':''}> 외피 레이어</label><label><input type="checkbox" data-voxel-details ${design.showDetails?'checked':''}> 입체 장식</label></div><div class="voxel-generate-actions"><button type="button" class="primary" data-voxel-generate>${draft?'다시 생성':'캐릭터 생성'}</button><button type="button" data-voxel-portrait>도우미 색상 가져오기</button></div><div class="voxel-file-actions"><button type="button" data-voxel-import>PNG 가져오기</button><button type="button" data-voxel-export>스킨 PNG 내보내기</button><input type="file" data-voxel-file accept="image/png,.png" hidden></div><p class="voxel-status" data-voxel-status role="status"></p><p class="voxel-error" data-voxel-error role="alert" hidden></p></div></div><footer>확정하면 작업실 캐릭터에도 적용됩니다. PNG는 64×64·128×128을 지원하며, 입체 장식은 도우미 설정에 함께 저장됩니다.</footer>`;
 const area=host.querySelector('.voxel-character-preview'),error=host.querySelector('[data-voxel-error]'),status=host.querySelector('[data-voxel-status]');
 const fail=message=>{error.textContent=message;error.hidden=false};
 try{preview=new CharacterPreview(area,helper)}catch{area.replaceChildren();area.classList.add('voxel-preview-fallback');area.innerHTML='<img alt="복셀 캐릭터 스킨 펼침도"><small>이 환경에서는 스킨 펼침도로 미리 볼 수 있습니다.</small>'}
 const value=()=>draft||generateSkin(design,helper);
 const paint=()=>{if(disposed)return;const config=value();if(preview)preview.set(config);else area.querySelector('img').src=config.skin;status.textContent=draft?(draft.source==='png'?'가져온 스킨':'맞춤 캐릭터')+' · '+(config.width||64)+'×'+(config.height||64)+' · '+(config.model==='slim'?'슬림':'기본'):'기본 캐릭터 · 생성해서 꾸밀 수 있습니다';host.querySelector('[data-voxel-generate]').textContent=draft?'다시 생성':'캐릭터 생성';error.hidden=true};
 const fields=()=>{for(const select of host.querySelectorAll('[data-voxel-field]'))select.value=design[select.dataset.voxelField];for(const input of host.querySelectorAll('[data-voxel-color]'))input.value=design.colors[input.dataset.voxelColor];host.querySelector('[data-voxel-model]').value=design.model};
 const generate=(variation=false)=>{if(importing)return;if(variation)design.variant++;draft=generateSkin(design,helper);paint()};
 host.querySelectorAll('[data-voxel-field]').forEach(select=>select.onchange=()=>{design[select.dataset.voxelField]=select.value;if(select.dataset.voxelField==='preset'){design.colors={...palettes[select.value]};[design.hairStyle,design.outfit,design.accessory]=presetStyles[select.value];fields()}generate()});
 host.querySelector('[data-voxel-model]').onchange=event=>{design.model=event.target.value;if(draft?.source==='png'){draft.model=design.model;paint()}else generate()};host.querySelectorAll('[data-voxel-color]').forEach(input=>input.oninput=()=>{design.colors[input.dataset.voxelColor]=input.value;generate()});
 for(const [key,field] of [['outer','showOuter'],['details','showDetails']])host.querySelector('[data-voxel-'+key+']').onchange=event=>{design[field]=event.target.checked;draft={...value(),[field]:event.target.checked};paint()};
 host.querySelector('[data-voxel-generate]').onclick=()=>generate(true);
 host.querySelector('[data-voxel-portrait]').onclick=async event=>{const button=event.currentTarget;button.disabled=true;try{const url=portrait();const known=Object.keys(palettes).find(key=>['lumi','tori','vex'].includes(key)&&String(url).includes(key));if(known){design.colors={...palettes[known]};design.preset=known;[design.hairStyle,design.outfit,design.accessory]=presetStyles[known]}else{const img=new Image();img.src=url||helper.image||'assets/lumi.png';await img.decode();if(disposed)return;const c=document.createElement('canvas');c.width=c.height=24;const ctx=c.getContext('2d');ctx.drawImage(img,0,0,24,24);const data=ctx.getImageData(0,0,24,24).data;const average=(x,y,w,h)=>{let r=0,g=0,b=0,n=0;for(let j=y;j<y+h;j++)for(let i=x;i<x+w;i++){const k=(j*24+i)*4;if(data[k+3]<128)continue;const light=(data[k]+data[k+1]+data[k+2])/3;if(light<18||light>246)continue;r+=data[k];g+=data[k+1];b+=data[k+2];n++}return n?'#'+[r,g,b].map(v=>Math.round(v/n).toString(16).padStart(2,'0')).join(''):null};design.colors.hair=average(5,1,14,7)||design.colors.hair;design.colors.cloth=average(3,16,18,8)||design.colors.cloth;design.colors.accent=shade(design.colors.cloth,1.2)}if(disposed)return;fields();generate()}catch{if(!disposed)fail('도우미 이미지의 색상을 읽을 수 없습니다. 아래 색상으로 직접 꾸밀 수 있습니다.')}finally{button.disabled=false}};
 host.querySelectorAll('[data-voxel-turn]').forEach(button=>button.onclick=()=>{if(preview){preview.yaw=Number(button.dataset.voxelTurn);preview.pitch=.2}});host.querySelector('[data-voxel-pose]').onchange=e=>{if(preview)preview.pose=e.target.value};
 const fileInput=host.querySelector('[data-voxel-file]');host.querySelector('[data-voxel-import]').onclick=()=>fileInput.click();fileInput.onchange=async()=>{const file=fileInput.files[0];if(!file||importing)return;importing=true;host.querySelector('[data-voxel-generate]').disabled=true;try{const skin=await importSkin(file);if(disposed)return;draft={...design,...skin,source:'png',hairStyle:'short',accessory:'none',outfit:'jacket'};paint()}catch(e){if(!disposed)fail(e.message||'스킨을 읽을 수 없습니다.')}finally{importing=false;fileInput.value='';host.querySelector('[data-voxel-generate]').disabled=false}};
 host.querySelector('[data-voxel-export]').onclick=()=>{const config=value(),a=document.createElement('a');a.href=config.skin;a.download=(helper.name||'helper').replace(/[\\/:*?"<>|]/g,'_')+'-skin.png';document.body.append(a);a.click();a.remove()};
 paint();const observer=new MutationObserver(()=>{if(!host.isConnected)dispose()});observer.observe(document.body,{childList:true,subtree:true});
 function dispose(){if(disposed)return;disposed=true;preview?.dispose();observer.disconnect()}
 return {getValue:()=>draft?structuredClone(draft):null,isBusy:()=>importing,dispose,get preview(){return preview}};
}

window.ConfectoryVoxel={defaultCharacter,generateSkin,createCharacter,mountCharacterEditor};
