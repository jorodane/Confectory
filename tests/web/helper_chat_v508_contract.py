"""Real production chat module + original v508 DOM/CSS, with an in-memory API.
Geometry/interaction boundary checks only. No account, CLI, provider or inference.
"""
import http.server,json,mimetypes,pathlib,re,sys,tempfile,threading,zipfile
from playwright.sync_api import sync_playwright,expect
repo=pathlib.Path(sys.argv[1]).resolve();root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-v508-chat-contract-'));z=zipfile.ZipFile(repo/'reference/site-ui/Confectory-Editor-Prototype-v508.zip');app=z.read('Confectory-v508/dist/app.js').decode()
# Use the prototype itself for the reference card, with its normal startup/Helper action.
class Handler(http.server.BaseHTTPRequestHandler):
 def log_message(self,*a):pass
 def do_GET(self):
  path=self.path.split('?',1)[0].lstrip('/') or 'index.html'
  if path=='helper-agents.js':data=(repo/'examples/editor-home/ui/helper-agents.js').read_bytes()
  elif path=='fixture.html':data=fixture_html.encode()
  elif path=='reference.html':data=reference_html.encode()
  else:
   try:data=z.read('Confectory-v508/dist/'+path)
   except KeyError:self.send_error(404);return
  self.send_response(200);self.send_header('Content-Type',mimetypes.guess_type(path)[0] or 'application/octet-stream');self.end_headers();self.wfile.write(data)
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();origin='http://127.0.0.1:'+str(server.server_port);fixture_html=reference_html=''
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu']);page=browser.new_page(viewport={'width':1440,'height':1000});page.route('**/*',lambda r:r.continue_() if r.request.url.startswith(origin) else r.abort());page.goto(origin);page.wait_for_timeout(2500)
 if page.locator('#later').is_visible() and page.locator('#later').is_enabled():page.locator('#later').click()
 expect(page.locator('.home-side [data-helper]').first).to_be_visible();page.locator('.home-side [data-helper]').first.click();expect(page.locator('.participant-expanded-card')).to_be_visible();card=page.locator('.participant-expanded-card').evaluate('(e)=>e.outerHTML');(root/'original-card.html').write_text(card)
 reference_html='<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="style.css">'+card
 fixture_html=reference_html+'''<script type="module">
 import {createHelperAgentsUI} from './helper-agents.js';await document.fonts.ready;
 const helper={id:'main',name:'루미'},draft={revision:'fixture',draftRevision:'basis',value:{name:'루미',globalDraft:''},dirty:false};
 const state={globalHelperSupported:true,connections:[],helperAgents:{agents:[{id:'fixture',model:'fixture-model',state:'ready',accountIdentity:{fingerprint:'owned-identity-a'}}],assignments:{main:'fixture'},turns:{}}};
 const control=globalThis.chatFixture={calls:[],errors:[],state,draft,persisted:'',counter:0,autoComplete:true,extra:false,badScope:false,badModel:false,common:false,fail:false,dropAck:false,saveDelay:0,startDelay:0,verificationState:'verified',accountFingerprint:'owned-identity-a'};
 const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)],esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));let ui;
 const update=()=>ui?.update($('#global-chat'));
 control.output=text=>{state.helperAgents.turns.main.output=text;update();};
 control.complete=()=>{const row=state.helperAgents.turns.main;row.state=control.fail?'error':'completed';row.output=control.fail?'':'OWNED UI CONTRACT RESPONSE';if(control.fail){row.errorCode='provider-error';row.errorDiagnostics={stage:'turn-start',rpcErrorCode:-32602,message:'PRIVATE never render',path:'/private/owned'};}row.records[0]={...row.records[0],state:row.state,output:row.output};update();};
 const invoke=async(endpoint,input)=>{
  control.calls.push(structuredClone(input));if(input.action==='conversation')return {};
  if(input.action==='readiness')return input.begin?{state:'checking',token:'owned-check'}:--control.readinessRemaining>0?{state:'checking',token:'owned-check'}:{state:'ready'};
  if(input.action==='prepare'){
   await new Promise(r=>setTimeout(r,10));const token='request-'+(++control.counter),scope={kind:'helper-global',helperId:'main',conversationId:'a'.repeat(32)},context={helper:'main',projectId:control.badScope?'PRIVATE-PROJECT':'',membership:{kind:'global'},conversationId:scope.conversationId,memory:control.common?[{scope:'common',text:'OWNED EXTRA'}]:[]};
   const verified=['verified','missing-identity'].includes(control.verificationState),verification={state:control.verificationState,supported:verified,message:'연결 준비 확인을 다시 진행하세요.'};if(control.verificationState==='verified')verification.accountIdentity={fingerprint:control.accountFingerprint};
   const preview={helper:'main',token,model:control.badModel?'different-model':'fixture-model',connection:'fixture',message:input.message,context,canStart:verified,policy:{verification,blockedReason:verified?null:verification.message,contentScope:scope,requirements:[{id:'contentApproved'},{id:'usageApproved'},...(control.extra?[{id:'extraRightApproved'}]:[])]}};
   state.helperAgents.preview=preview;state.helperAgents.turns.main={state:'prepared',requestId:token};return preview;
  }
  if(input.action==='start'){
   const preview=state.helperAgents.preview;if(!preview||input.token!==preview.token)throw Error('stale token');
   state.helperAgents.turns.main={state:'running',requestId:input.token,recordCount:1,historyPages:1,historyPage:0,records:[{requestId:input.token,message:preview.message,state:'running',output:''}],output:''};state.helperAgents.preview=null;update();
   if(control.autoComplete)setTimeout(control.complete,80);await new Promise(r=>setTimeout(r,control.startDelay));if(control.dropAck)throw Error('transport_rejected');return {};
  }
  if(input.action==='cancel'){state.helperAgents.turns.main.state='cancelled';update();return {};}
  if(input.action==='cancel-preview'){state.helperAgents.preview=null;return {};}
  throw Error('unexpected action');
 };
 const api={$, $$,esc,get current(){return state},get busy(){return false},connectionTitle:()=> 'Owned fixture',view:{call:invoke,update:async()=>update()},draft:()=>draft,toast:message=>control.errors.push(message),
  action:async(fn)=>{try{return await fn();}catch(error){control.errors.push(error.message);return false;}},
  saveDraft:async()=>{const text=draft.value.globalDraft;await new Promise(r=>setTimeout(r,control.saveDelay));control.persisted=text;draft.draftRevision='saved'+text;if(draft.value.globalDraft===text)draft.dirty=false;},
  modal:(title,html,mount)=>{const shade=document.createElement('div');shade.className='modal-shade';const modal=document.createElement('section');modal.className='modal';modal.innerHTML='<button data-close>×</button>'+html;modal.onkeydown=()=>{};shade.append(modal);document.body.append(shade);mount(modal,()=>shade.remove());}
 };
 ui=createHelperAgentsUI(api);control.flush=()=>ui.flushDrafts();control.ensureReady=()=>ui.ensureReady(helper);ui.renderGlobal($('#global-chat'),helper);control.ready=true;
 </script>'''
 def geometry():return page.locator('#global-chat').evaluate("r=>Object.fromEntries(['.messages','form','textarea','button[type=submit]'].map(s=>{const b=r.querySelector(s).getBoundingClientRect();return [s,{x:b.x,y:b.y,width:b.width,height:b.height}]}))")
 geometries=[]
 for width,height in [(1440,1000),(600,800)]:
  page.set_viewport_size({'width':width,'height':height});page.goto(origin+'/reference.html');page.evaluate('()=>document.fonts.ready');before=geometry();page.screenshot(path=str(root/f'original-{width}.png'));page.goto(origin+'/fixture.html');page.wait_for_function('globalThis.chatFixture?.ready');after=geometry();page.screenshot(path=str(root/f'restored-{width}.png'))
  geometries.append({'viewport':[width,height],'original':before,'restored':after})
  for selector,row in before.items():
   for field,value in row.items():assert abs(value-after[selector][field])<1,(width,selector,field,value,after[selector][field],before,after,page.locator('#global-chat form').evaluate('e=>[...e.children].map(n=>({tag:n.tagName,css:getComputedStyle(n).cssText,rect:n.getBoundingClientRect().toJSON(),font:getComputedStyle(n).font,style:n.getAttribute(\"style\")}))'))
 page.set_viewport_size({'width':1440,'height':1000});page.goto(origin+'/fixture.html');page.wait_for_function('globalThis.chatFixture?.ready');form=page.locator('#global-chat form');input=form.locator('textarea');send=form.locator('button[type=submit]')
 assert page.locator('#global-chat button').count()==1 and page.locator('#global-chat input').count()==0
 input.fill('한글 초안');page.wait_for_function("chatFixture.persisted==='한글 초안'");assert page.evaluate("chatFixture.calls.filter(x=>x.action==='start').length")==0
 input.dispatch_event('compositionstart');input.fill('조합 중');form.evaluate('e=>e.requestSubmit()');page.wait_for_timeout(100);assert page.evaluate("chatFixture.calls.filter(x=>x.action==='prepare').length")==0;input.dispatch_event('compositionend')
 # Persisted account identity is not evidence that the current session is verified.
 for phase in ['preflight-required','stale','cancelled','unauthenticated']:
  page.evaluate('(phase)=>{chatFixture.verificationState=phase;chatFixture.errors=[]}',phase);input.fill('before readiness');send.click();page.wait_for_function('chatFixture.errors.length>0');message=page.evaluate('chatFixture.errors.at(-1)');(root/'readiness-error.json').write_text(json.dumps({'phase':phase,'message':message},ensure_ascii=False))
  assert message=='연결 준비 확인을 다시 진행하세요.',(phase,message)
  assert page.evaluate("chatFixture.calls.filter(x=>x.action==='start').length")==0;expect(input).to_have_value('before readiness');expect(page.locator('[data-global-approval]')).to_have_count(0)
 page.evaluate("chatFixture.verificationState='missing-identity';chatFixture.errors=[]");send.click();page.wait_for_function('chatFixture.errors.length>0');assert 'codex-account-unverified' in page.evaluate('chatFixture.errors.at(-1)');assert page.evaluate("chatFixture.calls.filter(x=>x.action==='start').length")==0
 page.evaluate("chatFixture.verificationState='verified';chatFixture.accountFingerprint='owned-identity-b';chatFixture.errors=[]");send.click();page.wait_for_function('chatFixture.errors.length>0');assert 'codex-account-mismatch' in page.evaluate('chatFixture.errors.at(-1)');assert page.evaluate("chatFixture.calls.filter(x=>x.action==='start').length")==0
 page.evaluate("chatFixture.accountFingerprint='owned-identity-a';chatFixture.errors=[]")
 input.fill('normal');form.evaluate('e=>{e.requestSubmit();e.requestSubmit();}');page.wait_for_function("chatFixture.state.helperAgents.turns.main?.state==='completed'");expect(page.locator('[data-global-approval]')).to_have_count(0);assert page.evaluate("chatFixture.calls.filter(x=>x.action==='start').length")==1
 page.evaluate('chatFixture.autoComplete=false');input.fill('wait');send.click();page.wait_for_function("chatFixture.state.helperAgents.turns.main?.state==='running'");expect(send).to_have_text('중지');page.evaluate("chatFixture.output('스트리밍 일부')");expect(page.locator('#global-chat .messages')).to_contain_text('스트리밍 일부');input.fill('새 초안');send.click();page.wait_for_function("chatFixture.state.helperAgents.turns.main?.state==='cancelled'");expect(input).to_have_value('새 초안')
 page.evaluate('chatFixture.extra=true');input.fill('extra');send.click();expect(page.locator('[data-global-approval]')).to_be_visible();assert page.evaluate("chatFixture.calls.filter(x=>x.action==='start').length")==2;expect(page.locator('[data-global-start]')).to_be_disabled();page.locator('[data-global-review-cancel]').click();expect(input).to_have_value('extra')
 page.evaluate('chatFixture.extra=false;chatFixture.badScope=true');send.click();page.wait_for_timeout(100);assert page.evaluate("chatFixture.calls.filter(x=>x.action==='start').length")==2
 page.evaluate('chatFixture.badScope=false;chatFixture.badModel=true');send.click();page.wait_for_timeout(100);assert page.evaluate("chatFixture.calls.filter(x=>x.action==='start').length")==2
 page.evaluate('chatFixture.badModel=false;chatFixture.common=true');send.click();expect(page.locator('[data-global-approval]')).to_be_visible();assert page.evaluate("chatFixture.calls.filter(x=>x.action==='start').length")==2;page.locator('[data-global-review-cancel]').click()
 page.evaluate('chatFixture.common=false;chatFixture.dropAck=true');input.fill('ack-loss');send.click();page.wait_for_function("chatFixture.state.helperAgents.turns.main?.state==='running'");page.wait_for_timeout(50);assert page.evaluate("chatFixture.calls.filter(x=>x.action==='start').length")==3;page.evaluate('chatFixture.complete()')
 page.evaluate('chatFixture.dropAck=false;chatFixture.autoComplete=true;chatFixture.fail=true');input.fill('retry me');send.click();page.wait_for_function("chatFixture.state.helperAgents.turns.main?.state==='error'");expect(input).to_have_value('');expect(send).to_have_text('재시도');expect(page.locator('#global-chat .messages')).to_contain_text('provider-error · turn-start · rpcErrorCode=-32602');assert 'PRIVATE' not in page.locator('#global-chat .messages').inner_text()
 page.evaluate('chatFixture.saveDelay=150');input.fill('가');page.wait_for_timeout(190);input.fill('가나다');page.wait_for_function("chatFixture.persisted==='가나다'");assert page.evaluate("chatFixture.calls.filter(x=>x.action==='start').length")==4
 # Keyboard submission shares the original button's single pending path.
 before=page.evaluate("chatFixture.calls.filter(x=>x.action==='start').length");page.evaluate('chatFixture.fail=false');input.fill('line one');input.press('End');input.press('Shift+Enter');input.press('x');expect(input).to_have_value('line one\nx');assert page.evaluate("chatFixture.calls.filter(x=>x.action==='start').length")==before
 input.dispatch_event('compositionstart');input.press('Enter');form.evaluate('e=>e.requestSubmit()');page.wait_for_timeout(100);assert page.evaluate("chatFixture.calls.filter(x=>x.action==='start').length")==before;input.dispatch_event('compositionend')
 input.fill('keyboard once');input.press('Enter');form.evaluate('e=>e.requestSubmit()');page.wait_for_function("chatFixture.state.helperAgents.turns.main?.state==='completed'");expect(input).to_have_value('');assert page.evaluate("chatFixture.calls.filter(x=>x.action==='start').length")==before+1
 expect(send).to_be_enabled()
 # The user can type exactly the submitted text again while its acknowledgement is delayed.
 page.evaluate('chatFixture.startDelay=250;chatFixture.autoComplete=false');input.fill('same newer text');input.press('Enter');page.wait_for_function("chatFixture.state.helperAgents.turns.main?.state==='running'");input.fill('same newer text');page.wait_for_timeout(350);expect(input).to_have_value('same newer text');assert page.evaluate("chatFixture.calls.filter(x=>x.action==='start').length")==before+2;input.press('Enter');assert page.evaluate("chatFixture.calls.filter(x=>x.action==='cancel').length")==1;page.evaluate('chatFixture.complete()');expect(send).to_be_enabled()
 page.evaluate('chatFixture.startDelay=0;chatFixture.autoComplete=true;chatFixture.fail=true');input.fill('keyboard failed');input.press('Enter');page.wait_for_function("chatFixture.state.helperAgents.turns.main?.state==='error'");expect(input).to_have_value('');expect(send).to_have_text('재시도');expect(page.locator('#global-chat .messages')).to_contain_text('keyboard failed');page.screenshot(path=str(root/'safe-request-error.png'));page.wait_for_timeout(150);assert page.evaluate("chatFixture.calls.filter(x=>x.action==='start').length")==before+3
 page.evaluate('chatFixture.fail=false');input.press('Enter');page.wait_for_function("chatFixture.state.helperAgents.turns.main?.state==='completed'");expect(input).to_have_value('');assert page.evaluate("chatFixture.calls.filter(x=>x.action==='start').length")==before+4;assert page.evaluate("chatFixture.calls.filter(x=>x.action==='prepare').at(-1).message")=='keyboard failed'
 # Renewal waits without dispatch and refuses a changed binding before the next poll.
 before=page.evaluate("chatFixture.calls.filter(x=>x.action==='start').length")
 page.evaluate("chatFixture.state.helperAgents.agents[0].id='Confectory.Agent.Codex::Connection';chatFixture.state.helperAgents.assignments.main='Confectory.Agent.Codex::Connection';chatFixture.readinessRemaining=2")
 page.evaluate('()=>chatFixture.ensureReady()');assert page.evaluate("chatFixture.calls.filter(x=>x.action==='readiness').length")==3;assert page.evaluate("chatFixture.calls.filter(x=>x.action==='start').length")==before
 changed=page.evaluate("async()=>{setTimeout(()=>chatFixture.state.helperAgents.agents[0].configFingerprint='changed',20);try{await chatFixture.ensureReady();return '';}catch(e){return e.message;}}")
 assert 'codex-readiness-changed' in changed;assert page.evaluate("chatFixture.calls.filter(x=>x.action==='start').length")==before
 (root/'evidence.json').write_text(json.dumps({'pass':True,'originalGeometryMatchedAt':[1440,600],'geometry':geometries,'oneOriginalSendSlot':True,'checks':['unverified/expired/cancelled/auth missing identity distinguished','verified account mismatch blocked','same verified account allowed','IME','double submit','streaming','same-slot cancel','newer draft preserved','extra permissions conditional','unexpected project blocked','changed Agent blocked','extra memory conditional','lost ack no replay','accepted input cleared with explicit same-slot retry','Enter/ShiftEnter/IME','late identical new edit preserved','failure diagnostic redaction','renewal polling does not dispatch','binding change during renewal blocked','typing during autosave'],'realAccountOrInference':False,'root':str(root)},indent=2));print('PASS original v508 chat geometry and production UI contract '+str(root));browser.close()
server.shutdown()
