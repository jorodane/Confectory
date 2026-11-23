"""Actual Linux editor/engine: full-path owned ordinary child frame order only."""
import ast,copy,json,os,re,stat,sys,time,uuid
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
import v666_node_names_recovery_fixture as t
f=t.f;x=t.x;mode=sys.argv[3]if len(sys.argv)>3 else'normal'
method = mode.startswith('method-')
compound_parent = mode in ('method-compound-parent', 'method-compound-order', 'method-compound-dependency', 'method-compound-shared')
compound_dependency = mode == 'method-compound-dependency'
direct = mode == 'method-direct'
too_deep = mode == 'method-deep'
success = mode in ('normal', 'method-direct', 'method-nested', 'method-compound-order')
dependency = mode in ('dependency', 'method-dependency')
unavailable = mode in ('shared', 'method-shared', 'method-deep', 'method-compound-shared')
helper=Path(__file__).with_name('v821_function_document_ui.py')
exec(compile(ast.Module(body=[n for n in ast.parse(helper.read_text()).body if isinstance(n,ast.FunctionDef)],type_ignores=[]),str(helper),'exec'),globals())
def edge(a,b):return {'from':a,'port':'next','to':b}
def signature(args=[],ret='void'):return dict(args=args,**{'return':ret})
def code(id,file,sig=None,args={}):return dict(id=id,kind='code',control='next',intent=id,signature=sig or signature(),arguments=args,implementation=file)
def child(nodes,exits):return dict(schema=1,profile='sync-acyclic-nested-v1',entry=nodes[0]['id'],nodes=nodes,edges=[edge(n['id'],nodes[i+1]['id']if i+1<len(nodes)else'exit:return')for i,n in enumerate(nodes)],exits=exits)
def compound(id,graph,sig=None,args={}):return dict(id=id,kind='graph',control='next',intent=id,signature=sig or signature(),arguments=args,graph=graph)
amount=[dict(name='amount',type='int')];target=child([code('inner','Pair.body.inner.node.json',signature(amount,'int'),{'amount':{'input':'amount'}}),code('tail','Pair.body.tail.node.json')],{'return':{'node':'inner'}})
if dependency:target['nodes'][1].update(signature=signature([dict(name='value',type='int')]),arguments={'value':{'node':'inner'}})
peer=child([code('inner','Pair.peer.inner.node.json'),code('tail','Pair.peer.tail.node.json')],{'return':None})
base=copy.deepcopy(t.definition);base['profile']='sync-acyclic-nested-v1';body=base['nodes'][0];body.pop('implementation');body['kind']='graph';body['graph']=child([compound('nest',target,signature(amount,'int'),{'amount':{'input':'amount'}}),code('finish','Pair.finish.node.json')],{'return':{'node':'nest'}})
base['nodes'].insert(1,compound('other',child([compound('nest',peer)],{'return':None})));base['edges']=[edge('body','other'),edge('other','after'),edge('after','exit:return')]
sources={'body/nest/inner':('Pair.body.inner.node.json','global::System.Console.WriteLine("body");\r\nreturn checked(amount+3);'),'body/nest/tail':('Pair.body.tail.node.json','global::System.Console.WriteLine("inside");'),'body/finish':('Pair.finish.node.json','global::System.Console.WriteLine("parent-tail");'),'other/nest/inner':('Pair.peer.inner.node.json','global::System.Console.WriteLine("peer-inner");'),'other/nest/tail':('Pair.peer.tail.node.json','global::System.Console.WriteLine("peer-tail");')}
if compound_parent:
 sibling = base['nodes'][1]['graph']
 sibling['nodes'].append(code('finish', 'Pair.peer.finish.node.json'))
 sibling['edges'] = [edge('nest', 'finish'), edge('finish', 'exit:return')]
 sources['other/finish'] = ('Pair.peer.finish.node.json', 'return;')
if compound_dependency:
 finish = body['graph']['nodes'][1]
 finish.update(signature=signature([dict(name='value', type='int')]), arguments={'value': {'node': 'nest'}})
 sources['body/finish'] = ('Pair.finish.node.json', 'global::System.Console.WriteLine("parent-tail:" + value);')
if method:
 target['profile'] = peer['profile'] = 'sync-acyclic-methods-v1'
if direct:
 body['graph'] = target
 base['nodes'][1]['graph'] = peer
 del sources['body/finish']
 sources = {path.replace('/nest/', '/'): source for path, source in sources.items()}
if too_deep:
 middle = compound('middle', body['graph'], signature(amount, 'int'), {'amount': {'input': 'amount'}})
 body['graph'] = child([middle], {'return': {'node': 'middle'}})
 sources = {path.replace('body/', 'body/middle/', 1): source for path, source in sources.items()}
if mode=='shared':
 base['profile']='sync-acyclic-switch-v1';base['entry']='choose';body['branchOwner']='choose';base['exits']['return']={'constant':10};choose=code('choose','Pair.choose.node.json');choose['control']='switch';choose['executionEnum']={'primary':'next','members':[dict(id='next',name='None',value=0),dict(id='positive',name='Positive',value=1),dict(id='negative',name='Negative',value=2)]};base['nodes'].insert(0,choose);base['edges']=[edge('choose','other'),edge('other','after'),edge('after','exit:return'),edge('body','return:choose'),{'from':'choose','port':'case:positive','to':'body'},{'from':'choose','port':'case:negative','to':'body'}];sources['choose']=('Pair.choose.node.json','return Result.Positive;')
(f.project/t.graph_file).write_text(json.dumps(base,ensure_ascii=False));defs=f.metadata('blueprintDescribeOwned',project=str(f.manifest),id=f.n+'PairBody',text=(f.project/'PairBody.celem').read_text(),bodyTarget='common',graph=base,definitionsOnly=True);assert defs['state']=='node-definitions',defs
for key,(file,source)in sources.items():
 row=next(n for n in defs['nodes']+defs['nestedNodes']if n['id']==key);(f.project/file).write_text(json.dumps(dict(schema=1,node=key.split('/')[-1],definitionHash=row['definitionHash'],source=source),ensure_ascii=False))
after=f.project/'Pair.after.node.json';record=json.loads(after.read_text());record['definitionHash']=next(n['definitionHash']for n in defs['nodes']if n['id']=='after');after.write_text(json.dumps(record,ensure_ascii=False));x.physical={p:p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.parts}
if mode in ('method-shared', 'method-compound-shared'):
 declaration = f.project / 'PairBody.celem'
 original = declaration.read_text()
 binding = f'blueprint common "{t.graph_file}";'
 assert binding in original
 alternate = f.project / 'Alternate.graph.json'
 alternate.write_bytes((f.project / t.graph_file).read_bytes())
 declaration.write_text(original.replace(binding, binding + f' blueprint windows "{alternate.name}";'))
 x.physical[alternate] = alternate.read_bytes()
 x.physical[declaration] = declaration.read_bytes()
source_modes={p:stat.S_IMODE(p.stat().st_mode)for p in x.physical}
frame_path = 'body/middle/nest' if too_deep else 'body' if direct or compound_parent else 'body/nest'
peer_path = frame_path.replace('body', 'other')
frame = t.graph + '/graph:' + frame_path.replace('/', '/graph:')
other = t.graph + '/graph:' + peer_path.replace('/', '/graph:')
first, second = ('nest', 'finish') if compound_parent else ('inner', 'tail')
original_order = ['$entry', first, second, '$exit:return']
moved_order = ['$entry', second, first, '$exit:return']
move_control = f'[data-document-down="{first}"]' if compound_parent or direct else f'[data-document-up="{second}"]'
def read(id=frame):return f.invoke('blueprint',dict(action='read',id=id))['result']['result']
def order():return doc().locator('[data-document-cell]').evaluate_all('(els)=>els.map(e=>e.dataset.documentCell)')
def enter(path=frame_path):
 for name in path.split('/'):
  doc().locator('[data-document-internal="'+name+'"]').click();f.idle()
 expect(panel().locator('.bp-breadcrumbs')).to_be_visible()
 expect(doc().locator('[data-document-cell=nest]' if compound_parent else '[data-document-cell=inner]')).to_be_visible()
def root_view():panel().locator('.bp-breadcrumbs button').first.click();f.idle()
def request(data):return dict(action='authorBatch',documentFrame=copy.deepcopy(data.get('documentFrameOrderBinding')or dict(root=t.graph,graph=frame,path=frame_path,rootHash='0'*64,frameHash='0'*64)),id=frame,attempt=uuid.uuid4().hex,checkpointHash=data['checkpointHash'],sourceProof=x.proof(data),edits=[dict(action='entry',node='$entry',to=second),dict(action='route',node=second,port='next',to=first),dict(action='route',node=first,port='next',to='exit:return')])
def chosen(root):
 for cell in frame_path.split('/'):
  root = next(node['graph'] for node in root['nodes'] if node['id'] == cell)
 return root

def method_members(data):
 binding = data['documentFramePreviewBinding']
 result = f.invoke('blueprint', dict(action='nativePreview', id=data['id'], documentFrame=binding,
                                    checkpointHash=data['checkpointHash'], sourceProof=x.proof(data)))['result']['result']
 assert result['diagnostics']['assembledPath'] == data['privatePath']
 members = result['diagnostics']['members']
 assert '"body"' in members and '"inside"' in members and '"peer-inner"' not in members
 # Emission follows execution order. Compare each named method class in full.
 classes = re.split(r'(?=^private static class __fg_methods_[a-f0-9]{32} \{\n)', members, flags=re.MULTILINE)
 assert len(classes) == 3 and not classes[0]
 return sorted(classes[1:]), {node['id']: (node['sourceId'], node['definitionHash']) for node in data['nodes']}

def check_previous_reader():
 previous = os.environ.get('FRAME_ORDER_PREVIOUS')
 if not previous:
  return
 old = Path(previous)
 repo, report, editor_repo = f.repo, f.report, f.env['CONFECTORY_EDITOR_REPO']
 try:
  f.stop()
  f.repo, f.report = old / 'checkout', json.loads((old / 'report.json').read_text())
  f.env['CONFECTORY_EDITOR_REPO'] = str(f.repo)
  f.start(6)
  loaded = read()
  assert loaded['entry'] == second and read(other)['entry'] == first
  if compound_parent:
   assert loaded['edges'] == [edge(second, first), edge(first, 'exit:return')]
  f.invoke('reviewGroup', dict(ids=loaded['reviewIds'], target='portable'))
  assert f.state()['review']['status'] == 'ready'
  untouched()
 finally:
  f.stop()
  f.repo, f.report, f.env['CONFECTORY_EDITOR_REPO'] = repo, report, editor_repo
 f.checked('The previous engine cold-reads the version-1 checkpoint and reviews the same reordered child.')

def untouched():
 x.original();assert all(stat.S_IMODE(p.stat().st_mode)==mode for p,mode in source_modes.items())
try:
 f.start(0);f.invoke('select',dict(id=t.feature));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
 with sync_playwright()as pw:
  expect.set_options(timeout=45000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size(dict(width=1800,height=1400));open_document()
  if mode=='shared':assert doc().locator('[data-document-branch]').all_text_contents()==['Positive','Negative']
  enter();original=read();initial=order();assert initial==original_order
  if method:
   assert original['diagnostics']['state'] in ('source-ready', 'source-assembled')
  expect(doc().locator('[data-document-remove]')).to_have_count(0)
  if unavailable:
   assert original['documentFrameOrderBinding']is None;expect(doc().locator(move_control)).to_be_disabled()
  else:
   binding=original['documentFrameOrderBinding']
   assert binding is not None, (original['profile'], original['diagnostics']['state'])
   assert binding['root']==t.graph and binding['graph']==frame and binding['path']==frame_path
   if compound_parent:
    expect(doc().locator('[data-document-add="$entry"]')).to_have_count(0)
    expect(doc().locator('[data-document-add=finish]')).to_be_disabled()
    expect(doc().locator('[data-document-add=nest]')).to_be_enabled()
    expect(doc().locator('[data-document-drag=nest]')).to_be_disabled()
    assert binding['sources']
    if success:
     members = method_members(read(frame + '/graph:nest'))
     x.build('compound-order-original', 10, 'body\ninside\nparent-tail\npeer-inner\npeer-tail\nafter\n10')
   elif method:
    for cell in ('inner', 'tail'):
     expect(doc().locator(f'[data-document-add={cell}]')).to_be_enabled()
     expect(doc().locator(f'[data-document-drag={cell}]')).to_be_disabled()
    expect(doc().locator('[data-document-add="$entry"]')).to_be_enabled()
    if success:
     members = method_members(original)
     original_tail = 'peer-inner\npeer-tail\nafter\n10' if direct else 'parent-tail\npeer-inner\npeer-tail\nafter\n10'
     x.build('method-order-original', 10, 'body\ninside\n' + original_tail)
   else:
    expect(doc().locator('[data-document-add=inner]')).to_be_enabled()
    expect(doc().locator('[data-document-add=tail]')).to_be_enabled()
   doc().locator(move_control).click();f.idle()
  if not success:
   assert order()==initial and not pending();untouched();assert checkpoint.read_bytes()==before
   text_cell = second if compound_parent else first
   name = f'[data-document-name="{text_cell}"]'
   doc().locator(name).fill('자식 입력 보존 α');doc().locator('.fd-document-title').click();held=pending();assert held;f.invoke('blueprint',request(original),False);assert checkpoint.read_bytes()==before and pending()==held and read()['entry']==first;untouched();restart(1);assert pending()==held and order()==initial;expect(doc().locator(name)).to_have_value('자식 입력 보존 α');untouched()
   if compound_dependency:
    x.build('blocked-compound-dependency', 10, 'body\ninside\nparent-tail:10\npeer-inner\npeer-tail\nafter\n10')
    untouched()
   if mode == 'shared' or too_deep or mode == 'method-compound-shared':
    x.build('blocked-child-unchanged', 10, 'body\ninside\nparent-tail\npeer-inner\npeer-tail\nafter\n10')
    untouched()
   f.checked(f'{mode} refuses structural changes and preserves full-path private input through cold.')
  else:
   assert order()==moved_order;held=pending();assert len(held)==3 and read()['entry']==first;untouched();assert checkpoint.read_bytes()==before
   doc().locator('.fd-document-title').click();doc().press('Control+z');assert order()==initial and not pending();doc().press('Control+y');assert order()==moved_order and pending()==held
   root_view();enter(peer_path);peer_before=read(other);assert peer_before['documentFrameOrderBinding']['graph']==other and peer_before['entry']==first;expect(doc().locator(move_control)).to_be_disabled();assert pending()==held
   q=request(original);q['id']=other;f.invoke('blueprint',q,False);assert read(other)['entry']==first and pending()==held;root_view();enter();assert order()==moved_order and pending()==held
   panel().get_by_role('tab',name='블루프린트 보기',exact=True).click();expect(panel().locator(f'[data-bp-node="{first}"]')).to_be_visible();panel().get_by_role('tab',name='논리 코드',exact=True).click();restart(1);assert pending()==held and order()==moved_order;untouched()
   f.checked('Owned frame order, local Undo/Redo and cold recovery remain distinct from a sibling with the same local node IDs; other-frame inputs block movement')
   mutations = ['unbound','root','path','root-hash','frame-hash','qualified-node','exit','drop','source','remove','create','cross-edge','row-frame','owner','checkpoint','proof','mixed']
   if method:
    mutations = ['unbound', 'path', 'frame-hash', 'source', 'cross-edge', 'checkpoint', 'proof']
   for mutation in mutations:
    q=request(read())
    if mutation=='unbound':q.pop('documentFrame')
    elif mutation=='root':q['documentFrame']['root']=f.n+'Missing/body:common'
    elif mutation=='path':q['documentFrame']['path']=peer_path
    elif mutation=='root-hash':q['documentFrame']['rootHash']='0'*64
    elif mutation=='frame-hash':q['documentFrame']['frameHash']='0'*64
    elif mutation=='qualified-node':q['edits'][1]['node']='body/nest/tail'
    elif mutation=='exit':q['edits'][-1]['to']='exit:missing'
    elif mutation=='drop':q['edits'].pop()
    elif mutation=='source':q['edits'].append(dict(action='source',node='inner',text='return 0;'))
    elif mutation=='remove':q['edits'].append(dict(action='removeNode',node='inner'))
    elif mutation=='create':q['edits'].append(dict(action='createNode',node='extra',definition=dict(kind='code',control='next',intent='extra',signature=signature())))
    elif mutation=='cross-edge':q['edits'][1]['to']=other+'/node:'+first
    elif mutation=='row-frame':q['edits'][1]['frame']=other
    elif mutation=='owner':q.update(owner=f.n+'Missing',ownerHash='0'*64)
    elif mutation=='checkpoint':q['checkpointHash']='0'*64
    elif mutation=='proof':q['sourceProof']='[]'
    else:q['documentCompound']=True
    f.invoke('blueprint',q,False);assert checkpoint.read_bytes()==before and pending()==held and read()['entry']==first;untouched()
   f.invoke('blueprint',dict(action='serialRoutes',id=frame,basis=read()['basis'],routes=request(read())['edits']),False);assert checkpoint.read_bytes()==before;untouched()
   f.checked('unbound or forged root/path/frame/node/exit/body/owner/intent/source/checkpoint plans and direct serialRoutes refuse without live/checkpoint/input mutation')
   peer_file=f.project/'Pair.peer.inner.node.json';peer_bytes=peer_file.read_bytes();peer_file.write_bytes(peer_bytes+b' ')
   try:
    save();assert retained(held)and checkpoint.read_bytes()==before and read()['entry']==first;assert peer_file.read_bytes()==peer_bytes+b' ';assert all(p.read_bytes()==raw for p,raw in x.physical.items()if p!=peer_file)
   finally:peer_file.write_bytes(peer_bytes)
   checkpoint.chmod(0o400)
   try:save();assert retained(held)and checkpoint.read_bytes()==before and read()['entry']==first;untouched()
   finally:checkpoint.chmod(0o600)
   restart(2);assert retained(held)and order()==moved_order;save();assert not pending()and read()['entry']==second and read(other)['entry']==first;untouched()
   if method:
    saved_state = json.loads(checkpoint.read_bytes())
    unit = next(change for change in saved_state['changes'] if change['id'] == t.graph)
    observations = unit['propertyObservations']
    assert saved_state['version'] == observations['version'] == 1
    assert set(observations['sources']) == set(original['documentFrameOrderBinding']['sources'])
    assert any(row['path'] == peer_file.name for row in observations['sources'].values())
    if compound_parent:
     assert len(saved_state['history']['undo']) == 1
     assert [row['id'] for row in saved_state['changes']] == [t.graph]
     saved = checkpoint.read_bytes()
     f.invoke('blueprint', request(original), False)
     assert checkpoint.read_bytes() == saved and read()['entry'] == second
   f.checked('sibling physical-source CAS and checkpoint permission failures preserve exact inputs and original files; cold retry saves only the selected child atomically')
   history=f.invoke('draftHistory',dict(action='inspect'))['result']['result'];assert history['undo']['available'];assert f.invoke('draftHistory',dict(action='undo',token=history['undo']['token']))['result']['result']['accepted'];assert read()['entry']==first;f.invoke('saveDraft',{});restart(3);assert order()==initial and not pending();history=f.invoke('draftHistory',dict(action='inspect'))['result']['result'];assert history['redo']['available'];assert f.invoke('draftHistory',dict(action='redo',token=history['redo']['token']))['result']['result']['accepted'];assert read()['entry']==second;f.invoke('saveDraft',{});restart(4);assert order()==moved_order and read(other)['entry']==first;untouched()
   f.checked('shared Undo to original bytes, explicit Save/cold and Redo preserve root observations, full child path and sibling history boundary')
   r=review();r.locator('[data-reject]').click();untouched();r=review();path=f.project/t.graph_file
   observed = peer_file if method else path
   raw = observed.read_bytes()
   saved = checkpoint.read_bytes()
   observed.write_bytes(raw + b' ')
   try:
    r.locator('#confirm').click();f.idle()
    assert observed.read_bytes() == raw + b' ' and checkpoint.read_bytes() == saved
    assert all(protected.read_bytes() == data for protected, data in x.physical.items() if protected != observed)
   finally:
    observed.write_bytes(raw)
   if r.is_visible():r.locator('[data-reject]').click()
   if method and os.environ.get('FRAME_ORDER_PREVIOUS'):
    f.page.close()
    check_previous_reader()
    f.start(7)
    f.page = f.setup()
    f.page.set_viewport_size(dict(width=1800,height=1400))
    f.idle()
   r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle()
   peer_stdout = 'peer-inner\npeer-tail\nafter\n10'
   if compound_parent:
    x.build('compound-order-confirmed', 10, 'parent-tail\nbody\ninside\n' + peer_stdout)
   else:
    x.build('owned-child-order', 10, 'inside\nbody\n' + ('' if direct else 'parent-tail\n') + peer_stdout)
   assert all(p.read_bytes()==raw for p,raw in x.physical.items()if p!=path);assert all(stat.S_IMODE(p.stat().st_mode)==mode for p,mode in source_modes.items())
   expected = copy.deepcopy(base)
   chosen(expected).update(entry=second, edges=[edge(second, first), edge(first, 'exit:return')])
   assert json.loads(path.read_text()) == expected
   restart(5);assert order()==moved_order and not pending() and read(other)['entry']==first
   if method:
    assert method_members(read(frame + '/graph:nest' if compound_parent else frame)) == members
    f.checked('Both generated method identities and their complete C# members are unchanged after the new execution order.')
   if compound_parent:
    doc().locator('[data-document-up=nest]').click()
    f.idle()
    assert order() == initial and read()['entry'] == second
    doc().press('Control+z')
    assert order() == moved_order and not pending()
   f.checked('Review cancellation/final CAS preserve originals; Confirm changes only one qualified child entry/routes and real execution preserves input, return and parent continuation')
  f.page.screenshot(path=str(f.case/('frame-'+mode+'.png')),full_page=True);assert not f.errors and not f.external,(f.errors,f.external);f.browser.close()
except BaseException:
 if getattr(f,'page',None):
  try:(f.case/'frame-failure.html').write_text(f.page.content());(f.case/'frame-errors.json').write_text(json.dumps(f.errors,ensure_ascii=False));f.page.screenshot(path=str(f.case/'frame-failure.png'),timeout=10000)
  except Exception:pass
 raise
finally:
 (f.case/'frame-traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False));(f.case/'frame-checks.json').write_text(json.dumps(f.checks,ensure_ascii=False));f.stop()
print('V821_FRAME_STRUCTURE',mode,f.case,flush=True)
