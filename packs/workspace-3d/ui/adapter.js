// Display-only pack: no source, permission, execution or Worker dispatch API.
export function createOfficeView(api){
 let canvas=null,controls=null,engine=null,owner=null,key='',epoch=0,loading=false,zoom=null,editorZoom=null;
 const stylesheet=document.createElement('link');stylesheet.rel='stylesheet';stylesheet.href=new URL('./office.css',import.meta.url);document.head.append(stylesheet);
 const visible=()=>!!owner&&owner.workspacePresentation==='office'&&api.visible();
 const alive=(token,host,record)=>epoch===token&&canvas===host&&owner===record&&host?.isConnected&&api.owner()===record;
 const clean=()=>{epoch++;loading=false;try{engine?.dispose();}finally{engine=null;if(zoom)zoom.onclick=editorZoom;canvas?.classList.remove('is-voxel-office');controls?.remove();controls=null;canvas=null;owner=null;key='';}};
 function update(){
  const host=api.canvas(),record=api.owner(),identity=api.identity();
  if(!host||!record){if(canvas)clean();return;}
  if(host!==canvas||record!==owner||key!==identity){
   clean();canvas=host;owner=record;key=identity;zoom=host.querySelector('[data-workspace-zoom]');editorZoom=zoom?.onclick;
   controls=document.createElement('div');controls.className='workspace-view-controls';controls.innerHTML='<div class="workspace-view-swap" role="group" aria-label="Workspace 보기"><button type="button" data-workspace-view="office" aria-label="아이소메트릭 Workspace" title="아이소메트릭 Workspace"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" aria-hidden="true"><path d="m12 2 9 5-9 5-9-5 9-5Z M3 7v10l9 5 9-5V7 M12 12v10 M7 9.2l9-5 M17 9.2l-9-5"/></svg></button><button type="button" data-workspace-view="editor" aria-label="패널 Workspace" title="패널 Workspace"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="3" width="20" height="18" rx="2"/><path d="M2 8h20 M8 8v13 M11 12h8 M11 16h6"/></svg></button></div>';
   host.append(controls);const token=epoch;controls.onpointerdown=e=>e.stopPropagation();controls.onclick=e=>{const view=e.target.closest('[data-workspace-view]')?.dataset.workspaceView;if(!view||!alive(token,host,record))return;record.workspacePresentation=view;api.persist();update();};
  }
  const active=visible();canvas.classList.toggle('is-voxel-office',active);controls.hidden=!api.visible();
  for(const b of controls.querySelectorAll('[data-workspace-view]'))b.setAttribute('aria-pressed',String(b.dataset.workspaceView===(owner.workspacePresentation==='office'?'office':'editor')));
  if(zoom)zoom.onclick=active?()=>engine?.showZoom(zoom):editorZoom;
  if(engine&&engine.active!==active)engine.setVisible(active);
  if(!active||engine||loading)return;
  loading=true;const token=epoch,host=canvas,record=owner;
  import('./office.js').then(({mount})=>{
   if(!alive(token,host,record)||!visible())return;
   const valid=()=>alive(token,host,record)&&visible();
   const wheel=(current,event)=>Math.max(.3,Math.min(5,current*Math.exp(-Math.max(-120,Math.min(120,event.deltaY))*.002)));wheel.reset=()=>{};
   const read=()=>{if(!valid())return {name:'',objects:[],helpers:[],helperTitles:{},issues:[],skins:{},resources:[]};return api.read();};
   engine=mount(host,{read,owner:()=>record,workspaceId:()=>key,save:()=>{if(valid())api.persist();},zoom:()=>{},steppedZoom:wheel,
    announce:text=>{if(valid())controls.dataset.lastSelection=text;},notify:text=>{if(valid())api.toast(text);},
    openObject:id=>{if(valid()&&read().objects.some(row=>row.id===id))api.openObject(id);},
    openCategory:(group,parent)=>{if(valid()&&['concept','info','feature','module'].includes(group)&&(!parent||read().objects.some(row=>row.id===parent&&row.kind==='Category')))api.openCategory(group,parent);else if(valid()&&group==='resource')api.toast('자료 Browser는 아직 연결되지 않았습니다.');},
    canChat:()=>false,chat:()=>{},canWrite:()=>false,canArrange:()=>false,canInspectTask:()=>false,
    recover:()=>{if(valid())fail(new Error('Workspace3D context lost'),token,host,record);}});
   engine.setVisible(true);host.dataset.officeRenderer='ready';
  }).catch(error=>fail(error,token,host,record)).finally(()=>{if(alive(token,host,record))loading=false;});
 }
 function fail(error,token,host,record){
  if(!alive(token,host,record))return;
  try{engine?.dispose();}catch{}engine=null;
  host.querySelectorAll('.voxel-office,.office-workspace-map-shield').forEach(el=>el.remove());host.dataset.officeRenderer='unavailable';
  record.workspacePresentation='editor';api.persist();update();api.toast('이 환경에서 3D 작업실을 열지 못했습니다. 편집 Workspace로 전환했습니다.');
 }
 return {update,dispose:clean};
}
