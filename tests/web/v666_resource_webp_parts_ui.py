"""Real generated File copies, native part observations and decoded image pixels.
Delayed/corrupted replies are controlled transport fixtures, not external users.
"""
import sys,json,pathlib,hashlib,base64,uuid,shutil,traceback,time,io,random,struct,zlib
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
def urls():return f.page.evaluate('()=>structuredClone(__rasterURLs)')
def setup():
 global b
 f.page=f.browser.new_page(viewport=dict(width=1280,height=900));f.page.on('pageerror',lambda e:f.errors.append(str(e)));f.page.on('response',f.observe);f.page.route('**/*',f.route)
 f.page.add_init_script("""(()=>{const create=URL.createObjectURL.bind(URL),revoke=URL.revokeObjectURL.bind(URL);globalThis.__rasterURLs={live:[],created:[],revoked:[]};URL.createObjectURL=blob=>{const value=create(blob);if(['image/webp'].includes(blob.type)){__rasterURLs.live.push(value);__rasterURLs.created.push(value);}return value;};URL.revokeObjectURL=value=>{if(__rasterURLs.live.includes(value)){__rasterURLs.live=__rasterURLs.live.filter(x=>x!==value);__rasterURLs.revoked.push(value);}return revoke(value);};const base=fetch;globalThis.__rasterPlan={};globalThis.__rasterHeld=false;globalThis.__rasterCalls=[];fetch=async(...args)=>{let request;try{request=JSON.parse(args[1]?.body||'null')}catch{}if(request?.op==='observe'&&request.endpoint==='readProjectResourceImagePart')__rasterCalls.push(structuredClone(request.input));const response=await base(...args);if(request?.op!=='observe')return response;const plan=__rasterPlan[request.endpoint];if(!plan||plan.part!=null&&request.input?.part!==plan.part)return response;const body=await response.clone().json();if(!body.ok)return response;delete __rasterPlan[request.endpoint];const made=()=>new Response(JSON.stringify(body),{status:200,headers:{'Content-Type':'application/json'}});if(plan.action==='legacy'){delete body.result.imagePreview;return made();}if(plan.action==='descriptor'){body.result.imagePreview.partBytes--;return made();}if(plan.action==='corrupt'){body.result.data=(body.result.data[0]==='A'?'B':'A')+body.result.data.slice(1);return made();}if(plan.action==='mix'){body.result.item.contentGeneration='f'.repeat(64);return made();}__rasterHeld=true;return new Promise(resolve=>globalThis.__releaseRaster=(failed=false)=>{if(failed){body.ok=false;delete body.result;body.error={code:'owned_lost_image_part'};}resolve(made());});};})();""")
 def seen(response):
  try:
   q=response.request.post_data_json
   if isinstance(q,dict)and q.get('op')=='observe':
    result=response.json();data=result.get('result',{}).pop('data',None)
    if data is not None:result['retainedData']={'bytes':len(data),'sha256':hashlib.sha256(data.encode()).hexdigest()}
    observations.append(dict(request=q,result=result))
  except Exception:pass
 f.page.on('response',seen);f.goto_editor(f.page,f.url);f.idle();b=f.page.locator('.window[data-key^="browser:project:"]').last
def arm(action='hold',part=1,endpoint='readProjectResourceImagePart'):f.page.evaluate('({action,part,endpoint})=>{__rasterHeld=false;__rasterPlan[endpoint]={action,part};}',dict(action=action,part=part,endpoint=endpoint))
def held():f.page.wait_for_function('()=>__rasterHeld')
def release(failed=False):f.page.evaluate('failed=>__releaseRaster(failed)',failed)
def observed(input,endpoint='readProjectResourceImagePart'):
 v=f.mount()
 try:
  for _ in range(100):
   result=f.raw(dict(op='observe',view=v['view'],scope=v['scope'],endpoint=endpoint,input=input))
   if result.get('error',{}).get('code')!='busy':return result
   time.sleep(.02)
  raise AssertionError(result)
 finally:f.raw(dict(op='dispose',view=v['view']))
def ready(w,raw):
 image=Image.open(io.BytesIO(raw));width,height=image.size;img=w.locator('[data-resource-raster]');expect(img).to_be_visible();expect(w.locator('.resource-preview')).to_have_attribute('aria-busy','false');assert img.evaluate('e=>[e.naturalWidth,e.naturalHeight]')==[width,height];assert img.evaluate('e=>getComputedStyle(e).objectFit')=='contain';expect(w.locator('[data-resource-content-edit],[data-resource-content-save]')).to_have_count(0)
 if raw==png or len(raw)==4194304:
  actual=img.evaluate("async e=>{const c=document.createElement('canvas');c.width=e.naturalWidth;c.height=e.naturalHeight;const x=c.getContext('2d');x.drawImage(e,0,0);return [...new Uint8Array(await crypto.subtle.digest('SHA-256',x.getImageData(0,0,c.width,c.height).data))].map(v=>v.toString(16).padStart(2,'0')).join('')}");assert actual==hashlib.sha256(image.convert('RGBA').tobytes()).hexdigest(),actual
 else:
  points=[[0,0],[37,53],[width//2,height//2],[width-1,height-1]];actual=img.evaluate('(e,points)=>{const c=document.createElement("canvas");c.width=e.naturalWidth;c.height=e.naturalHeight;const x=c.getContext("2d");x.drawImage(e,0,0);return points.map(p=>[...x.getImageData(...p,1,1).data])}',points);rgb=image.convert('RGB')
  for point,value in zip(points,actual):assert value[3]==255 and max(abs(a-b)for a,b in zip(value[:3],rgb.getpixel(tuple(point))))<=4,(point,value,rgb.getpixel(tuple(point)))
 assert len(urls()['live'])==1;return img
def maximum(png):
 global baseline
 for w in f.page.locator('.window[data-key^="resource-file:"]').all():w.locator('[data-close]').first.click()
 f.page.evaluate('()=>document.activeElement?.blur()');f.pending();f.idle();ids=[x['id']for x in api()['items']if x['kind']!='folder']
 for n,id in enumerate(ids):b.locator('[data-resource-id="'+id+'"]').click(modifiers=['Control']if n else[])
 b.locator('[data-resource-id="'+ids[0]+'"]').click(button='right');f.page.get_by_role('button',name=str(len(ids))+'개 항목 삭제',exact=True).click();f.page.get_by_role('dialog',name='자료 삭제',exact=True).locator('[data-remove]').click();expect(b.locator('[data-resource-id]')).to_have_count(0);f.idle()
 raw=padded(png,4194304);assert len(raw)==4194304
 b.locator('[data-root]').click();b.locator('[data-new]').click()
 with f.page.expect_file_chooser()as event:f.page.locator('.context-menu').get_by_role('button',name='자료 추가',exact=True).click()
 event.value.set_files([dict(name='최대 WebP.webp',mimeType='image/webp',buffer=raw)]);expect(b.locator('[data-resource-id]')).to_have_count(1);expect(b.locator('[data-new]')).to_be_enabled();f.idle();row=next(x for x in api()['items']if x['kind']!='folder');baseline=store.read_bytes();before=f.page.evaluate('()=>__rasterCalls.length');w=opened(row['id']);ready(w,raw);calls=f.page.evaluate('n=>__rasterCalls.slice(n)',before);assert[x['part']for x in calls]==[0,1,2,3];assert row['hash']==hashlib.sha256(raw).hexdigest();original();f.checked('exact4MiB static WebP with inert RIFF metadata uses four pinned parts and original pixel plane; explicit generated-copy replacement preserves source and current storage limit')
def webp(width,height,lossless):
 image=Image.frombytes('RGB',(width,height),random.Random(932).randbytes(width*height*3));out=io.BytesIO();image.save(out,format='WEBP',lossless=lossless,quality=100);return out.getvalue()
def padded(raw,total):
 length=total-len(raw)-8;assert length>=0 and length%2==0;data=(b'https://must-not-load.invalid/inert-metadata'+random.Random(1666).randbytes(length))[:length];raw=raw+b'JUNK'+struct.pack('<I',length)+data;return raw[:4]+struct.pack('<I',len(raw)-8)+raw[8:]
def restart(index,project=None):
 f.pending();f.page.close();f.stop()
 if project:f.env['CONFECTORY_WEB_PROJECT']=str(project/'project.cproj')
 f.start(index);setup()
try:
 f.start(0)
 with sync_playwright()as p:
  expect.set_options(timeout=60000);f.browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);setup();browser();rng=random.Random(713)
  from v666_resource_webp_fixture import broken
  png=webp(640,600,True);jpeg=webp(1200,900,False);bad=padded(broken,1048600)
  assert 1048576<len(png)<=4194304 and 1048576<len(jpeg)<=4194304 and len(png)+len(jpeg)+len(bad)<=4194304
  b.locator('[data-new]').click()
  with f.page.expect_file_chooser()as event:f.page.locator('.context-menu').get_by_role('button',name='자료 추가',exact=True).click()
  event.value.set_files([dict(name='큰 무손실 WebP 🧪.webp',mimeType='image/webp',buffer=png),dict(name='큰 손실 WebP.webp',mimeType='image/webp',buffer=jpeg),dict(name='손상 entropy.webp',mimeType='image/webp',buffer=bad)])
  expect(b.locator('[data-resource-id]')).to_have_count(3);expect(b.locator('[data-new]')).to_be_enabled();f.idle();rows=api()['items'];id=next(x['id']for x in rows if x['name']=='큰 무손실 WebP 🧪.webp');jpg=next(x['id']for x in rows if x['name']=='큰 손실 WebP.webp');badid=next(x['id']for x in rows if x['name']=='손상 entropy.webp');baseline=store.read_bytes();f.page.locator('#chat-input').fill('큰 그림과 별개인 새 입력')
  if mode=='baseline':
   w=opened(id);expect(w.locator('.resource-preview')).to_contain_text('1 MiB를 넘는 파일');expect(w.locator('[data-resource-raster]')).to_have_count(0);assert 'imagePreview'not in observed(dict(project=f.state()['projectId'],id=id,hash=next(x['hash']for x in rows if x['id']==id)),'readProjectResource')['result'];closed(id);original();f.checked('published source reproduces metadata-only >1MiB static WebP with original copy unchanged');f.page.screenshot(path=str(f.case/'baseline.png'));f.browser.close();raise SystemExit(0)
  w=opened(id);ready(w,png);closed(id);w=opened(jpg);ready(w,jpeg);closed(jpg);original();assert not urls()['live']and store.read_bytes()==baseline;f.checked('real >1MiB File copies assemble native pinned parts and whole SHA before original contain renderer; full lossless WebP RGBA SHA and lossy WebP decoded sample pixels, no content editor or source writes')
  if mode=='normal':
   item=next(x for x in api()['items']if x['id']==id);target=dict(project=f.state()['projectId'],id=id,hash=item['hash']);header=observed(target,'readProjectResource')['result'];assert 'preview'not in header and 'data'not in header and header['imagePreview']['partBytes']==1048576;q=dict(target,generation=header['item']['contentGeneration'],revision=header['displayRevision'],part=1);reply=observed(q);assert reply['ok']and base64.urlsafe_b64decode(reply['result']['data'])==png[1048576:]
   for wrong in [dict(q,project=uuid.uuid4().hex),dict(q,id=uuid.uuid4().hex),dict(q,hash='0'*64),dict(q,generation='0'*64),dict(q,revision='0'*64),dict(q,part=-1),dict(q,part=2),dict(q,part=.5),dict(q,part='1'),dict(q,path='/outside'),target]:assert not observed(wrong)['ok']
   assert observed(q,'projectResourceLayout')['error']['code']=='endpoint_denied'
   v=f.mount()
   try:
    for _ in range(100):
     denied=f.raw(dict(op='invoke',view=v['view'],scope=v['scope'],expectedRevision=v['revision'],requestId=uuid.uuid4().hex,endpoint='readProjectResourceImagePart',input=q))
     if denied.get('error',{}).get('code')!='busy':break
     time.sleep(.02)
    assert denied['error']['code']=='endpoint_denied',denied
   finally:f.raw(dict(op='dispose',view=v['view']))
   f.checked('actual observation endpoint pins owner/id/whole hash/generation/revision and exact integer part; foreign/stale/path/omitted/out-of-range/mutation-lane requests reject without writes')
   arm('descriptor',None,'readProjectResource');w=opened(id);expect(w.locator('[data-resource-preview-retry]')).to_be_enabled();expect(w.locator('[data-resource-setting-description]')).to_have_attribute('readonly','');assert not urls()['live'];closed(id);arm('legacy',None,'readProjectResource');w=opened(id);expect(w.locator('.resource-preview')).to_contain_text('1 MiB를 넘는 파일');assert not urls()['live'];closed(id)
   for action in ['corrupt','mix']:
    count=len(urls()['created']);arm(action);w=opened(id);expect(w.locator('[data-resource-preview-retry]')).to_be_enabled();expect(w.locator('[data-resource-raster]')).to_have_count(0);assert len(urls()['created'])==count and not urls()['live'];w.locator('[data-resource-preview-retry]').click();ready(w,png);closed(id)
   f.checked('malformed capability, mixed generation and corrupt later part allocate no decoder/URL; old metadata-only header and explicit exact-copy retry remain supported')
   arm();w=opened(id);held();assert not urls()['live'];field=w.locator('[data-resource-setting-description]');expect(field).not_to_have_attribute('readonly','');field.evaluate("e=>{e.value='두 번째 조각 뒤에도 남을 설명 🧪';e.dispatchEvent(new Event('input',{bubbles:true}));}");release();ready(w,png);expect(field).to_have_value('두 번째 조각 뒤에도 남을 설명 🧪');field.press('Control+s');f.pending();f.idle();assert next(x for x in api()['items']if x['id']==id)['description']=='두 번째 조각 뒤에도 남을 설명 🧪';assert not observed(q)['ok'];closed(id);f.checked('no URL before the final part/whole SHA; late description survives completion and explicit save, then old display revision rejects')
   count=len(urls()['created']);w=opened(badid);expect(w.locator('[data-resource-preview-retry]')).to_be_enabled();assert not urls()['live']and len(urls()['created'])==count;closed(badid);f.checked('actual large corrupted WebP entropy fails bitmap decode without img fallback or allocating a Blob URL; original copy retained')
   damaged=json.loads(baseline);row=next(x for x in damaged['items']if x['id']==id);text=row['data'];offset=len(text)-100;row['data']=text[:offset]+('B'if text[offset]=='A'else'A')+text[offset+1:]
   try:store.write_text(json.dumps(damaged));w=opened(id);expect(w.locator('[data-resource-preview-retry]')).to_be_enabled();assert not urls()['live']
   finally:store.write_bytes(baseline)
   w.locator('[data-resource-preview-retry]').click();ready(w,png);f.checked('native full-file validation rejects tail corruption outside the first part; exact fixture restoration and explicit retry recover without changing originals')
   maximum(png)
  elif mode=='lifecycle':
   arm();w=opened(id);held();owner=f.state()['projectId'];listing=f.state()['listingId'];f.page.locator('#title').click();f.page.get_by_role('button',name='프로젝트 나가기',exact=True).click();expect(f.page.locator('.home-grid')).to_be_visible();release(True);assert not urls()['live'];f.page.locator('[data-enter="'+listing+'"]').click();f.idle();ready(viewer(id),png);closed(id);f.checked('Home retires an accepted pending part with no URL; late failure cannot cross the new current-project view')
   arm(part=0);w=opened(id);held();closed(id);w=opened(id);ready(w,png);release(True);ready(w,png);closed(id);f.checked('same-key repeated close/reopen discards the old pending part; only the current complete raster owns one URL')
   arm(part=0);w=opened(id);held();count=f.page.evaluate('()=>__rasterCalls.length');w.locator('[data-fold]').first.click();b.locator('[data-resource-id="'+id+'"]').click(button='right');f.page.get_by_role('button',name='삭제',exact=True).click();f.page.get_by_role('dialog',name='자료 삭제',exact=True).locator('[data-remove]').click();expect(viewer(id)).to_have_count(0);release();f.idle();assert not urls()['live']and f.page.evaluate('()=>__rasterCalls.length')==count;assert id not in[x['id']for x in api()['items']];baseline=store.read_bytes();f.checked('explicit confirmed deletion retires a pending first part, issues no further part and never resurrects the removed image')
   savedMode=store.stat().st_mode
   try:
    store.chmod(0);w=opened(jpg);expect(w.locator('[data-resource-preview-retry]')).to_be_enabled();expect(w.locator('[data-resource-raster]')).to_have_count(0);assert not urls()['live']
   finally:store.chmod(savedMode)
   w.locator('[data-resource-preview-retry]').click();ready(w,jpeg);closed(jpg);original();f.checked('actual native file-read permission denial allocates no bitmap/URL; exact-mode restoration and explicit retry recover, with source and other input retained')
   w=opened(jpg);img=ready(w,jpeg);old=img.get_attribute('src');f.pending();presentation=json.dumps(f.state()['presentation']);assert old not in presentation and base64.urlsafe_b64encode(jpeg).decode()not in presentation;restart(1);ready(viewer(jpg),jpeg);f.checked('cold engine restores only scoped owner/id/hash and re-reads full authorized raster; bytes/Blob URL/pending parts are absent from private presentation')
   other=f.case/'other same namespace';shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory','.build'));restart(2,other);expect(f.page.locator('.window[data-key^="resource-file:"]')).to_have_count(0);assert api()['items']==[]and not urls()['live'];restart(3,f.project);ready(viewer(jpg),jpeg);f.checked('another real project with identical namespace/declarations never inherits raster IDs/bytes/URLs; returning restores its exact owned copy')
  elif mode=='maximum':maximum(png)
  else:raise AssertionError(mode)
  assert store.read_bytes()==baseline;original();expect(f.page.locator('#chat-input')).to_have_value('큰 그림과 별개인 새 입력');assert not any(x.get('invoke',{}).get('endpoint')in['editDraft','saveDraft','reviewDraft','confirmDraft','runProject','startAI']for x in f.traffic);f.pending();f.page.screenshot(path=str(f.case/('webp-parts-'+mode+'.png')))
  for w in f.page.locator('.window[data-key^="resource-file:"]').all():w.locator('[data-close]').first.click()
  assert not urls()['live']and len(urls()['created'])==len(urls()['revoked']);f.browser.close()
except Exception as error:
 try:f.page.screenshot(path=str(f.case/'failure.png'))
 except Exception:pass
 (f.case/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:
 f.stop();(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'observations.json').write_text(json.dumps(observations,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2))
print('RESOURCE_WEBP_PARTS_UI_FIXTURE',f.case,flush=True)
