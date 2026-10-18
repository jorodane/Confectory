#!/usr/bin/env python3
"""Actual entry/home X11 acceptance; private evidence only."""
import ctypes as c
import json
import os
import subprocess
import signal
import sys
import time
lib=c.CDLL('libX11.so.6'); P=c.c_void_p; U=c.c_ulong; L=c.c_long

def native(name,result,*args):
    fn=getattr(lib,name);fn.restype=result;fn.argtypes=list(args);return fn
open_display=native('XOpenDisplay',P,c.c_char_p)
root_window=native('XDefaultRootWindow',U,P)
query=native('XQueryTree',c.c_int,P,U,c.POINTER(U),c.POINTER(U),c.POINTER(P),c.POINTER(c.c_uint))
fetch=native('XFetchName',c.c_int,P,U,c.POINTER(P));free=native('XFree',c.c_int,P)
flush=native('XFlush',c.c_int,P);send=native('XSendEvent',c.c_int,P,U,c.c_int,L,P)
keycode=native('XKeysymToKeycode',c.c_ubyte,P,U)
image=native('XGetImage',P,P,U,c.c_int,c.c_int,c.c_uint,c.c_uint,U,c.c_int)
pixel=native('XGetPixel',U,P,c.c_int,c.c_int);destroy=native('XDestroyImage',c.c_int,P)
atom=native('XInternAtom',U,P,c.c_char_p,c.c_int)
class Event(c.Structure):
    _fields_=[('type',c.c_int),('serial',U),('send',c.c_int),('display',P),('window',U),('root',U),('subwindow',U),('time',U),('x',c.c_int),('y',c.c_int),('xr',c.c_int),('yr',c.c_int),('state',c.c_uint),('detail',c.c_uint),('same',c.c_int)]
display=open_display(None);assert display,'Live X11 DISPLAY required'
from native_x11_controls import NativeControls
native_controls=NativeControls(display)
root=root_window(display);report=json.load(open(sys.argv[1],encoding='utf-8'))

def find(wanted):
    r,parent,children,count=U(),U(),P(),c.c_uint();query(display,root,c.byref(r),c.byref(parent),c.byref(children),c.byref(count))
    try:
        for window in c.cast(children,c.POINTER(U))[:count.value]:
            name=P();fetch(display,window,c.byref(name))
            if name:
                try:
                    if c.string_at(name)==wanted:return window
                finally:free(name)
    finally:
        if children:free(children)

def await_window(wanted):
    end=time.monotonic()+10
    while time.monotonic()<end:
        window=find(wanted)
        if window:return window
        time.sleep(.01)
    raise AssertionError('Game surface not mapped')

def press(window,key):
    if 'latest' in globals():
        trace=latest();field=trace.get('fields',{}).get(str(trace.get('focus',0))) if trace else None
        if isinstance(field,str):field=json.loads(field)
        if field and field.get('native') and field.get('visible'):
            native_controls.key(int(field['nativeHandle']),key);return
    for kind in (2,3):
        event=Event(kind,0,1,display,window,root,0,100,0,0,0,0,0,keycode(display,key if isinstance(key,int) else ord(key)),1)
        buffer=c.create_string_buffer(192);c.memmove(buffer,c.byref(event),c.sizeof(event));assert send(display,window,0,0,buffer)
    flush(display)

def colored(window,color):
    bitmap=image(display,window,0,0,400,240,U(-1).value,2);assert bitmap
    try:
        points=[]
        for y in range(50,230,2):
            for x in range(70,380,2):
                if pixel(bitmap,x,y)&0xffffff==color:points.append((x,y))
        return points
    finally:destroy(bitmap)

def wait_color(window,color,predicate,seconds):
    end=time.monotonic()+seconds
    while time.monotonic()<end:
        points=colored(window,color)
        if points and predicate(points):return points
        time.sleep(.005)
    raise AssertionError(f'Expected visible color {color:x} position not observed')

def close(window):
    buffer=c.create_string_buffer(192);c.c_int.from_buffer(buffer,0).value=33
    U.from_buffer(buffer,32).value=window;U.from_buffer(buffer,40).value=atom(display,b'WM_PROTOCOLS',0)
    c.c_int.from_buffer(buffer,48).value=32;U.from_buffer(buffer,56).value=atom(display,b'WM_DELETE_WINDOW',0)
    assert send(display,window,0,0,buffer);flush(display)


import tempfile,shutil,shlex
lookup=native('XKeycodeToKeysym',U,P,c.c_ubyte,c.c_int)
resize=native('XResizeWindow',c.c_int,P,U,c.c_uint,c.c_uint)
raise_window=native('XRaiseWindow',c.c_int,P,U)

from pathlib import Path
repo=os.path.abspath(os.path.join(os.path.dirname(__file__),'../..'))
storage=tempfile.mkdtemp(prefix='confectory-native-details-');root_path=Path(storage);home_storage=root_path/'storage';home_storage.mkdir();projects=[root_path/'first',root_path/'second'];original={}
for project in projects:
 shutil.copytree(Path(repo)/'examples/button-game',project,ignore=shutil.ignore_patterns('.confectory'));manifest=project/'project.cpack';manifest.write_text(manifest.read_text().replace('../../',repo+'/'));original.update({p:p.read_bytes() for p in project.rglob('*') if p.is_file()})
cards=[{'path':str(project/'project.cpack'),'title':'Native project '+str(i+1),'description':'Owned native listing'} for i,project in enumerate(projects)]+[{'path':str(root_path/'missing.cpack'),'title':'Missing native project','description':'Unavailable'}];catalog=home_storage/'projects.json';catalog.write_text(json.dumps(cards))
log_path=os.path.join(storage,'native.log');env=os.environ.copy();env.pop('CONFECTORY_UI',None);env.pop('CONFECTORY_WEB_PROJECT',None);env.update(CONFECTORY_EDITOR_REPO=repo,CONFECTORY_HOME_STORAGE=str(home_storage),CONFECTORY_ENTRY_STORAGE=str(home_storage),CONFECTORY_HOME_TRACE='1',CONFECTORY_ELEMENT_AUTHORING_HOST=os.path.join(repo,'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll'),XDG_DATA_HOME=str(root_path/'data'),XDG_CACHE_HOME=str(root_path/'cache'))
app=None;log=None;launch_count=0

def launch():
    global app,log,launch_count
    if launch_count and os.path.isfile(log_path):shutil.copy2(log_path,os.path.join(storage,f"native-launch-{launch_count}.log"))
    launch_count+=1
    log=open(log_path,'w',encoding='utf-8');app=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    return await_window(b'Confectory - Projects')

def latest():
    value=None
    with open(log_path,encoding='utf-8') as stream:
        for line in stream:
            if line.startswith('HOME_UI '):
                try:value=json.loads(line[8:])
                except json.JSONDecodeError:pass
    return value

def wait(predicate,message,seconds=30):
    end=time.monotonic()+seconds
    while time.monotonic()<end:
        state=latest()
        if state and predicate(state):return state
        if app.poll() is not None:raise AssertionError('Entry/home exited: '+open(log_path).read()[-3000:])
        time.sleep(.04)
    raise AssertionError(message+' '+str(latest()))

def click(window,id):
    raise_window(display,window);flush(display)
    state=wait(lambda t:id in t['hits'][::5],f'Control {id} unavailable')
    field=state.get('fields',{}).get(str(id))
    if isinstance(field,str):field=json.loads(field)
    if field and field.get('native'):
        native_controls.click(int(field['nativeHandle']),min(50,field['bounds'][2]//2),field['bounds'][3]//2);wait(lambda t:t['focus']==id,'native pointer focus');return
    n=state['hits'][::5].index(id)*5;_,x,y,w,h=state['hits'][n:n+5]
    for kind in (4,5):
        event=Event(kind,0,1,display,window,root,0,100,x+w//2,y+h//2,0,0,0,1,1)
        buf=c.create_string_buffer(192);c.memmove(buf,c.byref(event),c.sizeof(event));assert send(display,window,0,0,buf)
        flush(display);time.sleep(.04)
    time.sleep(.15)

def leave_project(window):
    click(window,33);wait(lambda t:t['model']['shell']['menu']=='project','project menu')
    click(window,15)

def type_text(window,text):
    trace=wait(lambda t:t['focus'] in [int(k) for k in t.get('fields',{})],'native text focus');field=trace['fields'].get(str(trace['focus']))
    if isinstance(field,str):field=json.loads(field)
    assert field and field.get('native'),'Visible input must use a native widget'
    native_controls.text(int(field['nativeHandle']),text)

def screenshot(window,name):
    path=os.path.join(storage,name+'.png');subprocess.run(['import','-window',str(window),path],check=True);return path

def end(window,interrupt=False):
    if interrupt:os.killpg(app.pid,signal.SIGINT)
    else:close(window)
    assert app.wait(timeout=30)==0,open(log_path).read()[-5000:];log.close()
    assert 'Entry/home jobs, controls, buffers, Owner, project contexts and native surface disposed' in open(log_path).read()

def field(id):
 state=wait(lambda t:id in t['hits'][::5] and not t['job'],'native field '+str(id));value=state['fields'][str(id)];value=json.loads(value) if isinstance(value,str) else value;assert value['native'] and value['provider']=='gtk3',value;return value

def fill(window,id,text):
 click(window,id);type_text(window,text);wait(lambda t:json.loads(t['fields'][str(id)])['text']==text,'typed native value '+str(id))
def idle(screen):return wait(lambda t:t['screen']==screen and not t['job'],screen+' idle')
def invariant(context=None):
 state=latest();model=state['model'];assert len(model['cards'])==3,model['cards'];assert all(path.read_bytes()==raw for path,raw in original.items()),'confirmed source changed';assert len(list(root_path.rglob('project.cpack')))==2,'detail view created an empty project'
 if context is not None:assert model['selected']['context']==context
 assert not model.get('ai') and not model.get('aiPreview') and not model.get('aiBindings') and not model.get('aiRuns'),model
 return state

def info(window,id=500):
 if latest()['screen']=='project':click(window,33);wait(lambda t:t['model']['shell']['menu']=='project','project menu');click(window,34)
 else:click(window,id)
 idle('information');return field(433)['text']
def source_score(window):
 if latest()['model'].get('workspace') is None:click(window,55);wait(lambda t:(t['model'].get('workspace') or {}).get('unit') and not t['job'],'source workspace')
 model=latest()['model'];units=model['workspace']['units'];ids=[row['id'] for row in units];target=ids.index('Example.ButtonGame::Score')
 while latest()['model']['workspace']['selected']!='Example.ButtonGame::Score':
  current=ids.index(latest()['model']['workspace']['selected']);expected=ids[current+(1 if current<target else -1)];click(window,57 if current<target else 56);wait(lambda t:t['model']['workspace']['selected']==expected and not t['job'],'select native owned source')
 return field(54)

try:
 a=launch();wait(lambda t:t['screen']=='intro' and 1 in t['hits'][::5],'intro');click(a,1);idle('home')
 text=info(a);assert 'Kind: project' in text and 'Confectory.FrameControl' in text and 'Reached packs: available' in text;text_token=field(431)['binding'];assert field(433)['readonly'];assert not any((project/'.confectory').exists() for project in projects);invariant()
 fill(a,431,'Native edited title');fill(a,432,'Unapplied listing text');click(a,430);idle('home');info(a);assert field(431)['text']=='Native edited title' and field(431)['binding']==text_token;assert json.loads(catalog.read_text())[0]['title']=='Native project 1';click(a,434);wait(lambda t:t['model'].get('projectInformation',{}).get('title')=='Native edited title' and not t['job'],'information save');assert json.loads(catalog.read_text())[0]['description']=='Unapplied listing text'
 fill(a,432,'CAS retained native input');saved_catalog=catalog.read_bytes();catalog.write_bytes(saved_catalog+b'\n');click(a,434);wait(lambda t:t['model']['status'].startswith('Error:') and not t['job'],'listing CAS refused');assert field(432)['text']=='CAS retained native input' and catalog.read_bytes()==saved_catalog+b'\n';catalog.write_bytes(saved_catalog);click(a,440);click(a,430);idle('home');text=info(a,502);assert 'unavailable' in text and latest()['model']['selected'] is None;click(a,430);idle('home');assert not Path(cards[2]['path']).exists();Path(cards[2]['path']).write_text('pack NativeLibrary version \"1\" {}');text=info(a,502);assert 'Kind: pack' in text and 'Reached packs: unsupported' in text;click(a,430);idle('home');Path(cards[2]['path']).unlink();invariant()
 click(a,8);idle('profile');assert latest()['model']['selected'] is None;assert 'No eligible Helper' in field(438)['text'];click(a,447);wait(lambda t:len(t['model']['helpers'])==1 and not t['job'],'global local recruitment');helper_file=home_storage/'helpers/helpers.json';helper_before=helper_file.read_bytes();assert field(438)['readonly'];fill(a,435,'Native chief');fill(a,436,'Native display role');fill(a,437,'Native display biography');fill(a,439,'GLOBAL NATIVE UNSENT');profile_token=field(435)['binding'];click(a,430);idle('home');click(a,8);idle('profile');assert field(435)['text']=='Native chief' and field(435)['binding']==profile_token;assert not list((home_storage/'helper-presentations').glob('*.json'));click(a,434);wait(lambda t:'saved;' in t['message'] and not t['job'],'profile explicit save');profile_file=next((home_storage/'helper-presentations').glob('*.json'));assert json.loads(profile_file.read_text())['globalDraft']=='GLOBAL NATIVE UNSENT' and helper_file.read_bytes()==helper_before;screenshot(a,'profile-saved')
 fill(a,435,'Native conflict retained');external=json.loads(profile_file.read_text());external['description']='External native display';profile_file.write_text(json.dumps(external));click(a,434);wait(lambda t:t['model']['status'].startswith('Error:') and not t['job'],'profile CAS refused');assert field(435)['text']=='Native conflict retained' and json.loads(profile_file.read_text())['description']=='External native display';click(a,440);wait(lambda t:json.loads(t['fields']['437'])['text']=='External native display','explicit discard reload');assert field(437)['text']=='External native display';saved_profile=profile_file.read_bytes();profile_file.write_text('{corrupt retained');click(a,430);idle('home');click(a,8);idle('profile');assert 'unavailable' in field(438)['text'] and 434 not in latest()['hits'][::5] and profile_file.read_text()=='{corrupt retained';profile_file.write_bytes(saved_profile);click(a,430);idle('home')
 click(a,100);idle('project');context=latest()['model']['selected']['context'];project_id=latest()['model']['selected']['projectId'];click(a,8);wait(lambda t:(t['model'].get('helperPanel') or {}).get('mode')=='helpers' and not t['job'],'project helper chooser');click(a,20);wait(lambda t:(t['model'].get('helperContext') or {}).get('helper')=='main-helper' and not t['job'],'selected helper');click(a,42);wait(lambda t:any('Native chief' in text for text in t['texts']),'native display identity')
 src=source_score(a);pending=src['text']+'\n// NATIVE_UNAPPLIED';fill(a,54,pending);source_token=field(54)['binding'];fill(a,38,'PROJECT NATIVE UNSENT');chat_token=field(38)['binding']
 text=info(a);assert 'main-helper' in text;assert latest()['model']['selected']['context']==context;fill(a,432,'Project info input retained');click(a,441);idle('profile');assert field(439)['text']=='GLOBAL NATIVE UNSENT';fill(a,435,'Cancelled native name');click(a,430);idle('information');assert field(432)['text']=='Project info input retained';click(a,430);idle('project');click(a,42);assert field(54)['text']==pending and field(54)['binding']==source_token;assert field(38)['text']=='PROJECT NATIVE UNSENT' and field(38)['binding']==chat_token;invariant(context);screenshot(a,'project-input-retained')
 leave_project(a);idle('home');click(a,103);idle('project');second_context=latest()['model']['selected']['context'];assert second_context!=context;info(a);click(a,430);idle('project');click(a,42);leave_project(a);idle('home');click(a,100);idle('project');assert latest()['model']['selected']['context']==context;src=source_score(a);assert src['text']==pending and src['binding']==source_token;invariant(context)
 # New process restores only explicit display saves; a view never restores execution authority.
 end(a,True)
 # Seed valid owner-local persisted recruitment records; no provider, account or product-only test path.
 helper_records=json.loads(helper_file.read_text());base_record=helper_records['helpers']['main-helper']
 for index in range(30):
  helper_id='z-fixture-'+str(index).zfill(2);record=json.loads(json.dumps(base_record));template=json.loads(record['template']);template['helper']=helper_id;record['template']=json.dumps(template);helper_records['helpers'][helper_id]=record
 helper_file.write_text(json.dumps(helper_records));a=launch();wait(lambda t:t['screen']=='intro' and 1 in t['hits'][::5],'cold intro');click(a,1);idle('home');assert latest()['model']['selected'] is None;info(a);assert field(431)['text']=='Native edited title';click(a,430);idle('home');click(a,8);idle('profile');assert field(435)['text']=='Native chief' and field(437)['text']=='External native display' and field(439)['text']=='GLOBAL NATIVE UNSENT';invariant();screenshot(a,'cold-profile')
 for index in range(30):
  expected='z-fixture-'+str(index).zfill(2);click(a,444);wait(lambda t:t['detailKey']=='profile/'+expected,'next persisted profile');assert field(435)['text']==expected
  if index==0:fill(a,437,'RETAINED while browsing 31 profiles')
 for index in reversed(range(30)):
  expected='main-helper' if index==0 else 'z-fixture-'+str(index-1).zfill(2);click(a,443);wait(lambda t:t['detailKey']=='profile/'+expected,'previous persisted profile')
  if index==1:assert field(437)['text']=='RETAINED while browsing 31 profiles'
 assert field(435)['text']=='Native chief';invariant()
 (root_path/'evidence.json').write_text(json.dumps({'projectId':project_id,'contexts':[context,second_context],'cards':3,'projectManifests':2,'unchangedSources':len(original),'provider':'gtk3-x11','profileSaved':True,'sourceAndChatBindingPreserved':True,'casRefusals':2,'coldExplicitSave':True,'eligibleProfilesBrowsed':31,'nativeFieldBudgetUnchanged':128},indent=2));end(a);app=None
 print('PASS native Home information/profile: GTK widgets, reachability, explicit save/CAS/cancel, same project source/chat buffers, two contexts and cold; no AI/project creation '+storage)
except Exception:
 print('Native evidence:',storage,flush=True)
 try:screenshot(a,'failure')
 except Exception:pass
 raise
finally:
 if app and app.poll() is None:os.killpg(app.pid,signal.SIGTERM);app.wait(timeout=15)
