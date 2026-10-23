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

try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(0);page=setup()
  def idle():
   page.wait_for_function('()=>typeof globalThis.confectoryFlushPresentation==="function"');page.evaluate('async()=>await confectoryFlushPresentation()')
  def browse():
   page.locator('#workspace').click(button='right',position={'x':700,'y':300});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=page.locator('.window[data-key^="browser:project:"]:visible');expect(b).to_be_visible(timeout=30000);return b
  b=browse();b.locator('[data-object="Owned.Elements::Monster"]').get_by_role('button',name='정의 열기',exact=True).click();w=page.locator('.window[data-key=schema]');expect(w.locator('.object-title-description')).to_be_visible(timeout=30000);b.locator('[data-close]').click();peer='다른 객체 미저장 설명 보존';w.locator('.object-title-description').click();w.locator('.object-title-description').fill(peer);w.locator('[data-close]').click();b=browse();b.locator('[data-tab=feature]').click();b.locator('[data-object="'+id+'"]').get_by_role('button',name='정의 열기',exact=True).click();w=page.locator('.window[data-key=declaration]');expect(w.locator('[data-function-write-direct]')).to_be_enabled(timeout=30000);b.locator('[data-close]').click();w.locator('[data-function-write-direct]').click();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-signature-id=seed]')).to_be_visible(timeout=30000);graphid=invoke('blueprint',{'action':'list','feature':id})['result']['result']['rows'][0]['id']
  def graph():return invoke('blueprint',{'action':'read','id':graphid})['result']['result']
  def originals():return all((project/k).read_bytes()==v for k,v in original.items())
  def private():idle();return [(k,v) for k,v in state()['presentation']['inputs']['blueprint'] if '|v508-author|' in k]
  def peers():idle();return [(k,v) for k,v in state()['presentation']['inputs']['schema'] if 'Owned.Elements::Monster' in k]
  def entry(name):return author.locator('.bp-pin-plug[data-node="$entry"][data-port="field:'+name+'"]')
  def choose(name,kind,array=False):
   entry(name).locator('.bp-entry-type-button').click();popup=page.get_by_role('dialog',name='속성 타입 선택',exact=True);popup.locator('[data-multi]').set_checked(array);popup.locator('[data-type="'+kind+'"]').click()
  def save():
   author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_have_text('저장됨',timeout=30000);expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000)
  def complete():
   author.locator('[data-bp-complete]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=30000)
   for cb in review.locator('[data-review-id]').all():cb.check()
   if review.locator('[data-additional-changes]').count():
    review.locator('[data-review-advanced]').click();ack=review.locator('[data-advanced-reviewed]')
    if ack.count():ack.check()
   expect(review.locator('#confirm')).to_be_enabled(timeout=30000);review.locator('#confirm').click();expect(review).to_have_count(0,timeout=60000);expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000)
  base=graph();peer_before=peers()
  invoke('select',{'id':'Owned.Elements::Attack'});other=invoke('inspectDeclaration',{'id':'Owned.Elements::Attack'})['state']['declaration'];invoke('editFunctionContract',{'id':'Owned.Elements::Attack','revision':other['revision'],'hash':other['textHash'],'edit':{'description':'출력 정의와 다른 기능 초안 보존'}});invoke('saveDraft',{})
  def other_draft():return next(row['draft'] for row in json.loads(next(project.glob('.confectory/edit-workspaces/*/draft.json')).read_text())['changes'] if row['id']=='Owned.Elements::Attack')
  other_before=other_draft()
  def actual_nodes():return author.locator('[data-bp-node^=export_]')
  def card(node):return author.locator('[data-bp-node="'+node+'"]')
  def focus_node(node):author.locator('[data-bp-overview-node="'+node+'"]').click()
  def new_output():
   author.locator('.bp-viewport').click(button='right',position={'x':530,'y':230});menu=page.get_by_role('dialog',name='블루프린트 노드 검색');menu.locator('[data-resource-kind]').select_option('export');menu.locator('[data-resource-output-create]').click();expect(actual_nodes()).to_have_count(1);return actual_nodes().get_attribute('data-bp-node')
  def enter_value(node,text):
   focus_node(node);control=card(node).locator('.bp-pin-plug input');control.fill(text);control.press('Enter')
  def link(source,target):
   focus_node(source);card(source).locator('.bp-port[data-side=out][data-port=next]').click();focus_node(target);card(target).locator('.bp-port[data-side=in]:not([data-kind])').click()
  def delete_message(cancel=False):
   author.locator('[data-output-remove=message]').click();dialog=page.get_by_role('dialog',name='출력 삭제',exact=True);expect(dialog.locator('.small')).to_contain_text('2개');dialog.locator('[data-output-delete-'+('cancel' if cancel else 'confirm')+']').click()
  # Server refuses treating an input as a selected output or a duplicate/incomplete order.
  bad={'args':base['signature']['args'],'returnType':base['signature']['return'],'remap':{a['name']:a['name'] for a in base['signature']['args']},'removeOutputs':['seed']};invoke('blueprint',{'action':'rootParameters','id':graphid,'basis':base['basis'],'plan':json.dumps(bad)},False);assert graph()['nodes']==base['nodes'] and originals();checked('forged output deletion cannot remove a root input or partly mutate its saved function/implementation/graph')
  node=new_output();assert not any(a.get('mode')=='out' for a in graph()['signature']['args']) and originals();control=card(node).locator('[data-bp-export-name]');control.fill('message');control.press('Enter');enter_value(node,'한글 출력 "값" 😀');p=json.loads(private()[0][1]['text']);assert len(private())==1 and p['args'][-1]=={'name':'message','type':'string','mode':'out'} and json.loads(p['outputCreates'][0]['valueJson'])=={'constant':'한글 출력 "값" 😀'};assert originals();checked('original new-output action, inline name and Unicode value remain ONE private coordinated root candidate with no final or shared source mutation')
  idle();page.close();stop();start(1);page=setup();idle();author=page.locator('.window[data-key=blueprint]');expect(card(node)).to_be_visible(timeout=30000);assert graph()['signature']==base['signature'] and other_draft()==other_before and peers()==peer_before;checked('new output definition and its assignment/value cold-restore privately while other saved and private drafts remain intact')
  # Original order keyboard moves the native return card before the new named out.
  row=author.locator('[data-output-entry-id=return]');row.focus();page.keyboard.press('Alt+ArrowUp');assert author.locator('[data-output-entry-id]').evaluate_all('(xs)=>xs.map(x=>x.dataset.outputEntryId)')==['return','message'];save();g=graph();assert g['outputOrder']==['return','message'] and any(a['name']=='message' and a['mode']=='out' for a in g['signature']['args']) and next(n for n in g['nodes'] if n['id']==node)['output']=='message' and other_draft()==other_before and originals();checked('original output order and new declared output+assignment save atomically across exact function/implementation/graph without finalizing or changing other drafts')
  # Native header drag separates the dense seed from the new output before real pin clicks.
  focus_node(node);box=card(node).locator(':scope > header strong').bounding_box();page.mouse.move(box['x']+box['width']/2,box['y']+box['height']/2);page.mouse.down();page.mouse.move(box['x']+box['width']/2+300,box['y']+box['height']/2+100,steps=15);page.mouse.up();link('body',node);link(node,'$exit:return');save();complete();assert other_draft()==other_before and peers()==peer_before;checked('new native out compiles only after explicit Review/Confirm with original real execution wiring and source/draft boundaries preserved')
  # The original sidebar's actual browser drag creates another assignment of the SAME definition.
  source=author.locator('[data-bp-output-id=message]');source.drag_to(author.locator('.bp-viewport'),target_position={'x':540,'y':220});expect(actual_nodes()).to_have_count(2);second=next(n for n in actual_nodes().evaluate_all('(xs)=>xs.map(x=>x.dataset.bpNode)') if n!=node);enter_value(second,'두 번째 출력');save();link(node,second);link(second,'$exit:return');save();complete();g=graph();assert len([n for n in g['nodes'] if n['kind']=='export' and n['output']=='message'])==2;page.screenshot(path=str(case/'output-definition-two-assignments.png'));checked('actual original sidebar drag adds a second same-definition assignment; typed value, serial routes and explicit compiler Confirm preserve its first source and other drafts')
  before=graph();delete_message(True);assert not private() and graph()['nodes']==before['nodes'] and other_draft()==other_before;checked('original counted output-definition deletion Cancel preserves both connected assignments, signature and saved draft')
  delete_message();expect(actual_nodes()).to_have_count(0);assert len(graph()['nodes'])==len(before['nodes']) and other_draft()==other_before;author.locator('.bp-viewport').focus();page.keyboard.press('Control+z');expect(actual_nodes()).to_have_count(2);assert not private();delete_message();save();g=graph();assert not any(a['name']=='message' for a in g['signature']['args']) and not any(n['kind']=='export' for n in g['nodes']) and any(e['from']=='body' and e['to']=='exit:return' for e in g['edges']) and g['outputOrder']==['return'];complete();assert other_draft()==other_before and peers()==peer_before;checked('same-window definition delete+Undo then atomic Save and explicit Confirm remove both assignments and only that out parameter while reconnecting the kept predecessor/terminal')
  idle();page.close();stop();start(2);page=setup();idle();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-output-entry-id=return]')).to_be_visible(timeout=30000);assert author.locator('[data-output-entry-id=message]').count()==0 and actual_nodes().count()==0 and other_draft()==other_before and peers()==peer_before;checked('confirmed grouped definition deletion, retained source input and output order restore after another real restart without incomplete saved root groups')
  page.close();stop();browser.close();assert not errors and not external,(errors,external)

except Exception:
 try:(case/'failure.json').write_text(json.dumps({'state':state(),'traffic':traffic,'errors':errors},indent=2))
 except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case));raise
finally:stop()
record={'checks':checks,'errors':errors,'external':external,'actualEngine':True,'nativeWindows':False,'accountOrInference':False,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
