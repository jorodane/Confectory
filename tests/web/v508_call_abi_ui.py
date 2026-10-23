"""Actual explicit callee ABI repair on the original refresh/C# modal; isolated coherent source update.
Save/Cancel/cold/Confirm and genuine-source-change guards; no account or inference.
"""
import json,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());kind=sys.argv[4];assert kind in ('bool','string','array');native_type={'bool':'bool','string':'string','array':'long[]'}[kind];fixture=pathlib.Path(sys.argv[3]).resolve();assert fixture==repo.parent/'scratch/v508-elements/actual13-source-fixture'
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

def sdk(operation,**body):
 p=subprocess.run([env['CONFECTORY_DOTNET'],str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps({'operation':operation,**body}),text=True,capture_output=True,env=env,check=True);v=json.loads(p.stdout);assert v['ok'],v;return v['result']
# Isolated real source contracts: each return retains its own consuming original field.
signature='(ref long seed,out long count,out bool active) -> '+native_type
nativefn='function Owned.Elements::NativeTyped '+signature+' {value blueprintPublishedOutputs = '+json.dumps(json.dumps(['return','count','active']))+';provide Owned.Elements::NativeTyped with Owned.Elements::NativeTypedBody;}'
(project/'elements/NativeTyped.celem').write_text(nativefn);(project/'elements/NativeTypedBody.celem').write_text('implementation Owned.Elements::NativeTypedBody for Owned.Elements::NativeTyped '+signature+' {body common "NativeTyped.csbody";}');ret={'bool':'true','string':json.dumps('한글 "반환" 😀',ensure_ascii=False),'array':'new long[]{9223372036854775700L}'}[kind];(project/'NativeTyped.csbody').write_text('seed+=1;count=9223372036854775700L;active=true;return '+ret+';');m=project/'project.cproj';t=m.read_text();i=t.rfind('}');m.write_text(t[:i]+'element NativeTyped function "elements/NativeTyped.celem";element NativeTypedBody implementation "elements/NativeTypedBody.celem";'+t[i:])
graphfile=next((project/'blueprints').glob('*.graph.json'));graphjson=json.loads(graphfile.read_text());implfile=project/'elements/SerialBlueprintBody.celem';callid='native_typed';prepared=sdk('blueprintPrepareCall',id='Owned.Elements::SerialBlueprintBody',text=implfile.read_text(),targetText=nativefn,graph=graphjson,definition={'id':callid,'feature':'Owned.Elements::NativeTyped','intent':'Typed original ref and output reference','control':'next'});g=prepared['graph'];g['profile']='sync-acyclic-methods-v1';next(n for n in g['nodes'] if n['id']==callid)['arguments']={'seed':{'input':'seed'}};consumer=next(n for n in g['nodes'] if n['id']=='body')['arguments'];consumer['seed']={'node':callid,'output':'count'};consumer['flag']={'node':callid,'output':'active'};consumer[{'bool':'flag','string':'title','array':'values'}[kind]]={'node':callid};g['exits']['return']={'node':callid,'output':'count'};g['entry']=callid;g['edges'].append({'from':callid,'port':'next','to':'body'});expected_consumers=__import__('copy').deepcopy(consumer);old_enum={'primary':'next','members':[{'id':'next','name':'NoBranch','value':0},{'id':'done','name':'완료','value':1}]};old_wrapper=sdk('blueprintCallWrapper',functionText=nativefn,executionEnum=old_enum,returnMapping='native-return-out-v1',source='return Result.NoBranch;');native=next(n for n in g['nodes'] if n['id']==callid);native['control']='switch';native['executionEnum']=old_enum;native['postCall']={'mode':'execution-enum','returnMapping':'native-return-out-v1','contractHash':old_wrapper['contractHash'],'source':old_wrapper['source'],'helpers':''};g['profile']='sync-acyclic-switch-v1';implfile.write_text(prepared['implementation']);graphfile.write_text(json.dumps(g));(project/'elements/NativeTyped.celem').write_text(nativefn.replace('ref long seed','long seed'));provider=project/'elements/NativeTypedBody.celem';provider.write_text(provider.read_text().replace('ref long seed','long seed'));original={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file() and '.confectory' not in p.parts}


try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(0);page=setup()
  def idle():page.evaluate('async()=>await confectoryFlushPresentation()')
  def browse():
   page.locator('#workspace').click(button='right',position={'x':700,'y':300});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();return page.locator('.window[data-key^="browser:project:"]:visible')
  b=browse();b.locator('[data-tab=feature]').click();b.locator('[data-object="Owned.Elements::Main"]').get_by_role('button',name='정의 열기',exact=True).click();main=page.locator('.window[data-key=declaration]');expect(main.locator('[data-inline-description]')).to_be_visible(timeout=30000);b.locator('[data-close]').click();main.locator('[data-inline-description]').fill('ABI와 별개로 보존할 함수 입력');main.locator('[data-close]').click();idle()
  b=browse();b.locator('[data-tab=feature]').click();b.locator('[data-object="'+id+'"]').get_by_role('button',name='정의 열기',exact=True).click();b.locator('[data-close]').click();page.locator('.window[data-key=declaration] [data-function-write-direct]').click();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-node="'+callid+'"] [data-wrapper-refresh]')).to_be_enabled(timeout=30000);graphid=invoke('blueprint',{'action':'list','feature':id})['result']['result']['rows'][0]['id']
  def graph():return invoke('blueprint',{'action':'read','id':graphid})['result']['result']
  def actual():return next(n for n in graph()['nodes'] if n['id']==callid)
  def card():return author.locator('[data-bp-node="'+callid+'"]')
  def focus():author.locator('[data-bp-overview-node="'+callid+'"]').click()
  def dialog():focus();card().locator('[data-wrapper-edit]').click();return page.get_by_role('dialog',name='분기 기능 편집 · NativeTyped',exact=True)
  def edit(d,text,region='body'):
   code=d.locator('[data-code-source]');code.evaluate('(el,region)=>{const spans=[...el.closest(".bp-script-editor").querySelectorAll("[data-code-highlight]>span")],part=spans.find(p=>p.dataset.codeRegion===region);if(!part)throw Error("source region missing");const start=spans.slice(0,spans.indexOf(part)).reduce((n,p)=>n+p.textContent.length,0);el.setSelectionRange(start,start+part.textContent.length)}',region);page.keyboard.insert_text(text);return code
  def source(text):
   d=dialog();edit(d,text);d.locator('[data-code-save]').click();expect(d).to_have_count(0)
  def private():idle();return [(k,v) for k,v in state()['presentation']['inputs']['blueprint'] if v['type']=='wrapper']
  def save():author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_have_text('저장됨',timeout=30000)
  def confirm():
   author.locator('[data-bp-complete]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=30000)
   for cb in review.locator('[data-review-id]').all():cb.check()
   if review.locator('[data-additional-changes]').count():
    review.locator('[data-review-advanced]').click();ack=review.locator('[data-advanced-reviewed]')
    if ack.count():ack.check()
   expect(review.locator('#confirm')).to_be_enabled(timeout=30000);review.locator('#confirm').click();expect(review).to_have_count(0,timeout=60000);expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000)
  def originals():return all((project/k).read_bytes()==v for k,v in original.items())
  def consumers_preserved():
   saved=json.loads(graphfile.read_text());return next(n for n in saved['nodes'] if n['id']=='body')['arguments']==expected_consumers and saved['exits']['return']=={'node':callid,'output':'count'}
  def peers():return {k:v for k,v in state()['presentation']['inputs'].items() if k not in ('blueprint','target') and (k!='source' or v.get('dirty'))}
  idle();peer=peers();(case/'peer-before.json').write_text(json.dumps(peer,ensure_ascii=False,indent=2));n=actual();assert n['postCallStale'] and not n['postCallSignatureMatches'] and n['callAbiAvailable'] and n['signature']['args'][0]['mode']=='ref' and n['currentCallSignature']['args'][0].get('mode') is None and originals();focus();card().locator('[data-wrapper-refresh]').click();pending=private();v=json.loads(pending[0][1]['text']);assert v['abi']['signature']==n['currentCallSignature'] and v['abi']['sourceHash']==n['callAbiSourceHash'] and v['refreshFrom']==n['postCall']['contractHash'];author.locator('.bp-viewport').focus();page.keyboard.press('Control+z');assert private()==[] and originals();focus();card().locator('[data-wrapper-refresh]').click();pending=private();d=dialog();text=d.locator('[data-code-source]').input_value();assert 'Invoke(long @seed' in text and 'Invoke(ref long @seed' not in text;edit(d,'throw new System.Exception();');d.locator('[data-code-cancel]').click();assert private()==pending and originals() and peers()==peer;checked('coherent callee ABI change is readonly until original explicit refresh; Undo/modal Cancel retain prior caller import, wires, code and unrelated input')
  idle();page.close();stop();start(1);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);assert private()==pending and originals() and peers()==peer;d=dialog();edit(d,'if(context.@return[0]!=9223372036854775700L||context.@count!=9223372036854775700L||!context.@active)throw new System.Exception();return Result.NoBranch;');d.locator('[data-code-save]').click();save();now=actual();assert now['signature']['args'][0].get('mode') is None and now['postCallSignatureMatches'] and not now['postCallStale'] and originals() and peers()==peer;checkpoint=next(project.glob('.confectory/edit-workspaces/*/draft.json'));rows=json.loads(checkpoint.read_text())['changes'];impl=next(r for r in rows if r['id']=='Owned.Elements::SerialBlueprintBody')['draft'];assert '(long, out long, out bool)' in impl and '(ref long, out long, out bool)' not in impl;checked('private ABI plan survives cold restart; one checkpoint-bound batch saves matching caller typed import/call signature and reviewed context code together without physical source writes')
  confirm();after_peer=peers();(case/'peer-after.json').write_text(json.dumps(after_peer,ensure_ascii=False,indent=2));facts={'import': '(long, out long, out bool)' in implfile.read_text(),'node':next(n for n in json.loads(graphfile.read_text())['nodes'] if n['id']==callid)['signature']['args'][0].get('mode') is None,'peers':after_peer==peer,'nativeBody':(project/'NativeTyped.csbody').read_bytes()==original['NativeTyped.csbody'],'reviewTarget':state()['presentation']['inputs']['target']=='portable'};(case/'confirm-facts.json').write_text(json.dumps(facts));assert all(facts.values()),facts;idle();page.close();stop();start(2);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);assert not actual()['postCallStale'] and actual()['signature']['args'][0].get('mode') is None and peers()==peer;focus();d=dialog();assert 'context.@return[0]' in d.locator('[data-code-source]').input_value();d.locator('[data-code-cancel]').click();checked('actual compiler Review/explicit Confirm commits coherent ABI and consumer SourceContext reads; cold restore keeps its existing data/ref/out connections and other private edits')
  source('return Result.NoBranch; // ABI 변경에도 보관할 입력');retained=private();saved=graphfile.read_bytes();saved_impl=implfile.read_bytes();idle();page.close();stop();fnfile=project/'elements/NativeTyped.celem';fnfile.write_text(fnfile.read_text().replace('-> long[]','-> bool'));provider.write_text(provider.read_text().replace('-> long[]','-> bool'));(project/'NativeTyped.csbody').write_text('seed+=1;count=9223372036854775700L;active=true;return true;');start(3);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);bad=actual();assert bad['postCallStale'] and not bad['callAbiAvailable'] and not bad['postCallSignatureMatches'];focus();expect(card().locator('[data-wrapper-refresh]')).to_be_disabled();fresh=graph();evil={'source':'return Result.NoBranch;','helpers':'','executionEnum':bad['executionEnum'],'contractHash':bad['postCallEditor']['contractHash'],'returnMapping':'native-return-out-v1','refreshFrom':bad['postCall']['contractHash'],'abi':{'signature':bad['currentCallSignature'],'sourceHash':bad['callAbiSourceHash']}};proof=json.dumps(sorted([[r['id'],r['revision'],r['hash']] for r in fresh['sources']]),separators=(',',':'));before=checkpoint.read_bytes();invoke('blueprint',{'action':'authorBatch','id':graphid,'attempt':uuid.uuid4().hex,'checkpointHash':fresh['checkpointHash'],'sourceProof':proof,'edits':[{'action':'rebindCallAbi','node':callid,'definition':evil}]},False);assert checkpoint.read_bytes()==before and graphfile.read_bytes()==saved and implfile.read_bytes()==saved_impl and private()==retained and peers()==peer;checked('incompatible native return type disables original ABI refresh and a forged batch is refused with exact checkpoint/import/graph/pending input preservation')
  page.screenshot(path=str(case/'abi-incompatible-preserved.png'));page.close();browser.close();assert not errors and not external,(errors,external)
except Exception:
 try:(case/'failure-state.json').write_text(json.dumps(state(),ensure_ascii=False,indent=2));(case/'failure.json').write_text(json.dumps({'traffic':traffic,'errors':errors},indent=2));page.screenshot(path=str(case/'failure.png'))
 except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case));raise
finally:stop()
record={'checks':checks,'errors':errors,'external':external,'actualEngine':True,'calleeAbiUi':True,'scope':'one owned wrapped call, unchanged names/types/out/return, value-ref change','nativeWindows':False,'accountOrInference':False,'projectRun':False,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
