"""Real engine/Chromium bootstrap faults. No substituted API replies.

Only named requests are aborted/delayed. A bootstrap error is not a schema
diagnosis; no source, draft, execution or permission operation is retried.
"""
import json,sys,traceback
from playwright.sync_api import sync_playwright,expect
import v666_finder_content_fixture as f

mode=sys.argv[3];page=None;events=[];posts=[];faults=[];errors=[]
saved='초기화 복구 · 저장된 입력 😀';live='다른 창의 아직 저장하지 않은 입력 😀'
blocked={'module':False,'mount':False};delayed=[]
def instrument(target):
 def intercept(route):
  request=route.request
  if not request.url.startswith(f.origin+'/'):raise AssertionError('Unexpected external request')
  body=request.post_data_json if request.method=='POST' else None
  if body is not None:posts.append(dict(page=id(target),body=body))
  if blocked['module'] and request.url==f.origin+'/v508-views.js':
   faults.append('module');route.abort('failed');return
  if blocked['mount'] and isinstance(body,dict) and body.get('op')=='mount':
   faults.append('mount');route.abort('failed');return
  route.continue_()
 target.route('**/*',intercept)
 target.on('pageerror',lambda error:errors.append(str(error)))
 target.on('requestfailed',lambda request:events.append(dict(path=request.url.removeprefix(f.origin).split('#')[0],failure=request.failure)))
def source_guard():
 f.original();assert f.host.poll() is None
 assert not errors,errors
 prohibited={'editDraft','saveDraft','reviewDraft','confirmDraft','startAI','prepareWorker','runProject','editDefinition','editDeclaration','editFunctionContract'}
 assert not prohibited.intersection(row['body'].get('endpoint')for row in posts),posts
def panel():
 expect(page.locator('[data-bootstrap-failure="empty"]')).to_be_visible()
 expect(page.get_by_role('heading',name='작업실을 불러오지 못했어요')).to_be_visible()
 expect(page.get_by_role('button',name='다시 불러오기',exact=True)).to_be_enabled()
 assert page.locator('#app').evaluate('element=>element.childElementCount')==1
 assert f.token not in page.locator('body').inner_text()
 assert not page.locator('body').inner_text().lower().count('type')
def ready():
 expect(page.locator('.work-body')).to_be_visible(timeout=20000)
 expect(page.locator('#chat-input')).to_have_value(saved)
 expect(page.locator('[data-bootstrap-failure]')).to_have_count(0)
 source_guard()

try:
 f.start(0)
 with sync_playwright() as pw:
  expect.set_options(timeout=20000)
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
  healthy=f.setup(browser)
  # The first state callback renders .work-body before the top-level helper
  # read settles and registers this explicit flush hook. Wait for the hook
  # this fixture uses, rather than treating a drawn frame as completed startup.
  healthy.wait_for_function('()=>typeof globalThis.confectoryFlushPresentation==="function"')
  healthy.locator('#chat-input').fill(saved);healthy.evaluate('()=>confectoryFlushPresentation()')
  expect(healthy.locator('#chat-input')).to_have_value(saved)
  healthy.locator('#chat-input').fill(live)
  # Hold the ordinary debounce in this healthy window: it must keep its DOM
  # input even while the second document cannot initialize.
  healthy.evaluate('()=>{window.__bootstrapInput=document.querySelector("#chat-input");}')
  page=browser.new_page(viewport={'width':1440,'height':1000});instrument(page)
  if mode in ['normal','lifecycle']:
   blocked['module']=True;page.goto(f.url,wait_until='load');panel();source_guard()
   assert len(faults)==1 and not posts,(faults,posts)
   page.wait_for_timeout(500);assert len(faults)==1 and not posts
   expect(healthy.locator('#chat-input')).to_have_value(live)
   assert healthy.evaluate('()=>window.__bootstrapInput===document.querySelector("#chat-input")')
   f.checked('one failed real module request shows a bounded recovery screen, no mount/mutation or automatic retry, and preserves the other window input/DOM')
   if mode=='lifecycle':
    page.get_by_role('button',name='다시 불러오기',exact=True).focus();page.keyboard.press('Enter');panel()
    assert len(faults)==2 and not posts
    page.close();page=browser.new_page(viewport={'width':1440,'height':1000});instrument(page);page.goto(f.url,wait_until='load');panel()
    assert len(faults)==3 and not posts
    f.checked('keyboard retry creates one new document; repeated failure and close/reopen remain read-only without duplicate initialization')
   # Persisted private state is restored by the established owner. Close the
   # healthy page first so its ordinary input debounce cannot race this check.
   healthy.locator('#chat-input').fill(saved);healthy.evaluate('()=>confectoryFlushPresentation()');healthy.close()
   blocked['module']=False;page.get_by_role('button',name='다시 불러오기',exact=True).click();ready()
   mounts=[row for row in posts if row['body'].get('op')=='mount'];assert len(mounts)==1,mounts
   f.checked('explicit full-document retry restores the existing private input with one real mount and no source/Task/Review replay')
   if mode=='lifecycle':
    page.close();f.stop();f.start(1);page=browser.new_page(viewport={'width':1440,'height':1000});instrument(page)
    from editor_navigation import goto_editor
    goto_editor(page,f.url);ready();f.checked('cold actual-engine restart restores saved state with a fresh session after failed/repeated/recovered bootstrap')
  elif mode=='partial':
   healthy.locator('#chat-input').fill(saved);healthy.evaluate('()=>confectoryFlushPresentation()');healthy.close();blocked['mount']=True;page.goto(f.url,wait_until='load')
   expect(page.locator('#status[data-bootstrap-failure="partial"]')).to_have_text('화면 초기화를 마치지 못했어요. 입력을 확인한 뒤 창을 새로고침해 주세요.')
   expect(page.locator('#toast')).to_have_class('show')
   expect(page.locator('.welcome[data-startup-ready="true"]')).to_be_visible()
   expect(page.locator('[data-bootstrap-failure="empty"]')).to_have_count(0)
   expect(page.get_by_role('button',name='다시 불러오기',exact=True)).to_have_count(0)
   snapshot=page.locator('#app').inner_html();page.wait_for_timeout(500)
   assert page.locator('#app').inner_html()==snapshot
   assert faults==['mount'] and len(posts)==1,(faults,posts)
   source_guard();f.checked('a failed real mount after render keeps the original owner DOM and shows a neutral diagnostic; no reset/retry button or automatic mount replay')
   blocked['mount']=False;page.close();page=browser.new_page(viewport={'width':1440,'height':1000});instrument(page)
   from editor_navigation import goto_editor
   goto_editor(page,f.url);ready();f.checked('a separately reopened document initializes normally after partial startup transport failure')
  elif mode=='retired':
   healthy.locator('#chat-input').fill(saved);healthy.evaluate('()=>confectoryFlushPresentation()');healthy.close()
   def hold(route):delayed.append(route)
   page.route(f.origin+'/v508-views.js',hold)
   page.goto(f.url,wait_until='commit');page.wait_for_function('()=>document.querySelector("#app")!==null')
   for _ in range(200):
    if delayed:break
    page.wait_for_timeout(10)
   assert len(delayed)==1
   # Retire the old document while its actual module request is pending. The
   # old import catch must not append an error to the replacement document.
   page.goto('about:blank');page.unroute(f.origin+'/v508-views.js',hold)
   try:delayed[0].abort('failed')
   except Exception:pass # a navigated-away request may already be cancelled
   page.wait_for_timeout(200);assert page.locator('[data-bootstrap-failure]').count()==0
   from editor_navigation import goto_editor
   goto_editor(page,f.url);ready();f.checked('pagehide during a pending real dependency request cannot publish a late failure into the next document or replay initialization')
  else:raise AssertionError(mode)
  source_guard();page.screenshot(path=str(f.root/('bootstrap-'+mode+'.png')));browser.close()
except Exception as error:
 if page:
  try:page.screenshot(path=str(f.root/'failure.png'));(f.root/'failure.html').write_text(page.content())
  except Exception:pass
 (f.root/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc()),ensure_ascii=False,indent=2));raise
finally:
 f.stop();f.save_evidence();(f.root/'bootstrap.json').write_text(json.dumps(dict(mode=mode,checks=f.checks,faults=faults,events=events,posts=posts,errors=errors,actualManagedEngine=True,substitutedAPIReplies=False,actualWindows=False,wholeUI=False),ensure_ascii=False,indent=2))
