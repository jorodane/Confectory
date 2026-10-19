import {test} from 'node:test';
import assert from 'node:assert/strict';
import {runInNewContext} from 'node:vm';
import {bridgePage} from '../worker/bridge-page.js';
const source=bridgePage.match(/<script nonce="confectory-bridge">([\s\S]*?)<\/script>/)[1];
async function until(promise){let timer;try{await Promise.race([promise,new Promise((_,reject)=>{timer=setTimeout(()=>reject(Error('bridge fixture timeout')),2000);})]);}finally{clearTimeout(timer);}}
async function fixture(cancelAt=null){
 const elements={'#state':{},'#close':{hidden:true},'#login':{hidden:false}},events=[],protocol='confectory.editor.v1',nonce='a'.repeat(64),sessionId='b'.repeat(32);
 let receive,dispatches=0,completions=0,release,doneResolve,pauseResolve,loginHiddenWhileConnected=false;
 const done=new Promise(r=>doneResolve=r),paused=new Promise(r=>pauseResolve=r);
 function answer(m,result){queueMicrotask(()=>receive({data:{protocol,nonce,requestId:m.requestId,result}}));}
 function nativeReply(m,result){if(cancelAt===m.type){release=()=>answer(m,result);pauseResolve();}else answer(m,result);}
 const native={addEventListener(_,callback){receive=callback;},postMessage(m){
  events.push(m);
  if(m.type==='ready')queueMicrotask(()=>receive({data:{protocol,type:'hello',nonce,instanceId:'engine'}}));
  else if(m.type==='paired')nativeReply(m,{});
  else if(m.type==='pulse'){loginHiddenWhileConnected=elements['#login'].hidden;answer(m,{instanceId:'engine',scopeVersion:1,scope:{id:'scope',projectId:'project',node:'',readOnly:false},tools:[]});}
  else if(m.type==='dispatch'){dispatches++;nativeReply(m,{value:{applied:true}});}
  else if(m.type==='close')answer(m,{});
 }};
 async function fetch(path,request){
  assert(path.startsWith('/api/'));assert.equal(request.credentials,'same-origin');assert.equal(request.headers['content-type'],'application/json');
  const payload=JSON.parse(request.body);events.push({path,payload});
  if(cancelAt==='api:'+path.slice(5))await new Promise(resolve=>{release=resolve;pauseResolve();});
  let result={ok:true};
  if(path==='/api/pair')result={sessionId,expiresAt:Date.now()+600000};
  if(path==='/api/claim')result={job:{id:'job',claim:'claim',callId:'call',name:'workspace_stage',arguments:{}}};
  if(path==='/api/complete'){completions++;if(completions===1)throw new TypeError('lost response');if(completions===2)return {ok:false,status:503,json:async()=>({error:{code:'temporary'}})};doneResolve();}
  return {ok:true,status:200,json:async()=>result};
 }
 runInNewContext(source,{window:{chrome:{webview:native}},document:{querySelector:q=>elements[q]},fetch,TypeError,Map,Promise,Error,Date,setTimeout(fn,ms){if(ms!==2000&&ms!==20000)queueMicrotask(fn);return 1;},clearTimeout(){}});
 if(cancelAt){
  await until(paused);
  if(cancelAt==='paired')assert.equal(elements['#login'].hidden,false,'An unacknowledged pair must not hide login as if connected');
  elements['#close'].onclick();release();await new Promise(r=>setTimeout(r,10));
 }else{await until(done);elements['#close'].onclick();await new Promise(r=>setTimeout(r,10));}
 return {events,dispatches,completions,loginHiddenWhileConnected,loginHiddenAfterClose:elements['#login'].hidden,closeHidden:elements['#close'].hidden,status:elements['#state'].textContent};
}
test('completion retries retransmit the same claim without executing the engine again',async()=>{
 const r=await fixture();assert.equal(r.dispatches,1);assert.equal(r.completions,3);
 const records=r.events.filter(e=>e.path==='/api/complete');assert.deepEqual(records[0].payload,records[1].payload);assert.deepEqual(records[1].payload,records[2].payload);
 assert.equal(r.events.filter(e=>e.type==='dispatch').length,1);assert(r.loginHiddenWhileConnected);assert.equal(r.loginHiddenAfterClose,false);
 assert.match(bridgePage,/signin-with-chatgpt\?return_to=%2Feditor-bridge/);assert(!bridgePage.includes('localStorage'));
});
test('closing during an engine operation discards its late completion',async()=>{
 const r=await fixture('dispatch');assert.equal(r.dispatches,1);assert.equal(r.completions,0);assert(r.events.some(e=>e.path==='/api/close'));assert(r.closeHidden);assert.match(r.status,/연결을 닫았습니다/);
});
for(const stage of ['api:pair','paired','api:pulse','api:claim'])test('closing during '+stage+' ignores late results and keeps the disconnected UI',async()=>{
 const r=await fixture(stage);assert.equal(r.dispatches,0);assert.equal(r.completions,0);assert(r.closeHidden);assert.equal(r.loginHiddenAfterClose,false);assert.match(r.status,/연결을 닫았습니다/);
 if(stage==='api:pair'){assert(!r.events.some(e=>e.type==='paired'));assert(r.events.some(e=>e.path==='/api/close'&&e.payload.sessionId==='b'.repeat(32)));}
 if(stage==='paired'||stage==='api:pulse')assert(!r.events.some(e=>e.path==='/api/claim'));
});
