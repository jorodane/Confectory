// Browser role providers: keyed DOM rendering, native text inputs and explicitly chosen files.
export function createHomeView(root=document){
 const get=id=>root.getElementById(id),cards=new Map();
 return {
  render(snapshot){const model=typeof snapshot==='string'?JSON.parse(snapshot):snapshot,selected=model.selected;
   get('title').textContent=selected?selected.namespace:'Open a pack';get('project').hidden=!selected;
   const paths=new Set(model.cards.map(card=>card.path));for(const [path,node] of cards){if(!paths.has(path)){node.remove();cards.delete(path);}}
   for(const card of model.cards){let node=cards.get(card.path);if(!node){node=root.createElement('div');node.className='card';cards.set(card.path,node);get('cards').append(node);}node.textContent=card.title;}
   get('status').textContent=model.status||'Ready';
   if(selected)get('capabilities').textContent=`${selected.kind} · standalone declaration: ${selected.standalone}. Independent browser/WASM: import, manifest drafts and downloads. Build/Play, native filesystem and OS multiwindow are unavailable.`;
  },
  dispose(){cards.clear();}
 };
}
export function bindText(input,onInput){const listener=()=>onInput(input.value);input.addEventListener('input',listener);return()=>input.removeEventListener('input',listener);}
export async function readChosenManifest(file){if(file.size>1048576)throw Error('Manifest exceeds one MiB');return {name:file.name,text:await file.text()};}
