import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {deflateRawSync} from 'node:zlib';
const root=process.argv[2],{officeDirectory,extractOfficeFiles,officeCRC}=await import(pathToFileURL(path.join(root,'examples/editor-home/ui/resource-office-zip.js')));
const encoder=new TextEncoder(),text=encoder.encode('actual UTF8 원본\r\n<script>literal only</script>');
assert.equal(officeCRC(encoder.encode('123456789')),0xcbf43926);
function zip(rows,{descriptor=false}={}){
 const locals=[],central=[];let offset=0;
 for(const [name,value,method=8]of rows){const data=typeof value==='string'?encoder.encode(value):value,rawName=Buffer.from(name),packed=method===8?deflateRawSync(data):Buffer.from(data),crc=officeCRC(data),flags=descriptor?8:0,local=Buffer.alloc(30+rawName.length),head=Buffer.alloc(46+rawName.length);local.writeUInt32LE(0x04034b50);local.writeUInt16LE(20,4);local.writeUInt16LE(flags,6);local.writeUInt16LE(method,8);local.writeUInt16LE(rawName.length,26);rawName.copy(local,30);if(!descriptor){local.writeUInt32LE(crc,14);local.writeUInt32LE(packed.length,18);local.writeUInt32LE(data.length,22);}head.writeUInt32LE(0x02014b50);head.writeUInt16LE(20,6);head.writeUInt16LE(flags,8);head.writeUInt16LE(method,10);head.writeUInt32LE(crc,16);head.writeUInt32LE(packed.length,20);head.writeUInt32LE(data.length,24);head.writeUInt16LE(rawName.length,28);head.writeUInt32LE(offset,42);rawName.copy(head,46);const tail=descriptor?Buffer.alloc(16):Buffer.alloc(0);if(descriptor){tail.writeUInt32LE(0x08074b50);tail.writeUInt32LE(crc,4);tail.writeUInt32LE(packed.length,8);tail.writeUInt32LE(data.length,12);}locals.push(local,packed,tail);central.push(head);offset+=local.length+packed.length+tail.length;
 }const body=Buffer.concat(central),end=Buffer.alloc(22);end.writeUInt32LE(0x06054b50);end.writeUInt16LE(rows.length,8);end.writeUInt16LE(rows.length,10);end.writeUInt32LE(body.length,12);end.writeUInt32LE(offset,16);return new Uint8Array(Buffer.concat([...locals,body,end]));
}
for(const method of[0,8])for(const descriptor of[false,true]){const data=zip([['word/document.xml',text,method],['ignored.bin','never rendered',0]],{descriptor}),result=await extractOfficeFiles(data,'docx');assert.equal(result.length,1);assert.deepEqual(new Uint8Array(result[0][1]),text);}
for(const [extension,name]of[['xlsx','xl/worksheets/sheet1.xml'],['pptx','ppt/slides/slide1.xml'],['odt','content.xml']])assert.equal((await extractOfficeFiles(zip([[name,text]]),extension))[0][0],name);
const valid=zip([['word/document.xml',text]]),entry=officeDirectory(valid,'docx')[0],cd=entry.data+entry.packed;
const mutate=(at,value,size=4)=>{const copy=valid.slice(),view=new DataView(copy.buffer);size===2?view.setUint16(at,value,true):view.setUint32(at,value,true);return copy;};
for(const data of[valid.slice(0,-1),zip([['word/document.xml',text],['word/document.xml',text]]),zip([['../word/document.xml',text]]),zip([['/word/document.xml',text]]),mutate(cd+20,0xffffffff),mutate(cd+24,0xffffffff),mutate(cd+42,0xffffffff),mutate(cd+8,1,2),mutate(cd+10,99,2),mutate(30,'x'.charCodeAt(0),2),mutate(cd+24,2097153),zip([['word/document.xml',text],['word/../x.xml','x']])])assert.throws(()=>officeDirectory(data,'docx'));
const corrupt=valid.slice();new DataView(corrupt.buffer).setUint32(14,0,true);new DataView(corrupt.buffer).setUint32(cd+16,0,true);await assert.rejects(extractOfficeFiles(corrupt,'docx'));
const lied=valid.slice();new DataView(lied.buffer).setUint32(22,text.length-1,true);new DataView(lied.buffer).setUint32(cd+24,text.length-1,true);await assert.rejects(extractOfficeFiles(lied,'docx'));
assert.throws(()=>officeDirectory(new Uint8Array(1048577),'docx'));assert.throws(()=>officeDirectory(valid,'docm'));
assert(!fs.readFileSync(path.join(root,'examples/editor-home/ui/resource-office-worker.js'),'utf8').includes('fetch('));
// Lifecycle/quota tests use explicit fakes, not a browser codec assertion.
const workers=[],observers=[],timers=new Map();let clock=0,failures=0,detached=0,active=true;
globalThis.Worker=class{constructor(url,options){assert(url.pathname.endsWith('/resource-office-worker.js'));assert.equal(options.type,'module');this.terminated=0;workers.push(this);}postMessage(){}terminate(){this.terminated++;}};
globalThis.document={body:{}};globalThis.MutationObserver=class{constructor(fn){this.fn=fn;observers.push(this);}observe(){}disconnect(){this.disconnected=true;}};
globalThis.setTimeout=fn=>{timers.set(++clock,fn);return clock;};globalThis.clearTimeout=id=>timers.delete(id);
const {mountResourceOffice}=await import(pathToFileURL(path.join(root,'examples/editor-home/ui/resource-office.js'))),node=()=>({replaceChildren(){},setAttribute(){}}),mount=()=>mountResourceOffice({preview:node(),toolbar:node(),controls:node(),status:node(),bytes:valid.slice(),extension:'docx',active:()=>active,onError:()=>failures++,onDetached:()=>detached++});
const disposals=Array.from({length:4},mount);assert.throws(mount);assert.equal(workers.length,4);const old=workers[0].onmessage;active=false;observers[0].fn();assert.equal(detached,1);old({data:{ok:false}});assert.equal(failures,0);assert.equal(workers[0].terminated,1);active=true;const release=mount();release();release();assert.equal(workers.at(-1).terminated,1);
for(const dispose of disposals)dispose();assert.equal(timers.size,0);const timed=mount(),deadline=[...timers.values()][0];deadline();timed();assert.equal(failures,1);assert.equal(workers.at(-1).terminated,1);assert.equal(timers.size,0);const bad=mount(),callback=workers.at(-1).onmessage;callback({data:{ok:false}});callback({data:{ok:false}});bad();assert.equal(failures,2);assert.equal(workers.at(-1).terminated,1);assert.equal(timers.size,0);active=false;mount();assert.equal(detached,2);assert.equal(timers.size,0);
console.log('PASS bounded ZIP/actual native stream/CRC plus explicitly faked Office worker quota, timeout, retirement and repeated cleanup; no vendor or extraction');
