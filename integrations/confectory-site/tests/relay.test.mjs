import {test} from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {readFileSync,mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import app from '../worker/index.js';

class D1 {
 constructor(path){this.raw=new DatabaseSync(path);}
 prepare(sql){const db=this,raw=this.raw;return {bind(...args){const statement=raw.prepare(sql);return {
  async first(){db.beforeFirst?.(sql,args);return statement.get(...args)??null;},
  async all(){return {results:statement.all(...args)};},
  async run(){const result=statement.run(...args);return {meta:{changes:Number(result.changes)}};}
 };}};}
 async batch(statements){this.raw.exec('BEGIN');try{const result=[];for(const statement of statements)result.push(await statement.run());this.raw.exec('COMMIT');return result;}catch(e){this.raw.exec('ROLLBACK');throw e;}}
}
test('private scoped tool schemas, persistent relay boundaries, duplicate calls, cancellation, expiry and cold storage',async t=>{
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
 const definitions=(await request('/mcp',{jsonrpc:'2.0',id:2,method:'tools/list'}))[1].result.tools;assert.equal(definitions.length,14);assert(definitions.some(t=>t.name==='confectory_tools'));assert(!JSON.stringify(definitions).includes('owner-a'));assert(!definitions.some(t=>/shell|confirm|execute/.test(t.name)));
 let pair=await api('pair',{instanceId:'engine'}),sessionId=pair.sessionId;
 const engine=(await mcp('confectory_engines')).engines[0];assert.equal(engine.scope,null);assert.equal(engine.scopeVersion,0);
 await api('pulse',{sessionId,instanceId:'engine',scopeVersion:0,scope:null,tools:[]},'owner-b',403);
 let pins={sessionId,instanceId:'engine',scopeVersion:1,scopeId:'scope1',projectId:'project1'},args={...pins,callId:'read1',arguments:{id:'Example::Body/body:common'}};
 await fails('workspace_read',args,'scope_changed');
 await fails('confectory_tools',pins,'scope_changed');
 const scope={id:'scope1',projectId:'project1',node:'Example::Body/body:common',readOnly:true};
 const toolRows=['workspace_list','workspace_read','workspace_inspect','workspace_stage','workspace_create','workspace_changes'].map(name=>{
  const properties={projectId:{type:'string',enum:['project1']},scopeId:{type:'string',enum:['scope1']}},required=['projectId','scopeId'];
  const field=(key,schema)=>{properties[key]=schema;required.push(key);};
  if(['workspace_read','workspace_inspect','workspace_stage','workspace_create'].includes(name))field('id',{type:'string',enum:[scope.node]});
  if(name==='workspace_list')field('query',{type:'string'});
  if(name==='workspace_stage'){field('text',{type:'string'});field('expectedRevision',{type:'integer',minimum:0});field('expectedHash',{type:'string'});}
  if(name==='workspace_create')field('kind',{type:'string',enum:['object','function']});
  return {name,description:'Exact '+name+' definition',parameters:{type:'object',properties,required,additionalProperties:false}};
 });
 const pulse=(version,current=scope)=>{if(current)for(const row of toolRows){row.parameters.properties.scopeId.enum=[current.id];row.parameters.properties.projectId.enum=[current.projectId];}return api('pulse',{sessionId,instanceId:'engine',scopeVersion:version,scope:current,tools:current?toolRows:[]});};
 await pulse(1);assert.equal((await mcp('confectory_engines')).engines[0].scope.readOnly,true);
 const scoped=(await mcp('confectory_tools',pins)).tools;assert.deepEqual(scoped.map(t=>t.name),['workspace_list','workspace_read','workspace_inspect','workspace_changes']);
 const readDefinition=scoped.find(t=>t.name==='workspace_read'),originalDefinition=toolRows.find(t=>t.name==='workspace_read');
 assert.equal(readDefinition.description,originalDefinition.description);assert.deepEqual(readDefinition.parameters,originalDefinition.parameters);
 const relaySchema=readDefinition.inputSchema;assert.deepEqual(relaySchema.properties.arguments,{type:'object',properties:{id:{type:'string',enum:[scope.node]}},required:['id'],additionalProperties:false});
 for(const [key,value] of Object.entries(pins))assert.deepEqual(relaySchema.properties[key].enum,[value]);
 assert.equal(relaySchema.additionalProperties,false);assert.deepEqual(relaySchema.required,[...Object.keys(pins),'callId','arguments']);
 // Returned callable schemas supply a valid request without duplicated engine pins.
 const discoveredArgs=Object.fromEntries(Object.entries(relaySchema.properties).filter(([key])=>Object.hasOwn(pins,key)).map(([key,value])=>[key,value.enum[0]]));
 discoveredArgs.callId='read1';discoveredArgs.arguments={id:relaySchema.properties.arguments.properties.id.enum[0]};assert.deepEqual(discoveredArgs,args);
 assert(!JSON.stringify(scoped).includes('expectedHash'));assert(!JSON.stringify(scoped).includes('workspace_stage'));assert(!JSON.stringify(scoped).includes('workspace_create'));
 // A same-generation permission update between pre/post reads cannot leak the old schema.
 const storedTools=db.raw.prepare('SELECT tools FROM sessions WHERE id = ?').get(sessionId).tools;let schemaReads=0;
 db.beforeFirst=(sql,values)=>{if(sql==='SELECT * FROM sessions WHERE id = ?'&&values[0]===sessionId&&++schemaReads===2)db.raw.prepare('UPDATE sessions SET tools = ? WHERE id = ?').run('[]',sessionId);};
 try{await fails('confectory_tools',pins,'scope_changed');}finally{db.beforeFirst=null;db.raw.prepare('UPDATE sessions SET tools = ? WHERE id = ?').run(storedTools,sessionId);}
 // Static discovery stays free of node/project/session schema values.
 const publicDefinitions=(await request('/mcp',{jsonrpc:'2.0',id:3,method:'tools/list'}))[1].result.tools;
 assert(!JSON.stringify(publicDefinitions).includes(scope.node));assert(!JSON.stringify(publicDefinitions).includes(sessionId));
 for(const wrong of [{instanceId:'foreign-engine'},{scopeVersion:0},{scopeId:'foreign-scope'},{projectId:'foreign-project'}])await fails('confectory_tools',{...pins,...wrong},'scope_changed');
 await fails('confectory_tools',pins,'owner_mismatch','owner-b');
 const foreign=await api('pair',{instanceId:'foreign-engine'},'owner-b');
 await api('pulse',{sessionId:foreign.sessionId,instanceId:'foreign-engine',scopeVersion:1,scope:{...scope,id:'foreign-scope',projectId:'foreign-project',node:'Foreign::PrivateNode'},tools:[{name:'workspace_read',description:'FOREIGN_PRIVATE_SCHEMA',parameters:{type:'object',properties:{foreignSecret:{type:'string'}}}},{name:'shell',description:'DENIED_TOOL_METADATA',parameters:{type:'object'}}]},'owner-b');
 const foreignPins={sessionId:foreign.sessionId,instanceId:'foreign-engine',scopeVersion:1,scopeId:'foreign-scope',projectId:'foreign-project'};
 await fails('confectory_tools',foreignPins,'owner_mismatch');
 const foreignTools=(await mcp('confectory_tools',foreignPins,'owner-b')).tools;assert.deepEqual(foreignTools.map(t=>t.name),['workspace_read']);assert(!JSON.stringify(foreignTools).includes('DENIED_TOOL_METADATA'));
 assert(!JSON.stringify(await mcp('confectory_tools',pins)).includes('FOREIGN_PRIVATE_SCHEMA'));
 await fails('workspace_stage',{...args,callId:'write'},'read_only');
 const queued=await mcp('workspace_read',discoveredArgs);assert.equal(queued.status,'queued');
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
 await fails('confectory_tools',pins,'scope_changed');await fails('confectory_tools',{...pins,scopeVersion:2},'scope_changed');
 await fails('confectory_result',{sessionId,requestId:queued.requestId},'scope_changed');
 await api('complete',completed,'owner-a',409);assert.equal((await api('claim',{sessionId})).job,null);
 scope.readOnly=false;scope.id='scope2';await pulse(3);pins={...pins,scopeId:'scope2',scopeVersion:3};
 const writable=(await mcp('confectory_tools',pins)).tools;assert.equal(writable.length,6);
 const stage=writable.find(t=>t.name==='workspace_stage');assert.deepEqual(stage.parameters,toolRows.find(t=>t.name==='workspace_stage').parameters);
 assert.deepEqual(stage.inputSchema.properties.arguments.required,['id','text','expectedRevision','expectedHash']);
 assert.deepEqual(stage.inputSchema.properties.arguments.properties.expectedRevision,{type:'integer',minimum:0});
 assert.deepEqual(writable.find(t=>t.name==='workspace_create').inputSchema.properties.arguments.properties.kind.enum,['object','function']);
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
 await fails('confectory_tools',{...pins,sessionId:previous},'session_retired');await fails('confectory_tools',{...pins,sessionId},'scope_changed');
 await api('claim',{sessionId:previous},'owner-a',410);assert.equal((await mcp('confectory_engines')).engines[0].scope,null);
 now+=16000;await fails('workspace_read',{...pins,sessionId},'engine_offline');await fails('confectory_tools',{...pins,sessionId},'engine_offline');
 now=pair.expiresAt+1;await api('pulse',{sessionId,instanceId:'engine',scopeVersion:0,scope:null,tools:[]},'owner-a',410);
 await fails('confectory_tools',{...pins,sessionId},'session_retired');
 assert.equal((await mcp('confectory_engines')).engines.length,0);
});

test('engine creation proposals without a project retain identity, idempotency, cancellation and expiry',async t=>{
 const folder=mkdtempSync(join(tmpdir(),'confectory-engine-creation-')),db=new D1(join(folder,'state.sqlite'));let now=1780000000000;
 t.mock.method(Date,'now',()=>now);t.after(()=>{db.raw.close();rmSync(folder,{recursive:true});});db.raw.exec(readFileSync(new URL('../drizzle/0000_demonic_tempest.sql',import.meta.url),'utf8'));
 const origin='https://confectory-connect.jorodane.chatgpt.site';
 async function request(path,value,owner='owner-a'){const r=await app.fetch(new Request(origin+path,{method:'POST',headers:{'content-type':'application/json',origin,'oai-authenticated-user-id':owner},body:JSON.stringify(value)}),{DB:db});return [r.status,await r.json()];}
 async function api(action,value,owner='owner-a',status=200){const [actual,result]=await request('/api/'+action,value,owner);assert.equal(actual,status,JSON.stringify(result));return result;}
 async function mcp(name,args={},owner='owner-a'){const [status,result]=await request('/mcp',{jsonrpc:'2.0',id:'owned',method:'tools/call',params:{name,arguments:args}},owner);assert.equal(status,200);return JSON.parse(result.result.content[0].text);}
 const definitions=['engine_project_options','engine_project_propose','engine_project_status'].map(name=>({name,description:'Engine-owned creation fixture',parameters:{type:'object',properties:{},additionalProperties:false}}));
 const pair=await api('pair',{instanceId:'engine-a'}),sessionId=pair.sessionId,pins={sessionId,instanceId:'engine-a'};
 await api('pulse',{sessionId,instanceId:'engine-a',scopeVersion:0,scope:null,tools:[],engineTools:definitions});
 assert.equal((await mcp('confectory_engines')).engines[0].scope,null);const discovered=await mcp('confectory_engine_tools',pins);assert.equal(discovered.tools.length,3);assert(discovered.tools.every(t=>!Object.hasOwn(t.inputSchema.properties,'projectId')));
 const proposal={title:'New project',description:'Discuss before creating',intent:'User explicitly asked for a creation proposal',templateId:'empty-projectpack',targetId:'dotnet'},args={...pins,callId:'proposal-1',arguments:proposal};
 assert.equal((await mcp('workspace_read',{...pins,scopeVersion:0,scopeId:'',projectId:'',callId:'bad',arguments:{id:'existing'}})).error.code,'scope_changed');
 assert.equal((await mcp('engine_project_propose',{...args,instanceId:'engine-b'})).error.code,'engine_changed');assert.equal((await mcp('engine_project_propose',args,'owner-b')).error.code,'owner_mismatch');
 for(const invalid of [{...args,arguments:{...proposal,directory:'/arbitrary'}},{...args,arguments:{...proposal,intent:''}},{...args,scopeId:'injected'}])assert.equal((await mcp('engine_project_propose',invalid)).error.code,'invalid_arguments');
 const queued=await mcp('engine_project_propose',args);assert(queued.requestId);assert.equal((await mcp('engine_project_propose',args)).requestId,queued.requestId);assert.equal((await mcp('engine_project_propose',{...args,arguments:{...proposal,title:'changed'}})).error.code,'call_id_reused');
 // Project grant changes cannot transform or retire an engine-level request.
 await api('pulse',{sessionId,instanceId:'engine-a',scopeVersion:1,scope:{id:'scope',projectId:'project',node:'',readOnly:true},tools:[],engineTools:definitions});await api('pulse',{sessionId,instanceId:'engine-a',scopeVersion:2,scope:null,tools:[],engineTools:definitions});
 const job=(await api('claim',{sessionId})).job;assert.equal(job.name,'engine_project_propose');assert.equal(job.scopeId,'');assert.equal(job.projectId,'');assert.equal(job.scopeVersion,0);assert.deepEqual(job.arguments,proposal);
 const result={value:{id:'a'.repeat(32),status:'pending',projectId:null,projectAccessGranted:false}};await api('complete',{sessionId,requestId:job.id,claim:job.claim,result},'owner-b',403);await api('complete',{sessionId,requestId:job.id,claim:job.claim,result});
 const receipt=await mcp('confectory_result',{sessionId,requestId:job.id});assert.equal(receipt.status,'completed');assert.equal(receipt.result.value.projectAccessGranted,false);assert.equal((await mcp('engine_project_confirm',{...pins,callId:'never',arguments:{}})).error.code,'tool_denied');
 const cancelled=await mcp('engine_project_options',{...pins,callId:'options',arguments:{}});await mcp('confectory_cancel',{sessionId,requestId:cancelled.requestId});assert.equal((await mcp('confectory_result',{sessionId,requestId:cancelled.requestId})).status,'cancelled');assert.equal((await api('claim',{sessionId})).job,null);
 const interrupted=await mcp('engine_project_options',{...pins,callId:'interrupted',arguments:{}});await api('claim',{sessionId});now+=90001;await api('pulse',{sessionId,instanceId:'engine-a',scopeVersion:2,scope:null,tools:[],engineTools:definitions});assert.equal((await mcp('confectory_result',{sessionId,requestId:interrupted.requestId})).status,'interrupted');assert.equal((await api('claim',{sessionId})).job,null);
 await api('close',{sessionId});assert.equal((await mcp('engine_project_options',{...pins,callId:'closed',arguments:{}})).error.code,'session_retired');const next=await api('pair',{instanceId:'engine-a'});assert.equal((await mcp('confectory_result',{sessionId:next.sessionId,requestId:job.id})).error.code,'request_refused');
});
