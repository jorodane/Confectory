from editor_navigation import goto_editor
import json,os,pathlib,subprocess,tempfile,time,shutil,sys,signal,urllib.request
from playwright.sync_api import sync_playwright,expect
expect.set_options(timeout=30000)
repo=pathlib.Path(sys.argv[1]).resolve();report=json.load(open(sys.argv[2]));root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-yogi-v318-'))
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
 else:raise AssertionError('read-only mount remained busy')
 try:return mounted['state']
 finally:assert send({'op':'dispose','view':mounted['view']})['ok']
def rpc(url,endpoint,input):
 token=url.split('#',1)[1];address=url.split('#',1)[0]+'api/request'
 def send(body):
  req=urllib.request.Request(address,data=json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':token})
  with urllib.request.urlopen(req,timeout=30) as response:return json.load(response)
 for attempt in range(8):
  view=send({'op':'mount'});
  if view.get('error',{}).get('code')=='busy':time.sleep(.02);continue
  assert view['ok'],view;rid='owned-run-probe-'+str(time.time_ns());envelope={'view':view['view'],'scope':view['scope']}
  try:
   accepted=send(dict(envelope,op='invoke',endpoint=endpoint,input=input,expectedRevision=view['revision'],requestId=rid));assert accepted['ok'],accepted
   for _ in range(300):
    result=send(dict(envelope,op='update'));assert result['ok'],result
    rows=[row for row in result['results'] if row['requestId']==rid]
    if rows:
     if rows[0].get('error',{}).get('code')=='stale_revision':break
     return rows[0],result['state']
    time.sleep(.01)
   else:raise AssertionError('pending actual command')
  finally:assert send(dict(envelope,op='dispose'))['ok']
 raise AssertionError('stale actual request after explicit fixture retries')
import hashlib,copy,uuid
errors=[];requests=[]
def store():
 files=list((project/'.confectory/yogi').glob('package-*.json'));assert len(files)==1,files
 return files[0]
def begin(browser,n):
 host,stream,url=start(n);page=browser.new_page(viewport={'width':1440,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)))
 def request(req):
  if req.url.endswith('api/request'):
   try:
    body=req.post_data_json
    if body.get('op')=='invoke':requests.append((body.get('endpoint'),body.get('input',{}).get('action')))
   except Exception:pass
 page.on('request',request);goto_editor(page,url);page.locator('.work-body').wait_for(timeout=30000);return host,stream,url,page
def open_yogi(page):
 page.locator('#yogi').click();expect(page.locator('#nav')).to_be_enabled();expect(page.locator('.yogi-clipboard')).to_be_visible()
def expand(page,kind):
 button=page.locator('[data-type="'+kind+'"]')
 if button.get_attribute('aria-expanded')!='true':button.click()
 expect(button).to_have_attribute('aria-expanded','true')
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 try:
  host,stream,url,page=begin(browser,0)
  try:
   page.locator('#nav').click();page.locator('.nav-menu button').filter(has_text='개념').first.click();expect(page.locator('#nav')).to_be_enabled();page.locator('#nav').click();page.locator('[data-id="Example.ButtonGame::Score"]').click();expect(page.locator('[data-schema-id]')).to_have_text('Example.ButtonGame::Score');page.locator('#yogi').click();expect(page.locator('#nav')).to_be_enabled();page.locator('[data-schema-field="initial"]').click();expand(page,'ey');expect(page.locator('#yogi-items')).to_contain_text('Example.ButtonGame::Score');expand(page,'lay');page.locator('#yogi-capture').click();expect(page.locator('#yogi-items')).to_contain_text('선택 영역 이미지',timeout=30000);page.locator('#yogi-text').fill('saved local description');page.locator('#yogi-save').click();expect(page.locator('#status')).to_contain_text('내용 적용됨');page.locator('#yogi-seal').click();expect(page.locator('.yogi-package')).to_be_visible();page.wait_for_function('()=>typeof globalThis.confectoryFlushPresentation==="function"');page.evaluate('()=>globalThis.confectoryFlushPresentation()');expect(page.locator('#workspace-save-state')).to_have_text('');state=public_state(url);assert state['yogi']['sealed'];assert len(state['yogi']['items'])==2;assert state['yogi']['storage']=={'bound':True,'dirty':False};saved_items=state['yogi']['items'];saved_image=next(item for item in saved_items if item['kind']=='image');assert 'pixels' not in saved_image['capture'];initial_doc=json.loads(store().read_text());assert initial_doc['project']==state['projectId'] and initial_doc['owner']=='local-user';assert initial_doc['package']['text']=='saved local description';page.screenshot(path=str(root/'actual-sealed.png'))
  finally:page.close();stop(host,stream)
  requests.clear();host,stream,url,page=begin(browser,1)
  try:
   expect(page.locator('.yogi-package')).to_be_visible();state=public_state(url);assert state['yogi']['sealed'];assert state['yogi']['text']=='saved local description';assert [item['item'] for item in state['yogi']['items']]==[item['item'] for item in saved_items];assert 1<=len([action for endpoint,action in requests if endpoint=='yogi'])<=8 and all(action=='show' for endpoint,action in requests if endpoint=='yogi'),requests;assert not any(endpoint in ['startAI','runProject','permission'] for endpoint,_ in requests)
   page.locator('.yogi-package').click();expect(page.locator('#yogi-text')).to_have_value('saved local description');page.locator('#yogi-text').fill('UNAPPLIED local description');page.locator('.yogi-clipboard [data-close]').click();expect(page.locator('.yogi-clipboard')).to_have_count(0);assert public_state(url)['yogi']['text']=='saved local description';open_yogi(page);expect(page.locator('#yogi-text')).to_have_value('UNAPPLIED local description');head=page.locator('.yogi-clipboard-head');box=head.bounding_box();page.mouse.move(box['x']+40,box['y']+18);page.mouse.down();page.mouse.move(690,320,steps=12);page.mouse.up();page.wait_for_function('()=>typeof globalThis.confectoryFlushPresentation==="function"');page.evaluate('()=>globalThis.confectoryFlushPresentation()');expect(page.locator('#workspace-save-state')).to_have_text('');position=saved()['yogiPresentation'];assert position['open'];page.locator('.brand').click();expect(page.locator('.home-grid')).to_be_visible();expect(page.locator('.yogi-clipboard')).to_have_count(0);page.locator('[data-enter]').first.click();expect(page.locator('#yogi-text')).to_have_value('UNAPPLIED local description');assert public_state(url)['yogi']['text']=='saved local description';page.wait_for_function('()=>typeof globalThis.confectoryFlushPresentation==="function"');page.evaluate('()=>globalThis.confectoryFlushPresentation()');expect(page.locator('#workspace-save-state')).to_have_text('');golden=json.loads(store().read_text());golden_bytes=store().read_bytes();page.screenshot(path=str(root/'actual-pending-description.png'))
  finally:page.close();stop(host,stream)
  requests.clear();host,stream,url,page=begin(browser,2)
  try:
   expect(page.locator('#yogi-text')).to_have_value('UNAPPLIED local description');bounds=page.locator('.yogi-clipboard').bounding_box();assert abs(bounds['x']-position['x'])<2 and abs(bounds['y']-position['y'])<2,(bounds,position);state=public_state(url);assert state['yogi']['text']=='saved local description';assert next(item for item in state['yogi']['items'] if item['kind']=='semantic')['availability']=='current';expand(page,'lay');page.locator('[data-operation="image-preview"]').click();canvas=page.locator('[data-yogi-image]');expect(canvas).to_be_visible();assert canvas.evaluate("canvas=>new Set(canvas.getContext('2d').getImageData(0,0,canvas.width,canvas.height).data).size>2");assert 1<=len([action for endpoint,action in requests if endpoint=='yogi'])<=8 and all(action=='show' for endpoint,action in requests if endpoint=='yogi');page.screenshot(path=str(root/'actual-cold-content.png'))
   # External owned writer: CAS must preserve both its file and the live unsaved text.
   concurrent=copy.deepcopy(golden);concurrent['package']['text']='external owned writer';store().write_text(json.dumps(concurrent));external=store().read_bytes();row,changed=rpc(url,'yogi',{'action':'text','text':'live conflict description'});assert not row['ok'];assert changed['yogi']['text']=='live conflict description' and changed['yogi']['storage']['dirty'];assert store().read_bytes()==external;row,changed=rpc(url,'yogi',{'action':'discard'});assert not row['ok'];assert len(changed['yogi']['items'])==2 and changed['yogi']['text']=='live conflict description';assert store().read_bytes()==external
  finally:page.close();stop(host,stream);store().write_bytes(golden_bytes)
  # Stored capture reservation is a bounded fixture record; restoration cannot recapture it.
  pending=copy.deepcopy(golden);image=next(item for item in pending['package']['items'] if item['kind']=='image')['capture'];ticket=uuid.uuid4().hex;pending['package']['pending']=[dict(item=ticket,**{key:image[key] for key in ['source','view','x','y','width','height']})];store().write_text(json.dumps(pending));host,stream,url,page=begin(browser,3)
  try:
   expect(page.locator('#yogi-text')).to_be_visible();state=public_state(url);assert state['yogi']['pending']==[];assert len(state['yogi']['interrupted'])==1 and state['yogi']['interrupted'][0]['item']==ticket;assert len(state['yogi']['items'])==2;expand(page,'lay');expect(page.locator('#yogi-items')).to_contain_text('캡처 중단됨');expect(page.locator('#yogi-seal')).to_be_disabled();assert json.loads(store().read_text())['package']['pending']==[];page.screenshot(path=str(root/'actual-interrupted-capture.png'))
  finally:page.close();stop(host,stream);store().write_bytes(golden_bytes)
  # Actual source changes/deletion in the owned ordinary copy, never in the repository.
  score=project/'Score.celem';original_score=score.read_bytes();score.write_text(score.read_text().replace('Game-owned score','Changed owned score'));host,stream,url,page=begin(browser,4)
  try:
   expect(page.locator('#yogi-text')).to_be_visible();state=public_state(url);item=next(item for item in state['yogi']['items'] if item['kind']=='semantic');assert item['availability']=='stale';assert item['metadata']==next(item for item in golden['package']['items'] if item['kind']=='semantic')['metadata'];expand(page,'ey');expect(page.locator('[data-availability="stale"]')).to_be_visible();page.screenshot(path=str(root/'actual-stale-reference.png'))
  finally:page.close();stop(host,stream);score.write_bytes(original_score)
  original_manifest=manifest.read_bytes();manifest.write_text(manifest.read_text().replace('element Score object "Score.celem";',''));host,stream,url,page=begin(browser,5)
  try:
   expect(page.locator('#yogi-text')).to_be_visible();state=public_state(url);assert next(item for item in state['yogi']['items'] if item['kind']=='semantic')['availability']=='deleted';expand(page,'ey');expect(page.locator('[data-availability="deleted"]')).to_be_visible();page.screenshot(path=str(root/'actual-deleted-reference.png'))
  finally:page.close();stop(host,stream);manifest.write_bytes(original_manifest)
  bad=[]
  for key,value in [('project','foreign-project'),('owner','other-owner'),('manifest',str(root/'foreign.cpack')),('schema',2)]:
   doc=copy.deepcopy(golden);doc[key]=value;bad.append((key,json.dumps(doc)))
  doc=copy.deepcopy(golden);doc['package']['recipient']='unsupported';bad.append(('unknown-field',json.dumps(doc)))
  doc=copy.deepcopy(golden);doc['package']['items'].append(copy.deepcopy(doc['package']['items'][0]));bad.append(('duplicate-item',json.dumps(doc)))
  doc=copy.deepcopy(golden);doc['package']['items']=[dict(copy.deepcopy(doc['package']['items'][0]),item=uuid.uuid4().hex) for _ in range(33)];bad.append(('capacity',json.dumps(doc)))
  doc=copy.deepcopy(golden);next(item for item in doc['package']['items'] if item['kind']=='image')['capture']['hash']='0'*64;bad.append(('image-hash',json.dumps(doc)))
  bad.append(('duplicate-property',json.dumps(golden).replace('"schema": 1','"schema": 1, "schema": 1',1)))
  bad.append(('byte-bound',json.dumps(golden)+' '*(5242881)))
  for n,(name,text) in enumerate(bad,6):
   store().write_text(text);before_bad=store().read_bytes();host,stream,url,page=begin(browser,n)
   try:
    expect(page.locator('.yogi-clipboard')).to_contain_text('저장 자료를 열지 못했습니다');state=public_state(url);assert state['yogi'] is None and state['yogiError']=='yogi_storage_or_scope_error';assert store().read_bytes()==before_bad,name;assert not state['workers'] and state['aiState']=='idle';page.screenshot(path=str(root/('rejected-'+name+'.png')))
   finally:page.close();stop(host,stream)
  store().write_bytes(golden_bytes);outside=root/'foreign-storage.json';outside.write_bytes(golden_bytes);file=store();file.unlink();file.symlink_to(outside);host,stream,url,page=begin(browser,20)
  try:
   expect(page.locator('.yogi-clipboard')).to_contain_text('저장 자료를 열지 못했습니다');assert file.is_symlink() and outside.read_bytes()==golden_bytes;assert public_state(url)['yogi'] is None
  finally:page.close();stop(host,stream);file.unlink();file.write_bytes(golden_bytes)
  assert not errors,errors;assert all((project/name).read_bytes()==data for name,data in before.items())
 finally:browser.close()
print('PASS ordinary ProjectPack durable Yogi actual content, scope validation, references and no replay '+str(root))
