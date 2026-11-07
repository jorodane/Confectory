"""Real module-Worker/native-copy Office previews; generated ZIP/XML fixtures only."""
import sys,json,pathlib,hashlib,base64,uuid,shutil,traceback,io,zipfile
from playwright.sync_api import sync_playwright,expect
import v536_wide_mixed as f
mode=sys.argv[3];store=f.project/'.confectory/resources.v1.json';b=None
def archive(parts):
 out=io.BytesIO()
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED)as z:
  for name,text in parts.items():z.writestr(name,text.encode())
 return out.getvalue()
def add(name,raw):
 revision=f.invoke('projectResources',dict(project=f.state()['projectId'],action='load'))['result']['result']['revision'];id=uuid.uuid4().hex
 f.invoke('projectResources',dict(project=f.state()['projectId'],action='import',revision=revision,command=uuid.uuid4().hex,item=dict(id=id,name=name,type='application/octet-stream',size=len(raw),hash=hashlib.sha256(raw).hexdigest(),modifiedAt=0,data=base64.urlsafe_b64encode(raw).decode())));return id
def setup():
 f.page=f.browser.new_page(viewport=dict(width=1280,height=900));f.page.on('pageerror',lambda e:f.errors.append(str(e)));f.page.on('response',f.observe);f.page.route('**/*',f.route)
 f.page.add_init_script("""(()=>{const Base=Worker;globalThis.__officeWorkers={created:0,terminated:0,held:0};globalThis.__holdOffice=false;globalThis.__releaseOffice=[];globalThis.Worker=class extends Base{constructor(...args){super(...args);const url=String(args[0]);if(!url.includes('resource-office-worker'))return;__officeWorkers.created++;const desc=Object.getOwnPropertyDescriptor(Base.prototype,'onmessage');Object.defineProperty(this,'onmessage',{set:fn=>desc.set.call(this,fn?event=>{if(__holdOffice){__officeWorkers.held++;__releaseOffice.push(()=>fn(event));}else fn(event);}:null),get:()=>desc.get.call(this)});let done=false;const stop=this.terminate.bind(this);this.terminate=()=>{if(!done){done=true;__officeWorkers.terminated++;}stop();};}};})();""")
 f.goto_editor(f.page,f.url);f.idle()
def browser():
 global b
 f.page.locator('#workspace').click(button='right',position=dict(x=700,y=260));f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]').last;b.locator('[data-tab=resource]').click();expect(b.locator('[data-new]')).to_be_enabled()
def viewer(id):return f.page.locator('.window[data-key="resource-file:'+id+'"]')
def opened(id):
 b.locator('[data-resource-id="'+id+'"]').press('Enter');w=viewer(id);expect(w).to_be_visible();return w
def ready(w,text):
 expect(w.locator('.resource-preview')).to_have_attribute('aria-busy','false');expect(w.locator('.resource-preview')).to_contain_text(text);expect(w.locator('[data-resource-content-save]')).to_have_count(0)
 if w.locator('[data-resource-preview-title]').inner_text().startswith('DOCX'):expect(w.locator('[data-resource-content-edit]')).to_be_enabled()
 else:expect(w.locator('[data-resource-content-edit]')).to_have_count(0)
def closed(id):opened(id).locator('[data-close]').first.click();expect(viewer(id)).to_have_count(0)
def workers():return f.page.evaluate('()=>__officeWorkers')
def release():f.page.evaluate('()=>{__holdOffice=false;__releaseOffice.splice(0).forEach(fn=>fn());}')
def unchanged():
 assert store.read_bytes()==baseline
 for name,raw in f.original.items():assert(f.project/name).read_bytes()==raw,name
 assert not f.errors and not f.external,(f.errors,f.external)
 assert not list((f.project/'.confectory').glob('resource-content/*.json'))
def restart(index,project=None):
 global b
 f.pending();f.page.close();f.stop()
 if project:f.env['CONFECTORY_WEB_PROJECT']=str(project/'project.cproj')
 f.start(index);setup();b=f.page.locator('.window[data-key^="browser:project:"]').last
 if not b.count():browser()
try:
 f.start(0)
 with sync_playwright()as p:
  expect.set_options(timeout=60000);f.browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);setup()
  doc=archive({'word/document.xml':'<w:document xmlns:w="urn:w"><w:body><w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:rPr><w:b/></w:rPr><w:t>생성 문서 &lt;script&gt;</w:t></w:r></w:p><w:tbl><w:tr><w:tc><w:p><w:r><w:t>표 값</w:t></w:r></w:p></w:tc></w:tr></w:tbl></w:body></w:document>'})
  sheet=archive({'xl/workbook.xml':'<workbook xmlns:r="urn:r"><sheets><sheet name="첫 시트" r:id="r1"/><sheet name="둘째" r:id="r2"/></sheets></workbook>','xl/_rels/workbook.xml.rels':'<Relationships><Relationship Id="r1" Target="worksheets/sheet1.xml"/><Relationship Id="r2" Target="/xl/worksheets/sheet2.xml"/><Relationship Id="external" TargetMode="External" Target="https://must-not-load.invalid/"/></Relationships>','xl/sharedStrings.xml':'<sst><si><t>문자 &lt;img&gt;</t></si></sst>','xl/worksheets/sheet1.xml':'<worksheet><sheetData><row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1"><f>1+1</f><v>2</v></c><c r="C1" t="b"><v>1</v></c></row></sheetData></worksheet>','xl/worksheets/sheet2.xml':'<worksheet><sheetData><row r="3"><c r="A3"><f>HYPERLINK("https://must-not-load.invalid/")</f></c><c r="B3" t="inlineStr"><is><t>두 번째 값</t></is></c></row></sheetData></worksheet>'})
  slides=archive({'ppt/slides/slide2.xml':'<p:sld xmlns:p="urn:p" xmlns:a="urn:a"><a:p><a:r><a:t>둘째 슬라이드</a:t></a:r></a:p></p:sld>','ppt/slides/slide1.xml':'<p:sld xmlns:p="urn:p" xmlns:a="urn:a"><a:p><a:r><a:t>첫 슬라이드</a:t></a:r></a:p></p:sld>'});odt=archive({'content.xml':'<office:document xmlns:office="urn:o" xmlns:text="urn:t"><text:p>ODT 본문</text:p></office:document>'})
  ids=[add('문서.docx',doc),add('시트.xlsx',sheet),add('슬라이드.pptx',slides),add('본문.odt',odt),add('추가.docx',doc)]
  bad=add('DTD.docx',archive({'word/document.xml':'<!DOCTYPE document [<!ENTITY test SYSTEM "https://must-not-load.invalid/">]><document>&test;</document>'}));crc=bytearray(doc);at=crc.index(b'PK\x01\x02');crc[at+16]^=1;badcrc=add('CRC.docx',bytes(crc));zip64=bytearray(doc);zip64[at+24:at+28]=b'\xff'*4;bad64=add('ZIP64.docx',bytes(zip64));broken=add('손상.docx',b'not a zip')
  baseline=store.read_bytes();browser();f.page.locator('#chat-input').fill('Office와 별개인 입력');f.page.locator('#chat-input').press('Tab');f.idle()
  w=opened(ids[0]);ready(w,'생성 문서 <script>');expect(w.locator('.resource-document h2 span')).to_have_css('font-weight','700');expect(w.locator('.resource-document td')).to_have_text('표 값');expect(w.locator('.resource-preview script')).to_have_count(0);unchanged();f.checked('real native SHA-verified DOCX/DEFLATE/module Worker renders bounded authored heading/table/literal text under existing CSP; no editor or data mutation')
  if mode=='normal':
   for id,text in zip(ids[1:4],['문자 <img>','첫 슬라이드','ODT 본문']):ready(opened(id),text)
   x=viewer(ids[1]);expect(x.locator('td').nth(1)).to_have_text('2');expect(x.locator('td').nth(2)).to_have_text('TRUE');select=x.locator('[data-resource-office-sheet]')
   for _ in range(3):select.select_option('1');ready(x,'두 번째 값');expect(x.locator('.resource-preview')).to_contain_text('=HYPERLINK');select.select_option('0');ready(x,'문자 <img>')
   expect(viewer(ids[2]).locator('.resource-document-slide p')).to_have_text(['첫 슬라이드','둘째 슬라이드']);unchanged();f.checked('real XLSX cached values/bool/shared text and repeated worksheet switching, numeric ordered PPTX and ODT text; formula remains literal and external relation never fetched')
   count=workers()['created'];fifth=opened(ids[4]);expect(fifth.locator('[data-resource-preview-retry]')).to_be_enabled();assert workers()['created']==count;closed(ids[0]);fifth=opened(ids[4]);fifth.locator('[data-resource-preview-retry]').click();ready(fifth,'생성 문서');closed(ids[4]);[closed(id)for id in ids[1:4]];f.checked('four active Office view leases enforce quota without fifth Worker; closing releases slot and explicit retry succeeds')
   for id in [bad,badcrc,bad64,broken]:
    w=opened(id);expect(w.locator('[data-resource-preview-retry]')).to_be_enabled();w.locator('[data-resource-preview-retry]').click();expect(w.locator('[data-resource-preview-retry]')).to_be_enabled();closed(id);unchanged()
   assert workers()['created']==workers()['terminated'];f.checked('DTD/external entity, CRC mismatch, ZIP64 and broken ZIP fail in real browser with bounded explicit retry; every failed Worker terminated and copies retained')
   f.page.evaluate('()=>__holdOffice=true');held=workers()['held'];w=opened(ids[0]);f.page.wait_for_function('(n)=>__officeWorkers.held>n',arg=held);closed(ids[0]);release();w=opened(ids[0]);ready(w,'생성 문서');f.page.evaluate("""()=>{const base=fetch;globalThis.__officeUpdatesHeld=0;const queue=[];fetch=async(...args)=>{const result=await base(...args);let req;try{req=JSON.parse(args[1]?.body||'null')}catch{}if(req?.op==='update'){__officeUpdatesHeld++;return new Promise(resolve=>queue.push(()=>resolve(result)));}return result;};globalThis.__releaseOfficeUpdates=()=>{fetch=base;queue.splice(0).forEach(resolve=>resolve());};}""");f.page.wait_for_function('()=>__officeUpdatesHeld>0');w.locator('[data-fold]').first.click();expect(w.locator('.resource-document')).to_have_count(0);w.locator('[data-fold]').first.click();ready(w,'생성 문서');f.page.evaluate('()=>__releaseOfficeUpdates()');unchanged();f.checked('held real Worker result after close/reopen cannot paint retired generation; fold/unfold retires and re-reads the same owner/ID')
   closed(ids[0]);f.page.evaluate('()=>__holdOffice=true');held=workers()['held'];w=opened(ids[0]);f.page.wait_for_function('(n)=>__officeWorkers.held>n',arg=held);expect(w.locator('[data-resource-preview-retry]')).to_be_enabled(timeout=15000);release();expect(w.locator('.resource-preview .resource-document')).to_have_count(0);w.locator('[data-resource-preview-retry]').click();ready(w,'생성 문서');unchanged();f.checked('actual Worker reply held beyond five-second deadline terminates once; late callback cannot replace failure, explicit authorized re-read recovers')
  elif mode=='lifecycle':
   f.pending();presentation=json.dumps(f.state()['presentation']);assert base64.urlsafe_b64encode(doc).decode()not in presentation;restart(1);w=viewer(ids[0]);ready(w,'생성 문서');unchanged();f.checked('cold engine restores owner/ID/hash and re-reads Office copy through new Worker; ZIP/XML/Worker state is not persisted')
   closed(ids[0]);permission=store.stat().st_mode
   try:store.chmod(0);w=opened(ids[0]);expect(w.locator('[data-resource-preview-retry]')).to_be_enabled();assert workers()['created']==workers()['terminated']
   finally:store.chmod(permission)
   w.locator('[data-resource-preview-retry]').click();ready(w,'생성 문서');unchanged();f.checked('real native read permission failure creates no Worker; explicit retry after restoring fixture mode retains data/input and succeeds')
   closed(ids[0]);f.page.evaluate('()=>__holdOffice=true');held=workers()['held'];w=opened(ids[0]);f.page.wait_for_function('(n)=>__officeWorkers.held>n',arg=held);listing=f.state()['listingId'];f.page.locator('#title').click();f.page.get_by_role('button',name='프로젝트 나가기',exact=True).click();expect(f.page.locator('.home-grid')).to_be_visible();release();assert workers()['created']==workers()['terminated'];f.page.locator('[data-enter="'+listing+'"]').click();f.idle();w=viewer(ids[0]);ready(w,'생성 문서');unchanged();f.checked('Home transition terminates held Worker; late result cannot cross owner generation and original project returns without reimport')
   other=f.case/'same namespace other project';shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory','.build'));restart(2,other);expect(viewer(ids[0])).to_have_count(0);assert workers()['created']==0;restart(3,f.project);w=viewer(ids[0]);ready(w,'생성 문서');unchanged();f.checked('real second project with same namespace has no Office IDs/Worker state; returning to original owner restores authorized copy')
  else:raise AssertionError(mode)
  expect(f.page.locator('#chat-input')).to_have_value('Office와 별개인 입력');unchanged();f.pending();f.page.screenshot(path=str(f.case/('resource-office-'+mode+'.png')));closed(ids[0]);assert workers()['created']==workers()['terminated'];f.browser.close()
except Exception as error:
 (f.case/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:
 f.stop();(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2))
print('RESOURCE_OFFICE_FIXTURE',f.case,flush=True)
