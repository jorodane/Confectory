import assert from 'node:assert/strict';import {pathToFileURL}from'node:url';
const {checkpointOfficeLayout:snapshot}=await import(pathToFileURL(process.argv[2]+'/packs/workspace-3d/ui/arrangement.js'));
const committed={rooms:{own:{x:1}},stations:{},storages:{},decorations:{},signs:{},cleaners:{},props:[{id:'existing',x:1}]};
const live={...structuredClone(committed),rooms:{own:{x:9}},props:[{id:'new',x:2}],camera:{x:3,z:4,scale:2},seenHelpers:['visible'],floorplanVersion:2};
const before=JSON.stringify(live),saved=snapshot(live,committed);assert.equal(JSON.stringify(live),before);assert.deepEqual(saved.props,committed.props);assert.deepEqual(saved.rooms,committed.rooms);assert.deepEqual(saved.camera,live.camera);assert.deepEqual(saved.seenHelpers,live.seenHelpers);
saved.props[0].x=999;saved.camera.x=99;assert.equal(committed.props[0].x,1);assert.equal(live.camera.x,3);
assert.deepEqual(snapshot(live),live);assert.deepEqual(snapshot(live,{...committed,source:'forbidden'}).source,undefined);assert.deepEqual(snapshot({...live,extra:'preserve'},committed).extra,'preserve');
console.log('PASS provisional arrangement cannot enter checkpoints; camera/other private metadata stay current; no input/alias mutation or unexpected pending fields');
