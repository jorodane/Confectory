import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
const source=fs.readFileSync(path.join(process.argv[2],'examples/editor-home/ui/feature-authoring.js'),'utf8');
const line=source.split('\n').find(line=>line.trimStart().startsWith('function ownedDirectCreation('));assert(line);
const context=vm.createContext({});vm.runInContext(line+'\nglobalThis.check=ownedDirectCreation;',context);
const check=context.check,copy=value=>JSON.parse(JSON.stringify(value));
const w={meta:{},authorData:{id:'G',rootId:'G',nodes:[{id:'body',kind:'code',control:'next'}],edges:[{from:'body',port:'next',to:'exit:return'}]}};
const definition={kind:'code',control:'next',intent:'',signature:{args:[],return:'void'}};
const cells=[['c',{node:'placed',type:'create',text:JSON.stringify(definition)}],['n',{node:'placed',type:'rename',text:'내부 기능'}],['i',{node:'placed',type:'intent',text:'명시한 동작'}],['s',{node:'placed',type:'source',text:'DoWork();'}],['r1',{node:'body',type:'route',text:'placed'}],['r2',{node:'placed',type:'route',text:'exit:return'}]];
assert.equal(check(w,cells),true);const latest=copy(cells);latest[3][1].text='NewWork();';assert.equal(check(w,latest),true);
for(const patch of [{privatePath:'inner'},{slotContext:{}},{privateCopy:{}},{rootId:'different'}])assert.equal(check({...w,authorData:{...w.authorData,...patch}},cells),false);
assert.equal(check({...w,meta:{copyDraft:{}}},cells),false);
for(const mutate of [c=>c.push(['x',{node:'$root',type:'root-parameters',text:'{}'}]),c=>c.splice(3,1),c=>{c[1][1].node='body';},c=>{c[3][1].type='parameters';},c=>{c[4][1].text='other';},c=>{c[5][1].text='unknown';},c=>{c[2][1].text=' ';}]){const c=copy(cells);mutate(c);assert.equal(check(w,c),false);}
for(const patch of [{branchOwner:'choose'},{kind:'call'},{control:'switch'},{signature:{args:[{name:'x',type:'int'}],return:'void'}},{signature:{args:[],return:'int'}},{signature:{args:{length:0},return:'void'}}]){const c=copy(cells);c[0][1].text=JSON.stringify({...definition,...patch});assert.equal(check(w,c),false);}
for(const patch of [{kind:'call'},{control:'switch'},{implementationContext:{}},{forwardCallerStorage:true}])assert.equal(check({...w,authorData:{...w.authorData,nodes:[{...w.authorData.nodes[0],...patch}]}},cells),false);
assert.equal(check({...w,authorData:{...w.authorData,nodes:[...w.authorData.nodes,{id:'placed',kind:'code',control:'next'}]}},cells),false);
console.log('PASS actual direct-creation guard: one explicit void creation/source/two-route splice only; non-owned/contract/branch/mixed/unrelated plans rejected');
