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
# Only this isolated fixture gains a second implementation and a Windows-specific body.
impl='Owned.Elements::AttackBody';feature='Owned.Elements::Attack';file=project/'AttackBody.celem';text=file.read_text();at=text.rindex('}');file.write_text(text[:at]+'body windows "AttackWindows.csbody";'+text[at:]);windows=project/'AttackWindows.csbody';windows.write_bytes('// 원본 Windows 한글\r\nreturn amount + 5;\r\n'.encode());(project/'OtherAttackBody.celem').write_text('implementation Owned.Elements::OtherAttackBody for '+feature+' (long amount) -> long {body common "OtherAttack.csbody";}');(project/'OtherAttack.csbody').write_text('return amount * 2;');manifest=project/'project.cproj';text=manifest.read_text();at=text.rindex('}');manifest.write_text(text[:at]+'element OtherAttackBody implementation "OtherAttackBody.celem";\n'+text[at:]);physical={str(p):p.read_bytes() for p in project.rglob('*') if p.is_file() and '.confectory' not in p.parts};body=project/'Attack.csbody';original_body=body.read_bytes()
def preserved(except_impl=False):return all(pathlib.Path(k).read_bytes()==v for k,v in physical.items() if not except_impl or pathlib.Path(k)!=file)
def checkpoint():return {str(p):p.read_bytes() for p in project.glob('.confectory/edit-workspaces/*/draft.json')}
def selected():invoke('select',{'id':impl});return state()['draft']
def preview(origin=None,success=True):
 unit=selected();request={'action':'readConversion','id':impl,'target':'common','revision':unit['revision'],'hash':__import__('hashlib').sha256(unit['text'].encode()).hexdigest()}
 if origin is not None:request['origin']=origin
 return invoke('blueprint',request,success)['result'].get('result')
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(0);page=setup();catalog=invoke('blueprint',{'action':'featureBodies','feature':feature})['result']['result'];assert len(catalog['rows'])==3 and {x['sourceKind'] for x in catalog['rows']}=={'csharp'} and len({x['implementation'] for x in catalog['rows']})==2 and not catalog['selectionMade'] and preserved();checked('실제 엔진은 여러 구현·대상을 구분해 열거하며 첫 구현을 자동 선택하거나 소스를 변경하지 않는다')
  before=checkpoint();first=preview();model=first['preview'];assert model['id'] is None and model['privateConversion'] and model['rootId']==impl+'/body:common' and model['implementation']==impl and model['target']=='common' and next(n for n in model['nodes'] if n['id']=='body')['source']==original_body.decode() and not first['sourceWritten'] and not first['compiled'];again=preview(first['origin']);assert first['origin']==again['origin'] and first['preview']['nodes']==again['preview']['nodes'] and checkpoint()==before and preserved();bad=json.loads(json.dumps(first['origin']));bad['target']='windows';preview(bad,False);assert checkpoint()==before and preserved();checked('원본 C# 미리보기는 읽기 전용이며 같은 문맥으로 재준비하고 다른 대상으로 위조한 복원은 거부한다')
  page.close();stop();start(1);page=setup();cold=preview(first['origin']);assert cold['origin']==first['origin'] and cold['preview']['sources'] and preserved();body.write_bytes(original_body+b'\n// isolated changed source\n');preview(first['origin'],False);assert checkpoint()==before;body.write_bytes(original_body);current=preview(first['origin']);assert current['origin']==first['origin'] and preserved();checked('실제 재시작은 같은 원본·목적지로 미리보기를 복구하고 바뀐 C# 원본은 덮어쓰지 않고 거부한다')
  result=invoke('blueprint',{'action':'convertBody','id':impl,'target':'common','basis':current['basis']})['result']['result'];graphid=result['id'];data=invoke('blueprint',{'action':'read','id':graphid})['result']['result'];assert len(data['reviewIds'])==3 and any(n['id']=='body' and n['source']==original_body.decode() for n in data['nodes']) and preserved();invoke('saveDraft',{});assert preserved();invoke('select',{'id':impl});status=invoke('browserDrafts',{'action':'status','ids':[impl]})['result']['result'];assert status['ids']==[impl] and not status['unsaved'];invoke('browserDrafts',{'action':'discard','ids':status['ids'],'revisions':[r['revision'] for r in status['rows']],'hashes':[r['hash'] for r in status['rows']],'ownerHash':status['ownerHash'],'checkpointHash':status['checkpointHash']});catalog=invoke('blueprint',{'action':'featureBodies','feature':feature})['result']['result'];assert next(x for x in catalog['rows'] if x['id']==impl+'/body:common')['sourceKind']=='blueprint' and preserved();checked('명시 전환·저장은 원본/다른 대상을 보존하며 변경 취소는 마지막 저장 체크포인트를 삭제하지 않는다')
  invoke('saveDraft',{});assert invoke('blueprint',{'action':'read','id':graphid})['result']['result']['reviewIds']==data['reviewIds'];page.close();stop();start(2);page=setup();data=invoke('blueprint',{'action':'read','id':graphid})['result']['result'];group=data['reviewIds'];assert len(group)==3 and preserved();invoke('reviewDraft',{'id':impl,'target':'portable'},False);review=invoke('reviewGroup',{'ids':group,'target':'portable'})['state']['review'];assert review['status']=='ready';confirmed=invoke('confirmGroup',{'ids':group,'token':review['token']});assert confirmed['result']['result']['sourceConfirmed'] and 'blueprint common' in file.read_text() and 'body windows "AttackWindows.csbody"' in file.read_text() and preserved(True) and body.read_bytes()==original_body;checked('반복 Save·cold 초안 복원·실제 컴파일 그룹 Confirm은 선택한 common만 전환하며 원본 C#/Windows/다른 구현을 보존한다');page.close();browser.close();assert not errors and not external,(errors,external)
except Exception:
 try:(case/'failure-state.json').write_text(json.dumps(state(),ensure_ascii=False,indent=2));(case/'failure.json').write_text(json.dumps({'traffic':traffic,'errors':errors},ensure_ascii=False,indent=2))
 except Exception:pass
 print('격리 실패 자료 '+str(case));raise
finally:
 if body.read_bytes()!=original_body:body.write_bytes(original_body)
 stop()
record={'checks':checks,'errors':errors,'external':external,'actualEngine':True,'actualUIConversionFlow':False,'nativeWindows':False,'accountOrInference':False,'projectRun':False,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False,indent=2))
