"""Real owned graph multi-selection/delete batch, cold restore and explicit compiler Confirm."""
import json,sys,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
import v536_wide_mixed as f
fn='function '+f.n+'Selection () -> long {}'
prepared=f.metadata('blueprintPrepareFeature',id=f.n+'Selection',text=fn,implementation=f.n+'SelectionBody',graphPath='Selection.graph.json',nodePath='Selection.body.node.json');graph=prepared['graph'];graph['profile']='sync-acyclic-implicit-out-v1'
for id in ['looseA','looseB']:graph['nodes'].append({'id':id,'kind':'code','control':'next','intent':'독립 '+id,'signature':{'args':[],'return':'void'},'implementation':'Selection.'+id+'.node.json','arguments':{}})
definitions=f.metadata('featureBlueprintNodes',featureSource=fn,graph=graph)
for row in definitions['nodes']:
 path=next(n['implementation'] for n in graph['nodes'] if n['id']==row['id']);(f.project/path).write_text(json.dumps({'schema':1,'node':row['id'],'definitionHash':row['definitionHash'],'source':'return 0;' if row['id']=='body' else ''}))
(f.project/'Selection.celem').write_text(fn);(f.project/'SelectionBody.celem').write_text(prepared['implementation']);(f.project/'Selection.graph.json').write_text(json.dumps(graph))
manifest=f.project/'project.cproj';text=manifest.read_text();at=text.rfind('}');manifest.write_text(text[:at]+'element Selection function "Selection.celem";element SelectionBody implementation "SelectionBody.celem";'+text[at:]);f.original={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file()};id=f.n+'SelectionBody/body:common'
def setup():
 page=f.browser.new_page(viewport={'width':2300,'height':1400});page.on('pageerror',lambda e:f.errors.append(str(e)));page.on('response',f.observe);page.route('**/*',f.route);goto_editor(page,f.url);return page
f.setup=setup
def author():return f.page.locator('.window[data-key=blueprint]')
def positions():return f.page.evaluate('Object.fromEntries(["looseA","looseB"].map(id=>{const n=document.querySelector("[data-bp-node="+id+"]");return [id,{x:parseFloat(n.style.left),y:parseFloat(n.style.top)}]}))')
def key(text):author().locator('.bp-viewport').focus();f.page.keyboard.press(text)
def selectBoth():
 for id in ['looseA','looseB']:
  author().locator('[data-bp-overview-node="'+id+'"]').click();author().locator('[data-bp-node="'+id+'"] [data-bp-node-name]').click(modifiers=['Control'])
 expect(author().locator('.bp-node.is-selected')).to_have_count(2)
def cold(index):
 f.pending();f.page.close();f.stop();f.start(index);f.page=setup();expect(author().locator('[data-bp-save]')).to_be_enabled(timeout=60000);f.idle()
try:
 with sync_playwright() as p:
  f.browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.start(0);f.invoke('saveDraft',{});baseline=f.invoke('blueprint',{'action':'read','id':id})['result']['result'];refused={'action':'authorBatch','id':id,'attempt':uuid.uuid4().hex,'checkpointHash':baseline['checkpointHash'],'sourceProof':json.dumps(sorted([[v['id'],v['revision'],v['hash']] for v in baseline['sources']]),separators=(',',':')),'edits':[{'action':'removeNode','node':'looseA'},{'action':'removeNode','node':'body'}]};f.invoke('blueprint',refused,False);after=f.invoke('blueprint',{'action':'read','id':id})['result']['result'];assert after['sources']==baseline['sources'] and after['checkpointHash']==baseline['checkpointHash'] and [n['id'] for n in after['nodes']]==['body','looseA','looseB'];f.originals();f.checked('a later connected removal rejects the whole native candidate: the first deletion, checkpoint and every original remain unchanged');f.page=setup();f.page.locator('#workspace').click(button='right',position={'x':1600,'y':700});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();browser=f.page.locator('.window[data-key^="browser:project:"]');browser.locator('[data-tab=feature]').click();browser.locator('[data-object="'+f.n+'Selection"]').press('Enter');f.page.locator('.window[data-key=declaration] [data-function-write-direct]').click();expect(author()).to_have_attribute('data-blueprint-body',id);f.idle()
  before=positions();selectBoth();handle=author().locator('[data-bp-node=looseB] [data-bp-node-name]');r=handle.bounding_box();f.page.mouse.move(r['x']+3,r['y']+3);f.page.mouse.down();f.page.mouse.move(r['x']+28,r['y']+13,steps=5);f.page.mouse.up();moved=positions();assert moved!=before;assert moved['looseA']['x']-before['looseA']['x']==moved['looseB']['x']-before['looseB']['x'];key('Control+z');assert positions()==before;key('Control+Shift+z');assert positions()==moved;f.originals();assert not f.pending()['blueprint'];f.checked('actual selected group moves and Undo/Redo change only saved private coordinates while all project inputs and sources stay unchanged')
  selectBoth();key('Delete');expect(author().locator('[data-bp-node=looseA]')).to_have_count(0);expect(author().locator('[data-bp-node=looseB]')).to_have_count(0);held=f.pending()['blueprint'];assert len([v for _,v in held if v.get('type')=='remove'])==2;key('Control+z');expect(author().locator('[data-bp-node=looseA]')).to_have_count(1);key('Control+Shift+z');expect(author().locator('[data-bp-node=looseB]')).to_have_count(0);f.originals();cold(1);assert f.pending()['blueprint']==held;expect(author().locator('[data-bp-node=looseA]')).to_have_count(0);f.originals();f.checked('two staged removals form one undoable edit and cold restores the whole selection intent without deleting original files')
  mark=len(f.traffic);author().locator('[data-bp-save]').click();expect(author().locator('.bp-status')).to_have_text('저장됨',timeout=120000);assert not f.pending()['blueprint'];data=f.invoke('blueprint',{'action':'read','id':id})['result']['result'];assert [n['id'] for n in data['nodes']]==['body'];requests=[v['invoke']['input'] for v in f.traffic[mark:] if v.get('invoke',{}).get('endpoint')=='blueprint' and v['invoke'].get('input',{}).get('action')=='authorBatch'];assert len(requests)==1 and [v['node'] for v in requests[0]['edits'] if v['action']=='removeNode']==['looseA','looseB'];saved=data['checkpointHash'];assert f.invoke('blueprint',{**requests[0],'action':'settledAuthorBatch'})['result']['result']['settled'];assert f.invoke('blueprint',requests[0])['result']['result']['settled'];assert f.invoke('blueprint',{'action':'read','id':id})['result']['result']['checkpointHash']==saved;f.originals();f.checked('one native authorBatch/CAS checkpoints both removals together and receipt lookup/retry does not repeat deletion or move the checkpoint')
  author().locator('[data-bp-complete]').click();review=f.page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=60000);review.locator('[data-reject]').click();f.originals();
  if not author().is_visible():f.page.locator('[data-tab-order-key="window:blueprint"] [role=tab]').click()
  expect(author()).to_be_visible();author().locator('[data-bp-complete]').click();expect(review).to_be_visible(timeout=60000)
  for cb in review.locator('[data-review-id]').all():cb.check()
  if review.locator('[data-additional-changes]').count():
   review.locator('[data-review-advanced]').click()
   if review.locator('[data-advanced-reviewed]').count():review.locator('[data-advanced-reviewed]').check()
  review.locator('#confirm').click();expect(review).to_have_count(0,timeout=120000);f.idle();assert {name for name,value in f.original.items() if (f.project/name).read_bytes()!=value}=={'Selection.graph.json'};assert [n['id'] for n in json.loads((f.project/'Selection.graph.json').read_text())['nodes']]==['body'];f.checked('Review Cancel preserves all originals and explicit compiler Confirm changes only the selected graph, retaining detached source files and every other owner')
  f.page.screenshot(path=str(f.case/'selection-confirmed.png'));assert not f.errors and not f.external,(f.errors,f.external);f.browser.close()
except Exception:
 try:f.page.screenshot(path=str(f.case/'failure.png'))
 except Exception:pass
 print('EVIDENCE '+str(f.case),flush=True);raise
finally:f.stop()
print(json.dumps({'checks':f.checks,'actualEngine':True,'renderer':True,'nativeWindows':False,'accountOrInference':False,'projectRun':False,'evidence':str(f.case)},ensure_ascii=False))
