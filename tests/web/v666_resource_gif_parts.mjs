import {loadResourceImages} from './resource_image_module.mjs';
import assert from'node:assert/strict';import path from'node:path';import{execFileSync}from'node:child_process';
const root=process.argv[2],{resourceImageInfo:info,mountResourceImage:mount}=await loadResourceImages(root);
const values=JSON.parse(execFileSync('python3',['-c',"import sys,json,base64;sys.path.insert(0,sys.argv[1]);import v666_resource_gif_fixture as f;print(json.dumps({k:base64.b64encode(getattr(f,k)).decode()for k in ['static87','animated','unsupported','interactive','oversized']}))",path.join(root,'tests/web')],{encoding:'utf8'}));for(const k in values)values[k]=Buffer.from(values[k],'base64');
const pad=(b,total)=>{const delta=total-b.length,n=Math.ceil((delta-3)/256);let left=delta-3-n;const chunks=[b.subarray(0,-1),Buffer.from([33,254])];for(let count=n;count>0;count--){const amount=Math.min(255,left-(count-1));assert(amount>0);chunks.push(Buffer.of(amount),Buffer.alloc(amount));left-=amount;}chunks.push(Buffer.of(0,59));const result=Buffer.concat(chunks);assert.equal(left,0);assert.equal(result.length,total);return result;};
for(const name of['static87','animated'])for(const length of[1048578,4194304])assert.deepEqual(info(pad(values[name],length)),{width:65,height:33,type:'image/gif',pixels:2145*(name==='animated'?2:1),frames:name==='animated'?2:1});
assert.throws(()=>info(pad(values.static87,4194305)),/resource_image_bytes/);
for(const name of['unsupported','interactive','oversized'])assert.throws(()=>info(pad(values[name],1048600)));
for(const sample of[values.static87,values.animated]){const big=pad(sample,4194304);assert.throws(()=>info(big.subarray(0,-1)));assert.throws(()=>info(Buffer.concat([big,Buffer.of(0)])));}
const weighted=pad(values.animated,1048600);weighted.writeUInt16LE(4096,6);weighted.writeUInt16LE(4096,8);assert.throws(()=>info(weighted),/resource_image_gif_budget/);assert.throws(()=>mount({bytes:weighted}),/resource_image_gif_budget/);
const noPalette=pad(values.static87,1048600);noPalette[10]&=127;assert.throws(()=>info(noPalette));
for(const sig of['xxxxftypheic','<svg xmlns="http://www.w3.org/2000/svg">']){const bytes=Buffer.alloc(1048577);bytes.write(sig);assert.throws(()=>info(bytes),/resource_image_bytes/);}
console.log('PASS large GIF87a/89a/default/animation metadata at >1MiB and exact4MiB; overflow/truncated/trailing/palette/control/dimensions and whole-canvas frame-weighted budget reject before DOM; unchanged64frame/lease/codec checks run separately, actual motion checked by compositor');
