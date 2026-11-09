"""Authored filename activation in Compact/Preview with unchanged Data path; generated assets only."""
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

def name(id):return source.locator('[data-resource-id="'+id+'"] .name')
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
  folder=category('카테고리 🧪');child=category('하위 카테고리',folder);a=add('선택 이름2.txt','text/plain','파일명과 독립인 원문 🧪\r\n'.encode());b=add('선택 이름10.md','text/markdown',b'original 10');source=browser();key=source.get_attribute('data-key');before=files();expect(source.locator('[data-resource-id]')).to_have_count(3)
  if mode=='baseline':
   for density in [0,40]:
    source.locator('[data-density="'+str(density)+'"]').click();name(a).click();name(a).click();wait_no_rename();expect(source.locator('[data-resource-name]')).to_have_count(0);assert files()==before
   source.locator('[data-resource-id="'+a+'"] .obj-icon').click();source.locator('[data-resource-id="'+a+'"]').press('F2');expect(source.locator('[data-resource-rename]')).to_be_visible();source.locator('[data-resource-rename]').press('Escape');assert files()==before;f.checked('published cd60e4a3 Compact/Preview captions lack authored selected-name activation while native/F2 alias editing already works')
  elif mode=='normal':
   for density in [0,40,100]:
    source.locator('[data-density="'+str(density)+'"]').click();expect(name(a)).to_have_attribute('data-resource-name',a);expect(name(a)).to_have_attribute('tabindex','0');source.locator('[data-resource-id="'+b+'"] .obj-icon').click();name(a).click();wait_no_rename();assert metadata(key)['resourceSelections']==[a];name(b).click(modifiers=['Control']);wait_no_rename();assert set(metadata(key)['resourceSelections'])=={a,b};name(a).click();wait_no_rename();name(a).click();field=source.locator('[data-resource-rename]');expect(field).to_be_visible();field.fill('취소할 표시 이름 🧪.txt');field.press('Escape');assert files()==before
    value='저장 이름 '+str(density)+' 🧪.txt';field=inline(a,value);field.press('Enter');expect(name(a)).to_have_attribute('title',value);f.idle();assert next(x for x in api()['items']if x['id']==a)['hash']==hashlib.sha256('파일명과 독립인 원문 🧪\r\n'.encode()).hexdigest();before=files()
    if density!=100:
     name(a).press('F2');expect(source.locator('[data-resource-rename]')).to_be_visible();source.locator('[data-resource-rename]').press('Escape');name(a).press('Enter');expect(f.page.locator('.window[data-key="resource-file:'+a+'"] .resource-document-text')).to_have_text('파일명과 독립인 원문 🧪');focus(source);assert files()==before
    name(folder).dblclick();expect(source.locator('[data-resource-id="'+child+'"]')).to_be_visible();wait_no_rename();source.locator('[data-root]').click();assert files()==before
   f.checked('Compact/Preview/Data share authored first-select, modifier selection, delayed name edit/cancel, native alias Save and folder double-click; non-Data caption F2/Enter preserve keyboard flow and source bytes')
   source.locator('[data-density="40"]').click();field=inline(a,'cold 미확정 파일명.txt');f.pending();restart(1);expect(source.locator('[data-resource-rename]')).to_have_value('cold 미확정 파일명.txt');source.locator('[data-resource-rename]').press('Escape');f.idle();expect(name(a)).to_have_attribute('title','저장 이름 100 🧪.txt');assert files()==before;f.checked('Preview cold restore retains the existing unsubmitted card-surface name/revision; input-only cancel leaves native alias unchanged')
  elif mode=='lifecycle':
   source.locator('[data-density="40"]').click();source.locator('[data-resource-id="'+a+'"] .obj-icon').click();name(a).click();source.locator('[data-browser-control=object-query]').fill('later search');wait_no_rename();source.locator('[data-browser-control=object-query]').fill('');source.locator('[data-resource-id="'+a+'"] .obj-icon').click();name(a).click();f.page.keyboard.press('Escape');wait_no_rename();assert files()==before
   source.locator('[data-resource-id="'+a+'"] .obj-icon').click();name(a).click();source.locator('[data-density="0"]').click();wait_no_rename();source.locator('[data-resource-id="'+a+'"] .obj-icon').click();name(a).click();choose('file');wait_no_rename();choose('all');assert files()==before;f.checked('new input, Escape, density remount and kind change invalidate old non-Data name activation without writes')
   source.locator('[data-resource-id="'+a+'"] .obj-icon').click();name(a).click();name(a).click(button='right');expect(f.page.locator('.context-menu')).to_be_visible();wait_no_rename();f.page.keyboard.press('Escape');assert files()==before;f.checked('opening the existing context menu retires the delayed caption edit; it does not open behind the menu')
   field=inline(a,'기준 파일명.txt');field.press('Enter');expect(name(a)).to_have_attribute('title','기준 파일명.txt');f.idle();before=files();path=f.project/'.confectory/resource-file-names.v1.json';permissions=path.stat().st_mode
   try:
    path.chmod(0o444);field=inline(a,'Compact 실패 입력.txt');field.press('Enter');expect(source.locator('[data-resource-layout-pending=retry]')).to_be_enabled();pending=metadata(key)['resourceLayoutPending'];pointer(name(b));wait_no_rename();assert metadata(key)['resourceLayoutPending']==pending and files()==before
   finally:path.chmod(permissions)
   restart(1);assert metadata(key)['resourceLayoutPending']==pending and files()==before;source.locator('[data-resource-layout-pending=retry]').click();f.idle();expect(name(a)).to_have_attribute('title','Compact 실패 입력.txt');assert not metadata(key).get('resourceLayoutPending');before=files();f.checked('actual readonly Compact caption Save denial preserves exact request and blocks later caption activation; cold same-command retry saves once')
   source.locator('[data-density="40"]').click();field=inline(a,'Preview 오래된 입력.txt');current=api();api('rename-file',revision=current['revision'],command=uuid.uuid4().hex,id=a,name='동료 저장 파일명.txt');before=files();field.press('Enter');expect(source.locator('[data-resource-layout-pending=retry]')).to_be_enabled();pending=metadata(key)['resourceLayoutPending'];restart(2);assert metadata(key)['resourceLayoutPending']==pending;source.locator('[data-resource-layout-pending=retry]').click();f.idle();expect(source.locator('[data-resource-layout-pending=retry]')).to_be_enabled();assert files()==before;source.locator('[data-resource-layout-pending=cancel]').click();f.idle();expect(name(a)).to_have_attribute('title','동료 저장 파일명.txt');assert files()==before;f.checked('actual peer alias change rejects stale Preview Save/cold/retry; input-only cancel preserves peer bytes and original ID/hash')
   name(a).evaluate('el=>globalThis.__oldResourceName=el.onclick');closed=key;source.locator('[data-close]').first.click();f.page.evaluate('()=>__oldResourceName({stopPropagation(){},detail:1})');assert not metadata(closed).get('resourceRenameInput');source=browser();key=source.get_attribute('data-key');f.page.evaluate('()=>__oldResourceName({stopPropagation(){},detail:1})');wait_no_rename();assert files()==before;f.checked('held old caption handler cannot reopen a closed source or alter a new browser window')
  else:raise AssertionError(mode)
  original();assert files()==before;f.pending();focus(source);f.page.screenshot(path=str(f.case/('resource-name-'+mode+'.png')));f.browser.close()
except Exception as error:
 try:f.page.screenshot(path=str(f.case/'failure.png'));(f.case/'failure.html').write_text(f.page.content())
 except Exception:pass
 (f.case/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:
 f.stop();(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2))
print('RESOURCE_NAME_UI',f.case,flush=True)
