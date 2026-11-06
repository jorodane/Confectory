import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
import {setTimeout as pause} from 'node:timers/promises';
const repo=process.argv[2],{createFinderContent}=await import(pathToFileURL(repo+'/examples/editor-home/ui/finder-content.js'));
async function until(test){const end=Date.now()+6000;while(!test()){assert.ok(Date.now()<end,'controller deadline');await pause(10);}}
const value=(id,fields=[])=>({id,status:'available',revision:1,textHash:'a'.repeat(64),viewHash:'b'.repeat(64),contentHash:'c'.repeat(64),fields});
const field=(name,valueJson,state='present')=>({name,valueJson,state});
function fixture(count=1){let context={key:'A|1|root',basis:'one',projectId:'A',namespace:'Owned.Test'},objects=Array.from({length:count},(_,i)=>({id:'Owned.Test::Row'+i,kind:'object',owned:true})),calls=[],changed=0,read=async ids=>({projectId:context.projectId,rows:ids.map(id=>value(id,[field('Description','"한글 😀"'),field('Large','9223372036854775806'),field('Compound',String.raw`["\ud83d\ude00",9223372036854775806,{"caption":"nested visible","blob":"NestedImageMustNotIndex","dataUrl":"data:image/png;base64,PayloadMustNotIndex"}]`),field('editorIcon','"data:image/png;base64,DoNotIndexImage"')]))});
 const controller=createFinderContent({context:()=>context,objects:()=>objects,ready:()=>true,read:(ids,alive)=>{calls.push([...ids]);return read(ids,alive);},changed:()=>changed++});
 return {controller,calls,get changed(){return changed},setContext:next=>context=next,setObjects:next=>objects=next,setRead:next=>read=next};
}
{
 const f=fixture(65);f.setObjects([...Array.from({length:65},(_,i)=>({id:'Owned.Test::Row'+i,kind:'object',owned:true})),{id:'External::NoGrant',kind:'object',owned:true},{id:'Owned.Test::Kind',kind:'enum',owned:true}]);f.controller.ensure(true);await until(()=>f.controller.status.phase==='partial');assert.deepEqual(f.calls.map(ids=>ids.length),[64,1]);assert.equal(f.controller.rows.size,65);assert.equal(f.controller.status.unsupported,1);assert.ok(f.calls.flat().every(id=>id.startsWith('Owned.Test::')));const text=f.controller.rows.get('Owned.Test::Row0').text;assert.ok(text.includes('한글 😀')&&text.includes('9223372036854775806')&&!text.includes('9223372036854775800')&&!text.includes('DoNotIndexImage')&&!text.includes('NestedImageMustNotIndex')&&!text.includes('PayloadMustNotIndex')&&text.includes('nested visible'));f.controller.close();assert.equal(f.controller.rows.size,0);
 console.log('PASS exact owned 64+1 read batches, honest unsupported kind, lexical int64 and decoded compound Unicode; no external IDs or image payloads');
}
{
 const f=fixture(65);let release;f.setRead(ids=>new Promise(resolve=>release=()=>resolve({projectId:'A',rows:ids.map(id=>value(id,[field('Old','"old project"')]))})));f.controller.ensure(true);await until(()=>release);f.controller.close();release();await pause(50);assert.equal(f.calls.length,1);assert.equal(f.controller.rows.size,0);assert.equal(f.controller.status.phase,'idle');f.setContext({key:'B|2|root',basis:'two',projectId:'B',namespace:'Owned.Test'});f.setObjects([{id:'Owned.Test::New',kind:'object',owned:true}]);f.setRead(async ids=>({projectId:'B',rows:ids.map(id=>value(id,[field('New','"new project"')]))}));f.controller.ensure(true);await until(()=>f.controller.status.phase==='ready');assert.deepEqual([...f.controller.rows.keys()],['Owned.Test::New']);f.controller.close();
 console.log('PASS close retires delayed data and remaining batches; same namespace in another project never adopts old content');
}
{
 const f=fixture();f.setRead(async ids=>({projectId:'foreign',rows:ids.map(id=>value(id))}));f.controller.ensure(true);await until(()=>f.controller.status.phase==='failed');assert.equal(f.controller.rows.size,0);await pause(220);f.controller.ensure(true);await pause(220);assert.equal(f.calls.length,1);f.setRead(async ids=>({projectId:'A',rows:ids.map(id=>value(id,[field('Visible','"ok"')]))}));f.controller.refresh();await until(()=>f.controller.status.phase==='ready');assert.equal(f.calls.length,2);f.controller.close();
 console.log('PASS foreign/tampered owner response fails closed and never retries until explicit refresh');
}
{
 const f=fixture();f.setRead(async ids=>({projectId:'A',rows:ids.map(id=>value(id,[field('Visible','"ok"'),field('Missing','"NeverIndexUnavailableValue"','missing')]))}));f.controller.ensure(true);await until(()=>f.controller.status.phase==='partial');assert.equal(f.controller.status.unavailable,1);assert.ok(!f.controller.rows.get('Owned.Test::Row0').text.includes('NeverIndexUnavailableValue'));f.setContext({key:'A|1|root',basis:'changed',projectId:'A',namespace:'Owned.Test'});f.controller.ensure(true);await until(()=>f.calls.length===2&&f.controller.status.phase==='partial');f.controller.close();
 console.log('PASS unavailable fields remain partial and source basis changes invalidate the previous snapshot');
}
{
 const f=fixture();f.setContext({key:'settings',basis:'one',projectId:'settings',namespace:'Confectory.AISettings'});f.setObjects([{id:'Confectory.AISettings::Connections',kind:'object',owned:true}]);f.controller.ensure(true);await until(()=>f.controller.status.phase==='restricted');assert.equal(f.calls.length,0);assert.equal(f.controller.rows.size,0);f.controller.close();console.log('PASS existing connection-settings exclusion is retained without reading credentials or expanding capability');
}
