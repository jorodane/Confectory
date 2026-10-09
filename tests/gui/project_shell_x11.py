#!/usr/bin/env python3
"""Actual project-shell acceptance; private evidence only."""
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
repo=os.path.abspath(os.path.join(os.path.dirname(__file__),'../..'))
storage=tempfile.mkdtemp(prefix='confectory-project-shell-gui-')
for n in range(10):os.mkdir(os.path.join(storage,f'Folder{n:02d}'))
log_path=os.path.join(storage,'native.log')
env=os.environ.copy();env.update(CONFECTORY_EDITOR_REPO=repo,CONFECTORY_HOME_STORAGE=storage,CONFECTORY_HOME_TRACE='1',CONFECTORY_ELEMENT_AUTHORING_HOST=os.path.join(repo,'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll'))
folder_request=os.path.join(storage,'folder-request.txt');os_helper=os.path.join(storage,'os-helper');os.mkdir(os_helper)
with open(os.path.join(os_helper,'xdg-open'),'w') as stream:stream.write('#!/bin/sh\nprintf "%s\\n" "$1" > '+shlex.quote(folder_request)+'\n')
os.chmod(os.path.join(os_helper,'xdg-open'),0o700);env['PATH']=os_helper+os.pathsep+env.get('PATH','')
stall=os.path.join(storage,'stall-description')
wrapper=os.path.join(storage,'existing-dotnet-test-wrapper.sh')
with open(wrapper,'w') as stream:stream.write('#!/bin/sh\nif [ "$2" = "describe" ] && [ -f '+shlex.quote(stall)+' ]; then sleep 1; fi\nexec '+shlex.quote(os.environ.get('CONFECTORY_DOTNET') or shutil.which('dotnet'))+' "$@"\n')
os.chmod(wrapper,0o700);env['CONFECTORY_DOTNET']=os.environ.get('CONFECTORY_DOTNET') or shutil.which('dotnet')
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

def assert_text_and_field_pixels(window,state):
    # Button text uses layout top-left origins; glyphs must occupy the upper half,
    # with no baseline shifted into a bottom crop. Multiline empty space keeps content color.
    ids=state['hits'][::5];n=ids.index(13)*5;_,x,y,w,h=state['hits'][n:n+5]
    bitmap=image(display,window,x,y,w,h,U(-1).value,2);assert bitmap
    try:assert sum(pixel(bitmap,i,j)==0xFFFFFF for i in range(w) for j in range(h//2))>8,'button text vertically clipped'
    finally:destroy(bitmap)
    field=json.loads(state['fields']['11']);x,y,w,h=field['bounds']
    bitmap=image(display,window,x,y,w,h,U(-1).value,2);assert bitmap
    try:assert pixel(bitmap,w//2,h-8)==0x1C2933,'unused multiline space must use content background';assert pixel(bitmap,0,h//2)==0x77AAC6,'focused border remains distinct'
    finally:destroy(bitmap)

def end(window,interrupt=False):
    if interrupt:os.killpg(app.pid,signal.SIGINT)
    else:close(window)
    assert app.wait(timeout=30)==0,open(log_path).read()[-5000:];log.close()
    assert 'Entry/home jobs, controls, buffers, Owner, project contexts and native surface disposed' in open(log_path).read()
try:
    a=launch();wait(lambda t:t['screen']=='intro' and 1 in t['hits'][::5],'intro');click(a,1);wait(lambda t:t['screen']=='home','offline home');home=latest()['controls']
    click(a,2);wait(lambda t:t['screen']=='create','new');click(a,10);type_text(a,'Shell Gui A');click(a,11);type_text(a,'A project workspace');click(a,13)
    state=wait(lambda t:t['screen']=='project' and t['model']['shell'],'project owns shell');context=state['model']['selected']['context'];path=state['model']['selected']['path'];assert state['model']['shell']['project']['context']==context and not state['model']['shell']['liveProvider'];project_control=state['controls'];assert project_control!=home
    wait(lambda t:38 in t['hits'][::5],'project chat field');click(a,38);type_text(a,'A local project draft');click(a,41);state=wait(lambda t:t['model']['shell']['draft']=='A local project draft','local draft retained without live sending');buffer=state['chatBuffers'][context];assert 'no message sent' in state['model']['shell']['notice']
    screenshot(a,'project-chat')
    # Actual product Helper controls use public scoped memory, without a model/provider.
    click(a,8);wait(lambda t:(t['model'].get('helperPanel') or {}).get('mode')=='helpers' and 23 in t['hits'][::5],'explicit Helper selection')
    click(a,23);wait(lambda t:len(t['model']['helpers'])==1 and 20 in t['hits'][::5],'recruit global Main Helper')
    click(a,20);state=wait(lambda t:(t['model'].get('helperPanel') or {}).get('mode')=='helper' and t['model'].get('helperContext',{}).get('helper')=='main-helper','connect global Helper to current project')
    assert state['model']['helperContext']['projectId']==state['model']['selected']['projectId']
    click(a,26);wait(lambda t:len(t['model']['helperContext']['memory'])==1,'remember draft only for project')
    click(a,27);wait(lambda t:t['model']['status'].startswith('Saved common'),'explicit common record')
    assert len(latest()['model']['helperContext']['memory'])==1
    click(a,25);wait(lambda t:len(t['model']['helperContext']['memory'])==2,'explicit common memory permission')
    click(a,25);wait(lambda t:len(t['model']['helperContext']['memory'])==1,'exclude common memory again')
    screenshot(a,'helper-project-scope');click(a,42);wait(lambda t:t['model']['shell']['menu']=='','close Helper controls')
    assert latest()['chatBuffers'][context]==buffer and latest()['model']['shell']['draft']=='A local project draft'

    # Tab/panel changes reuse the same borrowed context and buffer, with hidden controls ineligible.
    click(a,40);state=wait(lambda t:t['model']['shell']['tab']=='logs' and 38 not in t['hits'][::5],'logs tab hides chat interaction');assert state['model']['selected']['context']==context;assert state['model']['shell']['latestLog']
    state=wait(lambda t:53 in t['hits'][::5],'enabled read-only native log View');log_field=json.loads(state['fields']['53']);assert log_field['native'] and log_field['readonly'] and log_field['enabled'];expected_logs='\n'.join(state['model']['shell']['logs']);assert log_field['text']==expected_logs
    click(a,53);log_handle=int(log_field['nativeHandle']);native_controls.drag(log_handle,(8,12),(min(110,log_field['bounds'][2]-8),12));wait(lambda t:json.loads(t['fields']['53'])['caret']!=json.loads(t['fields']['53'])['anchor'],'native drag-select logs');native_controls.key(log_handle,'a',(0xFFE3,));native_controls.key(log_handle,'c',(0xFFE3,));native_controls.key(log_handle,'q');native_controls.key(log_handle,'x',(0xFFE3,));native_controls.key(log_handle,'v',(0xFFE3,));time.sleep(.3);state=latest();unchanged=json.loads(state['fields']['53']);assert unchanged['text']==expected_logs and unchanged['nativeHandle']==log_field['nativeHandle'];assert unchanged['caret']!=unchanged['anchor'],'unchanged renders retain native selection'
    click(a,39);wait(lambda t:t['model']['shell']['tab']=='chat' and 38 in t['hits'][::5],'chat tab');assert latest()['chatBuffers'][context]==buffer
    click(a,38);chat_field=json.loads(latest()['fields']['38']);chat_handle=int(chat_field['nativeHandle']);native_controls.key(chat_handle,'a',(0xFFE3,));native_controls.key(chat_handle,'v',(0xFFE3,));wait(lambda t:json.loads(t['fields']['38'])['text']==expected_logs,'native logs copy/paste into editable chat');native_controls.text(chat_handle,'A local project draft');wait(lambda t:json.loads(t['fields']['38'])['text']=='A local project draft','restore synthetic local draft')
    click(a,33);state=wait(lambda t:t['model']['shell']['menu']=='project' and 34 in t['hits'][::5],'project name menu');assert 38 in state['hits'][::5] and 36 in state['hits'][::5]
    modal_field=json.loads(state['fields']['38']);assert modal_field['visible'] and modal_field['enabled'],'ordinary panel preserves visible native text interaction';assert modal_field['nativeHandle']==chat_field['nativeHandle']
    click(a,34);wait(lambda t:t['model']['shell']['menu']=='info','project info');state=latest();menu_bounds=(216,58,440,290);workspace_clips=[state['textClips'][n*4:n*4+4] for n,text in enumerate(state['texts']) if text=='Workspace'];assert all(x>=menu_bounds[0]+menu_bounds[2] or x+w<=menu_bounds[0] or y>=menu_bounds[1]+menu_bounds[3] or y+h<=menu_bounds[1] for x,y,w,h in workspace_clips),'Workspace text clips exclude covered menu region';screenshot(a,'project-info');click(a,42);wait(lambda t:t['model']['shell']['menu']=='','close info')
    click(a,33);wait(lambda t:t['model']['shell']['menu']=='project','menu');click(a,35);wait(lambda t:t['model']['shell']['menu']=='settings','honest read-only settings');click(a,42);wait(lambda t:t['model']['shell']['menu']=='','close settings')
    click(a,6);wait(lambda t:t['model']['shell']['menu']=='providers','provider panel remains offline');assert not latest()['model']['shell']['liveProvider'];click(a,42);wait(lambda t:t['model']['shell']['menu']=='','close providers')
    click(a,33);wait(lambda t:t['model']['shell']['menu']=='project','folder menu');click(a,16);assert open(folder_request).read().strip()==os.path.dirname(path);click(a,42);wait(lambda t:t['model']['shell']['menu']=='','close folder menu')
    # Execute only this ProjectPack's declared entry, not the editor, and drain meaningful bounded output.
    with open(os.path.join(os.path.dirname(path),'main.csbody'),'w') as stream:stream.write('Console.WriteLine("GUI shell child A");while(true)System.Threading.Thread.Sleep(20);\n')
    click(a,36);state=wait(lambda t:t['model']['execution']['state']=='running','owned child running',seconds=90);assert state['model']['selected']['context']==context
    wait(lambda t:'GUI shell child A' in t['model']['shell']['latestLog'] or any('GUI shell child A' in line for line in t['model']['shell']['logs']),'child log visible')
    click(a,40);wait(lambda t:t['model']['shell']['tab']=='logs','run logs');screenshot(a,'project-running');state=latest();assert state['model']['shell']['project']['context']==context;log_field=json.loads(state['fields']['53']);native_controls.scroll(int(log_field['nativeHandle']),12,12,4);native_controls.scroll(int(log_field['nativeHandle']),12,12,-4);assert json.loads(latest()['fields']['53'])['text']=='\n'.join(latest()['model']['shell']['logs'])
    resize(display,a,640,520);flush(display);state=wait(lambda t:t['width']==640 and 37 in t['hits'][::5],'responsive shell');assert state['controls']==project_control
    for i in range(0,len(state['hits']),5):_,x,y,w,h=state['hits'][i:i+5];assert 0<=x<x+w<=640 and 0<=y<y+h<=520
    screenshot(a,'project-narrow');click(a,7);wait(lambda t:not t['sidebar'],'sidebar collapsed');click(a,7);wait(lambda t:t['sidebar'],'sidebar restored')
    leave_project(a);state=wait(lambda t:t['screen']=='home' and t['model']['selected'] is None,'hide running project');assert state['model']['executions'][context]['state']=='running';assert any(p['context']==context for p in state['model']['backgroundProjects'])
    click(a,19);wait(lambda t:t['screen']=='background' and 20 in t['hits'][::5],'hidden project icon');screenshot(a,'hidden-running-project');click(a,20);wait(lambda t:t['screen']=='project' and t['model']['selected']['context']==context,'restore original running project')
    click(a,33);wait(lambda t:t['model']['shell']['menu']=='project','complete-close menu');click(a,52);state=wait(lambda t:t['model'].get('closeRequest') is not None and 65 in t['hits'][::5],'working close confirmation');assert 38 not in state['hits'][::5];screenshot(a,'working-close-confirmation');click(a,66);wait(lambda t:t['model'].get('closeRequest') is None and t['model']['execution']['state']=='running','cancel close keeps work')
    click(a,37);wait(lambda t:t['model']['execution']['state']=='stopped','stop one child');click(a,39);wait(lambda t:38 in t['hits'][::5],'return draft');assert latest()['chatBuffers'][context]==buffer
    click(a,40);wait(lambda t:t['model']['shell']['tab']=='logs','hide retained chat before resize');resize(display,a,700,540);flush(display);wait(lambda t:t['width']==700 and t['height']==540,'resize while chat binding hidden')
    leave_project(a);state=wait(lambda t:t['screen']=='home' and t['model']['selected'] is None and t['model']['shell'] is None,'leave hides project chat without null project');assert state['controls']==home
    # Create a second project: its chat starts independently and cannot select/open project A.
    click(a,2);wait(lambda t:t['screen']=='create','second New');click(a,10);type_text(a,'Shell Gui B');click(a,13);state=wait(lambda t:t['screen']=='project' and t['model']['selected']['title']=='Shell Gui B','second context')
    other=state['model']['selected']['context'];assert other!=context and state['model']['shell']['draft']=='';wait(lambda t:38 in t['hits'][::5],'B field');assert latest()['chatBuffers'][other]!=buffer
    click(a,38);type_text(a,'B private draft');click(a,41);wait(lambda t:t['model']['shell']['draft']=='B private draft','B draft');leave_project(a);wait(lambda t:t['screen']=='home','leave B')
    click(a,100);state=wait(lambda t:t['screen']=='project' and t['model']['selected']['context']==context,'explicit reopen A');click(a,39);wait(lambda t:38 in t['hits'][::5],'A chat');assert latest()['model']['shell']['draft']=='A local project draft' and latest()['chatBuffers'][context]==buffer
    # Interrupt an actual owned build/execution; final manager disposal stops only its worker tree.
    click(a,36);wait(lambda t:t['model']['execution']['state'] in ('building','running'),'active build/execution remains responsive');click(a,33);wait(lambda t:t['model']['shell']['menu']=='project','final project close menu');click(a,52);wait(lambda t:t['model'].get('closeRequest') is not None,'final working close confirmation');click(a,65);state=wait(lambda t:t['screen']=='home' and t['model']['selected'] is None,'confirmed close retires project');assert context not in state['chatBuffers'];click(a,100);state=wait(lambda t:t['screen']=='project','reopen fully closed project');assert state['model']['selected']['context']!=context and state['model']['shell']['draft']=='A local project draft';click(a,36);wait(lambda t:t['model']['execution']['state'] in ('building','running'),'reopened execution');end(a,interrupt=True)
    # Restart does not open any project merely because a remembered project/chat exists.
    a=launch();wait(lambda t:t['screen']=='intro' and 1 in t['hits'][::5],'restart');click(a,1);state=wait(lambda t:t['screen']=='home' and len(t['model']['cards'])==2,'restart project catalog');assert state['model']['selected'] is None and state['model']['shell'] is None and not state['chatBuffers'];end(a)
    print('Project shell actual X11 project-to-chat context, sidebar/menu/info/settings/folder, local draft/tab isolation, Run/Stop/logs, resize/cancel/modal, explicit leave/reopen, no null restart, active build/execution interruption and cleanup PASS')
    print('Private GUI evidence: '+storage)
finally:
    if app is not None and app.poll() is None:os.killpg(app.pid,signal.SIGTERM);app.wait(timeout=10)
    if log is not None and not log.closed:log.close()
