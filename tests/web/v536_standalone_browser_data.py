"""Original standalone Browser Data over an owned source fixture; no accounts/inference.
Does not substitute provider success or native Windows execution for browser checks.
"""
import json,re,os,pathlib,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-standalone-data-'));project=case/'owned project';project.mkdir();n='Owned.Browser::'
sources={
 'Main.celem':'function '+n+'Main () -> int {provide '+n+'Main with '+n+'MainBody;}',
 'MainBody.celem':'implementation '+n+'MainBody for '+n+'Main () -> int {body common "Main.csbody";}',
 'Vitals.celem':'schema '+n+'Vitals {field HP single general long;}',
 'Stats.celem':'schema '+n+'Stats {field Speed single general int;field Target single reference '+n+'Vitals;field Counts multiple general long;}',
 'Unit.celem':'object '+n+'Unit {use schema '+n+'Vitals;data HP = 100;}',
 'Monster.celem':'object '+n+'Monster extends '+n+'Unit {use schema '+n+'Stats;data Speed = 2;data Target = '+n+'Unit;data Counts = [1, 2];description "원래 설명";}',
 'Slime.celem':'object '+n+'Slime extends '+n+'Monster {}',
 'Main.csbody':'return 0;'}
for name,text in sources.items():(project/name).write_text(text)
kind=lambda name:'schema' if name in ['Vitals','Stats'] else 'function' if name=='Main' else 'implementation' if name=='MainBody' else 'object'
(project/'project.cproj').write_text('project Owned.Browser version "1" {standalone true;entry '+n+'Main;'+''.join('element '+path[:-6]+' '+kind(path[:-6])+' "'+path+'";' for path in sources if path.endswith('.celem'))+'registry Confectory.Build.DotNet "'+str(repo/'targets/dotnet/pack.cpack')+'";dependency Confectory.Build.DotNet version "0.1.0";target portable Confectory.Build.DotNet::Portable;}')
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
try:
 start(0)
 with sync_playwright() as p:
  expect.set_options(timeout=30000);browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=setup(browser);idle();page.locator('#workspace').click(button='right',position={'x':700,'y':100});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=page.locator('.window[data-key^="browser:project:"]');expect(b.locator('[data-browser-enter="'+n+'Unit"]')).to_be_visible();b.locator('[data-browser-enter="'+n+'Unit"]').click();b.locator('[data-density="100"]').click();expect(cell('Speed')).to_have_value('2');expect(cell('HP')).to_have_value('100');assert b.locator('.instant-table-toolbar,[data-table-cell],[data-review-id],[data-browser-row-tools]').count()==0
  identity=row().locator('.browser-data-identity');identity.hover();tip=page.get_by_role('tooltip');expect(tip).to_contain_text('참조 · Hover');expect(tip).to_contain_text('Unit');page.keyboard.down('Shift');expect(tip).to_contain_text('역참조');expect(tip).to_contain_text('Slime');page.keyboard.up('Shift');page.mouse.move(1400,90);expect(tip).to_have_count(0);unchanged();page.screenshot(path=str(case/'standalone-data.png'));checked('독립 Data는 원본 행·셀·상세 버튼만 표시하며 실제 상속/Shift 역참조를 읽고 개발용 비교 표를 노출하지 않는다')
  cell('Speed').fill('잘못된 값' if False else '2147483648');cell('Speed').press('Enter');expect(cell('Speed')).to_have_attribute('aria-invalid','true');expect(cell('Speed')).to_have_value('2147483648');cell('Speed').press('Escape');expect(cell('Speed')).to_have_value('2');cell('Speed').fill('7');cell('Speed').press('Enter');idle();assert value('data:["Speed"]')=='7';unchanged();expect(b.locator('[data-browser-save]')).to_be_enabled();mark=len(traffic);b.locator('[data-browser-save]').click();completed('browserDrafts','save',mark);assert value('data:["Speed"]')=='7';unchanged();checked('잘못된 int 입력은 유지·취소할 수 있고 정상 셀 변경과 임시 저장은 공유 초안에만 반영된다')
  cell('Speed').fill('8');cell('Speed').press('Enter');idle();assert value('data:["Speed"]')=='8';expect(b.locator('[data-browser-discard]')).to_be_enabled();mark=len(traffic);b.locator('[data-browser-discard]').click();completed('browserDrafts','discard',mark);expect(cell('Speed')).to_have_value('7');assert value('data:["Speed"]')=='7';unchanged();checked('원본 변경 취소는 저장된 셀7을 복원하고 최종 파일은 보존한다')
  cell('설명').fill('cold 미저장 설명 한글');page.evaluate('async()=>await confectoryFlushPresentation()');page.close();stop();start(1);page=setup(browser);b=page.locator('.window[data-key^="browser:project:"]');idle();b.locator(':scope > .window-title .caption').click(position={'x':5,'y':8});expect(cell('설명')).to_have_value('cold 미저장 설명 한글');assert json.loads(value('description'))=='원래 설명';cell('설명').press('Enter');idle();assert json.loads(value('description'))=='cold 미저장 설명 한글';unchanged();checked('실제 프로세스 재시작은 미저장 한글 입력을 복원하며 Enter 전에는 원본이나 공유 값을 자동 변경하지 않는다')
  idle();detail=row().locator('[data-detail-path=\'["Target"]\']');detail.click();editor=page.locator('.window[data-key^="editor-"]').filter(has=page.locator('.object-title-name',has_text='Monster')).last;expect(editor.locator('[data-property-path=\'["Target"]\']')).to_be_visible();unchanged();editor.get_by_label('Target 기본값 선택',exact=True).click();picker=page.get_by_role('dialog',name='기본값 선택',exact=True);picker.locator('[data-reference-choice="'+n+'Slime"]').click();mark=len(traffic);editor.locator('[data-element-action=save]').click();completed('saveEditorView',None,mark);assert json.loads(value('data:["Target"]'))=={'$ref':n+'Slime'};unchanged();editor.get_by_label('Target 기본값 선택',exact=True).click();page.get_by_role('dialog',name='기본값 선택',exact=True).locator('[data-reference-choice="'+n+'Unit"]').click();editor.locator('[data-element-action=discard]').click();expect(editor.get_by_label('Target 기본값 선택',exact=True)).to_have_text('Slime');assert json.loads(value('data:["Target"]'))=={'$ref':n+'Slime'};page.screenshot(path=str(case/'reference-detail.png'));checked('참조형 Data 편집은 정확한 소유 요소와 필드의 독립 상세 창으로 연결하며 파일이나 참조 대상을 임의로 변경하지 않는다')
  editor.locator('[data-close]').click();page.evaluate('async()=>await confectoryFlushPresentation()');page.close();stop();start(2);page=setup(browser);b=page.locator('.window[data-key^="browser:project:"]');idle();b.locator(':scope > .window-title .caption').click(position={'x':5,'y':8});assert json.loads(value('data:["Target"]'))=={'$ref':n+'Slime'};unchanged();checked('참조 변경 저장·다음 선택 취소 후 실제 재시작에도 Slime 참조가 복원되고 최종 파일은 유지된다');cell('Speed').fill('2147483648');cell('Speed').press('Enter');expect(cell('Speed')).to_have_attribute('aria-invalid','true');mark=len(traffic);b.locator('[data-browser-confirm]').click();idle();assert not any(v['endpoint'] in ['reviewGroup','confirmGroup'] for v in traffic[mark:]);expect(cell('Speed')).to_have_value('2147483648');cell('Speed').press('Escape');idle();expect(b.locator('[data-browser-save]')).to_be_disabled();assert call('browserElements',{'ids':[n+'Monster']})['rows'][0]['checkpointSaved'];b.locator('[data-browser-confirm]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=60000)
  if review.locator('[data-review-advanced]').count():
   review.locator('[data-review-advanced]').click()
   if review.locator('[data-advanced-reviewed]').count():review.locator('[data-advanced-reviewed]').check()
  mark=len(traffic);review.locator('#confirm').click();expect(review).to_have_count(0,timeout=60000);completed('confirmGroup',None,mark);assert 'data Speed = 7' in (project/'Monster.celem').read_text();assert json.loads(re.search(r'description\s+("(?:\\.|[^"\\])*")',(project/'Monster.celem').read_text())[1])=='cold 미저장 설명 한글';assert all((project/k).read_bytes()==v for k,v in original.items() if k!='Monster.celem');checked('보관 중인 미적용 셀은 검토를 차단하고 명시적 저장·Review·compiler Confirm만 대상 Monster 파일을 최종 반영한다')
  confirmed={p.name:p.read_bytes() for p in project.iterdir() if p.is_file()};before=call('browserElements',{'ids':[n+'Monster']})['rows'][0];cell('Speed').fill('11');page.evaluate('async()=>await confectoryFlushPresentation()');proof={k:before[k] for k in ['revision','textHash','viewHash']};newer=call('editBrowserElement',{'id':n+'Monster','column':'description','valueJson':json.dumps('다른 편집자의 공유 변경',ensure_ascii=False),'version':proof});assert newer['accepted'];cell('Speed').press('Enter');expect(cell('Speed')).to_have_attribute('aria-invalid','true');expect(cell('Speed')).to_have_value('11');assert value('data:["Speed"]')=='7' and json.loads(value('description'))=='다른 편집자의 공유 변경';refused=call('editBrowserElement',{'id':n+'Monster','column':'data:["Speed"]','valueJson':'12','version':proof});assert not refused['accepted'] and refused['code']=='element-value-stale';assert all((project/k).read_bytes()==v for k,v in confirmed.items());checked('실제 타 편집의 소스 변경은 보관 입력 재적용과 오래된 서버 CAS를 모두 거절하고 타 편집 값·개인 입력·최종 파일을 보존한다')
  cell('Speed').press('Escape');expect(cell('Speed')).to_have_value('7');cell('Speed').fill('13');page.evaluate('async()=>await confectoryFlushPresentation()');before=call('browserElements',{'ids':[n+'Monster']})['rows'][0];call('select',{'id':n+'Vitals'});schema=state()['draft'];call('editDraft',{'id':n+'Vitals','revision':schema['revision'],'text':schema['text'].replace('HP single general long','HP single general int')});after=call('browserElements',{'ids':[n+'Monster']})['rows'][0];assert after['textHash']==before['textHash'] and after['contentHash']!=before['contentHash'];cell('Speed').press('Enter');expect(cell('Speed')).to_have_attribute('aria-invalid','true');expect(cell('Speed')).to_have_value('13');assert value('data:["Speed"]')=='7';assert all((project/k).read_bytes()==v for k,v in confirmed.items());checked('자기 소스가 같아도 실제 상속 스키마 변경은 내용 지문을 바꾸어 재적용을 차단하며 입력·확정 소스를 보존한다')
  assert not errors and not external,(errors,external);page.close();browser.close()
except Exception:
 try:(case/'failure.json').write_text(json.dumps({'errors':errors,'state':state(),'traffic':traffic,'results':results},ensure_ascii=False,indent=2));page.screenshot(path=str(case/'failure.png'))
 except Exception:pass
 print('OWNED FAILURE '+str(case),flush=True);raise
finally:stop()
record={'checks':checks,'case':str(case),'errors':errors,'external':external,'windowsExecuted':False,'actualAccountOrInference':False};(case/'evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False),flush=True)
