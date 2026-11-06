import fs from 'node:fs';import vm from 'node:vm';import assert from 'node:assert/strict';
const source=fs.readFileSync(process.argv[2]+'/examples/editor-home/ui/feature-authoring.js','utf8'),names=['ownedTextFields','sameRestoredSources','sameSettledInput','restoredOwnedSource'];
const functions=names.map(name=>source.split('\n').find(line=>line.startsWith(' function '+name+'(')));assert(functions.every(Boolean));
const proofFunction=source.split('\n').find(line=>line.includes(',proof=d=>')).split(',proof=')[1];
const context=vm.createContext({});vm.runInContext('const proof='+proofFunction+';const cellFrame=(w,key)=>key==="foreign"?"other":null;'+functions.join('\n')+'\nglobalThis.check={ownedTextFields,sameSettledInput,restoredOwnedSource};',context);
const {ownedTextFields:guard,sameSettledInput:settled,restoredOwnedSource:owned}=context.check;
const proof=JSON.stringify([['G',0,'a'.repeat(64)],['G/node:body',0,'b'.repeat(64)]]),cold=JSON.stringify([['G',1,'a'.repeat(64)],['G/node:body',1,'b'.repeat(64)]]);
const data={id:'G',rootId:'G',nodes:[{id:'body',kind:'code',control:'next'}]},w={authorData:data,meta:{}},cell=type=>[type,{node:'body',type,text:type+' original',proof}],cells=['rename','intent','source'].map(cell);
for(const group of [cells,cells.slice(0,2),[cells[0],cells[2]],cells.slice(1),[...cells].reverse()]){
 assert(guard(w,group));const journal={cells:group,edits:group.map(([,v])=>({action:v.type,node:v.node,text:v.text}))};assert.equal(owned(w,journal),group.some(([,v])=>v.type==='source'));
 for(const [,origin]of group){const late={...origin,text:'late '+origin.type};assert(settled(late,origin,cold,origin.type==='source',true));assert(!settled(late,origin,cold,false,false));assert(!settled(late,null,cold,true,true));assert(!settled({...late,node:'other'},origin,cold,true,true));assert(!settled(late,origin,cold.replace('a'.repeat(64),'c'.repeat(64)),true,true));}
}
for(const group of [cells.slice(0,1),[...cells,cells[2]],[cells[0],cells[0]],[cells[0],['foreign',cells[1][1]]],[cells[0],['intent',{...cells[1][1],node:'other'}]],[cells[0],['intent',{...cells[1][1],text:null}]],[cells[0],['argument',{...cells[1][1],type:'argument:amount'}]],[cells[0],['route',{...cells[1][1],type:'route'}]]])assert(!guard(w,group));
for(const mutate of [d=>d.privatePath='inner',d=>d.slotContext={},d=>d.privateCopy=true,d=>d.rootId='other',d=>d.nodes[0].kind='call',d=>d.nodes[0].control='switch',d=>d.nodes[0].implementationContext={},d=>d.nodes[0].forwardCallerStorage=true]){const d=structuredClone(data);mutate(d);assert(!guard({authorData:d,meta:{}},cells));}
assert(!guard({authorData:data,meta:{copyDraft:{}}},cells));
const origin=cells[1][1];assert(!settled({...origin,text:'late',proof:cold},origin,proof,false,true));
console.log('PASS actual closed two/three-field ordinary-node text admission and exact-origin late receipt proof; all text subsets, peer closure/field/node, duplicates, contracts and ownership boundaries checked');
