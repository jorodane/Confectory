import {loadResourceImages} from './resource_image_module.mjs';
import assert from 'node:assert/strict';
const {resourceImageInfo:info}=await loadResourceImages(process.argv[2]);
const bmp=(width,height,depth=24,zero=false)=>{const body=Math.ceil(width*depth/32)*4*Math.abs(height),b=Buffer.alloc(54+body);b.write('BM');b.writeUInt32LE(b.length,2);b.writeUInt32LE(54,10);b.writeUInt32LE(40,14);b.writeInt32LE(width,18);b.writeInt32LE(height,22);b.writeUInt16LE(1,26);b.writeUInt16LE(depth,28);b.writeUInt32LE(zero?0:body,34);return b;};
for(const depth of[24,32])for(const height of[-600,600])for(const zero of[false,true]){const b=bmp(641,height,depth,zero);assert(b.length>1048576&&b.length<=4194304);assert.deepEqual(info(b),{width:641,height:600,pixels:384600,type:'image/bmp'});}
const near=bmp(1023,1365);assert.equal(near.length,4193334);assert.deepEqual(info(near),{width:1023,height:1365,pixels:1396395,type:'image/bmp'});
assert.throws(()=>info(bmp(1023,1366)),/resource_image_bytes/);
for(const total of[4194304,4194305]){const b=Buffer.alloc(total);near.copy(b);b.writeUInt32LE(total,2);assert.throws(()=>info(b),total===4194304?/resource_image_bmp_pixels/:/resource_image_bytes/);}
for(const [offset,value,kind]of[[6,1,'writeUInt32LE'],[10,55,'writeUInt32LE'],[14,108,'writeUInt32LE'],[18,16385,'writeInt32LE'],[22,-2147483648,'writeInt32LE'],[26,2,'writeUInt16LE'],[28,8,'writeUInt16LE'],[30,3,'writeUInt32LE'],[34,1,'writeUInt32LE'],[46,1,'writeUInt32LE']]){const b=Buffer.from(near);b[kind](value,offset);assert.throws(()=>info(b));}
assert.throws(()=>info(near.subarray(0,-1)));assert.throws(()=>info(Buffer.concat([near,Buffer.of(0)])));
for(const sig of['GIF89a','RIFFxxxxWEBP','xxxxftypavif','<svg xmlns="http://www.w3.org/2000/svg">']){const b=Buffer.alloc(1048577);b.write(sig);assert.throws(()=>info(b),/resource_image_bytes/);}
console.log('PASS >1MiB BMP24/32 signed orientation/row padding/zero imageSize and near4MiB; exact4MiB malformed pixel plane, encoded overflow, original format/dimension restrictions, and other large formats remain rejected; metadata only, browser pixels separate');
