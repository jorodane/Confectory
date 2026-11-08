import {loadResourceImages} from './resource_image_module.mjs';
import assert from 'node:assert/strict';
const {resourceImageInfo:info}=await loadResourceImages(process.argv[2]);
const chunk=(name,data)=>{const b=Buffer.alloc(data.length+12);b.writeUInt32BE(data.length);b.write(name,4);data.copy(b,8);return b;};
function png(total,w=8,h=4){const head=Buffer.alloc(13);head.writeUInt32BE(w);head.writeUInt32BE(h,4);head[8]=8;head[9]=2;return Buffer.concat([Buffer.from([137,80,78,71,13,10,26,10]),chunk('IHDR',head),chunk('IDAT',Buffer.alloc(total-57)),chunk('IEND',Buffer.alloc(0))]);}
assert.deepEqual(info(png(4194304)),{width:8,height:4,pixels:32,type:'image/png'});
assert.throws(()=>info(png(4194305)),/resource_image_bytes/);
for(const [w,h]of[[16385,1],[4097,4096]])assert.throws(()=>info(png(1048577,w,h)),/resource_image_dimensions/);
const jpeg=Buffer.from([255,216,255,192,0,11,8,0,4,0,8,1,1,17,0,255,218,0,2,255,217]);
const app=Buffer.concat([Buffer.from([255,226,128,2]),Buffer.alloc(32768)]),largeJPEG=Buffer.concat([jpeg.subarray(0,2),...Array(64).fill(app),jpeg.subarray(2)]);
assert.deepEqual(info(largeJPEG),{width:8,height:4,pixels:32,type:'image/jpeg'});
for(const signature of['GIF89a','xxxxftypavif','<svg xmlns="http://www.w3.org/2000/svg">']){const bytes=Buffer.alloc(1048577);bytes.write(signature);assert.throws(()=>info(bytes),/resource_image_bytes/);}
const invalidBMP=Buffer.alloc(1048577);invalidBMP.write('BM');assert.throws(()=>info(invalidBMP),/resource_image_bmp_header/);
const invalidRIFF=Buffer.alloc(1048577);invalidRIFF.write('RIFFxxxxWEBP');assert.throws(()=>info(invalidRIFF),/resource_image_webp_size/);
console.log('PASS PNG/JPEG encoded maximum4MiB; side/pixel/remaining-format budgets unchanged; malformed large BMP still rejects; metadata screening only, actual decoding tested in Chromium');
