"""Actual project-copy static AVIF rendering and URL lifetime; generated inputs only."""
import sys,json,pathlib,hashlib,base64,uuid,shutil,traceback,time,io,struct,zlib
from PIL import Image
from playwright.sync_api import sync_playwright,expect
import v536_wide_mixed as f
mode=sys.argv[3];store=f.project/'.confectory/resources.v1.json';b=None

def api(action,**args):return f.invoke('projectResourceLayout',dict(action=action,project=f.state()['projectId'],**args))['result']['result']
def add(name,raw,type):
 revision=f.invoke('projectResources',dict(project=f.state()['projectId'],action='load'))['result']['result']['revision'];id=uuid.uuid4().hex
 f.invoke('projectResources',dict(project=f.state()['projectId'],action='import',revision=revision,command=uuid.uuid4().hex,item=dict(id=id,name=name,type=type,size=len(raw),hash=hashlib.sha256(raw).hexdigest(),modifiedAt=0,data=base64.urlsafe_b64encode(raw).decode())));return id

def setup():
 f.page=f.browser.new_page(viewport=dict(width=1280,height=900));f.page.on('pageerror',lambda e:f.errors.append(str(e)));f.page.on('response',f.observe);f.page.route('**/*',f.route)
 f.page.add_init_script("""(()=>{const create=URL.createObjectURL.bind(URL),revoke=URL.revokeObjectURL.bind(URL);globalThis.__rasterURLs={live:[],created:[],revoked:[]};URL.createObjectURL=blob=>{const value=create(blob);if(['image/png','image/jpeg','image/avif'].includes(blob.type)){__rasterURLs.live.push(value);__rasterURLs.created.push(value);}return value;};URL.revokeObjectURL=value=>{if(__rasterURLs.live.includes(value)){__rasterURLs.live=__rasterURLs.live.filter(x=>x!==value);__rasterURLs.revoked.push(value);}return revoke(value);};})();""")
 f.page.add_init_script("""(()=>{const base=createImageBitmap;globalThis.__avifBitmaps={created:0,closed:0,held:0};globalThis.__holdAvifDecode=false;globalThis.__releaseAvifDecode=[];createImageBitmap=async(...args)=>{const bitmap=await base(...args);if(args[0]?.type!=='image/avif')return bitmap;__avifBitmaps.created++;const wrapped={get width(){return bitmap.width},get height(){return bitmap.height},close(){__avifBitmaps.closed++;bitmap.close();}};if(__holdAvifDecode){__avifBitmaps.held++;return new Promise(resolve=>__releaseAvifDecode.push(()=>resolve(wrapped)));}return wrapped;};})();""")
 f.goto_editor(f.page,f.url);f.idle()
def browser():
 global b
 f.page.locator('#workspace').click(button='right',position=dict(x=700,y=260));f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]').last;b.locator('[data-tab=resource]').click();expect(b.locator('[data-new]')).to_be_enabled()
def viewer(id):return f.page.locator('.window[data-key="resource-file:'+id+'"]')
def opened(id):b.locator('[data-resource-id="'+id+'"]').press('Enter');w=viewer(id);expect(w).to_be_visible();return w
def ready(w,width=None,height=None):
 img=w.locator('[data-resource-raster]');expect(img).to_be_visible();expect(w.locator('.resource-preview')).to_have_attribute('aria-busy','false');assert img.evaluate('e=>e.complete&&e.naturalWidth>0');
 if width:assert img.evaluate('e=>[e.naturalWidth,e.naturalHeight]')==[width,height]
 expect(w.locator('[data-resource-content-edit],[data-resource-content-save]')).to_have_count(0);return img

def urls():return f.page.evaluate('()=>__rasterURLs')
def closed(id):viewer(id).locator('[data-close]').first.click();expect(viewer(id)).to_have_count(0);assert not urls()['live']
def unchanged():
 assert store.read_bytes()==baseline
 for name,raw in f.original.items():assert(f.project/name).read_bytes()==raw,name
 assert not f.errors and not f.external,(f.errors,f.external)
def hold_read():
 f.page.evaluate("""()=>{const base=fetch;let armed=true;globalThis.__imageReadHeld=false;fetch=async(...args)=>{let req;try{req=JSON.parse(args[1]?.body||'null')}catch{}const response=await base(...args);if(!armed||req?.op!=='observe'||req.endpoint!=='readProjectResource')return response;const actual=await response.clone().json();if(!actual.ok)return response;armed=false;globalThis.__imageReadHeld=true;return new Promise(resolve=>{globalThis.__releaseImageRead=()=>{fetch=base;resolve(response);};});};}""")
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
  from v666_resource_avif_fixture import color,subsampled,alpha,animated,unsupported,corrupt,oversized,truncated,mismatch
  png=color
  pngid=add('생성 <그림>.avif',color,'image/avif');jpgid=add('420 색상.avif',subsampled,'image/avif');progid=add('투명도.avif',alpha,'image/avif');rotid=add('크기 불일치.avif',mismatch,'image/avif');metaid=add('보통 MIME.avif',color,'application/octet-stream')
  animid=add('시퀀스.avif',animated,'image/avif');truncid=add('잘린.avif',truncated,'image/avif');profileid=add('다른 깊이.avif',unsupported,'image/avif')
  svg=add('외부를 읽지 않는.svg',b'<svg xmlns="http://www.w3.org/2000/svg" onload="globalThis.rasterExecuted=true"><image href="https://must-not-load.invalid/a"/></svg>','image/svg+xml');spoof=add('위장.avif',b'<html><script>globalThis.rasterExecuted=true</script></html>','image/avif')
  bad=add('손상 AV1.avif',corrupt,'image/avif');big=add('과도한 크기.avif',oversized,'image/avif');baseline=store.read_bytes();browser();f.page.locator('#chat-input').fill('그림과 별개인 입력');f.page.locator('#chat-input').press('Tab');f.idle()
  w=opened(pngid);img=ready(w,65,33);pixel=img.evaluate('e=>{const c=document.createElement("canvas");c.width=65;c.height=33;const ctx=c.getContext("2d");ctx.drawImage(e,0,0);return [...ctx.getImageData(4,4,1,1).data]}');assert all(abs(x-y)<=4 for x,y in zip(pixel,[240,10,20,255])),pixel;assert len(urls()['live'])==1;unchanged();f.checked('actual SHA-verified native SDR8 AVIF copy decodes to expected RGB pixels in the authored contain panel, without data/source changes or editor actions')
  if mode=='normal':
   previous=pngid
   for id in[jpgid,progid,metaid]:
    closed(previous);w=opened(id);img=ready(w,65,33);assert img.evaluate('e=>getComputedStyle(e).objectFit')=='contain';pixels=img.evaluate('e=>{const c=document.createElement("canvas");c.width=65;c.height=33;const g=c.getContext("2d");g.drawImage(e,0,0);return [...g.getImageData(40,4,1,1).data,...g.getImageData(40,30,1,1).data,...g.getImageData(4,4,1,1).data,...g.getImageData(20,4,1,1).data]}');assert all(abs(x-y)<=4 for x,y in zip(pixels[:8],[240,10,20,255,10,180,30,255])),pixels
    if id==progid:assert pixels[11]==0 and all(abs(x-y)<=6 for x,y in zip(pixels[12:16],[240,10,20,128])),pixels
    assert len(urls()['live'])==1;unchanged();previous=id
   closed(metaid);f.checked('actual 444/420 AVIF SDR pixels and alpha0/128/255 are correct; ordinary MIME uses verified bytes without source changes')
   for id in[svg,spoof,big,animid,truncid,profileid,rotid]:
    count=len(urls()['created']);w=opened(id);expect(w.locator('.resource-preview')).to_have_attribute('aria-busy','false');expect(w.locator('[data-resource-raster]')).to_have_count(0);assert len(urls()['created'])==count;assert not urls()['live'];closed(id);unchanged()
   assert not f.page.evaluate('()=>globalThis.rasterExecuted');f.checked('unsupported SVG/HTML masquerade, sequence/depth/truncated AVIF, mismatched AV1 dimensions and over-budget dimensions allocate no Blob URL and execute/fetch nothing; immutable copies remain available')
   w=opened(bad);expect(w.locator('[data-resource-preview-retry]')).to_be_enabled();assert not urls()['live'];count=len(urls()['created']);w.locator('[data-resource-preview-retry]').click();expect(w.locator('[data-resource-preview-retry]')).to_be_enabled();assert len(urls()['created'])==count and not urls()['live'];closed(bad);unchanged();f.checked('actual damaged AV1 decode and explicit same-copy retry allocate no URL and retain immutable bytes/input')
   f.page.evaluate('()=>{globalThis.__savedAvifDecoder=createImageBitmap;createImageBitmap=()=>Promise.reject(Error("controlled codec refusal"));}');count=len(urls()['created']);w=opened(pngid);expect(w.locator('[data-resource-preview-retry]')).to_be_enabled();assert len(urls()['created'])==count and not urls()['live'];f.page.evaluate('()=>{createImageBitmap=__savedAvifDecoder;}');w.locator('[data-resource-preview-retry]').click();ready(w,65,33);closed(pngid);unchanged();f.checked('controlled predecoder rejection produces the real native viewer retry without publishing a URL; explicit retry uses the unchanged authorized AVIF')
   f.page.evaluate('()=>__holdAvifDecode=true');held=f.page.evaluate('()=>__avifBitmaps.held');count=len(urls()['created']);w=opened(pngid);f.page.wait_for_function('(n)=>__avifBitmaps.held>n',arg=held);w.locator('[data-close]').first.click();f.page.evaluate('()=>{__holdAvifDecode=false;__releaseAvifDecode.splice(0).forEach(fn=>fn());}');f.page.wait_for_function('()=>__avifBitmaps.created===__avifBitmaps.closed');assert len(urls()['created'])==count and not urls()['live'];w=opened(pngid);ready(w,65,33);closed(pngid);unchanged();f.checked('closed view retains its in-flight decode lease until real bitmap completion, closes late bitmap and creates no retired URL; repeat open decodes only current owner')
   f.page.evaluate('()=>{globalThis.__savedAvifDecoder=createImageBitmap;globalThis.createImageBitmap=undefined;}');count=len(urls()['created']);w=opened(pngid);expect(w.locator('[data-resource-preview-retry]')).to_be_enabled();assert len(urls()['created'])==count and not urls()['live'];f.page.evaluate('()=>{createImageBitmap=__savedAvifDecoder;}');w.locator('[data-resource-preview-retry]').click();ready(w,65,33);closed(pngid);unchanged();f.checked('missing browser predecoder refuses AVIF without allocating a URL or changing bytes; restoring fixture capability and explicit retry decodes the authorized copy')
   hold_read();w=opened(pngid);f.page.wait_for_function('()=>__imageReadHeld');count=len(urls()['created']);w.locator('[data-close]').first.click();w=opened(pngid);ready(w,65,33);f.page.evaluate('()=>__releaseImageRead()');ready(w,65,33);assert len(urls()['created'])==count+1 and len(urls()['live'])==1;unchanged();f.checked('late successful native read after same-key close/reopen cannot allocate or paint a retired image; repeat open owns one current URL')
   old=w.locator('[data-resource-raster]').get_attribute('src');w.locator('[data-fold]').first.click();b.locator('[data-resource-id="'+pngid+'"]').click(button='right');f.page.get_by_role('button',name='이름 변경',exact=True).click();name=b.locator('[data-resource-rename]');name.fill('이름 바꾼 그림.avif');name.press('Enter');expect(w).to_have_attribute('aria-label','이름 바꾼 그림.avif');w.locator('[data-fold]').first.click();img=ready(w,65,33);assert img.get_attribute('src')!=old and old in urls()['revoked'] and len(urls()['live'])==1;unchanged();f.checked('actual inline display rename preserves image pixels/ID and replaces the old URL in its already-open viewer')
   src=img.get_attribute('src');count=len(urls()['created']);description=w.locator('[data-resource-setting-description]');description.fill('AVIF metadata note');description.press('Tab');f.idle();expect(description).to_have_value('AVIF metadata note');assert next(row for row in api('load')['items']if row['id']==pngid)['description']=='AVIF metadata note';assert img.get_attribute('src')==src and len(urls()['created'])==count;unchanged();f.checked('viewer description stores only existing authorized metadata and keeps current AVIF bytes/pixels/URL unchanged')
   closed(pngid);w=opened(jpgid);ready(w,65,33);w.locator('[data-fold]').first.click();b.locator('[data-resource-id="'+jpgid+'"]').click(button='right');f.page.get_by_role('button',name='삭제',exact=True).click();f.page.get_by_role('dialog',name='자료 삭제',exact=True).locator('[data-remove]').click();expect(viewer(jpgid)).to_have_count(0);assert not urls()['live'];assert jpgid not in [row['id']for row in api('load')['items']];baseline=store.read_bytes();w=opened(pngid);ready(w,65,33);unchanged();f.checked('explicit confirmed deletion closes the removed image and releases its URL while retaining the unselected AVIF/source/input')
  elif mode=='lifecycle':
   old=img.get_attribute('src');f.pending();presentation=json.dumps(f.state()['presentation']);assert old not in presentation and base64.urlsafe_b64encode(png).decode()not in presentation;restart(1);w=viewer(pngid);img=ready(w,65,33);assert img.get_attribute('src')!=old and len(urls()['live'])==1;unchanged();f.checked('cold engine restores owner/ID/hash only and re-reads pixels; Blob URLs/bytes are never private layout state')
   closed(pngid);permission=store.stat().st_mode
   try:store.chmod(0);w=opened(pngid);expect(w.locator('[data-resource-preview-retry]')).to_be_enabled();assert not urls()['live']
   finally:store.chmod(permission)
   w.locator('[data-resource-preview-retry]').click();ready(w,65,33);unchanged();f.checked('actual native read refusal/retry preserves original bytes and unrelated input; URL is created only after authorized successful observation')
   closed(pngid);hold_read();w=opened(pngid);f.page.wait_for_function('()=>__imageReadHeld');listing=f.state()['listingId'];f.page.locator('#title').click();f.page.get_by_role('button',name='프로젝트 나가기',exact=True).click();expect(f.page.locator('.home-grid')).to_be_visible();assert not urls()['live'];f.page.evaluate('()=>__releaseImageRead()');assert not urls()['live'];f.page.locator('[data-enter="'+listing+'"]').click();f.idle();w=viewer(pngid);ready(w,65,33);assert len(urls()['live'])==1;unchanged();f.checked('Home/project roundtrip retires pending native reads before URL creation; old success cannot paint another owner/generation')
   other=f.case/'same namespace other project';shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory','.build'));restart(2,other);expect(viewer(pngid)).to_have_count(0);assert api('load')['items']==[] and not urls()['live'];restart(3,f.project);w=viewer(pngid);ready(w,65,33);unchanged();f.checked('different real project with same namespace never inherits image IDs/bytes/URLs; original owner returns without reimport')
  else:raise AssertionError(mode)
  expect(f.page.locator('#chat-input')).to_have_value('그림과 별개인 입력');f.page.wait_for_function('()=>__avifBitmaps.created===__avifBitmaps.closed');unchanged();f.pending();f.page.screenshot(path=str(f.case/('resource-avif-'+mode+'.png')));closed(pngid);assert len(urls()['created'])==len(urls()['revoked']);f.browser.close()
except Exception as error:
 (f.case/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:
 f.stop();(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2))
print('RESOURCE_WEBP_FIXTURE',f.case,flush=True)
