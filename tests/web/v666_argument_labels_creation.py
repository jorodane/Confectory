"""Named input and out labels on first Save, alongside exact typed source proofs."""
from pathlib import Path
import json,runpy
import v666_typed_reference_types_fixture
import v666_function_types_fixture as x
from playwright.sync_api import expect
f=x.f;labels={'payload':'대상 정보 참조','snapshot':'원래 정보 값','choice':'선택한 종류 출력'}
def edit(popover):
 for name,label in labels.items():
  field=next(item for item in popover.locator('[data-signature-name]').all()if item.input_value()==name);identity=field.locator('..').get_attribute('data-signature-id');field.click(button='right');f.page.locator('.context-menu').get_by_role('button',name='표시 이름 편집',exact=True).click();current=popover.locator('[data-signature-id="'+identity+'"] [data-signature-name]');expect(current).to_have_attribute('data-name-mode','display');current.fill(label)
def verify(fn,signature):
 source=(f.project/('elements/'+fn.split('::')[1]+'.celem')).read_text();info=f.metadata('inspect',text=source);assert json.loads(info['values']['editorArgumentNames'])==labels;assert info['signature']['return']==signature['return'] and [(a['Name'],a['Type'],a.get('Mode','in'))for a in info['signature']['Args']]==[(a['name'],a['type'],a.get('mode','in'))for a in signature['args']]
 f.checked('first typed-function Save/Confirm retains input and out Unicode aliases alongside unchanged native parameter names, nominal types and complete source proofs')
x.edit_argument_labels=edit;x.verify_argument_labels=verify
runpy.run_path(str(Path(__file__).with_name('v666_typed_reference_types_ui.py')),run_name='__main__')
