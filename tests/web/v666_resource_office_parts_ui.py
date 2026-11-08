"""Real generated File copies, native part observations and decoded image pixels.
Delayed/corrupted replies are controlled transport fixtures, not external users.
"""
import sys,json,pathlib,hashlib,base64,uuid,shutil,traceback,time,io,random,zipfile,struct
from PIL import Image
from playwright.sync_api import sync_playwright,expect
import v536_wide_mixed as f
mode=sys.argv[3];store=f.project/'.confectory/resources.v1.json';b=None;observations=[]
def api(action='load',**kw):return f.invoke('projectResourceLayout',dict(action=action,project=f.state()['projectId'],**kw))['result']['result']
def original():
 for name,raw in f.original.items():assert(f.project/name).read_bytes()==raw,name
 assert not f.errors and not f.external,(f.errors,f.external)
def browser():
 global b
 f.page.locator('#workspace').click(button='right',position=dict(x=700,y=260));f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]').last;b.locator('[data-tab=resource]').click();expect(b.locator('[data-new]')).to_be_enabled()
def viewer(id):return f.page.locator('.window[data-key="resource-file:'+id+'"]')
def opened(id):
 b.locator('[data-resource-id="'+id+'"]').press('Enter');w=viewer(id);expect(w).to_be_visible();return w
def closed(id):viewer(id).locator('[data-close]').first.click();expect(viewer(id)).to_have_count(0)
def urls():return f.page.evaluate('()=>structuredClone(__officePartURLs)')
def setup():
 global b
 f.page=f.browser.new_page(viewport=dict(width=1280,height=900));f.page.on('pageerror',lambda e:f.errors.append(str(e)));f.page.on('response',f.observe);f.page.route('**/*',f.route)
 f.page.add_init_script("""(()=>{const Base=Worker;globalThis.__officeWorkers={created:0,terminated:0};globalThis.Worker=class extends Base{constructor(...args){super(...args);if(!String(args[0]).includes('resource-office-worker'))return;__officeWorkers.created++;let stopped=false;const stop=this.terminate.bind(this);this.terminate=()=>{if(!stopped){stopped=true;__officeWorkers.terminated++;}stop();};}};})();""")
 f.page.add_init_script("""(()=>{const create=URL.createObjectURL.bind(URL),revoke=URL.revokeObjectURL.bind(URL);globalThis.__officePartURLs={live:[],created:[],revoked:[]};URL.createObjectURL=blob=>{const value=create(blob);if(['image/png','image/jpeg'].includes(blob.type)){__officePartURLs.live.push(value);__officePartURLs.created.push(value);}return value;};URL.revokeObjectURL=value=>{if(__officePartURLs.live.includes(value)){__officePartURLs.live=__officePartURLs.live.filter(x=>x!==value);__officePartURLs.revoked.push(value);}return revoke(value);};const base=fetch;globalThis.__officePartPlan={};globalThis.__officePartHeld=false;globalThis.__officePartCalls=[];fetch=async(...args)=>{let request;try{request=JSON.parse(args[1]?.body||'null')}catch{}if(request?.op==='observe'&&request.endpoint==='readProjectResourceOfficePart')__officePartCalls.push(structuredClone(request.input));const response=await base(...args);if(request?.op!=='observe')return response;const plan=__officePartPlan[request.endpoint];if(!plan||plan.part!=null&&request.input?.part!==plan.part)return response;const body=await response.clone().json();if(!body.ok)return response;delete __officePartPlan[request.endpoint];const made=()=>new Response(JSON.stringify(body),{status:200,headers:{'Content-Type':'application/json'}});if(plan.action==='legacy'){delete body.result.officePreview;return made();}if(plan.action==='descriptor'){body.result.officePreview.partBytes--;return made();}if(plan.action==='corrupt'){body.result.data=(body.result.data[0]==='A'?'B':'A')+body.result.data.slice(1);return made();}if(plan.action==='mix'){body.result.item.contentGeneration='f'.repeat(64);return made();}__officePartHeld=true;return new Promise(resolve=>globalThis.__releaseOfficePart=(failed=false)=>{if(failed){body.ok=false;delete body.result;body.error={code:'owned_lost_image_part'};}resolve(made());});};})();""")
 def seen(response):
  try:
   q=response.request.post_data_json
   if isinstance(q,dict)and q.get('op')=='observe':
    result=response.json();data=result.get('result',{}).pop('data',None)
    if data is not None:result['retainedData']={'bytes':len(data),'sha256':hashlib.sha256(data.encode()).hexdigest()}
    observations.append(dict(request=q,result=result))
  except Exception:pass
 f.page.on('response',seen);f.goto_editor(f.page,f.url);f.idle();b=f.page.locator('.window[data-key^="browser:project:"]').last
def arm(action='hold',part=1,endpoint='readProjectResourceOfficePart'):f.page.evaluate('({action,part,endpoint})=>{__officePartHeld=false;__officePartPlan[endpoint]={action,part};}',dict(action=action,part=part,endpoint=endpoint))
def held():f.page.wait_for_function('()=>__officePartHeld')
def release(failed=False):f.page.evaluate('failed=>__releaseOfficePart(failed)',failed)
def observed(input,endpoint='readProjectResourceOfficePart'):
 v=f.mount()
 try:
  for _ in range(100):
   result=f.raw(dict(op='observe',view=v['view'],scope=v['scope'],endpoint=endpoint,input=input))
   if result.get('error',{}).get('code')!='busy':return result
   time.sleep(.02)
  raise AssertionError(result)
 finally:f.raw(dict(op='dispose',view=v['view']))
templates={'docx': {'word/document.xml': '<w:document xmlns:w="urn:w"><w:body><w:p><w:pPr><w:pStyle '
                               'w:val="Heading1"/></w:pPr><w:r><w:rPr><w:b/></w:rPr><w:t>생성 문서 '
                               '&lt;script&gt;</w:t></w:r></w:p><w:tbl><w:tr><w:tc><w:p><w:r><w:t>표 '
                               '값</w:t></w:r></w:p></w:tc></w:tr></w:tbl></w:body></w:document>'},
 'odt': {'content.xml': '<office:document xmlns:office="urn:o" xmlns:text="urn:t"><text:p>ODT 본문</text:p></office:document>'},
 'pptx': {'ppt/slides/slide1.xml': '<p:sld xmlns:p="urn:p" xmlns:a="urn:a"><a:p><a:r><a:t>첫 슬라이드</a:t></a:r></a:p></p:sld>',
          'ppt/slides/slide2.xml': '<p:sld xmlns:p="urn:p" xmlns:a="urn:a"><a:p><a:r><a:t>둘째 슬라이드</a:t></a:r></a:p></p:sld>'},
 'xlsx': {'xl/_rels/workbook.xml.rels': '<Relationships><Relationship Id="r1" Target="worksheets/sheet1.xml"/><Relationship Id="r2" '
                                        'Target="/xl/worksheets/sheet2.xml"/><Relationship Id="external" TargetMode="External" '
                                        'Target="https://must-not-load.invalid/"/></Relationships>',
          'xl/sharedStrings.xml': '<sst><si><t>문자 &lt;img&gt;</t></si></sst>',
          'xl/workbook.xml': '<workbook xmlns:r="urn:r"><sheets><sheet name="첫 시트" r:id="r1"/><sheet name="둘째" r:id="r2"/></sheets></workbook>',
          'xl/worksheets/sheet1.xml': '<worksheet><sheetData><row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1"><f>1+1</f><v>2</v></c><c r="C1" '
                                      't="b"><v>1</v></c></row></sheetData></worksheet>',
          'xl/worksheets/sheet2.xml': '<worksheet><sheetData><row r="3"><c r="A3"><f>HYPERLINK("https://must-not-load.invalid/")</f></c><c r="B3" '
                                      't="inlineStr"><is><t>두 번째 값</t></is></c></row></sheetData></worksheet>'}}

def sample(extension,size=None,broken=False):
 parts=dict(templates[extension]);parts=({'word/document.xml':'<!DOCTYPE document [<!ENTITY x SYSTEM "https://must-not-load.invalid/">]><document>&x;</document>'}if broken else parts)
 def make(length):
  out=io.BytesIO()
  with zipfile.ZipFile(out,'w')as archive:
   for name,text in parts.items():
    info=zipfile.ZipInfo(name,date_time=(2026,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;archive.writestr(info,text.encode())
   if length is not None:
    info=zipfile.ZipInfo('media/generated.bin',date_time=(2026,1,1,0,0,0));info.compress_type=zipfile.ZIP_STORED;archive.writestr(info,random.Random(1918).randbytes(length))
  return out.getvalue()
 if size is None:return make(None)
 length=max(0,size-3000)
 for _ in range(6):
  raw=make(length);delta=size-len(raw)
  if not delta:return raw
  length+=delta
 raise AssertionError('exact generated ZIP size')
def workers():return f.page.evaluate('()=>structuredClone(__officeWorkers)')
def drained():f.page.wait_for_function('()=>__officeWorkers.created===__officeWorkers.terminated')
def ready(w,extension='docx',large=True):
 expect(w.locator('.resource-preview')).to_have_attribute('aria-busy','false');expect(w.locator('.resource-preview')).to_contain_text({'docx':'생성 문서 <script>','xlsx':'문자 <img>','pptx':'첫 슬라이드','odt':'ODT 본문'}[extension]);expect(w.locator('[data-resource-content-save]')).to_have_count(0)
 if large:expect(w.locator('[data-resource-content-edit],[data-resource-content-restore]')).to_have_count(0);expect(w.locator('.resource-preview-status')).to_contain_text('읽기 전용')
 if extension=='docx':expect(w.locator('.resource-document h2 span')).to_have_css('font-weight','700');expect(w.locator('.resource-document td')).to_have_text('표 값');expect(w.locator('.resource-preview script')).to_have_count(0)
 elif extension=='xlsx':
  expect(w.locator('td').nth(1)).to_have_text('2');expect(w.locator('td').nth(2)).to_have_text('TRUE');select=w.locator('[data-resource-office-sheet]')
  for _ in range(2):select.select_option('1');expect(w.locator('.resource-preview')).to_contain_text('두 번째 값');expect(w.locator('.resource-preview')).to_contain_text('=HYPERLINK');select.select_option('0');expect(w.locator('.resource-preview')).to_contain_text('문자 <img>')
 elif extension=='pptx':expect(w.locator('.resource-document-slide p')).to_have_text(['첫 슬라이드','둘째 슬라이드'])
 drained()
def inputs(files):
 b.locator('[data-root]').click();b.locator('[data-new]').click()
 with f.page.expect_file_chooser()as event:f.page.locator('.context-menu').get_by_role('button',name='자료 추가',exact=True).click()
 event.value.set_files(files);expect(b.locator('[data-new]')).to_be_enabled();f.idle()
def delete(id):
 b.locator('[data-resource-id="'+id+'"]').click(button='right');f.page.get_by_role('button',name='삭제',exact=True).click();f.page.get_by_role('dialog',name='자료 삭제',exact=True).locator('[data-remove]').click();expect(b.locator('[data-resource-id="'+id+'"]')).to_have_count(0);f.idle()
def clear():
 for w in f.page.locator('.window[data-key^="resource-file:"]').all():w.locator('[data-close]').first.click()
 drained();f.page.evaluate('()=>document.activeElement?.blur()');f.pending();ids=[x['id']for x in api()['items']if x['kind']!='folder']
 if len(ids)==1:delete(ids[0]);return
 for n,id in enumerate(ids):b.locator('[data-resource-id="'+id+'"]').click(modifiers=['Control']if n else[])
 b.locator('[data-resource-id="'+ids[0]+'"]').click(button='right');f.page.get_by_role('button',name=str(len(ids))+'개 항목 삭제',exact=True).click();f.page.get_by_role('dialog',name='자료 삭제',exact=True).locator('[data-remove]').click();expect(b.locator('[data-resource-id]')).to_have_count(0);f.idle()
def extra_formats():
 global baseline
 for extension in ['xlsx','pptx']:inputs([dict(name='큰 추가.'+extension,mimeType='application/octet-stream',buffer=sample(extension,1234567))]);row=next(x for x in api()['items']if x['name']=='큰 추가.'+extension);w=opened(row['id']);ready(w,extension);closed(row['id'])
 delete(id);inputs([dict(name='큰 추가.odt',mimeType='application/octet-stream',buffer=sample('odt',1234567))]);row=next(x for x in api()['items']if x['name']=='큰 추가.odt');ready(opened(row['id']),'odt');closed(row['id']);f.checked('four existing Office formats display actual owned large ZIP/XML through one bounded read-only policy: DOCX heading/table, XLSX cached bool/formula/sheet switching, ordered PPTX and ODT; no code/relationship/macro execution')
 clear();raw=sample('docx',1050000,True);inputs([dict(name='큰 DTD.docx',mimeType='application/octet-stream',buffer=raw)]);row=next(x for x in api()['items']if x['kind']!='folder');w=opened(row['id']);expect(w.locator('[data-resource-preview-retry]')).to_be_enabled();drained();w.locator('[data-resource-preview-retry]').click();expect(w.locator('[data-resource-preview-retry]')).to_be_enabled();drained();f.checked('complete large ZIP with DTD/entity XML is rejected by unchanged parser policy with explicit retry, no external fetch or edit')
 clear();raw=sample('xlsx',4194304);inputs([dict(name='최대 워크북.xlsx',mimeType='application/octet-stream',buffer=raw)]);row=next(x for x in api()['items']if x['kind']!='folder');baseline=store.read_bytes();before=f.page.evaluate('()=>__officePartCalls.length');w=opened(row['id']);ready(w,'xlsx');calls=f.page.evaluate('n=>__officePartCalls.slice(n)',before);assert[x['part']for x in calls]==[0,1,2,3];f.page.screenshot(path=str(f.case/'actual-largest-office.png'));original();closed(row['id']);drained();f.checked('exact4MiB XLSX uses four pinned parts/full SHA and actual two-sheet values within unchanged ZIP/XML/DOM budgets; input and original source preserved')
def restart(index,project=None):
 f.pending();f.page.close();f.stop()
 if project:f.env['CONFECTORY_WEB_PROJECT']=str(project/'project.cproj')
 f.start(index);setup()
try:
 f.start(0)
 with sync_playwright()as p:
  expect.set_options(timeout=60000);f.browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);setup();browser();raw=sample('docx',1234567);inputs([dict(name='큰 문서 🧪.docx',mimeType='application/octet-stream',buffer=raw),dict(name='작은 슬라이드.pptx',mimeType='application/octet-stream',buffer=sample('pptx'))]);rows=api()['items'];id=next(x['id']for x in rows if x['name']=='큰 문서 🧪.docx');small=next(x['id']for x in rows if x['name']=='작은 슬라이드.pptx');baseline=store.read_bytes();f.page.locator('#chat-input').fill('큰 Office와 별개인 새 입력')
  if mode=='baseline':
   w=opened(id);expect(w.locator('.resource-preview')).to_contain_text('1 MiB를 넘는 파일');expect(w.locator('.resource-document')).to_have_count(0);assert workers()['created']==0;closed(id);ready(opened(small),'pptx',False);closed(small);drained();assert store.read_bytes()==baseline;original();f.checked('published baseline reproduces missing >1MiB Office preview with exact stored copy preserved and small Office renderer working')
  else:
   w=opened(id);ready(w);closed(id);drained();original();assert store.read_bytes()==baseline;f.checked('actual native >1MiB owned DOCX uses verified complete ZIP/SHA before real module Worker, original heading/table/literal text and read-only controls')
   if mode=='normal':
    target=dict(project=f.state()['projectId'],id=id,hash=hashlib.sha256(raw).hexdigest());header=observed(target,'readProjectResource')['result'];assert 'preview'not in header and 'imagePreview'not in header and 'pdfPreview'not in header and 'data'not in header and header['officePreview']['partBytes']==1048576 and header['officePreview']['extension']=='docx';q=dict(target,generation=header['item']['contentGeneration'],revision=header['displayRevision'],part=1);reply=observed(q);assert reply['ok']and base64.urlsafe_b64decode(reply['result']['data'])==raw[1048576:]
    for wrong in [dict(q,project=uuid.uuid4().hex),dict(q,id=uuid.uuid4().hex),dict(q,hash='0'*64),dict(q,generation='0'*64),dict(q,revision='0'*64),dict(q,part=-1),dict(q,part=2),dict(q,part=.5),dict(q,part='1'),dict(q,path='/outside'),target]:assert not observed(wrong)['ok']
    for endpoint in ['readProjectResourceImagePart','readProjectResourcePDFPart']:assert not observed(q,endpoint)['ok']
    assert observed(q,'projectResourceLayout')['error']['code']=='endpoint_denied';v=f.mount()
    try:
     for _ in range(100):
      denied=f.raw(dict(op='invoke',view=v['view'],scope=v['scope'],expectedRevision=v['revision'],requestId=uuid.uuid4().hex,endpoint='readProjectResourceOfficePart',input=q))
      if denied.get('error',{}).get('code')!='busy':break
      time.sleep(.02)
     assert denied['error']['code']=='endpoint_denied',denied
    finally:f.raw(dict(op='dispose',view=v['view']))
    for action in ['save-content','restore-content']:
     request=dict(project=target['project'],action=action,revision=header['displayRevision'],command=uuid.uuid4().hex,id=id,hash=target['hash'])
     if action=='save-content':request.update(type='text/plain',size=1,data=base64.urlsafe_b64encode(b'x').decode())
     f.invoke('projectResourceLayout',request,False)
    assert store.read_bytes()==baseline;f.checked('dedicated observation pins project/id/hash/import/display/part and rejects foreign/stale/path/type/mutation/image/PDF lanes; large save/restore still reject before writes')
    for action in ['descriptor','legacy']:
     before=workers()['created'];arm(action,None,'readProjectResource');w=opened(id)
     if action=='legacy':expect(w.locator('.resource-preview')).to_contain_text('1 MiB를 넘는 파일')
     else:expect(w.locator('[data-resource-preview-retry]')).to_be_enabled()
     assert workers()['created']==before;closed(id);drained()
    for action in ['corrupt','mix']:
     before=workers()['created'];arm(action);w=opened(id);expect(w.locator('[data-resource-preview-retry]')).to_be_enabled();assert workers()['created']==before;w.locator('[data-resource-preview-retry]').click();ready(w);closed(id);drained()
    before=workers()['created'];arm();w=opened(id);held();assert workers()['created']==before;field=w.locator('[data-resource-setting-description]');expect(field).not_to_have_attribute('readonly','');field.fill('조각 뒤에도 남을 Office 설명 🧪');release();ready(w);expect(field).to_have_value('조각 뒤에도 남을 Office 설명 🧪');field.press('Control+s');f.pending();f.idle();assert next(x for x in api()['items']if x['id']==id)['description']=='조각 뒤에도 남을 Office 설명 🧪';assert not observed(q)['ok'];closed(id);drained();f.checked('malformed/legacy capability and mixed/corrupt part allocate no Worker; exact-copy retry and late description survive decoder completion, explicit metadata save invalidates old part basis')
    damaged=json.loads(baseline);row=next(x for x in damaged['items']if x['id']==id);text=row['data'];at=len(text)-100;row['data']=text[:at]+('B'if text[at]=='A'else'A')+text[at+1:];before=workers()['created']
    try:store.write_text(json.dumps(damaged));w=opened(id);expect(w.locator('[data-resource-preview-retry]')).to_be_enabled();assert workers()['created']==before
    finally:store.write_bytes(baseline)
    w.locator('[data-resource-preview-retry]').click();ready(w);closed(id);drained();f.checked('native tail corruption outside first part rejects before any Worker; restoring generated fixture plus explicit retry recovers')
    extra_formats()
   elif mode=='lifecycle':
    before=workers()['created'];arm();w=opened(id);held();assert workers()['created']==before;listing=f.state()['listingId'];f.page.locator('#title').click();f.page.get_by_role('button',name='프로젝트 나가기',exact=True).click();expect(f.page.locator('.home-grid')).to_be_visible();release(True);drained();f.page.locator('[data-enter="'+listing+'"]').click();f.idle();ready(viewer(id));closed(id);drained();f.checked('Home retires accepted pending part without Worker; late failure cannot cross the current project/view')
    arm(part=0);w=opened(id);held();closed(id);w=opened(id);ready(w);release(True);ready(w);closed(id);drained();f.checked('repeated close/reopen fences old accepted response and owns only the new complete document')
    before=workers()['created'];arm();w=opened(id);held();w.locator('[data-fold]').first.click();release();f.page.wait_for_timeout(500);assert workers()['created']==before;w.locator('[data-fold]').first.click();ready(w);f.pending();presentation=json.dumps(f.state()['presentation']);assert base64.urlsafe_b64encode(raw).decode()not in presentation;restart(1);ready(viewer(id));assert workers()['created']==1;closed(id);drained();f.checked('folded pending parts allocate no Worker; unfold/cold restores owner/ID/hash through a fresh read, never ZIP/XML/partial transfer')
    permission=store.stat().st_mode;before=workers()['created']
    try:store.chmod(0);w=opened(id);expect(w.locator('[data-resource-preview-retry]')).to_be_enabled();assert workers()['created']==before
    finally:store.chmod(permission)
    w.locator('[data-resource-preview-retry]').click();ready(w);closed(id);drained();f.checked('actual native read denial creates no Worker; restoring fixture mode plus explicit retry preserves input and data')
    arm();w=opened(id);held();restart(2);ready(viewer(id));assert workers()['created']==1;otherProject=f.case/'same namespace other project';shutil.copytree(f.project,otherProject,ignore=shutil.ignore_patterns('.confectory','.build'));restart(3,otherProject);expect(viewer(id)).to_have_count(0);assert workers()['created']==0;restart(4,f.project);ready(viewer(id));f.checked('cold interruption discards pending transfer; same-namespace different project inherits no Office IDs/Worker/bytes, original owner restores without reimport')
   else:raise AssertionError(mode)
  expect(f.page.locator('#chat-input')).to_have_value('큰 Office와 별개인 새 입력');original();assert store.read_bytes()==baseline;f.pending();f.page.screenshot(path=str(f.case/('resource-office-parts-'+mode+'.png')));f.browser.close()
except Exception as error:
 if getattr(f,'page',None):
  try:f.page.screenshot(path=str(f.case/'failure.png'))
  except Exception:pass
 (f.case/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:
 f.stop();(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2));(f.case/'observations.json').write_text(json.dumps(observations,ensure_ascii=False,indent=2))
print('RESOURCE_OFFICE_PARTS_FIXTURE',f.case,flush=True)
