"""Actual Linux editor/engine: full-path owned ordinary child frame order only."""
import ast,copy,json,stat,sys,time,uuid
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
import v666_node_names_recovery_fixture as t
f=t.f;x=t.x;mode=sys.argv[3]if len(sys.argv)>3 else'normal'
helper=Path(__file__).with_name('v821_function_document_ui.py')
exec(compile(ast.Module(body=[n for n in ast.parse(helper.read_text()).body if isinstance(n,ast.FunctionDef)],type_ignores=[]),str(helper),'exec'),globals())
def edge(a,b):return {'from':a,'port':'next','to':b}
def signature(args=[],ret='void'):return dict(args=args,**{'return':ret})
def code(id,file,sig=None,args={}):return dict(id=id,kind='code',control='next',intent=id,signature=sig or signature(),arguments=args,implementation=file)
def child(nodes,exits):return dict(schema=1,profile='sync-acyclic-nested-v1',entry=nodes[0]['id'],nodes=nodes,edges=[edge(n['id'],nodes[i+1]['id']if i+1<len(nodes)else'exit:return')for i,n in enumerate(nodes)],exits=exits)
def compound(id,graph,sig=None,args={}):return dict(id=id,kind='graph',control='next',intent=id,signature=sig or signature(),arguments=args,graph=graph)
amount=[dict(name='amount',type='int')];target=child([code('inner','Pair.body.inner.node.json',signature(amount,'int'),{'amount':{'input':'amount'}}),code('tail','Pair.body.tail.node.json')],{'return':{'node':'inner'}})
if mode=='dependency':target['nodes'][1].update(signature=signature([dict(name='value',type='int')]),arguments={'value':{'node':'inner'}})
peer=child([code('inner','Pair.peer.inner.node.json'),code('tail','Pair.peer.tail.node.json')],{'return':None})
base=copy.deepcopy(t.definition);base['profile']='sync-acyclic-nested-v1';body=base['nodes'][0];body.pop('implementation');body['kind']='graph';body['graph']=child([compound('nest',target,signature(amount,'int'),{'amount':{'input':'amount'}}),code('finish','Pair.finish.node.json')],{'return':{'node':'nest'}})
base['nodes'].insert(1,compound('other',child([compound('nest',peer)],{'return':None})));base['edges']=[edge('body','other'),edge('other','after'),edge('after','exit:return')]
sources={'body/nest/inner':('Pair.body.inner.node.json','global::System.Console.WriteLine("body");\r\nreturn checked(amount+3);'),'body/nest/tail':('Pair.body.tail.node.json','global::System.Console.WriteLine("inside");'),'body/finish':('Pair.finish.node.json','global::System.Console.WriteLine("parent-tail");'),'other/nest/inner':('Pair.peer.inner.node.json','global::System.Console.WriteLine("peer-inner");'),'other/nest/tail':('Pair.peer.tail.node.json','global::System.Console.WriteLine("peer-tail");')}
if mode=='shared':
 base['profile']='sync-acyclic-switch-v1';base['entry']='choose';body['branchOwner']='choose';base['exits']['return']={'constant':10};choose=code('choose','Pair.choose.node.json');choose['control']='switch';choose['executionEnum']={'primary':'next','members':[dict(id='next',name='None',value=0),dict(id='positive',name='Positive',value=1),dict(id='negative',name='Negative',value=2)]};base['nodes'].insert(0,choose);base['edges']=[edge('choose','other'),edge('other','after'),edge('after','exit:return'),edge('body','return:choose'),{'from':'choose','port':'case:positive','to':'body'},{'from':'choose','port':'case:negative','to':'body'}];sources['choose']=('Pair.choose.node.json','return Result.Positive;')
(f.project/t.graph_file).write_text(json.dumps(base,ensure_ascii=False));defs=f.metadata('blueprintDescribeOwned',project=str(f.manifest),id=f.n+'PairBody',text=(f.project/'PairBody.celem').read_text(),bodyTarget='common',graph=base,definitionsOnly=True);assert defs['state']=='node-definitions',defs
for key,(file,source)in sources.items():
 row=next(n for n in defs['nodes']+defs['nestedNodes']if n['id']==key);(f.project/file).write_text(json.dumps(dict(schema=1,node=key.split('/')[-1],definitionHash=row['definitionHash'],source=source),ensure_ascii=False))
after=f.project/'Pair.after.node.json';record=json.loads(after.read_text());record['definitionHash']=next(n['definitionHash']for n in defs['nodes']if n['id']=='after');after.write_text(json.dumps(record,ensure_ascii=False));x.physical={p:p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.parts}
source_modes={p:stat.S_IMODE(p.stat().st_mode)for p in x.physical}
frame=t.graph+'/graph:body/graph:nest';other=t.graph+'/graph:other/graph:nest'
def read(id=frame):return f.invoke('blueprint',dict(action='read',id=id))['result']['result']
def order():return doc().locator('[data-document-cell]').evaluate_all('(els)=>els.map(e=>e.dataset.documentCell)')
def enter(path='body/nest'):
 for name in path.split('/'):
  doc().locator('[data-document-internal="'+name+'"]').click();f.idle()
 expect(panel().locator('.bp-breadcrumbs')).to_be_visible();expect(doc().locator('[data-document-cell=inner]')).to_be_visible()
def root_view():panel().locator('.bp-breadcrumbs button').first.click();f.idle()
def request(data):return dict(action='authorBatch',documentFrame=copy.deepcopy(data.get('documentFrameOrderBinding')or dict(root=t.graph,graph=frame,path='body/nest',rootHash='0'*64,frameHash='0'*64)),id=frame,attempt=uuid.uuid4().hex,checkpointHash=data['checkpointHash'],sourceProof=x.proof(data),edits=[dict(action='entry',node='$entry',to='tail'),dict(action='route',node='tail',port='next',to='inner'),dict(action='route',node='inner',port='next',to='exit:return')])
def chosen(root):return next(n for n in next(n for n in root['nodes']if n['id']=='body')['graph']['nodes']if n['id']=='nest')['graph']
def untouched():
 x.original();assert all(stat.S_IMODE(p.stat().st_mode)==mode for p,mode in source_modes.items())
try:
 f.start(0);f.invoke('select',dict(id=t.feature));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
 with sync_playwright()as pw:
  expect.set_options(timeout=45000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size(dict(width=1800,height=1400));open_document()
  if mode=='shared':assert doc().locator('[data-document-branch]').all_text_contents()==['Positive','Negative']
  enter();original=read();initial=order();assert initial==['$entry','inner','tail','$exit:return']
  expect(doc().locator('[data-document-remove]')).to_have_count(0)
  if mode=='shared':
   assert original['documentFrameOrderBinding']is None;expect(doc().locator('[data-document-up=tail]')).to_be_disabled()
  else:
   binding=original['documentFrameOrderBinding'];assert binding['root']==t.graph and binding['graph']==frame and binding['path']=='body/nest';expect(doc().locator('[data-document-add=inner]')).to_be_enabled();expect(doc().locator('[data-document-add=tail]')).to_be_enabled();doc().locator('[data-document-up=tail]').click();f.idle()
  if mode!='normal':
   assert order()==initial and not pending();untouched();assert checkpoint.read_bytes()==before
   doc().locator('[data-document-name=inner]').fill('자식 입력 보존 α');doc().locator('.fd-document-title').click();held=pending();assert held;f.invoke('blueprint',request(original),False);assert checkpoint.read_bytes()==before and pending()==held and read()['entry']=='inner';untouched();restart(1);assert pending()==held and order()==initial;expect(doc().locator('[data-document-name=inner]')).to_have_value('자식 입력 보존 α');untouched()
   if mode=='shared':x.build('shared-child-unchanged',10,'body\ninside\nparent-tail\npeer-inner\npeer-tail\nafter\n10');untouched()
   f.checked('child producer or shared ancestor entry refuses structural changes and preserves full-path private input through cold; existing shared execution remains valid')
  else:
   assert order()==['$entry','tail','inner','$exit:return'];held=pending();assert len(held)==3 and read()['entry']=='inner';untouched();assert checkpoint.read_bytes()==before
   doc().locator('.fd-document-title').click();doc().press('Control+z');assert order()==initial;doc().press('Control+y');assert order()[1]=='tail'
   root_view();enter('other/nest');peer_before=read(other);assert peer_before['documentFrameOrderBinding']['graph']==other and peer_before['entry']=='inner';expect(doc().locator('[data-document-up=tail]')).to_be_disabled();assert pending()==held
   q=request(original);q['id']=other;f.invoke('blueprint',q,False);assert read(other)['entry']=='inner'and pending()==held;root_view();enter();assert order()[1]=='tail'and pending()==held
   panel().get_by_role('tab',name='블루프린트 보기',exact=True).click();expect(panel().locator('[data-bp-node=inner]')).to_be_visible();panel().get_by_role('tab',name='논리 코드',exact=True).click();restart(1);assert pending()==held and order()[1]=='tail';untouched()
   f.checked('depth-two owned frame order, local Undo/Redo and cold recovery remain distinct from a sibling with the same local node IDs; other-frame inputs block movement')
   for mutation in ['unbound','root','path','root-hash','frame-hash','qualified-node','exit','drop','source','remove','create','cross-edge','row-frame','owner','checkpoint','proof','mixed']:
    q=request(read())
    if mutation=='unbound':q.pop('documentFrame')
    elif mutation=='root':q['documentFrame']['root']=f.n+'Missing/body:common'
    elif mutation=='path':q['documentFrame']['path']='other/nest'
    elif mutation=='root-hash':q['documentFrame']['rootHash']='0'*64
    elif mutation=='frame-hash':q['documentFrame']['frameHash']='0'*64
    elif mutation=='qualified-node':q['edits'][1]['node']='body/nest/tail'
    elif mutation=='exit':q['edits'][-1]['to']='exit:missing'
    elif mutation=='drop':q['edits'].pop()
    elif mutation=='source':q['edits'].append(dict(action='source',node='inner',text='return 0;'))
    elif mutation=='remove':q['edits'].append(dict(action='removeNode',node='inner'))
    elif mutation=='create':q['edits'].append(dict(action='createNode',node='extra',definition=dict(kind='code',control='next',intent='extra',signature=signature())))
    elif mutation=='cross-edge':q['edits'][1]['to']=other+'/node:inner'
    elif mutation=='row-frame':q['edits'][1]['frame']=other
    elif mutation=='owner':q.update(owner=f.n+'Missing',ownerHash='0'*64)
    elif mutation=='checkpoint':q['checkpointHash']='0'*64
    elif mutation=='proof':q['sourceProof']='[]'
    else:q['documentCompound']=True
    f.invoke('blueprint',q,False);assert checkpoint.read_bytes()==before and pending()==held and read()['entry']=='inner';untouched()
   f.invoke('blueprint',dict(action='serialRoutes',id=frame,basis=read()['basis'],routes=request(read())['edits']),False);assert checkpoint.read_bytes()==before;untouched()
   f.checked('unbound or forged root/path/frame/node/exit/body/owner/intent/source/checkpoint plans and direct serialRoutes refuse without live/checkpoint/input mutation')
   peer_file=f.project/'Pair.peer.inner.node.json';peer_bytes=peer_file.read_bytes();peer_file.write_bytes(peer_bytes+b' ')
   try:
    save();assert retained(held)and checkpoint.read_bytes()==before and read()['entry']=='inner';assert peer_file.read_bytes()==peer_bytes+b' ';assert all(p.read_bytes()==raw for p,raw in x.physical.items()if p!=peer_file)
   finally:peer_file.write_bytes(peer_bytes)
   checkpoint.chmod(0o400)
   try:save();assert retained(held)and checkpoint.read_bytes()==before and read()['entry']=='inner';untouched()
   finally:checkpoint.chmod(0o600)
   restart(2);assert retained(held)and order()[1]=='tail';save();assert not pending()and read()['entry']=='tail'and read(other)['entry']=='inner';untouched()
   f.checked('sibling physical-source CAS and checkpoint permission failures preserve exact inputs and original files; cold retry saves only the selected child atomically')
   history=f.invoke('draftHistory',dict(action='inspect'))['result']['result'];assert history['undo']['available'];assert f.invoke('draftHistory',dict(action='undo',token=history['undo']['token']))['result']['result']['accepted'];assert read()['entry']=='inner';f.invoke('saveDraft',{});restart(3);assert order()==initial and not pending();history=f.invoke('draftHistory',dict(action='inspect'))['result']['result'];assert history['redo']['available'];assert f.invoke('draftHistory',dict(action='redo',token=history['redo']['token']))['result']['result']['accepted'];assert read()['entry']=='tail';f.invoke('saveDraft',{});restart(4);assert order()[1]=='tail'and read(other)['entry']=='inner';untouched()
   f.checked('shared Undo to original bytes, explicit Save/cold and Redo preserve root observations, full child path and sibling history boundary')
   r=review();r.locator('[data-reject]').click();untouched();r=review();path=f.project/t.graph_file;raw=path.read_bytes();saved=checkpoint.read_bytes();path.write_bytes(raw+b' ')
   try:r.locator('#confirm').click();f.idle();assert path.read_bytes()==raw+b' 'and checkpoint.read_bytes()==saved
   finally:path.write_bytes(raw)
   if r.is_visible():r.locator('[data-reject]').click()
   r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();x.build('owned-child-order',10,'inside\nbody\nparent-tail\npeer-inner\npeer-tail\nafter\n10');assert all(p.read_bytes()==raw for p,raw in x.physical.items()if p!=path);assert all(stat.S_IMODE(p.stat().st_mode)==mode for p,mode in source_modes.items());written=json.loads(path.read_text());selected=chosen(written);assert selected['entry']=='tail';selected['entry']=target['entry'];selected['edges']=copy.deepcopy(target['edges']);assert written==base;restart(5);assert order()[1]=='tail'and not pending()and read(other)['entry']=='inner'
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
