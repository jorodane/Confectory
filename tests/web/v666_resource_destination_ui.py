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
def payloads(names,raw=None):return[dict(name=name,mimeType='text/plain',buffer=raw if raw is not None else ('generated '+name+'\r\n').encode())for name in names]
def menu():
 # Complete setup input blur/private state before requesting a native chooser.
 f.page.evaluate('()=>document.activeElement?.blur()');f.pending();f.idle();expect(b.locator('[data-new]')).to_be_enabled();b.locator('[data-new]').click()
 with f.page.expect_file_chooser()as chooser:f.page.locator('.context-menu').get_by_role('button',name='자료 추가',exact=True).click()
 return chooser.value
def choose(names,raw=None):menu().set_files(payloads(names,raw))
def files():return[row for row in api('load')['items']if row['kind']!='folder']
def pending():expect(b.locator('[data-resource-pending=retry]')).to_be_enabled()
def done(count):expect(b.locator('[data-resource-pending]')).to_have_count(0);expect(b.locator('[data-new]')).to_be_enabled();f.idle();assert len(files())==count

def hold_file(name):
 f.page.evaluate("""name=>{const original=File.prototype.arrayBuffer;globalThis.__destinationFileHeld=false;File.prototype.arrayBuffer=async function(){const bytes=await original.call(this);if(this.name!==name)return bytes;globalThis.__destinationFileHeld=true;return new Promise(resolve=>{globalThis.__releaseDestinationFile=()=>{File.prototype.arrayBuffer=original;resolve(bytes);};});};}""",name)
def drop(target,names):
 target.evaluate(r"""(el,names)=>{const d=new DataTransfer();for(const name of names)d.items.add(new File(['generated '+name+'\r\n'],name,{type:'text/plain'}));el.dispatchEvent(new DragEvent('drop',{dataTransfer:d,bubbles:true,cancelable:true}));}""",names)
try:
 f.start(0)
 with sync_playwright()as p:
  expect.set_options(timeout=60000);f.browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.idle();browser();folder('A');a=named('A')['id'];open_folder(a);folder('중첩 B');child=named('중첩 B')['id'];root();folder('C');c=named('C')['id'];open_folder(a);open_folder(child);assert not store.exists();f.page.locator('#chat-input').fill('목적지와 별개인 입력');choose(['first one.txt','first two.txt']);done(2);assert all(row['parent']==child for row in files());assert len(api('load')['items'])==5
  first=files()[0];row(first['id']).press('Enter');viewer=f.page.locator('.window[data-key="resource-file:'+first['id']+'"]');expect(viewer.locator('.resource-document-text')).to_have_text('generated '+first['name']+'\r\n');viewer.locator('[data-close]').first.click();original();f.checked('actual authored Add menu inside a nested category creates the first real resource store and both initial placements atomically; unchanged preview reads exact bytes')
  if mode=='normal':
   row(first['id']).click();drop(tree(c),['drop one.txt','drop two.txt']);done(4);assert all(row['parent']==c for row in files()if row['name'].startswith('drop '));expect(row(first['id'])).to_have_attribute('aria-selected','true');expect(b.locator('.browser-title-path')).to_contain_text('중첩 B');original();f.checked('generated external File drop on another folder tree binds that explicit target without importing to the open folder or clearing its current selection')
   before=store.read_bytes();topology=layout.read_bytes();permission=layout.stat().st_mode
   try:layout.chmod(0o444);choose(['failed one.txt','failed two.txt']);pending();assert store.read_bytes()==before and layout.read_bytes()==topology;expect(b.locator('[data-resource-recovery]')).to_contain_text('중첩 B')
   finally:layout.chmod(permission)
   b.locator('[data-resource-pending=retry]').click();done(6);assert all(row['parent']==child for row in files()if row['name'].startswith('failed '));original();f.checked('actual second destination-file write refusal rolls back the first resource write; selected files/target remain for exact retry')
   hold_reply();choose(['lost one.txt','lost two.txt']);f.page.wait_for_function('()=>__layoutHeld');assert len(files())==8;b.locator('[data-browser-control=object-query]').fill('늦은 새 검색');f.page.evaluate('()=>__releaseLayout()');pending();b.locator('[data-resource-pending=retry]').click();done(8);expect(b.locator('[data-browser-control=object-query]')).to_have_value('늦은 새 검색');assert all(row['parent']==child for row in files()if row['name'].startswith('lost '));original();f.checked('lost actual committed reply replays both original import receipts and placement without duplicates, retargeting or losing newer query input')
   root();folder('D');d=named('D')['id'];open_folder(d);chooser=menu();current=named('D');value=api('load');api('delete-folder',revision=value['revision'],command=uuid.uuid4().hex,id=d,hash=current['hash']);before=store.read_bytes();topology=layout.read_bytes();chooser.set_files(payloads(['never root one.txt','never root two.txt']));pending();assert store.read_bytes()==before and layout.read_bytes()==topology;expect(b.locator('[data-resource-recovery]')).to_contain_text('D');b.locator('[data-resource-reload]').click();f.idle();b.locator('[data-resource-pending=retry]').click();pending();assert store.read_bytes()==before;b.locator('[data-resource-pending=cancel]').click();expect(b.locator('[data-resource-pending]')).to_have_count(0);original();f.checked('destination removed while an actual chooser is open never falls back to ProjectPack; refresh/retry retains the original failed intent until input-only cancellation')
   root();open_folder(a);open_folder(child);choose(['maximum one.txt','maximum two.txt'],bytes([251])*524288);done(10);assert all(row['parent']is not None for row in files());original();f.checked('aggregate 1MiB File group crosses the actual destination API/IPC and stores both full copies with no transient root entries')
   f.invoke('projectResources',dict(action='prepare-import-many',project=f.state()['projectId'],revision='missing',imports=[]),False);before=store.read_bytes();api('import-files',False,revision=api('load')['revision'],resourceRevision='missing',command=uuid.uuid4().hex,parent=child,imports=[],plan={'writes':[]});assert store.read_bytes()==before;original();f.checked('editor rejects internal preparation and client-supplied generic plans; no new arbitrary write capability is exposed')
  elif mode=='lifecycle':
   hold_file('navigation two.txt');choose(['navigation one.txt','navigation two.txt']);f.page.wait_for_function('()=>__destinationFileHeld');assert len(files())==2;root();f.page.evaluate('()=>__releaseDestinationFile()');done(4);assert all(row['parent']==child for row in files());expect(b.locator('.browser-title-path')).not_to_contain_text('중첩 B');expect(b.locator('[data-resource-id]')).to_have_count(2);original();f.checked('navigation during later File read preserves the originally selected destination and never selects hidden imported IDs in the new surface')
   open_folder(a);open_folder(child);hold_file('Home two.txt');choose(['Home one.txt','Home two.txt']);f.page.wait_for_function('()=>__destinationFileHeld');f.pending();listing=f.state()['listingId'];f.page.locator('#title').click();f.page.get_by_role('button',name='프로젝트 나가기',exact=True).click();expect(f.page.locator('.home-grid')).to_be_visible();f.page.evaluate('()=>__releaseDestinationFile()');f.page.locator('[data-enter="'+listing+'"]').click();f.idle();b=f.page.locator('.window[data-key^="browser:project:"]').last;pending();assert len(files())==4;expect(b.locator('[data-resource-recovery]')).to_contain_text('중첩 B');b.locator('[data-resource-pending=retry]').click();done(6);assert all(row['parent']==child for row in files());original();f.checked('Home retires a pending File read; same-owner return requires explicit retry of the original files, folder and basis')
   permission=layout.stat().st_mode
   try:layout.chmod(0o444);choose(['cold one.txt','cold two.txt']);pending();f.pending();assert 'cold one.txt'not in json.dumps(f.state()['presentation'])
   finally:layout.chmod(permission)
   before=store.read_bytes();topology=layout.read_bytes();restart(1);expect(b.locator('[data-resource-pending]')).to_have_count(0);assert store.read_bytes()==before and layout.read_bytes()==topology and len(files())==6;original();f.checked('cold engine restores only confirmed nested files and private navigation; unfinished File bytes/commands are not persisted or replayed')
   other=f.case/'same namespace another project';shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory','.build'));restart(2,other);assert api('load')['items']==[];folder('B owned');owned=named('B owned')['id'];open_folder(owned);choose(['B private.txt']);done(1);assert files()[0]['parent']==owned;restart(3,f.project);assert len(files())==6 and all(row['parent']==child for row in files());assert not any(row['name']=='B private.txt'for row in files());original();f.checked('real project roundtrip never transfers foreign folder IDs, selected bytes or pending targets despite the same namespace')
  else:raise AssertionError(mode)
  expect(f.page.locator('#chat-input')).to_have_value('목적지와 별개인 입력');original();f.pending();f.page.screenshot(path=str(f.case/('destination-'+mode+'.png')));f.browser.close()
except Exception as error:
 try:f.page.screenshot(path=str(f.case/'failure.png'))
 except Exception:pass
 (f.case/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:
 f.stop();(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2))
print('RESOURCE_DESTINATION_FIXTURE',f.case,flush=True)
