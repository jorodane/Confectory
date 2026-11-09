"""Cold mixed receipt cannot rebase a changed native dependency."""
import pathlib,runpy,sys
import v666_header_bodies_fixture as x
sys.modules['v666_native_callers_fixture']=x
runpy.run_path(str(pathlib.Path(__file__).with_name('v666_native_callers_review.py')),run_name='__main__')
