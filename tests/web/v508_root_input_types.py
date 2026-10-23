"""Original root input type/add/remove UI against an isolated owned-element engine.
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
  def idle():
   page.wait_for_function('()=>typeof globalThis.confectoryFlushPresentation==="function"');page.evaluate('async()=>await confectoryFlushPresentation()')
  def browse():
   page.locator('#workspace').click(button='right',position={'x':700,'y':300});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=page.locator('.window[data-key^="browser:project:"]:visible');expect(b).to_be_visible(timeout=30000);return b
  b=browse();b.locator('[data-object="Owned.Elements::Monster"]').get_by_role('button',name='정의 열기',exact=True).click();w=page.locator('.window[data-key=schema]');expect(w.locator('.object-title-description')).to_be_visible(timeout=30000);b.locator('[data-close]').click();peer='다른 객체 미저장 설명 보존';w.locator('.object-title-description').click();w.locator('.object-title-description').fill(peer);w.locator('[data-close]').click();b=browse();b.locator('[data-tab=feature]').click();b.locator('[data-object="'+id+'"]').get_by_role('button',name='정의 열기',exact=True).click();w=page.locator('.window[data-key=declaration]');expect(w.locator('[data-function-write-direct]')).to_be_enabled(timeout=30000);b.locator('[data-close]').click();w.locator('[data-function-write-direct]').click();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-signature-id=seed]')).to_be_visible(timeout=30000);graphid=invoke('blueprint',{'action':'list','feature':id})['result']['result']['rows'][0]['id']
  def graph():return invoke('blueprint',{'action':'read','id':graphid})['result']['result']
  def originals():return all((project/k).read_bytes()==v for k,v in original.items())
  def private():idle();return [(k,v) for k,v in state()['presentation']['inputs']['blueprint'] if '|v508-author|' in k]
  def peers():idle();return [(k,v) for k,v in state()['presentation']['inputs']['schema'] if 'Owned.Elements::Monster' in k]
  def entry(name):return author.locator('.bp-pin-plug[data-node="$entry"][data-port="field:'+name+'"]')
  def choose(name,kind,array=False):
   entry(name).locator('.bp-entry-type-button').click();popup=page.get_by_role('dialog',name='속성 타입 선택',exact=True);popup.locator('[data-multi]').set_checked(array);popup.locator('[data-type="'+kind+'"]').click()
  def save():
   author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_have_text('저장됨',timeout=30000);expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000)
  def complete():
   author.locator('[data-bp-complete]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=30000)
   for cb in review.locator('[data-review-id]').all():cb.check()
   if review.locator('[data-additional-changes]').count():
    review.locator('[data-review-advanced]').click();ack=review.locator('[data-advanced-reviewed]')
    if ack.count():ack.check()
   expect(review.locator('#confirm')).to_be_enabled(timeout=30000);review.locator('#confirm').click();expect(review).to_have_count(0,timeout=60000);expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000)
  # Use the original node drag to expose overlapping plug overhang in this dense fixture.
  header=author.locator('[data-bp-node=body] .function-node-heading');box=header.bounding_box();page.mouse.move(box['x']+180,box['y']+20);page.mouse.down();page.mouse.move(box['x']+540,box['y']+20,steps=12);page.mouse.up()
  old=graph();peer_before=peers();assert len(peer_before)==1 and peer_before[0][1]['text']==peer
  choose('seed','int');entry('seed').locator('.bp-pin-remove').click();assert not private() and graph()['signature']==old['signature'] and originals() and peers()==peer_before;checked('original root type plug and X refuse changing/removing a bound input, preserving all source and other-object private input')
  bad={'args':[{**a,'type':'int'} if a['name']=='seed' else a for a in old['signature']['args']],'returnType':old['signature']['return'],'remap':{a['name']:None if a['name']=='seed' else a['name'] for a in old['signature']['args']}};invoke('blueprint',{'action':'rootParameters','id':graphid,'plan':json.dumps(bad),'basis':old['basis']},False);assert graph()['nodes']==old['nodes'] and graph()['signature']==old['signature'] and originals();checked('forged disconnected remap for a still-used root input refuses the complete three-source edit server-side')
  # Actual original Change Cancel on a separately staged, uncheckpointed typed root group.
  g=graph();temp={'args':[{**a,'type':'int'} if a['name']=='title' else a for a in g['signature']['args']]+[{'name':'spare','type':'string'}],'returnType':g['signature']['return'],'remap':{a['name']:None if a['name']=='title' else a['name'] for a in g['signature']['args']}};invoke('blueprint',{'action':'rootParameters','id':graphid,'plan':json.dumps(temp),'basis':g['basis']});author.locator(':scope > header [data-close]').click();b=browse();b.locator('[data-tab=feature]').click();b.locator('[data-object="'+id+'"]').get_by_role('button',name='정의 열기',exact=True).click();b.locator('[data-close]').click();w=page.locator('.window[data-key=declaration]');expect(w.locator('[data-feature-action=discard]')).to_be_enabled(timeout=30000);w.locator('[data-feature-action=discard]').click();expect(w.locator('[data-feature-action=discard]')).to_be_enabled(timeout=30000);assert graph()['signature']==old['signature'] and originals() and peers()==peer_before;checked('actual function Change Cancel restores typed signature, implementation and root graph as one unsaved group, retaining another object draft')
  w.locator('[data-function-write-direct]').click();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-signature-id=title]')).to_be_visible(timeout=30000);choose('title','int');assert json.loads(private()[0][1]['text'])['args'][3]['type']=='int';author.locator('.bp-viewport').focus();page.keyboard.press('Control+z');assert not private() and originals();checked('unused root input type is a private contract; original structural Undo cancels it without source writes')
  choose('title','int');author.locator('[data-signature-add=inputs]').click();author.locator('.bp-viewport').hover(position={'x':110,'y':200});page.keyboard.down('Control');page.mouse.wheel(0,300);page.mouse.wheel(0,300);page.keyboard.up('Control');choose('input1','long',True);name=author.locator('[data-signature-id=input1] [data-signature-name]');name.fill('extraValues');name.press('Enter');author.locator('[data-signature-add=inputs]').click();entry('input1').locator('.bp-pin-remove').click();plan=json.loads(private()[0][1]['text']);assert len(plan['args'])==7 and plan['args'][-1]=={'name':'extraValues','type':'long[]'} and originals() and peers()==peer_before;checked('original Add/type/array/name and X keep a new input entirely private and remove only the uncreated extra pin')
  idle();page.close();stop();start(1);page=setup();idle();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-signature-id=extraValues]')).to_be_visible(timeout=30000);assert graph()['signature']==old['signature'] and peers()==peer_before;checked('private unused-type replacement and new array pin restore after a real restart without shared or final source mutation')
  save();g=graph();assert g['signature']['args'][3]['type']=='int' and g['signature']['args'][-1]=={'name':'extraValues','type':'long[]'} and g['nodes']==old['nodes'] and originals() and peers()==peer_before;assert not private();checked('original Save atomically persists function/implementation/graph root types and new array input while original code, literals and peer draft remain unchanged')
  idle();page.close();stop();start(2);page=setup();idle();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-signature-id=extraValues]')).to_be_visible(timeout=30000);assert graph()['signature']==g['signature'] and peers()==peer_before;complete();assert all((project/k).read_bytes()==v for k,v in original.items() if k not in ['elements/Serial.celem','elements/SerialBlueprintBody.celem',str(next(project.glob('blueprints/*.graph.json')).relative_to(project))]);assert peers()==peer_before;page.screenshot(path=str(case/'root-input-types-confirmed.png'));checked('typed root contract survives checkpoint restart and explicit compiler Confirm changes only the owned function/implementation/graph, preserving peer input and node code')
  # Remove the now-saved but unused array input, not just a newly staged pin.
  entry('extraValues').locator('.bp-pin-remove').click();save();assert not any(a['name']=='extraValues' for a in graph()['signature']['args']);complete();assert peers()==peer_before;checked('original X removes a saved unused root input through a second exact three-source Save and explicit compiler Confirm')
  # The receipt refresh for our own unchanged Confirm must NOT bless an independent source change.
  author.locator('[data-signature-add=inputs]').click();retained=private();invoke('select',{'id':id});info=invoke('inspectDeclaration',{'id':id})['state']['declaration'];invoke('editFunctionContract',{'id':id,'revision':info['revision'],'hash':info['textHash'],'edit':{'description':'독립적으로 변경된 기능 원본'}});invoke('saveDraft',{});checkpoint=next(project.glob('.confectory/edit-workspaces/*/draft.json')).read_bytes();author.locator('[data-bp-save]').click();expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);expect(author.locator('.bp-status')).not_to_have_text('저장됨');assert private()==retained and next(project.glob('.confectory/edit-workspaces/*/draft.json')).read_bytes()==checkpoint and peers()==peer_before;assert not any(a['name']=='input1' for a in graph()['signature']['args']);assert invoke('inspectDeclaration',{'id':id})['state']['declaration']['description']=='독립적으로 변경된 기능 원본';checked('own Confirm receipt refresh does not accept a later changed function source: root input, other-object draft and prior checkpoint remain intact')
  page.close();stop();browser.close();assert not errors and not external,(errors,external)

except Exception:
 try:(case/'failure.json').write_text(json.dumps({'state':state(),'traffic':traffic,'errors':errors},indent=2))
 except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case));raise
finally:stop()
record={'checks':checks,'errors':errors,'external':external,'actualEngine':True,'nativeWindows':False,'accountOrInference':False,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
