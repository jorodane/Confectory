"""One directly owned child void insertion over actual Linux UI/engine and CAS.
Existing frame fixture only; its order test body is not executed.
"""
import ast,copy,json,os,shutil,stat,sys,time,uuid,subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
fixture=Path(__file__).with_name('v821_frame_structure_ui.py');nodes=ast.parse(fixture.read_text()).body
exec(compile(ast.Module(body=nodes[:next(i for i,n in enumerate(nodes)if isinstance(n,ast.Try))],type_ignores=[]),str(fixture),'exec'),globals())
at_start=mode in ('start', 'method-direct')
anchor='$entry' if at_start else 'inner'
if compound_parent:
 anchor = 'nest'
insertion_binding = 'documentFrameCompoundInsertion' if compound_parent else 'documentFrameOrderBinding'
insertion_action = 'frame-compound-insert' if compound_parent else 'frame-create'
def inserted_order(created):
 if compound_parent:
  return ['$entry', 'nest', created, 'finish', '$exit:return']
 return ['$entry',created,'inner','tail','$exit:return'] if at_start else ['$entry','inner',created,'tail','$exit:return']
def show_child():
 if panel().locator('.bp-breadcrumbs button').count():root_view()
 enter()
def resume(i):
 restart(i)
 show_child()
def reconnect(i):
 f.start(i)
 f.page = f.setup()
 f.page.set_viewport_size(dict(width=1800,height=1400))
 f.idle()
 open_document()
 show_child()
def proposal(data,node='cell_probe',after=anchor,to=None):
 incoming=dict(action='entry',node='$entry',to=node) if after=='$entry' else dict(action='route',node=after,port='next',to=node)
 successor=to or ('finish' if compound_parent else 'inner' if after=='$entry' else 'tail')
 return dict(action='authorBatch',documentFrame=copy.deepcopy(data.get(insertion_binding)or dict(root=t.graph,graph=frame,path=frame_path,rootHash='0'*64,frameHash='0'*64)),id=frame,attempt=uuid.uuid4().hex,checkpointHash=data['checkpointHash'],sourceProof=x.proof(data),edits=[dict(action='createNode',node=node,definition=dict(kind='code',control='next',intent='새 동작',signature=signature())),dict(action='rename',node=node,text='자식 추가 α'),dict(action='intent',node=node,text='자식 추가 α'),dict(action='source',node=node,text='global::System.Console.WriteLine("inserted-child");\nreturn;'),incoming,dict(action='route',node=node,port='next',to=successor)])

def check_other_project(original, checkpoint, held):
 duplicate = f.case / 'same IDs other project'
 shutil.copytree(f.project, duplicate, ignore=shutil.ignore_patterns('.confectory'))
 files = {path: path.read_bytes() for path in duplicate.rglob('*') if path.is_file()}
 archived = checkpoint.read_bytes()
 manifest = f.env['CONFECTORY_WEB_PROJECT']
 f.pending()
 f.page.close()
 f.stop()
 try:
  f.env['CONFECTORY_WEB_PROJECT'] = str(duplicate / f.manifest.name)
  f.start(6)
  f.invoke('select', dict(id=t.feature))
  f.invoke('saveDraft', {})
  duplicate_checkpoint = next(duplicate.glob('.confectory/edit-workspaces/*/draft.json'))
  duplicate_before = duplicate_checkpoint.read_bytes()
  same_ids = read()
  assert same_ids[insertion_binding] == original[insertion_binding]
  assert same_ids['checkpointHash'] != original['checkpointHash']
  f.invoke('blueprint', proposal(original), False)
  assert duplicate_checkpoint.read_bytes() == duplicate_before and len(read()['nodes']) == 2
  assert all(path.read_bytes() == data for path, data in files.items())
 finally:
  f.stop()
  f.env['CONFECTORY_WEB_PROJECT'] = manifest
 reconnect(7)
 assert checkpoint.read_bytes() == archived and retained(held)
 untouched()
 f.checked('A different project with identical graph IDs and bytes rejects the original insertion; returning restores its local inputs.')

def check_previous_insertion_reader(created, checkpoint):
 previous = os.environ.get('METHOD_INSERT_PREVIOUS')
 if not previous:
  return
 old = Path(previous)
 repo, report, editor_repo = f.repo, f.report, f.env['CONFECTORY_EDITOR_REPO']
 f.pending()
 saved = checkpoint.read_bytes()
 f.page.close()
 f.stop()
 try:
  f.repo, f.report = old / 'checkout', json.loads((old / 'report.json').read_text())
  f.env['CONFECTORY_EDITOR_REPO'] = str(f.repo)
  f.start(8)
  loaded = read()
  row = next(node for node in loaded['nodes'] if node['id'] == created)
  assert row['sourceId'] == frame.replace('/graph:', '/node:') + '/node:' + created
  assert row['signature'] == signature() and 'inserted-child' in row['source']
  assert len(read(other)['nodes']) == 2
  assert checkpoint.read_bytes() == saved
  f.invoke('reviewGroup', dict(ids=loaded['reviewIds'], target='portable'))
  assert f.state()['review']['status'] == 'ready'
  before_review, after_review = map(json.loads, (saved, checkpoint.read_bytes()))
  assert after_review['version'] == 1
  # Review exports fresh process-local observations and normalizes empty maps.
  for document in (before_review, after_review):
   document['history'].pop('epoch')
   for name in ('retirements', 'retirementOutcomes', 'privateCopies'):
    if document[name] is None:
     document[name] = {}
   for unit in document['changes']:
    unit.pop('revision')
  assert after_review == before_review
  new_unit = next(unit for unit in after_review['changes'] if unit['id'] == row['sourceId'])
  assert not (f.project / new_unit['path']).exists()
  untouched()
 finally:
  f.stop()
  f.repo, f.report, f.env['CONFECTORY_EDITOR_REPO'] = repo, report, editor_repo
 reconnect(9)
 f.checked('The unmodified previous engine reopens and reviews the version-1 checkpoint with the same new owned code.')
def edit_body(created, text='global::System.Console.WriteLine("inserted-child");\nreturn;'):
 cell = doc().locator(f'[data-document-code="{created}"]')
 expect(cell).to_be_enabled()
 cell.click()
 dialog = f.page.locator('.bp-script-dialog')
 source = dialog.locator('[data-code-source]')
 body = dialog.locator('[data-code-region=body]').text_content()
 source.evaluate('(el,text)=>{el.focus();const at=el.value.indexOf(text);if(at<0)throw Error("Missing protected body");el.setSelectionRange(at,at+text.length)}',body)
 f.page.keyboard.insert_text(text)
 expect(dialog.locator('[data-code-region=body]')).to_have_text(text)
 dialog.locator('[data-code-save]').click()
 expect(dialog).to_be_hidden()
 f.idle()
def confirm_with_compile_error(window):
 mark = len(f.traffic)
 window.locator('#confirm').click()
 deadline = time.monotonic() + 120
 while time.monotonic() < deadline:
  ids = {row['invoke']['requestId'] for row in f.traffic[mark:]
         if row.get('invoke',{}).get('endpoint') == 'confirmGroup'}
  replies = [row['result'] for row in f.traffic[mark:]
             if row.get('result',{}).get('requestId') in ids]
  if replies:
   reply = replies[-1]['result']
   f.idle()
   diagnostics = json.dumps(f.state(), ensure_ascii=False)
   assert reply['sourceConfirmed'] is False and 'CS0103' in diagnostics and 'MissingChildCellSymbol' in diagnostics, f.state().get('review')
   return
  f.page.wait_for_timeout(25)
 raise AssertionError('Missing compiler result from explicit Confirm')
def verify_compiler_recovery(checkpoint):
 invalid = 'MissingChildCellSymbol();\nreturn;'
 add = doc().locator(f'[data-document-add="{anchor}"]')
 add.click()
 f.idle()
 created, = [cell for cell in order() if cell.startswith('cell_')]
 edit_body(created,invalid)
 save()
 assert not pending() and order() == inserted_order(created)
 physical = {p:p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.parts}
 assert physical == x.physical
 resume(1)
 assert order() == inserted_order(created)
 inserted = next(node for node in read()['nodes'] if node['id']==created)
 assert inserted['source'] == invalid
 review().locator('[data-reject]').click()
 expect(f.page.locator('.window[data-key="review"]')).to_be_hidden()
 untouched()
 window = review()
 saved = checkpoint.read_bytes()
 confirm_with_compile_error(window)
 assert checkpoint.read_bytes() == saved
 assert {p:p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.parts} == physical
 assert next(node for node in read()['nodes'] if node['id']==created)['source'] == invalid
 f.checked('nested cell Save and cold reopen retain C#; Review cancel and real CS0103 Confirm leave the whole checkpoint and final files intact')

 resume(2)
 assert order() == inserted_order(created)
 edit_body(created)
 panel().locator('[data-bp-save]').click()
 f.idle()
 assert not pending()
 corrected = next(node for node in read()['nodes'] if node['id']==created)
 assert corrected['sourceId'] == inserted['sourceId'] and 'inserted-child' in corrected['source']
 untouched()
 resume(3)
 assert order() == inserted_order(created)
 window = review()
 window.locator('#confirm').click()
 expect(window).to_be_hidden(timeout=120000)
 f.idle()
 x.build('owned-child-compile-recovery',10,'body\ninserted-child\ninside\nparent-tail\npeer-inner\npeer-tail\nafter\n10')
 assert all(p.read_bytes()==v for p,v in physical.items() if p.name!=t.graph_file)
 files = {p for p in f.project.rglob('*.node.json') if '.confectory' not in p.parts} - physical.keys()
 assert len(files)==1 and json.loads(files.pop().read_text())['node']==created
 resume(4)
 assert order() == inserted_order(created) and len(read(other)['nodes'])==2 and not pending()
 f.checked('after cold recovery the same cell can be corrected, saved and explicitly confirmed; actual order, return, sibling and original sources are preserved')
def pure_denied(graph,path,edits):
 try:f.metadata('blueprintCellRegion',action=insertion_action,graph=graph,path=path,edits=edits)
 except (AssertionError,subprocess.CalledProcessError):return
 raise AssertionError('Unsupported pure insertion accepted')

def check_confirmed_compound_workflow():
 originals = {path: path.read_bytes() for path in f.project.rglob('*')
              if path.is_file() and '.confectory' not in path.parts and path.name != t.graph_file}
 panel().get_by_role('tab', name='네이티브 미리보기', exact=True).click()
 preview = panel().locator('.function-native-preview')
 expect(preview.locator('[role=status]')).to_contain_text('생성됨')
 expect(preview.locator('[data-native-body]')).to_contain_text('inserted-child')
 expect(preview.locator('[data-native-body]')).not_to_contain_text('peer-inner')
 expect(preview.locator('textarea,input,[contenteditable=true]')).to_have_count(0)
 panel().get_by_role('tab', name='논리 코드', exact=True).click()
 doc().locator('[data-document-internal=nest]').click()
 f.idle()
 doc().locator('[data-document-up=tail]').click()
 f.idle()
 assert order() == ['$entry', 'tail', 'inner', '$exit:return']
 save()
 assert not pending()
 restart(10)
 assert order() == ['$entry', 'tail', 'inner', '$exit:return']
 r = review()
 r.locator('#confirm').click()
 expect(r).to_be_hidden(timeout=120000)
 f.idle()
 x.build('compound-insert-then-child-order', 10, 'inside\nbody\ninserted-child\nparent-tail\npeer-inner\npeer-tail\nafter\n10')
 assert all(path.read_bytes() == raw for path, raw in originals.items())
 f.checked('After confirming insertion, the selected parent preview and a separate child reorder retain the actual insertion and sibling execution.')
try:
 f.start(0);f.invoke('select',dict(id=t.feature));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
 with sync_playwright()as pw:
  expect.set_options(timeout=45000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size(dict(width=1800,height=1400));open_document()
  insert_at_start=lambda:doc().locator('[data-document-add="$entry"]')
  if mode=='shared' or method:expect(insert_at_start()).to_have_count(0)
  else:expect(insert_at_start()).to_be_enabled()
  enter();original=read();initial=order()
  if method:
   assert original['diagnostics']['state'] in ('source-ready', 'source-assembled')
  if unavailable:
   expect(insert_at_start()).to_have_count(0)
   assert original.get(insertion_binding) is None
   expect(doc().locator(f'[data-document-add="{anchor}"]')).to_be_disabled()
   title = doc().locator(f'[data-document-name="{anchor}"]')
   title.fill('자식 입력 보존')
   doc().locator('.fd-document-title').click()
   held = pending()
   f.invoke('blueprint', proposal(original), False)
   assert checkpoint.read_bytes() == before and pending() == held
   untouched()
   resume(1)
   assert pending() == held
   expect(doc().locator(f'[data-document-name="{anchor}"]')).to_have_value('자식 입력 보존')
   x.build('child-insert-blocked-unchanged', 10, 'body\ninside\nparent-tail\npeer-inner\npeer-tail\nafter\n10')
   untouched()
   f.checked(f'{mode} refuses insertion in the UI and engine while preserving local inputs and the original execution.')
  elif mode=='compile-recovery':
   verify_compiler_recovery(checkpoint)
  else:
   assert original[insertion_binding]['path']==frame_path
   add=doc().locator('[data-document-add="'+anchor+'"]');expect(add).to_be_enabled()
   # Pure compiler plan limits include the new cell; metadata reads grant no writes.
   q=proposal(original);f.metadata('blueprintCellRegion',action=insertion_action,graph=base,path=frame_path,edits=q['edits'])
   if compound_parent:
    expect(insert_at_start()).to_have_count(0)
    expect(doc().locator('[data-document-add=finish]')).to_be_disabled()
    expect(doc().locator('[data-document-up=finish]')).to_be_disabled()
    pure_denied(base, frame_path, proposal(original, after='finish', to='exit:return')['edits'])
   else:
    qparent=proposal(original,node='finish');f.metadata('blueprintCellRegion',action=insertion_action,graph=base,path=frame_path,edits=qparent['edits'])
   huge=copy.deepcopy(base);c=chosen(huge)
   while len(c['nodes'])<63:c['nodes'].append(code('n'+str(len(c['nodes'])),'unused.node.json'))
   c['edges']=[edge(n['id'],c['nodes'][i+1]['id']if i+1<len(c['nodes'])else'exit:return')for i,n in enumerate(c['nodes'])];pure_denied(huge,frame_path,q['edits'])
   deep=child([code('inner','unused.node.json'),code('tail','unused2.node.json')],{'return':None})
   for i in reversed(range(9)):deep=child([compound('p'+str(i),deep)],{'return':None})
   pure_denied(deep,'/'.join('p'+str(i)for i in range(9)),q['edits'])
   many=child([compound('x'+str(i),child([code('n'+str(j),'unused.node.json')for j in range(51 if i==0 else 50)],{'return':None}))for i in range(5)],{'return':None});pure_denied(many,'x0',proposal(original,after='n0',to='n1')['edits'])
   add.click();f.idle();created=[id for id in order()if id.startswith('cell_')];assert len(created)==1;created=created[0];assert order()==inserted_order(created);assert len(pending())==6
   doc().locator('.fd-document-title').click();doc().press('Control+z');assert order()==initial;doc().press('Control+y');assert order()==inserted_order(created)
   if at_start:expect(insert_at_start()).to_be_disabled()
   edit_body(created);held=pending();assert len(held)==6;untouched();assert checkpoint.read_bytes()==before
   root_view();enter(peer_path);expect(add).to_be_disabled();assert read(other)['entry']==('nest' if compound_parent else 'inner');root_view();enter();assert pending()==held
   panel().get_by_role('tab',name='블루프린트 보기',exact=True).click()
   expect(panel().locator(f'[data-bp-node="{created}"]')).to_be_visible()
   if method:
    expect(panel().locator(f'[data-bp-link="route:{created}"]')).to_have_count(1)
   panel().get_by_role('tab',name='논리 코드',exact=True).click()
   assert order() == inserted_order(created)
   resume(1);assert pending()==held and created in order();untouched();f.checked('one qualified child insertion edits its protected C# body, private Undo/Redo and cold; sibling duplicate local IDs and original source/ABI remain distinct; depth/per-frame/global limits hold')
   faults=['unbound','root','path','root-hash','frame-hash','owner','frame','local-id','args','return','scope','continuation','source','remove','two','checkpoint','proof','mixed']
   if method:
    faults = ['unbound','path','frame-hash','args','return','continuation','source','checkpoint','proof']
   if at_start:faults+=['wrong-first-cell','wrong-entry-anchor','extra-entry-key']
   for mutation in faults:
    q=proposal(read());e=q['edits']
    if mutation=='unbound':q.pop('documentFrame')
    elif mutation=='root':q['documentFrame']['root']=f.n+'Missing/body:common'
    elif mutation=='path':q['documentFrame']['path']=peer_path
    elif mutation=='root-hash':q['documentFrame']['rootHash']='0'*64
    elif mutation=='frame-hash':q['documentFrame']['frameHash']='0'*64
    elif mutation=='owner':q.update(owner=f.n+'Missing',ownerHash='0'*64)
    elif mutation=='frame':e[0]['frame']=other
    elif mutation=='local-id':e[0]['node']='inner'
    elif mutation=='args':e[0]['definition']['signature']['args']=[dict(name='value',type='int')]
    elif mutation=='return':e[0]['definition']['signature']['return']='int'
    elif mutation=='scope':e[0]['definition']['branchOwner']='inner'
    elif mutation=='continuation':e[-1]['to']='exit:return'
    elif mutation=='wrong-first-cell':e[-1]['to']='tail'
    elif mutation=='wrong-entry-anchor':e[-2]['node']='inner'
    elif mutation=='extra-entry-key':e[-2]['port']='next'
    elif mutation=='source':e[3]['node']='inner'
    elif mutation=='remove':e[0]['action']='removeNode'
    elif mutation=='two':e.append(copy.deepcopy(e[0]))
    elif mutation=='checkpoint':q['checkpointHash']='0'*64
    elif mutation=='proof':q['sourceProof']='[]'
    else:q['documentCompound']=True
    f.invoke('blueprint',q,False);assert checkpoint.read_bytes()==before and pending()==held and len(read()['nodes'])==2;untouched()
   f.checked('The negative request matrix preserves the same checkpoint, graph, sources and local inputs.')
   if mode == 'method-nested' or compound_parent:
    check_other_project(original, checkpoint, held)
   peer_file=f.project/'Pair.peer.inner.node.json';raw=peer_file.read_bytes();peer_file.write_bytes(raw+b' ')
   try:save();assert retained(held)and checkpoint.read_bytes()==before and len(read()['nodes'])==2;assert peer_file.read_bytes()==raw+b' '
   finally:peer_file.write_bytes(raw)
   checkpoint.chmod(0o400)
   try:save();assert retained(held)and checkpoint.read_bytes()==before and len(read()['nodes'])==2;untouched()
   finally:checkpoint.chmod(0o600)
   resume(2);assert retained(held);save();assert not pending();current=read();made=next(n for n in current['nodes']if n['id']==created);assert made['sourceId']==frame.replace('/graph:', '/node:')+'/node:'+created;assert 'inserted-child'in made['source'];assert len(read(other)['nodes'])==2;untouched();resume(3);assert created in order()and not pending()
   if method:
    draft = json.loads(checkpoint.read_bytes())
    units = {row['id']: row for row in draft['changes']}
    sources = units[t.graph]['propertyObservations']['sources']
    assert draft['version'] == units[t.graph]['propertyObservations']['version'] == 1
    assert set(sources) == {*original[insertion_binding]['sources'], made['sourceId']}
    assert sources[made['sourceId']]['hash'] == 'missing'
    assert not (f.project / units[made['sourceId']]['path']).exists()
    expect(doc().locator(f'[data-document-add="{anchor}"]')).to_be_disabled()
   history=f.invoke('draftHistory',dict(action='inspect'))['result']['result'];assert history['boundary']=='OWNERSHIP_CHANGED'and not history['undo']['available']and not history['redo']['available'];saved=checkpoint.read_bytes()
   for direction in ['undo','redo']:
    result=f.invoke('draftHistory',dict(action=direction,token='stale-child-token'))['result']['result'];assert not result['accepted']and not result['changed'];assert checkpoint.read_bytes()==saved
   f.checked('sibling original CAS/checkpoint permission refusal preserve inputs and originals; retry/cold atomically retain only the new owned child body and existing shared OWNERSHIP_CHANGED boundary')
   r=review();r.locator('[data-reject]').click();untouched();r=review();saved=checkpoint.read_bytes();peer_file.write_bytes(raw+b' ')
   try:r.locator('#confirm').click();f.idle();assert peer_file.read_bytes()==raw+b' 'and checkpoint.read_bytes()==saved
   finally:peer_file.write_bytes(raw)
   if r.is_visible():r.locator('[data-reject]').click()
   r=review();saved=checkpoint.read_bytes();graph_path=f.project/t.graph_file;old_mode=stat.S_IMODE(graph_path.stat().st_mode);graph_path.chmod(0o400)
   try:r.locator('#confirm').click();f.idle();assert checkpoint.read_bytes()==saved and graph_path.read_bytes()==x.physical[graph_path];assert not[p for p in f.project.rglob('*.node.json')if p not in x.physical and '.confectory'not in p.parts]
   finally:graph_path.chmod(old_mode)
   if r.is_visible():r.locator('[data-reject]').click()
   if method:
    check_previous_insertion_reader(created, checkpoint)
   r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle()
   first_two='inserted-child\nbody' if at_start else 'body\ninserted-child'
   continuation = '\npeer-inner\npeer-tail\nafter\n10' if direct else '\nparent-tail\npeer-inner\npeer-tail\nafter\n10'
   expected = 'body\ninside\ninserted-child' + continuation if compound_parent else first_two+'\ninside'+continuation
   x.build('owned-child-insert',10,expected);assert all(p.read_bytes()==v for p,v in x.physical.items()if p.name!=t.graph_file);assert all(stat.S_IMODE(p.stat().st_mode)==m for p,m in source_modes.items());written=json.loads((f.project/t.graph_file).read_text());c=chosen(written);new=next(n for n in c['nodes']if n['id']==created)
   if at_start:
    assert c['entry']==created
    assert c['edges']==target['edges']+[edge(created,target['entry'])]
    c['entry']=target['entry']
   c['nodes'].remove(new);c['edges']=copy.deepcopy(chosen(base)['edges']);assert written==base;new_sources=[p for p in f.project.rglob('*.node.json')if p not in x.physical and '.confectory'not in p.parts];assert len(new_sources)==1 and json.loads(new_sources[0].read_text())['node']==created;resume(4);assert order()==inserted_order(created) and len(read(other)['nodes'])==2;f.checked('Review cancel/final sibling CAS and read-only graph preserve originals and missing new body; Confirm writes one graph insertion and one new local body, real execution returns 10 with parent/sibling continuation intact, and reopens')
   if compound_parent:
    check_confirmed_compound_workflow()
  doc().scroll_into_view_if_needed();f.page.screenshot(path=str(f.case/('child-insert-'+mode+'.png')),full_page=True);assert not f.errors and not f.external,(f.errors,f.external);f.browser.close()
except BaseException:
 if getattr(f,'page',None):
  try:(f.case/'child-insert-failure.html').write_text(f.page.content());f.page.screenshot(path=str(f.case/'child-insert-failure.png'),timeout=10000)
  except Exception:pass
 raise
finally:
 (f.case/'child-insert-traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False));(f.case/'child-insert-checks.json').write_text(json.dumps(f.checks,ensure_ascii=False));f.stop()
print('V821_CHILD_INSERT',mode,f.case,flush=True)
