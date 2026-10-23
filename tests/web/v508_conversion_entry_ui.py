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

impl='Owned.Elements::AttackBody';feature='Owned.Elements::Attack';file=project/'AttackBody.celem';text=file.read_text();at=text.rindex('}');file.write_text(text[:at]+'body windows "AttackWindows.csbody";'+text[at:]);windows=project/'AttackWindows.csbody';windows.write_bytes('// 다른 실행 대상\r\nreturn amount + 5;\r\n'.encode());body=project/'Attack.csbody';body.write_bytes(b'\xef\xbb\xbf'+'// 원본 한글 😀\r\nreturn amount + 1;\r\n'.encode());physical={str(p):p.read_bytes() for p in project.rglob('*') if p.is_file() and '.confectory' not in p.parts};wanted='// 선택한 common 복사 본문 한글 😀\nreturn amount + 17;\n'
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
  before=checkpoint();d=code_dialog();assert '// 원본 한글 😀\nreturn amount + 1;' in d.locator('[data-code-source]').input_value();d.locator('[data-code-cancel]').click();assert private()==[] and checkpoint()==before and preserved();d=code_dialog();d.locator('[data-code-save]').click();saved=private();assert len(saved)==1 and saved[0][1]['text']=='\ufeff// 원본 한글 😀\r\nreturn amount + 1;\r\n' and '|body:'+impl+'/body:common|' in saved[0][0];checked('실제 원본 C# 진입·취소와 편집 없는 코드 저장은 BOM/CRLF/한글 원본과 Windows 대상 파일을 보존하며 common만 명시한다')
  d=code_dialog();edit(d,wanted);d.locator('[data-code-save]').click();pending=private();assert pending[0][1]['text']==wanted and checkpoint()==before and preserved();page.screenshot(path=str(case/'conversion-preview.png'));page.close();stop();start(1);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-internal-code]')).to_be_enabled(timeout=30000);assert private()==pending and preserved();d=code_dialog();assert wanted in d.locator('[data-code-source]').input_value();edit(d,'return amount + 99;');d.locator('[data-code-cancel]').click();assert private()==pending;checked('비공개 C# 미리보기 본문은 실제 프로세스 재시작으로 복구되고 재편집 취소는 이전 미저장 입력을 유지한다')
  author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_have_text('저장됨',timeout=30000);assert private()==[] and preserved();graphid=impl+'/body:common';data=invoke('blueprint',{'action':'read','id':graphid})['result']['result'];assert next(n for n in data['nodes'] if n['id']=='body')['source']==wanted and len(data['reviewIds'])==3;page.close();stop();start(2);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);d=code_dialog();assert wanted in d.locator('[data-code-source]').input_value();d.locator('[data-code-cancel]').click();assert preserved();checked('실제 Save와 두 번째 cold 복원은 선택한 구현/본문만 노드 초안으로 저장하며 원본 C#/다른 target은 아직 미반영 상태다')
  author.locator('[data-bp-complete]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=30000)
  for cb in review.locator('[data-review-id]').all():cb.check()
  if review.locator('[data-additional-changes]').count():
   review.locator('[data-review-advanced]').click();ack=review.locator('[data-advanced-reviewed]')
   if ack.count():ack.check()
  expect(review.locator('#confirm')).to_be_enabled(timeout=30000);assert preserved();review.locator('#confirm').click();expect(review).to_have_count(0,timeout=60000);expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);assert 'blueprint common' in file.read_text() and 'body windows "AttackWindows.csbody"' in file.read_text() and preserved(True);checked('원본 기능 완성→변경 검토→실제 컴파일→명시적 그룹 Confirm만 common을 전환하며 C# 및 다른 실행 대상은 보존한다')
  d=code_dialog();edit(d,wanted+'// 확정 후 새 입력\n');d.locator('[data-code-save]').click();after=private();assert len(after)==1;page.close();stop();start(3);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);assert private()==after and preserved(True);d=code_dialog();assert '// 확정 후 새 입력' in d.locator('[data-code-source]').input_value();d.locator('[data-code-cancel]').click();page.screenshot(path=str(case/'conversion-confirmed-restored.png'));checked('확정 후 같은 창의 새 본문 입력은 재시작해도 구현 문맥과 함께 복구된다');page.close();browser.close();assert not errors and not external,(errors,external)
except Exception:
 try:(case/'failure-state.json').write_text(json.dumps(state(),ensure_ascii=False,indent=2));(case/'failure.json').write_text(json.dumps({'traffic':traffic,'errors':errors},ensure_ascii=False,indent=2));page.screenshot(path=str(case/'failure.png'))
 except Exception:pass
 print('격리 실패 자료 '+str(case));raise
finally:stop()
record={'checks':checks,'errors':errors,'external':external,'actualEngine':True,'actualUIConversionFlow':True,'nativeWindows':False,'accountOrInference':False,'projectRun':False,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False,indent=2))
