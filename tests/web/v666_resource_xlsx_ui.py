"""Owned XLSX cell edits via actual engine, byte-sidecar CAS and private recovery."""
import sys,json,pathlib,hashlib,base64,uuid,shutil,traceback,io,zipfile,time
from playwright.sync_api import sync_playwright,expect
import v536_wide_mixed as f
mode=sys.argv[3];b=None;mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';store=f.project/'.confectory/resources.v1.json'
from v666_resource_xlsx_fixture import parts,raw,ns
def api(action,**args):return f.invoke('projectResourceLayout',dict(action=action,project=f.state()['projectId'],**args))['result']['result']
def item():return next(x for x in api('load')['items']if x['id']==file)
def read():
 row=item();view=f.mount()
 try:
  for _ in range(100):
   result=f.raw(dict(op='observe',view=view['view'],scope=view['scope'],endpoint='readProjectResource',input=dict(project=f.state()['projectId'],id=file,hash=row['hash'])))
   if result.get('error',{}).get('code')=='busy':time.sleep(.02);continue
   assert result.get('ok'),result;return base64.urlsafe_b64decode(result['result']['data'])
  raise AssertionError('native XLSX read stayed busy')
 finally:f.raw(dict(op='dispose',view=view['view']))
def sheet_cells(value,path='xl/worksheets/sheet1.xml'):
 import xml.etree.ElementTree as et
 with zipfile.ZipFile(io.BytesIO(value)) as z:return {c.attrib['r']:c for c in et.fromstring(z.read(path)).findall('.//{'+ns+'}c')}
def contents(value):
 import xml.etree.ElementTree as et
 with zipfile.ZipFile(io.BytesIO(value))as z:
  assert z.testzip()is None
  for name,data in parts.items():
   if name not in ['xl/workbook.xml','xl/worksheets/sheet1.xml','xl/worksheets/sheet3.xml','xl/worksheets/sheet4.xml']:assert z.read(name)==(data.encode()if isinstance(data,str)else data),name
  doc=et.fromstring(z.read('xl/worksheets/sheet1.xml'));assert doc.find('.//{'+ns+'}mergeCell').attrib['ref']=='E1:F1';cells={c.attrib['r']:c for c in doc.findall('.//{'+ns+'}c')};assert cells['A1'].attrib['s']=='1'and cells['B1'].attrib['s']=='2';assert cells['D1'].find('{'+ns+'}f').text=='B1*2'and cells['D1'].find('{'+ns+'}v')is None;other=et.fromstring(z.read('xl/worksheets/sheet4.xml'));assert other.find('.//{'+ns+'}f').text=='1+1'and other.find('.//{'+ns+'}v')is None;calc=et.fromstring(z.read('xl/workbook.xml')).find('{'+ns+'}calcPr');assert calc.attrib['fullCalcOnLoad']=='1'and calc.attrib['forceFullCalc']=='1'and calc.attrib['calcMode']=='auto';return ''.join(cells['A1'].itertext())
def untouched():
 assert store.read_bytes()==baseline
 for path,data in f.original.items():assert(f.project/path).read_bytes()==data,path
 assert not f.errors and not f.external,(f.errors,f.external)
def setup():
 f.page=f.browser.new_page(viewport=dict(width=1280,height=900));f.page.on('pageerror',lambda e:f.errors.append(str(e)));f.page.on('response',f.observe);f.page.route('**/*',f.route)
 f.page.add_init_script("""(()=>{const Base=Worker;globalThis.__xlsxWorkers={created:0,terminated:0,held:0};globalThis.__holdXlsx='';globalThis.__releaseXlsx=[];Worker=class extends Base{constructor(...args){super(...args);if(!String(args[0]).includes('resource-xlsx-worker'))return;__xlsxWorkers.created++;let action='',dead=false;const post=this.postMessage.bind(this);this.postMessage=(value,...rest)=>{action=value.action;return post(value,...rest);};const desc=Object.getOwnPropertyDescriptor(Base.prototype,'onmessage');Object.defineProperty(this,'onmessage',{set:fn=>desc.set.call(this,fn?event=>{if(__holdXlsx===action){__xlsxWorkers.held++;__releaseXlsx.push(()=>fn(event));}else fn(event);}:null),get:()=>desc.get.call(this)});const stop=this.terminate.bind(this);this.terminate=()=>{if(!dead){dead=true;__xlsxWorkers.terminated++;}stop();};}};})();""");f.goto_editor(f.page,f.url);f.idle()
def browser():
 global b
 f.page.locator('#workspace').click(button='right',position=dict(x=700,y=260));f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]').last;b.locator('[data-tab=resource]').click();expect(b.locator('[data-new]')).to_be_enabled()
def viewer():return f.page.locator('.window[data-key="resource-file:'+file+'"]')
def opened():
 b.locator('[data-resource-id="'+file+'"]').press('Enter');w=viewer()
 if 'folded'in(w.get_attribute('class')or'').split():w.locator('[data-fold]').first.click()
 expect(w.locator('.resource-preview')).to_have_attribute('aria-busy','false');return w
def field(w,index=0):return w.locator('[data-resource-xlsx-cell="c:0:'+['A1','D1','B1'][index]+'"]')
def edit(w):
 w.locator('[data-resource-content-edit]').click();expect(field(w)).to_be_editable();expect(field(w,1)).to_have_attribute('readonly','');expect(field(w,2)).to_be_editable();expect(w.locator('[data-resource-xlsx-cell="c:0:F1"]')).to_have_attribute('readonly','');f.idle()
def save(w,text):
 field(w).fill(text);w.locator('[data-resource-content-save]').click();expect(w.locator('[data-resource-content-edit]')).to_be_enabled();f.idle();assert contents(read())==text;untouched()
def sidecar():return f.project/'.confectory/resource-content'/ (file+'.v1.json')
def profile():return next(f.storage.rglob(file+'.json'))
def discard(w):
 w.locator('[data-resource-content-cancel]').click();dialog=f.page.locator('.modal[aria-label="저장하지 않은 변경"]');dialog.locator('[data-discard]').click();expect(dialog).to_have_count(0);expect(w.locator('[data-resource-content-edit]')).to_be_enabled();f.idle()
def private_text(text):
 deadline=time.monotonic()+15;value=None
 while time.monotonic()<deadline:
  f.page.wait_for_timeout(50)
  try:value=json.loads(profile().read_text())['value']
  except (StopIteration,ValueError,FileNotFoundError):continue
  if value and text in value['changes'].values():return
 raise AssertionError(('private XLSX input not acknowledged',value))

def hold_native():
 f.page.evaluate("""()=>{const base=fetch;let wanted=null,armed=true;globalThis.__xlsxNativeHeld=false;fetch=async(...args)=>{let request;try{request=JSON.parse(args[1]?.body||'null')}catch{}if(armed&&request?.op==='invoke'&&request.endpoint==='projectResourceLayout'&&request.input?.action==='save-content')wanted=request.requestId;const response=await base(...args);if(!wanted||!armed||request?.op!=='update')return response;const body=await response.clone().json(),row=body.results?.find(r=>r.requestId===wanted);if(!row?.ok)return response;armed=false;__xlsxNativeHeld=true;return new Promise(resolve=>{globalThis.__releaseXlsxNative=()=>{fetch=base;delete row.result;row.ok=false;row.error={code:'owned_xlsx_lost_reply'};resolve(new Response(JSON.stringify(body),{status:200,headers:{'Content-Type':'application/json'}}));};});};}""")
def release():f.page.evaluate('()=>{__holdXlsx="";__releaseXlsx.splice(0).forEach(fn=>fn());}')
def restart(index,project=None):
 global b
 f.pending();f.page.close();f.stop()
 if project:f.env['CONFECTORY_WEB_PROJECT']=str(project/'project.cproj')
 f.start(index);setup();b=f.page.locator('.window[data-key^="browser:project:"]').last
 if not b.count():browser()
 else:f.idle()
try:
 f.start(0)
 with sync_playwright()as p:
  expect.set_options(timeout=60000);f.browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);setup();browser();b.locator('[data-resource-files]').set_input_files(dict(name='generated.xlsx',mimeType=mime,buffer=raw));f.idle();expect(b.locator('[data-new]')).to_be_enabled();file=api('load')['items'][0]['id'];baseline=store.read_bytes();w=opened();expect(w.locator('.resource-preview')).to_contain_text('original 🙂 sheet');edit(w);field(w).fill('cancel <literal>');private_text('cancel <literal>');w.locator('[data-close]').first.click();dialog=f.page.locator('.modal[aria-label="저장하지 않은 변경"]');expect(dialog).to_be_visible();dialog.locator('[data-keep]').click();expect(field(w)).to_have_value('cancel <literal>');discard(w);assert read()==raw;untouched();f.checked('original worksheet/cell editor and formula/covered-merge refusal; private text plus close Keep/cancel preserve exact imported ZIP and C# originals')
  edit(w);save(w,'saved 🙂 <literal>');saved_bytes=read();assert saved_bytes!=raw;assert item()['hasContentBackup'];f.checked('actual XLSX Save publishes cell data through native CAS/one-save backup, with independent Python CRC/XML/untouched-parts validation')
  w.locator('[data-resource-content-restore]').click();expect(w.locator('.resource-preview')).to_contain_text('original 🙂 sheet');f.idle();assert read()==raw;w.locator('[data-resource-content-restore]').click();expect(w.locator('.resource-preview')).to_contain_text('saved 🙂 <literal>');f.idle();assert read()==saved_bytes;untouched();f.checked('previous-content restore and restore cancel retain exact original and edited ZIP byte generations')
  f.page.locator('#chat-input').fill('independent XLSX input')
  if mode=='normal':
   edit(w);field(w,2).fill('2.5');w.locator('[data-resource-xlsx-cell="c:0:C1"]').fill('false');w.locator('[data-resource-xlsx-cell="c:0:G1"]').fill('001');w.locator('[data-resource-xlsx-sheet]').select_option('1');expect(w.locator('[data-resource-xlsx-cell="c:1:A1"]')).to_have_attribute('readonly','');w.locator('[data-resource-xlsx-sheet]').select_option('2');w.locator('[data-resource-xlsx-cell="c:2:A1"]').fill('=1+1');w.locator('[data-resource-xlsx-sheet]').select_option('0');save(w,'typed values 🙂');cells=sheet_cells(read());assert cells['B1'].attrib['t']=='n'and ''.join(cells['B1'].itertext())=='2.5';assert cells['C1'].attrib['t']=='b'and ''.join(cells['C1'].itertext())=='0';assert cells['G1'].attrib['t']=='inlineStr'and ''.join(cells['G1'].itertext())=='001';assert ''.join(sheet_cells(read(),'xl/worksheets/sheet3.xml')['A1'].itertext())=='=1+1';f.checked('actual sheet switching/private fields retain numeric, boolean, new leading-zero text and literal formula-looking text; protected sheet stays readonly and original formulas request recalculation')
   edit(w);permission=sidecar().stat().st_mode;before=sidecar().read_bytes()
   try:
    sidecar().chmod(0o444);field(w).fill('write failure input');w.locator('[data-resource-content-save]').click();expect(w.locator('[data-resource-content-save]')).to_have_text('저장 결과 다시 확인');expect(w.locator('[data-resource-content-save]')).to_be_enabled();assert sidecar().read_bytes()==before;expect(field(w)).to_have_value('write failure input')
   finally:sidecar().chmod(permission)
   w.locator('[data-resource-content-save]').click();expect(w.locator('[data-resource-content-edit]')).to_be_enabled();f.idle();assert contents(read())=='write failure input';untouched();f.checked('actual readonly content write refusal preserves binary pending request and cell input; exact retry recovers without reimport or source rewrite')
   edit(w);f.page.evaluate('()=>__holdXlsx="write"');held=f.page.evaluate('()=>__xlsxWorkers.held');field(w).fill('captured worker text');w.locator('[data-resource-content-save]').click();f.page.wait_for_function('(n)=>__xlsxWorkers.held>n',arg=held);field(w).fill('typed during worker compression');release();expect(field(w)).to_have_value('typed during worker compression');expect(w.locator('[data-resource-content-save]')).to_be_enabled();f.idle();assert contents(read())=='captured worker text';w.locator('[data-resource-content-save]').click();expect(w.locator('[data-resource-content-edit]')).to_be_enabled();f.idle();assert contents(read())=='typed during worker compression';untouched();f.checked('late typing while real compression worker replies is retained as a separate cell change after the captured binary Save, then explicitly saved')
   edit(w);hold_native();field(w).fill('native committed');w.locator('[data-resource-content-save]').click();f.page.wait_for_function('()=>__xlsxNativeHeld');field(w).fill('typed during native response');f.page.evaluate('()=>__releaseXlsxNative()');expect(w.locator('[data-resource-content-save]')).to_have_text('저장 결과 다시 확인');expect(w.locator('[data-resource-content-save]')).to_be_enabled();prior=sidecar().read_bytes();w.locator('[data-resource-content-save]').click();expect(field(w)).to_have_value('typed during native response');expect(w.locator('[data-resource-content-save]')).to_be_enabled();f.idle();assert sidecar().read_bytes()==prior and contents(read())=='native committed';w.locator('[data-resource-content-save]').click();expect(w.locator('[data-resource-content-edit]')).to_be_enabled();f.idle();assert contents(read())=='typed during native response';untouched();f.checked('lost native success reply replays exact frozen ZIP without another backup; newer typing survives receipt confirmation and its own explicit Save')
   edit(w);field(w).fill('stale local text');current=api('load');api('describe',revision=current['revision'],command=uuid.uuid4().hex,id=file,generation=item()['descriptionGeneration'],value='peer metadata');w.locator('[data-resource-content-save]').click();expect(w.locator('[data-resource-content-save]')).to_have_text('저장 결과 다시 확인');expect(w.locator('[data-resource-content-save]')).to_be_enabled();prior=sidecar().read_bytes();w.locator('[data-resource-content-save]').click();expect(w.locator('[data-resource-content-save]')).to_be_enabled();assert sidecar().read_bytes()==prior;discard(w);assert contents(read())=='typed during native response';untouched();f.checked('peer metadata after edit capture rejects old content basis through repeat/retry; explicit discard refreshes current data without implicit rebasing')
   edit(w);field(w).fill('held worker close');private_text('held worker close');held=f.page.evaluate('()=>__xlsxWorkers.held');f.page.evaluate('()=>__holdXlsx="write"');w.locator('[data-resource-content-save]').click();f.page.wait_for_function('(n)=>__xlsxWorkers.held>n',arg=held);w.locator('[data-fold]').first.click();f.page.wait_for_function('()=>__xlsxWorkers.created===__xlsxWorkers.terminated');release();w.locator('[data-fold]').first.click();expect(field(w)).to_have_value('held worker close');discard(w);untouched();f.checked('fold terminates an in-flight write Worker, ignores its held late callback and restores private cell input on unfold without writing the file')
  elif mode=='lifecycle':
   edit(w);field(w).fill('cold private input');private_text('cold private input');prior=sidecar().read_bytes();restart(1);w=viewer();expect(field(w)).to_have_value('cold private input');assert sidecar().read_bytes()==prior;discard(w);untouched();f.checked('cold real engine restores binary base and semantic cell input without automatic document Save')
   edit(w);hold_native();field(w).fill('cold lost committed');w.locator('[data-resource-content-save]').click();f.page.wait_for_function('()=>__xlsxNativeHeld');f.page.evaluate('()=>__releaseXlsxNative()');expect(w.locator('[data-resource-content-save]')).to_have_text('저장 결과 다시 확인');expect(w.locator('[data-resource-content-save]')).to_be_enabled();prior=sidecar().read_bytes();restart(2);w=viewer();expect(field(w)).to_have_value('cold lost committed');w.locator('[data-resource-content-save]').click();expect(w.locator('[data-resource-content-edit]')).to_be_enabled();f.idle();assert sidecar().read_bytes()==prior and contents(read())=='cold lost committed';untouched();f.checked('cold uncertain Save retains intended ZIP and exact original command; explicit replay confirms existing receipt without toggling the backup')
   edit(w);field(w).fill('immediate project exit input');listing=f.state()['listingId'];f.page.locator('#title').click();f.page.get_by_role('button',name='프로젝트 나가기',exact=True).click();expect(f.page.locator('.home-grid')).to_be_visible();f.page.locator('[data-enter="'+listing+'"]').click();f.idle();w=viewer();expect(field(w)).to_have_value('immediate project exit input');discard(w);untouched();f.checked('project departure flushes private XLSX input before changing the active owner; returning preserves current file data and independent chat')
   other=f.case/'same namespace other project';shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory','.build'));restart(3,other);assert api('load')['items']==[];expect(viewer()).to_have_count(0);restart(4,f.project);w=viewer();expect(w.locator('[data-resource-content-edit]')).to_be_enabled();assert contents(read())=='cold lost committed';untouched();f.checked('different actual project with same namespace cannot inherit XLSX ID, private cell draft or binary data')
  else:raise AssertionError(mode)
  expect(f.page.locator('#chat-input')).to_have_value('independent XLSX input');f.page.wait_for_function('()=>__xlsxWorkers.created===__xlsxWorkers.terminated');untouched();f.pending();f.page.screenshot(path=str(f.case/('xlsx-'+mode+'.png')));f.browser.close()
except Exception as e:
 page=getattr(f,'page',None)
 if page:
  try:(f.case/'failure.html').write_text(page.content());page.screenshot(path=str(f.case/'failure.png'),timeout=5000)
  except:pass
 (f.case/'failure.json').write_text(json.dumps(dict(error=repr(e),traceback=traceback.format_exc(),errors=f.errors,external=f.external),ensure_ascii=False));raise
finally:f.stop();(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2))
print('RESOURCE_XLSX_UI_FIXTURE',f.case,flush=True)
