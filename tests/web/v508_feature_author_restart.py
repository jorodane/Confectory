"""Cold pending-input restoration in a previously compiler-confirmed OWNED element fixture.
No account/grant/model invocation. Preserves source bytes and original draft proof.
"""
import json,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());fixture=pathlib.Path(sys.argv[3]).resolve();assert fixture.parent==pathlib.Path('/tmp') and fixture.name.startswith('confectory-feature-author-')
case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-feature-author-restart-'));project=case/'owned project';shutil.copytree(fixture/'owned project',project,ignore=shutil.ignore_patterns('.confectory','.build'));storage=case/'profile';storage.mkdir();original={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file() and '.confectory' not in p.parts};id='Owned.Elements::Spell';text='9223372036854775804';description='재시작할 미적용 설명 한글';env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(storage),CONFECTORY_ENTRY_STORAGE=str(storage),CONFECTORY_MCP_DIRECTORY=str(case/'instances'),CONFECTORY_WEB_PROJECT=str(project/'project.cproj'),CONFECTORY_DOTNET=env.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet'));env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];host=None;log=None;errors=[];external=[];checks=[]
def stop():
 global host,log
 if host and host.poll() is None:os.killpg(host.pid,signal.SIGTERM)
 if host:host.wait(timeout=15)
 if log:log.close()
def start(i):
 global host,log,origin,token,url
 file=case/f'host-{i}.log';log=file.open('w');host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 for _ in range(600):
  urls=[l.split(' ',1)[1] for l in file.read_text().splitlines() if l.startswith('CONFECTORY_WEB_UI ')]
  if urls:url=urls[-1];origin,token=url.split('/#');return
  assert host.poll() is None,file.read_text()[-1000:];time.sleep(.05)
 raise AssertionError('startup timeout')
def raw(body):return json.load(urllib.request.urlopen(urllib.request.Request(origin+'/api/request',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':token}),timeout=30))
def mount():
 for _ in range(300):
  v=raw({'op':'mount'})
  if v.get('ok'):return v
  assert v.get('error',{}).get('code')=='busy',v;time.sleep(.02)
 raise AssertionError('busy transport')
def state():
 v=mount()
 try:return v['state']
 finally:raw({'op':'dispose','view':v['view']})
def invoke(endpoint,body,success=True):
 for _ in range(4):
  v=mount();rid=uuid.uuid4().hex
  try:
   assert raw({'op':'invoke','view':v['view'],'scope':v['scope'],'expectedRevision':v['revision'],'requestId':rid,'endpoint':endpoint,'input':body})['ok']
   for _ in range(600):
    u=raw({'op':'update','view':v['view'],'scope':v['scope']});rows=[r for r in u.get('results',[]) if r['requestId']==rid]
    if rows:break
    time.sleep(.01)
   assert rows
   if rows[0].get('error',{}).get('code')=='stale_revision':continue
   assert bool(rows[0].get('ok')) is success,rows;return {'result':rows[0],'state':u.get('state')}
  finally:raw({'op':'dispose','view':v['view']})
 raise AssertionError('admission failed')
traffic=[];injected=0

def checked(text):
 checks.append(text);(case/'progress.json').write_text(json.dumps(checks,indent=2));print('PASS '+text,flush=True)
def observe(response):
 try:
  request=response.request.post_data_json
  if not isinstance(request,dict):return
  if request.get('op')=='invoke':traffic.append({'invoke':request})
  elif request.get('op')=='update':
   for result in response.json().get('results',[]):
    if not any(row.get('result',{}).get('requestId')==result['requestId'] for row in traffic):traffic.append({'result':result})
 except Exception:pass

def route(request):
 global injected
 if not request.request.url.startswith(origin):external.append(request.request.url);request.abort();return
 body=request.request.post_data_json if request.request.method=='POST' else None
 if isinstance(body,dict) and body.get('op')=='invoke' and body.get('endpoint')=='reviewDraft' and False:
  # Actual server rejects an explicitly stale transport revision before execution.
  injected+=1;body['expectedRevision']-=1;request.continue_(post_data=json.dumps(body));return
 request.continue_()

def setup():
 page=browser.new_page(viewport={'width':1280,'height':900});page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',observe);page.route('**/*',route);goto_editor(page,url);return page

def settled():
 expect(w.locator('[data-feature-action=save]')).to_be_enabled(timeout=30000)
 for _ in range(600):
  s=state();d=s.get('declaration')
  if d and d['id']==id and d['revision']==s['draft']['revision']:return s
  page.wait_for_timeout(20)
 raise AssertionError('feature inspect did not settle')
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(0);page=setup();page.locator('#workspace').click(button='right',position={'x':700,'y':300});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=page.locator('.window[data-key^="browser:project:"]');b.locator('[data-tab=feature]').click();row=b.locator('[data-object="'+id+'"]');expect(row).to_be_visible(timeout=30000);row.get_by_role('button',name='정의 열기',exact=True).click();w=page.locator('.window[data-key=declaration]');expect(w.locator('[data-function-write-direct]')).to_be_visible(timeout=30000);w.locator('[data-function-write-direct]').click();author=page.locator('.window[data-key=blueprint]');expect(author.locator('.bp-function-card')).to_have_count(1,timeout=30000);description=author.locator('[data-inline-description]');description.fill('재시작 의도 한글');author.locator('[data-internal-code]').click();script=page.get_by_role('dialog',name='C# Script · body',exact=True);code=script.locator('[data-code-source]');code.evaluate("(el,d)=>el.setSelectionRange(el.value.indexOf(d[0])+3,el.value.lastIndexOf(d[1]))", ["\n{\n", "\n}\n"]);page.keyboard.insert_text('return 8;\n');script.locator('[data-code-save]').click();invoke('select',{'id':'Owned.Elements::Main'});page.wait_for_function("()=>typeof confectoryFlushPresentation==='function'");page.evaluate('async()=>await confectoryFlushPresentation()');s=state();assert s['draft']['id']=='Owned.Elements::Main';key=s['projectId']+'|v508-author|'+id+'|';pending=[(k,v) for k,v in s['presentation']['inputs']['blueprint'] if k.startswith(key)];assert len(pending)==2,pending;assert all((project/k).read_bytes()==v for k,v in original.items());page.close();stop()
  start(1);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('.blueprint-editor')).to_be_visible(timeout=30000);expect(author.locator('[data-inline-description]')).to_have_value('재시작 의도 한글',timeout=30000);page.wait_for_function("()=>typeof confectoryFlushPresentation==='function'");page.evaluate('async()=>await confectoryFlushPresentation()');s=state();assert s['draft']['id']=='Owned.Elements::Main',s['draft'];assert [(k,v) for k,v in s['presentation']['inputs']['blueprint'] if k.startswith(key)]==pending;checked('cold restart restores original author frame with exact private intent/body/source proof while keeping a different primary selection')
  author.locator('[data-internal-code]').click();script=page.get_by_role('dialog',name='C# Script · body',exact=True);expect(script.locator('[data-code-source]')).to_contain_text('');assert 'return 8;' in script.locator('[data-code-source]').input_value();script.locator('[data-code-cancel]').click();author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_have_text('저장됨',timeout=30000);s=state();rows=invoke('blueprint',{'action':'list','feature':id})['result']['result']['rows'];graph=invoke('blueprint',{'action':'read','id':rows[0]['id']})['result']['result'];assert graph['nodes'][0]['intent']=='재시작 의도 한글';assert graph['nodes'][0]['source'].strip()=='return 8;';assert all((project/k).read_bytes()==v for k,v in original.items());checked('restored private code and intent save through current server receipts without implicit source rebase or final file changes')
  author.locator('[data-inline-description]').fill('충돌 뒤 입력 보존');fresh=invoke('blueprint',{'action':'read','id':graph['id']})['result']['result'];invoke('blueprint',{'action':'source','id':graph['id'],'basis':fresh['basis'],'node':'body','text':'return 9;'});mark=len(traffic);author.locator('[data-bp-save]').click();expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);expect(author.locator('[data-inline-description]')).to_have_value('충돌 뒤 입력 보존');latest=invoke('blueprint',{'action':'read','id':graph['id']})['result']['result'];assert latest['nodes'][0]['source']=='return 9;';assert latest['nodes'][0]['intent']=='재시작 의도 한글';assert all((project/k).read_bytes()==v for k,v in original.items());failed=[r for r in traffic[mark:] if r.get('result',{}).get('ok') is False];assert failed,traffic[mark:];checked('concurrent source mutation rejects stale author intent save, retaining user input and newer shared body without retrying source CAS or writing files')
  # Simulate owner lifecycle retirement while a modal has unsaved text: preserve it under its captured owner.
  author.locator('[data-internal-code]').click();script=page.get_by_role('dialog',name='C# Script · body',exact=True);code=script.locator('[data-code-source]');code.evaluate("(el,d)=>el.setSelectionRange(el.value.indexOf(d[0])+3,el.value.lastIndexOf(d[1]))", ["\n{\n", "\n}\n"]);page.keyboard.insert_text('return 10;\n');author.evaluate('el=>el.hidden=true');expect(script).to_have_count(0,timeout=10000);page.wait_for_function("()=>!document.querySelector('#app')?.inert");page.evaluate('async()=>await confectoryFlushPresentation()');s=state();kept=[v for k,v in s['presentation']['inputs']['blueprint'] if k==key+'body|source'];assert len(kept)==1 and 'return 10;' in kept[0]['text'];assert all((project/k).read_bytes()==v for k,v in original.items());checked('simulated owner hide closes Script modal and releases inert while preserving unsaved text under original owner/proof; no source write or scope transfer')
  page.close();stop();browser.close();assert not errors and not external,(errors,external)
except Exception:
 try:(case/'traffic.json').write_text(json.dumps(traffic,indent=2));(case/'failure-state.json').write_text(json.dumps(state(),indent=2));(case/'errors.json').write_text(json.dumps(errors))
 except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case));raise
finally:stop()
record={'checks':checks,'errors':errors,'external':external,'actualEngine':True,'accountOrInference':False,'nativeWindows':False,'sourcePreserved':True,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
