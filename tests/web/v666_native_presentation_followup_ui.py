"""All four original inputs survive failure/conflict/restart or save/cancel together."""
import json,os,pathlib,runpy,sys
import v666_native_presentation_followup_fixture as x
class CheckedBrowser:
 def __init__(self,browser):self.browser=browser
 def __getattr__(self,name):return getattr(self.browser,name)
 def close(self):
  cells=x.d.pending();retained=x.mode in ['conflict','projects','reproduce-header-ui'];assert len(cells)==(4 if retained else 0),cells
  if retained:
   assert next(v['text']for _,v in cells if v['kind']=='description')==x.description
   assert next(v['text']for _,v in cells if v['kind']=='icon')==x.icon
  x.f.checked('all four mixed owner/contract inputs '+('remain isolated and intact'if retained else'are saved or cancelled')+' at the observed UI boundary');return self.browser.close()
original_setup=x.f.setup
def setup():
 if not isinstance(x.f.browser,CheckedBrowser):x.f.browser=CheckedBrowser(x.f.browser)
 return original_setup()
x.f.setup=setup
os.environ['CONFECTORY_SHARED_BODIES']='1';sys.modules['v536_information_shared_bodies_fixture']=x
runpy.run_path(str(pathlib.Path(__file__).with_name('v536_information_shared_return_types_ui.py')),run_name='__main__')
