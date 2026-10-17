"""Real Home, new browser context and actual process restarts; no localStorage or project presentation substitute."""
import json,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request
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
 host=None;stream=None;context=None;page=None;starts=0
 def stop():
  global host,stream,context
  if context:context.close();context=None
  if host:
   os.killpg(host.pid,signal.SIGTERM)
   try:host.wait(timeout=10)
   except subprocess.TimeoutExpired:os.killpg(host.pid,signal.SIGKILL);host.wait()
   host=None;stream.close()
 def start():
  global host,stream,context,page,starts
  stop();log=root/('host-'+str(starts)+'.log');starts+=1;stream=log.open('w');host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True);deadline=time.monotonic()+90;url=None
  while time.monotonic()<deadline:
   for line in log.read_text().splitlines():
    if line.startswith('CONFECTORY_WEB_UI '):url=line.split(' ',1)[1]
   if url:break
   assert host.poll() is None,log.read_text();time.sleep(.05)
  assert url,log.read_text();context=browser.new_context(viewport={'width':1440,'height':1050});page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.goto(url);expect(page.locator('#home-save-state')).to_be_visible(timeout=60000);return url
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
   url=start();expect(page.locator('[data-stat="objects"][data-status="available"]')).to_have_count(2,timeout=60000);public=read_public(url);assert public['projectId']=='' and public['presentation'] is None;assert sorted(x['summary'].get('objects',-1) for x in public['cards'])==[-1,1,41];assert all(x['summary']['packsStatus']=='unsupported' and x['summary']['lastEditStatus']=='unsupported' for x in public['cards']);assert not any('path' in x for x in public['cards']);expect(page.locator('[data-stat="objects"][data-status="unavailable"]')).to_have_text('—');expect(page.locator('[data-stat="objects"][data-status="available"]').filter(has_text='41')).to_have_count(1)
   page.locator('#home-project-search').fill('State');expect(page.locator('[data-project]')).to_have_count(2);page.locator('#home-tab-packs').click();expect(page.locator('#home-pack-list [data-pack]').first).to_be_visible(timeout=60000);page.locator('#home-pack-search').fill('Confectory.BaseUI');page.locator('#home-pack-search').press('Enter');expect(page.locator('#home-pack-list [data-pack]')).to_have_count(2);chosen=page.locator('#home-pack-list [data-pack]').nth(1).get_attribute('data-pack');page.locator('#home-pack-list [data-pack]').nth(1).click();page.locator('#home-pack-search').fill('로컬 미적용 입력');page.locator('#home-pack-sort').click();page.locator('[data-pack-sort="name"]').click();page.locator('[data-pack-group="explore"]').click();page.locator('#home-pack-search').fill('REMOTE_PENDING');page.locator('[data-pack-group="local"]').click();expect(page.locator('#home-pack-search')).to_have_value('로컬 미적용 입력')
   for _ in range(4):page.locator('#home-tab-projects').click();page.locator('#home-tab-packs').click();page.locator('[data-pack-group="local"]').click()
   assert flush();stored=json.loads(prefs.read_text());assert stored['packs']['local']=={'draft':'로컬 미적용 입력','query':'Confectory.BaseUI','sort':'name','selected':chosen};assert catalog.read_bytes()==original_catalog;assert not (storage/'presentations').exists();page.screenshot(path='/tmp/confectory-v480-home-state.png',full_page=True)
   # A new process and a completely fresh browser context restore only host-owned Home state.
   start();expect(page.locator('#home-packs')).to_be_visible(timeout=60000);expect(page.locator('#home-pack-search')).to_have_value('로컬 미적용 입력');expect(page.locator('#home-pack-list [data-pack]')).to_have_count(2,timeout=60000);expect(page.locator('#home-pack-list [aria-pressed="true"]')).to_have_attribute('data-pack',chosen);page.locator('[data-pack-group="explore"]').click();expect(page.locator('#home-pack-search')).to_have_value('REMOTE_PENDING');page.locator('[data-pack-group="local"]').click();expect(page.locator('#home-pack-search')).to_have_value('로컬 미적용 입력');page.locator('#home-tab-projects').click();expect(page.locator('#home-project-search')).to_have_value('State');expect(page.locator('[data-project]')).to_have_count(2);assert flush()
   saved=prefs.read_bytes();prefs.chmod(0o444);page.locator('#home-project-search').fill('FAIL_PENDING');assert not flush();expect(page.locator('#home-save-state')).to_contain_text('저장 실패');expect(page.locator('#home-project-search')).to_have_value('FAIL_PENDING');assert prefs.read_bytes()==saved and catalog.read_bytes()==original_catalog;assert not (storage/'presentations').exists();prefs.chmod(0o644);page.locator('#home-save-retry').click();expect(page.locator('#home-save-state')).to_have_text('Home 보기 저장됨',timeout=60000);assert json.loads(prefs.read_text())['projectQuery']=='FAIL_PENDING';repaired=prefs.read_bytes()
   stop();prefs.write_bytes(b'broken{');start();expect(page.locator('#home-save-state')).to_contain_text('기존 파일을 유지');assert prefs.read_bytes()==b'broken{';expect(page.locator('#home-project-search')).to_have_value('');page.locator('#home-project-search').fill('RECOVERY_PENDING');assert not flush();expect(page.locator('#home-save-state')).to_contain_text('저장 실패');expect(page.locator('#home-project-search')).to_have_value('RECOVERY_PENDING');assert prefs.read_bytes()==b'broken{';prefs.write_bytes(repaired);page.locator('#home-save-retry').click();expect(page.locator('#home-save-state')).to_have_text('Home 보기 저장됨',timeout=60000);assert json.loads(prefs.read_text())['projectQuery']=='RECOVERY_PENDING';assert catalog.read_bytes()==original_catalog
   page.locator('#home-project-search').fill('State');assert flush();page.locator('[data-enter]').first.click();expect(page.locator('#nav')).to_be_enabled(timeout=60000);page.locator('.brand').click();expect(page.locator('#home-project-search')).to_have_value('State');expect(page.locator('[data-project]')).to_have_count(2);assert flush();start();expect(page.locator('#home-project-search')).to_have_value('State');expect(page.locator('[data-project]')).to_have_count(2);assert not errors,errors;assert catalog.read_bytes()==original_catalog;assert all(p.read_bytes()==b for p,b in before.items());page.screenshot(path='/tmp/confectory-v480-home-counts.png',full_page=True)
   print('PASS actual v480 Home preferences: actual cold process/fresh context, separate applied/draft groups and selection, repeated tabs and project return, readonly failure/retry, corrupt-file preservation/recovery, per-project confirmed totals 1/41 and unavailable distinction, unsupported pack/time, no source/presentation/catalog writes',flush=True)
  except Exception:
   if page:
    try:page.screenshot(path='/tmp/confectory-v480-home-state-failure.png',full_page=True);print('Home state failure:',page.locator('#home-save-state').inner_text(),page.locator('#toast').inner_text(),flush=True)
    except Exception:pass
   raise
  finally:
   if prefs.exists():prefs.chmod(0o644)
   stop();browser.close()
