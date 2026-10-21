// Existing confirmed identities + versioned owned declared relations. This is a
// private read projection; every edit/reference read still uses its owner gate.
export function createBrowserProjection(api){
 const caches=new Map(),group=kind=>kind==='function'||kind==='implementation'?'feature':kind==='module'?'module':kind==='schema'?'info':'concept';
 const declaration=kind=>['object','schema','category','concept','function','module','implementation'].includes(kind);
 const observed=()=>[...(api.current?.units||[]),...(api.current?.draft?[api.current.draft]:[])].filter(row=>declaration(row.kind)&&row.id.startsWith(api.current.namespace+'::'));
 const stateKey=()=>JSON.stringify(observed().map(row=>[row.id,row.revision]).sort());
 function entry(){const id=api.current?.projectId;if(!id)return null;if(!caches.has(id))caches.set(id,{});const cache=caches.get(id),incoming=api.current.relationsMap;if(incoming&&incoming.version!==cache.map?.version){cache.map=incoming;cache.failed=null;}return cache;}
 function needsRead(){const cache=entry();if(!cache||cache.failed===stateKey())return false;if(!cache.map)return true;return observed().some(row=>!cache.map.nodes.some(node=>node.owned&&node.id===row.id&&node.revision===row.revision));}
 function failed(){const cache=entry();if(cache)cache.failed=stateKey();}
 function retry(){const cache=entry();if(cache)cache.failed=null;}
 function projection(){const cache=entry(),inventory=api.current?.inventory;if(!cache)return {rows:[],parents:new Map(),children:new Map(),sources:new Map()};if(cache.projection&&cache.inventory===inventory&&cache.relations===cache.map?.version)return cache.projection;const inventoryKey=JSON.stringify(inventory);if(cache.projection&&cache.inventoryKey===inventoryKey&&cache.relations===cache.map?.version){cache.inventory=inventory;return cache.projection;}
  const map=new Map((inventory?.declarations||[]).map(row=>[row.id,{...row,group:group(row.kind)}])),edges=new Map(),sources=new Map(),owned=new Map((cache.map?.nodes||[]).filter(node=>node.owned).map(node=>[node.id,node]));
  for(const edge of cache.map?.edges||[]){if(!edges.has(edge.source))edges.set(edge.source,[]);edges.get(edge.source).push(edge);const source=owned.get(edge.source);if(source?.valid)for(const id of [edge.target,edge.function,edge.scope])if(id&&!sources.has(id))sources.set(id,source);}
  for(const node of owned.values()){const links=edges.get(node.id)||[];map.set(node.id,{...map.get(node.id),...node,namespace:node.id.split('::')[0],group:group(node.kind),parent:links.find(edge=>edge.role==='parent')?.target||null,relationships:links.filter(edge=>edge.role==='contain'||edge.role==='use'&&edge.kind==='schema'||edge.role==='field'&&edge.kind==='schema'),schemaIds:links.filter(edge=>edge.role==='use'&&edge.kind==='schema').map(edge=>edge.target)});}
  const rows=[...map.values()].map(row=>({...row,namespace:row.namespace||row.id.split('::')[0]})),parents=new Map(),children=new Map(),issues=new Map();
  for(const node of rows){let parent=null,status=node.owned?(node.valid===false?'invalid-source':owned.has(node.id)?'root':'unobserved'):'unobserved';
   if(node.parent&&node.valid!==false){let at=node.parent,depth=0;const seen=new Set([node.id]);status='linked';
    while(at){if(depth++>=64){status='depth-limit';break;}if(seen.has(at)){status=at===node.id?'cycle':'ancestor-cycle';break;}seen.add(at);const target=map.get(at);if(!target){status=depth===1?'unresolved':'ancestor-unresolved';break;}if(target.group!==node.group){status=depth===1?'group-boundary':'ancestor-boundary';break;}if(target.valid===false){status=depth===1?'invalid-parent':'ancestor-invalid';break;}at=target.parent;}
    if(status==='linked'||status.startsWith('ancestor-'))parent=node.parent;
   }
   parents.set(node.id,parent);issues.set(node.id,{status,declaredParent:node.parent||null});if(parent){if(!children.has(parent))children.set(parent,[]);children.get(parent).push(node);}
  }
  for(const values of children.values())values.sort((a,b)=>a.id.localeCompare(b.id));
  cache.inventory=inventory;cache.inventoryKey=inventoryKey;cache.relations=cache.map?.version;return cache.projection={rows,parents,children,sources,issues,version:cache.generation=(cache.generation||0)+1};
 }
 return {snapshot:projection,issue:id=>projection().issues?.get(id)||{status:"unobserved",declaredParent:null},rows:()=>projection().rows,parent:id=>projection().parents.get(id)||null,children:id=>projection().children.get(id)||[],source:id=>projection().sources.get(id)||null,workspaceRows:()=>{const p=projection();return p.rows.filter(row=>row.owned||p.sources.has(row.id)).map(row=>({...row,name:row.title||row.id.split('::').at(-1)}));},needsRead,failed,retry,group,get loading(){return !entry()?.map},get error(){return !!entry()?.failed}};
}
