"""Original standalone Browser Data over an owned source fixture; no accounts/inference.
Does not substitute provider success or native Windows execution for browser checks.
"""
import hashlib,json,re,os,pathlib,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-declaration-data-'));project=case/'owned project';project.mkdir();n='Owned.Browser::'
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
groups={'concept':['Category','Concept'],'info':['Vitals'],'feature':['Main','MainBody'],'module':['Tools']}
labels={'Category':'분류 표시','Concept':'Concept','Vitals':'생명 정보','Main':'Main','MainBody':'MainBody','Tools':'Tools'}
def focus():
 b.locator(':scope > .window-title .caption').click(position={'x':5,'y':8});idle()
def group(key):
 focus();b.locator('[data-tab="'+key+'"]').click();b.locator('[data-density="100"]').click();idle()
 for name in groups[key]:expect(desc(name)).to_be_visible()
def desc(name):return b.locator('[data-object="'+n+name+'"]').get_by_label(labels[name]+' 설명',exact=True)
def snapshot(name):return call('browserElements',{'ids':[n+name]})['rows'][0]
def saved():
 mark=len(traffic);expect(b.locator('[data-browser-save]')).to_be_enabled();b.locator('[data-browser-save]').click();completed('browserDrafts','save',mark)
def semantic(node):
 if isinstance(node,dict):return {k:semantic(v) for k,v in node.items() if k!='Loc'}
 if isinstance(node,list):return list(map(semantic,node))
 return node
def confirm():
 focus();expect(b.locator('[data-browser-confirm]')).to_be_enabled();b.locator('[data-browser-confirm]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=90000)
 if review.locator('[data-review-advanced]').count():
  review.locator('[data-review-advanced]').click()
  if review.locator('[data-advanced-reviewed]').count():review.locator('[data-advanced-reviewed]').check()
 mark=len(traffic);review.locator('#confirm').click();reply=completed('confirmGroup',None,mark);assert reply['result'].get('sourceConfirmed'),state().get('logs');expect(review).to_have_count(0,timeout=90000)
try:
 start(0)
 with sync_playwright() as p:
  expect.set_options(timeout=30000);browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=setup(browser);idle();page.locator('#workspace').click(button='right',position={'x':700,'y':100});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=page.locator('.window[data-key^="browser:project:"]')
  for key,names in groups.items():
   group(key)
   for name in names:
    row=snapshot(name);assert row['kind']==kind(name) and row['status']=='available';assert next(f for f in row['fields'] if f['column']=='description')['writable'];desc(name).fill('편집 '+name+' 한글');desc(name).press('Enter');idle();assert json.loads(next(f['valueJson'] for f in snapshot(name)['fields'] if f['column']=='description'))=='편집 '+name+' 한글';unchanged()
   saved();unchanged()
  checked('원본 네 Browser 탭에서 schema/function/implementation/module/category/concept 설명을 실제 공유 초안에 편집·임시 저장하며 소스는 보존한다')
  group('feature');desc('Main').fill('취소할 함수 설명');desc('Main').press('Enter');idle();mark=len(traffic);b.locator('[data-browser-discard]').click();completed('browserDrafts','discard',mark);expect(desc('Main')).to_have_value('편집 Main 한글');unchanged();checked('비객체 Data 변경 취소는 저장본을 복원하며 함수 본문·서명·참조를 삭제하지 않는다')
  group('info');expect(b.locator('[data-object="'+n+'Vitals"] .obj-icon')).to_have_text('♥');expect(b.locator('[data-tree-id="'+n+'Vitals"] .tree-object-icon')).to_have_text('♥');expect(b.locator('[data-tree-id="'+n+'Vitals"]')).to_contain_text('생명 정보');desc('Vitals').fill('재시작 미저장 정보 한글');page.evaluate('async()=>await confectoryFlushPresentation()');page.screenshot(path=str(case/'declaration-data.png'));page.close();stop();start(1);page=setup(browser);b=page.locator('.window[data-key^="browser:project:"]');idle();focus();expect(desc('Vitals')).to_have_value('재시작 미저장 정보 한글');assert json.loads(next(f['valueJson'] for f in snapshot('Vitals')['fields'] if f['column']=='description'))=='편집 Vitals 한글';desc('Vitals').press('Enter');idle();saved();unchanged();checked('다른 source 종류의 미저장 한글과 표시 이름·문자 아이콘은 실제 프로세스 재시작 후 복원하며 명시적 적용 전 공유 초안을 바꾸지 않는다')
  before=snapshot('Main');proof={k:before[k] for k in ['revision','textHash','viewHash']};changed=call('editBrowserElement',{'id':n+'Main','column':'description','valueJson':json.dumps('동시 변경'),'version':proof});assert changed['accepted'];stale=call('editBrowserElement',{'id':n+'Main','column':'description','valueJson':json.dumps('덮어쓰기'),'version':proof});assert not stale['accepted'];fresh=changed['row'];invalid=call('editBrowserElement',{'id':n+'Main','column':'signature','valueJson':'"x"','version':{k:fresh[k] for k in proof}},False);assert not invalid['ok'];call('browserElements',{'ids':[n+'MainBody/body:common']},False);call('browserElements',{'ids':['ReferenceApi::Work']},False);unchanged();checked('비객체 셀 쓰기는 설명 하나와 정확한 최신 CAS만 허용하며 오래된 버전·계약 필드·본문·타 namespace는 거절한다')
  # Explicit UI checkpoints/Review/Confirm, not direct source writes or automatic confirmation.
  for key in groups:
   group(key)
   confirm()
  for name in labels:
   text=(project/(name+'.celem')).read_text();assert 'description' in text
   # Formatting can normalize bytes; all semantic contracts/metadata must be identical.
   def inspect(text):
    r=subprocess.run([env['CONFECTORY_DOTNET'],str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps({'operation':'inspect','text':text}),text=True,capture_output=True,env=env,check=True);return json.loads(r.stdout)['result']
   old=inspect(sources[name+'.celem']);new=inspect(text);old.pop('description');new.pop('description');old.pop('descriptionDefined');new.pop('descriptionDefined');old['editor'].pop('description');new['editor'].pop('description');assert semantic(old)==semantic(new),(name,old,new)
  assert (project/'Main.csbody').read_text()==sources['Main.csbody'];checked('원본 헤더 저장→검토→compiler Confirm은 여섯 선언의 설명만 최종 반영하고 ID/종류/서명/구현/상속/필드/아이콘을 보존한다')
  assert not errors and not external,(errors,external);page.screenshot(path=str(case/'declaration-confirmed.png'));page.close();browser.close()
except Exception:
 try:(case/'failure.json').write_text(json.dumps({'errors':errors,'state':state(),'traffic':traffic,'results':results},ensure_ascii=False,indent=2));page.screenshot(path=str(case/'failure.png'))
 except Exception:pass
 print('OWNED FAILURE '+str(case),flush=True);raise
finally:stop()
record={'checks':checks,'case':str(case),'errors':errors,'external':external,'windowsExecuted':False,'actualAccountOrInference':False};(case/'evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False),flush=True)
