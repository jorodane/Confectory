import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';

// Execute the actual script injected by the Windows host, not a replacement API.
const program=readFileSync(new URL('../../targets/webview-windows/Program.cs',import.meta.url),'utf8');
const source=program.match(/AddScriptToExecuteOnDocumentCreatedAsync\("""\s*([\s\S]*?)\s*"""\)/)?.[1];
assert(source,'Windows host bridge script missing');
const window={};window.top=window;let receive;const sent=[];
const chrome={webview:{addEventListener(type,handler){assert.equal(type,'message');receive=handler;},postMessage(message){sent.push(message);}}};
runInNewContext(source,{window,chrome,setTimeout,clearTimeout});
assert.equal(typeof window.confectoryWebUI.connectSite,'function');
const opening=window.confectoryWebUI.connectSite();assert.equal(sent.length,1);
const request=sent[0];assert.equal(request.native,'site-connect');assert.equal(request.envelope,null);assert.equal(typeof request.id,'string');
receive({data:{id:'foreign-reply',reply:{ok:true}}});
receive({data:{id:request.id,reply:{ok:true}}});assert.equal((await opening).ok,true);
const rejected=window.confectoryWebUI.connectSite();receive({data:{id:sent[1].id,error:'transport_closed'}});await assert.rejects(rejected,/transport_closed/);
const disconnecting=window.confectoryWebUI.disconnectSite();assert.equal(sent[2].native,'site-disconnect');assert.equal(sent[2].envelope,null);receive({data:{id:sent[2].id,reply:{ok:true}}});assert.equal((await disconnecting).ok,true);
const frame={top:{}};runInNewContext(source,{window:frame,chrome,setTimeout,clearTimeout});assert.equal(frame.confectoryWebUI,undefined);
console.log('PASS actual Windows injected Site connect native envelope, correlation, rejection and frame exclusion; Windows runtime/login not executed');
