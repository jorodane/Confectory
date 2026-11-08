"""Actual native-owned metadata/private filter UI, generated assets only."""
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
def stash(value):
 source.locator('[data-resource-type-filter]').click();f.page.locator('.context-menu button').filter(has_text={'image':'그림','file':'기타 파일','document':'문서'}[value]).evaluate('el=>globalThis.__oldKind=el.onclick');f.page.keyboard.press('Escape')
def blocked_click():
 box=source.locator('[data-resource-type-filter]').bounding_box();assert box;f.page.mouse.click(box['x']+box['width']/2,box['y']+box['height']/2)
def old():f.page.evaluate('()=>__oldKind()')
def restart(i,project=None,restore_key=None):
 global source
 key=restore_key or source.get_attribute('data-key');f.pending();f.page.close();f.stop()
 if project:f.env['CONFECTORY_WEB_PROJECT']=str(project/'project.cproj')
 f.start(i);f.page=f.setup();f.idle();source=win(key)
 if not source.count():source=browser()
 else:expect(source.locator('[data-resource-status]')).to_be_visible();f.idle()

def rows():return source.locator('[data-resource-id]')
def row(id):return source.locator('[data-resource-id="'+id+'"]')
def listbox():return source.locator('[data-browser-control=objects]')
def keys(value):focus(source);listbox().focus();listbox().press(value)
def pick(id):focus(source);row(id).click()
def selected():return set(metadata(source.get_attribute('data-key')).get('resourceSelections',[]))
def dialog():return f.page.locator('.modal[aria-label="자료 삭제"]')
def viewer(id):return f.page.locator('.window[data-key="resource-file:'+id+'"]')
def rename(id,value):pick(id);row(id).press('F2');field=source.locator('[data-resource-rename]');expect(field).to_be_visible();field.fill(value);return field
try:
 f.start(0)
 with sync_playwright()as p:
  expect.set_options(timeout=60000);f.browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.idle()
  folder=category('분류 카테고리');child=category('하위 카테고리',folder);a=add('문서A.txt','text/plain','A 원문 🧪\r\n'.encode());b=add('문서B.md','text/markdown',b'B original\r\n');image=add('그림.png','image/png',base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jz1kAAAAASUVORK5CYII='));inside=add('하위 원본.txt','text/plain',b'child source');api('move',revision=api()['revision'],command=uuid.uuid4().hex,ids=[inside],parent=child);source=browser();key=source.get_attribute('data-key');before=files();store=f.project/'.confectory/resources.v1.json';store_before=store.read_bytes();choose('document');f.page.locator('#chat-input').fill('단축키와 별개인 입력');f.page.evaluate('()=>document.activeElement.blur()')
  if mode=='baseline':
   keys('Control+a');assert not selected();pick(a);row(a).press('F2');expect(source.locator('[data-resource-rename]')).to_have_count(0);keys('Delete');expect(dialog()).to_have_count(0);assert files()==before;f.checked('publishedcb195512 lacks list Control+A/F2/Delete while native metadata, context actions and original resource bytes already exist')
  elif mode=='normal':
   keys('Control+a');assert selected()=={folder,a,b};assert image not in selected()and inside not in selected();keys('Escape');assert not selected();keys('Meta+a');assert selected()=={folder,a,b};keys('Delete');expect(dialog()).to_contain_text('3개 항목');expect(dialog()).to_contain_text('2개 항목');dialog().locator('[data-cancel]').click();assert files()==before;f.checked('Control/Meta+A selects only visible filtered items, Escape clears private selection, Delete reuses the exact descendant-union confirmation and Cancel writes nothing')
   focus(source);query=source.locator('[data-browser-control=object-query]');query.fill('문서');query.press('Enter');keys('Control+a');assert selected()=={a,b};keys('Enter');expect(viewer(a).locator('.resource-document-text')).to_have_text('A 원문 🧪\r\n');expect(viewer(b).locator('.resource-document-text')).to_have_text('B original\r\n');assert viewer(a).count()==viewer(b).count()==1 and files()==before;f.checked('list Enter opens each selected actual text resource once through existing hash/ownership-checked viewers without mutations or source rewriting')
   field=rename(a,'문서A 취소.txt');field.press('Escape');expect(source.locator('[data-resource-rename]')).to_have_count(0);assert selected()=={a}and files()==before;field=rename(a,'문서A 새 이름.txt');field.press('Enter');f.idle();expect(source.locator('[data-resource-tree-id="'+a+'"]')).to_have_attribute('title','문서A 새 이름.txt');assert store.read_bytes()==store_before;before=files();f.checked('F2 uses the existing inline draft: Escape cancels only its text, explicit Enter saves the alias with unchanged original file bytes/ID and existing viewer synchronization')
   focus(source);query=source.locator('[data-browser-control=object-query]');query.fill('입력란 내용');query.press('Control+a');query.press('Delete');expect(query).to_have_value('');query.press('F2');expect(source.locator('[data-resource-rename]')).to_have_count(0);assert files()==before;query.press('Enter');expect(viewer(a)).to_have_count(1);f.checked('search input keeps native select/delete/Enter behavior and does not invoke list rename/delete/open shortcuts')
   keys('Control+a');source.locator('[data-resource-id="'+a+'"]').press('F2');expect(source.locator('[data-resource-rename]')).to_have_count(0);keys('Escape');pick(folder);row(folder).press('Enter');expect(source.locator('[data-directory-id="'+folder+'"]')).to_be_visible();expect(row(child)).to_be_visible();source.locator('[data-root]').click();f.idle();assert files()==before;f.checked('F2 never guesses a target from multiple selections; existing focused-card folder Enter remains a single navigation with unchanged native resources')
   pick(b);row(b).press('Delete');expect(dialog()).to_contain_text('문서B.md');assert files()==before;dialog().locator('[data-remove]').click();f.idle();expect(source.locator('[data-resource-layout-pending]')).to_have_count(0);remaining={x['id']for x in api()['items']};assert b not in remaining and remaining=={folder,child,a,image,inside};expect(viewer(b)).to_have_count(0);before=files();f.checked('only explicit keyboard Delete confirmation removes the intended owned copy through native atomic deletion; filtered image/descendants/other resource identities remain')
  elif mode=='lifecycle':
   field=rename(a,'문서A 기준.txt');field.press('Enter');expect(source.locator('[data-resource-tree-id="'+a+'"]')).to_have_attribute('title','문서A 기준.txt');f.idle();names=f.project/'.confectory/resource-file-names.v1.json';prior=names.read_bytes();permissions=names.stat().st_mode
   try:
    names.chmod(0o444);field=rename(a,'문서A 실패 복구.txt');field.press('Enter');expect(source.locator('[data-resource-layout-pending=retry]')).to_be_enabled();pending=metadata(key)['resourceLayoutPending'];held=selected();keys('Control+a');keys('F2');keys('Delete');keys('Escape');assert selected()==held and metadata(key)['resourceLayoutPending']==pending;expect(dialog()).to_have_count(0);assert names.read_bytes()==prior
   finally:names.chmod(permissions)
   f.pending();restart(1);assert metadata(key)['resourceLayoutPending']==pending and names.read_bytes()==prior;source.locator('[data-resource-layout-pending=retry]').click();f.idle();expect(source.locator('[data-resource-layout-pending]')).to_have_count(0);expect(source.locator('[data-resource-tree-id="'+a+'"]')).to_have_attribute('title','문서A 실패 복구.txt');assert len(json.loads(names.read_text())['items'])==1;before=files();f.checked('real alias write denial keeps exact keyboard draft/command; list shortcuts cannot discard pending input; cold never replays Save and explicit same-request retry writes one alias')
   field=rename(a,'문서A 재시작 입력.txt');f.pending();restart(2);field=source.locator('[data-resource-rename]');expect(field).to_have_value('문서A 재시작 입력.txt');field.press('Escape');assert files()==before;f.checked('unsubmitted F2 text restores on cold and inline Escape leaves the native alias and selection intact')
   field=rename(a,'문서A 오래된 입력.txt');current=api();api('rename-file',revision=current['revision'],command=uuid.uuid4().hex,id=a,name='문서A 동료.txt');peer=files();field.press('Enter');expect(source.locator('[data-resource-layout-pending=retry]')).to_be_enabled();keys('Delete');expect(dialog()).to_have_count(0);source.locator('[data-resource-reload]').click();f.idle();source.locator('[data-resource-layout-pending=retry]').click();f.idle();expect(source.locator('[data-resource-layout-pending=retry]')).to_be_enabled();assert files()==peer;source.locator('[data-resource-layout-pending=cancel]').click();f.idle();before=peer;f.checked('actual peer alias change remains protected by the original CAS after keyboard F2, readonly refresh and retry; cancelling only the pending input preserves peer bytes')
   pick(b);keys('Delete');expect(dialog()).to_be_visible();dialog().locator('[data-remove]').evaluate('el=>globalThis.__oldDeleteConfirm=el.onclick');dialog().locator('[data-cancel]').click();pick(a);f.page.evaluate('()=>__oldDeleteConfirm()');expect(dialog()).to_have_count(0);assert files()==before;f.checked('a cancelled deletion confirmation cannot act on a later selection or repeat a native deletion')
   source.locator('[data-resource-tree-id="'+child+'"]').focus();source.locator('[data-resource-tree-id="'+child+'"]').press('Control+a');assert selected()=={a};source.locator('[data-resource-tree-id="'+child+'"]').press('F2');source.locator('[data-resource-tree-id="'+child+'"]').press('Delete');expect(source.locator('[data-resource-rename]')).to_have_count(0);listbox().focus();listbox().dispatch_event('keydown',dict(key='Delete',isComposing=True));listbox().dispatch_event('keydown',dict(key='F2',repeat=True));listbox().dispatch_event('keydown',dict(key='Delete',repeat=True));expect(source).to_be_visible();expect(dialog()).to_have_count(0);expect(source.locator('[data-resource-rename]')).to_have_count(0);assert files()==before;f.checked('hierarchy controls, IME composition and held repeated activation do not become list rename/delete commands')
   source.locator('[data-browser-control=objects]').evaluate('el=>{let n=el;while(n&&!n.onkeydown)n=n.parentElement;globalThis.__keyBody=n;globalThis.__oldKeyHandler=n.onkeydown;globalThis.__keyTarget=el;}');source.locator('[data-close]').first.click();f.page.evaluate('()=>__oldKeyHandler({target:__keyTarget,key:"Delete",preventDefault(){},stopPropagation(){}})');expect(dialog()).to_have_count(0);assert files()==before
   listing=f.state()['listingId'];f.page.locator('#title').click();f.page.get_by_role('button',name='프로젝트 나가기',exact=True).click();expect(f.page.locator('.home-grid')).to_be_visible();f.page.evaluate('()=>__oldKeyHandler({target:__keyTarget,key:"F2",preventDefault(){},stopPropagation(){}})');f.page.locator('[data-enter="'+listing+'"]').click();f.idle();assert files()==before;f.checked('closed-source and departed-project key callbacks retire with their owner lifetime and cannot reopen dialogs, rename or mutate resources')
  else:raise AssertionError(mode)
  original();assert files()==before;f.pending();expect(f.page.locator('#chat-input')).to_have_value('단축키와 별개인 입력');f.page.screenshot(path=str(f.case/('resource-keyboard-'+mode+'.png')));f.browser.close()
except Exception as error:
 try:f.page.screenshot(path=str(f.case/'failure.png'));(f.case/'failure.html').write_text(f.page.content())
 except Exception:pass
 (f.case/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:
 f.stop();(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2))
print('RESOURCE_KEYBOARD_UI',f.case,flush=True)
