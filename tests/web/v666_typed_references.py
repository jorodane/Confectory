"""Real typed carrier/body and native chooser lifecycle via existing authored editor."""
from pathlib import Path
import runpy,sys
if '--chooser'in sys.argv:
 import v666_typed_reference_types_fixture
 target='v666_function_types_api.py'if'--api'in sys.argv else'v666_typed_reference_types_ui.py'
else:
 import v666_typed_references_fixture
 target='v666_information_struct_api.py'if'--api'in sys.argv else'v666_module_flow_ui.py'
runpy.run_path(str(Path(__file__).with_name(target)),run_name='__main__')
