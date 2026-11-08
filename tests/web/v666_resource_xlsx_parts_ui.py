"""Owned XLSX cell edits via actual engine, byte-sidecar CAS and private recovery."""
import sys,json,pathlib,hashlib,base64,uuid,shutil,traceback,io,zipfile,time,random
from playwright.sync_api import sync_playwright,expect
import v536_wide_mixed as f
mode=sys.argv[3];b=None;observations=[];read_plan=None;mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';store=f.project/'.confectory/resources.v1.json'
from v666_resource_xlsx_fixture import parts as small_parts,archive,ns
parts=dict(small_parts);parts['xl/media/image.bin']=random.Random(20261108).randbytes(2*1048576);raw=archive(parts);assert 1048576<len(raw)<4194304
def api(action,**args):return f.invoke('projectResourceLayout',dict(action=action,project=f.state()['projectId'],**args))['result']['result']
def item():return next(x for x in api('load')['items']if x['id']==file)
def read():
 row=item();view=f.mount()
 try:
  for _ in range(100):
   result=f.raw(dict(op='observe',view=view['view'],scope=view['scope'],endpoint='readProjectResource',input=dict(project=f.state()['projectId'],id=file,hash=row['hash'])))
   if result.get('error',{}).get('code')=='busy':time.sleep(.02);continue
   assert result.get('ok'),result;header=result['result']
   if header.get('data')is not None:return base64.urlsafe_b64decode(header['data'])
   data=b''
   for part in range((row['size']+1048575)//1048576):
    query=dict(project=header['project'],id=file,hash=row['hash'],generation=row['contentGeneration'],revision=header['displayRevision'],part=part)
    for retry in range(100):
     chunk=f.raw(dict(op='observe',view=view['view'],scope=view['scope'],endpoint='readProjectResourceOfficePart',input=query))
     if chunk.get('error',{}).get('code')!='busy':break
     time.sleep(.02)
    assert chunk.get('ok'),chunk;data+=base64.urlsafe_b64decode(chunk['result']['data'])
   assert len(data)==row['size']and hashlib.sha256(data).hexdigest()==row['hash'];return data
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
def cold_field(w,text):
 before=sidecar().read_bytes();retries=0
 for attempt in range(3):
  f.page.wait_for_function('(key)=>document.querySelector(`.window[data-key="${key}"] [data-resource-xlsx-cell]`)||document.querySelector(`.window[data-key="${key}"] [data-resource-preview-retry]`)||document.querySelector(`.window[data-key="${key}"] [data-resource-content-retry]`)',arg=w.get_attribute('data-key'),timeout=60000)
  if field(w).count():break
  retry=w.locator('[data-resource-preview-retry],[data-resource-content-retry]');assert retry.count()==1
  assert sidecar().read_bytes()==before and f.page.evaluate('()=>__xlsxSourceCalls')==0
  retry.click();retries+=1
 expect(field(w)).to_have_value(text);assert sidecar().read_bytes()==before and f.page.evaluate('()=>__xlsxSourceCalls')==0
 if retries:f.checked('cold readonly observation retry uses existing UI without document Save or input loss: '+str(retries))
def setup():
 f.page=f.browser.new_page(viewport=dict(width=1280,height=900));f.page.on('pageerror',lambda e:f.errors.append(str(e)));f.page.on('response',f.observe);f.page.route('**/*',f.route)
 f.page.add_init_script("""(()=>{const Base=Worker;globalThis.__xlsxWorkers={created:0,terminated:0,held:0};globalThis.__holdXlsx='';globalThis.__releaseXlsx=[];Worker=class extends Base{constructor(...args){super(...args);if(!String(args[0]).includes('resource-xlsx-worker'))return;__xlsxWorkers.created++;let action='',dead=false;const post=this.postMessage.bind(this);this.postMessage=(value,...rest)=>{action=value.action;return post(value,...rest);};const desc=Object.getOwnPropertyDescriptor(Base.prototype,'onmessage');Object.defineProperty(this,'onmessage',{set:fn=>desc.set.call(this,fn?event=>{if(__holdXlsx===action){__xlsxWorkers.held++;__releaseXlsx.push(()=>fn(event));}else fn(event);}:null),get:()=>desc.get.call(this)});const stop=this.terminate.bind(this);this.terminate=()=>{if(!dead){dead=true;__xlsxWorkers.terminated++;}stop();};}};})();""");f.page.add_init_script("""(()=>{const base=fetch;globalThis.__xlsxDraftBusy=__BUSY__;globalThis.__xlsxDraftBusyCount=0;globalThis.__xlsxSourceCalls=0;fetch=async(...args)=>{let q;try{q=JSON.parse(args[1]?.body||'null')}catch{}if(q?.op==='invoke'&&q.endpoint==='resourceContentDraft'&&q.input?.action==='apply')__xlsxSourceCalls++;if(q?.op==='observe'&&q.endpoint==='readResourceContentDraftPart'&&__xlsxDraftBusy>0){__xlsxDraftBusy--;__xlsxDraftBusyCount++;return new Response(JSON.stringify({ok:false,error:{code:'busy'}}),{status:200,headers:{'Content-Type':'application/json'}});}return base(...args);};})();""".replace('__BUSY__','5'if mode=='lifecycle'else'0'));
 def observed(response):
  try:
   q=response.request.post_data_json
   if isinstance(q,dict)and q.get('op')=='observe'and(q.get('endpoint','').startswith('readResource')or q.get('endpoint','').startswith('readProjectResource')):
    result=response.json();data=result.get('result',{}).pop('data',None)
    if data is not None:result['wireData']={'characters':len(data),'sha256':hashlib.sha256(data.encode()).hexdigest()}
    observations.append(dict(request=q,result=result))
  except Exception:pass
 f.page.on('response',observed)
 f.page.add_init_script("""(()=>{const base=fetch;let plan=__PLAN__;globalThis.__privateReadHeld=false;globalThis.__privateReadCorrupt=false;fetch=async(...args)=>{let q;try{q=JSON.parse(args[1]?.body||'null')}catch{}const response=await base(...args);if(!plan||q?.op!=='observe'||q.endpoint!=='readResourceContentDraftPart'||q.input.part!==1)return response;const v=await response.clone().json();if(!v.ok)return response;const chosen=plan;plan=null;const made=()=>new Response(JSON.stringify(v),{status:200,headers:{'Content-Type':'application/json'}});if(chosen==='corrupt'){const text=v.result.data;v.result.data=(text[0]==='A'?'B':'A')+text.slice(1);__privateReadCorrupt=true;return made();}__privateReadHeld=true;return new Promise(resolve=>__releasePrivateRead=()=>resolve(made()));};})();""".replace('__PLAN__',json.dumps(read_plan)));f.goto_editor(f.page,f.url);f.idle()
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
  if value and text in value['changes'].values():
   f.page.evaluate('()=>confectoryFlushPresentation()');f.pending();return
 raise AssertionError(('private XLSX input not acknowledged',value))

def hold_native():
 f.page.evaluate("""()=>{const base=fetch;let wanted=null,armed=true;globalThis.__xlsxNativeHeld=false;fetch=async(...args)=>{let request;try{request=JSON.parse(args[1]?.body||'null')}catch{}if(armed&&request?.op==='invoke'&&request.endpoint==='resourceContentDraft'&&request.input?.action==='apply')wanted=request.requestId;const response=await base(...args);if(!wanted||!armed||request?.op!=='update')return response;const body=await response.clone().json(),row=body.results?.find(r=>r.requestId===wanted);if(!row?.ok)return response;armed=false;__xlsxNativeHeld=true;return new Promise(resolve=>{globalThis.__releaseXlsxNative=()=>{fetch=base;delete row.result;row.ok=false;row.error={code:'owned_xlsx_lost_reply'};resolve(new Response(JSON.stringify(body),{status:200,headers:{'Content-Type':'application/json'}}));};});};}""")
def source_acks():
 ids={x['invoke']['requestId']for x in f.traffic if x.get('invoke',{}).get('endpoint')=='resourceContentDraft'and x['invoke'].get('input',{}).get('action')=='apply'}
 return sum(x.get('result',{}).get('requestId')in ids and x['result'].get('ok')is True for x in f.traffic if'result'in x)
def hold_private():
 f.page.evaluate("""()=>{const base=fetch,uploads=new Map();let armed=true,wanted=null;globalThis.__privateCommitHeld=false;fetch=async(...args)=>{let q;try{q=JSON.parse(args[1]?.body||'null')}catch{}if(q?.op==='invoke'&&q.endpoint==='projectResources'){const x=q.input;if(x.action==='upload-begin'&&x.target==='draft-xlsx')uploads.set(x.id,[]);if(x.action==='upload-chunk'&&uploads.has(x.id))uploads.get(x.id)[x.offset]=Uint8Array.from(atob(x.data.replaceAll('-','+').replaceAll('_','/')),c=>c.charCodeAt(0));if(x.action==='upload-commit'&&uploads.has(x.id)&&armed){const chunks=uploads.get(x.id),length=Object.values(chunks).reduce((n,b)=>n+b.length,0),bytes=new Uint8Array(length);for(const[offset,part]of Object.entries(chunks))bytes.set(part,Number(offset));const value=JSON.parse(new TextDecoder().decode(bytes));if(value.value?.pending?.action==='save-content')wanted=q.requestId;}}const response=await base(...args);if(!armed||!wanted||q?.op!=='update')return response;const v=await response.clone().json(),row=v.results?.find(r=>r.requestId===wanted);if(!row?.ok)return response;armed=false;__privateCommitHeld=true;return new Promise(resolve=>__releasePrivateCommit=()=>{delete row.result;row.ok=false;row.error={code:'owned_lost_private_commit_reply'};resolve(new Response(JSON.stringify(v),{status:200,headers:{'Content-Type':'application/json'}}));});};}""")
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
  expect.set_options(timeout=60000);f.browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);setup();browser();b.locator('[data-resource-files]').set_input_files(dict(name='generated.xlsx',mimeType=mime,buffer=raw));f.idle();expect(b.locator('[data-new]')).to_be_enabled();file=api('load')['items'][0]['id'];baseline=store.read_bytes();w=opened();expect(w.locator('.resource-preview')).to_contain_text('original 🙂 sheet')
  if mode=='baseline':
   expect(w.locator('[data-resource-content-edit]')).to_have_count(0);assert read()==raw;untouched();f.checked('baseline published98aa9945 actual2MiB XLSX has only readonly preview and no content editor; original/project copy preserved');raise SystemExit(0)
  edit(w);field(w).fill('cancel <literal>');private_text('cancel <literal>');w.locator('[data-close]').first.click();dialog=f.page.locator('.modal[aria-label="저장하지 않은 변경"]');expect(dialog).to_be_visible();dialog.locator('[data-keep]').click();expect(field(w)).to_have_value('cancel <literal>');discard(w);assert read()==raw;untouched();f.checked('original worksheet/cell editor and formula/covered-merge refusal; private text plus close Keep/cancel preserve exact imported ZIP and C# originals')
  edit(w);save(w,'saved 🙂 <literal>');saved_bytes=read();assert json.loads(sidecar().read_bytes())['format']=='xlsx-v1';assert saved_bytes!=raw;assert item()['hasContentBackup'];f.checked('actual XLSX Save publishes cell data through native CAS/one-save backup, with independent Python CRC/XML/untouched-parts validation')
  w.locator('[data-resource-content-restore]').click();expect(w.locator('.resource-preview')).to_contain_text('original 🙂 sheet');f.idle();assert read()==raw;w.locator('[data-resource-content-restore]').click();expect(w.locator('.resource-preview')).to_contain_text('saved 🙂 <literal>');f.idle();assert read()==saved_bytes;untouched();f.checked('previous-content restore and restore cancel retain exact original and edited ZIP byte generations')
  f.page.locator('#chat-input').fill('independent XLSX input')
  if mode=='normal':
   edit(w);field(w,2).fill('2.5');w.locator('[data-resource-xlsx-cell="c:0:C1"]').fill('false');w.locator('[data-resource-xlsx-cell="c:0:G1"]').fill('001');w.locator('[data-resource-xlsx-sheet]').select_option('1');expect(w.locator('[data-resource-xlsx-cell="c:1:A1"]')).to_have_attribute('readonly','');w.locator('[data-resource-xlsx-sheet]').select_option('2');w.locator('[data-resource-xlsx-cell="c:2:A1"]').fill('=1+1');w.locator('[data-resource-xlsx-sheet]').select_option('0');save(w,'saved 🙂 <literal>');cells=sheet_cells(read());assert cells['B1'].attrib['t']=='n'and ''.join(cells['B1'].itertext())=='2.5';assert cells['C1'].attrib['t']=='b'and ''.join(cells['C1'].itertext())=='0';assert cells['G1'].attrib['t']=='inlineStr'and ''.join(cells['G1'].itertext())=='001';assert ''.join(sheet_cells(read(),'xl/worksheets/sheet3.xml')['A1'].itertext())=='=1+1';f.checked('actual sheet switching/private fields retain numeric, boolean, new leading-zero text and literal formula-looking text; protected sheet stays readonly and original formulas request recalculation')
   prior=sidecar().read_bytes();edit(w);field(w).fill('temporary reverted input');field(w).fill('saved 🙂 <literal>');w.locator('[data-resource-content-save]').click();expect(w.locator('[data-resource-content-edit]')).to_be_enabled();f.idle();assert sidecar().read_bytes()==prior;untouched();f.checked('reverting edits before Save leaves current, previous-content backup and receipt byte-exact without a native content write')
   edit(w);field(w).fill('saved 🙂 <literal>');f.page.evaluate('()=>__holdXlsx="read"');held=f.page.evaluate('()=>__xlsxWorkers.held');w.locator('[data-resource-content-save]').click();f.page.wait_for_function('(n)=>__xlsxWorkers.held>n',arg=held);field(w).fill('late input during no-op read');release();expect(field(w)).to_have_value('late input during no-op read');expect(w.locator('[data-resource-content-save]')).to_be_enabled();f.idle();assert sidecar().read_bytes()==prior;w.locator('[data-resource-content-save]').click();expect(w.locator('[data-resource-content-edit]')).to_be_enabled();f.idle();assert contents(read())=='late input during no-op read';untouched();f.checked('no-op read keeps later typing as a separate private change; only explicit next Save updates content and its backup')
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
   edit(w);field(w).fill('cold private input');private_text('cold private input');prior=sidecar().read_bytes();restart(1);w=viewer();cold_field(w,'cold private input');assert sidecar().read_bytes()==prior;discard(w);untouched();assert f.page.evaluate('()=>__xlsxDraftBusyCount')==5;f.checked('cold real engine restores binary base and semantic cell input after five controlled read-only busy refusals, without automatic document Save')
   edit(w);hold_native();field(w).fill('cold lost committed');w.locator('[data-resource-content-save]').click();f.page.wait_for_function('()=>__xlsxNativeHeld');f.page.evaluate('()=>__releaseXlsxNative()');expect(w.locator('[data-resource-content-save]')).to_have_text('저장 결과 다시 확인');expect(w.locator('[data-resource-content-save]')).to_be_enabled();prior=sidecar().read_bytes();restart(2);w=viewer();cold_field(w,'cold lost committed');w.locator('[data-resource-content-save]').click();expect(w.locator('[data-resource-content-edit]')).to_be_enabled();f.idle();assert sidecar().read_bytes()==prior and contents(read())=='cold lost committed';untouched();f.checked('cold uncertain Save retains intended ZIP and exact original command; explicit replay confirms existing receipt without toggling the backup')
   edit(w);field(w).fill('immediate project exit input');listing=f.state()['listingId'];f.page.locator('#title').click();f.page.get_by_role('button',name='프로젝트 나가기',exact=True).click();expect(f.page.locator('.home-grid')).to_be_visible();f.page.locator('[data-enter="'+listing+'"]').click();f.idle();w=viewer();expect(field(w)).to_have_value('immediate project exit input');discard(w);untouched();f.checked('project departure flushes private XLSX input before changing the active owner; returning preserves current file data and independent chat')
   other=f.case/'same namespace other project';shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory','.build'));restart(3,other);assert api('load')['items']==[];expect(viewer()).to_have_count(0);restart(4,f.project);w=viewer();expect(w.locator('[data-resource-content-edit]')).to_be_enabled();assert contents(read())=='cold lost committed';untouched();f.checked('different actual project with same namespace cannot inherit XLSX ID, private cell draft or binary data')
  elif mode=='transport':
   edit(w);before_applies=source_acks();hold_private();field(w).fill('private commit captured');w.locator('[data-resource-content-save]').click();f.page.wait_for_function('()=>__privateCommitHeld');assert contents(read())=='saved 🙂 <literal>';field(w).fill('typed during private commit reply');f.page.evaluate('()=>__releasePrivateCommit()');expect(field(w)).to_have_value('typed during private commit reply');expect(w.locator('[data-resource-content-save]')).to_be_enabled();private_text('typed during private commit reply');assert contents(read())=='private commit captured'and source_acks()==before_applies+1;assert any(x['request']['endpoint']=='readResourceDocxReceipt'and x['result'].get('result',{}).get('status')=='confirmed'for x in observations);f.checked('lost accepted private commit is confirmed through readonly receipt without replaying upload/source Save; newer typing survives captured ZIP publication')
   w.locator('[data-resource-content-save]').click();expect(w.locator('[data-resource-content-edit]')).to_be_enabled();f.idle();assert contents(read())=='typed during private commit reply';edit(w);field(w).fill('private bytes after corrupt part');private_text('private bytes after corrupt part');before=sidecar().read_bytes();private_before=profile().read_bytes();(f.case/'before-corrupt-source.json').write_bytes(before);(f.case/'before-corrupt-private.json').write_bytes(private_before);read_plan='corrupt';restart(1);w=viewer();expect(w.locator('[data-resource-content-retry]')).to_be_enabled();assert f.page.evaluate('()=>__privateReadCorrupt'),'controlled corrupt response not delivered';assert sidecar().read_bytes()==before,'corrupt private read changed source';assert profile().read_bytes()==private_before,dict(reason='private bytes changed',before=hashlib.sha256(private_before).hexdigest(),after=hashlib.sha256(profile().read_bytes()).hexdigest());assert f.page.evaluate('()=>__xlsxSourceCalls')==0;w.locator('[data-resource-content-retry]').click();expect(field(w)).to_have_value('private bytes after corrupt part');assert sidecar().read_bytes()==before and f.page.evaluate('()=>__xlsxSourceCalls')==0;f.checked('corrupt private part never reaches editor or changes private/source bytes; explicit same-owner readonly retry recovers exact input')
   private_text('private bytes after corrupt part');read_plan='hold';restart(2);w=viewer();f.page.wait_for_function('()=>__privateReadHeld');w.locator('[data-close]').first.click();expect(viewer()).to_have_count(0);f.page.evaluate('()=>__releasePrivateRead()');read_plan=None;w=opened();expect(field(w)).to_have_value('private bytes after corrupt part');assert sidecar().read_bytes()==before and f.page.evaluate('()=>__xlsxSourceCalls')==0;discard(w);untouched();f.checked('late accepted private part after close cannot reopen or overwrite a new view; exact private input recovers while project bytes remain unchanged')
  else:raise AssertionError(mode)
  expect(f.page.locator('#chat-input')).to_have_value('independent XLSX input');f.page.wait_for_function('()=>__xlsxWorkers.created===__xlsxWorkers.terminated');untouched();f.pending();f.page.screenshot(path=str(f.case/('xlsx-'+mode+'.png')));f.browser.close()
except Exception as e:
 page=getattr(f,'page',None)
 if page:
  try:(f.case/'failure.html').write_text(page.content());page.screenshot(path=str(f.case/'failure.png'),timeout=5000)
  except:pass
 (f.case/'failure.json').write_text(json.dumps(dict(error=repr(e),traceback=traceback.format_exc(),errors=f.errors,external=f.external),ensure_ascii=False));raise
finally:
 f.stop();(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2))
 # Preserve every exact large wire string once; manifests retain full SHA/bytes.
 blobs=f.case/'wire-inputs';blobs.mkdir(exist_ok=True)
 def captured(value,key=''):
  if key=='data'and isinstance(value,str)and len(value)>8192:
   raw=value.encode();digest=hashlib.sha256(raw).hexdigest();target=blobs/(digest+'.txt')
   if not target.exists():target.write_bytes(raw)
   return dict(wireText='wire-inputs/'+target.name,bytes=len(raw),sha256=digest)
  if isinstance(value,dict):return{k:captured(v,k)for k,v in value.items()}
  if isinstance(value,list):return[captured(v)for v in value]
  return value
 (f.case/'traffic.json').write_text(json.dumps(captured(f.traffic),ensure_ascii=False,indent=2));(f.case/'observations.json').write_text(json.dumps(observations,ensure_ascii=False,indent=2))
print('RESOURCE_XLSX_PARTS_UI_FIXTURE',f.case,flush=True)
