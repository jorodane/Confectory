"""Information argument labels through the existing shared-owner lifecycle."""
import os,pathlib,runpy,sys
import v666_argument_labels_fixture as x
os.environ['CONFECTORY_SHARED_BODIES']='1';sys.modules['v536_information_shared_bodies_fixture']=x
runpy.run_path(str(pathlib.Path(__file__).with_name('v536_information_shared_return_types_ui.py')),run_name='__main__')
