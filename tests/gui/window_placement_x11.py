"""Real X11 pointer/resize and painted snap feedback using public placement contracts."""
import ctypes as c, json, os, signal, subprocess, sys, tempfile, time
from native_x11_controls import NativeControls
P=c.c_void_p; U=c.c_ulong
x=c.CDLL('libX11.so.6')
def bind(name,result,args):
    f=getattr(x,name);f.restype=result;f.argtypes=args;return f
display=bind('XOpenDisplay',P,[c.c_char_p])(None);assert display
native=NativeControls(display)
native.button(display,1,0,0);native.flush(display)
fetch=bind('XFetchName',c.c_int,[P,U,c.POINTER(P)])
get_image=bind('XGetImage',P,[P,U,c.c_int,c.c_int,c.c_uint,c.c_uint,U,c.c_int])
get_pixel=bind('XGetPixel',U,[P,c.c_int,c.c_int]);destroy_image=bind('XDestroyImage',c.c_int,[P])
atom=bind('XInternAtom',U,[P,c.c_char_p,c.c_int]);send=bind('XSendEvent',c.c_int,[P,U,c.c_int,c.c_long,P])
report=json.load(open(sys.argv[1],encoding='utf8'))
with tempfile.TemporaryDirectory(prefix='confectory-placement-gui-') as local:
    path=os.path.join(local,'gui.log');log=open(path,'w');app=subprocess.Popen(report['run'],stdout=log,stderr=log,start_new_session=True)
    def latest():
        for line in reversed(open(path).read().splitlines()):
            if line.startswith('PLACEMENT_UI '):
                value=json.loads(line[13:]);value['state']=json.loads(value['state']);return value
    def wait(predicate,reason):
        end=time.monotonic()+8
        while time.monotonic()<end:
            s=latest()
            if s and predicate(s):return s
            if app.poll() is not None:raise AssertionError(reason+' '+open(path).read()[-2000:])
            time.sleep(.03)
        raise AssertionError(reason+' '+str(latest()))
    def bounds(s,key):return s['state']['items'][key]['bounds']
    def pointer(win,xp,yp):
        rx,ry,child=c.c_int(),c.c_int(),U();assert native.translate(display,win,native.root,xp,yp,c.byref(rx),c.byref(ry),c.byref(child));native.motion(display,-1,rx.value,ry.value,0);native.flush(display)
    def pixel(win,xp,yp):
        image=get_image(display,win,xp,yp,1,1,U(-1).value,2);assert image
        try:return get_pixel(image,0,0)&0xffffff
        finally:destroy_image(image)
    try:
        wait(lambda s:bounds(s,'free')==[650,400,100,80],'initial independent bounds')
        root,parent,children,count=U(),U(),P(),c.c_uint();native.query(display,native.root,c.byref(root),c.byref(parent),c.byref(children),c.byref(count));window=0
        try:
            for win in c.cast(children,c.POINTER(U))[:count.value]:
                name=P();fetch(display,win,c.byref(name))
                if name:
                    try:
                        if c.string_at(name)==b'Confectory - Placement probe':window=win
                    finally:native.free(name)
        finally:
            if children:native.free(children)
        assert window
        native.raise_window(display,window);native.flush(display)
        pointer(window,512,212);native.button(display,1,1,0);native.flush(display);wait(lambda s:s['drag']=='pane','capture title')
        pointer(window,418,18);s=wait(lambda s:bounds(s,'pane')==[400,0,200,100],'8px contact and top alignment')
        assert s['state']['items']['pane']['contact']['edges']==[1,1,0,0]
        time.sleep(.08);assert pixel(window,402,2)==0x3388ff and pixel(window,402,60)==0x3388ff and pixel(window,500,50)!=0x3388ff,'actual blue contact pixels'
        native.button(display,1,0,0);native.flush(display);wait(lambda s:s['drag']=='','release capture');time.sleep(.08);assert pixel(window,402,2)!=0x3388ff,'release removes actual blue pixels'
        for _ in range(3):
            native.resize(display,window,300,200);native.flush(display);wait(lambda s:bounds(s,'free')==[200,120,100,80],'temporary safety bounds')
            native.resize(display,window,600,400);native.flush(display);wait(lambda s:bounds(s,'free')==[500,320,100,80],'partial recovery')
            native.resize(display,window,800,600);native.flush(display);s=wait(lambda s:bounds(s,'free')==[650,400,100,80] and bounds(s,'pane')==[400,0,200,100],'full free/relative recovery')
        native.resize(display,window,300,200);native.flush(display);wait(lambda s:bounds(s,'free')==[200,120,100,80],'safety before user move')
        pointer(window,212,132);native.button(display,1,1,0);native.flush(display);wait(lambda s:s['drag']=='free','free title capture');pointer(window,132,122);wait(lambda s:bounds(s,'free')==[120,110,100,80],'direct move replaces recovery');native.button(display,1,0,0);native.flush(display);wait(lambda s:s['drag']=='','direct move release')
        native.resize(display,window,800,600);native.flush(display);wait(lambda s:bounds(s,'free')==[120,110,100,80],'old free placement stays canceled')
        data=c.create_string_buffer(192);c.c_int.from_buffer(data).value=33;U.from_buffer(data,32).value=window;U.from_buffer(data,40).value=atom(display,b'WM_PROTOCOLS',0);c.c_int.from_buffer(data,48).value=32;U.from_buffer(data,56).value=atom(display,b'WM_DELETE_WINDOW',0);assert send(display,window,0,0,data);native.flush(display)
        assert app.wait(timeout=5)==0;assert 'Placement GUI cleanup PASS' in open(path).read();print('Placement actual X11 PASS: pointer, exact contact/alignment, blue pixels, repeated/partial recovery, direct move, cleanup')
    finally:
        native.button(display,1,0,0);native.flush(display)
        if app.poll() is None:os.killpg(app.pid,signal.SIGTERM);app.wait(timeout=5)
        log.close()
