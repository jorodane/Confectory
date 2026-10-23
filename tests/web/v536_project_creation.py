"""v536 creation surface/real sidebar drop/placement/restart over an isolated native contract.
The fixture supplies only an approved parent folder; no native Windows picker QA.
"""
from editor_navigation import goto_editor
import json,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
expect.set_options(timeout=30000)
project_chat=False;chat_provider=None
if project_chat:
 from project_chat_contract import OwnedChat
 chat_provider=OwnedChat()
repo=pathlib.Path(sys.argv[1]).resolve();root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-create-responsive-'));print('FIXTURE '+str(root),flush=True)
owned=root/'engine';editor=owned/'examples/editor-home';shutil.copytree(repo/'examples/editor-home',editor,ignore=shutil.ignore_patterns('.confectory'));(owned/'targets/dotnet').mkdir(parents=True);(owned/'targets/dotnet/pack.cpack').write_text('pack Owned.Marker version "1" {standalone false;}')
# Production model still uses the real repository/template. Only the native parent-selection boundary is supplied by the fixture.
pack=root/'browser-host';shutil.copytree(repo/'packs/browser-host',pack)
for p in editor.glob('*.cpack'):p.write_text(p.read_text().replace('../../',str(repo)+'/').replace(json.dumps(str(repo/'packs/browser-host/pack.cpack')),json.dumps(str(pack/'pack.cpack'))))
if project_chat:
 tools=root/'development-tools';shutil.copytree(repo/'packs/development-tools',tools)
 for p in editor.glob('*.cpack'):p.write_text(p.read_text().replace(json.dumps(str(repo/'packs/development-tools/pack.cpack')),json.dumps(str(tools/'pack.cpack'))))
 failure=root/'fail-once';failure.write_text('owned')
 p=tools/'Open.csbody';p.write_text('if(System.IO.File.Exists('+json.dumps(str(failure))+')){System.IO.File.Delete('+json.dumps(str(failure))+');throw new InvalidOperationException("owned-secret-must-not-leak");}\n'+p.read_text())
p=pack/'ServeBody.celem';p.write_text(p.read_text().replace('body common','import Confectory.WebUI::NativeRequest as NativeRequest (string,string,string) -> string;\nbody common'))
p=pack/'Serve.csbody';s=p.read_text();needle='if(request.Url.AbsolutePath=="/api/request")';assert needle in s
branch='''if(request.Url.AbsolutePath=="/fixture/native-create"){
   if(request.Headers["X-Confectory-Session"]!=session||request.HttpMethod!="POST"||request.ContentLength64<0||request.ContentLength64>8192)throw new UnauthorizedAccessException();
   using var read=new System.IO.StreamReader(request.InputStream);var value=System.Text.Json.Nodes.JsonNode.Parse(read.ReadToEnd())!.AsObject();foreach(var field in value)if(field.Key is not ("title" or "description" or "proposalId"))throw new ArgumentException("Fixture native selection only");value["directory"]=PARENT;
   var watch=System.Diagnostics.Stopwatch.StartNew();string reply=calls.NativeRequest.Invoke(owner,"create-project",value.ToJsonString());System.IO.File.AppendAllText(LOG,new System.Text.Json.Nodes.JsonObject{["title"]=value["title"]!.DeepClone(),["milliseconds"]=watch.ElapsedMilliseconds,["ok"]=System.Text.Json.Nodes.JsonNode.Parse(reply)!["ok"]!.DeepClone()}.ToJsonString()+"\\n");bytes=System.Text.Encoding.UTF8.GetBytes(reply);response.ContentType="application/json";
  }else '''.replace('PARENT',json.dumps(str(root/'projects'))).replace('LOG',json.dumps(str(root/'native-calls.jsonl')))
p.write_text(s.replace(needle,branch+needle,1));(root/'projects').mkdir()
env=os.environ.copy();env.pop('CONFECTORY_WEB_PROJECT',None);env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(root/'profile'),CONFECTORY_ENTRY_STORAGE=str(root/'profile'),CONFECTORY_MCP_DIRECTORY=str(root/'instances'),CONFECTORY_UI_TRACE='1',CONFECTORY_DOTNET=env.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet'));env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH']
with (root/'build.json').open('w') as output,(root/'build.err').open('w') as error:built=subprocess.run([env['CONFECTORY_DOTNET'],str(repo/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),'build',str(editor/'project.cpack'),'linux'],env=env,cwd=repo,stdout=output,stderr=error,timeout=180)
report=json.loads((root/'build.json').read_text());assert built.returncode==0 and report.get('tool',{}).get('ok'),report.get('diagnostics')
log_path=root/'host.log';log=log_path.open('w');host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);errors=[];evidence={}
try:
 for _ in range(600):
  urls=[l.split(' ',1)[1] for l in log_path.read_text().splitlines() if l.startswith('CONFECTORY_WEB_UI ')]
  if urls:url=urls[-1];break
  assert host.poll() is None,log_path.read_text()[-1000:];time.sleep(.05)
 else:raise AssertionError('startup timeout')
 origin,token=url.split('/#')
 def state():
  def send(body):return json.load(urllib.request.urlopen(urllib.request.Request(origin+'/api/request',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':token}),timeout=20))
  for _ in range(400):
   m=send({'op':'mount'})
   if m.get('error',{}).get('code')=='busy':time.sleep(.01);continue
   assert m['ok'],m;break
  else:raise AssertionError('mount busy')
  try:return m['state']
  finally:assert send({'op':'dispose','view':m['view']})['ok']
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu']);page=browser.new_page(viewport={'width':1440,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)))
  # Browser transport stays production. This emulates only the native API that is absent on Linux.
  page.add_init_script('''globalThis.__creationReply='normal';globalThis.confectoryWebUI={async chooseProjectParent(){if(globalThis.__parentCancel)return {ok:true,cancelled:true};return {ok:true,parent:'owned-parent',label:'Owned fixture projects'};},async createProject(title,description,parent,proposalId){if(globalThis.__creationReply==='cancel')return {ok:true,cancelled:true};if(globalThis.__creationReply==='fail')return {ok:false,error:{code:'owned-create-failure'}};if(globalThis.__holdNative){globalThis.__nativeWaiting=true;await new Promise(resolve=>globalThis.__releaseNative=resolve);globalThis.__holdNative=false;}const token=sessionStorage.getItem('confectory.webui.session');return (await fetch('/fixture/native-create',{method:'POST',headers:{'Content-Type':'application/json','X-Confectory-Session':token},body:JSON.stringify({title,description,...(proposalId?{proposalId}:{})})})).json();}};''')
  goto_editor(page,url);page.locator('#add-agent').click();dialog=page.get_by_role('dialog',name='Agent 추가',exact=True);dialog.get_by_role('button',name='OpenAI Responses',exact=True).click()
  for name,value in [('model','owned-no-inference'),('endpoint',chat_provider.endpoint if chat_provider else 'http://127.0.0.1:9/responses'),('credentialReference','')]:dialog.locator('[data-connection-field="'+name+'"]').fill(value)
  dialog.locator('[data-agent-register]').click();expect(dialog.locator('[data-agent-registration-state]')).to_contain_text('Agent 등록됨');dialog.locator('[data-connection-cancel]').click();assert state()['helpers']==[]
  def create(title,helper=None):
   page.locator('#new-project').click();modal=page.get_by_role('dialog',name='새 프로젝트 만들기',exact=True);modal.locator('#project-name').fill(title);modal.locator('#project-desc').fill('Owned creation responsiveness fixture');
   if helper:modal.locator('[data-project-helper="'+helper+'"]').click()
   modal.locator('button[type=submit]').click();return modal

  checks=[];external=[];plan_id=None;fail_plan=False;plan_failures=0
  def checked(message):checks.append(message);(root/'progress.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2));print('PASS '+message,flush=True)
  def calls():return [json.loads(x) for x in (root/'native-calls.jsonl').read_text().splitlines()] if (root/'native-calls.jsonl').exists() else []
  def route(r):
   global plan_id,fail_plan,plan_failures
   if not r.request.url.startswith(origin+'/'):external.append(r.request.url);r.abort();return
   body=r.request.post_data_json if r.request.method=='POST' else None
   if isinstance(body,dict) and body.get('op')=='invoke' and body.get('endpoint')=='projectHelpers' and body.get('input',{}).get('action')=='plan' and fail_plan:plan_id=body['requestId']
   if isinstance(body,dict) and body.get('op')=='update' and plan_id:
    response=r.fetch();payload=response.json()
    for result in payload.get('results',[]):
     if result['requestId']==plan_id and result.get('ok'):
      plan_id=None;fail_plan=False;plan_failures+=1;result['ok']=False;result.pop('result',None);result['error']={'code':'consumer_error'}
    r.fulfill(response=response,json=payload);return
   r.continue_()
  page.route('**/*',route)
  def surface(title='새 프로젝트 만들기'):return page.get_by_role('dialog',name=title,exact=True)
  def unblocked():
   assert not page.locator('#app').evaluate('e=>e.inert');assert page.locator('#app .topbar,#app .home-main,#app .work-main-column,#app #workspace,#app .chatbar,#app .coworker-bottom-dock').evaluate_all('(els)=>els.every(e=>!e.inert)');assert not page.locator('body').evaluate('e=>e.classList.contains("project-create-open")');assert page.locator('.project-create-host').count()==0
  def blocked(r):
   expect(r).to_have_attribute('data-reference-version','536');assert not page.locator('#app').evaluate('e=>e.inert');assert page.locator('#app .topbar,#app .home-main,#app .work-main-column,#app #workspace,#app .chatbar,#app .coworker-bottom-dock').evaluate_all('(els)=>els.every(e=>e.inert)');assert not page.locator('#home-participants').evaluate('e=>e.inert')
  # Hold only the native selection boundary, before any production creation call.
  page.evaluate('globalThis.__holdNative=true');first=create('Owned Created');page.wait_for_function('()=>globalThis.__nativeWaiting===true');first.locator('form').evaluate('e=>{e.requestSubmit();e.requestSubmit()}');assert not calls();blocked(first);page.evaluate('globalThis.__releaseNative()');expect(page.locator('.work-body')).to_be_visible();expect(first).to_have_count(0);unblocked();first_state=state();helper=first_state['mainHelperId'];first_project=first_state['projectId'];assert first_state['projectHelperIds']==[helper] and len(first_state['helpers'])==1 and len(calls())==1;assert first_state['helperAgents']['assignments'][helper]=='Confectory.Agent.Responses::Connection';first_bytes=(root/'projects/Owned Created/project.cproj').read_bytes();checked('실제 생성 영수증·자동 Agent 소속 Helper 배치와 반복 제출 차단, 생성 뒤 central/overlay/inert 해제 및 UI 반응')
  page.locator('.home-side [data-helper]').first.hover();expect(page.locator('[role=tooltip]')).to_be_visible();page.locator('.brand').click();expect(page.locator('#new-project')).to_be_enabled();page.locator('#add-helper').click();creator=page.locator('[data-reference-version="536"]');creator.locator('#participant-name').fill('전역 후보');creator.locator('#participant-description').fill('프로젝트 밖에서 만든 실제 격리 Helper');creator.locator('button[type=submit]').click();expect(creator).to_have_count(0);other=next(h['id'] for h in state()['helpers'] if h['id']!=helper);assert len(state()['helpers'])==2
  page.locator('.home-side [data-helper="'+helper+'"]').first.click();card=page.locator('.participant-expanded-card[data-helper-id="'+helper+'"]');card.locator('textarea').fill('다른 프로젝트로 가져가지 않을 전역 입력 한글');page.evaluate('async()=>await confectoryFlushPresentation()');profile=root/'profile/helper-presentations'/(__import__('hashlib').sha256(helper.encode()).hexdigest()+'.json')
  for _ in range(200):
   if profile.exists() and json.loads(profile.read_text())['globalDraft']=='다른 프로젝트로 가져가지 않을 전역 입력 한글':break
   page.wait_for_timeout(10)
  assert json.loads(profile.read_text())['globalDraft']=='다른 프로젝트로 가져가지 않을 전역 입력 한글'
  page.locator('#new-project').click();second=surface();blocked(second);second.locator('#project-name').fill('Owned Selected');second.locator('#project-desc').fill('v536 source project form');side=page.locator('.home-side [data-helper="'+helper+'"]');side.drag_to(second.locator('.project-helper-slot[data-helper-drop-index="0"]'));expect(second.locator('#project-helper-roster [data-project-helper="'+helper+'"]')).to_have_count(1);assert page.locator('.participant-expanded-card').count()==0 and state()['projectId']=='';assert len(calls())==1
  # Sidebar click adds another candidate; private roster removal does not revoke anything.
  page.locator('.home-side [data-helper="'+other+'"]').first.click();expect(second.locator('#project-helper-roster [data-project-helper]')).to_have_count(2);second.locator('[data-remove-helper="'+other+'"]').click();expect(second.locator('#project-helper-roster [data-project-helper]')).to_have_count(1);assert not state()['projectId'] and len(state()['helpers'])==2;checked('실제 사이드바 HTML 드롭/클릭은 후보만 선택하며 채팅·다른 프로젝트를 열거나 Agent/배치 상태를 먼저 바꾸지 않는다')
  second.locator('#choose-parent').click();expect(second.locator('#parent')).to_contain_text('Owned fixture projects');body=second.locator('.project-create-body');before=second.locator('.project-create-footer').bounding_box();body.evaluate('e=>e.scrollTop=e.scrollHeight');after=second.locator('.project-create-footer').bounding_box();assert abs(before['y']-after['y'])<1;second.locator('#project-packs-tab').click();second.locator('#project-settings-tab').click();assert body.evaluate('e=>e.scrollTop')>0;page.screenshot(path=str(root/'v536-create-selected.png'));checked('원본 고정 탭/하단 제어·독립 본문 스크롤과 탭별 스크롤 복원, 실제 승인 부모 선택을 연결한다')
  fail_plan=True;second.locator('button[type=submit]').click();expect(page.locator('#toast')).to_contain_text('프로젝트 생성 또는 도우미 배치를 완료하지 못했어요',timeout=30000);expect(second).to_be_visible();assert plan_failures==1 and len(calls())==2;second_project=state()['projectId'];assert second_project and second_project!=first_project and not state()['projectHelperIds'];blocked(second);assert len(state()['helpers'])==2;second.locator('button[type=submit]').click();expect(second).to_have_count(0);unblocked();assert len(calls())==2 and state()['projectHelperIds']==[helper] and len(state()['helpers'])==2;assert (root/'projects/Owned Created/project.cproj').read_bytes()==first_bytes and json.loads(profile.read_text())['globalDraft']=='다른 프로젝트로 가져가지 않을 전역 입력 한글';assert state()['helperAgents']['assignments'][helper]=='Confectory.Agent.Responses::Connection';checked('생성 뒤 배치 통신 실패를 주입해도 새 화면을 안전히 차단하며 재시도는 같은 영수증의 배치만 완료하고 프로젝트/Helper를 중복 생성하지 않는다')
  expect(page.locator('.home-side [data-helper="'+helper+'"]')).to_have_count(1);expect(page.locator('.home-side [data-helper="'+other+'"]')).to_have_count(0);page.locator('#add-helper').click();placement=surface('프로젝트 도우미 배치');blocked(placement);expect(placement.locator('#project-helper-available [data-project-helper="'+other+'"]')).to_have_count(1);placement.locator('[data-remove-helper="'+helper+'"]').click();assert state()['projectHelperIds']==[helper];placement.locator('button[type=submit]').click();expect(placement).to_have_count(0);unblocked();assert state()['projectHelperIds']==[] and len(state()['helpers'])==2;expect(page.locator('.home-side [data-helper]')).to_have_count(0)
  page.locator('#add-helper').click();placement=surface('프로젝트 도우미 배치');expect(placement.locator('#project-helper-available [data-project-helper]')).to_have_count(2);placement.locator('#project-helper-available [data-project-helper="'+helper+'"]').click();placement.locator('button[type=submit]').click();expect(placement).to_have_count(0);unblocked();assert state()['projectId']==second_project and state()['projectHelperIds']==[helper] and json.loads(profile.read_text())['globalDraft']=='다른 프로젝트로 가져가지 않을 전역 입력 한글';checked('현재 프로젝트만 배치·해제하고 미배치 전역 후보는 선택 화면에서 유지한다. 다른 Helper/Agent 소속과 전역 입력은 보존한다')
  page.locator('.brand').click();expect(page.locator('.home-side [data-helper]')).to_have_count(2);page.evaluate("globalThis.__creationReply='fail'");failed=create('Rejected Before Create');expect(page.locator('#toast')).to_contain_text('owned-create-failure');blocked(failed);assert len(calls())==2;failed.locator('[data-project-cancel]').click();unblocked();page.evaluate("globalThis.__creationReply='cancel'");cancel=create('Never Created');expect(cancel.locator('button[type=submit]')).to_be_enabled();blocked(cancel);cancel.locator('[data-project-cancel]').click();unblocked();assert not (root/'projects/Never Created').exists() and len(calls())==2 and len(state()['helpers'])==2;checked('호스트 생성 실패/취소는 파일·계정·배치를 만들지 않으며 취소 후 전체 컨트롤과 선택 입력 수명을 복구한다')
  page.locator('#new-project').click();again=surface();expect(again.locator('#project-name')).to_have_value('Never Created');page.evaluate('globalThis.__parentCancel=true');path=again.locator('#parent').inner_text();again.locator('#choose-parent').click();expect(again.locator('#choose-parent')).to_be_enabled();expect(again.locator('#parent')).to_have_text(path);page.screenshot(path=str(root/'v536-create-cancel-reopen.png'));again.locator('[data-project-cancel]').click();unblocked();checked('취소·재열기에서 입력을 유지하고 native 부모 선택 취소는 기존 경로를 바꾸지 않는다')
  # Actual restart: no fixture data is copied into the production workspace.
  page.close();os.killpg(host.pid,signal.SIGTERM);host.wait(timeout=15);log.close();log_path=root/'host-restart.log';log=log_path.open('w');host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  for _ in range(600):
   urls=[l.split(' ',1)[1] for l in log_path.read_text().splitlines() if l.startswith('CONFECTORY_WEB_UI ')]
   if urls:url=urls[-1];origin,token=url.split('/#');break
   assert host.poll() is None;time.sleep(.05)
  page=browser.new_page(viewport={'width':1440,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)));page.route('**/*',route);goto_editor(page,url);expect(page.locator('[data-enter]')).to_have_count(2);page.locator('.project-card').filter(has=page.get_by_role('heading',name='Owned Selected',exact=True)).locator('[data-enter]').click();expect(page.locator('.work-body')).to_be_visible();expect(page.locator('.home-side [data-helper="'+helper+'"]')).to_have_count(1);expect(page.locator('.home-side [data-helper="'+other+'"]')).to_have_count(0);assert state()['projectId']==second_project and state()['projectHelperIds']==[helper] and len(state()['helpers'])==2;assert json.loads(profile.read_text())['globalDraft']=='다른 프로젝트로 가져가지 않을 전역 입력 한글';assert len(calls())==2;unblocked();checked('실제 재시작 뒤 두 프로젝트·전역 Helper/Agent 소속·프로젝트별 배치·전역 초안을 복원하고 자동 생성/중복 생성하지 않는다')
  assert not errors and not external,(errors,external);assert '/fixture/native-create' not in (repo/'packs/browser-host/Serve.csbody').read_text();evidence={'checks':checks,'actualEngine':True,'nativeBoundaryFixture':True,'actualWindowsExecuted':False,'actualAccountOrInference':False,'nativeCalls':calls(),'errors':errors,'external':external,'evidence':str(root)};(root/'evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2));page.screenshot(path=str(root/'v536-restarted-selected-project.png'));print(json.dumps(evidence,ensure_ascii=False,indent=2))
  browser.close()
except BaseException:
 print('FAILED '+str(root),flush=True)
 try:(root/'failure-state.json').write_text(json.dumps(state(),ensure_ascii=False,indent=2))
 except Exception:pass
 try:page.screenshot(path=str(root/'failure.png'));print(json.dumps({'inert':page.locator('#app').evaluate('e=>e.inert'),'state':state().get('projectId'),'toast':page.locator('#toast').inner_text(),'errors':errors}),flush=True)
 except Exception:pass
 raise
finally:
 if host.poll() is None:os.killpg(host.pid,signal.SIGTERM);host.wait(timeout=15)
 log.close()
 if chat_provider:chat_provider.close()
