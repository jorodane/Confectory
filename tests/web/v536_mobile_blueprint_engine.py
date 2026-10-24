"""v536 documents/floating over Pack Manager in the actual generated engine.
No account/grant/model invocation. Preserves source bytes and original draft proof.
"""
import json,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());fixture=pathlib.Path(sys.argv[3]).resolve();assert fixture==repo.parent/'scratch/v508-elements/actual13-source-fixture'
case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-mobile-blueprint-'));project=case/'owned project';shutil.copytree(fixture/'owned project',project,ignore=shutil.ignore_patterns('.confectory','.build'));storage=case/'profile';storage.mkdir();original={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file() and '.confectory' not in p.parts};id='Owned.Elements::Serial';text='9223372036854775804';description='재시작할 미적용 설명 한글';env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(storage),CONFECTORY_ENTRY_STORAGE=str(storage),CONFECTORY_MCP_DIRECTORY=str(case/'instances'),CONFECTORY_WEB_PROJECT=str(project/'project.cproj'),CONFECTORY_DOTNET=env.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet'));env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];host=None;log=None;errors=[];external=[];checks=[]
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

try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(0);page=setup();page.set_viewport_size({'width':390,'height':844});page.locator('[data-mobile-files]').click();b=page.locator('.window[data-key="browser:project:mobile"]');b.locator('[data-tab=feature]').click();row=b.locator('[data-object="Owned.Elements::Serial"]');expect(row).to_be_visible(timeout=30000);row.press('Enter');decl=page.locator('.window[data-key=declaration]');expect(decl.locator('[data-function-write-direct]')).to_be_visible(timeout=30000);decl.locator('[data-function-write-direct]').click();author=page.locator('.window[data-key=blueprint]');flow=author.locator('[aria-label="카드 흐름 편집"]');expect(flow).to_be_visible(timeout=30000);expect(page.locator('[data-window-tab="blueprint"]')).to_have_attribute('aria-selected','true');expect(author.locator('.bp-layout')).to_have_attribute('inert','');expect(flow.locator('[data-flow-node="body"]')).to_be_visible();assert len(flow.locator('[data-flow-node]').all())>=3;page.screenshot(path=str(case/'initial-card-flow.png'));(case/'geometry.json').write_text(json.dumps({'host':flow.bounding_box(),'tabs':flow.locator('.bp-flow-tabs').bounding_box()},indent=2));checked('actual owned serial graph opens the v536 mobile card document with original tabs and inert desktop canvas, without demo graph or model calls')
  body=flow.locator('[data-flow-node="body"]');body.click();inspector=page.locator('.bp-flow-inspector:not([hidden])');expect(inspector).to_be_visible();text=inspector.locator('[data-flow-node-description]');pending='모바일에서 편집한 설명 한글 😀\n입력은 보관됩니다.';text.fill(pending);inspector.locator('[data-flow-code]').click();script=page.get_by_role('dialog',name='C# Script · body',exact=True);expect(script).to_be_visible();code=script.locator('[data-code-source]');original_code=code.input_value();code.evaluate("e=>e.setSelectionRange(e.value.indexOf('\\n{\\n')+3,e.value.lastIndexOf('\\n}\\n'))");page.keyboard.insert_text('return 1;');script.locator('[data-code-cancel]').click();expect(script).to_have_count(0);expect(text).to_have_value(pending);inspector.locator('[data-flow-back]').click();expect(body).to_contain_text(pending);page.set_viewport_size({'width':1440,'height':1000});expect(flow).to_be_hidden();expect(author.locator('[data-bp-node="body"] [data-inline-description]')).to_have_value(pending);page.set_viewport_size({'width':390,'height':844});expect(flow).to_be_visible();body.click();expect(inspector.locator('[data-flow-node-description]')).to_have_value(pending);page.screenshot(path=str(case/'node-inspector.png'));inspector.locator('[data-flow-back]').click();assert all((project/k).read_bytes()==v for k,v in original.items());checked('full-screen original node description keeps Korean/emoji/newline across back and width changes; explicit Script cancellation preserves prior body and source bytes')
  author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_have_text('저장됨',timeout=60000);assert all((project/k).read_bytes()==v for k,v in original.items());body=flow.locator('[data-flow-node="body"]');body.click();text=inspector.locator('[data-flow-node-description]');cold='재시작 전 미저장 입력 🧁';text.fill(cold);inspector.locator('[data-flow-done]').click();page.evaluate('()=>confectoryFlushPresentation()');before=state();blueprint=[(k,v) for k,v in before['presentation']['inputs']['blueprint'] if '|v508-author|' in k];assert any(v['text']==cold for k,v in blueprint);page.close();stop();start(1);page=setup();page.set_viewport_size({'width':390,'height':844});author=page.locator('.window[data-key=blueprint]');flow=author.locator('[aria-label="카드 흐름 편집"]');expect(flow).to_be_visible(timeout=60000);body=flow.locator('[data-flow-node="body"]');expect(body).to_contain_text(cold);body.click();inspector=page.locator('.bp-flow-inspector:not([hidden])');expect(inspector.locator('[data-flow-node-description]')).to_have_value(cold);inspector.locator('[data-flow-back]').click();author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_have_text('저장됨',timeout=60000);assert all((project/k).read_bytes()==v for k,v in original.items());checked('actual Save writes only the shared checkpoint; cold process restart restores unsaved mobile text and proven ownership before explicit restored Save')
  # Intent changes invalidate the previous implementation receipt. A real user
  # must explicitly acknowledge the existing Script before final compilation.
  author.locator('[data-bp-complete]').click();expect(author.locator('.bp-status')).to_contain_text('본문',timeout=30000);assert page.locator('.window[data-key=review]').count()==0;flow.locator('[data-flow-node="body"]').click();inspector=page.locator('.bp-flow-inspector:not([hidden])');inspector.locator('[data-flow-code]').click();script=page.get_by_role('dialog',name='C# Script · body',exact=True);script.locator('[data-code-save]').click();inspector.locator('[data-flow-back]').click();author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_have_text('저장됨',timeout=60000)
  author.locator('[data-bp-complete]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=60000);assert all((project/k).read_bytes()==v for k,v in original.items());review.locator('[data-reject]').click();assert all((project/k).read_bytes()==v for k,v in original.items());page.locator('[data-window-tab="blueprint"]').click();expect(flow).to_be_visible();author.locator('[data-bp-complete]').click();expect(review).to_be_visible(timeout=60000)
  for cb in review.locator('[data-review-id]').all():cb.check()
  if review.locator('[data-additional-changes]').count():
   review.locator('[data-review-advanced]').click();ack=review.locator('[data-advanced-reviewed]')
   if ack.count():ack.check()
  expect(review.locator('#confirm')).to_be_enabled(timeout=30000);review.locator('#confirm').click();expect(review).to_have_count(0,timeout=60000);changed=[k for k,v in original.items() if (project/k).read_bytes()!=v];assert changed and all(k.startswith('blueprints/') for k in changed),changed;source=json.loads(next((project/'blueprints').glob('*.graph.json')).read_text());assert next(n for n in source['nodes'] if n['id']=='body')['intent']==cold;page.screenshot(path=str(case/'confirmed-mobile.png'));checked('mobile completion remains separate from explicit selected Review/compiler Confirm and modifies only owned Blueprint files')
  assert not errors and not external,(errors,external);record={'checks':checks,'errors':errors,'actualEngine':True,'browserViewport':{'width':390,'height':844},'nativeWindowsOrMobileHardware':False,'actualCredentialsOrInference':False,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False,indent=2));page.close();stop();browser.close()
except Exception:
 try:(case/'failure.json').write_text(json.dumps({'state':state(),'traffic':traffic,'errors':errors},ensure_ascii=False,indent=2))
 except Exception:pass
 try:page.screenshot(path=str(case/'failure.png'))
 except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case),flush=True);raise
finally:stop()
