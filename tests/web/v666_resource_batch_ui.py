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
def many(names,raw=None):
 b.locator('[data-resource-files]').set_input_files([dict(name=name,mimeType='application/octet-stream',buffer=(raw if raw is not None else ('generated '+name+'\r\n').encode()))for name in names])
def pending():expect(b.locator('[data-resource-pending=retry]')).to_be_enabled()
def done(count):expect(b.locator('[data-resource-pending]')).to_have_count(0);wait_count(count);assert len(api('load')['items'])==count
try:
 f.start(0)
 with sync_playwright()as p:
  expect.set_options(timeout=60000);f.browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.idle();f.page.locator('#chat-input').fill('그룹 보관과 별개인 입력');open_browser();assert b.locator('[data-resource-files]').get_attribute('multiple')is not None
  names=['한글 <그룹>.bin','same name.bin','same name.bin'];many(names);done(3);saved=api('load');ids=[row['id']for row in saved['items']];assert len(set(ids))==3 and [row['name']for row in saved['items']]==names
  for row in saved['items']:assert base64.urlsafe_b64decode(api('read',id=row['id'],hash=row['hash'])['data'])==('generated '+row['name']+'\r\n').encode()
  assert sum(1 for row in b.locator('[aria-selected=true][data-resource-id]').all())==3;original();f.checked('one actual multi-file picker selection atomically stores three distinct native IDs including duplicate names, exact CRLF bytes and grouped selection')
  if mode=='normal':
   # All files are read before the single import-many request; an invalid second file preserves all originals.
   before=store.read_bytes();many(['valid.bin',' bad.bin ']);pending();assert store.read_bytes()==before;expect(b.locator('[data-resource-recovery]')).to_contain_text('valid.bin');expect(b.locator('[data-resource-recovery]')).to_contain_text('bad.bin');b.locator('[data-resource-pending=cancel]').click();done(3);original();f.checked('invalid second member rejects the complete real native mutation and preserves both volatile selections until explicit cancel')
   perms=store.stat().st_mode;before=store.read_bytes()
   try:
    store.chmod(0o444);many(['permission one.bin','permission two.bin']);pending();assert store.read_bytes()==before
   finally:store.chmod(perms)
   b.locator('[data-resource-pending=retry]').click();done(5);original();f.checked('real write refusal leaves no partial group; exact retry after restoring fixture permissions appends both files once')
   # Hold a real successful native invoke result and report response loss to the client.
   f.page.evaluate("""()=>{const base=fetch;let wanted=null,armed=true;globalThis.__batchHeld=false;fetch=async(...args)=>{let req;try{req=JSON.parse(args[1]?.body||'null')}catch{}if(armed&&req?.op==='invoke'&&req.endpoint==='projectResources'&&req.input?.action==='import-many')wanted=req.requestId;const response=await base(...args);if(!wanted||!armed||req?.op!=='update')return response;const body=await response.clone().json(),row=body.results?.find(r=>r.requestId===wanted);if(!row?.ok)return response;armed=false;globalThis.__batchHeld=true;return new Promise(resolve=>{globalThis.__releaseBatch=()=>{delete row.result;row.ok=false;row.error={code:'owned_lost_batch_reply'};fetch=base;resolve(new Response(JSON.stringify(body),{status:200,headers:{'Content-Type':'application/json'}}));};});};}""")
   many(['lost one.bin','lost two.bin']);f.page.wait_for_function('()=>__batchHeld');assert len(api('load')['items'])==7;b.locator('[data-browser-control=object-query]').fill('응답 뒤 새 검색');f.page.evaluate('()=>__releaseBatch()');pending();b.locator('[data-resource-pending=retry]').click();expect(b.locator('[data-resource-pending]')).to_have_count(0);assert len(api('load')['items'])==7;expect(b.locator('[data-browser-control=object-query]')).to_have_value('응답 뒤 새 검색');search('');original();f.checked('lost actual group success reply retains the exact per-item commands and newer query; explicit replay confirms all seven copies without duplicate writes')
   basis=api('load');api('import',revision=basis['revision'],command=uuid.uuid4().hex,item=item('peer.bin',b'peer owned bytes'));before=store.read_bytes();many(['stale one.bin','stale two.bin']);pending();assert store.read_bytes()==before;b.locator('[data-resource-reload]').click();f.idle();b.locator('[data-resource-pending=retry]').click();pending();assert store.read_bytes()==before;b.locator('[data-resource-pending=cancel]').click();many(['stale one.bin','stale two.bin']);done(10);original();f.checked('stale multi-import rejects before and after list refresh; only explicit cancellation/reselection creates a new observed group')
   before=store.read_bytes();many(['too large one.bin','too large two.bin'],bytes([251])*524289);expect(b.locator('[data-new]')).to_be_enabled();f.idle();assert store.read_bytes()==before;expect(b.locator('[data-resource-pending]')).to_have_count(0);many(['half one.bin','half two.bin'],bytes([251])*524288);done(12);original();f.checked('over-budget selection creates no pending mutation; exact aggregate 1MiB crosses the actual bounded transport atomically')
   # Deleting one confirmed member must make a lost batch replay fail instead of resurrecting it.
   batch_input=json.loads(json.dumps(next(row['invoke']['input']for row in reversed(f.traffic)if row.get('invoke',{}).get('endpoint')=='projectResources'and row['invoke']['input'].get('action')=='import-many')));batch_input.pop('action');batch_input.pop('project');selected=api('load');last=selected['items'][-1];layout=f.invoke('projectResourceLayout',dict(action='load',project=f.state()['projectId']))['result']['result'];f.invoke('projectResourceLayout',dict(action='delete-file',project=f.state()['projectId'],revision=layout['revision'],command=uuid.uuid4().hex,id=last['id'],hash=last['hash']));assert len(api('load')['items'])==11;before=store.read_bytes();api('import-many',False,**batch_input);assert store.read_bytes()==before;original();f.checked('lost batch replay rejects a deleted member instead of resurrecting it; ordinary confirmed resource deletion consumes the same per-item import receipt without altering unrelated grouped copies')
  elif mode=='lifecycle':
   listing=f.state()['listingId'];f.page.evaluate("""()=>{const original=File.prototype.arrayBuffer;globalThis.__batchReadHeld=false;File.prototype.arrayBuffer=async function(){const bytes=await original.call(this);if(this.name!=='late two.bin')return bytes;globalThis.__batchReadHeld=true;return new Promise(resolve=>{globalThis.__releaseBatchRead=()=>{File.prototype.arrayBuffer=original;resolve(bytes);};});};}""")
   many(['late one.bin','late two.bin']);f.page.wait_for_function('()=>__batchReadHeld');assert len(api('load')['items'])==3;f.pending();f.page.locator('#title').click();f.page.get_by_role('button',name='프로젝트 나가기',exact=True).click();expect(f.page.locator('.home-grid')).to_be_visible();f.page.evaluate('()=>__releaseBatchRead()');f.page.locator('[data-enter="'+listing+'"]').click();f.idle();b=f.page.locator('.window[data-key^="browser:project:"]').last;pending();assert len(api('load')['items'])==3;expect(b.locator('[data-resource-recovery]')).to_contain_text('late one.bin');expect(b.locator('[data-resource-recovery]')).to_contain_text('late two.bin');b.locator('[data-resource-pending=retry]').click();done(5);original();f.checked('Home during a later File read cannot partially upload or auto-replay; both files remain volatile until explicit same-owner retry')
   perms=store.stat().st_mode
   try:store.chmod(0o444);many(['restart one.bin','restart two.bin']);pending();assert len(api('load')['items'])==5;f.pending();assert 'restart one.bin'not in json.dumps(f.state()['presentation'])
   finally:store.chmod(perms)
   restarted(1);expect(b.locator('[data-resource-pending]')).to_have_count(0);assert len(api('load')['items'])==5;original();f.checked('cold engine restores confirmed copies only; unfinished multi-file bytes/commands never enter private layout or auto-upload')
   other=f.case/'other owned project';shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory','.build'));restarted(2,other);assert api('load')['items']==[];many(['B one.bin','B two.bin']);done(2);restarted(3,f.project);assert len(api('load')['items'])==5 and [row['id']for row in api('load')['items'][:3]]==ids;original();f.checked('another actual project with the same namespace never inherits selection or copies; each owned group survives project roundtrip independently')
  else:raise AssertionError(mode)
  expect(f.page.locator('#chat-input')).to_have_value('그룹 보관과 별개인 입력');original();f.pending();f.page.screenshot(path=str(f.case/('resource-batch-'+mode+'.png')));f.browser.close()
except Exception as error:
 try:f.page.screenshot(path=str(f.case/'failure.png'))
 except Exception:pass
 (f.case/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:
 f.stop();(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2))
print('RESOURCE_BATCH_FIXTURE',f.case,flush=True)
