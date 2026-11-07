import {pdfAssetURL} from './resource-pdf-policy.js';
const read=globalThis.fetch.bind(globalThis);
globalThis.fetch=(input,options={})=>{
 const method=options.method||(input instanceof Request?input.method:'GET');if(method!=='GET')return Promise.reject(Error('pdf_asset_method'));
 try{return read(pdfAssetURL(input instanceof Request?input.url:String(input),import.meta.url),{method:'GET',credentials:'omit',redirect:'error',mode:'same-origin',signal:options.signal});}catch(error){return Promise.reject(error);}
};
await import('./assets/vendor/pdfjs-dist-4.10.38/build/pdf.worker.min.mjs');

globalThis.postMessage({resourcePDFReady:true});
