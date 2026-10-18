import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const load=async path=>import('data:text/javascript;base64,'+Buffer.from(readFileSync(path,'utf8')).toString('base64'));
const {createPrivateLayoutHistory}=await load('examples/editor-home/ui/workspace-history.js');
const {createWorkspaceLinks}=await load('examples/editor-home/ui/workspace-links.js');
globalThis.requestAnimationFrame=()=>1;
const copy=structuredClone,row=key=>({key,x:10,y:20,width:300,height:200,placed:true,folded:false,hidden:false,meta:{id:'project::'+key,pending:'first',revision:'CAS-first'}});
const make=()=>({layout:['a','b','c'].map(row),workspaceItems:[{id:'note',kind:'note',x:5,y:6,width:200,height:160,text:'first note'}],workspaces:[{id:'child',name:'Child',parentId:'root',layout:[],items:[],links:[]}],links:[],visitedWorkspaceTabs:['root'],inputs:{source:{text:'first source',draft:{revision:'CAS-source'}}},editorBindings:[{view:1,id:'project::a',mode:'properties'}]});
let project=make(),restores=0,persists=0,ready=true;const messages=[];
const history=createPrivateLayoutHistory({project:()=>project,ready:()=>ready,capture:()=>{},restore:(fn,_,placement)=>{restores++;assert(placement);fn();},persist:()=>persists++,toast:value=>messages.push(value)});
const record=fn=>{const token=history.before('layout');fn();return history.record(token);};
const unchanged=fn=>{const before=JSON.stringify(project),count=restores;assert(!fn());assert.equal(JSON.stringify(project),before);assert.equal(restores,count);};
const count=()=>project.privateHistory?.undo.length||0;
const nodes=new Map(['a','b','c'].map(key=>[key,{key,kind:'window',placed:true,el:{hidden:false}}]));
const links=createWorkspaceLinks({state:{workspaceNodes:nodes},owner:()=>project,project:()=>project,canvas:()=>null,ready:()=>ready,save:()=>{},toast:value=>messages.push(value),contextMenu:()=>{},before:()=>history.before('layout'),record:token=>history.record(token)});
assert(links.connect(nodes.get('a'),nodes.get('b')));assert.equal(count(),1);
assert(links.connect(nodes.get('b'),nodes.get('c')));assert.equal(count(),2);
unchanged(()=>links.connect(nodes.get('c'),nodes.get('a')));unchanged(()=>links.connect(nodes.get('a'),nodes.get('b')));
assert(links.connect(nodes.get('a'),nodes.get('c')));assert.equal(count(),3);assert(history.undo());assert.deepEqual(project.links,[{parent:'a',child:'b'},{parent:'b',child:'c'}]);assert(history.redo());
assert(links.disconnectChildren(nodes.get('a')));assert.equal(count(),4);assert.deepEqual(project.links,[]);assert(history.undo());assert.equal(project.links.length,2);assert(history.redo());
unchanged(()=>links.disconnect({parent:'a',child:'b'}));unchanged(()=>links.disconnectChildren(nodes.get('a')));
assert(history.undo());assert(links.disconnect(project.links[0]));assert.equal(project.privateHistory.redo.length,0);
assert(history.undo());const branch=JSON.stringify(project.privateHistory);assert(!record(()=>{}));assert.equal(JSON.stringify(project.privateHistory),branch);assert(history.redo());

// A bundle transfer changes all owners and only its boundary edges in one entry.
project=make();project.links=[{parent:'a',child:'b'},{parent:'b',child:'c'}];
const original=copy(project);assert(record(()=>{const child=project.workspaces[0];child.layout=project.layout.splice(0,2);child.layout.forEach(w=>{w.x+=90;w.y+=40;});child.links=project.links.splice(0,1);project.links=[];}));
assert.equal(count(),1);assert.equal(project.privateHistory.undo[0].changes.filter(c=>c.kind==='windows').length,2);
const a=project.workspaces[0].layout[0];a.meta={id:'project::a',pending:'edited after movement',revision:'CAS-current'};
project.inputs.source.text='source edited after movement';project.editorBindings[0].mode='information';
assert(history.undo());assert.deepEqual(project.links,original.links);assert.equal(project.layout.find(w=>w.key==='a').meta.pending,'edited after movement');assert.equal(project.layout.find(w=>w.key==='a').meta.revision,'CAS-current');assert.equal(project.inputs.source.text,'source edited after movement');assert.equal(project.inputs.source.draft.revision,'CAS-source');assert.equal(project.editorBindings[0].mode,'information');
assert(history.redo());assert.equal(project.workspaces[0].layout[0].meta.revision,'CAS-current');
project=JSON.parse(JSON.stringify(project));assert(history.undo());assert.equal(project.layout.find(w=>w.key==='a').meta.revision,'CAS-current');assert(history.redo());
assert(!JSON.stringify(project.privateHistory).includes('CAS-'));assert(!JSON.stringify(project.privateHistory).includes('pending'));

// Canonical note bindings survive movement while current text/style/name stay live.
project=make();const note=project.workspaceItems[0];assert(record(()=>{project.layout[0].x+=30;note.x+=30;}));note.text='later note';note.name='later title';note.titleStyle={size:20,color:'#123456'};
assert(history.undo());assert.equal(project.workspaceItems[0],note);assert.equal(note.x,5);assert.equal(note.text,'later note');assert.equal(note.name,'later title');assert.deepEqual(note.titleStyle,{size:20,color:'#123456'});assert(history.redo());assert.equal(note.x,35);

// Conflicts in any member reject the whole candidate before a restore callback.
project=make();assert(record(()=>{project.layout[0].x+=30;project.layout[1].x+=30;}));project.layout[1].x++;unchanged(()=>history.undo());
project=make();assert(record(()=>{project.layout[0].x+=30;}));project.windowDocuments=[{key:'a'}];unchanged(()=>history.undo());
project=make();assert(record(()=>{project.layout[0].x+=30;}));project.workspaces[0].layout.push(copy(project.layout[0]));unchanged(()=>history.undo());
project=make();project.links=[{parent:'a',child:'b'}];assert(record(()=>{project.links=[];}));project.links=[{parent:'c',child:'b'}];unchanged(()=>history.undo());
project=make();project.links=[{parent:'a',child:'b'}];assert(record(()=>{project.links=[];}));project.links=[{parent:'b',child:'a'}];unchanged(()=>history.undo());
project=make();project.links=[{parent:'a',child:'b'}];assert(record(()=>{project.links=[];}));project.layout.splice(1,1);unchanged(()=>history.undo());
project=make();project.layout=Array.from({length:258},(_,n)=>row('w'+n));project.links=[{parent:'w0',child:'w1'}];assert(record(()=>{project.links=[];}));project.links=Array.from({length:255},(_,n)=>({parent:'w0',child:'w'+(n+2)}));unchanged(()=>history.undo());

// Project ownership, busy guards and 16-entry retention also survive JSON cold state.
project=make();const token=history.before('layout'),owner=project;project=make();project.layout[0].x=999;unchanged(()=>history.record(token));assert.equal(owner.privateHistory,undefined);
project=make();for(let n=0;n<20;n++)assert(record(()=>{project.layout[0].x++;}));assert.equal(count(),16);ready=false;unchanged(()=>history.undo());ready=true;
project=JSON.parse(JSON.stringify(project));for(let n=0;n<16;n++)assert(history.undo());assert.equal(project.layout[0].x,14);unchanged(()=>history.undo());for(let n=0;n<16;n++)assert(history.redo());assert.equal(project.layout[0].x,30);
assert(persists>0);console.log('PASS private layout history: atomic bundle/links and conflict rejection, current inputs/CAS and canonical note identity, no-op/branch, project ownership, JSON cold, busy and bounded retention');
