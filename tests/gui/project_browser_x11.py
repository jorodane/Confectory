#!/usr/bin/env python3
"""Private actual browser / shared-window-order GUI evidence; no user projects touched."""
import ctypes as c, json, os, signal, subprocess, sys, tempfile, time
from native_x11_controls import NativeControls
P=c.c_void_p; U=c.c_ulong
x=c.CDLL('libX11.so.6')
def bind(name,result,args):
    f=getattr(x,name);f.restype=result;f.argtypes=args;return f
display=bind('XOpenDisplay',P,[c.c_char_p])(None);assert display
native=NativeControls(display);root=native.root
fetch=bind('XFetchName',c.c_int,[P,U,c.POINTER(P)])
atom=bind('XInternAtom',U,[P,c.c_char_p,c.c_int])
send=bind('XSendEvent',c.c_int,[P,U,c.c_int,c.c_long,P])
def find():
    r,parent,children,count=U(),U(),P(),c.c_uint()
    native.query(display,root,c.byref(r),c.byref(parent),c.byref(children),c.byref(count))
    try:
        for win in c.cast(children,c.POINTER(U))[:count.value]:
            name=P();fetch(display,win,c.byref(name))
            if name:
                try:
                    if c.string_at(name)==b'Confectory - Project browser':return win
                finally:native.free(name)
    finally:
        if children:native.free(children)
report=json.load(open(sys.argv[1],encoding='utf8'));repo=os.path.abspath(os.path.join(os.path.dirname(__file__),'../..'))
storage=tempfile.mkdtemp(prefix='confectory-browser-gui-')
source=os.path.join(storage,'project.cpack')
with open(source,'w') as f:f.write('project BrowserFixture version "0.1.0" { entry BrowserFixture::Step; element First concept "First.celem"; element Second concept "Second.celem"; element Step function "Step.celem"; element Motion module "Motion.celem"; }')
for name,kind in [('First','concept'),('Second','concept'),('Step','function'),('Motion','module')]:
    with open(os.path.join(storage,name+'.celem'),'w') as f:f.write(kind+' BrowserFixture::'+name+(' () -> int' if kind=='function' else '')+' { }\n')
logpath=os.path.join(storage,'browser.log');log=open(logpath,'w');env=os.environ.copy();env.update(CONFECTORY_BROWSER_PROJECT=source,CONFECTORY_BROWSER_TRACE='1',CONFECTORY_ELEMENT_AUTHORING_HOST=os.path.join(repo,'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll'))
app=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=log,stderr=log,start_new_session=True)
def latest():
    lines=open(logpath).read().splitlines()
    for line in reversed(lines):
        if line.startswith('BROWSER_UI '):return json.loads(line[11:])
def wait(predicate,reason,seconds=15):
    end=time.monotonic()+seconds
    while time.monotonic()<end:
        state=latest()
        if state and predicate(state):return state
        if app.poll() is not None:raise AssertionError(reason+' exited: '+open(logpath).read()[-3000:])
        time.sleep(.04)
    raise AssertionError(reason+' '+str(latest()))
def row(state,key):return next(w for w in state['frame']['windows'] if w['id']==key)
def click(key,control):
    state=wait(lambda s:any(w['id']==key for w in s['frame']['windows']),'window present')
    r=row(state,key);field=next(v for v in r['controls'] if v['id']==control);regions=field['regions'];assert regions,'control must have visible region'
    a,b,w,h=regions[:4];native.click(window,a+min(8,w//2),b+h//2)
def close_surface():
    data=c.create_string_buffer(192);c.c_int.from_buffer(data).value=33;U.from_buffer(data,32).value=window;U.from_buffer(data,40).value=atom(display,b'WM_PROTOCOLS',0);c.c_int.from_buffer(data,48).value=32;U.from_buffer(data,56).value=atom(display,b'WM_DELETE_WINDOW',0);assert send(display,window,0,0,data);native.flush(display)
try:
    state=wait(lambda s:len(s['rows'])==2,'actual Concept rows');window=find();assert window
    click(1,100);wait(lambda s:'10' in s['fields'],'first semantic editor');click(1,101);state=wait(lambda s:'11' in s['fields'],'second semantic editor')
    assert state['editors']['10']!=state['editors']['11']
    first_handle=int(state['fields']['10']['nativeHandle']);second_handle=int(state['fields']['11']['nativeHandle']);assert first_handle!=second_handle
    original_second=state['fields']['11']['value']
    subprocess.run(['import','-window',str(window),os.path.join(storage,'browser-two-overlapping-editors.png')],check=True)
    # A visible piece of the lower native input activates its window and keeps field focus.
    first=row(state,10)['controls'][0];a,b,w,h=first['regions'][:4]
    native.click(window,a+8,b+min(8,h//2));state=wait(lambda s:s['frame']['active']==10 and s['fields']['10']['focus'],'first native click raises equal-order window')
    assert [w['id'] for w in state['frame']['windows']][-1]==10
    native.text(first_handle,'concept BrowserFixture::First { }\n// retained independent draft')
    state=wait(lambda s:'retained independent draft' in s['fields']['10']['value'],'native editing');assert state['fields']['11']['value']==original_second
    # The overlapping pixel/input ownership now belongs to the raised window.
    native.click(window,500,300);state=wait(lambda s:s['frame']['active']==10 and s['fields']['10']['focus'],'covered lower field cannot steal input')
    assert not state['fields']['11']['focus']
    click(10,23);state=wait(lambda s:row(s,10)['order']==5,'higher Render Order')
    second=row(state,11)['controls'][0];a,b,w,h=second['regions'][:4];native.click(window,a+8,b+min(8,h//2))
    state=wait(lambda s:s['frame']['active']==11 and s['fields']['11']['focus'],'lower-order field owns visible point')
    assert [w['id'] for w in state['frame']['windows']][-1]==10,'activation cannot cross higher Render Order'
    # Title drag keeps the existing native identity and text, while changing geometry.
    r=row(state,10);bounds=r['bounds'];native.drag(window,(bounds[0]+60,bounds[1]+20),(bounds[0]+105,bounds[1]+55))
    state=wait(lambda s:row(s,10)['bounds'][0]!=bounds[0],'semantic window moved');assert int(state['fields']['10']['nativeHandle'])==first_handle
    assert 'retained independent draft' in state['fields']['10']['value']
    click(10,21);state=wait(lambda s:not any(w['id']==10 for w in s['frame']['windows']),'minimize retires visual/input region');click(1,410);state=wait(lambda s:'10' in s['fields'] and s['fields']['10']['focus'],'restore native field focus');assert int(state['fields']['10']['nativeHandle'])==first_handle
    click(10,20);state=wait(lambda s:'10' not in s['editors'],'close one editor');assert int(state['fields']['11']['nativeHandle'])==second_handle
    click(1,100);state=wait(lambda s:'12' in s['fields'],'reopen first semantic editor');assert 'retained independent draft' in state['fields']['12']['value'];assert int(state['fields']['12']['nativeHandle'])!=first_handle
    # Independent tabs enumerate actual semantic kinds, preserving project context.
    click(1,2);state=wait(lambda s:s['tab']==1 and s['rows']==['BrowserFixture::Step'],'Feature tab');click(1,100);wait(lambda s:'13' in s['editors'],'Feature editor')
    click(1,3);wait(lambda s:s['tab']==2 and s['rows']==['BrowserFixture::Motion'],'Module tab')
    subprocess.run(['import','-window',str(window),os.path.join(storage,'browser-multiple-semantic-editors.png')],check=True)
    close_surface();assert app.wait(timeout=20)==0
    assert 'Project browser semantic editors, native inputs, workspace and Owner disposed' in open(logpath).read()
    assert open(os.path.join(storage,'First.celem')).read()=='concept BrowserFixture::First { }\n','draft editing does not save or rename sources implicitly'
    print('Project browser actual X11: semantic kinds, independent native inputs, shared occlusion/hit order, equal-order activation, higher-order boundary, move/minimize/restore/close and cleanup PASS; private evidence '+storage)
finally:
    if app.poll() is None:os.killpg(app.pid,signal.SIGINT);app.wait(timeout=20)
    log.close()
