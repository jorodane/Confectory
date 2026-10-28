"""Owned Set target/output atomic plan, recovery and compiler boundary; isolated engine, no user account."""
import hashlib,json,os,pathlib,signal,subprocess,sys,tempfile,time,urllib.request,uuid,copy
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-set-plan-'));project=case/'owned project';project.mkdir();n='Owned.Set::';env=os.environ.copy()
items={'Main':('function','function '+n+'Main () -> int {provide '+n+'Main with '+n+'MainBody;}'),'MainBody':('implementation','implementation '+n+'MainBody for '+n+'Main () -> int {import '+n+'Calc as Calc (long) -> long;body common "Main.csbody";}'),'Calc':('function','function '+n+'Calc (long amount) -> long {provide '+n+'Calc with '+n+'CalcBody;}'),'CalcBody':('implementation','implementation '+n+'CalcBody for '+n+'Calc (long amount) -> long {blueprint common "Calc.graph.json";}')}
g={'schema':1,'profile':'sync-acyclic-locals-v1','feature':n+'Calc','contractHash':hashlib.sha256(json.dumps({'feature':n+'Calc','signature':{'args':[{'type':'long','name':'amount'}],'return':'long'}},separators=(',',':')).encode()).hexdigest(),'entry':'finish','locals':[{'id':'counter','name':'현재 값','type':'long','initial':{'constant':0}}],'nodes':[{'id':'finish','kind':'export','control':'next','intent':'결과 내보내기','output':'return','signature':{'args':[{'name':'value','type':'long'}],'return':'void'},'arguments':{'value':{'constant':0}}}],'edges':[],'exits':{}}
# Ask the pure compiler metadata to provide its canonical feature contract hash.
q=subprocess.run([env['CONFECTORY_DOTNET'],str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps({'operation':'blueprintPrepareFeature','id':n+'Calc','text':'function '+n+'Calc (long amount) -> long {}','implementation':n+'Unused','graphPath':'unused.graph.json','nodePath':'unused.node.json'}),text=True,capture_output=True,check=True);v=json.loads(q.stdout);assert v['ok'],v;g['contractHash']=v['result']['graph']['contractHash']
if 'copy-boundary' in sys.argv[3:]:g['copySource']={'implementation':n+'Origin','target':'common','bodyOrigin':n+'Origin','sourceKind':'blueprint'}
g['profile']='sync-acyclic-alias-locals-v1';g['locals'].append({'id':'readonlyAlias','name':'읽기 전용 입력 별칭','type':'long','source':{'input':'amount'}})
sources={'Calc.graph.json':json.dumps(g,ensure_ascii=False),'Main.csbody':'return checked((int)calls.Calc.Invoke(4));'}
for name,(kind,text) in items.items():sources[name+'.celem']=text
sources['project.cproj']='project Owned.Set version "1" {standalone true;entry '+n+'Main;'+''.join('element '+name+' '+kind+' "'+name+'.celem";' for name,(kind,text) in items.items())+'registry Confectory.Build.DotNet "'+str(repo/'targets/dotnet/pack.cpack')+'";dependency Confectory.Build.DotNet version "0.1.0";target portable Confectory.Build.DotNet::Portable;}'
for name,text in sources.items():(project/name).write_bytes(text.encode())
original={p.name:p.read_bytes() for p in project.iterdir()};env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(case/'profile'),CONFECTORY_ENTRY_STORAGE=str(case/'profile'),CONFECTORY_MCP_DIRECTORY=str(case/'instances'),CONFECTORY_WEB_PROJECT=str(project/'project.cproj'));env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];host=None;log=None;checks=[]
def stop():
 global host,log
 if host and host.poll() is None:os.killpg(host.pid,signal.SIGTERM);host.wait(timeout=15)
 if log:log.close()
def start(index):
 global host,log,url,origin,token
 f=case/f'host-{index}.log';log=f.open('w');host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 for _ in range(600):
  urls=[v.split(' ',1)[1] for v in f.read_text().splitlines() if v.startswith('CONFECTORY_WEB_UI ')]
  if urls:url=urls[-1];origin,token=url.split('/#');return
  assert host.poll() is None,f.read_text();time.sleep(.05)
 raise AssertionError('host startup')
def raw(body):return json.load(urllib.request.urlopen(urllib.request.Request(origin+'/api/request',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':token}),timeout=30))
def mount():
 for _ in range(1000):
  row=raw({'op':'mount'})
  if row.get('ok'):return row
  assert row.get('error',{}).get('code')=='busy',row;time.sleep(.02)
 raise AssertionError('mount admission deadline')
def state():
 v=mount()
 try:return v['state']
 finally:raw({'op':'dispose','view':v['view']})
def call(endpoint,body,ok=True):
 for _ in range(4):
  v=mount();rid=uuid.uuid4().hex
  try:
   assert raw({'op':'invoke','view':v['view'],'scope':v['scope'],'expectedRevision':v['revision'],'requestId':rid,'endpoint':endpoint,'input':body})['ok']
   for _ in range(12000):
    r=raw({'op':'update','view':v['view'],'scope':v['scope']});rows=[row for row in r.get('results',[]) if row['requestId']==rid]
    if rows:break
    time.sleep(.01)
   assert rows,(endpoint,r)
   if rows[0].get('error',{}).get('code')=='stale_revision':continue
   assert bool(rows[0].get('ok'))==ok,rows
   return rows[0].get('result') if ok else rows[0]
  finally:raw({'op':'dispose','view':v['view']})
 raise AssertionError('transport revision changed before execution')
def checked(message):checks.append(message);(case/'checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2));print('PASS '+message,flush=True)
def unchanged():assert all((project/k).read_bytes()==v for k,v in original.items())
def current():return call('blueprint',{'action':'read','id':n+'CalcBody/body:common'})
def request(data,plan):return {'id':data['id'],'attempt':uuid.uuid4().hex,'sourceProof':json.dumps(sorted([[v['id'],v['revision'],v['hash']] for v in data['sources']]),separators=(',',':')),'checkpointHash':data['checkpointHash'],'edits':[{'action':'setPlan','node':'$sets','definition':plan}]}
try:
 start(0);data=current();initial=data['sources'];plan={'locals':[{'id':'firstValue','name':'첫 저장값','type':'long','initialJson':'0'},{'id':'secondValue','name':'두 번째 저장값','type':'long','initialJson':'0'}],'nodes':[{'id':'first','local':'counter','outputLocal':'firstValue','type':'long','valueJson':'{"input":"amount"}'},{'id':'second','local':'counter','outputLocal':'secondValue','type':'long','valueJson':'{"constant":9}'}],'routes':[{'node':'first','port':'next','to':'second'},{'node':'second','port':'next','to':'finish'}],'entry':'first','bindings':[{'node':'finish','name':'value','valueJson':'{"node":"first","output":"stored"}'}]};before=copy.deepcopy(plan)
 denied=call('blueprint',{'action':'setPlan','id':data['id'],'basis':data['basis'],'definition':plan},ok=False);assert not denied['ok'] and current()['sources']==initial;unchanged();checked('외부 직접 Set plan은 거절하고 원본/초안은 바꾸지 않는다')
 if 'copy-boundary' in sys.argv[3:]:
  refused=call('blueprint',{'action':'authorBatch',**request(data,plan)},ok=False);assert not refused['ok'] and current()['sources']==initial;unchanged();checked('복사 출처가 있는 graph는 owner 문맥을 생략해도 Set 원자 후보를 거절한다');print(json.dumps({'checks':checks,'actualEngine':True,'copyBoundaryOnly':True,'evidence':str(case)},ensure_ascii=False));sys.exit(0)
 command=request(data,plan);call('blueprint',{'action':'authorBatch',**command});assert plan==before;result=current();first=next(v for v in result['nodes'] if v['id']=='first');assert first['local']=='counter' and first['outputLocal']=='firstValue' and first['outputs']==[{'name':'stored','type':'long'}] and result['diagnostics']['state'] in ['source-ready','source-assembled'];assert len(result['locals'])==len(g['locals'])+2;unchanged();checked('두 Set와 각 출력 저장소·대상·연결·내보내기 binding은 한 후보/checkpoint로 저장되고 원본 파일은 쓰지 않는다')
 settled=call('blueprint',{'action':'settledAuthorBatch',**command});assert settled['settled'];checkpoint=result['checkpointHash'];retry=call('blueprint',{'action':'authorBatch',**command});assert retry['settled'] and current()['checkpointHash']==checkpoint;unchanged();stop();start(1);cold=current();assert cold['checkpointHash']==checkpoint and call('blueprint',{'action':'settledAuthorBatch',**command})['settled'];assert len(cold['locals'])==len(g['locals'])+2 and len(cold['nodes'])==3;unchanged();checked('저장 응답을 쓰지 않은 재조회·같은 요청 재시도·실제 프로세스 재시작이 중복이나 부분 저장 없이 동일 결과를 복구한다')
 invalid={'locals':[{'id':'firstValue','name':'실패 전에 바꾼 이름','type':'long'}],'nodes':[{'id':'first','local':'counter','outputLocal':'firstValue','type':'long','valueJson':'{"constant":2}'},{'id':'second','local':'counter','outputLocal':'secondValue','type':'int','valueJson':'{"constant":3}'}]};refused=call('blueprint',{'action':'authorBatch',**request(cold,invalid)},ok=False);assert not refused['ok'];after=current();assert after['sources']==cold['sources'] and after['checkpointHash']==checkpoint and next(v for v in after['locals'] if v['id']=='firstValue')['name']=='첫 저장값';unchanged();checked('늦은 두 번째 Set의 타입 실패는 앞선 이름/값 변경도 롤백하여 기존 초안을 전부 보존한다')
 typed={'nodes':[{'id':'first','local':'counter','outputLocal':'firstValue','type':'long','valueJson':'{"constant":"wrong"}'}]};refused=call('blueprint',{'action':'authorBatch',**request(after,typed)},ok=False);assert not refused['ok'] and current()['sources']==after['sources'] and current()['checkpointHash']==checkpoint;unchanged();checked('실제 값 자료형 오류는 최종 후보 검증에서 거절하며 값과 출력 저장소가 부분 적용되지 않는다')
 readonly={'nodes':[{'id':'first','local':'readonlyAlias','outputLocal':'firstValue','type':'long','valueJson':'{"constant":6}'}]};refused=call('blueprint',{'action':'authorBatch',**request(after,readonly)},ok=False);assert not refused['ok'] and current()['sources']==after['sources'] and current()['checkpointHash']==checkpoint;unchanged();checked('기존 입력 alias를 writable Set 대상으로 위조해도 거절하며 출력 셀과 기존 값을 바꾸지 않는다')
 stale=request(after,{'nodes':[{'id':'first','local':'counter','outputLocal':'firstValue','type':'long','valueJson':'{"constant":7}'}]});call('blueprint',{'action':'intent','id':after['id'],'basis':after['basis'],'node':'first','text':'다른 편집자가 저장한 설명'});call('saveDraft',{});peer=current();refused=call('blueprint',{'action':'authorBatch',**stale},ok=False);assert not refused['ok'] and current()['sources']==peer['sources'] and next(v for v in current()['nodes'] if v['id']=='first')['intent']=='다른 편집자가 저장한 설명';unchanged();checked('실제 peer/checkpoint 변경은 오래된 Set 후보를 거절하고 peer 초안과 재시도 입력을 보존한다')
 fresh=request(peer,stale['edits'][0]['definition']);call('blueprint',{'action':'authorBatch',**fresh});assert next(v for v in current()['nodes'] if v['id']=='first')['arguments'][0]['valueJson']=='{"constant":7}';assert next(v for v in current()['nodes'] if v['id']=='first')['intent']=='다른 편집자가 저장한 설명';unchanged();checked('명시적으로 새 source proof를 읽은 재시도는 peer 설명을 유지하며 선택한 Set 값만 저장한다')
 call('reviewGroup',{'ids':[data['id']],'target':'portable'});review=state()['review'];assert review['status']=='ready';unchanged();call('confirmGroup',{'ids':[data['id']],'token':review['token']});assert json.loads((project/'Calc.graph.json').read_text())['nodes'][1]['id']=='first';assert {name for name,b in original.items() if (project/name).read_bytes()!=b}=={'Calc.graph.json'};checked('별도 실제 compiler Review와 명시적 Confirm만 graph 원본을 반영하며 다른 함수/프로젝트 파일은 보존한다')
except Exception:
 print('EVIDENCE '+str(case),flush=True);raise
finally:stop()
record={'checks':checks,'actualEngine':True,'renderer':False,'projectRun':False,'accountOrInference':False,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False,indent=2))
