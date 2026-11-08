import {loadResourceImages} from './resource_image_module.mjs';
import assert from 'node:assert/strict';
const {resourceImageInfo:info,mountResourceImage:mount}=await loadResourceImages(process.argv[2]);
const chunk=(name,data)=>{const b=Buffer.alloc(8+data.length+(data.length&1));b.write(name);b.writeUInt32LE(data.length,4);data.copy(b,8);return b;};
const riff=(parts)=>{const b=Buffer.concat([Buffer.alloc(12),...parts]);b.write('RIFF');b.writeUInt32LE(b.length-8,4);b.write('WEBP',8);return b;};
const frame=()=>{const b=Buffer.from([0x30,0,0,0x9d,1,0x2a,64,0,32,0,0]);return chunk('VP8 ',b);};
const ll=()=>{const b=Buffer.alloc(6);b[0]=47;b.writeUInt32LE(63|(31<<14),1);return chunk('VP8L',b);};
const pad=(b,total)=>riff([b.subarray(12),chunk('JUNK',Buffer.alloc(total-b.length-8))]);
for(const frameBytes of[frame(),ll()])for(const total of[1048578,4194304]){const b=pad(riff([frameBytes]),total);assert.equal(b.length,total);assert.deepEqual(info(b),{width:64,height:32,pixels:2048,type:'image/webp'});}
assert.throws(()=>info(pad(riff([frame()]),4194306)),/resource_image_bytes/);
const max=pad(riff([ll()]),4194304),wrong=Buffer.from(max);wrong.writeUInt32LE(max.length-7,4);assert.throws(()=>info(wrong),/resource_image_webp_size/);
for(const b of[max.subarray(0,-1),Buffer.concat([max,Buffer.of(0)]),riff([chunk('VP8L',Buffer.of(0)),chunk('JUNK',Buffer.alloc(1048576))])])assert.throws(()=>info(b));
const extended=Buffer.alloc(10);extended[0]=2;extended.writeUIntLE(63,4,3);extended.writeUIntLE(31,7,3);
for(const b of[pad(riff([chunk('VP8X',extended),frame()]),1048600),pad(riff([chunk('ANIM',Buffer.alloc(6)),frame()]),1048600),pad(riff([ll(),chunk('ANMF',Buffer.alloc(16))]),1048600)]){
 assert.throws(()=>info(b),/resource_image_animation_unsupported/);assert.throws(()=>mount({bytes:b}),/resource_image_animation_unsupported/);
}
for(const sig of['GIF89a','xxxxftypavif','<svg xmlns="http://www.w3.org/2000/svg">']){const b=Buffer.alloc(1048577);b.write(sig);assert.throws(()=>info(b),/resource_image_bytes/);}
console.log('PASS static VP8/VP8L with bounded inert RIFF metadata at >1MiB/exact4MiB; overflow/RIFF size/padding/truncation and large animation rejection before DOM; remaining large formats bounded; actual entropy/pixels tested by Chromium separately');
