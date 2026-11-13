"""Existing type focus and mixed Save lifecycle in the original information UI."""
import os,pathlib,runpy,sys
import v666_property_type_focus_fixture as x
class CheckedBrowser:
 def __init__(self,browser):self.browser=browser
 def __getattr__(self,name):return getattr(self.browser,name)
 def close(self):
  cells=x.d.pending();expected=3 if x.mode=='reproduce-focus'else 5 if x.mode in ['conflict','projects']else 0;assert len(cells)==expected,cells
  x.f.checked('observed focus flow retains or settles exactly the expected owner inputs');return self.browser.close()
original_setup=x.f.setup
def setup():
 if not isinstance(x.f.browser,CheckedBrowser):x.f.browser=CheckedBrowser(x.f.browser)
 return original_setup()
x.f.setup=setup
os.environ['CONFECTORY_SHARED_BODIES']='1';sys.modules['v536_information_shared_bodies_fixture']=x
runpy.run_path(str(pathlib.Path(__file__).with_name('v536_information_shared_return_types_ui.py')),run_name='__main__')
