"""Actual native-owned PDF copies and PDF.js module Workers/canvas; generated inputs only."""
import sys,json,pathlib,hashlib,base64,uuid,shutil,traceback,io
from playwright.sync_api import sync_playwright,expect
import v536_wide_mixed as f
mode=sys.argv[3];store=f.project/'.confectory/resources.v1.json';b=None;assets=[]
def pdf(objects):
 raw=bytearray(b'%PDF-1.7\n%\xe2\xe3\xcf\xd3\n');offsets=[0]
 for i,text in enumerate(objects,1):offsets.append(len(raw));raw.extend(str(i).encode()+b' 0 obj\n'+(text.encode()if isinstance(text,str)else text)+b'\nendobj\n')
 start=len(raw);raw.extend(('xref\n0 '+str(len(offsets))+'\n0000000000 65535 f \n').encode());raw.extend(''.join(f'{at:010d} 00000 n \n'for at in offsets[1:]).encode());raw.extend(('trailer\n<< /Size '+str(len(offsets))+' /Root 1 0 R >>\nstartxref\n'+str(start)+'\n%%EOF\n').encode());return bytes(raw)
def stream(text):return '<< /Length '+str(len(text.encode()))+' >>\nstream\n'+text+'\nendstream'
def sample(width=320,height=240):return pdf(['<< /Type /Catalog /Pages 2 0 R /OpenAction 9 0 R >>','<< /Type /Pages /Kids [3 0 R 5 0 R] /Count 2 >>',f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {width} {height}] /Resources << /Font << /F1 7 0 R >> >> /Contents 4 0 R /Annots [8 0 R] >>',stream('1 0 0 rg 40 40 80 60 re f 0 0 0 rg BT /F1 18 Tf 40 160 Td (Generated PDF One) Tj ET'),f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {width} {height}] /Resources << /Font << /F1 7 0 R >> >> /Contents 6 0 R >>',stream('0 1 0 rg 40 40 80 60 re f 0 0 0 rg BT /F1 18 Tf 40 160 Td (Generated PDF Two) Tj ET'),'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>','<< /Type /Annot /Subtype /Link /Rect [40 40 120 100] /A << /S /URI /URI (https://must-not-load.invalid/pdf) >> >>','<< /S /JavaScript /JS (globalThis.pdfExecuted = true;) >>'])
def cmap():return pdf(['<< /Type /Catalog /Pages 2 0 R >>','<< /Type /Pages /Kids [3 0 R] /Count 1 >>','<< /Type /Page /Parent 2 0 R /MediaBox [0 0 320 240] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>',stream('0 0 1 rg 40 40 80 60 re f 0 0 0 rg BT /F1 18 Tf 40 160 Td <AC00B098B2E4> Tj ET'),'<< /Type /Font /Subtype /Type0 /BaseFont /HYSMyeongJo-Medium /Encoding /UniKS-UCS2-H /DescendantFonts [6 0 R] >>','<< /Type /Font /Subtype /CIDFontType0 /BaseFont /HYSMyeongJo-Medium /CIDSystemInfo << /Registry (Adobe) /Ordering (Korea1) /Supplement 2 >> /FontDescriptor 7 0 R /DW 1000 >>','<< /Type /FontDescriptor /FontName /HYSMyeongJo-Medium /Flags 4 /FontBBox [0 -200 1000 900] /ItalicAngle 0 /Ascent 880 /Descent -120 /CapHeight 700 /StemV 80 >>'])
def many_pages():return pdf(['<< /Type /Catalog /Pages 2 0 R >>','<< /Type /Pages /Kids ['+' '.join(str(i)+' 0 R'for i in range(3,1004))+'] /Count 1001 >>']+['<< /Type /Page /Parent 2 0 R /MediaBox [0 0 320 240] >>']*1001)
def embedded_pdf():
 from reportlab.pdfgen.canvas import Canvas
 from reportlab.pdfbase import pdfmetrics
 from reportlab.pdfbase.ttfonts import TTFont
 pdfmetrics.registerFont(TTFont('GeneratedEmbedded',str(f.repo/'examples/editor-home/ui/assets/vendor/pdfjs-dist-4.10.38/standard_fonts/LiberationSans-Regular.ttf')));out=io.BytesIO();doc=Canvas(out,pagesize=(320,240))
 for color in [(1,0,0),(0,1,0)]:
  doc.setFillColorRGB(*color);doc.rect(40,40,80,60,stroke=0,fill=1);doc.setFillColorRGB(0,0,0);doc.setFont('GeneratedEmbedded',18);doc.drawString(40,160,'Generated embedded font');doc.showPage()
 doc.save();return out.getvalue()
def add(name,raw):
 revision=f.invoke('projectResources',dict(project=f.state()['projectId'],action='load'))['result']['result']['revision'];id=uuid.uuid4().hex;f.invoke('projectResources',dict(project=f.state()['projectId'],action='import',revision=revision,command=uuid.uuid4().hex,item=dict(id=id,name=name,type='application/pdf',size=len(raw),hash=hashlib.sha256(raw).hexdigest(),modifiedAt=0,data=base64.urlsafe_b64encode(raw).decode())));return id
def setup():
 f.page=f.browser.new_page(viewport=dict(width=1280,height=900));f.page.on('pageerror',lambda e:f.errors.append(str(e)));f.page.on('response',f.observe);f.page.context.route('**/*',f.route);f.page.context.on('request',lambda request:assets.append(request.url)if'/assets/vendor/pdfjs-dist' in request.url else None)
 f.page.add_init_script("""(()=>{const Base=Worker;globalThis.__pdfWorkers={created:0,terminated:0,held:0};globalThis.__holdPDF=false;globalThis.__releasePDF=[];globalThis.Worker=class extends Base{constructor(...args){super(...args);if(!String(args[0]).includes('resource-pdf-worker'))return;__pdfWorkers.created++;const add=this.addEventListener.bind(this),remove=this.removeEventListener.bind(this),records=new Map();this.addEventListener=(type,fn,...rest)=>{if(type!=='message')return add(type,fn,...rest);const rec={active:true};rec.wrapper=event=>{const run=()=>{if(rec.active){if(typeof fn==='function')fn.call(this,event);else fn.handleEvent(event);}};if(__holdPDF){__pdfWorkers.held++;__releasePDF.push(run);}else run();};records.set(fn,rec);return add(type,rec.wrapper,...rest);};this.removeEventListener=(type,fn,...rest)=>{const rec=records.get(fn);if(type==='message'&&rec){rec.active=false;records.delete(fn);return remove(type,rec.wrapper,...rest);}return remove(type,fn,...rest);};let stopped=false;const stop=this.terminate.bind(this);this.terminate=()=>{if(!stopped){stopped=true;__pdfWorkers.terminated++;for(const rec of records.values())rec.active=false;records.clear();}stop();};}};})();""")
 f.goto_editor(f.page,f.url);f.idle()
def browser():
 global b
 f.page.locator('#workspace').click(button='right',position=dict(x=700,y=260));f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]').last;b.locator('[data-tab=resource]').click();expect(b.locator('[data-new]')).to_be_enabled()
def viewer(id):return f.page.locator('.window[data-key="resource-file:'+id+'"]')
def opened(id):b.locator('[data-resource-id="'+id+'"]').press('Enter');w=viewer(id);expect(w).to_be_visible();return w
def ready(w,page=1,color=None):
 expect(w.locator('.resource-preview')).to_have_attribute('aria-busy','false');c=w.locator('[data-resource-pdf-canvas]');expect(c).to_be_visible();expect(w.locator('[data-resource-pdf-pages]')).to_have_text(str(page)+' / '+('1'if color=='blue'else'2'));assert c.evaluate('e=>e.width*e.height<=4194304&&e.width<=4096&&e.height<=4096');expect(w.locator('[data-resource-content-edit],[data-resource-content-save]')).to_have_count(0)
 if color:
  pixel=c.evaluate('e=>[...e.getContext("2d").getImageData(Math.floor(e.width*60/320),Math.floor(e.height*180/240),1,1).data]');assert pixel==dict(red=[255,0,0,255],green=[0,255,0,255],blue=[0,0,255,255])[color],pixel
 return c
def workers():return f.page.evaluate('()=>__pdfWorkers')
def closed(id):opened(id).locator('[data-close]').first.click();expect(viewer(id)).to_have_count(0)
def release():f.page.evaluate('()=>{__holdPDF=false;__releasePDF.splice(0).forEach(run=>run());}')
def unchanged():
 assert store.read_bytes()==baseline
 for name,raw in f.original.items():assert(f.project/name).read_bytes()==raw,name
 assert not f.errors and not f.external,(f.errors,f.external);assert not f.page.evaluate('()=>globalThis.pdfExecuted');assert not list((f.project/'.confectory').glob('resource-content/*.json'))
def restart(index,project=None):
 global b
 f.pending();f.page.close();f.stop()
 if project:f.env['CONFECTORY_WEB_PROJECT']=str(project/'project.cproj')
 f.start(index);setup();b=f.page.locator('.window[data-key^="browser:project:"]').last
 if not b.count():browser()
try:
 f.start(0)
 with sync_playwright()as p:
  expect.set_options(timeout=60000);f.browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);setup();raw=sample();id=add('생성 <문서>.pdf',raw);second=add('둘째.pdf',raw);third=add('셋째.pdf',raw);cid=add('CMap.pdf',cmap());bad=add('손상.pdf',b'%PDF-1.7\ninvalid');huge=add('과도한 페이지.pdf',sample(30000,30000))
  from reportlab.pdfgen.canvas import Canvas
  from reportlab.lib.pdfencrypt import StandardEncryption
  output=io.BytesIO();doc=Canvas(output,encrypt=StandardEncryption('generated-fixture-only'));doc.drawString(40,50,'Generated encrypted fixture');doc.showPage();doc.save();locked=add('암호.pdf',output.getvalue());many=add('과도한 페이지 수.pdf',many_pages());embedded=add('임베디드 글꼴.pdf',embedded_pdf());baseline=store.read_bytes();browser();f.page.locator('#chat-input').fill('PDF와 별개인 입력');f.page.locator('#chat-input').press('Tab');f.idle();w=opened(id);ready(w,1,'red');expect(w.get_by_role('button',name='이전 페이지',exact=True)).to_be_disabled();unchanged();f.checked('real native SHA-verified copy renders actual red PDF pixels through an owned PDF.js module Worker/CSP, within exact canvas budget; source/input unchanged')
  if mode=='normal':
   w.get_by_role('button',name='다음 페이지',exact=True).click();ready(w,2,'green');expect(w.get_by_role('button',name='다음 페이지',exact=True)).to_be_disabled();w.get_by_label('미리보기 배율',exact=True).select_option('2');ready(w,2,'green');w.get_by_label('미리보기 배율',exact=True).select_option('fit');ready(w,2,'green');w.get_by_role('button',name='이전 페이지',exact=True).click();ready(w,1,'red');w.locator('[data-resource-pdf-canvas]').click(position=w.locator('[data-resource-pdf-canvas]').evaluate('e=>({x:e.clientWidth*60/320,y:e.clientHeight*180/240})'));expect(w.locator('.resource-preview a')).to_have_count(0);unchanged();f.checked('actual next/previous and fit/200% render the selected page/color; PDF JavaScript and URI annotation create no action, link layer, external request or edit')
   ready(opened(second),1,'red');n=workers()['created'];w3=opened(third);expect(w3.locator('[data-resource-preview-retry]')).to_be_enabled();assert workers()['created']==n;closed(second);f.page.wait_for_function('()=>__pdfWorkers.created-__pdfWorkers.terminated===1');w3=opened(third);w3.locator('[data-resource-preview-retry]').click();ready(w3,1,'red');closed(third);f.page.wait_for_function('()=>__pdfWorkers.created-__pdfWorkers.terminated===1');closed(id);f.page.wait_for_function('()=>__pdfWorkers.created===__pdfWorkers.terminated');f.checked('two PDF leases reject a third before creating a Worker; closing destroys document/bridge/worker and explicit retry uses released quota')
   w=opened(cid);ready(w,1,'blue');assert any('/cmaps/UniKS-UCS2-H.bcmap'in url for url in assets),assets;closed(cid);f.page.wait_for_function('()=>__pdfWorkers.created===__pdfWorkers.terminated');f.checked('real predefined Korean CMap request is served from exact opaque pinned native assets; canvas color renders with original caption/controls, no remote assets')
   for target in [bad,huge,locked,many]:
    w=opened(target);expect(w.locator('[data-resource-preview-retry]')).to_be_enabled()
    if target==locked:expect(w.locator('.resource-preview')).to_contain_text('암호가 필요한 PDF')
    f.page.wait_for_function('()=>__pdfWorkers.created===__pdfWorkers.terminated');w.locator('[data-resource-preview-retry]').click();expect(w.locator('[data-resource-preview-retry]')).to_be_enabled();closed(target);f.page.wait_for_function('()=>__pdfWorkers.created===__pdfWorkers.terminated');unchanged()
   f.checked('actual malformed/password PDF and oversized page fail read-only with explicit retry; no password/permission/source mutation and no live failed Workers')
   fontbase=f.page.evaluate('()=>document.fonts.size');w=opened(embedded);ready(w,1,'red');f.page.wait_for_function('(n)=>document.fonts.size>n',arg=fontbase);f.checked('actual embedded public Liberation fixture creates native FontFace objects before interrupted cleanup');f.page.evaluate('()=>__holdPDF=true');closed(embedded);f.page.wait_for_function('()=>__pdfWorkers.created===__pdfWorkers.terminated');release();(f.case/'font-lifetime.json').write_text(json.dumps(dict(before=fontbase,after=f.page.evaluate('()=>document.fonts.size'),workers=workers()),indent=2));f.page.wait_for_function('(n)=>document.fonts.size===n',arg=fontbase,timeout=3000);unchanged();f.checked('held termination acknowledgement after embedded font render cannot retain owned FontFaces after Worker deadline')
   f.page.evaluate('()=>__holdPDF=true');held=workers()['held'];w=opened(id);f.page.wait_for_function('(n)=>__pdfWorkers.held>n',arg=held);closed(id);f.page.wait_for_function('()=>__pdfWorkers.created===__pdfWorkers.terminated');release();w=opened(id);ready(w,1,'red');w.locator('[data-fold]').first.click();f.page.wait_for_function('()=>__pdfWorkers.created===__pdfWorkers.terminated');w.locator('[data-fold]').first.click();ready(w,1,'red');unchanged();f.checked('held real worker messages cannot publish after close/reopen; folding destroys document/worker and unfolding re-reads the same owner')
   closed(id);f.page.wait_for_function('()=>__pdfWorkers.created===__pdfWorkers.terminated');f.page.evaluate('()=>__holdPDF=true');held=workers()['held'];w=opened(id);f.page.wait_for_function('(n)=>__pdfWorkers.held>n',arg=held);expect(w.locator('[data-resource-preview-retry]')).to_be_enabled(timeout=20000);f.page.wait_for_function('()=>__pdfWorkers.created===__pdfWorkers.terminated');release();expect(w.locator('[data-resource-pdf-canvas]')).to_have_count(0);w.locator('[data-resource-preview-retry]').click();ready(w,1,'red');unchanged();f.checked('ten-second held-parser deadline retires worker; late callback cannot paint timeout, and explicit native re-read succeeds')
  elif mode=='lifecycle':
   f.pending();presentation=json.dumps(f.state()['presentation']);assert base64.urlsafe_b64encode(raw).decode()not in presentation;restart(1);w=viewer(id);ready(w,1,'red');assert workers()['created']==1;unchanged();f.checked('cold engine restores only owner/ID/hash, then creates a fresh document Worker and actual pixels; no bytes/bridge/page objects persisted')
   closed(id);f.page.wait_for_function('()=>__pdfWorkers.created===__pdfWorkers.terminated');permission=store.stat().st_mode
   try:store.chmod(0);w=opened(id);expect(w.locator('[data-resource-preview-retry]')).to_be_enabled();assert workers()['created']==workers()['terminated']
   finally:store.chmod(permission)
   w.locator('[data-resource-preview-retry]').click();ready(w,1,'red');unchanged();f.checked('actual native read denial creates no PDF Worker; restoring fixture permission and explicit retry preserve data and unrelated input')
   closed(id);f.page.wait_for_function('()=>__pdfWorkers.created===__pdfWorkers.terminated');f.page.evaluate('()=>__holdPDF=true');held=workers()['held'];w=opened(id);f.page.wait_for_function('(n)=>__pdfWorkers.held>n',arg=held);listing=f.state()['listingId'];f.page.locator('#title').click();f.page.get_by_role('button',name='프로젝트 나가기',exact=True).click();expect(f.page.locator('.home-grid')).to_be_visible();f.page.wait_for_function('()=>__pdfWorkers.created===__pdfWorkers.terminated');release();f.page.locator('[data-enter="'+listing+'"]').click();f.idle();w=viewer(id);ready(w,1,'red');unchanged();f.checked('Home/project transition fences pending worker messages and destroys old document before returning to original authorized copy')
   other=f.case/'same namespace other project';shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory','.build'));restart(2,other);expect(viewer(id)).to_have_count(0);assert workers()['created']==0;restart(3,f.project);w=viewer(id);ready(w,1,'red');unchanged();f.checked('real different project with same namespace inherits no PDF ID/Worker/bytes; original owner restores without reimport')
  else:raise AssertionError(mode)
  expect(f.page.locator('#chat-input')).to_have_value('PDF와 별개인 입력');unchanged();f.pending();f.page.screenshot(path=str(f.case/('resource-pdf-'+mode+'.png')));closed(id);f.page.wait_for_function('()=>__pdfWorkers.created===__pdfWorkers.terminated');f.browser.close()
except Exception as error:
 if getattr(f,'page',None):
  try:f.page.screenshot(path=str(f.case/'failure.png'))
  except Exception:pass
 (f.case/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:
 f.stop();(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2));(f.case/'assets.json').write_text(json.dumps(assets,indent=2))
print('RESOURCE_PDF_FIXTURE',f.case,flush=True)
