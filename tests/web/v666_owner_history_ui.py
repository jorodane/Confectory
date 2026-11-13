"""Original property type picker and explicit CSharp contract/body editors share one Save."""
import json,os,pathlib,runpy,sys
import v666_owner_history_fixture as x
class CheckedBrowser:
 def __init__(self,browser):self.browser=browser
 def __getattr__(self,name):return getattr(self.browser,name)
 def close(self):
  cells=x.d.pending();retained=x.mode in ['conflict','projects','reproduce-owner-ui'];assert len(cells)==(10 if retained else 0),cells
  x.f.checked('all ten scalar-owner/presentation/contract inputs '+('remain isolated and intact'if retained else'are saved or cancelled')+' at the observed UI boundary');return self.browser.close()
original_setup=x.f.setup
def setup():
 if not isinstance(x.f.browser,CheckedBrowser):x.f.browser=CheckedBrowser(x.f.browser)
 return original_setup()
x.f.setup=setup
os.environ['CONFECTORY_SHARED_BODIES']='1';sys.modules['v536_information_shared_bodies_fixture']=x
runpy.run_path(str(pathlib.Path(__file__).with_name('v536_information_shared_return_types_ui.py')),run_name='__main__')
