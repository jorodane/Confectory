"""A saved layout without a visible schema restores its cursor, not a hidden schema.
Run against the ordinary Linux EditorHome build with REPO BUILD_REPORT.
"""
from playwright.sync_api import sync_playwright,expect
import v821_object_fallback_roundtrip_ui as d
from editor_navigation import goto_editor
f=d.fixture;d.seed();expect.set_options(timeout=60000)
try:
 with sync_playwright() as p,p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']) as b:
  def page_for_host(n):
   f.start(n);page=b.new_page(viewport={'width':1800,'height':1200});page.route('**/*',lambda route:route.continue_() if route.request.url.startswith(f.origin+'/') else route.abort());goto_editor(page,f.url);return page
  def enter(page,name):
   page.locator('.project-card').filter(has=page.get_by_role('heading',name=name,exact=True)).locator('[data-enter]').click();expect(page.locator('#title')).to_contain_text(name);expect(page.locator('#project-menu')).to_be_enabled()
  page=page_for_host(0);editor,_=d.open_from_search(page,d.FIRST,d.PEER,'41',require_host=True);expected=f.state()['draft']['id'];assert expected==d.NS+'::'+d.PEER
  for key in page.locator('.window:visible').evaluate_all('rows=>rows.map(w=>w.dataset.key).filter(Boolean)'):
   w=page.locator(f'.window[data-key="{key}"]:visible');close=w.locator('[data-close]')
   if w.count() and close.count():close.first.click()
  if page.locator('.window[data-key="schema"]:visible').count():page.locator('.window[data-key="schema"] [data-close]').click()
  expect(page.locator('.window[data-key="schema"]')).not_to_be_visible();page.evaluate('()=>confectoryFlushPresentation()');page.close();f.stop();f.env.pop('CONFECTORY_WEB_PROJECT',None)
  schema=f.projects[0].parent/'private-source-StockInfo.celem';schema.write_text(schema.read_text().rstrip()[:-1]+' field RestartFlag single general string;\n}\n');f.before[str(schema)]=schema.read_bytes()
  page=page_for_host(1);enter(page,d.FIRST);state=f.state();assert state['draft']['id']==expected,state['draft']['id'];assert state.get('schema') is None,state.get('schema');expect(page.locator('.window[data-key="schema"]')).not_to_be_visible();print('PASS cold empty layout uses exact saved cursor, no hidden schema',flush=True)
  editor,_=d.open_from_search(page,d.FIRST,d.TARGET,d.BEFORE,require_host=True);expect(d.field(editor,'RestartFlag')).to_be_visible();note=d.field(editor,'Note').get_by_label('Note 기본값',exact=True);note.fill('Retained after empty layout');expect(note).to_have_value('Retained after empty layout');d.leave_to_home(page);enter(page,d.SECOND);other,_=d.open_from_search(page,d.SECOND,d.TARGET,'19',require_host=True);expect(d.field(other,'RestartFlag')).to_have_count(0);d.leave_to_home(page);enter(page,d.FIRST);expect(note).to_have_value('Retained after empty layout');f.original();print('PASS actual first property uses external schema, unsaved input and same-ID project isolation',flush=True)
finally:f.stop();print('evidence',f.root,flush=True)
