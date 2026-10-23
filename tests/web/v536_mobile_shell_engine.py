"""v536 mobile common shell over the actual engine in an isolated native creation fixture.
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
repo=pathlib.Path(sys.argv[1]).resolve();root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-mobile-engine-'));print('FIXTURE '+str(root),flush=True)
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

  checks=[];external=[]
  def checked(message):checks.append(message);(root/'progress.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2));print('PASS '+message,flush=True)
  page.route('**/*',lambda route:route.continue_() if route.request.url.startswith(origin+'/') else (external.append(route.request.url),route.abort())[-1])
  page.set_viewport_size({'width':390,'height':844});expect(page.locator('.mobile-workspace-actions')).to_be_visible();expect(page.locator('.home-side')).to_be_hidden();expect(page.locator('[data-mobile-files]')).to_be_hidden();page.locator('[data-mobile-people]').click();expect(page.locator('.home-side')).to_be_visible();page.locator('#add-helper').click();creator=page.locator('[data-reference-version="536"]');creator.locator('#participant-name').fill('모바일 전역 도우미');creator.locator('#participant-description').fill('한글 입력 보존');creator.locator('[data-close]').click();expect(creator).to_have_count(0);assert not page.locator('#app').evaluate('e=>e.inert');page.locator('#add-helper').click();expect(creator.locator('#participant-name')).to_have_value('모바일 전역 도우미');expect(creator.locator('#participant-description')).to_have_value('한글 입력 보존');creator.locator('button[type=submit]').click();expect(creator).to_have_count(0);assert len(state()['helpers'])==1;global_helper=state()['helpers'][0]['id'];page.locator('[data-mobile-people]').click();expect(page.locator('.home-side')).to_be_hidden();page.screenshot(path=str(root/'mobile-home.png'));checked('390px actual Home: mobile navigation, global Helper create and modal cleanup without project inheritance')
  modal=create('Owned Mobile');expect(modal).to_have_count(0);expect(page.locator('.work-body')).to_be_visible();project_id=state()['projectId'];project_helper=state()['mainHelperId'];assert state()['projectHelperIds']==[project_helper];expect(page.locator('.chatbar')).to_be_hidden();geometry={'topbar':page.locator('.topbar').bounding_box(),'tabs':page.locator('.workspace-tabs').bounding_box(),'buttons':{name:page.locator('[data-mobile-'+name+']').bounding_box() for name in ['people','files','chat','more']}};(root/'geometry.json').write_text(json.dumps(geometry));assert geometry['topbar']['height']==40 and geometry['tabs']['height']==32;assert all(b['x']>=0 and b['x']+b['width']<=390 and b['height']==36 for b in geometry['buttons'].values());page.screenshot(path=str(root/'mobile-workspace.png'));checked('actual project creation switches to compact work without stale inert/overlay; assigned project Helper remains distinct from global Helper')
  page.locator('[data-mobile-chat]').click();field=page.locator('#chat-input');expect(field).to_be_visible();field.fill('모바일 프로젝트 입력\n새 줄과 이모지 😀');page.keyboard.press('Escape');expect(page.locator('.chatbar')).to_be_hidden();page.locator('[data-mobile-chat]').click();expect(field).to_have_value('모바일 프로젝트 입력\n새 줄과 이모지 😀');page.screenshot(path=str(root/'mobile-project-chat.png'));assert field.bounding_box()['y']+field.bounding_box()['height']<=844;checked('actual project composer: panel close/reopen retains Korean multiline text; no prepare/login/model invocation')
  page.locator('[data-mobile-people]').click();expect(page.locator('.chatbar')).to_be_hidden();expect(page.locator('.home-side [data-helper="'+project_helper+'"]').first).to_be_visible();expect(page.locator('.home-side [data-helper="'+global_helper+'"]')).to_have_count(0);page.locator('[data-mobile-files]').click();expect(page.locator('.home-side')).to_be_hidden();window=page.locator('.window[data-key="browser:project:mobile"]');expect(window).to_be_visible();expect(window).to_have_class(__import__('re').compile('tab-document'));box=window.bounding_box();assert box['x']>=0 and box['x']+box['width']<=390 and box['y']>=40 and box['y']+box['height']<=844,box;query=window.locator('[data-browser-control="object-query"]');expect(query).to_be_enabled();query.fill('모바일 목록 검색 입력');page.screenshot(path=str(root/'mobile-browser.png'));assert state()['projectId']==project_id;checked('mobile list opens the real owned Project Browser and preserves project scope/assigned-only participants')
  page.locator('[data-mobile-more]').click();menu=page.locator('.context-menu');expect(menu.get_by_role('button',name='설정',exact=True)).to_be_visible();menu.get_by_role('button',name='설정',exact=True).click();settings=page.get_by_role('dialog',name='설정',exact=True);expect(settings).to_be_visible();assert page.locator('#app').evaluate('e=>e.inert');settings.locator('[data-close]').click();expect(settings).to_have_count(0);assert not page.locator('#app').evaluate('e=>e.inert');expect(query).to_have_value('모바일 목록 검색 입력');page.locator('[data-mobile-more]').click();page.locator('.context-menu').get_by_role('button',name='메뉴 닫기',exact=True).click();expect(page.locator('.context-menu')).to_have_count(0);checked('existing settings modal and touch menu close restore inert/focus ownership without replacing Browser input')
  page.locator('[data-mobile-chat]').click();expect(field).to_have_value('모바일 프로젝트 입력\n새 줄과 이모지 😀');page.set_viewport_size({'width':1280,'height':900});expect(page.locator('.mobile-workspace-actions')).to_be_hidden();expect(page.locator('.chatbar')).to_be_visible();expect(page.locator('.home-side')).to_be_visible();expect(field).to_have_value('모바일 프로젝트 입력\n새 줄과 이모지 😀');page.screenshot(path=str(root/'desktop-after-mobile.png'));checked('desktop return restores sidebar/chat/tabs and preserves same input and Browser document')
  page.set_viewport_size({'width':390,'height':600});expect(page.locator('.mobile-workspace-actions')).to_be_visible();page.locator('[data-mobile-chat]').click();expect(field).to_be_visible();assert field.bounding_box()['y']+field.bounding_box()['height']<=600;expect(field).to_have_value('모바일 프로젝트 입력\n새 줄과 이모지 😀');page.screenshot(path=str(root/'mobile-short-height.png'));checked('shorter visual viewport keeps the existing composer reachable; no font/control scaling')
  page.locator('[data-mobile-more]').click();page.locator('.context-menu').get_by_role('button',name='프로젝트 메뉴',exact=True).click();page.locator('.context-menu').get_by_role('button',name='프로젝트 나가기',exact=True).click();expect(page.locator('.home-grid')).to_be_visible();assert not state()['projectId'];expect(page.locator('[data-mobile-chat]')).to_be_hidden();page.locator('[data-mobile-people]').click();expect(page.locator('.home-side [data-helper]')).to_have_count(2);page.screenshot(path=str(root/'mobile-return-home.png'));checked('project Back uses existing leave route; Home restores global roster without deleting project/Helper/draft')
  # Cold reopen of the same isolated profile, with no login/consent/provider activity.
  page.close();os.killpg(host.pid,signal.SIGTERM);host.wait(timeout=15);log.close();log_path=root/'host-restart.log';log=log_path.open('w');host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  for _ in range(600):
   urls=[l.split(' ',1)[1] for l in log_path.read_text().splitlines() if l.startswith('CONFECTORY_WEB_UI ')]
   if urls:url=urls[-1];origin,token=url.split('/#');break
   assert host.poll() is None;time.sleep(.05)
  else:raise AssertionError('restart startup timeout')
  page=browser.new_page(viewport={'width':390,'height':844});page.on('pageerror',lambda e:errors.append(str(e)));page.route('**/*',lambda route:route.continue_() if route.request.url.startswith(origin+'/') else (external.append(route.request.url),route.abort())[-1]);goto_editor(page,url);expect(page.locator('[data-enter]')).to_have_count(1);page.locator('[data-enter]').click();expect(page.locator('.work-body')).to_be_visible();expect(page.locator('[data-mobile-chat]')).to_be_visible();page.locator('[data-mobile-chat]').click();expect(page.locator('#chat-input')).to_have_value('모바일 프로젝트 입력\n새 줄과 이모지 😀');assert state()['projectId']==project_id and state()['projectHelperIds']==[project_helper];page.screenshot(path=str(root/'mobile-restarted-chat.png'));checked('actual process restart restores mobile project draft and placement without opening Agent setup or sending a request')
  assert not errors and not external,(errors,external);evidence={'checks':checks,'actualEngine':True,'nativeBoundaryFixture':True,'actualWindowsExecuted':False,'actualAndroidExecuted':False,'actualAccountOrInference':False,'errors':errors,'external':external,'evidence':str(root)};(root/'evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2));print(json.dumps(evidence,ensure_ascii=False,indent=2));browser.close()
except BaseException:
 print('FAILED '+str(root),flush=True)
 try:page.screenshot(path=str(root/'failure.png'));print(json.dumps({'inert':page.locator('#app').evaluate('e=>e.inert'),'state':state().get('projectId'),'toast':page.locator('#toast').inner_text(),'errors':errors}),flush=True)
 except Exception:pass
 raise
finally:
 if host.poll() is None:os.killpg(host.pid,signal.SIGTERM);host.wait(timeout=15)
 log.close()
 if chat_provider:chat_provider.close()
