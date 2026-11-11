"""Argument presentation is separate from the retained native parameter contract."""
import copy,json
import v666_return_label_fixture as _prior
for _key in dir(_prior):
 if not _key.startswith('_'):globals()[_key]=getattr(_prior,_key)
labels=[{'amount':'입력 수량 😀','count':'반복 횟수 <값> &'}, {'amount':'원래 값','count':'추가 횟수'}]
metadata_key='editorArgumentNames'
def request():
 r=_prior.request()
 for i,row in enumerate(r['changes']):
  row.pop('returnName');row['argumentNames']=labels[i]
 return r
def verify_rows(rows):
 for i,fn in enumerate(functions):
  info=f.metadata('inspect',text=rows[fn]['draft']);assert n.canonical(info['signature'])==old and json.loads(info['values'][metadata_key])==labels[i],info

def verify(checkpoint):
 rows={row['id']:row for row in json.loads(checkpoint.read_text())['changes']};verify_rows(rows);group=rows[owner]['atomicEditGroup'];assert set([owner,*functions])<=set(group) and not any('/body:'in id for id in group),group;unchanged();return group
def verify_live():
 for i,fn in enumerate(functions):
  info=f.metadata('inspect',text=(f.project/('elements/'+fn.split('::')[1]+'.celem')).read_text());assert n.canonical(info['signature'])==old and json.loads(info['values'][metadata_key])==labels[i]
 assert all((f.project/path).read_bytes()==raw for path,raw in snapshot.items()if path not in ['elements/'+fn.split('::')[1]+'.celem'for fn in functions]);execute(original_result,'argument-labels-original-program');f.checked('labels persist with exact native signatures/C# bytes/caller connections and actual original execution46')
def label_input(popover,key):
 from playwright.sync_api import expect
 field=popover.locator('[data-signature-id=arg'+str(next(i for i,a in enumerate(old['args'])if a['name']==key))+'] [data-signature-name]');field.press('Shift+F10');f.page.locator('.context-menu').get_by_role('button',name='표시 이름 편집',exact=True).click();field=popover.locator('[data-signature-id=arg'+str(next(i for i,a in enumerate(old['args'])if a['name']==key))+'] [data-signature-name]');expect(field).to_have_attribute('data-name-mode','display');return field

def edit_contract(popover,index):
 from playwright.sync_api import expect
 field=popover.locator('[data-signature-id=arg0] [data-signature-name]')
 if mode=='reproduce-ui':
  expect(field).to_have_value('amount');assert not field.get_attribute('data-name-mode');field.fill('한글 표시 이름');popover.get_by_role('button',name='저장',exact=True).click();f.idle();held=d.pending();assert len(held)==1 and held[0][1]['signature']['args'][0]['name']=='한글 표시 이름' and 'argumentNames'not in held[0][1];f.page.screenshot(path=str(f.case/'native-name-only-baseline.png'));unchanged();f.checked('published detail treats a Korean/spaced display name as a changed native parameter instead of separate presentation');f.browser.close();raise SystemExit(0)
 if index==0:
  field.click(button='right');expect(f.page.locator('.context-menu')).to_be_visible();f.page.locator('.context-menu').get_by_role('button',name='C# 이름 편집',exact=True).focus();f.page.keyboard.press('Escape');expect(f.page.locator('.context-menu')).to_have_count(0);expect(popover).to_be_visible();expect(field).to_be_focused();assert not d.pending()
  label_input(popover,'amount').fill('');popover.get_by_role('button',name='저장',exact=True).click();expect(popover.locator('.property-error')).to_contain_text('1~60');assert not d.pending();f.checked('mouse/keyboard display mode is explicit; Escape closes only its menu and an empty alias retains input without changing native contracts')
 for key,label in labels[index].items():label_input(popover,key).fill(label)

def after_contract(index):pass

def verify_pins(panel,index):
 from playwright.sync_api import expect
 method=panel.locator('[data-inline-method="'+functions[index]+'"]')
 for label in labels[index].values():expect(method.locator('[data-pin-side=inputs] [data-function-pin-name="'+label+'"]')).to_have_attribute('data-function-pin-type','정수')
 expect(method.locator('[data-pin-side=outputs] [data-function-pin-name="결과"]')).to_have_count(1)
