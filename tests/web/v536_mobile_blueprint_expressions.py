"""v536 mobile Blueprint expressions in the actual generated engine.
No account/grant/model invocation. Preserves source bytes and original draft proof.
"""
import json,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());fixture=pathlib.Path(sys.argv[3]).resolve();assert fixture==repo.parent/'scratch/v508-elements/actual13-source-fixture'
case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-mobile-expressions-'));project=case/'owned project';shutil.copytree(fixture/'owned project',project,ignore=shutil.ignore_patterns('.confectory','.build'));storage=case/'profile';storage.mkdir();original={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file() and '.confectory' not in p.parts};id='Owned.Elements::Serial';text='9223372036854775804';description='재시작할 미적용 설명 한글';env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(storage),CONFECTORY_ENTRY_STORAGE=str(storage),CONFECTORY_MCP_DIRECTORY=str(case/'instances'),CONFECTORY_WEB_PROJECT=str(project/'project.cproj'),CONFECTORY_DOTNET=env.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet'));env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];host=None;log=None;errors=[];external=[];checks=[]
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

def setup():
 context=browser.new_context(viewport={'width':390,'height':844},has_touch=True,is_mobile=True);page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',observe);page.route('**/*',route);goto_editor(page,url);return page

def open_author():
 page.locator('[data-mobile-files]').click();b=page.locator('.window[data-key="browser:project:mobile"]');b.locator('[data-tab=feature]').click();row=b.locator('[data-object="Owned.Elements::Serial"]');expect(row).to_be_visible(timeout=30000);row.get_by_role('button',name='정의 열기',exact=True).click();decl=page.locator('.window[data-key=declaration]');expect(decl.locator('[data-function-write-direct]')).to_be_visible(timeout=30000);decl.locator('[data-function-write-direct]').click();expect(page.locator('.window[data-key=blueprint] [aria-label="카드 흐름 편집"]')).to_be_visible(timeout=30000)
def graph():return invoke('blueprint',{'action':'read','id':'Owned.Elements::SerialBlueprintBody/body:common'})['result']['result']
def pending():page.evaluate('()=>confectoryFlushPresentation()');return [(k,v) for k,v in state()['presentation']['inputs']['blueprint'] if '|v508-author|' in k]
def source_same():assert all((project/k).read_bytes()==v for k,v in original.items())
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(0);page=setup();open_author();author=page.locator('.window[data-key=blueprint]');flow=author.locator('[aria-label="카드 흐름 편집"]');flow.locator('[data-flow-node="body"]').click();inspector=page.locator('.bp-flow-inspector:not([hidden])');menu=page.get_by_role('dialog',name='핀 값 선택',exact=True)
  def part(path):return inspector.locator('[data-flow-value="field:seed"][data-value-path="'+json.dumps(path,separators=(',',':'))+'"]')
  def literal(path,text):
   part(path).click();expect(menu).to_be_visible();menu.get_by_role('searchbox',name='값 검색').fill(text);expect(menu.locator('[data-value-new]')).to_be_visible();menu.locator('[data-value-new]').click();expect(menu).to_have_count(0);expect(inspector).to_be_visible()
  part([]).click();menu.locator('[data-value-operator="+"]').click();expect(inspector).to_be_visible();expect(part([0])).to_be_visible();part([0]).click();menu.get_by_role('button',name='입력 · seed',exact=True).click();part([1]).click();menu.locator('[data-value-operator="*"]').click();expect(inspector).to_be_visible();part([1,0]).click();menu.get_by_role('button',name='입력 · other',exact=True).click();literal([1,1],'9223372036854775807');expect(part([1,1])).to_contain_text('9223372036854775807');assert inspector.locator('.bp-flow-expression').count()==2;page.screenshot(path=str(case/'nested-expression.png'));source_same();checked('original mobile expression cards expose nested operator/operand paths and retain the inspector through owned rerenders with exact long tokens')
  part([1]).click();menu.locator('[data-value-operator="/"]').click();literal([1,1],'0');inspector.locator('[data-flow-done]').click();author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_contain_text('0으로 나눌',timeout=30000);source_same();assert any('"operator":"/"' in v.get('text','') for k,v in pending());flow.locator('[data-flow-node="body"]').click();literal([1,1],'2');part([1,1]).click();menu.get_by_role('searchbox',name='값 검색').fill('9223372036854775808');expect(menu.get_by_role('status')).to_contain_text('범위');page.keyboard.press('Escape');expect(part([1,1])).to_contain_text('2');inspector.locator('[data-flow-value="field:title"]').click();title='실제 줄바꿈\n한글 "값" 🧁';menu.get_by_role('searchbox',name='값 검색').fill(json.dumps(title,ensure_ascii=False));menu.locator('[data-value-new]').click();expect(inspector.locator('[data-flow-value="field:title"]')).to_contain_text('한글 "값" 🧁');source_same();checked('invalid nested division fails checked Save, corrected operand survives literal cancellation, and Korean quoted multiline text remains in the owned input')
  inspector.locator('[data-flow-done]').click();private=pending();assert any('"operator":"+"' in v.get('text','') for k,v in private);page.set_viewport_size({'width':1440,'height':1000});expect(flow).to_be_hidden();expect(author.locator('[data-expression-operator="+"]')).to_be_visible();page.set_viewport_size({'width':390,'height':844});expect(flow).to_be_visible();pending();page.close();stop();start(1);page=setup();author=page.locator('.window[data-key=blueprint]');flow=author.locator('[aria-label="카드 흐름 편집"]');expect(flow).to_be_visible(timeout=60000);flow.locator('[data-flow-node="body"]').click();inspector=page.locator('.bp-flow-inspector:not([hidden])');expect(part([1,1])).to_contain_text('2');inspector.locator('[data-flow-done]').click();author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_have_text('저장됨',timeout=60000);body=next(n for n in graph()['nodes'] if n['id']=='body');args={a['name']:a['valueJson'] for a in body['arguments']};tree=json.loads(args['seed']);assert tree=={'binary':{'operator':'+','operands':[{'input':'seed'},{'binary':{'operator':'/','operands':[{'input':'other'},{'constant':2}]}}]}},tree;assert json.loads(args['title'])['constant']==title;source_same();checked('nested expression and exact multiline input survive desktop/mobile width switch and cold restart before real checked Save')
  author.locator('[data-bp-complete]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=60000);source_same()
  for cb in review.locator('[data-review-id]').all():cb.check()
  if review.locator('[data-additional-changes]').count():
   review.locator('[data-review-advanced]').click();ack=review.locator('[data-advanced-reviewed]')
   if ack.count():ack.check()
  review.locator('#confirm').click();expect(review).to_have_count(0,timeout=60000);changed=[k for k,v in original.items() if (project/k).read_bytes()!=v];assert changed and all(k.startswith('blueprints/') for k in changed),changed;checked('mobile nested-expression source update requires explicit selected compiler Confirm and preserves other original files')
  assert not errors and not external,(errors,external);record={'checks':checks,'actualEngine':True,'touchEmulation':True,'errors':errors,'changed':changed,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False,indent=2));page.close();stop();browser.close()
except Exception:
 try:(case/'failure.json').write_text(json.dumps({'state':state(),'traffic':traffic,'errors':errors},ensure_ascii=False,indent=2))
 except Exception:pass
 try:page.screenshot(path=str(case/'failure.png'))
 except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case),flush=True);raise
finally:stop()
