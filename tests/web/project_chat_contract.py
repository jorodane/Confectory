"""Owned provider and focused project/global chat contract; no real account or inference."""
import http.server,json,threading
from playwright.sync_api import expect
class OwnedChat:
 def __init__(self):
  self.requests=[];self.errors=[];owner=self
  class Handler(http.server.BaseHTTPRequestHandler):
   def log_message(self,*args):pass
   def do_POST(self):
    try:
     assert self.path=='/responses' and self.headers.get('Authorization') is None
     body=json.loads(self.rfile.read(int(self.headers['Content-Length'])));request=json.loads(body['input'][0]['content']);assert request['kind'] in ('project-chat','helper-global-chat');assert request['projectId']==request['context']['projectId'];assert body['store'] is False;owner.requests.append(request)
     text='OWNED '+request['kind']+' REPLY';wire=json.dumps({'status':'completed','output':[{'type':'message','role':'assistant','content':[{'type':'output_text','text':text}]}]}).encode();self.send_response(200);self.send_header('Content-Length',str(len(wire)));self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(wire)
    except Exception as e:owner.errors.append(type(e).__name__);self.send_error(500)
  self.server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=self.server.serve_forever,daemon=True).start();self.endpoint='http://127.0.0.1:'+str(self.server.server_port)+'/responses'
 def close(self):self.server.shutdown();self.server.server_close()
def run(page,state,root,provider):
 failures=[]
 def capture(response):
  if not response.url.endswith('/api/request'):return
  try:
   value=response.json().get('state',{})
   if value.get('operationError'):failures.append({'diagnostic':value['operationError'],'sourceError':value.get('sourceError')})
  except Exception:pass
 page.on('response',capture)
 before=state();project=before['projectId'];helper=before['mainHelperId'];files={p:p.read_bytes() for p in (root/'projects').rglob('*') if p.suffix in ('.cproj','.cpack','.celem','.csbody')}
 expect(page.locator('#helper-summary')).to_contain_text(helper);page.locator('.home-side [data-helper="'+helper+'"]').first.click();card=page.locator('.participant-expanded-card:not(.coworker-hover-card)');input=card.locator('textarea');expect(input).to_be_visible()
 input.fill('한글 조합');input.dispatch_event('compositionstart');input.press('Enter');page.wait_for_timeout(200);assert not state().get('aiPreview') and not provider.requests
 input.dispatch_event('compositionend');input.fill('한글 조합');input.press('Shift+Enter');expect(input).to_have_value('한글 조합\n');input.fill('owned project conversation');input.press('Enter')
 expect(page.locator('#toast')).to_contain_text('project_chat_failed / workspace-open / state_rejected');current=state();assert current['projectId']==project and current.get('sourceError') is None and current['operationError']=={'code':'project_chat_failed','stage':'workspace-open','cause':'state_rejected'};assert not provider.requests;assert 'owned-secret-must-not-leak' not in json.dumps(current);expect(input).to_have_value('owned project conversation');page.screenshot(path=str(root/'safe-project-failure.png'))
 # Retry the same ordinary chat via the Send button. Only a new owned capability is prepared.
 card.locator('[data-helper-send]').click();expect(page.locator('#ai-start')).to_be_disabled();assert not provider.requests
 # Hidden floating cards must not intercept the permission review controls.
 for flag in ('contentApproved','usageApproved'):
  page.locator('[data-permission="'+flag+'"]').check();expect(page.locator('[data-permission="'+flag+'"]').first).to_be_checked();page.wait_for_timeout(200)
 expect(page.locator('#ai-start')).to_be_enabled();page.screenshot(path=str(root/'project-permission.png'));page.locator('#ai-start').click()
 for _ in range(500):
  current=state()
  if current.get('aiState') in ('completed','error'):break
  page.wait_for_timeout(30)
 assert current.get('aiState')=='completed',{'state':current.get('aiState'),'code':current.get('aiErrorCode'),'providerErrors':provider.errors}
 assert current['projectId']==project and len(provider.requests)==1 and provider.requests[0]['kind']=='project-chat';expect(card.locator('.messages')).to_contain_text('OWNED project-chat REPLY');page.screenshot(path=str(root/'project-response.png'))
 # Preserve the owned project and switch only the visible context to Home for an ordinary global chat.
 page.locator('.brand').click();expect(page.locator('.home-grid')).to_be_visible();page.locator('.home-side [data-helper="'+helper+'"]').first.click();card=page.locator('.participant-expanded-card:not(.coworker-hover-card)');card.locator('textarea').fill('owned global conversation');card.locator('[data-global-send]').click();expect(card.locator('.messages')).to_contain_text('OWNED helper-global-chat REPLY');assert not state()['projectId'] and len(provider.requests)==2 and provider.requests[-1]['kind']=='helper-global-chat',{'projectId':state()['projectId'],'kinds':[r['kind'] for r in provider.requests]};page.screenshot(path=str(root/'global-response.png'))
 assert all(p.read_bytes()==data for p,data in files.items()),'Ordinary chat changed source files';assert not provider.errors,provider.errors
 evidence={'checks':['project IME Enter not sent','Shift Enter newline','Enter and button share route','redacted workspace-open failure','retry before provider dispatch','explicit project content/usage consent','owned project actual Responses HTTP round trip','project remains selected through response','Home global Responses HTTP round trip','no source file changes'],'diagnostic':failures,'providerKinds':[r['kind'] for r in provider.requests],'actualWindowsExecuted':False,'actualAccountOrInference':False}
 (root/'project-chat-evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2));print('PASS actual project/global owned chat contract '+str(root),flush=True)
