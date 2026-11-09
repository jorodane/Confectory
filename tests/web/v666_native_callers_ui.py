"""Authored information editor lifecycle with an actual retained native caller."""
import os,pathlib,runpy,sys
import v666_native_callers_fixture as x
os.environ['CONFECTORY_SHARED_BODIES']='1';sys.modules['v536_information_shared_bodies_fixture']=x
if x.mode=='conflict':
 import json
 original_setup=x.f.setup
 def observed_setup():
  page=original_setup()
  def trace(source,payload):
   with(x.f.case/'save-clicks.jsonl').open('a')as out:out.write(json.dumps(payload,ensure_ascii=False)+'\n')
  page.expose_binding('recordNativeCallerSaveClick',trace)
  page.evaluate("""()=>{for(const type of ['pointerdown','pointerup','click'])document.addEventListener(type,e=>{const button=e.target.closest?.('[data-element-action=save]');if(button)window.recordNativeCallerSaveClick({type,trusted:e.isTrusted,connected:button.isConnected,disabled:button.disabled,defaultPrevented:e.defaultPrevented,button:button.outerHTML,status:document.querySelector('#status')?.textContent,owner:button.closest('.window')?.dataset.key})},true)}""")
  return page
 x.f.setup=observed_setup
runpy.run_path(str(pathlib.Path(__file__).with_name('v536_information_shared_return_types_ui.py')),run_name='__main__')
