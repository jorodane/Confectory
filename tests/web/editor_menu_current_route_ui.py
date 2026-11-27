"""Real current workspace Browser action, synthetic local projects only.
Run with the normal EditorHome build report and current authoring host:
  python tests/web/editor_menu_current_route_ui.py REPO BUILD_REPORT
Pass base as an optional third argument only to reproduce the old pin failure.
"""
import json,sys,shutil
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
import v821_property_window_reopen_ui as r
from editor_navigation import goto_editor
f,d=r.fixture,r.fallback
r.seed();mode=sys.argv[3] if len(sys.argv)>3 else "candidate";library=f.root/'schema-editing';shutil.copytree(f.repo/'packs/schema-editing',library)
for manifest in f.projects:
 action=manifest.parent/'Menu.celem';action.write_text((f.repo/'examples/editor-context-actions/MetadataProposal.celem').read_text().replace('Example.EditorContextActions::MetadataProposal',d.NS+'::Menu'))
 manifest.write_text(manifest.read_text().rstrip()[:-1]+' registry Confectory.SchemaEditing '+json.dumps(str(library/'pack.cpack'))+'; dependency Confectory.SchemaEditing version "0.1.0"; element Menu object "Menu.celem"; }\n')
 for file in (manifest,action):f.before[str(file)]=file.read_bytes()
try:
 with sync_playwright() as p,p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']) as b:
  f.start(0);page=b.new_page(viewport={'width':2000,'height':1200});page.route('**/*',lambda route:route.continue_() if route.request.url.startswith(f.origin+'/') else route.abort());goto_editor(page,f.url)
  browser=r.browser_window(page);r.choose_tree_location(browser,f'[data-tree-id="{d.NS}::StockFolder"]');r.search(browser,d.LABEL,d.TARGET)
  item=browser.locator(f'[data-object="{d.NS}::{d.TARGET}"]');item.click(button='right');page.locator('.context-menu').get_by_role('button',name='스키마 열기',exact=True).click();expect(page.locator('.window[data-key="schema"] [data-property-value]').first).to_be_editable(timeout=30000);page.locator('.window[data-key="schema"] [data-close]').click();expect(page.locator('#project-menu')).to_be_enabled(timeout=30000)
  saved=f.state()['draft'];assert saved['id']==d.NS+'::'+d.TARGET,saved['id']
  def menu(label):

   for attempt in range(3):
    expect(page.locator('#project-menu')).to_be_enabled(timeout=30000)
    item.click(button='right');button=page.locator('.context-menu').get_by_role('button',name=label,exact=True);failure=page.locator('.context-menu').get_by_role('button',name='등록 기능 조회 실패 · 다시 여세요',exact=True);expect(button.or_(failure)).to_be_visible(timeout=30000)
    if button.is_visible():return button
    failure.click();print('menu error:',page.locator('#status').inner_text(),flush=True);page.wait_for_timeout(100)
   raise AssertionError('menu unavailable')
  if mode=='base':
   menu('등록 기능 · 메타데이터 변경안 · 미지원');print('PASS baseline actual menu unavailable',flush=True)
  else:
   menu('등록 기능 · 메타데이터 변경안').click();dialog=page.get_by_role('dialog',name='메타데이터 변경안');expect(dialog).to_be_visible();dialog.locator('[data-action-field]').fill('editorName');dialog.locator('[data-action-value]').fill('"Fixture proposal"');dialog.locator('[data-action-invoke]').click();expect(dialog).to_have_attribute('data-action-status','completed',timeout=30000);expect(dialog.locator('[data-action-result]')).to_contain_text('Fixture proposal');assert f.state()['draft']==saved;dialog.locator('[data-close]').click(); print('PASS current menu actual typed result, draft and source unchanged',flush=True)
   body=library/'Call.csbody';raw=body.read_bytes();body.write_bytes(raw+b'\n// Synthetic changed exact body\n');menu('등록 기능 · 메타데이터 변경안 · 미지원');body.write_bytes(raw);print('PASS modified body remains unavailable',flush=True)
  f.original()
finally:f.stop();print('evidence',f.root,flush=True)
