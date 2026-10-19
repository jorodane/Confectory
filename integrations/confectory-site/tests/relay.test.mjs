import {test} from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {readFileSync,mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import app from '../worker/index.js';

class D1 {
 constructor(path){this.raw=new DatabaseSync(path);}
 prepare(sql){const raw=this.raw;return {bind(...args){const statement=raw.prepare(sql);return {
  async first(){return statement.get(...args)??null;},
  async all(){return {results:statement.all(...args)};},
  async run(){const result=statement.run(...args);return {meta:{changes:Number(result.changes)}};}
 };}};}
 async batch(statements){this.raw.exec('BEGIN');try{const result=[];for(const statement of statements)result.push(await statement.run());this.raw.exec('COMMIT');return result;}catch(e){this.raw.exec('ROLLBACK');throw e;}}
}
test('private persistent relay boundaries, duplicate calls, cancellation, expiry and cold storage',async t=>{
 const folder=mkdtempSync(join(tmpdir(),'confectory-site-')),path=join(folder,'state.sqlite');let db=new D1(path),now=1780000000000,worker=app;
 t.mock.method(Date,'now',()=>now);t.after(()=>{db.raw.close();rmSync(folder,{recursive:true});});
 db.raw.exec(readFileSync(new URL('../drizzle/0000_demonic_tempest.sql',import.meta.url),'utf8'));
 const origin='https://confectory-connect.jorodane.chatgpt.site';
 async function request(path,value,owner='owner-a',extra={}){const r=await worker.fetch(new Request(origin+path,{method:'POST',headers:{'content-type':'application/json',origin,...(owner?{'oai-authenticated-user-id':owner}:{}),...extra},body:JSON.stringify(value)}),{DB:db});return [r.status,await r.json()];}
 const api=async(action,value,owner='owner-a',status=200)=>{const [s,r]=await request('/api/'+action,value,owner);assert.equal(s,status,JSON.stringify(r));return r;};
 const mcp=async(name,args={},owner='owner-a')=>{const [status,r]=await request('/mcp',{jsonrpc:'2.0',id:'fixture',method:'tools/call',params:{name,arguments:args}},owner);assert.equal(status,200);return JSON.parse(r.result.content[0].text);};
 const fails=async(name,args,code,owner='owner-a')=>assert.equal((await mcp(name,args,owner)).error?.code,code);
 assert.equal((await request('/mcp',{},null))[0],401);
 assert.equal((await request('/api/pair',{instanceId:'engine'},'owner-a',{origin:'https://foreign.invalid'}))[0],403);
 const discover=await request('/mcp',{jsonrpc:'2.0',id:1,method:'server/discover'});assert.deepEqual(discover[1].result.supportedVersions,['2026-07-28','2025-03-26']);
 const definitions=(await request('/mcp',{jsonrpc:'2.0',id:2,method:'tools/list'}))[1].result.tools;assert.equal(definitions.length,9);assert(!JSON.stringify(definitions).includes('owner-a'));assert(!definitions.some(t=>/shell|confirm|execute/.test(t.name)));
 let pair=await api('pair',{instanceId:'engine'}),sessionId=pair.sessionId;
 const engine=(await mcp('confectory_engines')).engines[0];assert.equal(engine.scope,null);assert.equal(engine.scopeVersion,0);
 await api('pulse',{sessionId,instanceId:'engine',scopeVersion:0,scope:null,tools:[]},'owner-b',403);
 let pins={sessionId,instanceId:'engine',scopeVersion:1,scopeId:'scope1',projectId:'project1'},args={...pins,callId:'read1',arguments:{id:'Example::Body/body:common'}};
 await fails('workspace_read',args,'scope_changed');
 const scope={id:'scope1',projectId:'project1',node:'Example::Body/body:common',readOnly:true};
 const toolRows=['workspace_list','workspace_read','workspace_inspect','workspace_stage','workspace_create','workspace_changes'].map(name=>({name,parameters:{type:'object'}}));
 const pulse=(version,current=scope)=>api('pulse',{sessionId,instanceId:'engine',scopeVersion:version,scope:current,tools:current?toolRows:[]});
 await pulse(1);assert.equal((await mcp('confectory_engines')).engines[0].scope.readOnly,true);
 await fails('workspace_stage',{...args,callId:'write'},'read_only');
 const queued=await mcp('workspace_read',args);assert.equal(queued.status,'queued');
 assert.equal((await mcp('workspace_read',{arguments:{id:'Example::Body/body:common'},callId:'read1',...pins})).requestId,queued.requestId);
 await fails('workspace_read',{...args,arguments:{id:'foreign'}},'call_id_reused');
 const job=(await api('claim',{sessionId})).job;assert.equal(job.id,queued.requestId);assert.equal((await api('claim',{sessionId})).job,null);
 const completed={sessionId,requestId:job.id,claim:job.claim,result:{value:{text:'owned source',revision:7,textHash:'hash'}}};
 await api('complete',completed,'owner-b',403);await api('complete',{...completed,claim:'wrong'},'owner-a',409);
 await api('complete',completed);assert.equal((await api('complete',completed)).duplicate,true);
 await api('complete',{...completed,result:{value:'changed'}},'owner-a',409);
 assert.equal((await mcp('confectory_result',{sessionId,requestId:job.id})).result.value.revision,7);
 await fails('confectory_result',{sessionId,requestId:job.id},'owner_mismatch','owner-b');
 const stale=await mcp('workspace_read',{...args,callId:'stale'});await pulse(2,null);
 await fails('confectory_result',{sessionId,requestId:queued.requestId},'scope_changed');
 await api('complete',completed,'owner-a',409);assert.equal((await api('claim',{sessionId})).job,null);
 scope.readOnly=false;scope.id='scope2';await pulse(3);pins={...pins,scopeId:'scope2',scopeVersion:3};
 const edit=await mcp('workspace_stage',{...pins,callId:'stage-once',arguments:{id:'body',text:'draft',expectedRevision:7,expectedHash:'hash'}});
 const editJob=(await api('claim',{sessionId})).job;assert.equal(editJob.id,edit.requestId);
 await mcp('confectory_cancel',{sessionId,requestId:edit.requestId});
 await api('complete',{sessionId,requestId:edit.requestId,claim:editJob.claim,result:{value:{applied:true}}},'owner-a',409);
 assert.equal((await mcp('confectory_result',{sessionId,requestId:edit.requestId})).status,'cancelled');
 const durable=await mcp('workspace_read',{...pins,callId:'durable',arguments:{id:'body'}});
 db.raw.close();db=new D1(path);worker=(await import('../worker/index.js?cold')).default;
 const cold=(await api('claim',{sessionId})).job;assert.equal(cold.id,durable.requestId);assert.equal(cold.scopeVersion,3);
 // Lease expiry reports an uncertain outcome instead of executing the claim again.
 now+=91000;await pulse(3);assert.equal((await api('claim',{sessionId})).job,null);
 assert.equal((await mcp('confectory_result',{sessionId,requestId:cold.id})).status,'interrupted');
 await api('complete',{sessionId,requestId:cold.id,claim:cold.claim,result:{value:{applied:true}}},'owner-a',409);
 assert.equal((await mcp('workspace_read',{...pins,callId:'durable',arguments:{id:'body'}})).requestId,cold.id);
 // Re-pairing the same engine retires every old queue and starts without a grant.
 const previous=sessionId;pair=await api('pair',{instanceId:'engine'});sessionId=pair.sessionId;assert.notEqual(sessionId,previous);
 await api('claim',{sessionId:previous},'owner-a',410);assert.equal((await mcp('confectory_engines')).engines[0].scope,null);
 now+=16000;await fails('workspace_read',{...pins,sessionId},'engine_offline');
 now=pair.expiresAt+1;await api('pulse',{sessionId,instanceId:'engine',scopeVersion:0,scope:null,tools:[]},'owner-a',410);
 assert.equal((await mcp('confectory_engines')).engines.length,0);
});
