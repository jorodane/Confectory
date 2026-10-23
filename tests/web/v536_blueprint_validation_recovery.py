"""Actual per-view process/control fixture. No account, grant, paid inference or user project."""
import json,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());root=pathlib.Path(sys.argv[3]).resolve();assert root.parent==pathlib.Path('/tmp') and root.name.startswith('confectory-feature-serial-engine-')
project=root/'owned project';projects=[project/'project.cproj']
before={str(p):p.read_bytes() for m in projects for p in m.parent.rglob('*') if p.is_file()};env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(root/'profile'),CONFECTORY_ENTRY_STORAGE=str(root/'profile'),CONFECTORY_MCP_DIRECTORY=str(root/'instances'),CONFECTORY_WEB_PROJECT=str(projects[0]));env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];host=None;stream=None;checks=[]
def checked(message):
 checks.append(message);(root/'checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2));print('PASS '+message,flush=True)
def stop():
 global host,stream
 if host and host.poll() is None:os.killpg(host.pid,signal.SIGTERM);host.wait(timeout=15)
 if stream:stream.close()
def start(n):
 global host,stream,origin,token,url
 log=root/f'host-{n}.log';stream=log.open('w');host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
 for _ in range(600):
  urls=[v.split(' ',1)[1] for v in log.read_text().splitlines() if v.startswith('CONFECTORY_WEB_UI ')]
  if urls:url=urls[-1];origin,token=url.split('/#');return
  assert host.poll() is None,log.read_text()[-2000:];time.sleep(.05)
 raise AssertionError('startup deadline')
def raw(body):return json.load(urllib.request.urlopen(urllib.request.Request(origin+'/api/request',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':token}),timeout=30))
def mount():
 for _ in range(500):
  v=raw({'op':'mount'})
  if v.get('ok'):return v
  assert v.get('error',{}).get('code')=='busy',v;time.sleep(.02)
 raise AssertionError('mount busy')
def state():
 v=mount()
 try:return v['state']
 finally:raw({'op':'dispose','view':v['view']})
def call(endpoint,body,ok=True):
 for attempt in range(4):
  v=mount();rid=uuid.uuid4().hex
  try:
   assert raw({'op':'invoke','view':v['view'],'scope':v['scope'],'expectedRevision':v['revision'],'requestId':rid,'endpoint':endpoint,'input':body})['ok']
   for _ in range(18000):
    u=raw({'op':'update','view':v['view'],'scope':v['scope']});rows=[r for r in u.get('results',[]) if r['requestId']==rid]
    if rows:break
    if u.get('error',{}).get('code')=='scope_changed':
     assert endpoint in ['openProject','leaveProject','closeProject'],(endpoint,u)
     return {'scopeChanged':True}
    time.sleep(.01)
   assert rows,(endpoint,u)
   r=rows[0]
   if r.get('error',{}).get('code')=='stale_revision':continue # refused before execution only
   assert bool(r.get('ok'))==ok,(endpoint,r)
   return r.get('result') if ok else r
  finally:raw({'op':'dispose','view':v['view']})
 raise AssertionError('admission changed')
def run(operation,row=None,ok=True,**values):return call('runWindow',{'operation':operation,**({'view':row['view'],'lease':row['lease'],'handle':row.get('handle','')} if row else {}),**values},ok)
def wait(row,condition,timeout=180):
 end=time.monotonic()+timeout
 while time.monotonic()<end:
  s=run('read',row)
  if condition(s):return s
  time.sleep(.05)
 raise AssertionError(s)
def start_run(row):return run('start',row,target='portable',command=uuid.uuid4().hex)
def connected(row):return wait(row,lambda s:s['state']=='running' and s['control'].get('connected') and int(s['control']['frame'])>1)
def control(row,action,ok=True):
 c=row['control'];return run('control',row,ok,action=action,**{k:str(c[k]) for k in ['runtime','ack','sequence']})
errors=[];traffic=[];external=[];graph_id='Owned.Elements::SerialBlueprintBody/body:common'
try:
 start(90)
 with sync_playwright() as p:
  from playwright.sync_api import expect
  expect.set_options(timeout=30000)
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page(viewport={'width':1440,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)))
  def observe(response):
   try:
    body=response.request.post_data_json
    if isinstance(body,dict) and body.get('op')=='invoke':traffic.append(body)
   except Exception:pass
  page.on('response',observe);page.route('**/*',lambda r:r.continue_() if r.request.url.startswith(origin+'/') else (external.append(r.request.url),r.abort()));goto_editor(page,url);author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-signature-id]')).to_have_count(6);expect(author.locator('.bp-status')).to_have_text('미저장 초안');expect(page.locator('.brand')).to_be_enabled();author.locator(':scope > .window-title .caption').click(position={'x':6,'y':10});pending=state()['presentation']['inputs']['blueprint'];assert len(pending)==1 and pending[0][1]['text']=='{"input":"seed"}';author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_have_text('저장됨',timeout=60000);saved=call('blueprint',{'action':'read','id':graph_id});assert saved['nodes'][0]['arguments'][1]['valueJson']=='{"input":"seed"}';assert all(pathlib.Path(k).read_bytes()==v for k,v in before.items() if '.confectory' not in pathlib.Path(k).parts and '.build' not in pathlib.Path(k).parts);checked('원본 헤더로 복원 창을 전면에 둔 뒤 실제 cold 미저장 핀 Save가 정확한 소유 증거로 성공하고 최종 소스는 보존된다')
  author.locator('[data-bp-complete]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=60000)
  if review.locator('[data-additional-changes]').count():
   review.locator('[data-review-advanced]').click();ack=review.locator('[data-advanced-reviewed]')
   if ack.count():ack.check()
  expect(review.locator('#confirm')).to_be_enabled();review.locator('#confirm').click();expect(review).to_have_count(0,timeout=60000);assert all(pathlib.Path(k).read_bytes()==v for k,v in before.items() if pathlib.Path(k).name!='project.cproj' and '.confectory' not in pathlib.Path(k).parts and '.build' not in pathlib.Path(k).parts);confirmed={str(f):f.read_bytes() for f in project.rglob('*') if f.is_file() and '.confectory' not in f.parts and '.build' not in f.parts};assert len(confirmed)>len([k for k in before if '.confectory' not in pathlib.Path(k).parts and '.build' not in pathlib.Path(k).parts]);checked('실제 그룹 Review와 명시적 compiler Confirm은 기존 원본을 유지하고 새 소유 생성 파일/등록만 반영하며 실행하지 않는다')
  author.locator(':scope > .window-title .caption').click(position={'x':6,'y':10});author.locator('[data-bp-overview]').focus();page.keyboard.press('Home');author.locator('.bp-pin-plug[data-node=body][data-side=in][data-port="field:seed"] input').click();page.get_by_role('dialog',name='핀 값 선택').get_by_role('button',name='입력 · seed',exact=True).click();fresh=call('blueprint',{'action':'read','id':graph_id});call('blueprint',{'action':'intent','id':graph_id,'basis':fresh['basis'],'node':'body','text':'newer owned shared intent'});author.locator('[data-bp-save]').click();expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=60000);page.evaluate('()=>confectoryFlushPresentation()');after=call('blueprint',{'action':'read','id':graph_id});assert after['nodes'][0]['arguments'][0]['valueJson']=='{"input":"other"}' and after['nodes'][0]['intent']=='newer owned shared intent';pending=state()['presentation']['inputs']['blueprint'];assert len(pending)==1 and pending[0][1]['text']=='{"input":"seed"}';assert all(pathlib.Path(k).read_bytes()==v for k,v in confirmed.items());expect(author.locator('.bp-status')).not_to_have_text('저장됨');checked('실제 다른 편집의 최신 intent는 오래된 핀 Save를 차단하고 새 공유값/개인 입력/확정 소스를 모두 보존한다')
  assert not errors and not external,(errors,external);page.screenshot(path=str(root/'validation-recovered.png'));print(json.dumps({'root':str(root),'checks':checks,'errors':errors,'external':external,'actualEngine':True,'nativeWindows':False},ensure_ascii=False),flush=True);page.close();browser.close()
except Exception:
 print('FAILURE '+str(root)+' '+json.dumps({'errors':errors},ensure_ascii=False),flush=True);raise
finally:stop()
