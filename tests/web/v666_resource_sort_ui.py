"""Actual native resource sort input/lifetime protection, generated assets only."""
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

labels={'original':'기본 순서','name':'이름 오름차순','name-desc':'이름 내림차순','newest':'최근 생성순'}
def sort(value,w=None):
 w=w or source;w.locator('[data-browser-control=browser-actions]').click();f.page.locator('.context-menu button').filter(has_text=labels[value]).click();assert metadata(w.get_attribute('data-key'))['sort']==value

def stash(value):
 source.locator('[data-browser-control=browser-actions]').click();f.page.locator('.context-menu button').filter(has_text=labels[value]).evaluate('el=>globalThis.__oldSort=el.onclick');f.page.keyboard.press('Escape')
def old():f.page.evaluate('()=>__oldSort()')
def blocked_click():
 box=source.locator('[data-browser-control=browser-actions]').bounding_box();assert box;f.page.mouse.click(box['x']+box['width']/2,box['y']+box['height']/2)
def ordered(w=None):return (w or source).locator('[data-resource-id]').evaluate_all('(xs)=>xs.map(x=>x.dataset.resourceId)')
try:
 f.start(0)
 with sync_playwright()as p:
  expect.set_options(timeout=60000);f.browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.idle()
  folder=category('공통 카테고리 🧪');doc10=add('공통 문서10.txt','text/plain',b'original 10');doc2=add('공통 문서2.txt','text/plain',b'original 2');file=add('공통 기타.bin','application/octet-stream',b'original binary');current=api();item=next(x for x in current['items']if x['id']==file);api('describe',revision=current['revision'],command=uuid.uuid4().hex,id=file,generation=item['descriptionGeneration'],value='보관된 설명');source=browser();key=source.get_attribute('data-key');before=files();expect(source.locator('[data-resource-id]')).to_have_count(4)
  if mode=='baseline':
   sort('name');stash('name-desc');sort('newest');old();assert metadata(key)['sort']=='name-desc';f.checked('published dbffa359 retained old sort callback overwrites a newer explicit choice')
   source.locator('[data-density="100"]').click();desc=source.locator('[data-resource-description="'+file+'"]');desc.fill('sort must not implicitly save');blocked_click();f.idle();f.page.wait_for_function("()=>!document.querySelector('[data-resource-description-status]')?.textContent?.includes('저장하고')");assert next(x for x in api()['items']if x['id']==file)['description']=='sort must not implicitly save';before=files();f.page.keyboard.press('Escape');f.checked('published dbffa359 actual sort pointer blurs and submits a dirty Data description although no Save was requested')
  elif mode=='normal':
   source.locator('[data-browser-control=browser-actions]').click();assert [x.removeprefix('✓ ')for x in f.page.locator('.context-menu button').all_text_contents()]==list(labels.values());f.page.keyboard.press('Escape')
   for value,wanted in [('name',[folder,file,doc2,doc10]),('name-desc',[folder,doc10,doc2,file]),('original',[folder,doc10,doc2,file]),('newest',[folder,file,doc2,doc10])]:
    sort(value);assert ordered()==wanted,(value,ordered(),wanted);assert files()==before
   f.checked('authored four orders use actual metadata: folders first, numeric Korean names, original import order and native creation timestamps; no resource writes')
   source.locator('[data-resource-id="'+doc2+'"]').click();source.locator('[data-resource-id="'+doc10+'"]').click(modifiers=['Control']);selected=metadata(key)['resourceSelections'];sort('name');assert metadata(key)['resourceSelections']==selected
   choose('document');query=source.locator('[data-browser-control=object-query]');query.fill('공통');query.press('Enter');query.fill('미확정 정렬 검색 🧪');sort('name-desc');assert ordered()==[folder,doc10,doc2];expect(query).to_have_value('미확정 정렬 검색 🧪');assert metadata(key)['query']=='공통';f.checked('sorting preserves selection, folder/kind membership and separate committed/unsubmitted search text')
   query.fill('');query.press('Enter');source.locator('[data-resource-tree-id="'+folder+'"]').click(button='right');f.page.locator('.context-menu').get_by_role('button',name='상위 카테고리 열기',exact=True).click();base_key=f.page.locator('.window[data-key^="browser-tree:resource:"]').last.get_attribute('data-key');base=win(base_key);sort('name',base);window_menu(base);f.page.locator('.context-menu').get_by_role('button',name='같은 브라우저 새 창으로 열기',exact=True).click();duplicate_key=f.page.locator('.window[data-key^="browser-tree:resource:"]').last.get_attribute('data-key');duplicate=win(duplicate_key);assert metadata(duplicate_key)['sort']=='name';sort('name-desc',duplicate);assert metadata(base_key)['sort']=='name'and metadata(key)['sort']=='name-desc';focus(source);f.checked('existing child-browser duplication retains the private sort then changes independently; original project window remains intact')
   source.locator('[data-browser-control=object-query]').fill('cold 정렬 입력');f.page.locator('#chat-input').fill('정렬과 독립인 대화');f.pending();restart(1);assert metadata(key)['sort']=='name-desc'and metadata(key)['resourceFilter']=='document';expect(source.locator('[data-browser-control=object-query]')).to_have_value('cold 정렬 입력');expect(f.page.locator('#chat-input')).to_have_value('정렬과 독립인 대화');assert ordered()==[folder,doc10,doc2]and files()==before;f.checked('real cold restart restores sort/filter, committed results, newer query and chat without asset or source mutation')
  elif mode=='lifecycle':
   sort('name');stash('name-desc');sort('newest');old();assert metadata(key)['sort']=='newest';stash('name-desc');choose('file');old();assert metadata(key)['sort']=='newest';f.checked('an older sort choice cannot replace a newer explicit sort or kind selection')
   stash('name-desc');source.locator('[data-browser-control=object-query]').fill('later search');old();assert metadata(key)['sort']=='newest';source.locator('[data-browser-control=object-query]').fill('');stash('name-desc');f.page.locator('#chat-input').fill('later unrelated input');old();expect(f.page.locator('#chat-input')).to_have_value('later unrelated input');assert metadata(key)['sort']=='newest';focus(source);f.checked('retired sort callbacks preserve newer search and unrelated editable focus')
   stash('name-desc');source.locator('[data-resource-id="'+file+'"]').click(button='right');f.page.locator('.context-menu').get_by_role('button',name='이름 변경',exact=True).click();rename=source.locator('[data-resource-rename]');rename.fill('보존할 미확정 이름.bin');blocked_click();expect(rename).to_be_focused();old();expect(rename).to_have_value('보존할 미확정 이름.bin');assert metadata(key)['sort']=='newest'and files()==before;rename.press('Escape');old();assert metadata(key)['sort']=='newest';f.checked('actual sort pointer and held callback cannot submit/discard an inline name draft')
   source.locator('[data-density="100"]').click();stash('name-desc');desc=source.locator('[data-resource-description="'+file+'"]');desc.fill('정렬이 저장하면 안 되는 설명');blocked_click();expect(desc).to_be_focused();old();expect(desc).to_have_value('정렬이 저장하면 안 되는 설명');assert metadata(key)['sort']=='newest'and not metadata(key)['resourceDescriptionDraft'].get('pending')and files()==before;f.pending();restart(1);desc=source.locator('[data-resource-description="'+file+'"]');expect(desc).to_have_value('정렬이 저장하면 안 되는 설명');assert metadata(key)['sort']=='newest'and files()==before;f.checked('actual pointer no longer blurs/submits a dirty Data description; cold retains exact input without automatic Save')
   desc.press('Escape');f.idle();stash('name-desc');desc=source.locator('[data-resource-description="'+file+'"]');desc.fill('실제 쓰기 실패 입력');draft=metadata(key)['resourceDescriptionDraft'];paths=[f.project/n for n in files()if n.endswith('.json')and 'resource-descriptions'in n];assert paths,files().keys();modes={p:p.stat().st_mode&0o777 for p in paths}
   for path in paths:path.chmod(0o444)
   try:
    desc.press('Enter');expect(source.locator('[data-resource-description-retry]:visible')).to_be_enabled();pending=metadata(key)['resourceDescriptionDraft']['pending'];blocked_click();old();assert metadata(key)['resourceDescriptionDraft']['pending']==pending and metadata(key)['sort']=='newest'and files()==before
   finally:
    for path,mode_bits in modes.items():path.chmod(mode_bits)
   restart(2);assert metadata(key)['resourceDescriptionDraft']['pending']==pending and files()==before;source.locator('[data-resource-description-retry]:visible').click();f.idle();expect(source.locator('[data-resource-description="'+file+'"]')).to_have_value('실제 쓰기 실패 입력');assert not metadata(key).get('resourceDescriptionDraft');assert next(x for x in api()['items']if x['id']==file)['description']=='실제 쓰기 실패 입력';before=files();sort('name-desc');f.checked('real native read-only denial preserves exact command/revision and blocks sort; cold same-request explicit retry saves once, then sorting resumes')
   stash('name');desc=source.locator('[data-resource-description="'+file+'"]');desc.fill('CAS 보존 입력');draft=metadata(key)['resourceDescriptionDraft'];current=api();item=next(x for x in current['items']if x['id']==file);api('describe',revision=current['revision'],command=uuid.uuid4().hex,id=file,generation=item['descriptionGeneration'],value='먼저 저장한 동료');before=files();desc.press('Enter');expect(source.locator('[data-resource-description-retry]:visible')).to_be_enabled();old();assert metadata(key)['sort']=='name-desc'and files()==before;restart(3);assert metadata(key)['resourceDescriptionDraft']['revision']==draft['revision'];source.locator('[data-resource-description-retry]:visible').click();f.idle();expect(source.locator('[data-resource-description-retry]:visible')).to_be_enabled();assert files()==before;source.locator('[data-resource-description-cancel]:visible').click();f.idle();expect(source.locator('[data-resource-description="'+file+'"]')).to_have_value('먼저 저장한 동료');sort('name');assert files()==before;f.checked('peer CAS rejection, cold retry and explicit input-only cancel preserve original basis and peer bytes; sort never rebases or writes the conflict')
   source.locator('[data-density="40"]').click();stash('name-desc');source.locator('[data-close]').first.click();old();assert metadata(key)['sort']=='name';source=browser();new_key=source.get_attribute('data-key');sort('newest');old();assert metadata(new_key)['sort']=='newest';key=new_key;stash('name-desc');listing=f.state()['listingId'];f.page.locator('#title').click();f.page.get_by_role('button',name='프로젝트 나가기',exact=True).click();expect(f.page.locator('.home-grid')).to_be_visible();old();f.page.locator('[data-enter="'+listing+'"]').click();f.idle();source=win(key);assert metadata(key)['sort']=='newest';f.checked('closed window and project departure invalidate held callbacks; new/returning windows keep their own private sort')
  else:raise AssertionError(mode)
  original();assert files()==before;f.pending();f.page.screenshot(path=str(f.case/('resource-sort-'+mode+'.png')));f.browser.close()
except Exception as error:
 try:f.page.screenshot(path=str(f.case/'failure.png'));(f.case/'failure.html').write_text(f.page.content())
 except Exception:pass
 (f.case/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:
 f.stop();(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2))
print('RESOURCE_SORT_UI',f.case,flush=True)
