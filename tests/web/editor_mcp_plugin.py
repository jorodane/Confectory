"""Actual engine-first connection, scoped existing drafts and integrated Codex UI."""
import json,pathlib,re,socket,sys,time,uuid
from playwright.sync_api import expect
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'protocol'))
from mcp_client import Client

def verify_mcp_plugin(page,project,mount,send,envelope,settle,restart,repo,env):
 page.set_viewport_size({'width':1360,'height':900});graph='Example.ButtonGame::NodeValueBody/body:common';source=graph+'/node:calculate';directory=pathlib.Path(env['CONFECTORY_MCP_DIRECTORY']);original={p:p.read_bytes() for p in project.iterdir() if p.is_file()};other=project.parent/'second-project';other_original={p:p.read_bytes() for p in other.iterdir() if p.is_file()};calls=[];layouts=[]
 def record(request):
  if request.url.endswith('/api/request'):
   try:
    data=json.loads(request.post_data or '{}')
    if data.get('op')=='invoke':calls.append(data.get('endpoint'))
   except ValueError:pass
 page.on('request',record)
 def ready():expect(page.locator('#add-agent')).to_be_enabled(timeout=180000)
 def window(key):return page.locator('.window[data-key="'+key+'"]')
 def state():
  v=mount();s=v['state'];assert send(envelope(v,'dispose'))['ok'];return s
 def invoke(endpoint,args,ok=True):
  v=mount();request=uuid.uuid4().hex;assert send(envelope(v,'invoke',endpoint=endpoint,input=args,requestId=request,expectedRevision=v['revision']))['ok'];result,_=settle(v,request);assert send(envelope(v,'dispose'))['ok'];assert result['ok']==ok,result;return result.get('result')
 def nav(label):
  ready();page.locator('#nav').click();page.locator('.nav-menu').get_by_role('button',name=label,exact=True).click();ready()
  if page.locator('.nav-menu').count():page.locator('#nav').click()
 def dialog():return page.locator('[data-connection-dialog]')
 def panel():return dialog().locator('[data-mcp-panel]')
 def open_ai():
  ready();page.locator('#add-agent').click();dialog().get_by_role('button',name='Codex',exact=True).click();expect(panel()).to_be_visible();ready()
 def close_ai():dialog().locator('[data-connection-cancel]').click();expect(dialog()).to_have_count(0);ready()
 def layout(label):
  assert page.locator('.modal').count()==1 and page.locator('[data-mcp-open]').count()==0 and window('mcp-bridge').count()==0
  bounds=dialog().evaluate("e=>{const r=e.getBoundingClientRect(),c=[...e.querySelectorAll('[data-connection-choice]')].map(e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height}});return {x:r.x,y:r.y,width:r.width,height:r.height,viewport:[innerWidth,innerHeight],scrollWidth:e.scrollWidth,clientWidth:e.clientWidth,cards:c}}")
  assert len(bounds['cards'])==2 and abs(bounds['cards'][0]['y']-bounds['cards'][1]['y'])<2,bounds
  assert bounds['x']>=0 and bounds['y']>=0 and bounds['x']+bounds['width']<=bounds['viewport'][0]+1 and bounds['y']+bounds['height']<=bounds['viewport'][1]+1 and bounds['scrollWidth']<=bounds['clientWidth']+1,bounds
  layouts.append(dict(label=label,**bounds));expect(page.locator('#toast')).not_to_have_class(re.compile(r'.*\bshow\b.*'),timeout=10000);page.screenshot(path='/tmp/confectory-mcp-'+label+'.png',full_page=True)
 def grant(readonly=True,node=source):
  panel().locator('[data-mcp-node]').select_option(node);panel().locator('[data-mcp-readonly]').set_checked(readonly);panel().locator('[data-mcp-grant]').click();ready();status=state()['mcpBridge'];assert status['state']=='ready' and status['instance']==engine;scope=status['scope'];assert scope['readOnly']==readonly and scope['node']==node;return scope
 def revoke():
  panel().locator('[data-mcp-revoke]').click();ready();assert state()['mcpBridge']['scope'] is None
 def site_pair():
  prepared=invoke('mcpBridge',dict(action='site-prepare'));assert prepared['url']=='https://confectory-connect.jorodane.chatgpt.site/editor-bridge'
  binding=dict(nonce=prepared['nonce'],sessionId=uuid.uuid4().hex)
  invoke('mcpBridge',dict(action='site-message',type='paired',expiresAt=int(time.time()*1000)+600000,**binding))
  visible=state()['mcpBridge']['site'];assert visible['state']=='connected' and not visible['scopeGranted'] and 'nonce' not in json.dumps(visible) and 'sessionId' not in visible
  return binding
 def site_call(binding,kind,ok=True,**extra):return invoke('mcpBridge',dict(action='site-message',type=kind,**binding,**extra),ok=ok)
 def site_grant(binding):
  expect(panel().locator('[data-mcp-site-grant]')).to_be_enabled();panel().locator('[data-mcp-site-grant]').click();ready();pulse=site_call(binding,'pulse');assert pulse['scope'];assert len(pulse['tools'])<=6 and len(pulse['engineTools'])==3, 'Old Sites must retain their workspace-only six-tool pulse';return pulse
 def site_job(pulse,name,arguments,call_id=None):return dict(id=uuid.uuid4().hex,claim=uuid.uuid4().hex,callId=call_id or uuid.uuid4().hex,name=name,arguments=arguments,instanceId=engine,scopeVersion=pulse['scopeVersion'],scopeId=pulse['scope']['id'],projectId=pulse['scope']['projectId'])
 def bp():return window('blueprint')
 def front(key):
  title=window(key).locator('.window-title');point=title.evaluate("e=>{const r=e.getBoundingClientRect();for(const f of [.8,.6,.3,.95]){const x=Math.floor(r.width*f),y=18,hit=document.elementFromPoint(r.left+x,r.top+y);if(hit&&e.contains(hit)&&!hit.closest('button'))return {x,y}}return null}");assert point;title.click(position=point)
 def host_call(arguments):
  descriptor=json.loads((directory/(engine+'.json')).read_text())
  with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as peer:
   peer.settimeout(5);peer.connect(descriptor['address']);peer.sendall((json.dumps(dict(instance=engine,operation='tools/call',payload=dict(name='workspace_read',callId=uuid.uuid4().hex,arguments=arguments)))+'\n').encode());raw=b''
   while b'\n' not in raw:raw+=peer.recv(65536)
  return json.loads(raw)
 # Existing project was opened by the fixture; explicitly return to Home before connection.
 page.locator('.brand').click();ready();assert state()['projectId']==''
 with Client(repo,directory,env) as client:
  assert client.call('confectory_instances')[0]['code']=='engine_not_running'
  open_ai();expect(panel().locator('[data-mcp-grant]')).to_be_disabled();panel().locator('[data-mcp-start]').click();ready();status=state()['mcpBridge'];engine=status['instance'];assert status['state']=='ready' and status['scope'] is None
  # The next login action must be visible without scrolling past project settings.
  next_action=panel().locator('[data-mcp-site-open]');next_bounds=next_action.evaluate("e=>{const r=e.getBoundingClientRect(),m=e.closest('.modal').getBoundingClientRect();return {top:r.top,bottom:r.bottom,modalTop:m.top,modalBottom:m.bottom,viewportHeight:innerHeight,scroll:e.closest('.modal').scrollTop}}")
  page.screenshot(path='/tmp/confectory-site-next-action.png',full_page=True)
  assert next_bounds['top']>=max(0,next_bounds['modalTop']) and next_bounds['bottom']<=min(next_bounds['viewportHeight'],next_bounds['modalBottom']),next_bounds
  expect(next_action).to_be_disabled();expect(panel().locator('[data-mcp-site-hint]')).to_contain_text('브라우저 진단 모드')
  expect(panel().locator('[data-mcp-status]')).to_contain_text('ChatGPT 연결은 아직 완료되지 않았습니다')
  # Owned native-capability fixture: the real button calls the exposed native
  # entry once. No Site request, login, account or Windows runtime is simulated.
  close_ai();page.evaluate("()=>{globalThis.ownedSiteWindowCalls=0;globalThis.confectoryWebUI={connectSite(){globalThis.ownedSiteWindowCalls++;return Promise.resolve({ok:true});}};}")
  page.set_viewport_size({'width':900,'height':760});open_ai();expect(panel().locator('[data-mcp-site-open]')).to_be_enabled()
  expect(panel().locator('[data-mcp-site-open]')).to_be_in_viewport(ratio=1)
  panel().locator('[data-mcp-site-open]').click();ready();assert page.evaluate('globalThis.ownedSiteWindowCalls')==1
  assert not state()['mcpBridge'].get('site'), 'A window acknowledgment must not claim an authenticated connection'
  close_ai();page.evaluate("()=>{globalThis.confectoryWebUI={send(){throw Error('owned unavailable native capability');}};}")
  open_ai();expect(panel().locator('[data-mcp-site-open]')).to_be_disabled();expect(panel().locator('[data-mcp-site-hint]')).to_contain_text('호스트에는 로그인 창 기능이 없습니다')
  close_ai();page.evaluate('()=>{delete globalThis.confectoryWebUI;}');page.set_viewport_size({'width':1360,'height':900});open_ai()
  expect(panel().locator('[data-mcp-instance]')).to_have_text(engine);connected=client.connect(engine);assert connected['scope'] is None and connected['state']=='ready';assert len(client.request('tools/list')['tools'])==7
  options,error=client.call('engine_project_options');assert not error and options['templates'][0]['id']=='empty-projectpack' and options['templates'][0]['buildTargets']==['portable','windows','linux']
  proposal_args=dict(title='Owned Creation Proposal',description='Only the engine user can confirm creation',intent='Please propose a new project',templateId='empty-projectpack',targetId='dotnet')
  proposal,error=client.call('engine_project_propose',proposal_args);assert not error and proposal['status']=='pending' and proposal['projectId'] is None and not proposal['projectAccessGranted']
  assert state()['projectId']=='' and state()['mcpBridge']['scope'] is None
  invoke('mcpBridge',dict(action='creation-confirm',proposalId=proposal['id'],directory='/must-not-create',title=proposal_args['title'],description=proposal_args['description']),ok=False)
  # No real native picker is used: verify the ordinary form is prefilled, then reject.
  close_ai();expect(page.locator('[data-creation-review]')).to_be_visible();page.locator('[data-creation-review]').click();expect(page.locator('#project-name')).to_have_value(proposal_args['title']);expect(page.locator('#project-desc')).to_have_value(proposal_args['description']);assert not state()['projectId']
  page.locator('.modal [data-close]').click();page.locator('[data-creation-reject]').click();ready();status,error=client.call('engine_project_status',dict(proposalId=proposal['id']));assert not error and status['status']=='rejected'
  assert client.call('engine_project_propose',dict(proposal_args,directory='/must-not-create'))[1]
  assert client.call('engine_project_confirm',dict(proposalId=proposal['id']))[1]
  open_ai();owned_site=site_pair();assert site_call(owned_site,'pulse')['scope'] is None
  site_call(dict(owned_site,nonce='0'*64),'pulse',ok=False);site_call(dict(owned_site,sessionId='f'*32),'pulse',ok=False)
  invoke('mcpBridge',dict(action='site-grant',connectionId=state()['mcpBridge']['site']['connectionId'],instanceId=engine,scopeVersion=0,scopeId='missing'),ok=False)
  site_call(owned_site,'close')
  assert client.call('workspace_read',dict(projectId='unselected',scopeId='0'*32,id=source))[0]['code']=='no_project_scope'
  layout('home-engine-only');page.set_viewport_size({'width':900,'height':760});layout('home-compact');page.set_viewport_size({'width':1360,'height':900});close_ai()
  page.locator('[data-project]').filter(has_text='Overview A').locator('[data-enter]').click();ready();project_id=state()['projectId'];assert client.call('confectory_status')[0]['scope'] is None and state()['mcpBridge']['instance']==engine
  assert client.call('workspace_read',dict(projectId=project_id,scopeId='0'*32,id=source))[0]['code']=='no_project_scope'
  # Even an ungranted old UI selection cannot be applied after A -> B -> A.
  ungranted_version=state()['mcpBridge']['scopeVersion'];page.locator('.brand').click();ready();page.locator('[data-project]').filter(has_text='Overview B').locator('[data-enter]').click();ready();page.locator('.brand').click();ready();page.locator('[data-project]').filter(has_text='Overview A').locator('[data-enter]').click();ready()
  invoke('mcpBridge',dict(action='scope',instanceId=engine,projectId=project_id,scopeVersion=ungranted_version,node='',readOnly=True),ok=False);assert state()['mcpBridge']['scope'] is None
  nav('기능 Blueprint');bp().locator('[data-bp-select="calculate"]').click();open_ai();expect(panel().locator('[data-mcp-readonly]')).to_be_checked();scope=grant();scope_id=scope['id'];assert client.call('confectory_status')[0]['scope']['id']==scope_id
  definitions=client.request('tools/list')['tools'];names={t['name'] for t in definitions};assert {'workspace_read','workspace_list','workspace_changes'}<=names and not {'workspace_stage','workspace_create','confirm','shell'}&names
  assert next(t for t in definitions if t['name']=='workspace_read')['inputSchema']['properties']['scopeId']['enum']==[scope_id]
  layout('project-scoped');page.set_viewport_size({'width':900,'height':760});layout('project-compact');page.set_viewport_size({'width':2200,'height':1400})
  # Malformed peers only lose their connection, not the engine or granted scope.
  descriptor=json.loads((directory/(engine+'.json')).read_text())
  with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as peer:
   peer.settimeout(3);peer.connect(descriptor['address'])
   try:peer.sendall(b'x'*(4194304+2048));peer.shutdown(socket.SHUT_WR);assert peer.recv(1)==b''
   except (BrokenPipeError,ConnectionResetError):pass
  assert client.call('confectory_status')[0]['instance']==engine
  read,error=client.call('workspace_read',dict(projectId=project_id,scopeId=scope_id,id=source));assert not error and json.loads(read['text'])['source']=='return value + 4;'
  owned_site=site_pair();assert site_call(owned_site,'pulse')['scope'] is None
  invoke('mcpBridge',dict(action='site-grant',connectionId='old-connection',instanceId=engine,scopeVersion=state()['mcpBridge']['scopeVersion'],scopeId=scope_id),ok=False)
  pulse=site_grant(owned_site);assert pulse['scope']['readOnly']
  remote_read=site_job(pulse,'workspace_read',dict(id=source));assert site_call(owned_site,'dispatch',job=remote_read)['value']==read
  site_call(owned_site,'dispatch',job=dict(remote_read,scopeId='foreign'),ok=False)
  site_call(owned_site,'dispatch',job=site_job(pulse,'confirm',{}),ok=False)
  site_call(owned_site,'dispatch',job=site_job(pulse,'workspace_stage',dict(id=source,text=read['text'],expectedRevision=read['revision'],expectedHash=read['textHash'])),ok=False)
  panel().locator('[data-mcp-site-revoke]').click();ready();assert site_call(owned_site,'pulse')['scope'] is None;site_call(owned_site,'dispatch',job=remote_read,ok=False)
  assert client.call('workspace_read',dict(projectId=project_id,scopeId=scope_id,id=source))[0]==read
  site_call(owned_site,'close')
  denied,error=client.call('workspace_stage',dict(projectId=project_id,scopeId=scope_id,id=source,text=read['text'],expectedRevision=read['revision'],expectedHash=read['textHash']));assert error and denied['code']=='read_only';assert all(p.read_bytes()==raw for p,raw in original.items())
  old_read=dict(projectId=project_id,scopeId=scope_id,id=source);revoke();assert client.call('confectory_status')[0]['scope'] is None and client.call('workspace_read',old_read)[1]
  scope=grant(False);scope_id=scope['id'];assert scope_id!=old_read['scopeId'];assert host_call(old_read)['code']=='scope_changed';close_ai()
  current,error=client.call('workspace_read',dict(projectId=project_id,scopeId=scope_id,id=source));assert not error
  open_ai();owned_site=site_pair();pulse=site_grant(owned_site);record=json.loads(current['text']);record['source']='return value + 6;'
  remote_stage=site_job(pulse,'workspace_stage',dict(id=source,text=json.dumps(record),expectedRevision=current['revision'],expectedHash=current['textHash']))
  staged=site_call(owned_site,'dispatch',job=remote_stage);assert staged['value']['applied'];assert site_call(owned_site,'dispatch',job=remote_stage)==staged
  current,error=client.call('workspace_read',dict(projectId=project_id,scopeId=scope_id,id=source));assert not error and json.loads(current['text'])['source']=='return value + 6;';assert all(p.read_bytes()==raw for p,raw in original.items())
  site_call(owned_site,'close');site_call(owned_site,'dispatch',job=remote_stage,ok=False);close_ai();record=json.loads(current['text']);record['source']='return value + 8;';text=json.dumps(record)
  front('blueprint');bp().locator('[data-bp-intent]').fill('MCP_UNSENT_INTENT');stage_args=dict(projectId=project_id,scopeId=scope_id,id=source,text=text,expectedRevision=current['revision'],expectedHash=current['textHash']);request=client.send('tools/call',dict(name='workspace_stage',arguments=stage_args),id='stage-once');result=client.receive(request)['result'];assert not result['isError'] and json.loads(result['content'][0]['text'])['applied'];client.send('tools/call',dict(name='workspace_stage',arguments=stage_args),id='stage-once');assert client.receive('stage-once')['result']==result
  expect(bp().locator('[data-bp-intent]')).to_have_value('MCP_UNSENT_INTENT');bp().locator('[data-bp-intent]').locator('..').locator('[data-apply]').click();ready();expect(bp().locator('[data-bp-intent]')).to_have_value('MCP_UNSENT_INTENT');bp().locator('[data-bp-intent]').locator('..').locator('[data-reset]').click()
  latest,error=client.call('workspace_read',dict(projectId=project_id,scopeId=scope_id,id=source));assert not error and latest['revision']==current['revision']+1;assert json.loads(latest['text'])['source']=='return value + 8;';assert all(p.read_bytes()==raw for p,raw in original.items())
  assert client.call('workspace_read',dict(projectId='foreign-project',scopeId=scope_id,id=source))[1];assert client.call('confirm',{})[1]
  bp().locator('[data-bp-read]').click();ready();bp().locator('[data-bp-code-open="calculate"]').click();code=window('blueprint-code:'+graph+'/calculate');code.locator('[data-bp-code]').fill('return value + 9;');code.locator('[data-apply]').click();ready();code.locator('[data-close]').click();assert client.call('workspace_read',dict(projectId=project_id,scopeId=scope_id,id=source))[1]
  open_ai();revoke();scope=grant(False);scope_id=scope['id'];close_ai();assert client.call('confectory_status')[0]['instance']==engine
  client.send('tools/call',dict(name='workspace_stage',arguments=stage_args),id='stage-once');cached=client.receive('stage-once')['result'];assert cached['isError'] and json.loads(cached['content'][0]['text'])['code']=='scope_changed'
  fresh,error=client.call('workspace_read',dict(projectId=project_id,scopeId=scope_id,id=source));assert not error and json.loads(fresh['text'])['source']=='return value + 9;'
  record=json.loads(fresh['text']);record['source']='return value + 10;';proposed=json.dumps(record);conflict,error=client.call('workspace_stage',dict(projectId=project_id,scopeId=scope_id,id=source,text=proposed,expectedRevision=fresh['revision'],expectedHash='0'*64));assert not error and conflict['conflict'] and not conflict['applied']
  accepted,error=client.call('workspace_stage',dict(projectId=project_id,scopeId=scope_id,id=source,text=proposed,expectedRevision=fresh['revision'],expectedHash=fresh['textHash']));assert not error and accepted['applied'];changes,error=client.call('workspace_changes',dict(projectId=project_id,scopeId=scope_id));assert not error and source in changes;assert all(p.read_bytes()==raw for p,raw in original.items())
  front('blueprint');bp().locator('[data-bp-read]').click();ready();bp().locator('[data-bp-review]').click();ready();review=window('review');review.locator('[data-review-advanced]').click();review.locator('[data-advanced-reviewed]').check();page.locator('#confirm').click();ready();assert json.loads((project/'calculate.node.json').read_text())['source']=='return value + 10;';assert all(p.read_bytes()==raw for p,raw in original.items() if p.name!='calculate.node.json')
  old_a=dict(projectId=project_id,scopeId=scope_id,id=source);old_version=state()['mcpBridge']['scopeVersion']
  page.locator('.brand').click();ready();assert client.call('confectory_status')[0]['scope'] is None;page.locator('[data-project]').filter(has_text='Overview B').locator('[data-enter]').click();ready();assert client.call('confectory_status')[0]['instance']==engine;assert client.call('workspace_read',old_a)[1]
  invoke('mcpBridge',dict(action='scope',instanceId=engine,projectId=project_id,scopeVersion=old_version,node=source),ok=False);assert state()['mcpBridge']['scope'] is None
  open_ai();b=grant(True,'');assert b['projectId']!=project_id;assert client.call('workspace_read',old_a)[1];assert host_call(old_a)['code']=='scope_changed';assert not client.call('workspace_list',dict(projectId=b['projectId'],scopeId=b['id'],query=''))[1];close_ai();assert all(p.read_bytes()==raw for p,raw in other_original.items())
  page.locator('#title').click();page.get_by_role('button',name='프로젝트 완전 종료',exact=True).click();expect(page.locator('.home-grid')).to_be_visible();ready();assert state()['projectId']=='' and client.call('confectory_status')[0]['instance']==engine and client.call('confectory_status')[0]['scope'] is None
  page.locator('[data-project]').filter(has_text='Overview A').locator('[data-enter]').click();ready();open_ai();again=grant(True,'');assert again['projectId']==project_id and again['id']!=old_a['scopeId'];assert client.call('workspace_read',old_a)[1];close_ai()
  invoke('saveDraft',{});restart();ready();assert client.call('confectory_status')[1] and client.call('confectory_instances')[0]['code']=='engine_not_running';open_ai();assert not state().get('mcpBridge') or state()['mcpBridge']['state']=='stopped';panel().locator('[data-mcp-start]').click();ready();new=state()['mcpBridge'];assert new['instance']!=engine and new['scope'] is None;invoke('mcpBridge',dict(action='scope',instanceId=engine,projectId=state()['projectId'],scopeVersion=new['scopeVersion'],node=''),ok=False);assert state()['mcpBridge']['scope'] is None;client.connect(new['instance']);assert client.call('workspace_read',old_a)[0]['code']=='no_project_scope';layout('after-cold');panel().locator('[data-mcp-stop]').click();ready()
  assert not {'runProject','startAI','prepareAI','startInstallation','startLogin','permission'}.intersection(calls),calls
  evidence=dict(engineCreationOptionsWithoutProject=True,proposalReviewPrefillAndReject=True,noRemoteCreationOrFolderArgument=True,actualEngine='ordinary EditorHome with existing DevelopmentTools',actualAdapter='managed MCP stdio over private Unix IPC',engineConnectedBeforeProject=True,explicitProjectScopeAfterConnection=True,staleUngrantedSelectionRefused=True,openCloseSwitchRetainEngine=True,scopeEpochRejectsOldSameProjectHandles=True,cachedAndRawOldScopeRefused=True,malformedPeerRetainsScope=True,initialReadOnly=True,existingSharedNodeDraft=True,duplicateStageOnce=True,unsentIntentAndOriginalFilesRetained=True,peerSourcePinAndHashCASRefused=True,humanCompilerReviewConfirm=True,coldRetiresConnectionAndScope=True,confirmedSource='return value + 10;',layouts=layouts,ownedSiteProtocolFixture=True,remoteStartsWithoutScope=True,remoteWrongNonceSessionAndConnectionRefused=True,remoteReadOnlyAndRevoke=True,remoteSharedDraftAndDuplicateStage=True,realSitesAuthentication=False,realWindowsRelayRuntime=False,realChatGPTApp=False,installed=False,registered=False,networkPort=False)
  pathlib.Path('/workspace/scratch/confectory-mcp-ui.json').write_text(json.dumps(evidence,indent=2)+'\n');print('PASS actual MCP plugin shared node/CAS/Confirm/cold '+json.dumps(evidence),flush=True)
