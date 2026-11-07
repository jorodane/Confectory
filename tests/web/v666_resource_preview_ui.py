"""Actual bounded native resource observations and authored read-only text window."""
import sys,json,pathlib,hashlib,base64,uuid,shutil,traceback,time
from playwright.sync_api import sync_playwright,expect
import v536_wide_mixed as f
mode=sys.argv[3];store=f.project/'.confectory/resources.v1.json';observations=[];b=None
def api(action,**args):return f.invoke('projectResources',dict(action=action,project=f.state()['projectId'],**args))['result']['result']
def add(name,raw,type='text/plain'):
 value=api('load');id=uuid.uuid4().hex;api('import',revision=value['revision'],command=uuid.uuid4().hex,item=dict(id=id,name=name,type=type,size=len(raw),hash=hashlib.sha256(raw).hexdigest(),modifiedAt=0,data=base64.urlsafe_b64encode(raw).decode()));return id
def original():
 for relative,raw in f.original.items():assert(f.project/relative).read_bytes()==raw,relative
 assert not f.errors and not f.external,(f.errors,f.external)
def browser():
 global b
 f.page.locator('#workspace').click(button='right',position=dict(x=700,y=260));f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]').last;b.locator('[data-tab=resource]').click();expect(b.locator('[data-new]')).to_be_enabled()
def viewer(id):return f.page.locator('.window[data-key="resource-file:'+id+'"]')
def opened(id,keyboard=False):
 row=b.locator('[data-resource-id="'+id+'"]');row.press('Enter')if keyboard else row.dblclick();w=viewer(id);expect(w).to_be_visible();return w
def closed(id):viewer(id).locator('[data-close]').first.click();expect(viewer(id)).to_have_count(0)
def observed(input,endpoint='readProjectResource'):
 v=f.mount()
 try:
  for _ in range(30):
   value=f.raw(dict(op='observe',view=v['view'],scope=v['scope'],endpoint=endpoint,input=input))
   if value.get('error',{}).get('code')!='busy':return value
   time.sleep(.02)
  raise AssertionError(value)
 finally:f.raw(dict(op='dispose',view=v['view']))
def setup():
 f.page=f.setup()
 def seen(response):
  try:
   data=response.request.post_data_json
   if isinstance(data,dict)and data.get('op')=='observe':observations.append(dict(request=data,result=response.json()))
  except Exception:pass
 f.page.on('response',seen);f.idle()
def hold_read():
 f.page.evaluate("""()=>{const original=fetch;let armed=true;globalThis.__previewReadHeld=false;fetch=async(...args)=>{let request;try{request=JSON.parse(args[1]?.body||'null')}catch{}const response=await original(...args);if(!armed||request?.op!=='observe'||request.endpoint!=='readProjectResource')return response;const actual=await response.clone().json();if(!actual.ok)return response;armed=false;globalThis.__previewActualRead=actual;globalThis.__previewReadHeld=true;return new Promise(resolve=>{globalThis.__releasePreviewRead=(failed=false)=>{fetch=original;resolve(failed?new Response(JSON.stringify({ok:false,error:{code:'owned_lost_read_reply'}}),{status:200,headers:{'Content-Type':'application/json'}}):response);};});};}""")
try:
 f.start(0)
 with sync_playwright()as p:
  expect.set_options(timeout=60000);f.browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);setup()
  raw='생성한 텍스트 🧪\r\n<script>globalThis.assetWasExecuted=true</script>\n<img src="https://must-not-load.invalid/test">\n'.encode();id=add('한글 원문 <안전>.html',raw,'text/html');wide='UTF16 한글 🧪\r\n둘째 줄';utf16=add('원문 UTF16.txt',b'\xfe\xff'+wide.encode('utf-16be'));binary=add('바이너리.bin',b'\x00\xfb\x01','application/octet-stream');baseline=store.read_bytes();browser();f.page.locator('#chat-input').fill('미리보기와 별개인 입력')
  w=opened(id,True);expect(w.locator('.resource-document-text')).to_have_text(raw.decode());assert w.locator('.resource-document-text').evaluate('el=>el.textContent')==raw.decode();expect(w.locator('pre script,pre img')).to_have_count(0);assert not f.page.evaluate('()=>globalThis.assetWasExecuted');expect(w.locator('[data-resource-setting-name]')).to_have_attribute('readonly','');expect(w.locator('[data-resource-content-save]')).to_have_count(0);expect(w.locator('[data-resource-content-edit]')).to_be_enabled();expect(f.page.locator('#chat-input')).to_have_value('미리보기와 별개인 입력');f.page.screenshot(path=str(f.case/'resource-text-preview.png'));assert store.read_bytes()==baseline;original();f.checked('actual keyboard-opened native read verifies SHA/identity and displays original UTF8/CRLF as literal read-only text in the authored resource window; HTML and external resources never execute')
  if mode=='normal':
   selected=next(row for row in api('load')['items']if row['id']==id);request=dict(project=f.state()['projectId'],id=id,hash=selected['hash']);good=observed(request);assert good['ok']and base64.urlsafe_b64decode(good['result']['data'])==raw
   for invalid in [dict(request,hash='0'*64),dict(request,id=uuid.uuid4().hex),dict(request,project=uuid.uuid4().hex),dict(request,action='import'),dict(request,path='/outside')]:assert not observed(invalid)['ok']
   assert observed(dict(action='import',**request),'projectResources')['error']['code']=='endpoint_denied';assert store.read_bytes()==baseline;original();f.checked('dedicated observation lane reads only exact current owned bytes; stale hash/unknown ID/foreign project/path/mutation fields and observing the import endpoint are rejected without writes')
   closed(id);w=opened(utf16);expect(w.locator('.resource-document-text')).to_have_text(wide);assert w.locator('.resource-document-text').evaluate('el=>el.textContent')==wide;closed(utf16);w=opened(binary);expect(w.locator('.resource-preview')).to_contain_text('이 형식의 미리보기는 아직 연결되지 않았어요');expect(w.locator('pre')).to_have_count(0);closed(binary);original();f.checked('authored BOM-based UTF16 text is displayed without rewriting bytes; unsupported binary format is explicit and never represented as a working renderer')
   permissions=store.stat().st_mode
   try:
    store.chmod(0);w=opened(id);expect(w.locator('[data-resource-preview-retry]')).to_be_enabled();expect(w.locator('pre')).to_have_count(0);expect(f.page.locator('#chat-input')).to_have_value('미리보기와 별개인 입력')
   finally:store.chmod(permissions)
   w.locator('[data-resource-preview-retry]').click();expect(w.locator('.resource-document-text')).to_have_text(raw.decode());assert store.read_bytes()==baseline;original();f.checked('real native file read refusal preserves store/query/other input and exposes an explicit same-ID/hash retry; restoring only fixture permissions recovers without import or rebase')
   closed(id);hold_read();w=opened(id);f.page.wait_for_function('()=>__previewReadHeld');w.locator('[data-close]').first.click();w=opened(id);expect(w.locator('.resource-document-text')).to_have_text(raw.decode());f.page.evaluate('()=>__releasePreviewRead(true)');expect(w.locator('.resource-document-text')).to_have_text(raw.decode());expect(w.locator('[data-resource-preview-retry]')).to_have_count(0);expect(viewer(id)).to_have_count(1);assert store.read_bytes()==baseline;original();f.checked('actual reply held after native success cannot place a late error into the same-key reopened window; repeat close/open creates one current read-only viewer')
  elif mode=='lifecycle':
   closed(id);hold_read();w=opened(id);f.page.wait_for_function('()=>__previewReadHeld');owner=f.state()['projectId'];listing=f.state()['listingId'];f.page.locator('#title').click();f.page.get_by_role('button',name='프로젝트 나가기',exact=True).click();expect(f.page.locator('.home-grid')).to_be_visible();assert not observed(dict(project=owner,id=id,hash=hashlib.sha256(raw).hexdigest()))['ok'];f.page.evaluate('()=>__releasePreviewRead(true)');f.page.locator('[data-enter="'+listing+'"]').click();f.idle();expect(viewer(id).locator('.resource-document-text')).to_have_text(raw.decode());assert store.read_bytes()==baseline;original();f.checked('Home/current-project restore retires the actual pending observation; a late failed response cannot replace the new owned preview or replay a mutation')
   f.pending();presentation=json.dumps(f.state()['presentation'],ensure_ascii=False);assert raw.decode()not in presentation and base64.urlsafe_b64encode(raw).decode()not in presentation;f.page.close();f.stop();f.start(1);setup();expect(viewer(id).locator('.resource-document-text')).to_have_text(raw.decode());assert store.read_bytes()==baseline;original();f.checked('real cold engine restores only owner/ID/hash layout and re-reads authorized bytes; raw text/base64 and pending requests are absent from durable presentation')
   other=f.case/'other same namespace';shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory','.build'));f.pending();f.page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(other/'project.cproj');f.start(2);setup();expect(f.page.locator('.window[data-key^="resource-file:"]')).to_have_count(0);assert api('load')['items']==[];assert store.read_bytes()==baseline;f.page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(f.project/'project.cproj');f.start(3);setup();expect(viewer(id).locator('.resource-document-text')).to_have_text(raw.decode());original();f.checked('same namespace/source IDs in another actual project cannot restore A resource windows or bytes; A return restores its own exact preview and source originals')
  else:raise AssertionError(mode)
  assert any(row['request']['endpoint']=='readProjectResource'for row in observations);assert not any(row.get('invoke',{}).get('endpoint')in ['editDraft','saveDraft','reviewDraft','confirmDraft','runProject','startAI']for row in f.traffic);assert store.read_bytes()==baseline;f.pending();original();f.page.screenshot(path=str(f.case/('preview-'+mode+'.png')));f.browser.close()
except Exception as error:
 (f.case/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:
 f.stop();(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'observations.json').write_text(json.dumps(observations,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2))
print('RESOURCE_PREVIEW_FIXTURE',f.case,flush=True)
