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
def cancel():
 b.locator('[data-resource-pending=cancel]').click();expect(b.locator('[data-resource-pending]')).to_have_count(0);f.idle()
def delete_file(id):
 parent=next(x['parent']for x in files()if x['id']==id);b.locator('[data-resource-tree-id="'+parent+'"]'if parent else'[data-root]').click();f.idle();b.locator('[data-resource-id="'+id+'"]').click(button='right');f.page.locator('.context-menu').get_by_role('button',name='삭제',exact=True).click();f.page.get_by_role('dialog',name='자료 삭제',exact=True).locator('[data-remove]').click();f.idle()
try:
 f.start(0)
 with sync_playwright()as p:
  expect.set_options(timeout=60000);f.browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.idle();browser();f.page.locator('#chat-input').fill('누적 자료와 별개인 입력')
  choose('first maximum',4194304,1);done(1);hashes('first maximum',4194304,1);first=files()[0];saved=store.read_bytes();assert json.loads(saved)['version']==1
  if mode=='baseline':
   choose('second maximum',4194304,1);pending();assert len(files())==1 and store.read_bytes()==saved;f.checked('published baseline refuses second4MiB File at aggregate4MiB, preserving first bytes/ID and failed selection');cancel()
  elif mode=='normal':
   a=folder();choose('second maximum',4194304,1);done(2);hashes('first maximum',4194304,1);hashes('second maximum',4194304,1);second=next(x for x in files()if x['id']!=first['id']);assert second['parent']==a;complete=store.read_bytes();assert json.loads(complete)['version']==2 and api()['limits']['totalBytes']==8388608 and api()['limits']['importBytes']==4194304 and api()['limits']['fileBytes']==4194304;bounded(first['id']);bounded(second['id']);f.checked('two successive actual4MiB selections retain8MiB exact bytes/IDs/receipts and folder placement, promote only on crossing4MiB, and keep per-file/selected/read/RPC bounds')
   choose('overflow',1,1);pending();assert store.read_bytes()==complete and len(files())==2;f.page.locator('#chat-input').fill('초과 실패 뒤 새 입력');cancel();assert store.read_bytes()==complete;f.checked('aggregate8MiB+one refuses atomically; cancel affects only failed selection and keeps new input plus both confirmed copies')
   delete_file(first['id']);assert json.loads(store.read_bytes())['version']==2 and len(files())==1;hashes('second maximum',4194304,1);b.locator('[data-root]').click();choose('replacement maximum',4194304,1);done(2);hashes('replacement maximum',4194304,1);hashes('second maximum',4194304,1);complete=store.read_bytes();ids=[x['id']for x in files()];restart(1);assert store.read_bytes()==complete and[x['id']for x in files()]==ids;original();f.checked('authored deletion frees only selected project copy, preserves v2 without silent downgrade and another exact4MiB append; cold restores all8MiB without upload/rewrite')
   other=f.case/'other owned project';shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory','.build'));restart(2,other);assert not files();restart(3,f.project);assert store.read_bytes()==complete and[x['id']for x in files()]==ids;expect(f.page.locator('#chat-input')).to_have_value('초과 실패 뒤 새 입력');f.checked('same-namespace different actual ProjectContext cannot read prior8MiB; explicit return and cold restore exact owned data and unrelated input')
  elif mode=='lifecycle':
   a=folder();before=store.read_bytes();topology=layout_path.read_bytes();permission=layout_path.stat().st_mode
   try:layout_path.chmod(0o444);choose('promoted retry',4194304,1);pending();assert store.read_bytes()==before and layout_path.read_bytes()==topology and json.loads(store.read_bytes())['version']==1
   finally:layout_path.chmod(permission)
   sent=upload_count();b.locator('[data-resource-pending=retry]').click();done(2);assert upload_count()==sent and json.loads(store.read_bytes())['version']==2;hashes('promoted retry',4194304,1);f.checked('real folder write refusal rolls back catalog promotion and placement together; exact retry consumes captured buffer once without changing first file')
   second=next(x for x in files()if x['id']!=first['id']);delete_file(second['id']);assert json.loads(store.read_bytes())['version']==2;b.locator('[data-root]').click();arm('upload-commit');choose('lost promoted maximum',4194304,1);f.page.wait_for_function('()=>__transferHeld');assert len(files())==2;f.page.locator('#chat-input').fill('승격 응답 유실 뒤 새 입력');f.page.evaluate('()=>__releaseTransfer()');pending();complete=store.read_bytes();sent=upload_count();b.locator('[data-resource-pending=retry]').click();done(2);assert store.read_bytes()==complete and upload_count()==sent;hashes('lost promoted maximum',4194304,1);f.checked('lost accepted8MiB reply resolves exact durable receipt, never duplicates/promotes twice/rebases or erases late input')
   second=next(x for x in files()if x['id']!=first['id']);delete_file(second['id']);before=store.read_bytes();arm('upload-chunk',False);choose('closed promotion',4194304,1);f.page.wait_for_function('()=>__transferHeld');b.locator('[data-close]').first.click();f.page.evaluate('()=>__releaseTransfer()');f.idle();browser();assert len(files())==1 and store.read_bytes()==before;restart(1);assert len(files())==1 and store.read_bytes()==before;hashes('first maximum',4194304,1);expect(f.page.locator('#chat-input')).to_have_value('승격 응답 유실 뒤 새 입력');f.checked('close fences late large chunk; restart retires unconfirmed upload and preserves exact confirmed v2 data without replay')
  else:raise AssertionError(mode)
  original();f.pending();f.page.screenshot(path=str(f.case/('resource-total-'+mode+'.png')));f.browser.close()
except Exception as e:
 try:f.page.screenshot(path=str(f.case/'failure.png'));(f.case/'failure.html').write_text(f.page.content())
 except Exception:pass
 (f.case/'failure.json').write_text(json.dumps(dict(error=repr(e),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:
 f.stop();(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2))
print('RESOURCE_TOTAL_UI',f.case,flush=True)
