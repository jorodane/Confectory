"""Authored category form/tree/drag against real owned native metadata; generated assets only."""
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
try:
 f.start(0)
 with sync_playwright()as p:
  expect.set_options(timeout=60000);f.browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.idle();browser();f.page.evaluate("""()=>{globalThis.__resourceDragEvents=[];for(const type of ['dragstart','dragover','drop','dragend'])document.addEventListener(type,event=>{const row={type,target:event.target.outerHTML?.slice(0,240),busy:document.querySelector('.brand').disabled};setTimeout(()=>{row.prevented=event.defaultPrevented;row.types=Array.from(event.dataTransfer?.types||[]);row.effect=event.dataTransfer?.effectAllowed;__resourceDragEvents.push(row)});},true);}""");assert not layout.exists();folder('취소할 카테고리',True);assert not layout.exists();folder('작업 <A>');a=named('작업 <A>')['id'];open_folder(a);folder('중첩 B');child=named('중첩 B')['id'];expect(tree(child)).to_have_count(1);root();f.checked('authored plus/name Confirm creates stable owned categories, Cancel creates nothing, and nested tree/title paths navigate actual stored parents')
  raw='자료의 원래 바이트 🧪\r\n<script>mustNotExecute()</script>'.encode();b.locator('[data-resource-files]').set_input_files(dict(name='생성한 원본.txt',mimeType='text/plain',buffer=raw));expect(b.locator('[data-new]')).to_be_enabled();f.idle();file=named('생성한 원본.txt')['id'];before=store.read_bytes();identity=(f.project/'.confectory/project-identity.json').read_bytes();f.page.locator('#chat-input').fill('이동과 별개인 새 입력');expect(row(file)).to_be_visible();expect(b.locator('[data-new]')).to_be_enabled();f.idle()
  row(file).drag_to(row(a));f.idle();moved(file,a);open_folder(a);expect(row(file)).to_be_visible();row(file).press('Enter');viewer=f.page.locator('.window[data-key="resource-file:'+file+'"]');expect(viewer.locator('.resource-document-text')).to_have_text(raw.decode());viewer.locator('[data-close]').first.click();row(file).drag_to(b.locator('[data-root]'));f.idle();moved(file,None);root();expect(row(file)).to_be_visible();assert store.read_bytes()==before;expect(f.page.locator('#chat-input')).to_have_value('이동과 별개인 새 입력');original();f.checked('actual internal drag into folder and back to ProjectPack changes parent metadata only; existing resource preview still reads the same ID/hash/original bytes and preserves unrelated input')
  open_folder(a);row(child).drag_to(b.locator('[data-root]'));f.idle();moved(child,None);root();row(a).drag_to(row(child));f.idle();moved(a,child);open_folder(child);prior=layout.read_bytes();row(a).drag_to(tree(a));f.idle();assert layout.read_bytes()==prior;root();original();f.checked('folder drag preserves child topology; attempted self drop is refused without storage changes or implicit default destination')
  if mode=='normal':
   # Permission failure retains submitted name and exact command, not raw asset bytes.
   permission=layout.stat().st_mode
   try:
    layout.chmod(0o444);folder('쓰기 실패 입력');expect(b.locator('[data-resource-layout-pending=retry]')).to_be_enabled();expect(b.locator('[data-resource-recovery]')).to_contain_text('쓰기 실패 입력');assert layout.read_bytes()==prior
   finally:layout.chmod(permission)
   b.locator('[data-resource-layout-pending=retry]').click();expect(b.locator('[data-resource-layout-pending=retry]')).to_have_count(0);f.idle();assert named('쓰기 실패 입력');original();f.checked('real native metadata write refusal preserves exact name/command and prior topology; explicit retry after fixture permission recovery saves once')
   hold_reply();folder('응답 유실',wait=False);f.page.wait_for_function('()=>__layoutHeld');count=len(api('load')['items']);b.locator('[data-browser-control=object-query]').fill('늦게 입력한 검색');f.page.evaluate('()=>__releaseLayout()');expect(b.locator('[data-resource-layout-pending=retry]')).to_be_enabled();b.locator('[data-resource-layout-pending=retry]').click();expect(b.locator('[data-resource-layout-pending=retry]')).to_have_count(0);assert len(api('load')['items'])==count;expect(b.locator('[data-browser-control=object-query]')).to_have_value('늦게 입력한 검색');f.checked('lost actual committed reply is resolved by exact receipt replay without duplicate category or replacement of newer query')
   # Race native catalogue, then submit UI intent based on its old displayed basis.
   b.locator('[data-new]').click();f.page.get_by_role('button',name='새 카테고리',exact=True).click();form=f.page.locator('.resource-name-form');form.locator('[name=name]').fill('오래된 입력');value=api('load');api('create-folder',revision=value['revision'],command=uuid.uuid4().hex,id=uuid.uuid4().hex,name='동시 저장',parent=None);form.get_by_role('button',name='확인',exact=True).click();f.idle();expect(b.locator('[data-resource-layout-pending=retry]')).to_be_enabled();count=len(api('load')['items']);b.locator('[data-resource-reload]').click();f.idle();b.locator('[data-resource-layout-pending=retry]').click();expect(b.locator('[data-resource-layout-pending=retry]')).to_be_enabled();assert len(api('load')['items'])==count;expect(b.locator('[data-resource-layout-pending=retry]')).to_have_count(1);b.locator('[data-resource-layout-pending=cancel]').click();expect(b.locator('[data-resource-layout-pending]')).to_have_count(0);original();f.checked('peer change before Confirm is rejected by exact basis; refresh/retry never rebases, recovery controls do not duplicate, explicit input cancel preserves peer category')
   # Forged external MIME and detached callbacks cannot move anything.
   root();row(file).evaluate('el=>globalThis.__retiredDrop=el.ondragstart');b.locator('[data-browser-control=object-query]').fill('없는 자료');b.locator('[data-browser-control=object-search]').click();prior=layout.read_bytes();f.page.evaluate('()=>{const d=new DataTransfer();d.setData("application/x-confectory-resource",JSON.stringify({projectId:"foreign",ids:[],nonce:"forged"}));document.querySelector("[data-root]").dispatchEvent(new DragEvent("drop",{dataTransfer:d,bubbles:true}));}');assert layout.read_bytes()==prior;original();f.checked('untrusted drag payload cannot impersonate current local drag ownership or mutate project metadata')
  elif mode=='lifecycle':
   hold_reply();folder('재시작 전 입력',wait=False);f.page.wait_for_function('()=>__layoutHeld');f.page.evaluate('()=>__releaseLayout()');expect(b.locator('[data-resource-layout-pending=retry]')).to_be_enabled();count=len(api('load')['items']);f.pending();pending=[w for w in f.state()['presentation'].get('windows',[])if False] if False else json.dumps(f.state()['presentation'],ensure_ascii=False);assert '재시작 전 입력'in pending and base64.urlsafe_b64encode(raw).decode()not in pending
   restart(1);expect(b.locator('[data-resource-layout-pending=retry]')).to_be_enabled();assert len(api('load')['items'])==count;b.locator('[data-resource-layout-pending=retry]').click();expect(b.locator('[data-resource-layout-pending=retry]')).to_have_count(0);assert len(api('load')['items'])==count;root();expect(row(file)).to_be_visible();assert store.read_bytes()==before;original();f.checked('cold engine restores category hierarchy and only private pending metadata; no auto mutation; explicit exact retry confirms saved identity once')
   listing=f.state()['listingId'];f.page.locator('#title').click();f.page.get_by_role('button',name='프로젝트 나가기',exact=True).click();expect(f.page.locator('.home-grid')).to_be_visible();f.page.locator('[data-enter="'+listing+'"]').click();f.idle();b=f.page.locator('.window[data-key^="browser:project:"]').last;expect(row(file)).to_be_visible();assert store.read_bytes()==before;original();f.checked('actual Home/project round trip restores only active project hierarchy and original resource identities')
   other=f.case/'same namespace other project';shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory','.build'));restart(2,other);assert api('load')['items']==[];expect(rows()).to_have_count(0);assert store.read_bytes()==before;restart(3,f.project);root();expect(row(file)).to_be_visible();original();f.checked('same namespace in another project cannot adopt resource folders/files; return restores original owned metadata')
  else:raise AssertionError(mode)
  assert store.read_bytes()==before and(f.project/'.confectory/project-identity.json').read_bytes()==identity;original();f.pending();f.page.screenshot(path=str(f.case/('resource-layout-'+mode+'.png')));f.browser.close()
except Exception as e:
 try:f.page.screenshot(path=str(f.case/'failure.png'));(f.case/'failure.html').write_text(f.page.content())
 except Exception:pass
 (f.case/'failure.json').write_text(json.dumps(dict(error=repr(e),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:
 f.stop();(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2))
print('RESOURCE_LAYOUT_UI_FIXTURE',f.case,flush=True)
