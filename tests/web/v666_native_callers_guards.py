"""Existing receipt tamper guards must include the newly retained native caller."""
import pathlib,runpy,sys
import v666_native_callers_fixture as x
x.helper_file=x.retained_header;x.helper_body=x.retained_file;sys.modules['v666_body_imports_fixture']=x
runpy.run_path(str(pathlib.Path(__file__).with_name('v666_body_imports_guards.py')),run_name='__main__')
