"""Legacy private body record reopening on the original root C# modal.
Only isolated fixture presentation JSON is converted to the prior persisted input shape.
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

id='Owned.Elements::Mode';fn='function '+id+' (long value,out long total) -> long {provide '+id+' with Owned.Elements::ModeBody;}';impl='implementation Owned.Elements::ModeBody for '+id+' (long nativeValue,out long nativeTotal) -> long {body common "Mode.csbody";}'
(project/'elements/Mode.celem').write_text(fn);(project/'elements/ModeBody.celem').write_text(impl);(project/'Mode.csbody').write_text('nativeValue += 1;nativeTotal=nativeValue;return nativeValue;');manifest=project/'project.cproj';text=manifest.read_text();at=text.rfind('}');manifest.write_text(text[:at]+'element Mode function "elements/Mode.celem";element ModeBody implementation "elements/ModeBody.celem";'+text[at:])
def sdk(operation,**body):
 p=subprocess.run([env['CONFECTORY_DOTNET'],str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps({'operation':operation,**body}),text=True,capture_output=True,env=env,check=True);v=json.loads(p.stdout);assert v['ok'],v;return v['result']
converted=sdk('blueprintConversion',project=str(project/'project.cproj'),id='Owned.Elements::ModeBody',text=impl,target='common',graphPath='blueprints/mode.graph.json',nodePath='mode.node.json');(project/'elements/ModeBody.celem').write_text(converted['implementation']);(project/'blueprints/mode.graph.json').write_text(json.dumps(converted['graph']));(project/'blueprints/mode.node.json').write_text(json.dumps(converted['node']));original={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file() and '.confectory' not in p.parts}

try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(0);page=setup()
  def idle():page.evaluate('async()=>await confectoryFlushPresentation()')
  def browse():
   page.locator('#workspace').click(button='right',position={'x':700,'y':300});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();return page.locator('.window[data-key^="browser:project:"]:visible')
  b=browse();b.locator('[data-object="Owned.Elements::Monster"]').get_by_role('button',name='정의 열기',exact=True).click();monster=page.locator('.window[data-key=schema]');expect(monster.locator('.object-title-description')).to_be_visible(timeout=30000);b.locator('[data-close]').click();monster.locator('.object-title-description').fill('공개 출력과 별개인 미저장 설명');monster.locator('[data-close]').click();idle()
  b=browse();b.locator('[data-tab=feature]').click();b.locator('[data-object="'+id+'"]').get_by_role('button',name='정의 열기',exact=True).click();b.locator('[data-close]').click();page.locator('.window[data-key=declaration] [data-function-write-direct]').click();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-node=body] [data-internal-code]')).to_be_visible(timeout=30000);graphid=invoke('blueprint',{'action':'list','feature':id})['result']['result']['rows'][0]['id']
  def graph():return invoke('blueprint',{'action':'read','id':graphid})['result']['result']
  def originals():return all((project/k).read_bytes()==v for k,v in original.items())
  def group():return invoke('browserDrafts',{'action':'status','ids':[id]})['result']['result']
  def cancel():
   s=group();assert len(s['ids'])==4;snap={'action':'discard','ids':s['ids'],'revisions':[r['revision'] for r in s['rows']],'hashes':[r['hash'] for r in s['rows']],'ownerHash':s['ownerHash'],'checkpointHash':s['checkpointHash']};invoke('browserDrafts',snap)
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
  def original_files():return all((project/k).read_bytes()==v for k,v in original.items())
  def node():return next(n for n in graph()['nodes'] if n['id']=='body')
  def private():idle();return [(k,v) for k,v in state()['presentation']['inputs']['blueprint'] if v['type']=='root-script']
  def dialog():author.locator('[data-bp-overview-node="body"]').click();author.locator('[data-bp-node="body"] [data-internal-code]').click();return page.get_by_role('dialog',name='C# Script · body',exact=True)
  def edit(d,region,text):
   code=d.locator('[data-code-source]');code.evaluate('(el,region)=>{const spans=[...el.closest(".bp-script-editor").querySelectorAll("[data-code-highlight]>span")],part=spans.find(p=>p.dataset.codeRegion===region);if(!part)throw Error("source region missing");const start=spans.slice(0,spans.indexOf(part)).reduce((n,p)=>n+p.textContent.length,0);el.setSelectionRange(start,start+part.textContent.length)}',region);page.keyboard.insert_text(text)
  def source(mode,code):
   d=dialog();edit(d,'parameters',('ref ' if mode=='ref' else '')+'long nativeValue, out long nativeTotal');edit(d,'body',code);d.locator('[data-code-save]').click();expect(d).to_have_count(0)
  def save():author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_have_text('저장됨',timeout=30000);expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000)
  assert node()['rootModeEditor'];idle();peer=state()['presentation']['inputs']['schema'];legacy='nativeValue += 7;nativeTotal=nativeValue;return nativeValue;'
  source('value',legacy);pending=private();assert len(pending)==1;idle();page.close();stop()
  # Historical presentation fixture only: old releases stored source as a raw string,
  # with the SAME original basis/proof. No user files/accounts or grants are touched.
  store=next((storage/'presentations').glob('*.json'));record=json.loads(store.read_text());cells=record['inputs']['blueprint'];entry=next(x for x in cells if x[1].get('type')=='root-script');entry[0]=entry[0].removesuffix('root-script')+'source';entry[1]['type']='source';entry[1]['text']=legacy;legacy_record=json.loads(json.dumps(entry));store.write_text(json.dumps(record));start(1);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);d=dialog();assert legacy in d.locator('[data-code-source]').input_value(),'historical unsaved body hidden by the new root-script route';assert d.locator('[data-code-highlight] [data-code-region=parameters]').count()==0;d.locator('[data-code-cancel]').click();idle();assert legacy_record in state()['presentation']['inputs']['blueprint'] and state()['presentation']['inputs']['schema']==peer and original_files();checked('historical raw source input reopens exactly after a cold restart without migration, changed source receipt or lost peer input; Cancel preserves it')
  edited='nativeValue += 8;nativeTotal=nativeValue;return nativeValue;';d=dialog();edit(d,'body',edited);d.locator('[data-code-save]').click();expect(d).to_have_count(0);idle();cells=state()['presentation']['inputs']['blueprint'];owned=[x for x in cells if '|'+id+'|body|' in x[0]];assert len(owned)==1 and owned[0][1]['type']=='source' and owned[0][1]['text']==edited;idle();page.close();stop();start(2);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);d=dialog();assert edited in d.locator('[data-code-source]').input_value();edit(d,'body','nativeValue += 99;nativeTotal=nativeValue;return nativeValue;');d.locator('[data-code-cancel]').click();save();assert node()['source']==edited and not graph()['signature']['args'][0].get('mode') and original_files();checked('historical source stays in its old format through edit/private Save/restart/Cancel and ordinary author Save, without creating a conflicting root-script entry or touching original files')
  idle();page.close();stop();start(3);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);assert node()['source']==edited;confirm();assert (project/'Mode.csbody').read_bytes()==original['Mode.csbody'] and 'ref long' not in (project/'elements/ModeBody.celem').read_text() and state()['presentation']['inputs']['schema']==peer;d=dialog();assert d.locator('[data-code-highlight] [data-code-region=parameters]').count()==1 and edited in d.locator('[data-code-source]').input_value();d.locator('[data-code-cancel]').click();checked('saved historical body survives cold recovery and explicit compiler Confirm; only after consuming old input is the new parameter region available')
  newer='nativeValue += 10;nativeTotal=nativeValue;return nativeValue;';source('ref',newer);pending=private();assert len(pending)==1;idle();page.close();stop();start(4);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);assert private()==pending;d=dialog();assert newer in d.locator('[data-code-source]').input_value() and 'ref long nativeValue' in d.locator('[data-code-source]').input_value();edit(d,'body','nativeValue += 99;nativeTotal=nativeValue;return nativeValue;');d.locator('[data-code-cancel]').click();save();assert len(group()['ids'])==4 and node()['source']==newer;confirm();assert 'ref long nativeValue' in (project/'elements/ModeBody.celem').read_text() and (project/'Mode.csbody').read_bytes()==original['Mode.csbody'] and state()['presentation']['inputs']['schema']==peer;checked('following explicit new-format value/ref edit has independent Cancel/private restart/atomic4 Save/compiler Confirm and preserves original native source plus older other-object input')
  d=dialog();page.screenshot(path=str(case/'legacy-root-after-confirm.png'));d.locator('[data-code-cancel]').click()
  retained='nativeValue += 11;nativeTotal=nativeValue;return nativeValue;';source('ref',retained);idle();page.close();stop();record=json.loads(store.read_text());entry=next(x for x in record['inputs']['blueprint'] if x[1].get('type')=='root-script');duplicate=json.loads(json.dumps(entry));entry[0]=entry[0].removesuffix('root-script')+'source';entry[1]['type']='source';entry[1]['text']=retained;legacy_record=json.loads(json.dumps(entry));record['inputs']['blueprint'].append(duplicate);store.write_text(json.dumps(record));start(5);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);before=node()['source'];author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_contain_text('다른 미저장 입력을 따로',timeout=30000);expect(author.locator('[data-bp-save]')).to_be_enabled();idle();assert node()['source']==before and duplicate in state()['presentation']['inputs']['blueprint'] and legacy_record in state()['presentation']['inputs']['blueprint'];checked('coexisting fresh historical/new private formats fail before any per-cell source write, retaining both proposals and the prior body');page.close();stop()
  # Remove only the test-injected competing proposal from the isolated fixture;
  # production never chooses, discards or grants a proposal automatically.
  record=json.loads(store.read_text());record['inputs']['blueprint']=[x for x in record['inputs']['blueprint'] if x[0]!=duplicate[0]];store.write_text(json.dumps(record));start('5b');page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);current=graph();changed='nativeValue += 12;nativeTotal=nativeValue;return nativeValue;';invoke('blueprint',{'action':'source','id':graphid,'node':'body','text':changed,'basis':current['basis']});invoke('saveDraft',{});idle();page.close();stop();start(6);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);d=dialog();assert retained in d.locator('[data-code-source]').input_value();d.locator('[data-code-cancel]').click();author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_contain_text('원본이나 계약이 바뀌었습니다',timeout=30000);expect(author.locator('[data-bp-save]')).to_be_enabled();idle();assert legacy_record in state()['presentation']['inputs']['blueprint'] and node()['source']==changed and state()['presentation']['inputs']['schema']==peer;checked('historical body input remains visible after a later saved source change and cold restart, but its old proof cannot overwrite that source; rejected Save retains both inputs')
  page.close();browser.close();assert not errors and not external,(errors,external)
except Exception:
 try:(case/'failure.json').write_text(json.dumps({'traffic':traffic,'errors':errors},indent=2));page.screenshot(path=str(case/'failure.png'))
 except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case));raise
finally:stop()
record={'checks':checks,'errors':errors,'external':external,'actualEngine':True,'nativeWindows':False,'accountOrInference':False,'fixtureLegacyPresentationOnly':True,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
