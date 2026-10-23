"""원본 자유 입력 정의/중첩 실수 승격을 격리 실제 엔진에서 검사한다.
입력 ABI와 별칭 타입을 유지하며 Save/Cancel/cold/Confirm; 계정/추론 없음.
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

def sdk(op,**data):
 p=subprocess.run([env['CONFECTORY_DOTNET'],str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps({'operation':op,**data}),text=True,capture_output=True,check=True,env=env);v=json.loads(p.stdout);assert v['ok'],v;return v['result']
feature_file=project/'elements/Serial.celem';impl_file=project/'elements/SerialBlueprintBody.celem';graphfile=next((project/'blueprints').glob('*.graph.json'));nodepath='nodes/promotion-body.node.json';created=sdk('blueprintPrepareFeature',id=id,text='function '+id+' (long seed,int narrow,double ratio,float quick) -> long {}',implementation='Owned.Elements::SerialBlueprintBody',graphPath=str(graphfile.relative_to(project)),nodePath=nodepath);g=created['graph'];producer={'id':'integer','kind':'code','control':'next','intent':'정수 저장소','displayName':'정수 값','signature':{'args':[],'return':'long'},'arguments':{},'implementation':'nodes/promotion-integer.node.json'};g['nodes'].insert(0,producer);g['entry']='integer';g['edges']=[{'from':'integer','port':'next','to':'body'},{'from':'body','port':'next','to':'exit:return'}];g['exits']={'return':{'node':'body'}};synthetic=len(sys.argv)>4 and sys.argv[4]=='synthetic';outputnode='$exit:return' if synthetic else 'give';
if not synthetic:
 g['profile']='sync-acyclic-implicit-v1';g['nodes'].append({'id':'give','kind':'export','control':'next','intent':'원본 내보내기','output':'return','signature':{'args':[{'name':'value','type':'long'}],'return':'void'},'arguments':{'value':{'input':'seed'}}});g['edges']=[{'from':'integer','port':'next','to':'body'},{'from':'body','port':'next','to':'give'},{'from':'give','port':'next','to':'exit:return'}];g['exits']={'return':None}
defs=sdk('featureBlueprintNodes',featureSource=created['function'],graph=g);assert defs.get('state')=='node-definitions',defs;feature_file.write_text(created['function']);impl_file.write_text(created['implementation']);graphfile.write_text(json.dumps(g))
for n in [n for n in g['nodes'] if n['kind']=='code']:
 definition=next(row for row in defs['nodes'] if row['id']==n['id']);file=graphfile.parent/n['implementation'];file.parent.mkdir(parents=True,exist_ok=True);file.write_text(json.dumps({'schema':1,'node':n['id'],'definitionHash':definition['definitionHash'],'source':'return 9007199254740992L;' if n['id']=='integer' else 'return seed;'}))
original_feature=feature_file.read_bytes();original_impl=impl_file.read_bytes();original_graph=graphfile.read_bytes();signatures={n['id']:n['signature'] for n in g['nodes']}

# A second valid owned C# implementation fixes the shared external function contract.
(project/'elements/OtherExportBody.celem').write_text('implementation Owned.Elements::OtherExportBody for '+id+' (long seed,int narrow,double ratio,float quick) -> long {body common "OtherExportBody.csbody";}');(project/'elements/OtherExportBody.csbody').write_text('return seed;');manifest=project/'project.cproj';text=manifest.read_text();at=text.rindex('}');manifest.write_text(text[:at]+'element OtherExportBody implementation "elements/OtherExportBody.celem";\n'+text[at:]);physical={str(p):p.read_bytes() for p in project.rglob('*') if p.is_file()}
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(0);page=setup();graphid=invoke('blueprint',{'action':'list','feature':id})['result']['result']['rows'][0]['id'];old=invoke('blueprint',{'action':'read','id':graphid})['result']['result'];proof=json.dumps(sorted([[s['id'],s['revision'],s['hash']] for s in old['sources']]),separators=(',',':'));checkpoints={str(p):p.read_bytes() for p in project.glob('.confectory/edit-workspaces/*/draft.json')};plan={'node':'give','name':'return','type':'double','path':[],'baseJson':'{"input":"seed"}','sourceJson':'{"input":"ratio"}'};invoke('blueprint',{'action':'authorBatch','id':graphid,'attempt':uuid.uuid4().hex,'sourceProof':proof,'checkpointHash':old['checkpointHash'],'edits':[{'action':'adaptOutput','node':'give','definition':plan}]},False);new=invoke('blueprint',{'action':'read','id':graphid})['result']['result'];assert old['sources']==new['sources'] and old['signature']==new['signature'] and all(pathlib.Path(k).read_bytes()==v for k,v in physical.items()) and {str(p):p.read_bytes() for p in project.glob('.confectory/edit-workspaces/*/draft.json')}==checkpoints;checked('다른 소유 구현이 공유하는 외부 출력 계약은 자동 변경하지 않고 모든 소스·저장본을 보존해 거부한다');page.close();browser.close();assert not errors and not external,(errors,external)
finally:stop()
record={'checks':checks,'errors':errors,'external':external,'actualEngine':True,'nativeWindows':False,'accountOrInference':False,'projectRun':False,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False,indent=2))
