"""Resume only an isolated failed three-view fixture; verify cancel without resetting its data."""
import json,os,pathlib,signal,subprocess,sys,time,urllib.request
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());case=pathlib.Path(sys.argv[3]).resolve();assert case.parent==pathlib.Path('/tmp') and case.name.startswith('confectory-element-reentry-') and (case/'failure.json').is_file()
project=case/'owned project';original={p:p.read_bytes() for p in project.iterdir() if p.is_file()};env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(case/'profile'),CONFECTORY_ENTRY_STORAGE=str(case/'profile'),CONFECTORY_MCP_DIRECTORY=str(case/'status-retry-instances'),CONFECTORY_WEB_PROJECT=str(project/'project.cproj'),CONFECTORY_DOTNET='/workspace/toolchains/dotnet-10.0.401/dotnet');env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];log=(case/'status-retry.log').open('w');host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);errors=[];traffic=[]
def observe(response):
 try:
  data=response.request.post_data_json
  if not isinstance(data,dict):return
  if data.get('op')=='invoke':traffic.append({'invoke':data})
  elif data.get('op')=='update':
   for result in response.json().get('results',[]):traffic.append({'result':result})
 except Exception:pass
injected=0
try:
 for _ in range(600):
  urls=[s.split(' ',1)[1] for s in (case/'status-retry.log').read_text().splitlines() if s.startswith('CONFECTORY_WEB_UI ')]
  if urls:url=urls[-1];origin,token=url.split('/#');break
  assert host.poll() is None;time.sleep(.05)
 else:raise AssertionError('startup timeout')
 def route(r):
  global injected
  if not r.request.url.startswith(origin+'/'):r.abort();return
  body=r.request.post_data_json if r.request.method=='POST' else None
  if isinstance(body,dict) and body.get('op')=='invoke' and body.get('endpoint')=='browserDrafts' and body.get('input')=={'action':'status','ids':['Owned.Elements::Slime']} and injected<3:
   assert body['expectedRevision']>0;body['expectedRevision']-=1;injected+=1;r.continue_(post_data=json.dumps(body));return
  r.continue_()
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page(viewport={'width':2700,'height':1500});page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',observe);page.route('**/*',route);goto_editor(page,url)
  def w(slot):return page.locator('.window[data-key="editor-'+str(slot)+'"]')
  def hp(slot):return w(slot).locator('[aria-label="HP 기본값"]')
  error=w(1).locator('[data-element-error]');expect(hp(1)).to_have_value('111',timeout=60000);expect(error).to_contain_text('변경 상태를 확인하지 못했어요',timeout=30000);assert injected==3;assert 'stale_revision' not in error.text_content();assert not errors,errors;expect(hp(2)).to_have_value('225');expect(hp(3)).to_have_value('225');page.screenshot(path=str(case/'safe-status-failure.png'));print('PASS three real transport admission rejections show accurate Korean read failure while all owned inputs remain',flush=True)
  for slot in [1,2,3]:
   if w(slot).is_visible() and 'window-document' not in (w(slot).get_attribute('class') or ''):w(slot).locator('[data-close]').click()
  page.locator('[data-window-tab="browser:project:mobile"]').click();b=page.locator('.window[data-key="browser:project:mobile"]');q=b.locator('[data-browser-control="object-query"]');expect(q).to_be_enabled();q.fill('Slime');b.locator('[data-browser-control="object-search"]').click();b.locator('[data-object="Owned.Elements::Slime"]').get_by_role('button',name='정의 열기',exact=True).click();expect(error).to_have_text('',timeout=30000);expect(hp(1)).to_have_value('111');expect(hp(2)).to_have_value('225');expect(hp(3)).to_have_value('225');page.evaluate('()=>confectoryFlushPresentation()');requests={x['invoke']['requestId']:x['invoke'] for x in traffic if 'invoke' in x};results={x['result']['requestId']:x['result'] for x in traffic if 'result' in x};success=[results[k] for k,q in requests.items() if q.get('endpoint')=='browserDrafts' and q.get('input')=={'action':'status','ids':['Owned.Elements::Slime']} and results.get(k,{}).get('ok')];assert success;assert injected==3;assert all(p.read_bytes()==text for p,text in original.items());assert all(not text.strip() for text in page.locator('[data-element-error]').all_text_contents());assert not errors,errors;page.screenshot(path=str(case/'safe-status-recovered.png'));record={'actualEngine':True,'fixtureReusedWithoutReset':True,'injectedTransportRejections':injected,'checks':['bounded background failure remains visible in Korean, not as raw protocol error or claimed success','explicit original document reentry performs new successful status validation before clearing the banner','Slime111 and both Monster225 values plus original source bytes remain unchanged'],'errors':errors,'nativeWindows':False,'actualCredentialsOrInference':False};(case/'status-retry-evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False,indent=2));browser.close()
finally:
 if host.poll() is None:os.killpg(host.pid,signal.SIGTERM);host.wait(timeout=15)
 log.close()
