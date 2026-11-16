"""Original type/source editors and existing caller value selection, one Save."""
import os,pathlib,sys
import v666_private_struct_input_fixture as x
os.environ['CONFECTORY_SHARED_BODIES']='1';sys.modules['v536_information_shared_bodies_fixture']=x
p=pathlib.Path(__file__).with_name('v536_information_shared_return_types_ui.py')
# Native nominal edits use the existing native-function-edit input kind.
source=p.read_text().replace("if v['kind']=='function-edit'","if v['kind']in ['function-edit','native-function-edit']")
if x.mode=='conflict':
 import runpy
 runpy.run_path(str(p.with_name('v666_private_struct_input_conflict.py')),run_name='__main__')
else:exec(compile(source,str(p),'exec'),dict(__name__='__main__'))
