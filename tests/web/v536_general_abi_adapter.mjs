import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
import path from 'node:path';
const {abiLiteral,defaultAbiRemap,projectAbiValue,remappedAbiArguments}=await import(pathToFileURL(path.join(process.argv[2],'examples/editor-home/ui/call-abi-remap.js')));
assert.equal(abiLiteral('9223372036854775806','long'),'9223372036854775806');assert.equal(abiLiteral('한글 "본문"','string'),JSON.stringify('한글 "본문"'));assert.equal(abiLiteral('false','bool'),'false');assert.throws(()=>abiLiteral('9223e','double'));assert.throws(()=>abiLiteral('3','Owned::Other'));
assert.deepEqual(defaultAbiRemap({args:[{name:'x',type:'long'},{name:'value',type:'int'}],return:'long'},{args:[{name:'value',type:'int'},{name:'renamed',type:'long'}],return:'bool'}),{inputs:{value:'value',renamed:null},outputs:{return:'return'}});
console.log('PASS exact long/raw text literals and same-name-only suggestions; rename/order never infer ordinal pin identity');

const maps={native:{inputs:{renamed:'amount',step:{valueJson:'9223372036854775806'}},outputs:{return:'total'}}};assert.equal(projectAbiValue('{"node":"native"}',maps),'{"node":"native","output":"total"}');assert.equal(projectAbiValue('{"constant":{"node":"native","raw":9223372036854775806}}',maps),'{"constant":{"node":"native","raw":9223372036854775806}}');assert.deepEqual(remappedAbiArguments([{name:'amount',type:'long',valueJson:'{"input":"amount"}'}],{args:[{name:'step',type:'long'},{name:'renamed',type:'double'}],return:'bool'},maps.native,(name,raw)=>raw),[{name:'step',type:'long',valueJson:'{"constant":9223372036854775806}'},{name:'renamed',type:'double',valueJson:'{"input":"amount"}'}]);console.log('PASS approved preview shows literal/source/input/output mappings; literal data and raw long are not recursively rewritten');
