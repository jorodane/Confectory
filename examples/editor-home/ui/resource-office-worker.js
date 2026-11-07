import {extractOfficeFiles} from './resource-office-zip.js';
let started=false;
globalThis.onmessage=async event=>{
 if(started)return;started=true;
 try{const {bytes,extension}=event.data;if(!(bytes instanceof ArrayBuffer))throw Error('office_input');const files=await extractOfficeFiles(new Uint8Array(bytes),extension);postMessage({ok:true,files},files.map(([,data])=>data));}
 catch{postMessage({ok:false});}
 finally{close();}
};
