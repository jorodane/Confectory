"""Reuse the existing full body-group lifecycle UI with the import fixture."""
import os,runpy,sys
import v666_body_imports_fixture as x
os.environ['CONFECTORY_SHARED_BODIES']='1';sys.modules['v536_information_shared_bodies_fixture']=x
runpy.run_path(str(x.f.repo/'tests/web/v536_information_shared_return_types_ui.py'),run_name='__main__')
