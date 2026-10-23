"""Original existing root output controls against an isolated owned-element engine.
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

def sdk(operation,**body):
 p=subprocess.run([env['CONFECTORY_DOTNET'],str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps({'operation':operation,**body}),text=True,capture_output=True,env=env,check=True);v=json.loads(p.stdout);assert v['ok'],v;return v['result']
# Only this disposable source fixture is seeded with an existing post-call consumer.
attackfile=project/'Attack.celem';attack=attackfile.read_text();attack=attack.replace('{','{ value blueprintPublishedOutputs = '+json.dumps(json.dumps(['return']))+';',1);attackfile.write_text(attack)
graphfile=next((project/'blueprints').glob('*.graph.json'));graphjson=json.loads(graphfile.read_text());implfile=project/'elements/SerialBlueprintBody.celem';rootfn=(project/'elements/Serial.celem').read_text();callid='call_after';definition={'id':callid,'feature':'Owned.Elements::Attack','intent':'Existing original call and post-call source','control':'next'}
prepared=sdk('blueprintPrepareCall',id='Owned.Elements::SerialBlueprintBody',text=implfile.read_text(),targetText=attack,graph=graphjson,definition=definition);g=prepared['graph'];g['profile']='sync-acyclic-methods-v1';g['entry']=callid;g['edges'].append({'from':callid,'port':'next','to':'body'});node=next(n for n in g['nodes'] if n['id']==callid);node['arguments']={'amount':{'constant':5}};snap=sdk('blueprintOutputSnapshot',functionText=attack);node['postCall']={'contractHash':snap['contractHash'],'source':'return @originalResult;'};implfile.write_text(prepared['implementation']);graphfile.write_text(json.dumps(g));original={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file() and '.confectory' not in p.parts}

try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(0);page=setup()
  def idle():page.evaluate('async()=>await confectoryFlushPresentation()')
  def browse():
   page.locator('#workspace').click(button='right',position={'x':700,'y':300});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();return page.locator('.window[data-key^="browser:project:"]:visible')
  b=browse();b.locator('[data-object="Owned.Elements::Monster"]').get_by_role('button',name='정의 열기',exact=True).click();monster=page.locator('.window[data-key=schema]');expect(monster.locator('.object-title-description')).to_be_visible(timeout=30000);b.locator('[data-close]').click();monster.locator('.object-title-description').fill('후처리 코드와 다른 객체 입력');monster.locator('[data-close]').click();idle()
  b=browse();b.locator('[data-tab=feature]').click();b.locator('[data-object="'+id+'"]').get_by_role('button',name='정의 열기',exact=True).click();b.locator('[data-close]').click();page.locator('.window[data-key=declaration] [data-function-write-direct]').click();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-node="'+callid+'"] [data-wrapper-edit]')).to_be_visible(timeout=30000);graphid=invoke('blueprint',{'action':'list','feature':id})['result']['result']['rows'][0]['id']
  def graph():return invoke('blueprint',{'action':'read','id':graphid})['result']['result']
  def actual():return next(n for n in graph()['nodes'] if n['id']==callid)
  def card():return author.locator('[data-bp-node="'+callid+'"]')
  def focus():author.locator('[data-bp-overview-node="'+callid+'"]').click()
  def dialog():focus();card().locator('[data-wrapper-edit]').click();return page.get_by_role('dialog',name='분기 기능 편집 · Attack',exact=True)
  def edit(d,text):
   code=d.locator('[data-code-source]');code.evaluate('(el,region)=>{const spans=[...el.closest(".bp-script-editor").querySelectorAll("[data-code-highlight]>span")],part=spans.find(p=>p.dataset.codeRegion===region);if(!part)throw Error("source region missing");const start=spans.slice(0,spans.indexOf(part)).reduce((n,p)=>n+p.textContent.length,0);el.setSelectionRange(start,start+part.textContent.length)}','body');page.keyboard.insert_text(text);return code
  def source(text):
   d=dialog();edit(d,text);d.locator('[data-code-save]').click();expect(d).to_have_count(0)
  def private():idle();return [(k,v) for k,v in state()['presentation']['inputs']['blueprint'] if v['type']=='post-call']
  def save():author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_have_text('저장됨',timeout=30000)
  def confirm():
   author.locator('[data-bp-complete]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=30000)
   for cb in review.locator('[data-review-id]').all():cb.check()
   if review.locator('[data-additional-changes]').count():
    review.locator('[data-review-advanced]').click();ack=review.locator('[data-advanced-reviewed]')
    if ack.count():ack.check()
   expect(review.locator('#confirm')).to_be_enabled(timeout=30000);review.locator('#confirm').click();expect(review).to_have_count(0,timeout=60000);expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000)
  idle();peer=state()['presentation']['inputs']['schema'];invoke('select',{'id':'Owned.Elements::Main'});other=invoke('inspectDeclaration',{'id':'Owned.Elements::Main'})['state']['declaration'];invoke('editFunctionContract',{'id':other['id'],'revision':other['revision'],'hash':other['textHash'],'edit':{'description':'다른 기능 초안 유지'}});invoke('saveDraft',{})
  def other_draft():return next(row['draft'] for row in json.loads(next(project.glob('.confectory/edit-workspaces/*/draft.json')).read_text())['changes'] if row['id']=='Owned.Elements::Main')
  other_before=other_draft();before=actual();d=dialog();code=d.locator('[data-code-source]');initial=code.input_value();code.evaluate('(el)=>el.setSelectionRange(0,6)');page.keyboard.insert_text('unsafe');expect(code).to_have_value(initial);edit(d,'return @context.@return + 2;');d.locator('[data-code-cancel]').click();assert private()==[] and actual()['postCall']==before['postCall'];checked('original wrapper editor opens over an existing owned consumer; fixed original call is protected and Cancel leaves source/private state untouched')
  wanted='return @context.@return + 2;';source(wanted);assert json.loads(private()[0][1]['text'])['source']==wanted and actual()['postCall']['source']!=wanted and all((project/k).read_bytes()==v for k,v in original.items());checked('original Code Save retains only a private After source with exact publication fingerprint, without changing callee, graph or sources')
  idle();page.close();stop();start(1);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);d=dialog();assert wanted in d.locator('[data-code-source]').input_value();d.locator('[data-code-cancel]').click();assert state()['presentation']['inputs']['schema']==peer and other_draft()==other_before;checked('real restart restores the pending C# After body and exact receipt along with other saved/private drafts')
  save();assert actual()['postCall']['source']==wanted and private()==[] and all((project/k).read_bytes()==v for k,v in original.items());checked('original author Save applies the real post-call source to one owned graph under current receipt/CAS and keeps final/callee files unchanged')
  confirm();assert json.loads(graphfile.read_text())['nodes'][-1]['postCall']['source']==wanted and attackfile.read_bytes()==original['Attack.celem'];assert other_draft()==other_before;focus();d=dialog();expect(d.locator('.bp-wrapper-bindings')).to_contain_text('context.@return');(case/'modal-dom.html').write_text(d.evaluate('(el)=>el.outerHTML'));page.screenshot(path=str(case/'post-call-editor-confirmed.png'));d.locator('[data-code-cancel]').click();checked('actual compiler Review/explicit Confirm accepts fixed original invocation plus After source and leaves original provider body/source and peer draft intact')
  idle();page.close();stop();start(2);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);assert actual()['postCall']['source']==wanted and other_draft()==other_before;source('return @context.@return + 3;');pending=private();stale=graph();invoke('select',{'id':'Owned.Elements::Attack'});a=invoke('inspectDeclaration',{'id':'Owned.Elements::Attack'})['state']['declaration'];invoke('editMetadata',{'id':a['id'],'revision':a['revision'],'hash':a['textHash'],'field':'blueprintPublishedOutputs','value':'[]'});invoke('blueprint',{'action':'postCall','id':graphid,'node':callid,'contractHash':before['postCall']['contractHash'],'text':'return 0;','basis':stale['basis']},False);inspected=graph();assert next(n for n in inspected['nodes'] if n['id']==callid)['postCallStale'] and inspected['diagnostics']['state']=='invalid';expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).not_to_have_text('저장됨',timeout=30000);assert private()==pending and state()['presentation']['inputs']['schema']==peer and other_draft()==other_before;assert json.loads(graphfile.read_text())['nodes'][-1]['postCall']['source']==wanted;checked('revoked source publication blocks stale mutation and fresh consumer loading/Save, while preserving confirmed code and all new/other inputs')
  page.close();browser.close();assert not errors and not external,(errors,external)
except Exception:
 try:(case/'failure.json').write_text(json.dumps({'traffic':traffic,'errors':errors},indent=2));page.screenshot(path=str(case/'failure.png'))
 except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case));raise
finally:stop()
record={'checks':checks,'errors':errors,'external':external,'actualEngine':True,'nativeWindows':False,'accountOrInference':False,'wrapperCreationUi':False,'eyeEnabled':False,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
