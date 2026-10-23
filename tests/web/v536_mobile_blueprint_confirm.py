"""Resume only an isolated failed three-view fixture; verify cancel without resetting its data."""
import json,os,pathlib,signal,subprocess,sys,time,urllib.request
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());case=pathlib.Path(sys.argv[3]).resolve();assert case.parent==pathlib.Path('/tmp') and case.name.startswith('confectory-mobile-blueprint-') and (case/'failure.json').is_file()
project=case/'owned project';original={p:p.read_bytes() for p in project.rglob('*') if p.is_file() and '.confectory' not in p.parts and '.build' not in p.parts};env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(case/'profile'),CONFECTORY_ENTRY_STORAGE=str(case/'profile'),CONFECTORY_MCP_DIRECTORY=str(case/'confirm-mobile-instances'),CONFECTORY_WEB_PROJECT=str(project/'project.cproj'),CONFECTORY_DOTNET='/workspace/toolchains/dotnet-10.0.401/dotnet');env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];log=(case/'confirm-mobile.log').open('w');host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);errors=[];traffic=[]
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
  urls=[s.split(' ',1)[1] for s in (case/'confirm-mobile.log').read_text().splitlines() if s.startswith('CONFECTORY_WEB_UI ')]
  if urls:url=urls[-1];origin,token=url.split('/#');break
  assert host.poll() is None;time.sleep(.05)
 else:raise AssertionError('startup timeout')
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);context=browser.new_context(viewport={'width':390,'height':844},has_touch=True,is_mobile=True);page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',observe);page.route('**/*',lambda r:r.continue_() if r.request.url.startswith(origin+'/') else r.abort());goto_editor(page,url);author=page.locator('.window[data-key=blueprint]');flow=author.locator('[aria-label="카드 흐름 편집"]');expect(flow).to_be_visible(timeout=60000);flow.locator('[data-flow-graph]').click();expect(flow).to_be_hidden();author.locator('[data-mobile-flow]').click();expect(flow).to_be_visible();cold='재시작 전 미저장 입력 🧁';body=flow.locator('[data-flow-node="body"]');expect(body).to_contain_text(cold);body.click();inspector=page.locator('.bp-flow-inspector:not([hidden])');expect(inspector.locator('[data-flow-node-description]')).to_have_value(cold);page.screenshot(path=str(case/'touch-inspector.png'));geometry={'inspector':inspector.bounding_box(),'header':inspector.locator('header').bounding_box(),'host':flow.bounding_box(),'tabs':flow.locator('.bp-flow-tabs').bounding_box()};assert geometry['host']=={'x':0,'y':112,'width':390,'height':732},geometry;assert geometry['inspector']=={'x':0,'y':0,'width':390,'height':844} and geometry['header']['height']==58,geometry;(case/'touch-geometry.json').write_text(json.dumps(geometry,indent=2));inspector.locator('[data-flow-code]').click();script=page.get_by_role('dialog',name='C# Script · body',exact=True);expect(script).to_be_visible();code=script.locator('[data-code-source]');assert 'return seed + other;' in code.input_value();script.locator('[data-code-save]').click();expect(script).to_have_count(0);inspector.locator('[data-flow-back]').click();author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_have_text('저장됨',timeout=60000);assert all(p.read_bytes()==text for p,text in original.items());print('PASS mobile original Script explicit save acknowledges body for changed intent without source write or bypassing stale-body guard',flush=True)
  author.locator('[data-bp-complete]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=60000);assert all(p.read_bytes()==text for p,text in original.items());review.locator('[data-reject]').click();page.locator('[data-window-tab="blueprint"]').click();expect(flow).to_be_visible(timeout=10000);expect(flow.locator('[data-flow-node="body"]')).to_contain_text(cold);print('PASS cancelling Review then original Blueprint tab reentry restores the same mobile editing surface and source ownership',flush=True);author.locator('[data-bp-complete]').click();expect(review).to_be_visible(timeout=60000)
  for cb in review.locator('[data-review-id]').all():cb.check()
  if review.locator('[data-additional-changes]').count():
   review.locator('[data-review-advanced]').click();ack=review.locator('[data-advanced-reviewed]')
   if ack.count():ack.check()
  expect(review.locator('#confirm')).to_be_enabled(timeout=30000);review.locator('#confirm').click();expect(review).to_have_count(0,timeout=60000);changed=[str(p.relative_to(project)) for p,text in original.items() if p.read_bytes()!=text];assert changed and all(name.startswith('blueprints/') for name in changed),changed;graph=json.loads(next((project/'blueprints').glob('*.graph.json')).read_text());assert next(n for n in graph['nodes'] if n['id']=='body')['intent']==cold;assert not errors,errors;result={'actualEngine':True,'fixtureReusedWithoutReset':True,'touchEmulation':True,'checks':['stale body guard requires explicit existing Script acknowledgement','Review cancellation and original tab reentry preserve mobile editor','explicit selected compiler Confirm writes only owned graph changes'],'changedFiles':changed,'errors':errors,'nativeWindowsOrMobileHardware':False,'actualCredentialsOrInference':False};(case/'confirm-mobile-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2));browser.close()
except Exception:
 (case/'confirm-mobile-failure.json').write_text(json.dumps({'traffic':traffic,'errors':errors},ensure_ascii=False,indent=2))
 try:page.screenshot(path=str(case/'confirm-mobile-failure.png'))
 except Exception:pass
 raise
finally:
 if host.poll() is None:os.killpg(host.pid,signal.SIGTERM);host.wait(timeout=15)
 log.close()
