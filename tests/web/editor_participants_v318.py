from editor_navigation import goto_editor
import uuid,json,os,pathlib,subprocess,tempfile,time,shutil,sys,signal,urllib.request
from playwright.sync_api import sync_playwright,expect
from owned_responses import OwnedResponses
expect.set_options(timeout=30000)
repo=pathlib.Path(sys.argv[1]).resolve();report=json.load(open(sys.argv[2]));root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-participants-v318-'))
project=root/'ordinary-button-game';shutil.copytree(repo/'examples/button-game',project,ignore=shutil.ignore_patterns('.confectory'));manifest=project/'project.cpack';manifest.write_text(manifest.read_text().replace('../../',str(repo)+'/'))
before={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file()}
env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(root/'storage'),CONFECTORY_ENTRY_STORAGE=str(root/'storage'),CONFECTORY_WEB_PROJECT=str(manifest),PATH=str(pathlib.Path(env.get('CONFECTORY_DOTNET','dotnet')).parent)+os.pathsep+env['PATH'])
def start(n):
 log=root/f'host-{n}.log';stream=log.open('w');host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
 deadline=time.monotonic()+60
 while time.monotonic()<deadline:
  for line in log.read_text().splitlines():
   if line.startswith('CONFECTORY_WEB_UI '):return host,stream,line.split(' ',1)[1]
  if host.poll() is not None:raise AssertionError(log.read_text())
  time.sleep(.1)
 os.killpg(host.pid,signal.SIGTERM);host.wait(timeout=10);stream.close();raise AssertionError(log.read_text())
def stop(host,stream):
 os.killpg(host.pid,signal.SIGTERM)
 try:host.wait(timeout=10)
 except subprocess.TimeoutExpired:os.killpg(host.pid,signal.SIGKILL);host.wait()
 stream.close()
def saved():
 files=list((root/'storage/presentations').glob('*.json'));assert len(files)==1,files
 return json.loads(files[0].read_text())
def public_state(url):
 token=url.split('#',1)[1];endpoint=url.split('#',1)[0]+'api/request'
 def send(body):
  request=urllib.request.Request(endpoint,data=json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':token})
  with urllib.request.urlopen(request,timeout=30) as reply:return json.load(reply)
 for _ in range(400):
  mounted=send({'op':'mount'})
  if mounted.get('error',{}).get('code')=='busy':time.sleep(.01);continue
  assert mounted['ok'],mounted;break
 else:raise AssertionError('Read-only snapshot stayed busy')
 try:return mounted['state']
 finally:assert send({'op':'dispose','view':mounted['view']})['ok']
def invoke(url,endpoint,args):
 class RejectedStale(Exception):pass
 token=url.split('#',1)[1];api=url.split('#',1)[0]+'api/request'
 def send(body):
  request=urllib.request.Request(api,data=json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':token})
  with urllib.request.urlopen(request,timeout=30) as response:return json.load(response)
 for attempt in range(4):
  mounted=send({'op':'mount'})
  if not mounted.get('ok'):page.wait_for_timeout(20);continue
  request_id=uuid.uuid4().hex
  try:
   ack=send({'op':'invoke','view':mounted['view'],'scope':mounted['scope'],'requestId':request_id,'endpoint':endpoint,'input':args,'expectedRevision':mounted['revision']})
   if not ack.get('ok'):
    assert ack.get('error',{}).get('code')=='stale_revision',ack
    continue
   if ack.get('completed') or 'result' in ack:return ack.get('result')
   for _ in range(500):
    reply=send({'op':'update','view':mounted['view'],'scope':mounted['scope']})
    if reply.get('error',{}).get('code')=='scope_changed':
     current=public_state(url)
     if endpoint=='projectHelpers':assert set(args['helpers']).issubset(set(current['projectHelperIds']))
     elif endpoint=='selectHelperConversation':assert current['helperProfile']['helper']==args['helper']
     elif endpoint=='bindHelperAgent':assert current['connection']=='Confectory.Agent.Responses::Connection'
     else:raise AssertionError(('unexpected scope change',endpoint))
     return {}
    for row in reply.get('results',[]):
     if row['requestId']==request_id:
      if not row.get('ok') and row.get('error',{}).get('code')=='stale_revision':raise RejectedStale()
      assert row['ok'],row;return row.get('result')
    page.wait_for_timeout(10)
   raise AssertionError('owned metadata action timeout')
  except RejectedStale:continue
  finally:send({'op':'dispose','view':mounted['view']})
 raise AssertionError('owned metadata action stayed stale')
owned=OwnedResponses(None)
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for n in range(2):
  host,stream,url=start(n);page=browser.new_page(viewport={'width':1440,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));goto_editor(page,url);page.locator('.work-body').wait_for(timeout=30000)
  try:
   if n==0:
    page.locator('.brand').click();expect(page.locator('.home-grid')).to_be_visible();page.locator('#add-agent').click();connection=page.get_by_role('dialog',name='Agent 추가',exact=True);connection.get_by_role('button',name='OpenAI Responses',exact=True).click()
    for name,value in [('model','owned-cold-recovery-fixture'),('endpoint',owned.endpoint),('credentialReference','')]:connection.locator('[data-connection-field="'+name+'"]').fill(value)
    connection.locator('[data-agent-register]').click();expect(connection.locator('[data-agent-registration-state]')).to_contain_text('Agent 등록됨');connection.locator('[data-connection-cancel]').click();invoke(url,'helperGlobal',{'action':'import','agent':'Confectory.Agent.Responses::Connection'});page.locator('[data-enter]').first.click();expect(page.locator('.work-body')).to_be_visible();invoke(url,'projectHelpers',{'helpers':['main-helper']});invoke(url,'selectHelperConversation',{'helper':'main-helper'});invoke(url,'bindHelperAgent',{'helper':'main-helper'});assert not owned.requests
    page.locator('.home-side [data-helper="main-helper"]').first.click();card=page.locator('.participant-expanded-card');expect(card.locator('form')).to_have_class('helper-chat-compose');expect(card.locator('textarea')).to_have_attribute('rows','1');expect(card.locator('[data-helper-connection],[data-helper-stop],#participant-talk')).to_have_count(0);assert abs(card.locator('.messages').bounding_box()['height']-108)<1;card.locator('textarea').fill('UNSENT helper conversation');card.locator('.helper-window-pin').click();expect(card).to_have_class(__import__('re').compile('is-pinned'));card.locator('.sd-character').click();expect(card.locator('.sd-compose')).to_be_visible();expect(card.locator('textarea[aria-label="Helper 대화 입력"]').last).to_have_value('UNSENT helper conversation');page.wait_for_function('()=>typeof globalThis.confectoryFlushPresentation==="function"');page.evaluate('()=>globalThis.confectoryFlushPresentation()');expect(page.locator('#workspace-save-state')).to_have_text('');state=public_state(url);assert state['aiState']=='idle';assert state['aiPreview'] is None;assert not state['workers'];assert not state['draft']['dirty'];assert 'memory' not in state['helperProfile'];snapshot=saved();assert snapshot['participants'][0]['helper']=='main-helper';assert snapshot['participants'][0]['pinned'];page.screenshot(path=str(root/'actual-before-restart.png'))
    card.locator('textarea').last.press('Escape');card.locator('.sd-character').press('Escape');expect(card).to_have_count(0);page.locator('#augment').click();page.locator('[data-propose]').click();page.locator('#augment-direction').fill('owned loopback proposals for a cold record, no real account');page.locator('.modal button[type=submit]').click();expect(page.locator('#ai-start')).to_be_disabled();assert owned.requests==[]
    for permission in ['contentApproved','usageApproved']:
     choice=page.locator('[data-permission="'+permission+'"]');choice.check();expect(choice).to_be_enabled()
    page.locator('#ai-start').click();expect(page.locator('[data-card]')).to_have_count(3);assert len(owned.requests)==1;page.locator('[data-card]').first.click();expect(page.locator('#worker-summary button')).to_have_count(1);worker=public_state(url)['workers'][0];worker_id=worker['id'];page.locator('.augment-overlay [data-close]').click();page.locator('.home-side [data-helper="main-helper"]').first.click();page.locator('.participant-expanded-card [data-worker]').first.click();expect(page.locator('.window[data-key="worker"]')).to_contain_text(worker_id);assert len(owned.requests)==1;page.wait_for_function('()=>typeof globalThis.confectoryFlushPresentation==="function"');page.evaluate('()=>globalThis.confectoryFlushPresentation()');expect(page.locator('#workspace-save-state')).to_have_text('');page.locator('.home-side [data-helper="main-helper"]').first.click();page.locator('.participant-expanded-card .helper-window-pin').click();page.wait_for_function('()=>typeof globalThis.confectoryFlushPresentation==="function"');page.evaluate('()=>globalThis.confectoryFlushPresentation()');expect(page.locator('#workspace-save-state')).to_have_text('');
    page.locator('.brand').click();expect(page.locator('.home-grid')).to_be_visible();expect(page.locator('.participant-expanded-card')).to_have_count(0);page.locator('[data-enter]').first.click();expect(page.locator('.participant-expanded-card')).to_have_count(1);expect(page.locator('.participant-expanded-card textarea').last).to_have_value('UNSENT helper conversation')
   else:
    expect(page.locator('.window[data-key="worker"]')).to_contain_text('실행 소유자가 복원되지');expect(page.locator('#worker-prepare')).to_be_disabled();expect(page.locator('#worker-stop')).to_be_disabled();state=public_state(url);assert len(state['workers'])==1;assert state['workers'][0]['status']=='ready';assert state['workers'][0]['id']==worker_id;assert not state['aiOwnerAvailable'];assert len(owned.requests)==1
    card=page.locator('.participant-expanded-card');expect(card).to_have_count(1);expect(card).to_have_attribute('data-helper-id','main-helper');expect(card).to_have_class(__import__('re').compile('is-pinned'));card.locator('.sd-character').click();expect(card.locator('textarea').last).to_have_value('UNSENT helper conversation');card.locator('textarea').last.press('Escape');card.locator('.sd-character').press('Escape');expect(card).to_have_count(0);state=public_state(url);assert state['aiState']=='idle';assert state['aiPreview'] is None;assert len(state['workers'])==1;assert not state['draft']['dirty'];page.screenshot(path=str(root/'actual-after-restart.png'))
   assert not errors,errors
   assert all((project/name).read_bytes()==data for name,data in before.items())
  except Exception as e:
   page.screenshot(path=str(root/f'failure-{n}.png'));raise AssertionError(str(e)+'\nEvidence: '+str(root)+'\nErrors: '+str(errors)) from e
  finally:page.close();stop(host,stream)
 browser.close()
owned.close()
print('PASS ordinary ProjectPack actual Helper identity and unsubmitted input cold recovery '+str(root))
