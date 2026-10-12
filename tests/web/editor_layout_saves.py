import json,os,pathlib,subprocess,tempfile,time,shutil,sys,signal,urllib.request,hashlib
from playwright.sync_api import sync_playwright,expect
expect.set_options(timeout=30000)
repo=pathlib.Path(sys.argv[1]).resolve();report=json.load(open(sys.argv[2]));root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-layout-measure-'))
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
 mounted=send({'op':'mount'});assert mounted['ok'],mounted
 try:return mounted['state']
 finally:assert send({'op':'dispose','view':mounted['view']})['ok']
import ctypes,struct
lib=ctypes.CDLL('libc.so.6',use_errno=True);lib.inotify_init1.argtypes=[ctypes.c_int];lib.inotify_add_watch.argtypes=[ctypes.c_int,ctypes.c_char_p,ctypes.c_uint32];fd=lib.inotify_init1(os.O_NONBLOCK|os.O_CLOEXEC);assert fd>=0
writes=[];calls=[];call_times=[];results={}
def drain():
 while True:
  try:data=os.read(fd,65536)
  except BlockingIOError:break
  offset=0
  while offset<len(data):
   wd,mask,cookie,length=struct.unpack_from('iIII',data,offset);name=data[offset+16:offset+16+length].split(b'\0',1)[0].decode();offset+=16+length
   if mask&0x80 and name.endswith('.json'):writes.append(name)
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);host,stream,url=start(0);page=browser.new_page(viewport={'width':1440,'height':1000});page.goto(url);page.locator('.work-body').wait_for();page.wait_for_timeout(1200)
 folder=root/'storage/presentations';folder.mkdir(parents=True,exist_ok=True);assert lib.inotify_add_watch(fd,str(folder).encode(),0x80|0x08)>=0
 def req(request):
  if request.url.endswith('api/request'):
   try:
    body=request.post_data_json
    if body.get('op')=='invoke' and body.get('endpoint')=='savePresentation':calls.append(body);call_times.append(time.monotonic())
   except Exception:pass
 page.on('request',req);page.evaluate("()=>{globalThis.layoutNotices=[];const target=document.querySelector('#workspace-save-state');new MutationObserver(()=>layoutNotices.push(target.textContent)).observe(target,{childList:true,subtree:true,characterData:true});}")
 def phase(name,action,wait=1600):

  if len(sys.argv)>3 and sys.argv[3]=='after':page.evaluate('()=>globalThis.confectoryFlushPresentation()');page.wait_for_timeout(100)
  drain();a=len(calls);b=len(writes);baseline=saved();page.evaluate('()=>layoutNotices.length=0');began=time.monotonic();action();duration=time.monotonic()-began;page.wait_for_timeout(wait);drain()
  def input_hash(row):return hashlib.sha256(json.dumps(row.get('inputs'),sort_keys=True).encode()).hexdigest()[:12]
  requests=[{'afterStartSeconds':round(stamp-began,3),'inputHash':input_hash(body['input']['presentation']),'camera':body['input']['presentation'].get('workspaceView')} for body,stamp in zip(calls[a:],call_times[a:])]
  results[name]={'actionSeconds':duration,'baselineInputHash':input_hash(baseline),'requests':len(calls)-a,'requestDetails':requests,'actualFileReplacements':len(writes)-b,'statusTransitions':page.evaluate('()=>layoutNotices.slice()')}
 try:
  phase('idle_poll',lambda:None,2500)
  def menus():
   for _ in range(5):page.locator('#workspace').click(button='right',position={'x':1100,'y':400});page.keyboard.press('Escape');page.wait_for_timeout(350)
  phase('right_click_menus',menus)
  phase('same_origin_repeat',lambda:[(page.locator('#workspace-home-tab').click(),page.wait_for_timeout(350)) for _ in range(5)])
  def pan():
   page.mouse.move(1100,350);page.mouse.down(button='middle')
   for i in range(8):page.mouse.move(1100+i*4,350+i*3);page.wait_for_timeout(100)
   page.mouse.up(button='middle')
  phase('pan',pan)
  phase('zoom_burst_300ms',lambda:[(page.mouse.move(1100,350),page.mouse.wheel(0,-20),page.wait_for_timeout(300)) for _ in range(8)])
  if len(sys.argv)>3 and sys.argv[3]=='after':phase('slow_zoom_550ms',lambda:[(page.mouse.move(1100,350),page.mouse.wheel(0,20),page.wait_for_timeout(550)) for _ in range(8)])
  page.locator('#nav').click();page.locator('.nav-menu button').filter(has_text='개념').first.click();expect(page.locator('#nav')).to_be_enabled();page.locator('#nav').click();page.wait_for_timeout(1400)
  phase('selection_focus',lambda:[(page.locator('.window[data-key="browser"] .window-title').click(),page.wait_for_timeout(300)) for _ in range(5)])
  def window_drag():
   box=page.locator('.window[data-key="browser"]').bounding_box();page.mouse.move(box['x']+170,box['y']+16);page.mouse.down()
   for i in range(8):page.mouse.move(box['x']+170+i*3,box['y']+16+i*2);page.wait_for_timeout(100)
   page.mouse.up()
  phase('window_move',window_drag)
  page.locator('#workspace').click(button='right',position={'x':1050,'y':450});page.get_by_role('button',name='메모 만들기',exact=True).click();page.wait_for_timeout(1400);note=page.locator('.workspace-note textarea').last
  phase('continuous_input_300ms',lambda:[(note.type(ch),page.wait_for_timeout(300)) for ch in 'abcdefghi'])
  # Re-send exactly the already persisted presentation through the normal API.
  token=url.split('#',1)[1];address=url.split('#',1)[0]+'api/request'
  def send(body):
   request=urllib.request.Request(address,data=json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':token})
   with urllib.request.urlopen(request,timeout=30) as response:return json.load(response)
  def identical():
   view=send({'op':'mount'});assert view['ok'],view;rid='identical-'+str(time.time_ns());envelope={'view':view['view'],'scope':view['scope']};request=dict(envelope,op='invoke',endpoint='savePresentation',input={'presentation':saved()},expectedRevision=view['revision'],requestId=rid);calls.append(request);assert send(request)['ok']
   call_times.append(time.monotonic())
   try:
    for _ in range(400):
     reply=send(dict(envelope,op='update'));assert reply['ok'];row=next((row for row in reply['results'] if row['requestId']==rid),None)
     if row:assert row['ok'],row;return
     time.sleep(.01)
    raise AssertionError('identical save pending')
   finally:assert send(dict(envelope,op='dispose'))['ok']
  phase('identical_snapshot',identical)
  if len(sys.argv)>3 and sys.argv[3]=='after':
   assert results['right_click_menus']['actualFileReplacements']==0,results
   assert results['same_origin_repeat']['actualFileReplacements']==0,results
   assert results['idle_poll']['actualFileReplacements']==0,results
   assert results['identical_snapshot']['actualFileReplacements']==0,results
   assert results['zoom_burst_300ms']['actualFileReplacements']<=1,results
   assert results['slow_zoom_550ms']['actualFileReplacements']<=1,results
   assert results['continuous_input_300ms']['actualFileReplacements']<=__import__('math').ceil(results['continuous_input_300ms']['actionSeconds']/2)+1 and results['continuous_input_300ms']['actualFileReplacements']<9,results
   assert all(not any('저장됨' in text or '저장 중' in text for text in value['statusTransitions']) for value in results.values()),results
   # A camera burst becomes one periodic checkpoint, followed by no writes in an unchanged period.
   page.evaluate('()=>globalThis.confectoryFlushPresentation()');page.wait_for_timeout(100);drain();a=len(writes)
   pan();page.wait_for_timeout(16000);drain();assert len(writes)-a==1,(len(writes)-a,results)
   a=len(writes);page.wait_for_timeout(16000);drain();assert len(writes)==a,'unchanged period wrote'
   # Project exit flushes a fresh camera state without waiting for its period.
   pan();page.locator('.brand').click();expect(page.locator('.home-grid')).to_be_visible();snapshot=saved();assert snapshot['workspaceView']['x']!=0;page.locator('[data-enter]').first.click();page.locator('.work-body').wait_for()
   page.evaluate('()=>globalThis.confectoryFlushPresentation()');
   # Real save failure remains visible; no ignored success or swallowed exit flush.
   file=next(folder.glob('*.json'));file.chmod(0o400)
   try:
    pan();outcome=page.evaluate("async()=>{try{await confectoryFlushPresentation();return 'unexpected success'}catch(e){return e.message}}");assert outcome=='consumer_error',outcome;expect(page.locator('#workspace-save-state')).to_have_text('배치 저장 실패')
   finally:file.chmod(0o600)
   page.evaluate('()=>globalThis.confectoryFlushPresentation()');expect(page.locator('#workspace-save-state')).to_have_text('')

  (root/'measurement.json').write_text(json.dumps({'profile':sys.argv[3] if len(sys.argv)>3 else 'before','platform':'Linux ordinary EditorHome/Chromium; does not measure user Windows','phases':results},ensure_ascii=False,indent=2));print(json.dumps(results,ensure_ascii=False));print('EVIDENCE '+str(root));print('PASS ordinary ProjectPack actual periodic layout checkpoint and visible failure')
 finally:page.close();stop(host,stream);browser.close();os.close(fd)
