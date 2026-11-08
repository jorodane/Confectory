"""Native owned-copy text editing, durable private draft and one-save backup UI.
Generated fixtures only; Linux engine+Chromium, never Windows/WebView2/device execution.
"""
import sys,json,pathlib,hashlib,base64,uuid,shutil,traceback,time
from playwright.sync_api import sync_playwright,expect
import v536_wide_mixed as f
read_events=[]
base_observe=f.observe
def traced_read(response):
 base_observe(response)
 try:
  request=response.request.post_data_json
  if isinstance(request,dict)and request.get('op')=='observe':
   body=response.json();read_events.append(dict(endpoint=request.get('endpoint'),ok=body.get('ok'),error=body.get('error')));(f.case/'read-events.json').write_text(json.dumps(read_events,indent=2))
 except Exception:pass
f.observe=traced_read
busy_events=[]
busy_pages=0
busy_recoveries=[]
if '--busy-reads'in sys.argv:
 def busy_setup():
  global busy_pages
  busy_pages+=1;limit=3 if mode=='lifecycle'and busy_pages==4 else 1
  page=f.browser.new_page(viewport={'width':1280,'height':900});page.on('pageerror',lambda e:f.errors.append(str(e)));page.on('response',f.observe);page.route('**/*',f.route)
  page.add_init_script("""(()=>{const base=fetch,counts=new Map();globalThis.__contentReadAttempts=[];globalThis.__contentReadBusy=[];globalThis.__contentReadOutcomes=[];fetch=async(...args)=>{let q;try{q=JSON.parse(args[1]?.body||'null')}catch{}const tracked=q?.op==='observe'&&['readResourceContentDraft','readResourceContentPending'].includes(q.endpoint),row={endpoint:q?.endpoint,input:q?.input};let response;if(tracked){__contentReadAttempts.push(row);const count=counts.get(q.endpoint)||0;counts.set(q.endpoint,count+1);if(count<(q.endpoint==='readResourceContentDraft'?LIMIT:1)){__contentReadBusy.push(row);response=new Response(JSON.stringify({ok:false,error:{code:'busy'}}),{status:200,headers:{'Content-Type':'application/json'}});}}response=response||await base(...args);if(tracked){const reply=await response.clone().json();__contentReadOutcomes.push({...row,ok:reply.ok,code:reply.error?.code||null});}return response;};})();""".replace('LIMIT',str(limit)))
  f.goto_editor(page,f.url);return page
 f.setup=busy_setup

def capture_busy():
 if '--busy-reads'not in sys.argv:return
 data=f.page.evaluate('()=>({attempts:__contentReadAttempts,busy:__contentReadBusy,outcomes:__contentReadOutcomes})')
 for row in data['busy']:
  matches=[q for q in data['attempts']if q==row];assert len(matches)>=2,(row,data)
 busy_events.append(data);(f.case/'busy-read-events.json').write_text(json.dumps(busy_events,indent=2))
def recover_busy_read():
 if '--busy-reads'not in sys.argv:return
 w=viewer(id)
 if not w.count():return
 f.page.wait_for_function("id=>{const w=document.querySelector('.window[data-key=\"resource-file:'+id+'\"]');return w?.querySelector('[data-resource-content-edit],[data-resource-content-save],[data-resource-preview-retry]')}",arg=id)
 retry=w.locator('[data-resource-preview-retry]')
 if not retry.count():return
 outcomes=f.page.evaluate('()=>__contentReadOutcomes');last=outcomes[-3:]
 assert len(last)==3 and all(row['code']=='busy'and row['endpoint']==last[0]['endpoint']and row['input']==last[0]['input']for row in last),outcomes
 assert last[0]['input']==dict(project=f.state()['projectId'],id=id),last
 snapshots={str(p.relative_to(f.project)):p.read_bytes()for folder in ['resource-content','resources.v1.json']for p in ([(f.project/'.confectory'/folder)]if (f.project/'.confectory'/folder).is_file()else(f.project/'.confectory'/folder).rglob('*'))if p.is_file()}
 private={str(p.relative_to(f.storage)):p.read_bytes()for p in (f.storage/'resource-content-drafts').rglob('*.json')}
 retry.click();expect(w.locator('[data-resource-content-edit],[data-resource-content-save]')).to_be_enabled()
 for name,raw in snapshots.items():assert(f.project/name).read_bytes()==raw,name
 for name,raw in private.items():assert(f.storage/name).read_bytes()==raw,name
 busy_recoveries.append(dict(outcomes=last,explicitRetry=True,resourceAndPrivateBytesUnchanged=True));(f.case/'busy-exhaustion-recovery.json').write_text(json.dumps(busy_recoveries,indent=2));f.checked('three same-target busy reads stop at the bound; explicit existing Retry restores input without content write, private intent rewrite or mutation replay')

mode=sys.argv[3];store=f.project/'.confectory/resources.v1.json';b=None

def api(action,**args):return f.invoke('projectResourceLayout',dict(action=action,project=f.state()['projectId'],**args))['result']['result']
def add(name,raw,type='text/plain'):
 revision=f.invoke('projectResources',dict(project=f.state()['projectId'],action='load'))['result']['result']['revision'];id=uuid.uuid4().hex
 f.invoke('projectResources',dict(project=f.state()['projectId'],action='import',revision=revision,command=uuid.uuid4().hex,item=dict(id=id,name=name,type=type,size=len(raw),hash=hashlib.sha256(raw).hexdigest(),modifiedAt=0,data=base64.urlsafe_b64encode(raw).decode())));return id

def browser():
 global b
 f.page.locator('#workspace').click(button='right',position=dict(x=700,y=260));f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]').last;b.locator('[data-tab=resource]').click();expect(b.locator('[data-new]')).to_be_enabled()
def viewer(id):return f.page.locator('.window[data-key="resource-file:'+id+'"]')
def opened(id):
 b.locator('[data-resource-id="'+id+'"]').press('Enter');w=viewer(id);expect(w).to_be_visible();expect(w.locator('[data-resource-content-edit],[data-resource-content-save]')).to_be_enabled();return w
def edit(w,text):
 if w.locator('[data-resource-content-edit]').count():w.locator('[data-resource-content-edit]').click()
 field=w.locator('[aria-label="파일 내용"]');expect(field).to_be_visible();field.fill(text);return field

def draft(id):
 paths=list((f.storage/'resource-content-drafts').glob('*/'+id+'.json'));return json.loads(paths[0].read_text())['value']if paths else None

def persisted(id,text):
 for _ in range(200):
  value=draft(id)
  if value and base64.urlsafe_b64decode(value['data']).decode('utf-8-sig').replace('\r\n','\n')==text:return value
  f.page.wait_for_timeout(50)
 raise AssertionError(dict(draft=draft(id),text=text))

def exact():
 assert store.read_bytes()==original_store
 for name,raw in f.original.items():assert(f.project/name).read_bytes()==raw,name
 assert not f.errors and not f.external,(f.errors,f.external)
def native_text(id):
 item=next(row for row in api('load')['items']if row['id']==id);view=f.mount()
 try:
  for _ in range(100):
   result=f.raw(dict(op='observe',view=view['view'],scope=view['scope'],endpoint='readProjectResource',input=dict(project=f.state()['projectId'],id=id,hash=item['hash'])))
   if result.get('error',{}).get('code')=='busy':time.sleep(.02);continue
   assert result.get('ok'),result;return base64.urlsafe_b64decode(result['result']['data'])
  raise AssertionError('native current-content read stayed busy')
 finally:f.raw(dict(op='dispose',view=view['view']))
def restart(i,project=None):
 global b
 f.pending();capture_busy();f.page.close();f.stop()
 if project:f.env['CONFECTORY_WEB_PROJECT']=str(project/'project.cproj')
 f.start(i);f.page=f.setup();f.idle();b=f.page.locator('.window[data-key^="browser:project:"]').last
 if not b.count():browser()
 recover_busy_read()

def hold():
 f.page.evaluate("""()=>{const base=fetch;globalThis.__contentHeld=false;let wanted=null,armed=true;fetch=async(...args)=>{let request;try{request=JSON.parse(args[1]?.body||'null')}catch{}if(armed&&request?.op==='invoke'&&request.endpoint==='projectResourceLayout'&&['save-content','restore-content'].includes(request.input?.action))wanted=request.requestId;const response=await base(...args);if(!wanted||!armed||request?.op!=='update')return response;let body;try{body=await response.clone().json()}catch{return response}const row=body.results?.find(r=>r.requestId===wanted);if(!row?.ok)return response;armed=false;globalThis.__contentHeld=true;return new Promise(resolve=>{globalThis.__releaseContent=()=>{fetch=base;delete row.result;row.ok=false;row.error={code:'owned_lost_content_reply'};resolve(new Response(JSON.stringify(body),{status:200,headers:{'Content-Type':'application/json'}}));};});};}""")
try:
 f.start(0)
 with sync_playwright()as p:
  expect.set_options(timeout=60000);f.browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.idle()
  raw='원문 🧪\r\n<script>literal</script>\r\n'.encode();id=add('생성 텍스트.txt',raw);utf16=add('UTF16 원문.txt',b'\xfe\xff'+'원문\r\n두째'.encode('utf-16be'));image=add('수정하지 않는 그림.svg',b'<svg/>','image/svg+xml');original_store=store.read_bytes();browser();w=opened(id);f.page.locator('#chat-input').fill('자료 내용과 별개 입력');f.page.locator('#chat-input').press('Tab');f.idle()
  field=edit(w,'수정한 본문\n둘째 🧪');persisted(id,'수정한 본문\n둘째 🧪');assert native_text(id)==raw;exact();f.checked('editing writes only the active project private recovery draft; literal text, imported snapshots and unrelated source/chat unchanged')
  if mode=='normal':
   w.locator('[data-resource-content-save]').click();expect(w.locator('[data-resource-content-edit]')).to_be_enabled();assert native_text(id)=='수정한 본문\r\n둘째 🧪'.encode();assert draft(id)is None;exact();f.checked('explicit Save publishes UTF8/CRLF copy metadata and one-step backup, clearing only acknowledged draft')
   hold();w.locator('[data-resource-content-restore]').click();f.page.wait_for_function('()=>__contentHeld');expect(w.locator('[data-resource-content-edit]')).to_be_disabled();expect(w.locator('[data-resource-content-restore]')).to_be_disabled();f.page.evaluate('()=>__releaseContent()');expect(w.locator('.resource-preview-status')).to_contain_text('저장 결과를 확인하지 못');expect(w.locator('[data-resource-content-edit]')).to_be_disabled();confirmed_restore=(f.project/('.confectory/resource-content/'+id+'.v1.json')).read_bytes();w.locator('[data-resource-content-restore]').click();expect(w.locator('[data-resource-content-restore]')).to_have_text('복원 취소');expect(w.locator('[data-resource-content-edit]')).to_be_enabled();assert(f.project/('.confectory/resource-content/'+id+'.v1.json')).read_bytes()==confirmed_restore;assert native_text(id)==raw;w.locator('[data-resource-content-restore]').click();expect(w.locator('[data-resource-content-restore]')).to_have_text('이전 내용 복원');assert native_text(id)=='수정한 본문\r\n둘째 🧪'.encode();exact();f.checked('in-flight and unknown restore blocks new editor entry; exact lost-reply confirmation never toggles twice; previous-content restore and restore cancellation swap exact bytes without altering immutable import')
   edit(w,'취소할 입력');persisted(id,'취소할 입력');w.locator('[data-close]').first.click();dialog=f.page.get_by_role('dialog',name='저장하지 않은 변경',exact=True);expect(dialog).to_be_visible();dialog.locator('[data-keep]').click();expect(w.locator('[aria-label="파일 내용"]')).to_have_value('취소할 입력');w.locator('[aria-label="파일 내용"]').press('Escape');f.page.get_by_role('dialog',name='저장하지 않은 변경',exact=True).locator('[data-discard]').click();expect(w.locator('[data-resource-content-edit]')).to_be_enabled();exact();f.checked('dirty close offers keep/discard; explicit cancel discards only private input and preserves current/backup')
   w.locator('[data-close]').first.click();w=opened(utf16);edit(w,'변경\n끝').press('Control+s');expect(w.locator('[data-resource-content-edit]')).to_be_enabled();assert native_text(utf16)==b'\xfe\xff'+'변경\r\n끝'.encode('utf-16be');exact();f.checked('UTF16BE BOM and CRLF encoding retained by actual editor save')
   w.locator('[data-close]').first.click();w=opened(id);edit(w,'제출 본문');persisted(id,'제출 본문');hold();w.locator('[data-resource-content-save]').click();f.page.wait_for_function('()=>__contentHeld');w.locator('[aria-label="파일 내용"]').fill('응답 대기 중 더 새 입력');f.page.evaluate('()=>__releaseContent()');expect(w.locator('.resource-preview-status')).to_contain_text('저장 결과를 확인하지 못');persisted(id,'응답 대기 중 더 새 입력');assert native_text(id)=='제출 본문'.encode();before=api('load')['items'];w.locator('[data-resource-content-save]').click();expect(w.locator('[aria-label="파일 내용"]')).to_have_value('응답 대기 중 더 새 입력');assert api('load')['items']==before;persisted(id,'응답 대기 중 더 새 입력');w.locator('[data-resource-content-save]').click();expect(w.locator('[data-resource-content-edit]')).to_be_enabled();assert native_text(id)=='응답 대기 중 더 새 입력'.encode();exact();f.checked('lost actual save reply keeps exact pending intent and newer text; replay adds no backup, later explicit Save publishes only newer input')
  elif mode=='lifecycle':
   restart(1);w=viewer(id);expect(w.locator('[aria-label="파일 내용"]')).to_have_value('수정한 본문\n둘째 🧪');assert native_text(id)==raw;exact();f.checked('cold engine restores acknowledged private text input and original basis without auto-saving')
   pending=draft(id);side=f.project/'.confectory/resource-content';side.mkdir(exist_ok=True);side.chmod(0o555)
   try:w.locator('[data-resource-content-save]').click();expect(w.locator('.resource-preview-status')).to_contain_text('저장 결과를 확인하지 못');expect(w.locator('[aria-label="파일 내용"]')).to_have_value('수정한 본문\n둘째 🧪');assert native_text(id)==raw;exact()
   finally:side.chmod(0o755)
   restart(2);w=viewer(id);expect(w.locator('[data-resource-content-save]')).to_have_text('저장 결과 다시 확인');assert native_text(id)==raw;w.locator('[data-resource-content-save]').click();expect(w.locator('[data-resource-content-edit]')).to_be_enabled();assert native_text(id)=='수정한 본문\r\n둘째 🧪'.encode();exact();f.checked('native read-only write failure preserves all bytes and private exact request across cold restart; explicit retry succeeds')
   edit(w,'응답 유실 후 재시작');persisted(id,'응답 유실 후 재시작');hold();w.locator('[data-resource-content-save]').click();f.page.wait_for_function('()=>__contentHeld');f.page.evaluate('()=>__releaseContent()');expect(w.locator('.resource-preview-status')).to_contain_text('저장 결과를 확인하지 못');confirmed=native_text(id);restart(3);w=viewer(id);expect(w.locator('[data-resource-content-save]')).to_have_text('저장 결과 다시 확인');assert native_text(id)==confirmed;sidecar=f.project/('.confectory/resource-content/'+id+'.v1.json');before=sidecar.read_bytes();w.locator('[data-resource-content-save]').click();expect(w.locator('[data-resource-content-edit]')).to_be_enabled();assert sidecar.read_bytes()==before;exact();f.checked('cold restart of actual successful-but-lost native reply requires explicit exact replay and does not write another backup')
   edit(w,'충돌할 입력');persisted(id,'충돌할 입력');basis=api('load');api('save-content',revision=basis['revision'],command=uuid.uuid4().hex,id=id,hash=next(row for row in basis['items']if row['id']==id)['hash'],type='text/plain',size=4,data='cGVlcg==');peer=native_text(id);w.locator('[data-resource-content-save]').click();expect(w.locator('.resource-preview-status')).to_contain_text('저장 결과를 확인하지 못');expect(w.locator('[aria-label="파일 내용"]')).to_have_value('충돌할 입력');assert native_text(id)==peer;restart(4);w=viewer(id);expect(w.locator('[aria-label="파일 내용"]')).to_have_value('충돌할 입력');w.locator('[data-resource-content-save]').click();expect(w.locator('.resource-preview-status')).to_contain_text('저장 결과를 확인하지 못');assert native_text(id)==peer;w.locator('[data-resource-content-cancel]').click();f.page.get_by_role('dialog',name='저장하지 않은 변경',exact=True).locator('[data-discard]').click();expect(w.locator('[data-resource-content-edit]')).to_be_enabled();exact();f.checked('peer update refuses stale content after restart and retry; explicit cancel keeps peer bytes and clears only local intent')
   edit(w,'프로젝트 왕복 입력');persisted(id,'프로젝트 왕복 입력');other=f.case/'same namespace other project';shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory','.build'));restart(5,other);expect(viewer(id)).to_have_count(0);assert api('load')['items']==[];restart(6,f.project);w=viewer(id);expect(w.locator('[aria-label="파일 내용"]')).to_have_value('프로젝트 왕복 입력');assert native_text(id)==peer;exact();f.checked('another real project with the same namespace never adopts private text input; returning restores the original project draft and unchanged current copy')
  else:raise AssertionError(mode)
  if '--busy-reads'in sys.argv:
   assert mode!='lifecycle'or busy_recoveries,'forced three-busy refusal and explicit Retry must execute'
   capture_busy();assert any(row['endpoint']=='readResourceContentDraft'for page in busy_events for row in page['busy']);assert mode!='lifecycle'or any(row['endpoint']=='readResourceContentPending'for page in busy_events for row in page['busy']);f.checked('controlled first busy private-draft/pending observations retry the exact same target and restore input/uncertain command; no mutation replay or automatic rebase')
  f.page.screenshot(path=str(f.case/('resource-content-'+mode+'.png')));f.pending();exact();f.browser.close()
except Exception as error:
 if '--busy-reads'in sys.argv:
  try:(f.case/'failed-read-outcomes.json').write_text(json.dumps(f.page.evaluate('()=>__contentReadOutcomes'),indent=2))
  except Exception:pass
 (f.case/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:
 f.stop();(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2))
