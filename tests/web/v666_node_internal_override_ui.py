"""Reuse the authored M11 screen with an explicitly owned overriding body."""
import pathlib,sys
import v666_node_internal_override_fixture as n
source=pathlib.Path(__file__).with_name('v666_node_internal_ui.py').read_text()
if '--parent-conflict' in sys.argv:
 source=source.replace("file=f.project/'Flow.node.json';file.write_bytes", "file=f.project/'M11Parent.celem';file.write_bytes",1)
cancel='''  if mode=='cancel':
   panel().locator('.bp-viewport').press('Control+z');expect(panel().locator('[data-bp-node=calculate]')).to_be_visible();assert not pending() and checkpoint.read_bytes()==before;original();restart(2);expect(panel().locator('[data-bp-node=calculate]')).to_be_visible();assert not pending();original();x.build('override-cancel',7);f.checked('override 전환 취소·cold는 부모와 자기 원문·기존 활성 구현·입력을 보존한다');f.browser.close();raise SystemExit(0)
'''
source=source.replace("  if mode=='project':",cancel+"  if mode=='project':",1)
try:exec(compile(source,str(pathlib.Path(__file__).with_name('v666_node_internal_ui.py')),'exec'))
finally:
 for p,(_,mode) in n.parent_files.items():assert p.read_bytes()==n.x.physical[p] and p.stat().st_mode==mode,p
