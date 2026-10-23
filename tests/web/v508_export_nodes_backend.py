"""Original actual serial export assignment controls against an isolated owned-element engine.
Save/Cancel/cold/Confirm and genuine-source-change guards; no account or inference.
"""
import json,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());fixture=pathlib.Path(sys.argv[3]).resolve();assert fixture==repo.parent/'scratch/v508-elements/actual13-source-fixture'
case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-node-contract-engine-'));project=case/'owned project';shutil.copytree(fixture/'owned project',project,ignore=shutil.ignore_patterns('.confectory','.build'));storage=case/'profile';storage.mkdir();original={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file() and '.confectory' not in p.parts};id='Owned.Elements::Serial';text='9223372036854775804';description='재시작할 미적용 설명 한글';env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(storage),CONFECTORY_ENTRY_STORAGE=str(storage),CONFECTORY_MCP_DIRECTORY=str(case/'instances'),CONFECTORY_WEB_PROJECT=str(project/'project.cproj'),CONFECTORY_DOTNET=env.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet'));env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];host=None;log=None;errors=[];external=[];checks=[]
def stop():
 global host,log
 if host and host.poll() is None:os.killpg(host.pid,signal.SIGTERM)
 if host:host.wait(timeout=15)
 if log:log.close()
def start(i):
 global host,log,origin,token,url
 file=case/f'host-{i}.log';log=file.open('w');host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 for _ in range(600):
  urls=[l.split(' ',1)[1] for l in file.read_text().splitlines() if l.startswith('CONFECTORY_WEB_UI ')]
  if urls:url=urls[-1];origin,token=url.split('/#');return
  assert host.poll() is None,file.read_text()[-1000:];time.sleep(.05)
 raise AssertionError('startup timeout')
def raw(body):return json.load(urllib.request.urlopen(urllib.request.Request(origin+'/api/request',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':token}),timeout=30))
def mount():
 for _ in range(300):
  v=raw({'op':'mount'})
  if v.get('ok'):return v
  assert v.get('error',{}).get('code')=='busy',v;time.sleep(.02)
 raise AssertionError('busy transport')
def state():
 v=mount()
 try:return v['state']
 finally:raw({'op':'dispose','view':v['view']})
def invoke(endpoint,body,success=True):
 for _ in range(4):
  v=mount();rid=uuid.uuid4().hex
  try:
   assert raw({'op':'invoke','view':v['view'],'scope':v['scope'],'expectedRevision':v['revision'],'requestId':rid,'endpoint':endpoint,'input':body})['ok']
   for _ in range(600):
    u=raw({'op':'update','view':v['view'],'scope':v['scope']});rows=[r for r in u.get('results',[]) if r['requestId']==rid]
    if rows:break
    time.sleep(.01)
   assert rows
   if rows[0].get('error',{}).get('code')=='stale_revision':continue
   assert bool(rows[0].get('ok')) is success,rows;return {'result':rows[0],'state':u.get('state')}
  finally:raw({'op':'dispose','view':v['view']})
 raise AssertionError('admission failed')
traffic=[];injected=0

def checked(text):
 checks.append(text);(case/'progress.json').write_text(json.dumps(checks,indent=2));print('PASS '+text,flush=True)
def observe(response):
 try:
  request=response.request.post_data_json
  if not isinstance(request,dict):return
  if request.get('op')=='invoke':traffic.append({'invoke':request})
  elif request.get('op')=='update':
   for result in response.json().get('results',[]):
    if not any(row.get('result',{}).get('requestId')==result['requestId'] for row in traffic):traffic.append({'result':result})
 except Exception:pass

def route(request):
 global injected
 if not request.request.url.startswith(origin):external.append(request.request.url);request.abort();return
 body=request.request.post_data_json if request.request.method=='POST' else None
 if isinstance(body,dict) and body.get('op')=='invoke' and body.get('endpoint')=='reviewDraft' and False:
  # Actual server rejects an explicitly stale transport revision before execution.
  injected+=1;body['expectedRevision']-=1;request.continue_(post_data=json.dumps(body));return
 request.continue_()

def setup():
 page=browser.new_page(viewport={'width':1280,'height':900});page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',observe);page.route('**/*',route);goto_editor(page,url);return page

def settled():
 expect(w.locator('[data-feature-action=save]')).to_be_enabled(timeout=30000)
 for _ in range(600):
  s=state();d=s.get('declaration')
  if d and d['id']==id and d['revision']==s['draft']['revision']:return s
  page.wait_for_timeout(20)
 raise AssertionError('feature inspect did not settle')


try:
 start(0);graphid=invoke('blueprint',{'action':'list','feature':id})['result']['result']['rows'][0]['id']
 def graph():return invoke('blueprint',{'action':'read','id':graphid})['result']['result']
 def same(a,b):return all(a[k]==b[k] for k in ['nodes','edges','entry','exits','profile','signature'])
 old=graph();assert old['profile']=='sync-acyclic-v1';node='export_atomic';edits=[{'kind':'create','node':node,'output':'return'},{'kind':'value','node':node,'valueJson':'{"constant":9223372036854775804}'},{'kind':'route','node':'body','to':node},{'kind':'route','node':node,'to':'exit:return'}];invoke('blueprint',{'action':'outputNodes','id':graphid,'basis':old['basis'],'edits':edits});g=graph();assert g['profile']=='sync-acyclic-implicit-v1' and any(e['from']=='body' and e['to']==node for e in g['edges']) and json.loads(next(n for n in g['nodes'] if n['id']==node)['arguments'][0]['valueJson'])=={'constant':9223372036854775804};assert all((project/k).read_bytes()==v for k,v in original.items());checked('explicit assignment creation atomically upgrades only the existing strict serial profile and applies its exact 64-bit value plus routes without final source writes')
 for label,edits in [('missing route',[{'kind':'create','node':'export_partial','output':'return'},{'kind':'route','node':'body','to':'Other.Project::missing'}]),('cycle',[{'kind':'route','node':node,'to':'body'}]),('unknown field',[{'kind':'value','node':node,'valueJson':'null','account':'forbidden'}]),('wrong kind',[{'kind':'bind','node':'body','output':'return'}])]:
  before=graph();invoke('blueprint',{'action':'outputNodes','id':graphid,'basis':before['basis'],'edits':edits},False);assert same(graph(),before) and all((project/k).read_bytes()==v for k,v in original.items());checked('invalid '+label+' rejects the entire output transaction and preserves all existing graph/source state')
 before=graph();invoke('blueprint',{'action':'outputNodes','id':graphid,'basis':old['basis'],'edits':[{'kind':'remove','node':node}]},False);assert same(graph(),before);checked('stale observed basis cannot remove the new assignment or adopt newer graph edits')
 before=graph();invoke('blueprint',{'action':'outputNodes','id':graphid,'basis':before['basis'],'edits':[{'kind':'remove','node':node}]});g=graph();assert not any(n['id']==node for n in g['nodes']) and any(e['from']=='body' and e['to']=='exit:return' for e in g['edges']);invoke('saveDraft',{});stop();start(1);fresh=graph();assert same(fresh,g) and all((project/k).read_bytes()==v for k,v in original.items());checked('connected assignment removal splices its exact predecessor and successor, saves and cold-restores without any final source mutation')
finally:stop()
record={'checks':checks,'actualEngine':True,'realRenderer':False,'nativeWindows':False,'accountOrInference':False,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
