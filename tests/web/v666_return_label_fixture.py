"""Native return identity stays fixed while its information-card label changes."""
import copy,json
import v666_native_callers_fixture as _prior
for _key in dir(_prior):
 if not _key.startswith('_'):globals()[_key]=getattr(_prior,_key)
labels=['계산한 결과 😀','최종 합계 <값> &' ];metadata_key='editorReturnName'
def request():
 r=_prior.request()
 for index,row in enumerate(r['changes']):row['mapping'].pop('bodies');row['returnName']=labels[index]
 return r
def verify_rows(rows):
 for index,fn in enumerate(functions):
  info=f.metadata('inspect',text=rows[fn]['draft']);assert n.canonical(info['signature'])==old and info['values'][metadata_key]==labels[index],info
def verify(checkpoint):
 rows={r['id']:r for r in json.loads(checkpoint.read_text())['changes']};verify_rows(rows);group=rows[owner]['atomicEditGroup'];assert set([owner,*functions])<=set(group);assert not any('/body:'in id for id in group),group;unchanged();return group
def verify_live():
 for index,fn in enumerate(functions):
  info=f.metadata('inspect',text=(f.project/('elements/'+fn.split('::')[1]+'.celem')).read_text());assert n.canonical(info['signature'])==old and info['values'][metadata_key]==labels[index]
 assert all((f.project/path).read_bytes()==raw for path,raw in snapshot.items()if path not in ['elements/'+fn.split('::')[1]+'.celem'for fn in functions]);execute(original_result,'labels-with-original-native-code');f.checked('return labels persist while native/public signatures, return IDs, all C# bytes and graph connections stay unchanged; actual original program46')
def edit_contract(popover,index):
 from playwright.sync_api import expect
 field=popover.locator('[data-signature-id=return] [data-signature-name]')
 if mode=='reproduce-ui':
  assert field.evaluate('el=>el.readOnly');expect(field).to_have_value('결과');f.page.screenshot(path=str(f.case/'readonly-return-name-baseline.png'));assert not d.pending();unchanged();f.checked('published original detail exposes a fixed readonly return-name control although the authored prototype allows output naming');f.browser.close();raise SystemExit(0)
 expect(field).to_be_editable()
 if index==0:
  field.fill('취소할 표시 이름');popover.locator('[data-detail-cancel]').click();assert not d.pending()
  f.owner().locator('[data-inline-method=\"'+functions[index]+'\"] > .function-node-heading').dblclick(position={'x':190,'y':3});field=popover.locator('[data-signature-id=return] [data-signature-name]');expect(field).to_have_value('결과');field.fill('');popover.get_by_role('button',name='저장',exact=True).click();expect(popover.locator('.property-error')).to_contain_text('1~60');assert not d.pending();f.checked('cancel leaves the return name unchanged; empty display name retains its popover/input and creates no pending edit')
 field.fill(labels[index])
def after_contract(index):pass
def verify_pins(panel,index):
 from playwright.sync_api import expect
 method=panel.locator('[data-inline-method="'+functions[index]+'"]')
 expect(method.locator('[data-pin-side=outputs] [data-function-pin-name="'+labels[index]+'"]')).to_have_attribute('data-function-pin-type','정수')
 assert method.locator('[data-pin-side=inputs] [data-function-pin-name]').evaluate_all('(els)=>els.map(e=>e.dataset.functionPinName)')==['amount','count']
