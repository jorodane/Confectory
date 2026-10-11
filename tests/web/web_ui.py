"""Real ordinary EditorHome + ButtonGame packs through the common local web transport."""
import hashlib,json,os,pathlib,signal,subprocess,sys,tempfile,time,urllib.request,urllib.error,uuid,shutil
from playwright.sync_api import sync_playwright,expect
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());kind=sys.argv[3]
with tempfile.TemporaryDirectory(prefix='confectory-web-ui-') as directory:
 root=pathlib.Path(directory);env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_ENTRY_STORAGE=str(root/'storage'),CONFECTORY_HOME_STORAGE=str(root/'storage'),XDG_DATA_HOME=str(root/'data'),XDG_CACHE_HOME=str(root/'cache'))
 if env.get('CONFECTORY_DOTNET'):env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env.get('PATH','')
 # A regular existing user project copy, with actual object source and normal draft storage.
 project=root/'button-game';shutil.copytree(repo/'examples/button-game',project,ignore=shutil.ignore_patterns('.confectory'))
 manifest=project/'project.cpack';manifest.write_text(manifest.read_text().replace('../../',str(repo)+'/'))
 env['CONFECTORY_WEB_PROJECT']=str(manifest)
 original=(project/'Score.celem').read_bytes();log=root/'host.log'
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
   for headers in [{},{'X-Confectory-Session':token,'Origin':'https://untrusted.invalid'}]:
    try:urllib.request.urlopen(urllib.request.Request(origin+'/api/request',data=b'{"op":"mount"}',headers=headers));raise AssertionError('unauthorized transport accepted')
    except urllib.error.HTTPError as error:assert error.code==403
   for path in ['/missing.js','/../project.cpack','/api/snapshot']:
    try:urllib.request.urlopen(origin+path);raise AssertionError('undeclared resource served')
    except urllib.error.HTTPError:pass
   first=send({'op':'mount'});assert first['ok'];op='increase' if kind=='button' else 'objects'
   request=envelope(first,'invoke',endpoint=op,requestId='wrong-scope',expectedRevision=first['revision'],input={});request['scope']={'projectId':'other','helperId':'other'}
   assert send(request)['error']['code']=='scope_mismatch'
   request['scope']=dict(first['scope'],helperId='forged-helper');assert send(request)['error']['code']=='scope_mismatch'
   for denied in ['shell','readFile','Confectory.EditorHome.Model::Command','confirm','ai-start','host.open-file','host.close']:
    assert send(envelope(first,'invoke',endpoint=denied,requestId=denied,expectedRevision=first['revision'],input={}))['error']['code']=='endpoint_denied'
   stale=send(envelope(first,'invoke',endpoint=op,requestId='stale',expectedRevision=first['revision']-1,input={}));assert stale['ok'];assert settle(first,'stale')[0]['error']['code']=='stale_revision'
   request=envelope(first,'invoke',endpoint=op,requestId='dedup',expectedRevision=first['revision'],input={});assert send(request)['ok'];row,new=settle(first,'dedup');assert row['ok'],row
   assert send(request)['requestId']=='dedup';request['input']={'unexpected':'changed'};assert send(request)['error']['code']=='request_id_reused'
   assert send(envelope(first,'cancel',requestId='dedup'))['status']=='already_completed'
   assert send(envelope(first,'dispose'))['ok'];assert send(envelope(first,'update'))['error']['code']=='view_closed'
   with sync_playwright() as p:
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
     assert page.locator('.bubble-dock button:disabled').count()==4
     assert page.locator('.home-side').is_visible()
     page.locator('#objects-refresh').click();button=page.locator('[data-id="Example.ButtonGame::Score"]');expect(button).to_be_visible();button.click();expect(page.locator('#selection')).to_have_text('Example.ButtonGame::Score')
     source=page.locator('#source');text=source.input_value()+'\n// common-web-ui-draft\n';source.fill(text);page.locator('#save').click();expect(page.locator('#status')).to_have_text('Draft saved; final sources unchanged',timeout=30000)
     assert (project/'Score.celem').read_bytes()==original,'Save performed source Confirm'
     page.locator('#reconnect').click();expect(page.locator('#status')).to_contain_text('Reconnected');expect(source).to_have_value(text)
     page.reload();expect(page.locator('#status')).to_have_text('Ready');expect(source).to_have_value(text)
     # Another independent mount reads the same domain draft, without a UI-only storage copy.
     second=send({'op':'mount'});assert second['state']['draft']['text']==text and second['state']['draft']['dirty'];assert 'context' not in second['state'] and 'path' not in second['state']['draft']
     # Consumer CAS also rejects an outdated draft revision under a fresh transport revision.
     stale_input={'id':second['state']['draft']['id'],'text':'must not replace the shared draft','revision':second['state']['draft']['revision']-1}
     assert send(envelope(second,'invoke',endpoint='editDraft',requestId='draft-cas',expectedRevision=second['revision'],input=stale_input))['ok']
     result,current=settle(second,'draft-cas');assert not result['ok'] and current['state']['draft']['text']==text
     request=envelope(second,'invoke',endpoint='select',requestId='foreign-object',expectedRevision=current['revision'],input={'id':'Unowned.Project::Object'})
     assert send(request)['ok'];assert not settle(second,'foreign-object')[0]['ok']
     assert send(envelope(second,'dispose'))['ok']
     page.locator('#review').click();expect(page.locator('#confirm')).to_be_enabled(timeout=30000)
     assert (project/'Score.celem').read_bytes()==original,'Review performed source Confirm'
     review=send({'op':'mount'});assert review['state']['review']['id']=='Example.ButtonGame::Score'
     assert review['state']['review']['before']==original.decode() and review['state']['review']['after']==text
     assert 'path' not in review['state']['review'];assert send(envelope(review,'dispose'))['ok']
     page.locator('#confirm').click();expect(page.locator('#status')).to_have_text('Source confirmed',timeout=90000)
     assert (project/'Score.celem').read_text()==text,'explicit compiler-backed Confirm did not apply exact reviewed source'
     page.locator('#schema').click();expect(page.locator('[data-schema-id]')).to_have_text('Example.ButtonGame::Score',timeout=30000)
     schema_state=send({'op':'mount'});assert schema_state['state']['schema']['id']=='Example.ButtonGame::Score';assert send(envelope(schema_state,'dispose'))['ok']
     pending_text=text+'\n// retained browser input\n';source.fill(pending_text)
     page.locator('.brand').click();expect(page.locator('[data-project]')).to_have_count(1,timeout=30000)
     page.screenshot(path='/tmp/confectory-v196-consumer-home.png',full_page=True)
     assert page.locator('#open-local').is_disabled(),'browser diagnostic must not acquire native file authority'
     page.locator('[data-project]').click();expect(page.locator('#source')).to_have_value(pending_text,timeout=30000)
     assert (project/'Score.celem').read_text()==text,'hide/open committed unsaved browser input'
     assert send({'op':'mount'})['state']['draft']['text']==text,'HTML input became domain draft without Apply'
     source_window=page.locator('.window[data-key="source"]');source_window.locator('[data-fold]').click();expect(source).not_to_be_visible()
     assert source.input_value()==pending_text;source_window.locator('[data-fold]').click();expect(source).to_have_value(pending_text)
     area=page.locator('#workspace').bounding_box();bounds=source_window.bounding_box();assert bounds['y']+bounds['height']<=area['y']+area['height']-94+1,'editor overlaps reserved dock area'
     page.set_viewport_size({'width':960,'height':700});expect(source).to_have_value(pending_text);page.set_viewport_size({'width':1280,'height':720})
     page.locator('#run').click();expect(page.locator('#run')).to_contain_text('중지',timeout=30000)
     execution=send({'op':'mount'});assert execution['state']['executionState'] in ['building','running'];assert send(envelope(execution,'dispose'))['ok']
     page.locator('#run').click();expect(page.locator('#run')).to_contain_text('실행',timeout=30000)
     stopped=send({'op':'mount'});assert stopped['state']['executionState']=='stopped',stopped['state']['executionState'];assert send(envelope(stopped,'dispose'))['ok']
     expect(page.locator('#execution-logs')).to_contain_text('Stopped this project execution');expect(source).to_have_value(pending_text)
     assert (project/'Score.celem').read_text()==text,'Run/Stop applied unconfirmed browser input'
     changed_view=send({'op':'mount'});assert send(envelope(changed_view,'invoke',endpoint='select',requestId='other-editor-selection',expectedRevision=changed_view['revision'],input={'id':'Example.ButtonGame::Main'}))['ok']
     changed_row,changed_state=settle(changed_view,'other-editor-selection');assert changed_row['ok'];assert changed_state['state']['draft']['id']=='Example.ButtonGame::Main'
     expect(page.locator('#source-notice')).to_contain_text('입력을 유지했습니다',timeout=30000);expect(source).to_have_value(pending_text);expect(page.locator('#selection')).to_have_text('Example.ButtonGame::Score')
     page.locator('.window[data-key="browser"] .window-title strong').click();page.locator('[data-id="Example.ButtonGame::Score"]').click();expect(page.locator('#source-notice')).to_have_text('',timeout=30000);expect(source).to_have_value(pending_text)
     assert send(envelope(changed_view,'dispose'))['ok']





    page.screenshot(path='/tmp/confectory-web-ui-'+kind+'.png',full_page=True);assert not errors,errors;browser.close()
   print('Actual common WebUI '+kind+' Chromium PASS')
  finally:
   if host.poll() is None:host.send_signal(signal.SIGINT)
   try:host.wait(timeout=15)
   except subprocess.TimeoutExpired:host.kill();host.wait();raise AssertionError('host lifetime cleanup did not complete')
   assert host.returncode==0,log.read_text()
