"""Office finder through actual permitted Helper/Worker state and original camera UI."""
import sys,pathlib,runpy,json,re
from playwright.sync_api import expect
mode=sys.argv[3];sys.argv[3]='io'if mode=='live'else'phase-cold'
import v536_wide_mixed as f
base=f.checked;tested=set();held=False
forbidden={'select','editDraft','editField','editMetadata','editDeclaration','editViewDeclaration','saveDraft','reviewDraft','confirmDraft','reviewGroup','confirmGroup','runProject','startAI','prepareAI','prepareWorker','nodeTask','startBuild','adoptWorker','stopWorker'}
def panel():return f.page.locator('#workspace-find-panel')
def open_find():
 f.page.get_by_role('tab',name='Workspace',exact=True).click();f.page.locator('#worker-finder-bubble').click();expect(panel()).to_be_visible();expect(panel()).to_have_attribute('data-office','true');return panel()
def close():
 if panel().count():panel().get_by_role('searchbox').press('Escape');expect(panel()).to_have_count(0)
def safe(start):
 f.original();assert not f.errors and not f.external,(f.errors,f.external)
 requests=[x['invoke']for x in f.traffic[start:]if x.get('invoke')];assert not forbidden.intersection(x.get('endpoint')for x in requests),requests

def empty():
 start=len(f.traffic);f.page.locator('#chat-input').fill('3D 찾기에서도 보존할 개인 입력');open_find();expect(panel().locator('[data-find-mode="workers"]')).to_have_attribute('aria-pressed','true');expect(panel().locator('.workspace-find-worker')).to_have_count(0)
 for zone in ['__lobby','__concept','__info','__feature','__module']:
  if not panel().count():open_find()
  expect(panel().locator('[data-find-zone="'+zone+'"]')).to_be_enabled();panel().locator('[data-find-zone="'+zone+'"]').click();expect(panel()).to_have_count(0)
 open_find();panel().locator('[data-find-mode="elements"]').click();field=panel().get_by_role('searchbox');field.fill('Slot');row=panel().locator('.workspace-find-result').filter(has=f.page.locator('strong',has_text=re.compile('^Slot$')));expect(row).to_have_count(1);expect(row).to_be_enabled();row.click();expect(panel()).to_have_count(0);expect(f.page.locator('.voxel-office .office-inspector')).to_be_visible();expect(f.page.locator('.voxel-office .office-inspector')).to_contain_text('Slot');expect(f.page.locator('#chat-input')).to_have_value('3D 찾기에서도 보존할 개인 입력');safe(start);base('finder original zone shortcuts and exact owned element selection focus the real room/station without opening a source editor, granting authority or starting work')
 # Retained callbacks cannot act on a newer panel even in the same project.
 open_find();old=panel().locator('[data-find-zone="__info"]');old.evaluate('el=>globalThis.__retiredOfficeFind=el.onclick');close();open_find();panel().get_by_role('searchbox').fill('유지할 새 검색어');f.page.evaluate('()=>__retiredOfficeFind()');expect(panel().get_by_role('searchbox')).to_have_value('유지할 새 검색어');close();expect(f.page.locator('#worker-finder-bubble')).to_be_focused();safe(start);base('retired office navigation callback cannot close a newer query or navigate after Escape; original focus restoration and private input remain')
 # Presentation switch retires the office scope; the panel finder remains intact.
 open_find();f.page.get_by_role('button',name='패널 Workspace',exact=True).click();expect(panel()).to_have_count(0);f.page.locator('#worker-finder-bubble').click();expect(panel()).to_have_attribute('data-office','false');expect(panel().locator('[data-find-mode="workers"]')).to_have_count(0);close();f.page.get_by_role('button',name='아이소메트릭 Workspace',exact=True).click();expect(f.page.locator('.voxel-office')).to_be_visible();safe(start);base('office/editor switch disposes the old scope and preserves the original panel finder; neither mode creates source/task operations')

def workers(query):
 start=len(f.traffic);open_find();field=panel().get_by_role('searchbox');field.fill(query);row=panel().locator('.workspace-find-worker');expect(row).to_have_count(1);expect(row).to_contain_text(query);expect(row).to_be_enabled();expect(panel().locator('.workspace-find-helper-name strong')).to_contain_text('실제 배정 도우미');field.press('Enter');expect(panel()).to_have_count(0);expect(f.page.locator('.voxel-office [data-office-radial-name]')).to_be_visible();expect(f.page.locator('.voxel-office [data-office-radial-name]')).to_contain_text('Worker');safe(start)
 open_find();panel().locator('[data-find-mode="text"]').click();panel().get_by_role('searchbox').fill('기능 공장');room=panel().locator('.workspace-find-result').filter(has=f.page.locator('strong',has_text='기능 공장'));expect(room).to_have_count(1);room.click();expect(panel()).to_have_count(0);safe(start);base('actual visible Worker status search and Enter follow its exact actor; authored room text result focuses the current room without dispatch or movement-dependent execution')
 open_find();field=panel().get_by_role('searchbox');field.fill('Slot');expect(panel().locator('.workspace-find-matches')).to_be_visible();expect(panel().locator('.workspace-find-matches button')).not_to_have_count(0);close();safe(start)
 # Existing narrow viewport rules and repeated open/close, no emulated device claim.
 f.page.set_viewport_size(dict(width=390,height=844));open_find();box=panel().bounding_box();assert box['x']>=0 and box['x']+box['width']<=391,box;close();f.page.set_viewport_size(dict(width=1280,height=900));safe(start)
 f.page.evaluate('()=>confectoryFlushPresentation()');assert '유지할 새 검색어'not in json.dumps(f.state()['presentation'],ensure_ascii=False);base('office name suggestions, repeat/390px browser layout and query exclusion from private presentation are verified; this is not mobile device execution')

def checked(message):
 base(message)
 if message.startswith('3D empty read')and'empty'not in tested:tested.add('empty');empty()
 if message.startswith('existing explicit native assignment')and'ready'not in tested:tested.add('ready');workers('배정 대기')
 if message.startswith('actual approved Worker is running')and'running'not in tested:tested.add('running');workers('작업 중')
 if message.startswith('cold journal cannot recreate')and'cold'not in tested:
  tested.add('cold');expect(panel()).to_have_count(0);workers('실행 확인 필요');assert not f.state()['planningOwnerAvailable'];base('cold opens no finder or execution owner; native interrupted Worker status is searchable without restoring active IO or authority')
 f.page.screenshot(path=str(f.case/'office-finder-last.png'))
f.checked=checked
runpy.run_path(str(pathlib.Path(f.__file__).parent/'v666_office_workers_ui.py'),run_name='__main__')
assert {'empty','ready','running'if mode=='live'else'cold'}<=tested,tested
