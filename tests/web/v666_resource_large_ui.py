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
 b.locator('[data-browser-control=object-query]').fill('');b.locator('[data-browser-control=object-query]').press('Enter');f.page.evaluate('()=>document.activeElement?.blur()');f.pending();f.idle()
 # Remove only this fixture's confirmed generated copies through authored UI.
 for parent in dict.fromkeys(x['parent']for x in files()):
  b.locator('[data-resource-tree-id="'+parent+'"]'if parent else'[data-root]').click();f.idle();ids=[x['id']for x in files()if x['parent']==parent]
  for index,id in enumerate(ids):b.locator('[data-resource-id="'+id+'"]').click(modifiers=['Control']if index else[])
  b.locator('[data-resource-id="'+ids[0]+'"]').click(button='right');f.page.locator('.context-menu').get_by_role('button',name=str(len(ids))+'개 항목 삭제'if len(ids)>1 else'삭제',exact=True).click();f.page.get_by_role('dialog',name='자료 삭제',exact=True).locator('[data-remove]').click();f.idle()
 assert not files();original()
def folder():
 f.page.evaluate('()=>document.activeElement?.blur()');f.pending();f.idle();expect(b.locator('[data-new]')).to_be_enabled();b.locator('[data-new]').click();f.page.locator('.context-menu').get_by_role('button',name='새 카테고리',exact=True).click();form=f.page.locator('.resource-name-form');form.locator('[name=name]').fill('큰 선택 목적지');form.get_by_role('button',name='확인',exact=True).click();f.idle();id=next(x['id']for x in api()['items']if x['kind']=='folder');b.locator('[data-resource-id="'+id+'"]').dblclick();return id

def restart(index,project=None,flush=True):
 global b
 if flush:f.pending()
 f.page.close();f.stop()
 if project:f.env['CONFECTORY_WEB_PROJECT']=str(project/'project.cproj')
 f.start(index);f.page=f.setup();f.idle();b=f.page.locator('.window[data-key^="browser:project:"]').last
 if not b.count():browser()
 else:expect(b.locator('[data-resource-status]')).to_be_visible();f.idle()
def hashes(prefix,size=600000,count=2):
 rows=[x for x in files()if x['name'].startswith(prefix)];assert len(rows)==count
 saved=json.loads((pathlib.Path(f.env['CONFECTORY_WEB_PROJECT']).parent/'.confectory/resources.v1.json').read_text())['items']
 for n in range(count):
  row=next(x for x in rows if x['name']==prefix+' '+str(n)+' 🧪.bin');raw=bytes([151+n])*size;assert row['hash']==hashlib.sha256(raw).hexdigest();actual=next(x for x in saved if x['id']==row['id']);assert base64.urlsafe_b64decode(actual['data'])==raw
def bounded(id):
 item=next(x for x in files()if x['id']==id);q=f.invoke('projectResources',dict(action='read',project=f.state()['projectId'],id=id,hash=item['hash']))['result']['result'];assert q['encoding']=='unavailable'and q['reason']=='resource_preview_file_budget'and 'data'not in q and len(json.dumps(q).encode())<16384;return item
try:
 f.start(0)
 with sync_playwright()as p:
  expect.set_options(timeout=60000);f.browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.idle();browser();f.page.locator('#chat-input').fill('큰 파일과 별개인 새 입력')
  assert api()['limits']['fileBytes']==4194304 and api()['limits']['contentFileBytes']==1048576
  if mode=='normal':
   a=folder();choose('large folder',2097152,1);done(1);hashes('large folder',2097152,1);item=files()[0];id=item['id'];assert item['parent']==a;bounded(id);saved=store.read_bytes();b.locator('[data-resource-id="'+id+'"]').press('Enter');w=f.page.locator('.window[data-key="resource-file:'+id+'"]');expect(w.locator('.resource-preview')).to_contain_text('1 MiB를 넘는 파일');expect(w.locator('[data-resource-setting-name]')).to_have_value(item['name']);expect(w.locator('.resource-text-editor')).to_have_count(0)
   field=w.locator('[data-resource-setting-description]');field.fill('내용 전송과 별개인 큰 파일 설명 🧪');field.press('Tab');f.pending();f.idle();assert next(x for x in files()if x['id']==id).get('description')=='내용 전송과 별개인 큰 파일 설명 🧪';assert store.read_bytes()==saved
   w.locator('[data-close]').first.click();b.locator('[data-resource-id="'+id+'"]').click(button='right');f.page.get_by_role('button',name='이름 변경',exact=True).click();name=b.locator('[data-resource-rename]');name.fill('큰 파일 이름 🧪.txt');name.press('Enter');expect(b.locator('[data-resource-tree-id="'+id+'"]')).to_have_attribute('title','큰 파일 이름 🧪.txt');f.idle();assert store.read_bytes()==saved;item=bounded(id)
   f.invoke('projectResourceLayout',dict(action='save-content',project=f.state()['projectId'],revision=api()['revision'],command=uuid.uuid4().hex,id=id,hash=item['hash'],type=item['type'],size=1,data='QQ=='),False);assert store.read_bytes()==saved and not(f.project/'.confectory/resource-content'/str(id+'.v1.json')).exists();api();original();f.checked('actual2MiB folder File is preserved exactly; large preview publishes honest bounded metadata and editable description/current rename; forced small edit is rejected before creating an oversized backup')
   before=store.read_bytes();topology=layout_path.read_bytes();permission=layout_path.stat().st_mode
   try:layout_path.chmod(0o444);choose('large retry',2097152,1);pending();assert store.read_bytes()==before and layout_path.read_bytes()==topology
   finally:layout_path.chmod(permission)
   sent=upload_count();b.locator('[data-resource-pending=retry]').click();done(2);assert upload_count()==sent;hashes('large retry',2097152,1);original();f.checked('two2MiB files reach unchanged4MiB aggregate; actual folder write refusal rolls back bytes/layout and exact retry uses the completed staged buffer');clear();b.locator('[data-root]').click()
   choose('single maximum',4194304,1);done(1);hashes('single maximum',4194304,1);id=files()[0]['id'];bounded(id);saved=store.read_bytes();ids=[id];f.pending();presentation=json.dumps(f.state()['presentation']);assert base64.urlsafe_b64encode(bytes([151])*4194304).decode()not in presentation;restart(1);assert store.read_bytes()==saved and[x['id']for x in files()]==ids;hashes('single maximum',4194304,1);bounded(id);original();f.checked('one root4MiB File uses the batch transfer schema and one atomic commit; cold restores exact bytes/ID without an oversized RPC result or private bytes');clear()
   before=store.read_bytes();sent=upload_count();choose('over file',4194305,1);f.idle();expect(b.locator('[data-resource-pending]')).to_have_count(0);choose('over aggregate',2097153,2);f.idle();expect(b.locator('[data-resource-pending]')).to_have_count(0);assert store.read_bytes()==before and upload_count()==sent;original();f.checked('file4MiB+1 and aggregate4MiB+2 refuse before reading/staging; authored deletion removes confirmed large copies without altering original sources')
  elif mode=='lifecycle':
   arm('upload-commit');choose('lost maximum',4194304,1);f.page.wait_for_function('()=>__transferHeld');assert len(files())==1;b.locator('[data-browser-control=object-query]').fill('큰 파일 뒤의 늦은 검색');f.page.evaluate('()=>__releaseTransfer()');pending();saved=store.read_bytes();sent=upload_count();b.locator('[data-resource-pending=retry]').click();done(1);assert upload_count()==sent and store.read_bytes()==saved;expect(b.locator('[data-browser-control=object-query]')).to_have_value('큰 파일 뒤의 늦은 검색');hashes('lost maximum',4194304,1);bounded(files()[0]['id']);original();f.checked('lost accepted4MiB commit retains exact original intent and newer search/chat input; explicit retry revalidates receipt with no duplicate/upload/rebase');clear()
   before=store.read_bytes();arm('upload-chunk',False);choose('closed maximum',4194304,1);f.page.wait_for_function('()=>__transferHeld');b.locator('[data-close]').first.click();f.page.evaluate('()=>__releaseTransfer()');f.idle();browser();key=b.get_attribute('data-key');expect(b.locator('[data-resource-pending]')).to_have_count(0);assert not files()and store.read_bytes()==before;f.pending();listing=f.state()['listingId'];f.page.locator('#title').click();f.page.get_by_role('button',name='프로젝트 나가기',exact=True).click();expect(f.page.locator('.home-grid')).to_be_visible();f.page.locator('[data-enter="'+listing+'"]').click();f.idle();b=f.page.locator('.window[data-key="'+key+'"]');expect(b).to_be_visible();choose('confirmed maximum',4194304,1);done(1);hashes('confirmed maximum',4194304,1);saved=store.read_bytes();ids=[x['id']for x in files()];restart(1);assert store.read_bytes()==saved and[x['id']for x in files()]==ids;original();f.checked('closing a real browser fences a late4MiB chunk; Home retires only session staging and cold restores only the explicitly confirmed copy')
   other=f.case/'same namespace different owner';shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory','.build'));restart(2,other);assert not files();choose('other maximum',4194304,1);done(1);hashes('other maximum',4194304,1);restart(3,f.project);assert store.read_bytes()==saved and[x['id']for x in files()]==ids;original();f.checked('real same-namespace project roundtrip isolates large byte stores, identities, pending input and transfer ownership');clear();before=store.read_bytes();arm('upload-chunk',False);choose('cold unconfirmed',4194304,1);f.page.wait_for_function('()=>__transferHeld');restart(4,flush=False);expect(b.locator('[data-resource-pending]')).to_have_count(0);assert store.read_bytes()==before and not files();original();f.checked('restart during a partial large upload never publishes or automatically replays unconfirmed File bytes')
  else:raise AssertionError(mode)
  for row in f.traffic:
   if row.get('invoke',{}).get('input',{}).get('action','').startswith('upload-'):assert len(json.dumps(row['invoke'],ensure_ascii=False).encode())<2097152
  expect(f.page.locator('#chat-input')).to_have_value('큰 파일과 별개인 새 입력');original();f.pending();f.page.screenshot(path=str(f.case/('resource-large-'+mode+'.png')));f.browser.close()
except Exception as e:
 try:f.page.screenshot(path=str(f.case/'failure.png'))
 except Exception:pass
 (f.case/'failure.json').write_text(json.dumps(dict(error=repr(e),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:
 f.stop();(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2))
print('RESOURCE_LARGE_UI',f.case,flush=True)
