"""Production native creation contract over an isolated loopback host fixture.
The fixture supplies only an approved parent folder; no native Windows picker QA.
"""
from editor_navigation import goto_editor
import json,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
expect.set_options(timeout=30000)
project_chat=os.environ.get('CONFECTORY_PROJECT_CHAT')=='1';chat_provider=None
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
  page.add_init_script('''globalThis.__creationReply='normal';globalThis.confectoryWebUI={async chooseProjectParent(){return {ok:true,parent:'owned-parent',label:'Owned fixture projects'};},async createProject(title,description,parent,proposalId){if(globalThis.__creationReply==='cancel')return {ok:true,cancelled:true};const token=sessionStorage.getItem('confectory.webui.session');return (await fetch('/fixture/native-create',{method:'POST',headers:{'Content-Type':'application/json','X-Confectory-Session':token},body:JSON.stringify({title,description,...(proposalId?{proposalId}:{})})})).json();}};''')
  goto_editor(page,url);page.locator('#add-agent').click();dialog=page.get_by_role('dialog',name='Agent 추가',exact=True);dialog.get_by_role('button',name='OpenAI Responses',exact=True).click()
  for name,value in [('model','owned-no-inference'),('endpoint',chat_provider.endpoint if chat_provider else 'http://127.0.0.1:9/responses'),('credentialReference','')]:dialog.locator('[data-connection-field="'+name+'"]').fill(value)
  dialog.locator('[data-agent-register]').click();expect(dialog.locator('[data-agent-registration-state]')).to_contain_text('Agent 등록됨');dialog.locator('[data-connection-cancel]').click();assert state()['helpers']==[]
  def create(title,helper=None):
   page.locator('#new-project').click();modal=page.get_by_role('dialog',name='새 프로젝트 만들기',exact=True);modal.locator('#project-name').fill(title);modal.locator('#project-desc').fill('Owned creation responsiveness fixture');
   if helper:modal.locator('[data-project-helper="'+helper+'"]').click()
   modal.locator('button[type=submit]').click();return modal
  first=create('Owned Created');expect(page.locator('.work-body')).to_be_visible(timeout=30000)
  for _ in range(500):
   value=state()
   if value.get('mainHelperId'):break
   page.wait_for_timeout(20)
  else:raise AssertionError('created project never received its owned Main Helper')
  page.wait_for_timeout(300);evidence['afterCreation']={'inert':page.locator('#app').evaluate('e=>e.inert'),'overlays':page.locator('#overlays').inner_text(),'projectId':value['projectId'],'mainHelperId':value['mainHelperId'],'helperIds':value['projectHelperIds'],'errors':errors};page.screenshot(path=str(root/'created.png'))
  assert (root/'projects/Owned Created/project.cproj').is_file();assert len(value['helpers'])==1;assert value['helperAgents']['assignments'][value['mainHelperId']]=='Confectory.Agent.Responses::Connection'
  if project_chat:
   from project_chat_contract import run
   run(page,state,root,chat_provider)
  elif os.environ.get('CONFECTORY_EXPECT_CREATE_BUG')=='1':
   assert evidence['afterCreation']['inert'] and not evidence['afterCreation']['overlays'];(root/'evidence.json').write_text(json.dumps(evidence,indent=2));print('REPRODUCED orphaned inert after actual native-contract project creation '+str(root),flush=True)
  else:
   assert not evidence['afterCreation']['inert'],evidence
   expect(page.locator('#add-helper')).to_be_enabled();page.locator('.home-side [data-helper]').first.hover();expect(page.locator('[role=tooltip]')).to_be_visible();page.locator('.brand').click();expect(page.locator('#new-project')).to_be_enabled();helper=value['mainHelperId']
   second=create('Owned Selected',helper);expect(page.locator('.work-body')).to_be_visible();expect(page.locator('#helper-summary')).to_contain_text(helper);assert state()['projectHelperIds']==[helper] and len(state()['helpers'])==1;assert not page.locator('#app').evaluate('e=>e.inert');page.locator('.brand').click();expect(page.locator('#new-project')).to_be_enabled()
   # Duplicate failure remains in its visible modal; cancel restores background interaction.
   duplicate=create('Owned Created');expect(page.locator('#toast')).to_contain_text('작업을 완료하지 못했습니다.');expect(duplicate).to_be_visible();expect(duplicate.locator('[data-project-cancel]')).to_be_enabled();assert page.locator('#app').evaluate('e=>e.inert');duplicate.locator('[data-project-cancel]').click();assert not page.locator('#app').evaluate('e=>e.inert');expect(page.locator('#new-project')).to_be_enabled();assert len(state()['cards'])==2
   page.evaluate("globalThis.__creationReply='cancel'");cancel=create('Never Created');expect(cancel.locator('[data-project-cancel]')).to_be_enabled();cancel.locator('[data-project-cancel]').click();assert not (root/'projects/Never Created').exists();assert not page.locator('#app').evaluate('e=>e.inert');assert len(state()['helpers'])==1
   # Repeated modal replacement must release exactly its own inert state.
   page.locator('#new-project').click();page.get_by_role('dialog',name='새 프로젝트 만들기',exact=True).locator('[data-project-cancel]').click();page.locator('#add-agent').click();page.get_by_role('dialog',name='Agent 추가',exact=True).locator('[data-connection-cancel]').click();assert not page.locator('#app').evaluate('e=>e.inert')
   lifecycle=page.evaluate("""async()=>{const {createV508Views}=await import('/v508-views.js');const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];const owned=createV508Views({$, $$,esc:s=>s}),app=$('#app');let firstClose;owned.modal('Outer','<button>Outer</button>',(r,close)=>{firstClose=close;owned.modal('Inner','<button>Inner</button>');});const nested=app.inert&&$('[aria-label="Inner"]')!==null;firstClose();const staleCloseSafe=app.inert&&$('[aria-label="Inner"]')!==null;owned.dismissModal();const released=!app.inert&&!$('#overlays').children.length;app.inert=true;owned.modal('Independent owner','<button>Owned</button>');owned.dismissModal();const priorInertPreserved=app.inert;app.inert=false;return {nested,staleCloseSafe,released,priorInertPreserved};}""")
   assert all(lifecycle.values()),lifecycle;evidence['modalOwnership']=lifecycle
   assert not errors,errors;evidence['checks']=['actual creation native contract','automatic Agent-owned Main Helper','selected Helper without duplicate','native cancel','duplicate failure leaves visible usable modal','post-create hover and controls','project/home modal cleanup'];evidence['nativeCalls']=[json.loads(x) for x in (root/'native-calls.jsonl').read_text().splitlines()];evidence['actualWindowsExecuted']=False;evidence['actualAccountOrInference']=False;(root/'evidence.json').write_text(json.dumps(evidence,indent=2));page.screenshot(path=str(root/'responsive-home.png'));print('PASS actual native-contract creation / inert / scope / cancel / duplicate responsiveness '+str(root),flush=True)
  browser.close()
except BaseException:
 print('FAILED '+str(root),flush=True)
 try:page.screenshot(path=str(root/'failure.png'));print(json.dumps({'inert':page.locator('#app').evaluate('e=>e.inert'),'state':state().get('projectId'),'toast':page.locator('#toast').inner_text(),'errors':errors}),flush=True)
 except Exception:pass
 raise
finally:
 if host.poll() is None:os.killpg(host.pid,signal.SIGTERM);host.wait(timeout=15)
 log.close()
 if chat_provider:chat_provider.close()
