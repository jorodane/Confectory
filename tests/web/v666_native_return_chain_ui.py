"""Existing return mapping and own-source editor save a real imported call chain."""
import os,pathlib,runpy,sys
import v666_native_return_chain_fixture as x
os.environ['CONFECTORY_SHARED_BODIES']='1';sys.modules['v536_information_shared_bodies_fixture']=x
if x.mode=='conflict':runpy.run_path(str(pathlib.Path(__file__).with_name('v666_native_chain_conflict.py')),run_name='__main__')
else:runpy.run_path(str(pathlib.Path(__file__).with_name('v536_information_shared_return_types_ui.py')),run_name='__main__')
