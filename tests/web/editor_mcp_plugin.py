"""Actual EditorHome/DevelopmentTools and managed MCP stdio; no ChatGPT installation."""
import json,os,pathlib,socket,sys,uuid
from playwright.sync_api import expect
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'protocol'))
from mcp_client import Client

def verify_mcp_plugin(page,project,mount,send,envelope,settle,restart,repo,env):
 page.set_viewport_size({'width':2200,'height':1400});graph='Example.ButtonGame::NodeValueBody/body:common';source=graph+'/node:calculate';directory=pathlib.Path(env['CONFECTORY_MCP_DIRECTORY']);original={p:p.read_bytes() for p in project.iterdir() if p.is_file()};other=project.parent/'second-project';other_original={p:p.read_bytes() for p in other.iterdir() if p.is_file()};calls=[]
 def record(request):
  if request.url.endswith('/api/request'):
   try:
    data=json.loads(request.post_data or '{}')
    if data.get('op')=='invoke':calls.append(data.get('endpoint'))
   except ValueError:pass
 page.on('request',record)
 def ready():expect(page.locator('#nav')).to_be_enabled(timeout=180000)
 def window(key):return page.locator('.window[data-key="'+key+'"]')
 def state():
  v=mount();s=v['state'];assert send(envelope(v,'dispose'))['ok'];return s
 def invoke(endpoint,args):
  v=mount();request=uuid.uuid4().hex;assert send(envelope(v,'invoke',endpoint=endpoint,input=args,requestId=request,expectedRevision=v['revision']))['ok'];result,_=settle(v,request);assert send(envelope(v,'dispose'))['ok'];assert result['ok'],result;return result.get('result')
 def nav(label):
  ready();page.locator('#nav').click();page.locator('.nav-menu').get_by_role('button',name=label,exact=True).click();ready()
  if page.locator('.nav-menu').count():page.locator('#nav').click()
 def panel():return window('mcp-bridge')
 def bp():return window('blueprint')
 def front(key):
  title=window(key).locator('.window-title');point=title.evaluate("e=>{const r=e.getBoundingClientRect();for(const f of [.8,.6,.3,.95]){const x=Math.floor(r.width*f),y=18,hit=document.elementFromPoint(r.left+x,r.top+y);if(hit&&e.contains(hit)&&!hit.closest('button'))return {x,y}}return null}");assert point;title.click(position=point)
 def bridge_start(readonly=True,node=source):
  front('mcp-bridge');panel().locator('[data-mcp-node]').select_option(node);panel().locator('[data-mcp-readonly]').set_checked(readonly);panel().locator('[data-mcp-start]').click();ready();status=state()['mcpBridge'];assert status['state']=='ready',status;assert status['readOnly']==readonly and status['node']==node;return status
 def bridge_stop():nav('ChatGPT 플러그인 연결');panel().locator('[data-mcp-stop]').click();ready();assert state()['mcpBridge']['state']=='stopped'
 with Client(repo,directory,env) as client:
  assert client.call('confectory_instances')[0]['code']=='engine_not_running'
  nav('기능 Blueprint');bp().locator('[data-bp-select="calculate"]').click();nav('ChatGPT 플러그인 연결');expect(panel().locator('[data-mcp-readonly]')).to_be_checked();a=bridge_start();project_id=a['projectId'];client.connect(a['instance']);names={t['name'] for t in client.request('tools/list')['tools']};assert {'workspace_read','workspace_list','workspace_changes'}<=names and not {'workspace_stage','workspace_create','confirm','shell'}&names
  # A malformed peer must only lose its own IPC connection, not the user's scope.
  descriptor=json.loads((directory/(a['instance']+'.json')).read_text());assert descriptor['transport']=='unix'
  with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as peer:
   peer.settimeout(3);peer.connect(descriptor['address'])
   try:peer.sendall(b'x'*(4194304+2048));peer.shutdown(socket.SHUT_WR);assert peer.recv(1)==b''
   except (BrokenPipeError,ConnectionResetError):pass
  after,error=client.call('confectory_status');assert not error and after['instance']==a['instance'],after
  read,error=client.call('workspace_read',dict(projectId=project_id,id=source));assert not error and json.loads(read['text'])['source']=='return value + 4;';denied,error=client.call('workspace_stage',dict(projectId=project_id,id=source,text=read['text'],expectedRevision=read['revision'],expectedHash=read['textHash']));assert error and denied['code']=='read_only';assert all(p.read_bytes()==raw for p,raw in original.items())
  bridge_stop();assert client.call('confectory_status')[1];a=bridge_start(False);client.connect(a['instance']);assert 'workspace_stage' in {t['name'] for t in client.request('tools/list')['tools']}
  current,error=client.call('workspace_read',dict(projectId=project_id,id=source));assert not error;record=json.loads(current['text']);record['source']='return value + 8;';text=json.dumps(record)
  front('blueprint');bp().locator('[data-bp-intent]').fill('MCP_UNSENT_INTENT');request=client.send('tools/call',dict(name='workspace_stage',arguments=dict(projectId=project_id,id=source,text=text,expectedRevision=current['revision'],expectedHash=current['textHash'])),id='stage-once');result=client.receive(request)['result'];assert not result['isError'] and json.loads(result['content'][0]['text'])['applied'];client.send('tools/call',dict(name='workspace_stage',arguments=dict(projectId=project_id,id=source,text=text,expectedRevision=current['revision'],expectedHash=current['textHash'])),id='stage-once');assert client.receive('stage-once')['result']==result
  expect(bp().locator('[data-bp-intent]')).to_have_value('MCP_UNSENT_INTENT');bp().locator('[data-bp-intent]').locator('..').locator('[data-apply]').click();ready();expect(bp().locator('[data-bp-intent]')).to_have_value('MCP_UNSENT_INTENT');bp().locator('[data-bp-intent]').locator('..').locator('[data-reset]').click()
  latest,error=client.call('workspace_read',dict(projectId=project_id,id=source));assert not error and latest['revision']==current['revision']+1;assert json.loads(latest['text'])['source']=='return value + 8;';assert all(p.read_bytes()==raw for p,raw in original.items())
  assert client.call('workspace_read',dict(projectId='foreign-project',id=source))[1];assert client.call('confirm',{})[1]
  # Existing UI is a genuine peer writer in the same draft, not a second proposal store.
  bp().locator('[data-bp-read]').click();ready();bp().locator('[data-bp-code-open="calculate"]').click();code=window('blueprint-code:'+graph+'/calculate');code.locator('[data-bp-code]').fill('return value + 9;');code.locator('[data-apply]').click();ready();code.locator('[data-close]').click();assert client.call('workspace_read',dict(projectId=project_id,id=source))[1]
  assert client.call('workspace_stage',dict(projectId=project_id,id=source,text=text,expectedRevision=latest['revision'],expectedHash=latest['textHash']))[1]
  bridge_stop();a=bridge_start(False);client.connect(a['instance']);fresh,error=client.call('workspace_read',dict(projectId=project_id,id=source));assert not error and json.loads(fresh['text'])['source']=='return value + 9;'
  record=json.loads(fresh['text']);record['source']='return value + 10;';proposed=json.dumps(record);conflict,error=client.call('workspace_stage',dict(projectId=project_id,id=source,text=proposed,expectedRevision=fresh['revision'],expectedHash='0'*64));assert not error and conflict['conflict'] and not conflict['applied'];assert client.call('workspace_read',dict(projectId=project_id,id=source))[0]['textHash']==fresh['textHash']
  accepted,error=client.call('workspace_stage',dict(projectId=project_id,id=source,text=proposed,expectedRevision=fresh['revision'],expectedHash=fresh['textHash']));assert not error and accepted['applied'];changes,error=client.call('workspace_changes',dict(projectId=project_id));assert not error and source in changes;assert all(p.read_bytes()==raw for p,raw in original.items())
  front('blueprint');bp().locator('[data-bp-read]').click();ready();bp().locator('[data-bp-review]').click();ready();review=window('review');review.locator('[data-review-advanced]').click();review.locator('[data-advanced-reviewed]').check();page.locator('#confirm').click();ready();assert json.loads((project/'calculate.node.json').read_text())['source']=='return value + 10;';assert all(p.read_bytes()==raw for p,raw in original.items() if p.name!='calculate.node.json')
  # Switching projects retires the original host scope, including its old node pin.
  page.locator('.brand').click();page.locator('[data-project]').filter(has_text='Overview B').locator('[data-enter]').click();ready();assert client.call('confectory_status')[1];nav('ChatGPT 플러그인 연결');b=bridge_start(True,'');assert b['projectId']!=project_id;client.connect(b['instance']);assert not client.call('workspace_list',dict(projectId=b['projectId'],query=''))[1];assert client.call('workspace_list',dict(projectId=project_id,query=''))[1];assert all(p.read_bytes()==raw for p,raw in other_original.items())
  invoke('saveDraft',{});restart();ready();assert client.call('confectory_status')[1];assert client.call('confectory_instances')[0]['code']=='engine_not_running';expect(panel()).to_have_attribute('aria-label','ChatGPT 플러그인 연결');expect(panel().locator('[data-mcp-readonly]')).to_be_checked();assert not state().get('mcpBridge') or state()['mcpBridge']['state']=='stopped'
  assert not {'runProject','startAI','prepareAI','startInstallation','startLogin','permission'}.intersection(calls),calls
  evidence=dict(actualEngine='ordinary EditorHome with existing DevelopmentTools',actualAdapter='managed MCP stdio over private Unix IPC',malformedPeerRetainsScope=True,initialReadOnly=True,existingSharedNodeDraft=True,duplicateStageOnce=True,unsentIntentAndOriginalFilesRetained=True,peerSourcePinAndHashCASRefused=True,humanCompilerReviewConfirm=True,projectSwitchAndColdRetireScope=True,confirmedSource='return value + 10;',realChatGPTApp=False,installed=False,registered=False,networkPort=False)
  page.screenshot(path='/tmp/confectory-mcp-plugin.png',full_page=True);pathlib.Path('/workspace/scratch/confectory-mcp-ui.json').write_text(json.dumps(evidence,indent=2)+'\n');print('PASS actual MCP plugin shared node/CAS/Confirm/cold '+json.dumps(evidence),flush=True)
