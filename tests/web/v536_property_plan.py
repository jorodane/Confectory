"""v536 Set desktop/mobile UI, private input restoration and atomic compiler boundary; isolated project."""
import hashlib,json,os,pathlib,signal,subprocess,sys,tempfile,time,urllib.request,uuid,copy
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-set-plan-'));project=case/'owned project';project.mkdir();n='Owned.Set::';env=os.environ.copy()
model='Confectory.ObjectModel';reader='fg_call_'+hashlib.sha256((model+'::Read').encode()).hexdigest()[:24];setter='fg_call_'+hashlib.sha256((model+'::Set').encode()).hexdigest()[:24]
items={'Main':('function','function '+n+'Main () -> int {provide '+n+'Main with '+n+'MainBody;}'),'MainBody':('implementation','implementation '+n+'MainBody for '+n+'Main () -> int {import '+n+'Calc as Calc (object,long) -> long;import '+model+'::Create as Create (string,string[],object[]) -> object;body common "Main.csbody";}'),'Calc':('function','function '+n+'Calc (object target,long replacement) -> long {provide '+n+'Calc with '+n+'CalcBody;}'),'CalcBody':('implementation','implementation '+n+'CalcBody for '+n+'Calc (object target,long replacement) -> long {import '+model+'::Read as '+reader+' (object,string,string,string) -> object;import '+model+'::Set as '+setter+' (object,string,string,string,object) -> void;blueprint common "Calc.graph.json";}'),'Vitals':('schema','schema '+n+'Vitals {field health single general long;}'),'Monster':('object','object '+n+'Monster {use schema '+n+'Vitals;}')}
def metadata(operation,**fields):
 r=subprocess.run([env['CONFECTORY_DOTNET'],str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps({'operation':operation,**fields}),text=True,capture_output=True,check=True,env=env);v=json.loads(r.stdout);assert v['ok'],v;return v['result']
g=metadata('blueprintPrepareFeature',id=n+'Calc',text='function '+n+'Calc (object target,long replacement) -> long {}',implementation=n+'CalcBody',graphPath='Calc.graph.json',nodePath='combine.node.json')['graph'];g['profile']='sync-acyclic-property-set-v1';g['entry']='before';g['locals']=[{'id':'counter','name':'현재 값','type':'long','initial':{'constant':0}},{'id':'firstValue','name':'첫 저장값','type':'long','initial':{'constant':0}},{'id':'secondValue','name':'다음 저장값','type':'long','initial':{'constant':0}}]
g['nodes']=[{'id':'before','kind':'property','control':'next','intent':'읽기 전 현재값','propertyOwner':n+'Monster','field':'health','fieldContractHash':'','signature':{'args':[{'name':'target','type':'object'}],'return':'long'},'arguments':{'target':{'input':'target'}}},{'id':'first','kind':'set','control':'next','intent':'첫 출력 보관','local':'counter','outputLocal':'firstValue','signature':{'args':[{'name':'value','type':'long'}],'return':'void'},'arguments':{'value':{'node':'before','output':'return'}}},{'id':'write','kind':'property-set','control':'next','intent':'실행 시점의 필드에 쓰기','propertyOwner':n+'Monster','field':'health','fieldContractHash':'','signature':{'args':[{'name':'target','type':'object'},{'name':'value','type':'long'}],'return':'void'},'arguments':{'target':{'input':'target'},'value':{'input':'replacement'}}},{'id':'second','kind':'set','control':'next','intent':'다음 출력 보관','local':'counter','outputLocal':'secondValue','signature':{'args':[{'name':'value','type':'long'}],'return':'void'},'arguments':{'value':{'constant':0}}},{'id':'combine','kind':'code','control':'next','intent':'두 스냅샷 비교','displayName':'보관값 합치기','signature':{'args':[{'name':'before','type':'long'},{'name':'after','type':'long'}],'return':'long'},'arguments':{'before':{'node':'first','output':'stored'},'after':{'node':'second','output':'stored'}},'implementation':'combine.node.json'},{'id':'finish','kind':'export','control':'next','intent':'결과 내보내기','output':'return','signature':{'args':[{'name':'value','type':'long'}],'return':'void'},'arguments':{'value':{'node':'combine','output':'return'}}}];g['edges']=[{'from':a,'port':'next','to':b} for a,b in [('before','first'),('first','write'),('write','second'),('second','combine'),('combine','finish')]];g['exits']={}
sources={name+'.celem':text for name,(_,text) in items.items()};sources['project.cproj']='project Owned.Set version "1" {standalone true;entry '+n+'Main;'+''.join('element '+name+' '+kind+' "'+name+'.celem";' for name,(kind,text) in items.items())+'registry Confectory.Build.DotNet "'+str(repo/'targets/dotnet/pack.cpack')+'";dependency Confectory.Build.DotNet version "0.1.0";registry '+model+' "'+str(repo/'packs/object-model/pack.cpack')+'";dependency '+model+' version "0.1.0";target portable Confectory.Build.DotNet::Portable;}'
for name,text in sources.items():(project/name).write_bytes(text.encode())
descriptor=metadata('blueprintPropertyCatalog',project=str(project/'project.cproj'),sourceId=n+'CalcBody',owner=n+'Monster')['descriptor'];field=descriptor['fields'][0]
g['nodes'][0]['fieldContractHash']=g['nodes'][2]['fieldContractHash']=field['hash'];contracts={model+'::'+k:(repo/'packs/object-model'/(k+'.celem')).read_text() for k in ['Read','Set']};defs=metadata('featureBlueprintNodes',featureSource=items['Calc'][1],graph=g,propertyContracts={n+'Monster':descriptor},featureContracts=contracts);assert defs['state']=='node-definitions',defs
record={'schema':1,'node':'combine','definitionHash':next(v for v in defs['nodes'] if v['id']=='combine')['definitionHash'],'source':'return before*100+after;'}
sources['combine.node.json']=json.dumps(record);sources['Calc.graph.json']=json.dumps(g,ensure_ascii=False);sources['Main.csbody']='object target=calls.Create.Invoke('+json.dumps(json.dumps(descriptor,separators=(',',':')))+',new[]{'+json.dumps(field['id'])+'},new object[]{10L});Console.WriteLine(calls.Calc.Invoke(target,20));Console.WriteLine(calls.Calc.Invoke(target,30));return 0;'
for name,text in sources.items():(project/name).write_bytes(text.encode())
if 'new-import' in sys.argv[3:]:
 g['nodes']=[v for v in g['nodes'] if v['id']!='before'];g['entry']='first';g['nodes'][0]['arguments']['value']={'constant':1};g['edges']=[e for e in g['edges'] if e['from']!='before'];sources['Calc.graph.json']=json.dumps(g,ensure_ascii=False);sources['CalcBody.celem']=sources['CalcBody.celem'].replace('import '+model+'::Read as '+reader+' (object,string,string,string) -> object;','');(project/'Calc.graph.json').write_text(sources['Calc.graph.json']);(project/'CalcBody.celem').write_text(sources['CalcBody.celem'])
if 'copy-boundary' in sys.argv[3:]:
 g['copySource']={'implementation':n+'Origin','target':'common','bodyOrigin':n+'Origin','sourceKind':'blueprint'};(project/'Calc.graph.json').write_text(json.dumps(g,ensure_ascii=False))
original={p.name:p.read_bytes() for p in project.iterdir() if p.is_file()};env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(case/'profile'),CONFECTORY_ENTRY_STORAGE=str(case/'profile'),CONFECTORY_MCP_DIRECTORY=str(case/'instances'),CONFECTORY_WEB_PROJECT=str(project/'project.cproj'));env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];host=None;log=None;checks=[]
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

if __name__=='__main__':
 try:
  start(0);data=current();plan={'reads':[{'node':'after','owner':n+'Monster','field':'health','descriptor':descriptor,'targetJson':'{"input":"target"}'}],'changes':[{'action':'route','node':'write','port':'next','to':'after'},{'action':'route','node':'after','port':'next','to':'second'},{'action':'argument','node':'second','name':'value','valueJson':'{"node":"after","output":"return"}'}]}
  def command(plan,data=data):return {'action':'authorBatch','id':data['id'],'attempt':uuid.uuid4().hex,'sourceProof':json.dumps(sorted([[v['id'],v['revision'],v['hash']] for v in data['sources']]),separators=(',',':')),'checkpointHash':data['checkpointHash'],'edits':[{'action':'propertyPlan','node':'$properties','definition':plan}]}
  if 'copy-boundary' in sys.argv[3:]:
   assert data['requiresCoupledCopy'];call('blueprint',command(plan),ok=False);assert current()['sources']==data['sources'];unchanged();checked('복사 provenance graph는 owner 문맥을 생략한 Property 후보도 거절한다');print(json.dumps({'checks':checks,'evidence':str(case)},ensure_ascii=False));sys.exit(0)
  baseline=copy.deepcopy(data)
  def rejected(plan):
   call('blueprint',command(plan),ok=False);after=current();assert after['sources']==baseline['sources'] and after['checkpointHash']==baseline['checkpointHash'];unchanged()
  call('blueprint',{'action':'propertyPlan','id':data['id'],'definition':plan},ok=False);assert current()['sources']==data['sources'];unchanged();checked('Property plan을 실제 checkpoint author 후보 밖에서 직접 호출하면 거절한다')
  bad=copy.deepcopy(plan);bad['reads'][0]['descriptor']['fields'][0]['hash']='0'*64;rejected(bad);checked('선택 후 바뀐 필드 계약 descriptor는 거절하고 새 노드/가져오기/연결을 부분 적용하지 않는다')
  bad=copy.deepcopy(plan);bad['changes'].append({'action':'argument','node':'second','name':'missing','valueJson':'{"constant":7}'});rejected(bad);checked('늦은 입력 대상 오류는 앞서 준비한 읽기·typed 가져오기·경로까지 같은 후보에서 롤백한다')
  bad=copy.deepcopy(plan);bad['reads'][0]['targetJson']='{"input":"replacement"}';rejected(bad);checked('실제 receiver 자료형 오류는 최종 graph 검증으로 거절하며 기존 두 Set와 schema를 유지한다')
  bad=copy.deepcopy(plan);bad['changes']=[{'action':'source','node':'combine','text':'return 0;'}];rejected(bad);checked('Property 결합 경로를 통한 임의 본문 쓰기와 지원 밖 action을 거절한다')
  bad=copy.deepcopy(plan);bad['changes']=[{'action':'argument','node':'second','name':'value','valueJson':'{"node":"after","output":"return"}'}];rejected(bad);checked('실행 시점이 지정되지 않은 읽기를 소비만 연결해 제출하면 가용성/attachment 검사가 거절한다')
  valid=command(plan);call('blueprint',valid);after=current();assert len(after['nodes'])==len(data['nodes'])+1;assert after['diagnostics']['state'] in ['source-ready','source-assembled'];assert (next(v for v in after['sources'] if v['id']==n+'CalcBody')['hash']==next(v for v in data['sources'] if v['id']==n+'CalcBody')['hash'])==('new-import' not in sys.argv[3:]);unchanged();checked('명시적 읽기/receiver/소비/직렬 연결은 한 후보로 저장하고 기존 typed 구현은 보존하며 누락한 읽기 import만 함께 준비한다')
  retry={**valid,'action':'settledAuthorBatch'};assert call('blueprint',retry)['settled'];checkpoint=after['checkpointHash'];call('blueprint',valid);assert current()['checkpointHash']==checkpoint and len(current()['nodes'])==len(after['nodes']);unchanged();checked('같은 시도의 receipt 조회와 재시도는 읽기 노드·경로·저장소를 중복 생성하지 않는다')
 except Exception:
  print('EVIDENCE '+str(case),flush=True);raise
 finally:stop()
 record={'checks':checks,'actualEngine':True,'renderer':False,'projectRun':False,'accountOrInference':False,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False,indent=2))
