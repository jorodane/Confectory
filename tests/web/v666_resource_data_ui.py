"""Authored resource Data controls on actual native-owned metadata; generated assets only."""
import sys,json,pathlib,hashlib,base64,uuid,traceback,shutil
from playwright.sync_api import sync_playwright,expect
import v536_wide_mixed as f
mode=sys.argv[3];source=None

def api(action='load',**kw):return f.invoke('projectResourceLayout',dict(project=f.state()['projectId'],action=action,**kw))['result']['result']
def add(name,mime,raw):
 revision=f.invoke('projectResources',dict(project=f.state()['projectId'],action='load'))['result']['result']['revision'];id=uuid.uuid4().hex
 f.invoke('projectResources',dict(project=f.state()['projectId'],action='import',revision=revision,command=uuid.uuid4().hex,item=dict(id=id,name=name,type=mime,size=len(raw),hash=hashlib.sha256(raw).hexdigest(),data=base64.urlsafe_b64encode(raw).decode(),modifiedAt=0)));return id

def category(name,parent=None):
 id=uuid.uuid4().hex;api('create-folder',revision=api()['revision'],command=uuid.uuid4().hex,id=id,name=name,parent=parent);return id

def win(key):return f.page.locator('.window[data-key="'+key+'"]')
def focus(w):
 f.page.locator('#worker-finder-bubble').click();panel=f.page.locator('#workspace-find-panel');expect(panel).to_be_visible();panel.locator('[data-find-mode=elements]').click();panel.get_by_role('searchbox').fill('');panel.locator('[data-find-key="node:'+w.get_attribute('data-key')+'"]').click();expect(panel).to_have_count(0);f.idle()
def window_menu(w):
 title=w.locator(':scope > .window-title');position=title.evaluate("""node=>{const b=node.getBoundingClientRect();for(let y=3;y<b.height;y+=4)for(let x=5;x<b.width-5;x+=7){const el=document.elementFromPoint(b.left+x,b.top+y);if(el&&node.contains(el)&&!el.closest('button,input,select,textarea,.browser-title-path'))return{x,y};}throw Error('window title has no free menu point');}""");title.click(button='right',position=position)
def browser():
 f.page.locator('#workspace').click(button='right',position=dict(x=700,y=260));f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]').last;b.locator('[data-tab=resource]').click();expect(b.locator('[data-new]')).to_be_enabled();return b

def files():return{str(p.relative_to(f.project)):p.read_bytes()for p in(f.project/'.confectory').rglob('*')if p.is_file()and('resource'in str(p)or p.name=='project-identity.json')}
def original():
 for n,raw in f.original.items():assert(f.project/n).read_bytes()==raw,n
 assert not f.errors and not f.external,(f.errors,f.external)
def metadata(key):
 f.pending()
 def find(v):
  if isinstance(v,dict):
   if v.get('key')==key and isinstance(v.get('meta'),dict):return v['meta']
   for x in v.values():
    result=find(x)
    if result is not None:return result
  if isinstance(v,list):
   for x in v:
    result=find(x)
    if result is not None:return result
 return find(f.state()['presentation'])
def choose(value,w=None):
 w=w or source;w.locator('[data-resource-type-filter]').click();labels={'all':'모든 자료','document':'문서','image':'그림','mesh':'메시','file':'기타 파일'};f.page.locator('.context-menu button').filter(has_text=labels[value]).click();expect(w.locator('[data-resource-type-filter]')).to_have_attribute('aria-pressed',str(value!='all').lower());assert metadata(w.get_attribute('data-key')).get('resourceFilter')==value

def visible(w=None):return set((w or source).locator('[data-resource-id]').evaluate_all('(xs)=>xs.map(x=>x.dataset.resourceId)'))
def restart(i,project=None,restore_key=None):
 global source
 key=restore_key or source.get_attribute('data-key');f.pending();f.page.close();f.stop()
 if project:f.env['CONFECTORY_WEB_PROJECT']=str(project/'project.cproj')
 f.start(i);f.page=f.setup();f.idle();source=win(key)
 if not source.count():source=browser()
 else:expect(source.locator('[data-resource-status]')).to_be_visible();f.idle()

def name(id):return source.locator('[data-resource-name="'+id+'"]')
def prop(id,key):return source.locator('[data-resource-id="'+id+'"] [data-resource-property="'+key+'"]')
def open_button(id):return source.locator('[data-resource-open="'+id+'"]')
def inline(id,value):
 source.locator('[data-resource-id="'+id+'"] .obj-icon').click();name(id).click();field=source.locator('[data-resource-rename]');expect(field).to_be_visible();field.fill(value);return field
def pointer(locator):
 locator.scroll_into_view_if_needed();box=locator.bounding_box();assert box;f.page.mouse.click(box['x']+box['width']/2,box['y']+box['height']/2)
def wait_no_rename():f.page.wait_for_timeout(350);expect(source.locator('[data-resource-rename]')).to_have_count(0)
try:
 f.start(0)
 with sync_playwright()as p:
  expect.set_options(timeout=60000);f.browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.idle()
  folder=category('카테고리 🧪');child=category('하위 카테고리',folder);a=add('자료 문서2.txt','text/plain','원래 자료2 🧪\r\n'.encode());b=add('자료 문서10.md','text/markdown',b'original document 10');binary=add('자료 기타.bin','application/octet-stream',b'original binary\x00\xff');source=browser();key=source.get_attribute('data-key');source.locator('[data-density="100"]').click();expect(source.locator('[data-resource-id]')).to_have_count(4);before=files()
  if mode=='baseline':
   expect(source.locator('.browser-data-identity,.browser-data-fields,[data-resource-name],[data-resource-open],[data-resource-property]')).to_have_count(0);expect(source.locator('[data-resource-description]')).to_have_count(4);assert {x['id']for x in api()['items']}=={folder,child,a,b,binary};f.checked('published eda49871 Data rows omit authored identity/name button, kind/size fields and explicit open despite ready native metadata and existing CSS')
  elif mode=='normal':
   expect(source.locator('.browser-data-identity')).to_have_count(4);expect(source.locator('.browser-data-fields')).to_have_count(4);expect(source.locator('[data-resource-open]')).to_have_count(4)
   current=api();names={x['id']:x['name']for x in current['items']};kinds={'folder':'카테고리','document':'문서','file':'파일'}
   for item in current['items']:
    if item['id']==child:continue
    expect(prop(item['id'],'kind')).to_have_value(kinds[item['kind']]);expect(prop(item['id'],'kind')).to_have_attribute('readonly','');expect(prop(item['id'],'size')).to_have_value('—'if item['kind']=='folder'else str(item['size'])+' B');expect(prop(item['id'],'size')).to_have_attribute('readonly','');expect(name(item['id'])).to_have_attribute('title',item['name'])
   f.checked('authored Data identity, readonly native kind/size, editable description and explicit open exist for file/folder with exact Unicode names and no fabricated metadata')
   name(a).click();expect(source.locator('[data-resource-id="'+a+'"]')).to_have_attribute('aria-selected','true');wait_no_rename();assert files()==before;name(b).click(modifiers=['Control']);wait_no_rename();assert set(metadata(key)['resourceSelections'])=={a,b};name(a).click();wait_no_rename();name(a).click();field=source.locator('[data-resource-rename]');expect(field).to_be_visible();field.fill('자료 이름 <보존> 🧪.txt');field.press('Escape');wait_no_rename();assert files()==before;f.checked('first name click selects; a later selected-name click opens existing inline editor; explicit Escape discards only that draft')
   field=inline(a,'저장한 문서 이름 🧪.txt');field.press('Enter');expect(name(a)).to_have_attribute('title','저장한 문서 이름 🧪.txt');f.idle();item=next(x for x in api()['items']if x['id']==a);assert item['hash']==hashlib.sha256('원래 자료2 🧪\r\n'.encode()).hexdigest();before=files();f.checked('selected Data name uses existing atomic alias Save and preserves ID/hash/source bytes')
   source.locator('[data-resource-id="'+a+'"] .obj-icon').click();chosen=metadata(key)['resourceSelections'];prop(b,'kind').click();prop(b,'size').dblclick();assert metadata(key)['resourceSelections']==chosen;expect(f.page.locator('.window[data-key="resource-file:'+b+'"]')).to_have_count(0);assert files()==before
   data=f.page.evaluate("""id=>{const input=document.querySelector('[data-resource-id="'+id+'"] [data-resource-property="kind"]'),dt=new DataTransfer(),e=new DragEvent('dragstart',{bubbles:true,cancelable:true,dataTransfer:dt});input.dispatchEvent(e);return{prevented:e.defaultPrevented,types:[...dt.types]}}""",b);assert data==dict(prevented=True,types=[]);f.checked('readonly metadata keeps native text interaction without selecting/opening a row or emitting a resource drag payload')
   open_button(b).click();view=f.page.locator('.window[data-key="resource-file:'+b+'"]');expect(view.locator('.resource-document-text')).to_have_text('original document 10');assert metadata(key)['resourceSelections']==chosen;focus(source);assert files()==before;open_button(folder).click();expect(source.locator('[data-resource-id="'+child+'"]')).to_be_visible();assert metadata(key)['resourceFolder']==folder;source.locator('[data-root]').click();f.checked('explicit per-item open reads the actual owned document without altering selection, and folder open enters its actual category')
   name(a).dblclick();expect(f.page.locator('.window[data-key="resource-file:'+a+'"] .resource-document-text')).to_have_text('원래 자료2 🧪');focus(source);wait_no_rename();assert files()==before;f.checked('name double-click opens the actual document and cancels the delayed rename')
   field=inline(a,'cold 보관 이름 입력.txt');f.pending();restart(1);expect(source.locator('[data-resource-rename]')).to_have_value('cold 보관 이름 입력.txt');source.locator('[data-resource-rename]').press('Escape');f.idle();expect(name(a)).to_have_attribute('title','저장한 문서 이름 🧪.txt');expect(prop(a,'kind')).to_have_value('문서');assert files()==before;f.checked('real cold Data restore preserves unsubmitted inline name, then input-only cancel restores current native alias and readonly metadata')
  elif mode=='lifecycle':
   source.locator('[data-resource-id="'+a+'"] .obj-icon').click();name(a).click();source.locator('[data-browser-control=object-query]').fill('later input');wait_no_rename();source.locator('[data-browser-control=object-query]').fill('');source.locator('[data-resource-id="'+a+'"] .obj-icon').click();name(a).click();f.page.keyboard.press('Escape');wait_no_rename();assert files()==before;f.checked('new search input and Escape permanently cancel a pending selected-name activation')
   source.locator('[data-resource-id="'+a+'"] .obj-icon').click();name(a).click();desc=source.locator('[data-resource-description="'+b+'"]');desc.fill('편집 중인 설명 🧪');wait_no_rename();pointer(open_button(a));expect(desc).to_be_focused();pointer(name(a));expect(desc).to_be_focused();pointer(prop(a,'kind'));expect(desc).to_be_focused();assert files()==before and not metadata(key)['resourceDescriptionDraft'].get('pending');f.pending();restart(1);desc=source.locator('[data-resource-description="'+b+'"]');expect(desc).to_have_value('편집 중인 설명 🧪');expect(prop(b,'kind')).to_have_value('문서');assert files()==before;desc.press('Escape');f.idle();f.checked('new description input cancels pending rename; new Data controls cannot blur/submit that draft; cold retains the exact input and metadata')
   field=inline(a,'기준 이름.txt');field.press('Enter');expect(name(a)).to_have_attribute('title','기준 이름.txt');f.idle();before=files();path=f.project/'.confectory/resource-file-names.v1.json';permissions=path.stat().st_mode
   try:
    path.chmod(0o444);field=inline(a,'실패한 Data 이름.txt');field.press('Enter');expect(source.locator('[data-resource-layout-pending=retry]')).to_be_enabled();pending=metadata(key)['resourceLayoutPending'];pointer(open_button(b));pointer(name(b));wait_no_rename();assert metadata(key)['resourceLayoutPending']==pending and files()==before
   finally:path.chmod(permissions)
   restart(2);assert metadata(key)['resourceLayoutPending']==pending and files()==before;source.locator('[data-resource-layout-pending=retry]').click();f.idle();expect(name(a)).to_have_attribute('title','실패한 Data 이름.txt');assert not metadata(key).get('resourceLayoutPending');before=files();f.checked('actual readonly alias Save denial fences Data name/open, preserves exact pending request across cold, then explicit same-command retry saves once')
   field=inline(a,'오래된 Data 이름.txt');current=api();api('rename-file',revision=current['revision'],command=uuid.uuid4().hex,id=a,name='먼저 저장한 동료.txt');before=files();field.press('Enter');expect(source.locator('[data-resource-layout-pending=retry]')).to_be_enabled();pending=metadata(key)['resourceLayoutPending'];restart(3);assert metadata(key)['resourceLayoutPending']==pending;source.locator('[data-resource-layout-pending=retry]').click();f.idle();expect(source.locator('[data-resource-layout-pending=retry]')).to_be_enabled();assert files()==before;source.locator('[data-resource-layout-pending=cancel]').click();f.idle();expect(name(a)).to_have_attribute('title','먼저 저장한 동료.txt');assert files()==before;f.checked('peer native alias CAS conflict keeps original input/basis through cold/retry; input-only cancel shows peer alias without writes')
   name(a).evaluate('el=>globalThis.__oldDataName=el.onclick');closed=key;source.locator('[data-close]').first.click();f.page.evaluate('()=>__oldDataName({stopPropagation(){},detail:1})');assert not metadata(closed).get('resourceRenameInput');source=browser();key=source.get_attribute('data-key');source.locator('[data-density="100"]').click();f.page.evaluate('()=>__oldDataName({stopPropagation(){},detail:1})');wait_no_rename();assert files()==before;f.checked('held name handler after close cannot reopen hidden or newly created window input')
  else:raise AssertionError(mode)
  original();assert files()==before;f.pending();f.page.screenshot(path=str(f.case/('resource-data-'+mode+'.png')));f.browser.close()
except Exception as error:
 try:f.page.screenshot(path=str(f.case/'failure.png'));(f.case/'failure.html').write_text(f.page.content())
 except Exception:pass
 (f.case/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:
 f.stop();(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2))
print('RESOURCE_DATA_UI',f.case,flush=True)
