"""Vertical document cells over real engine metadata, private inputs and Save/CAS.

Linux Chromium and .NET only. No mockup visual equivalence or Windows claim.
"""
import ast,copy,json,pathlib,sys,time,traceback,uuid
from playwright.sync_api import sync_playwright,expect

mode=sys.argv[3] if len(sys.argv)>3 else 'normal'
if mode=='branches':
 import v666_root_execution_fixture as t
 x=t;f=t.f
else:
 import v666_node_names_recovery_fixture as t
 x=t.x;f=t.f

def panel():return f.author()
def doc():return panel().locator('.function-document')
def pending():return f.pending()['blueprint']
def open_document():
 f.idle()
 if not panel().is_visible() or not doc().count():
  f.page.locator('#workspace').click(button='right',position={'x':1300,'y':300});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click()
  b=f.page.locator('.window[data-key^="browser:project:"]');b.get_by_role('button',name='기능',exact=True).click();b.locator('[data-browser-control=object-query]').fill(t.feature.split('::')[-1]);b.locator('[data-browser-control=object-search]').click();b.locator('[data-object="'+t.feature+'"]').press('Enter');b.locator('[data-close]').first.click();f.idle();f.page.locator('[data-operation=feature-author-open]').first.click()
 expect(doc()).to_be_visible()
def restart(i):
 f.pending();f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});f.idle();open_document()
def save():
 mark=len(f.traffic);panel().locator('[data-bp-save]').click();deadline=time.monotonic()+120
 while time.monotonic()<deadline:
  requests={r['invoke']['requestId']for r in f.traffic[mark:]if r.get('invoke',{}).get('endpoint')=='blueprint'and r['invoke'].get('input',{}).get('action')in ['authorBatch','settledAuthorBatch']}
  if requests and any(r.get('result',{}).get('requestId')in requests for r in f.traffic[mark:]):break
  f.page.wait_for_timeout(25)
 else:raise AssertionError('No source-bound atomic Save request/result within deadline')
 f.idle();expect(panel().locator('.bp-status')).not_to_have_text('저장 중…',timeout=120000)
 assert not any(r.get('invoke',{}).get('endpoint')=='blueprint'and r['invoke'].get('input',{}).get('action')in ['argument','rename']for r in f.traffic[mark:]),'serial live edits are forbidden for document name/value Save'
 return f.traffic[mark:]
def retained(held):return all(dict(pending()).get(key)==value for key,value in held)
def review():
 panel().locator('[data-bp-complete]').click();f.idle()
 if f.page.locator('#review-creation').is_visible():f.page.locator('#review-creation').click();f.idle()
 f.page.locator('.window[data-key=review]:visible,.window[data-key=targets]:visible').first.wait_for(state='visible',timeout=90000);targets=f.page.locator('.window[data-key=targets]')
 if targets.is_visible():targets.locator('[data-target-choice]').select_option('portable');targets.locator('[data-close]').click();panel().locator('[data-bp-complete]').click();f.idle()
 r=f.page.locator('.window[data-key=review]');expect(r).to_be_visible(timeout=90000)
 if r.locator('[data-review-advanced]').is_visible():r.locator('[data-review-advanced]').click()
 if r.locator('[data-advanced-reviewed]').count():r.locator('[data-advanced-reviewed]').check()
 return r
def literal(text):
 doc().locator('[data-document-value=body][data-document-port="field:amount"]').click();q=f.page.get_by_role('dialog',name='핀 값 선택').get_by_role('searchbox',name='값 검색');q.fill(text);q.press('Enter')

try:
 f.start(0);f.invoke('select',{'id':t.feature});f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
 with sync_playwright() as pw:
  expect.set_options(timeout=45000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});open_document()
  try:
   baseline=t.read();x.original();assert not pending();expect(panel().get_by_role('tab',name='논리 코드',exact=True)).to_have_attribute('aria-selected','true')
   if mode=='branches':
    cell=doc().locator('[data-document-cell=choose]');names=cell.locator('.fd-branch-tabs [data-document-branch]').all_text_contents();assert names==['Positive','Negative'],names
    cell.get_by_role('button',name='분기 내용 접기',exact=True).click();expect(cell.locator('.fd-branch-tabs')).to_be_visible();expect(cell.locator('.fd-branch-panel').first).to_be_hidden()
    cell.locator('[data-document-fold=choose]').click();expect(cell.locator('.fd-branch-tabs')).to_be_hidden();expect(cell.locator('>.fd-cell-header .fd-cell-title')).to_be_visible()
    restart(1);cell=doc().locator('[data-document-cell=choose]');expect(cell.locator('.fd-cell-content').first).to_be_hidden();cell.locator('[data-document-fold=choose]').click();expect(cell.locator('.fd-branch-tabs')).to_be_visible();expect(cell.locator('.fd-branch-panel').first).to_be_hidden()
    assert not pending() and checkpoint.read_bytes()==before;t.read();x.original();x.build('vertical-branches',t.result_code,t.initial_stdout);f.checked('real execution-enum branch names and nested fold states survive cold without source, draft or execution changes')
   else:
    assert doc().locator('[data-document-cell]').evaluate_all('(els)=>els.map(e=>e.dataset.documentCell)')==['$entry','body','after','$exit:return']
    first=doc().locator('[data-document-cell=body]');left=first.locator('.fd-inputs').bounding_box();right=first.locator('.fd-outputs').bounding_box();assert left['x']+left['width']<right['x'];first.locator('[data-document-fold=body]').click()
    panel().get_by_role('tab',name='블루프린트 보기',exact=True).click();expect(panel().locator('.bp-viewport')).to_be_visible();positions=panel().locator('[data-bp-node=body]').get_attribute('style')
    panel().get_by_role('tab',name='논리 코드',exact=True).click();expect(first.locator('.fd-cell-content')).to_be_hidden();first.locator('[data-document-fold=body]').click();assert not pending();assert checkpoint.read_bytes()==before;assert t.read()['nodes']==baseline['nodes'];x.original()
    f.checked('real graph defaults to vertical next order and left/right pins; fold/view switches preserve graph, checkpoint, inputs and native sources')
    # Bound the new atomic classifier: no other node/frame or unknown field.
    template=dict(action='authorBatch',id=t.graph,checkpointHash=baseline['checkpointHash'],sourceProof=x.proof(baseline),edits=[dict(action='rename',node='body',text='not-applied'),dict(action='argument',node='body',name='amount',valueJson='{"constant":9}')])
    for kind in ['other-node','unknown-argument','other-frame']:
     request=copy.deepcopy(template);request['attempt']=uuid.uuid4().hex
     if kind=='other-node':request['edits'][1]['node']='after'
     elif kind=='unknown-argument':request['edits'][1]['name']='not-owned'
     else:request['edits'][1]['frame']=t.graph+'/graph:body'
     f.invoke('blueprint',request,False);assert checkpoint.read_bytes()==before and t.read()['nodes']==baseline['nodes'];x.original()
    f.checked('atomic name/value guard rejects other node/frame and unknown argument without live, checkpoint or original changes')
    doc().locator('[data-document-code=body]').click();dialog=f.page.locator('.bp-script-dialog');expect(dialog.locator('[data-code-source]')).to_be_visible();assert 'amount+3' in dialog.locator('[data-code-source]').input_value();dialog.locator('[data-code-cancel]').click();assert not pending();x.original()
    literal('9');name='문서 계산 α 😀';first.locator('[data-document-name=body]').fill(name);doc().locator('.fd-document-title').click();held=pending();assert len(held)==2,held
    panel().get_by_role('tab',name='블루프린트 보기',exact=True).click();expect(panel().locator('[data-bp-node=body] [data-bp-node-name]')).to_have_text(name);assert panel().locator('[data-bp-node=body]').get_attribute('style')==positions
    panel().get_by_role('tab',name='논리 코드',exact=True).click();restart(1);assert pending()==held;x.original();assert checkpoint.read_bytes()==before;expect(doc().locator('[data-document-name=body]')).to_have_value(name);expect(doc().locator('[data-document-value=body][data-document-port="field:amount"]')).to_have_text('9')
    f.checked('document edits share the original graph draft and retain exact pending name/value across view switches and cold restart')
    if mode=='storage':
     checkpoint.chmod(0o400)
     try:
      save();assert retained(held) and checkpoint.read_bytes()==before;assert t.read()['nodes']==baseline['nodes'];x.original();(f.case/'failed-save-inputs.json').write_text(json.dumps(pending(),ensure_ascii=False))
     finally:checkpoint.chmod(0o600)
     restart(2);assert retained(held);f.checked('failed checkpoint write keeps both document inputs, original bytes and cold recovery')
    save();expect(panel().locator('.bp-status')).to_have_text('저장됨');assert not pending();data=t.read();body=next(n for n in data['nodes']if n['id']=='body');assert body['displayName']==name;assert body['arguments'][0]['valueJson']=='{"constant":9}',body;x.original()
    saved_nodes=data['nodes']
    for direction,wanted in [('undo',baseline['nodes']),('redo',saved_nodes)]:
     h=f.invoke('draftHistory',{'action':'inspect'})['result']['result'];assert h[direction]['available'];assert f.invoke('draftHistory',{'action':direction,'token':h[direction]['token']})['result']['result']['accepted'];assert t.read()['nodes']==wanted;x.original()
    f.invoke('saveDraft',{});restart(3);assert not pending();expect(doc().locator('[data-document-name=body]')).to_have_value(name)
    f.checked('one explicit Save atomically checkpoints document name/value; cold restore preserves source/ABI and has no private inputs')
    r=review();r.locator('[data-reject]').click();x.original();r=review();path=f.project/t.graph_file;raw=path.read_bytes();checkpoint_before=checkpoint.read_bytes();path.write_bytes(raw+b' ')
    try:r.locator('#confirm').click();f.idle();assert path.read_bytes()==raw+b' ' and checkpoint.read_bytes()==checkpoint_before;assert all(p.read_bytes()==v for p,v in x.physical.items()if p!=path)
    finally:path.write_bytes(raw)
    if r.is_visible():r.locator('[data-reject]').click()
    r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();assert all(p.read_bytes()==v for p,v in x.physical.items()if p!=path);written=json.loads(path.read_text());assert next(n for n in written['nodes']if n['id']=='body')['arguments']['amount']=={'constant':9};x.build('vertical-confirm',12,'body\nafter\n12');restart(4);assert not pending();f.checked('Review cancel and final CAS refuse stale original; fresh Confirm executes actual .NET result 12 with all other originals/ABI unchanged')
   f.page.screenshot(path=str(f.case/'document-engine.png'),timeout=10000,full_page=True);assert not f.errors and not f.external,(f.errors,f.external)
  except Exception:
   f.page.screenshot(path=str(f.case/'failure.png'),timeout=10000);(f.case/'failure.html').write_text(f.page.content());(f.case/'failure.json').write_text(json.dumps(dict(pending=pending(),errors=f.errors,traffic=f.traffic[-25:]),ensure_ascii=False));raise
  f.browser.close()
finally:
 (f.case/'checks.json').write_text(json.dumps(dict(checks=f.checks,actualEngine=True,actualLinux=True,actualWindows=False,fullUI=False,mockupVisualCompared=False),ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False));f.stop()
print('V821_DOCUMENT_ENGINE',f.case,flush=True)
