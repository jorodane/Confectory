"""Original action-card enum panel, existing native code source and exact owned candidate."""
import json
from playwright.sync_api import sync_playwright,expect
import v536_mobile_enum_pins as f
node=next(v for v in f.g['nodes'] if v['id']=='ready');node['control']='switch';node['executionEnum']={'primary':'next','members':[{'id':'next','name':'NoBranch','value':0},{'id':'extra','name':'Extra','value':7}]};definitions=f.metadata('featureBlueprintNodes',featureSource=f.items['Calc'][1],featureContracts={f.n+'Native':f.items['Native'][1]},graph=f.g)
for definition in definitions['nodes']:
 if definition['definition']['kind']!='code':continue
 name=definition['id'];path=f.project/('Caller.node.json' if name=='body' else name+'.node.json');record=json.loads(path.read_text());record['definitionHash']=definition['definitionHash']
 if name=='ready':record['source']='return Result.NoBranch;'
 path.write_text(json.dumps(record))
(f.project/'Caller.graph.json').write_text(json.dumps(f.g));f.original={p.name:p.read_bytes() for p in f.project.iterdir()}
def author():return f.page.locator('.window[data-key=blueprint]')
def editor():return f.page.locator('.bp-flow-inspector:not([hidden])')
def panel():return editor().locator('[data-flow-node-branches]')
try:
 f.start(0)
 with sync_playwright() as p:
  f.browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup(f.browser);f.open_author();f.page.set_viewport_size({'width':390,'height':844});author().locator('[data-flow-fold="native:case:ready"] > summary').click();author().locator('[data-flow-node=ready]').click();expect(panel().locator('[data-contract-branch]')).to_have_count(1);entry=panel().locator('[data-contract-branch=extra]');entry.press('F2');field=entry.locator('input');field.fill('Additional');field.press('Enter');panel().locator('[data-contract-add]').click();expect(panel().locator('[data-contract-branch]')).to_have_count(2);held=f.pending();plan=json.loads(next(v['text'] for _,v in held if v.get('type')=='enum-code'));assert plan['source']=='return Result.NoBranch;' and [(v['id'],v['name'],v['value']) for v in plan['executionEnum']['members'][:2]]==[('next','NoBranch',0),('extra','Additional',7)];assert f.current()['edges']==f.g['edges'];f.unchanged();f.checked('original action F2/name/add panel keeps the existing C# body, stable enum ID/value, owner and every execution route')
  editor().locator('[data-flow-done]').click();author().locator('[data-bp-save]').click();expect(author().locator('.bp-status')).to_have_text('저장됨',timeout=120000);assert not f.pending();after=f.current();ready=next(v for v in after['nodes'] if v['id']=='ready');assert ready['executionEnum']==plan['executionEnum'] and ready['source']==plan['source'] and after['edges']==f.g['edges'];f.unchanged();f.checked('action enum changes use the existing one enumCode authorBatch candidate/checkpoint and leave all original files unchanged')
  author().locator('[data-bp-complete]').click();review=f.page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=60000)
  for cb in review.locator('[data-review-id]').all():cb.check()
  if review.locator('[data-additional-changes]').count():
   review.locator('[data-review-advanced]').click()
   if review.locator('[data-advanced-reviewed]').count():review.locator('[data-advanced-reviewed]').check()
  review.locator('#confirm').click();expect(review).to_have_count(0,timeout=120000);changed={name for name,text in f.original.items() if (f.project/name).read_bytes()!=text};assert changed=={'Caller.graph.json','ready.node.json'},changed;assert json.loads((f.project/'ready.node.json').read_text())['source']=='return Result.NoBranch;';f.checked('explicit compiler Confirm changes only owned graph/code record; the other code nodes, wrapper, callee and other implementation remain exact')
  assert not f.errors and not f.external,(f.errors,f.external);f.browser.close()
except Exception:
 print('EVIDENCE '+str(f.case),flush=True);raise
finally:f.stop()
print(json.dumps({'checks':f.checks,'actualEngineRenderer':True,'nativeWindowsOrMobile':False,'accountOrInference':False,'projectRun':False,'evidence':str(f.case)},ensure_ascii=False))
