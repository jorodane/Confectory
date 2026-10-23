"""Resume only an isolated failed three-view fixture; verify cancel without resetting its data."""
import json,os,pathlib,signal,subprocess,sys,time,urllib.request
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());case=pathlib.Path(sys.argv[3]).resolve();assert case.parent==pathlib.Path('/tmp') and case.name.startswith('confectory-element-instances-') and (case/'failure.json').is_file()
project=case/'owned project';original={p:p.read_bytes() for p in project.iterdir() if p.is_file()};env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(case/'profile'),CONFECTORY_ENTRY_STORAGE=str(case/'profile'),CONFECTORY_MCP_DIRECTORY=str(case/'cancel-instances'),CONFECTORY_WEB_PROJECT=str(project/'project.cproj'),CONFECTORY_DOTNET='/workspace/toolchains/dotnet-10.0.401/dotnet');env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];log=(case/'cancel-recheck.log').open('w');host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);errors=[];traffic=[]
def observe(response):
 try:
  data=response.request.post_data_json
  if not isinstance(data,dict):return
  if data.get('op')=='invoke':traffic.append({'invoke':data})
  elif data.get('op')=='update':
   for result in response.json().get('results',[]):traffic.append({'result':result})
 except Exception:pass
try:
 for _ in range(600):
  urls=[s.split(' ',1)[1] for s in (case/'cancel-recheck.log').read_text().splitlines() if s.startswith('CONFECTORY_WEB_UI ')]
  if urls:url=urls[-1];origin,token=url.split('/#');break
  assert host.poll() is None;time.sleep(.05)
 else:raise AssertionError('startup timeout')
 def state():
  def send(body):return json.load(urllib.request.urlopen(urllib.request.Request(origin+'/api/request',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':token}),timeout=20))
  for _ in range(300):
   value=send({'op':'mount'})
   if value.get('ok'):break
   assert value.get('error',{}).get('code')=='busy';time.sleep(.02)
  try:return value['state']
  finally:send({'op':'dispose','view':value['view']})
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page(viewport={'width':2700,'height':1500});page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',observe);page.route('**/*',lambda r:r.continue_() if r.request.url.startswith(origin+'/') else r.abort());goto_editor(page,url)
  def hp(slot):return page.locator('.window[data-key="editor-'+slot+'"] [aria-label="HP 기본값"]')
  expect(hp('1')).to_have_value('111',timeout=60000);expect(hp('2')).to_have_value('222');expect(hp('3')).to_have_value('333');before=state();assert len(before['editorViews'])==3;page.locator('.window[data-key="editor-2"] [data-element-action="discard"]').click();page.evaluate('()=>confectoryFlushPresentation()');snapshot={'dom':page.locator('.window[data-key="editor-2"]').inner_text(),'error':page.locator('.window[data-key="editor-2"] [data-element-error]').text_content(),'state':state(),'traffic':traffic};(case/'cancel-diagnostic.json').write_text(json.dumps(snapshot,ensure_ascii=False,indent=2));print('CANCEL ERROR '+snapshot['error'],flush=True);expect(hp('2')).to_have_value('111',timeout=6000);expect(hp('3')).to_have_value('333');page.evaluate('()=>confectoryFlushPresentation()');after=state();assert len(after['editorViews'])==3;assert not [k for k,v in after['presentation']['inputs']['schema'] if '|view:2|element|' in k];assert [v for k,v in after['presentation']['inputs']['schema'] if '|view:3|element|' in k][0]['text']=='333';assert all(p.read_bytes()==text for p,text in original.items());assert not errors,errors;page.screenshot(path=str(case/'cancel-rechecked.png'));result={'actualEngine':True,'fixtureReusedWithoutReset':True,'checks':['cold stored 111/222/333 and original View proofs preserved','explicit view-two cancel reads shared saved111; view-three333 retained','view count and original source bytes unchanged'],'errors':errors,'nativeWindows':False,'actualCredentialsOrInference':False};(case/'cancel-recheck-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2));browser.close()
finally:
 if host.poll() is None:os.killpg(host.pid,signal.SIGTERM);host.wait(timeout=15)
 log.close()
