"""Authored empty-list/ProjectPack menus; real owned storage, generated File inputs only."""
import sys,json,hashlib,uuid,shutil,traceback
from playwright.sync_api import sync_playwright,expect
import v536_wide_mixed as f
mode=sys.argv[3];store=f.project/'.confectory/resources.v1.json';layout=f.project/'.confectory/resource-layout.v1.json';b=None
def api(action,success=True,**args):return f.invoke('projectResourceLayout',dict(action=action,project=f.state()['projectId'],**args),success)['result'].get('result')
def items():return api('load')['items']
def named(name):return next(x for x in items()if x['name']==name)
def files():return[x for x in items()if x['kind']!='folder']
def row(id):return b.locator('[data-resource-id="'+id+'"]')
def tree(id):return b.locator('[data-resource-tree-id="'+(id or '')+'"]')
def browser():
 global b
 f.page.locator('#workspace').click(button='right',position=dict(x=700,y=260));f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]').last;b.locator('[data-tab=resource]').click();expect(b.locator('[data-new]')).to_be_enabled()
def stable():f.page.evaluate('()=>document.activeElement?.blur()');f.pending();f.idle();expect(b.locator('[data-new]')).to_be_enabled()
def menu(where):
 stable()
 if where=='tree':tree(None).click(button='right')
 elif where=='add':b.locator('[data-new]').click()
 else:
  node=b.locator('[data-browser-control=objects]');box=node.bounding_box();node.click(button='right',position=dict(x=box['width']-18,y=box['height']-18))
 m=f.page.locator('.context-menu');expect(m).to_be_visible();expect(m.get_by_role('button')).to_have_text(['자료 추가','새 카테고리']);return m
def create(where,name,cancel=False,wait=True):
 menu(where).get_by_role('button',name='새 카테고리',exact=True).click();form=f.page.locator('.resource-name-form');form.locator('[name=name]').fill(name);form.get_by_role('button',name='취소'if cancel else'확인',exact=True).click();expect(form).to_have_count(0)
 if wait:f.idle()
def chooser(where):
 m=menu(where)
 with f.page.expect_file_chooser()as event:m.get_by_role('button',name='자료 추가',exact=True).click()
 return event.value
def payloads(names):return[dict(name=name,mimeType='text/plain',buffer=('generated '+name+'\r\n').encode())for name in names]
def choose(where,names):chooser(where).set_files(payloads(names))
def done(count):expect(b.locator('[data-resource-pending]')).to_have_count(0);expect(b.locator('[data-new]')).to_be_enabled();f.idle();assert len(files())==count
def pending(kind='import'):expect(b.locator('[data-resource-pending=retry]'if kind=='import'else'[data-resource-layout-pending=retry]')).to_be_enabled()
def original():
 for name,raw in f.original.items():assert(f.project/name).read_bytes()==raw,name
 assert not f.errors and not f.external,(f.errors,f.external)
def root():b.locator('[data-root]').click();f.idle()
def enter(id):row(id).dblclick();f.idle()
def hold_reply():
 f.page.evaluate("""()=>{const base=fetch;globalThis.__entryHeld=false;let wanted=null,armed=true;fetch=async(...args)=>{let request;try{request=JSON.parse(args[1]?.body||'null')}catch{}if(armed&&request?.op==='invoke'&&request.endpoint==='projectResourceLayout'&&request.input?.action==='create-folder')wanted=request.requestId;const response=await base(...args);if(!wanted||!armed||request?.op!=='update')return response;let body;try{body=await response.clone().json()}catch{return response}const row=body.results?.find(r=>r.requestId===wanted);if(!row?.ok)return response;armed=false;globalThis.__entryHeld=true;return new Promise(resolve=>{globalThis.__releaseEntry=()=>{fetch=base;delete row.result;row.ok=false;row.error={code:'owned_lost_entry_reply'};resolve(new Response(JSON.stringify(body),{status:200,headers:{'Content-Type':'application/json'}}));};});};}""")
def hold_file(name):
 f.page.evaluate("""name=>{const base=File.prototype.arrayBuffer;globalThis.__entryReadHeld=false;File.prototype.arrayBuffer=async function(){const bytes=await base.call(this);if(this.name!==name)return bytes;globalThis.__entryReadHeld=true;return new Promise(resolve=>{globalThis.__releaseEntryRead=()=>{File.prototype.arrayBuffer=base;resolve(bytes);};});};}""",name)
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
  expect.set_options(timeout=60000);f.browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.idle();browser();f.page.locator('#chat-input').fill('자료 진입과 별개인 입력');create('blank','취소한 카테고리',True);assert not layout.exists()and not store.exists();create('blank','A');a=named('A')['id'];assert named('A')['parent']is None;enter(a);original();f.checked('actual authored empty-list menu opens the existing category form; cancellation writes nothing and confirmation creates the owned category without source or layout redesign')
  choose('tree',['root one.txt','root two.txt']);done(2);assert all(x['parent']is None for x in files());expect(b.locator('.browser-title-path')).to_contain_text('A');original();f.checked('ProjectPack tree menu imports generated File copies to root even while the visible list is a child category; one existing atomic batch and exact hashes are used')
  choose('blank',['nested.txt']);done(3);assert named('nested.txt')['parent']==a;assert named('nested.txt')['hash']==hashlib.sha256(b'generated nested.txt\r\n').hexdigest();original();f.checked('blank child-list menu targets the displayed category and stores the exact bytes through the existing final-CAS import')
  if mode=='normal':
   row(named('nested.txt')['id']).click(button='right');m=f.page.locator('.context-menu');expect(m.get_by_role('button')).to_have_text(['자료 열기','이름 변경','삭제']);f.page.keyboard.press('Escape');create('tree','Root B');assert named('Root B')['parent']is None;expect(b.locator('.browser-title-path')).to_contain_text('A');original();f.checked('existing item menu never falls through to creation; root category creation remains root-scoped without changing child navigation')
   before=store.read_bytes();topology=layout.read_bytes();permission=layout.stat().st_mode
   try:layout.chmod(0o444);choose('blank',['retry one.txt','retry two.txt']);pending();assert store.read_bytes()==before and layout.read_bytes()==topology
   finally:layout.chmod(permission)
   expect(b.locator('[data-resource-recovery]')).to_contain_text('A');b.locator('[data-resource-pending=retry]').click();done(5);assert all(x['parent']==a for x in files()if x['name'].startswith('retry '));original();f.checked('real placement write refusal rolls back both new copies; the original menu destination and File input survive for exact retry')
   hold_reply();create('tree','Lost Root',wait=False);f.page.wait_for_function('()=>__entryHeld');assert named('Lost Root')['parent']is None;b.locator('[data-browser-control=object-query]').fill('더 늦은 검색 입력');f.page.evaluate('()=>__releaseEntry()');pending('layout');b.locator('[data-resource-layout-pending=retry]').click();expect(b.locator('[data-resource-layout-pending]')).to_have_count(0);f.idle();assert len([x for x in items()if x['name']=='Lost Root'])==1;expect(b.locator('[data-browser-control=object-query]')).to_have_value('더 늦은 검색 입력');original();f.checked('lost committed root-folder reply reuses its original command without duplicates or losing a newer search input')
   # A different writer after menu creation must not be silently rebased or retargeted.
   m=menu('blank');value=api('load');api('create-folder',revision=value['revision'],command=uuid.uuid4().hex,id=uuid.uuid4().hex,name='Other writer',parent=None);before=layout.read_bytes();m.get_by_role('button',name='새 카테고리',exact=True).click();form=f.page.locator('.resource-name-form');form.locator('[name=name]').fill('Stale menu');form.get_by_role('button',name='확인',exact=True).click();pending('layout');assert layout.read_bytes()==before;expect(b.locator('[data-resource-recovery]')).to_contain_text('Stale menu');b.locator('[data-resource-layout-pending=cancel]').click();assert not any(x['name']=='Stale menu'for x in items());original();f.checked('category creation retains the revision captured by the menu and rejects an intervening writer; failed input cancellation changes no confirmed data')
   b.locator('[data-resource-reload]').click();f.idle();create('add','D');d=named('D')['id'];enter(d);pick=chooser('blank');value=api('load');api('delete-folder',revision=value['revision'],command=uuid.uuid4().hex,id=d,hash=named('D')['hash']);before=store.read_bytes();topology=layout.read_bytes();pick.set_files(payloads(['never-root.txt']));pending();assert store.read_bytes()==before and layout.read_bytes()==topology;b.locator('[data-resource-pending=cancel]').click();original();f.checked('folder removal during the actual chooser never falls back to root; original failed destination remains until explicit input cancellation')
   b.locator('[data-resource-reload]').click();f.idle();root();pick=chooser('tree');before=store.read_bytes();pick.set_files([]);f.idle();assert store.read_bytes()==before;menu('blank');f.page.keyboard.press('Escape');original();f.checked('empty chooser selection and dismissed creation menus do not write or replay files; subsequent authored entry remains usable')
  elif mode=='lifecycle':
   hold_file('delayed root.txt');choose('tree',['delayed root.txt']);f.page.wait_for_function('()=>__entryReadHeld');root();f.page.evaluate('()=>__releaseEntryRead()');done(4);assert named('delayed root.txt')['parent']is None;original();f.checked('navigation during File read preserves the root destination captured at the tree menu')
   enter(a);pick=chooser('tree');f.pending();listing=f.state()['listingId'];f.page.locator('#title').click();f.page.get_by_role('button',name='프로젝트 나가기',exact=True).click();expect(f.page.locator('.home-grid')).to_be_visible();before=store.read_bytes();pick.set_files(payloads(['retired chooser.txt']));f.page.locator('[data-enter="'+listing+'"]').click();f.idle();b=f.page.locator('.window[data-key^="browser:project:"]').last;expect(b.locator('[data-resource-status]')).to_be_visible();f.idle();assert store.read_bytes()==before;expect(b.locator('[data-resource-pending]')).to_have_count(0);original();f.checked('Home retires the chooser owner/token; a late File selection cannot import into the returning project')
   m=menu('tree');f.page.evaluate('()=>globalThis.__oldResourceMenu=document.querySelector(".context-menu button")');b.locator('[data-close]').first.evaluate('e=>e.click()');f.page.evaluate('()=>__oldResourceMenu.click()');assert not f.page.locator('[data-resource-files]').count();assert store.read_bytes()==before;browser();original();f.checked('a retained detached menu callback cannot reopen a retired picker or write after its browser is closed')
   permission=layout.stat().st_mode
   try:layout.chmod(0o444);create('tree','Cold Root');pending('layout');assert 'Cold Root'in json.dumps(f.pending())
   finally:layout.chmod(permission)
   restart(1);pending('layout');b.locator('[data-resource-layout-pending=retry]').click();expect(b.locator('[data-resource-layout-pending]')).to_have_count(0);f.idle();assert named('Cold Root')['parent']is None;original();f.checked('failed root category intent survives cold engine restoration and explicit retry with the same original parent/revision/command')
   other=f.case/'same namespace other project';shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory','.build'));restart(2,other);assert items()==[];create('blank','Other project');assert named('Other project')['parent']is None;restart(3,f.project);assert not any(x['name']=='Other project'for x in items())and named('Cold Root')['parent']is None;original();f.checked('real same-namespace project roundtrip isolates menu owners, folder intents and resources')
  else:raise AssertionError(mode)
  expect(f.page.locator('#chat-input')).to_have_value('자료 진입과 별개인 입력');original();f.pending();f.page.screenshot(path=str(f.case/('resource-entry-'+mode+'.png')));f.browser.close()
except Exception as error:
 try:f.page.screenshot(path=str(f.case/'failure.png'))
 except Exception:pass
 (f.case/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:
 f.stop();(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2))
print('RESOURCE_ENTRY_FIXTURE',f.case,flush=True)
