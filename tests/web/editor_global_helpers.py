"""Actual production EditorHome UI + owned Responses HTTP; no service/account/project creation."""
import hashlib, json, os, pathlib, signal, subprocess, sys, tempfile, time, urllib.request
from playwright.sync_api import sync_playwright, expect

expect.set_options(timeout=30000)
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text())
root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-global-ui-'));storage=root/'storage'
fixture=subprocess.Popen(['python3',str(repo/'tests/protocol/global_helper_http.py'),str(root)],stdout=subprocess.PIPE,text=True)
endpoint=fixture.stdout.readline().strip();assert endpoint.startswith('http://127.0.0.1:')
env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_ENTRY_STORAGE=str(storage),CONFECTORY_HOME_STORAGE=str(storage),CONFECTORY_MCP_DIRECTORY=str(root/'instances'),CONFECTORY_UI_TRACE='1');env.pop('CONFECTORY_WEB_PROJECT',None)
if env.get('CONFECTORY_DOTNET'):env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH']
log_path=root/'host.log';log=log_path.open('w');host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
errors=[];external=[];evidence={}
try:
 for _ in range(600):
  urls=[line.split(' ',1)[1] for line in log_path.read_text().splitlines() if line.startswith('CONFECTORY_WEB_UI ')]
  if urls:url=urls[-1];break
  assert host.poll() is None,log_path.read_text();time.sleep(.1)
 else:raise AssertionError('production host startup timeout')
 origin,token=url.split('/#')
 def state():
  def send(body):
   request=urllib.request.Request(origin+'/api/request',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':token})
   with urllib.request.urlopen(request,timeout=20) as response:return json.load(response)
  for _ in range(400):
   mounted=send({'op':'mount'})
   if mounted.get('error',{}).get('code')=='busy':time.sleep(.01);continue
   assert mounted['ok'],mounted;break
  else:raise AssertionError('read-only mount busy')
  try:return mounted['state']
  finally:assert send({'op':'dispose','view':mounted['view']})['ok']
 def requests():return [json.loads(line) for line in (root/'requests.jsonl').read_text().splitlines()] if (root/'requests.jsonl').exists() else []
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu'])
  page=browser.new_page(viewport={'width':1440,'height':1000});page.on('pageerror',lambda error:errors.append(str(error)))
  def route(request):
   if request.request.url.startswith(origin) or request.request.url.startswith('data:'):request.continue_()
   else:external.append(request.request.url);request.abort()
  page.route('**/*',route);invocations=[]
  page.on('request',lambda request:invocations.append(request.post_data_json['endpoint']) if request.url.endswith('/api/request') and request.post_data_json.get('op')=='invoke' else None)
  page.goto(url);expect(page.locator('.welcome')).to_have_attribute('aria-busy','false');expect(page.locator('#later')).to_be_enabled();page.screenshot(path=str(root/'startup.png'))
  page.locator('#connect').click();dialog=page.get_by_role('dialog',name='Agent 추가',exact=True);expect(dialog.locator('[data-mcp-panel]')).to_have_count(0);page.screenshot(path=str(root/'v508-agent-choices.png'));dialog.get_by_role('button',name='Codex',exact=True).click();expect(dialog.locator('[data-connection-discovery]')).to_be_visible();assert not requests();dialog.locator('[data-connection-cancel]').click();expect(dialog).to_have_count(0)
  page.locator('#later').click();expect(page.locator('.home-grid')).to_be_visible();expect(page.locator('.startup-flight-layer')).to_have_count(0);expect(page.locator('[data-participant-toggle="agent"]')).to_have_attribute('aria-label','AGENT (0)');expect(page.locator('.home-side [data-agent]')).to_have_count(0);page.screenshot(path=str(root/'v508-home.png'))
  page.locator('#add-helper').click();dialog=page.get_by_role('dialog',name='Agent 추가',exact=True);expect(page.locator('[data-v508-helper]')).to_have_count(0);dialog.locator('[data-connection-cancel]').click();expect(dialog).to_have_count(0)
  page.locator('#add-agent').click();dialog=page.get_by_role('dialog',name='Agent 추가',exact=True);dialog.get_by_role('button',name='OpenAI Responses',exact=True).click();expect(dialog.locator('[data-connection-field="model"]')).to_be_visible();expect(dialog.locator('[data-connection-error]')).to_be_hidden();expect(dialog.locator('[data-mcp-panel]')).to_have_count(0)
  for key,value in [('model','owned-global-http'),('endpoint',endpoint),('credentialReference','')]:dialog.locator('[data-connection-field="'+key+'"]').fill(value)
  page.screenshot(path=str(root/'v508-responses-settings.png'));dialog.locator('[data-agent-register]').click();expect(dialog.locator('[data-agent-registration-state]')).to_contain_text('Agent 등록됨');assert not requests();actual=state();assert actual['projectId']=='' and len(actual['helperAgents']['agents'])==1 and actual['helperAgents']['agents'][0]['accountVerified'] is False
  dialog.locator('[data-connection-cancel]').click();expect(dialog).to_have_count(0);expect(page.locator('[data-participant-toggle="agent"]')).to_have_attribute('aria-label','AGENT (1)');expect(page.locator('.home-side [data-agent] .connection-dot')).to_have_attribute('aria-label','설정 등록됨 · 인증 미확인')
  page.locator('#add-helper').click();creator=page.locator('[data-v508-helper]');expect(creator.locator('.helper-create-artwork')).to_be_visible();expect(creator.locator('.helper-agent-dropdown summary')).to_contain_text('OpenAI Responses');expect(creator.get_by_text('나중에 배정',exact=True)).to_have_count(0)
  page.screenshot(path=str(root/'v508-helper-add.png'));creator.locator('#participant-name').fill('Owned new Helper');creator.locator('#participant-short-description').fill('Global planning');creator.locator('#participant-description').fill('Independent calm global Helper');creator.locator('[data-close]').click();page.locator('#add-helper').click();creator=page.locator('[data-v508-helper]');expect(creator.locator('#participant-name')).to_have_value('Owned new Helper');expect(creator.locator('#participant-description')).to_have_value('Independent calm global Helper')
  for width,height in [(900,760),(600,800)]:
   page.set_viewport_size({'width':width,'height':height});page.screenshot(path=str(root/f'v508-helper-{width}.png'));box=creator.bounding_box();assert box and box['x']>=0 and box['x']+box['width']<=width+1,box;assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
  page.set_viewport_size({'width':1440,'height':1000});creator.locator('button[type=submit]').click();expect(creator).to_have_count(0);expect(page.locator('.home-side [data-helper]')).to_have_count(1);helper=page.locator('.home-side [data-helper]').get_attribute('data-helper');assert helper.startswith('helper-') and state()['helperAgents']['assignments'][helper]=='Confectory.Agent.Responses::Connection'
  star=page.locator('[data-favorite-helper="'+helper+'"]');star.click();expect(star).to_have_attribute('aria-pressed','true');expect(page.locator('.participant-expanded-card')).to_have_count(0);toggle=page.locator('.helper-group-toggle');toggle.click();expect(toggle).to_have_attribute('aria-expanded','false');toggle.click();expect(toggle).to_have_attribute('aria-expanded','true');page.screenshot(path=str(root/'registered-helper-home.png'))
  def open_helper(id):
   page.locator('.home-side [data-helper="'+id+'"]').first.click();return page.locator('.participant-expanded-card[data-helper-id="'+id+'"]')
  card=open_helper(helper);expect(card.locator('[data-global-prepare]')).to_be_enabled();card.locator('textarea').fill('hello-global');card.locator('[data-global-save]').click();expect(card.locator('[data-global-save]')).to_be_enabled();assert not requests()
  def prepare(message):
   card.locator('textarea').fill(message);card.locator('[data-global-prepare]').click();approval=page.locator('[data-global-approval]');expect(approval).to_be_visible();expect(approval.locator('[data-global-start]')).to_be_disabled();return approval
  def approve(approval):
   for item in approval.locator('[data-global-permission]').all():item.check()
   expect(approval.locator('[data-global-start]')).to_be_enabled();approval.locator('[data-global-start]').click();expect(approval).to_have_count(0)
  approval=prepare('hello-global');assert not requests();preview=state()['helperAgents']['preview'];assert preview['context']['projectId']=='' and preview['context']['memory']==[];approval.locator('[data-global-review-cancel]').click();expect(card.locator('textarea')).to_have_value('hello-global')
  approval=prepare('hello-global');page.screenshot(path=str(root/'global-content-approval.png'));approve(approval);expect(card.locator('[data-global-status]')).to_have_text('전역 응답 수신');expect(card.locator('.global-helper-messages')).to_contain_text('OWNED GLOBAL HTTP FIXTURE');assert len(requests())==1
  approval=prepare('fail-global');approve(approval);expect(card.locator('[data-global-status]')).to_contain_text('전역 요청 실패');row=state()['helperAgents']['turns'][helper];assert row['output']=='' and row['answerReceived'] is False
  approval=prepare('wait-global');approve(approval);expect(card.locator('[data-global-stop]')).to_be_enabled();card.locator('textarea').fill('UNSENT while original request runs');card.locator('[data-global-stop]').click();expect(card.locator('[data-global-status]')).to_have_text('전역 요청 취소됨');expect(card.locator('textarea')).to_have_value('UNSENT while original request runs');(root/'release').write_text('');card.locator('[data-global-save]').click();expect(card.locator('[data-global-save]')).to_be_enabled();card.locator('[data-close]').click()
  page.locator('#new-project').click();create=page.get_by_role('dialog',name='새 프로젝트 만들기',exact=True);create.locator('#project-name').fill('Not submitted owned draft');create.locator('[data-project-helper="'+helper+'"]').click();expect(create.locator('#project-helper-roster')).to_contain_text('Owned new Helper');create.locator('[data-project-tab="packs"]').click();expect(create.locator('#project-packs-panel')).to_be_visible();expect(create.locator('#recommend')).to_be_disabled();page.screenshot(path=str(root/'v508-create-packs.png'));create.locator('[data-project-tab="project"]').click();expect(create.locator('#project-name')).to_have_value('Not submitted owned draft');page.screenshot(path=str(root/'v508-create-project.png'));create.locator('[data-project-cancel]').click();page.locator('#new-project').click();expect(page.locator('#project-name')).to_have_value('Not submitted owned draft');page.locator('[data-project-cancel]').click();assert state()['projectId']==''
  page.reload();expect(page.locator('.home-grid')).to_be_visible();card=open_helper(helper);expect(card.locator('textarea')).to_have_value('UNSENT while original request runs');expect(card.locator('[data-global-record]')).to_have_count(2);assert state()['helperAgents']['turns'][helper]['recordCount']==3;card.locator('[data-global-history-older]').click();expect(card.locator('.global-helper-messages')).to_contain_text('OWNED GLOBAL HTTP FIXTURE');assert len(requests())==3
  page.screenshot(path=str(root/'global-cold-history.png'))
  (root/'release').unlink();(root/'waiting').unlink(missing_ok=True);approval=prepare('wait-global');approve(approval)
  for _ in range(200):
   if (root/'waiting').exists():break
   time.sleep(.01)
  assert (root/'waiting').exists();journal=storage/'helper-conversations'/(hashlib.sha256(helper.encode()).hexdigest()+'.json');changed=json.loads(journal.read_text());changed['ownedConcurrentEdit']=True;original=json.dumps(changed);journal.write_text(original);(root/'release').write_text('')
  expect(card.locator('[data-global-status]')).to_contain_text('기록 저장');expect(card.locator('[data-current-global-output]')).to_contain_text('OWNED GLOBAL HTTP FIXTURE');assert journal.read_text()==original and len(requests())==4
  assert not errors,errors;assert not external,external;assert not (root/'error').exists(),(root/'error').read_text() if (root/'error').exists() else ''
  evidence={'root':str(root),'checks':['real startup readiness; internal Codex setup without external connector panel','registered Agent-only sidebar','Agent-owned Helper creation without project','v508 Helper-add input preservation at 1440/900/600; group/favorite interactions','approval cancel and explicit consent','actual Responses reply, HTTP failure, original request cancel','draft/history reload without provider replay','v508 project/packs tabs, real Helper roster, no project submission'],'historyCasPreservesOriginalAndResponse':True,'httpRequests':len(requests()),'pageErrors':errors,'externalRequests':external,'projectId':state()['projectId']}
  (root/'evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2));print('PASS actual global Helper UI: '+json.dumps(evidence,ensure_ascii=False));browser.close()
except BaseException:
 print("UI_ERRORS",errors,"EXTERNAL",external,"HOST",log_path.read_text()[-2500:]);raise
finally:
 if host.poll() is None:os.killpg(host.pid,signal.SIGTERM);host.wait(timeout=15)
 if fixture.poll() is None:fixture.terminate();fixture.wait(timeout=10)
 log.close()
