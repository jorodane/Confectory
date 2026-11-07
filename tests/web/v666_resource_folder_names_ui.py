"""Authored inline category rename against native metadata; original files and IDs remain immutable."""
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
names=f.project/'.confectory/resource-folder-names.v1.json'
def begin_rename(id,value,surface='card'):
 node=tree(id)if surface=='tree'else row(id);node.click(button='right');f.page.get_by_role('button',name='이름 변경',exact=True).click();input=b.locator('[data-resource-rename]');expect(input).to_be_visible();input.fill(value);return input
def renamed(id,value,surface='card',blur=False):
 input=begin_rename(id,value,surface)
 if blur:b.locator('[data-browser-control=object-query]').click()
 else:input.press('Enter')
 expect(tree(id)).to_have_attribute('title',value);f.idle()
def exact_sources():
 original();assert store.read_bytes()==file_bytes and(f.project/'.confectory/project-identity.json').read_bytes()==identity_bytes
try:
 f.start(0)
 with sync_playwright()as p:
  expect.set_options(timeout=60000);f.browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.idle();browser();folder('원래 A');a=named('원래 A')['id'];open_folder(a);folder('자식 B');child=named('자식 B')['id'];root();raw='변경하지 않는 바이트 🧪\r\n'.encode();b.locator('[data-resource-files]').set_input_files(dict(name='변경하지 않는 원본.txt',mimeType='text/plain',buffer=raw));f.idle();expect(b.locator('[data-new]')).to_be_enabled();file=named('변경하지 않는 원본.txt')['id'];file_bytes=store.read_bytes();identity_bytes=(f.project/'.confectory/project-identity.json').read_bytes();topology=layout.read_bytes();assert not names.exists()
  input=begin_rename(a,'취소할 입력');input.press('Escape');expect(b.locator('[data-resource-rename]')).to_have_count(0);assert not names.exists();expect(tree(a)).to_have_attribute('title','원래 A');exact_sources();f.checked('authored card context menu and inline Escape cancel never create name metadata or mutate original topology/file bytes')
  renamed(a,'첫 이름 <안전> 🧪');assert layout.read_bytes()==topology;assert len(json.loads(names.read_text())['items'])==1;exact_sources();f.checked('actual inline Enter publishes a literal Unicode folder name with stable IDs/parents and unchanged v1 topology/create receipts and copied file bytes')
  open_folder(a);renamed(a,'경로 이름',surface='tree',blur=True);expect(b.locator('.browser-title-path')).to_contain_text('경로 이름');expect(row(child)).to_be_visible();assert layout.read_bytes()==topology;exact_sources();root();f.checked('tree inline blur updates the open title path and all catalogue instances without changing child identities or source contracts')
  f.page.locator('#chat-input').fill('이름 변경과 별개인 입력')
  if mode=='normal':
   prior=names.read_bytes();permission=names.stat().st_mode
   try:
    names.chmod(0o444);input=begin_rename(a,'실패 입력 보존');input.press('Enter');expect(b.locator('[data-resource-layout-pending=retry]')).to_be_enabled();expect(b.locator('[data-resource-recovery]')).to_contain_text('실패 입력 보존');assert names.read_bytes()==prior
   finally:names.chmod(permission)
   b.locator('[data-resource-layout-pending=retry]').click();expect(tree(a)).to_have_attribute('title','실패 입력 보존');expect(b.locator('[data-resource-layout-pending]')).to_have_count(0);exact_sources();f.checked('real name-file write refusal retains exact submitted name/ID/revision/command; restoring only fixture permissions allows same-request retry')
   hold_reply();input=begin_rename(a,'응답 유실 이름');input.press('Enter');f.page.wait_for_function('()=>__layoutHeld');b.locator('[data-browser-control=object-query]').fill('응답 이후 새 검색');f.page.evaluate('()=>__releaseLayout()');expect(b.locator('[data-resource-layout-pending=retry]')).to_be_enabled();b.locator('[data-resource-layout-pending=retry]').click();expect(tree(a)).to_have_attribute('title','응답 유실 이름');expect(b.locator('[data-resource-layout-pending]')).to_have_count(0);expect(b.locator('[data-browser-control=object-query]')).to_have_value('응답 이후 새 검색');assert len(json.loads(names.read_text())['items'])==1;exact_sources();f.checked('lost actual committed rename reply is resolved by exact receipt replay without duplicate alias, rebase or loss of newer query')
   input=begin_rename(a,'오래된 이름 입력');basis=api('load');api('rename-folder',revision=basis['revision'],command=uuid.uuid4().hex,id=a,name='동시 저장 이름');input.press('Enter');expect(b.locator('[data-resource-layout-pending=retry]')).to_be_enabled();peer=names.read_bytes();b.locator('[data-resource-reload]').click();f.idle();b.locator('[data-resource-layout-pending=retry]').click();expect(b.locator('[data-resource-layout-pending=retry]')).to_be_enabled();assert names.read_bytes()==peer;b.locator('[data-resource-layout-pending=cancel]').click();expect(b.locator('[data-resource-layout-pending]')).to_have_count(0);expect(tree(a)).to_have_attribute('title','동시 저장 이름');exact_sources();f.checked('peer rename after inline basis capture is rejected through refresh/retry; input-only cancel preserves peer name and current metadata')
   input=begin_rename(a,'이전 취소');input.evaluate('el=>globalThis.__oldRenameKey=el.onkeydown');input.press('Escape');input=begin_rename(a,'새 미확정 이름');f.page.evaluate('()=>__oldRenameKey(new KeyboardEvent("keydown",{key:"Enter"}))');expect(input).to_have_value('새 미확정 이름');assert names.read_bytes()==peer;input.press('Escape');exact_sources();f.checked('retired inline Enter callback cannot submit or clear a newer name input')
  elif mode=='lifecycle':
   prior=names.read_bytes();input=begin_rename(a,'재시작 미확정 입력');f.pending();assert '재시작 미확정 입력'in json.dumps(f.state()['presentation'],ensure_ascii=False);restart(1);expect(b.locator('[data-resource-rename]')).to_have_value('재시작 미확정 입력');assert names.read_bytes()==prior;b.locator('[data-resource-rename]').press('Escape');expect(b.locator('[data-resource-rename]')).to_have_count(0);assert names.read_bytes()==prior;exact_sources();f.checked('real cold restart restores unconfirmed inline input and original basis without automatically saving; Escape cancels only the preserved input')
   hold_reply();input=begin_rename(a,'저장 응답 재확인');input.press('Enter');f.page.wait_for_function('()=>__layoutHeld');f.page.evaluate('()=>__releaseLayout()');expect(b.locator('[data-resource-layout-pending=retry]')).to_be_enabled();saved=names.read_bytes();f.pending();restart(2);expect(b.locator('[data-resource-layout-pending=retry]')).to_be_enabled();assert names.read_bytes()==saved;b.locator('[data-resource-layout-pending=retry]').click();expect(b.locator('[data-resource-layout-pending]')).to_have_count(0);expect(tree(a)).to_have_attribute('title','저장 응답 재확인');assert names.read_bytes()==saved;exact_sources();f.checked('cold restart restores staged rename receipt input without auto mutation; explicit same-command retry confirms current name without another write')
   other=f.case/'same namespace other project';shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory','.build'));restart(3,other);assert api('load')['items']==[];expect(b.locator('[data-resource-rename],[data-resource-layout-pending]')).to_have_count(0);assert names.read_bytes()==saved;restart(4,f.project);expect(tree(a)).to_have_attribute('title','저장 응답 재확인');assert names.read_bytes()==saved;exact_sources();f.checked('same-namespace project cannot adopt another project folder names or pending inputs; returning restores only its owned state')
  else:raise AssertionError(mode)
  assert layout.read_bytes()==topology;exact_sources();f.pending();expect(f.page.locator('#chat-input')).to_have_value('이름 변경과 별개인 입력');f.page.screenshot(path=str(f.case/('folder-renames-'+mode+'.png')));f.browser.close()
except Exception as error:
 (f.case/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:
 f.stop();(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2))
print('RESOURCE_FOLDER_RENAMES_UI_FIXTURE',f.case,flush=True)
