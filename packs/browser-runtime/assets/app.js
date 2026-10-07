import { dotnet } from './_framework/dotnet.js';
import { createHomeView,bindText,readChosenManifest } from './dom.js';
const view=createHomeView();
const $=id=>document.getElementById(id);
const runtime=await dotnet.create();runtime.setModuleImports('confectory.browser.dom',{render:snapshot=>view.render(snapshot)});const config=runtime.getConfig();const exports=await runtime.getAssemblyExports(config.mainAssemblyName);exports.Confectory.Browser.Bridge.Initialize();
export const browserBridge=exports.Confectory.Browser.Bridge;
let model=null,current=null,busy=false;const drafts=new Map();
async function api(action,payload={}){const raw=exports.Confectory.Browser.Bridge.Request(action,JSON.stringify(payload));const result=JSON.parse(raw);if(result.error)throw Error(result.error);return result;}
addEventListener('pagehide',event=>{if(!event.persisted)browserBridge.Close();});

function dirty(){return current&&($('source').value!==current.original||$('chat').value!==current.savedChat);}
function sync(){if(!current)return;current.text=$('source').value;current.chat=$('chat').value;$('dirty').textContent=dirty()?'Unsaved changes — download to save a local copy':'No unsaved changes';}
function render(){view.render(model);}
$('file').addEventListener('change',async event=>{const file=event.target.files[0];event.target.value='';if(!file)return; // Picker cancellation leaves every buffer unchanged.
 if(busy){$('status').textContent='Busy; retry after the current request.';return;}busy=true;
 try{const chosen=await readChosenManifest(file),text=chosen.text;const next=await api('import',chosen);if(next.status.startsWith('Error:')){$('status').textContent=next.status;return;}model=next;const key=model.selected.path;if(current&&current.key===key){$('status').textContent='Already open; drafts retained';return;}sync();current=drafts.get(key)||{key,name:file.name,original:text,text,chat:'',savedChat:''};drafts.set(key,current);$('source').value=current.text;$('chat').value=current.chat;render();sync();}catch(error){$('status').textContent=error.message;}finally{busy=false;}});
const closeSource=bindText($('source'),sync),closeChat=bindText($('chat'),sync);
addEventListener('pagehide',event=>{if(!event.persisted){closeSource();closeChat();view.dispose();}});
$('leave').addEventListener('click',async()=>{if(!current||busy)return;if(dirty()&&!confirm('Leave this project? Unsaved drafts remain in this browser session. Download the manifest first to save a file.'))return;busy=true;try{sync();model=await api('leave',{draft:current.chat});current=null;render();}catch(error){$('status').textContent=error.message;}finally{busy=false;}});
$('download').addEventListener('click',()=>{if(!current)return;sync();const url=URL.createObjectURL(new Blob([current.text],{type:'text/plain;charset=utf-8'}));const link=document.createElement('a');link.href=url;link.download=current.name;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);$('status').textContent='Download requested; verify the saved file in your browser';sync();});
addEventListener('beforeunload',event=>{if(dirty()||[...drafts.values()].some(d=>d.text!==d.original||d.chat!==d.savedChat)){event.preventDefault();event.returnValue='';}});
try{model=await api('snapshot');render();}catch(error){$('status').textContent=error.message;}
