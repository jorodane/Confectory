import assert from 'node:assert/strict';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {execFileSync} from 'node:child_process';
const root=process.argv[2],url=n=>pathToFileURL(path.join(root,'examples/editor-home/ui',n)).href;
const {captureMixedCell,mixedCellMatches,receiptFieldProof,rebaseMixedCell,restoredMixedProof}=await import(url('mixed-declaration.js'));
const fn='Owned.Types::Info_Function_'+'e'.repeat(32),owner='Owned.Types::Info',signature={args:[{name:'value',type:'Confectory.Information.IValue'}],return:'void'},proof={shapeHash:'a'.repeat(64),sources:{}};
const before={id:owner,kind:'schema',textHash:'a'.repeat(64),revision:0,ownFunctions:[]};
const value={kind:'native-function-edit',id:fn,functionHash:'b'.repeat(64),hash:before.textHash,revision:0,name:'new',description:'',signature,nativeTypes:{'Confectory.Information.IValue':proof,['$function:'+fn]:proof},mapping:{before:{args:[],return:'void'},args:{}}};
const change=captureMixedCell(value,before),start='p|'+owner+'|element|',key=start+'function:'+fn;
assert.equal(change.type,'function-edit');assert.deepEqual(change.nativeTypes,value.nativeTypes);assert(mixedCellMatches(key,value,change,start));assert(!mixedCellMatches(key,{...value,nativeTypes:{}},change,start));
const current={...before,textHash:'c'.repeat(64),revision:2,ownFunctions:[{id:fn,name:'new',description:'',signature,writable:true,origin:owner,hash:'d'.repeat(64)}]},late={...value,name:'late'};
const receipt=receiptFieldProof(late,change,current);assert(receipt);const inputs=new Map([[key,late]]);assert(rebaseMixedCell(inputs,start,key,late,receipt,current));assert.equal(inputs.get(key).name,'late');assert.equal(inputs.get(key).kind,'function-edit');assert(restoredMixedProof(inputs.get(key),current));assert(!captureMixedCell(inputs.get(key),current).nativeTypes);
// Execute the published previous capture adapter, not a reimplementation of it.
let old=execFileSync('git',['show','246fd701fffbd2ac2a5bdc14f0bc70504bbd2014:examples/editor-home/ui/mixed-declaration.js'],{cwd:root,encoding:'utf8'});
old=old.replaceAll("'./module-pin-presentation.js'",JSON.stringify(url('module-pin-presentation.js'))).replaceAll("'./typed-json.js'",JSON.stringify(url('typed-json.js')));
const previous=await import('data:text/javascript;base64,'+Buffer.from(old).toString('base64'));
assert.throws(()=>previous.captureMixedCell(value,before),/입력은 유지/);
console.log('PASS exact protected selection, late-name receipt rebasing and actual prior UI adapter refusal without dropping native source guards');
