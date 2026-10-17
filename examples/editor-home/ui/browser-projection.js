// Existing confirmed identities + versioned owned declared relations. This is a
// private read projection; every edit/reference read still uses its owner gate.
export function createBrowserProjection(api){
 const caches=new Map(),group=kind=>kind==='function'||kind==='implementation'?'feature':kind==='module'?'module':'concept';
 const declaration=kind=>['object','schema','category','concept','function','module','implementation'].includes(kind);
 const observed=()=>[...(api.current?.units||[]),...(api.current?.draft?[api.current.draft]:[])].filter(row=>declaration(row.kind)&&row.id.startsWith(api.current.namespace+'::'));
 const stateKey=()=>JSON.stringify(observed().map(row=>[row.id,row.revision]).sort());
 function entry(){const id=api.current?.projectId;if(!id)return null;if(!caches.has(id))caches.set(id,{});const cache=caches.get(id),incoming=api.current.relationsMap;if(incoming&&incoming.version!==cache.map?.version){cache.map=incoming;cache.failed=null;}return cache;}
 function needsRead(){const cache=entry();if(!cache||cache.failed===stateKey())return false;if(!cache.map)return true;return observed().some(row=>!cache.map.nodes.some(node=>node.owned&&node.id===row.id&&node.revision===row.revision));}
 function failed(){const cache=entry();if(cache)cache.failed=stateKey();}
 function retry(){const cache=entry();if(cache)cache.failed=null;}
 function projection(){const cache=entry(),inventory=api.current?.inventory;if(!cache)return {rows:[],parents:new Map(),children:new Map(),sources:new Map()};if(cache.projection&&cache.inventory===inventory&&cache.relations===cache.map)return cache.projection;
  const map=new Map((inventory?.declarations||[]).map(row=>[row.id,{...row,group:group(row.kind)}])),edges=new Map(),sources=new Map(),owned=new Map((cache.map?.nodes||[]).filter(node=>node.owned).map(node=>[node.id,node]));
  for(const edge of cache.map?.edges||[]){if(!edges.has(edge.source))edges.set(edge.source,[]);edges.get(edge.source).push(edge);const source=owned.get(edge.source);if(source?.valid)for(const id of [edge.target,edge.function,edge.scope])if(id&&!sources.has(id))sources.set(id,source);}
  for(const node of owned.values()){const links=edges.get(node.id)||[];map.set(node.id,{...map.get(node.id),...node,namespace:node.id.split('::')[0],group:group(node.kind),parent:links.find(edge=>edge.role==='parent')?.target||null,schemaIds:links.filter(edge=>edge.role==='use'&&edge.kind==='schema').map(edge=>edge.target)});}
  const rows=[...map.values()],parents=new Map(),children=new Map();
  for(const node of rows){let parent=null;if(node.parent&&map.has(node.parent)&&map.get(node.parent).group===node.group){const seen=new Set([node.id]);let at=node.parent,valid=true,depth=0;for(;at&&depth<64;depth++){if(seen.has(at)){valid=false;break;}seen.add(at);at=map.get(at)?.parent;}if(valid&&!at)parent=node.parent;}
   parents.set(node.id,parent);if(parent){if(!children.has(parent))children.set(parent,[]);children.get(parent).push(node);}}
  cache.inventory=inventory;cache.relations=cache.map;return cache.projection={rows,parents,children,sources};
 }
 return {rows:()=>projection().rows,parent:id=>projection().parents.get(id)||null,children:id=>projection().children.get(id)||[],source:id=>projection().sources.get(id)||null,workspaceRows:()=>{const p=projection();return p.rows.filter(row=>row.owned||p.sources.has(row.id)).map(row=>({...row,name:row.title||row.id.split('::').at(-1)}));},needsRead,failed,retry,group,get loading(){return !entry()?.map},get error(){return !!entry()?.failed}};
}
