"""Continue a completed owned consent fixture through real engine restarts.
No user profile/account, external OAuth, provider network or paid inference.
"""
import json,os,pathlib,signal,subprocess,sys,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();root=pathlib.Path(sys.argv[2]).resolve();case=pathlib.Path(sys.argv[3]).resolve()
assert root.parent==pathlib.Path('/tmp') and root.name.startswith('confectory-cli-flow-') and case.parent==root
assert (case/'agent-common-evidence.json').is_file(),'Only continue a completed owned fixture'
report=json.loads((root/'build.json').read_text());storage=case/'profile';checks=[];errors=[];external=[];host=None;log=None
(root/'active.json').write_text(json.dumps({'case':str(case)}))
env=os.environ.copy();env['PATH']=str(pathlib.Path(env.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet')).parent)+os.pathsep+env['PATH'];env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_ENTRY_STORAGE=str(storage),CONFECTORY_HOME_STORAGE=str(storage),CONFECTORY_MCP_DIRECTORY=str(case/'instances'),CONFECTORY_ELEMENT_AUTHORING_HOST=str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll'),CONFECTORY_PROJECT_EXECUTION_HOST=str(repo/'targets/project-execution-host/bin/Release/net10.0/Confectory.ProjectExecutionHost.dll'))
def control(**values):
 p=case/'control.json';d=json.loads(p.read_text());d.update(values);p.write_text(json.dumps(d))
def requests():return [json.loads(l) for l in (case/'requests.jsonl').read_text().splitlines()]
def turns():return [r for r in requests() if r.get('method')=='turn/start']
def receipts():return [r for r in json.loads((storage/'chat-use-grants.json').read_text())['grants'] if r['state']=='active']
def start():
 global host,log,origin,token,url
 log=(case/'lifecycle-host.log').open('w');host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 for _ in range(1000):
  urls=[s.split(' ',1)[1] for s in (case/'lifecycle-host.log').read_text().splitlines() if s.startswith('CONFECTORY_WEB_UI ')]
  if urls:url=urls[-1];origin,token=url.split('/#');return
  assert host.poll() is None;time.sleep(.02)
 raise AssertionError('owned lifecycle startup timed out')
def stop():
 if host and host.poll() is None:os.killpg(host.pid,signal.SIGTERM);host.wait(timeout=15)
 if log:log.close()
def raw(body,path='/api/request'):
 req=urllib.request.Request(origin+path,data=json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':token});return json.load(urllib.request.urlopen(req,timeout=30))
def state():
 for _ in range(500):
  v=raw({'op':'mount'})
  if v.get('error',{}).get('code')=='busy':page.wait_for_timeout(10);continue
  assert v['ok'],v;break
 else:raise AssertionError('owned lifecycle state busy')
 try:return v['state']
 finally:raw({'op':'dispose','view':v['view']})
def invoke(endpoint,body):
 for attempt in range(4):
  v=raw({'op':'mount'});assert v['ok'],v;rid=uuid.uuid4().hex
  try:
   ack=raw({'op':'invoke','view':v['view'],'scope':v['scope'],'expectedRevision':v['revision'],'requestId':rid,'endpoint':endpoint,'input':body});assert ack['ok'],ack
   for _ in range(600):
    update=raw({'op':'update','view':v['view'],'scope':v['scope']});found=[r for r in update.get('results',[]) if r['requestId']==rid]
    if not update.get('ok'):result={'error':update['error']};break
    if found:result=found[0];break
    page.wait_for_timeout(10)
   else:raise AssertionError('owned action pending')
  finally:raw({'op':'dispose','view':v['view']})
  if result.get('error',{}).get('code')=='stale_revision' and attempt<3:continue
  return result

def setup_page():
 p=browser.new_page(viewport={'width':1440,'height':1000});p.on('pageerror',lambda e:errors.append(str(e)))
 def route(r):
  if r.request.url.startswith(origin+'/') or r.request.url.startswith('data:'):r.continue_()
  else:external.append(r.request.url);r.abort()
 p.route('**/*',route);return p

def settings():
 page.locator('#add-agent').click();d=page.get_by_role('dialog',name='Agent 추가',exact=True);d.get_by_role('button',name='Codex',exact=True).click();return d

def card():return page.locator('.participant-expanded-card:not(.coworker-hover-card)')
def open_helper():
 page.locator('.home-side [data-helper="'+helper+'"]').first.click();expect(card().locator('button[type=submit]')).to_be_enabled();return card()
def send(text,count):
 card().locator('textarea').fill(text);card().locator('textarea').press('Enter');expect(card().locator('textarea')).to_have_value('')
 for _ in range(1200):
  s=state();turn=s['helperAgents']['turns'].get(helper,{})
  if turn.get('state')=='completed' and len(turns())==count:break
  if turn.get('state')=='error':raise AssertionError('owned send failed '+str(turn.get('errorCode')))
  page.wait_for_timeout(20)
 else:raise AssertionError('owned lifecycle response pending')
 expect(card().locator('.messages')).to_contain_text('OWNED CLI HELPER REPLY');expect(page.locator('[data-chat-use-consent],[data-global-approval]')).to_have_count(0)

try:
 control(holdAccount=False,readEmail='');start()
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu']);page=setup_page();goto_editor(page,url)
  # A previous interrupted fixture attempt may have explicitly accepted its OWN grant.
  if receipts():
   d=settings();expect(d.locator('[data-agent-use-revoke]')).to_be_enabled();d.locator('[data-agent-use-revoke]').click();expect(d.locator('[data-agent-use-accept]')).to_be_enabled();d.locator('[data-close]').click()
   for _ in range(500):
    if state().get('connectionSetup') is None:break
    page.wait_for_timeout(10)
  s=state();assert s['projectId']=='';helper=s['helpers'][0]['id'];baseline=len(turns());assert not receipts();assert s['helperAgents']['agents'][0]['readiness']['state']=='ready';checks.append('revoked legacy ready registration restores technically but never acquires common consent')
  d=settings();expect(d.locator('[data-agent-use-accept]')).to_be_enabled();challenge=state()['codexOnboarding']['useConsent']['challenge'];d.locator('[data-close]').click()
  for _ in range(500):
   if state().get('connectionSetup') is None:break
   page.wait_for_timeout(10)
  else:raise AssertionError('Agent settings cleanup not acknowledged')
  denied=invoke('chatUse',{'action':'agent-accept','agent':'Confectory.Agent.Codex::Connection','challenge':challenge});assert denied.get('error') and not receipts();checks.append('closed Agent settings reject even previously issued valid consent challenge')
  d=settings();expect(d.locator('[data-agent-use-accept]')).to_be_enabled();assert 'OpenAI' in d.locator('[data-agent-use-consent]').inner_text() and '금액 상한' in d.locator('[data-agent-use-consent]').inner_text();expect(d.locator('input[type=checkbox]')).to_have_count(0)
  for width,height in ((640,500),(375,700)):
   page.set_viewport_size({'width':width,'height':height});d.locator('[data-agent-use-accept]').scroll_into_view_if_needed();expect(d.locator('[data-agent-use-accept]')).to_be_visible();assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');page.screenshot(path=str(case/f'agent-consent-{width}.png'))
  page.set_viewport_size({'width':1440,'height':1000});d.locator('[data-agent-use-accept]').click();expect(d.locator('[data-cli-done]')).to_be_enabled();expect(d).to_be_visible();d.locator('[data-cli-done]').click();common=receipts()[0]['id'];assert len(receipts())==1;checks.append('existing Agent explicitly accepts once in same modal; small 640x500 and375x700 copy/action usable without horizontal overflow')
  open_helper();send('Owned lifecycle initial',baseline+1);before={r['id'] for r in receipts()};assert raw({},'/fixture/expire')['ok'];send('Owned lifecycle after technical expiry',baseline+2);assert before=={r['id'] for r in receipts()};checks.append('technical expiry renews with stable common grant and direct send');card().locator('[data-close]').click();page.close();stop()
  start();page=setup_page();goto_editor(page,url);expect(page.locator('.agent-home .connection-dot.ready')).to_have_count(1,timeout=30000);assert state()['helperAgents']['agents'][0]['readiness']['state']=='ready';assert receipts()[0]['id']==common;open_helper();send('Owned lifecycle after full engine restart',baseline+3);assert len(receipts())==1 and receipts()[0]['id']==common;checks.append('full engine restart connects at startup without settings/input and direct sends preserve common grant');print('MILESTONE expiry and full restart direct sends passed',flush=True)
  control(holdAccount=True);reads=sum(r.get('method')=='account/read' for r in requests());card().locator('textarea').fill('Owned queued before Agent revoke');card().locator('textarea').press('Enter');expect(card().locator('textarea')).to_have_value('')
  for _ in range(500):
   if sum(r.get('method')=='account/read' for r in requests())>reads:break
   page.wait_for_timeout(20)
  else:raise AssertionError('owned provider fresh account check not reached')
  card().locator('[data-close]').click();d=settings();expect(d.locator('[data-agent-use-revoke]')).to_be_enabled();d.locator('[data-agent-use-revoke]').click();expect(d.locator('[data-agent-use-accept]')).to_be_enabled();control(holdAccount=False);assert not receipts()
  for _ in range(500):
   if state()['helperAgents']['turns'].get(helper,{}).get('state')!='running':break
   page.wait_for_timeout(20)
  assert len(turns())==baseline+3;d.locator('[data-close]').click();open_helper();card().locator('textarea').fill('Owned future after revoke');card().locator('textarea').press('Enter');expect(page.locator('#toast')).to_contain_text('chat-use-agent-consent-required');expect(card().locator('textarea')).to_have_value('Owned future after revoke');assert len(turns())==baseline+3;checks.append('Agent settings revoke cancels queued provider before context dispatch and blocks future send')
  card().locator('[data-close]').click();d=settings();expect(d.locator('[data-agent-use-accept]')).to_be_enabled();d.locator('[data-agent-use-accept]').click();expect(d.locator('[data-cli-done]')).to_be_enabled();d.locator('[data-cli-done]').click();open_helper();control(readEmail='changed-lifecycle@fixture.invalid');card().locator('textarea').fill('Owned foreign account must not dispatch');card().locator('textarea').press('Enter')
  for _ in range(1000):
   t=state()['helperAgents']['turns'].get(helper,{})
   if t.get('state')=='error':break
   page.wait_for_timeout(20)
  else:raise AssertionError('changed account did not fail closed')
  assert len(turns())==baseline+3 and t.get('errorCode');assert state()['helperAgents']['agents'][0]['accountIdentity']['email']!='changed-lifecycle@fixture.invalid';expect(page.locator('[data-chat-use-consent]')).to_have_count(0);checks.append('changed live fixture account rejected before model turn; registered identity not silently replaced');page.screenshot(path=str(case/'changed-account-blocked.png'));control(readEmail='')
  assert not errors and not external,(errors,external);(case/'agent-lifecycle-evidence.json').write_text(json.dumps({'checks':checks,'extraFixtureTurns':len(turns())-baseline,'accountFailureCode':t.get('errorCode'),'noActualAccountOAuthOrInference':True,'windowsExecuted':False},indent=2));print('PASS actual Agent lifecycle renderer '+str(case),flush=True);browser.close()
except BaseException:
 try:page.screenshot(path=str(case/'lifecycle-failure.png'));print('SAFE FAILURE '+json.dumps({'project':state().get('projectId'),'toast':page.locator('#toast').inner_text(),'pageErrors':errors}),flush=True)
 except Exception:pass
 raise
finally:control(holdAccount=False,readEmail='');stop()
