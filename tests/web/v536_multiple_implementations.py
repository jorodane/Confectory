"""Actual v536 multiple implementation contexts, C# conversion, no accounts/inference/run."""
import hashlib,json,re,os,pathlib,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-multiple-implementations-'));project=case/'owned project';project.mkdir();n='Owned.Context::'
env=os.environ.copy();env.update(CONFECTORY_DOTNET=env.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet'))
def metadata(operation,**data):
 r=subprocess.run([env['CONFECTORY_DOTNET'],str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps({'operation':operation,**data}),text=True,capture_output=True,env=env,check=True);v=json.loads(r.stdout);assert v['ok'],v;return v['result']
items={
 'Main':('function','function '+n+'Main () -> int {provide '+n+'Main with '+n+'MainBody;}'),
 'MainBody':('implementation','implementation '+n+'MainBody for '+n+'Main () -> int {import '+n+'Calc as Global (long) -> long;import '+n+'Calc as A (long) -> long in '+n+'A;import '+n+'Calc as B (long) -> long in '+n+'B;body common "Main.csbody";}'),
 'Calc':('function','function '+n+'Calc (long amount) -> long {description "같은 기능의 세 구현";provide '+n+'Calc with '+n+'Default;}'),
 'Default':('implementation','implementation '+n+'Default for '+n+'Calc (long amount) -> long {body common "Default.csbody";body windows "Windows.csbody";}'),
 'Rules':('module','module '+n+'Rules {require '+n+'Calc (long) -> long;default '+n+'Calc with '+n+'Default;}'),
 'A':('object','object '+n+'A {module '+n+'Rules;provide '+n+'Calc with '+n+'Alpha;}'),
 'B':('object','object '+n+'B {module '+n+'Rules;provide '+n+'Calc with '+n+'Beta;}')}
sources={'Main.csbody':'return checked((int)(calls.Global.Invoke(1)+calls.A.Invoke(1)+calls.B.Invoke(1)));','Default.csbody':'\ufeff// 원본 기본 구현 한글 😀\r\nreturn amount + 100;\r\n','Windows.csbody':'// 다른 실행 대상\r\nreturn amount + 200;\r\n'}
for name,code in [('Alpha','return amount+11;'),('Beta','return amount+12;')]:
 prepared=metadata('blueprintPrepareFeature',id=n+'Calc',text='function '+n+'Calc (long amount) -> long {description "같은 기능의 세 구현";}',implementation=n+name,graphPath=name+'.graph.json',nodePath=name+'.node.json');items[name]=('implementation',prepared['implementation']);definitions=metadata('featureBlueprintNodes',featureSource=items['Calc'][1],graph=prepared['graph']);record={'schema':1,'node':'body','definitionHash':next(v['definitionHash'] for v in definitions['nodes'] if v['id']=='body'),'source':code};sources[name+'.graph.json']=json.dumps(prepared['graph']);sources[name+'.node.json']=json.dumps(record)
for name,(kind,text) in items.items():sources[name+'.celem']=text
sources['project.cproj']='project Owned.Context version "1" {standalone true;entry '+n+'Main;'+''.join('element '+name+' '+kind+' "'+name+'.celem";' for name,(kind,text) in items.items())+'registry Confectory.Build.DotNet "'+str(repo/'targets/dotnet/pack.cpack')+'";dependency Confectory.Build.DotNet version "0.1.0";target portable Confectory.Build.DotNet::Portable;}'
for name,text in sources.items():(project/name).write_bytes(text.encode())
original={p.name:p.read_bytes() for p in project.iterdir()};env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(case/'profile'),CONFECTORY_ENTRY_STORAGE=str(case/'profile'),CONFECTORY_MCP_DIRECTORY=str(case/'instances'),CONFECTORY_WEB_PROJECT=str(project/'project.cproj'));env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];host=None;log=None;traffic=[];results={};errors=[];external=[];checks=[]
def stop():
 global host,log
 if host and host.poll() is None:os.killpg(host.pid,signal.SIGTERM);host.wait(timeout=15)
 if log:log.close()
def start(index):
 global host,log,url,origin,token
 f=case/f'host-{index}.log';log=f.open('w');host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 for _ in range(600):
  urls=[v.split(' ',1)[1] for v in f.read_text().splitlines() if v.startswith('CONFECTORY_WEB_UI ')]
  if urls:url=urls[-1];origin,token=url.split('/#');return
  assert host.poll() is None,f.read_text();time.sleep(.05)
 raise AssertionError('host startup')
def raw(body):return json.load(urllib.request.urlopen(urllib.request.Request(origin+'/api/request',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':token}),timeout=30))
def mount():
 for _ in range(1000):
  row=raw({'op':'mount'})
  if row.get('ok'):return row
  assert row.get('error',{}).get('code')=='busy',row;time.sleep(.02)
 raise AssertionError('mount admission deadline')
def state():
 v=mount()
 try:return v['state']
 finally:raw({'op':'dispose','view':v['view']})
def call(endpoint,body,ok=True):
 for _ in range(4):
  v=mount();rid=uuid.uuid4().hex
  try:
   assert raw({'op':'invoke','view':v['view'],'scope':v['scope'],'expectedRevision':v['revision'],'requestId':rid,'endpoint':endpoint,'input':body})['ok']
   for _ in range(12000):
    r=raw({'op':'update','view':v['view'],'scope':v['scope']});rows=[row for row in r.get('results',[]) if row['requestId']==rid]
    if rows:break
    time.sleep(.01)
   assert rows,(endpoint,r)
   if rows[0].get('error',{}).get('code')=='stale_revision':continue
   assert bool(rows[0].get('ok'))==ok,rows
   return rows[0].get('result') if ok else rows[0]
  finally:raw({'op':'dispose','view':v['view']})
 raise AssertionError('transport revision changed before execution')
def checked(message):checks.append(message);(case/'checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2));print('PASS '+message,flush=True)
def unchanged():assert all((project/k).read_bytes()==v for k,v in original.items())
def setup(browser):
 page=browser.new_page(viewport={'width':1480,'height':1050});page.on('pageerror',lambda e:errors.append(str(e)))
 def observe(response):
  try:
   body=response.request.post_data_json
   if isinstance(body,dict) and body.get('op')=='invoke':traffic.append(body)
   elif isinstance(body,dict) and body.get('op')=='update':
    for result in response.json().get('results',[]):results[result['requestId']]=result
  except Exception:pass
 page.on('response',observe);page.route('**/*',lambda r:r.continue_() if r.request.url.startswith(origin+'/') else (external.append(r.request.url),r.abort()));goto_editor(page,url);return page
def idle():expect(page.locator('.brand')).to_be_enabled(timeout=60000)
def completed(endpoint,action,mark):
 for _ in range(3000):
  requests=[r for r in traffic[mark:] if r['endpoint']==endpoint and r.get('input',{}).get('action')==action]
  rows=[results[r['requestId']] for r in requests if r['requestId'] in results]
  good=[r for r in rows if r.get('ok')]
  if good:idle();return good[-1]
  refused=[r for r in rows if r.get('error',{}).get('code')!='stale_revision'];assert not refused,refused
  page.wait_for_timeout(20)
 raise AssertionError((endpoint,action,'actual response not observed',page.get_by_role('status').all_text_contents()))
def pending():page.evaluate('async()=>await confectoryFlushPresentation()');return state()['presentation']['inputs']['blueprint']
def open_row(name,group):
 idle();page.locator('#workspace').click(button='right',position={'x':1240,'y':650});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=page.locator('.window[data-key^="browser:project:"]');b.locator('[data-tab="'+group+'"]').click();row=b.locator('[data-object="'+n+name+'"]');expect(row).to_have_attribute('aria-disabled','false');row.press('Enter');idle();b.locator('[data-close]').click();return b
def object_slot(name):
 open_row(name,'concept');w=page.locator('.window[data-key=schema]');slot=w.locator('[data-module-method="'+n+'Calc"]');expect(slot.locator('[data-function-edit]')).to_be_enabled();slot.locator('[data-function-edit]').click();author=page.locator('.window[data-key=blueprint]');expect(author).to_have_attribute('data-blueprint-owner',n+name);expect(author).to_have_attribute('data-blueprint-body',n+('Alpha' if name=='A' else 'Beta')+'/body:common');idle();expect(author.locator('[data-internal-code]')).to_be_enabled();return author
def global_feature():
 open_row('Calc','feature');w=page.locator('.window[data-key=declaration]');w.locator('[data-function-write-direct]').click();author=page.locator('.window[data-key=blueprint]');expect(author).to_have_attribute('data-blueprint-owner','');expect(author).to_have_attribute('data-blueprint-body',n+'Default/body:common');idle();expect(author.locator('[data-internal-code]')).to_be_enabled();return author
def code_dialog():
 author.locator(':scope > .window-title .caption').click(position={'x':5,'y':8});author.locator('[data-bp-overview-node=body]').click();author.locator('[data-bp-node=body] [data-internal-code]').click();return page.get_by_role('dialog',name='C# Script · body',exact=True)
def edit_code(text,flush=True):
 d=code_dialog();field=d.locator('[data-code-source]');field.evaluate('(el)=>{const spans=[...el.closest(".bp-script-editor").querySelectorAll("[data-code-highlight]>span")],part=spans.find(p=>p.dataset.codeRegion==="body"),start=spans.slice(0,spans.indexOf(part)).reduce((n,p)=>n+p.textContent.length,0);el.setSelectionRange(start,start+part.textContent.length)}');page.keyboard.insert_text(text);d.locator('[data-code-save]').click();return pending() if flush else None
def expected_keys(rows):return {key.split('|v508-author|',1)[1].rsplit('|body|source',1)[0] for key,value in rows}
try:
 start(0)
 with sync_playwright() as p:
  expect.set_options(timeout=30000);browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=setup(browser);idle();author=object_slot('A');rows=edit_code('return amount + 21;');assert len(rows)==1 and '|slot:'+n+'A:'+n+'Alpha|' in rows[0][0];author=object_slot('B');d=code_dialog();assert 'return amount+12;' in d.locator('[data-code-source]').input_value();d.locator('[data-code-cancel]').click();rows=edit_code('return amount + 22;');assert len(rows)==2;author=object_slot('A');d=code_dialog();assert 'return amount + 21;' in d.locator('[data-code-source]').input_value();d.locator('[data-code-cancel]').click();unchanged();checked('실제 객체 A/B의 같은 기능은 서로 다른 Alpha/Beta 구현을 열고 전환·Script 취소에도 두 비공개 본문을 따로 보존한다')
  author=global_feature();d=code_dialog();assert '// 원본 기본 구현 한글 😀' in d.locator('[data-code-source]').input_value(),'global feature reused a prior object slot body instead of its declared default';d.locator('[data-code-cancel]').click();assert len(pending())==2;unchanged();checked('객체 슬롯 편집 뒤 전역 기능은 그 슬롯을 재사용하지 않고 명시 provide의 기본 C# common을 읽기 전용 미리보기로 연다')
  wanted='// 전역 기본 구현 새 본문 한글 😀\nreturn amount + 101;\n';rows=edit_code(wanted);assert len(rows)==3 and any('|body:'+n+'Default/body:common|' in key for key,value in rows);page.screenshot(path=str(case/'three-implementation-contexts.png'));page.close();stop();start(1);page=setup(browser);author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-internal-code]')).to_be_enabled();assert pending()==rows;d=code_dialog();assert wanted in d.locator('[data-code-source]').input_value();d.locator('[data-code-cancel]').click();author=object_slot('B');d=code_dialog();assert 'return amount + 22;' in d.locator('[data-code-source]').input_value();d.locator('[data-code-cancel]').click();author=object_slot('A');d=code_dialog();assert 'return amount + 21;' in d.locator('[data-code-source]').input_value();d.locator('[data-code-cancel]').click();author=global_feature();d=code_dialog();assert wanted in d.locator('[data-code-source]').input_value();d.locator('[data-code-cancel]').click();unchanged();checked('실제 프로세스 재시작과 세 구현 재선택은 구현별 미저장 입력·BOM/CRLF 원본·Windows 대상과 소유 객체를 보존한다')
  # Inject only this isolated renderer's result, after the real server has completed Save.
  armed='lost';save_rid=None;lost=0;late=0;late_text=wanted+'// 저장 대기 중 새 입력\n'
  def recovery_route(request):
   global armed,save_rid,lost,late
   if not request.request.url.startswith(origin+'/'):external.append(request.request.url);request.abort();return
   body=request.request.post_data_json if request.request.method=='POST' else None
   if isinstance(body,dict) and body.get('op')=='invoke' and body.get('endpoint')=='saveDraft' and armed:save_rid=body['requestId']
   if isinstance(body,dict) and body.get('op')=='update' and save_rid:
    response=request.fetch();payload=response.json()
    for result in payload.get('results',[]):
     if result['requestId']!=save_rid or not result.get('ok'):continue
     mode=armed;armed=None;save_rid=None
     if mode=='lost':lost+=1;result['ok']=False;result.pop('result',None);result['error']={'code':'consumer_error'}
     elif mode=='late':late+=1;edit_code(late_text,flush=False)
    request.fulfill(response=response,json=payload);return
   request.continue_()
  page.unroute('**/*');page.route('**/*',recovery_route);author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_contain_text('consumer_error',timeout=60000);assert lost==1 and pending()==rows;unchanged();data=call('blueprint',{'action':'read','id':n+'Default/body:common'});assert next(row['source'] for row in data['nodes'] if row['id']=='body')==wanted;before_ids=[row['id'] for row in call('blueprint',{'action':'featureBodies','feature':n+'Calc'})['rows']];checked('다른 두 구현 입력을 남긴 실제 변환 Save의 응답 유실은 원본/대상/입력을 보존하며 서버 결과를 실패 UI와 구분한다')
  page.close();stop();start(2);page=setup(browser);author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled();assert pending()==rows;page.unroute('**/*');page.route('**/*',recovery_route);armed='late';save_rid=None;author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_contain_text('새 입력',timeout=60000);left=pending();assert late==1 and len(left)==3 and any(value.get('text')==late_text for key,value in left);assert [row['id'] for row in call('blueprint',{'action':'featureBodies','feature':n+'Calc'})['rows']]==before_ids;unchanged();checked('응답 유실 뒤 cold·명시적 재시도는 같은 변환을 확인하고 중복 생성 없이 늦은 입력과 A/B 미저장 본문을 보존한다')
  author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_have_text('저장됨',timeout=60000);left=pending();assert len(left)==2 and all('|slot:' in key for key,value in left);unchanged();data=call('blueprint',{'action':'read','id':n+'Default/body:common'});assert next(row['source'] for row in data['nodes'] if row['id']=='body')==late_text;checked('늦은 입력의 다음 Save는 Default/common만 갱신하고 다른 구현의 초안과 원본 C#/Windows 대상은 보존한다')
  def review():
   author.locator('[data-bp-complete]').click();w=page.locator('.window[data-key=review]');expect(w).to_be_visible(timeout=60000);assert state()['review']['status']=='ready';return w
  def accept(w):
   if w.locator('[data-review-advanced]').count():
    w.locator('[data-review-advanced]').click()
    if w.locator('[data-advanced-reviewed]').count():w.locator('[data-advanced-reviewed]').check()
   mark=len(traffic);w.locator('#confirm').click();result=completed('confirmGroup',None,mark);assert result['result'].get('sourceConfirmed'),state()['logs'];expect(w).to_have_count(0,timeout=90000)
  w=review();old_token=state()['review']['token'];unchanged();assert pending()==left;w.locator('[data-reject]').click();expect(w).to_be_hidden();unchanged();assert pending()==left;w=review();assert state()['review']['token']!=old_token;accept(w);assert 'blueprint common' in (project/'Default.celem').read_text();assert all((project/key).read_bytes()==value for key,value in original.items() if key!='Default.celem');original={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file() and '.confectory' not in p.parts};checked('변환 Review 취소와 새 명시적 compiler Confirm은 Default 선언/새 graph·node만 반영하며 원본 C#/Windows/A/B 구현과 두 비공개 입력을 보존한다')
  for owner,implementation,code in [('A','Alpha','return amount + 21;'),('B','Beta','return amount + 22;')]:
   author=object_slot(owner);d=code_dialog();assert code in d.locator('[data-code-source]').input_value();d.locator('[data-code-cancel]').click();author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_have_text('저장됨',timeout=60000);unchanged();data=call('blueprint',{'action':'read','id':n+implementation+'/body:common'});assert next(row['source'] for row in data['nodes'] if row['id']=='body')==code;w=review();accept(w);changed={key for key,value in original.items() if (project/key).read_bytes()!=value};assert changed=={implementation+'.node.json'},changed;original={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file() and '.confectory' not in p.parts}
  assert pending()==[];checked('같은 기능의 Alpha/Beta는 실제 UI에서 각각 저장·컴파일 확정되고 선택한 node만 변경하며 다른 구현/객체/함수/전역 변환 결과를 보존한다')
  edit_code('return amount + 33;');held=pending();call('select',{'id':n+'B'});call('schema',{'id':n+'B'});owner=state()['schema'];call('editDeclaration',{'id':n+'B','revision':owner['revision'],'hash':owner['textHash'],'edit':{'action':'provide-function','function':n+'Calc','implementation':n+'Alpha'}});author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_contain_text('입력은 유지',timeout=60000);assert pending()==held;data=call('blueprint',{'action':'read','id':n+'Beta/body:common'});assert next(row['source'] for row in data['nodes'] if row['id']=='body')=='return amount + 22;';unchanged();checked('다른 편집자가 B의 연결 구현을 바꾸면 오래된 슬롯 저장은 거절하고 새 비공개33·기존 Beta22·다른 모든 확정 소스를 보존한다')
  assert not errors and not external,(errors,external);page.close();browser.close()
except Exception:
 try:(case/'failure.json').write_text(json.dumps({'errors':errors,'state':state(),'traffic':traffic,'results':results},ensure_ascii=False,indent=2));page.screenshot(path=str(case/'failure.png'))
 except Exception:pass
 print('OWNED FAILURE '+str(case),flush=True);raise
finally:stop()
record={'checks':checks,'case':str(case),'errors':errors,'external':external,'windowsExecuted':False,'actualAccountOrInference':False};(case/'evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False),flush=True)
