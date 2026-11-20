"""Actual Linux editor/engine: exclusive switch cells, original returns and guards."""
import ast,copy,json,sys,time,uuid
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
import v666_root_execution_fixture as t
f=t.f;x=t;mode=sys.argv[3]if len(sys.argv)>3 else'normal'
helper_path=Path(__file__).with_name('v821_function_document_ui.py')
helpers=ast.parse(helper_path.read_text())
exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),str(helper_path),'exec'),globals())

graph=copy.deepcopy(t.root)
def cell(id,owner=None):
 return dict(id=id,kind='code',control='next',intent=id,signature=dict(args=[],**{'return':'void'}),arguments={},implementation=id+'.node.json',**({'branchOwner':owner}if owner else{}))
graph['nodes'] += [cell('a','choose'),cell('b','choose'),cell('continued')]
graph['edges']=[dict(**{'from':'choose','port':'next','to':'continued'}),dict(**{'from':'choose','port':'case:positive','to':'a'}),dict(**{'from':'choose','port':'case:negative','to':'exit:no'}),dict(**{'from':'a','port':'next','to':'b'}),dict(**{'from':'b','port':'next','to':'return:choose'}),dict(**{'from':'continued','port':'next','to':'exit:none'})]
bodies={'choose':t.original_source,'a':'global::System.Console.WriteLine("A");','b':'global::System.Console.WriteLine("B");','continued':'global::System.Console.WriteLine("continue");'}
if mode=='branch':
 # Same-case drag can preserve a root input binding. A case transfer cannot move this cell.
 bound=next(node for node in graph['nodes'] if node['id']=='b')
 bound['signature']['args']=[dict(type='long',name='amount')]
 bound['arguments']={'amount':{'input':'amount'}}
if mode=='dependency':
 graph['nodes'][1]['signature']['return']='int';graph['nodes'][2]['signature']['args']=[dict(type='int',name='value')];graph['nodes'][2]['arguments']={'value':{'node':'a'}}
 bodies['a']='global::System.Console.WriteLine("A");return 3;';bodies['b']='global::System.Console.WriteLine("B:"+value);'
if mode=='shared':next(e for e in graph['edges']if e['port']=='case:negative')['to']='a'
if mode=='fallback':graph['edges']=[e for e in graph['edges']if e['port']!='case:positive']+[dict(**{'from':'choose','port':'default','to':'a'})]
defs=f.metadata('featureBlueprintNodes',featureSource=t.function,graph=graph);assert defs['state']=='node-definitions',defs
for id,source in bodies.items():
 file='Flow.node.json'if id=='choose'else id+'.node.json'
 (f.project/file).write_text(json.dumps(dict(schema=1,node=id,definitionHash=next(n['definitionHash']for n in defs['nodes']if n['id']==id),source=source),ensure_ascii=False))
(f.project/'Flow.graph.json').write_text(json.dumps(graph,ensure_ascii=False))
(f.project/'MainBody.celem').write_text('implementation '+f.n+'MainBody for '+f.n+'Main () -> int {import '+t.feature+' as Flow (long) -> void;body common "Main.csbody";}')
(f.project/'Main.csbody').write_text('foreach(long amount in new long[]{1,-1}){calls.Flow.Invoke(amount);global::System.Console.WriteLine("main:"+amount);}return 7;')
t.physical={p:p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.parts}
def physical():return {p:p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.parts}
def branch(port='case:positive'):return doc().locator('[data-document-panel="'+port+'"]')
def order():return branch().locator('[data-document-cell]').evaluate_all('(els)=>els.map(e=>e.dataset.documentCell)')
def request(data,port='case:positive',terminal='return:choose'):
 return dict(action='authorBatch',documentBranch=True,id=t.graph,attempt=uuid.uuid4().hex,checkpointHash=data['checkpointHash'],sourceProof=t.proof(data),edits=[dict(action='route',node='choose',port=port,to='b'),dict(action='route',node='b',port='next',to='a'),dict(action='route',node='a',port='next',to=terminal)])
def source(id,text):
 doc().locator('[data-document-code="'+id+'"]').click();dialog=f.page.locator('.bp-script-dialog');body=dialog.locator('[data-code-region=body]').text_content();area=dialog.locator('[data-code-source]');area.evaluate('(el,text)=>{el.focus();const i=el.value.indexOf(text);if(i<0)throw Error("Body missing");el.setSelectionRange(i,i+text.length)}',body);f.page.keyboard.insert_text(text);dialog.locator('[data-code-save]').click();f.idle()
try:
 f.start(0);f.invoke('select',dict(id=t.feature));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
 with sync_playwright()as pw:
  expect.set_options(timeout=45000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':1900,'height':1500});open_document();baseline=t.read()
  expect(doc().locator('[data-document-cell=choose]')).to_be_visible();labels=doc().locator('[data-document-cell=choose] > .fd-cell-content > .fd-branches > .fd-branch-tabs [data-document-branch]').all_text_contents();assert labels==['Positive','Negative'],labels
  if mode=='history':
   branch().locator('[data-document-branch-add]').click();f.idle();created=next(n for n in order()if n.startswith('cell_'));doc().locator('.fd-document-title').click();doc().press('Control+z');expect(doc().locator('[data-document-cell="'+created+'"]')).to_have_count(0);assert not pending();doc().press('Control+y');expect(doc().locator('[data-document-cell="'+created+'"]')).to_be_visible();assert len(pending())==6
   save();assert not pending();history=f.invoke('draftHistory',dict(action='inspect'))['result']['result'];assert not history['undo']['available']and history['boundary']=='OWNERSHIP_CHANGED';t.original();restart(1);assert order()==[created,'a','b']and not pending();t.original();f.checked('private insertion Undo/Redo restores all six inputs; explicit Save and cold retain the existing ownership history boundary and unchanged physical originals')
  elif mode=='legacy':
   legacy=dict(action='authorBatch',id=t.graph,attempt=uuid.uuid4().hex,checkpointHash=baseline['checkpointHash'],sourceProof=t.proof(baseline),edits=[dict(action='createNode',node='legacy_cell',definition=dict(kind='code',control='next',intent='legacy typed cell',signature=dict(args=[dict(type='int',name='value')],**{'return':'void'}),branchOwner='choose')),dict(action='intent',node='legacy_cell',text='legacy typed cell'),dict(action='source',node='legacy_cell',text='global::System.Console.WriteLine(value);'),dict(action='argument',node='legacy_cell',name='value',valueJson='{"constant":5}'),dict(action='route',node='choose',port='case:negative',to='legacy_cell'),dict(action='route',node='legacy_cell',port='next',to='exit:yes')]);accepted=f.invoke('blueprint',legacy)['result']['result'];assert accepted['checkpointSaved'];t.original();restart(1);fresh=t.read();node=next(n for n in fresh['nodes']if n['id']=='legacy_cell');assert node['branchOwner']=='choose'and node['arguments'][0]['valueJson']=='{"constant":5}';t.original();f.checked('existing unflagged six-edit typed branch creation retains its original explicit API, source ownership and cold restore contract')
  elif mode in ['dependency','shared','fallback']:
   if mode=='dependency':branch().locator('[data-document-up=b]').click();f.idle();assert order()==['a','b']and not pending()
   else:
    if mode=='shared':expect(branch().locator('[data-document-up=b]')).to_be_disabled()
    expect(branch().locator('[data-document-branch-add]')).to_be_disabled()
   forged=request(baseline);f.invoke('blueprint',forged,False);assert checkpoint.read_bytes()==before and t.read()['edges']==baseline['edges'];t.original()
   doc().locator('[data-document-name=a]').fill('보존할 입력 α 😀');held=pending();expect(doc().locator('[data-document-down=a]')).to_be_disabled();restart(1);assert pending()==held;t.original();assert checkpoint.read_bytes()==before
   f.checked('unsafe '+mode+' branch order is refused by UI and source-bound engine candidate; unrelated private input survives cold without live/checkpoint/original mutation')
  else:
   assert order()==['a','b'];branch().locator('[data-document-up=b]').click();f.idle();assert order()==['b','a'];held=pending();assert len(held)==3;t.original()
   doc().locator('.fd-document-title').click();doc().press('Control+z');assert order()==['a','b'];doc().press('Control+y');assert order()==['b','a']
   panel().get_by_role('tab',name='블루프린트 보기',exact=True).click();expect(panel().locator('[data-bp-node=a]')).to_be_visible();panel().get_by_role('tab',name='논리 코드',exact=True).click();restart(1);assert pending()==held and order()==['b','a'];t.original()
   checkpoint.chmod(0o400)
   try:save();assert retained(held)and checkpoint.read_bytes()==before and t.read()['edges']==baseline['edges'];t.original()
   finally:checkpoint.chmod(0o600)
   save();assert not pending();saved=t.read()
   for direction,wanted in [('undo',baseline['edges']),('redo',saved['edges'])]:
    h=f.invoke('draftHistory',dict(action='inspect'))['result']['result'];assert h[direction]['available'];assert f.invoke('draftHistory',dict(action=direction,token=h[direction]['token']))['result']['result']['accepted'];assert t.read()['edges']==wanted
   f.invoke('saveDraft',{});restart(2);assert order()==['b','a'];t.original();f.checked('one branch reorder preserves enum/owner/return and other paths; private/shared Undo/Redo, cold and checkpoint permission failure retain exact state')
   current=t.read()
   for forged in [request(current,'case:negative'),request(current,terminal='exit:yes')]:
    previous=checkpoint.read_bytes();f.invoke('blueprint',forged,False);assert checkpoint.read_bytes()==previous and t.read()['edges']==current['edges'];t.original()
   forged=dict(action='authorBatch',documentBranch=True,id=t.graph,attempt=uuid.uuid4().hex,checkpointHash=current['checkpointHash'],sourceProof=t.proof(current),edits=[dict(action='createNode',node='forged_cell',definition=dict(kind='code',control='next',intent='forged',signature=dict(args=[],**{'return':'void'}),branchOwner='choose')),*[dict(action=a,node='forged_cell',text='return;'if a=='source'else'forged')for a in ['rename','intent','source']],dict(action='route',node='choose',port='case:negative',to='forged_cell'),dict(action='route',node='forged_cell',port='next',to='exit:yes')]);previous=checkpoint.read_bytes();f.invoke('blueprint',forged,False);assert checkpoint.read_bytes()==previous and t.read()['edges']==current['edges'];t.original()
   f.invoke('blueprint',dict(action='serialRoutes',id=t.graph,basis=current['basis'],routes=request(current)['edits']),False);assert checkpoint.read_bytes()==previous and t.read()['edges']==current['edges'];t.original()
   f.checked('changing branch identity or its original continuation is refused before any candidate is checkpointed')
   r=review();r.locator('[data-reject]').click();t.original();r=review();path=f.project/'Flow.graph.json';raw=path.read_bytes();saved_checkpoint=checkpoint.read_bytes();path.write_bytes(raw+b' ')
   try:r.locator('#confirm').click();f.idle();assert path.read_bytes()==raw+b' 'and checkpoint.read_bytes()==saved_checkpoint
   finally:path.write_bytes(raw)
   if r.is_visible():r.locator('[data-reject]').click()
   r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();t.build('branch-order',7,'callee:1\nB\nA\ncontinue\nmain:1\ncallee:-1\nmain:-1');assert all(p.read_bytes()==raw for p,raw in t.physical.items()if p!=path);confirmed=physical();restart(3)
   f.checked('fresh Confirm executes reordered positive cells then the original continuation; negative exit and all existing C# declarations/bodies stay unchanged')
   # The initially empty negative branch keeps its original early exit.
   doc().locator('[data-document-branch="case:negative"]').click();branch('case:negative').locator('[data-document-branch-add]').click();f.idle();created=[n for n in branch('case:negative').locator('[data-document-cell]').evaluate_all('(els)=>els.map(e=>e.dataset.documentCell)')if n.startswith('cell_')];assert len(created)==1;created=created[0]
   doc().locator('.fd-document-title').click();doc().press('Control+z');expect(doc().locator('[data-document-cell="'+created+'"]')).to_have_count(0);doc().press('Control+y');expect(doc().locator('[data-document-cell="'+created+'"]')).to_be_visible()
   source(created,'global::System.Console.WriteLine("negative");\nreturn;');held=pending();assert len(held)==6;restart(4);assert pending()==held;assert physical()==confirmed
   save();assert not pending();history=f.invoke('draftHistory',dict(action='inspect'))['result']['result'];assert not history['undo']['available'] and history['boundary']=='OWNERSHIP_CHANGED';r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();t.build('branch-empty-insert',7,'callee:1\nB\nA\ncontinue\nmain:1\ncallee:-1\nnegative\nmain:-1');assert all(p.read_bytes()==raw for p,raw in confirmed.items()if p!=path);written=json.loads(path.read_text());made=next(n for n in written['nodes']if n['id']==created);assert made['branchOwner']=='choose';assert next(e['to']for e in written['edges']if e['from']==created)=='exit:no';confirmed=physical();restart(5)
   f.checked('empty branch insertion and protected C# editing survive cold and atomically Confirm; original early exit, ownership and existing sources remain intact')
   doc().locator('[data-document-branch="case:positive"]').click();branch().locator('[data-document-add=b]').click();f.idle();created=next(n for n in order()if n.startswith('cell_'));source(created,'global::System.Console.WriteLine("inserted");\nreturn;');save();assert not pending();r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();t.build('branch-inner-insert',7,'callee:1\nB\ninserted\nA\ncontinue\nmain:1\ncallee:-1\nnegative\nmain:-1');assert all(p.read_bytes()==raw for p,raw in confirmed.items()if p!=path);restart(6);assert order()==['b',created,'a']
   f.checked('insertion inside an existing branch executes only on that branch and returns to the original continuation; saved graph and legacy view agree after cold')
  f.page.screenshot(path=str(f.case/('branch-structure-'+mode+'.png')),full_page=True);assert not f.errors and not f.external,(f.errors,f.external);f.browser.close()
except BaseException:
 if getattr(f,'page',None):
  try:(f.case/'branch-failure.html').write_text(f.page.content());(f.case/'branch-errors.json').write_text(json.dumps(f.errors,ensure_ascii=False));f.page.screenshot(path=str(f.case/'branch-failure.png'),timeout=10000)
  except Exception:pass
 raise
finally:
 (f.case/'branch-traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False));(f.case/'branch-checks.json').write_text(json.dumps(f.checks,ensure_ascii=False));f.stop()
print('V821_BRANCH_STRUCTURE',mode,f.case,flush=True)
