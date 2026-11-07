import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
const {createResourceBrowser}=await import(pathToFileURL(process.argv[2]+'/examples/editor-home/ui/resource-browser.js'));
let reads=0;const api={get current(){reads++;throw Error('runtime_not_initialized');},get view(){reads++;throw Error('runtime_not_initialized');},get busy(){reads++;throw Error('runtime_not_initialized');},get restoring(){reads++;throw Error('runtime_not_initialized');}};
const browser=createResourceBrowser(api);assert.equal(reads,0);assert.equal(typeof browser.mount,'function');assert.equal(typeof browser.beforeClose,'function');console.log('PASS resource browser construction leaves runtime view/current/busy getters lazy, before WebView initialization');
