// Transport coalescing must preserve revision validation, ownership and unreplayed calls.
import fs from 'node:fs';
import assert from 'node:assert/strict';
const source=fs.readFileSync(new URL('../../packs/web-ui/Client.csbody',import.meta.url),'utf8').split('"""')[1];
const {WebView}=await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));
let mounts=0,reads=0;const waiting=[],invoked=[],rendered=[];
const transport=async request=>{
 if(request.op==='mount'){const n=++mounts;return {ok:true,view:'v'+n,scope:{project:'p'+n},revision:n,state:{project:'p'+n}};}
 if(request.op==='update'){assert(!('receivedRequestIds' in request));reads++;return new Promise(resolve=>waiting.push(resolve));}
 if(request.op==='invoke'){invoked.push(request);return {ok:true,status:'pending'};}
 if(request.op==='dispose')return {ok:true};
 throw Error('unexpected operation');
};
const view=new WebView(transport,state=>rendered.push(state.project));await view.mount();
const a=view.update(),b=view.update();assert.equal(a,b);assert.equal(reads,1);
waiting.shift()({ok:true,revision:1,state:{project:'p1'},results:[]});await Promise.all([a,b]);
const call=view.call('edit',{revision:1,value:'retained'});const invoke=invoked[0];assert.equal(invoke.expectedRevision,1);
const read=view.update();waiting.shift()({ok:true,revision:2,state:{project:'p1-edited'},results:[{requestId:invoke.requestId,ok:true,result:{accepted:true}}]});await read;assert.deepEqual(await call,{accepted:true});assert.equal(invoked.length,1);
// An old in-flight update cannot coalesce with or overwrite a new mounted owner.
const old=view.update();await view.dispose();await view.mount();const fresh=view.update();assert.notEqual(old,fresh);
waiting.shift()({ok:true,revision:99,state:{project:'retired'},results:[]});await old;assert.equal(view.state.project,'p2');
waiting.shift()({ok:true,revision:2,state:{project:'p2'},results:[]});await fresh;assert(!rendered.includes('retired'));
// Failed reads release the coalescing slot; callers explicitly retry, never re-invoke edits.
const fail=view.update();waiting.shift()({ok:false,error:{code:'consumer_error'}});await assert.rejects(fail,/consumer_error/);
const retry=view.update();waiting.shift()({ok:true,revision:2,state:{project:'p2'},results:[]});await retry;assert.equal(invoked.length,1);
const pending=view.call('pending',{});const rejection=assert.rejects(pending,/view_closed/);await view.dispose();await rejection;
console.log('PASS coalesced snapshots, exact revision, retired generation, failed-read retry and no mutation replay');

// Slow diagnostics never displace the actual ready event or queue multiple
// telemetry transports beside an ordinary retained command.
const batches=[],finish=[];
const diagnostic=new WebView(async request=>{
 if(request.op==='mount')return {ok:true,view:'diagnostic',scope:{project:'fixture'},revision:1,state:{},performance:true};
 if(request.op==='performance'){batches.push(request);return new Promise(resolve=>finish.push(resolve));}
 if(request.op==='dispose')return {ok:true};
 throw Error('unexpected diagnostic operation');
});
await diagnostic.mount();
for(let i=0;i<40;i++)diagnostic.performanceMark('renderer-update','',performance.now()-30);
diagnostic.performanceMark('window-ready','openEditorView',performance.now()-10);
diagnostic.flushPerformance();
assert.equal(batches.length,1);assert.equal(batches[0].rows.length,32);
assert(batches[0].rows.some(row=>row.stage==='window-ready'));
diagnostic.performanceMark('restore-total','restore',performance.now()-20);
diagnostic.performanceMark('property-save-ready','direct-property-save',performance.now()-20);
diagnostic.performanceMark('window-ready','reopenEditorView',performance.now()-20);
for(let i=0;i<80;i++)diagnostic.performanceMark('renderer-call','browserDrafts',performance.now()-30);
diagnostic.flushPerformance();assert.equal(batches.length,1);
finish.shift()({ok:true});await new Promise(resolve=>setImmediate(resolve));diagnostic.flushPerformance();assert.equal(batches.length,2);
assert.deepEqual(Object.keys(batches[1].rows[0]).sort(),['elapsedMs','operation','pageMs','stage']);
assert(batches[1].rows.some(row=>row.stage==='restore-total'));
assert(batches[1].rows.some(row=>row.stage==='property-save-ready'));
assert(batches[1].rows.some(row=>row.stage==='window-ready'&&row.operation==='reopenEditorView'));
finish.shift()({ok:true});await new Promise(resolve=>setImmediate(resolve));await diagnostic.dispose();
console.log('PASS bounded performance batches keep ready events and at most one transport in flight');

// A bounded completion is a normal revisioned snapshot, not a second command.
// Background reads are suppressed during the short acknowledgement only;
// explicit updates, an expired wait and the ordinary fallback remain available.
const completions=[],completionReads=[],completionRenders=[];
const completionView=new WebView(async request=>{
 if(request.op==='mount')return {ok:true,view:'completion',scope:{project:'fixture'},revision:1,state:{value:'before'}};
 if(request.op==='invoke')return new Promise(resolve=>completions.push({request,resolve}));
 if(request.op==='update')return new Promise(resolve=>completionReads.push(resolve));
 if(request.op==='dispose')return {ok:true};
 throw Error('unexpected completion operation');
},state=>completionRenders.push(state.value));
await completionView.mount();
const fast=completionView.call('connectionSetup',{}, {completion:true});
await completionView.poll();assert.equal(completionReads.length,0);
const fastRow=completions.shift();assert.equal(fastRow.request.completion,true);
fastRow.resolve({ok:true,status:'pending',completion:{ok:true,revision:2,state:{value:'ready'},results:[{requestId:fastRow.request.requestId,ok:true,result:{ready:true}}]}});
assert.deepEqual(await fast,{ready:true});assert.equal(completionView.revision,2);assert.equal(completionReads.length,0);assert.deepEqual(completionRenders,['before','ready']);
const slow=completionView.call('connectionSetup',{}, {completion:true});const slowRow=completions.shift();
await new Promise(resolve=>setTimeout(resolve,170));const expired=completionView.poll();assert.equal(completionReads.length,1);
completionReads.shift()({ok:true,busy:true,results:[]});await expired;
slowRow.resolve({ok:true,status:'pending'});await new Promise(resolve=>setImmediate(resolve));assert.equal(completionReads.length,1);
completionReads.shift()({ok:true,revision:3,state:{value:'fallback'},results:[{requestId:slowRow.request.requestId,ok:true,result:{ready:true}}]});assert.deepEqual(await slow,{ready:true});
const stale=completionView.call('connectionSetup',{}, {completion:true});const staleRow=completions.shift();staleRow.resolve({ok:true,status:'pending',completion:{ok:true,revision:4,state:{value:'newer'},results:[{requestId:staleRow.request.requestId,ok:false,error:{code:'stale_revision'}}]}});await assert.rejects(stale,/stale_revision/);assert.equal(completionView.revision,4);
const retired=completionView.call('connectionSetup',{}, {completion:true});const retiredRow=completions.shift();const rejected=assert.rejects(retired,/view_closed/);await completionView.dispose();await rejected;retiredRow.resolve({ok:true,completion:{ok:true,revision:99,state:{value:'retired'},results:[]}});await new Promise(resolve=>setImmediate(resolve));assert(!completionRenders.includes('retired'));
console.log('PASS bounded completion snapshot, fallback, stale admission and retired acknowledgement');

// Result exclusion filters only rows actually received by this mounted view.
// A read started before a new admission can still carry its completion;
// lost reads acknowledge nothing and never trigger a second invocation.
const selectedReads=[],selectedInvokes=[];
const selective=new WebView(async request=>{
 if(request.op==='mount')return {ok:true,view:'selection',scope:{project:'fixture'},revision:1,state:{},receivedResultSelection:true};
 if(request.op==='invoke'){selectedInvokes.push(request);return {ok:true,status:'pending'};}
 if(request.op==='update')return new Promise((resolve,reject)=>selectedReads.push({request,resolve,reject}));
 if(request.op==='dispose')return {ok:true};
 throw Error('unexpected result selection operation');
});
await selective.mount();
const initial=selective.update();assert.deepEqual(selectedReads[0].request.receivedRequestIds,[]);
const first=selective.call('edit',{value:1});const firstId=first.requestId;
await new Promise(resolve=>setImmediate(resolve));assert.equal(selectedReads.length,1);
selectedReads.shift().reject(Error('transport_lost'));await assert.rejects(initial,/transport_lost/);
const retried=selective.update();assert.deepEqual(selectedReads[0].request.receivedRequestIds,[]);
const second=selective.call('edit',{value:2});const secondId=second.requestId;
await new Promise(resolve=>setImmediate(resolve));
// The second result was admitted after the request was sent, but is not
// excluded. Both results can settle with the same old in-flight read.
selectedReads.shift().resolve({ok:true,revision:2,state:{},results:[{requestId:firstId,ok:true,result:{accepted:1}},{requestId:secondId,ok:false,error:{code:'stale_revision'}}]});
await assert.rejects(second,/stale_revision/);await retried;assert.deepEqual(await first,{accepted:1});
const idle=selective.update();assert.deepEqual(selectedReads[0].request.receivedRequestIds,[firstId,secondId]);
selectedReads.shift().resolve({ok:true,revision:2,state:{},results:[]});await idle;
assert.equal(selectedInvokes.length,2);await selective.dispose();
await selective.mount();const freshSelection=selective.update();assert.deepEqual(selectedReads[0].request.receivedRequestIds,[]);
selectedReads.shift().resolve({ok:true,revision:1,state:{},results:[]});await freshSelection;await selective.dispose();
console.log('PASS received-result exclusion, lost read, concurrent admission, stale rejection and no replay');

// Exact public field references are tied to the request's captured state, not
// the latest mutable UI. Old peers still receive the full ordinary state.
const reuseReads=[],reuseInvokes=[];
const reuse=new WebView(async request=>{
 if(request.op==='mount')return {ok:true,view:'metadata',scope:{project:'same'},revision:1,state:{inventory:{rows:[{id:'A'}]}},stateReuseFields:['inventory'],stateFieldHashes:{inventory:'a'}};
 if(request.op==='update')return new Promise(resolve=>reuseReads.push({request,resolve}));
 if(request.op==='invoke')return new Promise(resolve=>reuseInvokes.push({request,resolve}));
 if(request.op==='dispose')return {ok:true};throw Error('unexpected state reference operation');
});
await reuse.mount();const inventoryA=reuse.state.inventory;assert(Object.isFrozen(inventoryA.rows[0]));assert.throws(()=>{inventoryA.rows[0].id='modified';},TypeError);
const same=reuse.update();assert.deepEqual(reuseReads[0].request.knownStateFields,{inventory:'a'});reuseReads.shift().resolve({ok:true,revision:2,state:{},stateFieldHashes:{inventory:'a'},reusedStateFields:{inventory:'a'},results:[]});await same;assert.equal(reuse.state.inventory,inventoryA);
const older=reuse.update();const edited=reuse.call('edit',{}, {completion:true});assert.deepEqual(reuseInvokes[0].request.knownStateFields,{inventory:'a'});const invocation=reuseInvokes.shift();invocation.resolve({ok:true,completion:{ok:true,revision:4,state:{inventory:{rows:[{id:'B'}]}},stateFieldHashes:{inventory:'b'},results:[{requestId:invocation.request.requestId,ok:true,result:{accepted:true}}]}});assert.deepEqual(await edited,{accepted:true});reuseReads.shift().resolve({ok:true,revision:3,state:{},stateFieldHashes:{inventory:'a'},reusedStateFields:{inventory:'a'},results:[]});await older;assert.equal(reuse.state.inventory.rows[0].id,'B');
const wrong=reuse.update();reuseReads.shift().resolve({ok:true,revision:5,state:{},stateFieldHashes:{inventory:'a'},reusedStateFields:{inventory:'a'},results:[]});await assert.rejects(wrong,/state_reference_mismatch/);assert.equal(reuse.state.inventory.rows[0].id,'B');
await reuse.dispose();await reuse.mount();assert.equal(reuse.state.inventory.rows[0].id,'A');await reuse.dispose();
console.log('PASS exact immutable state references, stale completion ordering, mismatch refusal and remount isolation');

// A relation patch is only accepted for the captured immutable public map and
// exact version, even across an intervening state with no current map. An old
// view cannot lend its basis to a new activation.
const deltaReads=[],deltaInvokes=[];
const mapA={version:'a',scope:'owned',status:'snapshot',nodes:[{id:'A',revision:1},{id:'B',revision:1}],edges:[{key:'e',source:'A',target:'B'}]};
const delta=new WebView(async request=>{
 if(request.op==='mount')return {ok:true,view:'delta',scope:{project:'one'},revision:1,state:{relationsMap:structuredClone(mapA)},stateReuseFields:['relationsMap'],stateFieldHashes:{relationsMap:'a'},relationMapDeltas:true};
 if(request.op==='update')return new Promise(resolve=>deltaReads.push({request,resolve}));
 if(request.op==='invoke')return new Promise(resolve=>deltaInvokes.push({request,resolve}));
 if(request.op==='dispose')return {ok:true};throw Error('unexpected delta operation');
});
await delta.mount();const initialMap=delta.state.relationsMap;
const absent=delta.update();deltaReads.shift().resolve({ok:true,revision:2,state:{relationsMap:null},stateFieldHashes:{},results:[]});await absent;assert.equal(delta.state.relationsMap,null);
const patch={basis:'a',hash:'b',header:{version:'b',scope:'owned',status:'snapshot'},nodes:{length:2,edits:[[0,{id:'A',revision:2}]]},edges:{length:1,edits:[]}};
const changed=delta.update();assert.equal(deltaReads[0].request.relationMapDelta,true);assert.deepEqual(deltaReads[0].request.knownStateFields,{relationsMap:'a'});
deltaReads.shift().resolve({ok:true,revision:3,state:{},stateFieldHashes:{relationsMap:'b'},relationMapDelta:patch,results:[]});await changed;
assert.equal(delta.state.relationsMap.nodes[0].revision,2);assert.equal(delta.state.relationsMap.nodes[1],initialMap.nodes[1]);assert.equal(delta.state.relationsMap.edges[0],initialMap.edges[0]);assert(Object.isFrozen(delta.state.relationsMap.nodes[0]));
const invalid=delta.update();deltaReads.shift().resolve({ok:true,revision:4,state:{},stateFieldHashes:{relationsMap:'b'},relationMapDelta:patch,results:[]});await assert.rejects(invalid,/state_delta_mismatch/);assert.equal(delta.state.relationsMap.version,'b');
const fallback=delta.update();assert(!deltaReads[0].request.knownStateFields);deltaReads.shift().resolve({ok:true,revision:4,state:{relationsMap:structuredClone(mapA)},stateFieldHashes:{relationsMap:'a'},results:[]});await fallback;
const olderDelta=delta.update(),newerDelta=delta.call('read',{}, {completion:true});const deltaInvocation=deltaInvokes.shift();deltaInvocation.resolve({ok:true,completion:{ok:true,revision:6,state:{relationsMap:{...mapA,version:'c'}},stateFieldHashes:{relationsMap:'c'},results:[{requestId:deltaInvocation.request.requestId,ok:true,result:{}}]}});await newerDelta;
deltaReads.shift().resolve({ok:true,revision:5,state:{},stateFieldHashes:{relationsMap:'b'},relationMapDelta:patch,results:[]});await olderDelta;assert.equal(delta.state.relationsMap.version,'c');
await delta.dispose();await delta.mount();assert.equal(delta.state.relationsMap.version,'a');await delta.dispose();
console.log('PASS exact relation delta across absent state, unchanged row identity, wrong basis fallback, stale completion and remount isolation');

await delta.mount();
const recovery=delta.call('write',{}, {completion:true}), recoveryInvoke=deltaInvokes.shift();
recoveryInvoke.resolve({ok:true,completion:{ok:true,revision:2,state:{},stateFieldHashes:{relationsMap:'b'},relationMapDelta:{...patch,basis:'wrong'},results:[{requestId:recoveryInvoke.request.requestId,ok:true,result:{saved:true}}]}});
await new Promise(resolve=>setTimeout(resolve,0));
assert.equal(deltaReads.length,1);assert(!deltaReads[0].request.knownStateFields);
deltaReads.shift().resolve({ok:true,revision:2,state:{relationsMap:{...mapA,version:'b'}},stateFieldHashes:{relationsMap:'b'},results:[{requestId:recoveryInvoke.request.requestId,ok:true,result:{saved:true}}]});
assert.deepEqual(await recovery,{saved:true});assert.equal(deltaInvokes.length,0);await delta.dispose();
console.log('PASS invalid completion delta recovers retained result through full update without replay');

// Ordinary state equality is content-bound, not revision-bound. The retained
// base is an independent JSON value, so presentation mutations cannot corrupt
// a later exact host reference. The relation field follows its own proof.
const baseReads=[],baseInvokes=[];
const simple=new WebView(async request=>{
 if(request.op==='mount')return {ok:true,view:'base',scope:{project:'p'},revision:1,state:{presentation:{label:'original'},counter:1,relationsMap:structuredClone(mapA)},stateReuseFields:['relationsMap'],stateFieldHashes:{relationsMap:'a'},relationMapDeltas:true,baseStateReuse:true,stateBaseHash:'base1'};
 if(request.op==='update')return new Promise(resolve=>baseReads.push({request,resolve}));
 if(request.op==='invoke')return new Promise(resolve=>baseInvokes.push({request,resolve}));
 if(request.op==='dispose')return {ok:true};throw Error('unexpected base state operation');
});
await simple.mount();simple.state.presentation.label='local mutation';
const sameBase=simple.update();assert.equal(baseReads[0].request.knownStateBase,'base1');
baseReads.shift().resolve({ok:true,revision:2,state:{},stateBaseHash:'base1',reusedStateBase:'base1',stateFieldHashes:{relationsMap:'b'},relationMapDelta:patch,results:[]});await sameBase;
assert.equal(simple.state.presentation.label,'original');assert.equal(simple.state.relationsMap.nodes[0].revision,2);
const changedBase=simple.update();
baseReads.shift().resolve({ok:true,revision:2,state:{presentation:{label:'fresh evidence'},counter:2},stateBaseHash:'base2',stateFieldHashes:{relationsMap:'b'},reusedStateFields:{relationsMap:'b'},results:[]});await changedBase;
assert.equal(simple.state.presentation.label,'fresh evidence');assert.equal(simple.state.counter,2);
const badBase=simple.update();baseReads.shift().resolve({ok:true,revision:3,state:{},stateBaseHash:'base1',reusedStateBase:'base1',results:[]});await assert.rejects(badBase,/state_base_mismatch/);
const recoverBase=simple.update();assert(!baseReads[0].request.knownStateBase);baseReads.shift().resolve({ok:true,revision:3,state:{presentation:{label:'full fallback'},counter:3,relationsMap:null},stateBaseHash:'base3',results:[]});await recoverBase;
assert.equal(simple.state.presentation.label,'full fallback');
const baseCall=simple.call('save',{}, {completion:true}),baseInvocation=baseInvokes.shift();assert.equal(baseInvocation.request.knownStateBase,'base3');
baseInvocation.resolve({ok:true,completion:{ok:true,revision:4,state:{},stateBaseHash:'wrong',reusedStateBase:'wrong',results:[{requestId:baseInvocation.request.requestId,ok:true,result:{saved:true}}]}});
await new Promise(resolve=>setTimeout(resolve,0));assert.equal(baseReads.length,1);assert(!baseReads[0].request.knownStateBase);
baseReads.shift().resolve({ok:true,revision:4,state:{presentation:{label:'committed'},counter:4,relationsMap:null},stateBaseHash:'base4',results:[{requestId:baseInvocation.request.requestId,ok:true,result:{saved:true}}]});assert.deepEqual(await baseCall,{saved:true});assert.equal(baseInvokes.length,0);
await simple.dispose();await simple.mount();assert.equal(simple.state.presentation.label,'original');await simple.dispose();
console.log('PASS exact ordinary-state reference, mutable UI isolation, same-revision changed content, full fallback and no replay');

// Automatic short completion is scoped to a successful source confirmation,
// not ordinary restore reads or draft mutations.
const postReads=[],postInvokes=[];
const postSave=new WebView(async request=>{
 if(request.op==='mount')return {ok:true,view:'post-save',scope:{project:'p'},revision:1,state:{},readCompletion:true,inventoryCompletion:true};
 if(request.op==='update')return new Promise(resolve=>postReads.push({request,resolve}));
 if(request.op==='invoke')return new Promise(resolve=>postInvokes.push({request,resolve}));
 if(request.op==='dispose')return {ok:true};throw Error('unexpected post-save operation');
});
async function postResult(endpoint,input,result,completion,options={}){
 const call=postSave.call(endpoint,input,options),inv=postInvokes.shift();
 assert.equal(inv.request.completion===true,completion);
 const state={ok:true,revision:postSave.revision+1,state:{},results:[{requestId:inv.request.requestId,ok:true,result}]};
 if(completion)inv.resolve({ok:true,completion:state});
 else{inv.resolve({ok:true});await new Promise(resolve=>setTimeout(resolve,0));postReads.shift().resolve(state);}
 assert.deepEqual(await call,result);
}
await postSave.mount();
await postResult('localInventory',{}, {accepted:true},false);
await postResult('localInventory',{}, {accepted:true},true,{completion:true});
await postResult('localInventory',{relations:true}, {accepted:true},false);
await postResult('browserDrafts',{action:'status'},{state:'ready'},false);
await postResult('directPropertyConfirm',{}, {sourceConfirmed:true},false);
await postResult('browserDrafts',{action:'save'},{state:'applied'},false);
await postResult('browserDrafts',{action:'status'},{state:'ready'},true);
await postResult('relationsMap',{}, {accepted:true},true);
await postResult('browserDrafts',{action:'status'},{state:'ready'},false);
await postSave.dispose();
console.log('PASS bounded post-confirm read completion, ordinary restore and draft mutations retain fallback');
