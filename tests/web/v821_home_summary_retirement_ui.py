"""Real local Home cancellation/return with nine recent cards, no external services."""
import json,re,shutil
from playwright.sync_api import sync_playwright,expect
import v821_object_fallback_roundtrip_ui as d
from editor_navigation import goto_editor
f=d.fixture;d.seed();profile=f.root/'profile';listing=profile/'projects.json';cards=json.loads(listing.read_text());counts={}
for i in range(6):
 folder=f.root/f'recent-{i}';shutil.copytree(f.projects[0].parent,folder,ignore=shutil.ignore_patterns('.confectory','.build'));manifest=folder/'project.cpack';extra=folder/'HomeExtra.celem';extra.write_text(f'object {d.NS}::HomeExtra {{}}\n');manifest.write_text(manifest.read_text().rstrip()[:-1]+' element HomeExtra object "HomeExtra.celem"; }\n');cards.append({'path':str(manifest),'title':f'Recent {i}','description':''});counts[f'Recent {i}']=len(re.findall(r'\belement\s+\w+\s+object\s+',manifest.read_text()))
for name,manifest in zip((d.FIRST,d.SECOND),f.projects):counts[name]=len(re.findall(r'\belement\s+\w+\s+object\s+',manifest.read_text()))
cards.append({'path':str(f.root/'missing'/'project.cpack'),'title':'Missing Recent','description':''});listing.write_text(json.dumps(cards));f.env['CONFECTORY_UI_TRACE']='1';expect.set_options(timeout=60000)
try:
 with sync_playwright() as p,p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']) as b:
  f.start(0);page=f.setup(b);page.evaluate('()=>globalThis.confectoryWebUITrace=[]');d.leave_to_home(page)
  def tile(name):return page.locator('.project-card').filter(has=page.get_by_role('heading',name=name,exact=True))
  def admitted():page.wait_for_function("()=>confectoryWebUITrace?.some(r=>r.stage==='call'&&r.endpoint==='homeSummaries'&&r.code==='completed')")
  def back():page.evaluate('()=>globalThis.confectoryWebUITrace=[]');d.leave_to_home(page)
  def enter(name):tile(name).locator('[data-enter]').click();expect(page.locator('#title')).to_contain_text(name);expect(page.locator('#project-menu')).to_be_enabled();return f.state()['projectId']
  admitted();a=enter(d.FIRST);back();admitted();b_id=enter(d.SECOND);assert a!=b_id;back();admitted();assert enter(d.FIRST)==a;back();print('PASS rapid return and independent same-ID selection',flush=True)
  # New project form remains interactive while summary work is retired or queued.
  admitted();page.locator('#new-project').click();expect(page.locator('#project-name')).to_be_editable();page.locator('#project-name').fill('Cancelled synthetic project');page.locator('[data-project-cancel]').click();expect(page.locator('#create-form')).to_have_count(0)
  for name,count in counts.items():stat=tile(name).locator('[data-stat=objects]');expect(stat).to_have_attribute('data-status','available');expect(stat).to_have_text(str(count))
  missing=tile('Missing Recent').locator('[data-stat=objects]');expect(missing).to_have_attribute('data-status','unavailable');expect(missing).to_have_text('—');assert page.locator('.project-card [data-enter]').count()==9;print('PASS each returned summary accurate, absent file unavailable, new form cancel preserved listing',flush=True)
  tile('Missing Recent').locator('[data-enter]').click();expect(page.locator('#new-project')).to_be_enabled();assert f.state()['projectId']=='';assert enter(d.SECOND)==b_id;back();print('PASS missing project open preserves Home and valid next selection',flush=True)
  assert not f.errors and not f.external;f.original()
finally:f.stop();print('evidence',f.root,flush=True)
