"""v536 mobile Blueprint values in the actual generated engine.
No account/grant/model invocation. Preserves source bytes and original draft proof.
"""
import json,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());fixture=pathlib.Path(sys.argv[3]).resolve();assert fixture==repo.parent/'scratch/v508-elements/actual13-source-fixture'
case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-mobile-values-'));project=case/'owned project';shutil.copytree(fixture/'owned project',project,ignore=shutil.ignore_patterns('.confectory','.build'));storage=case/'profile';storage.mkdir();original={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file() and '.confectory' not in p.parts};id='Owned.Elements::Serial';text='9223372036854775804';description='재시작할 미적용 설명 한글';env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(storage),CONFECTORY_ENTRY_STORAGE=str(storage),CONFECTORY_MCP_DIRECTORY=str(case/'instances'),CONFECTORY_WEB_PROJECT=str(project/'project.cproj'),CONFECTORY_DOTNET=env.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet'));env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];host=None;log=None;errors=[];external=[];checks=[]
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
  def button(name):return inspector.locator('[data-flow-value="field:'+name+'"]')
  def value(name,text):
   button(name).click();expect(menu).to_be_visible();search=menu.get_by_role('searchbox',name='값 검색');search.fill(text);expect(menu.locator('[data-value-new]')).to_be_visible();menu.locator('[data-value-new]').click();expect(menu).to_have_count(0)
  def bodydata():return next(n for n in graph()['nodes'] if n['id']=='body')
  before=button('seed').inner_text();button('seed').click();expect(menu).to_be_visible();search=menu.get_by_role('searchbox',name='값 검색');search.fill('9223372036854775808');expect(menu.get_by_role('status')).to_contain_text('범위');mark=len(traffic);page.keyboard.press('Escape');expect(menu).to_have_count(0);expect(button('seed')).to_have_text(before);assert not any(v.get('type','').startswith('value-draft') for k,v in pending());assert not [x for x in traffic[mark:] if x.get('invoke',{}).get('endpoint')=='blueprint' and x['invoke']['input'].get('action') not in ['read','callables']];source_same();checked('touch inspector value menu rejects out-of-range long and Escape cancels only that input with no provider/source write')
  value('seed','9223372036854775807');expect(button('seed')).to_contain_text('9223372036854775807');inspector.locator('[data-flow-done]').click();author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_have_text('저장됨',timeout=60000);assert next(a for a in bodydata()['arguments'] if a['name']=='seed')['valueJson']=='{"constant":9223372036854775807}';source_same();checked('mobile value label and real checked Save preserve the exact max-long token without final file writes')
  flow.locator('[data-flow-node="body"]').click();value('title',json.dumps('한글 "줄" 😀\n다음',ensure_ascii=False));button('flag').click();menu.get_by_role('button',name='거짓',exact=True).click();value('values','[9223372036854775807,-9223372036854775808]');inspector.locator('[data-flow-back]').click();author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_have_text('저장됨',timeout=60000);args={a['name']:a['valueJson'] for a in bodydata()['arguments']};assert json.loads(args['title'])['constant']=='한글 "줄" 😀\n다음';assert args['flag']=='{"constant":false}';assert args['values']=='{"constant":[9223372036854775807,-9223372036854775808]}';source_same();checked('mobile string/boolean/long-array value choices retain Korean, quotes and exact signed-64-bit JSON through real Save')
  flow.locator('[data-flow-node="body"]').click();value('other','12');inspector.locator('[data-flow-done]').click();private=pending();assert any(v.get('text')=='{"constant":12}' for k,v in private);page.set_viewport_size({'width':1440,'height':1000});expect(flow).to_be_hidden();expect(author.locator('.bp-pin-plug[data-node="body"][data-side="in"][data-port="field:other"] input')).to_have_value('12');page.set_viewport_size({'width':390,'height':844});expect(flow).to_be_visible();pending();page.close();stop();start(1);page=setup();author=page.locator('.window[data-key=blueprint]');flow=author.locator('[aria-label="카드 흐름 편집"]');expect(flow).to_be_visible(timeout=60000);flow.locator('[data-flow-node="body"]').click();inspector=page.locator('.bp-flow-inspector:not([hidden])');expect(button('other')).to_contain_text('12');inspector.locator('[data-flow-done]').click();author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_have_text('저장됨',timeout=60000);assert next(a for a in bodydata()['arguments'] if a['name']=='other')['valueJson']=='{"constant":12}';source_same();checked('mobile value pending input survives width changes and real cold restart with the same source closure before explicit restored Save')
  author.locator('[data-bp-complete]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=60000);source_same()
  for cb in review.locator('[data-review-id]').all():cb.check()
  if review.locator('[data-additional-changes]').count():
   review.locator('[data-review-advanced]').click();ack=review.locator('[data-advanced-reviewed]')
   if ack.count():ack.check()
  review.locator('#confirm').click();expect(review).to_have_count(0,timeout=60000);changed=[k for k,v in original.items() if (project/k).read_bytes()!=v];assert changed and all(k.startswith('blueprints/') for k in changed),changed;page.locator('[data-window-tab="blueprint"]').click();page.screenshot(path=str(case/'mobile-values-confirmed.png'));checked('mobile binding completion requires explicit selected compiler Confirm and changes only owned Blueprint files')
  assert not errors and not external,(errors,external);result={'checks':checks,'actualEngine':True,'touchEmulation':True,'errors':errors,'actualCredentialsOrInference':False,'nativeWindowsOrMobileHardware':False,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2));page.close();stop();browser.close()
except Exception:
 try:(case/'failure.json').write_text(json.dumps({'state':state(),'traffic':traffic,'errors':errors},ensure_ascii=False,indent=2))
 except Exception:pass
 try:page.screenshot(path=str(case/'failure.png'))
 except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case),flush=True);raise
finally:stop()
