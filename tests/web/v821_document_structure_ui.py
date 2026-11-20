"""Real document structure, source-bound atomic Save, next semantics and guards."""
import ast,copy,json,sys,time,uuid
from playwright.sync_api import sync_playwright,expect
import v666_node_names_recovery_fixture as t
f=t.f;x=t.x;mode=sys.argv[3]if len(sys.argv)>3 else'normal'
# Reuse only the existing user-flow helpers, without running their test body.
helpers=ast.parse((f.repo/'tests/web/v821_function_document_ui.py').read_text())
exec(compile(ast.Module(body=[node for node in helpers.body if isinstance(node,ast.FunctionDef)],type_ignores=[]),str(f.repo/'tests/web/v821_function_document_ui.py'),'exec'),globals())
if mode=='dependency':
 graph=copy.deepcopy(t.definition);after=next(node for node in graph['nodes']if node['id']=='after');after['signature']['args']=[dict(name='value',type='int')];after['arguments']={'value':{'node':'body'}}
 definitions=f.metadata('featureBlueprintNodes',featureSource=t.base.function if hasattr(t,'base')else x.function,graph=graph)
 (f.project/t.graph_file).write_text(json.dumps(graph,ensure_ascii=False))
 for node,file in [('body',t.base.source_file),('after','Pair.after.node.json')]:
  path=f.project/file;record=json.loads(path.read_text());record['definitionHash']=next(n['definitionHash']for n in definitions['nodes']if n['id']==node);path.write_text(json.dumps(record,ensure_ascii=False))
 x.physical={p:p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.parts}

def order():return doc().locator('[data-document-cell]').evaluate_all('(els)=>els.map(el=>el.dataset.documentCell)')
def exact_sources():return {p:p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.parts}
try:
 f.start(0);f.invoke('select',{'id':t.feature});f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
 with sync_playwright()as pw:
  expect.set_options(timeout=45000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});open_document();baseline=t.read();initial=order()
  doc().locator('[data-document-up=after]').click();f.idle()
  if mode=='dependency':
   assert order()==initial and not pending();assert t.read()['nodes']==baseline['nodes'];x.original();assert checkpoint.read_bytes()==before
   forged=dict(action='authorBatch',id=t.graph,checkpointHash=baseline['checkpointHash'],sourceProof=x.proof(baseline),attempt=uuid.uuid4().hex,edits=[dict(action='entry',node='$entry',to='after'),dict(action='route',node='after',port='next',to='body'),dict(action='route',node='body',port='next',to='exit:return')])
   f.invoke('blueprint',forged,False);assert t.read()['nodes']==baseline['nodes'];assert checkpoint.read_bytes()==before;x.original();f.checked('declared producer dependencies reject unsafe document move before mutation and reject a forged backend candidate atomically')
  else:
   assert order()==['$entry','after','body','$exit:return'];held=pending();assert len(held)==3;assert t.read()['entry']==baseline['entry'];x.original()
   doc().locator('.fd-document-title').click();doc().press('Control+z');expect(doc().locator('[data-document-cell]').nth(1)).to_have_attribute('data-document-cell','body');doc().press('Control+y');expect(doc().locator('[data-document-cell]').nth(1)).to_have_attribute('data-document-cell','after')
   panel().get_by_role('tab',name='블루프린트 보기',exact=True).click();expect(panel().locator('[data-bp-node=body]')).to_be_visible();panel().get_by_role('tab',name='논리 코드',exact=True).click();restart(1);assert order()==['$entry','after','body','$exit:return'];assert pending()==held;x.original();f.checked('document move changes the shared next projection, supports private Undo/Redo and cold recovery, and preserves authored source and legacy view')
   checkpoint.chmod(0o400)
   try:save();assert retained(held);assert checkpoint.read_bytes()==before;assert t.read()['entry']==baseline['entry'];x.original()
   finally:checkpoint.chmod(0o600)
   save();assert not pending();assert t.read()['entry']=='after';x.original();saved_nodes=t.read()['nodes']
   for direction,wanted in [('undo',baseline['entry']),('redo','after')]:
    h=f.invoke('draftHistory',dict(action='inspect'))['result']['result'];assert f.invoke('draftHistory',dict(action=direction,token=h[direction]['token']))['result']['result']['accepted'];assert t.read()['entry']==wanted
   f.invoke('saveDraft',{});restart(2);assert order()==['$entry','after','body','$exit:return'];f.checked('complete root cell order checkpoints atomically; permission failure retains live graph/checkpoint/inputs, and shared history plus cold restores the accepted chain')
   r=review();r.locator('[data-reject]').click();x.original();r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();x.build('document-order',10,'after\nbody\n10');assert all(p.read_bytes()==raw for p,raw in x.physical.items()if p.name!=t.graph_file);first_confirm=exact_sources();f.checked('Review cancellation preserves originals; confirmed order executes after then body in a rebuilt real engine without rewriting node code/contracts')
   doc().locator('[data-document-add=after]').click();f.idle();created=[node for node in order()if node.startswith('cell_')];assert len(created)==1;created=created[0];assert len(pending())==6;assert t.read()['entry']=='after';assert exact_sources()==first_confirm
   doc().locator('[data-document-code="'+created+'"]').click();dialog=f.page.locator('.bp-script-dialog');source=dialog.locator('[data-code-source]');body=dialog.locator('[data-code-region=body]').text_content();source.evaluate('(el,text)=>{el.focus();const start=el.value.indexOf(text);if(start<0)throw Error("Editable body missing");el.setSelectionRange(start,start+text.length)}',body);f.page.keyboard.insert_text('global::System.Console.WriteLine("inserted");\nreturn;');assert 'inserted' in dialog.locator('[data-code-region=body]').text_content();dialog.locator('[data-code-save]').click();f.idle();held=pending();restart(3);assert order()==['$entry','after',created,'body','$exit:return'];assert pending()==held;assert exact_sources()==first_confirm
   save();assert not pending();assert next(node for node in t.read()['nodes']if node['id']==created)['source'].find('inserted')>=0;assert exact_sources()==first_confirm
   r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();x.build('document-insert',10,'after\ninserted\nbody\n10');assert all(p.read_bytes()==raw for p,raw in first_confirm.items()if p.name!=t.graph_file);restart(4);assert order()==['$entry','after',created,'body','$exit:return'];f.checked('document inserts a real void C# cell into the shared chain; code editing, cold pending recovery, atomic Save and Confirm execute the new cell while preserving existing sources')
  f.page.screenshot(path=str(f.case/('document-structure-'+mode+'.png')),full_page=True);assert not f.errors and not f.external,(f.errors,f.external);f.browser.close()
finally:
 (f.case/'structure-traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False));(f.case/'structure-checks.json').write_text(json.dumps(f.checks,ensure_ascii=False));f.stop()
print('V821_DOCUMENT_STRUCTURE',mode,f.case,flush=True)
