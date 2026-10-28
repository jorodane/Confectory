"""Actual v536 multiple implementation contexts, C# conversion, no accounts/inference/run."""
import hashlib,json,re,os,pathlib,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-mobile-special-pins-'));project=case/'owned project';project.mkdir();n='Owned.Context::'
env=os.environ.copy();env.update(CONFECTORY_DOTNET=env.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet'))
def metadata(operation,**data):
 r=subprocess.run([env['CONFECTORY_DOTNET'],str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps({'operation':operation,**data}),text=True,capture_output=True,env=env,check=True);v=json.loads(r.stdout);assert v['ok'],v;return v['result']
items={
 'Main':('function','function '+n+'Main () -> int {provide '+n+'Main with '+n+'MainBody;}'),
 'MainBody':('implementation','implementation '+n+'MainBody for '+n+'Main () -> int {body common "Main.csbody";}'),
 'Mode':('function','function '+n+'Mode (long value,out long total) -> long {provide '+n+'Mode with '+n+'ModeBody;}'),
 'ModeBody':('implementation','implementation '+n+'ModeBody for '+n+'Mode (long nativeValue,out long nativeTotal) -> long {body common "Mode.csbody";}')}
sources={'Main.csbody':'return 0;','Mode.csbody':'// 원본 네이티브 이름과 out 저장소 한글 😀\nnativeValue+=1;nativeTotal=nativeValue;return nativeValue;'}
for name,(kind,text) in items.items():sources[name+'.celem']=text
sources['project.cproj']='project Owned.Context version "1" {standalone true;entry '+n+'Main;'+''.join('element '+name+' '+kind+' "'+name+'.celem";' for name,(kind,text) in items.items())+'registry Confectory.Build.DotNet "'+str(repo/'targets/dotnet/pack.cpack')+'";dependency Confectory.Build.DotNet version "0.1.0";target portable Confectory.Build.DotNet::Portable;}'
for name,text in sources.items():(project/name).write_bytes(text.encode())
converted=metadata('blueprintConversion',project=str(project/'project.cproj'),id=n+'ModeBody',text=items['ModeBody'][1],target='common',graphPath='Mode.graph.json',nodePath='Mode.node.json')
(project/'ModeBody.celem').write_text(converted['implementation']);(project/'Mode.graph.json').write_text(json.dumps(converted['graph']));(project/'Mode.node.json').write_text(json.dumps(converted['node']))
original={p.name:p.read_bytes() for p in project.iterdir() if p.is_file()};env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(case/'profile'),CONFECTORY_ENTRY_STORAGE=str(case/'profile'),CONFECTORY_MCP_DIRECTORY=str(case/'instances'),CONFECTORY_WEB_PROJECT=str(project/'project.cproj'));env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];host=None;log=None;traffic=[];results={};errors=[];external=[];checks=[]
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
def graph():return call('blueprint',{'action':'read','id':n+'ModeBody/body:common'})
def editor():
 overlay=page.locator('.bp-flow-overlay-host:visible');overlay.locator('[data-flow-code]').click();return page.get_by_role('dialog',name='C# Script · body',exact=True)
def edit(d,region,text):
 code=d.locator('[data-code-source]');code.evaluate('(el,region)=>{const spans=[...el.closest(".bp-script-editor").querySelectorAll("[data-code-highlight]>span")],part=spans.find(p=>p.dataset.codeRegion===region);if(!part)throw Error("source region missing");const start=spans.slice(0,spans.indexOf(part)).reduce((n,p)=>n+p.textContent.length,0);el.setSelectionRange(start,start+part.textContent.length)}',region);page.keyboard.insert_text(text)
def body_card():
 author.locator('[data-flow-tab=flow]').click();author.locator('[data-flow-node=body]').click();expect(page.locator('.bp-flow-overlay-host:visible [data-flow-code]')).to_be_enabled()
try:
 start(0)
 with sync_playwright() as p:
  expect.set_options(timeout=30000);browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=setup(browser);open_row('Mode','feature');page.locator('.window[data-key=declaration] [data-function-write-direct]').click();author=page.locator('.window[data-key=blueprint]');expect(author).to_have_attribute('data-blueprint-body',n+'ModeBody/body:common');assert graph()['nodes'][0]['rootModeEditor'];page.set_viewport_size({'width':390,'height':844});expect(author.locator('[data-flow-tab=inputs]')).to_be_visible();author.locator('[data-flow-tab=inputs]').click();inputs=author.locator('[data-flow-declarations] [data-mobile-contract-field]');assert inputs.count()==1 and inputs.first.get_attribute('data-mobile-contract-field')=='value';expect(inputs.locator('[data-signature-type]')).to_be_disabled();expect(inputs.locator('input')).to_have_attribute('readonly','');author.locator('[data-flow-tab=outputs]').click();outputs=author.locator('[data-flow-declarations] [data-mobile-contract-field]');assert set(outputs.evaluate_all('(rows)=>rows.map(r=>r.dataset.mobileContractField)'))=={'total','return'};unchanged();checked('390폭 원본 입력/출력 탭은 보호된 whole-body 입력과 out/반환을 분리해 표시하며 특수 계약을 일반 타입 버튼으로 바꾸지 않는다')
  body_card();d=editor();edit(d,'parameters','ref int nativeValue, out long nativeTotal');d.locator('[data-code-save]').click();expect(d.locator('[data-code-error]')).to_be_visible();assert 'ref int nativeValue' in d.locator('[data-code-source]').input_value() and pending()==[];d.locator('[data-code-cancel]').click();unchanged();checked('모바일 원본 C# 버튼은 같은 매개변수 영역으로 연결되고 비호환 타입은 오류·입력 보존 후 취소 가능하다')
  wanted='// 모바일 값/ref 편집 한글 😀\nnativeValue+=2;nativeTotal=nativeValue;return nativeValue;';d=editor();edit(d,'parameters','ref long nativeValue, out long nativeTotal');edit(d,'body',wanted);d.locator('[data-code-save]').click();held=pending();assert len(held)==1 and held[0][1]['type']=='root-script';assert json.loads(held[0][1]['text'])['source']==wanted;unchanged();page.set_viewport_size({'width':1480,'height':1050});expect(author.locator('[data-bp-node=body] [data-internal-code]')).to_be_visible();author.locator('[data-bp-overview-node=body]').click();author.locator('[data-bp-node=body] [data-internal-code]').click();d=page.get_by_role('dialog',name='C# Script · body',exact=True);assert wanted in d.locator('[data-code-source]').input_value() and 'ref long nativeValue' in d.locator('[data-code-source]').input_value();d.locator('[data-code-cancel]').click();page.set_viewport_size({'width':390,'height':844});unchanged();checked('C# 코드 저장은 명시적 value/ref와 기존 out·네이티브 이름을 비공개 입력으로 보관하며 desktop/mobile 폭 전환에도 유지한다')
  pending();page.close();stop();start(1);page=setup(browser);page.set_viewport_size({'width':390,'height':844});author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled();assert pending()==held;body_card();d=editor();assert wanted in d.locator('[data-code-source]').input_value() and 'ref long nativeValue' in d.locator('[data-code-source]').input_value();d.locator('[data-code-cancel]').click();unchanged();page.screenshot(path=str(case/'mobile-special-pin-editor.png'));checked('실제 프로세스 재시작은 모바일 특수핀의 미적용 C# 입력과 원본·out 저장소를 보존한다')
  page.locator('.bp-flow-overlay-host:visible [data-flow-done]').click();author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_have_text('저장됨',timeout=60000);current=graph();assert current['signature']['args'][0]['mode']=='ref' and current['signature']['args'][1]['mode']=='out';node=next(v for v in current['nodes'] if v['id']=='body');assert node['signature']['args'][0]['name']=='nativeValue' and node['source']==wanted;assert pending()==[];unchanged();checked('모바일 Save는 기존4개 원자 그룹으로 함수·구현·graph·본문을 함께 저장하고 out 및 이름 매핑을 보존한다')
  author.locator('[data-bp-complete]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=60000);assert state()['review']['status']=='ready';review.locator('[data-reject]').click();expect(review).to_be_hidden();unchanged();page.locator('[data-tab-order-key="window:blueprint"] [role=tab]').click();expect(author).to_be_visible();author.locator('[data-bp-complete]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=60000)
  if review.locator('[data-review-advanced]').count():
   review.locator('[data-review-advanced]').click()
   if review.locator('[data-advanced-reviewed]').count():review.locator('[data-advanced-reviewed]').check()
  mark=len(traffic);review.locator('#confirm').click();result=completed('confirmGroup',None,mark);assert result['result']['sourceConfirmed'];expect(review).to_have_count(0,timeout=90000);changed={key for key,value in original.items() if (project/key).read_bytes()!=value};assert changed=={'Mode.celem','ModeBody.celem','Mode.graph.json','Mode.node.json'},changed;assert (project/'Mode.csbody').read_bytes()==original['Mode.csbody'];checked('390폭 Review 취소와 명시적 compiler Confirm은 분리되며 선택한4개 소스만 반영하고 기존 C#/Main을 보존한다')
  assert not errors and not external,(errors,external);page.close();browser.close()
except Exception:
 try:page.screenshot(path=str(case/'failure.png'));(case/'failure.json').write_text(json.dumps({'checks':checks,'state':state(),'errors':errors},ensure_ascii=False,indent=2))
 except Exception:pass
 print('EVIDENCE '+str(case),flush=True);raise
finally:stop()
record={'checks':checks,'actualEngine':True,'browserWidth':390,'nativeWindowsOrMobile':False,'accountOrInference':False,'projectRun':False,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False,indent=2))
