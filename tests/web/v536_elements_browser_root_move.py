"""v536 explicit inheritance parent Root regression, separate from Browser classification.
No account/grant/model invocation. Preserves source bytes and original draft proof.
"""
import json,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());fixture=pathlib.Path(sys.argv[3]).resolve();assert fixture==repo.parent/'scratch/v508-elements/actual13-source-fixture'
case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-element-mutation-'));project=case/'owned project';shutil.copytree(fixture/'owned project',project,ignore=shutil.ignore_patterns('.confectory','.build'));(project/'Other.celem').write_text('object Owned.Elements::Other extends Owned.Elements::Unit {data HP = 50;}');(project/'project.cproj').write_text((project/'project.cproj').read_text().replace('registry Confectory.Build.DotNet','element Other object "Other.celem";registry Confectory.Build.DotNet',1));(project/'Third.celem').write_text('object Owned.Elements::Third extends Owned.Elements::Unit {data HP = 60;}');(project/'project.cproj').write_text((project/'project.cproj').read_text().replace('registry Confectory.Build.DotNet','element Third object \"Third.celem\";registry Confectory.Build.DotNet',1));(project/'Bare.celem').write_text('object Owned.Elements::Bare extends Owned.Elements::Unit {}');(project/'project.cproj').write_text((project/'project.cproj').read_text().replace('registry Confectory.Build.DotNet','element Bare object \"Bare.celem\";registry Confectory.Build.DotNet',1));storage=case/'profile';storage.mkdir();original={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file() and '.confectory' not in p.parts};id='Owned.Elements::Serial';text='9223372036854775804';description='재시작할 미적용 설명 한글';env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(storage),CONFECTORY_ENTRY_STORAGE=str(storage),CONFECTORY_MCP_DIRECTORY=str(case/'instances'),CONFECTORY_WEB_PROJECT=str(project/'project.cproj'),CONFECTORY_DOTNET=env.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet'));env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];host=None;log=None;errors=[];external=[];checks=[]
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

def source_same():assert all((project/k).read_bytes()==v for k,v in original.items())
def idle():page.wait_for_function('()=>document.querySelector(".topbar .brand")?.disabled===false')
def flush():page.evaluate('()=>confectoryFlushPresentation()');return state()
def wait_operation(endpoint,after):
 for _ in range(6000):
  ids={r['invoke']['requestId'] for r in traffic[after:] if r.get('invoke',{}).get('endpoint')==endpoint};results=[r['result'] for r in traffic[after:] if r.get('result',{}).get('requestId') in ids];good=[r for r in results if r.get('ok')]
  if good:return good[-1]
  bad=[r for r in results if r.get('error',{}).get('code')!='stale_revision'];assert not bad,bad;page.wait_for_timeout(10)
 raise AssertionError('operation did not complete: '+endpoint)
def wait_any(endpoint,after):
 for _ in range(6000):
  ids={r['invoke']['requestId'] for r in traffic[after:] if r.get('invoke',{}).get('endpoint')==endpoint};results=[r['result'] for r in traffic[after:] if r.get('result',{}).get('requestId') in ids and r.get('result',{}).get('error',{}).get('code')!='stale_revision']
  if results:return results[-1]
  page.wait_for_timeout(10)
 raise AssertionError('no result '+endpoint)
def focus_window(win):
 point=win.evaluate("""el=>{const r=el.getBoundingClientRect();for(let y=r.top+5;y<Math.min(innerHeight-5,r.bottom-5);y+=20)for(let x=r.left+5;x<Math.min(innerWidth-5,r.right-5);x+=20){const at=document.elementFromPoint(x,y);if(at?.closest('.window')===el&&!at.closest('button,input,textarea,select,[data-resize]'))return {x,y};}return null;}""");assert point;page.mouse.click(point['x'],point['y'])
def definition(name):
 idle();focus_window(b);q=b.locator('[data-browser-control="object-query"]');q.fill(name);b.locator('[data-browser-control="object-search"]').click();expect(q).to_have_value(name);b.locator('[data-object="Owned.Elements::'+name+'"]').click(button='right');page.get_by_role('button',name='스키마 열기',exact=True).click();expect(w.locator('.object-title-name')).to_have_text(name,timeout=30000);idle();focus_window(w)
def drop(source,target):
 transfer=page.evaluate_handle('()=>new DataTransfer()');source.dispatch_event('dragstart',{'dataTransfer':transfer});target.dispatch_event('dragover',{'dataTransfer':transfer});target.dispatch_event('drop',{'dataTransfer':transfer})
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(0);page=setup();page.set_viewport_size({'width':1480,'height':1050});idle();page.locator('#workspace').click(button='right',position={'x':700,'y':100});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=page.locator('.window[data-key^="browser:project:"]');w=page.locator('.window[data-key=schema]');definition('Unit');w.locator('[aria-label="HP 기본값"]').fill('111');section=w.locator('.object-variations');row=lambda key:section.locator('[data-object="Owned.Elements::'+key+'"]')
  def keep_unit_input():
   assert any('Owned.Elements::Unit|element|' in key and value.get('text')=='111' for key,value in flush()['presentation']['inputs']['schema'])
  def root_choice(key):
   # Folder Root is a distinct operation, covered by v536_browser_folders_multi_root.py.
   definition(key);focus_window(w);w.locator('.object-parent-change').click();page.locator('.object-parent-picker [data-parent-choice=""]').click()
  root_choice('Bare');assert 'extends Owned.Elements::Unit' in state()['draft']['text'];after=len(traffic);w.locator('[data-element-action=discard]').click();wait_operation('schema',after);assert 'extends Owned.Elements::Unit' in state()['draft']['text'];source_same();keep_unit_input();checked('cancelling an explicit parent Root choice leaves inheritance, all final files and another object private111 unchanged')
  root_choice('Bare');after=len(traffic);w.locator('[data-element-action=save]').click();wait_operation('editObjectStructure',after);wait_operation('saveDraft',after);assert 'extends' not in state()['draft']['text'];source_same();keep_unit_input();checked('the original parent picker saves a valid explicit parent removal to the working copy only, without a classification drop or source publication')
  root_choice('Other');after=len(traffic);w.locator('[data-element-action=save]').click();rejected=wait_any('editObjectStructure',after);assert not rejected['ok'];assert 'extends Owned.Elements::Unit' in state()['draft']['text'];source_same();keep_unit_input();idle();focus_window(w);after=len(traffic);w.locator('[data-element-action=discard]').click();wait_operation('schema',after);assert 'extends Owned.Elements::Unit' in state()['draft']['text'];checked('invalid inherited-data parent removal still fails the full graph guard; cancelling its pending input preserves the existing source')
  definition('Bare');idle();flush();page.close();stop();start(1);page=setup();page.set_viewport_size({'width':1480,'height':1050});w=page.locator('.window[data-key=schema]');expect(w.locator('.object-title-name')).to_have_text('Bare',timeout=60000);assert 'extends' not in state()['draft']['text'];source_same();keep_unit_input();idle();focus_window(w);w.locator('[data-element-action=confirm]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=60000);assert [r['id'] for r in state()['review']['units']]==['Owned.Elements::Bare'];review.locator('[data-reject]').click();expect(review).to_be_hidden();source_same();focus_window(w);w.locator('[data-element-action=confirm]').click();expect(review).to_be_visible(timeout=60000)
  if review.locator('[data-additional-changes]').count():
   review.locator('[data-review-advanced]').click();ack=review.locator('[data-advanced-reviewed]')
   if ack.count():ack.check()
  after=len(traffic);review.locator('#confirm').click();result=wait_operation('confirmGroup',after);assert result['result']['sourceConfirmed'];expect(review).to_be_hidden(timeout=60000);assert 'extends' not in (project/'Bare.celem').read_text();assert all((project/k).read_bytes()==v for k,v in original.items() if k!='Bare.celem');keep_unit_input();idle();page.screenshot(path=str(case/'root-confirmed.png'));checked('saved explicit parent removal survives restart and Review cancel; a separate compiler Confirm changes only Bare while preserving unrelated private input')
  assert not errors and not external,(errors,external);print(json.dumps({'checks':checks,'case':str(case),'categoryMovement':False},ensure_ascii=False,indent=2));page.close();stop();browser.close()
except Exception:
 try:page.screenshot(path=str(case/'root-failure.png'))
 except Exception:pass
 try:(case/'root-failure.json').write_text(json.dumps({'state':state(),'traffic':traffic,'errors':errors},ensure_ascii=False,indent=2))
 except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case),flush=True);raise
finally:stop()
