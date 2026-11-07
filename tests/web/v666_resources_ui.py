"""Real native project resource copies through authored browser; generated File inputs only."""
import sys,json,pathlib,hashlib,base64,uuid,shutil,traceback
from playwright.sync_api import sync_playwright,expect
import v536_wide_mixed as f
mode=sys.argv[3];store=f.project/'.confectory/resources.v1.json';b=None
def api(action,success=True,**args):return f.invoke('projectResources',dict(action=action,project=f.state()['projectId'],**args),success)['result'].get('result')
def rows():return b.locator('[data-resource-id]')
def original():
 for relative,raw in f.original.items():assert(f.project/relative).read_bytes()==raw,relative
 assert not f.errors and not f.external,(f.errors,f.external)
def open_browser():
 global b
 f.page.locator('#workspace').click(button='right',position=dict(x=700,y=260));f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]').last;b.locator('[data-tab=resource]').click();expect(b.locator('[data-resource-files]')).to_have_count(1);expect(b.locator('[data-new]')).to_be_enabled(timeout=60000)
def pick(name,content=b'owned resource\r\n',type='text/plain'):
 b.locator('[data-resource-files]').set_input_files(dict(name=name,mimeType=type,buffer=content))
def search(value):
 b.locator('[data-browser-control=object-query]').fill(value);b.locator('[data-browser-control=object-search]').click()
def wait_count(count):
 f.page.wait_for_function('(count)=>document.querySelectorAll("[data-resource-id]").length===count',arg=count,timeout=60000);f.idle()
def restarted(index,project=None):
 global b
 f.pending();f.page.close();f.stop()
 if project:f.env['CONFECTORY_WEB_PROJECT']=str(project/'project.cproj')
 f.start(index);f.page=f.setup();f.idle();b=f.page.locator('.window[data-key^="browser:project:"]').last
 if not b.count():open_browser()
 else:
  expect(b.locator('[data-resource-files]')).to_have_count(1);expect(b.locator('[data-new]')).to_be_enabled(timeout=60000)
def item(name,raw):return dict(id=uuid.uuid4().hex,name=name,type='text/plain',size=len(raw),hash=hashlib.sha256(raw).hexdigest(),modifiedAt=0,data=base64.urlsafe_b64encode(raw).decode())
try:
 f.start(0)
 with sync_playwright()as p:
  expect.set_options(timeout=60000);f.browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']);f.page=f.setup();f.idle();f.page.locator('#chat-input').fill('자료 보관 중에도 보존할 입력');open_browser();expect(rows()).to_have_count(0);assert not store.exists();original();f.checked('authored resource tab opens a real empty owned project without creating an asset store, changing source selection or granting execution')
  raw='생성한 검사용 사본 🧪\r\n<script>externalMustNeverRun()</script>\n'.encode();pick('한글 자료 <안전>.txt',raw);wait_count(1);saved=api('load');first=saved['items'][0];assert first['name']=='한글 자료 <안전>.txt';read=api('read',id=first['id'],hash=first['hash']);assert base64.urlsafe_b64decode(read['data'])==raw;expect(f.page.locator('#chat-input')).to_have_value('자료 보관 중에도 보존할 입력');original();f.checked('explicit generated File input creates one exact native copy with stable ID and original CRLF/UTF8 bytes; no code, HTML or provider execution')
  search('한글');expect(rows()).to_have_count(1)
  for density in ['0','100','40']:b.locator('[data-density="'+density+'"]').click();expect(rows()).to_have_count(1)
  rows().first.focus();rows().first.press('Enter');expect(rows().first).to_have_attribute('aria-selected','true');f.page.screenshot(path=str(f.case/'resource-browser.png'));f.checked('original search, Compact/Data/Preview density and keyboard selection use confirmed asset metadata; rich content editors are not fabricated')
  if mode=='normal':
   identity=f.project/'.confectory/project-identity.json';identity_bytes=identity.read_bytes();owner_bytes=store.read_bytes()
   try:
    identity.unlink();api('load',False);assert not identity.exists(),'resource read recreated a missing project identity';assert store.read_bytes()==owner_bytes
    changed=json.loads(identity_bytes);changed['namespace']='Other.Namespace';identity.write_text(json.dumps(changed));api('load',False);assert json.loads(identity.read_text())['namespace']=='Other.Namespace';assert store.read_bytes()==owner_bytes
   finally:identity.write_bytes(identity_bytes)
   original();f.checked('missing or namespace-changed identity is rejected without lazy creation/rebind or resource/source repair writes; only the fixture restores its exact original record')
   # Hold one actual successful native reply, then report a client-side loss.
   f.page.evaluate("""()=>{const base=fetch;globalThis.__resourceReplyHeld=false;let wanted=null,armed=true;fetch=async(...args)=>{let request;try{request=JSON.parse(args[1]?.body||'null')}catch{}if(armed&&request?.op==='invoke'&&request.endpoint==='projectResources'&&request.input?.action==='import')wanted=request.requestId;const response=await base(...args);if(!wanted||!armed||request?.op!=='update')return response;let body;try{body=await response.clone().json()}catch{return response}const row=body.results?.find(r=>r.requestId===wanted);if(!row?.ok)return response;armed=false;globalThis.__resourceActualReply=structuredClone(row);globalThis.__resourceReplyHeld=true;return new Promise(resolve=>{globalThis.__releaseResourceReply=()=>{delete row.result;row.ok=false;row.error={code:'owned_test_lost_reply'};resolve(new Response(JSON.stringify(body),{status:200,headers:{'Content-Type':'application/json'}}));};});};}""")
   pick('retry exact.txt',b'second owned copy');f.page.wait_for_function('()=>__resourceReplyHeld',timeout=60000);assert len(api('load')['items'])==2;b.locator('[data-browser-control=object-query]').fill('보관 응답 뒤 새 검색어');f.page.evaluate('()=>__releaseResourceReply()');expect(b.locator('[data-resource-pending=retry]')).to_be_enabled();expect(b.locator('[data-browser-control=object-query]')).to_have_value('보관 응답 뒤 새 검색어');b.locator('[data-resource-pending=retry]').click();expect(b.locator('[data-resource-pending=retry]')).to_have_count(0);assert len(api('load')['items'])==2;expect(b.locator('[data-browser-control=object-query]')).to_have_value('보관 응답 뒤 새 검색어');original();f.checked('lost actual success reply preserves newer query/File retry input; exact command replay confirms two resources without duplicate append or implicit rebase')
   # Actual read-only store failure; preserve pending bytes and retry unchanged.
   prior=store.read_bytes();permissions=store.stat().st_mode
   try:
    store.chmod(0o444);pick('실패 입력 유지.txt',b'failed input retained');expect(b.locator('[data-resource-pending=retry]')).to_be_enabled();assert store.read_bytes()==prior;expect(b.locator('[data-resource-recovery]')).to_contain_text('실패 입력 유지.txt');expect(f.page.locator('#chat-input')).to_have_value('자료 보관 중에도 보존할 입력')
   finally:store.chmod(permissions)
   b.locator('[data-resource-pending=retry]').click();expect(b.locator('[data-resource-pending=retry]')).to_have_count(0);assert len(api('load')['items'])==3;original();f.checked('real destination write refusal preserves exact prior store and volatile chosen bytes; restoring only fixture permissions allows explicit same-command retry')
   # Another actual append races the displayed list; never rebase old intent.
   basis=api('load');api('import',revision=basis['revision'],command=uuid.uuid4().hex,item=item('別の確認済み資料.txt',b'other authorized append'));pick('conflict pending.txt',b'do not silently rebase');expect(b.locator('[data-resource-pending=retry]')).to_be_enabled();assert len(api('load')['items'])==4;b.locator('[data-resource-reload]').click();f.idle();expect(b.locator('[data-resource-recovery]')).to_contain_text('conflict pending.txt');b.locator('[data-resource-pending=retry]').click();expect(b.locator('[data-resource-pending=retry]')).to_be_enabled();assert len(api('load')['items'])==4
   b.locator('[data-resource-pending=cancel]').click();expect(b.locator('[data-resource-pending]')).to_have_count(0);pick('conflict pending.txt',b'do not silently rebase');expect(b.locator('[data-new]')).to_be_enabled();f.idle();assert len(api('load')['items'])==5;original();f.checked('stale store CAS refuses the old append through refresh/retry; only explicit local cancellation and re-selection creates a new authorized command, retaining all prior identities')
   search('한글');expect(rows()).to_have_count(1);rows().first.evaluate('el=>globalThis.__retiredResourceRow=el.onclick');search('no such resource');f.page.evaluate('()=>__retiredResourceRow()');expect(rows()).to_have_count(0);expect(b.locator('[data-browser-control=object-query]')).to_have_value('no such resource');original();f.checked('retained row callbacks cannot select a filtered-away asset or replace newer query input')
   search('');large=bytes([251])*1048576;pick('maximum binary.bin',large,'application/octet-stream');wait_count(6);maximum=next(row for row in api('load')['items']if row['name']=='maximum binary.bin');read=api('read',id=maximum['id'],hash=maximum['hash']);assert base64.urlsafe_b64decode(read['data'])==large;original();f.checked('actual full-size generated binary File crosses the real native invoke/read transport and restores all 1MiB without text conversion, execution or source changes')
  elif mode=='lifecycle':
   listing=f.state()['listingId'];f.page.evaluate("""()=>{globalThis.__retiredResourceTab=document.querySelector('[data-tab=concept]').onclick;globalThis.__retiredResourceDensity=document.querySelector('[data-density=\"100\"]').onclick;const original=File.prototype.arrayBuffer;File.prototype.arrayBuffer=async function(){const bytes=await original.call(this);if(this.name!=='late private file.txt')return bytes;globalThis.__lateResourceFileHeld=true;return new Promise(resolve=>{globalThis.__releaseLateResourceFile=()=>{File.prototype.arrayBuffer=original;resolve(bytes);};});};}""")
   pick('late private file.txt',b'volatile selected bytes never replay');f.page.wait_for_function('()=>__lateResourceFileHeld');f.pending();f.page.locator('#title').click();f.page.get_by_role('button',name='프로젝트 나가기',exact=True).click();expect(f.page.locator('.home-grid')).to_be_visible();f.page.evaluate('()=>__releaseLateResourceFile()');f.page.locator('[data-enter="'+listing+'"]').click();f.idle();b=f.page.locator('.window[data-key^="browser:project:"]').last;expect(b.locator('[data-resource-files]')).to_have_count(1);expect(b.locator('[data-resource-pending=cancel]')).to_be_enabled();f.page.evaluate('()=>{__retiredResourceTab();__retiredResourceDensity();}');expect(b.locator('[data-tab=resource]')).to_have_class('selected');expect(b.locator('[data-density="40"]')).to_have_attribute('aria-pressed','true');assert len(api('load')['items'])==1;b.locator('[data-resource-pending=cancel]').click();expect(b.locator('[data-resource-pending]')).to_have_count(0);original();f.checked('retired File read and callback cannot upload or change the current surface after Home and same-project return; volatile input remains explicit until local cancellation')
   # Only private metadata is checkpointed; source bytes never enter presentation.
   search('한글');f.pending();presentation=json.dumps(f.state()['presentation'],ensure_ascii=False);assert base64.urlsafe_b64encode(raw).decode()not in presentation;restarted(1);expect(rows()).to_have_count(1);assert api('load')['items'][0]['id']==first['id'];expect(rows().first).to_have_attribute('aria-selected','true');assert base64.urlsafe_b64decode(api('read',id=first['id'],hash=first['hash'])['data'])==raw;original();f.checked('actual cold engine restores original resource IDs/bytes and private browser query/selection; presentation contains no file payload and no import is replayed')
   other=f.case/'other same-ID namespace';shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory','.build'));old_project=f.state()['projectId'];restarted(2,other);assert api('load')['items']==[];expect(rows()).to_have_count(0);f.invoke('projectResources',dict(action='load',project=old_project),False);assert json.loads(store.read_text())['items'][0]['id']==first['id'];original();f.checked('another actual project with identical namespace/source IDs cannot adopt A resources or use its ProjectContext capability')
   pick('B owned.txt',b'B isolated bytes');wait_count(1);assert api('load')['items'][0]['name']=='B owned.txt';restarted(3,f.project);expect(rows()).to_have_count(1);assert api('load')['items'][0]['id']==first['id'];expect(b).not_to_contain_text('B owned.txt');original();f.checked('project round trip restores each native asset store independently without opening foreign files or changing prior sources')
  else:raise AssertionError(mode)
  f.pending();original();f.page.screenshot(path=str(f.case/('resource-'+mode+'.png')));f.browser.close()
except Exception as e:
 try:f.page.screenshot(path=str(f.case/'failure.png'));(f.case/'failure.html').write_text(f.page.content())
 except Exception:pass
 (f.case/'failure.json').write_text(json.dumps(dict(error=repr(e),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:
 f.stop();(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2))
print('RESOURCE_UI_FIXTURE',f.case,flush=True)
