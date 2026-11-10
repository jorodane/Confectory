"""Actual existing C# body Save/CAS lifecycle over information array fields."""
from pathlib import Path
import runpy,sys
import v666_information_arrays_fixture
kind='api'if'--api'in sys.argv else'ui'
runpy.run_path(str(Path(__file__).with_name('v666_information_struct_api.py'if kind=='api'else'v666_information_arrays_ui.py')),run_name='__main__')
