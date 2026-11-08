"""Actual scoped parent browsers; native metadata only, generated fixtures."""
import sys,json,pathlib,hashlib,base64,uuid,traceback,shutil,time,re
from playwright.sync_api import sync_playwright,expect
import v536_wide_mixed as f
mode=sys.argv[3];reads=[];resource_scripts=[];base_observe=f.observe;source=None

def traced(response):
 base_observe(response)
 try:
  if response.url.split('?')[0].endswith('/resource-browser.js'):resource_scripts.append(hashlib.sha256(response.body()).hexdigest())
  q=response.request.post_data_json
  if isinstance(q,dict)and q.get('op')=='observe'and q.get('endpoint')=='readProjectResourceLocation':reads.append(dict(request=q,response=response.json()))
 except Exception:pass
f.observe=traced

def api(action='load',**kw):return f.invoke('projectResourceLayout',dict(project=f.state()['projectId'],action=action,**kw))['result']['result']
def add(name,raw):
 revision=f.invoke('projectResources',dict(project=f.state()['projectId'],action='load'))['result']['result']['revision'];id=uuid.uuid4().hex
 f.invoke('projectResources',dict(project=f.state()['projectId'],action='import',revision=revision,command=uuid.uuid4().hex,item=dict(id=id,name=name,type='text/plain',size=len(raw),hash=hashlib.sha256(raw).hexdigest(),data=base64.urlsafe_b64encode(raw).decode(),modifiedAt=0)));return id

def category(name,parent=None):
 id=uuid.uuid4().hex;api('create-folder',revision=api()['revision'],command=uuid.uuid4().hex,id=id,name=name,parent=parent);return id

def move(id,parent):api('move',revision=api()['revision'],command=uuid.uuid4().hex,ids=[id],parent=parent)
def win(key):return f.page.locator('.window[data-key="'+key+'"]')
def tree_keys():return set(f.page.locator('.window[data-key^="browser-tree:resource:"]').evaluate_all('(xs)=>xs.map(x=>x.dataset.key)'))
def focus(w):
 if 'window-document'in(w.get_attribute('class')or''):f.page.locator('[data-window-tab="'+w.get_attribute('data-key')+'"]').click();f.idle();return
 f.page.locator('#worker-finder-bubble').click();panel=f.page.locator('#workspace-find-panel');expect(panel).to_be_visible();panel.locator('[data-find-mode=elements]').click();panel.get_by_role('searchbox').fill('');target=panel.locator('[data-find-key="node:'+w.get_attribute('data-key')+'"]');expect(target).to_be_enabled();target.click();expect(panel).to_have_count(0);f.idle()
def browser():
 f.page.locator('#workspace').click(button='right',position=dict(x=700,y=260));f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]').last;b.locator('[data-tab=resource]').click();expect(b.locator('[data-new]')).to_be_enabled();return b

def menu(w,id,tree=True):
 focus(w);w.locator('[data-resource-tree-id="'+id+'"]'if tree else'[data-resource-id="'+id+'"]').click(button='right');return f.page.locator('.context-menu').get_by_role('button',name='상위 카테고리 열기',exact=True)
def open_parent(w,id,parent,tree=True):
 prior=tree_keys();menu(w,id,tree).click();f.page.wait_for_function("(prior)=>[...document.querySelectorAll('.window')].some(x=>x.dataset.key?.startsWith('browser-tree:resource:')&&!prior.includes(x.dataset.key))",arg=list(prior));new=tree_keys()-prior;assert len(new)==1;key=next(iter(new));assert key.startswith('browser-tree:resource:'+str(parent or'null')+':');result=win(key);expect(result.locator('[data-resource-id="'+id+'"]').first).to_have_attribute('aria-selected','true');expect(result.locator('[data-resource-id="'+id+'"]').first).to_be_focused();assert not result.locator('[data-tab]').count();assert 'window-document'not in(result.get_attribute('class')or'');return result

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
def hold(at=1,corrupt=False):
 f.page.evaluate("""({at,corrupt})=>{const base=globalThis.__parentBaseFetch||fetch;globalThis.__parentBaseFetch=base;globalThis.__parentHistory??=[];globalThis.__parentHeld=false;globalThis.__parentReadCount=0;fetch=async(...a)=>{let q;try{q=JSON.parse(a[1]?.body||'null')}catch{}const response=await base(...a);if(q?.op!=='observe'||q.endpoint!=='readProjectResourceLocation')return response;__parentReadCount++;const body=await response.clone().json();__parentHistory.push({input:q.input,reply:body});if(__parentReadCount!==at)return response;if(!body.ok)return response;__parentHeld=true;return new Promise(resolve=>{globalThis.__releaseParent=()=>{if(corrupt)body.result.parent={id:'0'.repeat(32),kind:'folder',name:'foreign',hash:'0'.repeat(64)};resolve(new Response(JSON.stringify(body),{status:200,headers:{'Content-Type':'application/json'}}));};});};}""",dict(at=at,corrupt=corrupt))
def release():f.page.evaluate('()=>__releaseParent()')
def held(w,id):menu(w,id).click();f.page.wait_for_function('()=>__parentHeld')
def stable(prior):
 f.page.wait_for_timeout(250);assert tree_keys()==prior

def restart(i,project=None):
 global source
 key=source.get_attribute('data-key');f.pending();f.page.close();f.stop()
 if project:f.env['CONFECTORY_WEB_PROJECT']=str(project/'project.cproj')
 f.start(i);f.page=f.setup();f.idle();source=win(key)
try:
 f.start(0)
 with sync_playwright()as p:
  expect.set_options(timeout=60000);f.browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.idle()
  a=category('상위 <A> 🧪');b=category('하위 B',a);peer=add('peer source.txt',b'peer');deep=add('deep current.txt','원본 🧪\r\n'.encode());top=add('root file.txt',b'root');move(peer,a);move(deep,b);before=files();source=browser();source_key=source.get_attribute('data-key');source.locator('[data-resource-id="'+a+'"]').dblclick();f.idle();query=source.locator('[data-browser-control=object-query]');query.fill('peer');query.press('Enter');f.page.locator('#chat-input').fill('상위 탐색과 별개인 새 입력');f.page.evaluate('()=>document.activeElement?.blur()');f.pending()
  if mode=='baseline':
   expect(menu(source,deep)).to_have_count(0);f.page.keyboard.press('Escape');assert files()==before;f.checked('published resource context menu lacks the authored parent browser action, retaining exact source bytes')
  elif mode=='baseline-query':
   restart(1);saved=metadata(source_key);assert saved['query']=='peer'and saved['queryInput']=='peer';actual=source.locator('[data-browser-control=object-query]').input_value();assert actual=='',dict(actual=actual,saved=saved);import subprocess;expected=hashlib.sha256(subprocess.check_output(['git','show','064e922d2e2e9906284534c3fe1168ffcd50034f:examples/editor-home/ui/resource-browser.js'],cwd=f.repo)).hexdigest();assert resource_scripts and set(resource_scripts)=={expected},resource_scripts;f.checked('published064e browser bytes reproduce empty cold query control while exact peer query/input remain in native private presentation')
  elif mode=='late-chat':
   hold();prior=tree_keys();held(source,deep);f.page.locator('#chat-input').fill('later independent input');release();f.page.wait_for_function("(n)=>[...document.querySelectorAll('.window')].filter(x=>x.dataset.key?.startsWith('browser-tree:resource:')).length===n",arg=len(prior)+1);created=win(next(iter(tree_keys()-prior)));expect(created.locator('[data-resource-id="'+deep+'"]').first).to_be_focused();expect(f.page.locator('#chat-input')).to_have_value('later independent input');f.checked('pre-fix delayed parent navigation steals focus after later unrelated chat input despite preserving its bytes')
  elif mode=='normal':
   view=open_parent(source,deep,b);expect(view.locator('.browser-title-path')).to_have_text('하위 B');expect(view.locator('[data-resource-tree-id="'+a+'"]').first).to_have_count(0);expect(view.locator('[data-root]')).to_have_count(0);expect(view.locator('[data-browser-control=object-query]')).to_have_value('');assert metadata(source_key)['resourceFolder']==a and metadata(source_key)['query']=='peer';assert files()==before;f.checked('separate parent-rooted browser selects/focuses the actual file, clears only its own query and preserves source parent/filter/data')
   saved_key=view.get_attribute('data-key');focus(view);view.locator(':scope > .window-title').click(button='right',position=dict(x=20,y=10));f.page.locator('.context-menu').get_by_role('button',name='같은 브라우저 새 창으로 열기',exact=True).click();duplicate=f.page.locator('.window[data-key^="browser-tree:resource:"]').last;assert duplicate.get_attribute('data-key')!=saved_key;expect(duplicate.locator('.browser-title-path')).to_have_text('하위 B');expect(duplicate.locator('[data-resource-tree-id="'+a+'"]')).to_have_count(0);duplicate.locator('[data-close]').first.click();f.checked('existing duplicate action retains the category root through the established browser key, with no new stored root/permission format')
   folder_view=open_parent(source,b,a);expect(folder_view.locator('.browser-title-path')).to_have_text('상위 <A> 🧪');expect(folder_view.locator('img')).to_have_count(0);folder_view.locator('[data-resource-id="'+b+'"]').press('Enter');expect(folder_view.locator('.browser-title-path')).to_contain_text('하위 B');folder_view.locator('[data-directory-id="'+a+'"]').click();expect(folder_view.locator('[data-resource-id="'+b+'"]')).to_be_visible();f.checked('folder parent opens its containing category rather than entering the selected folder; Enter and anchored breadcrumbs retain normal navigation and literal names')
   root_view=open_parent(source,top,None);expect(root_view.locator('[data-root]')).to_be_visible();expect(root_view.locator('[data-resource-id="'+top+'"]')).to_have_attribute('aria-selected','true');root_folder=open_parent(source,a,None);expect(root_folder.locator('[data-root]')).to_be_visible();f.checked('root file and root category use a fresh ProjectPack browser with the exact selected identity; no implicit default folder or source move')
   restart(1);restored=win(saved_key);expect(restored.locator('[data-resource-id="'+deep+'"]')).to_have_attribute('aria-selected','true');expect(restored.locator('.browser-title-path')).to_have_text('하위 B');expect(restored.locator('[data-resource-tree-id="'+a+'"]')).to_have_count(0);expect(source.locator('[data-browser-control=object-query]')).to_have_value('peer');expect(f.page.locator('#chat-input')).to_have_value('상위 탐색과 별개인 새 입력');assert files()==before;f.checked('cold restart restores root/selection through existing private key/meta, preserving source query/chat and every resource byte without replaying navigation')
  elif mode=='lifecycle':
   hold();prior=tree_keys();read_before=len(reads);held(source,deep);menu(source,deep).click();assert f.page.evaluate('__parentReadCount')==1;release();f.page.wait_for_function("(n)=>[...document.querySelectorAll('.window')].filter(x=>x.dataset.key?.startsWith('browser-tree:resource:')).length===n",arg=len(prior)+1);assert f.page.evaluate('__parentReadCount')==2;initial_key=next(iter(tree_keys()-prior));f.checked('same pending source/target coalesces repeated clicks, then performs final readonly recheck and opens once')
   hold(corrupt=True);prior=tree_keys();held(source,deep);release();expect(source.locator('[data-resource-reload]')).to_be_visible();stable(prior);assert files()==before;source.locator('[data-resource-reload]').click();f.idle();f.checked('forged parent metadata creates no window, preserves all data and exposes only existing explicit readonly recovery')
   hold();prior=tree_keys();held(source,deep);catalog=f.project/'.confectory/resources.v1.json';permissions=catalog.stat().st_mode
   try:catalog.chmod(0o000);release();expect(source.locator('[data-resource-reload]')).to_be_visible();stable(prior)
   finally:catalog.chmod(permissions)
   assert files()==before;source.locator('[data-resource-reload]').click();f.idle();f.checked('read permission loss after initial proof prevents any parent window; explicit readonly refresh after fixture recovery preserves all originals')
   hold();prior=tree_keys();held(source,deep);source.locator('[data-browser-control=object-query]').fill('newer query while waiting');release();stable(prior);expect(source.locator('[data-browser-control=object-query]')).to_have_value('newer query while waiting');f.checked('later source query input fences the delayed navigation and preserves current focus/input rather than opening a stale window')
   hold();prior=tree_keys();held(source,deep);f.page.locator('#chat-input').fill('new chat input while parent waits');release();stable(prior);expect(f.page.locator('#chat-input')).to_have_value('new chat input while parent waits');expect(f.page.locator('#chat-input')).to_be_focused();assert files()==before;f.checked('later unrelated chat input keeps its focus and exact value; delayed navigation is retired without opening or moving a window')
   hold();prior=tree_keys();held(source,deep);source.locator('[data-close]').first.click();release();stable(prior);f.checked('closing source retires delayed metadata request with no late new window or mutation')
   # Reopen the retained project browser using the existing native workspace menu.
   source=browser();source_key=source.get_attribute('data-key');hold();prior=tree_keys();held(source,deep);move(deep,a);peer_bytes=files();release();expect(source.locator('[data-resource-reload]')).to_be_visible();stable(prior);assert files()==peer_bytes;source.locator('[data-resource-reload]').click();f.idle();fresh=open_parent(source,deep,a);expect(fresh.locator('.browser-title-path')).to_have_text('상위 <A> 🧪');assert files()==peer_bytes;f.checked('actual peer move after initial proof is refused at final observation; explicit list refresh then opens current parent and never replays/mutates the move')
   orphan=win(initial_key);current=api();removed=next(x for x in current['items']if x['id']==b);api('delete-folder',revision=current['revision'],command=uuid.uuid4().hex,id=b,hash=removed['hash']);peer_bytes=files();prior=tree_keys();menu(orphan,b).click();expect(orphan.locator('[data-resource-reload]')).to_be_visible();stable(prior);orphan.locator('[data-resource-reload]').click();f.idle();expect(orphan.locator('[data-root]')).to_be_visible();assert files()==peer_bytes;f.checked('removed view root follows authored ProjectPack fallback only after explicit refresh; selected file already moved elsewhere and every byte/ID remain protected')
   focus(source);source.locator(':scope > .window-title').click(button='right',position=dict(x=20,y=10));f.page.locator('.context-menu').get_by_role('button',name='탭으로 열기',exact=True).click();expect(source).to_have_class(re.compile('window-document'));forced=open_parent(source,deep,a);assert 'window-document'not in(forced.get_attribute('class')or'');f.checked('an active document-tab source still opens an independent workspace window through existing placement/focus rules')
   focus(source);hold();prior=tree_keys();held(source,deep);listing=f.state()['listingId'];f.page.locator('#title').click();f.page.get_by_role('button',name='프로젝트 나가기',exact=True).click();expect(f.page.locator('.home-grid')).to_be_visible();release();f.page.locator('[data-enter="'+listing+'"]').click();f.idle();stable(prior);assert files()==peer_bytes;expect(f.page.locator('#chat-input')).to_have_value('new chat input while parent waits');f.checked('Home/project departure retires a held navigation; returning preserves all prior windows/input without replaying the request')
  else:raise AssertionError(mode)
  if mode=='normal':assert files()==before
  original();f.pending();(f.case/'location-client-history.json').write_text(json.dumps(f.page.evaluate('()=>globalThis.__parentHistory||[]'),ensure_ascii=False,indent=2));assert all(len(json.dumps(x['response']).encode())<16384 for x in reads);f.page.screenshot(path=str(f.case/('resource-parent-'+mode+'.png')));f.browser.close()
except Exception as error:
 try:f.page.screenshot(path=str(f.case/'failure.png'));(f.case/'failure.html').write_text(f.page.content())
 except Exception:pass
 (f.case/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:
 f.stop();(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'location-reads.json').write_text(json.dumps(reads,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2))
print('RESOURCE_PARENT_UI',f.case,flush=True)
