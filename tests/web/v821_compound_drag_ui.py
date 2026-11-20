"""Actual desktop mouse drag of whole compound calls over the existing order contract."""
import ast,copy,json,stat,sys,time,uuid
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
import v666_node_names_recovery_fixture as t
f=t.f;x=t.x;mode=sys.argv[3]if len(sys.argv)>3 else'normal'
helper=Path(__file__).with_name('v821_function_document_ui.py')
exec(compile(ast.Module(body=[n for n in ast.parse(helper.read_text()).body if isinstance(n,ast.FunctionDef)],type_ignores=[]),str(helper),'exec'),globals())
def edge(a,b):return {'from':a,'port':'next','to':b}
def code(id,args,ret,file,arguments={}):return dict(id=id,kind='code',control='next',intent=id,signature=dict(args=args,**{'return':ret}),arguments=arguments,implementation=file)
def child(nodes,exits):return dict(schema=1,profile='sync-acyclic-nested-v1',entry=nodes[0]['id'],nodes=nodes,edges=[edge(n['id'],nodes[i+1]['id']if i+1<len(nodes)else'exit:return')for i,n in enumerate(nodes)],exits=exits)
base=copy.deepcopy(t.definition);base['profile']='sync-acyclic-nested-v1'
body=base['nodes'][0];body.pop('implementation');body['kind']='graph';body['graph']=child([code('inner',[dict(name='amount',type='int')],'int','Pair.inner.node.json',{'amount':{'input':'amount'}}),code('tail',[],'void','Pair.tail.node.json')],{'return':{'node':'inner'}})
other=dict(id='other',kind='graph',control='next',intent='other compound',signature=dict(args=[],**{'return':'void'}),arguments={},graph=child([code('inner',[],'void','Pair.other.node.json')],{'return':None}))
if mode=='dependency':
 other['signature']['args']=[dict(name='value',type='int')];other['arguments']={'value':{'node':'body'}}
base['nodes'].insert(1,other);base['edges']=[edge('body','other'),edge('other','after'),edge('after','exit:return')]
if mode=='shared':
 base['profile']='sync-acyclic-switch-v1';base['entry']='choose';other['branchOwner']='choose'
 choose=code('choose',[],'void','Pair.choose.node.json');choose['control']='switch';choose['executionEnum']={'primary':'next','members':[{'id':'next','name':'None','value':0},{'id':'positive','name':'Positive','value':1},{'id':'negative','name':'Negative','value':2}]};base['nodes'].insert(0,choose)
 base['edges']=[edge('choose','body'),edge('body','after'),edge('after','exit:return'),{'from':'choose','port':'case:positive','to':'other'},{'from':'choose','port':'case:negative','to':'other'},edge('other','return:choose')]
(f.project/t.graph_file).write_text(json.dumps(base,ensure_ascii=False))
defs=f.metadata('blueprintDescribeOwned',project=str(f.manifest),id=f.n+'PairBody',text=(f.project/'PairBody.celem').read_text(),bodyTarget='common',graph=base,definitionsOnly=True);assert defs['state']=='node-definitions',defs
sources={'body/inner':('Pair.inner.node.json','global::System.Console.WriteLine("body");\r\nreturn '+'checked(amount+3);'),'body/tail':('Pair.tail.node.json','global::System.Console.WriteLine("inside");'),'other/inner':('Pair.other.node.json','global::System.Console.WriteLine("other");')}
if mode=='shared':sources['choose']=('Pair.choose.node.json','return Result.Positive;')
for key,(file,source)in sources.items():
 definition=next(n for n in defs['nodes']+defs['nestedNodes']if n['id']==key)
 (f.project/file).write_text(json.dumps(dict(schema=1,node=key.split('/')[-1],definitionHash=definition['definitionHash'],source=source),ensure_ascii=False))
# The existing ordinary leaf keeps its original source and newly observed identity.
after=f.project/'Pair.after.node.json';record=json.loads(after.read_text());record['definitionHash']=next(n['definitionHash']for n in defs['nodes']if n['id']=='after');after.write_text(json.dumps(record,ensure_ascii=False))
(f.project/t.graph_file).write_text(json.dumps(base,ensure_ascii=False));x.physical={p:p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.parts}
def order():return doc().locator('[data-document-cell]').evaluate_all('(els)=>els.map(e=>e.dataset.documentCell)')
def request(data,ids=['other','body','after']):return dict(action='authorBatch',documentCompound=True,id=t.graph,attempt=uuid.uuid4().hex,checkpointHash=data['checkpointHash'],sourceProof=x.proof(data),edits=[dict(action='entry',node='$entry',to=ids[0])]+[dict(action='route',node=n,port='next',to=ids[i+1]if i+1<len(ids)else'exit:return')for i,n in enumerate(ids)])
def untouched():
 x.original();assert all(stat.S_IMODE(p.stat().st_mode)==m for p,m in source_modes.items())
def subtree():return {n['id']:copy.deepcopy(n)for n in base['nodes']}
# Load helpers only: no ordinary fixture setup or test body executes here.
helper=Path(__file__).with_name('v821_cell_drag_ui.py');exec(compile(ast.Module(body=[n for n in ast.parse(helper.read_text()).body if isinstance(n,ast.FunctionDef)],type_ignores=[]),str(helper),'exec'),globals())
source_modes={p:stat.S_IMODE(p.stat().st_mode)for p in x.physical}
try:
 f.start(0);f.invoke('select',dict(id=t.feature));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
 with sync_playwright()as pw:
  expect.set_options(timeout=45000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size(dict(width=1800,height=1400));open_document();enlarge();original=t.read();initial=order();folded()
  if mode=='shared':
   assert original['documentCompoundOrderAvailable']is False
   expect(doc().locator('[data-document-up=other]')).to_be_disabled()
   assert doc().locator('[data-document-branch]').all_text_contents()==['Positive','Negative'];expect(grip('other')).to_be_disabled();move('other','body',valid=False,disabled=True);assert order()==initial and not pending()
  else:
   assert original['documentCompoundOrderAvailable']is True
   if mode=='dependency':
    move('other','body',valid=False);assert order()==initial and not pending()
   else:
    # Move the complete body invocation down, then the other invocation up.
    move('body','other',after=True,capture=True);wait_order(['other','body','after']);assert len(pending())==4;untouched();assert checkpoint.read_bytes()==before
    local_undo();wait_order(['body','other','after']);local_undo(True);wait_order(['other','body','after']);local_undo();wait_order(['body','other','after'])
    move('other','body');wait_order(['other','body','after']);local_undo();wait_order(['body','other','after']);assert not pending()
    start_drag('other');hover('body');expect(f.page.locator('.fd-cell-drop-marker')).to_have_count(1);f.page.keyboard.press('Escape');f.page.mouse.up();wait_order(['body','other','after']);assert not pending()
    start_drag('other');r=panel().locator('.window-title').bounding_box();f.page.mouse.move(r['x']+20,r['y']+8,steps=10);f.page.mouse.up();wait_order(['body','other','after']);assert not pending()
    move('other','other',valid=False);assert not pending();untouched();assert checkpoint.read_bytes()==before
    grip('other').focus();f.page.keyboard.press('Alt+ArrowUp');f.idle();wait_order(['other','body','after']);local_undo();wait_order(['body','other','after'])
    cell('other').locator('[data-document-fold]').click();up=doc().locator('[data-document-up=other]');expect(up).to_be_visible();up.focus();f.page.keyboard.press('Enter');f.idle();wait_order(['other','body','after']);local_undo();wait_order(['body','other','after']);folded()
    move('body','other',after=True);wait_order(['other','body','after']);assert t.read()['nodes']==original['nodes']
    f.checked('actual mouse moves complete compound calls up/down with one private order record; Escape/outside/self cancel, original button Enter and grip Alt arrows preserve every descendant and adjacent source')
  if mode!='normal':
   assert order()==initial and not pending();untouched();assert checkpoint.read_bytes()==before
   doc().locator('[data-document-name=after]').fill('보존할 입력 α');doc().locator('.fd-document-title').click();held=pending();assert held
   forged=request(original);f.invoke('blueprint',forged,False);assert checkpoint.read_bytes()==before;assert pending()==held;assert t.read()['entry']==original['entry'];untouched()
   restart(1);assert pending()==held;expect(doc().locator('[data-document-name=after]')).to_have_value('보존할 입력 α');assert order()==initial;untouched()
   if mode=='shared':x.build('compound-shared-unchanged',10,'other\nbody\ninside\nafter\n10');untouched()
   f.checked('unsupported shared/branch compound or producer-before-consumer move rejects UI/backend and preserves exact unsaved input through cold restart')
  else:
   assert order()==['$entry','other','body','after','$exit:return'];held=pending();assert len(held)==4;assert checkpoint.read_bytes()==before;untouched()
   doc().locator('.fd-document-title').click();doc().press('Control+z');assert order()==initial;doc().press('Control+y');assert order()[1]=='other'
   # Existing inner navigation uses the qualified frame. No move/add authority leaks inside.
   cell('body').locator('[data-document-fold]').click();doc().locator('[data-document-internal=body]').click();f.idle();expect(doc().locator('[data-document-cell=inner]')).to_be_visible();expect(doc().locator('[data-document-up=tail]')).to_be_disabled();expect(grip('inner')).to_be_disabled();expect(grip('tail')).to_be_disabled();expect(doc().locator('[data-document-add=inner]')).to_be_disabled();assert not f.invoke('blueprint',dict(action='read',id=t.graph+'/graph:body'))['result']['result']['documentCompoundOrderAvailable']
   panel().locator('.bp-breadcrumbs button').first.click();f.idle();assert pending()==held and order()[1]=='other'
   panel().get_by_role('tab',name='블루프린트 보기',exact=True).click();expect(panel().locator('[data-bp-node=body]')).to_be_visible();panel().get_by_role('tab',name='논리 코드',exact=True).click();restart(1);assert pending()==held and order()[1]=='other';untouched()
   f.checked('compound move stays one invocation with unchanged descendant sources, frame navigation, private Undo/Redo, legacy view and cold input recovery')
   for mutation in ['unflagged','frame','exit','drop','body','owner','stale-proof','stale-checkpoint','mixed-intent']:
    q=request(original)
    if mutation=='unflagged':q.pop('documentCompound')
    elif mutation=='frame':q['id']=t.graph+'/graph:body'
    elif mutation=='exit':q['edits'][-1]['to']='exit:missing'
    elif mutation=='drop':q['edits']=q['edits'][:-1]
    elif mutation=='body':q['edits'].append(dict(action='source',node='body',text='return;'))
    elif mutation=='owner':q.update(owner=f.n+'Missing',ownerHash='0'*64)
    elif mutation=='stale-proof':q['sourceProof']='[]'
    elif mutation=='stale-checkpoint':q['checkpointHash']='0'*64
    else:q['documentBranch']=True
    f.invoke('blueprint',q,False);assert checkpoint.read_bytes()==before and pending()==held;assert t.read()['entry']==original['entry'];untouched()
   f.invoke('blueprint',dict(action='serialRoutes',id=t.graph,basis=original['basis'],routes=request(original)['edits']),False);assert checkpoint.read_bytes()==before;untouched()
   f.checked('scope/owner/exit/source/intent/checkpoint forgeries and direct serialRoutes are rejected without mutation')
   checkpoint.chmod(0o400)
   try:save();assert retained(held)and checkpoint.read_bytes()==before and t.read()['entry']==original['entry'];untouched()
   finally:checkpoint.chmod(0o600)
   save();assert not pending();assert t.read()['entry']=='other';untouched()
   for direction,wanted in [('undo','body'),('redo','other')]:
    history=f.invoke('draftHistory',dict(action='inspect'))['result']['result'];assert history[direction]['available'];assert f.invoke('draftHistory',dict(action=direction,token=history[direction]['token']))['result']['result']['accepted'];assert t.read()['entry']==wanted;untouched()
   f.invoke('saveDraft',{});restart(2);assert order()[1]=='other'and not pending()
   f.checked('atomic checkpoint permission failure/retry and shared Undo/Redo preserve compound membership, contracts and cold saved order')
   r=review();r.locator('[data-reject]').click();untouched();r=review();path=f.project/t.graph_file;raw=path.read_bytes();saved=checkpoint.read_bytes();path.write_bytes(raw+b' ')
   try:r.locator('#confirm').click();f.idle();assert path.read_bytes()==raw+b' 'and checkpoint.read_bytes()==saved
   finally:path.write_bytes(raw)
   if r.is_visible():r.locator('[data-reject]').click()
   r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();x.build('compound-order',10,'other\nbody\ninside\nafter\n10');assert all(p.read_bytes()==raw for p,raw in x.physical.items()if p!=path);written=json.loads(path.read_text());assert {n['id']:n for n in written['nodes']}==subtree();assert written['exits']==base['exits'];restart(3);assert order()[1]=='other'and not pending()
   assert all(stat.S_IMODE(p.stat().st_mode)==m for p,m in source_modes.items())
   f.checked('Review cancellation/final CAS preserve originals; Confirm changes only parent routes and real rebuilt execution preserves child return and continuation')
   doc().locator('[data-document-name=after]').fill('복합 이동 뒤 입력 보존 α');doc().locator('.fd-document-title').click();held=pending();expect(grip('body')).to_be_disabled();folded();move('body','other',valid=False,disabled=True);assert pending()==held;restart(4);assert pending()==held;expect(doc().locator('[data-document-name=after]')).to_have_value('복합 이동 뒤 입력 보존 α');assert {n['id']:n for n in json.loads(path.read_text())['nodes']}==subtree()
  f.page.screenshot(path=str(f.case/('compound-drag-'+mode+'.png')),full_page=True);assert not f.errors and not f.external,(f.errors,f.external);f.browser.close()
except BaseException:
 if getattr(f,'page',None):
  try:(f.case/'compound-failure.html').write_text(f.page.content());(f.case/'compound-errors.json').write_text(json.dumps(f.errors,ensure_ascii=False));f.page.screenshot(path=str(f.case/'compound-failure.png'),timeout=10000)
  except Exception:pass
 raise
finally:
 (f.case/'compound-traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False));(f.case/'compound-checks.json').write_text(json.dumps(f.checks,ensure_ascii=False));f.stop()
print('V821_COMPOUND_DRAG',mode,f.case,flush=True)
