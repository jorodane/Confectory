import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';

const source=fs.readFileSync(path.join(process.argv[2],'examples/editor-home/ui/feature-authoring.js'),'utf8');
const names=['sameRestoredSources','sameSettledInput','restoredOwnedSource',...(source.includes(' function ownedTextPair(')?['ownedTextPair']:[])];
const functions=names.map(name=>source.split('\n').find(line=>line.trimStart().startsWith('function '+name+'(')));
assert(functions.every(Boolean));
const proof=source.split('\n').find(line=>line.includes(',proof=d=>')).split(',proof=')[1];
const context=vm.createContext({});
vm.runInContext('const cellFrame=(w,key)=>key==="foreign"?"other":null;const proof='+proof+'\n'+functions.join('\n')+'\nglobalThis.check={sameSettledInput,restoredOwnedSource};',context);
const {sameSettledInput,restoredOwnedSource}=context.check;
const before=JSON.stringify([['G',0,'a'.repeat(64)],['G/node:body',0,'b'.repeat(64)]]);
const restored=JSON.stringify([['G',1,'a'.repeat(64)],['G/node:body',1,'b'.repeat(64)]]);
const origin={node:'body',type:'source',proof:before,text:'accepted body'};
const late={...origin,text:'later body'};
assert.equal(sameSettledInput(late,origin,restored,true),true);
assert.equal(sameSettledInput(late,origin,restored,false),false);
assert.equal(sameSettledInput(late,origin,restored.replace('a'.repeat(64),'c'.repeat(64)),true),false);
assert.equal(sameSettledInput(late,null,restored,true),false);
for(const patch of [{node:'other'},{type:'intent'},{proof:restored}])
 assert.equal(sameSettledInput({...late,...patch},origin,restored,true),patch.proof===restored);
const w={meta:{},authorData:{id:'G',rootId:'G',nodes:[{id:'body',kind:'code'}]}};
const journal={cells:[['key',origin]],edits:[{action:'source',node:'body',text:origin.text}]};
assert.equal(restoredOwnedSource(w,journal),true);
for(const patch of [{privatePath:'inner'},{slotContext:{}},{privateCopy:{}},{rootId:'other'}])
 assert.equal(restoredOwnedSource({...w,authorData:{...w.authorData,...patch}},journal),false);
assert.equal(restoredOwnedSource({...w,meta:{copyDraft:{}}},journal),false);
for(const patch of [{implementationContext:{}},{forwardCallerStorage:true},{kind:'call'}])
 assert.equal(restoredOwnedSource({...w,authorData:{...w.authorData,nodes:[{...w.authorData.nodes[0],...patch}]}},journal),false);
for(const patch of [{frame:'inner'},{node:'other'},{action:'rootParameters'}])
 assert.equal(restoredOwnedSource(w,{...journal,edits:[{...journal.edits[0],...patch}]}),false);
assert.equal(restoredOwnedSource(w,{...journal,cells:[...journal.cells,...journal.cells]}),false);
if(names.includes('ownedTextPair')){
 const pairWindow={meta:{},authorData:{...w.authorData,nodes:[{id:'body',kind:'code',control:'next'}]}},nameOrigin={node:'body',type:'rename',proof:before,text:'accepted name'};
 const pair={cells:[['name',nameOrigin],['source',origin]],edits:[{action:'rename',node:'body',text:nameOrigin.text},{action:'source',node:'body',text:origin.text}]};
 assert.equal(restoredOwnedSource(pairWindow,pair),true);
 assert.equal(restoredOwnedSource(pairWindow,{...pair,cells:[pair.cells[0],['source',{...origin,node:'other'}]]}),false);
 assert.equal(sameSettledInput({...nameOrigin,text:'late name'},nameOrigin,restored,false,true),true);
 assert.equal(sameSettledInput({...nameOrigin,text:'late name'},nameOrigin,restored,true),false);
 assert.equal(sameSettledInput({...nameOrigin,text:'late name'},nameOrigin,restored.replace('a'.repeat(64),'c'.repeat(64)),false,true),false);
 assert.equal(sameSettledInput({...nameOrigin,text:'late name'},null,restored,false,true),false);
}
console.log('PASS real source-proof recovery helpers: exact bytes/identity/origin only; explicit same-node text pair, peer hashes, missing origin and non-owned contexts checked');
