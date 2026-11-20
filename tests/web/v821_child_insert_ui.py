"""One directly owned child void insertion over actual Linux UI/engine and CAS.
Existing frame fixture only; its order test body is not executed.
"""
import ast,copy,json,stat,sys,time,uuid,subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
fixture=Path(__file__).with_name('v821_frame_structure_ui.py');nodes=ast.parse(fixture.read_text()).body
exec(compile(ast.Module(body=nodes[:next(i for i,n in enumerate(nodes)if isinstance(n,ast.Try))],type_ignores=[]),str(fixture),'exec'),globals())
def resume(i):
 restart(i)
 if panel().locator('.bp-breadcrumbs button').count():root_view()
 enter()
def proposal(data,node='cell_probe',after='inner',to='tail'):
 return dict(action='authorBatch',documentFrame=copy.deepcopy(data.get('documentFrameOrderBinding')or dict(root=t.graph,graph=frame,path='body/nest',rootHash='0'*64,frameHash='0'*64)),id=frame,attempt=uuid.uuid4().hex,checkpointHash=data['checkpointHash'],sourceProof=x.proof(data),edits=[dict(action='createNode',node=node,definition=dict(kind='code',control='next',intent='새 동작',signature=signature())),dict(action='rename',node=node,text='자식 추가 α'),dict(action='intent',node=node,text='자식 추가 α'),dict(action='source',node=node,text='global::System.Console.WriteLine("inserted-child");\nreturn;'),dict(action='route',node=after,port='next',to=node),dict(action='route',node=node,port='next',to=to)])
def edit_body(created):
 doc().locator('[data-document-code="'+created+'"]').click();dialog=f.page.locator('.bp-script-dialog');source=dialog.locator('[data-code-source]');body=dialog.locator('[data-code-region=body]').text_content();source.evaluate('(el,text)=>{el.focus();const at=el.value.indexOf(text);if(at<0)throw Error("Missing protected body");el.setSelectionRange(at,at+text.length)}',body);f.page.keyboard.insert_text('global::System.Console.WriteLine("inserted-child");\nreturn;');dialog.locator('[data-code-save]').click();f.idle()
def pure_denied(graph,path,edits):
 try:f.metadata('blueprintCellRegion',action='frame-create',graph=graph,path=path,edits=edits)
 except (AssertionError,subprocess.CalledProcessError):return
 raise AssertionError('Unsupported pure insertion accepted')
try:
 f.start(0);f.invoke('select',dict(id=t.feature));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
 with sync_playwright()as pw:
  expect.set_options(timeout=45000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size(dict(width=1800,height=1400));open_document();enter();original=read();initial=order()
  if mode=='shared':
   assert original['documentFrameOrderBinding']is None;expect(doc().locator('[data-document-add=inner]')).to_be_disabled();doc().locator('[data-document-name=inner]').fill('공유 경계 입력 보존');doc().locator('.fd-document-title').click();held=pending();f.invoke('blueprint',proposal(original),False);assert checkpoint.read_bytes()==before and pending()==held;untouched();resume(1);assert pending()==held;expect(doc().locator('[data-document-name=inner]')).to_have_value('공유 경계 입력 보존');x.build('child-insert-shared-unchanged',10,'body\ninside\nparent-tail\npeer-inner\npeer-tail\nafter\n10');untouched();f.checked('shared ancestor refuses child addition in UI/server and retains full-path private input and original execution through cold')
  else:
   assert original['documentFrameOrderBinding']['path']=='body/nest';expect(doc().locator('[data-document-add=inner]')).to_be_enabled()
   # Pure compiler plan limits include the new cell; metadata reads grant no writes.
   q=proposal(original);f.metadata('blueprintCellRegion',action='frame-create',graph=base,path='body/nest',edits=q['edits'])
   qparent=proposal(original,node='finish');f.metadata('blueprintCellRegion',action='frame-create',graph=base,path='body/nest',edits=qparent['edits'])
   huge=copy.deepcopy(base);c=chosen(huge)
   while len(c['nodes'])<63:c['nodes'].append(code('n'+str(len(c['nodes'])),'unused.node.json'))
   c['edges']=[edge(n['id'],c['nodes'][i+1]['id']if i+1<len(c['nodes'])else'exit:return')for i,n in enumerate(c['nodes'])];pure_denied(huge,'body/nest',q['edits'])
   deep=child([code('inner','unused.node.json'),code('tail','unused2.node.json')],{'return':None})
   for i in reversed(range(9)):deep=child([compound('p'+str(i),deep)],{'return':None})
   pure_denied(deep,'/'.join('p'+str(i)for i in range(9)),q['edits'])
   many=child([compound('x'+str(i),child([code('n'+str(j),'unused.node.json')for j in range(51 if i==0 else 50)],{'return':None}))for i in range(5)],{'return':None});pure_denied(many,'x0',proposal(original,after='n0',to='n1')['edits'])
   doc().locator('[data-document-add=inner]').click();f.idle();created=[id for id in order()if id.startswith('cell_')];assert len(created)==1;created=created[0];assert order()==['$entry','inner',created,'tail','$exit:return'];assert len(pending())==6;doc().locator('.fd-document-title').click();doc().press('Control+z');assert order()==initial;doc().press('Control+y');assert created in order();edit_body(created);held=pending();assert len(held)==6;untouched();assert checkpoint.read_bytes()==before
   root_view();enter('other/nest');expect(doc().locator('[data-document-add=inner]')).to_be_disabled();assert read(other)['entry']=='inner';root_view();enter();assert pending()==held
   panel().get_by_role('tab',name='블루프린트 보기',exact=True).click();expect(panel().locator('[data-bp-node="'+created+'"]').first).to_be_visible();panel().get_by_role('tab',name='논리 코드',exact=True).click();resume(1);assert pending()==held and created in order();untouched();f.checked('one qualified child insertion edits its protected C# body, private Undo/Redo and cold; sibling duplicate local IDs and original source/ABI remain distinct; depth/per-frame/global limits hold')
   for mutation in ['unbound','root','path','root-hash','frame-hash','owner','frame','local-id','args','return','scope','continuation','source','remove','two','checkpoint','proof','mixed']:
    q=proposal(read());e=q['edits']
    if mutation=='unbound':q.pop('documentFrame')
    elif mutation=='root':q['documentFrame']['root']=f.n+'Missing/body:common'
    elif mutation=='path':q['documentFrame']['path']='other/nest'
    elif mutation=='root-hash':q['documentFrame']['rootHash']='0'*64
    elif mutation=='frame-hash':q['documentFrame']['frameHash']='0'*64
    elif mutation=='owner':q.update(owner=f.n+'Missing',ownerHash='0'*64)
    elif mutation=='frame':e[0]['frame']=other
    elif mutation=='local-id':e[0]['node']='inner'
    elif mutation=='args':e[0]['definition']['signature']['args']=[dict(name='value',type='int')]
    elif mutation=='return':e[0]['definition']['signature']['return']='int'
    elif mutation=='scope':e[0]['definition']['branchOwner']='inner'
    elif mutation=='continuation':e[-1]['to']='exit:return'
    elif mutation=='source':e[3]['node']='inner'
    elif mutation=='remove':e[0]['action']='removeNode'
    elif mutation=='two':e.append(copy.deepcopy(e[0]))
    elif mutation=='checkpoint':q['checkpointHash']='0'*64
    elif mutation=='proof':q['sourceProof']='[]'
    else:q['documentCompound']=True
    f.invoke('blueprint',q,False);assert checkpoint.read_bytes()==before and pending()==held and len(read()['nodes'])==2;untouched()
   f.checked('missing/forged full-path binding, other owner/frame, ABI/scope/continuation/source mutation, removal, extra creation, stale checkpoint/proof and mixed intents refuse atomically')
   peer_file=f.project/'Pair.peer.inner.node.json';raw=peer_file.read_bytes();peer_file.write_bytes(raw+b' ')
   try:save();assert retained(held)and checkpoint.read_bytes()==before and len(read()['nodes'])==2;assert peer_file.read_bytes()==raw+b' '
   finally:peer_file.write_bytes(raw)
   checkpoint.chmod(0o400)
   try:save();assert retained(held)and checkpoint.read_bytes()==before and len(read()['nodes'])==2;untouched()
   finally:checkpoint.chmod(0o600)
   resume(2);assert retained(held);save();assert not pending();current=read();made=next(n for n in current['nodes']if n['id']==created);assert made['sourceId']==t.graph+'/node:body/node:nest/node:'+created;assert 'inserted-child'in made['source'];assert len(read(other)['nodes'])==2;untouched();resume(3);assert created in order()and not pending()
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
   r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();x.build('owned-child-insert',10,'body\ninserted-child\ninside\nparent-tail\npeer-inner\npeer-tail\nafter\n10');assert all(p.read_bytes()==v for p,v in x.physical.items()if p.name!=t.graph_file);assert all(stat.S_IMODE(p.stat().st_mode)==m for p,m in source_modes.items());written=json.loads((f.project/t.graph_file).read_text());c=chosen(written);new=next(n for n in c['nodes']if n['id']==created);c['nodes'].remove(new);c['edges']=copy.deepcopy(target['edges']);assert written==base;new_sources=[p for p in f.project.rglob('*.node.json')if p not in x.physical and '.confectory'not in p.parts];assert len(new_sources)==1 and json.loads(new_sources[0].read_text())['node']==created;resume(4);assert created in order()and len(read(other)['nodes'])==2;f.checked('Review cancel/final sibling CAS and read-only graph preserve originals and missing new body; Confirm writes one graph insertion and one new local body, real execution returns 10 with parent/sibling continuation intact, and reopens')
  doc().scroll_into_view_if_needed();f.page.screenshot(path=str(f.case/('child-insert-'+mode+'.png')),full_page=True);assert not f.errors and not f.external,(f.errors,f.external);f.browser.close()
except BaseException:
 if getattr(f,'page',None):
  try:(f.case/'child-insert-failure.html').write_text(f.page.content());f.page.screenshot(path=str(f.case/'child-insert-failure.png'),timeout=10000)
  except Exception:pass
 raise
finally:
 (f.case/'child-insert-traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False));(f.case/'child-insert-checks.json').write_text(json.dumps(f.checks,ensure_ascii=False));f.stop()
print('V821_CHILD_INSERT',mode,f.case,flush=True)
