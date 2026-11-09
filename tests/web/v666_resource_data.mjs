import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
const root=process.argv[2];
const {createResourceLayoutControls}=await import(pathToFileURL(root+'/examples/editor-home/ui/resource-layout.js'));
const realSet=globalThis.setTimeout,realClear=globalThis.clearTimeout,realDocument=globalThis.document;
let next=0,timers=new Map(),made=0;
globalThis.setTimeout=(fn,ms)=>{assert.equal(ms,260);const id=++next;timers.set(id,fn);return id;};globalThis.clearTimeout=id=>timers.delete(id);
try{
 function fixture(){
  timers.clear();let selected=[],alive=true,pending=false,revision='r1';const row={id:'file',name:'원본 🧪.txt',kind:'document',hash:'hash'},token={},w={meta:{density:100},el:{},resourceScope:'owned',resourceLifetime:token};
  const node={isConnected:true,hasAttribute:()=>false,replaceChildren:input=>{node.input=input;}};
  globalThis.document={activeElement:{closest:()=>null},createElement:()=>{made++;return{dataset:{},setAttribute(){},focus(){},select(){}};}};
  const api={current:{projectId:'owned'},busy:false,alive:()=>alive,catalogue:()=>({status:'ready',revision,items:[row]}),rows:()=>[row],pending:()=>pending,persist(){},render(){},selection:{ids:()=>selected,select:(w,item)=>{selected=[item.id];w.resourceUserSelection=(w.resourceUserSelection||0)+1;}}};
  const controls=createResourceLayoutControls(api);controls.bindDataName(w,node,row,'owned',token);const click=()=>node.onclick({stopPropagation(){},detail:1});const run=()=>{for(const[id,fn]of [...timers]){timers.delete(id);fn();}};
  return{w,node,controls,click,run,select:()=>{selected=['file'];},stale:()=>{revision='r2';},hide:()=>{alive=false;},pending:()=>{pending=true;}};
 }
 let f=fixture();const before=made;f.click();assert.equal(timers.size,0);f.click();const obsolete=[...timers.values()][0];f.click();assert.equal(timers.size,1);obsolete();assert.equal(made,before);f.run();assert.equal(made,before+1);assert.equal(f.w.meta.resourceRenameInput.name,'원본 🧪.txt');assert.equal(f.w.meta.resourceRenameInput.revision,'r1');
 for(const cancel of [f=>f.controls.cancelNameActivation(f.w),f=>f.stale(),f=>f.hide(),f=>f.pending(),f=>{f.w.meta.queryInput='later';},f=>{f.w.resourceUserSelection=(f.w.resourceUserSelection||0)+1;},f=>{f.node.isConnected=false;},f=>{document.activeElement={closest:s=>s.startsWith('input')?{}:null};},f=>f.controls.retire(f.w)]){
  f=fixture();f.select();const before=made;f.click();cancel(f);f.run();assert.equal(made,before);assert.equal(f.w.meta.resourceRenameInput,undefined);
 }
 f=fixture();f.select();f.click();f.node.ondblclick();f.run();assert.equal(f.w.meta.resourceRenameInput,undefined);
 f=fixture();f.select();f.controls.bindDrag(f.w,f.node,{id:'file',hash:'hash'},'owned',{});
 let payload,prevented=false;const tree={closest:s=>s==='button'?tree:null};f.node.ondragstart({target:tree,currentTarget:f.node,stopPropagation(){},preventDefault(){prevented=true;},dataTransfer:{setData:(k,v)=>{payload=JSON.parse(v);}}});assert.equal(prevented,false);assert.deepEqual(payload.ids,['file']);assert.equal(payload.projectId,'owned');
 for(const selector of ['input,textarea,select,[contenteditable]','[data-resource-open]']){payload=null;prevented=false;f.node.ondragstart({target:{closest:s=>s===selector?{}:null},currentTarget:f.node,stopPropagation(){},preventDefault(){prevented=true;},dataTransfer:{setData:()=>{payload=true;}}});assert.equal(prevented,true);assert.equal(payload,null);}
 console.log('PASS actual Data-name activation: first select, coalesced delayed rename, exact native basis; stale/pending/input/focus/detached/retired/double-click rejection without Save');
}finally{globalThis.setTimeout=realSet;globalThis.clearTimeout=realClear;globalThis.document=realDocument;}
