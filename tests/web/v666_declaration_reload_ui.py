"""Explicit form discard preserves cancel/failure/late-input and native CAS."""
import json,sys,time,traceback
from playwright.sync_api import sync_playwright,expect
import v666_declaration_reload_fixture as fixture
f=fixture.f;ns=fixture.ns;mode=sys.argv[3];detached='view'in sys.argv[4:];leaf='ReloadModule'if detached else'ReloadCategory';owner=ns+leaf;page=None;key='declaration';endpoint='openEditorView'if detached else'inspectDeclaration'
def panel():return page.locator('.window[data-key="'+key+'"]')
def field():return panel().locator('[data-decl-property=displayName]')
def idle():expect(page.locator('.brand')).to_be_enabled(timeout=60000)
def pending():page.evaluate('async()=>await confectoryFlushPresentation()');return f.state()['presentation']['inputs']['declarations']
def record():return next((v for k,v in pending()if k.endswith('|'+owner)),None)
def reads():return [r for r in f.requests if r.get('endpoint')==endpoint and r.get('input',{}).get('id')==owner]
def dialog():return page.get_by_role('dialog',name='현재 초안 다시 읽기',exact=True)
def reload():panel().locator('[data-declaration-current]').click()
def open_card():
 global key
 page.get_by_role('tab',name='Workspace',exact=True).click();idle()
 existing=page.locator('[data-window-tab="'+key+'"]')
 if existing.count()and panel().locator('[data-declaration-id]').count()and panel().locator('[data-declaration-id]').inner_text()==owner:existing.click();idle()
 if panel().locator('[data-declaration-id]').is_visible()and panel().locator('[data-declaration-id]').inner_text()==owner:return
 page.locator('#worker-finder-bubble').click();finder=page.locator('#workspace-find-panel');finder.get_by_role('searchbox').fill(leaf);finder.locator('[data-find-key="object:'+owner+'"],[data-find-key="node:'+key+'"]').first.click();expect(panel().locator('[data-declaration-id]')).to_have_text(owner);idle()
 if detached and key=='declaration':
  panel().locator('[data-declaration-keep]').click();idle();views=[v for v in f.state()['editorViews']if v['id']==owner and v['mode']=='declaration'];assert len(views)==1;key='editor-'+views[0]['view'];expect(field()).to_be_visible();f.call('select',{'id':ns+'Tick'});idle()
def edit(text):field().fill(text);assert record()['properties']['value']['displayName']==text
def ask():reload();expect(dialog()).to_be_visible();expect(field()).not_to_have_value('')
def confirm():dialog().locator('[data-declaration-reload-confirm]').click();expect(dialog()).to_have_count(0);idle()
def normal():
 n=len(reads());reload();end=time.monotonic()+20
 while len(reads())==n and time.monotonic()<end:page.wait_for_timeout(50)
 idle();expect(dialog()).to_have_count(0);assert len(reads())==n+1
 edit('지우기 전 확인할 이름😀');held=record();n=len(reads());ask();assert len(reads())==n;dialog().get_by_role('button',name='취소',exact=True).click();expect(dialog()).to_have_count(0);expect(field()).to_have_value('지우기 전 확인할 이름😀');assert record()==held and len(reads())==n;f.checked('read without private input is direct; pending form discard requires explicit approval and Cancel does not read or discard')
 if detached:
  box=panel().locator('[data-module-new]');box.locator('summary').click();new=box.locator('[data-module-new-form]');new.locator('[data-module-function]').fill(ns+'Main');new.locator('[data-module-args]').fill('int, out string');held=record();assert any(k.startswith('module-')for k in held)
  ask();dialog().get_by_role('button',name='취소',exact=True).click();expect(new.locator('[data-module-args]')).to_have_value('int, out string');assert record()==held
 ask();confirm();expect(field()).to_have_value('');assert not record();f.checked('explicit approval clears only unchanged form snapshot; independent module name/contract Cancel and existing reset/release path preserve source contracts')
 if detached:
  panel().locator('[data-declaration-release]').click();idle();expect(panel()).to_have_count(0)
def failure():
 edit('조회 실패에도 보존할 이름');held=record();page.evaluate('''(target)=>{const base=fetch,lost=new Set();globalThis.__denyReload=true;globalThis.fetch=async(...args)=>{let b;try{b=JSON.parse(args[1]?.body||'{}')}catch{}if(__denyReload&&b?.op==='invoke'&&b.endpoint===target){__denyReload=false;lost.add(b.requestId);}const response=await base(...args);if(b?.op==='update'){const result=await response.clone().json();let changed=false;for(const row of result.results||[])if(lost.delete(row.requestId)){row.ok=false;row.error={code:'transport-interrupted'};delete row.result;changed=true;}if(changed)return new Response(JSON.stringify(result),{status:200,headers:{'Content-Type':'application/json'}});}return response;};}''',endpoint)
 ask();confirm();expect(field()).to_have_value('조회 실패에도 보존할 이름');assert record()==held;f.checked('lost read-only reply never discards private values or retries a mutation; explicit retry remains available')
 ask();confirm();expect(field()).to_have_value('');assert not record()
def late(browser):
 global page
 edit('同じ入力😀');held=record();n=len(reads());ask();field().evaluate('(el)=>{for(const value of ["別の入力","同じ入力😀"]){el.value=value;el.dispatchEvent(new Event("input",{bubbles:true}));}}');dialog().locator('[data-declaration-reload-confirm]').click();expect(dialog()).to_have_count(0);idle();assert len(reads())==n and record()==held;expect(field()).to_have_value('同じ入力😀');f.checked('same-text ABA while the approval dialog is open invalidates approval without a read or input loss')
 ids=set();paused={}
 def hold(route):
  body=route.request.post_data_json
  if body.get('op')=='invoke'and body.get('endpoint')==endpoint and body.get('input',{}).get('id')==owner:ids.add(body['requestId'])
  response=route.fetch();data=response.json()
  if not paused and any(r.get('requestId')in ids and r.get('ok')for r in data.get('results',[])):paused.update(route=route,response=response);return
  route.fulfill(response=response,json=data)
 page.route('**/api/request',hold);ask();dialog().locator('[data-declaration-reload-confirm]').click()
 for _ in range(600):
  if paused:break
  page.wait_for_timeout(50)
 assert paused
 field().evaluate('(el)=>{for(const value of ["途中の入力","同じ入力😀"]){el.value=value;el.dispatchEvent(new Event("input",{bubbles:true}));}}');paused['route'].fulfill(response=paused['response']);page.unroute('**/api/request',hold);idle();expect(field()).to_have_value('同じ入力😀');assert record()==held;f.checked('same-text ABA after approval while read reply is held survives exact snapshot/epoch fencing')
 page.evaluate('async()=>await confectoryFlushPresentation()');page.close();f.stop();f.start(1);page=f.setup(browser);open_card();expect(field()).to_have_value('同じ入力😀');assert record()==held;f.checked('cold restart restores the retained form values and original CAS basis, with no pending approval replay')
def conflict():
 edit('旧基準の未適用入力');held=record();current=f.call('inspectDeclaration',{'id':owner});info=f.state()['declaration'];f.call('editDeclaration',{'id':owner,'revision':info['revision'],'hash':info['textHash'],'edit':{'action':'properties','values':{'displayName':'別の共有下書き'}}});idle();panel().locator('[data-properties-apply]').click();idle();expect(field()).to_have_value('旧基準の未適用入力');assert record()==held;f.call('inspectDeclaration',{'id':owner});idle();assert f.state()['declaration']['values']['editorName']=='別の共有下書き';f.checked('native stale revision/hash still rejects Apply; reload never silently rebases or overwrites the peer draft')
 ask();confirm();expect(field()).to_have_value('別の共有下書き');assert not record();assert f.state()['draft']['id']==owner;f.checked('explicit discard then reads the actual current owned draft, preserving ID/contracts/original source bytes')
def scope(browser):
 global page,key
 edit('프로젝트 A의 미적용 이름');held=record();ask();n=len(reads());f.call('leaveProject',{});expect(page.locator('.home-grid')).to_be_visible();
 if dialog().is_visible():dialog().locator('[data-declaration-reload-confirm]').click()
 expect(dialog()).to_have_count(0);assert len(reads())==n;page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(f.projects[1]);f.start(1);page=f.setup(browser);key='declaration';open_card();expect(field()).to_have_value('');f.checked('stale dialog after leaving project cannot read/discard/reopen its old owner; same-ID project B has separate input')
 page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(f.projects[0]);f.start(2);page=f.setup(browser);key='declaration';open_card();expect(field()).to_have_value('프로젝트 A의 미적용 이름');assert record()==held;f.checked('return to A restores its exact private values without replaying the discarded approval dialog')
try:
 f.start(0)
 with sync_playwright()as p:
  expect.set_options(timeout=60000);browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=f.setup(browser);open_card();pending();idle();page.wait_for_timeout(150);idle()
  try:
   if mode=='baseline':
    edit('다시 읽기에 사라지는 이름');reload();idle();expect(dialog()).to_have_count(0);expect(field()).to_have_value('');assert not record();f.checked('published baseline discards unapplied declaration input on a read-only reread without approval')
   else:{'normal':normal,'failure':failure,'late':lambda:late(browser),'conflict':conflict,'scope':lambda:scope(browser)}[mode]()
   f.original();assert not f.errors and not f.external,(f.errors,f.external);assert not ({'saveDraft','saveEditorView','reviewDraft','confirmDraft','runProject','startAI'}|({'editDeclaration','editViewDeclaration'}if mode!='conflict'else set())).intersection(r.get('endpoint')for r in f.requests);page.screenshot(path=str(f.root/('declaration-reload-'+mode+'.png')));page.close();browser.close()
  except Exception:
   try:page.screenshot(path=str(f.root/'failure.png'));(f.root/'failure.html').write_text(page.content())
   except Exception:pass
   raise
except Exception as error:(f.root/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:f.save_evidence();f.stop()
print('DECLARATION_RELOAD_FIXTURE',f.root,flush=True)
