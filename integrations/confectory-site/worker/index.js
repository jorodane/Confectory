import { bridgePage } from './bridge-page.js';

const PROTOCOL = 'confectory.editor.v1';
const WORKSPACE = new Set(['workspace_list','workspace_read','workspace_inspect','workspace_stage','workspace_create','workspace_changes']);
const SESSION_MS = 30 * 60 * 1000, LIVE_MS = 15000, JOB_MS = 90000;
const json = (value, status=200) => new Response(JSON.stringify(value), {status, headers:{'content-type':'application/json; charset=utf-8','cache-control':'no-store','x-content-type-options':'nosniff'}});
class Refused extends Error { constructor(code, status=409){super(code);this.status=status;} }
const refuse = (code, status) => { throw new Refused(code,status); };
const id = x => typeof x === 'string' && /^[a-zA-Z0-9_-]{1,128}$/.test(x);
const object = x => x && typeof x === 'object' && !Array.isArray(x);
const uid = () => crypto.randomUUID().replaceAll('-','');
const parse = x => x === null || x === undefined ? null : JSON.parse(x);
function canonical(x){if(Array.isArray(x))return '['+x.map(canonical).join(',')+']';if(object(x))return '{'+Object.keys(x).sort().map(k=>JSON.stringify(k)+':'+canonical(x[k])).join(',')+'}';return JSON.stringify(x);}
async function digest(x){return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(canonical(x)))),x=>x.toString(16).padStart(2,'0')).join('');}
async function body(request){
  const reader=request.body?.getReader(); if(!reader)refuse('body_required',400);
  const chunks=[];let size=0;
  try{while(true){const part=await reader.read();if(part.done)break;size+=part.value.length;if(size>1572864){await reader.cancel();refuse('payload_budget',413);}chunks.push(part.value);}}
  finally{reader.releaseLock();}
  const bytes=new Uint8Array(size);let at=0;for(const part of chunks){bytes.set(part,at);at+=part.length;}
  try{const value=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bytes));if(!object(value))refuse('invalid_request',400);return value;}catch(e){if(e instanceof Refused)throw e;refuse('invalid_json',400);}
}
const stmt=(db,sql,...args)=>db.prepare(sql).bind(...args);
async function session(db,owner,sid,now,live=true){
  if(!id(sid))refuse('invalid_session',400);
  const row=await stmt(db,'SELECT * FROM sessions WHERE id = ?',sid).first();
  if(!row)refuse('session_missing',404);if(row.owner!==owner)refuse('owner_mismatch',403);
  if(row.revoked||row.expires<=now)refuse('session_retired',410);
  if(live&&row.heartbeat<=now-LIVE_MS)refuse('engine_offline',409);return row;
}
function scopeMatches(row,args){
  const scope=parse(row.scope);
  if(!scope||row.instance!==args.instanceId||row.scope_version!==args.scopeVersion||scope.id!==args.scopeId||scope.projectId!==args.projectId)refuse('scope_changed');
  return scope;
}
async function retireJobs(db,owner,sid,reason){
  await stmt(db,"UPDATE requests SET status = 'cancelled', result = ? WHERE owner = ? AND session = ? AND status IN ('queued','claimed')",JSON.stringify({error:{code:reason}}),owner,sid).run();
}
async function relay(db,owner,path,input,now){
  if(path==='pair'){
    if(!id(input.instanceId))refuse('invalid_instance',400);
    await db.batch([
      stmt(db,'DELETE FROM requests WHERE owner = ? AND expires < ?',owner,now-3600000),
      stmt(db,'DELETE FROM sessions WHERE owner = ? AND expires < ?',owner,now-3600000),
    ]);
    const count=await stmt(db,'SELECT COUNT(*) AS n FROM sessions WHERE owner = ? AND revoked = 0 AND expires > ? AND instance <> ?',owner,now,input.instanceId).first();
    if(count.n>=16)refuse('connection_budget',429);
    // Every pair starts without a project. An existing connection never donates its grant.
    const sid=uid(),expires=now+SESSION_MS;
    await db.batch([
      stmt(db,"UPDATE requests SET status = 'cancelled', result = ? WHERE owner = ? AND session IN (SELECT id FROM sessions WHERE owner = ? AND instance = ?) AND status IN ('queued','claimed')",JSON.stringify({error:{code:'engine_reconnected'}}),owner,owner,input.instanceId),
      stmt(db,'UPDATE sessions SET revoked = 1, scope = NULL, tools = ? WHERE owner = ? AND instance = ?','[]',owner,input.instanceId),
      stmt(db,'INSERT INTO sessions (id,owner,instance,expires,heartbeat,revoked,scope,tools,scope_version) VALUES (?,?,?,?,?,0,NULL,?,0)',sid,owner,input.instanceId,expires,now,'[]'),
    ]);return {protocol:PROTOCOL,sessionId:sid,expiresAt:expires};
  }
  const s=await session(db,owner,input.sessionId,now,false);
  if(path==='pulse'){
    if(input.instanceId!==s.instance||!Number.isSafeInteger(input.scopeVersion)||input.scopeVersion<0||input.scopeVersion<s.scope_version)refuse('scope_changed');
    let scope=null,tools=[];
    if(input.scope!==null){
      const v=input.scope;if(!object(v)||!id(v.id)||!id(v.projectId)||typeof v.readOnly!=='boolean'||typeof v.node!=='string'||v.node.length>1024)refuse('invalid_scope',400);
      // Titles and filesystem paths are unnecessary for the remote grant.
      scope={id:v.id,projectId:v.projectId,node:v.node,readOnly:v.readOnly};
      if(!Array.isArray(input.tools)||input.tools.length>6)refuse('invalid_tools',400);
      tools=input.tools.filter(t=>WORKSPACE.has(t.name)&&object(t.parameters)).map(t=>({name:t.name,description:String(t.description??'').slice(0,2048),parameters:t.parameters}));
      if(v.readOnly)tools=tools.filter(t=>!['workspace_stage','workspace_create'].includes(t.name));
    }
    const encoded=JSON.stringify(scope);
    if(input.scopeVersion===s.scope_version&&encoded!==(s.scope??'null'))refuse('scope_changed');
    if(input.scopeVersion!==s.scope_version||encoded!==(s.scope??'null'))await retireJobs(db,owner,s.id,'scope_changed');
    const updated=await stmt(db,'UPDATE sessions SET heartbeat = ?, scope = ?, tools = ?, scope_version = ? WHERE id = ? AND owner = ? AND revoked = 0 AND expires > ? AND scope_version <= ?',now,scope?encoded:null,JSON.stringify(tools),input.scopeVersion,s.id,owner,now,input.scopeVersion).run();
    if(!updated.meta.changes)refuse('session_retired',410);return {ok:true,expiresAt:s.expires};
  }
  if(path==='close'){
    await stmt(db,'UPDATE sessions SET revoked = 1, scope = NULL, tools = ? WHERE id = ? AND owner = ?','[]',s.id,owner).run();
    await retireJobs(db,owner,s.id,'session_retired');return {ok:true};
  }
  if(s.heartbeat<=now-LIVE_MS)refuse('engine_offline');
  if(path==='claim'){
    // A crashed claim becomes uncertain, never automatically executable again.
    await stmt(db,"UPDATE requests SET status = 'interrupted', result = ? WHERE owner = ? AND session = ? AND ((status = 'claimed' AND lease <= ?) OR (status = 'queued' AND expires <= ?))",JSON.stringify({error:{code:'execution_interrupted'}}),owner,s.id,now,now).run();
    const claim=uid();
    const job=await stmt(db,"UPDATE requests SET status = 'claimed', claim = ?, lease = ? WHERE id = (SELECT id FROM requests WHERE owner = ? AND session = ? AND status = 'queued' AND expires > ? ORDER BY created, id LIMIT 1) AND status = 'queued' RETURNING *",claim,now+JOB_MS,owner,s.id,now).first();
    if(!job)return {job:null};
    try{scopeMatches(s,{instanceId:job.instance,scopeVersion:job.scope_version,scopeId:job.scope_id,projectId:job.project_id});}catch(e){await retireJobs(db,owner,s.id,'scope_changed');throw e;}
    return {job:{id:job.id,claim,callId:job.call_id,name:job.name,arguments:parse(job.arguments),instanceId:job.instance,scopeVersion:job.scope_version,scopeId:job.scope_id,projectId:job.project_id}};
  }
  if(path==='complete'){
    if(!id(input.requestId)||!id(input.claim)||!object(input.result))refuse('invalid_result',400);
    const job=await stmt(db,'SELECT * FROM requests WHERE id = ?',input.requestId).first();
    if(!job||job.owner!==owner||job.session!==s.id)refuse('request_refused',403);
    scopeMatches(s,{instanceId:job.instance,scopeVersion:job.scope_version,scopeId:job.scope_id,projectId:job.project_id});
    if(job.claim!==input.claim)refuse('claim_changed');
    const result=JSON.stringify(input.result);if(result.length>1048576)refuse('result_budget',413);
    if(job.status==='completed'){if(result!==job.result)refuse('result_changed');return {ok:true,duplicate:true};}
    const done=await stmt(db,"UPDATE requests SET status = 'completed', result = ? WHERE id = ? AND owner = ? AND status = 'claimed' AND claim = ? AND lease > ? AND expires > ? AND EXISTS (SELECT 1 FROM sessions WHERE sessions.id = requests.session AND sessions.owner = requests.owner AND sessions.revoked = 0 AND sessions.expires > ? AND sessions.scope_version = requests.scope_version AND json_extract(sessions.scope,'$.id') = requests.scope_id)",result,job.id,owner,input.claim,now,now,now).run();
    if(!done.meta.changes)refuse('request_retired');return {ok:true};
  }
  refuse('unknown_route',404);
}
const scopePins={sessionId:{type:'string'},instanceId:{type:'string'},scopeVersion:{type:'integer'},scopeId:{type:'string'},projectId:{type:'string'}};
const pins={...scopePins,callId:{type:'string',pattern:'^[a-zA-Z0-9_-]{1,128}$'},arguments:{type:'object'}};
function permittedTools(s,scope){return parse(s.tools).filter(t=>WORKSPACE.has(t.name)&&object(t.parameters)&&!(scope.readOnly&&['workspace_stage','workspace_create'].includes(t.name)));}
function scopedDefinition(t,s,scope){
  const argumentsSchema=structuredClone(t.parameters);
  // These two engine arguments are injected from the validated transport pins.
  // Retain the original parameters as well as the exact callable relay schema.
  if(object(argumentsSchema.properties)){delete argumentsSchema.properties.projectId;delete argumentsSchema.properties.scopeId;}
  if(Array.isArray(argumentsSchema.required))argumentsSchema.required=argumentsSchema.required.filter(k=>!['projectId','scopeId'].includes(k));
  const properties={...structuredClone(pins),arguments:argumentsSchema};
  for(const [key,value] of Object.entries({sessionId:s.id,instanceId:s.instance,scopeVersion:s.scope_version,scopeId:scope.id,projectId:scope.projectId}))properties[key].enum=[value];
  return {name:t.name,description:t.description,parameters:t.parameters,inputSchema:{type:'object',properties,required:Object.keys(pins),additionalProperties:false}};
}
const tools=[
 {name:'confectory_engines',description:'List this signed-in owner’s live engines and explicitly granted scope. Connection alone grants no project access.',inputSchema:{type:'object',properties:{},additionalProperties:false}},
 {name:'confectory_tools',description:'Fetch the exact permitted workspace definitions for one explicit current grant before calling workspace tools. Each definition includes original engine parameters and a callable relay inputSchema. The transport injects projectId and scopeId into engine arguments; omit them inside arguments.',inputSchema:{type:'object',properties:scopePins,required:Object.keys(scopePins),additionalProperties:false}},
 ...[...WORKSPACE].map(name=>({name,description:'Queue '+name+' for one explicitly identified engine and grant. First fetch its exact inputSchema with confectory_tools. Results are fetched with confectory_result. Editing uses shared drafts; final Review/Confirm stays in the editor.',inputSchema:{type:'object',properties:pins,required:Object.keys(pins),additionalProperties:false}})),
 ...['result','cancel'].map(op=>({name:'confectory_'+op,description:op==='result'?'Read a queued request result. An interrupted edit has an unknown outcome: inspect shared changes before creating a new call.':'Cancel a queued request or discard a running result; applied draft changes are not rolled back.',inputSchema:{type:'object',properties:{sessionId:{type:'string'},requestId:{type:'string'}},required:['sessionId','requestId'],additionalProperties:false}}))
];
async function tool(db,owner,name,args,now){
  if(name==='confectory_engines'){
    const list=await stmt(db,'SELECT id,instance,scope,scope_version,expires FROM sessions WHERE owner = ? AND revoked = 0 AND expires > ? AND heartbeat > ? ORDER BY id',owner,now,now-LIVE_MS).all();
    return {engines:list.results.map(s=>({sessionId:s.id,instanceId:s.instance,scope:parse(s.scope),scopeVersion:s.scope_version,expiresAt:s.expires}))};
  }
  const s=await session(db,owner,args.sessionId,now);
  if(name==='confectory_tools'){
    const scope=scopeMatches(s,args),definitions=permittedTools(s,scope).map(t=>scopedDefinition(t,s,scope));
    const current=await session(db,owner,s.id,Date.now());scopeMatches(current,args);
    if(current.tools!==s.tools)refuse('scope_changed');
    return {tools:definitions};
  }
  if(name==='confectory_result'||name==='confectory_cancel'){
    if(!id(args.requestId))refuse('invalid_request',400);
    let job=await stmt(db,'SELECT * FROM requests WHERE id = ?',args.requestId).first();
    if(!job||job.owner!==owner||job.session!==s.id)refuse('request_refused',403);
    scopeMatches(await session(db,owner,s.id,now),{instanceId:job.instance,scopeVersion:job.scope_version,scopeId:job.scope_id,projectId:job.project_id});
    if(name==='confectory_cancel'){
      await stmt(db,"UPDATE requests SET status = 'cancelled', result = ? WHERE id = ? AND owner = ? AND status IN ('queued','claimed')",JSON.stringify({error:{code:'cancelled'}}),job.id,owner).run();
      job=await stmt(db,'SELECT * FROM requests WHERE id = ?',job.id).first();
    }
    if((job.status==='queued'&&job.expires<=now)||(job.status==='claimed'&&(job.lease<=now||job.expires<=now)))return {requestId:job.id,status:'interrupted',error:{code:'execution_interrupted'}};
    return {requestId:job.id,status:job.status,...(job.result?{result:parse(job.result)}:{})};
  }
  if(!WORKSPACE.has(name))refuse('tool_denied',403);
  const scope=scopeMatches(s,args);if(!id(args.callId)||!object(args.arguments)||Object.hasOwn(args.arguments,'scopeId'))refuse('invalid_arguments',400);
  if(scope.readOnly&&['workspace_stage','workspace_create'].includes(name))refuse('read_only',403);
  if(!permittedTools(s,scope).some(t=>t.name===name))refuse('tool_denied',403);
  const fingerprint=await digest({name,args}),rid=uid();
  const prior=await stmt(db,'SELECT id,fingerprint,status FROM requests WHERE owner = ? AND session = ? AND call_id = ?',owner,s.id,args.callId).first();
  if(prior){if(prior.fingerprint!==fingerprint)refuse('call_id_reused');return {requestId:prior.id,status:prior.status};}
  const count=await stmt(db,'SELECT COUNT(*) AS n FROM requests WHERE owner = ? AND session = ?',owner,s.id).first();if(count.n>=256)refuse('request_budget',429);
  await stmt(db,"INSERT INTO requests (id,owner,session,instance,scope_version,scope_id,project_id,name,arguments,call_id,fingerprint,status,created,expires) SELECT ?,?,?,?,?,?,?,?,?,?,?,'queued',?,? WHERE EXISTS (SELECT 1 FROM sessions WHERE id = ? AND owner = ? AND revoked = 0 AND expires > ? AND heartbeat > ? AND scope_version = ? AND json_extract(scope,'$.id') = ?) ON CONFLICT(owner,session,call_id) DO NOTHING",rid,owner,s.id,s.instance,s.scope_version,scope.id,scope.projectId,name,JSON.stringify(args.arguments),args.callId,fingerprint,now,now+JOB_MS,s.id,owner,now,now-LIVE_MS,s.scope_version,scope.id).run();
  const job=await stmt(db,'SELECT id,fingerprint,status FROM requests WHERE owner = ? AND session = ? AND call_id = ?',owner,s.id,args.callId).first();
  if(!job)refuse('scope_changed');
  if(job.fingerprint!==fingerprint)refuse('call_id_reused');return {requestId:job.id,status:job.status};
}
async function mcp(db,owner,input,now){
  const reply=result=>({jsonrpc:'2.0',id:input.id,result});
  if(input.jsonrpc!=='2.0'||typeof input.method!=='string')return json({jsonrpc:'2.0',id:input.id??null,error:{code:-32600,message:'Invalid Request'}},400);
  if(input.method.startsWith('notifications/'))return new Response(null,{status:202});
  if(input.method==='server/discover')return json(reply({name:'Confectory Connect',version:'0.1.0',supportedVersions:['2026-07-28','2025-03-26'],capabilities:{tools:{listChanged:false}}}));
  if(input.method==='initialize')return json(reply({protocolVersion:input.params?.protocolVersion==='2026-07-28'?'2026-07-28':'2025-03-26',capabilities:{tools:{listChanged:false}},serverInfo:{name:'Confectory Connect',version:'0.1.0'}}));
  if(input.method==='ping')return json(reply({}));
  if(input.method==='tools/list')return json(reply({tools}));
  if(input.method!=='tools/call')return json({jsonrpc:'2.0',id:input.id,error:{code:-32601,message:'Method not found'}});
  try{const result=await tool(db,owner,input.params?.name,input.params?.arguments??{},now);return json(reply({content:[{type:'text',text:JSON.stringify(result)}]}));}
  catch(e){if(!(e instanceof Refused))throw e;return json(reply({isError:true,content:[{type:'text',text:JSON.stringify({error:{code:e.message}})}]}));}
}
export default {
 async fetch(request,env){
  try{
   const url=new URL(request.url),owner=request.headers.get('oai-authenticated-user-id');
   if(!owner||owner.length>512)return json({error:{code:'authentication_required'}},401);
   if(request.method==='GET'&&(url.pathname==='/'||url.pathname==='/editor-bridge'))return new Response(bridgePage,{headers:{'content-type':'text/html; charset=utf-8','cache-control':'no-store','content-security-policy':"default-src 'none'; script-src 'nonce-confectory-bridge'; style-src 'nonce-confectory-bridge'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'",'x-content-type-options':'nosniff','referrer-policy':'no-referrer'}});
   if(request.method!=='POST')return json({error:{code:'method_not_allowed'}},405);
   if(!env.DB)return json({error:{code:'storage_unavailable'}},503);
   if(url.pathname==='/mcp')return await mcp(env.DB,owner,await body(request),Date.now());
   if(!url.pathname.startsWith('/api/'))return json({error:{code:'not_found'}},404);
   // API cookies alone are insufficient for a cross-origin mutation.
   if(request.headers.get('origin')!==url.origin||request.headers.get('content-type')?.split(';')[0]!=='application/json')refuse('origin_refused',403);
   return json(await relay(env.DB,owner,url.pathname.slice(5),await body(request),Date.now()));
  }catch(e){if(e instanceof Refused)return json({error:{code:e.message}},e.status);return json({error:{code:'internal_error'}},500);}
 }
};
