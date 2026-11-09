"""Mixed presentation cannot hide or weaken the original native read scope."""
import pathlib,runpy,sys
import v666_header_bodies_fixture as x
x.helper_file=x.retained_header;x.helper_body=x.retained_file;sys.modules['v666_body_imports_fixture']=x
runpy.run_path(str(pathlib.Path(__file__).with_name('v666_body_imports_guards.py')),run_name='__main__')
