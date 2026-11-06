"""Actual engine presentation lifecycle; generated projects, no source transactions."""
import json,sys,traceback
from playwright.sync_api import sync_playwright,expect
import v666_finder_content_fixture as f
mode=sys.argv[3];page=None
zoom=lambda:page.locator('#workspace [data-workspace-zoom]')
menu=lambda:page.get_by_role('dialog',name='화면 배율',exact=True)
def opened():
 zoom().click();expect(menu()).to_be_visible();return menu()
def at(value):expect(zoom()).to_have_text(str(value)+'%')
def set_zoom(value):
 opened().locator('[data-zoom-preset="'+str(value)+'"]').click();at(value);menu().locator('[data-zoom-value]').press('Escape')
def capture():
 menu().evaluate('''m=>{const input=m.querySelector('[data-zoom-value]'),slider=m.querySelector('[data-zoom-slider]'),preset=m.querySelector('[data-zoom-preset="400"]');globalThis.__retiredZoom={menu:m,input,slider,preset,open:document.querySelector('[data-workspace-zoom]').onclick,blur:input.onblur,enter:input.onkeydown,slide:slider.oninput,click:preset.onclick};}''')
def late():
 page.evaluate('''()=>{const r=__retiredZoom;r.input.value='425';r.slider.value='475';r.slide({target:r.slider});r.click();r.blur();r.enter({key:'Enter',preventDefault(){},stopPropagation(){}});}''')
def flush():page.evaluate('()=>confectoryFlushPresentation()')
def guards():
 f.original();assert not f.errors and not f.external,(f.errors,f.external)
 forbidden={'editDraft','saveDraft','reviewDraft','confirmDraft','confirm','confirmGroup','edit','authorBatch','runProject','runWindow','nodeTask','startAI'}
 assert not forbidden.intersection(r.get('endpoint')for r in f.requests)
def repeated():
 set_zoom(150);opened();capture();menu().locator('[data-zoom-value]').fill('425');menu().locator('[data-zoom-value]').press('Escape');at(150)
 opened();menu().locator('[data-zoom-value]').fill('200');late()
 if mode=='baseline':
  at(400);f.checked('published Workspace retired controls change the reopened menu scale from 150 to 400; stale slider/preset/blur/Enter callbacks reproduce cross-menu mutation');return
 at(150);expect(menu().locator('[data-zoom-value]')).to_have_value('200');menu().locator('[data-zoom-value]').press('Enter');at(200);menu().locator('[data-zoom-value]').press('Escape')
 for _ in range(3):
  opened();capture();menu().locator('[data-zoom-value]').fill('300');menu().locator('[data-zoom-value]').press('Escape');late();at(200);expect(menu()).to_have_count(0)
 opened().locator('[data-zoom-value]').fill('900');menu().locator('[data-zoom-value]').press('Enter');at(500);menu().locator('[data-zoom-value]').press('Escape')
 opened().locator('[data-zoom-slider]').evaluate("el=>{el.value='400';el.dispatchEvent(new Event('input',{bubbles:true}));}");at(400);page.locator('#chat-input').click();expect(menu()).to_have_count(0)
 f.checked('retired slider/preset/blur/Enter cannot apply to a reopened menu; active Enter, Escape, slider, outside click and 500% clamp retain authored behavior')
def scope(browser):
 global page
 page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(f.projects[1]);f.start(1);page=f.setup(browser);second=f.state()['listingId'];set_zoom(75);flush()
 page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(f.projects[0]);f.start(2);page=f.setup(browser);first=f.state()['listingId'];page.locator('#chat-input').fill('프로젝트 A의 확대와 별도 개인 입력');set_zoom(300);flush();opened();capture();menu().locator('[data-zoom-value]').fill('450')
 f.call('leaveProject',{});expect(page.locator('.home-grid')).to_be_visible();expect(menu()).to_have_count(0);late();page.evaluate('()=>__retiredZoom.open()');expect(menu()).to_have_count(0)
 f.call('openProject',{'id':second});expect(page.locator('.work-body')).to_be_visible();at(75);page.evaluate('()=>__retiredZoom.open()');expect(menu()).to_have_count(0);opened();menu().locator('[data-zoom-value]').fill('125');late();at(75);expect(menu().locator('[data-zoom-value]')).to_have_value('125');menu().locator('[data-zoom-value]').press('Enter');at(125);menu().locator('[data-zoom-value]').press('Escape');page.locator('#chat-input').fill('프로젝트 B의 별도 입력');flush();guards()
 f.checked('native ProjectContext leave cancels uncommitted zoom; old callbacks cannot mutate home or B with matching window IDs, current B controls still work')
 f.call('leaveProject',{});f.call('openProject',{'id':first});expect(page.locator('.work-body')).to_be_visible();at(300);expect(page.locator('#chat-input')).to_have_value('프로젝트 A의 확대와 별도 개인 입력');late();at(300);flush()
 page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(f.projects[1]);f.start(3);page=f.setup(browser);at(125);expect(page.locator('#chat-input')).to_have_value('프로젝트 B의 별도 입력');expect(menu()).to_have_count(0)
 f.checked('A→B→A and B engine cold restore only each project’s accepted zoom/private input; no popup or discarded numeric draft is restored')
try:
 f.start(0)
 with sync_playwright()as p:
  expect.set_options(timeout=60000);browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=f.setup(browser)
  page.locator('#chat-input').fill('확대 중 보존할 개인 입력 😀');repeated();expect(page.locator('#chat-input')).to_have_value('확대 중 보존할 개인 입력 😀')
  if mode=='scope':scope(browser)
  elif mode=='normal':
   flush();page.close();f.stop();f.start(1);page=f.setup(browser);at(400);expect(menu()).to_have_count(0);expect(page.locator('#chat-input')).to_have_value('확대 중 보존할 개인 입력 😀');f.checked('engine cold restores committed 400% and private input, no stale menu or discarded draft')
  elif mode!='baseline':raise AssertionError(mode)
  guards();page.screenshot(path=str(f.root/('zoom-lifetime-'+mode+'.png')));page.close();browser.close()
except Exception as e:
 try:page.screenshot(path=str(f.root/'failure.png'));(f.root/'failure.html').write_text(page.content())
 except Exception:pass
 (f.root/'failure.json').write_text(json.dumps(dict(error=repr(e),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:f.save_evidence();f.stop()
print('ZOOM_LIFETIME_FIXTURE',f.root,flush=True)
