"""Authored file display names and current read-only preview; immutable copies/IDs/receipts."""
import sys,json,pathlib,hashlib,base64,uuid,shutil,traceback
from playwright.sync_api import sync_playwright,expect
import v536_wide_mixed as f
mode=sys.argv[3];store=f.project/'.confectory/resources.v1.json';layout=f.project/'.confectory/resource-layout.v1.json';b=None

def api(action,success=True,**args):return f.invoke('projectResourceLayout',dict(action=action,project=f.state()['projectId'],**args),success)['result'].get('result')
def rows():return b.locator('[data-resource-id]')
def original():
 for relative,raw in f.original.items():assert(f.project/relative).read_bytes()==raw,relative
 assert not f.errors and not f.external,(f.errors,f.external)
def browser():
 global b
 f.page.locator('#workspace').click(button='right',position=dict(x=700,y=260));f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]').last;b.locator('[data-tab=resource]').click();expect(b.locator('[data-new]')).to_be_enabled()
def folder(name,cancel=False,wait=True):
 b.locator('[data-new]').click();f.page.get_by_role('button',name='새 카테고리',exact=True).click();form=f.page.locator('.resource-name-form');expect(form).to_be_visible();form.locator('[name=name]').fill(name);form.get_by_role('button',name='취소'if cancel else'확인',exact=True).click();expect(form).to_have_count(0)
 if not cancel and wait:f.idle()
def row(id):return b.locator('[data-resource-id="'+id+'"]')
def tree(id):return b.locator('[data-resource-tree-id="'+id+'"]')
def root():b.locator('[data-root]').click();f.idle()
def named(name):return next(x for x in api('load')['items']if x['name']==name)
def moved(id,parent):
 actual=next(x for x in api('load')['items']if x['id']==id)['parent']
 if actual!=parent:
  f.page.screenshot(path=str(f.case/'drag-failure.png'));(f.case/'drag-failure.html').write_text(f.page.content());(f.case/'drag-events.json').write_text(json.dumps(f.page.evaluate('()=>globalThis.__resourceDragEvents||[]'),ensure_ascii=False));raise AssertionError(dict(id=id,expected=parent,actual=actual,errors=f.errors))
def open_folder(id):row(id).dblclick();f.idle();expect(b.locator('.browser-title-path')).to_contain_text(next(x['name']for x in api('load')['items']if x['id']==id))
def hold_reply():
 f.page.evaluate("""()=>{const base=fetch;globalThis.__layoutHeld=false;let wanted=null,armed=true;fetch=async(...args)=>{let request;try{request=JSON.parse(args[1]?.body||'null')}catch{}if(armed&&request?.op==='invoke'&&request.endpoint==='projectResourceLayout'&&request.input?.action!=='load')wanted=request.requestId;const response=await base(...args);if(!wanted||!armed||request?.op!=='update')return response;let body;try{body=await response.clone().json()}catch{return response}const row=body.results?.find(r=>r.requestId===wanted);if(!row?.ok)return response;armed=false;globalThis.__layoutHeld=true;return new Promise(resolve=>{globalThis.__releaseLayout=()=>{fetch=base;delete row.result;row.ok=false;row.error={code:'owned_lost_layout_reply'};resolve(new Response(JSON.stringify(body),{status:200,headers:{'Content-Type':'application/json'}}));};});};}""")
def restart(index,project=None):
 global b
 f.pending();f.page.close();f.stop()
 if project:f.env['CONFECTORY_WEB_PROJECT']=str(project/'project.cproj')
 f.start(index);f.page=f.setup();f.idle();b=f.page.locator('.window[data-key^="browser:project:"]').last
 if not b.count():browser()
 else:expect(b.locator('[data-resource-status]')).to_be_visible();f.idle()
names=f.project/'.confectory/resource-file-names.v1.json'
def begin_rename(id,value,surface='card'):
 node=tree(id)if surface=='tree'else row(id);node.click(button='right');f.page.get_by_role('button',name='이름 변경',exact=True).click();input=b.locator('[data-resource-rename]');expect(input).to_be_visible();input.fill(value);return input
def renamed(id,value,surface='card',blur=False):
 input=begin_rename(id,value,surface)
 if blur:b.locator('[data-browser-control=object-query]').click()
 else:input.press('Enter')
 expect(tree(id)).to_have_attribute('title',value);f.idle()
def exact_sources():
 original();assert store.read_bytes()==file_bytes and(f.project/'.confectory/project-identity.json').read_bytes()==identity_bytes
def viewer(id):return f.page.locator('.window[data-key="resource-file:'+id+'"]')
def opened_file(id,held=False):
 row(id).press('Enter');w=viewer(id);expect(w).to_be_visible()
 if not held:expect(w.locator('.resource-document-text')).to_have_text(raw.decode())
 w.locator('[data-fold]').first.click();return w
def current_viewer_name(w,name):
 expect(w).to_have_attribute('aria-label',name);expect(w.locator('[data-resource-setting-name]')).to_have_value(name);expect(w.locator('.resource-document-text')).to_have_text(raw.decode())
def hold_file_read():
 f.page.evaluate("""()=>{const base=fetch;let armed=true;globalThis.__fileReadHeld=false;fetch=async(...args)=>{let request;try{request=JSON.parse(args[1]?.body||'null')}catch{}const response=await base(...args);if(!armed||request?.op!=='observe'||request.endpoint!=='readProjectResource')return response;const actual=await response.clone().json();if(!actual.ok)return response;armed=false;globalThis.__fileReadHeld=true;return new Promise(resolve=>{globalThis.__releaseOldFileRead=()=>{fetch=base;resolve(response);};});};}""")
try:
 f.start(0)
 with sync_playwright()as p:
  expect.set_options(timeout=60000);f.browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.idle();browser();folder('카테고리');folder_id=named('카테고리')['id'];raw='변경하지 않는 원본 바이트 🧪\r\n<script>neverExecute()</script>'.encode();b.locator('[data-resource-files]').set_input_files(dict(name='원래 파일.txt',mimeType='text/plain',buffer=raw));f.idle();expect(b.locator('[data-new]')).to_be_enabled();file=named('원래 파일.txt')['id'];file_bytes=store.read_bytes();identity_bytes=(f.project/'.confectory/project-identity.json').read_bytes();topology=layout.read_bytes();assert not names.exists()
  input=begin_rename(file,'취소 이름.md');input.press('Escape');expect(b.locator('[data-resource-rename]')).to_have_count(0);assert not names.exists();expect(tree(file)).to_have_attribute('title','원래 파일.txt');exact_sources();f.checked('authored file context inline Escape cancels only the input without creating display-name storage or rewriting original copy metadata')
  renamed(file,'첫 파일 <안전>.md');assert layout.read_bytes()==topology;w=opened_file(file);current_viewer_name(w,'첫 파일 <안전>.md');exact_sources();f.checked('actual Enter renames the complete display name with a stable ID/hash; opening its unchanged bytes shows current metadata in the original read-only preview')
  renamed(file,'열린 미리보기.txt',surface='tree',blur=True);current_viewer_name(w,'열린 미리보기.txt');expect(w.locator('[data-resource-setting-name]')).to_have_attribute('readonly','');assert layout.read_bytes()==topology;exact_sources();f.checked('tree inline blur refreshes an already-open preview title/read-only filename from current authorized metadata while preserving MIME/kind/content and byte identity')
  f.page.locator('#chat-input').fill('파일 이름과 별개인 입력')
  if mode=='normal':
   prior=names.read_bytes();permission=names.stat().st_mode
   try:
    names.chmod(0o444);input=begin_rename(file,'쓰기 실패 이름.txt');input.press('Enter');expect(b.locator('[data-resource-layout-pending=retry]')).to_be_enabled();expect(b.locator('[data-resource-recovery]')).to_contain_text('쓰기 실패 이름.txt');assert names.read_bytes()==prior
   finally:names.chmod(permission)
   b.locator('[data-resource-layout-pending=retry]').click();expect(tree(file)).to_have_attribute('title','쓰기 실패 이름.txt');expect(b.locator('[data-resource-layout-pending]')).to_have_count(0);current_viewer_name(w,'쓰기 실패 이름.txt');exact_sources();f.checked('real display-name file write refusal retains exact pending name/ID/revision/command; explicit retry recovers without rewriting bytes/topology')
   hold_reply();input=begin_rename(file,'응답 유실 파일.md');input.press('Enter');f.page.wait_for_function('()=>__layoutHeld');b.locator('[data-browser-control=object-query]').fill('뒤늦은 파일 검색');f.page.evaluate('()=>__releaseLayout()');expect(b.locator('[data-resource-layout-pending=retry]')).to_be_enabled();b.locator('[data-resource-layout-pending=retry]').click();expect(tree(file)).to_have_attribute('title','응답 유실 파일.md');expect(b.locator('[data-resource-layout-pending]')).to_have_count(0);expect(b.locator('[data-browser-control=object-query]')).to_have_value('뒤늦은 파일 검색');assert len(json.loads(names.read_text())['items'])==1;current_viewer_name(w,'응답 유실 파일.md');exact_sources();f.checked('lost actual rename success reply reuses its exact receipt without duplicate aliases or replacement of newer query/current preview state')
   input=begin_rename(file,'오래된 파일 입력.txt');basis=api('load');api('rename-file',revision=basis['revision'],command=uuid.uuid4().hex,id=file,name='동시 파일 이름.txt');input.press('Enter');expect(b.locator('[data-resource-layout-pending=retry]')).to_be_enabled();peer=names.read_bytes();b.locator('[data-resource-reload]').click();f.idle();b.locator('[data-resource-layout-pending=retry]').click();expect(b.locator('[data-resource-layout-pending=retry]')).to_be_enabled();assert names.read_bytes()==peer;b.locator('[data-resource-layout-pending=cancel]').click();expect(b.locator('[data-resource-layout-pending]')).to_have_count(0);expect(tree(file)).to_have_attribute('title','동시 파일 이름.txt');current_viewer_name(w,'동시 파일 이름.txt');exact_sources();f.checked('peer update after inline capture is refused through refresh/retry; cancelling only the local intent preserves the peer filename and bytes')
   w.locator('[data-close]').first.click();hold_file_read();w=opened_file(file,True);f.page.wait_for_function('()=>__fileReadHeld');renamed(file,'늦은 읽기 보호.md');current_viewer_name(w,'늦은 읽기 보호.md');f.page.evaluate('()=>__releaseOldFileRead()');current_viewer_name(w,'늦은 읽기 보호.md');expect(w.locator('[data-resource-preview-retry]')).to_have_count(0);exact_sources();f.checked('actual old read success held after native completion cannot overwrite a newer renamed preview; metadata change retires the old token and rereads the same ID/hash')
  elif mode=='lifecycle':
   w.locator('[data-close]').first.click();prior=names.read_bytes();input=begin_rename(file,'재시작 미확정 파일.md');f.pending();assert '재시작 미확정 파일.md'in json.dumps(f.state()['presentation'],ensure_ascii=False);restart(1);expect(b.locator('[data-resource-rename]')).to_have_value('재시작 미확정 파일.md');assert names.read_bytes()==prior;b.locator('[data-resource-rename]').press('Escape');expect(b.locator('[data-resource-rename]')).to_have_count(0);assert names.read_bytes()==prior;exact_sources();f.checked('cold engine restores file-kind inline input with its original basis without automatic rename; Escape preserves confirmed metadata')
   hold_reply();input=begin_rename(file,'저장 재확인 파일.txt');input.press('Enter');f.page.wait_for_function('()=>__layoutHeld');f.page.evaluate('()=>__releaseLayout()');expect(b.locator('[data-resource-layout-pending=retry]')).to_be_enabled();saved=names.read_bytes();f.pending();restart(2);expect(b.locator('[data-resource-layout-pending=retry]')).to_be_enabled();assert names.read_bytes()==saved;b.locator('[data-resource-layout-pending=retry]').click();expect(b.locator('[data-resource-layout-pending]')).to_have_count(0);expect(tree(file)).to_have_attribute('title','저장 재확인 파일.txt');assert names.read_bytes()==saved;w=opened_file(file);current_viewer_name(w,'저장 재확인 파일.txt');w.locator('[data-close]').first.click();exact_sources();f.checked('cold staged rename restores exact request only; explicit replay performs no extra write and the reopened native preview reads current name/original bytes')
   other=f.case/'same namespace other project';shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory','.build'));restart(3,other);assert api('load')['items']==[];expect(b.locator('[data-resource-rename],[data-resource-layout-pending]')).to_have_count(0);assert names.read_bytes()==saved;restart(4,f.project);expect(tree(file)).to_have_attribute('title','저장 재확인 파일.txt');assert names.read_bytes()==saved;exact_sources();f.checked('same namespace in another actual project cannot adopt file-name data/inputs; returning restores only the original project name state')
  else:raise AssertionError(mode)
  assert layout.read_bytes()==topology;exact_sources();f.pending();expect(f.page.locator('#chat-input')).to_have_value('파일 이름과 별개인 입력');f.page.screenshot(path=str(f.case/('file-renames-'+mode+'.png')));f.browser.close()
except Exception as error:
 (f.case/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:
 f.stop();(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2))
print('RESOURCE_FILE_RENAMES_UI_FIXTURE',f.case,flush=True)
