// Editor projection only. The engine independently checks the original region,
// complete plan, value dominance, source closure and checkpoint CAS.
const normal=to=>to?.startsWith('$exit:')?to.slice(1):to;
export function branchCellRegion(data,edges,owner,port,allowFrame=false){
 const binding=allowFrame?data.documentFrameCaseOrderBinding:null;
 const frame=!!(data.privatePath&&binding&&binding.root===data.rootId&&binding.graph===data.id&&binding.path===data.privatePath);
 if(!data.id||(!frame&&(data.id!==data.rootId||data.privatePath))||data.slotContext||data.privateCopy||data.privateConversion||data.executionExitMode||data.profile!=='sync-acyclic-switch-v1'||data.nodes.length>=64)return null;
 const byId=new Map(data.nodes.map(n=>[n.id,n])),parent=byId.get(owner);
 if(!parent||parent.kind!=='code'||parent.control!=='switch'||parent.branchOwner||parent.postCall||parent.implementationContext||parent.executionSource||parent.async||parent.forwardCallerStorage||!parent.executionEnum?.members.some(m=>m.id!==parent.executionEnum.primary&&port==='case:'+m.id))return null;
 if(new Set(edges.map(e=>e.from+'|'+e.port)).size!==edges.length||!edges.some(e=>e.from===owner&&e.port===port))return null;
 const next=(id,p)=>normal(edges.find(e=>e.from===id&&e.port===p)?.to)||'return:'+owner,order=[],seen=new Set();let at=next(owner,port);
 while(byId.has(at)){
  const n=byId.get(at);if(n.kind!=='code'||n.control!=='next'||n.branchOwner!==owner||n.implementationContext||n.forwardCallerStorage||n.postCall||n.async||n.executionEnum||seen.has(at))return null;
  seen.add(at);order.push(at);at=next(at,'next');
 }
 if(at!=='return:'+owner&&!(at?.startsWith('exit:')&&(data.exits||[]).some(e=>(e.name||e.id)===at.slice(5))))return null;
 for(let i=0;i<order.length;i++){
  const from=i?order[i-1]:owner,p=i?'next':port,id=order[i];
  if(data.entry===id||edges.some(e=>normal(e.to)===id&&(e.from!==from||e.port!==p))||edges.some(e=>e.from===id&&e.port!=='next'))return null;
 }
 if(frame&&!order.length)return null;
 return {owner,port,order,exit:at,frame};
}

export function branchOrderCells(data,cells){
 const routes=cells.map(([,v])=>v),anchors=routes.filter(v=>v.type.startsWith('route:case:'));
 if(anchors.length!==1||routes.some(v=>typeof v.text!=='string'||v.type!=='route'&&!v.type.startsWith('route:case:'))||new Set(routes.map(v=>v.node)).size!==routes.length)return false;
 const anchor=anchors[0],region=branchCellRegion(data,data.edges,anchor.node,anchor.type.slice(6),true);
 if(!region||region.frame&&region.order.length<2||routes.length!==region.order.length+1||routes.some(v=>v!==anchor&&!region.order.includes(v.node)))return false;
 const byId=new Map(routes.map(v=>[v.node,v])),seen=new Set();let at=normal(anchor.text);
 while(region.order.includes(at)){if(seen.has(at))return false;seen.add(at);at=normal(byId.get(at)?.text);}
 return seen.size===region.order.length&&at===region.exit;
}

export function branchCreationCells(data,cells,allowFrame=false){
 try{
  if(cells.length!==6||!['create','rename','intent','source'].every(type=>cells.filter(([,v])=>v.type===type).length===1))return false;
  const creation=cells.find(([,v])=>v.type==='create')[1],definition=JSON.parse(creation.text),created=creation.node,owner=definition.branchOwner;
  if(!owner||data.nodes.some(n=>n.id===created)||Object.keys(definition).length!==5||Object.keys(definition).some(k=>!['kind','control','intent','signature','branchOwner'].includes(k))||definition.kind!=='code'||definition.control!=='next'||!definition.intent?.trim()||Object.keys(definition.signature).length!==2||definition.signature.return!=='void'||!Array.isArray(definition.signature.args)||definition.signature.args.length)return false;
  const routes=cells.filter(([,v])=>v.type==='route'||v.type.startsWith('route:case:')).map(([,v])=>v),out=routes.find(v=>v.node===created),incoming=routes.find(v=>v.node!==created);
  if(routes.length!==2||!out||out.type!=='route'||!incoming||incoming.text!==created||cells.some(([,v])=>!routes.includes(v)&&v.node!==created))return false;
  for(const member of data.nodes.find(n=>n.id===owner)?.executionEnum?.members||[]){
   const region=branchCellRegion(data,data.edges,owner,'case:'+member.id,allowFrame);if(!region||region.frame&&data.documentFrameCaseCreationAvailable!==true)continue;
   const i=region.order.indexOf(incoming.node),valid=incoming.node===owner&&incoming.type==='route:'+region.port||i>=0&&incoming.type==='route';
   if(valid&&normal(out.text)===(i<0?region.order[0]||region.exit:region.order[i+1]||region.exit))return true;
  }
 }catch{}
 return false;
}

// Whole compound invocations stay in the same physical root frame. Descendant
// eligibility is projected by the engine from the observed original graph.
export function compoundCellChain(data,edges=data.edges){
 if(data.documentCompoundOrderAvailable!==true||!data.id||data.id!==data.rootId||data.privatePath||data.slotContext||data.privateCopy||data.privateConversion||data.executionExitMode||data.asyncTransition?.enabled||data.profile!=='sync-acyclic-nested-v1'||!data.nodes.some(n=>n.kind==='graph')||data.nodes.length>=64)return null;
 if(data.nodes.some(n=>!['code','graph'].includes(n.kind)||n.control!=='next'||n.branchOwner||n.implementationContext||n.contextBoundary||n.forwardCallerStorage||n.postCall||n.async||n.executionEnum))return null;
 const names=new Set(data.nodes.map(n=>n.id)),routes=edges.filter(e=>e.from!=='$entry'),start=edges.find(e=>e.from==='$entry'&&e.port==='next')?.to||data.entry;
 if(routes.length!==names.size||routes.some(e=>e.port!=='next'||!names.has(e.from))||new Set(routes.map(e=>e.from)).size!==names.size)return null;
 const order=[],seen=new Set();let at=start;
 while(names.has(at)){if(seen.has(at))return null;seen.add(at);order.push(at);at=normal(routes.find(e=>e.from===at).to);}
 return order.length===names.size&&at?.startsWith('exit:')&&(data.exits||[]).some(e=>e.name===at.slice(5))?{order,exit:at,compound:true}:null;
}
export function compoundOrderCells(data,cells){
 const region=compoundCellChain(data),rows=cells.map(([,v])=>v);
 if(!region||rows.length!==region.order.length+1||new Set(rows.map(v=>v.node)).size!==rows.length||rows.filter(v=>v.type==='entry'&&v.node==='$entry').length!==1||rows.some(v=>typeof v.text!=='string'||!(v.type==='entry'&&v.node==='$entry'||v.type==='route'&&region.order.includes(v.node))))return false;
 const links=new Map(rows.map(v=>[v.node,normal(v.text)])),seen=new Set();let at=links.get('$entry');
 while(region.order.includes(at)){if(seen.has(at))return false;seen.add(at);at=links.get(at);}
 return seen.size===region.order.length&&at===region.exit;
}

export function frameCellChain(data,edges=data.edges){
 const binding=data.documentFrameOrderBinding;
 if(!binding||binding.root!==data.rootId||binding.graph!==data.id||binding.path!==data.privatePath||!data.privatePath||data.slotContext||data.privateCopy||data.privateConversion||data.executionExitMode||data.asyncTransition?.enabled||!['sync-acyclic-nested-v1','sync-acyclic-methods-v1'].includes(data.profile)||!data.nodes.length||data.nodes.length>=64)return null;
 if(data.nodes.some(n=>n.kind!=='code'||n.control!=='next'||n.branchOwner||n.implementationContext||n.contextBoundary||n.forwardCallerStorage||n.postCall||n.async||n.executionEnum))return null;
 const names=new Set(data.nodes.map(n=>n.id)),routes=edges.filter(e=>e.from!=='$entry'),start=edges.find(e=>e.from==='$entry'&&e.port==='next')?.to||data.entry;
 if(routes.length!==names.size||routes.some(e=>e.port!=='next'||!names.has(e.from))||new Set(routes.map(e=>e.from)).size!==names.size)return null;
 const order=[],seen=new Set();let at=start;
 while(names.has(at)){if(seen.has(at))return null;seen.add(at);order.push(at);at=normal(routes.find(e=>e.from===at).to);}
 return order.length===names.size&&at?.startsWith('exit:')&&(data.exits||[]).some(e=>e.name===at.slice(5))?{order,exit:at,frame:true}:null;
}
export function frameOrderCells(data,cells){
 const region=frameCellChain(data),rows=cells.map(([,v])=>v);
 if(!region||rows.length!==region.order.length+1||new Set(rows.map(v=>v.node)).size!==rows.length||rows.filter(v=>v.type==='entry'&&v.node==='$entry').length!==1||rows.some(v=>typeof v.text!=='string'||!(v.type==='entry'&&v.node==='$entry'||v.type==='route'&&region.order.includes(v.node))))return false;
 const links=new Map(rows.map(v=>[v.node,normal(v.text)])),seen=new Set();let at=links.get('$entry');
 while(region.order.includes(at)){if(seen.has(at))return false;seen.add(at);at=links.get(at);}
 return seen.size===region.order.length&&at===region.exit;
}

export function serialCreationCells(data,cells,placement='frame'){
 try{
  const chain=placement==='frame'&&data.profile==='sync-acyclic-nested-v1'?frameCellChain(data):null;
  const first=placement==='root-start'?data.documentRootStart?.entry:chain?.order[0];
  const compounds=placement==='compound'?data.documentCompoundInsertion?.nodes:null;
  if((!first&&!compounds?.length)||cells.length!==6||!['create','rename','intent','source'].every(type=>cells.filter(([,v])=>v.type===type).length===1))return false;
  const creation=cells.find(([,v])=>v.type==='create')[1],id=creation.node,definition=JSON.parse(creation.text);
  if(data.nodes.some(n=>n.id===id)||Object.keys(definition).length!==4||Object.keys(definition).some(k=>!['kind','control','intent','signature'].includes(k))||definition.kind!=='code'||definition.control!=='next'||!definition.intent?.trim()||Object.keys(definition.signature).length!==2||definition.signature.return!=='void'||!Array.isArray(definition.signature.args)||definition.signature.args.length)return false;
  const routes=cells.filter(([,v])=>v.type==='route'||v.type==='entry').map(([,v])=>v),out=routes.find(v=>v.type==='route'&&v.node===id),incoming=routes.find(v=>v.node!==id);
  if(routes.length!==2||!out||!incoming||incoming.text!==id||cells.some(([,v])=>!routes.includes(v)&&v.node!==id))return false;
  if(incoming.type==='entry')return !!first&&incoming.node==='$entry'&&out.text===first;
  if(compounds)return compounds.includes(incoming.node)&&data.edges.some(edge=>edge.from===incoming.node&&edge.port==='next'&&normal(edge.to)===normal(out.text));
  if(!chain)return false;
  const index=chain.order.indexOf(incoming.node);return index>=0&&normal(out.text)===(chain.order[index+1]||chain.exit);
 }catch{return false;}
}
