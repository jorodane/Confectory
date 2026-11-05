import fs from 'node:fs';import vm from 'node:vm';import assert from 'node:assert/strict';
const source=fs.readFileSync(process.argv[2]+'/examples/editor-home/ui/feature-authoring.js','utf8');
const line=source.split('\n').find(s=>s.startsWith(' function ownedTextPair('));assert(line);
const run=vm.runInNewContext('(()=>{const cellFrame=(w,key)=>key.includes("foreign")?"foreign":null;'+line+';return ownedTextPair;})()');
const data={id:'owner/body:common',rootId:'owner/body:common',nodes:[{id:'body',kind:'code',control:'next'}]},w={authorData:data,meta:{}},cells=[['name',{node:'body',type:'rename',text:'이름'}],['source',{node:'body',type:'source',text:'return 1;'}]];
assert(run(w,cells));assert(run(w,structuredClone(cells)));assert(run(w,[[cells[0][0],{...cells[0][1],text:'늦은 이름'}],cells[1]]));
for(const change of [d=>d.privatePath='nested',d=>d.slotContext={},d=>d.privateCopy=true,d=>d.rootId='other',d=>d.nodes[0].kind='call',d=>d.nodes[0].control='switch',d=>d.nodes[0].implementationContext={},d=>d.nodes[0].forwardCallerStorage=true]){const d=structuredClone(data);change(d);assert(!run({authorData:d,meta:{}},cells));}
assert(!run({authorData:data,meta:{copyDraft:{}}},cells));
for(const c of [cells.slice(0,1),[...cells,cells[1]],[cells[0],['foreign',cells[1][1]]],[cells[0],['source',{...cells[1][1],node:'other'}]],[cells[0],['source',{...cells[1][1],type:'parameters'}]],[cells[0],['source',{...cells[1][1],text:null}]]])assert(!run(w,c));
console.log('PASS exact same-node direct-owned next name/source pair; contracts, other nodes, ownership and extra cells rejected');
