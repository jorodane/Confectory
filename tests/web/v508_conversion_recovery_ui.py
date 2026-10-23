"""원본 UI에서 기존 C# 본문 미리보기/취소/저장/cold/명시적 컴파일 Confirm. 격리 fixture만 사용."""
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

def sdk(op,**data):
 p=subprocess.run([env['CONFECTORY_DOTNET'],str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps({'operation':op,**data}),text=True,capture_output=True,check=True,env=env);v=json.loads(p.stdout);assert v['ok'],v;return v['result']

impl='Owned.Elements::AttackBody';feature='Owned.Elements::Attack';file=project/'AttackBody.celem';text=file.read_text();at=text.rindex('}');file.write_text(text[:at]+'body windows "AttackWindows.csbody";'+text[at:]);windows=project/'AttackWindows.csbody';windows.write_bytes('// 다른 실행 대상\r\nreturn amount + 5;\r\n'.encode());body=project/'Attack.csbody';body.write_bytes(b'\xef\xbb\xbf'+'// 원본 한글 😀\r\nreturn amount + 1;\r\n'.encode());(project/'OtherAttackBody.celem').write_text('implementation Owned.Elements::OtherAttackBody for '+feature+' (long amount) -> long {body common "OtherAttack.csbody";}');(project/'OtherAttack.csbody').write_text('return amount * 2;');manifest=project/'project.cproj';text=manifest.read_text();at=text.rindex('}');manifest.write_text(text[:at]+'element OtherAttackBody implementation "OtherAttackBody.celem";\n'+text[at:]);physical={str(p):p.read_bytes() for p in project.rglob('*') if p.is_file() and '.confectory' not in p.parts};wanted='// 선택한 common 복사 본문 한글 😀\nreturn amount + 17;\n'
def preserved(skip_impl=False):return all(pathlib.Path(k).read_bytes()==v for k,v in physical.items() if not skip_impl or pathlib.Path(k)!=file)
def checkpoint():return {str(p):p.read_bytes() for p in project.glob('.confectory/edit-workspaces/*/draft.json')}
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(0);page=setup()
  def idle():page.evaluate('async()=>await confectoryFlushPresentation()')
  def browse():
   page.locator('#workspace').click(button='right',position={'x':700,'y':300});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();return page.locator('.window[data-key^="browser:project:"]:visible')
  def open_feature():
   b=browse();b.locator('[data-tab=feature]').click();b.locator('[data-object="'+feature+'"]').get_by_role('button',name='정의 열기',exact=True).click();b.locator('[data-close]').click();page.locator('.window[data-key=declaration] [data-function-write-direct]').click();return page.locator('.window[data-key=blueprint]')
  author=open_feature();expect(author.locator('[data-internal-code]')).to_be_enabled(timeout=30000)
  def code_dialog():
   author.locator('[data-bp-overview-node=body]').click();author.locator('[data-bp-node=body] [data-internal-code]').click();return page.get_by_role('dialog',name='C# Script · body',exact=True)
  def edit(d,text):
   code=d.locator('[data-code-source]');code.evaluate('(el)=>{const spans=[...el.closest(".bp-script-editor").querySelectorAll("[data-code-highlight]>span")],part=spans.find(p=>p.dataset.codeRegion==="body");const start=spans.slice(0,spans.indexOf(part)).reduce((n,p)=>n+p.textContent.length,0);el.setSelectionRange(start,start+part.textContent.length)}');page.keyboard.insert_text(text)
  def private():idle();return state()['presentation']['inputs']['blueprint']

  d=code_dialog();edit(d,wanted);d.locator('[data-code-save]').click();pending=private();assert len(pending)==1 and preserved();armed='lost';rid=None;lost=0;late=0;late_text=wanted+'// 응답 대기 중 새 입력\n'
  def recovery_route(request):
   global armed,rid,lost,late
   if not request.request.url.startswith(origin):external.append(request.request.url);request.abort();return
   body=request.request.post_data_json if request.request.method=='POST' else None
   if isinstance(body,dict) and body.get('op')=='invoke' and body.get('endpoint')=='saveDraft' and armed:rid=body['requestId']
   if isinstance(body,dict) and body.get('op')=='update' and rid:
    response=request.fetch();payload=response.json()
    for result in payload.get('results',[]):
     if result['requestId']!=rid or not result.get('ok'):continue
     mode=armed;armed=None;rid=None
     if mode=='lost':
      lost+=1;result['ok']=False;result.pop('result',None);result['error']={'code':'consumer_error'}
     elif mode=='late':
      late+=1;d=code_dialog();edit(d,late_text);d.locator('[data-code-save]').click()
    request.fulfill(response=response,json=payload);return
   request.continue_()
  page.unroute('**/*');page.route('**/*',recovery_route);author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_contain_text('consumer_error',timeout=30000);assert lost==1 and private()==pending and preserved();graphid=impl+'/body:common';data=invoke('blueprint',{'action':'read','id':graphid})['result']['result'];assert next(n for n in data['nodes'] if n['id']=='body')['source']==wanted and data['conversionOriginHash'];before_ids=[r['id'] for r in invoke('blueprint',{'action':'featureBodies','feature':feature})['result']['result']['rows']];checked('두 구현 중 원본 provide 대상만 열며 실제 Save 응답 유실을 주입해도 입력과 원본/다른 구현을 보존한다')
  idle();page.close();stop();start(1);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);assert private()==pending and preserved();d=code_dialog();assert wanted in d.locator('[data-code-source]').input_value();d.locator('[data-code-cancel]').click();page.unroute('**/*');page.route('**/*',recovery_route);armed='late';rid=None;author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_contain_text('새 입력',timeout=30000);rows=private();assert late==1 and len(rows)==1 and rows[0][1]['text']==late_text and preserved();assert [r['id'] for r in invoke('blueprint',{'action':'featureBodies','feature':feature})['result']['result']['rows']]==before_ids;checked('응답 유실 후 cold 복원·재시도는 같은 전환을 확인하며 중복 생성 없이 저장 대기 중 새 입력을 남긴다')
  author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_have_text('저장됨',timeout=30000);assert private()==[] and preserved();data=invoke('blueprint',{'action':'read','id':graphid})['result']['result'];assert next(n for n in data['nodes'] if n['id']=='body')['source']==late_text;author.locator('[data-bp-complete]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=30000)
  for cb in review.locator('[data-review-id]').all():cb.check()
  if review.locator('[data-additional-changes]').count():
   review.locator('[data-review-advanced]').click();ack=review.locator('[data-advanced-reviewed]')
   if ack.count():ack.check()
  expect(review.locator('#confirm')).to_be_enabled(timeout=30000);review.locator('#confirm').click();expect(review).to_have_count(0,timeout=60000);assert 'blueprint common' in file.read_text() and preserved(True);checked('늦게 입력한 본문은 별도 Save·실제 컴파일·명시적 Confirm으로만 반영되고 다른 구현/다른 target/C# 원본을 보존한다');page.screenshot(path=str(case/'conversion-recovery-confirmed.png'));page.close();browser.close();assert not errors and not external,(errors,external)

except Exception:
 try:(case/'failure-state.json').write_text(json.dumps(state(),ensure_ascii=False,indent=2));(case/'failure.json').write_text(json.dumps({'traffic':traffic,'errors':errors},ensure_ascii=False,indent=2));page.screenshot(path=str(case/'failure.png'))
 except Exception:pass
 print('격리 실패 자료 '+str(case));raise
finally:stop()
record={'checks':checks,'errors':errors,'external':external,'actualEngine':True,'actualUIConversionFlow':True,'nativeWindows':False,'accountOrInference':False,'projectRun':False,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False,indent=2))
