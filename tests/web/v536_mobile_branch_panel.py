"""Original mobile branch list on a real owned wrapper; no account/inference/run."""
import json,sys
from playwright.sync_api import sync_playwright,expect
import v536_mobile_enum_pins as f
def author():return f.page.locator('.window[data-key=blueprint]')
def panel():return f.page.locator('.bp-flow-inspector:not([hidden]) [data-flow-node-branches]')
def row(id):return panel().locator('[data-contract-branch="'+id+'"]')
def enum():return json.loads(next(v['text'] for _,v in f.pending() if v.get('type')=='wrapper'))['executionEnum']
def graphKeys(key):
 overlay=f.page.locator('.bp-flow-inspector:not([hidden])')
 if overlay.count():overlay.locator('[data-flow-done]').click()
 author().locator('[data-flow-graph]').click();author().locator('.bp-viewport').focus();f.page.keyboard.press(key)
try:
 f.start(0)
 with sync_playwright() as p:
  f.browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup(f.browser);f.author=f.open_author();f.page.set_viewport_size({'width':390,'height':844});expect(author().locator('[data-flow-node=native]')).to_be_visible();author().locator('[data-flow-node=native]').click();expect(panel().locator('[data-contract-branch]')).to_have_count(2);before=f.current();edges=before['edges'];row('ready').locator('[data-contract-remove]').click();expect(f.page.locator('#toast')).to_contain_text('실행 줄');assert not f.pending();f.unchanged();f.checked('original mobile list exposes stable owned Ready/Done branches and refuses connected branch deletion without partial input')
  row('done').locator('[data-contract-label]').dblclick();field=row('done').locator('[data-contract-name]');field.fill('Finished');field.press('Enter');expect(row('done').locator('[data-contract-label]')).to_have_text('Finished');row('done').locator('[data-branch-up]').click();expect(panel().locator('[data-contract-branch]').first).to_have_attribute('data-contract-branch','done');panel().locator('[data-contract-add]').click();expect(panel().locator('[data-contract-branch]')).to_have_count(3);value=enum();added=next(m['id'] for m in value['members'] if m['name']=='Branch1');assert [m['id'] for m in value['members']]==['next','done','ready',added];assert {m['id']:m['value'] for m in value['members']}=={'next':0,'done':2,'ready':1,added:3};row('ready').press('Alt+ArrowDown');assert [m['id'] for m in enum()['members']]==['next','done',added,'ready'];row('ready').press('Alt+ArrowUp');assert enum()==value;f.page.screenshot(path=str(f.case/'mobile-branch-inspector.png'));f.unchanged();f.checked('rename/order/add reuse one wrapper plan while preserving native values, stable pin IDs, source and every existing route')
  graphKeys('Control+z');assert [m['id'] for m in enum()['members']]==['next','done',added,'ready'];graphKeys('Control+z');assert enum()==value;graphKeys('Control+z');assert len(enum()['members'])==3
  for _ in range(3):graphKeys('Control+Shift+z')
  assert enum()==value;f.checked('mobile panel changes share the original graph Undo/Redo history as one whole branch operation')
  if author().locator('[data-mobile-flow]').is_visible():author().locator('[data-mobile-flow]').click()
  author().locator('[data-flow-node=native]').click();row(added).locator('[data-contract-label]').dblclick();bad=row(added).locator('[data-contract-name]');bad.fill('bad name');bad.press('Enter');assert any(v.get('type','').startswith('contract-draft:branch-name:') for _,v in f.pending());f.pending();f.page.close();f.stop();f.start(1);f.page=f.setup(f.browser);f.page.set_viewport_size({'width':390,'height':844});expect(author().locator('[data-flow-node=native]')).to_be_visible(timeout=60000);author().locator('[data-flow-node=native]').click();bad=row(added).locator('[data-contract-name]');expect(bad).to_have_value('bad name');expect(bad).to_be_visible();bad.press('Escape');assert enum()==value and not any(v.get('type','').startswith('contract-draft:branch-name:') for _,v in f.pending());f.unchanged();f.checked('incomplete branch name survives real restart and explicit Escape cancels only that raw name while keeping the complete enum plan')
  f.page.locator('.bp-flow-inspector:not([hidden]) [data-flow-done]').click();author().locator('[data-bp-save]').click();expect(author().locator('.bp-status')).to_have_text('저장됨',timeout=120000);assert not f.pending();assert f.native(f.current())['executionEnum']==value and f.current()['edges']==edges;f.unchanged();author().locator('[data-bp-complete]').click();review=f.page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=60000);review.locator('[data-reject]').click();f.unchanged();f.page.locator('[data-tab-order-key="window:blueprint"] [role=tab]').click();author().locator('[data-bp-complete]').click();expect(review).to_be_visible(timeout=60000)
  for cb in review.locator('[data-review-id]').all():cb.check()
  if review.locator('[data-additional-changes]').count():
   review.locator('[data-review-advanced]').click()
   if review.locator('[data-advanced-reviewed]').count():review.locator('[data-advanced-reviewed]').check()
  review.locator('#confirm').click();expect(review).to_have_count(0,timeout=120000);assert {name for name,text in f.original.items() if (f.project/name).read_bytes()!=text}=={'Caller.graph.json'};f.checked('Save/cold enum is separately compiler-confirmed and changes only the selected caller graph, preserving callee/body/objects and other implementation')
  f.page.screenshot(path=str(f.case/'mobile-branch-panel.png'));assert not f.errors and not f.external,(f.errors,f.external);f.browser.close()
except Exception:
 print('EVIDENCE '+str(f.case),flush=True);raise
finally:f.stop()
print(json.dumps({'checks':f.checks,'actualEngineRenderer':True,'nativeWindowsOrMobile':False,'accountOrInference':False,'projectRun':False,'evidence':str(f.case)},ensure_ascii=False))
