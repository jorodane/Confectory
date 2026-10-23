"""Actual per-view process/control fixture. No account, grant, paid inference or user project."""
import json,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-run-read-error-'))
projects=[]
for name in ['first','second']:
 p=root/name;shutil.copytree(repo/'examples/frame-loop',p,ignore=shutil.ignore_patterns('.confectory','.build'));m=p/'project.cpack';m.write_text(m.read_text().replace('../../',str(repo)+'/'));projects.append(m)
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
errors=[];page=None
try:
 start(0)
 with sync_playwright() as p:
  from playwright.sync_api import expect
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.route('**/*',lambda r:r.continue_() if r.request.url.startswith(origin+'/') else r.abort());goto_editor(page,url);page.locator('#run').click();w=page.locator('.run-window:visible');expect(w.locator('[data-run-play]')).to_be_enabled();w.locator('[data-run-play]').click();expect(w.locator('.caption strong')).to_have_text('실행 중',timeout=180000);expect(w.locator('[data-run-pause]')).to_be_enabled()
  page.evaluate("""()=>{const base=fetch,ids=new Set();let hold=true;globalThis.fetch=async(...args)=>{let env;try{env=JSON.parse(args[1]?.body||'{}')}catch{}if(hold&&env?.op==='invoke'&&env.endpoint==='runWindow'&&env.input?.operation==='read')ids.add(env.requestId);const response=await base(...args);if(hold&&env?.op==='update'){const data=await response.clone().json();const rows=data.results?.filter(r=>ids.has(r.requestId))||[];if(rows.length){globalThis.__readHeld=true;await new Promise(resolve=>globalThis.__releaseReadError=resolve);hold=false;for(const row of rows){row.ok=false;row.error={code:'consumer_error'};delete row.result;}return new Response(JSON.stringify(data),{status:200,headers:{'Content-Type':'application/json'}});}}return response;};}""")
  page.wait_for_function('()=>globalThis.__readHeld===true');page.locator('#chat-input').fill('읽기 오류 뒤에도 유지할 입력');page.locator('#title').click();page.get_by_role('button',name='프로젝트 정보',exact=True).click();page.evaluate('()=>__releaseReadError()');expect(page.locator('[data-project-information]')).to_be_visible(timeout=60000);expect(page.locator('#chat-input')).to_have_value('읽기 오류 뒤에도 유지할 입력');assert w.locator('[data-run-retry]').is_visible();assert not errors,errors;checked('실행 상태 읽기 실패는 해당 실행창에 남기고 대기 중인 별도 프로젝트 정보 동작·새 입력을 취소하지 않는다');print(json.dumps({'root':str(root),'checks':checks,'errors':errors,'actualEngine':True,'nativeWindows':False},ensure_ascii=False),flush=True);page.close();browser.close()
except Exception:
 print('FAILURE '+str(root)+' '+json.dumps(errors),flush=True)
 if page:
  try:page.evaluate('()=>globalThis.__releaseReadError?.()')
  except Exception:pass
 raise
finally:stop()
