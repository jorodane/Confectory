"""Original type Undo/Redo focus, lifecycle, draft field and ownership boundaries."""
import pathlib,runpy,sys
check=next((a.removeprefix('--check=')for a in sys.argv if a.startswith('--check=')),'ui')
if check in ['late','conflict']:
 import v666_property_type_focus_fixture as x
 sys.modules['v666_native_schema_contracts_fixture']=x
 runpy.run_path(str(pathlib.Path(__file__).with_name('v666_native_schema_contracts_'+check+'.py')),run_name='__main__')
else:runpy.run_path(str(pathlib.Path(__file__).with_name('v666_property_type_focus_'+check+'.py')),run_name='__main__')
