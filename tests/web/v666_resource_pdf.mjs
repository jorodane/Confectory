import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
import {readFileSync} from 'node:fs';
const root=process.argv[2],{pdfCanvasPlan:plan,pdfAssetURL:asset}=await import(pathToFileURL(root+'/examples/editor-home/ui/resource-pdf-policy.js'));
for(const[width,height,available,zoom,dpr]of[[612,792,580,'fit',1],[612,792,580,'2',2],[14400,14400,600,'fit',4],[20,7000,34,'1',2]]){
 const value=plan(width,height,available,zoom,dpr);assert(value.canvasWidth*value.canvasHeight<=4194304&&value.canvasWidth<=4096&&value.canvasHeight<=4096&&value.width<=8192&&value.height<=8192);
}
for(const args of[[0,1,500,'fit',1],[1,Infinity,500,'fit',1],[NaN,1,500,'fit',1],[15000,1,500,'fit',1],[1,14000,500,'fit',1],[612,792,580,'99',1],[612,792,-1,'1',1],[8192,8192,500,'2',1]])assert.throws(()=>plan(...args));
const here='https://own.invalid/resource-pdf-worker.js',prefix='https://own.invalid/assets/vendor/pdfjs-dist-4.10.38/';
assert.equal(asset(prefix+'cmaps/UniKS-UCS2-H.bcmap',here),prefix+'cmaps/UniKS-UCS2-H.bcmap');assert.equal(asset(prefix+'standard_fonts/LiberationSans-Regular.ttf',here),prefix+'standard_fonts/LiberationSans-Regular.ttf');
for(const value of['https://outside.invalid/data',prefix+'cmaps/../build/pdf.min.mjs',prefix+'cmaps/a.bcmap?x=1',prefix+'standard_fonts/a.ttf#fragment',prefix+'cmaps/a%2fhidden.bcmap','/api/request',prefix+'cmaps/a.js'])assert.throws(()=>asset(value,here));
const worker=readFileSync(root+'/examples/editor-home/ui/resource-pdf-worker.js','utf8');assert(worker.includes("credentials:'omit'")&&worker.includes("redirect:'error'")&&worker.includes("method!=='GET'"));
console.log('PASS exact bounded PDF canvas arithmetic and fixed same-origin font/CMap URL policy; actual renderer/worker lifecycle requires browser checks');
