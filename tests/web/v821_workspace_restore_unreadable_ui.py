"""Synthetic permission failure is not a missing registration."""
from playwright.sync_api import sync_playwright,expect
import v821_property_window_reopen_ui as r
from editor_navigation import goto_editor
f,d=r.fixture,r.fallback;r.seed();expect.set_options(timeout=60000)
source=f.projects[0].parent/'private-source-PeerRecord.celem'
try:
 with sync_playwright() as p,p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']) as b:
  def page(n):
   f.start(n);p=b.new_page(viewport={'width':2000,'height':1200});p.route('**/*',lambda route:route.continue_() if route.request.url.startswith(f.origin+'/') else route.abort());goto_editor(p,f.url);return p
  def enter(p):p.locator('.project-card').filter(has=p.get_by_role('heading',name=d.FIRST,exact=True)).locator('[data-enter]').click();expect(p.locator('#title')).to_contain_text(d.FIRST)
  p=page(0);notes={}
  for name,folder in [(d.TARGET,'StockFolder'),(d.PEER,'PeerFolder'),('Extra1','ExtraFolder1')]:
   w,key=r.floating.open_properties(p,name,folder);value='Synthetic retained '+name;r.floating.property_value(w,'Note').fill(value);notes[key]=value
  p.evaluate('()=>confectoryFlushPresentation()');p.close();f.stop();f.env.pop('CONFECTORY_WEB_PROJECT',None)
  source.chmod(0)
  try:source.read_bytes();raise AssertionError('fixture is not unreadable')
  except PermissionError:pass
  p=page(1);enter(p);expect(p.locator('#workspace-save-state')).to_contain_text('복원 실패');print('PASS unreadable registration reports restoration failure, not missing owner',flush=True);assert '일부 편집창 복원 실패' not in p.locator('#workspace-save-state').inner_text();p.close();f.stop();source.chmod(0o600)
  p=page(2);enter(p);expect(p.locator('#project-menu')).to_be_enabled();
  for key,value in notes.items():expect(r.floating.property_value(p.locator(f'.window[data-key="{key}"]'),'Note')).to_have_value(value)
  f.original();print('PASS permission restored: exact three owners and retained input',flush=True)
finally:source.chmod(0o600);f.stop();print('evidence',f.root,flush=True)
