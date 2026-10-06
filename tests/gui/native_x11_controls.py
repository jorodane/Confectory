"""Owned-display native widget input helpers; tests seed their own clipboard text."""
import ctypes as c
import time
P=c.c_void_p;U=c.c_ulong
class NativeControls:
    def __init__(self,display):
        self.errors=[]
        self.display=display;self.x=c.CDLL('libX11.so.6');self.xt=c.CDLL('libXtst.so.6')
        def bind(lib,name,result,args):
            f=getattr(lib,name);f.restype=result;f.argtypes=args;return f
        callback=c.CFUNCTYPE(c.c_int,P,P)
        def error(display,event):
            code=c.c_ubyte.from_address(int(event)+32).value;request=c.c_ubyte.from_address(int(event)+33).value
            if (code,request)!=(3,20):self.errors.append((code,request))
            return 0
        self.error_handler=callback(error);bind(self.x,'XSetErrorHandler',P,[P])(c.cast(self.error_handler,P))
        self.move=bind(self.x,'XMoveWindow',c.c_int,[P,U,c.c_int,c.c_int])
        self.resize=bind(self.x,'XResizeWindow',c.c_int,[P,U,c.c_uint,c.c_uint])
        self.attributes=bind(self.x,'XGetWindowAttributes',c.c_int,[P,U,P])
        self.code=bind(self.x,'XKeysymToKeycode',c.c_ubyte,[P,U]);self.lookup=bind(self.x,'XKeycodeToKeysym',U,[P,c.c_ubyte,c.c_int])
        self.focus=bind(self.x,'XSetInputFocus',c.c_int,[P,U,c.c_int,U]);self.flush=bind(self.x,'XFlush',c.c_int,[P])
        self.translate=bind(self.x,'XTranslateCoordinates',c.c_int,[P,U,U,c.c_int,c.c_int,c.POINTER(c.c_int),c.POINTER(c.c_int),c.POINTER(U)])
        self.query=bind(self.x,'XQueryTree',c.c_int,[P,U,c.POINTER(U),c.POINTER(U),c.POINTER(P),c.POINTER(c.c_uint)]);self.free=bind(self.x,'XFree',c.c_int,[P]);self.raise_window=bind(self.x,'XRaiseWindow',c.c_int,[P,U])
        self.root=bind(self.x,'XDefaultRootWindow',U,[P])(display)
        self.key_event=bind(self.xt,'XTestFakeKeyEvent',c.c_int,[P,c.c_uint,c.c_int,U])
        self.motion=bind(self.xt,'XTestFakeMotionEvent',c.c_int,[P,c.c_int,c.c_int,c.c_int,U])
        self.button=bind(self.xt,'XTestFakeButtonEvent',c.c_int,[P,c.c_uint,c.c_int,U])
    def key(self,window,symbol,modifiers=()):
        assert not self.errors,self.errors
        if isinstance(symbol,str):symbol=ord(symbol)
        assert c.sizeof(P)==8,'Native X11 test ABI requires 64-bit process'
        deadline=time.monotonic()+3
        attributes=c.create_string_buffer(136)
        while time.monotonic()<deadline:
            assert self.attributes(self.display,int(window),attributes),'Native input window unavailable'
            if c.c_int.from_buffer(attributes,92).value==2:break
            time.sleep(.02)
        else:raise AssertionError('Native input window not viewable')
        self.focus(self.display,int(window),2,0)
        for modifier in modifiers:self.key_event(self.display,self.code(self.display,modifier),1,0)
        code=self.code(self.display,symbol);assert code,f'No native keycode for {symbol:x}'
        self.key_event(self.display,code,1,0);self.key_event(self.display,code,0,0)
        for modifier in reversed(modifiers):self.key_event(self.display,self.code(self.display,modifier),0,0)
        self.flush(self.display);time.sleep(.025)
    def click(self,window,x,y):
        top=int(window)
        for _ in range(8):
            root,parent,children,count=U(),U(),P(),c.c_uint()
            assert self.query(self.display,top,c.byref(root),c.byref(parent),c.byref(children),c.byref(count))
            if children:self.free(children)
            if parent.value==self.root:break
            top=parent.value
        parent_attributes=c.create_string_buffer(136);root_attributes=c.create_string_buffer(136)
        assert self.attributes(self.display,top,parent_attributes) and self.attributes(self.display,self.root,root_attributes)
        top_x=c.c_int.from_buffer(parent_attributes,0).value;top_y=c.c_int.from_buffer(parent_attributes,4).value;top_w=c.c_int.from_buffer(parent_attributes,8).value;top_h=c.c_int.from_buffer(parent_attributes,12).value
        screen_w=c.c_int.from_buffer(root_attributes,8).value;screen_h=c.c_int.from_buffer(root_attributes,12).value
        if top_x<0 or top_y<0 or top_x+top_w>screen_w or top_y+top_h>screen_h:self.move(self.display,top,0,0)
        self.raise_window(self.display,top);self.flush(self.display);time.sleep(.08)
        rx,ry,child=c.c_int(),c.c_int(),U()
        assert self.translate(self.display,int(window),self.root,x,y,c.byref(rx),c.byref(ry),c.byref(child))
        self.motion(self.display,-1,rx.value,ry.value,0);self.button(self.display,1,1,0);self.button(self.display,1,0,0);self.flush(self.display);time.sleep(.12)
    def drag(self,window,start,end):
        self.click(window,*start)
        rx,ry,child=c.c_int(),c.c_int(),U()
        assert self.translate(self.display,int(window),self.root,*end,c.byref(rx),c.byref(ry),c.byref(child))
        self.button(self.display,1,1,0);self.motion(self.display,-1,rx.value,ry.value,0);self.button(self.display,1,0,0);self.flush(self.display);time.sleep(.15)
    def scroll(self,window,x,y,steps):
        self.click(window,x,y)
        for _ in range(abs(steps)):
            self.button(self.display,5 if steps>0 else 4,1,0);self.button(self.display,5 if steps>0 else 4,0,0)
        self.flush(self.display);time.sleep(.15)
    def text(self,window,text):
        self.key(window,'a',(0xFFE3,)) # toolkit-owned Select All
        for char in text:
            symbol=0xFF0D if char=='\n' else ord(char);code=self.code(self.display,symbol);assert code,f'No native keycode for {char!r}'
            modifiers=(0xFFE1,) if self.lookup(self.display,code,0)!=symbol and self.lookup(self.display,code,1)==symbol else ()
            self.key(window,symbol,modifiers)
        time.sleep(.15)
    def folder(self,find,wait_window,path=None,cancel=False):
        dialog=wait_window(b'Select folder')
        # Isolated dummy Xorg has no window manager to constrain GTK's saved size.
        self.resize(self.display,dialog,800,600);self.flush(self.display);time.sleep(.3)
        if cancel:self.key(dialog,0xFF1B)
        else:
            if path is not None:
                self.click(dialog,300,180)
                self.key(dialog,'l',(0xFFE3,));self.text(dialog,path.rstrip('/')+'/');self.key(dialog,0xFF08);time.sleep(.3)
            if find(b'Select folder'):
                attributes=c.create_string_buffer(136);assert self.attributes(self.display,dialog,attributes);width=c.c_int.from_buffer(attributes,8).value;height=c.c_int.from_buffer(attributes,12).value
                self.click(dialog,width-45,height-25);time.sleep(.25)
        deadline=time.monotonic()+10
        while find(b'Select folder') and time.monotonic()<deadline:time.sleep(.04)
        assert not find(b'Select folder'),'Native chooser did not close'
