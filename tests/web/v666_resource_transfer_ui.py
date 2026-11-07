"""Real multi-part File selection and one atomic native commit; generated inputs only."""
import sys,json,pathlib,hashlib,base64,uuid,traceback,shutil
from playwright.sync_api import sync_playwright,expect
import v536_wide_mixed as f
mode=sys.argv[3];store=f.project/'.confectory/resources.v1.json';layout_path=f.project/'.confectory/resource-layout.v1.json';b=None

def api(action='load',**kw):return f.invoke('projectResourceLayout',dict(action=action,project=f.state()['projectId'],**kw))['result']['result']
def files():return[x for x in api()['items']if x['kind']!='folder']
def original():
 for k,v in f.original.items():assert(f.project/k).read_bytes()==v,k
 assert not f.errors and not f.external,(f.errors,f.external)
def browser():
 global b
 f.page.locator('#workspace').click(button='right',position=dict(x=700,y=260));f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]').last;b.locator('[data-tab=resource]').click();expect(b.locator('[data-new]')).to_be_enabled()
def payloads(prefix,size=600000,count=2):return[dict(name=prefix+' '+str(n)+' 🧪.bin',mimeType='application/octet-stream',buffer=bytes([151+n])*size)for n in range(count)]
def choose(prefix,size=600000,count=2):
 f.page.evaluate('()=>document.activeElement?.blur()');f.pending();f.idle();b.locator('[data-new]').click()
 with f.page.expect_file_chooser()as event:f.page.locator('.context-menu').get_by_role('button',name='자료 추가',exact=True).click()
 event.value.set_files(payloads(prefix,size,count))
def done(count):expect(b.locator('[data-resource-pending]')).to_have_count(0);expect(b.locator('[data-new]')).to_be_enabled();f.idle();assert len(files())==count

def pending():expect(b.locator('[data-resource-pending=retry]')).to_be_enabled()
def upload_count():return sum(r.get('invoke',{}).get('input',{}).get('action')=='upload-chunk'for r in f.traffic)
def arm(action,lose=True):
 f.page.evaluate("""({action,lose})=>{const base=fetch;let wanted=null,armed=true;globalThis.__transferHeld=false;fetch=async(...args)=>{let req;try{req=JSON.parse(args[1]?.body||'null')}catch{}if(armed&&req?.op==='invoke'&&req.endpoint==='projectResources'&&req.input?.action===action)wanted=req.requestId;const response=await base(...args);if(!armed||!wanted||req?.op!=='update')return response;let body;try{body=await response.clone().json()}catch{return response}const row=body.results?.find(r=>r.requestId===wanted);if(!row?.ok)return response;armed=false;globalThis.__transferHeld=true;return new Promise(resolve=>{globalThis.__releaseTransfer=()=>{fetch=base;if(lose){row.ok=false;delete row.result;row.error={code:'owned_lost_transfer_reply'};}resolve(new Response(JSON.stringify(body),{status:200,headers:{'Content-Type':'application/json'}}));};});};}""",dict(action=action,lose=lose))
def clear():
 # Remove only this fixture's confirmed generated copies through authored UI.
 for parent in dict.fromkeys(x['parent']for x in files()):
  b.locator('[data-resource-tree-id="'+(parent or '')+'"]').click();f.idle();ids=[x['id']for x in files()if x['parent']==parent]
  for index,id in enumerate(ids):b.locator('[data-resource-id="'+id+'"]').click(modifiers=['Control']if index else[])
  b.locator('[data-resource-id="'+ids[0]+'"]').click(button='right');f.page.locator('.context-menu').get_by_role('button',name=str(len(ids))+'개 항목 삭제'if len(ids)>1 else'삭제',exact=True).click();f.page.get_by_role('dialog',name='자료 삭제',exact=True).locator('[data-remove]').click();f.idle()
 assert not files();original()
def folder():
 b.locator('[data-new]').click();f.page.locator('.context-menu').get_by_role('button',name='새 카테고리',exact=True).click();form=f.page.locator('.resource-name-form');form.locator('[name=name]').fill('큰 선택 목적지');form.get_by_role('button',name='확인',exact=True).click();f.idle();id=next(x['id']for x in api()['items']if x['kind']=='folder');b.locator('[data-resource-id="'+id+'"]').dblclick();return id

def restart(index,project=None,flush=True):
 global b
 if flush:f.pending()
 f.page.close();f.stop()
 if project:f.env['CONFECTORY_WEB_PROJECT']=str(project/'project.cproj')
 f.start(index);f.page=f.setup();f.idle();b=f.page.locator('.window[data-key^="browser:project:"]').last
 if not b.count():browser()
 else:expect(b.locator('[data-resource-status]')).to_be_visible();f.idle()
def hashes(prefix,size=600000,count=2):
 rows=[x for x in files()if x['name'].startswith(prefix)]
 assert len(rows)==count
 for n in range(count):
  row=next(x for x in rows if x['name']==prefix+' '+str(n)+' 🧪.bin');raw=bytes([151+n])*size;assert row['hash']==hashlib.sha256(raw).hexdigest();read=api('read',id=row['id'],hash=row['hash']);assert base64.urlsafe_b64decode(read['data'])==raw
try:
 f.start(0)
 with sync_playwright()as p:
  expect.set_options(timeout=60000);f.browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.idle();browser();f.page.locator('#chat-input').fill('분할 보관과 별개인 입력');a=folder();choose('first');done(2);hashes('first');assert all(x['parent']==a for x in files());assert any(r.get('invoke',{}).get('input',{}).get('target')=='layout-import-files'for r in f.traffic);original();f.checked('actual File selection above 1MiB reaches bounded native chunks and one existing folder/file atomic commit; UTF-8 names, IDs, hashes, bytes and explicit destination are exact')
  if mode=='normal':
   before=store.read_bytes();topology=layout_path.read_bytes();permission=layout_path.stat().st_mode
   try:layout_path.chmod(0o444);choose('write refusal');pending();assert store.read_bytes()==before and layout_path.read_bytes()==topology
   finally:layout_path.chmod(permission)
   sent=upload_count();b.locator('[data-resource-pending=retry]').click();done(4);assert upload_count()==sent;hashes('write refusal');original();f.checked('actual placement write refusal rolls back the complete large group; exact retry reuses the staged bytes and original final CAS without another upload');clear();b.locator('[data-resource-tree-id="'+a+'"]').click()
   before=store.read_bytes();arm('upload-chunk');choose('lost chunk');f.page.wait_for_function('()=>__transferHeld');assert store.read_bytes()==before;f.page.evaluate('()=>__releaseTransfer()');pending();b.locator('[data-resource-pending=retry]').click();done(2);hashes('lost chunk');original();f.checked('lost successful chunk reply resumes from the acknowledged native offset; no partial files, duplicate bytes or duplicate IDs are published');clear();b.locator('[data-resource-tree-id="'+a+'"]').click()
   arm('upload-commit');choose('lost commit');f.page.wait_for_function('()=>__transferHeld');assert len(files())==2;b.locator('[data-browser-control=object-query]').fill('더 늦은 검색 입력');f.page.evaluate('()=>__releaseTransfer()');pending();sent=upload_count();b.locator('[data-resource-pending=retry]').click();done(2);assert upload_count()==sent;expect(b.locator('[data-browser-control=object-query]')).to_have_value('더 늦은 검색 입력');hashes('lost commit');original();f.checked('lost committed reply revalidates original durable receipts without re-upload/duplication and preserves newer search input');clear();b.locator('[data-resource-tree-id="'+a+'"]').click()
   arm('upload-commit');choose('cancel committed');f.page.wait_for_function('()=>__transferHeld');f.page.evaluate('()=>__releaseTransfer()');pending();saved=store.read_bytes();b.locator('[data-resource-pending=cancel]').click();done(2);assert store.read_bytes()==saved;original();f.checked('input cancellation after a lost committed reply retires volatile transfer bytes only and never deletes confirmed copies');clear();b.locator('[data-resource-tree-id="'+a+'"]').click()
   arm('upload-chunk',False);choose('stale');f.page.wait_for_function('()=>__transferHeld');v=f.invoke('projectResources',dict(action='load',project=f.state()['projectId']))['result']['result'];raw=b'peer';f.invoke('projectResources',dict(action='import',project=f.state()['projectId'],revision=v['revision'],command=uuid.uuid4().hex,item=dict(id=uuid.uuid4().hex,name='peer.bin',type='application/octet-stream',size=len(raw),hash=hashlib.sha256(raw).hexdigest(),modifiedAt=0,data=base64.urlsafe_b64encode(raw).decode())));peer=store.read_bytes();f.page.evaluate('()=>__releaseTransfer()');pending();assert store.read_bytes()==peer;b.locator('[data-resource-pending=retry]').click();pending();assert store.read_bytes()==peer;b.locator('[data-resource-reload]').click();f.idle();b.locator('[data-resource-pending=cancel]').click();done(1);original();f.checked('a real peer after staging survives repeated final-CAS rejection; refresh/cancel never rebases or partly applies the selected group');clear();b.locator('[data-resource-tree-id="'+a+'"]').click()
   arm('upload-chunk',False);choose('close');f.page.wait_for_function('()=>__transferHeld');b.locator('[data-close]').first.evaluate('e=>e.click()');f.page.evaluate('()=>__releaseTransfer()');f.idle();browser();pending();assert not files();b.locator('[data-resource-pending=cancel]').click();done(0);choose('after cancel');done(2);hashes('after cancel');original();f.checked('close/reopen fences a late partial upload reply; explicit cancellation releases the session slot for the next real selection');clear()
   before=store.read_bytes();sent=upload_count();choose('over aggregate',1048576,5);f.idle();expect(b.locator('[data-resource-pending]')).to_have_count(0);choose('over file',1048577,1);f.idle();expect(b.locator('[data-resource-pending]')).to_have_count(0);assert store.read_bytes()==before and upload_count()==sent;b.locator('[data-resource-tree-id=""]').click();choose('maximum',1048576,4);done(4);hashes('maximum',1048576,4);assert all(x['parent']is None for x in files());assert json.loads(store.read_text())['version']==1;original();f.checked('exact 4MiB selection is one root v1 transaction; per-file 1MiB and aggregate 4MiB+ guards reject before upload without broadening stored grammar or per-file read size')
  elif mode=='lifecycle':
   clear();b.locator('[data-resource-tree-id="'+a+'"]').click();f.page.evaluate("""()=>{const base=File.prototype.arrayBuffer;globalThis.__transferReadHeld=false;File.prototype.arrayBuffer=async function(){const value=await base.call(this);if(!this.name.startsWith('Home 1'))return value;globalThis.__transferReadHeld=true;return new Promise(resolve=>{globalThis.__releaseTransferRead=()=>{File.prototype.arrayBuffer=base;resolve(value);};});};}""");choose('Home');f.page.wait_for_function('()=>__transferReadHeld');f.pending();listing=f.state()['listingId'];f.page.locator('#title').click();f.page.get_by_role('button',name='프로젝트 나가기',exact=True).click();expect(f.page.locator('.home-grid')).to_be_visible();f.page.evaluate('()=>__releaseTransferRead()');f.page.locator('[data-enter="'+listing+'"]').click();f.idle();b=f.page.locator('.window[data-key^="browser:project:"]').last;pending();assert not files();b.locator('[data-resource-pending=retry]').click();done(2);hashes('Home');original();f.checked('Home during a later File read starts no upload or partial write; original files/destination require explicit same-owner retry');clear();b.locator('[data-resource-tree-id="'+a+'"]').click();f.pending();before=store.read_bytes();arm('upload-chunk',False);choose('cold pending');f.page.wait_for_function('()=>__transferHeld');assert store.read_bytes()==before;restart(1,flush=False);expect(b.locator('[data-resource-pending]')).to_have_count(0);assert store.read_bytes()==before and not files();original();f.checked('cold engine loses unconfirmed transfer memory and File inputs without publishing/replaying bytes or altering the durable store')
   b.locator('[data-resource-tree-id=""]').click();choose('cold maximum',1048576,4);done(4);ids=[x['id']for x in files()];saved=store.read_bytes();f.pending();presentation=json.dumps(f.state()['presentation']);assert base64.urlsafe_b64encode(bytes([151])*1048576).decode()not in presentation;restart(2);assert store.read_bytes()==saved and[x['id']for x in files()]==ids;hashes('cold maximum',1048576,4);original();f.checked('confirmed maximum v1 group restores with the same IDs and exact per-file bytes; private layout contains no upload body')
   other=f.case/'same namespace other project';shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory','.build'));restart(3,other);assert not files();choose('B');done(2);hashes('B');restart(4,f.project);assert store.read_bytes()==saved and[x['id']for x in files()]==ids;original();f.checked('same-namespace real project roundtrip never transfers file bytes, staging IDs or pending targets between owners')
  else:raise AssertionError(mode)
  for row in f.traffic:
   if row.get('invoke',{}).get('input',{}).get('action','').startswith('upload-'):assert len(json.dumps(row['invoke'],ensure_ascii=False).encode())<2097152
  expect(f.page.locator('#chat-input')).to_have_value('분할 보관과 별개인 입력');original();f.pending();f.page.screenshot(path=str(f.case/('resource-transfer-'+mode+'.png')));f.browser.close()
except Exception as e:
 try:f.page.screenshot(path=str(f.case/'failure.png'))
 except Exception:pass
 (f.case/'failure.json').write_text(json.dumps(dict(error=repr(e),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:
 f.stop();(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2))
print('RESOURCE_TRANSFER_UI',f.case,flush=True)
