"""Authored additive/range selection, selected deletion union and private owner lifetime."""
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

def picked():return set(b.locator('[data-resource-id][aria-selected=true]').evaluate_all('(rows)=>rows.map(row=>row.dataset.resourceId)'))
def pick(ids):
 for index,id in enumerate(ids):row(id).click(modifiers=['Control']if index else[])
 assert picked()==set(ids),(picked(),ids)
def multi_dialog(id,count,extra=0,cancel=False,submit=True):
 row(id).click(button='right');f.page.get_by_role('button',name=str(count)+'개 항목 삭제',exact=True).click();dialog=f.page.locator('.modal[aria-label="자료 삭제"]');expect(dialog).to_contain_text(str(count)+'개 항목')
 if extra:expect(dialog).to_contain_text('외 '+str(extra)+'개 항목')
 if submit:dialog.locator('[data-cancel]'if cancel else'[data-remove]').click()
 return dialog
try:
 f.start(0)
 with sync_playwright()as p:
  expect.set_options(timeout=60000);f.browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.idle();browser();raw='선택한 프로젝트 사본 🧪\r\n<script>neverExecute()</script>'.encode();raw_copy=bytes(raw)
  top,child=staged_tree('선택할 카테고리');root();folder('남길 카테고리');keep=named('남길 카테고리')['id'];peer=imported('남길 사본.txt');peer_record=next(x for x in json.loads(store.read_text())['items']if x['id']==peer);file=imported('선택 파일.txt');y=imported('추가 파일.txt');z=imported('다른 파일.txt');nested=imported('하위 파일.txt');move_to(nested,child);root();renamed(top,'선택 <안전> 🧪');open_folder(top);open_folder(child);renamed(nested,'하위 별칭.md');root();identity_bytes=(f.project/'.confectory/project-identity.json').read_bytes();f.page.locator('#chat-input').fill('다중 삭제와 별개인 입력');f.page.locator('#chat-input').press('Tab');f.idle()
  before=snapshot();order=rows().evaluate_all('(rows)=>rows.map(row=>row.dataset.resourceId)');first=order.index(peer);last=order.index(y);row(peer).click();row(y).click(modifiers=['Shift']);assert picked()==set(order[min(first,last):max(first,last)+1]);row(file).click(modifiers=['Control']);assert file not in picked();row(z).click(modifiers=['Meta']);assert z in picked();f.checked('actual Ctrl toggle, Meta additive and Shift visible-order range use explicit IDs without adding folders or all targets')
  selected=picked();b.get_by_role('button',name='표시 크기 6단계',exact=True).click();assert picked()==selected;b.locator('[data-browser-control=object-query]').fill('다른 파일');b.locator('[data-browser-control=object-query]').press('Enter');expect(rows()).to_have_count(1);row(z).click(button='right');f.page.get_by_role('button',name=str(len(selected))+'개 항목 삭제',exact=True).click();dialog=f.page.locator('.modal[aria-label="자료 삭제"]');dialog.locator('[data-cancel]').click();assert snapshot()==before;f.checked('density/search preserve prior explicit selection; multi-delete confirmation counts hidden selected IDs and Cancel writes no project data')
  root();b.get_by_role('button',name='표시 크기 3단계',exact=True).click();b.locator('[data-browser-control=browser-actions]').click();f.page.get_by_role('button',name='이름 내림차순',exact=True).click();order=rows().evaluate_all('(rows)=>rows.map(row=>row.dataset.resourceId)');row(order[1]).click();row(order[-1]).click(modifiers=['Shift']);assert picked()==set(order[1:]);row(order[0]).click(button='right');expect(f.page.get_by_role('button',name='이름 변경',exact=True)).to_be_visible();assert picked()=={order[0]};f.page.keyboard.press('Escape');assert snapshot()==before;f.checked('Shift follows current sorted visible order; right-click outside selection resets to the original single-item menu')
  if mode=='normal':
   pick([y,z]);row(y).drag_to(row(keep));expect(row(y)).to_have_count(0);expect(row(z)).to_have_count(0);f.idle();moved(y,keep);moved(z,keep);open_folder(keep);pick([y,z]);row(y).drag_to(tree(''));expect(row(y)).to_have_count(0);expect(row(z)).to_have_count(0);f.idle();moved(y,None);moved(z,None);root();intact_peer();f.checked('drag reuses the existing explicit multi-ID move contract; selected files move together and unselected bytes remain exact')
   peer_view=opened_file(peer);pick([top,file]);before=snapshot();multi_dialog(file,2,extra=2,cancel=True);assert snapshot()==before;folder_names=f.project/'.confectory/resource-folder-names.v1.json';permission=folder_names.stat().st_mode
   try:
    folder_names.chmod(0o444);multi_dialog(file,2,extra=2);pending();expect(b.locator('[data-resource-recovery]')).to_contain_text('2개 항목');assert snapshot()==before;assert picked()=={top,file}
   finally:folder_names.chmod(permission)
   hold_reply();b.locator('[data-resource-layout-pending=retry]').click();f.page.wait_for_function('()=>__layoutHeld');assert {top,child,file,nested}.isdisjoint(selected_ids());saved=snapshot();pick([y,z]);b.locator('[data-browser-control=object-query]').fill('더 늦은 검색 입력');f.page.evaluate('()=>__releaseLayout()');pending();b.locator('[data-resource-layout-pending=retry]').click();no_pending();assert snapshot()==saved;assert picked()=={y,z};expect(b.locator('[data-browser-control=object-query]')).to_have_value('더 늦은 검색 입력');expect(peer_view).to_be_visible();intact_peer();f.checked('real five-file write refusal and actual lost success retain exact mixed targets; replay writes nothing and preserves newer additive selection/query plus outside preview')
   root();top,child=staged_tree('동시 선택');file=imported('동시 대상 파일.txt');pick([top,file]);dialog=multi_dialog(file,2,extra=1,submit=False);basis=api('load');api('rename-file',revision=basis['revision'],command=uuid.uuid4().hex,id=file,name='동시 보존 파일.txt');dialog.locator('[data-remove]').click();pending();saved=snapshot();b.locator('[data-resource-reload]').click();f.idle();b.locator('[data-resource-layout-pending=retry]').click();pending();assert snapshot()==saved and {top,child,file}.issubset(selected_ids());b.locator('[data-resource-layout-pending=cancel]').click();no_pending();intact_peer();f.checked('one target changed after confirmation rejects the entire selection through refresh/retry; input-only cancellation preserves every peer target')
  elif mode=='lifecycle':
   pick([top,file]);before=snapshot();f.pending();restart(1);assert picked()=={top,file};no_pending();assert snapshot()==before;f.checked('cold private workspace restores explicit selected IDs and anchor without issuing a deletion')
   hold_reply();multi_dialog(file,2,extra=2);f.page.wait_for_function('()=>__layoutHeld');f.page.evaluate('()=>__releaseLayout()');pending();f.pending();saved=snapshot();restart(2);pending();assert {top,child,file,nested}.isdisjoint(selected_ids())and snapshot()==saved;pick([y,z]);b.locator('[data-resource-layout-pending=retry]').click();no_pending();assert snapshot()==saved and picked()=={y,z};intact_peer();f.checked('cold exact selected intent is never auto-replayed; explicit lost-response receipt confirmation preserves a newer selection and writes nothing')
   f.pending();other=f.case/'other actual project';shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory','.build'));restart(3,other);assert api('load')['items']==[];assert picked()==set();no_pending();assert snapshot()==saved;restart(4,f.project);no_pending();assert picked()=={y,z};intact_peer();f.checked('other actual project cannot adopt selected IDs, pending delete or resources; returning restores only original private selection and surviving data')
  else:raise AssertionError(mode)
  intact_peer();f.pending();expect(f.page.locator('#chat-input')).to_have_value('다중 삭제와 별개인 입력');f.page.screenshot(path=str(f.case/('multi-deletion-'+mode+'.png')));f.browser.close()
except Exception as error:
 (f.case/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:
 f.stop();(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2))
print('RESOURCE_MULTI_DELETION_UI_FIXTURE',f.case,flush=True)
