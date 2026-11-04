// Exercise the actual authoring transaction builder, including its old gap.
import fs from 'node:fs';
import assert from 'node:assert/strict';
const source=fs.readFileSync(new URL('../../examples/editor-home/ui/feature-authoring.js',import.meta.url),'utf8');
const names=['asyncInputCell','coupledAsync','authorEdits'];
const functions=names.map(name=>source.split('\n').find(line=>line.startsWith(' function '+name+'(')));
assert(functions.every(Boolean));
const build=new Function(functions.join('\n')+';return authorEdits;')();
for(const port of ['completion','case:positive']){
 const records=[{node:'fresh',type:'create',text:JSON.stringify({kind:'code',control:'next',branchOwner:'choose',intent:'authored Task',signature:{args:[],return:'void'}})},{node:'choose',type:'route:'+port,text:'fresh'},{node:'fresh',type:'route',text:'return:choose'},{node:'fresh',type:'source',text:'await Work();'},{node:'$async',type:'async-plan',text:JSON.stringify({enabled:true,nodes:[{node:'fresh',enabled:true}]})}];
 const cells=records.map((r,i)=>['key'+i,r]);const original=structuredClone(cells),batch=build(cells);
 assert.deepEqual(cells,original);
 assert.deepEqual(batch.map(e=>e.action),['createNode','route','route','source','asyncTransition']);
 assert.equal(batch[0].definition.branchOwner,'choose');
 assert.deepEqual(batch[1],{action:'route',node:'choose',port,to:'fresh'});
 assert.equal(batch[2].to,'return:choose');assert.equal(batch[3].text,'await Work();');
 assert.throws(()=>build([...cells,['duplicate',records.at(-1)]]));
 for(const type of ['route:true','route:default','route:unknown','remove','root-execution'])assert.throws(()=>build([...cells,['unrelated',{node:'choose',type,text:''}]]));
}
console.log('PASS completion/result first Task uses one explicit batch; ownership/routes/source preserved; unrelated structure and duplicate Task refused');
