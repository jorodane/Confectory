"""생산자 눈 버튼→소비자 계약 갱신→명시적 공동 확정의 격리 엔진 검증."""
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

def sdk(operation,**body):
 v=subprocess.run([env['CONFECTORY_DOTNET'],str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps({'operation':operation,**body}),text=True,capture_output=True,env=env,check=True);reply=json.loads(v.stdout);assert reply['ok'],reply;return reply['result']
producer='Owned.Elements::Serial';consumer='Owned.Elements::Consumer';producer_file=project/'elements/Serial.celem';producer_graph=next((project/'blueprints').glob('*.graph.json'));callid='producer_call'
signature='(long seed,long other,int narrow,string title,bool flag,long[] values) -> long'
created=sdk('blueprintPrepareFeature',id=consumer,text='function '+consumer+' '+signature+' {}',implementation='Owned.Elements::ConsumerBody',graphPath='blueprints/consumer.graph.json',nodePath='nodes/consumer-unused.node.json')
consumer_file=project/'elements/Consumer.celem';consumer_impl=project/'elements/ConsumerBody.celem';consumer_graph=project/'blueprints/consumer.graph.json'
g=created['graph'];g['nodes']=[];g['edges']=[];g['entry']='';g['exits']={'return':None}
prepared=sdk('blueprintPrepareCall',id='Owned.Elements::ConsumerBody',text=created['implementation'],targetText=producer_file.read_text(),graph=g,definition={'id':callid,'feature':producer,'intent':'생산자의 공개 출력을 읽는 소비자','control':'next'})
g=prepared['graph'];native=next(n for n in g['nodes'] if n['id']==callid);native['arguments']={p['name']:{'input':p['name']} for p in native['signature']['args']};native['control']='switch';enum={'primary':'next','members':[{'id':'next','name':'NoBranch','value':0},{'id':'done','name':'완료','value':1}]};native['executionEnum']=enum;wrapped=sdk('blueprintCallWrapper',functionText=producer_file.read_text(),executionEnum=enum,returnMapping='native-return-out-v1',source='return Result.NoBranch;');native['postCall']={'mode':'execution-enum','returnMapping':'native-return-out-v1','contractHash':wrapped['contractHash'],'source':wrapped['source'],'helpers':''};g['profile']='sync-acyclic-switch-v1';g['entry']=callid;g['edges']=[{'from':callid,'port':'next','to':'exit:return'}];g['exits']={'return':{'node':callid,'output':'return'}}
consumer_file.write_text(created['function']);consumer_impl.write_text(prepared['implementation']);consumer_graph.write_text(json.dumps(g));manifest=project/'project.cproj';t=manifest.read_text();i=t.rfind('}');manifest.write_text(t[:i]+'element Consumer function "elements/Consumer.celem";element ConsumerBody implementation "elements/ConsumerBody.celem";'+t[i:]);original={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file() and '.confectory' not in p.parts}

try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(0);page=setup()
  def idle():page.evaluate('async()=>await confectoryFlushPresentation()')
  def browse():
   page.locator('#workspace').click(button='right',position={'x':700,'y':300});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();return page.locator('.window[data-key^="browser:project:"]:visible')
  def open_feature(feature):
   w=page.locator('.window[data-key=blueprint]')
   if w.is_visible():w.locator(':scope > header [data-close]').click()
   b=browse();b.locator('[data-tab=feature]').click();b.locator('[data-object="'+feature+'"]').get_by_role('button',name='정의 열기',exact=True).click();b.locator('[data-close]').click();page.locator('.window[data-key=declaration] [data-function-write-direct]').click();w=page.locator('.window[data-key=blueprint]');expect(w.locator('[data-bp-save]')).to_be_enabled(timeout=30000);expect(w.locator('[data-bp-complete]')).to_be_enabled(timeout=30000);return w
  def read(feature):
   graphid=invoke('blueprint',{'action':'list','feature':feature})['result']['result']['rows'][0]['id'];return invoke('blueprint',{'action':'read','id':graphid})['result']['result']
  def call():return next(n for n in read(consumer)['nodes'] if n['id']==callid)
  def focus():
   author.locator('[data-bp-overview-node="'+callid+'"]').click();page.evaluate('()=>new Promise(requestAnimationFrame)')
  def card():return author.locator('[data-bp-node="'+callid+'"]')
  def reveal(button):
   vp=author.locator('.bp-viewport');box=vp.bounding_box();delta=button.evaluate('(el)=>{const a=el.getBoundingClientRect(),v=el.closest(".bp-viewport").getBoundingClientRect();return {x:a.x+a.width/2-v.x-v.width/2,y:a.y+a.height/2-v.y-v.height/2}}');page.mouse.move(box['x']+box['width']/2,box['y']+box['height']/2);page.mouse.wheel(delta['x'],delta['y']);page.evaluate('()=>new Promise(requestAnimationFrame)')
  def refresh():
   focus();button=card().locator('[data-wrapper-refresh]');reveal(button);button.click()
  def dialog():
   focus();button=card().locator('[data-wrapper-edit]');reveal(button);button.click();return page.get_by_role('dialog',name='분기 기능 편집 · Serial',exact=True)
  def edit(d,text):
   code=d.locator('[data-code-source]');code.evaluate('(el)=>{const spans=[...el.closest(".bp-script-editor").querySelectorAll("[data-code-highlight]>span")],part=spans.find(p=>p.dataset.codeRegion==="body");if(!part)throw Error("source region missing");const start=spans.slice(0,spans.indexOf(part)).reduce((n,p)=>n+p.textContent.length,0);el.setSelectionRange(start,start+part.textContent.length)}');page.keyboard.insert_text(text)
  def source(text):
   d=dialog();edit(d,text);d.locator('[data-code-save]').click();expect(d).to_have_count(0)
  def save():author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_have_text('저장됨',timeout=30000)
  def private():idle();return state()['presentation']['inputs']['blueprint']
  def originals():return all((project/k).read_bytes()==v for k,v in original.items())
  def peers():return {k:v for k,v in state()['presentation']['inputs'].items() if k not in ('blueprint','target') and (k!='source' or v.get('dirty'))}
  # 실제 원본 정의창의 독립 입력을 보존 대상으로 둔다.
  b=browse();b.locator('[data-tab=feature]').click();b.locator('[data-object="Owned.Elements::Main"]').get_by_role('button',name='정의 열기',exact=True).click();main=page.locator('.window[data-key=declaration]');expect(main.locator('[data-inline-description]')).to_be_visible(timeout=30000);b.locator('[data-close]').click();main.locator('[data-inline-description]').fill('공개 출력 흐름과 별개의 함수 입력');main.locator('[data-close]').click();idle();peer=peers()
  author=open_feature(producer);eye=author.locator('[data-output-exposed=return]');expect(eye).to_be_enabled();eye.click();expect(eye).to_have_attribute('aria-pressed','true');pending=private();author.locator('.bp-viewport').focus();page.keyboard.press('Control+z');expect(eye).to_have_attribute('aria-pressed','false');eye.click();assert private()==pending and originals() and peers()==peer;save();prod=read(producer);assert json.loads(prod['featureDefinition']['values']['blueprintPublishedOutputs'])==['return'];assert originals();checked('생산자의 원본 눈 버튼·취소 후 선택과 저장은 공개 출력만 초안에 반영하고 원본 파일과 다른 입력을 보존한다')
  author=open_feature(consumer);n=call();assert n['postCallStale'] and n['postCallSignatureMatches'];focus();expect(card().locator('[data-wrapper-refresh]')).to_be_enabled();old=n['postCall'];refresh();pending=private();d=dialog();assert 'public long @return { get; }' in d.locator('[data-code-source]').input_value();edit(d,'throw new System.Exception();');d.locator('[data-code-cancel]').click();assert private()==pending and call()['postCall']==old and peers()==peer;author.locator('.bp-viewport').focus();page.keyboard.press('Control+z');focus();expect(card().locator('[data-wrapper-refresh]')).to_be_enabled();refresh();source('if(context.@return==long.MinValue)throw new System.Exception();return Result.NoBranch;');pending=private();idle();page.close();stop();start(1);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);assert private()==pending and originals() and peers()==peer;save();assert not call()['postCallStale'] and originals();checked('소비자의 명시적 갱신·본문 편집·취소·재시작 후 저장에서 공개 SourceContext와 기존 연결·입력을 보존한다')
  def review_open():
   author.locator('[data-bp-complete]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=30000);actual_review=state()['review'];ids=[u['id'] for u in actual_review['units']];required=read(producer)['reviewIds'];assert set(required)<=set(ids) and 'Owned.Elements::ConsumerBody/body:common' in ids and 'Owned.Elements::Main' not in ids;assert set(required)<=set(actual_review['requiredIds']);return review
  def confirm(review):
   for cb in review.locator('[data-review-group]').all():cb.check()
   if review.locator('[data-additional-changes]').count():
    review.locator('[data-review-advanced]').click();ack=review.locator('[data-advanced-reviewed]')
    if ack.count():ack.check()
   expect(review.locator('#confirm')).to_be_enabled(timeout=30000);review.locator('#confirm').click();expect(review).to_have_count(0,timeout=60000)
  # 소비자만 지정한 위조/누락 검토는 기존 서버 보호가 계속 거부한다.
  current=read(consumer);omitted=[x['id'] for x in current['sources'] if x['id'] not in ('Owned.Elements::SerialBlueprintBody','Owned.Elements::SerialBlueprintBody/body:common')];invoke('reviewGroup',{'ids':omitted,'target':'portable'},False);assert originals() and peers()==peer
  review=review_open();(case/'review-state.json').write_text(json.dumps(state()['review'],ensure_ascii=False,indent=2));review.locator('[data-reject]').click();expect(review).to_have_count(0);assert originals() and peers()==peer;idle();page.close();stop();start(2);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);assert not call()['postCallStale'] and originals() and peers()==peer;checked('누락된 생산자 묶음의 검토는 서버가 거부하며, 실제 공동 검토 취소·재시작은 양쪽 저장 초안과 별개 입력을 보존한다')
  review=review_open();required=review.locator('[data-review-group]').first;required.uncheck();expect(review.locator('#confirm')).to_be_disabled();required.check();confirm(review);assert 'blueprintPublishedOutputs' in producer_file.read_text();assert 'context.@return' in next(n for n in json.loads(consumer_graph.read_text())['nodes'] if n['id']==callid)['postCall']['source'];assert peers()==peer;checked('생산자와 소비자의 실제 공동 컴파일 검토·명시적 확정이 공개 출력과 소비 코드를 함께 반영한다')
  expected_args=json.loads(consumer_graph.read_text())['nodes'][0]['arguments'];expected_routes=json.loads(consumer_graph.read_text())['edges'];physical_consumer=consumer_graph.read_bytes();idle();page.close();stop();start(3);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);assert not call()['postCallStale'] and peers()==peer;source('if(context.@return==long.MinValue)throw new System.Exception();return Result.NoBranch; // 철회해도 보관할 소비자 입력');pending=private()
  author=open_feature(producer);eye=author.locator('[data-output-exposed=return]');expect(eye).to_have_attribute('aria-pressed','true');eye.click();expect(eye).to_have_attribute('aria-pressed','false');save();author=open_feature(consumer);n=call();assert n['postCallStale'] and n['postCallEditor']['snapshot']['fields']==[];assert private()==pending and consumer_graph.read_bytes()==physical_consumer and peers()==peer
  # 철회 전 근거를 새 근거로 간주하지 않고, 실패 후 원래 입력을 그대로 둔다.
  author.locator('[data-bp-save]').click();expect(page.locator('#toast')).to_be_visible() if page.locator('#toast').count() else None;idle();assert private()==pending and consumer_graph.read_bytes()==physical_consumer;refresh();renewed=private();d=dialog();assert '철회해도 보관할 소비자 입력' in d.locator('[data-code-source]').input_value() and 'public long @return { get; }' not in d.locator('[data-code-source]').input_value();edit(d,'return Result.NoBranch; // 공개 철회 후 명시적으로 수정');d.locator('[data-code-cancel]').click();assert private()==renewed;source('return Result.NoBranch; // 공개 철회 후 명시적으로 수정');save();assert not call()['postCallStale'];review=review_open();confirm(review);saved=json.loads(consumer_graph.read_text());assert saved['nodes'][0]['arguments']==expected_args and saved['edges']==expected_routes and 'context.@return' not in saved['nodes'][0]['postCall']['source'];assert json.loads(read(producer)['featureDefinition']['values'].get('blueprintPublishedOutputs','[]'))==[] and peers()==peer;checked('공개 철회는 오래된 소비 근거·저장을 차단하고 입력을 보존하며, 명시적 갱신과 수동 본문 수정 후에만 공동 확정한다')
  idle();page.close();stop();start(4);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);assert not call()['postCallStale'] and call()['postCallEditor']['snapshot']['fields']==[] and peers()==peer;assert json.loads(consumer_graph.read_text())['nodes'][0]['arguments']==expected_args;checked('최종 재시작에서도 철회된 공개 범위·소비 코드·기존 데이터 연결과 별개 입력이 일치한다')
  page.screenshot(path=str(case/'producer-consumer-confirmed.png'));page.close();browser.close();assert not errors and not external,(errors,external)
except Exception:
 try:(case/'failure-state.json').write_text(json.dumps(state(),ensure_ascii=False,indent=2));(case/'failure.json').write_text(json.dumps({'traffic':traffic,'errors':errors},indent=2));page.screenshot(path=str(case/'failure.png'))
 except Exception:pass
 print('격리 실패 자료 '+str(case));raise
finally:stop()
record={'checks':checks,'errors':errors,'external':external,'actualEngine':True,'producerConsumerUi':True,'nativeWindows':False,'accountOrInference':False,'projectRun':False,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False,indent=2))
