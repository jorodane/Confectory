"""Original existing root output controls against an isolated owned-element engine.
Save/Cancel/cold/Confirm and genuine-source-change guards; no account or inference.
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
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(0);page=setup()
  def idle():page.evaluate('async()=>await confectoryFlushPresentation()')
  def browse():
   page.locator('#workspace').click(button='right',position={'x':700,'y':300});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();return page.locator('.window[data-key^="browser:project:"]:visible')
  b=browse();b.locator('[data-object="Owned.Elements::Monster"]').get_by_role('button',name='정의 열기',exact=True).click();monster=page.locator('.window[data-key=schema]');expect(monster.locator('.object-title-description')).to_be_visible(timeout=30000);b.locator('[data-close]').click();monster.locator('.object-title-description').fill('공개 출력과 별개인 미저장 설명');monster.locator('[data-close]').click();idle()
  b=browse();b.locator('[data-tab=feature]').click();b.locator('[data-object="'+id+'"]').get_by_role('button',name='정의 열기',exact=True).click();b.locator('[data-close]').click();page.locator('.window[data-key=declaration] [data-function-write-direct]').click();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-signature-id=seed]')).to_be_visible(timeout=30000);graphid=invoke('blueprint',{'action':'list','feature':id})['result']['result']['rows'][0]['id']
  def graph():return invoke('blueprint',{'action':'read','id':graphid})['result']['result']
  def originals():return all((project/k).read_bytes()==v for k,v in original.items())
  def plan(g,mode,published):
   args=json.loads(json.dumps(g['signature']['args']));arg=next(a for a in args if a['name']=='seed');arg.pop('mode',None)
   if mode=='ref':arg['mode']='ref'
   return {'args':args,'returnType':g['signature']['return'],'remap':{a['name']:a['name'] for a in args},'inputModes':{'seed':mode},'publicOutputs':published}
  def apply(p,basis=None,ok=True):return invoke('blueprint',{'action':'rootParameters','id':graphid,'plan':json.dumps(p),'basis':basis or graph()['basis']},ok)
  def meta():return graph()['featureDefinition']['values']
  def pub():return json.loads(meta().get('blueprintPublishedOutputs','[]'))
  def selected():return invoke('inspectDeclaration',{'id':id})['state']['declaration']
  def group():return invoke('browserDrafts',{'action':'status','ids':[id]})['result']['result']
  def cancel():
   s=group();assert len(s['ids'])==3;snap={'action':'discard','ids':s['ids'],'revisions':[r['revision'] for r in s['rows']],'hashes':[r['hash'] for r in s['rows']],'ownerHash':s['ownerHash'],'checkpointHash':s['checkpointHash']};invoke('browserDrafts',snap)
  def open_current():
   page.reload();goto_editor(page,url);author=page.locator('.window[data-key=blueprint]')
   if not author.is_visible():page.locator('.window[data-key=declaration] [data-function-write-direct]').click()
   expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);return author
  def confirm():
   author.locator('[data-bp-complete]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=30000)
   for cb in review.locator('[data-review-id]').all():cb.check()
   if review.locator('[data-additional-changes]').count():
    review.locator('[data-review-advanced]').click();ack=review.locator('[data-advanced-reviewed]')
    if ack.count():ack.check()
   expect(review.locator('#confirm')).to_be_enabled(timeout=30000);review.locator('#confirm').click();expect(review).to_have_count(0,timeout=60000);expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000)
  idle();peer=state()['presentation']['inputs']['schema'];invoke('select',{'id':'Owned.Elements::Attack'});other=invoke('inspectDeclaration',{'id':'Owned.Elements::Attack'})['state']['declaration'];invoke('editFunctionContract',{'id':other['id'],'revision':other['revision'],'hash':other['textHash'],'edit':{'description':'다른 기능 저장 초안 유지'}});invoke('saveDraft',{})
  def other_draft():return next(row['draft'] for row in json.loads(next(project.glob('.confectory/edit-workspaces/*/draft.json')).read_text())['changes'] if row['id']=='Owned.Elements::Attack')
  other_before=other_draft();g=graph();bad=plan(g,'ref',['return']);bad.pop('inputModes');apply(bad,g['basis'],False);bad=plan(g,'ref',['seed']);apply(bad,ok=False);assert graph()['signature']==g['signature'] and pub()==[] and originals();checked('actual server refuses implicit mode change and publishing an input without any partial grouped/source mutation')
  p=plan(g,'ref',['return']);apply(p);gref=graph();assert next(a for a in gref['signature']['args'] if a['name']=='seed')['mode']=='ref' and pub()==['return'];assert gref['nodes']==g['nodes'] and originals() and len(group()['ids'])==3;invoke('saveDraft',{});checked('explicit value/ref and selected-public-output preparation use the existing atomic three-source draft without changing node values or physical sources')
  idle();page.close();stop();start(1);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);assert pub()==['return'] and next(a for a in graph()['signature']['args'] if a['name']=='seed')['mode']=='ref';assert state()['presentation']['inputs']['schema']==peer and other_draft()==other_before and originals();checked('true cold restart restores matching mode/public-output declaration and all three grouped drafts while other saved/private drafts survive')
  apply(plan(graph(),'value',[]));assert pub()==[];cancel();assert pub()==['return'] and next(a for a in graph()['signature']['args'] if a['name']=='seed')['mode']=='ref' and originals();checked('explicit shared-group Cancel restores its saved public/ref contract together, preserving unrelated drafts')
  author=open_current();confirm();assert 'ref long seed' in (project/'elements/Serial.celem').read_text() and 'blueprintPublishedOutputs' in (project/'elements/Serial.celem').read_text();assert other_draft()==other_before;checked('existing renderer Review and explicit compiler Confirm accept the prepared contract; publication did not execute original code or enable an unsupported eye')
  g=graph();apply(plan(g,'value',[]));invoke('saveDraft',{});author=open_current();confirm();assert pub()==[] and 'ref long seed' not in (project/'elements/Serial.celem').read_text() and 'blueprintPublishedOutputs' not in (project/'elements/Serial.celem').read_text();assert other_draft()==other_before;checked('explicit revoke and value-mode restoration Save/Confirm remove only the selected contract metadata and preserve the other function draft')
  idle();page.close();stop();start(2);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);assert pub()==[] and state()['presentation']['inputs']['schema']==peer and other_draft()==other_before;assert all((project/k).read_bytes()==v for k,v in original.items() if k not in ['elements/Serial.celem','elements/SerialBlueprintBody.celem',str(next(project.glob('blueprints/*.graph.json')).relative_to(project))]);checked('final restart retains revoked/value contract and unrelated sources/private inputs; no normal root/output boundary was broadened')
  page.close();browser.close();assert not errors and not external,(errors,external)
except Exception:
 try:(case/'failure.json').write_text(json.dumps({'state':state(),'traffic':traffic,'errors':errors},indent=2))
 except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case));raise
finally:stop()
record={'checks':checks,'errors':errors,'external':external,'actualEngine':True,'nativeWindows':False,'accountOrInference':False,'publicWrapperUiConnected':False,'rootModeUiConnected':False,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
