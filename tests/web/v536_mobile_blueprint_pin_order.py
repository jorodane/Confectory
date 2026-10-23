"""v536 mobile Blueprint values in the actual generated engine.
No account/grant/model invocation. Preserves source bytes and original draft proof.
"""
import json,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());fixture=pathlib.Path(sys.argv[3]).resolve();assert fixture==repo.parent/'scratch/v508-elements/actual13-source-fixture'
case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-mobile-pin-order-'));project=case/'owned project';shutil.copytree(fixture/'owned project',project,ignore=shutil.ignore_patterns('.confectory','.build'));storage=case/'profile';storage.mkdir();original={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file() and '.confectory' not in p.parts};id='Owned.Elements::Serial';text='9223372036854775804';description='재시작할 미적용 설명 한글';env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(storage),CONFECTORY_ENTRY_STORAGE=str(storage),CONFECTORY_MCP_DIRECTORY=str(case/'instances'),CONFECTORY_WEB_PROJECT=str(project/'project.cproj'),CONFECTORY_DOTNET=env.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet'));env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];host=None;log=None;errors=[];external=[];checks=[]
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
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(0);page=setup();open_author();author=page.locator('.window[data-key=blueprint]');flow=author.locator('[aria-label="카드 흐름 편집"]');flow.locator('[data-flow-tab=inputs]').click();defs=flow.locator('[data-flow-declarations]');fields=lambda:defs.locator('[data-mobile-contract-field]').evaluate_all('(xs)=>xs.map(x=>x.dataset.mobileContractField)');initial=fields();seed=defs.locator('[data-mobile-contract-field=seed]');seed.locator('[data-signature-remove]').click();expect(page.locator('#toast')).to_contain_text('연결');assert fields()==initial and not pending();source_same();checked('original mobile root-input removal refuses a used binding without clearing source or any existing private input')
  defs.locator('[data-mobile-contract-add]').click();extra=defs.locator('[data-mobile-contract-field=input1]');expect(extra).to_be_visible();extra.locator('[data-signature-remove]').click();expect(extra).to_have_count(0);defs.locator('[data-mobile-contract-field=seed] [data-order-step="1"]').click();expect(defs.locator('[data-mobile-contract-field]').first).to_have_attribute('data-mobile-contract-field','other');assert fields()==[initial[1],initial[0],*initial[2:]];page.screenshot(path=str(case/'ordered-mobile-inputs.png'));author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_have_text('저장됨',timeout=60000);assert [a['name'] for a in graph()['signature']['args']]==fields();source_same();checked('original touch arrows reorder the exact owned root contract; adding then removing an unused pin and checked Save preserve name-bound existing values')
  flow.locator('[data-flow-tab=outputs]').click();output=flow.locator('[data-mobile-contract-field=return]');eye=output.locator('[data-output-exposed]');expect(eye).to_have_attribute('aria-pressed','false');eye.click();expect(output.locator('[data-output-exposed]')).to_have_attribute('aria-pressed','true');output.locator('[data-output-exposed]').click();expect(output.locator('[data-output-exposed]')).to_have_attribute('aria-pressed','false');output.locator('[data-signature-remove]').click();dialog=page.get_by_role('dialog',name='출력 삭제',exact=True);expect(dialog).to_be_visible();dialog.locator('[data-output-delete-cancel]').click();expect(dialog).to_have_count(0);expect(output).to_be_visible();author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_have_text('저장됨',timeout=60000);source_same();checked('mobile public-output eye delegates existing SourceContext exposure only, and original output-delete cancellation preserves the declaration and connected output')
  flow.locator('[data-flow-tab=flow]').click();detached=flow.locator('.bp-flow-detached [data-flow-node]').first;node=detached.get_attribute('data-flow-node');detached.click();inspector=page.locator('.bp-flow-inspector:not([hidden])');inputs=inspector.locator('[data-flow-node-inputs]');inputs.locator('[data-mobile-contract-add]').click();inputs.locator('[data-mobile-contract-add]').click();expect(inputs.locator('[data-mobile-contract-field]')).to_have_count(2);inputs.locator('[data-mobile-contract-field=input2] [data-order-step="-1"]').click();expect(inputs.locator('[data-mobile-contract-field]').first).to_have_attribute('data-mobile-contract-field','input2');inspector.locator('[data-flow-code]').click();script=page.get_by_role('dialog',name='C# Script · 내부 기능',exact=True);expect(script).to_be_visible();assert script.locator('[data-code-source]').input_value().index('string input2')<script.locator('[data-code-source]').input_value().index('string input1');script.locator('[data-code-save]').click();expect(script).to_have_count(0);inspector.locator('[data-flow-done]').click();author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_have_text('저장됨',timeout=60000);saved=next(n for n in graph()['nodes'] if n['id']==node);assert [a['name'] for a in saved['signature']['args']]==['input2','input1'];source_same();checked('original mobile node-input arrows keep guarded C# parameter order consistent and Save only the selected node contract')
  pending();page.close();stop();start(1);page=setup();tab=page.locator('[data-window-tab=blueprint]');expect(tab).to_be_visible(timeout=60000);tab.click();author=page.locator('.window[data-key=blueprint]');flow=author.locator('[aria-label="카드 흐름 편집"]');expect(flow).to_be_visible(timeout=60000);flow.locator('[data-flow-tab=inputs]').click();defs=flow.locator('[data-flow-declarations]');assert fields()==[initial[1],initial[0],*initial[2:]];flow.locator('[data-flow-tab=flow]').click();flow.locator('[data-flow-node="'+node+'"]').click();inspector=page.locator('.bp-flow-inspector:not([hidden])');expect(inspector.locator('[data-flow-node-inputs] [data-mobile-contract-field]').first).to_have_attribute('data-mobile-contract-field','input2');inspector.locator('[data-flow-done]').click();author.locator('[data-bp-complete]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=60000);source_same()
  for cb in review.locator('[data-review-id]').all():cb.check()
  if review.locator('[data-additional-changes]').count():
   review.locator('[data-review-advanced]').click();ack=review.locator('[data-advanced-reviewed]')
   if ack.count():ack.check()
  review.locator('#confirm').click();expect(review).to_have_count(0,timeout=60000);changed=[k for k,v in original.items() if (project/k).read_bytes()!=v];assert changed and all(k.startswith('blueprints/') or k in ['elements/Serial.celem','elements/SerialBlueprintBody.celem'] for k in changed),changed;assert not errors and not external,(errors,external);checked('root/node mobile contract order survives actual cold restart and requires explicit compiler Confirm while unrelated sources remain byte-identical')
  record={'checks':checks,'actualEngine':True,'touchEmulation':True,'actualCredentialsOrInference':False,'nativeWindowsOrMobileHardware':False,'changed':changed,'errors':errors,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False,indent=2));page.close();stop();browser.close()
except Exception:
 try:(case/'failure.json').write_text(json.dumps({'state':state(),'traffic':traffic,'errors':errors},ensure_ascii=False,indent=2))
 except Exception:pass
 try:page.screenshot(path=str(case/'failure.png'))
 except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case),flush=True);raise
finally:stop()
