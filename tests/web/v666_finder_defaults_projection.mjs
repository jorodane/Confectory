import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
import {setTimeout as pause} from 'node:timers/promises';
const {createFinderContent}=await import(pathToFileURL(process.argv[2]+'/examples/editor-home/ui/finder-content.js'));
async function read(fields,incomplete=false){const c=createFinderContent({context:()=>({key:'A',basis:'one',projectId:'A',namespace:'Owned'}),objects:()=>[{id:'Owned::Info',kind:'schema',owned:true}],ready:()=>true,read:async()=>({projectId:'A',rows:[{id:'Owned::Info',status:'available',fields,incomplete}]}),changed:()=>{}});c.ensure(true);const end=Date.now()+5000;while(!['ready','partial'].includes(c.status.phase)){assert.ok(Date.now()<end);await pause(10);}return c;}
const field=(name,valueJson)=>({name,state:'present',valueJson});
{
 const c=await read([field('기본값 · Greeting',String.raw`"\uae30\ubcf8\uc778\uc0ac\ud83d\ude00"`),field('기본값 · Huge','9223372036854775806'),field('기본값 · Compound',String.raw`{"caption":"\u96ea\ud83d\ude80","blob":"PayloadMustNotIndex","image":"data:image/png;base64,ImageMustNotIndex"}`)]);const text=c.rows.get('Owned::Info').text;assert.ok(text.includes('기본인사😀')&&text.includes('雪🚀')&&text.includes('9223372036854775806')&&!text.includes('9223372036854776000')&&!text.includes('MustNotIndex'));assert.equal(c.status.phase,'ready');c.close();assert.equal(c.rows.size,0);console.log('PASS typed-default JSON decodes Unicode and preserves int64 lexemes while omitting nested payload fields');
}
{
 const c=await read([field('기본값 · Large',JSON.stringify('x'.repeat(21000)+'TailMustBePartial'))]);assert.equal(c.status.phase,'partial');assert.ok(!c.rows.get('Owned::Info').text.includes('TailMustBePartial'));assert.ok(c.rows.get('Owned::Info').text.length<=20050);c.close();console.log('PASS text budget truncation is explicitly partial instead of false complete no-match');
}
{
 const c=await read([field('설명','"safe"')],true);assert.equal(c.status.phase,'partial');assert.ok(c.rows.get('Owned::Info').text.includes('safe'));c.close();console.log('PASS unavailable default records preserve safe description and native partial status');
}
