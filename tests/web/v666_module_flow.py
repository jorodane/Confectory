"""Module public execution closure through existing Review/CAS body UI/API."""
from pathlib import Path
import runpy,sys
import v666_module_flow_fixture
kind='api'if'--api'in sys.argv else'ui'
if kind=='api':
    source=Path(__file__).with_name('v666_information_struct_api.py').read_text()
    source=source.replace('path=f.project/x.schema_path',"path=f.project/'MethodSlot.celem'").replace("peer=raw.replace(b'general long',b'general int')","peer=raw.replace(bytes([92,34])+b'value'+bytes([92,34])+b': 12',bytes([92,34])+b'value'+bytes([92,34])+b': 13');assert peer!=raw")
    source=source.replace('x.unchanged({x.schema_path})',"x.unchanged({'MethodSlot.celem'})").replace('information definition after the body snapshot','required public branch after the body snapshot').replace('a schema type change after compiler Review','a required public branch change after compiler Review')
    exec(compile(source,str(Path(__file__).with_name('v666_information_struct_api.py')),'exec'),{'__name__':'__main__'})
else:
    runpy.run_path(str(Path(__file__).with_name('v666_module_flow_ui.py')),run_name='__main__')
