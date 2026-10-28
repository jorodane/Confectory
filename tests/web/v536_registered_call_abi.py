"""Actual explicit registered-call ABI, direct declaration receipts, no account/inference/run."""
import hashlib,json,re,os,pathlib,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-registered-call-abi-'));project=case/'owned project';project.mkdir();n='Owned.Context::'
env=os.environ.copy();env.update(CONFECTORY_DOTNET=env.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet'))
def metadata(operation,**data):
 r=subprocess.run([env['CONFECTORY_DOTNET'],str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps({'operation':operation,**data}),text=True,capture_output=True,env=env,check=True);v=json.loads(r.stdout);assert v['ok'],v;return v['result']
items={
 'Main':('function','function '+n+'Main () -> int {provide '+n+'Main with '+n+'MainBody;}'),
 'MainBody':('implementation','implementation '+n+'MainBody for '+n+'Main () -> int {import '+n+'Calc as Chosen (long) -> long in '+n+'A;body common "Main.csbody";}'),
 'Calc':('function','function '+n+'Calc (long amount) -> long {provide '+n+'Calc with '+n+'Caller;}'),
 'Other':('implementation','implementation '+n+'Other for '+n+'Calc (long amount) -> long {body common "Other.csbody";}'),
 'Rules':('module','module '+n+'Rules {require '+n+'Calc (long) -> long;}'),
 'A':('object','object '+n+'A {module '+n+'Rules;provide '+n+'Calc with '+n+'Caller;}'),
 'B':('object','object '+n+'B {module '+n+'Rules;provide '+n+'Calc with '+n+'Other;}')}
lib=case/'Lib';lib.mkdir();foreign_fn='function Lib::Native (ref long amount) -> long {provide Lib::Native with Lib::NativeBody;}'
(lib/'Native.celem').write_text(foreign_fn);(lib/'NativeBody.celem').write_text('implementation Lib::NativeBody for Lib::Native (ref long amount) -> long {body common "Native.csbody";}');(lib/'Native.csbody').write_text('return amount+3;');(lib/'pack.cpack').write_text('pack Lib version "1" {element Native function "Native.celem";element NativeBody implementation "NativeBody.celem";}')
prepared=metadata('blueprintPrepareFeature',id=n+'Calc',text='function '+n+'Calc (long amount) -> long {}',implementation=n+'Caller',graphPath='Caller.graph.json',nodePath='Caller.node.json')
defs=metadata('featureBlueprintNodes',featureSource=items['Calc'][1],graph=prepared['graph'])
record={'schema':1,'node':'body','definitionHash':defs['nodes'][0]['definitionHash'],'source':'return amount;'}
prepared=metadata('blueprintPrepareCall',id=n+'Caller',text=prepared['implementation'],targetText=foreign_fn,graph=prepared['graph'],definition={'id':'native','feature':'Lib::Native','intent':'기존 호출 계약 갱신','control':'next'})
g=prepared['graph'];g['profile']='sync-acyclic-switch-v1';node=next(v for v in g['nodes'] if v['id']=='native');node['arguments']={'amount':{'input':'amount'}};g['entry']='native';g['edges'].append({'from':'native','port':'next','to':'body'});next(v for v in g['nodes'] if v['id']=='body')['arguments']={'amount':{'node':'native'}}
enum={'primary':'next','members':[{'id':'next','name':'NoBranch','value':0}]}
wrapper=metadata('blueprintCallWrapper',functionText=foreign_fn,executionEnum=enum,returnMapping='native-return-out-v1',source='return Result.NoBranch;')
node.update(control='switch',executionEnum=enum,postCall={'mode':'execution-enum','returnMapping':'native-return-out-v1','contractHash':wrapper['contractHash'],'source':wrapper['source'],'helpers':''})
items['Caller']=('implementation',prepared['implementation'])
(lib/'Native.celem').write_text(foreign_fn.replace('(ref long','(long'));p=lib/'NativeBody.celem';p.write_text(p.read_text().replace('(ref long','(long'))
sources={'Main.csbody':'return checked((int)calls.Chosen.Invoke(1));','Other.csbody':'return amount+8;','Caller.graph.json':json.dumps(g),'Caller.node.json':json.dumps(record)}
for name,(kind,text) in items.items():sources[name+'.celem']=text
sources['project.cproj']='project Owned.Context version "1" {standalone true;entry '+n+'Main;'+''.join('element '+name+' '+kind+' "'+name+'.celem";' for name,(kind,text) in items.items())+'registry Lib "../Lib/pack.cpack";dependency Lib version "1";registry Confectory.Build.DotNet "'+str(repo/'targets/dotnet/pack.cpack')+'";dependency Confectory.Build.DotNet version "0.1.0";target portable Confectory.Build.DotNet::Portable;}'
for name,text in sources.items():(project/name).write_bytes(text.encode())
original={p.name:p.read_bytes() for p in project.iterdir()};env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(case/'profile'),CONFECTORY_ENTRY_STORAGE=str(case/'profile'),CONFECTORY_MCP_DIRECTORY=str(case/'instances'),CONFECTORY_WEB_PROJECT=str(project/'project.cproj'));env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];host=None;log=None;traffic=[];results={};errors=[];external=[];checks=[]
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
def setup(browser):
 page=browser.new_page(viewport={'width':1480,'height':1050});page.on('pageerror',lambda e:errors.append(str(e)))
 def observe(response):
  try:
   body=response.request.post_data_json
   if isinstance(body,dict) and body.get('op')=='invoke':traffic.append(body)
   elif isinstance(body,dict) and body.get('op')=='update':
    for result in response.json().get('results',[]):results[result['requestId']]=result
  except Exception:pass
 page.on('response',observe);page.route('**/*',lambda r:r.continue_() if r.request.url.startswith(origin+'/') else (external.append(r.request.url),r.abort()));goto_editor(page,url);return page
def idle():expect(page.locator('.brand')).to_be_enabled(timeout=60000)
def completed(endpoint,action,mark):
 for _ in range(3000):
  requests=[r for r in traffic[mark:] if r['endpoint']==endpoint and r.get('input',{}).get('action')==action]
  rows=[results[r['requestId']] for r in requests if r['requestId'] in results]
  good=[r for r in rows if r.get('ok')]
  if good:idle();return good[-1]
  refused=[r for r in rows if r.get('error',{}).get('code')!='stale_revision'];assert not refused,refused
  page.wait_for_timeout(20)
 raise AssertionError((endpoint,action,'actual response not observed',page.get_by_role('status').all_text_contents()))
def pending():page.evaluate('async()=>await confectoryFlushPresentation()');return state()['presentation']['inputs']['blueprint']
def open_row(name,group):
 idle();page.locator('#workspace').click(button='right',position={'x':1240,'y':650});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=page.locator('.window[data-key^="browser:project:"]');b.locator('[data-tab="'+group+'"]').click();row=b.locator('[data-object="'+n+name+'"]');expect(row).to_have_attribute('aria-disabled','false');row.press('Enter');idle();b.locator('[data-close]').click();return b
def open_slot():
 open_row('A','concept');w=page.locator('.window[data-key=schema]');slot=w.locator('[data-module-method="'+n+'Calc"]');expect(slot.locator('[data-function-edit]')).to_be_enabled();slot.locator('[data-function-edit]').click();a=page.locator('.window[data-key=blueprint]');expect(a).to_have_attribute('data-blueprint-owner',n+'A');expect(a).to_have_attribute('data-blueprint-body',n+'Caller/body:common');idle();return a
foreign_original={p.name:p.read_bytes() for p in lib.iterdir() if p.is_file()}
def foreign_same():assert all((lib/name).read_bytes()==b for name,b in foreign_original.items())
def collect_wrapper():return [(k,v) for k,v in pending() if v.get('type')=='wrapper']
def focus_call():author.locator(':scope > .window-title .caption').click(position={'x':5,'y':8});author.locator('[data-bp-overview-node=native]').click()
def current():return call('blueprint',{'action':'read','id':n+'Caller/body:common'})
try:
 start(0)
 with sync_playwright() as p:
  expect.set_options(timeout=30000);browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=setup(browser);author=open_slot();expect(author.locator('[data-bp-node=native] [data-wrapper-refresh]')).to_be_enabled();data=current();node=next(v for v in data['nodes'] if v['id']=='native');assert node['callAbiAvailable'] and node['callAbiReceipt']['id']=='Lib::Native' and node['callAbiReceipt']['textHash']==hashlib.sha256((lib/'Native.celem').read_bytes()).hexdigest();assert not any(row['id'].startswith('Lib::') for row in data['sources']);unchanged();foreign_same();checked('직접 등록 callable의 선언/manifest receipt만 읽어 기존 소유 슬롯의 ABI 갱신 버튼에 연결하고 외부 소스는 쓰기 대상에 넣지 않는다')
  focus_call();author.locator('[data-bp-node=native] [data-wrapper-refresh]').click();held=collect_wrapper();plan=json.loads(held[0][1]['text']);assert plan['abi']['receipt']==node['callAbiReceipt'];owner=state()['schema'];fresh=call('blueprint',{'action':'read','id':data['id'],'owner':n+'A','ownerHash':owner['textHash']});batch={'action':'authorBatch','id':data['id'],'attempt':uuid.uuid4().hex,'checkpointHash':fresh['checkpointHash'],'sourceProof':json.dumps(sorted([[r['id'],r['revision'],r['hash']] for r in fresh['sources']])),'owner':n+'A','ownerHash':owner['textHash'],'edits':[{'action':'rebindCallAbi','node':'native','definition':__import__('copy').deepcopy(plan)}]};batch['edits'][0]['definition']['abi'].pop('receipt');call('blueprint',batch,False);batch['edits'][0]['definition']=__import__('copy').deepcopy(plan);batch['edits'][0]['definition']['abi']['receipt']['manifestHash']='0'*64;call('blueprint',batch,False);assert collect_wrapper()==held;unchanged();foreign_same();checked('누락·위조된 등록 manifest receipt는 서버에서 거절하며 typed import·graph와 사용자 입력을 보존한다')
  pack=lib/'pack.cpack';pack.write_bytes(foreign_original['pack.cpack']+b' ');author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_contain_text('입력은 유지',timeout=60000);assert collect_wrapper()==held;assert next(v for v in current()['nodes'] if v['id']=='native')['signature']['args'][0]['mode']=='ref';unchanged();assert (lib/'Native.celem').read_bytes()==foreign_original['Native.celem'];checked('같은 함수 문구여도 등록 manifest가 바뀌면 실제 UI Save를 거절하고 기존 graph/import와 입력·저장 시도 기록을 유지한다')
  journal=next(value for key,value in pending() if value.get('kind')=='author-attempt');settlement={'action':'settledAuthorBatch','id':journal['graph'],'attempt':journal['attempt'],'checkpointHash':journal['checkpointHash'],'sourceProof':journal['sourceProof'],'edits':journal['edits'],'owner':n+'A','ownerHash':owner['textHash']};same=call('blueprint',settlement);assert not same['settled'] and same['baselineUnchanged'];bad=__import__('copy').deepcopy(settlement);bad['checkpointHash']='0'*64;assert not call('blueprint',bad)['baselineUnchanged'];bad=__import__('copy').deepcopy(settlement);bad_proof=json.loads(bad['sourceProof']);bad_proof[0][2]='0'*64;bad['sourceProof']=json.dumps(bad_proof);assert not call('blueprint',bad)['baselineUnchanged'];assert collect_wrapper()==held;unchanged();checked('새 계약 재확인은 원래 checkpoint·전체 소유 source closure가 그대로인 경우만 허용하고 다른 hash/checkpoint는 재시도 기록을 해제하지 않는다')
  pending();page.close();stop();start(1);page=setup(browser);author=page.locator('.window[data-key=blueprint]');expect(author).to_have_attribute('data-blueprint-owner',n+'A');expect(author.locator('[data-bp-save]')).to_be_enabled();assert collect_wrapper()==held;focus_call();author.locator('[data-bp-node=native] [data-wrapper-refresh]').click();held=collect_wrapper();assert json.loads(held[0][1]['text'])['abi']['receipt']['manifestHash']==hashlib.sha256(pack.read_bytes()).hexdigest();assert json.loads(held[0][1]['text'])['refreshFrom']==plan['refreshFrom'];foreign_original['pack.cpack']=pack.read_bytes();author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_have_text('저장됨',timeout=60000);assert pending()==[];past=call('blueprint',settlement);assert not past['baselineUnchanged'] and not past['settled'];assert next(v for v in current()['nodes'] if v['id']=='native')['signature']['args'][0].get('mode') is None;unchanged();foreign_same();checked('변경된 등록 계약의 명시적 재확인 뒤 cold·명시적 재시도는 보관한 ABI/import를 함께 checkpoint하며 외부 팩과 원본 파일은 Confirm 전 보존한다')
  author.locator('[data-bp-complete]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=60000);assert state()['review']['status']=='ready';assert all(not r['id'].startswith('Lib::') for r in state()['review']['units']);review.locator('[data-reject]').click();expect(review).to_be_hidden();unchanged();foreign_same();author.locator('[data-bp-complete]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=60000)
  if review.locator('[data-review-advanced]').count():
   review.locator('[data-review-advanced]').click()
   if review.locator('[data-advanced-reviewed]').count():review.locator('[data-advanced-reviewed]').check()
  mark=len(traffic);review.locator('#confirm').click();result=completed('confirmGroup',None,mark);assert result['result']['sourceConfirmed'];expect(review).to_have_count(0,timeout=90000);changed={name for name,b in original.items() if (project/name).read_bytes()!=b};assert changed=={'Caller.celem','Caller.graph.json'},changed;foreign_same();page.screenshot(path=str(case/'registered-abi-confirmed.png'));checked('실제 Review 취소와 새 명시적 compiler Confirm은 소유 Caller 선언/graph만 반영하고 등록 팩·함수·provider 원본은 보존한다')
  assert not errors and not external,(errors,external);page.close();browser.close()
except Exception:
 print('EVIDENCE '+str(case),flush=True);raise
finally:stop()
record={'checks':checks,'actualEngine':True,'registeredContractOnly':True,'nativeWindows':False,'accountOrInference':False,'projectRun':False,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False,indent=2))
