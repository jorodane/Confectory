import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
import path from 'node:path';
const root=process.argv[2],load=name=>import(pathToFileURL(path.join(root,'examples/editor-home/ui',name)));
const {captureMixedCell,mixedCellMatches,receiptFieldProof,rebaseMixedCell,restoredMixedProof}=await load('mixed-declaration.js');
const image='data:image/webp;base64,'+'UklGRgAA'.repeat(200),late='data:image/webp;base64,'+'UklGRgBB'.repeat(200),hash='a'.repeat(64),nextHash='b'.repeat(64),fieldHash='c'.repeat(64),fnHash='d'.repeat(64),id='Owned::Info',fn=id+'_Function_'+'1'.repeat(32),start='p|'+id+'|element|';
const shape={kind:'general',cardinality:'single',type:'long'},before={id,kind:'schema',revision:0,textHash:hash},row={path:['Count'],...shape,schemaOrigin:id,fieldSource:id,schemaHash:nextHash,icon:image,valueJson:'9223372036854775805'};
const property={kind:'schema-icon',text:image,path:['Count'],contract:shape,schema:id,schemaHash:hash,hash,revision:0},change=captureMixedCell(property,before);assert(mixedCellMatches(start+'schema-icon:["Count"]',property,change,start));assert(!mixedCellMatches(start+'schema-icon:["Count"]',{...property,text:late},change,start));
const saved={...before,revision:2,textHash:nextHash,rows:[row]},proof=receiptFieldProof({...property,text:late},change,saved);assert.equal(proof.accepted,image);const cells=new Map();rebaseMixedCell(cells,start,start+'schema-icon:["Count"]',{...property,text:late},proof,saved);const held=[...cells.values()][0];assert.equal(held.text,late);assert(restoredMixedProof(held,saved));assert(!restoredMixedProof(held,{...saved,rows:[{...row,icon:late}]}));assert(!restoredMixedProof(held,{...saved,textHash:hash}));
console.log('PASS full property image request/receipt identity, late input and schema/hash ownership preserve exact values; truncated or different accepted images cannot rebase');
for(const kind of ['function-add','function-edit']){
 const value={kind,id:fn,name:'Owned',description:'한글',signature:{args:[],return:'void'},icon:late,hash,revision:0,...(kind==='function-edit'?{functionHash:fieldHash}:{})},accepted={...value,icon:image},request=captureMixedCell(accepted,before),key=start+'function:'+fn;
 const after={...saved,ownFunctions:[{id:fn,origin:id,writable:true,hash:fnHash,name:'Owned',description:'한글',signature:value.signature,icon:image}]};
 assert(mixedCellMatches(key,accepted,request,start));assert(!mixedCellMatches(key,value,request,start));const p=receiptFieldProof(value,request,after);assert.equal(p.acceptedIcon,image);assert.equal(p.kind,'function-edit');assert.equal(p.id,fn);const values=new Map();rebaseMixedCell(values,start,key,value,p,after);const preserved=values.get(key);assert.equal(preserved.icon,late);assert(restoredMixedProof(preserved,after));assert(!restoredMixedProof(preserved,{...after,ownFunctions:[{...after.ownFunctions[0],hash:hash}]}));assert.equal(receiptFieldProof(value,request,{...after,ownFunctions:[{...after.ownFunctions[0],icon:late}]}),null);
}
console.log('PASS existing/new function image receipts keep one function ID and change creation into explicit edit only after exact accepted image/hash proof');
