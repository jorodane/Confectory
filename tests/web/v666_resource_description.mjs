import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
const {createResourceBrowser}=await import(pathToFileURL(process.argv[2]+'/examples/editor-home/ui/resource-browser.js'));
let reads=0;const api={get current(){reads++;throw Error('runtime_not_initialized');},get view(){reads++;throw Error('runtime_not_initialized');},get busy(){reads++;throw Error('runtime_not_initialized');},get restoring(){reads++;throw Error('runtime_not_initialized');}};
const browser=createResourceBrowser(api);assert.equal(reads,0);assert.equal(typeof browser.mount,'function');assert.equal(typeof browser.beforeClose,'function');console.log('PASS resource browser construction leaves runtime view/current/busy getters lazy, before WebView initialization');

const {createResourceDescriptions}=await import(pathToFileURL(process.argv[2]+'/examples/editor-home/ui/resource-description.js'));
globalThis.document={createElement:()=>({dataset:{},setAttribute(){},append(){},remove(){}})};
const descriptions=createResourceDescriptions({current:{projectId:'owned'},persist(){}}),field={isConnected:true,tagName:'INPUT',value:'',after(){},addEventListener(){}},w={meta:{resourceDescriptionDraft:{owner:'owned',id:'a'.repeat(32),generation:'b'.repeat(64),revision:'c'.repeat(64),original:'',value:'preserved'}}};
const cleanup=descriptions.bind({w,field,item:{id:'a'.repeat(32),descriptionGeneration:'b'.repeat(64)},revision:'c'.repeat(64),active:()=>true});assert.equal(descriptions.active(w),true);assert.equal(field.value,'preserved');field.isConnected=false;assert.equal(descriptions.active(w),false);assert.equal(w.meta.resourceDescriptionDraft.value,'preserved');cleanup();delete globalThis.document;console.log('PASS retired DOM bindings cannot block a replacement browser rendering or erase its private description');
