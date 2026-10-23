"""v536 documents/floating over Pack Manager in the actual generated engine.
No account/grant/model invocation. Preserves source bytes and original draft proof.
"""
import json,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());fixture=pathlib.Path(sys.argv[3]).resolve();assert fixture==repo.parent/'scratch/v508-elements/actual13-source-fixture'
case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-element-reentry-'));project=case/'owned project';shutil.copytree(fixture/'owned project',project,ignore=shutil.ignore_patterns('.confectory','.build'));storage=case/'profile';storage.mkdir();original={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file() and '.confectory' not in p.parts};id='Owned.Elements::Serial';text='9223372036854775804';description='재시작할 미적용 설명 한글';env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(storage),CONFECTORY_ENTRY_STORAGE=str(storage),CONFECTORY_MCP_DIRECTORY=str(case/'instances'),CONFECTORY_WEB_PROJECT=str(project/'project.cproj'),CONFECTORY_DOTNET=env.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet'));env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];host=None;log=None;errors=[];external=[];checks=[]
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

def completed(endpoint,after=0):
 for _ in range(1200):
  requests={x['invoke']['requestId'] for x in traffic[after:] if x.get('invoke',{}).get('endpoint')==endpoint}
  rows=[x['result'] for x in traffic[after:] if x.get('result',{}).get('requestId') in requests]
  valid=[x for x in rows if x.get('ok')]
  if valid:return valid[-1]
  rejected=[x for x in rows if not x.get('ok') and x.get('error',{}).get('code')!='stale_revision'];assert not rejected,rejected;page.wait_for_timeout(20)
 raise AssertionError('missing server completion '+endpoint)

try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(0);page=setup();page.set_viewport_size({'width':2700,'height':1500});page.locator('#workspace').click(button='right',position={'x':80,'y':100});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();browser_key='browser:project:root';b=page.locator('.window[data-key^="browser:project:"]');browser_key=b.get_attribute('data-key');q=b.locator('[data-browser-control="object-query"]')
  def window(slot):return page.locator('.window[data-key="editor-'+str(slot)+'"]')
  def hp(slot):return window(slot).locator('[aria-label="HP 기본값"]')
  def row(name):
   expect(q).to_be_enabled();q.fill(name);b.locator('[data-browser-control="object-search"]').click();result=b.locator('[data-object="Owned.Elements::'+name+'"]');expect(result).to_be_visible();return result
  def new(name,slot,arrange=True):
   row(name).click(button='right',position={'x':8,'y':8});page.locator('.context-menu').get_by_role('button',name='새 창으로 열기',exact=True).click();expect(window(slot).locator('.object-title-name')).to_have_text(name,timeout=30000)
   if arrange:
    title=window(slot).locator('.object-title-name').bounding_box();box=window(slot).bounding_box();target=980+(int(slot)-1)*500;page.mouse.move(title['x']+10,title['y']+8);page.mouse.down();page.mouse.move(target+title['x']-box['x']+10,160+title['y']-box['y']+8,steps=15);page.mouse.up()
  def flush():page.evaluate('()=>confectoryFlushPresentation()');return state()
  def unchanged(except_monster=False):assert all((project/k).read_bytes()==v for k,v in original.items() if not except_monster or k!='Monster.celem')
  def dock(key):
   tab=page.locator('[data-window-tab="'+key+'"]')
   if tab.count():tab.click();return
   page.locator('.window[data-key="'+key+'"]').locator('.window-title').click(button='right',position={'x':100,'y':8});page.locator('.context-menu').get_by_role('button',name='탭으로 열기',exact=True).click();expect(tab).to_be_visible()
  new('Unit',1);page.evaluate('()=>globalThis.oldUnitDiscard=document.querySelector(".window[data-key=editor-1] [data-element-action=discard]").onclick');window(1).locator('[data-close]').click();new('Monster',2);hp(2).fill('222');new('Monster',3);hp(3).fill('333');new('Slime',1);expect(hp(2)).to_have_value('222');expect(hp(3)).to_have_value('333');s=flush();assert [(v['view'],v['id']) for v in s['editorViews'] if v['view']=='1']==[('1','Owned.Elements::Slime')];assert len(s['editorViews'])==3;assert not [x for x in s['presentation']['layout'] if x['key']=='editor-1' and x.get('meta',{}).get('id')=='Owned.Elements::Unit'];unchanged();checked('original menu reclaims only a hidden clean Unit cursor for Slime; both Monster inputs, three-slot cap and source bytes remain intact')
  hp(1).fill('111');before=len(traffic);page.evaluate('()=>oldUnitDiscard()');page.evaluate('()=>confectoryFlushPresentation()');expect(hp(1)).to_have_value('111');assert not [x for x in traffic[before:] if x.get('invoke',{}).get('endpoint') in ['editViewField','browserDrafts'] and x['invoke'].get('input',{}).get('action')=='discard'];row('Unit').click(button='right',position={'x':8,'y':8});page.locator('.context-menu').get_by_role('button',name='새 창으로 열기',exact=True).click();expect(page.locator('#toast')).to_contain_text('세 개');expect(hp(2)).to_have_value('222');expect(hp(3)).to_have_value('333');unchanged();checked('retired callback cannot affect the replacement cursor; all pending cursors refuse reclamation without deleting input')
  at=len(traffic);window(2).locator('[data-element-action="save"]').click();completed('saveEditorView',at);expect(window(2).locator('[data-element-error]')).to_have_text('');window(3).locator('[data-element-action="discard"]').click();expect(hp(3)).to_have_value('222');s=flush();basis=next(v for v in s['editorViews'] if v['view']=='2')['schema'];invoke('editViewField',{'view':'2','id':'Owned.Elements::Monster','path':['HP'],'field':'HP','valueJson':'223','revision':basis['revision'],'hash':basis['textHash']});expect(hp(3)).to_have_value('223');hp(3).fill('334');window(3).locator('[data-element-action="discard"]').click();expect(hp(3)).to_have_value('223');s=flush();assert 'data HP = 223' in next(v for v in s['editorViews'] if v['view']=='2')['draft']['text'];assert not [x for x in traffic if x.get('invoke',{}).get('endpoint')=='browserDrafts' and x['invoke']['input'].get('action')=='discard'];expect(hp(1)).to_have_value('111');unchanged();checked('local cancel rechecks current server state and preserves another cursor shared unsaved stage instead of discarding its work')
  at=len(traffic);window(2).locator('[data-element-action="save"]').click();completed('saveEditorView',at);hp(2).fill('224');window(2).locator('[data-element-action="confirm"]').click();review=page.locator('.window[data-key="review"]');expect(review).to_be_visible(timeout=30000);unchanged();review.locator('[data-reject]').click();unchanged();expect(hp(1)).to_have_value('111');window(2).locator('[data-element-action="confirm"]').click();expect(review).to_be_visible(timeout=30000)
  for choice in review.locator('input[type="checkbox"][data-review-id]').all():choice.check()
  if review.locator('[data-additional-changes]').count():
   review.locator('[data-review-advanced]').click();ack=review.locator('[data-advanced-reviewed]')
   if ack.count():ack.check()
  at=len(traffic);expect(review.locator('#confirm')).to_be_enabled(timeout=30000);review.locator('#confirm').click();result=completed('confirmGroup',at);assert result['result']['sourceConfirmed'];expect(review).to_have_count(0,timeout=30000);assert 'data HP = 224' in (project/'Monster.celem').read_text();unchanged(True);expect(hp(1)).to_have_value('111');hp(2).fill('225');at=len(traffic);window(2).locator('[data-element-action="save"]').click();completed('saveEditorView',at);expect(window(2).locator('[data-element-error]')).to_have_text('');assert 'data HP = 224' in (project/'Monster.celem').read_text();checked('bound element explicit Review can cancel without source writes; separate selected compiler Confirm writes only Monster and same cursor edits again afterward')
  dock(browser_key);target=row('Monster').get_by_role('button',name='정의 열기',exact=True);page.evaluate('()=>confectoryFlushPresentation()');hp(2).evaluate('e=>globalThis.monsterHP=e');target.click();expect(page.locator('[data-window-tab="editor-2"]')).to_have_attribute('aria-selected','true');expect(hp(2)).to_have_value('225');assert hp(2).evaluate('e=>e===monsterHP');page.locator('[data-window-tab-close="editor-2"]').click();page.locator('[data-window-tab="'+browser_key+'"]').click();row('Monster').get_by_role('button',name='정의 열기',exact=True).click();expect(hp(2)).to_have_value('225');assert hp(2).evaluate('e=>e===monsterHP');page.locator('[data-window-tab="'+browser_key+'"]').click();row('Slime').get_by_role('button',name='정의 열기',exact=True).click();expect(hp(1)).to_have_value('111');expect(page.locator('[data-window-tab="editor-1"]')).to_have_attribute('aria-selected','true');page.locator('[data-window-tab-close="editor-1"]').click();page.locator('[data-window-tab="'+browser_key+'"]').click();new('Slime',1,False);expect(page.locator('[data-window-tab="'+browser_key+'"]')).to_have_attribute('aria-selected','true');expect(hp(1)).to_have_value('111');page.locator('#workspace-pack-tab').click();expect(page.locator('#workspace-pack-tab')).to_have_attribute('aria-selected','true');expect(hp(1)).to_be_visible();expect(hp(1)).to_have_value('111');checked('normal document definition open and close/reentry retain exact owned input DOM; explicit new-window floats above document and Pack Manager without changing its owner')
  s=flush();basis=next(v for v in s['editorViews'] if v['view']=='3')['schema'];owner=s['projectId'];presentation=s['presentation'];page.close();legacy=owner+'|Owned.Elements::Monster|view:3|["HP"]';presentation['inputs']['schema'].append([legacy,{'text':'226','revision':basis['revision'],'hash':basis['textHash']}]);invoke('savePresentation',{'presentation':presentation});stop();start(1);page=setup();page.set_viewport_size({'width':2700,'height':1500});expect(hp(1)).to_have_value('111',timeout=60000);expect(hp(2)).to_have_value('225',timeout=60000);expect(hp(3)).to_have_value('226',timeout=60000);s=flush();pending=s['presentation']['inputs']['schema'];assert not [k for k,v in pending if k==legacy];assert any(k==owner+'|Owned.Elements::Monster|view:3|element|["HP"]' and v['text']=='226' for k,v in pending);assert len(s['editorViews'])==3;assert not s['presentation'].get('recoveryFailed');expect(page.locator('#workspace-pack-tab')).to_have_attribute('aria-selected','true');unchanged(True);checked('actual process restart restores replacement bindings and Pack background; previous generic property input migrates only its own cursor, retaining other input and source proof')
  # Closed document #2 is restored by its original Browser entry; mobile uses the same owned binding.
  for slot in [1,2,3]:
   if window(slot).is_visible():
    close_tab=page.locator('[data-window-tab-close="editor-'+str(slot)+'"]')
    if close_tab.count():close_tab.click()
    else:window(slot).locator('[data-close]').click()
  page.set_viewport_size({'width':390,'height':844});page.locator('[data-mobile-files]').click();b=page.locator('.window[data-key="browser:project:mobile"]');q=b.locator('[data-browser-control="object-query"]');row('Slime').get_by_role('button',name='정의 열기',exact=True).click();expect(page.locator('[data-window-tab="editor-1"]')).to_have_attribute('aria-selected','true');expect(hp(1)).to_have_value('111');page.screenshot(path=str(case/'mobile-reentry.png'));page.set_viewport_size({'width':2700,'height':1500});s=flush();assert len(s['editorViews'])==3;expect(hp(3)).to_have_value('226');unchanged(True);checked('ordinary mobile List to definition reentry reuses the exact project-owned cursor with input intact instead of allocating another View')
  page.locator('[data-window-tab="browser:project:mobile"]').click();row('Monster').click(button='right',position={'x':8,'y':8});page.locator('.context-menu').get_by_role('button',name='새 창으로 열기',exact=True).click();expect(hp(3)).to_be_visible();window(3).locator('[data-element-action="discard"]').click();expect(hp(3)).to_have_value('225');page.evaluate('()=>confectoryFlushPresentation()');assert all(not message.strip() for message in page.locator('[data-element-error]').all_text_contents());expect(hp(1)).to_have_value('111');unchanged(True);page.screenshot(path=str(case/'final-cursors.png'));checked('legacy cursor cancel reads latest saved value after restart; serialized background status leaves no stale-revision banner or cross-window input loss')
  assert not errors and not external,(errors,external);result={'checks':checks,'actualEngine':True,'sourceChangeOnlyAfterExplicitConfirm':'Monster HP224','errors':errors,'external':external,'nativeWindows':False,'actualCredentialsOrInference':False,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2));page.close();stop();browser.close()
except Exception:
 try:(case/'failure.json').write_text(json.dumps({'state':state(),'traffic':traffic,'errors':errors},ensure_ascii=False,indent=2))
 except Exception:pass
 try:page.screenshot(path=str(case/'failure.png'))
 except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case),flush=True);raise
finally:stop()
