"""Actual readonly union beside existing versioned writable table inputs."""
import json,shutil,uuid,time
from pathlib import Path
from playwright.sync_api import expect

def prepare_discovery(project,root,repo,env):
 p='Example.ButtonGame::'
 fixtures={'UnionOtherSchema':('schema',f'schema {p}UnionOtherSchema {{field amount single general string;}}'),'UnionOther':('object',f'object {p}UnionOther {{use schema {p}UnionOtherSchema;data amount = "variant";value nullish = 0;}}'),'UnionBare':('object',f'object {p}UnionBare {{}}'),'UnionBroken':('object',f'object {p}UnionBroken {{}}'),'UnionMany':('object','object '+p+'UnionMany {'+''.join('value field'+str(n).zfill(3)+' = '+str(n)+';' for n in range(80))+'}')}
 for n in range(18):fixtures['UnionRow'+str(n).zfill(2)]=('object','object '+p+'UnionRow'+str(n).zfill(2)+' {value index = '+str(n)+';}')
 for name,(_,source) in fixtures.items():(project/(name+'.celem')).write_text(source)
 (project/'UnionBroken.celem').write_text('broken owned declaration')
 schema=project/'TableStats.celem';text=schema.read_text();schema.write_text(text[:text.rfind('}')]+ 'field zero single general long;field unsetText single general string;}')
 score=project/'Score.celem';score.write_text(score.read_text().replace('{','{value nullish = 1;value empty = "";value falsey = false;data zero = 0;',1))
 manifest=project/'project.cpack';text=manifest.read_text();at=text.rfind('}');manifest.write_text(text[:at]+''.join('element '+name+' '+kind+' "'+name+'.celem";' for name,(kind,_) in fixtures.items())+text[at:])
 second=root/'second-project';shutil.copytree(project,second,ignore=shutil.ignore_patterns('.confectory'));score=second/'Score.celem';score.write_text(score.read_text().replace('9223372036854775807','41'))
 storage=root/'storage';storage.mkdir(exist_ok=True);(storage/'projects.json').write_text(json.dumps([{'path':str(folder/'project.cpack'),'title':name,'description':'Owned IMP3 fixture'} for folder,name in [(project,'Union project A'),(second,'Union project B')]]))
 env.update(CONFECTORY_FIELD_TEST_HOLD=str(root/'field-hold'),CONFECTORY_FIELD_TEST_ENTERED=str(root/'field-entered'))

def verify_discovery(page,project,mount,send,envelope,settle,restart):
 page.set_viewport_size({'width':2600,'height':1550});p='Example.ButtonGame::';score=p+'Score';twin=p+'TableTwin';other=p+'UnionOther';bare=p+'UnionBare';broken=p+'UnionBroken';many=p+'UnionMany';amount='data:["amount"]';unset='data:["unsetText"]';zero='data:["zero"]';root=project.parent;hold=root/'field-hold';entered=root/'field-entered';schema=project/'TableStats.celem';reference=root/'browser-reference/External.celem';second=root/'second-project';originals={f:f.read_bytes() for folder in [project,second,reference.parent] for f in folder.rglob('*') if f.is_file() and '.confectory' not in f.parts}
 def state():
  v=mount();s=v['state'];assert send(envelope(v,'dispose'))['ok'];return s
 def invoke(endpoint,args,ok=True):
  v=mount();rid=uuid.uuid4().hex;assert send(envelope(v,'invoke',endpoint=endpoint,input=args,requestId=rid,expectedRevision=v['revision']))['ok'];r,_=settle(v,rid);assert r['ok']==ok,r;assert send(envelope(v,'dispose'))['ok'];return r
 def ready():expect(page.locator('#nav')).to_be_enabled(timeout=120000);expect(page.locator('#workspace-save-state')).not_to_contain_text('편집창 복원 중',timeout=120000)
 def window(key):return page.locator('.window[data-key="'+key+'"]')
 def move(w,x,y):
  b=w.locator('.window-title').bounding_box();page.mouse.move(b['x']+60,b['y']+15);page.mouse.down();page.mouse.move(x+60,y+15,steps=12);page.mouse.up()
 def browse():
  ready();page.locator('#nav').click();page.locator('.nav-menu').get_by_role('button',name='개념',exact=True).click();ready()
  if page.locator('.nav-menu').count():page.locator('#nav').click()
  w=window('browser');w.locator('input[aria-label="객체 표시 밀도 Compact Preview Data"]').evaluate('(e)=>{e.value="100";e.dispatchEvent(new Event("input",{bubbles:true}));}');return w
 def write_cell(id=score):return window('browser').locator('[data-table-cell="'+id+'"][data-column=\''+amount+'\']')
 def table():return state()['tables'][0]
 def private_meta():
  page.evaluate('()=>globalThis.confectoryFlushPresentation()');return {r['key']:r['meta'] for r in state()['presentation']['layout']}
 def dcell(id,field):return window('field-discovery').locator('[data-discovery-cell="'+id+'"][data-field-key=\''+field+'\']')
 def result():expect(window('field-discovery').locator('[data-discovery-summary]')).to_be_visible(timeout=120000);expect(window('field-discovery').locator('[data-discovery-status]')).to_contain_text('행별 관측값',timeout=120000)
 def filter_field(text):
  d=window('field-discovery');d.locator('[data-discovery-filter]').fill(text);d.locator('[data-discovery-apply-filter]').click();result()
 def choose(ids,commit=True):
  d=window('field-discovery');d.locator('[data-discovery-choose]').click();expect(d.locator('[data-discovery-object]')).not_to_have_count(0,timeout=120000);d.locator('[data-discovery-clear-choices]').click()
  for id in ids:d.locator('[data-discovery-object="'+id+'"]').check()
  d.locator('[data-discovery-commit-choices]' if commit else '[data-discovery-cancel-choices]').click()
  if commit:result()
 def pending_invariant(binding=True):
  if binding:
   expect(write_cell()).to_have_value('5');expect(window('browser').locator('[data-table-fill-value]')).to_have_value('7');expect(window('browser').locator('[data-table-select="'+score+'"]')).to_be_checked();assert table()['ids']==[score] and table()['columns']==[amount];assert write_cell().evaluate('e=>e===globalThis.__imp3Cell')
  else:
   # Existing source-dirty guard defers Browser filter/table restoration. Check the exact retained inputs, without applying the source or loading a write table.
   browser=private_meta()['browser'];assert all(browser[k]==before[k] for k in ['tableInputs','tableFill','tableSelected','tableDefinition']);expect(window('browser').locator('[data-browser-control=objects]')).to_contain_text('미적용 소스 입력을 먼저 적용하세요.')
  assert not state()['workers'] and state()['aiState']=='idle' and not state()['aiPreview']
 def sources():
  for f,raw in originals.items():assert f.read_bytes()==raw,f
 def begin_hold(d):
  private_meta();ready()
  if entered.exists():entered.unlink()
  hold.write_text('owned');d.locator('[data-discovery-refresh]').click()
  deadline=time.monotonic()+15
  while not entered.exists() and time.monotonic()<deadline:page.wait_for_timeout(20)
  assert entered.exists(),'owned metadata barrier not reached';expect(d.locator('[data-discovery-cancel]')).to_be_enabled()
 w=browse();w.locator('[data-browser-fields]').click();b=window('custom');expect(b.locator('[data-table-object]')).not_to_have_count(0,timeout=120000);ready();b.locator('[data-table-probe]').select_option(score);ready()
 for check in b.locator('[data-table-object]').all():check.uncheck()
 b.locator('[data-table-object="'+score+'"]').check()
 for check in b.locator('[data-table-field]').all():check.uncheck()
 b.locator('[data-table-field=\''+amount+'\']').check();b.locator('[data-table-create]').click();ready();b.locator('[data-close]').click();expect(write_cell()).to_have_value('9223372036854775807')
 # Prepare explicit source selection before capturing the live pending input bindings.
 invoke('select',{'id':score});ready();w.locator('[data-browser-control="browser-actions"]').click();page.locator('#advanced-source').click();source=page.locator('#source');expect(source).to_be_visible();pending_source=source.input_value()+'\n// IMP3_PENDING_SOURCE';source.fill(pending_source);source.evaluate('e=>globalThis.__imp3Source=e');move(window('source'),650,800);source_text=state()['draft']['text']
 write_cell().fill('5');write_cell().evaluate('e=>globalThis.__imp3Cell=e');w.locator('[data-table-select="'+score+'"]').check()
 w.locator('[data-table-fill-value]').fill('7');before=private_meta()['browser'];write_hash=table()['definitionHash'];w.locator('[data-browser-discover]').click();d=window('field-discovery');expect(d.locator('[data-discovery-root]')).to_be_visible();result();move(d,1200,120);pending_invariant();choose([score,other,bare,broken]);expect(d.locator('[data-discovery-summary]')).to_contain_text('조회 실패 1개');expect(dcell(score,amount).locator('[data-discovery-json]')).to_have_text('9223372036854775807');expect(dcell(other,amount).locator('[data-discovery-json]')).to_have_text('"variant"');expect(dcell(bare,amount)).to_have_attribute('data-value-state','missing');expect(dcell(broken,amount)).to_have_attribute('data-defined','unknown');expect(dcell(score,unset)).to_have_attribute('data-value-state','unset');expect(dcell(score,zero).locator('code')).to_have_text('0');expect(dcell(score,'nullish').locator('code')).to_have_text('null');expect(dcell(other,'nullish').locator('code')).to_have_text('0');expect(dcell(score,'falsey').locator('code')).to_have_text('false');expect(dcell(score,'empty').locator('code')).to_have_text('""');assert not d.locator('[data-table-cell],[data-table-select],[data-table-apply]').count();pending_invariant();sources()
 # Even valid current readonly versions cannot add a row or field to a writable definition.
 observed=invoke('discoverFields',{'action':'union','projectId':state()['projectId'],'ids':[score,other],'query':'','request':'scope-proof'})['result'];version=lambda id:{k:next(r for r in observed['rows'] if r['id']==id)[k] for k in ['revision','textHash','viewHash']}
 invoke('editTable',{'table':table()['table'],'ids':[other],'field':amount,'valueJson':'"changed"','versions':{other:version(other)},'operation':'set'},False)
 invoke('editTable',{'table':table()['table'],'ids':[score],'field':'nullish','valueJson':'2','versions':{score:version(score)},'operation':'set'},False);pending_invariant();sources()
 # A cancelled target dialog and local row filter do not alter the applied IDs or writing table.
 chosen=private_meta()['field-discovery']['fieldDiscovery']['ids'];choose([twin],False);assert private_meta()['field-discovery']['fieldDiscovery']['ids']==chosen;d.locator('[data-discovery-row-filter]').fill('UnionOther');expect(d.locator('[data-discovery-row="'+score+'"]')).to_be_hidden();pending_invariant();d.locator('[data-discovery-row-filter]').fill('');filter_field('nullish');expect(d.locator('[data-discovery-column]')).to_have_count(1);expect(dcell(score,'nullish').locator('code')).to_have_text('null');d.locator('[data-discovery-filter]').fill('pending-filter');d.locator('[data-discovery-reset-filter]').click();expect(d.locator('[data-discovery-filter]')).to_have_value('nullish');pending_invariant()
 # Exact source editor DOM is retained as well as both independent table inputs.
 def source_pending(binding=True):
  expect(page.locator('#source')).to_have_value(pending_source)
  if binding:assert page.locator('#source').evaluate('e=>e===globalThis.__imp3Source')
  assert state()['draft']['text']==source_text
 # Cooperative cancel after the first bounded metadata call; no late publication.
 begin_hold(d);d.locator('[data-discovery-cancel]').click();expect(d.locator('[data-discovery-status]')).to_contain_text('취소됨');hold.unlink();page.wait_for_timeout(200);expect(d.locator('[data-discovery-status]')).to_contain_text('취소됨');pending_invariant();source_pending()
 # Applying a new field filter cancels the old request and ignores its response.
 begin_hold(d);d.locator('[data-discovery-filter]').fill('zero');d.locator('[data-discovery-apply-filter]').click();hold.unlink();result();expect(d.locator('[data-discovery-column]')).to_have_count(1);expect(d.locator('[data-discovery-column]')).to_have_attribute('data-discovery-column',zero);pending_invariant();source_pending()
 # Mid-read confirmed schema drift refuses a mixed projection; a fresh read observes it.
 choose([score,twin]);filter_field('amount');schema_before=schema.read_bytes();begin_hold(d);text=schema.read_text();schema.write_text(text[:text.rfind('}')]+'field newAmount single general long;}');hold.unlink();expect(d.locator('[data-discovery-status]')).to_contain_text('조회 실패',timeout=120000);pending_invariant();source_pending();d.locator('[data-discovery-refresh]').click();result();expect(d.locator('[data-discovery-column=\'data:["newAmount"]\']')).to_be_visible();pending_invariant();source_pending()
 # Discovery did not rebase the old cell/fill version, or widen their rows/columns.
 w.locator('[data-table-apply="'+score+'"][data-column=\''+amount+'\']').click();ready();expect(write_cell()).to_have_value('5');assert table()['snapshot']['rows'][0]['cellInfo'][amount]['valueJson']=='9223372036854775807';assert table()['definitionHash']==write_hash;assert private_meta()['browser']['tableFill']['versions']==before['tableFill']['versions'];source_pending();schema.write_bytes(schema_before)
 # Explicit bounds are navigable without adding write fields or input controls.
 choose([many]);filter_field('field');expect(d.locator('[data-discovery-column]')).to_have_count(16);first_column=d.locator('[data-discovery-column]').first.get_attribute('data-discovery-column');d.locator('[data-discovery-fields-next]').click();result();assert d.locator('[data-discovery-column]').first.get_attribute('data-discovery-column')!=first_column;pending_invariant();source_pending()
 rows=[p+'UnionRow'+str(n).zfill(2) for n in range(18)];choose(rows);filter_field('index');expect(d.locator('[data-discovery-row]')).to_have_count(16);d.locator('[data-discovery-rows-next]').click();result();expect(d.locator('[data-discovery-row]')).to_have_count(2);assert d.locator('[data-discovery-row]').evaluate_all('es=>es.map(e=>e.dataset.discoveryRow)')==rows[16:];pending_invariant();source_pending()
 # Registered object identities never enter the selectable read scope or a write table.
 response=invoke('discoverFields',{'action':'union','projectId':state()['projectId'],'ids':[score,'BrowserReference::External'],'query':'','request':'foreign'},False);assert not response['ok'];assert table()['ids']==[score] and table()['columns']==[amount];sources()
 choose([score,other]);filter_field('amount');d.locator('[data-discovery-filter]').fill('unapplied filter input');saved=private_meta();spec=saved['field-discovery']['fieldDiscovery'];assert set(spec)=={'projectId','ids','query','queryInput','rowOffset','fieldPage','rowFilter'} and spec['ids']==[score,other] and spec['query']=='amount' and spec['queryInput']=='unapplied filter input';source_pending();pending_invariant();page.screenshot(path='/tmp/confectory-imp3-before-cold.png',full_page=True)
 # Cold restore uses only saved IDs/filter/pages. Both the schema and values are read again.
 text=schema.read_text();schema.write_text(text[:text.rfind('}')]+'field coldAmount single general long;}');originals[schema]=schema.read_bytes();restart();ready();d=window('field-discovery');result();expect(d.locator('[data-discovery-filter]')).to_have_value('unapplied filter input');expect(d.locator('[data-discovery-column=\'data:["coldAmount"]\']')).to_be_visible();pending_invariant(False);source_pending(False);restored=private_meta();assert restored['browser']['tableInputs']==saved['browser']['tableInputs'] and restored['browser']['tableFill']==saved['browser']['tableFill'];assert restored['field-discovery']['fieldDiscovery']['ids']==[score,other];sources();page.screenshot(path='/tmp/confectory-imp3-after-cold.png',full_page=True)
 # A/B/A has independent private scopes even when the object IDs are identical.
 first_id=state()['projectId'];page.locator('.brand').click();expect(page.locator('[data-enter]')).to_have_count(2);page.locator('[data-project]').filter(has_text='Union project B').locator('[data-enter]').click();ready();w=browse();w.locator('[data-browser-discover]').click();d=window('field-discovery');expect(d.locator('[data-discovery-choices]')).to_be_visible();expect(d.locator('[data-discovery-object]')).not_to_have_count(0,timeout=120000);d.locator('[data-discovery-object="'+score+'"]').check();d.locator('[data-discovery-commit-choices]').click();result();move(d,1200,120);filter_field('amount');expect(dcell(score,amount).locator('code')).to_have_text('41');assert state()['projectId']!=first_id and not state()['tables'];page.locator('.brand').click();page.locator('[data-project]').filter(has_text='Union project A').locator('[data-enter]').click();ready();d=window('field-discovery');expect(d.locator('[data-discovery-filter]')).to_have_value('unapplied filter input');expect(dcell(score,amount).locator('code')).to_have_text('9223372036854775807');pending_invariant(False);source_pending(False);sources()
 print('PASS actual IMP3 automatic field union: exact JSON and missing/null/default/type variants, bounded pages/partial failures, independent write selections and original CAS, unchanged pending source/cell/fill DOM, cancel/late response/filter/selection, current cold schema and A/B/A isolation; no source writes or AI',flush=True)
