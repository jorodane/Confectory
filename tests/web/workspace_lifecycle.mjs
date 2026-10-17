import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const moduleAt=async path=>import('data:text/javascript;base64,'+Buffer.from(readFileSync(path,'utf8')).toString('base64'));
const {createWorkspaceLinks}=await moduleAt('examples/editor-home/ui/workspace-links.js');
const {createPrivateDeletionHistory}=await moduleAt('examples/editor-home/ui/workspace-history.js');
globalThis.requestAnimationFrame=()=>1;
let project={layout:[],workspaces:[],workspaceItems:[],links:[],visitedWorkspaceTabs:['root'],inputs:{source:'live input'}};const messages=[],nodes=new Map();let saves=0;
const links=createWorkspaceLinks({state:{workspaceNodes:nodes},owner:()=>project,project:()=>project,canvas:()=>null,ready:()=>true,save:()=>saves++,toast:value=>messages.push(value),contextMenu:()=>{}});
for(const key of ['a','b','c'])nodes.set(key,{key,kind:'window',placed:true,el:{hidden:false}});
assert(links.connect(nodes.get('a'),nodes.get('b')));assert(links.connect(nodes.get('b'),nodes.get('c')));assert.deepEqual(links.descendants([nodes.get('a')]).map(n=>n.key),['a','b','c']);assert(!links.connect(nodes.get('c'),nodes.get('a')));assert.equal(project.links.length,2);
assert(links.connect(nodes.get('a'),nodes.get('c')));assert.deepEqual(project.links,[{parent:'a',child:'b'},{parent:'a',child:'c'}]);const old=nodes.get('b');nodes.set('b',{...old});assert(!links.connect(nodes.get('a'),old));links.remove(['c']);assert.equal(project.links.length,1);
const layout=(key,hidden=false)=>({key,x:10,y:20,width:300,height:200,placed:true,folded:false,hidden,meta:{pending:'original',basis:'original-source-hash'}});
project={layout:[layout('a'),layout('b')],workspaces:[],workspaceItems:[],links:[{parent:'a',child:'b'}],visitedWorkspaceTabs:['root'],inputs:{source:'unchanged'}};
const history=createPrivateDeletionHistory({project:()=>project,ready:()=>true,capture:()=>{},restore:fn=>fn(),persist:()=>saves++,toast:value=>messages.push(value)});
const before=history.before();project.layout[0].hidden=true;project.links=[];history.record(before);project.layout[0].meta.pending='newest private input';project.inputs.source='newest source input';assert(history.undo());assert.equal(project.layout[0].hidden,false);assert.equal(project.layout[0].meta.pending,'newest private input');assert.equal(project.inputs.source,'newest source input');assert.deepEqual(project.links,[{parent:'a',child:'b'}]);assert(history.redo());assert.equal(project.layout[0].hidden,true);
// The same JSON, not a live JS closure, restores the inverse after a process boundary.
project=JSON.parse(JSON.stringify(project));assert(history.undo());assert.equal(project.layout[0].meta.basis,'original-source-hash');assert(history.redo());project.layout[0].x++;const conflicted=JSON.stringify(project);assert(!history.undo());assert.equal(JSON.stringify(project),conflicted);
const owner=project;project={layout:[],workspaces:[],workspaceItems:[],visitedWorkspaceTabs:['root'],inputs:{source:'another project'}};assert(!history.undo());assert.equal(project.inputs.source,'another project');project=owner;
console.log('PASS private links: one parent/cycles/stale handles/descendants; deletion inverses: JSON cold, latest inputs/CAS preserved, atomic conflict and project isolation');
