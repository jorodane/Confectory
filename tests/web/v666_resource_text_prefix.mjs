import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {webcrypto,createHash} from 'node:crypto';
import {resolve} from 'node:path';
if(!globalThis.crypto)Object.defineProperty(globalThis,'crypto',{value:webcrypto});
const {decodeResourceTextPrefix:decode}=await import('data:text/javascript;base64,'+readFileSync(resolve(process.argv[2],'examples/editor-home/ui/resource-text-prefix.js')).toString('base64'));
const bytes=Buffer.alloc(1048576);let random=713;
for(let n=0;n<bytes.length;n++){random^=random<<13;random^=random>>>17;random^=random<<5;bytes[n]=random&255;}
const header={status:'ready',project:'a'.repeat(32),item:{id:'b'.repeat(32),name:'large.txt',size:4194304,hash:'c'.repeat(64),contentGeneration:'d'.repeat(64)},displayRevision:'e'.repeat(64),encoding:'unavailable',reason:'resource_preview_file_budget',preview:{encoding:'base64url-prefix-v1',bytes:1048576,total:4194304}};
const reply={status:'ready',project:header.project,item:structuredClone(header.item),displayRevision:header.displayRevision,encoding:'base64url-prefix-v1',data:bytes.toString('base64').replaceAll('+','-').replaceAll('/','_'),preview:{bytes:1048576,total:4194304,sha256:createHash('sha256').update(bytes).digest('hex')}};
assert.deepEqual(Buffer.from(await decode(header,reply)),bytes);
const reorder=structuredClone(reply);reorder.item=Object.fromEntries(Object.entries(reorder.item).reverse());assert.deepEqual(Buffer.from(await decode(header,reorder)),bytes);
let rejected=0;
for(const change of [r=>r.project='f'.repeat(32),r=>r.item.id='f'.repeat(32),r=>r.item.hash='f'.repeat(64),r=>r.item.contentGeneration='f'.repeat(64),r=>r.item.name='renamed.txt',r=>r.displayRevision='f'.repeat(64),r=>r.preview.total--,r=>r.preview.bytes--,r=>r.preview.sha256='f'.repeat(64),r=>r.preview.extra=true,r=>r.encoding='base64url',r=>r.reason='unavailable',r=>r.data=r.data.slice(0,-1),r=>r.data=r.data.trimEnd().replace(/=+$/,''),r=>r.data=' '+r.data,r=>r.data=(r.data[0]==='A'?'B':'A')+r.data.slice(1)]){
 const r=structuredClone(reply);change(r);await assert.rejects(decode(header,r));rejected++;
}
for(const change of [h=>h.preview=[],h=>h.preview.bytes='1048576',h=>h.preview.extra=true,h=>h.item.size=1048576,h=>h.item.size=4194305,h=>h.item.hash=[],h=>h.data='',h=>h.reason='other']){
 const h=structuredClone(header);change(h);await assert.rejects(decode(h,reply));rejected++;
}
console.log('PASS exact prefix bytes/SHA, pinned identity, canonical base64 and '+rejected+' malformed/stale/tampered rejections; whole-file hash remains native responsibility');
