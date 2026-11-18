"""Existing delayed Save and real late input checks for this source closure."""
import pathlib,runpy,sys
import v666_retained_import_closure_fixture as x
sys.modules['v666_private_scalar_return_fixture']=x
runpy.run_path(str(pathlib.Path(__file__).with_name('v666_private_scalar_return_late.py')),run_name='__main__')
