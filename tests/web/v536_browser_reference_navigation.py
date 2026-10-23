"""Original standalone Browser Data over an owned source fixture; no accounts/inference.
Does not substitute provider success or native Windows execution for browser checks.
"""
import hashlib,json,re,os,pathlib,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-browser-reference-'));project=case/'owned project';project.mkdir();n='Owned.Browser::'
sources={
 'Main.celem':'function '+n+'Main () -> int {provide '+n+'Main with '+n+'MainBody;}',
 'MainBody.celem':'implementation '+n+'MainBody for '+n+'Main () -> int {body common "Main.csbody";}',
 'Vitals.celem':'schema '+n+'Vitals {field HP single general long;}',
 'Stats.celem':'schema '+n+'Stats {field Speed single general int;field Target single reference '+n+'Vitals;field Counts multiple general long;}',
 'Unit.celem':'object '+n+'Unit {use schema '+n+'Vitals;data HP = 100;}',
 'Monster.celem':'object '+n+'Monster extends '+n+'Unit {use schema '+n+'Stats;data Speed = 2;data Target = '+n+'Unit;data Counts = [1, 2];description "원래 설명";}',
 'Slime.celem':'object '+n+'Slime extends '+n+'Monster {}',
 'Main.csbody':'return 0;'}
sources.update({
 'Category.celem':'category '+n+'Category {description "분류 설명";value editorName = "분류 표시";value editorIcon = "📁";}',
 'Concept.celem':'concept '+n+'Concept {description "개념 설명";}',
 'Tools.celem':'module '+n+'Tools {description "모듈 설명";}',
})
sources['Main.celem']=sources['Main.celem'].replace(' {',' {description "함수 설명";value editorIcon = "★";use function ReferenceApi::Work;',1)
sources['MainBody.celem']=sources['MainBody.celem'].replace(' {',' {description "구현 설명";',1)
sources['Vitals.celem']=sources['Vitals.celem'].replace(' {',' {description "정보 설명";value editorName = "생명 정보";value editorIcon = "♥";',1)
api_pack=case/'registered-api';api_pack.mkdir();(api_pack/'pack.cpack').write_text('pack ReferenceApi version "1" {element Work function "Work.celem";element Unused function "Unused.celem";element WorkBody implementation "WorkBody.celem";}');external_text='function ReferenceApi::Work () -> int {description "등록 참조";provide ReferenceApi::Work with ReferenceApi::WorkBody;}';(api_pack/'Work.celem').write_text(external_text);(api_pack/'Unused.celem').write_text('function ReferenceApi::Unused () -> int {}');(api_pack/'WorkBody.celem').write_text('implementation ReferenceApi::WorkBody for ReferenceApi::Work () -> int {body common \"Work.csbody\";}');(api_pack/'Work.csbody').write_text('return 2;')
for name,text in sources.items():(project/name).write_text(text)
kind=lambda name:'schema' if name in ['Vitals','Stats'] else 'function' if name=='Main' else 'implementation' if name=='MainBody' else 'module' if name=='Tools' else 'category' if name=='Category' else 'concept' if name=='Concept' else 'object'
(project/'project.cproj').write_text('project Owned.Browser version "1" {standalone true;entry '+n+'Main;'+''.join('element '+path[:-6]+' '+kind(path[:-6])+' "'+path+'";' for path in sources if path.endswith('.celem'))+'registry ReferenceApi \"'+str(api_pack/'pack.cpack')+'\";dependency ReferenceApi version \"1\";registry Confectory.Build.DotNet "'+str(repo/'targets/dotnet/pack.cpack')+'";dependency Confectory.Build.DotNet version "0.1.0";target portable Confectory.Build.DotNet::Portable;}')
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
def row():return b.locator('[data-object="'+n+'Monster"]')
def cell(label):return row().get_by_label('Monster '+label,exact=True)
def value(column):return next(f['valueJson'] for row in call('browserElements',{'ids':[n+'Monster']})['rows'] if row['id']==n+'Monster' for f in row['fields'] if f['column']==column)
def focus():b.locator(':scope > .window-title .caption').click(position={'x':5,'y':8});idle()
try:
 start(0)
 with sync_playwright() as p:
  expect.set_options(timeout=30000);browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=setup(browser);idle();page.locator('#workspace').click(button='right',position={'x':700,'y':100});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=page.locator('.window[data-key^="browser:project:"]');b.locator('[data-tab=feature]').click();b.locator('[data-density="100"]').click();field=b.locator('[data-object="'+n+'Main"]').get_by_label('Main 설명',exact=True);expect(field).to_be_visible();field.fill('참조 소유자의 저장된 설명');field.press('Enter');idle();mark=len(traffic);expect(b.locator('[data-browser-save]')).to_be_enabled();b.locator('[data-browser-save]').click();completed('browserDrafts','save',mark);unchanged()
  b.locator('[data-tree-select="ns:ReferenceApi"]').click();target=b.locator('[data-object="ReferenceApi::Work"]');expect(target).to_be_visible();assert target.locator('[data-browser-value]').count()==0;target.locator('[data-data-detail]').click();idle();definition=page.locator('.window[data-key=definition]');expect(definition.locator('[data-reference-text]')).to_have_value(external_text);assert definition.locator('[data-reference-text]').evaluate('e=>e.readOnly');unchanged();assert '등록 참조' not in json.dumps(state().get('presentation'));checked('등록 namespace의 Browser Data 상세는 소유 source의 직접 참조 gate로 확정 정의만 읽으며 외부 셀/쓰기/본문 조회를 만들지 않는다')
  source=call('browserElements',{'ids':[n+'Main']})['rows'][0];request={'sourceId':n+'Main','id':'ReferenceApi::Unused','revision':source['revision'],'hash':source['textHash']};call('readReferenceDefinition',request);denied=state()['referenceDefinition'];assert denied.get('status')=='unavailable' and denied.get('code')=='NOT_DECLARED_REFERENCE';focus();unused=b.locator('[data-object="ReferenceApi::Unused"]');unused.locator('[data-data-detail]').click();dialog=page.get_by_role('dialog',name='등록 팩 선언',exact=True);expect(dialog).to_be_visible();expect(dialog).to_contain_text('직접 선언한 참조가 없습니다');dialog.get_by_role('button',name='닫기',exact=True).click();unchanged();checked('등록 목록에 있는 미참조 선언도 Browser 상세에서 권한을 넓히지 않으며 서버 직접 요청도 거절한다')
  definition.locator(':scope>.window-title .caption').click(position={'x':5,'y':8});page.evaluate('async()=>await confectoryFlushPresentation()');page.close();stop();start(1);page=setup(browser);idle();definition=page.locator('.window[data-key=definition]');expect(definition.locator('[data-reference-text]')).to_have_count(0);mark=len(traffic);definition.locator('[data-reference-reload]').click();completed('readReferenceDefinition',None,mark);expect(definition.locator('[data-reference-text]')).to_have_value(external_text);unchanged();checked('실제 재시작은 참조 내용을 자동 조회하지 않고 복원하며 명시적 다시 읽기에서 저장된 소유 source의 직접 참조를 재검사한다')
  source=call('browserElements',{'ids':[n+'Main']})['rows'][0];changed=call('editBrowserElement',{'id':n+'Main','column':'description','valueJson':json.dumps('실제 타 편집 변경'),'version':{k:source[k] for k in ['revision','textHash','viewHash']}});assert changed['accepted'];mark=len(traffic);definition.locator('[data-reference-reload]').click()
  for _ in range(3000):
   requests=[r for r in traffic[mark:] if r['endpoint']=='readReferenceDefinition'];replies=[results[r['requestId']] for r in requests if r['requestId'] in results]
   if replies:break
   page.wait_for_timeout(20)
  assert replies and not replies[-1]['ok'],replies;assert json.loads(next(f['valueJson'] for f in call('browserElements',{'ids':[n+'Main']})['rows'][0]['fields'] if f['column']=='description'))=='실제 타 편집 변경';unchanged();checked('실제 소유 source 변경 뒤 오래된 참조 요청은 실패하며 다른 편집 값과 원본 파일을 보존한다')
  assert not errors and not external,(errors,external);page.screenshot(path=str(case/'reference-data.png'));page.close();browser.close()
except Exception:
 try:(case/'failure.json').write_text(json.dumps({'errors':errors,'state':state(),'traffic':traffic,'results':results},ensure_ascii=False,indent=2));page.screenshot(path=str(case/'failure.png'))
 except Exception:pass
 print('OWNED FAILURE '+str(case),flush=True);raise
finally:stop()
record={'checks':checks,'case':str(case),'errors':errors,'external':external,'windowsExecuted':False,'actualAccountOrInference':False};(case/'evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False),flush=True)
