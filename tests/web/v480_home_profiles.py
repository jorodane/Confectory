from editor_navigation import goto_editor
"""IMP1 through the ordinary EditorHome transport, real private files and cold processes."""
import hashlib,json,os,pathlib,re,shutil,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
expect.set_options(timeout=45000)
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text())
root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-home-profiles-'));storage=root/'storage';storage.mkdir()
projects=[root/'first',root/'second'];before={}
for project in projects:
 shutil.copytree(repo/'examples/button-game',project,ignore=shutil.ignore_patterns('.confectory'))
 manifest=project/'project.cpack';manifest.write_text(manifest.read_text().replace('../../',str(repo)+'/'))
 before.update({p:p.read_bytes() for p in project.rglob('*') if p.is_file()})
cards=[{'path':str(p/'project.cpack'),'title':'Profile Project '+str(n+1),'description':'Local listing '+str(n+1)} for n,p in enumerate(projects)]
cards.append({'path':str(root/'missing.cpack'),'title':'Missing','description':'Retained unavailable listing'})
catalog=storage/'projects.json';catalog.write_text(json.dumps(cards));ids=[hashlib.sha256(c['path'].encode()).hexdigest()[:32].upper() for c in cards]
env=os.environ.copy();env.pop('CONFECTORY_WEB_PROJECT',None);env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(storage),CONFECTORY_ENTRY_STORAGE=str(storage),XDG_DATA_HOME=str(root/'data'),XDG_CACHE_HOME=str(root/'cache'))
if env.get('CONFECTORY_DOTNET'):env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH']
host=None;stream=None;page=None;errors=[];endpoints=[];starts=0

def stop():
 global host,stream,page
 if page:page.context.close();page=None
 if host:
  os.killpg(host.pid,signal.SIGTERM)
  try:host.wait(timeout=10)
  except subprocess.TimeoutExpired:os.killpg(host.pid,signal.SIGKILL);host.wait()
  host=None;stream.close()
def start():
 global host,stream,page,starts,origin,token
 stop();starts+=1;log=root/('host-'+str(starts)+'.log');stream=log.open('w');host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
 deadline=time.monotonic()+90;url=None
 while time.monotonic()<deadline:
  for line in log.read_text().splitlines():
   if line.startswith('CONFECTORY_WEB_UI '):url=line.split(' ',1)[1]
  if url:break
  assert host.poll() is None,log.read_text();time.sleep(.05)
 assert url,log.read_text();origin,token=url.split('/#');context=browser.new_context(viewport={'width':1440,'height':1100});page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
 def track(req):
  if req.url.endswith('/api/request') and req.method=='POST':
   b=req.post_data_json
   if b.get('op')=='invoke':endpoints.append(b.get('endpoint'))
 page.on('request',track);goto_editor(page,url);expect(page.locator('[data-enter]')).to_have_count(3);expect(page.locator('#add-helper')).to_be_enabled()
def send(body):
 return json.load(urllib.request.urlopen(urllib.request.Request(origin+'/api/request',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':token}),timeout=30))
def mount():
 for _ in range(600):
  v=send({'op':'mount'})
  if v.get('error',{}).get('code')=='busy':time.sleep(.02);continue
  assert v['ok'],v;return v
 raise AssertionError('mount remained busy')
def state():
 v=mount()
 try:return v['state']
 finally:assert send({'op':'dispose','view':v['view'],'scope':v['scope']})['ok']
def invoke(endpoint,data,accepted=True):
 v=mount();req=str(uuid.uuid4());envelope={'view':v['view'],'scope':v['scope']}
 try:
  r=send(dict(envelope,op='invoke',endpoint=endpoint,input=data,requestId=req,expectedRevision=v['revision']))
  assert r['ok'],r
  for _ in range(600):
   r=send(dict(envelope,op='update'));assert r['ok'],r
   result=next((row for row in r.get('results',[]) if row['requestId']==req),None)
   if result:
    assert result['status']==('completed' if accepted else 'failed'),result
    return result.get('value')
   time.sleep(.02)
  raise AssertionError('invoke stayed pending')
 finally:assert send(dict(envelope,op='dispose'))['ok']
def info(index=0):
 if page.locator('#title').count():page.locator('#title').click()
 else:page.locator('[data-manage="'+ids[index]+'"]').click()
 page.locator('.context-menu').get_by_role('button',name='프로젝트 정보',exact=True).click();expect(page.locator('[data-project-information]')).to_be_visible();return page.get_by_role('dialog',name='프로젝트 정보',exact=True)
def close():page.locator('#overlays .modal [data-close]').click()
def enter(index=0):page.locator('[data-enter="'+ids[index]+'"]').click();expect(page.locator('#nav')).to_be_enabled()
def helper_card():
 page.locator('.home-side [data-helper="main-helper"]').first.click();return page.locator('.participant-expanded-card[data-helper-id="main-helper"]')
def settings():
 c=helper_card();c.locator('.helper-window-settings').click();expect(page.locator('[data-helper-settings]')).to_be_visible();return page.locator('[data-helper-settings]')
def invariant(project=None):
 s=state();assert len(s['cards'])==3 and s['aiState']=='idle' and s['aiPreview'] is None and not s['workers'] and s['connection'] is None,s
 if project is not None:assert s['projectId']==project
 assert all(p.read_bytes()==raw for p,raw in before.items()),'confirmed project source changed'
 assert len(list(root.rglob('project.cpack')))==2,'profile created a separate project'
 assert not errors,errors
 return s
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 try:
  start();r=info();expect(r.locator('[data-project-kind]')).to_have_text('project');expect(r.locator('[data-project-requirements]')).to_contain_text('Confectory.BaseUI');assert not any((project/'.confectory').exists() for project in projects)
  r.locator('[data-information-title]').fill('Edited local title');r.locator('[data-information-description]').fill('Unapplied listing description');close();r=info();expect(r.locator('[data-information-title]')).to_have_value('Edited local title');assert json.loads(catalog.read_text())[0]['title']=='Profile Project 1'
  r.locator('button[type=submit]').click();expect(r).to_have_count(0);expect(page.locator('[data-enter="'+ids[0]+'"]')).to_contain_text('Edited local title');assert json.loads(catalog.read_text())[0]['description']=='Unapplied listing description'
  r=info();r.locator('[data-information-description]').fill('CAS retained listing input');catalog_bytes=catalog.read_bytes();external_bytes=catalog_bytes+b'\n';catalog.write_bytes(external_bytes);r.locator('button[type=submit]').click();expect(page.locator('#status')).to_contain_text('입력은 유지');expect(r.locator('[data-information-description]')).to_have_value('CAS retained listing input');assert catalog.read_bytes()==external_bytes;catalog.write_bytes(catalog_bytes);r.locator('[data-information-discard]').click()
  r=info(2);expect(r.locator('[data-project-kind]')).to_have_text('유형 확인 불가');close();assert not (root/'missing.cpack').exists();invariant('')
  # Home profile edit and global draft have no project context at all.
  page.locator('#add-helper').click();page.locator('[data-recruit="global"]').click();expect(page.locator('#global-helper-list')).to_contain_text('main-helper');close();helper_store=storage/'helpers/helpers.json';immutable_helper=helper_store.read_bytes();imported_profile=next((storage/'helper-presentations').glob('*.json')).read_bytes();r=settings();r.locator('#participant-name').fill('Local Chief');r.locator('#participant-short-description').fill('Display role');r.locator('#participant-description').fill('Display biography');close();r=settings();expect(r.locator('#participant-name')).to_have_value('Local Chief');assert next((storage/'helper-presentations').glob('*.json')).read_bytes()==imported_profile;r.locator('[data-profile-save]').click();expect(r).to_have_count(0)
  c=helper_card();expect(c.locator('.helper-profile-identity>strong')).to_have_text('Local Chief');c.locator('textarea').fill('GLOBAL ONLY unsent draft');c.locator('textarea').fill('GLOBAL second saved draft');page.evaluate('()=>globalThis.confectoryFlushPresentation()');expect(c.locator('textarea')).to_have_value('GLOBAL second saved draft');expect(page.locator('#add-helper')).to_be_enabled();assert json.loads(next((storage/'helper-presentations').glob('*.json')).read_text())['globalDraft']=='GLOBAL second saved draft';c.locator('[data-close]').click();invariant('');assert helper_store.read_bytes()==immutable_helper
  saved_profile=state()['helpers'][0]['presentation'];bad=dict(saved_profile['value']);bad['memory']='cannot inject AI memory';profile_path=next((storage/'helper-presentations').glob('*.json'));profile_bytes=profile_path.read_bytes();invoke('saveHelperPresentation',{'helper':'main-helper','revision':saved_profile['revision'],'value':bad},False);assert profile_path.read_bytes()==profile_bytes and helper_store.read_bytes()==immutable_helper
  oversized=dict(saved_profile['value']);oversized['name']='x'*81;invoke('saveHelperPresentation',{'helper':'main-helper','revision':saved_profile['revision'],'value':oversized},False);assert profile_path.read_bytes()==profile_bytes
  profile_path.write_text('{corrupt retained');invoke('globalHelpers',{});assert state()['helpers'][0]['presentation']['unavailable'];r=settings();expect(r.locator('[data-profile-save]')).to_be_disabled();close();assert profile_path.read_text()=='{corrupt retained';profile_path.write_bytes(profile_bytes);invoke('globalHelpers',{})
  enter();s=invariant();project_id=s['projectId'];assert project_id
  page.locator('#add-helper').click();page.locator('[data-recruit="global"]').click();page.locator('#helper-list [data-operation="helper"]').click();close();expect(page.locator('#helper-summary')).to_contain_text('main-helper');assert state()['helperProfile']['personality']=='Collaborative project development assistant';assert 'globalDraft' not in state()['helperProfile']
  # Preserve a live unsubmitted property field and actual DOM identity across both surfaces.
  page.locator('#nav').click();page.locator('.nav-menu button').filter(has_text='개념').first.click();page.locator('[data-id="Example.ButtonGame::Score"]').click();field=page.locator('.window[data-key="schema"] [data-description]');expect(field).to_be_visible();field.fill('IMP1 PROPERTY UNAPPLIED');field.evaluate('el=>globalThis.__imp1Field=el')
  r=info();expect(r.locator('[data-information-helper]')).to_contain_text('main-helper');r.locator('[data-information-description]').fill('Kept only as input');close();expect(field).to_have_value('IMP1 PROPERTY UNAPPLIED');assert field.evaluate('el=>el===globalThis.__imp1Field')
  c=helper_card();c.locator('textarea[aria-label="Helper 대화 입력"]').fill('PROJECT ONLY unsent draft');c.locator('[data-helper-global]').click();expect(c.locator('[aria-label="전역 Helper 대화 입력"]')).to_have_value('GLOBAL second saved draft');c.locator('[data-helper-project]').click();expect(c.locator('textarea[aria-label="Helper 대화 입력"]')).to_have_value('PROJECT ONLY unsent draft');c.locator('.helper-window-settings').click();r=page.locator('[data-helper-settings]');r.locator('#participant-name').fill('Cancelled profile input');r.locator('[data-profile-cancel]').click();r=settings();expect(r.locator('#participant-name')).to_have_value('Cancelled profile input');r.locator('[data-profile-discard]').click();expect(field).to_have_value('IMP1 PROPERTY UNAPPLIED');invariant(project_id)
  # Read/save requests cannot edit a foreign listing or Helper through this project view.
  invoke('projectInformation',{'id':ids[1]},False);invoke('saveHelperPresentation',{'helper':'foreign-helper','revision':'missing','value':{}},False);r=info();close();invariant(project_id)
  # Stale revision/CAS rejects another writer while retaining the visible draft.
  r=settings();r.locator('#participant-name').fill('Retained conflict input');profile_file=next((storage/'helper-presentations').glob('*.json'));saved=json.loads(profile_file.read_text());saved['description']='External display edit';profile_file.write_text(json.dumps(saved));r.locator('[data-profile-save]').click();expect(page.locator('#status')).to_contain_text('입력은 유지');expect(r.locator('#participant-name')).to_have_value('Retained conflict input');assert json.loads(profile_file.read_text())['description']=='External display edit';r.locator('[data-profile-discard]').click();invariant(project_id)
  page.screenshot(path=str(root/'project-inputs.png'),full_page=True)
  page.evaluate('()=>globalThis.confectoryFlushPresentation()');page.locator('.brand').click();expect(page.locator('[data-enter]')).to_have_count(3);enter(1);second_id=invariant()['projectId'];assert second_id!=project_id
  page.locator('#add-helper').click();page.locator('[data-recruit="project"]').click();expect(page.locator('#helper-list')).to_contain_text('project-helper-'+second_id);close()
  c=helper_card();expect(c.locator('textarea[aria-label="Helper 대화 입력"]')).to_be_disabled();c.locator('[data-helper-global]').click();expect(c.locator('[aria-label="전역 Helper 대화 입력"]')).to_have_value('GLOBAL second saved draft');c.locator('[data-close]').click();page.locator('.brand').click();enter();expect(page.locator('.window[data-key="schema"] [data-description]')).to_have_value('IMP1 PROPERTY UNAPPLIED');r=info();expect(r.locator('[data-information-description]')).to_have_value('Kept only as input');close();invariant(project_id);assert all(h['id']!='project-helper-'+second_id for h in state()['helpers']);invoke('saveHelperPresentation',{'helper':'project-helper-'+second_id,'revision':'missing','value':{}},False)
  # New process + fresh browser restores explicit saves, existing project draft only after explicit open.
  start();r=settings();expect(r.locator('#participant-name')).to_have_value('Local Chief');expect(r.locator('#participant-description')).to_have_value('External display edit');close();c=helper_card();expect(c.locator('[aria-label="전역 Helper 대화 입력"]')).to_have_value('GLOBAL second saved draft');c.locator('[data-close]').click();invariant('');enter();expect(page.locator('.window[data-key="schema"] [data-description]')).to_have_value('IMP1 PROPERTY UNAPPLIED');c=helper_card();expect(c.locator('textarea[aria-label="Helper 대화 입력"]')).to_have_value('PROJECT ONLY unsent draft');invariant(project_id)
  assert not set(endpoints)&{'startAI','permission','startInstallation','startLogin','startConnectionCheck','host.create-project'},endpoints
  page.screenshot(path=str(root/'cold-restored.png'),full_page=True);(root/'evidence.json').write_text(json.dumps({'projectIds':[project_id,second_id],'cards':3,'endpoints':endpoints,'errors':errors,'sourceFilesUnchanged':len(before)},indent=2))
 except Exception:
  if page:page.screenshot(path=str(root/'failure.png'),full_page=True);print('status:',page.locator('#status').inner_text(),flush=True)
  print('Evidence:',root,'errors:',errors,flush=True);raise
 finally:stop();browser.close()
print('PASS actual v480 project information and Helper profiles; context/drafts/CAS/cold/no project creation '+str(root))
