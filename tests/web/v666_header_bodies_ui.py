"""Original mixed Save, interrupted/repeated/restarted/conflicting UI paths."""
import json,os,pathlib,runpy,sys
import v666_header_bodies_fixture as x
class CheckedBrowser:
 def __init__(self,browser):self.browser=browser
 def __getattr__(self,name):return getattr(self.browser,name)
 def close(self):
  cells=x.d.pending();retained=x.mode in ['conflict','projects','reproduce-header-ui']
  assert len(cells)==(4 if retained else 0),cells
  if retained:
   assert next(v['text']for _,v in cells if v['kind']=='description')==x.description
   assert next(v['text']for _,v in cells if v['kind']=='icon')==x.icon
  x.f.checked('all four mixed inputs '+('remain isolated and intact'if retained else'are explicitly saved or cancelled')+' at the observed UI boundary');return self.browser.close()
original_setup=x.f.setup
def setup():
 if not isinstance(x.f.browser,CheckedBrowser):x.f.browser=CheckedBrowser(x.f.browser)
 page=original_setup()
 if x.mode=='conflict':
  def trace(source,payload):
   with(x.f.case/'save-clicks.jsonl').open('a')as out:out.write(json.dumps(payload,ensure_ascii=False)+'\n')
  page.expose_binding('recordMixedSaveClick',trace)
  page.evaluate("""()=>{for(const type of ['pointerdown','pointerup','click'])document.addEventListener(type,e=>{const b=e.target.closest?.('[data-element-action=save]');if(b)window.recordMixedSaveClick({type,trusted:e.isTrusted,disabled:b.disabled,status:document.querySelector('#status')?.textContent})},true)}""")
 return page
x.f.setup=setup
os.environ['CONFECTORY_SHARED_BODIES']='1';sys.modules['v536_information_shared_bodies_fixture']=x
runpy.run_path(str(pathlib.Path(__file__).with_name('v536_information_shared_return_types_ui.py')),run_name='__main__')
