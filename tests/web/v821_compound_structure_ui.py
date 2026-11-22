"""Actual Linux engine: move complete owned compound invocations, never flatten frames."""
import ast,copy,json,subprocess,sys,time,uuid
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
if mode in {'dependency','insert'}:
 other['signature']['args']=[dict(name='value',type='int')];other['arguments']={'value':{'node':'body'}}
if mode=='insert':
 other['graph']['nodes'][0]['signature']['args']=[dict(name='value',type='int')]
 other['graph']['nodes'][0]['arguments']={'value':{'input':'value'}}
base['nodes'].insert(1,other);base['edges']=[edge('body','other'),edge('other','after'),edge('after','exit:return')]
if mode=='shared':
 base['profile']='sync-acyclic-switch-v1';base['entry']='choose';other['branchOwner']='choose'
 choose=code('choose',[],'void','Pair.choose.node.json');choose['control']='switch';choose['executionEnum']={'primary':'next','members':[{'id':'next','name':'None','value':0},{'id':'positive','name':'Positive','value':1},{'id':'negative','name':'Negative','value':2}]};base['nodes'].insert(0,choose)
 base['edges']=[edge('choose','body'),edge('body','after'),edge('after','exit:return'),{'from':'choose','port':'case:positive','to':'other'},{'from':'choose','port':'case:negative','to':'other'},edge('other','return:choose')]
(f.project/t.graph_file).write_text(json.dumps(base,ensure_ascii=False))
defs=f.metadata('blueprintDescribeOwned',project=str(f.manifest),id=f.n+'PairBody',text=(f.project/'PairBody.celem').read_text(),bodyTarget='common',graph=base,definitionsOnly=True);assert defs['state']=='node-definitions',defs
sources={'body/inner':('Pair.inner.node.json','global::System.Console.WriteLine("body");\r\nreturn '+'checked(amount+3);'),'body/tail':('Pair.tail.node.json','global::System.Console.WriteLine("inside");'),'other/inner':('Pair.other.node.json','global::System.Console.WriteLine("other");')}
if mode=='shared':sources['choose']=('Pair.choose.node.json','return Result.Positive;')
if mode=='insert':sources['other/inner']=('Pair.other.node.json','global::System.Console.WriteLine("other:"+value);')
for key,(file,source)in sources.items():
 definition=next(n for n in defs['nodes']+defs['nestedNodes']if n['id']==key)
 (f.project/file).write_text(json.dumps(dict(schema=1,node=key.split('/')[-1],definitionHash=definition['definitionHash'],source=source),ensure_ascii=False))
# The existing ordinary leaf keeps its original source and newly observed identity.
after=f.project/'Pair.after.node.json';record=json.loads(after.read_text());record['definitionHash']=next(n['definitionHash']for n in defs['nodes']if n['id']=='after');after.write_text(json.dumps(record,ensure_ascii=False))
(f.project/t.graph_file).write_text(json.dumps(base,ensure_ascii=False));x.physical={p:p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.parts}
def order():return doc().locator('[data-document-cell]').evaluate_all('(els)=>els.map(e=>e.dataset.documentCell)')
def request(data,ids=['other','body','after']):return dict(action='authorBatch',documentCompound=True,id=t.graph,attempt=uuid.uuid4().hex,checkpointHash=data['checkpointHash'],sourceProof=x.proof(data),edits=[dict(action='entry',node='$entry',to=ids[0])]+[dict(action='route',node=n,port='next',to=ids[i+1]if i+1<len(ids)else'exit:return')for i,n in enumerate(ids)])
def insertion_request(data,anchor='body',successor='other'):
 node='cell_probe'
 return dict(action='authorBatch',documentCompound=True,id=t.graph,attempt=uuid.uuid4().hex,checkpointHash=data['checkpointHash'],sourceProof=x.proof(data),edits=[
  dict(action='createNode',node=node,definition=dict(kind='code',control='next',intent='복합 호출 뒤 동작',signature={'args':[],'return':'void'})),
  dict(action='rename',node=node,text='복합 호출 뒤 동작'),dict(action='intent',node=node,text='복합 호출 뒤 동작'),dict(action='source',node=node,text='return;'),
  dict(action='route',node=anchor,port='next',to=node),dict(action='route',node=node,port='next',to=successor)])
def untouched():x.original()
def subtree():return {n['id']:copy.deepcopy(n)for n in base['nodes']}

def verify_insertion(original,initial,checkpoint,before):
 assert set(original['documentCompoundInsertion']['nodes'])=={'body','other'}
 add=doc().locator('[data-document-add=body]');expect(add).to_be_enabled()
 expect(doc().locator('[data-document-add=after]')).to_be_disabled()
 add.click();f.idle();created=order()[2];inserted=['$entry','body',created,*initial[2:]]
 assert created.startswith('cell_') and order()==inserted and len(pending())==6
 doc().press('Control+z');assert order()==initial and not pending()
 doc().press('Control+y');assert order()==inserted
 doc().locator('[data-document-code="'+created+'"]').click()
 dialog=f.page.locator('.bp-script-dialog');source=dialog.locator('[data-code-source]');body_text=dialog.locator('[data-code-region=body]').text_content()
 source.evaluate('(el,text)=>{el.focus();const at=el.value.indexOf(text);if(at<0)throw Error("Editable body missing");el.setSelectionRange(at,at+text.length)}',body_text)
 f.page.keyboard.insert_text('global::System.Console.WriteLine("inserted-after-compound");\nreturn;')
 dialog.locator('[data-code-save]').click();f.idle();held=pending();assert len(held)==6
 f.invoke('blueprint',insertion_request(original,successor='after'),False)
 f.invoke('blueprint',insertion_request(original,anchor='after',successor='exit:return'),False)
 ambiguous=copy.deepcopy(base);ambiguous['edges'].append(edge('body','after'))
 try:f.metadata('blueprintCellRegion',action='compound-insert',graph=ambiguous,edits=insertion_request(original)['edits'])
 except (AssertionError,subprocess.CalledProcessError):pass
 else:raise AssertionError('An ambiguous compound continuation was accepted')
 assert pending()==held and checkpoint.read_bytes()==before and t.read()['edges']==original['edges'];untouched()
 f.checked('one compound continuation changes locally; Undo/Redo keeps the whole insertion and a retargeted route or noncompound anchor is refused')

 graph_path=f.project/t.graph_file;raw=graph_path.read_bytes();changed=json.loads(raw)
 next(edge for edge in changed['edges'] if edge['from']=='body')['to']='after';changed_bytes=json.dumps(changed).encode()
 graph_path.write_bytes(changed_bytes)
 try:
  save();assert retained(held) and checkpoint.read_bytes()==before and graph_path.read_bytes()==changed_bytes
  assert all(p.read_bytes()==content for p,content in x.physical.items() if p!=graph_path)
 finally:graph_path.write_bytes(raw)
 restart(1);assert retained(held) and order()==inserted;untouched()
 save();assert not pending() and t.read()['entry']==original['entry'];untouched()
 restart(2);assert order()==inserted and not pending()
 history=f.invoke('draftHistory',dict(action='inspect'))['result']['result']
 assert history['boundary']=='OWNERSHIP_CHANGED' and not history['undo']['available']
 f.checked('a changed parent continuation refuses Save and preserves input; atomic Save and cold restart retain the new cell and original entry')

 r=review();r.locator('[data-reject]').click();untouched()
 r=review();saved=checkpoint.read_bytes();peer=f.project/'Pair.other.node.json';peer_raw=peer.read_bytes();peer.write_bytes(peer_raw+b' ')
 try:
  r.locator('#confirm').click();f.idle();assert checkpoint.read_bytes()==saved and peer.read_bytes()==peer_raw+b' ' and graph_path.read_bytes()==raw
 finally:peer.write_bytes(peer_raw)
 if r.is_visible():r.locator('[data-reject]').click()
 r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle()
 x.build('compound-insert',10,'body\ninside\ninserted-after-compound\nother:10\nafter\n10')
 written=json.loads(graph_path.read_bytes());assert written['entry']==base['entry'];assert written['edges']==[edge('body',created),*base['edges'][1:],edge(created,'other')]
 written['edges']=base['edges'];written['nodes']=[n for n in written['nodes'] if n['id']!=created]
 assert written==base and all(p.read_bytes()==content for p,content in x.physical.items() if p!=graph_path)
 new_sources={p for p in f.project.rglob('*.node.json') if p not in x.physical and '.confectory' not in p.parts}
 assert len(new_sources)==1 and json.loads(new_sources.pop().read_text())['node']==created
 restart(3);assert order()==inserted and not pending()
 f.checked('Confirm refuses a late child source change; fresh Confirm runs the new cell between the compound and its value consumer with original return, bindings and sources')

try:
 f.start(0);f.invoke('select',dict(id=t.feature));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
 with sync_playwright()as pw:
  expect.set_options(timeout=45000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size(dict(width=1800,height=1400));open_document();original=t.read();initial=order()
  if mode=='shared':
   assert original['documentCompoundOrderAvailable']is False
   assert original['documentCompoundInsertion'] is None
   expect(doc().locator('[data-document-add=other]')).to_be_disabled()
   f.invoke('blueprint',insertion_request(original,anchor='other',successor='return:choose'),False)
   assert checkpoint.read_bytes()==before;untouched()
   expect(doc().locator('[data-document-up=other]')).to_be_disabled()
   assert doc().locator('[data-document-branch]').all_text_contents()==['Positive','Negative']
  elif mode!='insert':
   assert original['documentCompoundOrderAvailable']is True
   doc().locator('[data-document-up=other]').click();f.idle()
  if mode=='insert':verify_insertion(original,initial,checkpoint,before)
  elif mode!='normal':
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
   doc().locator('[data-document-internal=body]').click();f.idle();expect(doc().locator('[data-document-cell=inner]')).to_be_visible();expect(doc().locator('[data-document-up=tail]')).to_be_disabled();expect(doc().locator('[data-document-add=inner]')).to_be_disabled();assert not f.invoke('blueprint',dict(action='read',id=t.graph+'/graph:body'))['result']['result']['documentCompoundOrderAvailable']
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
   f.checked('Review cancellation/final CAS preserve originals; Confirm changes only parent routes and real rebuilt execution preserves child return and continuation')
  f.page.screenshot(path=str(f.case/('compound-'+mode+'.png')),full_page=True);assert not f.errors and not f.external,(f.errors,f.external);f.browser.close()
except BaseException:
 if getattr(f,'page',None):
  try:(f.case/'compound-failure.html').write_text(f.page.content());(f.case/'compound-errors.json').write_text(json.dumps(f.errors,ensure_ascii=False));f.page.screenshot(path=str(f.case/'compound-failure.png'),timeout=10000)
  except Exception:pass
 raise
finally:
 (f.case/'compound-traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False));(f.case/'compound-checks.json').write_text(json.dumps(f.checks,ensure_ascii=False));f.stop()
print('V821_COMPOUND_STRUCTURE',mode,f.case,flush=True)
