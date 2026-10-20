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
  page=browser.new_page(viewport={'width':1440,'height':1000});page.add_init_script('''const ownedFetch=fetch;globalThis.fetch=async(...args)=>{let body;try{body=JSON.parse(args[1]?.body||'{}');}catch{}if(globalThis.__draftDelayOnce&&body?.op==='invoke'&&body.endpoint==='helperGlobal'&&body.input?.action==='draft'){const ms=globalThis.__draftDelayOnce;globalThis.__draftDelayOnce=0;globalThis.__draftDelayed=true;await new Promise(r=>setTimeout(r,ms));}return ownedFetch(...args);};''');page.on('pageerror',lambda error:errors.append(str(error)))
  def route(request):
   if request.request.url.startswith(origin) or request.request.url.startswith('data:'):request.continue_()
   else:external.append(request.request.url);request.abort()
  page.route('**/*',route);invocations=[]
  page.on('request',lambda request:invocations.append(request.post_data_json['endpoint']) if request.url.endswith('/api/request') and request.post_data_json.get('op')=='invoke' else None)
  page.goto(url);expect(page.locator('.welcome')).to_have_attribute('aria-busy','false');expect(page.locator('#later')).to_be_enabled();page.screenshot(path=str(root/'startup.png'))
  page.locator('#connect').click();dialog=page.get_by_role('dialog',name='Agent 추가',exact=True);expect(dialog.locator('[data-mcp-panel]')).to_have_count(0);page.screenshot(path=str(root/'v508-agent-choices.png'));dialog.get_by_role('button',name='Codex',exact=True).click();expect(dialog.locator('[data-cli-login]')).to_be_enabled();assert not requests();dialog.locator('[data-connection-cancel]').click();expect(dialog).to_have_count(0)
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
  page.locator('#add-helper').click();creator=page.locator('[data-v508-helper]');creator.locator('#participant-name').fill('Second owned Helper');creator.locator('#participant-description').fill('Independent second conversation');creator.locator('button[type=submit]').click();expect(creator).to_have_count(0);other=next(value for value in page.locator('.home-side [data-helper]').evaluate_all('(es)=>es.map(e=>e.dataset.helper)') if value!=helper)
  card=open_helper(helper);send=card.locator('[data-global-send]');expect(send).to_be_enabled();expect(card.locator('textarea')).to_have_attribute('rows','1');expect(card.locator('form')).to_have_class('helper-chat-compose')
  forbidden='[data-global-prepare],[data-global-save],[data-global-discard],[data-global-common],[data-global-agent],[data-global-status],[data-global-history-older],[data-global-stop],[data-global-agent-settings]'
  expect(card.locator(forbidden)).to_have_count(0);fresh_rect=card.locator('form').bounding_box();button_rect=send.bounding_box();assert abs(card.locator('.messages').bounding_box()['height']-108)<1
  page.screenshot(path=str(root/'v508-chat-fresh.png'))
  def wait_state(wanted):
   for _ in range(700):
    value=state()['helperAgents']['turns'].get(helper,{})
    if value.get('state')==wanted:return value
    page.wait_for_timeout(30)
   print('WAIT_FAILURE_BODY',page.locator('body').inner_text()[-2000:],flush=True);page.screenshot(path=str(root/'failure.png'));raise AssertionError('owned Helper did not reach '+wanted)
  def wait_saved(text,id=None):
   id=id or helper
   profile=storage/'helper-presentations'/(hashlib.sha256(id.encode()).hexdigest()+'.json')
   for _ in range(300):
    if profile.exists() and json.loads(profile.read_text()).get('globalDraft')==text:return
    page.wait_for_timeout(20)
   raise AssertionError('automatic draft not saved')
  card.locator('textarea').fill('한글 초안 자동 보관');wait_saved('한글 초안 자동 보관');assert not requests();card.locator('[data-close]').click();card=open_helper(helper);expect(card.locator('textarea')).to_have_value('한글 초안 자동 보관')
  card.locator('textarea').fill('첫 Helper 전환 입력');card=open_helper(other);card.locator('textarea').fill('둘째 Helper 별도 입력');card=open_helper(helper);expect(card.locator('textarea')).to_have_value('첫 Helper 전환 입력');wait_saved('첫 Helper 전환 입력');wait_saved('둘째 Helper 별도 입력',other)
  page.evaluate('globalThis.__draftDelayOnce=500');card.locator('textarea').fill('가');page.wait_for_function('()=>globalThis.__draftDelayed===true');card.locator('textarea').fill('가나다라 마지막');wait_saved('가나다라 마지막');assert not requests()
  profile=storage/'helper-presentations'/(hashlib.sha256(helper.encode()).hexdigest()+'.json');stored=json.loads(profile.read_text());stored['globalDraft']='다른 창의 저장 입력';stored['description']='CONCURRENT metadata retained';original=json.dumps(stored,ensure_ascii=False);profile.write_text(original)
  card.locator('textarea').fill('내 미저장 입력');conflict=page.get_by_role('dialog',name='보관된 입력이 바뀌었어요',exact=True);expect(conflict).to_be_visible();assert profile.read_text()==original;page.screenshot(path=str(root/'draft-conflict-choice.png'));conflict.locator('[data-keep-saved]').click();expect(card.locator('textarea')).to_have_value('다른 창의 저장 입력');assert profile.read_text()==original
  stored['globalDraft']='또 바뀐 저장 입력';original=json.dumps(stored,ensure_ascii=False);profile.write_text(original);card.locator('textarea').fill('명시적으로 선택한 내 입력');expect(conflict).to_be_visible();assert profile.read_text()==original;conflict.locator('[data-close]').click();card.locator('textarea').fill('명시적으로 선택한 최종 입력');expect(conflict).to_be_visible();conflict.locator('[data-keep-mine]').click();wait_saved('명시적으로 선택한 최종 입력');assert json.loads(profile.read_text())['description']=='CONCURRENT metadata retained';assert not requests();page.screenshot(path=str(root/'draft-conflict-resolved.png'))
  card.locator('textarea').evaluate("e=>e.dispatchEvent(new CompositionEvent('compositionstart',{bubbles:true}))");card.locator('textarea').fill('한글 입력 조합');card.locator('form').evaluate('e=>e.requestSubmit()');page.wait_for_timeout(250);assert not requests();card.locator('textarea').evaluate("e=>e.dispatchEvent(new CompositionEvent('compositionend',{bubbles:true}))");wait_saved('한글 입력 조합')
  def send_message(message):
   card.locator('textarea').fill(message);expect(card.locator('[data-global-send]')).to_have_text('보내기');card.locator('[data-global-send]').click();expect(page.locator('[data-global-approval]')).to_have_count(0)
  card.locator('textarea').fill('hello-global');card.locator('textarea').press('Shift+Enter');expect(card.locator('textarea')).to_have_value('hello-global\n');card.locator('textarea').fill('hello-global');card.locator('textarea').press('Enter');wait_state('completed');expect(card.locator('.messages')).to_contain_text('OWNED GLOBAL HTTP FIXTURE');assert len(requests())==1;wait_saved('');page.screenshot(path=str(root/'v508-chat-reply.png'))
  # Reopen without typing or sending: project presentation updates must not erase global history.
  count=len(requests());card.locator('[data-close]').click();card=open_helper(helper);expect(card.locator('.messages')).to_contain_text('hello-global');expect(card.locator('.messages')).to_contain_text('OWNED GLOBAL HTTP FIXTURE');page.wait_for_timeout(200);assert len(requests())==count;page.screenshot(path=str(root/'reopened-history.png'))
  card=open_helper(other);expect(card.locator('.messages')).not_to_contain_text('hello-global');card=open_helper(helper);expect(card.locator('.messages')).to_contain_text('hello-global');assert len(requests())==count
  send_message('fail-global');row=wait_state('error');assert row['output']=='' and row['answerReceived'] is False;expect(card.locator('textarea')).to_have_value('');wait_saved('');expect(card.locator('[data-global-send]')).to_have_text('재시도');expect(card.locator('.messages')).to_contain_text('fail-global');expect(card.locator('.messages')).to_contain_text('provider-http-error');page.screenshot(path=str(root/'safe-request-failure.png'))
  (root/'allow-retry').write_text('owned');card.locator('[data-global-send]').click();wait_state('completed');expect(card.locator('.messages')).to_contain_text('OWNED GLOBAL HTTP FIXTURE');assert len(requests())==3;wait_saved('')
  send_message('wait-global');wait_state('running');stop=card.locator('[data-global-send]');expect(stop).to_have_text('중지');running_rect=stop.bounding_box();assert abs(running_rect['width']-button_rect['width'])<1 and abs(running_rect['height']-button_rect['height'])<1;page.screenshot(path=str(root/'v508-chat-running.png'))
  card.locator('textarea').fill('UNSENT while original request runs');stop.click();wait_state('cancelled');expect(card.locator('textarea')).to_have_value('UNSENT while original request runs');(root/'release').write_text('');wait_saved('UNSENT while original request runs');card.locator('[data-close]').click()
  page.locator('#new-project').click();create=page.get_by_role('dialog',name='새 프로젝트 만들기',exact=True);create.locator('#project-name').fill('Not submitted owned draft');create.locator('[data-project-helper="'+helper+'"]').click();expect(create.locator('#project-helper-roster')).to_contain_text('Owned new Helper');create.locator('[data-project-tab="packs"]').click();expect(create.locator('#project-packs-panel')).to_be_visible();expect(create.locator('#recommend')).to_be_disabled();page.screenshot(path=str(root/'v508-create-packs.png'));create.locator('[data-project-tab="project"]').click();expect(create.locator('#project-name')).to_have_value('Not submitted owned draft');page.screenshot(path=str(root/'v508-create-project.png'));create.locator('[data-project-cancel]').click();page.locator('#new-project').click();expect(page.locator('#project-name')).to_have_value('Not submitted owned draft');page.locator('[data-project-cancel]').click();assert state()['projectId']==''
  page.evaluate('()=>globalThis.confectoryFlushPresentation()');page.close();os.killpg(host.pid,signal.SIGTERM);host.wait(timeout=15);log.close();log=log_path.open('w');host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  for _ in range(600):
   urls=[line.split(' ',1)[1] for line in log_path.read_text().splitlines() if line.startswith('CONFECTORY_WEB_UI ')]
   if urls:url=urls[-1];break
   assert host.poll() is None;time.sleep(.05)
  else:raise AssertionError('owned engine restart timeout')
  origin,token=url.split('/#');page=browser.new_page(viewport={'width':1440,'height':1000});page.add_init_script('''const ownedFetch=fetch;let delayed=false;globalThis.fetch=async(...args)=>{let body;try{body=JSON.parse(args[1]?.body||'{}');}catch{}if(!delayed&&body?.endpoint==='helperGlobal'&&body.input?.action==='conversation'){delayed=true;globalThis.__conversationDelayed=true;await new Promise(r=>setTimeout(r,350));}return ownedFetch(...args);};''');page.on('pageerror',lambda error:errors.append(str(error)));page.route('**/*',route);page.goto(url);expect(page.locator('.home-grid')).to_be_visible();card=open_helper(helper);expect(card.locator('textarea')).to_have_value('UNSENT while original request runs')
  page.wait_for_function('globalThis.__conversationDelayed');card=open_helper(other);page.wait_for_timeout(450);expect(card.locator('.messages')).not_to_contain_text('wait-global');expect(card.locator('textarea')).to_have_value('둘째 Helper 별도 입력');card=open_helper(helper);expect(card.locator('.messages')).to_contain_text('wait-global');assert len(requests())==4

  for _ in range(300):
   if state()['helperAgents']['turns'].get(helper,{}).get('recordCount')==4:break
   page.wait_for_timeout(20)
  else:raise AssertionError('owned history not loaded after engine restart')
  card.locator('.messages').evaluate("e=>{e.scrollTop=0;e.dispatchEvent(new WheelEvent('wheel',{deltaY:-100}));}");expect(card.locator('.messages')).to_contain_text('OWNED GLOBAL HTTP FIXTURE');assert len(requests())==4;page.screenshot(path=str(root/'global-cold-history.png'))
  (root/'release').unlink();(root/'waiting').unlink(missing_ok=True);send_message('wait-global');wait_state('running')
  for _ in range(200):
   if (root/'waiting').exists():break
   page.wait_for_timeout(10)
  assert (root/'waiting').exists();journal=storage/'helper-conversations'/(hashlib.sha256(helper.encode()).hexdigest()+'.json');changed=json.loads(journal.read_text());changed['ownedConcurrentEdit']=True;original=json.dumps(changed);journal.write_text(original);(root/'release').write_text('')
  row=wait_state('completed');assert row['historyError'];expect(page.get_by_text('받은 응답은 유지하지만 대화 기록을 보관하지 못했어요. 저장 상태를 확인하세요.',exact=True)).to_be_visible();expect(card.locator('.messages')).to_contain_text('OWNED GLOBAL HTTP FIXTURE');assert journal.read_text()==original and len(requests())==5
  assert not errors,errors;assert not external,external;assert not (root/'error').exists(),(root/'error').read_text() if (root/'error').exists() else ''
  evidence={'root':str(root),'checks':['real startup readiness; internal Codex setup without external connector panel','registered Agent-only sidebar','Agent-owned Helper creation without project','v508 Helper-add input preservation at 1440/900/600; group/favorite interactions','normal explicit Send without duplicate approval, original DOM/108px message area, original Send/stop dimensions, Korean composition guard, automatic draft persistence','Enter sends/ShiftEnter newline, actual Responses reply, accepted input cleared, explicit retry, safe HTTP failure, original request cancel, reopen-only history and two-Helper separation','delayed history response after Helper switch cannot render into the other Helper; actual engine restart, independent two-Helper drafts, typing during delayed save, both CAS conflict choices, same-message retry, scroll history without replay','v508 project/packs tabs, real Helper roster, no project submission'],'historyCasPreservesOriginalAndResponse':True,'httpRequests':len(requests()),'pageErrors':errors,'externalRequests':external,'projectId':state()['projectId']}
  (root/'evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2));print('PASS actual global Helper UI: '+json.dumps(evidence,ensure_ascii=False));browser.close()
except BaseException:
 print("UI_ROOT",str(root),flush=True)
 try:
  print("FAILED_STATE",json.dumps(state().get("helperAgents",{}),ensure_ascii=False)[-5000:]);print("FAILED_BODY",page.locator("body").inner_text()[-1800:]);page.screenshot(path=str(root/"failure.png"))
 except Exception:pass
 print("UI_ERRORS",errors,"EXTERNAL",external,"HOST",log_path.read_text()[-2500:]);raise
finally:
 if host.poll() is None:os.killpg(host.pid,signal.SIGTERM);host.wait(timeout=15)
 if fixture.poll() is None:fixture.terminate();fixture.wait(timeout=10)
 log.close()
