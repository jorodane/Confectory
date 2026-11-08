import assert from'node:assert/strict';import fs from'node:fs';import path from'node:path';import{createHash}from'node:crypto';
const root=process.argv[2],{decodeRunSurface:decode,decodeRunSize:size}=await import('data:text/javascript;base64,'+fs.readFileSync(path.join(root,'examples/editor-home/ui/run-surface.js')).toString('base64'));
const width=2560,height=1440,raw=Buffer.alloc(width*height*4);let seed=0x1730489d;for(let i=0;i<raw.length;i++){seed^=seed<<13;seed^=seed>>>17;seed^=seed<<5;raw[i]=seed&255;}
const epoch='a'.repeat(32),hash=createHash('sha256').update(raw).digest('hex'),cap={min:240,max:2560,maxPixels:3686400},resize={...cap,sequence:0,ack:0,command:'',width,height};
const packet=(index=0)=>({available:true,runtime:epoch,revision:'1',cursor:epoch+':1',format:'rgba8',encoding:'base64url-parts-v1',width,height,sha256:hash,unchanged:false,resize,part:index,parts:19,pixels:raw.subarray(index*786432,Math.min((index+1)*786432,raw.length)).toString('base64url')});
let calls=[];const result=await decode(packet(),null,'owned',async cursor=>{calls.push(cursor);return packet(Number(cursor.split(':').at(-1)));});assert.equal(calls.length,18);assert.deepEqual(Buffer.from(result.pixels),raw);assert.equal(result.sha256,hash);assert.equal(result.resize.max,2560);
const unchanged={...packet(),encoding:'base64url',unchanged:true};for(const key of['pixels','part','parts'])delete unchanged[key];assert.equal(await decode(unchanged,result,'owned'),result);
for(const corrupt of [q=>q.runtime='b'.repeat(32),q=>q.revision='2',q=>q.part=4,q=>q.parts=4,q=>q.resize={...resize,command:'bad'},q=>q.pixels=q.pixels.slice(1),q=>q.pixels=(q.pixels[0]==='A'?'B':'A')+q.pixels.slice(1)])await assert.rejects(()=>decode(packet(),null,'owned',async cursor=>{const q=packet(Number(cursor.split(':').at(-1)));if(q.part===1)corrupt(q);return q;}));
await assert.rejects(()=>decode(packet(),null,'owned'));for(const bad of[{parts:20},{height:1441},{encoding:'base64url'},{resize:{...resize,maxPixels:3686401}}])await assert.rejects(()=>decode({...packet(),...bad},null,'owned',async()=>{throw Error('must not read invalid manifest');}));
assert.throws(()=>size({...resize,maxPixels:262144},null,width,height));assert.throws(()=>size({...resize,max:640,maxPixels:262144},resize,640,360));
console.log('PASS complete high-entropy2560x1440 RGBA and whole SHA; bounded exact19 parts including index18, unchanged receipt, wrong/mixed/missing/corrupt data and capability rejection');

assert.equal(calls.at(-1),'slice:'+epoch+':1:18');
for(const bad of [{resize:{...resize,max:1280,maxPixels:921600}},{resize:{...resize,max:2560}},{resize:{...resize,max:2561}},{width:2561}])await assert.rejects(()=>decode({...packet(),...bad},null,'owned',()=>{throw Error('must reject before reading');}));
const{runAutoDimensions:auto}=await import('data:text/javascript;base64,'+fs.readFileSync(path.join(root,'examples/editor-home/ui/run-auto-fit.js')).toString('base64'));
assert.deepEqual(auto(2560,1440,cap),{width:2560,height:1440});assert.deepEqual(auto(1440,2560,cap),{width:1440,height:2560});assert.equal(auto(2560,1441,cap),null);assert.equal(auto(2560,1440,{min:240,max:1280,maxPixels:921600}),null);
console.log('PASS QHD explicit capability and two-digit final slice; HD/legacy bounds remain independent; authored custom/auto area limits');
