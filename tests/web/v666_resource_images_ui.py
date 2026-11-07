"""Actual project-copy static PNG/JPEG rendering and URL lifetime; generated inputs only."""
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
 f.page.add_init_script("""(()=>{const create=URL.createObjectURL.bind(URL),revoke=URL.revokeObjectURL.bind(URL);globalThis.__rasterURLs={live:[],created:[],revoked:[]};URL.createObjectURL=blob=>{const value=create(blob);if(['image/png','image/jpeg'].includes(blob.type)){__rasterURLs.live.push(value);__rasterURLs.created.push(value);}return value;};URL.revokeObjectURL=value=>{if(__rasterURLs.live.includes(value)){__rasterURLs.live=__rasterURLs.live.filter(x=>x!==value);__rasterURLs.revoked.push(value);}return revoke(value);};})();""")
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

def encoded(format,color,**kwargs):
 stream=io.BytesIO();Image.new('RGB',(64,32),color).save(stream,format=format,**kwargs);return stream.getvalue()
def chunk(kind,data):return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data))
try:
 f.start(0)
 with sync_playwright()as p:
  expect.set_options(timeout=60000);f.browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);setup()
  png=encoded('PNG',(240,10,20));jpg=encoded('JPEG',(10,180,30));progressive=encoded('JPEG',(240,70,5),progressive=True);exif=Image.Exif();exif[274]=6;rotated=encoded('JPEG',(10,180,30),exif=exif)
  pngid=add('생성 <그림>.png',png,'image/png');jpgid=add('생성 JPEG.jpg',jpg,'image/jpeg');progid=add('점진 JPEG.jpg',progressive,'image/jpeg');rotid=add('회전 JPEG.jpg',rotated,'image/jpeg')
  svg=add('외부를 읽지 않는.svg',b'<svg xmlns="http://www.w3.org/2000/svg" onload="globalThis.rasterExecuted=true"><image href="https://must-not-load.invalid/a"/></svg>','image/svg+xml');spoof=add('위장.png',b'<html><script>globalThis.rasterExecuted=true</script></html>','image/png')
  ihdr=struct.pack('>IIBBBBB',64,32,3,2,0,0,0);bad=add('손상.png',b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',ihdr)+chunk(b'IDAT',b'\x00')+chunk(b'IEND',b''),'image/png');wide=bytearray(png);wide[16:20]=struct.pack('>I',16385);big=add('과도한 크기.png',bytes(wide),'image/png');baseline=store.read_bytes();browser();f.page.locator('#chat-input').fill('그림과 별개인 입력');f.page.locator('#chat-input').press('Tab');f.idle()
  w=opened(pngid);img=ready(w,64,32);pixel=img.evaluate('e=>{const c=document.createElement("canvas");c.width=64;c.height=32;const ctx=c.getContext("2d");ctx.drawImage(e,0,0);return [...ctx.getImageData(4,4,1,1).data]}');assert pixel==[240,10,20,255],pixel;assert len(urls()['live'])==1;unchanged();f.checked('actual SHA-verified native PNG copy decodes to expected pixels in the authored contain panel, without data/source changes or editor actions')
  if mode=='normal':
   for id in[jpgid,progid,rotid]:
    closed(pngid if id==jpgid else jpgid if id==progid else progid);w=opened(id);img=ready(w,32 if id==rotid else 64,64 if id==rotid else 32);assert img.evaluate('e=>getComputedStyle(e).objectFit')=='contain';assert len(urls()['live'])==1;unchanged()
   closed(rotid);f.checked('baseline/progressive and EXIF-oriented JPEG use real browser pixels and the same panel; each replaced/closed view releases its Blob URL')
   for id in[svg,spoof,big]:
    count=len(urls()['created']);w=opened(id);expect(w.locator('.resource-preview')).to_have_attribute('aria-busy','false');expect(w.locator('[data-resource-raster]')).to_have_count(0);assert len(urls()['created'])==count;assert not urls()['live'];closed(id);unchanged()
   assert not f.page.evaluate('()=>globalThis.rasterExecuted');f.checked('unsupported SVG/HTML masquerade and over-budget dimensions allocate no Blob URL and execute/fetch nothing; immutable copies remain available')
   w=opened(bad);expect(w.locator('[data-resource-preview-retry]')).to_be_enabled();assert not urls()['live'];count=len(urls()['created']);w.locator('[data-resource-preview-retry]').click();expect(w.locator('[data-resource-preview-retry]')).to_be_enabled();assert len(urls()['created'])==count+1 and not urls()['live'];closed(bad);unchanged();f.checked('real browser decode failure and explicit same-copy retry revoke every failed URL and retain data/input')
   hold_read();w=opened(pngid);f.page.wait_for_function('()=>__imageReadHeld');count=len(urls()['created']);w.locator('[data-close]').first.click();w=opened(pngid);ready(w,64,32);f.page.evaluate('()=>__releaseImageRead()');ready(w,64,32);assert len(urls()['created'])==count+1 and len(urls()['live'])==1;unchanged();f.checked('late successful native read after same-key close/reopen cannot allocate or paint a retired image; repeat open owns one current URL')
   old=w.locator('[data-resource-raster]').get_attribute('src');w.locator('[data-fold]').first.click();b.locator('[data-resource-id="'+pngid+'"]').click(button='right');f.page.get_by_role('button',name='이름 변경',exact=True).click();name=b.locator('[data-resource-rename]');name.fill('이름 바꾼 그림.png');name.press('Enter');expect(w).to_have_attribute('aria-label','이름 바꾼 그림.png');w.locator('[data-fold]').first.click();img=ready(w,64,32);assert img.get_attribute('src')!=old and old in urls()['revoked'] and len(urls()['live'])==1;unchanged();f.checked('actual inline display rename preserves image pixels/ID and replaces the old URL in its already-open viewer')
   closed(pngid);w=opened(jpgid);ready(w,64,32);w.locator('[data-fold]').first.click();b.locator('[data-resource-id="'+jpgid+'"]').click(button='right');f.page.get_by_role('button',name='삭제',exact=True).click();f.page.get_by_role('dialog',name='자료 삭제',exact=True).locator('[data-remove]').click();expect(viewer(jpgid)).to_have_count(0);assert not urls()['live'];assert jpgid not in [row['id']for row in api('load')['items']];baseline=store.read_bytes();w=opened(pngid);ready(w,64,32);unchanged();f.checked('explicit confirmed deletion closes the removed image and releases its URL while retaining the unselected PNG/source/input')
  elif mode=='lifecycle':
   old=img.get_attribute('src');f.pending();presentation=json.dumps(f.state()['presentation']);assert old not in presentation and base64.urlsafe_b64encode(png).decode()not in presentation;restart(1);w=viewer(pngid);img=ready(w,64,32);assert img.get_attribute('src')!=old and len(urls()['live'])==1;unchanged();f.checked('cold engine restores owner/ID/hash only and re-reads pixels; Blob URLs/bytes are never private layout state')
   closed(pngid);permission=store.stat().st_mode
   try:store.chmod(0);w=opened(pngid);expect(w.locator('[data-resource-preview-retry]')).to_be_enabled();assert not urls()['live']
   finally:store.chmod(permission)
   w.locator('[data-resource-preview-retry]').click();ready(w,64,32);unchanged();f.checked('actual native read refusal/retry preserves original bytes and unrelated input; URL is created only after authorized successful observation')
   closed(pngid);hold_read();w=opened(pngid);f.page.wait_for_function('()=>__imageReadHeld');listing=f.state()['listingId'];f.page.locator('#title').click();f.page.get_by_role('button',name='프로젝트 나가기',exact=True).click();expect(f.page.locator('.home-grid')).to_be_visible();assert not urls()['live'];f.page.evaluate('()=>__releaseImageRead()');assert not urls()['live'];f.page.locator('[data-enter="'+listing+'"]').click();f.idle();w=viewer(pngid);ready(w,64,32);assert len(urls()['live'])==1;unchanged();f.checked('Home/project roundtrip retires pending native reads before URL creation; old success cannot paint another owner/generation')
   other=f.case/'same namespace other project';shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory','.build'));restart(2,other);expect(viewer(pngid)).to_have_count(0);assert api('load')['items']==[] and not urls()['live'];restart(3,f.project);w=viewer(pngid);ready(w,64,32);unchanged();f.checked('different real project with same namespace never inherits image IDs/bytes/URLs; original owner returns without reimport')
  else:raise AssertionError(mode)
  expect(f.page.locator('#chat-input')).to_have_value('그림과 별개인 입력');unchanged();f.pending();f.page.screenshot(path=str(f.case/('resource-images-'+mode+'.png')));closed(pngid);assert len(urls()['created'])==len(urls()['revoked']);f.browser.close()
except Exception as error:
 (f.case/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:
 f.stop();(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2))
print('RESOURCE_IMAGES_FIXTURE',f.case,flush=True)
