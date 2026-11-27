// Actual renderer's narrow post-confirm status evidence gate.
import assert from 'node:assert/strict';
import {acceptedDetachedStatusStamp} from '../../examples/editor-home/ui/elements.js';
const id='Fixture::Owner',scope='first-project';
const schema={id,kind:'object',revision:5,textHash:'new-source',rows:[{schemaHash:'schema-1'}]};
const status={state:'ready',ids:[id],rows:[{id,revision:5,hash:'new-source',dirty:false,unsaved:false}],dirty:false,unsaved:false,canRecover:false};
const queued={...schema,revision:4};
const read=(s=status,a=schema,d=schema,q=queued,dirty=true)=>acceptedDetachedStatusStamp(scope,id,s,q,a,d,dirty);
assert.equal(read(),scope+'|'+id+'|5|["schema-1"]');
assert.notEqual(read(),acceptedDetachedStatusStamp('second-project',id,status,queued,schema,schema,true));
for(const changed of [
 {...status,state:'error'}, {...status,dirty:true}, {...status,unsaved:true},
 {...status,canRecover:true}, {...status,ids:[id,'Fixture::Other']},
 {...status,rows:[]}, {...status,rows:[{...status.rows[0],revision:4}]},
 {...status,rows:[{...status.rows[0],hash:'old-source'}]},
 {...status,rows:[{...status.rows[0],dirty:true}]},
 {...status,rows:[{...status.rows[0],unsaved:true}]}
])assert.equal(read(changed),null);
for(const changed of [
 {...schema,id:'Fixture::Other'}, {...schema,kind:'schema'}, {...schema,revision:6},
 {...schema,textHash:'other-source'}, {...schema,rows:[{schemaHash:'schema-2'}]},
]){assert.equal(read(status,changed,schema),null);assert.equal(read(status,schema,changed),null);}
assert.equal(read(status,null,schema),null);
assert.equal(read(status,schema,schema,queued,false),null);
assert.equal(read(status,schema,schema,{...queued,textHash:'before-staging'}),null);
assert.equal(read(status,schema,schema,{...queued,revision:3}),null);
assert.equal(read(status,schema,schema,{...queued,rows:[{schemaHash:'old-schema'}]}),null);
assert.equal(read(status,schema,null),null);
console.log('PASS exact clean accepted detached status; stale source/schema, other owner, dirty/group/recovery refuse.');
