"""Real Home, new browser context and actual process restarts; no localStorage or project presentation substitute."""
import json,os,pathlib,re,shutil,signal,subprocess,sys,tempfile,time,urllib.request
from playwright.sync_api import sync_playwright,expect
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text())
with tempfile.TemporaryDirectory(prefix='confectory-home-state-') as directory:
 root=pathlib.Path(directory);storage=root/'storage';storage.mkdir();first=root/'first';second=root/'second'
 for project in [first,second]:
  shutil.copytree(repo/'examples/button-game',project,ignore=shutil.ignore_patterns('.confectory'));manifest=project/'project.cpack';manifest.write_text(manifest.read_text().replace('../../',str(repo)+'/'))
 manifest=second/'project.cpack';raw=manifest.read_text();i=raw.rfind('}');manifest.write_text(raw[:i]+''.join('element Extra'+str(n)+' object "extra-'+str(n)+'.celem";' for n in range(40))+raw[i:])
 for n in range(40):(second/('extra-'+str(n)+'.celem')).write_text('object Example.ButtonGame::Extra'+str(n)+' {}')
 cards=[{'path':str(first/'project.cpack'),'title':'State Project One','description':'First confirmed owner','favorite':False},{'path':str(second/'project.cpack'),'title':'State Project Two','description':'Different root total','favorite':True},{'path':str(root/'missing.cpack'),'title':'Missing Project','description':'Unavailable file','favorite':False}];catalog=storage/'projects.json';catalog.write_text(json.dumps(cards,separators=(',',':')));original_catalog=catalog.read_bytes();before={p:p.read_bytes() for project in [first,second] for p in project.rglob('*') if p.is_file()};prefs=storage/'home-preferences.json'
 env=os.environ.copy();env.pop('CONFECTORY_WEB_PROJECT',None);env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(storage),CONFECTORY_ENTRY_STORAGE=str(storage),XDG_DATA_HOME=str(root/'data'),XDG_CACHE_HOME=str(root/'cache'))
 if env.get('CONFECTORY_DOTNET'):env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH']
 host=None;stream=None;context=None;page=None;starts=0;held_summaries=[]
 def stop():
  global host,stream,context
  if context:context.close();context=None
  if host:
   os.killpg(host.pid,signal.SIGTERM)
   try:host.wait(timeout=10)
   except subprocess.TimeoutExpired:os.killpg(host.pid,signal.SIGKILL);host.wait()
   host=None;stream.close()
 def start(pending_initial=False,hold_summary=False):
  global host,stream,context,page,starts
  stop();log=root/('host-'+str(starts)+'.log');starts+=1;stream=log.open('w');host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True);deadline=time.monotonic()+90;url=None
  while time.monotonic()<deadline:
   for line in log.read_text().splitlines():
    if line.startswith('CONFECTORY_WEB_UI '):url=line.split(' ',1)[1]
   if url:break
   assert host.poll() is None,log.read_text();time.sleep(.05)
  assert url,log.read_text();context=browser.new_context(viewport={'width':1440,'height':1050});page=context.new_page();page.on('pageerror',lambda e:(errors.append(str(e)),print('Home browser error at host',starts,getattr(e,'stack',str(e)),flush=True)))
  if pending_initial:
   blocked=[]
   def delay_initial(route):
    request=route.request.post_data_json
    if request.get('op')=='invoke' and request.get('endpoint')=='globalHelpers':blocked.append(route);return
    route.continue_()
   context.route('**/api/request',delay_initial)
  if hold_summary:
   held_summaries.clear()
   def hold_summary_request(route):
    body=route.request.post_data_json
    if body.get('op')=='invoke' and body.get('endpoint')=='homeSummaries' and not held_summaries:held_summaries.append(route);return
    route.continue_()
   context.route('**/api/request',hold_summary_request)
  page.goto(url,wait_until='domcontentloaded');expect(page.locator('#home-save-state')).to_be_visible(timeout=60000)
  if hold_summary:
   deadline=time.monotonic()+30
   while not held_summaries and time.monotonic()<deadline:page.wait_for_timeout(10)
   assert held_summaries,'Home summary request was not held'
  if pending_initial:
   deadline=time.monotonic()+30
   while not blocked and time.monotonic()<deadline:page.wait_for_timeout(10)
   assert blocked,'initial helper request was not held';page.evaluate("()=>dispatchEvent(new PageTransitionEvent('pagehide'))");page.wait_for_timeout(100)
   for route in blocked:route.abort()
   context.unroute('**/api/request');assert not errors,errors
  return url
 def flush():return page.evaluate('()=>globalThis.confectoryFlushHomePreferences()')
 def read_public(url):
  origin,token=url.split('/#');req=lambda v:json.load(urllib.request.urlopen(urllib.request.Request(origin+'/api/request',data=json.dumps(v).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':token}),timeout=20))
  for _ in range(400):
   v=req({'op':'mount'})
   if v.get('error',{}).get('code')=='busy':time.sleep(.02);continue
   assert v['ok'],v;assert req({'op':'dispose','view':v['view'],'scope':v['scope']})['ok'];return v['state']
  raise AssertionError('public snapshot unavailable')
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);errors=[]
  try:
   start(pending_initial=True) # A real pagehide must retire a pending initial read without an unhandled rejection.
   # The ordinary ButtonGame now reaches FrameControl as well as the previous ten packs.
   url=start(hold_summary=True);entry=page.locator('[data-enter]').first.element_handle();assert entry;held_summaries[0].continue_()
   expect(page.locator('[data-stat="objects"][data-status="available"]')).to_have_count(2,timeout=60000)
   assert entry.evaluate('node=>node.isConnected'),'summary-only update replaced the project entry button'
   public=read_public(url);assert public['projectId']=='' and public['presentation'] is None;assert sorted(x['summary'].get('objects',-1) for x in public['cards'])==[-1,1,41];assert all(x['summary']['packsStatus']=='available' and x['summary']['packs']==11 and x['summary']['lastEditStatus']=='none' for x in public['cards'] if x['summary']['status']=='available');assert not any('path' in x for x in public['cards']);expect(page.locator('[data-stat="objects"][data-status="unavailable"]')).to_have_text('—');expect(page.locator('[data-stat="objects"][data-status="available"]').filter(has_text='41')).to_have_count(1)
   page.locator('#home-project-search').fill('State');expect(page.locator('[data-project]')).to_have_count(2);page.locator('#home-tab-packs').click();expect(page.locator('#home-pack-list [data-pack]').first).to_be_visible(timeout=60000);page.locator('#home-pack-search').fill('Confectory.BaseUI');page.locator('#home-pack-search').press('Enter');expect(page.locator('#home-pack-list [data-pack]')).to_have_count(2);chosen=page.locator('#home-pack-list [data-pack]').nth(1).get_attribute('data-pack');page.locator('#home-pack-list [data-pack]').nth(1).click();page.locator('#home-pack-search').fill('로컬 미적용 입력');page.locator('#home-pack-sort').click();page.locator('[data-pack-sort="name"]').click();page.locator('[data-pack-group="explore"]').click();page.locator('#home-pack-search').fill('REMOTE_PENDING');page.locator('[data-pack-group="local"]').click();expect(page.locator('#home-pack-search')).to_have_value('로컬 미적용 입력')
   for _ in range(4):page.locator('#home-tab-projects').click();page.locator('#home-tab-packs').click();page.locator('[data-pack-group="local"]').click()
   assert flush();stored=json.loads(prefs.read_text());assert stored['packs']['local']=={'draft':'로컬 미적용 입력','query':'Confectory.BaseUI','sort':'name','selected':chosen};assert catalog.read_bytes()==original_catalog;assert not (storage/'presentations').exists();page.screenshot(path='/tmp/confectory-v480-home-state.png',full_page=True)
   # A new process and a completely fresh browser context restore only host-owned Home state.
   start();expect(page.locator('#home-packs')).to_be_visible(timeout=60000);expect(page.locator('#home-pack-search')).to_have_value('로컬 미적용 입력');expect(page.locator('#home-pack-list [data-pack]')).to_have_count(2,timeout=60000);expect(page.locator('#home-pack-list [aria-pressed="true"]')).to_have_attribute('data-pack',chosen);page.locator('[data-pack-group="explore"]').click();expect(page.locator('#home-pack-search')).to_have_value('REMOTE_PENDING');page.locator('[data-pack-group="local"]').click();expect(page.locator('#home-pack-search')).to_have_value('로컬 미적용 입력');page.locator('#home-tab-projects').click();expect(page.locator('#home-project-search')).to_have_value('State');expect(page.locator('[data-project]')).to_have_count(2);assert flush()
   saved=prefs.read_bytes();prefs.chmod(0o444);page.locator('#home-project-search').fill('FAIL_PENDING');assert not flush();expect(page.locator('#home-save-state')).to_contain_text('저장 실패');expect(page.locator('#home-project-search')).to_have_value('FAIL_PENDING');assert prefs.read_bytes()==saved and catalog.read_bytes()==original_catalog;assert not (storage/'presentations').exists();prefs.chmod(0o644);page.locator('#home-save-retry').click();expect(page.locator('#home-save-state')).to_have_text('Home 보기 저장됨',timeout=60000);assert json.loads(prefs.read_text())['projectQuery']=='FAIL_PENDING';repaired=prefs.read_bytes()
   stop();prefs.write_bytes(b'broken{');start();expect(page.locator('#home-save-state')).to_contain_text('기존 파일을 유지');assert prefs.read_bytes()==b'broken{';expect(page.locator('#home-project-search')).to_have_value('');page.locator('#home-project-search').fill('RECOVERY_PENDING');assert not flush();expect(page.locator('#home-save-state')).to_contain_text('저장 실패');expect(page.locator('#home-project-search')).to_have_value('RECOVERY_PENDING');assert prefs.read_bytes()==b'broken{';prefs.write_bytes(repaired);page.locator('#home-save-retry').click();expect(page.locator('#home-save-state')).to_have_text('Home 보기 저장됨',timeout=60000);assert json.loads(prefs.read_text())['projectQuery']=='RECOVERY_PENDING';assert catalog.read_bytes()==original_catalog
   page.locator('#home-project-search').fill('State');assert flush();page.locator('[data-enter]').first.click();expect(page.locator('#nav')).to_be_enabled(timeout=60000);page.locator('.brand').click();expect(page.locator('#home-project-search')).to_have_value('State');expect(page.locator('[data-project]')).to_have_count(2);assert flush();start();expect(page.locator('#home-project-search')).to_have_value('State');expect(page.locator('[data-project]')).to_have_count(2);assert not errors,errors;assert catalog.read_bytes()==original_catalog;assert all(p.read_bytes()==b for p,b in before.items());page.screenshot(path='/tmp/confectory-v480-home-counts.png',full_page=True)
   # Actual source controls feed the new Home summaries; restart with no browser storage.
   url=start(hold_summary=True);page.locator('[data-enter]').filter(has_text='State Project One').click();held_summaries[0].continue_()
   expect(page.locator('#nav')).to_be_enabled(timeout=120000);page.locator('.brand').click()
   expect(page.locator('[data-stat="packs"][data-status="available"]')).to_have_count(2,timeout=60000)
   public=read_public(url);one=next(c['id'] for c in public['cards'] if c['title']=='State Project One');original_score=(first/'Score.celem').read_bytes()
   def enter_score():
    expect(page.locator('[data-enter="'+one+'"]').first).to_be_visible();page.locator('[data-enter="'+one+'"]').click();expect(page.locator('#nav')).to_be_enabled(timeout=120000);page.locator('#nav').click();page.locator('.nav-menu').get_by_role('button',name='개념',exact=True).click();expect(page.locator('#nav')).to_be_enabled(timeout=120000)
    if page.locator('.nav-menu').count():page.locator('#nav').click()
    browser_window=page.locator('.window[data-key="browser"]');expect(browser_window.locator('[data-namespace="Example.ButtonGame"]')).to_be_visible(timeout=120000);browser_window.locator('[data-namespace="Example.ButtonGame"]').click();expect(browser_window.locator('[data-browser-definition="Example.ButtonGame::Score"]')).to_be_visible(timeout=120000);browser_window.locator('[data-browser-definition="Example.ButtonGame::Score"]').click();expect(page.locator('[data-schema-field="initial"]')).to_be_visible(timeout=120000)
   def home_event(kind=None):
    page.locator('.brand').click();expect(page.locator('[data-project="'+one+'"] [data-stat="lastEdit"][data-status="available"]')).to_be_visible(timeout=120000);
    if kind:expect(page.locator('[data-project="'+one+'"] time[data-stat="lastEdit"]')).to_have_attribute('title',re.compile(('원본 Confirm' if kind=='confirm' else '초안 Save')+' 성공'),timeout=120000)
    snapshot=read_public(url);return next(c['summary']['lastEdit'] for c in snapshot['cards'] if c['id']==one)
   enter_score();value=page.locator('[data-schema-field="initial"]');value.fill('7');value.locator('..').get_by_role('button',name='Apply field',exact=True).click();expect(page.locator('#status')).to_have_text('Shared field draft updated',timeout=120000);page.locator('#semantic-save').click();expect(page.locator('#status')).to_have_text('Draft saved; final sources unchanged',timeout=120000)
   saved_event=home_event();assert saved_event['kind']=='save' and saved_event['sequence']==1;assert (first/'Score.celem').read_bytes()==original_score
   url=start();expect(page.locator('[data-project="'+one+'"] time[data-stat="lastEdit"]')).to_have_attribute('datetime',saved_event['at'],timeout=120000);assert next(c['summary']['lastEdit'] for c in read_public(url)['cards'] if c['id']==one)==saved_event
   enter_score();expect(page.locator('[data-schema-field="initial"]')).to_have_value('7');page.locator('#semantic-review').click();expect(page.locator('#confirm')).to_be_enabled(timeout=120000);page.locator('.window[data-key="review"] [data-close]').click();assert home_event()==saved_event
   enter_score();page.locator('#semantic-review').click();expect(page.locator('#confirm')).to_be_enabled(timeout=120000);page.locator('#confirm').click();expect(page.locator('#status')).to_contain_text('Source confirmed',timeout=120000);confirmed_event=home_event('confirm');assert confirmed_event['kind']=='confirm' and confirmed_event['sequence']==2,confirmed_event;assert b'initial = 7' in (first/'Score.celem').read_bytes()
   url=start();expect(page.locator('[data-project="'+one+'"] time[data-stat="lastEdit"]')).to_have_attribute('datetime',confirmed_event['at'],timeout=120000);assert next(c['summary']['lastEdit'] for c in read_public(url)['cards'] if c['id']==one)==confirmed_event
   expect(page.locator('[data-project="'+one+'"] [data-stat="packs"]')).to_have_text('11');assert catalog.read_bytes()==original_catalog and not errors,errors;page.screenshot(path='/tmp/confectory-v480-home-summary.png',full_page=True)
   print('PASS actual v480 Home preferences: pending initial-read pagehide cancellation, actual cold process/fresh context, separate applied/draft groups and selection, repeated tabs and project return, readonly failure/retry, corrupt-file preservation/recovery, per-project confirmed totals 1/41 and unavailable distinction, actual entry/target inclusion (11, includes FrameControl and excludes registered build tool), source Save and compiler Confirm event, review cancellation, exact process/fresh-context event restore, no incidental source/catalog writes',flush=True)
  except Exception:
   if page:
    try:page.screenshot(path='/tmp/confectory-v480-home-state-failure.png',full_page=True);print('Home state failure:',page.locator('#home-save-state').inner_text(),page.locator('#toast').inner_text(),flush=True)
    except Exception:pass
   raise
  finally:
   if prefs.exists():prefs.chmod(0o644)
   stop();browser.close()
