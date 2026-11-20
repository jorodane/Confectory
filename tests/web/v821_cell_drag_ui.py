"""Real Linux desktop mouse drag over the existing complete order/Undo/Save contract.
Positive movement uses browser mouse input, not synthetic drag events. Stale-token
refusal is explicitly synthetic. No mobile/Windows/full-UI claim.
"""
import ast,copy,json,stat,sys,time,uuid
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
mode=sys.argv[3]if len(sys.argv)>3 else'normal'
if mode in ['frame','branch']:
 fixture=Path(__file__).with_name('v821_'+('frame'if mode=='frame'else'branch')+'_structure_ui.py');body=ast.parse(fixture.read_text()).body
 exec(compile(ast.Module(body=body[:next(i for i,n in enumerate(body)if isinstance(n,ast.Try))],type_ignores=[]),str(fixture),'exec'),globals())
else:
 import v666_node_names_recovery_fixture as t
 f=t.f;x=t.x
 helper=Path(__file__).with_name('v821_function_document_ui.py');exec(compile(ast.Module(body=[n for n in ast.parse(helper.read_text()).body if isinstance(n,ast.FunctionDef)],type_ignores=[]),str(helper),'exec'),globals())
 graph=copy.deepcopy(t.definition)
 for id in ['middle','last']:graph['nodes'].append(dict(id=id,kind='code',control='next',intent=id,signature=dict(args=[],**{'return':'void'}),arguments={},implementation='Pair.'+id+'.node.json'))
 graph['edges']=[dict(**{'from':a,'port':'next','to':b})for a,b in zip(['body','after','middle','last'],['after','middle','last','exit:return'])]
 if mode=='dependency':
  after=next(n for n in graph['nodes']if n['id']=='after');after['signature']['args']=[dict(name='value',type='int')];after['arguments']={'value':{'node':'body'}}
 defs=f.metadata('featureBlueprintNodes',featureSource=t.base.function,graph=graph);assert defs['state']=='node-definitions',defs
 for node in graph['nodes']:
  p=f.project/node['implementation'];record=json.loads(p.read_text())if p.exists()else dict(schema=1,node=node['id'],source='global::System.Console.WriteLine("'+node['id']+'");')
  record['definitionHash']=next(n['definitionHash']for n in defs['nodes']if n['id']==node['id']);p.write_text(json.dumps(record,ensure_ascii=False))
 (f.project/t.graph_file).write_text(json.dumps(graph,ensure_ascii=False));x.physical={p:p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.parts}
source_modes={p:stat.S_IMODE(p.stat().st_mode)for p in (x.physical if hasattr(x,'physical')else t.physical)}
def cell(id):return doc().locator('[data-document-cell="'+id+'"]')
def grip(id):return doc().locator('[data-document-drag="'+id+'"]')
def flow():return doc().locator('[data-document-panel="case:positive"]')if mode=='branch'else doc()
def ids():return flow().locator(':scope>[data-document-cell]').evaluate_all('(els)=>els.map(e=>e.dataset.documentCell)').copy()
def logical_ids():return [id for id in ids()if not id.startswith('$')]
def wait_order(wanted):
 deadline=time.monotonic()+10
 while time.monotonic()<deadline:
  if logical_ids()==wanted:return
  f.page.wait_for_timeout(25)
 assert logical_ids()==wanted,(logical_ids(),wanted)
def unchanged():
 x.original();assert all(stat.S_IMODE(p.stat().st_mode)==m for p,m in source_modes.items())
def folded():
 # Each click rerenders the document; find the next current element again.
 for _ in range(128):
  chosen=next((b for b in doc().locator('[data-document-fold][aria-expanded=true]').all()if b.is_visible()and not b.locator('xpath=ancestor::article[1]').locator(':scope>.fd-cell-content>.fd-branches').count()),None)
  if chosen is None:break
  chosen.click();f.page.wait_for_timeout(30)
 else:raise AssertionError('fold setup did not settle')
 f.page.wait_for_timeout(80)
def enlarge():
 # Real resize gesture; do not bypass the application's layout with DOM styles.
 handle=panel().locator('[data-resize=se]');r=handle.bounding_box()
 if r:
  f.page.mouse.move(r['x']+r['width']/2,r['y']+r['height']/2);f.page.mouse.down();f.page.mouse.move(1390,1120,steps=12);f.page.mouse.up();f.page.wait_for_timeout(80)
def start_drag(id,disabled=False):
 print("DRAG_START",id,"disabled",grip(id).is_disabled(),"order",logical_ids(),flush=True)
 if not disabled:expect(grip(id)).to_be_enabled()
 grip(id).scroll_into_view_if_needed();grip(id).evaluate("el=>el.addEventListener('dragstart',e=>{window.lastDocumentCellToken=e.dataTransfer.getData('application/x-confectory-document-cell')},{once:true})");r=grip(id).bounding_box();assert r
 f.page.mouse.move(r['x']+r['width']/2,r['y']+r['height']/2);f.page.mouse.down();f.page.mouse.move(r['x']+r['width']/2+12,r['y']+r['height']/2+8,steps=6);f.page.wait_for_timeout(80)
def hover(id,after=False):
 r=cell(id).bounding_box();assert r
 f.page.mouse.move(r['x']+r['width']/2,r['y']+(r['height']-7 if after else 7),steps=15);f.page.wait_for_timeout(350)
def move(id,target,after=False,valid=True,capture=False,disabled=False):
 start_drag(id,disabled);hover(target,after);marker=f.page.locator('.fd-cell-drop-marker')
 if valid:
  expect(marker).to_have_count(1);assert marker.bounding_box()['width']>100
  if capture:f.page.screenshot(path=str(f.case/'desktop-drag-placement.png'),full_page=True)
 else:expect(marker).to_have_count(0)
 f.page.mouse.up();f.idle();f.page.wait_for_timeout(100);expect(marker).to_have_count(0)
def local_undo(redo=False):
 doc().locator('.fd-document-title').click();doc().press('Control+y'if redo else'Control+z');f.page.wait_for_timeout(100)
def restart_drag(i):
 f.pending();f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size(dict(width=1800,height=1400));f.idle();open_document()
def stale_drop(id,token):
 # Refusal only: a completed drag's token cannot authorize a later frame/branch.
 grip(id).evaluate('''(el,token)=>{const dt=new DataTransfer();dt.setData('application/x-confectory-document-cell',token);el.dispatchEvent(new DragEvent('drop',{bubbles:true,dataTransfer:dt,clientX:el.getBoundingClientRect().x,clientY:el.getBoundingClientRect().y}));}''',token);f.page.wait_for_timeout(80)
try:
 f.start(0);f.invoke('select',dict(id=t.feature));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
 with sync_playwright()as pw:
  expect.set_options(timeout=45000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size(dict(width=1800,height=1400));open_document();enlarge()
  if mode=='frame':enter()
  folded();initial=logical_ids();assert len(initial)>=2
  if mode=='dependency':
   baseline=t.read();move('after','body',valid=False);wait_order(initial);assert not pending();move('body','after',after=True,valid=False);wait_order(initial);assert not pending()and checkpoint.read_bytes()==before;unchanged()
   # A drag uses the same source-bound engine order validation as the buttons.
   q=dict(action='authorBatch',id=t.graph,attempt=uuid.uuid4().hex,checkpointHash=baseline['checkpointHash'],sourceProof=x.proof(baseline),edits=[dict(action='entry',node='$entry',to='after')]+[dict(action='route',node=a,port='next',to=b)for a,b in zip(['after','body','middle','last'],['body','middle','last','exit:return'])]);f.invoke('blueprint',q,False);assert not pending()and checkpoint.read_bytes()==before;unchanged();x.build('dependent-drag-unchanged',10,'body\nafter\nmiddle\nlast\n10');f.checked('actual desktop drags cannot move a consumer above its producer or producer below its consumer; no marker/mutation, forged engine order refuses and original execution is unchanged')
  elif mode in ['frame','branch']:
   first,last=initial[0],initial[-1];move(last,first,capture=True);wait_order([last]+initial[:-1]);held=pending();assert held;unchanged();assert checkpoint.read_bytes()==before
   local_undo();wait_order(initial);local_undo(True);wait_order([last]+initial[:-1]);local_undo();wait_order(initial);assert not pending()
   # The original button and keyboard path remain available in this exact scope.
   cell(last).locator("[data-document-fold]").click();button=flow().locator('[data-document-up="'+last+'"]');expect(button).to_be_visible();button.click();f.idle();wait_order([last]+initial[:-1]);local_undo();wait_order(initial);folded()
   start_drag(last)
   if mode=='branch':hover('choose')
   else:
    r=panel().locator('.bp-breadcrumbs').bounding_box();f.page.mouse.move(r['x']+12,r['y']+12,steps=10);f.page.wait_for_timeout(60)
   expect(f.page.locator('.fd-cell-drop-marker')).to_have_count(0);f.page.mouse.up();wait_order(initial);assert not pending()and checkpoint.read_bytes()==before;unchanged();token=f.page.evaluate('window.lastDocumentCellToken');assert token
   if mode=='frame':
    root_view();enter('other/nest');folded();other_before=logical_ids();stale_drop('inner',token);wait_order(other_before);assert not pending();doc().locator('[data-document-name=inner]').fill('다른 frame 입력 보존');doc().locator('.fd-document-title').click();held=pending();stale_drop('inner',token);assert pending()==held;unchanged();f.checked('same full-path child mouse drag and button/Undo use the original order path; breadcrumb/outside drop cancels, and a synthetic completed token cannot move another frame with duplicate local IDs or overwrite its input')
   else:
    # This cell takes a root input. Same-case order may change, but its execution condition may not.
    start_drag(last);r=doc().locator('[data-document-branch="case:negative"]').bounding_box();x_pos=r['x']+r['width']/2;y_pos=r['y']+r['height']/2
    f.page.mouse.move(x_pos+3,y_pos,steps=10);f.page.mouse.move(x_pos,y_pos,steps=3)
    expect(f.page.locator('.fd-cell-drop-marker')).to_have_count(0);f.page.mouse.up();wait_order(initial);assert not pending() and checkpoint.read_bytes()==before;unchanged()
    f.checked('same-case mouse drag and button/Undo work with a root input; dropping that cell on the owner or another case preserves the original route and binding')
  else:
   assert initial==['body','after','middle','last']
   move('last','body',capture=True);wait_order(['last','body','after','middle']);assert len(pending())==5;unchanged();assert checkpoint.read_bytes()==before
   local_undo();wait_order(initial);assert not pending();local_undo(True);wait_order(['last','body','after','middle']);local_undo();wait_order(initial)
   move('body','middle',after=True);wait_order(['after','middle','body','last']);local_undo();wait_order(initial)
   move('body','$exit:return');wanted=['after','middle','last','body'];wait_order(wanted);held=pending();assert len(held)==5;unchanged();assert checkpoint.read_bytes()==before
   panel().get_by_role('tab',name='블루프린트 보기',exact=True).click();expect(panel().locator('[data-bp-node=body]')).to_be_visible();assert pending()==held;panel().get_by_role('tab',name='논리 코드',exact=True).click();wait_order(wanted);assert pending()==held;folded()
   f.checked('real mouse drag moves an ordinary cell up, down and to the original terminal; placement marker is visible and each complete order is one private Undo/Redo edit with no source/checkpoint write')
   start_drag('last');hover('after');expect(f.page.locator('.fd-cell-drop-marker')).to_have_count(1);f.page.keyboard.press('Escape');f.page.mouse.up();f.page.wait_for_timeout(100);wait_order(wanted);assert pending()==held;expect(f.page.locator('.fd-cell-drop-marker')).to_have_count(0)
   start_drag('last');r=panel().locator('.window-title').bounding_box();f.page.mouse.move(r['x']+20,r['y']+8,steps=10);f.page.mouse.up();wait_order(wanted);assert pending()==held;expect(f.page.locator('.fd-cell-drop-marker')).to_have_count(0)
   move('last','last',valid=False);wait_order(wanted);assert pending()==held;unchanged();assert checkpoint.read_bytes()==before
   # Existing buttons and their keyboard activation, plus accessible grip arrows.
   cell('body').locator('[data-document-fold]').click();up=doc().locator('[data-document-up=body]');expect(up).to_be_visible();expect(up).to_be_enabled();up.focus();f.page.set_viewport_size(dict(width=1801,height=1400));f.page.wait_for_timeout(100);assert up.evaluate('el=>document.activeElement===el');f.page.keyboard.press('Enter');f.idle();wait_order(['after','middle','body','last']);local_undo();wait_order(wanted);folded()
   grip('body').focus();f.page.keyboard.press('Alt+ArrowUp');f.idle();wait_order(['after','middle','body','last']);local_undo();wait_order(wanted)
   f.checked('Escape, outside/invalid/self drop preserve exact pending inputs and order; existing Enter/button, Ctrl+Z/Y and grip Alt+arrows share the same movement path')
   checkpoint.chmod(0o400)
   try:save();assert retained(held)and checkpoint.read_bytes()==before;unchanged()
   finally:checkpoint.chmod(0o600)
   save();assert not pending()and t.read()['entry']=='after';unchanged()
   for direction,entry in [('undo','body'),('redo','after')]:
    history=f.invoke('draftHistory',dict(action='inspect'))['result']['result'];assert f.invoke('draftHistory',dict(action=direction,token=history[direction]['token']))['result']['result']['accepted'];assert t.read()['entry']==entry
   f.invoke('saveDraft',{});restart_drag(1);wait_order(wanted);assert not pending();unchanged();f.checked('drag order uses the existing atomic Save/CAS and shared Undo/Redo; checkpoint permission failure retains input and cold reopening retains the accepted chain')
   r=review();r.locator('[data-reject]').click();unchanged();r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();x.build('desktop-drag-order',10,'after\nmiddle\nlast\nbody\n10');assert all(p.read_bytes()==raw for p,raw in x.physical.items()if p.name!=t.graph_file);restart_drag(2);wait_order(wanted)
   doc().locator('[data-document-name=after]').fill('드래그 거절 뒤 이름 입력 α');doc().locator('.fd-document-title').click();held=pending();expect(grip('last')).to_be_disabled();move('last','after',valid=False,disabled=True);wait_order(wanted);assert pending()==held;restart_drag(3);wait_order(wanted);assert pending()==held;expect(doc().locator('[data-document-name=after]')).to_have_value('드래그 거절 뒤 이름 입력 α');f.checked('explicit Review/Confirm and rebuilt engine execute only the reordered chain; later private text disables drag and survives attempted drag plus cold without loss')
  f.page.screenshot(path=str(f.case/('cell-drag-'+mode+'.png')),full_page=True);assert not f.errors and not f.external,(f.errors,f.external);f.browser.close()
except BaseException:
 if getattr(f,'page',None):
  try:(f.case/'drag-failure.html').write_text(f.page.content());f.page.screenshot(path=str(f.case/'drag-failure.png'),timeout=10000)
  except Exception:pass
 raise
finally:
 (f.case/'drag-traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False));(f.case/'drag-checks.json').write_text(json.dumps(f.checks,ensure_ascii=False));f.stop()
print('V821_CELL_DRAG',mode,f.case,flush=True)
