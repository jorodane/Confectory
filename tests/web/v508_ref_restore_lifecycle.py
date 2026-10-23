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

control={'armed':False,'held':None}
base_route=route
def route(request):
 body=request.request.post_data_json if request.request.method=='POST' else None
 if control['armed'] and isinstance(body,dict) and body.get('op')=='invoke' and body.get('endpoint')=='savePresentation' and not body.get('input',{}).get('presentation',{}).get('inputs',{}).get('blueprint'):
  control['armed']=False;control['held']=request;return
 base_route(request)

try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(0);page=setup();page.locator('#workspace').click(button='right',position={'x':700,'y':300});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=page.locator('.window[data-key^="browser:project:"]');b.locator('[data-tab=feature]').click();row=b.locator('[data-object="'+id+'"]');expect(row).to_be_visible(timeout=30000);row.get_by_role('button',name='정의 열기',exact=True).click();w=page.locator('.window[data-key=declaration]');expect(w.locator('[data-function-write-direct]')).to_be_visible(timeout=30000);w.locator('[data-function-write-direct]').click();author=page.locator('.window[data-key=blueprint]');expect(author.locator('.bp-function-card')).to_have_count(2,timeout=30000);nodeid=author.locator('.bp-function-card').last.get_attribute('data-bp-node');graphid=invoke('blueprint',{'action':'list','feature':id})['result']['result']['rows'][0]['id']

  def graph():return invoke('blueprint',{'action':'read','id':graphid})['result']['result']
  def reopen_author():
   page.wait_for_function('()=>typeof globalThis.confectoryFlushPresentation==="function"')
   page.evaluate('async()=>await confectoryFlushPresentation()')
   if not page.locator('.window[data-key=blueprint]').is_visible():page.locator('.window[data-key=declaration] [data-function-write-direct]').click()
  def originals():return all((project/k).read_bytes()==v for k,v in original.items())
  # Only the owned fixture is prepared through existing product APIs; no deployed setup API.
  g=graph();invoke('blueprint',{'action':'upgradeProfile','id':graphid,'profile':'sync-acyclic-ref-nodes-v1','basis':g['basis']});g=graph();invoke('blueprint',{'action':'parameters','id':graphid,'node':nodeid,'argsJson':json.dumps([{'name':'value','type':'long','mode':'ref'},{'name':'echo','type':'long','mode':'out'}]),'remapJson':'{}','returnType':'long','basis':g['basis']});g=graph();invoke('blueprint',{'action':'source','id':graphid,'node':nodeid,'text':'value += 1;echo=value;return value;','basis':g['basis']});invoke('saveDraft',{});page.reload();goto_editor(page,url);reopen_author();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-node="'+nodeid+'"]')).to_be_visible(timeout=30000)
  def focus_node():author.locator('[data-bp-overview-node="'+nodeid+'"]').click()
  def card():return author.locator('[data-bp-node="'+nodeid+'"]')
  def names(side,name):return card().locator('[data-action-side="'+side+'"][data-action-field="'+name+'"] [data-action-field-name]')
  def save():
   gated=len(checks)==1
   if gated:control['armed']=True;control['held']=None
   author.locator('[data-bp-save]').click()
   if gated:
    for _ in range(600):
     if control['held']:break
     page.wait_for_timeout(10)
    assert control['held'],'post-apply presentation retirement request not observed'
    expect(author.locator('[data-bp-save]')).to_be_disabled();expect(author.locator('.bp-status')).to_have_text('저장 중…')
    assert any(v.get('type')=='argument:counter' for k,v in state()['presentation']['inputs']['blueprint'])
    accepted=next(n for n in graph()['nodes'] if n['id']==nodeid);assert json.loads(accepted['arguments'][0]['valueJson'])=={'input':'seed'}
    control['held'].continue_();control['held']=None;checked('saved status waits for real post-apply private-input persistence; source is accepted but pending cleanup cannot appear complete')
   expect(author.locator('.bp-status')).to_have_text('저장됨',timeout=30000);expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000)
   assert not [(k,v) for k,v in state()['presentation']['inputs']['blueprint'] if '|v508-author|' in k], 'completed Save must retire exact accepted input on disk'

  def script(text):
   card().locator('[data-internal-code]').click();dialog=page.get_by_role('dialog',name='C# Script · 내부 기능',exact=True);code=dialog.locator('[data-code-source]');assert 'ref long counter' in code.input_value() and 'out long total' in code.input_value();code.evaluate('(el,d)=>el.setSelectionRange(el.value.indexOf(d[0])+3,el.value.lastIndexOf(d[1]))',["\n{\n","\n}\n"]);page.keyboard.insert_text(text+'\n');dialog.locator('[data-code-save]').click()
  focus_node();expect(names('inputs','value')).to_be_editable();expect(names('outputs','echo')).to_be_editable();assert card().locator('[data-action-side=outputs]').count()==2;names('inputs','value').fill('counter');names('inputs','value').press('Enter');names('outputs','echo').fill('total');names('outputs','echo').press('Enter');script('counter += 2;total=counter;return counter;');save();g=graph();node=next(n for n in g['nodes'] if n['id']==nodeid);assert node['signature']['args']==[{'name':'counter','type':'long','mode':'ref'},{'name':'total','type':'long','mode':'out'}] and node['sourceStatus']=='available' and originals();checked('original existing ref input/out output rename and protected Script retain exact modes and ordinary static source ownership')
  field=card().locator('.bp-pin-plug[data-side=in][data-port="field:counter"] input');field.fill('44');field.press('Enter');expect(page.get_by_role('dialog',name='핀 값 선택').locator('[role=status]')).to_contain_text('참조 입력');assert not any(r.get('invoke',{}).get('input',{}).get('valueJson')=='{"constant":44}' for r in traffic);field.press('Escape');card().locator('.bp-pin-plug[data-side=in][data-port="field:counter"] [aria-label="값 목록 열기"]').click();page.get_by_role('button',name='입력 · seed',exact=True).click();save();g=graph();node=next(n for n in g['nodes'] if n['id']==nodeid);assert json.loads(node['arguments'][0]['valueJson'])=={'input':'seed'} and node['signature']['args'][0]['mode']=='ref';checked('ref value menu refuses numeric literal and original storage connection saves an input reference without downgrading to value mode')
  before=graph();wrong=[{'name':'counter','type':'long'},{'name':'total','type':'long','mode':'out'}];invoke('blueprint',{'action':'parameters','id':graphid,'node':nodeid,'argsJson':json.dumps(wrong),'remapJson':'{"counter":"counter","total":"total"}','returnType':'long','basis':before['basis']},False);assert graph()['nodes']==before['nodes'] and originals();checked('forged ref-to-value remap is rejected server-side with original connections/source retained')
  # Bind both independent node outputs before testing protected removal/type changes.
  fresh=graph();invoke('blueprint',{'action':'entry','id':graphid,'node':nodeid,'basis':fresh['basis']});fresh=graph();invoke('blueprint',{'action':'route','id':graphid,'node':nodeid,'port':'next','to':'body','basis':fresh['basis']});fresh=graph();invoke('blueprint',{'action':'argument','id':graphid,'node':'body','name':'other','valueJson':json.dumps({'node':nodeid,'output':'total'}),'basis':fresh['basis']});invoke('saveDraft',{});page.reload();goto_editor(page,url);reopen_author();author=page.locator('.window[data-key=blueprint]');focus_node();before=graph();card().locator('.bp-pin-plug[data-side=out][data-port="field:total"] .bp-pin-remove').click();expect(names('outputs','total')).to_be_visible();assert graph()['nodes']==before['nodes'];checked('consumed named multi-output cannot be removed through original pin control')
  page.evaluate('async()=>await confectoryFlushPresentation()');page.close();stop();start(1);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-node="'+nodeid+'"]')).to_be_visible(timeout=30000);g=graph();assert next(n for n in g['nodes'] if n['id']=='body')['arguments'][1]['valueJson']==json.dumps({'node':nodeid,'output':'total'},separators=(',',':'));author.locator('[data-bp-complete]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=30000)
  for cb in review.locator('[data-review-id]').all():cb.check()
  if review.locator('[data-additional-changes]').count():
   review.locator('[data-review-advanced]').click();ack=review.locator('[data-advanced-reviewed]')
   if ack.count():ack.check()
  expect(review.locator('#confirm')).to_be_enabled(timeout=30000);review.locator('#confirm').click();expect(review).to_have_count(0,timeout=60000);assert any(r.get('result',{}).get('result',{}).get('sourceConfirmed') for r in traffic);assert all((project/k).read_bytes()==v for k,v in original.items() if k.endswith('.celem') or k=='project.cproj');expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);page.wait_for_function('()=>!document.querySelector("#app").inert');page.screenshot(path=str(case/'ref-output-confirmed.png'));checked('actual cold restart and explicit compiler Confirm accept storage-backed ref mutation plus named output use while all declarations stay unchanged')
  # A separate, genuinely changed source MUST preserve unsaved input and fail closed after cold restart.
  page.reload();goto_editor(page,url);reopen_author();author=page.locator('.window[data-key=blueprint]');focus_node();card().locator('.bp-pin-plug[data-side=in][data-port="field:counter"] [aria-label="값 목록 열기"]').click();page.get_by_role('button',name='입력 · other',exact=True).click();page.evaluate('async()=>await confectoryFlushPresentation()');retained=state()['presentation']['inputs']['blueprint'];assert any(v.get('text')=='{"input":"other"}' for k,v in retained)
  invoke('select',{'id':id});info=invoke('inspectDeclaration',{'id':id})['state']['declaration'];invoke('editFunctionContract',{'id':id,'revision':info['revision'],'hash':info['textHash'],'edit':{'description':'외부에서 바뀐 실제 기능 설명'}});invoke('saveDraft',{});checkpoint=next(project.glob('.confectory/edit-workspaces/*/draft.json')).read_bytes();page.evaluate('async()=>await confectoryFlushPresentation()');page.close();stop();start(2);page=setup();reopen_author();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);author.locator('[data-bp-complete]').click();expect(author.locator('.bp-status')).to_contain_text('원본이나 계약이 바뀌었습니다',timeout=30000);expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000)
  assert state()['presentation']['inputs']['blueprint']==retained and next(project.glob('.confectory/edit-workspaces/*/draft.json')).read_bytes()==checkpoint;assert json.loads(next(n for n in graph()['nodes'] if n['id']==nodeid)['arguments'][0]['valueJson'])=={'input':'seed'};assert invoke('inspectDeclaration',{'id':id})['state']['declaration']['description']=='외부에서 바뀐 실제 기능 설명';checked('actual changed function source after private ref input survives cold restart blocks Complete without overwriting source, accepted binding or retained input/checkpoint')
  page.close();stop();browser.close();assert not errors and not external,(errors,external)

except Exception:
 try:(case/'failure.json').write_text(json.dumps({'state':state(),'traffic':traffic,'errors':errors},indent=2))
 except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case));raise
finally:stop()
record={'checks':checks,'errors':errors,'external':external,'actualEngine':True,'nativeWindows':False,'accountOrInference':False,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
