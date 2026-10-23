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
 if isinstance(body,dict) and body.get('op')=='invoke' and body.get('endpoint')=='blueprint' and injected==0:
  command=body.get('input',{})
  if command.get('action')=='route' and command.get('port','').startswith('case:'):
   injected+=1;command['node']='missing-node';request.continue_(post_data=json.dumps(body));return
  if command.get('action')=='authorBatch':
   injected+=1;step=next(row for row in command['edits'] if row['action']=='source');step['node']='missing-node';request.continue_(post_data=json.dumps(body));return
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
# Disposable native VOID original; normal wrapper state is created only by the UI.
voidfn='function Owned.Elements::NativeVoid () -> void {provide Owned.Elements::NativeVoid with Owned.Elements::NativeVoidBody;}';(project/'elements/NativeVoid.celem').write_text(voidfn);(project/'elements/NativeVoidBody.celem').write_text('implementation Owned.Elements::NativeVoidBody for Owned.Elements::NativeVoid () -> void {body common "NativeVoid.csbody";}');(project/'NativeVoid.csbody').write_text('// isolated no-account void fixture');m=project/'project.cproj';t=m.read_text();i=t.rfind('}');m.write_text(t[:i]+'element NativeVoid function "elements/NativeVoid.celem";element NativeVoidBody implementation "elements/NativeVoidBody.celem";'+t[i:])
graphfile=next((project/'blueprints').glob('*.graph.json'));graphjson=json.loads(graphfile.read_text());implfile=project/'elements/SerialBlueprintBody.celem';callid='native_void';prepared=sdk('blueprintPrepareCall',id='Owned.Elements::SerialBlueprintBody',text=implfile.read_text(),targetText=voidfn,graph=graphjson,definition={'id':callid,'feature':'Owned.Elements::NativeVoid','intent':'Native void reference','control':'next'});g=prepared['graph'];g['profile']='sync-acyclic-methods-v1';g['entry']=callid;g['edges'].append({'from':callid,'port':'next','to':'body'});implfile.write_text(prepared['implementation']);graphfile.write_text(json.dumps(g));original={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file() and '.confectory' not in p.parts}

try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(0);page=setup()
  def idle():page.evaluate('async()=>await confectoryFlushPresentation()')
  def browse():
   page.locator('#workspace').click(button='right',position={'x':700,'y':300});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();return page.locator('.window[data-key^="browser:project:"]:visible')
  b=browse();b.locator('[data-object="Owned.Elements::Monster"]').get_by_role('button',name='정의 열기',exact=True).click();monster=page.locator('.window[data-key=schema]');expect(monster.locator('.object-title-description')).to_be_visible(timeout=30000);b.locator('[data-close]').click();monster.locator('.object-title-description').fill('후처리 코드와 다른 객체 입력');monster.locator('[data-close]').click();idle()
  b=browse();b.locator('[data-tab=feature]').click();b.locator('[data-object="'+id+'"]').get_by_role('button',name='정의 열기',exact=True).click();b.locator('[data-close]').click();page.locator('.window[data-key=declaration] [data-function-write-direct]').click();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-node="'+callid+'"] [data-bp-wrap-call]')).to_be_enabled(timeout=30000);graphid=invoke('blueprint',{'action':'list','feature':id})['result']['result']['rows'][0]['id']
  def graph():return invoke('blueprint',{'action':'read','id':graphid})['result']['result']
  def actual():return next(n for n in graph()['nodes'] if n['id']==callid)
  def card():return author.locator('[data-bp-node="'+callid+'"]')
  def focus():author.locator('[data-bp-overview-node="'+callid+'"]').click()
  def dialog():focus();card().locator('[data-wrapper-edit]').click();return page.get_by_role('dialog',name='분기 기능 편집 · NativeVoid',exact=True)
  def edit(d,text,region='body'):
   code=d.locator('[data-code-source]');code.evaluate('(el,region)=>{const spans=[...el.closest(".bp-script-editor").querySelectorAll("[data-code-highlight]>span")],part=spans.find(p=>p.dataset.codeRegion===region);if(!part)throw Error("source region missing");const start=spans.slice(0,spans.indexOf(part)).reduce((n,p)=>n+p.textContent.length,0);el.setSelectionRange(start,start+part.textContent.length)}',region);page.keyboard.insert_text(text);return code
  def source(text):
   d=dialog();edit(d,text);d.locator('[data-code-save]').click();expect(d).to_have_count(0)
  def private():idle();return [(k,v) for k,v in state()['presentation']['inputs']['blueprint'] if v['type']=='wrapper']
  def save():author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_have_text('저장됨',timeout=30000)
  def confirm():
   author.locator('[data-bp-complete]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=30000)
   for cb in review.locator('[data-review-id]').all():cb.check()
   if review.locator('[data-additional-changes]').count():
    review.locator('[data-review-advanced]').click();ack=review.locator('[data-advanced-reviewed]')
    if ack.count():ack.check()
   expect(review.locator('#confirm')).to_be_enabled(timeout=30000);review.locator('#confirm').click();expect(review).to_have_count(0,timeout=60000);expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000)
  def originals():return all((project/k).read_bytes()==v for k,v in original.items())
  idle();peer=state()['presentation']['inputs']['schema'];focus();card().locator('[data-bp-wrap-call]').click();expect(card().locator('[data-owned-branch]')).to_have_count(1);assert len(private())==1 and actual()['control']=='next' and originals();author.locator('.bp-viewport').click(position={'x':10,'y':10});page.keyboard.press('Control+z');expect(card().locator('[data-owned-branch]')).to_have_count(0);assert private()==[] and originals();checked('original normal wrapper button creates a private enum branch and original structural Undo cancels it without source writes or other-input loss')
  focus();card().locator('[data-bp-wrap-call]').click();before=private();d=dialog();(case/'wrapper-modal.html').write_text(d.evaluate('(el)=>el.outerHTML'));assert d.locator('[data-code-highlight] [data-code-region=enum]').count()==1 and 'OriginalResult' in d.locator('[data-code-source]').input_value();edit(d,'NoBranch = 0, 完了 = 0,','enum');d.locator('[data-code-save]').click();expect(d.locator('[data-code-error]')).to_be_visible();d.locator('[data-code-cancel]').click();assert private()==before and actual()['control']=='next';d=dialog();edit(d,'return Pick();');edit(d,'private static Result Pick(){return Result.분기1;}','helpers');d.locator('[data-code-save]').click();expect(d).to_have_count(0);before=private();assert len(before)==1;idle();page.close();stop();start(1);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);assert private()==before and state()['presentation']['inputs']['schema']==peer and originals();d=dialog();assert 'return Pick();' in d.locator('[data-code-source]').input_value() and 'Pick(){return Result.분기1;}' in d.locator('[data-code-source]').input_value();d.locator('[data-code-cancel]').click();checked('original enum/body/helper modal rejects duplicate values, Cancel preserves prior input, and private normal creation restores after true restart with exact other-object input')
  save();n=actual();assert n['control']=='switch' and n['postCall']['mode']=='execution-enum' and graph()['profile']=='sync-acyclic-switch-v1' and any(e['from']==callid and e['port']=='next' and e['to']=='body' for e in graph()['edges']) and originals();confirm();assert state()['presentation']['inputs']['schema']==peer;checked('normal author Save creates the real owned wrapper using strict server contract validation, retains original main continuation and passes explicit real compiler Review/Confirm')
  existing_actions={n['id'] for n in graph()['nodes'] if n['id'].startswith('action_')};n=actual();branch=next(m for m in n['executionEnum']['members'] if m['id']!=n['executionEnum']['primary']);author.locator('[data-bp-overview-node="body"]').click();seed=author.locator('[data-bp-node="body"]');y=float(seed.evaluate('(el)=>parseFloat(el.style.top)'));box=seed.locator('.function-node-heading').bounding_box();page.mouse.move(box['x']+80,box['y']+22);page.mouse.down();page.mouse.move(box['x']+80,box['y']+202,steps=8);page.mouse.up();assert float(seed.evaluate('(el)=>parseFloat(el.style.top)'))>=y+150;focus();rail=card().locator('[data-port="case:'+branch['id']+'"]');assert rail.evaluate('(el)=>{const r=el.getBoundingClientRect();return el.contains(document.elementFromPoint(r.x+r.width/2,r.y+r.height/2))}');rail.click();author.locator('.bp-viewport').click(button='right',position={'x':420,'y':320});menu=page.get_by_role('dialog',name='블루프린트 노드 검색',exact=True);menu.get_by_role('button',name='동작 만들기',exact=True).click();new=author.locator('[data-bp-node^="action_"]'+''.join(':not([data-bp-node="'+old+'"])' for old in existing_actions));expect(new).to_have_count(1);child=new.get_attribute('data-bp-node');author.locator('[data-bp-overview-node="'+child+'"]').click();new.locator('[data-inline-description]').fill('선택된 enum 경로의 동작');new.locator('[data-internal-code]').click();code=page.get_by_role('dialog',name='C# Script · 내부 기능',exact=True);edit(code,'return;');code.locator('[data-code-save]').click();idle();captured=[x for x in state()['presentation']['inputs']['blueprint'] if '|v508-author|'+id+'|' in x[0]];author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_have_text('consumer_error',timeout=30000);idle();remaining=state()['presentation']['inputs']['blueprint'];present=[key for key,value in captured if [key,value] in remaining];failed={'captured':captured,'remaining':remaining,'createdInLiveDraft':any(n['id']==child for n in graph()['nodes']),'capturedKeysRetained':len(present),'capturedCount':len(captured)};(case/'failed-save-facts.json').write_text(json.dumps(failed,ensure_ascii=False,indent=2));page.close();stop();start(2);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);new=author.locator('[data-bp-node="'+child+'"]');expect(new).to_have_count(1);idle();assert all(x in state()['presentation']['inputs']['blueprint'] for x in captured) and not any(n['id']==child for n in graph()['nodes']);checked('failed candidate Save leaves all private creation/route/body input and no live node, then cold restart restores the exact private new action without partial checkpoint')
  save();g=graph();assert any(n['id']==child and n['sourceStatus']=='available' for n in g['nodes']) and len([n for n in g['nodes'] if n['id']==child])==1;confirm();idle();checkpoint=next(project.glob('.confectory/edit-workspaces/*/draft.json'));assert graph()['checkpointHash']==__import__('hashlib').sha256(checkpoint.read_bytes()).hexdigest();author.locator('[data-bp-overview-node="'+child+'"]').click();new=author.locator('[data-bp-node="'+child+'"]');new.locator('[data-internal-code]').click();code=page.get_by_role('dialog',name='C# Script · 내부 기능',exact=True);edit(code,'// 자기 확정 뒤 같은 창에서 재편집\nreturn;');code.locator('[data-code-save]').click();save();assert graph()['checkpointHash']==__import__('hashlib').sha256(checkpoint.read_bytes()).hexdigest();confirm();idle();assert graph()['checkpointHash']==__import__('hashlib').sha256(checkpoint.read_bytes()).hexdigest() and state()['presentation']['inputs']['schema']==peer;checked('own Save and compiler Confirm refresh only their known checkpoint, allowing the same open window to re-edit and confirm while unrelated private input survives');page.close();stop();start(3);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);assert len([n for n in graph()['nodes'] if n['id']==child])==1 and next(n for n in graph()['nodes'] if n['id']==child)['sourceStatus']=='available' and '// 자기 확정 뒤 같은 창에서 재편집' in json.dumps(graph(),ensure_ascii=False) and state()['presentation']['inputs']['schema']==peer;checked('retry after cold rejected Save creates one owned action/route/source, passes explicit compiler Confirm and restores once with other input preserved')
  page.close();browser.close();assert not errors and not external,(errors,external)

except Exception:
 try:(case/'failure-state.json').write_text(json.dumps(state(),ensure_ascii=False,indent=2));(case/'failure.json').write_text(json.dumps({'traffic':traffic,'errors':errors},indent=2));page.screenshot(path=str(case/'failure.png'))
 except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case));raise
finally:stop()
record={'checks':checks,'errors':errors,'external':external,'actualEngine':True,'normalWrapperCreation':True,'injectedRejectedSave':True,'nativeVoidOnly':True,'nativeWindows':False,'accountOrInference':False,'projectRun':False,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
