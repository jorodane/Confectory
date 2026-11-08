import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
const r=process.argv[2],m=await import(pathToFileURL(r+'/examples/editor-home/ui/resource-filter.js'));
assert.deepEqual(m.resourceKindChoices.map(x=>[...x]),[['all','모든 자료'],['document','문서'],['image','그림'],['mesh','메시'],['file','기타 파일']]);
const rows=[{kind:'folder',id:'f'},{kind:'image',id:'i'},{kind:'document',id:'d'},{kind:'file',id:'x'}];
for(const [value,expected]of[['all','fidx'],['document','fd'],['image','fi'],['mesh','f'],['file','fx']])assert.equal(rows.filter(row=>m.resourceMatchesFilter(row,value)).map(x=>x.id).join(''),expected);
for(const value of[undefined,null,{},['image'],false,0,'__proto__','IMAGE','image\0','image '.repeat(1000)]){assert.equal(m.resourceFilterValue(value),'all');assert.equal(rows.filter(row=>m.resourceMatchesFilter(row,value)).length,4);}
const snapshot=JSON.stringify(rows);for(const [value]of m.resourceKindChoices)rows.filter(row=>m.resourceMatchesFilter(row,value));assert.equal(JSON.stringify(rows),snapshot);assert(Object.isFrozen(m.resourceKindChoices)&&m.resourceKindChoices.every(Object.isFrozen));
console.log('PASS authored five kinds, folders survive every filter, no synthetic mesh result, unknown private preference falls back to all, original metadata unchanged');
const {createResourceDescriptions}=await import(pathToFileURL(r+'/examples/editor-home/ui/resource-description.js'));
class Element{constructor(){this.dataset={};this.isConnected=true;this.value='';}append(){}after(){}addEventListener(){}setAttribute(){}remove(){this.isConnected=false;}closest(){return{remove(){}};}}
globalThis.document={createElement:()=>new Element()};let writes=0;
const owner='1'.repeat(32),id='2'.repeat(32),generation='3'.repeat(64),revision='4'.repeat(64),draft={owner,id,generation,revision,value:'미확정 🧪',original:'old',pending:{revision,command:'5'.repeat(32),id,generation,value:'submitted'}};
const api={current:{projectId:owner},persist(){writes++;}},manager=createResourceDescriptions(api),w={meta:{resourceDescriptionDraft:structuredClone(draft)}};
const unbind=manager.bind({w,field:new Element(),item:{id,descriptionGeneration:generation},revision,active:()=>true,orphan:true});
assert(manager.canRebind(w,[{id,descriptionGeneration:generation}]));assert(!manager.canRebind(w,[{id,descriptionGeneration:'6'.repeat(64)}]));assert(!manager.canRebind(w,[]));assert(!manager.canRebind(w,[{id:'7'.repeat(32),descriptionGeneration:generation}]));assert.deepEqual(w.meta.resourceDescriptionDraft,draft);assert.equal(writes,0);api.current.projectId='8'.repeat(32);assert(!manager.canRebind(w,[{id,descriptionGeneration:generation}]));api.current.projectId=owner;unbind();assert(!manager.canRebind(w,[{id,descriptionGeneration:generation}]));
manager.bind({w,field:new Element(),item:{id,descriptionGeneration:generation},revision,active:()=>true});assert(!manager.canRebind(w,[{id,descriptionGeneration:generation}]));assert.deepEqual(w.meta.resourceDescriptionDraft,draft);assert.equal(writes,0);
console.log('PASS only live same-owner/same-generation orphan fields may rebind; existing editable fields and changed generation are fenced; exact input/revision/pending receipt unchanged and no save');
