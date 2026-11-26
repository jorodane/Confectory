"""Actual nested private Logic Code reference insertion, isolated source and project guards."""
import ast,copy,json,shutil,sys
from pathlib import Path
from playwright.sync_api import expect,sync_playwright

fixture=Path(__file__).with_name('v821_frame_structure_ui.py')
setup=ast.parse(fixture.read_text()).body
exec(compile(ast.Module(body=setup[:next(i for i,n in enumerate(setup)if isinstance(n,ast.Try))],type_ignores=[]),str(fixture),'exec'),globals())
donor=f.n+'PrivateProbe'
marker=f.case/'private-call-run.txt'
(f.project/'PrivateProbe.celem').write_text(f'function {donor} (int amount) -> void {{provide {donor} with {donor}Body;}}')
(f.project/'PrivateProbeBody.celem').write_text(f'implementation {donor}Body for {donor} (int amount) -> void {{body common "PrivateProbe.csbody";}}')
(f.project/'PrivateProbe.csbody').write_text('global::System.Console.WriteLine("private-probe:"+amount);global::System.IO.File.WriteAllText('+json.dumps(str(marker))+',amount.ToString());')
manifest=f.project/'project.cproj'
manifest.write_text(manifest.read_text().rstrip().removesuffix('}')+'element PrivateProbe function "PrivateProbe.celem";element PrivateProbeBody implementation "PrivateProbeBody.celem";}')
x.physical={p:p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.parts}
original_graph=json.loads((f.project/t.graph_file).read_text())
other_project=f.case/'same ids other project'
shutil.copytree(f.project,other_project,ignore=shutil.ignore_patterns('.confectory','.build'))
other_bytes={p:p.read_bytes()for p in other_project.rglob('*')if p.is_file()}
try:
 f.start(0);f.invoke('select',dict(id=t.feature));f.invoke('saveDraft',{})
 checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
 with sync_playwright()as pw:
  expect.set_options(timeout=45000)
  f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  f.page=f.setup();f.page.set_viewport_size(dict(width=1900,height=1500))
  f.open_owner(f.n+'Target1')
  f.owner().locator('.object-title-description').fill('independent local input')
  peer=[(k,v)for k,v in f.pending()['schema']if '|'+f.n+'Target1|element|'in k]
  assert peer
  def peer_kept():
   assert all(dict(f.pending()['schema']).get(k)==v for k,v in peer)
  open_document();enter()
  original=read();assert original['documentFrameOrderBinding']['path']==frame_path
  add=doc().locator('[data-document-insert-call=inner]');expect(add).to_be_enabled()
  add.click();picker=f.page.get_by_role('dialog',name='블루프린트 노드 검색')
  candidate=picker.locator('[data-resource-feature="'+donor+'"]');expect(candidate).to_be_visible()
  picker.locator('[data-resource-close]').click();assert not pending()
  add.click();expect(candidate).to_be_visible();candidate.click()
  cell=doc().locator('[data-document-cell^="call_"]');expect(cell).to_be_visible();id=cell.get_attribute('data-document-cell')
  assert order()==['$entry','inner',id,'tail','$exit:return']
  doc().press('Control+z');expect(cell).to_have_count(0);assert not pending()
  doc().press('Control+y');expect(cell).to_be_visible()
  value=cell.locator('[data-document-value][data-document-port="field:amount"]')
  value.click();f.page.get_by_role('dialog',name='핀 값 선택').get_by_role('button',name='입력 · amount',exact=True).click()
  expect(value).to_contain_text('amount')
  held=pending();assert len(held)==4
  x.original();peer_kept();assert checkpoint.read_bytes()==before
  root_view();enter(peer_path)
  assert not doc().locator('[data-document-cell^="call_"]').count() and not doc().locator('[data-document-insert-call=inner]').count()
  assert pending()==held
  root_view();enter();assert order()==['$entry','inner',id,'tail','$exit:return'] and pending()==held
  path=f.project/t.graph_file;raw=path.read_bytes();path.write_bytes(raw+b' ')
  try:
   panel().locator('[data-bp-save]').click();f.idle()
   expect(panel().locator('.bp-status')).not_to_have_text('저장됨')
   assert all(dict(pending()).get(k)==v for k,v in held) and checkpoint.read_bytes()==before and path.read_bytes()==raw+b' '
  finally:path.write_bytes(raw)
  restart(1)
  if not doc().locator('[data-document-cell^="call_"]').count():enter()
  assert order()==['$entry','inner',id,'tail','$exit:return']
  panel().locator('[data-bp-save]').click();expect(panel().locator('.bp-status')).to_have_text('저장됨',timeout=120000);f.idle()
  x.original();peer_kept()
  row=next(n for n in read()['nodes']if n['id']==id)
  assert row['calledFeature']==donor and row['arguments'][0]['valueJson']=='{"input":"amount"}'
  assert len(read(other)['nodes'])==2
  r=review();r.locator('[data-reject]').click();expect(r).to_be_hidden();x.original()
  r=review()
  sibling=f.project/'Pair.peer.inner.node.json';sibling_raw=sibling.read_bytes();saved=checkpoint.read_bytes()
  sibling.write_bytes(sibling_raw+b' ')
  try:
   r.locator('#confirm').click();f.idle()
   assert sibling.read_bytes()==sibling_raw+b' ' and checkpoint.read_bytes()==saved and path.read_bytes()==raw
  finally:sibling.write_bytes(sibling_raw)
  if r.is_visible():r.locator('[data-reject]').click()
  r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle()
  written=json.loads(path.read_text());selected=chosen(written);node=next(n for n in selected['nodes']if n['id']==id)
  assert node['kind']=='call' and node['feature']==donor and node['arguments']=={'amount':{'input':'amount'}}
  assert next(e['to']for e in selected['edges']if e['from']=='inner')==id
  assert next(e['to']for e in selected['edges']if e['from']==id)=='tail'
  selected['nodes'].remove(node);selected['edges']=[e for e in selected['edges']if e['from']!=id]
  next(e for e in selected['edges']if e['from']=='inner')['to']='tail'
  assert written==original_graph
  assert all(p.read_bytes()==raw for p,raw in x.physical.items()if p not in (path,f.project/'PairBody.celem'))
  x.build('private-call',10,'body\nprivate-probe:7\ninside\nparent-tail\npeer-inner\npeer-tail\nafter\n10')

  restart(2)
  if not doc().locator('[data-document-cell^="call_"]').count():enter()
  assert order()==['$entry','inner',id,'tail','$exit:return'];peer_kept()
  f.checked('actual nested frame: call search, one local Undo/Redo, exact input, external conflict refusal, saved review and execution, cold reopen and unrelated local description input')
  f.page.close();f.stop()
  f.env['CONFECTORY_WEB_PROJECT']=str(other_project/'project.cproj')
  f.start(3);f.page=f.setup();f.page.set_viewport_size(dict(width=1900,height=1500));open_document();enter()
  assert order()==original_order and not pending()
  assert all(p.read_bytes()==raw for p,raw in other_bytes.items())
  f.checked('identical IDs in a separate project retain the original graph and files')
  f.page.close();f.stop()
  f.env['CONFECTORY_WEB_PROJECT']=str(manifest)
  f.start(4);f.page=f.setup();f.page.set_viewport_size(dict(width=1900,height=1500));f.idle()
  marker.unlink()
  f.page.get_by_role('button',name='프로젝트 실행',exact=True).click()
  expect(f.page.locator('.run-window:visible [data-run-frame]')).to_have_text('종료 코드 10',timeout=120000)
  assert marker.read_text()=='7'
  peer_kept()
  f.checked('ordinary project Run after returning executes the confirmed private call with 7')
  assert not f.errors and not f.external,(f.errors,f.external)
  f.browser.close()
except Exception:
 try:
  (f.case/'private-call-failure.html').write_text(f.page.content())
  f.page.screenshot(path=str(f.case/'private-call-failure.png'),timeout=5000)
 except Exception:pass
 raise
finally:
 (f.case/'private-call-checks.json').write_text(json.dumps(f.checks,ensure_ascii=False));(f.case/'private-call-traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False));f.stop()
print('V821_PRIVATE_CALL',f.case,flush=True)
