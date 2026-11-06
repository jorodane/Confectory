// Checkpoint only committed private geometry; preserve current camera/view metadata.
export function checkpointOfficeLayout(layout,pending=null){
 const value=structuredClone(layout);
 if(pending)for(const key of ['rooms','stations','storages','decorations','signs','cleaners','props'])if(Object.hasOwn(pending,key))value[key]=structuredClone(pending[key]);
 return value;
}
