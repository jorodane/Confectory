import {readFile,cp,mkdir,lstat,readdir} from 'node:fs/promises';
import {resolve,join} from 'node:path';
import {fileURLToPath} from 'node:url';
const source=fileURLToPath(new URL('../',import.meta.url));
const target=resolve(process.argv[2]??'/workspace/sites/confectory-connect');
if(target===resolve(source)||target.startsWith(resolve(source)+'/'))throw Error('Use a separate Sites source checkout');
const manifest=JSON.parse(await readFile(join(source,'.openai/hosting.json'),'utf8'));
try{const existing=JSON.parse(await readFile(join(target,'.openai/hosting.json'),'utf8'));if(existing.project_id!==manifest.project_id)throw Error('Destination belongs to another Site');}catch(e){if(e.code!=='ENOENT')throw e;}
async function regular(path){const s=await lstat(path);if(s.isSymbolicLink()||(!s.isDirectory()&&!s.isFile()))throw Error('Source links/devices are forbidden');if(s.isDirectory())for(const item of await readdir(path))await regular(join(path,item));}
await mkdir(target,{recursive:true});
// Never copy the engine checkout, .git, credentials, node_modules or local state.
for(const name of ['worker','db','drizzle','scripts','tests','.openai','package.json','package-lock.json','drizzle.config.js','.gitignore','README.md']){
 await regular(join(source,name));await cp(join(source,name),join(target,name),{recursive:true});
}
console.log('Staged source for '+manifest.project_id+' at '+target);
