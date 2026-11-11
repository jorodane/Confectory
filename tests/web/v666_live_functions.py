"""Live function storage through existing owned body Save/Review/Confirm UI."""
from pathlib import Path
import runpy,sys
import v666_live_functions_fixture
if '--api'in sys.argv:
 source=Path(__file__).with_name('v666_information_struct_api.py').read_text().replace("peer=raw.replace(b'general long',b'general int')","peer=raw.replace(b'long value',b'long changed');assert peer!=raw")
 exec(compile(source,str(Path(__file__).with_name('v666_information_struct_api.py')),'exec'),{'__name__':'__main__'})
else:runpy.run_path(str(Path(__file__).with_name('v666_module_flow_ui.py')),run_name='__main__')
