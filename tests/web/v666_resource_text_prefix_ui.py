"""Real engine/File chooser/Chromium prefix observations; generated assets only.
Delayed/corrupt replies are controlled transport fixtures, not external users.
"""
import sys,json,pathlib,hashlib,base64,uuid,shutil,traceback,time
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
def setup():
 global b
 f.page=f.setup();f.idle();b=f.page.locator('.window[data-key^="browser:project:"]').last
 f.page.evaluate("""()=>{const base=fetch;globalThis.__prefixPlan={};globalThis.__prefixHeld={};globalThis.__prefixRelease={};fetch=async(...args)=>{let request;try{request=JSON.parse(args[1]?.body||'null')}catch{}const response=await base(...args);if(request?.op!=='observe')return response;const action=__prefixPlan[request.endpoint];if(!action)return response;const body=await response.clone().json();if(!body.ok)return response;delete __prefixPlan[request.endpoint];const made=()=>new Response(JSON.stringify(body),{status:200,headers:{'Content-Type':'application/json'}});if(action==='legacy'){delete body.result.preview;return made();}if(action==='descriptor'){body.result.preview.bytes--;return made();}if(action==='corrupt'){body.result.data=(body.result.data[0]==='A'?'B':'A')+body.result.data.slice(1);return made();}__prefixHeld[request.endpoint]=true;return new Promise(resolve=>__prefixRelease[request.endpoint]=(failed=false)=>{if(failed){body.ok=false;delete body.result;body.error={code:'owned_lost_prefix_reply'};}resolve(made());});};}""")
 def seen(response):
  try:
   q=response.request.post_data_json
   if isinstance(q,dict)and q.get('op')=='observe':
    result=response.json();data=result.get('result',{}).pop('data',None)
    if data is not None:result['retainedData']={'bytes':len(data),'sha256':hashlib.sha256(data.encode()).hexdigest()}
    observations.append(dict(request=q,result=result))
  except Exception:pass
 f.page.on('response',seen)
def arm(endpoint='previewProjectResourceText',action='hold'):f.page.evaluate('([e,a])=>{__prefixHeld[e]=false;__prefixPlan[e]=a;}',[endpoint,action])
def held(endpoint='previewProjectResourceText'):f.page.wait_for_function('e=>__prefixHeld[e]',arg=endpoint)
def release(endpoint='previewProjectResourceText',failed=False):f.page.evaluate('([e,failed])=>__prefixRelease[e](failed)',[endpoint,failed])
def observed(input,endpoint='previewProjectResourceText'):
 v=f.mount()
 try:
  for _ in range(100):
   result=f.raw(dict(op='observe',view=v['view'],scope=v['scope'],endpoint=endpoint,input=input))
   if result.get('error',{}).get('code')!='busy':return result
   time.sleep(.02)
  raise AssertionError(result)
 finally:f.raw(dict(op='dispose',view=v['view']))
def displayed(w,raw):
 pre=w.locator('.resource-document-text');expect(pre).to_be_visible();prefix=raw[:1048576];encoding='utf-16'if prefix[:2]in[b'\xff\xfe',b'\xfe\xff']else'utf-8-sig';expected=hashlib.sha256(prefix.decode(encoding,errors='replace').encode()).hexdigest()
 actual=pre.evaluate("async el=>[...new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(el.textContent)))].map(v=>v.toString(16).padStart(2,'0')).join('')")
 assert actual==expected,(actual,expected);expect(w.locator('.resource-preview-status')).to_contain_text('앞부분 1 MiB');expect(w.locator('[data-resource-content-edit],[data-resource-content-save],pre script,pre img')).to_have_count(0);assert not f.page.evaluate('()=>globalThis.prefixWasExecuted')
def restart(index,project=None):
 f.pending();f.page.close();f.stop()
 if project:f.env['CONFECTORY_WEB_PROJECT']=str(project/'project.cproj')
 f.start(index);setup()
try:
 f.start(0)
 with sync_playwright()as p:
  expect.set_options(timeout=60000);f.browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);setup();browser()
  pattern='생성 텍스트 🧪\r\n<script>globalThis.prefixWasExecuted=true</script><img src="https://must-not-load.invalid/prefix">\n'.encode();raw=b'\xef\xbb\xbf'+(pattern*20000)[:2097144];wide=b'\xff\xfe'+('UTF16 한글 🧪\r\n'*90000).encode('utf-16le')[:1048576]
  b.locator('[data-new]').click()
  with f.page.expect_file_chooser()as event:f.page.locator('.context-menu').get_by_role('button',name='자료 추가',exact=True).click()
  event.value.set_files([dict(name='큰 원문 🧪.html',mimeType='text/html',buffer=raw),dict(name='큰 UTF16.txt',mimeType='text/plain',buffer=wide),dict(name='큰 binary.bin',mimeType='application/octet-stream',buffer=b'X'*1048577)])
  expect(b.locator('[data-resource-pending]')).to_have_count(0);expect(b.locator('[data-new]')).to_be_enabled();expect(b.locator('[data-resource-id]')).to_have_count(3);f.idle();rows=api()['items'];id=next(x['id']for x in rows if x['name']=='큰 원문 🧪.html');utf16=next(x['id']for x in rows if x['name']=='큰 UTF16.txt');baseline=store.read_bytes();f.page.locator('#chat-input').fill('미리보기와 별개인 새 입력')
  w=opened(id);displayed(w,raw);closed(id);w=opened(utf16);displayed(w,wide);closed(utf16);original();assert store.read_bytes()==baseline;f.checked('real File import and native prefix observation render exactly the authored first 1MiB for UTF8/BOM/CRLF/partial character and UTF16; literal markup never executes, no content editor or source writes')
  if mode=='normal':
   item=next(x for x in api()['items']if x['id']==id);target=dict(project=f.state()['projectId'],id=id,hash=item['hash']);header=observed(target,'readProjectResource')['result'];q=dict(target,generation=header['item']['contentGeneration'],revision=header['displayRevision']);reply=observed(q);assert reply['ok']and base64.urlsafe_b64decode(reply['result']['data'])==raw[:1048576]and reply['result']['item']['hash']==hashlib.sha256(raw).hexdigest()
   for wrong in [dict(q,project=uuid.uuid4().hex),dict(q,id=uuid.uuid4().hex),dict(q,hash='0'*64),dict(q,generation='0'*64),dict(q,revision='0'*64),dict(q,path='/outside'),target]:assert not observed(wrong)['ok']
   binary=next(x for x in api()['items']if x['name']=='큰 binary.bin');binary_target=dict(project=target['project'],id=binary['id'],hash=binary['hash']);binary_header=observed(binary_target,'readProjectResource')['result'];assert 'preview'not in binary_header and 'data'not in binary_header
   assert not observed(dict(binary_target,generation=binary_header['item']['contentGeneration'],revision=binary_header['displayRevision']))['ok']
   binary_window=opened(binary['id']);expect(binary_window.locator('.resource-preview')).to_contain_text('1 MiB를 넘는 파일');expect(binary_window.locator('pre')).to_have_count(0);closed(binary['id'])
   assert observed(q,'projectResourceLayout')['error']['code']=='endpoint_denied'
   v=f.mount()
   try:assert f.raw(dict(op='invoke',view=v['view'],scope=v['scope'],expectedRevision=v['revision'],requestId=uuid.uuid4().hex,endpoint='previewProjectResourceText',input=q))['error']['code']=='endpoint_denied'
   finally:f.raw(dict(op='dispose',view=v['view']))
   assert store.read_bytes()==baseline;f.checked('actual engine observation whitelist pins project/id/full hash/generation/display revision; foreign/stale/missing/extra fields and observing mutation endpoint are rejected')
   arm('readProjectResource','descriptor');w=opened(id);expect(w.locator('[data-resource-preview-retry]')).to_be_enabled();expect(w.locator('[data-resource-setting-description]')).to_have_attribute('readonly','');expect(w.locator('pre')).to_have_count(0);closed(id);arm('readProjectResource','legacy');w=opened(id);expect(w.locator('.resource-preview')).to_contain_text('1 MiB를 넘는 파일');expect(w.locator('pre')).to_have_count(0);closed(id);arm(action='corrupt');w=opened(id);expect(w.locator('[data-resource-preview-retry]')).to_be_enabled();expect(w.locator('pre')).to_have_count(0);w.locator('[data-resource-preview-retry]').click();displayed(w,raw);closed(id);f.checked('metadata-only legacy header remains supported; controlled corrupt prefix is never rendered, explicit same-file retry recovers without a mutation')
   # Both observations are paused after the real native success. No synthetic bytes.
   arm('readProjectResource');arm();w=opened(id);held('readProjectResource');field=w.locator('[data-resource-setting-description]');expect(field).to_have_attribute('readonly','');release('readProjectResource');held();expect(field).not_to_have_attribute('readonly','');field.evaluate("el=>{el.value='읽기 응답 뒤에도 남을 새 설명 🧪';el.dispatchEvent(new Event('input',{bubbles:true}));}");release();displayed(w,raw);expect(field).to_have_value('읽기 응답 뒤에도 남을 새 설명 🧪');field.press('Control+s');f.pending();f.idle();assert next(x for x in api()['items']if x['id']==id)['description']=='읽기 응답 뒤에도 남을 새 설명 🧪';assert not observed(q)['ok'];closed(id);f.checked('description stays readonly until verified header, then accepts late input during prefix read and preserves it through response and explicit save; stale compound revision is refused')
   # Mutate only this fixture store outside the displayed prefix; retain exact bytes.
   damaged=json.loads(baseline);damaged_item=next(x for x in damaged['items']if x['id']==id);text=damaged_item['data'];offset=len(text)-100;damaged_item['data']=text[:offset]+('B'if text[offset]=='A'else'A')+text[offset+1:]
   try:
    store.write_text(json.dumps(damaged));w=opened(id);expect(w.locator('[data-resource-preview-retry]')).to_be_enabled();expect(w.locator('pre')).to_have_count(0)
   finally:store.write_bytes(baseline)
   w.locator('[data-resource-preview-retry]').click();displayed(w,raw);closed(id);original();f.checked('actual native whole-file verification rejects corruption outside visible prefix, preserves input and retries after exact fixture restoration')
   arm();w=opened(id);held();closed(id);w=opened(id);displayed(w,raw);release(failed=True);displayed(w,raw);expect(w.locator('[data-resource-preview-retry]')).to_have_count(0);f.checked('repeated close/reopen owns a new preview token; delayed old failure cannot replace the current view')
  elif mode=='lifecycle':
   arm();w=opened(id);held();owner=f.state()['projectId'];listing=f.state()['listingId'];f.page.locator('#title').click();f.page.get_by_role('button',name='프로젝트 나가기',exact=True).click();expect(f.page.locator('.home-grid')).to_be_visible();assert not observed(dict(project=owner,id=id,hash=hashlib.sha256(raw).hexdigest(),generation='0'*64,revision='0'*64))['ok'];release(failed=True);f.page.locator('[data-enter="'+listing+'"]').click();f.idle();displayed(viewer(id),raw);f.checked('Home retires the pending prefix; late failed reply cannot cross current-project ownership on return')
   f.pending();presentation=json.dumps(f.state()['presentation'],ensure_ascii=False);assert base64.urlsafe_b64encode(raw[:1048576]).decode()not in presentation
   restart(1);displayed(viewer(id),raw);f.checked('cold restart restores only scoped owner/ID/hash layout and re-observes bytes without storing preview payload or replaying mutation')
   other=f.case/'other same namespace';shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory','.build'));restart(2,other);expect(f.page.locator('.window[data-key^="resource-file:"]')).to_have_count(0);assert api()['items']==[];assert store.read_bytes()==baseline;restart(3,f.project);displayed(viewer(id),raw);f.checked('another real project with identical declaration IDs cannot restore the first project resource bytes; returning restores the exact prefix')
  else:raise AssertionError(mode)
  assert store.read_bytes()==baseline;original();assert not any(x.get('invoke',{}).get('endpoint')in['editDraft','saveDraft','reviewDraft','confirmDraft','runProject','startAI']for x in f.traffic);expect(f.page.locator('#chat-input')).to_have_value('미리보기와 별개인 새 입력');f.pending();f.page.screenshot(path=str(f.case/('prefix-'+mode+'.png')));f.browser.close()
except Exception as error:
 (f.case/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:
 f.stop();(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'observations.json').write_text(json.dumps(observations,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2))
print('RESOURCE_TEXT_PREFIX_UI_FIXTURE',f.case,flush=True)
