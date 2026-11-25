// Transport coalescing must preserve revision validation, ownership and unreplayed calls.
import fs from 'node:fs';
import assert from 'node:assert/strict';
const source=fs.readFileSync(new URL('../../packs/web-ui/Client.csbody',import.meta.url),'utf8').split('"""')[1];
const {WebView}=await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));
let mounts=0,reads=0;const waiting=[],invoked=[],rendered=[];
const transport=async request=>{
 if(request.op==='mount'){const n=++mounts;return {ok:true,view:'v'+n,scope:{project:'p'+n},revision:n,state:{project:'p'+n}};}
 if(request.op==='update'){reads++;return new Promise(resolve=>waiting.push(resolve));}
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
diagnostic.flushPerformance();assert.equal(batches.length,1);
finish.shift()({ok:true});await new Promise(resolve=>setImmediate(resolve));diagnostic.flushPerformance();assert.equal(batches.length,2);
assert.deepEqual(Object.keys(batches[1].rows[0]).sort(),['elapsedMs','operation','pageMs','stage']);
finish.shift()({ok:true});await new Promise(resolve=>setImmediate(resolve));await diagnostic.dispose();
console.log('PASS bounded performance batches keep ready events and at most one transport in flight');
