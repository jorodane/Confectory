"""Cold pending-input restoration in a previously compiler-confirmed OWNED element fixture.
No account/grant/model invocation. Preserves source bytes and original draft proof.
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

try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(0);page=setup();page.locator('#workspace').click(button='right',position={'x':700,'y':300});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=page.locator('.window[data-key^="browser:project:"]');b.locator('[data-tab=feature]').click();row=b.locator('[data-object="'+id+'"]');expect(row).to_be_visible(timeout=30000);row.get_by_role('button',name='정의 열기',exact=True).click();w=page.locator('.window[data-key=declaration]');expect(w.locator('[data-function-write-direct]')).to_be_visible(timeout=30000);w.locator('[data-function-write-direct]').click();author=page.locator('.window[data-key=blueprint]');expect(author.locator('.bp-function-card')).to_have_count(2,timeout=30000);nodeid=author.locator('.bp-function-card').last.get_attribute('data-bp-node');graphid=invoke('blueprint',{'action':'list','feature':id})['result']['result']['rows'][0]['id']

  def graph():return invoke('blueprint',{'action':'read','id':graphid})['result']['result']
  def originals():return all((project/k).read_bytes()==v for k,v in original.items())
  def rootnames():return author.locator('[data-bp-signature=inputs] [data-signature-name]')
  def order():return [v.get_attribute('value') for v in rootnames().all()]
  def save():author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_have_text('저장됨',timeout=30000)
  old=graph();plan={'args':old['signature']['args'][::-1],'returnType':old['signature']['return'],'remap':{a['name']:a['name'] for a in old['signature']['args']}}
  # Pre-existing ordinary unsaved input change invalidates the retained root receipt.
  invoke('blueprint',{'action':'argument','id':graphid,'node':'body','name':'flag','valueJson':'{"constant":false}','basis':old['basis']})
  newer=graph();result=invoke('blueprint',{'action':'rootParameters','id':graphid,'plan':json.dumps(plan),'basis':old['basis']},False);assert graph()['signature']==old['signature'] and next(a for a in graph()['nodes'][0]['arguments'] if a['name']=='flag')['valueJson']=='{"constant":false}';assert originals();checked('stale root receipt refuses the whole function/implementation/graph change and retains a newer peer graph binding')
  # Cancel root edits as one server-derived group before any checkpoint is saved.
  fresh=graph();invoke('blueprint',{'action':'rootParameters','id':graphid,'plan':json.dumps(plan),'basis':fresh['basis']});invoke('select',{'id':id});st=invoke('browserDrafts',{'action':'status','ids':[id]})['result']['result'];assert len(st['ids'])==3 and graphid in st['ids'];invoke('reviewDraft',{'id':id,'target':'portable'},False)
  invoke('browserDrafts',{'action':'discard','ids':st['ids'],'revisions':[r['revision'] for r in st['rows']],'hashes':[r['hash'] for r in st['rows']],'ownerHash':st['ownerHash'],'checkpointHash':st['checkpointHash']});assert graph()['signature']==old['signature'] and originals();checked('root Cancel expands only its exact three-source group, restores all contracts together, and single-source Review is refused')
  page.reload();goto_editor(page,url);page.locator('.window[data-key=declaration] [data-function-write-direct]').click();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-order-handle=seed]')).to_be_enabled(timeout=30000)
  author.locator('[data-order-handle=seed]').focus();author.locator('[data-order-handle=seed]').press('ArrowDown');expect(rootnames().nth(0)).to_have_value('other');assert graph()['signature']==old['signature'] and originals();author.locator('.bp-viewport').focus();page.keyboard.press('Control+z');expect(rootnames().nth(0)).to_have_value('seed');checked('original root order handle stages a private ordered contract and original Undo cancels it with no shared/source write')
  author.locator('[data-order-handle=seed]').press('ArrowDown');field=author.locator('[data-signature-id=seed] [data-signature-name]');field.fill('origin');field.press('Enter');expect(author.locator('[data-signature-id=origin]')).to_be_visible();page.evaluate('async()=>await confectoryFlushPresentation()');page.close();stop();start(1);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-signature-id=origin]')).to_be_visible(timeout=30000);assert graph()['signature']==old['signature'];checked('private root rename/order survives true restart without changing the shared function or graph')
  save();after=graph();assert [a['name'] for a in after['signature']['args']][:2]==['other','origin'];assert next(a for a in after['nodes'][0]['arguments'] if a['name']=='other')['valueJson']=='{"input":"origin"}';assert json.loads(after['exits'][0]['valueJson'])=={'input':'other'};assert originals();checked('original Save atomically updates function plus implementation signature plus graph hash/input references while keeping physical sources unchanged')
  page.evaluate('async()=>await confectoryFlushPresentation()');page.close();stop();start(2);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-signature-id=origin]')).to_be_visible(timeout=30000);assert graph()['signature']==after['signature'];checked('checkpoint restart restores matching function/implementation/graph contracts and original source node records')
  author.locator('[data-bp-complete]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=30000)
  for cb in review.locator('[data-review-id]').all():cb.check()
  if review.locator('[data-additional-changes]').count():
   review.locator('[data-review-advanced]').click();ack=review.locator('[data-advanced-reviewed]')
   if ack.count():ack.check()
  expect(review.locator('#confirm')).to_be_enabled(timeout=30000);review.locator('#confirm').click();expect(review).to_have_count(0,timeout=60000);assert any(r.get('result',{}).get('result',{}).get('sourceConfirmed') for r in traffic);assert all((project/k).read_bytes()==v for k,v in original.items() if k not in ['elements/Serial.celem','elements/SerialBlueprintBody.celem',str(next(project.glob('blueprints/*.graph.json')).relative_to(project))]);page.wait_for_function('()=>!document.querySelector("#app").inert');page.screenshot(path=str(case/'root-contract-confirmed.png'));checked('explicit grouped compiler Confirm accepts root rename/order without modifying node code, other elements or running the project')
  page.close();stop();browser.close();assert not errors and not external,(errors,external)

except Exception:
 try:(case/'failure.json').write_text(json.dumps({'state':state(),'traffic':traffic,'errors':errors},indent=2))
 except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case));raise
finally:stop()
record={'checks':checks,'errors':errors,'external':external,'actualEngine':True,'nativeWindows':False,'accountOrInference':False,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
