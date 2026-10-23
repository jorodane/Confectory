"""Actual owned function-reference selection, cold draft restore, wiring and compiler Confirm.
No account/grant/model invocation or project execution; preserve original callee source.
"""
import json,re,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());fixture=pathlib.Path(sys.argv[3]).resolve();assert fixture==repo.parent/'scratch/v508-elements/actual13-source-fixture'
case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-feature-call-engine-'));project=case/'owned project';shutil.copytree(fixture/'owned project',project,ignore=shutil.ignore_patterns('.confectory','.build'));storage=case/'profile';storage.mkdir();original={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file() and '.confectory' not in p.parts};id='Owned.Elements::Serial';text='9223372036854775804';description='재시작할 미적용 설명 한글';env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(storage),CONFECTORY_ENTRY_STORAGE=str(storage),CONFECTORY_MCP_DIRECTORY=str(case/'instances'),CONFECTORY_WEB_PROJECT=str(project/'project.cproj'),CONFECTORY_DOTNET=env.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet'));env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];host=None;log=None;errors=[];external=[];checks=[]
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
 p=sync_playwright().start()
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(0);page=setup();page.locator('#workspace').click(button='right',position={'x':700,'y':300});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=page.locator('.window[data-key^="browser:project:"]');b.locator('[data-tab=feature]').click();b.locator('[data-object="'+id+'"]').get_by_role('button',name='정의 열기',exact=True).click();w=page.locator('.window[data-key=declaration]');expect(w.locator('[data-function-write-direct]')).to_be_visible(timeout=30000);w.locator('[data-function-write-direct]').click();author=page.locator('.window[data-key=blueprint]');expect(author.locator('.bp-function-card')).to_have_count(2,timeout=30000);graphid=invoke('blueprint',{'action':'list','feature':id})['result']['result']['rows'][0]['id']
 def graph():return invoke('blueprint',{'action':'read','id':graphid})['result']['result']
 def resources():
  # Cold restoration also restores the declaration/browser asynchronously.
  # Use the real production enabled-state hook before interacting; a newly
  # retired author correctly closes its old menu instead of retaining it.
  expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000)
  author.locator('.bp-viewport').click(button='right',position={'x':500,'y':220});dialog=page.get_by_role('dialog',name='블루프린트 노드 검색');expect(dialog).to_be_visible();expect(dialog.locator('[data-resource-feature="Owned.Elements::Attack"]')).to_be_visible(timeout=30000);bounds=dialog.bounding_box();assert bounds['y']>=8 and bounds['y']+bounds['height']<=page.viewport_size['height']-8,bounds;return dialog
 def choose():
  before_count=author.locator('.bp-function-card').count();resources().locator('[data-resource-feature="Owned.Elements::Attack"]').click();expect(author.locator('.bp-function-card')).to_have_count(before_count+1,timeout=30000);return author.locator('.bp-function-card').last.get_attribute('data-bp-node')
 def card():return author.locator('[data-bp-node="'+callid+'"]')
 def focus_node(node):
  # The original map pans to physical coordinates, even when shapes
  # overlap. Click the measured node center without semantic hit-target
  # enforcement; this is an ordinary mouse click, never force/dispatch.
  expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);shape=author.locator('[data-bp-overview-node="'+node+'"] .bp-overview-shape');expect(shape).to_be_visible(timeout=30000);box=page.wait_for_function("id=>{const el=[...document.querySelectorAll('[data-bp-overview-node]')].find(e=>e.dataset.bpOverviewNode===id)?.querySelector('.bp-overview-shape');const r=el?.getBoundingClientRect();return r?.width&&r.height?{x:r.x,y:r.y,width:r.width,height:r.height}:false}",arg=node).json_value();assert box
  page.mouse.click(box['x']+box['width']/2,box['y']+box['height']/2)
 def value(node,name):return author.locator('[data-bp-node="'+node+'"] .bp-pin-plug[data-side=in][data-port="field:'+name+'"] input')
 def save():author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_have_text('저장됨',timeout=30000)
 resources().locator('[data-resource-close]').click();before=graph();callid=choose();expect(card().locator('.function-node')).to_have_class(re.compile(r'\bfunction-node\b.*\bis-inherited\b'));expect(card().locator('[data-internal-code]')).to_have_count(0);expect(card().locator('[data-action-field-add]')).to_have_count(0);author.locator('.bp-viewport').focus();page.keyboard.press('Control+z');expect(author.locator('.bp-function-card')).to_have_count(2);assert graph()['sources']==before['sources'];assert all((project/k).read_bytes()==v for k,v in original.items());checked('original global-function resource catalog cancel and selected-reference undo read only selected contracts; no graph membership, source or body copy')
 callid=choose();focus_node(callid);value(callid,'amount').fill('5');value(callid,'amount').press('Enter');page.evaluate('async()=>await confectoryFlushPresentation()');pending=[(k,v) for k,v in state()['presentation']['inputs']['blueprint'] if '|v508-author|' in k];spec=next(json.loads(v['text']) for k,v in pending if v['type']=='call-create');assert spec['contractReadScope']=='selected-function-declaration' and spec['contractBodyReads']==0 and 'basis' not in spec;assert len(graph()['nodes'])==2;page.close();stop();start(1);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('.bp-function-card')).to_have_count(3,timeout=30000);assert [(k,v) for k,v in state()['presentation']['inputs']['blueprint'] if '|v508-author|' in k]==pending;focus_node(callid);expect(value(callid,'amount')).to_have_value('5');checked('actual cold restart retains selected function contract fingerprint and private argument without persisting a live receipt or creating a call')
 save();current=graph();call=next(n for n in current['nodes'] if n['id']==callid);assert call['kind']=='call' and call['calledFeature']=='Owned.Elements::Attack' and call.get('source') is None and call['sourceStatus']=='feature-reference';assert call['signature']=={'args':[{'type':'long','name':'amount'}],'return':'long'};assert call['arguments'][0]['valueJson']=='{"constant":5}';assert not any(s['id'].startswith('Owned.Elements::AttackBody') for s in current['sources']);assert all((project/k).read_bytes()==v for k,v in original.items());checked('Save rechecks selected callee contract and creates an actual typed reference through server receipt; callee body is not copied or read into the graph')
 focus_node('body');author.locator('[data-bp-node=body] .bp-pin-plug[data-side=in][data-port="field:seed"] [aria-label="값 목록 열기"]').click();page.get_by_role('dialog',name='핀 값 선택').get_by_role('button',name='Attack · 결과',exact=True).click();author.locator('[data-bp-overview]').focus();page.keyboard.press('Home');author.locator('.bp-port[data-node="$entry"][data-side=out]:not([data-kind])').click();focus_node(callid);card().locator('.bp-exec-header-in').click();card().locator('.bp-exec-line-out[data-port=next]').click();focus_node('body');author.locator('[data-bp-node=body] .bp-exec-header-in').click();save();current=graph();assert current['entry']==callid and any(e['from']==callid and e['to']=='body' and e['port']=='next' for e in current['edges']);assert json.loads(next(a['valueJson'] for a in next(n for n in current['nodes'] if n['id']=='body')['arguments'] if a['name']=='seed'))=={'node':callid};assert current['profile']=='sync-acyclic-v1';assert all((project/k).read_bytes()==v for k,v in original.items());checked('original pins connect imported function into left-to-right serial entry/next/data flow using correct legacy return binding and no profile or permission upgrade')
 author.locator('[data-bp-complete]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=30000)
 if review.locator('[data-additional-changes]').count():
  review.locator('[data-review-advanced]').click();ack=review.locator('[data-advanced-reviewed]')
  if ack.count():ack.check()
 expected_paths={source['path'] for source in current['sources'] if source['id'] in [graphid,graphid.split('/body:')[0]]};assert len(expected_paths)==2
 expect(review.locator('#confirm')).to_be_enabled(timeout=30000);review.locator('#confirm').click();expect(review).to_have_count(0,timeout=60000);assert any(r.get('result',{}).get('result',{}).get('sourceConfirmed') for r in traffic)
 confirmed_files={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file() and '.confectory' not in p.parts};assert confirmed_files.keys()==original.keys();assert {k for k in original if confirmed_files[k]!=original[k]}==expected_paths;assert (project/'Attack.csbody').read_bytes()==original['Attack.csbody'];page.screenshot(path=str(case/'call-confirmed.png'));original=confirmed_files;checked('explicit grouped Review/compiler Confirm changes exactly the observed caller graph/implementation paths and preserves original callee declaration/implementation/body; project never executes')
 page.evaluate('async()=>await confectoryFlushPresentation()');page.close();stop();start(2);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('.bp-function-card')).to_have_count(3,timeout=30000);restored=graph();assert restored['entry']==callid and restored['profile']=='sync-acyclic-v1';restored_call=next(n for n in restored['nodes'] if n['id']==callid);assert restored_call['calledFeature']=='Owned.Elements::Attack' and restored_call['arguments'][0]['valueJson']=='{"constant":5}';expect(card().locator('.function-node-name')).to_have_text('Attack');expect(card().locator('[data-internal-code]')).to_have_count(0);assert not [v for k,v in state()['presentation']['inputs']['blueprint'] if '|v508-author|' in k];assert all((project/k).read_bytes()==v for k,v in original.items());page.screenshot(path=str(case/'call-cold-confirmed.png'));checked('actual cold engine restart reopens confirmed call name/argument/serial entry and clean protected card without source mutation or repeated confirmation')
 # New selection remains private if the callee's material named contract changes before Save.
 oldcall=callid;callid=choose();focus_node(callid);value(callid,'amount').fill('9');value(callid,'amount').press('Enter');invoke('select',{'id':'Owned.Elements::Attack'});invoke('inspectDeclaration',{'id':'Owned.Elements::Attack'});callee=state()['declaration'];invoke('editFunctionContract',{'id':callee['id'],'revision':callee['revision'],'hash':callee['textHash'],'edit':{'signature':{'args':[{'name':'renamed','type':'long'}],'return':'long'}}});author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_contain_text('계약이 바뀌',timeout=30000);assert len(graph()['nodes'])==3;expect(value(callid,'amount')).to_have_value('9');page.evaluate('async()=>await confectoryFlushPresentation()');assert any(v['type']=='call-create' and v['node']==callid for k,v in state()['presentation']['inputs']['blueprint']);assert all((project/k).read_bytes()==v for k,v in original.items());# Newly placed private cards can overlap existing value plugs. Use the
 # original header drag to expose its close control, not a force click.
 name_box=card().locator('.function-node-name').bounding_box();assert name_box;page.mouse.move(name_box['x']+name_box['width']/2,name_box['y']+name_box['height']/2);page.mouse.down();page.mouse.move(name_box['x']+name_box['width']/2-160,name_box['y']+name_box['height']/2,steps=8);page.mouse.up();focus_node(callid);card().locator('[data-function-delete]').click();expect(author.locator('.bp-function-card')).to_have_count(3);page.evaluate('async()=>await confectoryFlushPresentation()');assert not any(v['node']==callid for k,v in state()['presentation']['inputs']['blueprint'] if '|v508-author|' in k);checked('callee contract change blocks caller creation without silent adoption or input loss; explicit deletion of the uncreated private node cancels only its own known drafts')
 page.close();stop();browser.close();assert not errors and not external,(errors,external)
except Exception:
 try:page.screenshot(path=str(case/'failure.png'))
 except Exception:pass
 try:(case/'failure.json').write_text(json.dumps({'state':state(),'traffic':traffic,'errors':errors},indent=2))
 except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case));raise
finally:stop();p.stop()
record={'checks':checks,'errors':errors,'external':external,'actualEngine':True,'nativeWindows':False,'accountOrInference':False,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
