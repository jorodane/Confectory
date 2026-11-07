// Isolate image state in Node while resolving the static SVG dependency explicitly.
import fs from 'node:fs';
import path from 'node:path';
export async function loadResourceImages(root){
 const folder=path.join(root,'examples/editor-home/ui'),uri=code=>'data:text/javascript;base64,'+Buffer.from(code).toString('base64');
 const svg=uri(fs.readFileSync(path.join(folder,'resource-svg.js'),'utf8'));
 const code=fs.readFileSync(path.join(folder,'resource-images.js'),'utf8').replace("'./resource-svg.js'",JSON.stringify(svg));
 return import(uri(code));
}
