// Origin-local owned virtual files. Runtime assemblies and application schemas are excluded.
export async function openStorage(bridge) {
 const db=await new Promise((resolve,reject)=>{const r=indexedDB.open('confectory-owned-files',1);r.onupgradeneeded=()=>r.result.createObjectStore('snapshots');r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(r.error);r.onblocked=()=>reject(Error('Browser storage upgrade blocked'));});
 const key=new URL('.',location.href).pathname;
 function transaction(mode,value){return new Promise((resolve,reject)=>{const t=db.transaction('snapshots',mode),store=t.objectStore('snapshots');let result;const r=mode==='readonly'?store.get(key):store.put(value,key);r.onsuccess=()=>result=r.result;t.oncomplete=()=>resolve(result);t.onerror=()=>reject(t.error);t.onabort=()=>reject(t.error??Error('Browser storage transaction aborted'));});}
 const saved=await transaction('readonly');if(saved!==undefined){if(typeof saved!=='string')throw Error('Invalid browser storage record');bridge.RestoreStorage(saved);}
 let last=saved??'{}',pending=Promise.resolve(),error=null,busy=false;
 const state={get error(){return error?.message??null;},get pending(){return pending;},flush(){if(busy)return pending.then(()=>state.flush());busy=true;pending=(async()=>{try{const next=bridge.ExportStorage();if(next!==last){await transaction('readwrite',next);last=next;}error=null;}catch(e){error=e;console.error('Owned browser storage was not saved',e);throw e;}finally{busy=false;}})();return pending;}};
 // Serialize asynchronous commits. A page unload cannot guarantee transaction completion;
 // callers can await flush() before announcing export/reload completion.
 const timer=setInterval(()=>{if(!busy)state.flush().catch(()=>{});},1000);
 addEventListener('visibilitychange',()=>{if(document.visibilityState==='hidden')state.flush().catch(()=>{});});
 addEventListener('pagehide',()=>{clearInterval(timer);state.flush().catch(()=>{});});
 return state;
}
