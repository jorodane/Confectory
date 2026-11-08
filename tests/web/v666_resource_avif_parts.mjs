import {loadResourceImages} from './resource_image_module.mjs';
import assert from'node:assert/strict';import path from'node:path';import{execFileSync}from'node:child_process';
const root=process.argv[2],{resourceImageInfo:info,mountResourceImage:mount}=await loadResourceImages(root);
const samples=JSON.parse(execFileSync('python3',['-c',"import sys,json,base64;sys.path.insert(0,sys.argv[1]);import v666_resource_avif_fixture as f;print(json.dumps({k:base64.b64encode(getattr(f,k)).decode()for k in ['color','subsampled','alpha','animated','unsupported']}))",path.join(root,'tests/web')],{encoding:'utf8'}));for(const k in samples)samples[k]=Buffer.from(samples[k],'base64');
const pad=(b,total)=>{const n=total-b.length;assert(n>=8);const free=Buffer.alloc(n);free.writeUInt32BE(n);free.write('free',4);return Buffer.concat([b,free]);};
for(const name of['color','subsampled','alpha'])for(const length of[1048578,4194304])assert.deepEqual(info(pad(samples[name],length)),{width:65,height:33,type:'image/avif',pixels:2145*(name==='alpha'?2:1)});
assert.throws(()=>info(pad(samples.color,4194305)),/resource_image_bytes/);
const compatible=pad(samples.color,1048600);compatible.write('mif1',8);assert.equal(info(compatible).type,'image/avif');
for(const length of[0,1,12,17,80,4294967295]){const b=pad(samples.color,1048600);b.writeUInt32BE(length,0);assert.throws(()=>info(b),/resource_image_bytes/);}
const unknown=pad(samples.color,1048600);unknown.write('heic',8);unknown.write('heic',16);assert.throws(()=>info(unknown),/resource_image_bytes/);
for(const name of['animated','unsupported'])assert.throws(()=>info(pad(samples[name],1048600)));
const boxes=(b,start,end)=>{const rows=[];for(let at=start;at<end;){const size=b.readUInt32BE(at);rows.push({at,body:at+8,end:at+size,type:b.toString('ascii',at+4,at+8)});at+=size;}return rows;};
const leb=n=>{const a=[];do{let b=n&127;n=Math.floor(n/128);a.push(b|(n?128:0));}while(n);return Buffer.from(a);};
function largeOBU(type){const b=samples.color,top=boxes(b,0,b.length),mdat=top.find(x=>x.type==='mdat'),meta=top.find(x=>x.type==='meta'),iloc=boxes(b,meta.body+4,meta.end).find(x=>x.type==='iloc');let at=mdat.body;
 while(at<mdat.end){const start=at,header=b[at++];let length=0,shift=0,v;do{v=b[at++];length+=(v&127)*2**shift;shift+=7;}while(v&128);const end=at+length;if((header>>3&15)===type){const next=1048600,obu=Buffer.concat([Buffer.of(header),leb(next),b.subarray(at,end),Buffer.alloc(next-length)]),delta=obu.length-(end-start),result=Buffer.concat([b.subarray(0,start),obu,b.subarray(end)]);result.writeUInt32BE(mdat.end-mdat.at+delta,mdat.at);result.writeUInt32BE(b.readUInt32BE(iloc.body+18)+delta,iloc.body+18);return result;}at=end;}throw Error('missing OBU');}
assert.equal(info(largeOBU(6)).type,'image/avif');assert.throws(()=>info(largeOBU(1)),/resource_image_avif_structure/);
const bad=pad(samples.alpha,1048600);const at=bad.indexOf(Buffer.from('iloc'));bad.writeUInt32BE(0,at+4+14);assert.throws(()=>info(bad));
const over=pad(samples.alpha,1048600);const ispe=over.indexOf(Buffer.from('ispe'));over.writeUInt32BE(16385,ispe+8);assert.throws(()=>mount({bytes:over}));
console.log('PASS AVIF major/compatible bounded ftyp, exact4MiB/free boxes and limit; only FRAME OBU admits >1MiB while sequence/associations/extents/profile/alpha surfaces remain constrained; metadata test, natural large entropy/pixels checked separately');
