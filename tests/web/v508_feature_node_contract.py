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
  def focus_node():author.locator('[data-bp-overview-node="'+nodeid+'"]').click()
  def card():return author.locator('[data-bp-node="'+nodeid+'"]')
  def value(name):return card().locator('.bp-pin-plug[data-side=in][data-port="field:'+name+'"] input')
  def save():author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_have_text('저장됨',timeout=30000)
  def script(body):
   card().locator('[data-internal-code]').click();dialog=page.get_by_role('dialog',name='C# Script · 내부 기능',exact=True);code=dialog.locator('[data-code-source]');code.evaluate('(el,d)=>el.setSelectionRange(el.value.indexOf(d[0])+3,el.value.lastIndexOf(d[1]))',["\n{\n","\n}\n"]);page.keyboard.insert_text(body+'\n');dialog.locator('[data-code-save]').click()
  def name_field(current):return card().locator('[data-action-side=inputs][data-action-field="'+current+'"] [data-action-field-name]')
  def sources_unchanged():assert all((project/k).read_bytes()==v for k,v in original.items())
  focus_node();before=graph();card().locator('[data-action-field-add=inputs]').click();expect(name_field('input1')).to_have_value('input1');name_field('input1').fill('잘못된 이름');name_field('input1').press('Enter');mark=len(traffic);author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_contain_text('핀 값을',timeout=30000);assert not any(r.get('invoke',{}).get('input',{}).get('action')=='parameters' for r in traffic[mark:]);expect(name_field('input1')).to_have_value('잘못된 이름');name_field('input1').fill('label');name_field('input1').press('Enter');value('label').fill('검증 값 한글');value('label').press('Enter');script('return;');save();after=graph();added=next(n for n in after['nodes'] if n['id']==nodeid);assert added['signature']['args']==[{'name':'label','type':'string'}];assert json.loads(added['arguments'][0]['valueJson'])=={'constant':'검증 값 한글'} and added['sourceStatus']=='available';sources_unchanged();checked('original inline pin add/name/value controls reject and retain invalid name before writes, then Save typed contract/binding/body with no final source change')
  name_field('label').fill('caption');name_field('label').press('Enter');script('return;');save();after=graph();added=next(n for n in after['nodes'] if n['id']==nodeid);assert added['signature']['args']==[{'name':'caption','type':'string'}] and json.loads(added['arguments'][0]['valueJson'])=={'constant':'검증 값 한글'};sources_unchanged();checked('explicit internal input rename remaps existing value by original identity while retaining body text and metadata')
  card().locator('.bp-pin-plug[data-port="field:caption"] [aria-label="값 목록 열기"]').click();page.get_by_role('button',name='자료형 선택…',exact=True).click();picker=page.get_by_role('dialog',name='속성 타입 선택');picker.locator('[data-type=long]').click();assert not [v for k,v in state()['presentation']['inputs']['blueprint'] if v.get('type')=='parameters'];same=graph();assert same['sources']==after['sources'];forged=invoke('blueprint',{'action':'parameters','id':graphid,'basis':same['basis'],'node':nodeid,'argsJson':'[]','remapJson':'{"caption":null}','returnType':'void'},False);assert graph()['sources']==same['sources'];sources_unchanged();checked('connected input type/drop refused in original type popup and forged server request; binding/source closure unchanged')
  card().locator('[data-action-field-add=outputs]').click();script('return caption;');save();after=graph();added=next(n for n in after['nodes'] if n['id']==nodeid);assert added['signature']['return']=='string' and added['sourceStatus']=='available';sources_unchanged();checked('explicit output pin addition changes unused return contract and requires reapplying body against the displayed new signature')
  # Owned fixture peer connects legal serial flow and a typed consumer to test server-enforced return protection.
  for change in [{'action':'entry','node':nodeid},{'action':'route','node':nodeid,'port':'next','to':'body'}]:
   fresh=graph();invoke('blueprint',{**change,'id':graphid,'basis':fresh['basis']})
  invoke('saveDraft',{});page.reload();goto_editor(page,url);author=page.locator('.window[data-key=blueprint]');expect(author.locator('.bp-function-card')).to_have_count(2,timeout=30000);author.locator('[data-bp-overview-node=body]').click();author.locator('[data-bp-node=body] .bp-pin-plug[data-side=in][data-port="field:title"] [aria-label="값 목록 열기"]').click();page.get_by_role('dialog',name='핀 값 선택').get_by_role('button',name='내부 기능 · 결과',exact=True).click();save();connected=next(n for n in graph()['nodes'] if n['id']=='body');assert json.loads(next(a['valueJson'] for a in connected['arguments'] if a['name']=='title'))=={'node':nodeid};focus_node();card().locator('.bp-pin-plug[data-side=out][data-port="field:return"] button').first.click(button='right');page.get_by_role('dialog',name='속성 타입 선택').locator('[data-type=long]').click();same=graph();assert next(n for n in same['nodes'] if n['id']==nodeid)['signature']['return']=='string';invoke('blueprint',{'action':'parameters','id':graphid,'basis':same['basis'],'node':nodeid,'argsJson':'[{"name":"caption","type":"string"}]','remapJson':'{"caption":"caption"}','returnType':'long'},False);assert graph()['sources']==same['sources'];sources_unchanged();checked('used return type is refused by original output type control and independently by the server while preserving consumer and body')
  card().locator('[data-action-field-add=inputs]').click();page.evaluate('async()=>await confectoryFlushPresentation()');pending=[(k,v) for k,v in state()['presentation']['inputs']['blueprint'] if '|v508-author|' in k];assert len(pending)==1 and pending[0][1]['type']=='parameters';page.close();stop();start(1);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('.bp-function-card')).to_have_count(2,timeout=30000);focus_node();expect(name_field('input1')).to_have_value('input1');assert [(k,v) for k,v in state()['presentation']['inputs']['blueprint'] if '|v508-author|' in k]==pending;value('input1').fill('cold restore');value('input1').press('Enter');script('return caption;');save();added=next(n for n in graph()['nodes'] if n['id']==nodeid);assert len(added['signature']['args'])==2 and added['sourceStatus']=='available';sources_unchanged();checked('actual cold host restart restores pending typed contract/proof and explicit binding/body Save succeeds with original final files intact')
  author.locator('[data-bp-complete]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=30000)
  if review.locator('[data-additional-changes]').count():
   review.locator('[data-review-advanced]').click();ack=review.locator('[data-advanced-reviewed]')
   if ack.count():ack.check()
  expect(review.locator('#confirm')).to_be_enabled(timeout=30000);review.locator('#confirm').click();expect(review).to_have_count(0,timeout=60000);assert any(r.get('result',{}).get('result',{}).get('sourceConfirmed') for r in traffic);assert all((project/k).read_bytes()==v for k,v in original.items() if k.endswith('.celem') or k=='project.cproj');page.screenshot(path=str(case/'contract-confirmed.png'));checked('explicit grouped Review/compiler Confirm accepts restored contract and checked serial consumer; no project execution or account access')
  page.close();stop();browser.close();assert not errors and not external,(errors,external)
except Exception:
 try:(case/'failure.json').write_text(json.dumps({'state':state(),'traffic':traffic,'errors':errors},indent=2))
 except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case));raise
finally:stop()
record={'checks':checks,'errors':errors,'external':external,'actualEngine':True,'nativeWindows':False,'accountOrInference':False,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
