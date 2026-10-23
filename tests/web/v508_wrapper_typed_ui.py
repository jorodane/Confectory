"""Native typed return +ref/two-out wrapper and explicit enum receipt refresh on the original UI.
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
graphfile=next((project/'blueprints').glob('*.graph.json'));graphjson=json.loads(graphfile.read_text());implfile=project/'elements/SerialBlueprintBody.celem';callid='native_typed';prepared=sdk('blueprintPrepareCall',id='Owned.Elements::SerialBlueprintBody',text=implfile.read_text(),targetText=nativefn,graph=graphjson,definition={'id':callid,'feature':'Owned.Elements::NativeTyped','intent':'Typed original ref and output reference','control':'next'});g=prepared['graph'];g['profile']='sync-acyclic-methods-v1';next(n for n in g['nodes'] if n['id']==callid)['arguments']={'seed':{'input':'seed'}};consumer=next(n for n in g['nodes'] if n['id']=='body')['arguments'];consumer['seed']={'node':callid,'output':'count'};consumer['flag']={'node':callid,'output':'active'};consumer[{'bool':'flag','string':'title','array':'values'}[kind]]={'node':callid};g['exits']['return']={'node':callid,'output':'count'};g['entry']=callid;g['edges'].append({'from':callid,'port':'next','to':'body'});expected_consumers=__import__('copy').deepcopy(consumer);implfile.write_text(prepared['implementation']);graphfile.write_text(json.dumps(g));original={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file() and '.confectory' not in p.parts}

try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(0);page=setup()
  def idle():page.evaluate('async()=>await confectoryFlushPresentation()')
  def browse():
   page.locator('#workspace').click(button='right',position={'x':700,'y':300});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();return page.locator('.window[data-key^="browser:project:"]:visible')
  b=browse();b.locator('[data-object="Owned.Elements::Monster"]').get_by_role('button',name='정의 열기',exact=True).click();monster=page.locator('.window[data-key=schema]');expect(monster.locator('.object-title-description')).to_be_visible(timeout=30000);b.locator('[data-close]').click();monster.locator('.object-title-description').fill('후처리 코드와 다른 객체 입력');monster.locator('[data-close]').click();idle()
  b=browse();b.locator('[data-tab=feature]').click();b.locator('[data-object="'+id+'"]').get_by_role('button',name='정의 열기',exact=True).click();b.locator('[data-close]').click();page.locator('.window[data-key=declaration] [data-function-write-direct]').click();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-node="'+callid+'"] [data-bp-wrap-call]')).to_be_enabled(timeout=30000);graphid=invoke('blueprint',{'action':'list','feature':id})['result']['result']['rows'][0]['id']
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
  idle();peer=state()['presentation']['inputs']['schema'];n=actual();assert n['signature']['return']==native_type and [a.get('mode') for a in n['signature']['args']]==['ref','out','out'];assert json.loads(n['arguments'][0]['valueJson'])=={'input':'seed'};focus();expect(card().locator('.bp-port[data-side=out][data-kind=data]')).to_have_count(3);card().locator('[data-bp-wrap-call]').click();d=dialog();guard={'bool':'if(!context.@return)throw new System.Exception();','string':'if(context.@return!='+json.dumps('한글 "반환" 😀',ensure_ascii=False)+')throw new System.Exception();','array':'if(context.@return[0]!=9223372036854775700L)throw new System.Exception();'}[kind];wanted=guard+'return Result.분기1;';edit(d,wanted);d.locator('[data-code-save]').click();before=private();d=dialog();edit(d,'throw new System.Exception();');d.locator('[data-code-cancel]').click();assert private()==before and actual()['control']=='next' and originals();idle();page.close();stop();start(1);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);assert private()==before and state()['presentation']['inputs']['schema']==peer;checked(kind+': original typed data/ref/two-out pins, private wrapper Cancel and true restart preserve all input/consumers and source bytes')
  save();n=actual();assert n['signature']['return']==native_type and n['postCall']['returnMapping']=='native-return-out-v1' and n['postCall']['source']==wanted and originals();confirm();assert consumers_preserved() and (project/'elements/NativeTyped.celem').read_text()==nativefn and (project/'NativeTyped.csbody').read_bytes()==original['NativeTyped.csbody'];checked(kind+': real original Save/compiler Review/explicit Confirm retain native return/ref/two-out calling convention and pre-existing consumers')
  idle();page.close();stop();start(2);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);n=actual();assert n['signature']['return']==native_type and n['postCall']['source']==wanted and n['postCall']['returnMapping']=='native-return-out-v1' and consumers_preserved() and state()['presentation']['inputs']['schema']==peer;focus();expect(card().locator('.bp-port[data-side=out][data-kind=data]')).to_have_count(3);checked(kind+': confirmed typed wrapper/ref/two-out ports and consumers restore after a second real process restart')
  if kind=='array':
   source(wanted+'// 보존할 후속 입력');old_pending=private();old_shared=actual()['postCall'];invoke('select',{'id':'Owned.Elements::NativeTyped'});a=invoke('inspectDeclaration',{'id':'Owned.Elements::NativeTyped'})['state']['declaration'];invoke('editMetadata',{'id':a['id'],'revision':a['revision'],'hash':a['textHash'],'field':'blueprintPublishedOutputs','value':json.dumps(['count','active'])});inspected=graph();row=next(n for n in inspected['nodes'] if n['id']==callid);assert row['postCallStale'] and row['postCallSignatureMatches'] and [f['name'] for f in row['postCallEditor']['snapshot']['fields']]==['count','active'] and inspected['diagnostics']['state']=='invalid';invoke('blueprint',{'action':'wrapCall','id':graphid,'node':callid,'contractHash':row['postCallEditor']['contractHash'],'returnMapping':'native-return-out-v1','refreshFrom':'0'*64,'text':'return Result.NoBranch;','executionEnum':row['executionEnum'],'basis':inspected['basis']},False);assert private()==old_pending and actual()['postCall']==old_shared;invoke('saveDraft',{});idle();page.close();stop();start(3);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);focus();expect(card().locator('[data-wrapper-refresh]')).to_be_visible();expect(card().locator('[data-wrapper-refresh]')).to_be_enabled();assert private()==old_pending;checked('stale array enum wrapper is displayable with old input, rejects forged receipt and exposes original explicit refresh only for an unchanged native signature')
   card().locator('[data-wrapper-refresh]').click();staged=private();v=json.loads(staged[0][1]['text']);assert v['source']==wanted+'// 보존할 후속 입력' and v['executionEnum']==row['executionEnum'] and v['returnMapping']=='native-return-out-v1' and v['contractHash']!=old_shared['contractHash'] and v['refreshFrom']==old_shared['contractHash'];expect(card().locator('[data-wrapper-refresh]')).to_be_hidden();author.locator('.bp-viewport').focus();page.keyboard.press('Control+z');assert private()==old_pending;expect(card().locator('[data-wrapper-refresh]')).to_be_visible();focus();card().locator('[data-wrapper-refresh]').click();d=dialog();edit(d,'return Result.분기1;');assert 'public long[] @return { get;' not in d.locator('[data-code-source]').input_value();d.locator('[data-code-save]').click();save();confirm();assert consumers_preserved() and not actual()['postCallStale'] and state()['presentation']['inputs']['schema']==peer;checked('explicit enum refresh/Undo/manual code review/Save/Confirm keeps enum IDs, return mapping and all data consumers while removing only revoked context access')
   idle();page.close();stop();start(4);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);assert not actual()['postCallStale'] and consumers_preserved() and actual()['postCall']['returnMapping']=='native-return-out-v1' and state()['presentation']['inputs']['schema']==peer;checked('explicitly renewed enum wrapper and original data/ref/out consumers restore after cold restart with unrelated private input')
   source('return Result.분기1; // 전달 방식 변경 전 입력');pending=private();old=actual()['postCall'];saved_graph=graphfile.read_bytes();checkpoint=next(project.glob('.confectory/edit-workspaces/*/draft.json'));saved_checkpoint=checkpoint.read_bytes();native_bytes=(project/'elements/NativeTyped.celem').read_bytes();changed=__import__('copy').deepcopy(actual()['signature']);changed['args'][0].pop('mode');invoke('select',{'id':'Owned.Elements::NativeTyped'});a=invoke('inspectDeclaration',{'id':'Owned.Elements::NativeTyped'})['state']['declaration'];invoke('editFunctionContract',{'id':a['id'],'revision':a['revision'],'hash':a['textHash'],'edit':{'signature':changed}},False);n=actual();assert n['signature']['args'][0]['mode']=='ref' and n['postCallSignatureMatches'] and not n['postCallStale'] and n['postCall']==old and graphfile.read_bytes()==saved_graph and checkpoint.read_bytes()==saved_checkpoint and (project/'elements/NativeTyped.celem').read_bytes()==native_bytes and private()==pending and consumers_preserved();idle();page.close();stop();start(5);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);n=actual();focus();expect(card().locator('[data-wrapper-refresh]')).to_be_hidden();assert n['signature']['args'][0]['mode']=='ref' and not n['postCallStale'] and private()==pending and graphfile.read_bytes()==saved_graph and checkpoint.read_bytes()==saved_checkpoint and consumers_preserved() and state()['presentation']['inputs']['schema']==peer;checked('actual signature editor rejects an inconsistent ref-to-value declaration before mutation; native signature, saved checkpoint/graph, pending input and consumers survive true restart')

  focus();page.screenshot(path=str(case/('typed-'+kind+'-confirmed.png')));page.close();browser.close();assert not errors and not external,(errors,external)
except Exception:
 try:(case/'failure-state.json').write_text(json.dumps(state(),ensure_ascii=False,indent=2));(case/'failure.json').write_text(json.dumps({'traffic':traffic,'errors':errors},indent=2));page.screenshot(path=str(case/'failure.png'))
 except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case));raise
finally:stop()
record={'checks':checks,'errors':errors,'external':external,'actualEngine':True,'nativeReturn':native_type,'refAndTwoOut':True,'explicitEnumRefresh':kind=='array','nativeWindows':False,'accountOrInference':False,'projectRun':False,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
