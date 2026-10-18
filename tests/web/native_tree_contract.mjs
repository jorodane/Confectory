// Shared fixture compares the native projection with the existing WebUI contract.
import fs from 'node:fs';
const {createBrowserProjection}=await import('data:text/javascript;base64,'+Buffer.from(fs.readFileSync(process.argv[2]+'/examples/editor-home/ui/browser-projection.js')).toString('base64'));
const inventory={status:'available',packs:[{namespace:'Owned.Api'},{namespace:'Foreign.Api'}],declarations:[{id:'Foreign.Api::Parent',kind:'object',owned:false,parent:null},{id:'Foreign.Api::Unused',kind:'object',owned:false,parent:null}]};
const relationsMap={version:'fixture-v1',nodes:[],edges:[]};
function node(name,kind='object',valid=true){relationsMap.nodes.push({id:'Owned.Api::'+name,kind,owned:true,valid,revision:2,textHash:'a'.repeat(64)});}
function edge(name,parent,role='parent',kind='object'){relationsMap.edges.push({source:'Owned.Api::'+name,target:parent,role,kind});}
for(const name of ['Root','Middle','Leaf','Dangling','DanglingChild','CycleA','CycleB','CycleChild','Cross','Schema','Contained','Bad','BadChild','Feature','Boundary'])node(name,name==='Feature'?'function':name==='Schema'?'schema':'object',name!=='Bad');
edge('Middle','Owned.Api::Root');edge('Leaf','Owned.Api::Middle');edge('Leaf','Owned.Api::Contained','contain');edge('Leaf','Owned.Api::Schema','use','schema');edge('Dangling','Missing::Parent');edge('DanglingChild','Owned.Api::Dangling');edge('CycleA','Owned.Api::CycleB');edge('CycleB','Owned.Api::CycleA');edge('CycleChild','Owned.Api::CycleA');edge('Cross','Foreign.Api::Parent');edge('BadChild','Owned.Api::Bad');edge('Boundary','Owned.Api::Feature');
for(let n=0;n<66;n++){node('Depth'+n);if(n)edge('Depth'+n,'Owned.Api::Depth'+(n-1));}
const current={projectId:'tree-one',namespace:'Owned.Api',inventory,relationsMap};const api=createBrowserProjection({current});
const expected=Object.fromEntries(api.rows().map(row=>[row.id,{parent:api.parent(row.id)||'',...api.issue(row.id),declaredParent:api.issue(row.id).declaredParent||'',source:api.source(row.id)?.id||''}]));
fs.writeFileSync(process.argv[3],JSON.stringify({inventory,relationsMap,expected}));
