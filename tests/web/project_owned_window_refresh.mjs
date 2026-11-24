import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const source=readFileSync(new URL('../../examples/editor-home/ui/v508-runtime.js', import.meta.url), 'utf8');
const logic=source.slice(source.indexOf('let ownedProjectWindow='),source.indexOf('async function flushProjectChatDraft('));
const createFixture=new Function(`
 const row={id:'Local::View',title:'Test card',renderer:'element-view-card',field:'Note',value:'A'};
 const createNode=()=>({style:{},dataset:{},setAttribute(){},append(){}});
 const document={createElement:createNode};
 const anchor={isConnected:true};
 const current={projectId:'Alpha'};
 let page='work',lastPanel,windows=[],canOpen=true,delayed=null;
 const innerHeight=900;
 const view={generation:1,scope:{projectActivation:'a'},async observe(endpoint){
  if(endpoint==='listProjectWindows'&&delayed)return delayed.promise;
  const activation=view.scope.projectActivation;
  if(endpoint==='listProjectWindows')return {status:'available',projectActivation:activation,windows};
  if(endpoint==='readProjectWindow')return canOpen?{status:'available',projectActivation:activation,window:row}:{status:'unavailable'};
  throw Error(endpoint);
 }};
 const menu=()=>({isConnected:true,style:{top:'20px'},items:[],offsetHeight:200,querySelector(){},insertBefore(item){this.items.push(item)},_close(){this.isConnected=false}});
 const button=()=>({dataset:{}});
 const toast=()=>{};
 function modal(title,html,mount){
  const root={querySelector:createNode};
  const panel={closed:false};
  mount(root,()=>{panel.closed=true;root._ownedCleanup()});
  lastPanel=panel;
 }
 ${logic}
 return {
  menu,async list(m){await loadProjectWindowMenu(m,anchor)}, async open(){await openProjectOwnedWindow(row.id,anchor);return lastPanel},
  authorized(){windows=[{id:row.id,title:row.title}];canOpen=true}, hidden(){windows=[];canOpen=false},
  pauseList(){let fire;const promise=new Promise(resolve=>{fire=resolve});delayed={promise,fire};},
  resumeHiddenList(){const old=delayed;delayed=null;old.fire({status:'available',projectActivation:'a',windows:[]});},
  anotherProject(){current.projectId='Bravo';view.generation++;view.scope.projectActivation='b'},
  currentlyOpen(){return !!ownedProjectWindow}
 }
`);
const f=createFixture();
f.authorized();
const initial=await f.open();
const visible=f.menu();
await f.list(visible);
assert.equal(visible.items.length,1);
assert.equal(initial.closed,false);
f.hidden();
const updated=f.menu();
await f.list(updated);
assert.equal(updated.items.length,0);
assert.equal(initial.closed,true,'An authoritative empty list closes the already open View.');
assert.equal(f.currentlyOpen(),false);
await f.open();
assert.equal(f.currentlyOpen(),false,'A hidden View cannot reopen from a stale attempted selection.');

f.authorized();
const oldPanel=await f.open();
const m=f.menu();
f.pauseList();
const loading=f.list(m);
f.anotherProject();
const nextPanel=await f.open();
assert.equal(oldPanel.closed,true);
f.resumeHiddenList();
await loading;
assert.equal(nextPanel.closed,false,'A late response from Alpha cannot close the new project panel.');
assert.equal(f.currentlyOpen(),true);
console.log('PASS browser project window refresh keeps confirmed views, revokes hidden views and guards late project responses');
