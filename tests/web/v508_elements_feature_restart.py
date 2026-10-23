"""Cold pending-input restoration in a previously compiler-confirmed OWNED element fixture.
No account/grant/model invocation. Preserves source bytes and original draft proof.
"""
import json,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());fixture=pathlib.Path(sys.argv[3]).resolve();assert fixture.parent==pathlib.Path('/tmp') and fixture.name.startswith('confectory-elements-feature-')
case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-elements-feature-restart-'));project=case/'owned project';shutil.copytree(fixture/'owned project',project,ignore=shutil.ignore_patterns('.confectory','.build'));storage=case/'profile';storage.mkdir();original={p.name:p.read_bytes() for p in project.iterdir() if p.is_file()};id='Owned.Elements::Attack';text='9223372036854775804';description='재시작할 미적용 설명 한글';env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(storage),CONFECTORY_ENTRY_STORAGE=str(storage),CONFECTORY_MCP_DIRECTORY=str(case/'instances'),CONFECTORY_WEB_PROJECT=str(project/'project.cproj'),CONFECTORY_DOTNET=env.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet'));env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];host=None;log=None;errors=[];external=[];checks=[]
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
 if isinstance(body,dict) and body.get('op')=='invoke' and body.get('endpoint')=='reviewDraft' and injected==0:
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
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(-1);page=setup();page.locator('#workspace').click(button='right',position={'x':700,'y':300});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=page.locator('.window[data-key^="browser:project:"]');b.locator('[data-tab=feature]').click();row=b.locator('[data-object="'+id+'"]');expect(row).to_be_visible(timeout=30000);row.get_by_role('button',name='정의 열기',exact=True).click();w=page.locator('.window[data-key=declaration]');expect(w.locator('[data-inline-description]')).to_be_visible(timeout=30000);s=settled();basis=s['declaration'];invoke('editFunctionContract',{'id':id,'revision':basis['revision'],'hash':basis['textHash'],'edit':{'signature':{'args':[{'name':'damage','type':'long'}],'return':'long'},'description':'공격 설명 한글'}});invoke('saveDraft',{});invoke('inspectDeclaration',{'id':id});expect(w.locator('[data-inline-description]')).to_have_value('공격 설명 한글');page.wait_for_function("()=>typeof confectoryFlushPresentation==='function'");page.evaluate('async()=>await confectoryFlushPresentation()');page.close();stop();start(0);page=setup();w=page.locator('.window[data-key=declaration]');description=w.locator('[data-inline-description]');expect(description).to_have_value('공격 설명 한글',timeout=30000);s=settled();assert s['declaration']['signature']['Args'][0]['Name']=='damage',s['declaration'];assert all((project/k).read_bytes()==v for k,v in original.items());checked('cold process restores saved compatible function signature and Korean description without changing final sources')

  for browser_window in page.locator('.window.browser-view:not([hidden])').all():browser_window.locator('[data-close]').click()
  w.locator('[data-feature-action=confirm]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=30000);s=state();old_token=s['review']['token'];assert s['review']['status']=='ready';assert injected==1
  results=[row['result'] for row in traffic if 'result' in row];requests=[row['invoke'] for row in traffic if row.get('invoke',{}).get('endpoint')=='reviewDraft'];matched=[r for r in results if r['requestId'] in [v['requestId'] for v in requests]];assert len(requests)>=2 and any(r.get('error',{}).get('code')=='stale_revision' for r in matched) and any(r.get('ok') for r in matched),(requests,matched);checked('real backend rejects injected stale review transport before execution; bounded retry opens current Review without Confirm or source writes')
  # Changing reviewed content invalidates server token. Old approval is never reusable.
  basis=s['declaration'] or invoke('inspectDeclaration',{'id':id})['state']['declaration'];invoke('editFunctionContract',{'id':id,'revision':basis['revision'],'hash':basis['textHash'],'edit':{'description':'최신 검토 설명'}});failed=invoke('confirmGroup',{'token':old_token,'ids':[id]},False);assert not failed['result'].get('ok');assert all((project/k).read_bytes()==v for k,v in original.items());expect(review.locator('#confirm')).to_be_disabled(timeout=30000);checked('reviewed content change invalidates old token and disables old Confirm; forged stale approval writes no sources')
  review.locator('[data-reject]').click();invoke('inspectDeclaration',{'id':id});expect(description).to_have_value('최신 검토 설명',timeout=30000);settled();w.locator('[data-feature-action=confirm]').click();expect(review).to_be_visible(timeout=30000);s=state();assert s['review']['token']!=old_token;expect(review.get_by_role('group',name='설명',exact=True).locator('[data-semantic-after]')).to_have_text('최신 검토 설명')
  if review.locator('[data-additional-changes]').count():
   review.locator('[data-review-advanced]').click();ack=review.locator('[data-advanced-reviewed]')
   if ack.count():expect(ack).not_to_be_checked();ack.check()
  expect(review.locator('#confirm')).to_be_enabled(timeout=30000);review.locator('#confirm').click();expect(review).to_have_count(0,timeout=60000);assert all((project/k).read_bytes()==v for k,v in original.items() if k!='Attack.celem');text=(project/'Attack.celem').read_text();assert 'damage' in text and 'provide Owned.Elements::Attack with Owned.Elements::AttackBody' in text;page.screenshot(path=str(case/'feature-confirmed.png'));checked('explicit fresh Review and compiler Confirm update only selected function, preserving implementation/body/module/ancestor bytes')
  page.wait_for_function("()=>typeof confectoryFlushPresentation==='function'");page.evaluate('async()=>await confectoryFlushPresentation()');confirmed=(project/'Attack.celem').read_bytes();page.close();stop();start(1);page=setup();w=page.locator('.window[data-key=declaration]');description=w.locator('[data-inline-description]');expect(description).to_have_value('최신 검토 설명',timeout=30000);s=settled();assert not s['draft']['dirty'];assert s['declaration']['signature']['Args'][0]['Name']=='damage';assert (project/'Attack.celem').read_bytes()==confirmed;page.screenshot(path=str(case/'feature-confirmed-restarted.png'));checked('second cold process restores confirmed function content and clean draft without stale Review or duplicate edits');page.close();stop();browser.close();assert not errors and not external,(errors,external)
except Exception:
 try:(case/'traffic.json').write_text(json.dumps(traffic,indent=2));(case/'failure-state.json').write_text(json.dumps(state(),indent=2));(case/'errors.json').write_text(json.dumps(errors))
 except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case));raise
finally:stop()
record={'checks':checks,'errors':errors,'external':external,'actualEngine':True,'accountOrInference':False,'nativeWindows':False,'sourcePreserved':True,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
