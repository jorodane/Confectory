"""Read-only exact child emitter output in real Linux engine/UI; no sibling text."""
import ast,copy,hashlib,json,stat,sys,time
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
fixture=Path(__file__).with_name('v821_frame_structure_ui.py');nodes=ast.parse(fixture.read_text()).body
exec(compile(ast.Module(body=nodes[:next(i for i,n in enumerate(nodes)if isinstance(n,ast.Try))],type_ignores=[]),str(fixture),'exec'),globals())
upper=mode=='upper'
leaf=frame
if upper:
 frame=t.graph+'/graph:body';other=t.graph+'/graph:other'
first_path='body' if upper else 'body/nest'
second_path='other' if upper else 'other/nest'
binding_key='documentFramePreviewBinding' if upper else 'documentFrameOrderBinding'
name_cell='nest' if upper else 'inner'

def open_child(path):
 if upper:
  doc().locator('[data-document-internal="'+path+'"]').click();f.idle()
  expect(doc().locator('[data-document-cell=nest]')).to_be_visible()
 else:enter(path)

def preview(data,id=None,ok=True,**extra):
 binding=data.get(binding_key)or data.get('documentFrameOrderBinding')or dict(root=t.graph,graph=frame,path='body/nest',rootHash=hashlib.sha256(json.dumps(base,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),frameHash=hashlib.sha256(json.dumps(target,separators=(',',':'),ensure_ascii=False).encode()).hexdigest())
 return f.invoke('blueprint',dict(action='nativePreview',id=id or data['id'],documentFrame=copy.deepcopy(binding),sourceProof=x.proof(data),checkpointHash=data['checkpointHash'],**extra),ok)['result'].get('result')
def scope_text(result):return result['diagnostics']['body']+result['diagnostics']['members']
def native_view():return panel().locator('.function-native-preview')
def native():panel().get_by_role('tab',name='네이티브 미리보기',exact=True).click();expect(native_view()).to_be_visible()
def logic():panel().get_by_role('tab',name='논리 코드',exact=True).click();expect(doc()).to_be_visible()
def ui_generated(expected):
 view=native_view();expect(view.locator('[role=status]')).to_contain_text('생성됨',timeout=90000);expect(view.locator('[data-native-body]')).to_have_text(expected['diagnostics']['body'],use_inner_text=False);assert view.locator('[data-native-body]').text_content()==expected['diagnostics']['body'];assert view.locator('[data-native-members]').text_content()==expected['diagnostics']['members'];assert not view.locator('textarea,input,[contenteditable=true]').count()
def preserved():
 untouched();assert checkpoint.read_bytes()==before;assert f.invoke('draftHistory',dict(action='inspect'))['result']['result']==history
try:
 f.start(0);f.invoke('select',dict(id=t.feature));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();history=f.invoke('draftHistory',dict(action='inspect'))['result']['result'];a=read(frame)
 if mode=='shared':
  preview(a,ok=False)
  shared_parent=read(t.graph+'/graph:body')
  assert shared_parent['documentFrameOrderBinding'] is None and 'documentFramePreviewBinding' not in shared_parent
  preserved()
 else:
  first=preview(a)
  assert (first['id'],first['rootId'],first['privatePath'])==(frame,t.graph,first_path)
  assert set(first)=={'id','rootId','privatePath',binding_key,'checkpointHash','sources','diagnostics','sourceWritten','compiled'}
  assert not first['sourceWritten'] and not first['compiled']
  assert first['diagnostics']['assembledPath']==first_path and first['diagnostics']['state']=='source-assembled'
  assert hashlib.sha256(scope_text(first).encode()).hexdigest()==first['diagnostics']['bodyHash']
  assert all(label not in json.dumps(first) for label in ['peer-inner','peer-tail'])
  assert 'WriteLine("after")' not in scope_text(first)
  assert ('parent-tail' in scope_text(first))==upper
  second=preview(read(other));assert second['diagnostics']['assembledPath']==second_path
  assert all(label in scope_text(second) for label in ['peer-inner','peer-tail'])
  assert all(label not in scope_text(second) for label in ['parent-tail','WriteLine("body")','WriteLine("inside")','WriteLine("after")'])
  assert first['diagnostics']['bodyHash']!=second['diagnostics']['bodyHash']
  if upper:
   assert a['documentFrameOrderBinding'] is None
   assert set(first['diagnostics'])=={'state','body','members','bodyHash','assembledPath'}
   assert not first['diagnostics']['members'] and not second['diagnostics']['members']
   nested=preview(read(leaf))
   assert nested['diagnostics']['body'] in first['diagnostics']['body']
   assert nested['diagnostics']['body'] not in second['diagnostics']['body']
   assert 'WriteLine("parent-tail")' not in scope_text(nested)
  whole=f.invoke('blueprint',dict(action='nativePreview',id=t.graph))['result']['result']['diagnostics'];assert first['diagnostics']['body']in whole['body']and second['diagnostics']['body']in whole['body'];assert first['diagnostics']['members']in whole['members']and second['diagnostics']['members']in whole['members'];assert 'selectedAssembly'not in whole
  for mutation in ['unbound','root','path','root-hash','frame-hash','sibling','owner','surface','proof','revision','checkpoint','not-graph']:
   q=dict(action='nativePreview',id=frame,documentFrame=copy.deepcopy(a[binding_key]),sourceProof=x.proof(a),checkpointHash=a['checkpointHash'])
   if mutation=='unbound':q.pop('documentFrame')
   elif mutation=='root':q['documentFrame']['root']=f.n+'Missing/body:common'
   elif mutation=='path':q['documentFrame']['path']=second_path
   elif mutation=='root-hash':q['documentFrame']['rootHash']='0'*64
   elif mutation=='frame-hash':q['documentFrame']['frameHash']='0'*64
   elif mutation=='sibling':q['id']=other
   elif mutation=='owner':q['owner']=f.n+'Missing'
   elif mutation=='surface':q['uiSurface']='view:1'
   elif mutation=='proof':q['sourceProof']='[]'
   elif mutation=='revision':rows=json.loads(q['sourceProof']);rows[0][1]+=1;q['sourceProof']=json.dumps(rows)
   elif mutation=='checkpoint':q['checkpointHash']='0'*64
   else:q['id']=frame+'/graph:inner'
   f.invoke('blueprint',q,False);preserved()
  f.checked('exact child output is captured by the actual root emitter, matches its generated body/members/hash, distinguishes sibling local IDs, excludes sibling C# payload and refuses wrong scope/proof/checkpoint without writes')
 with sync_playwright()as pw:
  expect.set_options(timeout=45000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size(dict(width=1800,height=1400));open_document();open_child(first_path)
  if upper:
   expect(doc().locator('[data-document-up=finish]')).to_be_disabled()
   expect(doc().locator('[data-document-add=finish]')).to_be_disabled()
  native();view=native_view()
  if mode=='shared':
   expect(view.locator('[role=status]')).to_contain_text('지원하지');assert not view.locator('[data-native-body]').text_content()and not view.locator('[data-native-members]').text_content();preserved();x.build('child-preview-shared-original',10,'body\ninside\nparent-tail\npeer-inner\npeer-tail\nafter\n10');untouched();f.checked('shared/branch ancestor stays unsupported in actual UI/API without root/sibling fallback; original execution and source/modes remain unchanged')
  else:
   ui_generated(first);expect(view.locator('.fd-native-scope')).to_contain_text('선택한 자식');preserved();f.page.screenshot(path=str(f.case/'child-preview-generated.png'),full_page=True)
   for file in ['Pair.body.inner.node.json','Pair.peer.inner.node.json']:
    p=f.project/file;raw=p.read_bytes();p.write_bytes(raw+b' ')
    try:view.locator('[data-native-refresh]').click();expect(view.locator('[role=status]')).to_contain_text('생성에 실패');assert not view.locator('[data-native-body]').text_content()and not view.locator('[data-native-members]').text_content();assert p.read_bytes()==raw+b' 'and checkpoint.read_bytes()==before
    finally:p.write_bytes(raw)
    view.locator('[data-native-refresh]').click();ui_generated(first);preserved()
   p=f.project/'Pair.body.inner.node.json';old_mode=stat.S_IMODE(p.stat().st_mode);p.chmod(0o000)
   try:view.locator('[data-native-refresh]').click();expect(view.locator('[role=status]')).to_contain_text('생성에 실패');assert not view.locator('[data-native-body]').text_content()and not view.locator('[data-native-members]').text_content();assert checkpoint.read_bytes()==before
   finally:p.chmod(old_mode)
   graph_path=f.project/t.graph_file;old_mode=stat.S_IMODE(graph_path.stat().st_mode);graph_path.chmod(0o400);checkpoint.chmod(0o400)
   try:view.locator('[data-native-refresh]').click();ui_generated(first);assert checkpoint.read_bytes()==before
   finally:graph_path.chmod(old_mode);checkpoint.chmod(0o600)
   preserved();f.checked('actual child preview is read-only, clears body and members on selected/sibling source or read-permission failure, and works with read-only source/checkpoint without expanding write rights')
   logic();root_view();open_child(second_path);native();ui_generated(second);preserved();f.checked('actual sibling navigation with identical local node IDs shows the other exact scope without child A code')
   requests=set();paused={}
   def hold(route):
    body=route.request.post_data_json
    if body.get('op')=='invoke'and body.get('endpoint')=='blueprint'and body.get('input',{}).get('action')=='nativePreview'and body['input'].get('id')==other:requests.add(body['requestId'])
    response=route.fetch();payload=response.json()
    if not paused and body.get('op')=='update'and any(r.get('requestId')in requests for r in payload.get('results',[])):paused.update(route=route,response=response,payload=payload);return
    route.fulfill(response=response)
   f.page.route('**/api/request',hold);view.locator('[data-native-refresh]').click();deadline=time.monotonic()+90
   while not paused and time.monotonic()<deadline:f.page.wait_for_timeout(30)
   # Global transport busy state blocks path navigation until update completes.
   # Change private input (an available user action), then release the real old result.
   assert paused,'actual old child response missing';logic();doc().locator('[data-document-name="'+name_cell+'"]').fill('응답 대기 중 입력 α');doc().locator('.fd-document-title').click();native();expect(view.locator('[role=status]')).to_contain_text('저장하지 않은 입력');paused['route'].fulfill(response=paused['response'],json=paused['payload']);f.page.unroute_all(behavior='wait');f.idle();late=pending();assert '응답 대기 중 입력 α'in json.dumps(late,ensure_ascii=False);assert not view.locator('[data-native-body]').text_content()and not view.locator('[data-native-members]').text_content();preserved()
   f.checked('a held actual child emitter response cannot display stale C# over later private input; body/member containers stay empty and later input is retained')
   logic();doc().locator('[data-document-name="'+name_cell+'"]').fill('자식 입력 보존 α');doc().locator('.fd-document-title').click();held=pending();assert held;native();expect(view.locator('[role=status]')).to_contain_text('저장하지 않은 입력');assert not view.locator('[data-native-body]').text_content()and not view.locator('[data-native-members]').text_content();assert pending()==held;preserved()
   f.pending();f.page.close();f.stop();f.start(1);f.page=f.setup();f.page.set_viewport_size(dict(width=1800,height=1400));f.idle();expect(native_view()).to_be_visible();expect(native_view().locator('[role=status]')).to_contain_text('저장하지 않은 입력');assert pending()==held;preserved();x.build('child-preview-unchanged',10,'body\ninside\nparent-tail\npeer-inner\npeer-tail\nafter\n10');untouched();f.checked('unsaved/cold child input refuses preview without losing text, source or history; actual unchanged root engine executes both qualified child scopes and returns 10')
  f.page.screenshot(path=str(f.case/('child-preview-'+mode+'.png')),full_page=True);assert not f.errors and not f.external,(f.errors,f.external);f.browser.close()
 if upper:
  f.stop()
  foreign=f.case/'other project';foreign.mkdir()
  foreign_manifest=foreign/'project.cproj'
  foreign_manifest.write_text('''project Other.Preview version "1" {
   standalone true;entry Other.Preview::Main;
   element Main function "Main.celem";element MainBody implementation "MainBody.celem";
  }''')
  (foreign/'Main.celem').write_text('function Other.Preview::Main () -> int {provide Other.Preview::Main with Other.Preview::MainBody;}')
  (foreign/'MainBody.celem').write_text('implementation Other.Preview::MainBody for Other.Preview::Main () -> int {body common "Main.csbody";}')
  (foreign/'Main.csbody').write_text('return 41;')
  foreign_originals={p:p.read_bytes() for p in foreign.iterdir()}
  f.env['CONFECTORY_WEB_PROJECT']=str(foreign_manifest)
  f.start(2)
  f.invoke('select',dict(id='Other.Preview::Main'))
  rejection=f.invoke('blueprint',dict(action='nativePreview',id=frame,documentFrame=a[binding_key],
                                     sourceProof=x.proof(a),checkpointHash=a['checkpointHash']),False)['result']
  assert not rejection.get('result') and not any(label in json.dumps(rejection) for label in ['peer-inner','parent-tail'])
  assert all(p.read_bytes()==raw for p,raw in foreign_originals.items())
  untouched();assert checkpoint.read_bytes()==before
  f.checked('another active project cannot read emitter output using the prior project’s child observation; both projects keep their original files')
except BaseException:
 if getattr(f,'page',None):
  try:(f.case/'child-preview-failure.html').write_text(f.page.content());f.page.screenshot(path=str(f.case/'child-preview-failure.png'),timeout=10000)
  except Exception:pass
 raise
finally:
 (f.case/'child-preview-traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False));(f.case/'child-preview-checks.json').write_text(json.dumps(f.checks,ensure_ascii=False));f.stop()
print('V821_CHILD_PREVIEW',mode,f.case,flush=True)
