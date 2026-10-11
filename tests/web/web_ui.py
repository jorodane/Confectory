"""Real ordinary EditorHome + ButtonGame packs through the common local web transport."""
import re,hashlib,json,os,pathlib,signal,subprocess,sys,tempfile,time,urllib.request,urllib.error,uuid,shutil
from playwright.sync_api import sync_playwright,expect
from owned_responses import OwnedResponses
class FailureEvidence:
 def __enter__(self):return self
 def __exit__(self,type,error,traceback):
  if error is not None:
   try:
    page.screenshot(path='/tmp/confectory-web-ui-failure.png',full_page=True);print('UI failure status:',page.locator('#status').inner_text(),flush=True)
    print('UI failure controls:',page.evaluate("()=>({confirm:document.querySelector('#confirm')?.disabled,run:document.querySelector('#run')?.disabled,source:document.querySelector('#selection')?.textContent})"),flush=True)
   except Exception:pass
  return False
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());kind=sys.argv[3]
with tempfile.TemporaryDirectory(prefix='confectory-web-ui-') as directory:
 root=pathlib.Path(directory);env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_ENTRY_STORAGE=str(root/'storage'),CONFECTORY_HOME_STORAGE=str(root/'storage'),XDG_DATA_HOME=str(root/'data'),XDG_CACHE_HOME=str(root/'cache'))
 if env.get('CONFECTORY_DOTNET'):env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env.get('PATH','')
 # A regular existing user project copy, with actual object source and normal draft storage.
 project=root/'button-game';shutil.copytree(repo/'examples/button-game',project,ignore=shutil.ignore_patterns('.confectory'))
 manifest=project/'project.cpack';manifest.write_text(manifest.read_text().replace('../../',str(repo)+'/'))
 env['CONFECTORY_WEB_PROJECT']=str(manifest)
 original=(project/'Score.celem').read_bytes();log=root/'host.log';owned=OwnedResponses(None) if kind=='editor' else None
 with log.open('w') as output:
  host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=output,stderr=subprocess.STDOUT)
  try:
   url=None;deadline=time.monotonic()+45
   while time.monotonic()<deadline:
    for line in log.read_text().splitlines():
     if line.startswith('CONFECTORY_WEB_UI '):url=line.split(' ',1)[1]
    if url:break
    assert host.poll() is None,log.read_text();time.sleep(.1)
   assert url,log.read_text();origin,token=url.split('/#')
   def send(data):
    req=urllib.request.Request(origin+'/api/request',data=json.dumps(data).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':token})
    return json.load(urllib.request.urlopen(req,timeout=20))
   def envelope(view,op,**kw):return dict(op=op,view=view['view'],scope=view['scope'],**kw)
   def settle(view,request_id):
    for _ in range(200):
     reply=send(envelope(view,'update'));assert reply['ok'],reply
     for row in reply['results']:
      if row['requestId']==request_id:return row,reply
     time.sleep(.01)
    raise AssertionError('request remained pending')
   def mount():
    for _ in range(400):
     reply=send({'op':'mount'})
     if reply.get('error',{}).get('code')=='busy':time.sleep(.01);continue
     assert reply.get('ok') and 'view' in reply,reply
     return reply
    raise AssertionError('read-only mount stayed busy')
   for headers in [{},{'X-Confectory-Session':token,'Origin':'https://untrusted.invalid'}]:
    try:urllib.request.urlopen(urllib.request.Request(origin+'/api/request',data=b'{"op":"mount"}',headers=headers));raise AssertionError('unauthorized transport accepted')
    except urllib.error.HTTPError as error:assert error.code==403
   for path in ['/missing.js','/../project.cpack','/api/snapshot']:
    try:urllib.request.urlopen(origin+path);raise AssertionError('undeclared resource served')
    except urllib.error.HTTPError:pass
   first=mount();assert first['ok'];op='increase' if kind=='button' else 'objects'
   request=envelope(first,'invoke',endpoint=op,requestId='wrong-scope',expectedRevision=first['revision'],input={});request['scope']={'projectId':'other','helperId':'other'}
   assert send(request)['error']['code']=='scope_mismatch'
   request['scope']=dict(first['scope'],helperId='forged-helper');assert send(request)['error']['code']=='scope_mismatch'
   for denied in ['shell','readFile','Confectory.EditorHome.Model::Command','confirm','ai-start','host.open-file','host.create-project','host.close']:
    assert send(envelope(first,'invoke',endpoint=denied,requestId=denied,expectedRevision=first['revision'],input={}))['error']['code']=='endpoint_denied'
   stale=send(envelope(first,'invoke',endpoint=op,requestId='stale',expectedRevision=first['revision']-1,input={}));assert stale['ok'];assert settle(first,'stale')[0]['error']['code']=='stale_revision'
   request=envelope(first,'invoke',endpoint=op,requestId='dedup',expectedRevision=first['revision'],input={});assert send(request)['ok'];row,new=settle(first,'dedup');assert row['ok'],row
   assert send(request)['requestId']=='dedup';request['input']={'unexpected':'changed'};assert send(request)['error']['code']=='request_id_reused'
   assert send(envelope(first,'cancel',requestId='dedup'))['status']=='already_completed'
   assert send(envelope(first,'dispose'))['ok'];assert send(envelope(first,'update'))['error']['code']=='view_closed'
   with sync_playwright() as p,FailureEvidence():
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-gpu']);page=browser.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(url);expect(page.locator('#status')).to_have_text('Ready',timeout=30000)
    if kind=='button':
     expect(page.locator('#score')).to_have_text('1');page.locator('#increase').click();expect(page.locator('#score')).to_have_text('2');page.locator('#reconnect').click();expect(page.locator('#score')).to_have_text('2');page.locator('#reset').click();expect(page.locator('#score')).to_have_text('0')
    else:
     # Every original portrait must cross the ordinary declared-resource transport intact.
     for image_path in sorted((repo/'examples/editor-home/ui/assets').glob('*.png')):
      served=urllib.request.urlopen(origin+'/assets/'+image_path.name).read()
      assert hashlib.sha256(served).digest()==hashlib.sha256(image_path.read_bytes()).digest()
      assert page.evaluate("async path=>{const image=new Image();image.src=path;await image.decode();return image.naturalWidth>0&&image.naturalHeight>0}",'/assets/'+image_path.name)
     page.locator('#issues').click();expect(page.locator('.modal')).to_contain_text('연결되지 않았습니다');page.locator('.modal [data-close]').click()
     assert page.locator('.home-side').is_visible()
     assert not page.locator('#source').is_visible(),'raw source should be an explicit advanced view'
     page.locator('#add-helper').click();expect(page.locator('[data-recruit="global"]')).to_be_visible()
     page.locator('[data-recruit="global"]').click();expect(page.locator('#helper-list')).to_contain_text('main-helper')
     page.locator('#helper-list button').click();expect(page.locator('#helper-summary')).to_contain_text('main-helper',timeout=30000)
     # Common memory excluded by default. No provider or account is opened.
     expect(page.locator('#allow-common')).not_to_be_checked()
     page.locator('#helper-memory').fill('local explicitly scoped note');page.locator('#remember').click();expect(page.locator('#status')).to_contain_text('로컬에 저장됨')
     page.locator('#chat').click();page.locator('#chat-input').fill('local project message');page.locator('#chat-input').blur();expect(page.locator('#status')).to_contain_text('전송 없음')
     page.locator('#add-agent').click();expect(page.locator('#connection-list button')).not_to_have_count(0)
     local_state=mount();assert local_state['scope']['helperId']=='main-helper';assert not local_state['scope']['allowCommon'];assert local_state['state']['chatDraft']=='local project message';assert local_state['state']['aiState']=='idle';assert 'memory' not in local_state['state']['helperProfile'];assert 'config' not in local_state['state'];assert send(envelope(local_state,'dispose'))['ok']
     for key in ['connections','helpers']:
      page.locator('.window[data-key="'+key+'"] [data-close]').click()

     page.locator('#nav').click();button=page.locator('[data-id="Example.ButtonGame::Score"]');expect(button).to_be_visible();button.click();expect(page.locator('[data-schema-id]')).to_have_text('Example.ButtonGame::Score');page.screenshot(path='/tmp/confectory-v196-semantic-project.png',full_page=True);page.locator('#yogi').click();page.locator('#yogi-exactly').click();expect(page.locator('#yogi-items')).to_contain_text('Example.ButtonGame::Score');page.locator('#yogi-capture').click();expect(page.locator('#yogi-items')).to_contain_text('선택 영역 이미지',timeout=30000);page.locator('[data-operation="image-preview"]').click();expect(page.locator('[data-yogi-image]')).to_be_visible();assert page.locator('[data-yogi-image]').evaluate("canvas=>{const bytes=canvas.getContext('2d').getImageData(0,0,canvas.width,canvas.height).data;return new Set(bytes).size>2}")
     capture_state=mount();images=[item for item in capture_state['state']['yogi']['items'] if item['kind']=='image'];assert len(images)==1 and 'pixels' not in images[0]['capture'];assert 0<images[0]['capture']['width']<=512 and 0<images[0]['capture']['height']<=512
     invalid={'action':'capture','id':'Example.ButtonGame::Score','image':{'encoding':'rgb24-base64','width':1,'height':1,'pixels':'AAAA','hash':'0'*64}}
     assert send(envelope(capture_state,'invoke',endpoint='yogi',requestId='bad-capture-hash',expectedRevision=capture_state['revision'],input=invalid))['ok'];rejected,after_capture=settle(capture_state,'bad-capture-hash');assert not rejected['ok'];assert len(after_capture['state']['yogi']['items'])==2 and after_capture['state']['yogi']['pending']==[];assert send(envelope(capture_state,'dispose'))['ok']
     page.locator('#yogi-text').fill('local object package');page.locator('#yogi-save').click();expect(page.locator('#status')).to_contain_text('내용 적용됨');page.locator('#yogi-seal').click();expect(page.locator('#yogi-seal')).to_have_text('봉인 해제');page.locator('.window[data-key="yogi"] [data-close]').click();page.locator('.window[data-key="schema"] [data-close]').click();page.locator('#nav').click();page.locator('#advanced-source').click();expect(page.locator('#status')).to_have_text('고급 소스 탐색',timeout=30000);expect(page.locator('#selection')).to_have_text('Example.ButtonGame::Score')
     advanced=mount();bodies=[u['id'] for u in advanced['state']['units'] if u['kind']=='body'];assert bodies,'advanced mode must expose actual owned bodies';owned.target=bodies[0];assert send(envelope(advanced,'dispose'))['ok']
     page.locator('[data-id="'+bodies[0]+'"]').click();expect(page.locator('#selection')).to_have_text(bodies[0],timeout=30000)
     page.locator('#nav').click();page.locator('[data-id="Example.ButtonGame::Score"]').click();expect(page.locator('#advanced-source')).to_be_enabled(timeout=30000);page.locator('#nav').click();page.locator('#advanced-source').click()
     # Independent production Model owners retain exact IDs and local input across selection/hide/poll.
     page.locator('#nav').click();page.locator('#keep-source').click()
     one=page.locator('.window[data-key="editor-1"]');expect(one.locator('[data-editor-id]')).to_have_text('Example.ButtonGame::Score')
     first_text=one.locator('[data-editor-source]').input_value();one.locator('[data-editor-source]').fill(first_text+'\n// retained independently\n')
     page.locator('#nav').click();page.locator('[data-id="'+bodies[0]+'"]').click();page.locator('#nav').click();page.locator('#keep-source').click()
     two=page.locator('.window[data-key="editor-2"]');expect(two.locator('[data-editor-id]')).to_have_text(bodies[0]);other_text=two.locator('[data-editor-source]').input_value();two.locator('[data-editor-source]').fill(other_text+'\n// second independent input\n')
     page.locator('#nav').click();page.locator('[data-id="Example.ButtonGame::Score"]').click();expect(page.locator('#advanced-source')).to_be_enabled(timeout=30000)
     # A primary selection does not retarget either independent source window.
     expect(one.locator('[data-editor-source]')).to_have_value(first_text+'\n// retained independently\n');expect(two.locator('[data-editor-source]')).to_have_value(other_text+'\n// second independent input\n')
     page.locator('.brand').click();expect(page.locator('[data-project]')).not_to_have_count(0);page.locator('[data-project]').filter(has_text='ButtonGame').first.click()
     one=page.locator('.window[data-key="editor-1"]');two=page.locator('.window[data-key="editor-2"]');expect(one.locator('[data-editor-source]')).to_have_value(first_text+'\n// retained independently\n');expect(two.locator('[data-editor-source]')).to_have_value(other_text+'\n// second independent input\n')
     page.locator('#nav').click();page.locator('#retained-editors button').nth(0).click();one.locator('[data-close]').click();page.locator('#nav').click();page.locator('#retained-editors button').nth(0).click();expect(one.locator('[data-editor-source]')).to_have_value(first_text+'\n// retained independently\n')
     one.locator('[data-editor-apply]').click();expect(page.locator('#status')).to_have_text('Shared draft updated',timeout=30000)
     shared=mount();assert shared['state']['draft']['text']==first_text+'\n// retained independently\n';assert shared['state']['editorViews'][0]['id']=='Example.ButtonGame::Score';assert shared['state']['editorViews'][1]['id']==bodies[0];assert send(envelope(shared,'dispose'))['ok']
     # Restore only the edited draft through the public CAS action, and release clean owners.
     one.locator('[data-editor-source]').fill(first_text);one.locator('[data-editor-apply]').click();expect(page.locator('#status')).to_have_text('Shared draft updated');one.locator('[data-editor-release]').click();expect(page.locator('#retained-editors button')).to_have_count(1)
     page.locator('#nav').click();page.locator('#retained-editors button').click();two.locator('[data-editor-reset]').click();two.locator('[data-editor-release]').click()
     page.locator('#nav').click();page.locator('#object-kind').select_option('function');expect(page.locator('#objects [data-id="Example.ButtonGame::Score"]')).to_have_count(0,timeout=30000);expect(page.locator('#objects [data-id="Example.ButtonGame::Main"]')).to_be_visible(timeout=30000)
     page.locator('#nav').click();page.locator('#keep-properties').click();prop=page.locator('.window[data-key="editor-1"]');expect(prop.locator('[data-schema-id]')).to_have_text('Example.ButtonGame::Score')
     page.locator('#nav').click();page.locator('[data-id="Example.ButtonGame::Main"]').click();expect(page.locator('#advanced-source')).to_be_enabled(timeout=30000);page.locator('#nav').click();page.locator('#retained-editors button').click()
     field=prop.locator('[data-schema-field="initial"]');field.fill('7');field.locator('..').get_by_role('button',name='Apply field',exact=True).click();expect(page.locator('#status')).to_have_text('Shared field draft updated',timeout=30000);expect(prop.locator('[data-schema-field="initial"]')).to_have_value('7')
     field=prop.locator('[data-schema-field="initial"]');field.fill('0');field.locator('..').get_by_role('button',name='Apply field',exact=True).click();expect(prop.locator('[data-schema-field="initial"]')).to_have_value('0',timeout=30000);prop.locator('[data-operation="release-view"]').click();expect(page.locator('#retained-editors button')).to_have_count(0)
     page.locator('#object-kind').select_option('object');expect(page.locator('#objects [data-id="Example.ButtonGame::Main"]')).to_have_count(0);expect(page.locator('#objects [data-id="Example.ButtonGame::Score"]')).to_be_visible();page.locator('[data-id="Example.ButtonGame::Score"]').click();expect(page.locator('#advanced-source')).to_be_enabled();page.locator('#nav').click();page.locator('#advanced-source').click();expect(page.locator('#source')).to_be_visible(timeout=30000)
     no_task=mount()
     for endpoint in ['prepareWorker','stopWorker','recoverWorker','inspectAdoption','reviewWorker','adoptWorker']:
      no_task_state=send(envelope(no_task,'update'));request_id='foreign-'+endpoint;assert send(envelope(no_task,'invoke',endpoint=endpoint,requestId=request_id,expectedRevision=no_task_state['revision'],input={'task':'unowned-task','ids':['Unowned::Source'],'token':'forged','goalEvidence':'must not write'}))['ok'];failed,no_task_state=settle(no_task,request_id);assert not failed['ok'],endpoint
     assert send(envelope(no_task,'dispose'))['ok']
     source=page.locator('#source');text=source.input_value()+'\n// common-web-ui-draft\n';source.fill(text);page.locator('#save').click();expect(page.locator('#status')).to_have_text('Draft saved; final sources unchanged',timeout=30000)
     assert (project/'Score.celem').read_bytes()==original,'Save performed source Confirm'
     retained_draft=mount();assert retained_draft['state']['draft']['text']==text;assert send(envelope(retained_draft,'dispose'))['ok']
     page.reload();expect(page.locator('#status')).to_have_text('Ready');page.locator('#nav').click();page.locator('#advanced-source').click();expect(source).to_have_value(text)
     # Another independent mount reads the same domain draft, without a UI-only storage copy.
     second=mount();assert second['state']['draft']['text']==text and second['state']['draft']['dirty'];assert 'context' not in second['state'] and 'path' not in second['state']['draft']
     # Consumer CAS also rejects an outdated draft revision under a fresh transport revision.
     stale_input={'id':second['state']['draft']['id'],'text':'must not replace the shared draft','revision':second['state']['draft']['revision']-1}
     assert send(envelope(second,'invoke',endpoint='editDraft',requestId='draft-cas',expectedRevision=second['revision'],input=stale_input))['ok']
     result,current=settle(second,'draft-cas');assert not result['ok'] and current['state']['draft']['text']==text
     request=envelope(second,'invoke',endpoint='select',requestId='foreign-object',expectedRevision=current['revision'],input={'id':'Unowned.Project::Object'})
     assert send(request)['ok'];assert not settle(second,'foreign-object')[0]['ok']
     assert send(envelope(second,'dispose'))['ok']
     page.locator('#review').click();expect(page.locator('#confirm')).to_be_enabled(timeout=30000)
     assert (project/'Score.celem').read_bytes()==original,'Review performed source Confirm'
     review=mount();assert review['state']['review']['id']=='Example.ButtonGame::Score'
     assert review['state']['review']['before']==original.decode() and review['state']['review']['after']==text
     assert 'path' not in review['state']['review'];assert send(envelope(review,'dispose'))['ok']
     page.locator('#confirm').click();expect(page.locator('#status')).to_have_text('Source confirmed',timeout=180000)
     assert (project/'Score.celem').read_text()==text,'explicit compiler-backed Confirm did not apply exact reviewed source'
     page.locator('#schema').click();expect(page.locator('[data-schema-id]')).to_have_text('Example.ButtonGame::Score',timeout=30000)
     schema_state=mount();assert schema_state['state']['schema']['id']=='Example.ButtonGame::Score';assert send(envelope(schema_state,'dispose'))['ok']
     # Actual settings pack authoring and permission review, with no credentials or provider dispatch.
     page.locator('.brand').click();expect(page.locator('.home-grid')).to_be_visible(timeout=30000);page.locator('#add-helper').click();expect(page.locator('#global-helper-list')).to_contain_text('main-helper');page.locator('.modal [data-close]').click();page.locator('#add-agent').click()
     page.locator('#connection-choice').select_option('Confectory.Agent.Responses::Connection');page.locator('#connection-edit').click()
     expect(page.locator('[data-schema-id]')).to_have_text('Confectory.AISettings::Settings',timeout=30000)
     assert not page.locator('#source').is_visible()
     for name,value in [('model','owned-ui-no-call'),('endpoint',owned.endpoint),('credentialReference','')]:
      field=page.locator('[data-schema-field="'+name+'"]');field.fill(value);field.locator('..').get_by_role('button',name='Apply field',exact=True).click();expect(page.locator('#status')).to_have_text('Shared field draft updated',timeout=30000)
     page.locator('#semantic-save').click();expect(page.locator('#status')).to_have_text('Draft saved; final sources unchanged',timeout=30000)
     page.locator('.brand').click();expect(page.locator('[data-project]')).to_have_count(1,timeout=30000);page.locator('[data-enter]').click()
     page.locator('#add-agent').click();page.locator('#connection-list button').filter(has_text='Confectory.Agent.Responses::Connection').click();expect(page.locator('#status')).to_contain_text('전송 없음',timeout=30000)
     page.locator('.window[data-key="connections"] [data-close]').click();page.locator('#chat').click();page.locator('#chat-input').fill('review without sending');page.locator('#chat-prepare').click();expect(page.locator('#ai-start')).to_be_disabled(timeout=30000)
     preview=mount();assert preview['state']['aiPreview']['message']=='review without sending';assert 'config' not in preview['state']['aiPreview'];assert len(preview['state']['aiPreview']['requirements'])==2
     assert send(envelope(preview,'invoke',endpoint='startAI',requestId='unapproved-start',expectedRevision=preview['revision'],input={'token':preview['state']['aiPreview']['token']}))['ok'];refused,after=settle(preview,'unapproved-start');assert not refused['ok'] and after['state']['aiOutput'] in [None,''];assert send(envelope(preview,'dispose'))['ok']
     page.locator('[data-permission="contentApproved"]').check();expect(page.locator('#status')).to_contain_text('아직 전송 없음');expect(page.locator('#ai-start')).to_be_disabled()
     page.locator('#cancel-preview').click();expect(page.locator('#status')).to_contain_text('전송 없음');page.locator('#logs-tab').click()
     page.locator('#augment').click();page.locator('#augment-direction').fill('retain semantic object focus');page.locator('#reroll').click();expect(page.locator('#ai-start')).to_be_disabled(timeout=30000)
     proposal=mount();assert proposal['state']['aiPreview']['kind']=='proposals' and proposal['state']['aiPreview']['target']=='Example.ButtonGame::Score';assert proposal['state']['augment']['cards']==[];assert proposal['state']['workers']==[];assert send(envelope(proposal,'dispose'))['ok']
     page.locator('#cancel-preview').click();expect(page.locator('#status')).to_contain_text('전송 없음');assert owned.requests==[],'preflight/denied start contacted provider'
     # Positive HTML path over unchanged production Responses, Agent, tools, Task and adoption contracts.
     page.locator('#augment').click();page.locator('#augment-direction').fill('Owned loopback proposal, no account or credentials');page.locator('#reroll').click()
     def approve_and_start():
      for permission in ['contentApproved','usageApproved']:
       choice=page.locator('[data-permission="'+permission+'"]');choice.check();expect(choice).to_be_enabled(timeout=30000)
      expect(page.locator('#ai-start')).to_be_enabled(timeout=30000);page.locator('#ai-start').click();expect(page.locator('.window[data-key="ai-preview"]')).to_have_count(0,timeout=30000)
     approve_and_start();expect(page.locator('[data-card]')).to_have_count(3,timeout=30000);assert len(owned.requests)==1 and not owned.errors,owned.errors
     page.locator('[data-card]').first.click();expect(page.locator('#worker-summary button')).to_have_count(1,timeout=30000);page.locator('.window[data-key="augment"] [data-close]').click();page.locator('.home-side [data-helper]').filter(has_text='main-helper').click();page.locator('.modal [data-worker]').click();page.locator('#worker-prepare').click();approve_and_start()
     expect(page.locator('#worker-source-list')).to_contain_text(bodies[0],timeout=30000);expect(page.locator('.window[data-key="worker"]')).to_contain_text('awaiting-verification',timeout=30000);assert len(owned.requests)==4 and not owned.errors,owned.errors
     body_owner=bodies[0].split('::',1)[1].split('/body:',1)[0];locator=re.search(r'element\s+'+re.escape(body_owner)+r'\s+implementation\s+"([^"]+)"',manifest.read_text());assert locator;definition=(project/locator.group(1)).read_text();body_path=project/re.search(r'body\s+common\s+"([^"]+)"',definition).group(1);before_worker=body_path.read_text();assert 'owned HTTP Worker draft' not in before_worker,'Worker bypassed draft boundary'
     page.locator('[data-worker-source]').check();page.locator('#worker-review').click();expect(page.locator('#worker-adopt')).to_be_enabled(timeout=30000);assert body_path.read_text()==before_worker,'Review committed Worker draft'
     page.locator('#worker-goal-evidence').fill('Observed exact owned HTTP comment staged in the selected body. Compiler and source acceptance only; game runtime outcome not executed.');page.locator('#worker-adopt').click();expect(page.locator('.window[data-key="worker-review"]')).to_have_count(0,timeout=180000);assert body_path.read_text()==before_worker+'\n// owned HTTP Worker draft; human review required\n'
     adopted=mount();assert adopted['state']['workers'][0]['status']=='completed';assert adopted['state']['workers'][0]['adoptionState']=='recorded';assert send(envelope(adopted,'dispose'))['ok'];page.locator('.window[data-key="worker"] [data-close]').click()
     page.locator('#build-target').click();expect(page.locator('[data-target-choice] option')).to_have_count(3);page.locator('[data-target-choice]').select_option('windows');expect(page.locator('#status')).to_contain_text('windows');page.locator('[data-target-choice]').select_option('linux');page.locator('.window[data-key="targets"] [data-close]').click()
     page.locator('#nav').click();page.locator('#advanced-source').click()
     from semantic_authoring import verify_schema_authoring
     verify_schema_authoring(page,project,mount,send,envelope)
     pending_text=text+'\n// retained browser input\n';source.fill(pending_text)
     page.locator('.brand').click();expect(page.locator('[data-project]')).to_have_count(1,timeout=30000)
     page.screenshot(path='/tmp/confectory-v196-consumer-home.png',full_page=True)
     page.locator('#open-project').click();expect(page.locator('.modal')).to_contain_text('지원하지 않습니다');page.locator('.modal [data-close]').click()
     page.locator('[data-enter]').click();expect(page.locator('#source')).to_have_value(pending_text,timeout=30000)
     assert (project/'Score.celem').read_text()==text,'hide/open committed unsaved browser input'
     assert mount()['state']['draft']['text']==text,'HTML input became domain draft without Apply'
     source_window=page.locator('.window[data-key="source"]');source_window.locator('[data-fold]').click();expect(source).not_to_be_visible()
     assert source.input_value()==pending_text;source_window.locator('[data-fold]').click();expect(source).to_have_value(pending_text)
     area=page.locator('#workspace').bounding_box();bounds=source_window.bounding_box();assert bounds['y']+bounds['height']<=area['y']+area['height']-94+1,'editor overlaps reserved dock area'
     page.set_viewport_size({'width':960,'height':700});expect(source).to_have_value(pending_text);page.set_viewport_size({'width':1280,'height':720})
     page.locator('#run').click();expect(page.locator('#run')).to_contain_text('중지',timeout=30000)
     execution=mount();assert execution['state']['executionState'] in ['building','running'];assert send(envelope(execution,'dispose'))['ok']
     page.locator('#run').click();expect(page.locator('#run')).to_contain_text('실행',timeout=30000)
     stopped=mount();assert stopped['state']['executionState']=='stopped',stopped['state']['executionState'];assert send(envelope(stopped,'dispose'))['ok']
     expect(page.locator('#execution-logs')).to_contain_text('Stopped this project execution');expect(source).to_have_value(pending_text)
     assert (project/'Score.celem').read_text()==text,'Run/Stop applied unconfirmed browser input'
     changed_view=mount();assert send(envelope(changed_view,'invoke',endpoint='select',requestId='other-editor-selection',expectedRevision=changed_view['revision'],input={'id':'Example.ButtonGame::Main'}))['ok']
     changed_row,changed_state=settle(changed_view,'other-editor-selection');assert changed_row['ok'];assert changed_state['state']['draft']['id']=='Example.ButtonGame::Main'
     expect(page.locator('#source-notice')).to_contain_text('입력을 유지했습니다',timeout=30000);expect(source).to_have_value(pending_text);expect(page.locator('#selection')).to_have_text('Example.ButtonGame::Score')
     page.locator('#nav').click();page.locator('[data-id="Example.ButtonGame::Score"]').click();expect(page.locator('#source-notice')).to_have_text('',timeout=30000);expect(source).to_have_value(pending_text)
     assert send(envelope(changed_view,'dispose'))['ok']





    page.screenshot(path='/tmp/confectory-web-ui-'+kind+'.png',full_page=True);assert not errors,errors;browser.close()
   print('Actual common WebUI '+kind+' Chromium PASS')
  except Exception:
   try:
    page.screenshot(path='/tmp/confectory-web-ui-failure.png',full_page=True);print('UI failure status:',page.locator('#status').inner_text(),flush=True)
   except Exception:pass
   raise
  finally:
   if host.poll() is None:host.send_signal(signal.SIGINT)
   try:host.wait(timeout=15)
   except subprocess.TimeoutExpired:host.kill();host.wait();raise AssertionError('host lifetime cleanup did not complete')
   if owned is not None:owned.close()
   assert host.returncode==0,log.read_text()
