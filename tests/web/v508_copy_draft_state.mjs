import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const moduleRoot=fs.mkdtempSync(path.join(os.tmpdir(),'confectory-copy-state-'));
fs.writeFileSync(path.join(moduleRoot,'package.json'),'{"type":"module"}');
for(const name of fs.readdirSync(path.join(process.cwd(),'examples/editor-home/ui')).filter(name=>name.endsWith('.js')))fs.copyFileSync(path.join(process.cwd(),'examples/editor-home/ui',name),path.join(moduleRoot,name));
const {createFeatureAuthoring}=await import(pathToFileURL(path.join(moduleRoot,'feature-authoring.js')));

const checks=[];
function fixture(){
 const inputs=new Map(),current={projectId:'fixture-project'},windows=new Map();let persisted=0;
 const api={authorInputs:inputs,$:()=>null,$$:()=>[],esc:s=>s,windows,get current(){return current},persist:()=>persisted++};
 const author=createFeatureAuthoring(api);
 const add=(owner,feature,suffix)=>{const copy={owner,function:feature,implementation:'Owned::Copy'+suffix,source:'Library::Original',target:'common',fingerprint:'snapshot'+suffix};const key=current.projectId+'|v508-copy|'+owner+'|'+feature,prefix=current.projectId+'|v508-author|'+feature+'|slot:'+owner+':'+copy.implementation+'|';inputs.set(key,{kind:'copy-selection',copy});inputs.set(prefix+'body|source',{node:'body',type:'source',text:'private '+suffix});return {key,prefix};};
 const own=add('Owned::Child','Api::One','A'),other=add('Owned::Other','Api::One','B');return {author,inputs,current,own,other,get persisted(){return persisted}};
}
{
 const f=fixture(),snapshot=f.author.copyDiscardSnapshot('Owned::Child');f.inputs.set(f.own.prefix+'body|source',{node:'body',type:'source',text:'late replacement'});assert.throws(()=>f.author.discardCopies(snapshot),/새 복사 입력/);assert.equal(f.inputs.get(f.own.prefix+'body|source').text,'late replacement');assert.equal(f.inputs.size,4);checks.push('replaced private text after Cancel snapshot refuses deletion and preserves both owners');
}
{
 const f=fixture(),snapshot=f.author.copyDiscardSnapshot('Owned::Child');f.inputs.set(f.own.prefix+'new|intent',{type:'intent',text:'late new node'});assert.throws(()=>f.author.discardCopies(snapshot),/새 복사 입력/);assert.equal(f.inputs.size,5);checks.push('new private node input after Cancel snapshot refuses deletion without clearing prior source');
}
{
 const f=fixture(),snapshot=f.author.copyDiscardSnapshot('Owned::Child');const old=f.inputs.get(f.own.key);f.inputs.set(f.own.key,{...old,copy:{...old.copy,implementation:'Owned::Replacement'}});assert.throws(()=>f.author.discardCopies(snapshot),/새 복사 입력/);assert.equal(f.inputs.size,4);checks.push('changed copy selection during cancellation refuses the old snapshot');
}
{
 const f=fixture(),snapshot=f.author.copyDiscardSnapshot('Owned::Child');f.current.projectId='other-project';assert.throws(()=>f.author.discardCopies(snapshot),/프로젝트/);assert.equal(f.inputs.size,4);checks.push('project navigation refuses a captured private-copy Cancel');
}
{
 const f=fixture(),snapshot=f.author.copyDiscardSnapshot('Owned::Child');f.author.discardCopies(snapshot);assert.equal(f.inputs.size,2);assert(f.inputs.has(f.other.key)&&f.inputs.has(f.other.prefix+'body|source'));assert.equal(f.author.copyDrafts('Owned::Child').length,0);assert.equal(f.author.copyDrafts('Owned::Other').length,1);assert.equal(f.persisted,1);checks.push('valid scoped cancellation removes only one owner and preserves another owner using the same public function');
}
console.log(JSON.stringify({checks,actualModule:true,controlledPrivateState:true,actualEngine:false,realRenderer:false},null,2));
