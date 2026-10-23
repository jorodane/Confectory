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

from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
errors=[];traffic=[];results={}
def setup(browser):
 page=browser.new_page(viewport={'width':1480,'height':1050});page.on('pageerror',lambda e:errors.append(str(e)))
 def observe(response):
  try:
   body=response.request.post_data_json
   if isinstance(body,dict) and body.get('op')=='invoke':traffic.append(body)
   elif isinstance(body,dict) and body.get('op')=='update':
    for result in response.json().get('results',[]):results[result['requestId']]=result
  except Exception:pass
 page.on('response',observe);page.route('**/*',lambda r:r.continue_() if r.request.url.startswith(origin+'/') else r.abort());goto_editor(page,url);return page
def idle():expect(page.locator('.brand')).to_be_enabled(timeout=60000)
def pending():page.evaluate('async()=>await confectoryFlushPresentation()');return state()['presentation']['inputs']['blueprint']
def author():return page.locator('.window[data-key=blueprint]')
def open_author():
 idle();page.locator('#workspace').click(button='right',position={'x':1240,'y':650});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=page.locator('.window[data-key^="browser:project:"]');b.locator('[data-tab="feature"]').click();row=b.locator('[data-object="'+n+'Calc"]');expect(row).to_have_attribute('aria-disabled','false');row.press('Enter');idle();b.locator('[data-close]').click();page.locator('.window[data-key=declaration] [data-function-write-direct]').click();expect(author().locator('[data-bp-save]')).to_be_enabled();idle()
def value(id,text):
 author().locator('[data-bp-node="'+id+'"] .bp-pin-plug[data-side=in] input').click();menu=page.get_by_role('dialog',name='핀 값 선택',exact=True);menu.get_by_role('searchbox',name='값 검색').fill(text);menu.get_by_role('searchbox',name='값 검색').press('Enter');expect(menu).not_to_be_visible()
def saved(mark):
 for _ in range(3000):
  requests=[r for r in traffic[mark:] if r['endpoint']=='blueprint' and r.get('input',{}).get('action')=='authorBatch'];rows=[results[r['requestId']] for r in requests if r['requestId'] in results]
  if any(r.get('ok') for r in rows):idle();return requests
  refused=[r for r in rows if r.get('error',{}).get('code')!='stale_revision'];assert not refused,refused
  page.wait_for_timeout(20)
 raise AssertionError(('save response missing',page.get_by_role('status').all_text_contents()))
try:
 start(0)
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=setup(browser);open_author();expect(author().locator('.bp-kind-property')).to_have_count(1);expect(author().locator('.bp-kind-set')).to_have_count(2);assert author().locator('[data-bp-node=before] .bp-exec-line').count()==0;assert pending()==[];assert not errors,errors;unchanged();checked('기존 속성 읽기는 원본 실행핀 없는 카드와 대상/값으로 열리고 기존 읽기→Set 저장→필드 쓰기 순서를 유지한다')
  # Create the second independent read through the original resource menu.
  author().locator('.bp-viewport').click(button='right',position={'x':330,'y':220});menu=page.get_by_role('dialog',name='블루프린트 노드 검색',exact=True);menu.locator('[data-resource-kind]').select_option('property');expect(menu.locator('[data-resource-property=health]')).to_be_visible(timeout=60000);idle();menu.locator('[data-resource-property=health]').click();expect(author().locator('.bp-kind-property')).to_have_count(2);created=next(v['node'] for _,v in pending() if v['type']=='property-plan' and not json.loads(v['text']).get('existing'));assert len(current()['nodes'])==6;unchanged();checked('원본 검색에서 새 속성을 골라도 계약/노드/가져오기는 비공개 선택으로 보관하고 원본·공유 초안에 먼저 쓰지 않는다')
  # Mobile value selectors use the same actual hidden desktop pins and checked bindings.
  page.set_viewport_size({'width':390,'height':844});author().locator('[data-flow-node="'+created+'"]').click();overlay=page.locator('.bp-flow-overlay-host:visible');overlay.locator('[data-flow-value]').click();values=page.get_by_role('dialog',name='핀 값 선택',exact=True);values.get_by_role('button',name='입력 · target',exact=True).click();overlay.locator('[data-flow-done]').click();author().locator('[data-flow-node=second]').click();overlay.locator('[data-flow-value]').click();values=page.get_by_role('dialog',name='핀 값 선택',exact=True);values.get_by_role('button',name='속성 · health · health',exact=True).last.click();overlay=page.locator('.bp-flow-overlay-host:visible');overlay.locator('[data-flow-done]').click();held=pending();plan=next(json.loads(v['text']) for _,v in held if v['type']=='property-plan' and not json.loads(v['text']).get('existing'));assert plan['attached'];assert len(current()['nodes'])==6;unchanged();page.screenshot(path=str(case/'property-mobile.png'));checked('실제 모바일 값 선택은 명시한 receiver와 소비 Set을 연결하고 그 작업 직전 읽기 경로를 같은 개인 계획에 보관한다')
  page.close();stop();start(1);page=setup(browser);page.set_viewport_size({'width':390,'height':844});expect(author().locator('[data-bp-save]')).to_be_enabled();idle();assert pending()==held;mark=len(traffic);author().locator('[data-bp-save]').click();requests=saved(mark);assert requests[-1]['input']['edits'][0]['action']=='propertyPlan';data=current();assert data['diagnostics']['state'] in ['source-ready','source-assembled'],data['diagnostics'];assert next(v for v in data['nodes'] if v['id']=='second')['arguments'][0]['valueJson']==json.dumps({'node':created,'output':'return'},separators=(',',':'));assert {'from':'write','port':'next','to':created} in data['edges'] and {'from':created,'port':'next','to':'second'} in data['edges'];assert next(v for v in data['nodes'] if v['id']=='first')['arguments'][0]['valueJson']=='{"node":"before","output":"return"}';unchanged();checked('재시작 후 하나의 후보/CAS로 새 읽기·typed 가져오기·receiver·소비 binding·실행 attachment를 함께 저장하며 첫 출력/원본을 보존한다')
  author().locator('[data-bp-complete]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=120000)
  if review.locator('[data-review-advanced]').count():
   review.locator('[data-review-advanced]').click()
   if review.locator('[data-advanced-reviewed]').count():review.locator('[data-advanced-reviewed]').check()
  review.locator('#confirm').click();expect(review).not_to_be_visible(timeout=120000);idle();assert {name for name,b in original.items() if (project/name).read_bytes()!=b}=={'Calc.graph.json'},'existing typed imports and exact implementation bytes must be preserved';checked('화면의 명시적 compiler Confirm만 새 읽기/Set 연결 graph를 반영하고 다른 원본은 유지한다')
  output=subprocess.run([env['CONFECTORY_DOTNET'],str(repo/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),'build',str(project/'project.cproj'),'portable'],cwd=repo,env=env,text=True,capture_output=True,check=True);built=json.loads(output.stdout);(case/'fixture-build.json').write_text(output.stdout);run=subprocess.run(built['run'],cwd=project,env=env,text=True,capture_output=True,check=True);assert run.stdout.strip()=='1020\n2030',(run.stdout,run.stderr);checked('격리 CLR 실행에서10→쓰기20→별도 읽기20과 다음 호출20→30을 확인하고 같은 대상에 후속 Set을 해도 앞 보관 출력10/20을 유지한다')
  assert not errors,errors;browser.close()
except Exception:
 print('EVIDENCE '+str(case),flush=True);print('PAGE_ERRORS '+str(errors),flush=True);raise
finally:stop()
record={'checks':checks,'actualEngine':True,'renderer':True,'isolatedFixtureCLR':True,'engineProjectRun':False,'accountOrInference':False,'nativeWindows':False,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False,indent=2))
