"""The authored M11 screen with registered read-only ancestor observations."""
import pathlib,sys
import v666_node_internal_external_override_fixture as n
source=pathlib.Path(__file__).with_name('v666_node_internal_ui.py').read_text()
if '--parent-conflict' in sys.argv:
 source=source.replace("file=f.project/'Flow.node.json';file.write_bytes(x.physical[file]+b' ')", "file=n.parent_file;n.change_parent(b' ')",1)
cancel='''  if mode=='cancel':
   panel().locator('.bp-viewport').press('Control+z');expect(panel().locator('[data-bp-node=calculate]')).to_be_visible();assert not pending() and checkpoint.read_bytes()==before;original();restart(2);assert not pending();original();n.ancestors_original();f.checked('등록 부모 원본과 입력을 보존하며 전환을 취소하고 cold 복원한다');f.browser.close();raise SystemExit(0)
'''
source=source.replace("  if mode=='project':",cancel+"  if mode=='project':",1)
try:exec(compile(source,str(pathlib.Path(__file__).with_name('v666_node_internal_ui.py')),'exec'))
finally:n.ancestors_original()
