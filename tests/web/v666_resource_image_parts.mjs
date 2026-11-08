import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {webcrypto,createHash} from 'node:crypto';
import {resolve} from 'node:path';
if(!globalThis.crypto)Object.defineProperty(globalThis,'crypto',{value:webcrypto});
const {readResourceImageParts:read}=await import('data:text/javascript;base64,'+readFileSync(resolve(process.argv[2],'examples/editor-home/ui/resource-image-parts.js')).toString('base64'));
const digest=b=>createHash('sha256').update(b).digest('hex'),bytes=Buffer.alloc(4194297);let random=713;
for(let n=0;n<bytes.length;n++){random^=random<<13;random^=random>>>17;random^=random<<5;bytes[n]=random&255;}
const header={status:'ready',project:'a'.repeat(32),item:{id:'b'.repeat(32),name:'large.png',kind:'image',size:bytes.length,hash:digest(bytes),contentGeneration:'d'.repeat(64)},displayRevision:'e'.repeat(64),encoding:'unavailable',reason:'resource_preview_file_budget',imagePreview:{encoding:'base64url-image-parts-v1',partBytes:1048576,total:bytes.length}};
function reply(q){const part=bytes.subarray(q.part*1048576,(q.part+1)*1048576);return {status:'ready',project:header.project,item:structuredClone(header.item),displayRevision:header.displayRevision,encoding:'base64url-image-part-v1',data:part.toString('base64').replaceAll('+','-').replaceAll('/','_'),preview:{part:q.part,offset:q.part*1048576,bytes:part.length,total:bytes.length,sha256:digest(part)}};}
const calls=[];assert.deepEqual(Buffer.from(await read(header,async q=>{calls.push(q);return reply(q);},()=>true)),bytes);assert.deepEqual(calls.map(q=>q.part),[0,1,2,3]);assert(calls.every(q=>q.id===header.item.id&&q.hash===header.item.hash&&q.generation===header.item.contentGeneration&&q.revision===header.displayRevision));
let rejected=0;
for(const change of [r=>r.project='f'.repeat(32),r=>r.item.id='f'.repeat(32),r=>r.item.hash='f'.repeat(64),r=>r.item.contentGeneration='f'.repeat(64),r=>r.item.name='other.png',r=>r.displayRevision='f'.repeat(64),r=>r.preview.part++,r=>r.preview.offset++,r=>r.preview.bytes--,r=>r.preview.total--,r=>r.preview.sha256='f'.repeat(64),r=>r.preview.extra=true,r=>r.encoding='base64url',r=>r.reason='unavailable',r=>r.data=r.data.slice(0,-1),r=>r.data=r.data.replace(/=+$/,''),r=>r.data=' '+r.data,r=>r.data=(r.data[0]==='A'?'B':'A')+r.data.slice(1)]){
 let count=0;await assert.rejects(read(header,async q=>{count++;const r=reply(q);change(r);return r;},()=>true));assert.equal(count,1);rejected++;
}
for(const change of [h=>h.imagePreview=[],h=>h.imagePreview.extra=true,h=>h.item.size=1048576,h=>h.item.size=4194305,h=>h.item.kind='document',h=>h.preview={encoding:'base64url-prefix-v1'},h=>h.data='',h=>h.item.hash=[]]){
 const h=structuredClone(header);change(h);let count=0;await assert.rejects(read(h,async()=>{count++;},()=>true));assert.equal(count,0);rejected++;
}
let count=0,active=true;await assert.rejects(read(header,async q=>{count++;active=false;return reply(q);},()=>active));assert.equal(count,1);
count=0;await assert.rejects(read(header,async()=>{count++;},()=>false));assert.equal(count,0);
count=0;await assert.rejects(read(header,async q=>{count++;const r=reply(q);if(q.part===1)r.item.contentGeneration='f'.repeat(64);return r;},()=>true));assert.equal(count,2);
count=0;await assert.rejects(read(header,async q=>{count++;const r=reply(q);if(q.part===2){const b=Buffer.from(bytes.subarray(2*1048576,3*1048576));b[0]^=1;r.data=b.toString('base64').replaceAll('+','-').replaceAll('/','_');r.preview.sha256=digest(b);}return r;},()=>true));assert.equal(count,4); // matching part SHA cannot bypass whole SHA
count=0;assert.deepEqual(Buffer.from(await read(header,async q=>{count++;if(count===1)throw Error('busy');return reply(q);},()=>true)),bytes);assert.equal(count,5);
count=0;await assert.rejects(read(header,async()=>{count++;throw Error('busy');},()=>true));assert.equal(count,3);
count=0;await assert.rejects(read(header,async()=>{count++;throw Error('observation_failed');},()=>true));assert.equal(count,1);
console.log('PASS whole raster assembly, short final part, pinned ordered observations, '+rejected+' malformed/stale/tampered refusals, whole SHA, retirement and bounded busy-only retries');
