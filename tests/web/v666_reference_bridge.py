"""Explicit instance binding through existing native body Save/Review/Confirm."""
from pathlib import Path
import runpy,sys
import v666_reference_bridge_fixture
if '--api'in sys.argv:runpy.run_path(str(Path(__file__).with_name('v666_information_struct_api.py')),run_name='__main__')
else:runpy.run_path(str(Path(__file__).with_name('v666_module_flow_ui.py')),run_name='__main__')
