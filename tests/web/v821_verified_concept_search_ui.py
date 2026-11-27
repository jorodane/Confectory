"""Current-project verified search rejects changed sources without displaying stale rows.

Run with REPO BUILD_REPORT 40|400. Uses the existing disposable project fixture.
"""
from playwright.sync_api import expect,sync_playwright
import v821_warm_source_refresh_ui as w
f=w.fixture
w.seed();f.start(0)
try:
 with sync_playwright() as p,p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']) as b:
  expect.set_options(timeout=90000)
  page=f.setup(b);w.enter(page,w.FIRST);window=w.browser_window(page)
  seen=[]
  def response(r):
   try:
    q=r.request.post_data_json
    if q.get('endpoint')=='verifiedConceptSearch' and q.get('op')=='observe':seen.append(r.json()['result']['status'])
   except Exception:pass
  page.on('response',response)
  w.search(window,w.SAME,'LookupObject');assert seen[-1]=='ready',seen
  w.enter(page,w.SECOND);window=w.browser_window(page);w.search(window,'대조 표식','LookupObject')
  w.enter(page,w.FIRST);window=w.browser_window(page)
  expect(window.get_by_role('textbox',name='의미 객체 검색',exact=True)).to_have_value(w.SAME)
  expect(window.locator(f'[data-object="{w.NS}::LookupObject"]')).to_be_visible()
  w.search(window,w.SAME,'LookupObject');assert seen[-1]=='ready',seen
  print('PASS retained query restored from new activation',flush=True)
  root=window.locator('.browser-file-pane')
  field=window.get_by_role('textbox',name='의미 객체 검색',exact=True)
  button=window.get_by_role('button',name='검색 확정',exact=True)
  source=f.projects[0].parent/'private-source-LookupObject.celem'
  schema=f.projects[0].parent/'private-source-LookupInfo.celem'
  for mode,path in [('rename',source),('schema',schema),('permission',source),('missing',source)]:
   data=path.read_bytes();permissions=path.stat().st_mode
   if mode=='rename':path.write_text(path.read_text().replace(w.SAME,'Active external rename'))
   elif mode=='schema':path.write_text(path.read_text().replace('string','long'))
   elif mode=='permission':path.chmod(0)
   else:path.unlink()
   try:
    before=len(seen);field.fill('LookupObject');button.click()
    expect(root).to_contain_text('원본이 변경되었습니다. 검색을 다시 적용하세요.')
    expect(window.locator('[data-tree-source-invalid]')).to_be_visible()
    expect(window.locator(f'[data-tree-id="{w.NS}::LookupObject"]')).to_have_count(0)
    expect(window.locator('[data-object]')).to_have_count(0)
    assert len(seen)>before and seen[-1]=='stale',(mode,seen)
    print('PASS active source invalidation',mode,flush=True)
   finally:
    if mode=='permission':path.chmod(permissions)
    else:path.write_bytes(data)
   w.search(window,w.SAME,'LookupObject');assert seen[-1]=='ready',seen
  source.write_text(source.read_text().replace(w.SAME,'Active external rename'));f.before[str(source)]=source.read_bytes()
  w.enter(page,w.SECOND);window=w.browser_window(page);w.search(window,'대조 표식','LookupObject')
  w.enter(page,w.FIRST);window=w.browser_window(page);w.search(window,'Active external rename','LookupObject')
  editor=w.property_editor(window,'Active external rename');expect(editor.get_by_label('Note 기본값',exact=True)).to_have_value('Baseline Note')
  f.original();assert not f.errors and not f.external
  print('PASS active stale result hidden, peer same-ID isolated, reentry shows fresh label and editable value',flush=True)
finally:
 f.stop();print('evidence',f.root,flush=True)
