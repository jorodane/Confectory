"""Real generated File copies, native part observations and decoded image pixels.
Delayed/corrupted replies are controlled transport fixtures, not external users.
"""
import sys,json,pathlib,hashlib,base64,uuid,shutil,traceback,time,io,random
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
def urls():return f.page.evaluate('()=>structuredClone(__pdfPartURLs)')
def setup():
 global b
 f.page=f.browser.new_page(viewport=dict(width=1280,height=900));f.page.on('pageerror',lambda e:f.errors.append(str(e)));f.page.on('response',f.observe);f.page.route('**/*',f.route)
 f.page.add_init_script("""(()=>{const Base=Worker;globalThis.__pdfWorkers={created:0,terminated:0};globalThis.Worker=class extends Base{constructor(...args){super(...args);if(!String(args[0]).includes('resource-pdf-worker'))return;__pdfWorkers.created++;let stopped=false;const stop=this.terminate.bind(this);this.terminate=()=>{if(!stopped){stopped=true;__pdfWorkers.terminated++;}stop();};}};})();""")
 f.page.add_init_script("""(()=>{const create=URL.createObjectURL.bind(URL),revoke=URL.revokeObjectURL.bind(URL);globalThis.__pdfPartURLs={live:[],created:[],revoked:[]};URL.createObjectURL=blob=>{const value=create(blob);if(['image/png','image/jpeg'].includes(blob.type)){__pdfPartURLs.live.push(value);__pdfPartURLs.created.push(value);}return value;};URL.revokeObjectURL=value=>{if(__pdfPartURLs.live.includes(value)){__pdfPartURLs.live=__pdfPartURLs.live.filter(x=>x!==value);__pdfPartURLs.revoked.push(value);}return revoke(value);};const base=fetch;globalThis.__pdfPartPlan={};globalThis.__pdfPartHeld=false;globalThis.__pdfPartCalls=[];fetch=async(...args)=>{let request;try{request=JSON.parse(args[1]?.body||'null')}catch{}if(request?.op==='observe'&&request.endpoint==='readProjectResourcePDFPart')__pdfPartCalls.push(structuredClone(request.input));const response=await base(...args);if(request?.op!=='observe')return response;const plan=__pdfPartPlan[request.endpoint];if(!plan||plan.part!=null&&request.input?.part!==plan.part)return response;const body=await response.clone().json();if(!body.ok)return response;delete __pdfPartPlan[request.endpoint];const made=()=>new Response(JSON.stringify(body),{status:200,headers:{'Content-Type':'application/json'}});if(plan.action==='legacy'){delete body.result.pdfPreview;return made();}if(plan.action==='descriptor'){body.result.pdfPreview.partBytes--;return made();}if(plan.action==='corrupt'){body.result.data=(body.result.data[0]==='A'?'B':'A')+body.result.data.slice(1);return made();}if(plan.action==='mix'){body.result.item.contentGeneration='f'.repeat(64);return made();}__pdfPartHeld=true;return new Promise(resolve=>globalThis.__releasePDFPart=(failed=false)=>{if(failed){body.ok=false;delete body.result;body.error={code:'owned_lost_image_part'};}resolve(made());});};})();""")
 def seen(response):
  try:
   q=response.request.post_data_json
   if isinstance(q,dict)and q.get('op')=='observe':
    result=response.json();data=result.get('result',{}).pop('data',None)
    if data is not None:result['retainedData']={'bytes':len(data),'sha256':hashlib.sha256(data.encode()).hexdigest()}
    observations.append(dict(request=q,result=result))
  except Exception:pass
 f.page.on('response',seen);f.goto_editor(f.page,f.url);f.idle();b=f.page.locator('.window[data-key^="browser:project:"]').last
def arm(action='hold',part=1,endpoint='readProjectResourcePDFPart'):f.page.evaluate('({action,part,endpoint})=>{__pdfPartHeld=false;__pdfPartPlan[endpoint]={action,part};}',dict(action=action,part=part,endpoint=endpoint))
def held():f.page.wait_for_function('()=>__pdfPartHeld')
def release(failed=False):f.page.evaluate('failed=>__releasePDFPart(failed)',failed)
def observed(input,endpoint='readProjectResourcePDFPart'):
 v=f.mount()
 try:
  for _ in range(100):
   result=f.raw(dict(op='observe',view=v['view'],scope=v['scope'],endpoint=endpoint,input=input))
   if result.get('error',{}).get('code')!='busy':return result
   time.sleep(.02)
  raise AssertionError(result)
 finally:f.raw(dict(op='dispose',view=v['view']))
padding=0
def pdf(objects):
 if padding:objects=[*objects,b'<< /Length '+str(padding).encode()+b' >>\nstream\n'+random.Random(731).randbytes(padding)+b'\nendstream']
 raw=bytearray(b'%PDF-1.7\n%\xe2\xe3\xcf\xd3\n');offsets=[0]
 for i,text in enumerate(objects,1):offsets.append(len(raw));raw.extend(str(i).encode()+b' 0 obj\n'+(text.encode()if isinstance(text,str)else text)+b'\nendobj\n')
 start=len(raw);raw.extend(('xref\n0 '+str(len(offsets))+'\n0000000000 65535 f \n').encode());raw.extend(''.join(f'{at:010d} 00000 n \n'for at in offsets[1:]).encode());raw.extend(('trailer\n<< /Size '+str(len(offsets))+' /Root 1 0 R >>\nstartxref\n'+str(start)+'\n%%EOF\n').encode());return bytes(raw)
def stream(text):return '<< /Length '+str(len(text.encode()))+' >>\nstream\n'+text+'\nendstream'
def sample(width=320,height=240):return pdf(['<< /Type /Catalog /Pages 2 0 R /OpenAction 9 0 R >>','<< /Type /Pages /Kids [3 0 R 5 0 R] /Count 2 >>',f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {width} {height}] /Resources << /Font << /F1 7 0 R >> >> /Contents 4 0 R /Annots [8 0 R] >>',stream('1 0 0 rg 40 40 80 60 re f 0 0 0 rg BT /F1 18 Tf 40 160 Td (Generated PDF One) Tj ET'),f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {width} {height}] /Resources << /Font << /F1 7 0 R >> >> /Contents 6 0 R >>',stream('0 1 0 rg 40 40 80 60 re f 0 0 0 rg BT /F1 18 Tf 40 160 Td (Generated PDF Two) Tj ET'),'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>','<< /Type /Annot /Subtype /Link /Rect [40 40 120 100] /A << /S /URI /URI (https://must-not-load.invalid/pdf) >> >>','<< /S /JavaScript /JS (globalThis.pdfExecuted = true;) >>'])
def large_pdf(size=1234567):
 global padding
 padding=max(0,size-2000)
 for _ in range(6):
  raw=sample();delta=size-len(raw)
  if not delta:padding=0;return raw
  padding+=delta
 raise AssertionError('exact generated PDF size')
def workers():return f.page.evaluate('()=>structuredClone(__pdfWorkers)')
def drained():f.page.wait_for_function('()=>__pdfWorkers.created===__pdfWorkers.terminated')
def ready(w,page=1):
 expect(w.locator('.resource-preview')).to_have_attribute('aria-busy','false');expect(w.locator('[data-resource-pdf-pages]')).to_have_text(str(page)+' / 2');c=w.locator('[data-resource-pdf-canvas]');expect(c).to_be_visible();assert c.evaluate('e=>e.width*e.height<=4194304&&e.width<=4096&&e.height<=4096');pixel=c.evaluate('e=>[...e.getContext("2d").getImageData(Math.floor(e.width*60/320),Math.floor(e.height*180/240),1,1).data]');assert pixel==([255,0,0,255]if page==1 else[0,255,0,255]),pixel;expect(w.locator('[data-resource-content-edit],[data-resource-content-save]')).to_have_count(0);assert not f.page.evaluate('()=>globalThis.pdfExecuted');return c
def inputs(files):
 b.locator('[data-root]').click();b.locator('[data-new]').click()
 with f.page.expect_file_chooser()as event:f.page.locator('.context-menu').get_by_role('button',name='자료 추가',exact=True).click()
 event.value.set_files(files);expect(b.locator('[data-new]')).to_be_enabled();f.idle()
def maximum():
 global baseline
 for w in f.page.locator('.window[data-key^="resource-file:"]').all():w.locator('[data-close]').first.click()
 drained();f.page.evaluate('()=>document.activeElement?.blur()');f.pending();ids=[x['id']for x in api()['items']if x['kind']!='folder']
 for n,id in enumerate(ids):b.locator('[data-resource-id="'+id+'"]').click(modifiers=['Control']if n else[])
 b.locator('[data-resource-id="'+ids[0]+'"]').click(button='right');f.page.get_by_role('button',name=str(len(ids))+'개 항목 삭제',exact=True).click();f.page.get_by_role('dialog',name='자료 삭제',exact=True).locator('[data-remove]').click();expect(b.locator('[data-resource-id]')).to_have_count(0);f.idle();raw=large_pdf(4194304);inputs([dict(name='최대 PDF.pdf',mimeType='application/pdf',buffer=raw)]);row=next(x for x in api()['items']if x['kind']!='folder');baseline=store.read_bytes();before=f.page.evaluate('()=>__pdfPartCalls.length');w=opened(row['id']);ready(w);calls=f.page.evaluate('n=>__pdfPartCalls.slice(n)',before);assert[x['part']for x in calls]==[0,1,2,3];w.get_by_role('button',name='다음 페이지',exact=True).click();ready(w,2);f.page.screenshot(path=str(f.case/'actual-largest-pdf.png'));original();closed(row['id']);drained();f.checked('exact4MiB generated valid PDF uses four native pinned parts/full SHA and actual two-page renderer within unchanged canvas budget; original source and store size ceiling preserved')
def restart(index,project=None):
 f.pending();f.page.close();f.stop()
 if project:f.env['CONFECTORY_WEB_PROJECT']=str(project/'project.cproj')
 f.start(index);setup()
try:
 f.start(0)
 with sync_playwright()as p:
  expect.set_options(timeout=60000);f.browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);setup();browser();raw=large_pdf();bad=b'%PDF-1.7\ninvalid'+b'x'*1048576;unsupported=b'not a PDF'+b'x'*1048576
  inputs([dict(name='큰 문서 🧪.pdf',mimeType='application/pdf',buffer=raw),dict(name='작은 문서.pdf',mimeType='application/pdf',buffer=sample()),dict(name='손상 큰 문서.pdf',mimeType='application/pdf',buffer=bad),dict(name='다른 내용.pdf',mimeType='application/pdf',buffer=unsupported)])
  expect(b.locator('[data-resource-id]')).to_have_count(4);rows=api()['items'];id=next(x['id']for x in rows if x['name']=='큰 문서 🧪.pdf');small=next(x['id']for x in rows if x['name']=='작은 문서.pdf');badid=next(x['id']for x in rows if x['name']=='손상 큰 문서.pdf');other=next(x['id']for x in rows if x['name']=='다른 내용.pdf');baseline=store.read_bytes();f.page.locator('#chat-input').fill('큰 PDF와 별개인 새 입력')
  if mode=='baseline':
   w=opened(id);expect(w.locator('.resource-preview')).to_contain_text('1 MiB를 넘는 파일');expect(w.locator('[data-resource-pdf-canvas]')).to_have_count(0);assert workers()['created']==0;closed(id);ready(opened(small));closed(small);drained();assert store.read_bytes()==baseline;original();f.checked('published baseline reproduces missing >1MiB PDF preview while exact stored copy and small-PDF renderer remain valid')
  else:
   w=opened(id);ready(w);w.get_by_role('button',name='다음 페이지',exact=True).click();ready(w,2);w.get_by_label('미리보기 배율',exact=True).select_option('2');ready(w,2);w.get_by_label('미리보기 배율',exact=True).select_option('fit');ready(w,2);closed(id);drained();original();assert store.read_bytes()==baseline;f.checked('real native >1MiB PDF copy reaches actual owned PDF.js Worker only after complete bytes/SHA; red/green pages and fit/200% controls work without edits, scripts, links or external requests')
   if mode=='normal':
    target=dict(project=f.state()['projectId'],id=id,hash=hashlib.sha256(raw).hexdigest());header=observed(target,'readProjectResource')['result'];assert 'preview'not in header and 'imagePreview'not in header and 'data'not in header and header['pdfPreview']['partBytes']==1048576;q=dict(target,generation=header['item']['contentGeneration'],revision=header['displayRevision'],part=1);reply=observed(q);assert reply['ok']and base64.urlsafe_b64decode(reply['result']['data'])==raw[1048576:]
    for wrong in [dict(q,project=uuid.uuid4().hex),dict(q,id=uuid.uuid4().hex),dict(q,hash='0'*64),dict(q,generation='0'*64),dict(q,revision='0'*64),dict(q,part=-1),dict(q,part=2),dict(q,part=.5),dict(q,part='1'),dict(q,path='/outside'),target]:assert not observed(wrong)['ok']
    assert not observed(q,'readProjectResourceImagePart')['ok'];assert observed(q,'projectResourceLayout')['error']['code']=='endpoint_denied';v=f.mount()
    try:
     for _ in range(100):
      denied=f.raw(dict(op='invoke',view=v['view'],scope=v['scope'],expectedRevision=v['revision'],requestId=uuid.uuid4().hex,endpoint='readProjectResourcePDFPart',input=q))
      if denied.get('error',{}).get('code')!='busy':break
      time.sleep(.02)
     assert denied['error']['code']=='endpoint_denied',denied
    finally:f.raw(dict(op='dispose',view=v['view']))
    f.checked('dedicated observation pins ID/hash/import generation/display revision/integer part; foreign/stale/extra path/omitted/out-of-range/mutation/image lanes reject without writes')
    for action in ['descriptor','legacy']:
     before=workers()['created'];arm(action,None,'readProjectResource');w=opened(id)
     if action=='legacy':expect(w.locator('.resource-preview')).to_contain_text('1 MiB를 넘는 파일')
     else:expect(w.locator('[data-resource-preview-retry]')).to_be_enabled()
     assert workers()['created']==before;closed(id);drained()
    for action in ['corrupt','mix']:
     before=workers()['created'];arm(action);w=opened(id);expect(w.locator('[data-resource-preview-retry]')).to_be_enabled();assert workers()['created']==before;w.locator('[data-resource-preview-retry]').click();ready(w);closed(id);drained()
    f.checked('malformed/legacy capability and mixed/corrupt later part create no Worker; explicit same-copy retry recovers after full SHA verification')
    before=workers()['created'];arm();w=opened(id);held();assert workers()['created']==before;field=w.locator('[data-resource-setting-description]');expect(field).not_to_have_attribute('readonly','');field.fill('조각 뒤에도 남을 PDF 설명 🧪');release();ready(w);expect(field).to_have_value('조각 뒤에도 남을 PDF 설명 🧪');field.press('Control+s');f.pending();f.idle();assert next(x for x in api()['items']if x['id']==id)['description']=='조각 뒤에도 남을 PDF 설명 🧪';assert not observed(q)['ok'];closed(id);drained();f.checked('late description during second part survives decoder completion; explicit metadata save changes basis so stale part rejects')
    before=workers()['created'];w=opened(other);expect(w.locator('.resource-preview')).to_contain_text('1 MiB를 넘는 파일');assert workers()['created']==before;closed(other);w=opened(badid);expect(w.locator('[data-resource-preview-retry]')).to_be_enabled();drained();closed(badid);assert store.read_bytes()==baseline;f.checked('unsupported signature stays metadata-only and complete malformed PDF fails read-only; bounded worker retires, original copy preserved')
    damaged=json.loads(baseline);row=next(x for x in damaged['items']if x['id']==id);text=row['data'];at=len(text)-100;row['data']=text[:at]+('B'if text[at]=='A'else'A')+text[at+1:];before=workers()['created']
    try:store.write_text(json.dumps(damaged));w=opened(id);expect(w.locator('[data-resource-preview-retry]')).to_be_enabled();assert workers()['created']==before
    finally:store.write_bytes(baseline)
    w.locator('[data-resource-preview-retry]').click();ready(w);closed(id);drained();f.checked('native tail corruption outside first part rejects before any Worker; fixture restoration plus explicit retry recovers exact bytes')
    maximum()
   elif mode=='lifecycle':
    before=workers()['created'];arm();w=opened(id);held();assert workers()['created']==before;listing=f.state()['listingId'];f.page.locator('#title').click();f.page.get_by_role('button',name='프로젝트 나가기',exact=True).click();expect(f.page.locator('.home-grid')).to_be_visible();release(True);drained();f.page.locator('[data-enter="'+listing+'"]').click();f.idle();ready(viewer(id));closed(id);drained();f.checked('Home retires pending accepted part with no document; late failure cannot cross current project/view')
    arm(part=0);w=opened(id);held();closed(id);w=opened(id);ready(w);release(True);ready(w);closed(id);drained();f.checked('repeated close/reopen fences old response and owns only the new complete document')
    before=workers()['created'];arm();w=opened(id);held();w.locator('[data-fold]').first.click();release();f.page.wait_for_timeout(500);assert workers()['created']==before;w.locator('[data-fold]').first.click();ready(w);f.pending();presentation=json.dumps(f.state()['presentation']);assert base64.urlsafe_b64encode(raw).decode()not in presentation;restart(1);ready(viewer(id));assert workers()['created']==1;closed(id);drained();f.checked('folded pending parts allocate no document; unfold/cold restores only owner/ID/hash and fresh Worker, never bytes or partial transfer')
    permission=store.stat().st_mode;before=workers()['created']
    try:store.chmod(0);w=opened(id);expect(w.locator('[data-resource-preview-retry]')).to_be_enabled();assert workers()['created']==before
    finally:store.chmod(permission)
    w.locator('[data-resource-preview-retry]').click();ready(w);closed(id);drained();f.checked('actual read denial creates no Worker; restoring generated fixture permission plus explicit retry preserves all input and data')
    arm();w=opened(id);held();restart(2);ready(viewer(id));assert workers()['created']==1;otherProject=f.case/'same namespace other project';shutil.copytree(f.project,otherProject,ignore=shutil.ignore_patterns('.confectory','.build'));restart(3,otherProject);expect(viewer(id)).to_have_count(0);assert workers()['created']==0;restart(4,f.project);ready(viewer(id));f.checked('cold interruption discards pending transfer; same-namespace different project inherits no PDF/Worker/bytes, original owner restores without reimport')
   else:raise AssertionError(mode)
  expect(f.page.locator('#chat-input')).to_have_value('큰 PDF와 별개인 새 입력');original();assert store.read_bytes()==baseline;f.pending();f.page.screenshot(path=str(f.case/('resource-pdf-parts-'+mode+'.png')));f.browser.close()
except Exception as error:
 if getattr(f,'page',None):
  try:f.page.screenshot(path=str(f.case/'failure.png'))
  except Exception:pass
 (f.case/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:
 f.stop();(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2));(f.case/'observations.json').write_text(json.dumps(observations,ensure_ascii=False,indent=2))
print('RESOURCE_PDF_PARTS_FIXTURE',f.case,flush=True)
