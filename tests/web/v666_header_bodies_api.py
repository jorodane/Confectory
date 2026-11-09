"""Mixed owner presentation retains the existing native-caller final CAS."""
import pathlib,runpy,sys
import v666_header_bodies_fixture as x
sys.modules['v666_native_callers_fixture']=x
runpy.run_path(str(pathlib.Path(__file__).with_name('v666_native_callers_api.py')),run_name='__main__')
