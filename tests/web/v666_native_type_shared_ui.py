"""Existing type/body UI over two explicit plans for one shared caller."""
import sys,runpy
from pathlib import Path
import v666_native_type_shared_fixture as x
original_checked=x.f.checked
def checked(message):return original_checked(message.replace('four selected C# bodies','three unique C# bodies from four explicit selections').replace('four authored body plans','four explicit selections for three unique sources'))
x.f.checked=checked
sys.modules['v666_native_type_group_fixture']=x
runpy.run_path(str(Path(__file__).with_name('v666_native_type_group_ui.py')),run_name='__main__')
