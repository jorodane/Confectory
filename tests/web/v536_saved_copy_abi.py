"""Saved one-target copy ABI snapshot, actual engine/renderer; no copy-creation or live account claim.
Fixture setup shares the finite local call context used by v536_slot_call_abi.
"""
import hashlib,json,re,os,pathlib,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
nested='nested' in sys.argv[3:];is_view='view' in sys.argv[3:];general='remap' in sys.argv[3:];closure='closure' in sys.argv[3:];correction='correction' in sys.argv[3:];corrected=False
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-saved-copy-abi-'));project=case/'owned project';project.mkdir();n='Owned.Context::'
env=os.environ.copy();env.update(CONFECTORY_DOTNET=env.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet'))
def metadata(operation,**data):
 r=subprocess.run([env['CONFECTORY_DOTNET'],str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps({'operation':operation,**data}),text=True,capture_output=True,env=env,check=True);v=json.loads(r.stdout);assert v['ok'],v;return v['result']
items={
 'Main':('function','function '+n+'Main () -> int {provide '+n+'Main with '+n+'MainBody;}'),
 'MainBody':('implementation','implementation '+n+'MainBody for '+n+'Main () -> int {import '+n+'Calc as Chosen (long) -> long in '+n+'A;body common "Main.csbody";}'),
 'Calc':('function','function '+n+'Calc (long amount) -> long {provide '+n+'Calc with '+n+'Copy;}'),
 'Native':('function','function '+n+'Native (ref long amount) -> long {provide '+n+'Native with '+n+'NativeBody;}'),
 'NativeBody':('implementation','implementation '+n+'NativeBody for '+n+'Native (ref long amount) -> long {body common "Native.csbody";}'),
 'Other':('implementation','implementation '+n+'Other for '+n+'Calc (long amount) -> long {body common "Other.csbody";}'),
 'Rules':('module','module '+n+'Rules {require '+n+'Calc (long) -> long;}'),
 'A':('object','object '+n+'A {module '+n+'Rules;provide '+n+'Calc with '+n+'Copy;}'),
 'B':('object','object '+n+'B {module '+n+'Rules;provide '+n+'Calc with '+n+'Other;}')}
if is_view:items['A']=('schema',items['A'][1].replace('object ','schema ',1))
assert not closure or nested and general
registered='registered' in sys.argv[3:];assert not general or nested and not registered;callee='Lib::Native' if registered else n+'Native';callee_text=items['Native'][1].replace(n+'Native','Lib::Native') if registered else items['Native'][1]
lib=case/'Lib'
if registered:
 lib.mkdir();(lib/'Native.celem').write_text(callee_text.replace('(ref long','(long'));(lib/'NativeBody.celem').write_text('implementation Lib::NativeBody for Lib::Native (long amount) -> long {body common \"Native.csbody\";}');(lib/'Native.csbody').write_text('return amount+3;');(lib/'pack.cpack').write_text('pack Lib version \"1\" {element Native function \"Native.celem\";element NativeBody implementation \"NativeBody.celem\";}')
prepared=metadata('blueprintPrepareFeature',id=n+'Calc',text='function '+n+'Calc (long amount) -> long {}',implementation=n+'Copy',graphPath='Copy.graph.json',nodePath='Copy.node.json')
defs=metadata('featureBlueprintNodes',featureSource=items['Calc'][1],graph=prepared['graph'])
record={'schema':1,'node':'body','definitionHash':defs['nodes'][0]['definitionHash'],'source':'return amount;'}
prepared=metadata('blueprintPrepareCall',id=n+'Copy',text=prepared['implementation'],targetText=callee_text,graph=prepared['graph'],definition={'id':'native','feature':callee,'intent':'기존 호출 계약 갱신','control':'next'})
g=prepared['graph'];g['profile']='sync-acyclic-switch-v1';node=next(v for v in g['nodes'] if v['id']=='native');node['arguments']={'amount':{'input':'amount'}};g['entry']='native';g['edges'].append({'from':'native','port':'next','to':'body'});next(v for v in g['nodes'] if v['id']=='body')['arguments']={'amount':{'node':'native'}}
enum={'primary':'next','members':[{'id':'next','name':'NoBranch','value':0}]}
wrapper=metadata('blueprintCallWrapper',functionText=callee_text,executionEnum=enum,returnMapping='native-return-out-v1',source='return Result.NoBranch;')
node.update(control='switch',executionEnum=enum,postCall={'mode':'execution-enum','returnMapping':'native-return-out-v1','contractHash':wrapper['contractHash'],'source':wrapper['source'],'helpers':''})
if nested:
 child={'schema':1,'profile':'sync-acyclic-switch-v1','entry':'native','nodes':[__import__('copy').deepcopy(node)],'edges':[{'from':'native','port':'next','to':'exit:return'}],'exits':{'return':{'node':'native'}},'locals':[{'id':'kept','name':'정확한 값','type':'long','initial':{'constant':9223372036854775806}}]};body_node=next(v for v in g['nodes'] if v['id']=='body');body_node['arguments']={'amount':{'node':'frame'}};g.update(profile='sync-acyclic-nested-v1',entry='frame',nodes=[{'id':'frame','kind':'graph','control':'next','intent':'기존 내부 호출','signature':{'args':[{'name':'amount','type':'long'}],'return':'long'},'arguments':{'amount':{'input':'amount'}},'graph':child},*[v for v in g['nodes'] if v['id']!='native']],edges=[{**e,'from':'frame' if e['from']=='native' else e['from']} for e in g['edges']])
 if closure:
  second=__import__('copy').deepcopy(g['nodes'][0]);second['id']='other';second['intent']='다른 frame의 기존 호출';second['arguments']={'amount':{'node':'frame'}};g['nodes'].insert(1,second);next(v for v in g['nodes'] if v['id']=='body')['arguments']={'amount':{'node':'other'}};g['edges']=[{'from':'frame','port':'next','to':'other'},{'from':'other','port':'next','to':'body'},{'from':'body','port':'next','to':'exit:return'}]
 assert metadata('featureBlueprintDescribe',featureSource=items['Calc'][1],graph=g,featureContracts={callee:callee_text},implementations={'body':record})['state']=='source-ready'
current_signature={'args':[{'type':'int','name':'step'},{'type':'double','name':'renamed'},{'type':'long','name':'total','mode':'out'}],'return':'bool'} if general else {'args':[{'type':'long','name':'amount'}],'return':'long'}
current_text=callee_text.replace('(ref long amount) -> long','(int step,double renamed,out long total) -> bool' if general else '(long amount) -> long')
explicit_remap={'inputs':{'step':{'valueJson':'3'},'renamed':'amount'},'outputs':{'return':'total'}}
items['Copy']=('implementation',prepared['implementation'])
for key in ['Native','NativeBody']:items[key]=(items[key][0],items[key][1].replace('(ref long amount) -> long','(int step,double renamed,out long total) -> bool' if general else '(long amount) -> long'))
# The saved independent donor/copy snapshot predates the callee ABI change.
# This is not a claim that the new-copy API already supports wrapped graphs.
provenance={'implementation':n+'Donor','target':'common','bodyOrigin':n+'Donor','sourceKind':'blueprint'}
donor=__import__('copy').deepcopy(g);next(v for v in donor['nodes'] if v['id']=='body')['implementation']='Donor.node.json';items['Donor']=('implementation',prepared['implementation'].replace(n+'Copy',n+'Donor').replace('Copy.graph.json','Donor.graph.json'));g['copySource']=provenance
# The donor has independently adopted the current ABI; the saved copy still
# carries its older snapshot. The product repair must never rewrite the donor.
if 'stale-donor' not in sys.argv[3:]:
 current_wrapper=metadata('blueprintCallWrapper',functionText=current_text,executionEnum=enum,returnMapping='native-return-out-v1',source=wrapper['source'])
 if closure:
  query={'id':n+'Donor','text':items['Donor'][1],'graph':donor,'functionText':items['Calc'][1],'feature':callee,'featureContracts':{callee:current_text},'records':{'body':record}}
  preview=metadata('blueprintCallAbiUses',**query);plans=preview['plans']
  for key,value in plans.items():value['remap']=__import__('copy').deepcopy(explicit_remap);value['remap']['inputs']['step']['valueJson']='5' if key.startswith('other/') else '3'
  current_donor=metadata('blueprintCallAbiUses',**query,binding=preview['binding'],plans=plans)
 else:
  current_donor=metadata('blueprintCallAbi',id=n+'Donor',text=items['Donor'][1],graph=donor,node='native',signature=current_signature,contractHash=current_wrapper['contractHash'],**({'privatePath':'frame'} if nested else {}),**({'remap':explicit_remap} if general else {}))
 items['Donor']=('implementation',current_donor['implementation']);donor=current_donor['graph']
sources={'Donor.graph.json':json.dumps(donor),'Donor.node.json':json.dumps(record),'Main.csbody':'return checked((int)calls.Chosen.Invoke(1));','Other.csbody':'return amount+8;','Native.csbody':'total=checked((long)renamed);return step>0;' if general else 'return amount+3;','Copy.graph.json':json.dumps(g),'Copy.node.json':json.dumps(record)}
for name,(kind,text) in items.items():sources[name+'.celem']=text
sources['project.cproj']='project Owned.Context version "1" {standalone true;entry '+n+'Main;'+''.join('element '+name+' '+kind+' "'+name+'.celem";' for name,(kind,text) in items.items())+'registry Confectory.Build.DotNet "'+str(repo/'targets/dotnet/pack.cpack')+'";dependency Confectory.Build.DotNet version "0.1.0";target portable Confectory.Build.DotNet::Portable;target linux Confectory.Build.DotNet::Linux;}'
if registered:sources['project.cproj']=sources['project.cproj'].replace('registry Confectory.Build.DotNet', 'registry Lib \"../Lib/pack.cpack\";dependency Lib version \"1\";registry Confectory.Build.DotNet')
foreign_original={p:p.read_bytes() for p in lib.iterdir()} if registered else {}
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
def unchanged():
 assert all((project/k).read_bytes()==v for k,v in original.items())
 assert all(p.read_bytes()==v for p,v in foreign_original.items())
def setup(browser):
 page=browser.new_page(viewport={'width':2300,'height':1700} if is_view else {'width':1480,'height':1050});page.on('pageerror',lambda e:errors.append(str(e)))
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
 if is_view:
  global primary_text
  call('select',{'id':n+'B'});call('saveDraft',{});primary_text=state()['draft']['text']
  call('openEditorView',{'view':'1','id':n+'A','viewMode':'properties'});w=page.locator('.window[data-key=editor-1]');expect(w.locator('.object-title-name')).to_have_text('A')
 else:
  open_row('A','concept');w=page.locator('.window[data-key=schema]')
 slot=w.locator('[data-module-method="'+n+'Calc"]');expect(slot.locator('[data-function-edit]')).to_be_enabled();slot.locator('[data-function-edit]').click();a=page.locator('.window[data-key=blueprint]');expect(a).to_have_attribute('data-blueprint-owner',n+'A');expect(a).to_have_attribute('data-blueprint-body',n+'Copy/body:common');idle()
 if nested:
  a.locator('[data-bp-overview-node=frame]').click();a.locator('[data-bp-node=frame] [data-function-write-direct]').click();expect(a.locator('[data-bp-node=native]')).to_be_visible();pending()
 return a
def view_basis():
 if not is_view:return {}
 row=next(r for r in state()['editorViews'] if r['view']=='1');return {'view':'1','viewBinding':row['authorBinding']}
# Pure receipt tests: the helper verifies source ownership and exact shape, no I/O.
receipt_request={'id':n+'Copy','text':prepared['implementation'],'implementationPath':'Copy.celem','functionText':items['Calc'][1],'graphId':n+'Copy/body:common','graphPath':'Copy.graph.json','graph':g,'owner':n+'A','ownerText':items['A'][1],'objects':[{'id':n+k,'path':k+'.celem','text':v[1]} for k,v in items.items() if v[0] in ['object','schema']],'requirements':[{'function':n+'Calc','signature':{'Args':[{'Type':'long','Name':'amount'}],'return':'long'},'moduleSignature':{'Args':[{'Type':'long','Name':'arg0'}],'return':'long'}}],'providers':[{'function':n+'Calc','implementation':n+'Copy','origin':n+'A','contract':{'status':'valid'}}]}
proof=metadata('blueprintCopyAbiBinding',**receipt_request);assert proof['provenance']==provenance and proof['target']=='common'
for boundary in ['target','path','multi-target','provenance','unit-provenance','external-owner','shared-owner','no-requirement','invalid-provider','external-function']:
 r=__import__('copy').deepcopy(receipt_request)
 if boundary=='target':r['graphId']=n+'Copy/body:windows'
 elif boundary=='path':r['graphPath']='Donor.graph.json'
 elif boundary=='multi-target':r['text']=r['text'].replace('blueprint common','body windows "Other.csbody";blueprint common')
 elif boundary=='provenance':r['graph']['copySource']['implementation']=n+'Copy'
 elif boundary=='unit-provenance':r['unitProvenance']={**provenance,'target':'windows'}
 elif boundary=='external-owner':r['owner']='Other.Namespace::A'
 elif boundary=='shared-owner':r['objects'][1]['text']=r['objects'][1]['text'].replace(n+'Other',n+'Copy')
 elif boundary=='no-requirement':r['requirements']=[]
 elif boundary=='invalid-provider':r['providers'][0]['contract']['status']='invalid'
 else:r['functionText']=r['functionText'].replace(n+'Calc','External.Pack::Calc')
 result=subprocess.run([env['CONFECTORY_DOTNET'],str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps({'operation':'blueprintCopyAbiBinding',**r}),text=True,capture_output=True,env=env,check=True);assert not json.loads(result.stdout)['ok'],boundary
checked('단일 저장 복사본 receipt를 준비하고 대상·locator·다중본문·출처·공유소유·요구계약 위조 10종을 거절한다')
def read_copy():return call('blueprint',{'action':'read','id':n+'Copy/body:common'+('/graph:frame' if nested else ''),'owner':n+'A','ownerHash':hashlib.sha256((project/'A.celem').read_bytes()).hexdigest(),**view_basis()})
def batch(data,plan):return {'action':'authorBatch','id':data['id'],'attempt':uuid.uuid4().hex,'checkpointHash':data['checkpointHash'],'sourceProof':json.dumps(sorted([[v['id'],v['revision'],v['hash']] for v in data['sources']])),'edits':[{'action':'rebindCopyAbi','node':'native','definition':plan}],'owner':n+'A','ownerHash':hashlib.sha256((project/'A.celem').read_bytes()).hexdigest(),**view_basis()}
if 'metadata-only' in sys.argv[3:]:
 assert closure
 query={'id':n+'Copy','text':items['Copy'][1],'graph':g,'functionText':items['Calc'][1],'feature':callee,'featureContracts':{callee:current_text},'records':{'body':record}}
 preview=metadata('blueprintCallAbiUses',**query);assert set(preview['plans'])=={'frame/native','other/native'};plans=__import__('copy').deepcopy(preview['plans'])
 for key,value in plans.items():value['remap']=__import__('copy').deepcopy(explicit_remap);value['remap']['inputs']['step']['valueJson']='5' if key.startswith('other/') else '3'
 candidate=metadata('blueprintCallAbiUses',**query,binding=preview['binding'],plans=plans);unchanged()
 assert candidate['graph']['copySource']==provenance and candidate['uses']==['frame/native','other/native']
 for frame in candidate['graph']['nodes'][:2]:
  call_node=frame['graph']['nodes'][0];assert call_node['arguments']['step']=={'constant':5 if frame['id']=='other' else 3};assert frame['graph']['exits']['return']=={'node':'native','output':'total'};assert frame['graph']['locals'][0]['initial']['constant']==9223372036854775806
 checked('순수 closure는 같은 로컬 ID의 두 frame 대응·정확한 값·출처를 구분하고 공유 import를 한 후보로 갱신한다')
 wide=__import__('copy').deepcopy(query);root_call=__import__('copy').deepcopy(g['nodes'][0]['graph']['nodes'][0]);wide['graph']['nodes'].insert(0,root_call);wide['graph']['profile']='sync-acyclic-switch-v1';wide['graph']['entry']='native';wide['graph']['nodes'][1]['arguments']['amount']={'node':'native'};wide['graph']['edges'].insert(0,{'from':'native','port':'next','to':'frame'})
 wide_preview=metadata('blueprintCallAbiUses',**wide);wide_plans=wide_preview['plans']
 for key,value in wide_plans.items():value['remap']=__import__('copy').deepcopy(explicit_remap)
 wide_result=metadata('blueprintCallAbiUses',**wide,binding=wide_preview['binding'],plans=wide_plans);assert len(wide_result['uses'])==3;assert wide_result['graph']['nodes'][1]['arguments']['amount']=={'node':'native','output':'total'}
 for frame in wide_result['graph']['nodes'][1:3]:assert frame['graph']['exits']['return']=={'node':'native','output':'total'}
 unchanged();checked('Root와 private의 동일 로컬 ID는 각 frame의 소비자만 대응하며 경계를 넘어 잘못 재연결하지 않는다')
 for mutation in ['missing','unknown','last-output','stale','path','unscoped']:
  q=__import__('copy').deepcopy(query);binding=__import__('copy').deepcopy(preview['binding']);bad=__import__('copy').deepcopy(plans)
  if mutation=='missing':del bad['other/native']
  elif mutation=='unknown':bad['foreign/native']=__import__('copy').deepcopy(bad['other/native'])
  elif mutation=='last-output':bad['other/native']['remap']['outputs']['return']='return'
  elif mutation=='stale':binding['graphHash']='0'*64
  elif mutation=='path':bad['other/native']['privatePath']='frame'
  else:
   result=subprocess.run([env['CONFECTORY_DOTNET'],str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps({'operation':'blueprintCallAbi','id':n+'Copy','text':items['Copy'][1],'graph':g,'privatePath':'frame','node':'native','signature':current_signature,'contractHash':current_wrapper['contractHash'],'remap':explicit_remap,'coordinatedUses':True}),text=True,capture_output=True,check=True);assert not json.loads(result.stdout)['ok'];continue
  result=subprocess.run([env['CONFECTORY_DOTNET'],str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps({'operation':'blueprintCallAbiUses',**q,'binding':binding,'plans':bad}),text=True,capture_output=True,check=True);assert not json.loads(result.stdout)['ok'],mutation;unchanged()
 checked('누락/추가/경로/오래된 closure·마지막 비호환 대응과 단일 API boolean 우회는 전체 거절하고 원본을 쓰지 않는다')
 print(json.dumps({'checks':checks,'actualEngine':False,'evidence':str(case)},ensure_ascii=False));sys.exit(0)
try:
 start(0)
 call('saveDraft',{})
 call('select',{'id':n+'A'});call('schema',{'id':n+'A'});(case/'schema.json').write_text(json.dumps(state().get('schema'),ensure_ascii=False))
 with sync_playwright() as p:
  expect.set_options(timeout=30000);browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=setup(browser);author=open_slot();card=author.locator('[data-bp-node=native]');refresh=card.locator('[data-wrapper-refresh]');data=read_copy();row=next(v for v in data['nodes'] if v['id']=='native');(case/'initial-read.json').write_text(json.dumps(data,ensure_ascii=False));assert row['callAbiAvailable'] and row['copyAbiBinding']['provenance']==provenance;expect(refresh).to_be_enabled();unchanged();checked('실제 직접 배치된 저장 복사본에만 기존 원본 계약 갱신 버튼을 연결하고 출처를 표시 데이터에 보존한다')
  # Root access without selected direct owner still cannot edit a copied body.
  root=call('blueprint',{'action':'read','id':n+'Copy/body:common'+('/graph:frame' if nested else '')});assert not next(v for v in root['nodes'] if v['id']=='native')['callAbiAvailable']
  author.locator(':scope > .window-title').click(position={'x':700,'y':12});author.locator('[data-bp-overview-node=native]').click();refresh.click()
  if general:
   def choose():
    form=page.locator('[data-abi-remap-accept]').locator('..').locator('..')
    for section in form.locator('[data-abi-target]').all():
     section.locator('[data-abi-input=step]').select_option('value');section.locator('[data-abi-value=step]').fill('5' if section.get_attribute('data-abi-target')=='other/native' else '3');section.locator('[data-abi-input=renamed]').select_option('pin:amount');section.locator('[data-abi-output=return]').select_option('return' if correction and not corrected and section.get_attribute('data-abi-target')=='other/native' else 'total')
    return form
   form=choose()
   page.screenshot(path=str(case/'private-mapping-dialog.png'))
   form.locator('[data-abi-remap-cancel]').click()
   assert not pending();unchanged()
   refresh.click();choose()
   assert any(v.get('type')=='abi-remap-form' for _,v in pending())
   page.close();stop();start(3);page=setup(browser)
   author=page.locator('.window[data-key=blueprint]')
   expect(author.locator('[data-bp-node=native]')).to_be_visible()
   # Complete the original cold workspace/view restoration before editing.
   pending();idle()
   author.locator(':scope > .window-title').click(position={'x':700,'y':12})
   author.locator('[data-bp-overview-node=native]').click()
   author.locator('[data-wrapper-refresh]').click()
   form=page.locator('[data-abi-remap-accept]').locator('..').locator('..')
   selected_form=form.locator('[data-abi-target="frame/native"]') if closure else form
   expect(selected_form.locator('[data-abi-value=step]')).to_have_value('3')
   expect(selected_form.locator('[data-abi-input=renamed]')).to_have_value('pin:amount')
   expect(selected_form.locator('[data-abi-output=return]')).to_have_value('total')
   selected_form.locator('[data-abi-value=step]').fill('3e')
   form.locator('[data-abi-remap-accept]').click()
   expect(form.locator('[data-abi-error]')).to_be_visible()
   page.screenshot(path=str(case/'invalid-before-flush.png'))
   assert not any(v.get('type')=='wrapper' for _,v in pending())
   page.screenshot(path=str(case/'invalid-after-flush.png'))
   expect(form.locator('[data-abi-error]')).to_be_visible()
   selected_form.locator('[data-abi-value=step]').fill('3')
   form.locator('[data-abi-remap-accept]').click()
   unchanged()
   checked('기존 내부 계약 갱신의 명시 대응 취소·불완전 값·cold 복원은 입력과 원문을 보존한다')
  held=pending();assert len(held)==1;plan=json.loads(held[0][1]['text']);assert not closure or plan['abi']['useGroup']==row['callAbiUseGroupBinding'] and set(plan['abi']['usePlans'])=={'frame/native','other/native'};assert plan['abi']['copyBinding']==row['copyAbiBinding'];assert not general or plan['abi']['remap']==explicit_remap;unchanged();page.screenshot(path=str(case/'copy-abi-explicit-refresh.png'));checked('명시적 갱신은 복사 소유자·target·출처와 원본 callee hash를 함께 초안에 고정하고 파일은 쓰지 않는다')
  if 'peer-input' in sys.argv[3:]:
   checkpoint=next(project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();author.locator('.bp-breadcrumbs button').first.click();expect(author.locator('[data-bp-node=body]')).to_be_visible();author.locator('[data-bp-overview-node=body]').click();author.locator('[data-bp-node=body] [data-inline-description]').fill('다른 frame의 보존할 입력');author.locator('[data-bp-overview-node=frame]').click();author.locator('[data-bp-node=frame] [data-function-write-direct]').click();expect(author.locator('[data-bp-node=native]')).to_be_visible();all_held=pending();assert any(v.get('type')=='intent' and v['text']=='다른 frame의 보존할 입력' for _,v in all_held);author.locator('[data-bp-save]').click();expect(page.get_by_role('status').last).to_contain_text('같은 구현의 이전 입력',timeout=30000);assert checkpoint.read_bytes()==before and dict(pending())==dict(all_held);unchanged();page.close();stop();start(1);page=setup(browser);author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-node=native]')).to_be_visible();assert dict(pending())==dict(all_held) and checkpoint.read_bytes()==before;unchanged();checked('다른 frame의 별도 입력이 있으면 ABI 저장을 전체 차단하고 두 문맥의 원문/계획을 cold 복원에서도 보존한다');browser.close();print(json.dumps({'checks':checks,'evidence':str(case)},ensure_ascii=False));sys.exit(0)
  if 'source-change' in sys.argv[3:]:
   checkpoint=next(project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();file=project/'Copy.node.json';record=json.loads(file.read_text());record['source']='return amount+9;';file.write_text(json.dumps(record));original[file.name]=file.read_bytes();mark=len(traffic);author.locator('[data-bp-save]').click()
   for _ in range(1800):
    requests=[r for r in traffic[mark:] if r['endpoint']=='blueprint' and r.get('input',{}).get('action')=='authorBatch'];refused=[results[r['requestId']] for r in requests if r['requestId'] in results and not results[r['requestId']].get('ok') and results[r['requestId']].get('error',{}).get('code')!='stale_revision']
    if refused:break
    page.wait_for_timeout(20)
   assert refused and checkpoint.read_bytes()==before;assert all(dict(pending()).get(k)==v for k,v in held);unchanged();page.close();stop();start(1);page=setup(browser);author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-node=native]')).to_be_visible();assert all(dict(pending()).get(k)==v for k,v in held);assert checkpoint.read_bytes()==before;unchanged();checked('실제 Root body source 변경은 같은 callee 계획이라도 전체 미적용하고 peer 원문·CP·원래 입력을 재시작에도 보존한다');browser.close();print(json.dumps({'checks':checks,'evidence':str(case)},ensure_ascii=False));sys.exit(0)
  if 'cancel' in sys.argv[3:]:
   author.locator('.bp-viewport').focus();page.keyboard.press('Control+z');assert pending()==[];unchanged();assert next(v for v in read_copy()['nodes'] if v['id']=='native')['signature']['args'][0].get('mode')=='ref';page.close();stop();start(1);page=setup(browser);author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled();assert not pending();assert next(v for v in read_copy()['nodes'] if v['id']=='native')['signature']['args'][0].get('mode')=='ref';unchanged();checked('명시적 갱신 Undo는 복사 ABI 입력만 취소하고 cold 재시작에서도 원본 계약·소스·다른 객체를 보존한다');assert not errors,errors;browser.close();print(json.dumps({'checks':checks,'evidence':str(case)},ensure_ascii=False));sys.exit(0)
  if 'storage' in sys.argv[3:]:
   checkpoint=next(project.glob('.confectory/edit-workspaces/*/draft.json'));before_bytes=checkpoint.read_bytes();before=read_copy();checkpoint.chmod(0o400);mark=len(traffic);author.locator('[data-bp-save]').click()
   for _ in range(1800):
    attempts=[r for r in traffic[mark:] if r['endpoint']=='blueprint' and r.get('input',{}).get('action')=='authorBatch'];refused=[results[r['requestId']] for r in attempts if r['requestId'] in results and not results[r['requestId']].get('ok') and results[r['requestId']].get('error',{}).get('code')!='stale_revision']
    if refused:break
    page.wait_for_timeout(20)
   assert refused,'missing real storage refusal';idle();assert checkpoint.read_bytes()==before_bytes;assert read_copy()['sources']==before['sources'];retained=dict(pending());assert all(retained.get(k)==v for k,v in held);unchanged();checkpoint.chmod(0o600);page.close();stop();start(1);page=setup(browser);author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled();retained=dict(pending());assert all(retained.get(k)==v for k,v in held);mark=len(traffic);author.locator('[data-bp-save]').click();completed('blueprint','authorBatch',mark);assert pending()==[];assert not next(v for v in read_copy()['nodes'] if v['id']=='native')['postCallStale'];unchanged();checked('실제 checkpoint 쓰기 거절은 복사 선언/import/graph 전체를 미적용하고 입력을 보존하며 cold 재시도는 한 번만 저장한다');assert not errors,errors;browser.close();print(json.dumps({'checks':checks,'evidence':str(case)},ensure_ascii=False));sys.exit(0)
  if 'conflict' in sys.argv[3:]:
   # Existing peer edit is intentionally kept: no new-baseline automatic retry.
   before=read_copy();call('select',{'id':n+'B'});peer_basis=state()['draft'];call('editDeclaration',{'id':n+'B','revision':peer_basis['revision'],'hash':hashlib.sha256(peer_basis['text'].encode()).hexdigest(),'edit':{'action':'properties','values':{'description':'동료 편집자의 보관 설명'}}});call('saveDraft',{});peer_text=state()['draft']['text'];peer=read_copy();mark=len(traffic);author.locator('[data-bp-save]').click()
   for _ in range(1800):
    attempts=[r for r in traffic[mark:] if r['endpoint']=='blueprint' and r.get('input',{}).get('action')=='authorBatch'];refused=[results[r['requestId']] for r in attempts if r['requestId'] in results and not results[r['requestId']].get('ok') and results[r['requestId']].get('error',{}).get('code')!='stale_revision']
    if refused:break
    page.wait_for_timeout(20)
   assert refused,'missing actual stale checkpoint refusal';idle();retained=dict(pending());assert all(retained.get(k)==v for k,v in held);after=read_copy();assert after['sources']==peer['sources'] and after['checkpointHash']==peer['checkpointHash'];call('select',{'id':n+'B'});assert state()['draft']['text']==peer_text;assert next(v for v in after['nodes'] if v['id']=='native')['signature']['args'][0].get('mode')=='ref';unchanged();page.close();stop();start(1);page=setup(browser);author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled();retained=dict(pending());assert all(retained.get(k)==v for k,v in held);assert read_copy()['checkpointHash']==peer['checkpointHash'];unchanged();checked('실제 peer Save 이후 오래된 복사 ABI 저장은 CAS로 전체 거절하고 두 입력·기존 checkpoint를 cold 복원에서도 보존한다');assert not errors,errors;browser.close();print(json.dumps({'checks':checks,'evidence':str(case)},ensure_ascii=False));sys.exit(0)
  if 'response-loss' in sys.argv[3:]:
   ids=set();lost={}
   def intercept(route):
    body=route.request.post_data_json
    if body.get('op')=='invoke' and body.get('endpoint')=='blueprint' and body.get('input',{}).get('action')=='authorBatch':ids.add(body['requestId'])
    response=route.fetch();payload=response.json()
    if not lost and body.get('op')=='update' and any(v.get('requestId') in ids for v in payload.get('results',[])):
     assert all(v.get('ok') for v in payload['results'] if v.get('requestId') in ids);payload['results']=[{'requestId':v['requestId'],'ok':False,'error':{'code':'transport-interrupted'}} if v.get('requestId') in ids else v for v in payload['results']];lost['changed']=True;route.fulfill(response=response,json=payload);return
    route.fulfill(response=response)
   page.route('**/api/request',intercept);author.locator('[data-bp-save]').click()
   for _ in range(1800):
    if lost:break
    page.wait_for_timeout(20)
   assert lost,'missing real successful reply to lose';idle();page.unroute('**/api/request',intercept);assert pending()==[];saved=read_copy();assert not next(v for v in saved['nodes'] if v['id']=='native')['postCallStale'];checkpoint=saved['checkpointHash'];page.close();stop();start(1);page=setup(browser);author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled();assert not pending();assert read_copy()['checkpointHash']==checkpoint;unchanged();checked('실제 성공 응답을 유실해도 복사 ABI receipt가 완료를 확인하며 cold 복원에 중복·부분 저장이나 재전송 입력을 남기지 않는다');assert not errors,errors;browser.close();print(json.dumps({'checks':checks,'evidence':str(case)},ensure_ascii=False));sys.exit(0)
  if correction:
   checkpoint=next(project.glob('.confectory/edit-workspaces/*/draft.json'));before_rejection=checkpoint.read_bytes();mark=len(traffic);author.locator('[data-bp-save]').click()
   for _ in range(1800):
    requests=[r for r in traffic[mark:] if r['endpoint']=='blueprint' and r.get('input',{}).get('action')=='authorBatch'];refused=[results[r['requestId']] for r in requests if r['requestId'] in results and not results[r['requestId']].get('ok') and results[r['requestId']].get('error',{}).get('code')!='stale_revision']
    if refused:break
    page.wait_for_timeout(20)
   assert refused and checkpoint.read_bytes()==before_rejection;unchanged();failed=pending();old_attempt=next(v for _,v in failed if v.get('kind')=='author-attempt');assert next(v for v in read_copy()['nodes'] if v['id']=='native')['signature']['args'][0].get('mode')=='ref'
   author.locator('.bp-viewport').focus();page.keyboard.press('Control+z');corrected=True;author.locator('[data-wrapper-refresh]').click();choose().locator('[data-abi-remap-accept]').click();held=pending();plan=json.loads(next(v['text'] for _,v in held if v.get('type')=='wrapper'));assert plan['abi']['usePlans']['other/native']['remap']['outputs']['return']=='total';assert next(v for _,v in held if v.get('kind')=='author-attempt')==old_attempt;assert checkpoint.read_bytes()==before_rejection;unchanged();checked('마지막 호출 거절 후 실제 Undo와 새 명시 대응은 미적용 기록·원래 기준을 보존하며 올바른 전체 후보로 재시도한다')
  # Client cannot downgrade to legacy action or forge copy evidence.
  base=batch(read_copy(),plan)
  mutations=['legacy','no-binding','target','donor','no-owner','mixed']+(['private-path','private-graph'] if nested else [])+(['unmapped-output','incompatible-output','missing-input'] if general else [])+(['missing-use','unknown-use','wrong-use-path','stale-use-group','bad-last-output'] if closure else [])
  for mutation in mutations:
   b=__import__('copy').deepcopy(base);b['attempt']=uuid.uuid4().hex;checkpoint=next(project.glob('.confectory/edit-workspaces/*/draft.json'));checkpoint_bytes=checkpoint.read_bytes()
   if mutation=='legacy':b['edits'][0]['action']='rebindCallAbi'
   elif mutation=='no-binding':del b['edits'][0]['definition']['abi']['copyBinding']
   elif mutation=='target':b['edits'][0]['definition']['abi']['copyBinding']['target']='windows'
   elif mutation=='donor':b['edits'][0]['definition']['abi']['copyBinding']['provenance']['implementation']=n+'Other'
   elif mutation=='no-owner':del b['owner'];del b['ownerHash']
   elif mutation=='unmapped-output':b['edits'][0]['definition']['abi']['remap']['outputs']['return']=None
   elif mutation=='incompatible-output':b['edits'][0]['definition']['abi']['remap']['outputs']['return']='return'
   elif mutation=='missing-input':del b['edits'][0]['definition']['abi']['remap']['inputs']['renamed']
   elif mutation=='missing-use':del b['edits'][0]['definition']['abi']['usePlans']['other/native']
   elif mutation=='unknown-use':b['edits'][0]['definition']['abi']['usePlans']['foreign/native']=__import__('copy').deepcopy(plan['abi']['usePlans']['other/native'])
   elif mutation=='wrong-use-path':b['edits'][0]['definition']['abi']['usePlans']['other/native']['privatePath']='frame'
   elif mutation=='stale-use-group':b['edits'][0]['definition']['abi']['useGroup']['graphHash']='0'*64
   elif mutation=='bad-last-output':b['edits'][0]['definition']['abi']['usePlans']['other/native']['remap']['outputs']['return']='return'

   elif mutation=='private-path':b['edits'][0]['definition']['abi']['copyBinding']['privatePath']='other'
   elif mutation=='private-graph':b['edits'][0]['definition']['abi']['copyBinding']['privateGraph']=n+'Copy/body:common/graph:other'
   else:b['edits'].append({'action':'intent','node':'native','text':'not silently mixed'})
   call('blueprint',b,False);unchanged();assert pending()==held and checkpoint.read_bytes()==checkpoint_bytes
  checked('legacy 우회·binding/경로 누락·위조·소유자 누락·혼합 요청은 전체 미적용이고 UI 입력과 donor를 보존한다 ('+str(len(mutations))+'건)')
  if is_view:
   for mutation in ['nonce','view','owner']:
    b=__import__('copy').deepcopy(base);b['attempt']=uuid.uuid4().hex
    if mutation=='nonce':b['viewBinding']='stale-binding'
    elif mutation=='view':b['view']='2'
    else:b['owner']=n+'B'
    call('blueprint',b,False);unchanged();assert pending()==held
   checked('독립 정보 창은 현재 owner·nonce·문서 문맥만 허용하고 타창/타owner/이전binding 요청을 전체 거절한다')
  # A rejected compiler review cannot bypass technical contract validation.
  page.close();stop();start(1);page=setup(browser);author=page.locator('.window[data-key=blueprint]');expect(author).to_have_attribute('data-blueprint-owner',n+'A');expect(author.locator('[data-bp-save]')).to_be_enabled();assert pending()==held;unchanged();checked('저장 전 명시적 copy ABI 초안은 cold 재시작에서 소유자·출처·대상과 함께 복원한다')
  mark=len(traffic);author.locator('[data-bp-save]').click();completed('blueprint','authorBatch',mark);assert pending()==[];unchanged();saved=read_copy();node=next(v for v in saved['nodes'] if v['id']=='native');assert node['signature']['args'][0].get('mode') is None and not node['postCallStale'];assert node['copyAbiBinding']==row['copyAbiBinding'];assert saved['slotContext']['copySource']==provenance
  if nested:
   assert saved['locals'][0]['initialJson']=='9223372036854775806' and saved['edges']==g['nodes'][0]['graph']['edges'];assert row['copyAbiBinding']['privatePath']=='frame' and row['copyAbiBinding']['privateGraph']==data['id'];assert row['copyAbiBinding']['graph']==data['rootId']
  if is_view:assert state()['draft']['id']==n+'B' and state()['draft']['text']==primary_text;checked('독립 창 private ABI 저장은 다른 primary 문서와 원문을 변경하지 않는다')
  checked('한 authorBatch 후보/CAS에서 복사본 typed import·wrapper·graph만 저장하고 출처·객체·donor 파일은 유지한다')
  accepted=next(r['input'] for r in traffic[mark:] if r['endpoint']=='blueprint' and r.get('input',{}).get('action')=='authorBatch' and results.get(r['requestId'],{}).get('ok'));replay=call('blueprint',{**accepted,'action':'settledAuthorBatch',**view_basis()});assert replay['settled'];again=call('blueprint',{**accepted,**view_basis()});assert again['settled'];unchanged();assert not pending();checked('동일 attempt 재조회·재시도는 receipt로 이미 저장한 결과를 확인하며 중복 변경하지 않는다')
  page.close();stop();start(2);page=setup(browser);author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled();assert not pending();saved=read_copy();assert saved['slotContext']['copySource']==provenance;author.locator('[data-bp-complete]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=60000);assert state()['review']['status']=='ready';review.locator('[data-reject]').click();expect(review).to_be_hidden();unchanged();checked('저장된 복사 ABI cold 복원·컴파일 Review와 취소는 원본 파일을 보존한다')
  author.locator('[data-bp-complete]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=60000)
  if review.locator('[data-review-advanced]').count():
   review.locator('[data-review-advanced]').click()
   if review.locator('[data-advanced-reviewed]').count():review.locator('[data-advanced-reviewed]').check()
  mark=len(traffic);review.locator('#confirm').click();result=completed('confirmGroup',None,mark)
  if 'stale-donor' in sys.argv[3:]:
   assert not result['result'].get('sourceConfirmed');unchanged();assert any('CONTRACT_MISMATCH' in v for v in state()['logs']);assert not next(v for v in read_copy()['nodes'] if v['id']=='native')['postCallStale'];checked('다른 donor 자체가 오래된 계약이면 compiler Confirm은 안전하게 거절하고 원본을 자동 수정하거나 복사 저장 초안을 버리지 않는다');assert not errors,errors;browser.close();print(json.dumps({'checks':checks,'evidence':str(case)},ensure_ascii=False));sys.exit(0)
  if is_view:assert state()['draft']['id']==n+'B' and state()['draft']['text']==primary_text
  assert result['result'].get('sourceConfirmed');expect(review).to_have_count(0,timeout=90000);changed={k for k,v in original.items() if (project/k).read_bytes()!=v};assert changed=={'Copy.celem','Copy.graph.json'},changed;assert json.loads((project/'Copy.graph.json').read_text())['copySource']==provenance
  if nested:
   expected=__import__('copy').deepcopy(g)
   for frame in expected['nodes'][:2 if closure else 1]:
    leaf=frame['graph']['nodes'][0];leaf['signature']=plan['abi']['signature'];leaf['postCall']['contractHash']=plan['contractHash']
    if general:leaf['arguments']={'step':{'constant':5 if closure and frame['id']=='other' else 3},'renamed':{'input':'amount'}};frame['graph']['exits']['return']={'node':'native','output':'total'}
   assert json.loads((project/'Copy.graph.json').read_text())==expected
  checked('명시적 compiler Confirm은 Copy 선언과 graph만 반영하고 donor·callee·부모/다른 객체·원본 node 본문은 byte 보존한다')
  assert not errors and not external,(errors,external);page.close();browser.close()
except Exception:
 try:page.screenshot(path=str(case/'failure.png'))
 except Exception:pass
 try:(case/'failure-state.json').write_text(json.dumps({k:v for k,v in state().items() if k in ['review','sourceError','logs','operationError']},ensure_ascii=False,indent=2))
 except Exception:pass
 (case/'transport.json').write_text(json.dumps({'traffic':traffic,'results':results},ensure_ascii=False,indent=2));(case/'failure.json').write_text(json.dumps({'checks':checks,'errors':errors,'external':external,'evidence':str(case)},ensure_ascii=False,indent=2));print('EVIDENCE '+str(case),flush=True);raise
finally:stop()
record={'checks':checks,'actualEngine':True,'nativeWindows':False,'accountOrInference':False,'projectRun':False,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False,indent=2))
