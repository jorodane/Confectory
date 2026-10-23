import assert from 'node:assert/strict';
import fs from 'node:fs';
const source=fs.readFileSync(process.argv[2]+'/examples/editor-home/ui/v508-runtime.js','utf8');
const code=source.slice(source.indexOf('async function reviewSelected(id)'),source.indexOf('\nfunction reviewGroup()'));
const AsyncFunction=Object.getPrototypeOf(async function(){}).constructor;
async function check(change,expected){
 let current={projectId:'fixture-project',draft:{id:'Fixture::Monster',revision:7,text:'fixture source'},runTarget:'test'},calls=0,shown=0,validated=0;
 const choices=new Map(),view={async update(){},async call(endpoint,input){assert.equal(endpoint,'reviewDraft');assert.deepEqual(input,{id:'Fixture::Monster',target:'test'});if(++calls===1){change?.(current,choices);throw Error('stale_revision');}}};
 const run=new AsyncFunction('current','conflictInputs','targetChoices','view','assertBrowserDataApplied','showReview','modal','esc','controls','toast',code+';await reviewSelected("Fixture::Monster");');
 let failure;try{await run(current,new Map(),choices,view,async ids=>{assert.deepEqual(ids,['Fixture::Monster']);validated++;},()=>shown++,()=>assert.fail('unexpected creation dialog'),v=>v,()=>{},()=>{});}catch(e){failure=e;}
 if(expected){assert.match(failure?.message||'',/검토할 내용이 바뀌었습니다/);assert.equal(calls,1);assert.equal(shown,0);}else{assert.equal(failure,undefined);assert.equal(calls,2);assert.equal(shown,1);assert.equal(validated,2);}
}
await check(null,false);
for(const change of [s=>s.draft.revision++,s=>s.draft.text+=' changed',s=>s.draft.id='Fixture::Other',s=>s.projectId='other-project',(s,c)=>c.set(s.projectId,'other-target')])await check(change,true);
console.log('PASS review admission: one known-unexecuted stale retries; revision/text/selection/project/target changes stop before any second Review');
