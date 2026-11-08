// Original parent navigation: validated owned metadata, independent private browser.
const id=/^[a-f0-9]{32}$/,hash=/^[a-f0-9]{64}$/;
export function resourceParentRoot(key,items){const match=/^browser-tree:resource:([a-f0-9]{32}|null):[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/.exec(key);return match&&items.some(row=>row.id===match[1]&&row.kind==='folder')?match[1]:null;}
export function validateResourceLocation(value,selection){
 const item=value?.item,parent=value?.parent,keys=value&&Object.keys(value).sort().join('|');
 if(keys!=='format|item|parent|project|revision|status'||value.status!=='ready'||value.format!=='resource-location-v1'||!id.test(value.project)||value.project!==selection.project||!hash.test(value.revision)||value.revision!==selection.revision||!item||item.id!==selection.id||!id.test(item.id)||item.hash!==selection.hash||!hash.test(item.hash)||item.kind!==selection.kind||!['folder','file','document','image','mesh'].includes(item.kind)||(item.parent??null)!==(selection.parent??null)||typeof item.name!=='string'||!item.name.length||item.name.length>180||item.data!==undefined)throw Error('resource_location');
 if(item.parent===null){if(parent!==null)throw Error('resource_location_parent');}
 else if(!id.test(item.parent)||!parent||parent.id!==item.parent||parent.kind!=='folder'||!hash.test(parent.hash)||typeof parent.name!=='string'||!parent.name.length||parent.name.length>180||parent.data!==undefined)throw Error('resource_location_parent');
 return value;
}
export function createResourceParent(api){
 const jobs=new Map();
 function retire(w){const job=jobs.get(w);if(job){jobs.delete(w);job.controller.abort();}}
 function open(w,row,project,revision,active){
  if(!active())return;const selection={project,id:row.id,hash:row.hash,revision,kind:row.kind,parent:row.parent??null},key=JSON.stringify(selection),prior=jobs.get(w);if(prior){if(prior.key===key&&prior.active())return prior.promise;retire(w);}
  const job={controller:new AbortController(),key,active};jobs.set(w,job);const owns=()=>jobs.get(w)===job&&active();
  const read=async()=>{for(let attempt=0;;attempt++){if(!owns())throw Error('scope_changed');try{return await api.observe('readProjectResourceLocation',{project,id:row.id,hash:row.hash,revision},job.controller.signal);}catch(error){if(!owns()||error.message!=='busy'||attempt===2)throw error;await new Promise(resolve=>setTimeout(resolve,50));}}};
  const shape=value=>JSON.stringify(Object.keys(value).sort().map(key=>[key,value[key]&&typeof value[key]==='object'?shape(value[key]):value[key]]));
  job.promise=(async()=>{try{const value=validateResourceLocation(await read(),selection);if(!owns())return;const final=validateResourceLocation(await read(),selection);if(!owns())return;if(shape(value)!==shape(final))throw Error('resource_location_changed');api.open(final.item,final.parent);api.opened?.(w);}catch{if(owns())api.failed(w);}finally{if(jobs.get(w)===job)jobs.delete(w);}})();return job.promise;
 }
 globalThis.addEventListener?.('pagehide',()=>{for(const w of jobs.keys())retire(w);},{once:true});return {open,retire};
}
