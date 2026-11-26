// v536 data-only property cards over explicit existing node-time reads.
export function createPropertyAuthoring({api,esc,field,entries,get,inputs,prefix,store}){
 const supported=w=>!!w.authorData.id&&!w.authorData.requiresCoupledCopy&&!w.authorData.slotContext&&!w.authorData.privateCopy&&!w.authorData.privatePath&&!w.meta.copyDraft&&['sync-acyclic-property-v1','sync-acyclic-methods-v1','sync-acyclic-switch-v1','sync-acyclic-property-set-v1','sync-acyclic-property-ref-v1','async-acyclic-switch-v1'].includes(w.authorData.profile)&&!w.authorData.nodes.some(n=>n.implementationContext||n.forwardCallerStorage);
 const record=(w,id)=>entries(w).find(([,v])=>v.node===id&&v.type==='property-plan')?.[1];
 function ensure(w,id){if(record(w,id))return;const row=w.authorData.nodes?.find(n=>n.id===id&&['property','property-set'].includes(n.kind));if(!row)return;if(!supported(w))throw Error('이 구현의 속성 편집은 아직 지원하지 않아요. 입력은 유지됩니다.');store(w,id,'property-plan',JSON.stringify({existing:true,id}));}
 function stageRead(w,ready){if(ready.id!==w.authorData.id||ready.node.kind!=='property'||ready.readTiming!=='execution-node')throw Error('현재 속성 읽기 계약을 확인해 주세요.');const node=ready.node,row={...node,signature:node.signature,arguments:Object.entries(node.arguments).map(([name,value])=>({name,type:'object',valueJson:JSON.stringify(value)})),property:ready.descriptor.fields.find(f=>f.name===node.field),privateNew:true};store(w,node.id,'property-plan',JSON.stringify({id:node.id,row,descriptor:ready.descriptor,attached:false}));}
 function create(w,ready){if(!supported(w))throw Error('현재 속성 읽기 계약을 확인해 주세요.');stageRead(w,ready);}
 function createAttached(w,ready,consumer,links,write){stageRead(w,ready);attach(w,ready.node,consumer,links,write);}
 function overlay(w,rows){for(const [,v] of entries(w))if(v.type==='property-plan'){const p=JSON.parse(v.text);if(!p.existing&&!rows.some(r=>r.id===v.node))rows.push({...p.row});}}
 function fields(w,row,side){if(side==='inputs')return [field({id:'target',name:'대상 객체',type:'object'},0)];return [field({id:'return',name:row.field,type:row.signature.return},0)];}
 function markup(w,row,index){const x=w.meta.blueprintPositions?.[row.id]?.x??172+index*430,y=w.meta.blueprintPositions?.[row.id]?.y??0,id=esc(row.id),type=fields(w,row,'outputs')[0],label=type.type+(type.multi?' 여러 개':'');return '<article class="bp-node bp-kind-property" data-bp-node="'+id+'" style="left:'+x+'px;top:'+y+'px"><header class="bp-node-header"><strong>속성 · '+esc(row.field)+'</strong><button type="button" data-bp-remove aria-label="속성 노드 삭제" '+(!row.privateNew?'disabled title="연결한 읽기는 현재 실행 계약을 유지합니다."':'')+'>×</button></header><div class="bp-node-body"><p>대상 객체를 연결해 주세요.</p><div class="bp-property-target"><span>대상 '+esc(row.propertyOwner?.split('::').at(-1)||'객체')+'</span><button type="button" class="bp-port bp-port-in bp-data-port" data-node="'+id+'" data-side="in" data-kind="data" data-port="field:target" aria-label="대상 객체 입력 핀" style="--pin-color:#8bbdf3"><span></span></button></div><div class="bp-property-value">'+esc(label)+'<button type="button" class="bp-port bp-data-port bp-port-out" data-node="'+id+'" data-side="out" data-kind="data" data-port="field:return" style="--pin-color:'+({정수:'#73dca4',실수:'#61cdd3',조건:'#e86f83',글자:'#d9a2de',객체:'#8bbdf3'}[type.type]||'#c8ae7f')+'" aria-label="'+esc(row.field)+' 출력 핀"><span></span></button></div></div></article>';}
 function attach(w,row,consumer,raw,write){const cell=record(w,row.id);if(!cell)return write();const p=JSON.parse(cell.text);if(p.existing||p.attached)return write();if(!consumer||consumer.kind==='property'||consumer.branchOwner)throw Error('같은 기본 실행 줄에서 이 값을 사용할 작업을 선택해 주세요. 입력은 유지됩니다.');const incoming=raw.filter(l=>l.to===consumer.id);if(incoming.length!==1||incoming[0].port!=='next')throw Error('이 값을 사용할 작업의 실행 줄을 먼저 하나로 연결해 주세요. 입력은 유지됩니다.');const edge=incoming[0];p.attached=true;store(w,row.id,'property-plan',JSON.stringify(p));store(w,edge.from,edge.from==='$entry'?'entry':edge.port==='next'?'route':'route:'+edge.port,row.id);store(w,row.id,'route',consumer.id);write();}
 function projectLinks(rows,raw){const reads=new Set(rows.filter(r=>r.kind==='property').map(r=>r.id));return raw.filter(l=>!reads.has(l.from)).flatMap(l=>{let to=l.to,chain=[],seen=new Set();while(reads.has(to)&&!seen.has(to)){seen.add(to);chain.push(to);to=raw.find(v=>v.from===to&&v.port==='next')?.to;}return to?[{...l,to,readChain:chain}]:[];});}
 return {supported,ensure,create,createAttached,overlay,fields,markup,attach,projectLinks};
}

export function selectPropertyRead({api,esc,request,current,receivers,type,consumers=null,stage}){
 api.modal('속성 읽기 연결',
  '<label>대상 입력 <select data-property-receiver><option value="">선택</option>'+
  receivers.map(name=>'<option value="'+esc(name)+'">'+esc(name)+'</option>').join('')+'</select></label>'+
  '<label>객체 정의 <select data-property-owner disabled><option value="">선택</option></select></label>'+
  '<label>속성 <select data-property-field disabled><option value="">선택</option></select></label>'+
  (consumers?'<label>값을 받을 입력 <select data-property-consumer disabled><option value="">선택</option></select></label>':'')+
  '<p role="status" data-property-status></p><div class="actions"><button type="button" data-property-cancel>취소</button>'+
  '<button type="button" data-property-connect disabled>연결</button></div>',(dialog,close)=>{
   const target=dialog.querySelector('[data-property-receiver]'),owner=dialog.querySelector('[data-property-owner]');
   const field=dialog.querySelector('[data-property-field]'),status=dialog.querySelector('[data-property-status]');
   const apply=dialog.querySelector('[data-property-connect]'),consumer=dialog.querySelector('[data-property-consumer]');
   const supportedTypes=new Set(consumers?consumers.map(row=>row.type):[type]),fieldTypes=new Map();
   const alive=()=>dialog.isConnected&&current();
   const update=()=>{apply.disabled=owner.disabled||field.disabled||!target.value||!owner.value||!field.value||
    !!(consumer&&(consumer.disabled||!consumer.value));};
   function updateConsumers(){
    if(!consumer)return;
    consumer.length=1;
    for(const row of consumers)if(row.type===fieldTypes.get(field.value))
     consumer.add(new Option(row.label,row.name));
    consumer.disabled=consumer.length===1;
   }
   const remote=(operation,fields={})=>request({action:operation,...fields},alive);
   dialog.querySelector('[data-property-cancel]').onclick=close;
   target.onchange=update;
   field.onchange=()=>{updateConsumers();update();};
   if(consumer)consumer.onchange=update;
   owner.onchange=()=>api.work(async()=>{
    const selected=owner.value;
    field.length=1;fieldTypes.clear();field.disabled=true;updateConsumers();update();status.textContent='';
    if(!selected||!alive())return;
    owner.disabled=true;
    try{
     const details=await remote('propertyCatalog',{owner:selected});
     if(!alive()||owner.value!==selected)return;
     for(const property of details.descriptor.fields.filter(property=>property.supported&&supportedTypes.has(property.clrType))){
      fieldTypes.set(property.name,property.clrType);
      field.add(new Option(property.name,property.name));
     }
     field.disabled=field.length===1;
     if(field.disabled)status.textContent=consumers?'다음 셀의 입력과 자료형이 같은 속성이 없습니다.':'이 입력과 자료형이 같은 속성이 없습니다.';
    }finally{if(alive()){owner.disabled=false;update();}}
   },'');
   apply.onclick=()=>api.work(async()=>{
    if(!alive()||apply.disabled)return;
    const receiver=target.value,definition=owner.value,name=field.value;
    const input=consumer?.value,expectedType=consumer?consumers.find(row=>row.name===input)?.type:type;
    if(!receivers.includes(receiver)||expectedType!==fieldTypes.get(name))return;
    const controls=[target,owner,field,...(consumer?[consumer]:[])];
    for(const control of [apply,...controls])control.disabled=true;
    try{
     const ready=await remote('readProperty',{node:'property_'+crypto.randomUUID().replaceAll('-',''),
      owner:definition,field:name,targetJson:JSON.stringify({input:receiver}),access:'read'});
     if(!alive())return;
     if(ready.node.propertyOwner!==definition||ready.node.field!==name||ready.node.signature.return!==expectedType||
        ready.node.arguments.target?.input!==receiver)throw Error('선택한 대상과 속성 계약이 바뀌었습니다. 입력은 유지됩니다.');
     close();stage(ready,input);
    }finally{if(alive()){for(const control of controls)control.disabled=false;update();}}
   },'');
   // Use the same registered project catalog as the Blueprint property picker.
   api.work(async()=>{
    const catalog=await remote('propertyCatalog',{page:0,query:''});
    if(!alive())return;
    for(const row of catalog.rows||[])owner.add(new Option(row.id,row.id));
    owner.disabled=owner.length===1;
   },'');
   target.focus();
  });
}
export function propertyPlanEdits(cells,setEdits){
 const property=cells.filter(([,v])=>v.type==='property-plan').map(([,v])=>JSON.parse(v.text)),rest=cells.filter(([,v])=>v.type!=='property-plan'),reads=[];
 for(const p of property){if(p.existing)continue;if(!p.attached)throw Error('속성 출력과 사용할 작업을 연결해 주세요. 입력은 유지됩니다.');reads.push({node:p.id,owner:p.row.propertyOwner,field:p.row.field,descriptor:p.descriptor,targetJson:rest.find(([,v])=>v.node===p.id&&v.type==='argument:target')?.[1]?.text??p.row.arguments.find(a=>a.name==='target').valueJson});}
 let sets=null,changes=[];if(rest.some(([,v])=>v.type==='set-plan'))sets=setEdits(rest)[0].definition;else for(const [,v] of rest){if(v.type.startsWith('argument:'))changes.push({action:'argument',node:v.node,name:v.type.slice(9),valueJson:v.text});else if(v.type==='route'||v.type.startsWith('route:'))changes.push({action:'route',node:v.node,port:v.type==='route'?'next':v.type.slice(6),to:v.text});else if(v.type==='entry'&&v.node==='$entry')changes.push({action:'entry',node:v.text});else if(v.type==='exit')changes.push({action:'exit',name:v.node.slice(6),valueJson:v.text});else throw Error('속성 연결과 다른 편집은 나누어 저장해 주세요. 모든 입력은 유지됩니다.');}
 return [{action:'propertyPlan',node:'$properties',definition:{reads,...(sets?{sets}:{}),changes}}];
}
