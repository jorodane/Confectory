"""Retained caller contract group survives a real late header input."""
import pathlib,runpy,sys
import v666_retained_caller_input_fixture as x
sys.modules['v666_private_scalar_return_fixture']=x
runpy.run_path(str(pathlib.Path(__file__).with_name('v666_private_scalar_return_late.py')),run_name='__main__')
