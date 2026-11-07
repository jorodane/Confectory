import assert from 'node:assert/strict';
import {webcrypto} from 'node:crypto';
import {pathToFileURL} from 'node:url';
import path from 'node:path';
globalThis.crypto??=webcrypto;
const root=path.resolve(process.argv[2]),{createResourceSelection}=await import(pathToFileURL(path.join(root,'examples/editor-home/ui/resource-selection.js'))),{createResourceLayoutControls}=await import(pathToFileURL(path.join(root,'examples/editor-home/ui/resource-layout.js')));
const a='a'.repeat(32),b='b'.repeat(32),c='c'.repeat(32),owner='d'.repeat(32),items=[a,b,c].map(id=>({id,kind:'document',name:id,hash:'1'.repeat(64)})),catalogue={items,revision:'2'.repeat(64)};
for(const [selected,source,expected]of[[[a],b,[b]],[[a,b],a,[a,b]],[[],c,[c]]]){
 let stages=0,persisted=0,data=null;const w={meta:{resourceSelections:[...selected],resourceSelected:selected[0]||null},body:{querySelectorAll:()=>[]}};
 const selection=createResourceSelection({catalogue:()=>catalogue,rows:()=>items,persist:()=>persisted++});
 const controls=createResourceLayoutControls({current:{projectId:owner},alive:()=>true,pending:()=>false,catalogue:()=>catalogue,selection,persist:()=>persisted++,stage:()=>stages++});
 const node={isConnected:true};controls.bindDrag(w,node,items.find(row=>row.id===source),owner,{});node.ondragstart({currentTarget:node,stopPropagation(){},preventDefault(){throw Error('valid explicit source refused')},dataTransfer:{setData(type,raw){assert.equal(type,'application/x-confectory-resource');data=JSON.parse(raw);}}});
 assert.deepEqual(data.ids,expected,'drag payload differs from the explicit source selection');assert.deepEqual(selection.ids(w),expected,'dragging outside the selected set must select only the dragged source');assert.equal(data.projectId,owner);assert.equal(data.revision,catalogue.revision);assert.equal(stages,0,'drag start must not issue a native mutation');node.ondragend();
 console.log('PASS actual selection/drag adapter',JSON.stringify({selected,source,expected,persisted,nativeWrites:stages,realBrowser:false}));
}
