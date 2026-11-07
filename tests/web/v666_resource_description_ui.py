"""Actual engine/Chromium: authored file/folder descriptions, durable exact pending input."""
import sys,json,pathlib,uuid,shutil,traceback
from playwright.sync_api import sync_playwright,expect
import v536_wide_mixed as f
mode=sys.argv[3];b=None;description=f.project/'.confectory/resource-descriptions.v1.json'
def api(action,**args):return f.invoke('projectResourceLayout',dict(action=action,project=f.state()['projectId'],**args))['result']['result']
def catalogue():return api('load')
def item(id):return next(row for row in catalogue()['items']if row['id']==id)
def browser():
 global b
 f.page.locator('#workspace').click(button='right',position=dict(x=700,y=260));f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]').last;b.locator('[data-tab=resource]').click();expect(b.locator('[data-new]')).to_be_enabled();b.get_by_role('button',name='표시 크기 6단계',exact=True).click()
def row(id):return b.locator('[data-resource-id="'+id+'"]')
def data(id):return row(id).locator('[data-resource-description]')
def viewer(id):return f.page.locator('.window[data-key="resource-file:'+id+'"]')
def settings(id):return viewer(id).locator('[data-resource-setting-description]')
def opened(id):
 row(id).press('Enter');w=viewer(id);expect(w.locator('[data-resource-setting-description]')).to_be_visible();expect(w.locator('.resource-document-text')).to_have_text(raw.decode());return w
def unchanged():
 assert(f.project/'.confectory/resources.v1.json').read_bytes()==original_store
 for path,content in f.original.items():assert(f.project/path).read_bytes()==content,path
 assert not f.errors and not f.external,(f.errors,f.external)
def saved(id,value):
 expect(settings(id)).to_have_value(value)if viewer(id).count()else None
 f.page.wait_for_function('()=>!document.querySelector("[data-resource-description-cancel]:not([hidden])")');assert item(id).get('description','')==value;unchanged()
def hold():
 f.page.evaluate("""()=>{const base=fetch;let wanted=null,armed=true;globalThis.__descriptionHeld=false;fetch=async(...args)=>{let request;try{request=JSON.parse(args[1]?.body||'null')}catch{}if(armed&&request?.op==='invoke'&&request.endpoint==='projectResourceLayout'&&request.input?.action==='describe')wanted=request.requestId;const response=await base(...args);if(!wanted||!armed||request?.op!=='update')return response;const body=await response.clone().json(),row=body.results?.find(r=>r.requestId===wanted);if(!row?.ok)return response;armed=false;__descriptionHeld=true;return new Promise(resolve=>{globalThis.__releaseDescription=()=>{fetch=base;delete row.result;row.ok=false;row.error={code:'owned_lost_description_reply'};resolve(new Response(JSON.stringify(body),{status:200,headers:{'Content-Type':'application/json'}}));};});};}""")
def retry(w):return w.locator('[data-resource-description-retry]:not([hidden])')
def cancel(w):return w.locator('[data-resource-description-cancel]:not([hidden])')
def restart(index,project=None):
 global b
 f.pending();f.page.close();f.stop()
 if project:f.env['CONFECTORY_WEB_PROJECT']=str(project/'project.cproj')
 f.start(index);f.page=f.setup();f.idle();b=f.page.locator('.window[data-key^="browser:project:"]').last
 if not b.count():browser()
 else:expect(b.locator('[data-resource-status]')).to_be_visible();f.idle()
try:
 f.start(0)
 with sync_playwright()as p:
  expect.set_options(timeout=60000);f.browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.idle();browser();raw='unchanged generated text\r\n🧪'.encode();b.locator('[data-resource-files]').set_input_files(dict(name='notes.txt',mimeType='text/plain',buffer=raw));f.idle();expect(b.locator('[data-new]')).to_be_enabled();file=catalogue()['items'][0]['id'];original_store=(f.project/'.confectory/resources.v1.json').read_bytes()
  b.locator('[data-new]').click();f.page.get_by_role('button',name='새 카테고리',exact=True).click();form=f.page.locator('.resource-name-form');form.locator('[name=name]').fill('folder');form.get_by_role('button',name='확인',exact=True).click();f.idle();folder=next(x['id']for x in catalogue()['items']if x['kind']=='folder')
  expect(data(file)).to_have_value('');data(file).focus();data(file).press_sequentially('undo');data(file).press('Control+z');expect(data(file)).to_have_value('');data(file).press('Escape');f.idle();assert not description.exists();f.checked('native text Undo retains its original meaning without writing resource metadata')
  data(file).fill('취소 입력');data(file).press('Escape');expect(data(file)).to_have_value('');assert not description.exists();unchanged();f.checked('authored Data description input Escape cancels private input without creating metadata or changing source bytes')
  data(folder).fill('folder search tag');data(folder).press('Enter');f.idle();assert item(folder)['description']=='folder search tag';data(file).fill('first <literal> 설명');data(file).press('Tab');f.idle();assert item(file)['description']=='first <literal> 설명';unchanged();f.checked('actual Enter/blur independently stores file and folder descriptions with stable IDs, original topology and immutable bytes')
  w=opened(file);expect(settings(file)).to_have_value('first <literal> 설명');expect(settings(file)).to_have_attribute('maxlength','1000');settings(file).fill('  여러 줄\n\t<safe> 😀  ');settings(file).press('Tab');saved(file,'  여러 줄\n\t<safe> 😀  ');f.checked('authored viewer settings textarea preserves multiline whitespace and literal markup while keeping native read/hash/content controls intact')
  # Fold the preview so its geometry cannot obscure the browser search.
  w.locator('[data-fold]').first.click();b.locator('[data-browser-control=object-query]').fill('folder search tag');b.locator('[data-browser-control=object-query]').press('Enter');expect(b.locator('[data-resource-id]')).to_have_count(1);expect(row(folder)).to_be_visible();b.locator('[data-browser-control=object-query]').fill('');b.locator('[data-browser-control=object-query]').press('Enter');f.idle();unchanged();f.checked('same original current-folder search matches stored description, not only name; clearing search preserves identities and selection')
  row(file).press('Enter');w=viewer(file)
  f.page.locator('#chat-input').fill('독립 입력 보존')
  if mode=='normal':
   prior=description.read_bytes();permission=description.stat().st_mode
   try:
    description.chmod(0o444);settings(file).fill('write failure');settings(file).press('Tab');expect(retry(w)).to_be_enabled();assert description.read_bytes()==prior;expect(settings(file)).to_have_value('write failure')
   finally:description.chmod(permission)
   retry(w).click();saved(file,'write failure');f.checked('real native metadata write refusal retains exact private command/value; retry recovers after permission restoration without altering originals')
   hold();settings(file).fill('lost success');settings(file).press('Tab');f.page.wait_for_function('()=>__descriptionHeld');assert item(file)['description']=='lost success';assert 'lost success'in json.dumps(f.state()['presentation'],ensure_ascii=False);settings(file).fill('late description');f.page.evaluate('()=>__releaseDescription()');expect(retry(w)).to_be_enabled();retry(w).click();expect(settings(file)).to_have_value('late description');expect(cancel(w)).to_be_enabled();assert item(file)['description']=='lost success';settings(file).focus();settings(file).press('Tab');saved(file,'late description');f.checked('durable intent exists before native delivery; lost reply replays exact command, preserving newer typing until a separate explicit blur save')
   settings(file).fill('stale local');c=catalogue();api('describe',revision=c['revision'],command=uuid.uuid4().hex,id=file,generation=item(file)['descriptionGeneration'],value='peer value');settings(file).press('Tab');expect(retry(w)).to_be_enabled();prior=description.read_bytes();retry(w).click();expect(retry(w)).to_be_enabled();assert description.read_bytes()==prior;expect(settings(file)).to_have_value('stale local');cancel(w).click();saved(file,'peer value');f.checked('peer edit after capture causes CAS rejection without implicit rebase; retry keeps local input, explicit cancel displays current peer value')
   permission=description.stat().st_mode
   try:
    description.chmod(0o444);settings(file).fill('keep until cancel');settings(file).press('Tab');expect(retry(w)).to_be_enabled()
   finally:description.chmod(permission)
   w.locator('[data-close]').first.click();dialog=f.page.locator('.modal[aria-label="저장하지 않은 설명"]');expect(dialog).to_be_visible();dialog.locator('[data-keep]').click();expect(settings(file)).to_have_value('keep until cancel');cancel(w).click();saved(file,'peer value');f.checked('dirty close is guarded, continuing editing preserves text and explicit input cancellation preserves committed metadata')
  elif mode=='lifecycle':
   prior=description.read_bytes();settings(file).fill('cold uncommitted');f.pending();assert 'cold uncommitted'in json.dumps(f.state()['presentation'],ensure_ascii=False);restart(1);w=viewer(file);expect(settings(file)).to_have_value('cold uncommitted');assert description.read_bytes()==prior;cancel(w).click();saved(file,'  여러 줄\n\t<safe> 😀  ');f.checked('cold real engine restores unsaved description from private presentation without automatic save, preserving original basis until explicit cancellation')
   hold();settings(file).fill('cold lost reply');settings(file).press('Tab');f.page.wait_for_function('()=>__descriptionHeld');f.page.evaluate('()=>__releaseDescription()');expect(retry(w)).to_be_enabled();prior=description.read_bytes();restart(2);w=viewer(file);expect(retry(w)).to_be_enabled();retry(w).click();saved(file,'cold lost reply');assert description.read_bytes()==prior;f.checked('cold restart retains exact uncertain command and explicit retry confirms existing receipt without an extra metadata write')
   other=f.case/'same namespace other project';shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory','.build'));restart(3,other);assert catalogue()['items']==[];expect(viewer(file)).to_have_count(0);assert description.read_bytes()==prior;restart(4,f.project);w=viewer(file);expect(settings(file)).to_have_value('cold lost reply');unchanged();f.checked('same namespace in another actual project inherits no private input, metadata or file; returning restores original authorized description and bytes')
   settings(file).fill('retired generation private input');f.pending();c=catalogue();old=item(file);api('delete-file',revision=c['revision'],command=uuid.uuid4().hex,id=file,hash=old['hash']);c=catalogue();import base64,hashlib
   f.invoke('projectResources',dict(action='import',project=f.state()['projectId'],revision=c['resourceRevision'],command=uuid.uuid4().hex,item=dict(id=file,name='reused.txt',type='text/plain',size=len(raw),hash=hashlib.sha256(raw).hexdigest(),modifiedAt=0,data=base64.urlsafe_b64encode(raw).decode())))
   assert item(file).get('description','')=='';restart(5,f.project);w=viewer(file);expect(w.get_by_label('보관된 설명 입력',exact=True)).to_have_value('retired generation private input');expect(settings(file)).to_have_value('');expect(settings(file)).to_have_attribute('readonly','');assert item(file).get('description','')=='';cancel(w).click();expect(w.get_by_label('보관된 설명 입력',exact=True)).to_have_count(0);assert item(file).get('description','')=='';f.checked('deleted and reimported same ID never adopts old private description; cold restored orphan input remains visible/read-only until explicit cancellation')

  else:raise AssertionError(mode)
  expect(f.page.locator('#chat-input')).to_have_value('독립 입력 보존');unchanged();f.pending();f.page.screenshot(path=str(f.case/('description-'+mode+'.png')));f.browser.close()
except Exception as error:
 page=getattr(f,'page',None)or(next(iter(f.browser.contexts[0].pages),None)if getattr(f,'browser',None)and f.browser.contexts else None)
 if page:
  try:page.screenshot(path=str(f.case/'failure.png'));(f.case/'failure.html').write_text(page.content())
  except:pass
 (f.case/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:
 f.stop();(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2));(f.case/'errors.json').write_text(json.dumps(dict(pageErrors=f.errors,external=f.external),ensure_ascii=False,indent=2))
print('RESOURCE_DESCRIPTION_UI_FIXTURE',f.case,flush=True)
