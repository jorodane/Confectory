"""Explicit category subtree deletion; exact observed closure, receipts and private UI lifetime."""
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
 if blur:input.press('Tab')
 else:input.press('Enter')
 expect(tree(id)).to_have_attribute('title',value);f.idle()
def exact_sources():
 original();assert store.read_bytes()==file_bytes and(f.project/'.confectory/project-identity.json').read_bytes()==identity_bytes
def viewer(id):return f.page.locator('.window[data-key="resource-file:'+id+'"]')
def opened_file(id,held=False):
 row(id).press('Enter');w=viewer(id);expect(w).to_be_visible()
 if not held:expect(w.locator('.resource-document-text')).to_have_text(raw.decode())

 if 'folded'not in(w.get_attribute('class')or'').split():w.locator('[data-fold]').first.click()
 return w
def close_file(id):
 row(id).press('Enter');viewer(id).locator('[data-close]').first.click();expect(viewer(id)).to_have_count(0)
def current_viewer_name(w,name):
 expect(w).to_have_attribute('aria-label',name);expect(w.locator('[data-resource-setting-name]')).to_have_value(name);expect(w.locator('.resource-document-text')).to_have_text(raw.decode())
def hold_file_read():
 f.page.evaluate("""()=>{const base=fetch;let armed=true;globalThis.__fileReadHeld=false;fetch=async(...args)=>{let request;try{request=JSON.parse(args[1]?.body||'null')}catch{}const response=await base(...args);if(!armed||request?.op!=='observe'||request.endpoint!=='readProjectResource')return response;const actual=await response.clone().json();if(!actual.ok)return response;armed=false;globalThis.__fileReadHeld=true;return new Promise(resolve=>{globalThis.__releaseOldFileRead=()=>{fetch=base;resolve(response);};});};}""")

def delete_dialog(id,cancel=False,surface='card',submit=True):
 (tree(id)if surface=='tree'else row(id)).click(button='right');f.page.get_by_role('button',name='삭제',exact=True).click();dialog=f.page.locator('.modal[aria-label="자료 삭제"]')
 expect(dialog).to_contain_text('자료 삭제')
 if submit:dialog.locator('[data-cancel]'if cancel else'[data-remove]').click()
 return dialog

def selected_ids():return {x['id']for x in api('load')['items']}
def intact_peer():
 original();assert (f.project/'.confectory/project-identity.json').read_bytes()==identity_bytes
 assert next(x for x in json.loads(store.read_text())['items']if x['id']==peer)==peer_record
 assert raw==raw_copy

def pending():expect(b.locator('[data-resource-layout-pending=retry]')).to_be_enabled()
def no_pending():expect(b.locator('[data-resource-layout-pending]')).to_have_count(0)

def imported(name):
 root();b.locator('[data-resource-files]').set_input_files(dict(name=name,mimeType='text/plain',buffer=raw));f.idle();expect(b.locator('[data-new]')).to_be_enabled();return named(name)['id']
def move_to(id,parent):
 node=row(id)if row(id).count()else tree(id);target=row(parent)if parent and row(parent).count()else tree(parent or'');node.drag_to(target)
 if row(id).count():expect(row(id)).to_have_count(0)
 f.idle();moved(id,parent)
def snapshot():return {p.name:p.read_bytes()for p in (f.project/'.confectory').glob('resource*.json')}
def folder_delete(id,cancel=False,submit=True,count=None,surface='card'):
 dialog=delete_dialog(id,cancel=cancel,surface=surface,submit=False)
 if count is not None:expect(dialog).to_contain_text('외 '+str(count)+'개 항목')
 if submit:dialog.locator('[data-cancel]'if cancel else'[data-remove]').click()
 return dialog

def staged_tree(title):
 root();folder(title);top=named(title)['id'];open_folder(top);folder(title+' 하위');child=named(title+' 하위')['id'];root();return top,child
try:
 f.start(0)
 with sync_playwright()as p:
  expect.set_options(timeout=60000);f.browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.idle();browser();raw='카테고리의 프로젝트 사본 🧪\r\n<script>neverExecute()</script>'.encode();raw_copy=bytes(raw)
  top,child=staged_tree('삭제할 카테고리');open_folder(top);open_folder(child);folder('옮겨 나온 카테고리');escaped=named('옮겨 나온 카테고리')['id'];move_to(escaped,None);root();renamed(escaped,'남길 카테고리');peer=imported('남길 원본 사본.txt');peer_record=next(x for x in json.loads(store.read_text())['items']if x['id']==peer);file=imported('직접 하위 파일.txt');move_to(file,top);nested_file=imported('중첩 하위 파일.txt');move_to(nested_file,child);root();renamed(top,'삭제 <안전> 🧪');open_folder(top);open_folder(child);renamed(nested_file,'삭제할 별칭.md');root();identity_bytes=(f.project/'.confectory/project-identity.json').read_bytes();f.page.locator('#chat-input').fill('카테고리 삭제와 별개인 입력')
  before=snapshot();folder_delete(top,cancel=True,count=3);assert snapshot()==before;f.checked('authored category confirmation shows transitive descendant count; Cancel preserves all bytes/topology/names/receipts')
  if mode=='normal':
   peer_view=opened_file(peer);hold_file_read();tree(file).dblclick();w=viewer(file);expect(w).to_be_visible();
   if 'folded'not in(w.get_attribute('class')or'').split():w.locator('[data-fold]').first.click()
   f.page.wait_for_function('()=>__fileReadHeld');folder_names=f.project/'.confectory/resource-folder-names.v1.json';permission=folder_names.stat().st_mode
   try:
    folder_names.chmod(0o444);folder_delete(top,count=3);pending();expect(b.locator('[data-resource-recovery]')).to_contain_text('삭제 <안전> 🧪');assert snapshot()==before;expect(w).to_be_visible()
   finally:folder_names.chmod(permission)
   b.locator('[data-resource-layout-pending=retry]').click();no_pending();expect(viewer(file)).to_have_count(0);f.page.evaluate('()=>__releaseOldFileRead()');expect(viewer(file)).to_have_count(0);expect(peer_view).to_be_visible();assert selected_ids()=={escaped,peer};intact_peer();expect(tree(escaped)).to_have_attribute('title','남길 카테고리');f.checked('real folder-name write refusal preserves the whole subtree; retry removes all five data components, aborts delayed child preview and preserves outside viewer/copy/moved-out category')
   top,child=staged_tree('유실 응답 카테고리');hold_reply();folder_delete(top,count=1);f.page.wait_for_function('()=>__layoutHeld');assert top not in selected_ids()and child not in selected_ids();b.locator('[data-browser-control=object-query]').fill('뒤늦은 카테고리 검색');f.page.evaluate('()=>__releaseLayout()');pending();saved=snapshot();b.locator('[data-resource-layout-pending=retry]').click();no_pending();assert snapshot()==saved;expect(b.locator('[data-browser-control=object-query]')).to_have_value('뒤늦은 카테고리 검색');intact_peer();f.checked('lost actual subtree deletion success replays exact receipt without new writes or replacing newer query; empty categories never rewrite surviving copy storage')
   top,child=staged_tree('동시 변경 카테고리');late=imported('옮길 자식.txt');move_to(late,child);dialog=folder_delete(top,submit=False,count=2);basis=api('load');api('move',revision=basis['revision'],command=uuid.uuid4().hex,ids=[late],parent=None);dialog.locator('[data-remove]').click();pending();saved=snapshot();b.locator('[data-resource-reload]').click();f.idle();b.locator('[data-resource-layout-pending=retry]').click();pending();assert snapshot()==saved and {top,child,late}.issubset(selected_ids());b.locator('[data-resource-layout-pending=cancel]').click();no_pending();assert next(x for x in api('load')['items']if x['id']==late)['parent']is None;intact_peer();f.checked('child moved after confirmation makes frozen deletion stale; refresh/retry never expands/rebases deletion, and input-only cancellation preserves peer topology')
  elif mode=='lifecycle':
   open_folder(top);open_folder(child);hold_reply();folder_delete(top,count=3,surface='tree');f.page.wait_for_function('()=>__layoutHeld');f.page.evaluate('()=>__releaseLayout()');pending();f.pending();saved=snapshot();restart(1);pending();assert selected_ids()=={escaped,peer}and snapshot()==saved;b.locator('[data-resource-layout-pending=retry]').click();no_pending();assert snapshot()==saved;expect(b.locator('.browser-title-path')).to_contain_text('ProjectPack');intact_peer();f.checked('cold restore retains exact ancestor delete intent without automatic replay; explicit receipt confirmation writes nothing and deleted active folder falls back to ProjectPack')
   other=f.case/'other actual project';shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory','.build'));restart(2,other);assert api('load')['items']==[];no_pending();assert snapshot()==saved;restart(3,f.project);no_pending();assert selected_ids()=={escaped,peer};intact_peer();f.checked('actual project switch cannot import subtree deletion/data/private pending state; returning retains only confirmed original-project peers')
  else:raise AssertionError(mode)
  intact_peer();f.pending();expect(f.page.locator('#chat-input')).to_have_value('카테고리 삭제와 별개인 입력');f.page.screenshot(path=str(f.case/('folder-deletion-'+mode+'.png')));f.browser.close()
except Exception as error:
 (f.case/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:
 f.stop();(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2))
print('RESOURCE_FOLDER_DELETION_UI_FIXTURE',f.case,flush=True)
