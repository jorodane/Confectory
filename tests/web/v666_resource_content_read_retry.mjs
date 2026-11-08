import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';
globalThis.addEventListener=()=>{};
const {createResourceContent}=await import('data:text/javascript;base64,'+readFileSync(resolve(process.argv[2],'examples/editor-home/ui/resource-content.js')).toString('base64'));
const project='a'.repeat(32),id='b'.repeat(32),generation='c'.repeat(64);
async function test(read,reason,alive=()=>true){
 let writes=0;const calls=[],api={current:{projectId:project},view:{observe:async(endpoint,input)=>{calls.push({endpoint,input});return read(calls.length,api);},call:()=>{writes++;throw Error('unexpected mutation');}},work:()=>{writes++;throw Error('unexpected mutation');}};
 const promise=createResourceContent(api).mount({w:{},item:{id,contentGeneration:generation},result:{},bytes:new TextEncoder().encode('safe'),alive,status:{},preview:{},actions:{},toolbar:{}});
 await assert.rejects(promise,{message:reason});assert.equal(writes,0);assert(calls.every(q=>q.endpoint==='readResourceContentDraft'&&q.input.project===project&&q.input.id===id));return calls;
}
assert.equal((await test(()=>{throw Error('busy');},'busy')).length,3);
assert.equal((await test(()=>{throw Error('observation_failed');},'observation_failed')).length,1);
let active=true;assert.equal((await test(()=>{active=false;throw Error('busy');},'scope_changed',()=>active)).length,1);
assert.equal((await test((n,api)=>{api.current.projectId='d'.repeat(32);throw Error('busy');},'scope_changed')).length,1);
active=true;assert.equal((await test(()=>{setTimeout(()=>active=false,0);throw Error('busy');},'scope_changed',()=>active)).length,1);
assert.equal((await test(n=>{if(n===1)throw Error('busy');return {project:'d'.repeat(32),id};},'resource_draft_owner')).length,2);
assert.equal((await test((n,api)=>{api.current.projectId='d'.repeat(32);return {project,id};},'scope_changed')).length,1);
console.log('PASS private content read busy-only maximum3 retries, same target, no writes, retirement/project change and post-read owner rejection');
