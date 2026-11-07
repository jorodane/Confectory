"""Real editor reload/cold/project isolation with stalled owned HTTP peers.

The slow client is an actual socket, not a substituted API reply. This reproduces
transport starvation separately from the earlier unexplained empty-app incident.
"""
import json,socket,sys,time,traceback,urllib.parse
from playwright.sync_api import sync_playwright,expect
import v666_finder_content_fixture as f
page=None;peers=[];timings=[];mode=sys.argv[3];events=[]
def ready():
 page.wait_for_selector('.work-body',timeout=10000)
 expect(page.locator('#workspace')).to_have_attribute('data-office-renderer','ready',timeout=10000)
 expect(page.locator('#chat-input')).to_have_value('초기화 검사 · 보존할 입력 😀')
 f.original();assert f.host.poll()is None
def peer(partial=False):
 address=urllib.parse.urlsplit(f.origin);s=socket.socket();s.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,1024);s.settimeout(3);s.connect((address.hostname,address.port));peers.append(s)
 if partial:s.sendall(('POST /api/request HTTP/1.1\r\nHost: '+address.netloc+'\r\nX-Confectory-Session: '+f.token+'\r\nContent-Length: 1024\r\n\r\n{').encode())
 else:s.sendall(('GET /assets/tori-bust.png HTTP/1.1\r\nHost: '+address.netloc+'\r\nConnection: keep-alive\r\n\r\n').encode()*6)
 return s
def retire(s):s.close();peers.remove(s)
def instrument():
 page.on('requestfailed',lambda request:events.append(dict(kind='requestfailed',url=request.url.split('#')[0],failure=request.failure)))
 page.on('console',lambda message:events.append(dict(kind='console',level=message.type,message=message.text[:600]))if message.type=='error'else None)
def guards():
 f.original();assert not f.errors and not f.external,(f.errors,f.external)
 assert not {'editDraft','saveDraft','reviewDraft','confirmDraft','startAI','prepareWorker','runProject','editDefinition','editDeclaration','editFunctionContract'}.intersection(r.get('endpoint')for r in f.requests)
try:
 f.env['CONFECTORY_WEB_PROJECT']=str(f.projects[1]);f.start(0);second=f.state()['listingId'];f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(f.projects[0]);f.start(1)
 with sync_playwright()as pw:
  expect.set_options(timeout=30000);browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']);page=f.setup(browser);instrument();first=f.state()['listingId']
  page.get_by_role('button',name='아이소메트릭 Workspace',exact=True).click();expect(page.locator('#workspace')).to_have_attribute('data-office-renderer','ready');page.locator('#chat-input').fill('초기화 검사 · 보존할 입력 😀');page.evaluate('()=>confectoryFlushPresentation()')
  value=f.state()['presentation'];child='startup-owned-child';value['workspaces'].append(dict(id=child,name='Startup owned child',parentId='root',layout=[],view=dict(x=0,y=0,scale=1),items=[]));value['visitedWorkspaceTabs'].append(child);f.call('savePresentation',dict(presentation=value))
  slow=peer();partial=peer(True);time.sleep(.2)
  for number in range(8 if mode=='normal'else 4):
   start=time.monotonic();page.reload();ready();timings.append(dict(reload=number+1,seconds=time.monotonic()-start,appChildren=page.locator('#app').evaluate('el=>el.childElementCount')))
  guards();f.checked('actual 3D/root-child reloads initialize while another real image client and partial authenticated POST stop reading/sending; private chat and original sources survive')
  retire(slow);retire(partial);page.reload();ready();guards();f.checked('disconnect after stalled transfers preserves the live host and next reload without replaying source/Task/Review operations')
  page.locator('#workspace-tab-'+child).click();page.get_by_role('tab',name='Workspace',exact=True).click();ready();f.call('leaveProject',{});page.wait_for_selector('.home-grid');f.call('openProject',{'id':second});page.wait_for_selector('.work-body');expect(page.locator('#chat-input')).not_to_have_value('초기화 검사 · 보존할 입력 😀');f.call('leaveProject',{});page.wait_for_selector('.home-grid');f.call('openProject',{'id':first});ready();guards();f.checked('child/root and project A/B/A navigation preserves private owner isolation after transport interruption')
  page.close();f.stop();f.start(2);page=f.setup(browser);instrument();ready();guards();page.screenshot(path=str(f.root/'startup-cold.png'));f.checked('new actual engine restores the exact private input/3D view with a fresh session; original sources and execution/confirmation boundaries remain unchanged');browser.close()
except Exception as error:
 if page:
  try:page.screenshot(path=str(f.root/'failure.png'));(f.root/'failure.html').write_text(page.content())
  except Exception:pass
 (f.root/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc()),ensure_ascii=False,indent=2));raise
finally:
 for s in peers:s.close()
 f.stop();f.save_evidence();(f.root/'startup-transport.json').write_text(json.dumps(dict(mode=mode,timings=timings,events=events,checks=f.checks,realHTTP=True,substitutedReplies=False,actualManagedEngine=True,actualWindows=False,actualMobile=False,wholeUI=False),ensure_ascii=False,indent=2))
