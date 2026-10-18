"""Actual Home + normal copied provider + owned HTTP archives. Never installs a real CLI or uses an account."""
import fcntl,hashlib,http.server,io,json,os,pathlib,signal,subprocess,sys,tarfile,tempfile,threading,time,urllib.request,zipfile
from playwright.sync_api import sync_playwright,expect
expect.set_options(timeout=25000)
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());descriptor=pathlib.Path(sys.argv[3]);root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-click-preparation-'));profile=root/'profile';profile.mkdir();managed=root/'managed';storageBase=managed;old=root/'existing';old.mkdir();(old/'keep.txt').write_text('EXISTING INSTALL/ACCOUNT MUST SURVIVE');before=(old/'keep.txt').read_bytes();(root/'control.json').write_text('{}')
binary=(repo/'tests/protocol/codex_preparation_owned.py').read_text().replace('__OWNED_ROOT__',str(root)).encode()
assets={};downloads=[];slow=threading.Event()
class Server(http.server.BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_GET(self):
  downloads.append(self.path);payload=assets.get(self.path,b'');self.send_response(200);self.send_header('Content-Length',str(len(payload)));self.end_headers()
  try:
   if self.path=='/slow':
    self.wfile.write(payload[:16]);self.wfile.flush();slow.set()
    deadline=time.monotonic()+90
    while slow.is_set() and time.monotonic()<deadline:time.sleep(.02)
    self.wfile.write(payload[16:])
   else:self.wfile.write(payload)
  except (BrokenPipeError,ConnectionResetError):pass
http=http.server.ThreadingHTTPServer(('127.0.0.1',0),Server);threading.Thread(target=http.serve_forever,daemon=True).start()
def archive(kind='zip',entries=None):
 b=io.BytesIO();entries=entries or [('codex-owned',binary,'file')]
 if kind=='zip':
  with zipfile.ZipFile(b,'w',zipfile.ZIP_DEFLATED) as z:
   for name,content,typ in entries:
    info=zipfile.ZipInfo(name);info.external_attr=(0o120777 if typ=='symlink' else 0o100700)<<16;z.writestr(info,content)
 else:
  with tarfile.open(fileobj=b,mode='w:gz',format=tarfile.USTAR_FORMAT) as t:
   for name,content,typ in entries:
    info=tarfile.TarInfo(name);info.mode=0o700;info.size=len(content)
    if typ in ['symlink','hardlink']:info.type=tarfile.SYMTYPE if typ=='symlink' else tarfile.LNKTYPE;info.linkname=str(old/'keep.txt');info.size=0;t.addfile(info)
    else:t.addfile(info,io.BytesIO(content))
 return b.getvalue()
def configure(payload=None,kind='zip',name='/good',**extra):
 payload=payload or archive(kind);assets[name]=payload
 spec={'supported':True,'publisher':'OWNED TEST','version':'0.159.0-alpha.3','target':'linux-x64','asset':'owned.zip','url':f'http://127.0.0.1:{http.server_port}{name}','sha256':hashlib.sha256(payload).hexdigest(),'archiveKind':kind,'archiveExecutable':'codex-owned','binaryName':'codex','rootBase':str(storageBase),'maxDownloadBytes':262144,'maxUnpackedBytes':1048576,'maxEntries':16,'downloadTimeoutSeconds':60}
 spec.update(extra);descriptor.write_text(json.dumps(spec));return spec
configure()
env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_ENTRY_STORAGE=str(root/'storage'),CONFECTORY_HOME_STORAGE=str(root/'storage'),HOME=str(profile),PATH=os.pathsep.join([str(pathlib.Path(env['CONFECTORY_DOTNET']).parent),'/usr/bin','/bin']))
for key in ['CODEX_HOME','LOCALAPPDATA','CONFECTORY_CODEX','PACKENGINE_CODEX','CONFECTORY_WEB_PROJECT','NPM_CONFIG_PREFIX','npm_config_prefix']:env.pop(key,None)
log=(root/'host.log').open('w');host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
def boot():
 deadline=time.monotonic()+60
 while time.monotonic()<deadline:
  for line in (root/'host.log').read_text().splitlines():
   if line.startswith('CONFECTORY_WEB_UI '):return line.split(' ',1)[1]
  assert host.poll() is None,(root/'host.log').read_text();time.sleep(.1)
 raise AssertionError('Host did not start')
url=boot();origin,token=url.split('/#')
def send(body):
 request=urllib.request.Request(origin+'/api/request',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':token})
 with urllib.request.urlopen(request,timeout=20) as response:return json.load(response)
def state(endpoint=None,payload=None):
 for _ in range(400):
  view=send({'op':'mount'})
  if view.get('error',{}).get('code')=='busy':time.sleep(.01);continue
  assert view['ok'],view;break
 else:raise AssertionError('Mount remained busy')
 try:
  if endpoint is None:return view['state']
  request='owned-'+str(time.monotonic_ns());envelope={'view':view['view'],'scope':view['scope']};assert send(dict(envelope,op='invoke',endpoint=endpoint,requestId=request,expectedRevision=view['revision'],input=payload or {}))['ok']
  for _ in range(400):
   result=send(dict(envelope,op='update'));assert result['ok'],result
   for row in result.get('results',[]):
    if row['requestId']==request:return row
   time.sleep(.01)
  raise AssertionError('Command remained pending')
 finally:assert send({'op':'dispose','view':view['view']})['ok']
connection={'connection':'Confectory.Agent.Codex::Connection'}
def invoke(endpoint,**args):
 # Admission stale_revision guarantees that the command did not execute.
 # Preserve the same explicit consent token; never replay consumer/source CAS failures.
 for attempt in range(3):
  result=state(endpoint,dict(connection,**args))
  if result.get('error',{}).get('code')!='stale_revision' or attempt==2:return result
def setup():return state()['connectionSetup']
def field(name):return next(row['value'] for row in setup()['schema']['rows'] if row['name']==name)
def wait_job(key,states):
 deadline=time.monotonic()+30
 while time.monotonic()<deadline:
  value=setup().get(key) or {}
  if value.get('state') in states:return value
  time.sleep(.08)
 raise AssertionError((key,states,{k:setup().get(k) for k in ['preparation','login','outcome']}))
def requests():return [json.loads(row) for row in (root/'requests.jsonl').read_text().splitlines()] if (root/'requests.jsonl').exists() else []
def approvals(login=False):return {k:True for k in (['loginProcessApproved','accountInteractionApproved','accountStorageApproved'] if login else ['downloadApproved','storageApproved','versionCheckApproved'])}
def plan_start(login=False):
 result=invoke('prepareLogin' if login else 'prepareInstallation');assert result['ok'],result;value=setup()['login' if login else 'preparation'];assert value['state']=='approval-required',value;started=invoke('startLogin' if login else 'startInstallation',token=value['token'],approvals=approvals(login));assert started['ok'],started;return value
def fresh_ui_plan(selector,login=False):
 key='login' if login else 'preparation';prior=(setup().get(key) or {}).get('token')
 dialog.locator(selector).click();box=dialog.locator('[data-job="'+key+'"]')
 page.wait_for_function("arg=>{const box=document.querySelector('[data-job=\"'+arg.key+'\"]');if(!box||box.dataset.jobState!=='approval-required')return false;const state=JSON.parse(box.dataset.snapshot||'{}');return Boolean(state.token)&&state.token!==arg.prior}",arg={'key':key,'prior':prior})
 expect(page.locator('#add-agent')).to_be_enabled();return box
errors=[];external=[]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu']);page=browser.new_page(viewport={'width':1440,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)));page.route('https://**/*',lambda route:(external.append(route.request.url),route.abort()))
 try:
  page.goto(url);expect(page.locator('.home-grid')).to_be_visible()
  def open_dialog():
   page.locator('#add-agent').click();dialog=page.get_by_role('dialog',name='사용할 AI',exact=True);dialog.get_by_role('button',name='Codex',exact=True).click();expect(dialog.locator('[data-install-prepare]')).to_be_visible();return dialog
  dialog=open_dialog();page.screenshot(path=str(root/'actual-ai-picker.png'));dialog.locator('[data-basic-check]').click();expect(dialog.locator('[data-job="preparation"] [data-job-consent]')).to_have_count(3);assert not downloads and not requests() and not managed.exists();page.screenshot(path=str(root/'actual-preparation-consent.png'))
  stale=setup()['preparation']['token'];invoke('startInstallation',token=stale,approvals={});assert not downloads
  dialog.locator('[data-connection-cancel]').click();expect(dialog).not_to_be_visible();assert not invoke('startInstallation',token=stale,approvals=approvals())['ok'];dialog=open_dialog()
  # Settings changes invalidate the form-bound consent even when changed back later.
  invoke('prepareInstallation',url='http://127.0.0.1:1/untrusted',root=str(old));preview=setup()['preparation'];assert preview['source'].startswith(f'http://127.0.0.1:{http.server_port}/')
  row=next(row for row in setup()['schema']['rows'] if row['name']=='model');invoke('editConnectionSetup',path=row['path'],value='owned-stale',revision=setup()['schema']['revision']);assert not invoke('startInstallation',token=preview['token'],approvals=approvals())['ok'];invoke('editConnectionSetup',path=row['path'],value='',revision=setup()['schema']['revision']);assert not downloads
  # An existing unrecognized root is never adopted or overwritten.
  storageBase.mkdir();(storageBase/'keep.txt').write_bytes(before);managed=pathlib.Path(str(storageBase)+'-separate')
  # Reject corrupt, aliased, escaping, linked and over-budget archives before any file is executable.
  cases=[('digest',archive(),'zip',{'sha256':'0'*64},'preparation_digest_mismatch'),('traversal',archive(entries=[('../escaped',b'X','file')]),'zip',{},'preparation_archive_rejected'),('absolute',archive(entries=[('/escaped',b'X','file')]),'zip',{},'preparation_archive_rejected'),('drive',archive(entries=[('C:/escaped',b'X','file')]),'zip',{},'preparation_archive_rejected'),('backslash',archive(entries=[('a\\b',b'X','file')]),'zip',{},'preparation_archive_rejected'),('alias',archive(entries=[('same',b'a','file'),('SAME',b'b','file')]),'zip',{},'preparation_archive_rejected'),('link',archive(entries=[('codex-owned',b'keep','symlink')]),'zip',{},'preparation_archive_rejected'),('tar-link',archive('tar.gz',[('codex-owned',b'','hardlink')]),'tar.gz',{},'preparation_archive_rejected'),('expanded',archive(entries=[('codex-owned',b'X'*10000,'file')]),'zip',{'maxUnpackedBytes':100},'preparation_archive_rejected')]
  for label,payload,kind,extra,code in cases:
   configure(payload,kind,name='/'+label,**extra);plan_start();value=wait_job('preparation',['failed']);assert value['code']==code,(label,value);assert not list(managed.glob('installations/*/*/.pending-*')) and not (root/'escaped').exists();assert (old/'keep.txt').read_bytes()==before
  assert not requests() and (storageBase/'keep.txt').read_bytes()==before
  configure();lock=(managed/'preparation.lock').open('a+b');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  try:plan_start();assert wait_job('preparation',['failed'])['code']=='preparation_busy'
  finally:fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
  linked=root/'linked-root';linked.symlink_to(old,target_is_directory=True);configure(rootBase=str(linked));assert not invoke('prepareInstallation')['ok'];assert (old/'keep.txt').read_bytes()==before
  configure(name='/slow');slow.clear();plan=plan_start();assert slow.wait(5);before_count=len(downloads);invoke('startInstallation',token=plan['token'],approvals=approvals());assert len(downloads)==before_count
  dialog.locator('[data-job="preparation"] [data-job-cancel]').click();wait_job('preparation',['cancelling','cancelled']);slow.clear();wait_job('preparation',['cancelled']);assert field('executable') in ['', 'codex'] and not list(managed.glob('installations/*/*/.pending-*'))
  # Cancel the owned version-check process, then retry in a fresh unique transaction.
  configure();(root/'version-ready').unlink(missing_ok=True);(root/'control.json').write_text(json.dumps({'holdVersion':True}));plan_start()
  deadline=time.monotonic()+10
  while not (root/'version-ready').exists():assert time.monotonic()<deadline;time.sleep(.02)
  invoke('cancelInstallation');wait_job('preparation',['cancelled']);assert field('executable') in ['', 'codex'];(root/'control.json').write_text('{}')
  # An unvalidated installation cannot become a prepared or logged-in result.
  (root/'control.json').write_text(json.dumps({'version':'0.159.2'}));plan_start();assert wait_job('preparation',['failed'])['code']=='preparation_version_mismatch';assert not requests();(root/'control.json').write_text('{}')
  configure(kind='tar.gz');box=fresh_ui_plan('[data-install-prepare]');expect(box.locator('[data-job-consent]')).to_have_count(3)
  for checkbox in box.locator('[data-job-consent]').all():checkbox.check()
  box.locator('[data-job-start]').click();expect(box).to_have_attribute('data-job-state','prepared');prepared=pathlib.Path(field('executable'));assert prepared.exists() and prepared.parent.name.startswith('install-');assert not field('managedHome') and not requests();assert not list(managed.glob('installations/*/*/.pending-*'))
  # Login always uses a fresh home. Cancellation removes it, code and consent; saved installations remain.
  box.locator('[data-job-continue]').click();login=dialog.locator('[data-job="login"]');expect(login.locator('[data-job-consent]')).to_have_count(3)
  hold=descriptor.parent/'owned-hold-account';ready=descriptor.parent/'owned-account-ready';hold.write_text('hold');launches=(root/'process-starts').read_text() if (root/'process-starts').exists() else ''
  for checkbox in login.locator('[data-job-consent]').all():checkbox.check()
  login.locator('[data-job-start]').click();deadline=time.monotonic()+10
  while not ready.exists():assert time.monotonic()<deadline;time.sleep(.02)
  login.locator('[data-job-cancel]').click();wait_job('login',['cancelling','cancelled']);hold.unlink();wait_job('login',['cancelled']);assert ((root/'process-starts').read_text() if (root/'process-starts').exists() else '')==launches;assert not list(managed.glob('accounts/account-*'))
  login=fresh_ui_plan('[data-login-prepare]',True);expect(login.locator('[data-job-consent]')).to_have_count(3)
  for checkbox in login.locator('[data-job-consent]').all():checkbox.check()
  login.locator('[data-job-start]').click();expect(login).to_have_attribute('data-job-state','waiting-user');expect(login.locator('[data-login-code]')).to_have_text('TEST-4240');expect(login.locator('[data-login-page]')).to_have_attribute('href','https://auth.openai.com/codex/device');assert not field('managedHome');assert not any(r['method'] in ['thread/start','turn/start','model/list'] for r in requests())
  login.locator('[data-job-cancel]').click();expect(login).to_have_attribute('data-job-state','cancelled');expect(login.locator('[data-login-code]')).to_have_count(0);assert not list(managed.glob('accounts/account-*')) and prepared.exists()
  # Gate rejects 0.159.2 before requesting any login or account operation.
  (root/'control.json').write_text(json.dumps({'version':'0.159.2'}));count=len(requests());plan_start(True);assert wait_job('login',['failed'])['code']=='login_version_unverified';assert [r['method'] for r in requests()[count:]]==['initialize'];(root/'control.json').write_text('{}')
  # A redirected login page is never exposed or opened.
  (root/'control.json').write_text(json.dumps({'invalidUrl':True}));plan_start(True);assert wait_job('login',['failed'])['code']=='login_service_unavailable';assert not list(managed.glob('accounts/account-*'));(root/'control.json').write_text('{}')
  plan_start(True);wait_job('login',['waiting-user']);dialog.locator('[data-connection-cancel]').click();expect(dialog).not_to_be_visible();(root/'complete-login').write_text('late');time.sleep(.3);assert not list(managed.glob('accounts/account-*'));(root/'complete-login').unlink();dialog=open_dialog();assert not field('managedHome') and field('executable')==str(prepared)
  login=fresh_ui_plan('[data-login-prepare]',True);expect(login.locator('[data-job-consent]')).to_have_count(3)
  for checkbox in login.locator('[data-job-consent]').all():checkbox.check()
  login.locator('[data-job-start]').click();expect(login).to_have_attribute('data-job-state','waiting-user');(root/'complete-login').write_text('complete');expect(login).to_have_attribute('data-job-state','login-complete');account=pathlib.Path(field('managedHome'));assert (account/'.owned-signed-in').exists() and (account/'.confectory-account-ready').exists();assert account!=prepared.parent and field('credentialReference')=='codex:managed'
  login.locator('[data-job-continue]').click();expect(dialog.locator('[data-check-consent]')).to_have_count(4);assert all(not checkbox.is_checked() for checkbox in dialog.locator('[data-check-consent]').all())
  for checkbox in dialog.locator('[data-check-consent]').all():checkbox.check()
  dialog.locator('[data-connection-check-start]').click();expect(dialog.locator('[data-connection-result]')).to_have_attribute('data-connection-outcome','models-found');assert setup()['outcome'].get('authenticated') is False;assert not any(r['method'] in ['thread/start','turn/start'] for r in requests())
  dialog.locator('[data-catalogue-model]').select_option('owned-protocol-fixture');dialog.locator('[data-catalogue-select]').click();expect(dialog.locator('[data-check-consent]')).to_have_count(4);assert all(not box.is_checked() for box in dialog.locator('[data-check-consent]').all());page.screenshot(path=str(root/'actual-home-prepared.png'));assert not errors and not external,(errors,external);assert (old/'keep.txt').read_bytes()==before
  (root/'evidence.json').write_text(json.dumps({'normalHomeEntry':True,'ownedDownloadAndDigestAndSafeExtraction':True,'archiveRejections':len(cases),'cancelDownloadAndVersionAndLoginAndClose':True,'cancelBeforeProcessZeroLaunch':True,'unownedRootAndLinksPreserved':True,'crossProcessPreparationLock':True,'separateManagedInstallAndAccount':True,'staleConsentAndDuplicateStart':True,'versionGateUnchanged':True,'modelPreflightAndRequestApprovalRemainSeparate':True,'realInstallationAccountTokenOrModelCalls':False},indent=2));print('PASS actual Home click preparation and device login; OWNED fixtures only',root,flush=True)
 except Exception:
  print('Evidence',root,flush=True);page.screenshot(path=str(root/'failure.png'));print('State',json.dumps({key:(setup() or {}).get(key) for key in ['preparation','login','outcome']},ensure_ascii=False),flush=True);raise
 finally:
  browser.close();slow.clear();http.shutdown()
  if host.poll() is None:os.killpg(host.pid,signal.SIGTERM)
  host.wait(timeout=15);log.close()
