#!/usr/bin/env python3
"""Actual native text/folder service acceptance on an isolated owned X11 display."""
import ctypes as c,json,os,signal,subprocess,sys,tempfile,time
from pathlib import Path
from native_x11_controls import NativeControls
P=c.c_void_p;U=c.c_ulong;x=c.CDLL('libX11.so.6')
def api(name,result,args):
 f=getattr(x,name);f.restype=result;f.argtypes=args;return f
open_display=api('XOpenDisplay',P,[c.c_char_p]);d=open_display(None);assert d,'Live isolated DISPLAY required';ui=NativeControls(d)
query=api('XQueryTree',c.c_int,[P,U,c.POINTER(U),c.POINTER(U),c.POINTER(P),c.POINTER(c.c_uint)]);fetch=api('XFetchName',c.c_int,[P,U,c.POINTER(P)]);free=api('XFree',c.c_int,[P])
resize=api('XResizeWindow',c.c_int,[P,U,c.c_uint,c.c_uint])
shape=c.CDLL('libXext.so.6');shape.XShapeGetRectangles.restype=P;shape.XShapeGetRectangles.argtypes=[P,U,c.c_int,c.POINTER(c.c_int),c.POINTER(c.c_int)]
class Rectangle(c.Structure):
 _fields_=[('x',c.c_short),('y',c.c_short),('width',c.c_ushort),('height',c.c_ushort)]
observed_shapes=set()
def shape_width(window,kind=0):
 count,ordering=c.c_int(),c.c_int();rectangles=shape.XShapeGetRectangles(d,int(window),kind,c.byref(count),c.byref(ordering));assert rectangles and count.value
 try:
  width=max(r.x+r.width for r in c.cast(rectangles,c.POINTER(Rectangle))[:count.value])
  if width not in observed_shapes:observed_shapes.add(width);print("Observed native visual clip width:",width,flush=True)
  return width
 finally:free(rectangles)

def find(title):
 root,parent,children,count=U(),U(),P(),c.c_uint();query(d,ui.root,c.byref(root),c.byref(parent),c.byref(children),c.byref(count))
 try:
  for w in c.cast(children,c.POINTER(U))[:count.value]:
   name=P();fetch(d,w,c.byref(name))
   if name:
    try:
     if c.string_at(name)==title:return w
    finally:free(name)
 finally:
  if children:free(children)
store=Path(tempfile.mkdtemp(prefix='confectory-native-service-'));log_path=store/'native.log';env=os.environ.copy();env['CONFECTORY_NATIVE_FOLDER']=str(store)
report=json.load(open(sys.argv[1]));log=open(log_path,'w');app=subprocess.Popen(report['run'],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
def rows():
 out={}
 for line in log_path.read_text().splitlines():
  if line.startswith('NATIVE_UI '):r=json.loads(line[10:]);out[r['view']]=r
 return out
def wait(predicate,label,seconds=15):
 end=time.monotonic()+seconds
 while time.monotonic()<end:
  result=rows()
  if predicate(result):return result
  if app.poll() is not None:raise AssertionError(log_path.read_text()[-3000:])
  time.sleep(.025)
 raise AssertionError(label+' '+str(rows()))
def window(title):
 end=time.monotonic()+15
 while time.monotonic()<end:
  w=find(title)
  if w:return w
  time.sleep(.02)
 raise AssertionError('Native window unavailable: '+repr(title))
def field(view,id):return next(f for f in rows()[view]['native']['fields'] if f['id']==id and f['visible'])
def focus(view,id):
 f=field(view,id);ui.click(f['nativeHandle'],50,80 if id==2 else 22);wait(lambda r:r[view]['native']['focus']==id,'native pointer focus');return int(f['nativeHandle'])
def value(view,index,expected):return wait(lambda r:r[view]['values'][index]==expected,'native model '+repr(expected))
try:
 r=wait(lambda r:len(r)==2,'two independent views');a=int(r[0]['surface']);b=int(r[1]['surface']);identity=field(0,1)['nativeHandle'];token=field(0,1)['binding']
 h=focus(0,1);ui.text(h,'alpha beta gamma');value(0,0,'alpha beta gamma');ui.key(h,0xFF57);ui.key(h,0xFF51,(0xFFE3,));ui.key(h,0xFF50,(0xFFE1,));ui.key(h,'x');value(0,0,'xgamma')
 # Clipboard is seeded exclusively by these synthetic values on this test display.
 ui.text(h,'Synthetic clipboard');value(0,0,'Synthetic clipboard');ui.key(h,'a',(0xFFE3,));ui.key(h,'c',(0xFFE3,));h2=focus(1,1);ui.key(h2,'a',(0xFFE3,));ui.key(h2,'v',(0xFFE3,));value(1,0,'Synthetic clipboard');ui.key(h2,'a',(0xFFE3,));ui.key(h2,'x',(0xFFE3,));value(1,0,'');ui.key(h2,'v',(0xFFE3,));value(1,0,'Synthetic clipboard');assert rows()[0]['values'][0]=='Synthetic clipboard'
 h=focus(0,2);ui.text(h,'first line\nsecond line');value(0,1,'first line\nsecond line');ui.key(h,'z',(0xFFE3,));wait(lambda r:r[0]['values'][1]!='first line\nsecond line','toolkit source undo');ui.key(h,'z',(0xFFE3,0xFFE1));value(0,1,'first line\nsecond line')
 h=focus(0,3);ui.key(h,'q');value(0,2,'Synthetic readonly');ui.click(field(0,4)['nativeHandle'],8,8);ui.key(a,0xFFBE);h=focus(0,1);ui.key(h,'q');assert rows()[0]['values'][3]=='Synthetic disabled'
 ui.key(h,0xFFC5);r=value(0,0,'External model value');assert field(0,1)['nativeHandle']==identity and field(0,1)['binding']==token;wait(lambda r:field(0,1)['caret']==8 and field(0,1)['anchor']==3,'external model selection')
 ui.key(h,0xFFC1);wait(lambda r:shape_width(identity)==230 and shape_width(identity,2)==230,'native visual/input clip');assert field(0,1)['nativeHandle']==identity and rows()[0]['values'][0]=='External model value';ui.click(a,370,70);wait(lambda r:not field(0,1)['focus'],'clipped region cannot take native focus');ui.click(int(identity),60,20);wait(lambda r:field(0,1)['focus'],'visible native region takes focus');ui.key(h,0xFFC1);wait(lambda r:shape_width(identity)==460 and shape_width(identity,2)==460,'native clip restoration');assert field(0,1)['binding']==token
 ui.key(h,0xFFC0);wait(lambda r:all(not f['visible'] for f in r[0]['native']['fields']),'hidden fields');ui.key(a,0xFFC0);wait(lambda r:any(f['id']==1 and f['visible'] and f['nativeHandle']==identity for f in r[0]['native']['fields']),'same native identity after show')
 resize(d,a,700,600);ui.flush(d);time.sleep(.2);assert field(0,1)['nativeHandle']==identity
 h=focus(0,1);ui.key(h,0xFF09);wait(lambda r:r[0]['native']['focus']==2,'native Tab app navigation')
 ui.key(a,0xFFC3);ui.folder(find,window,cancel=True);wait(lambda r:'"state":"cancelled"' in log_path.read_text(),'native folder cancellation')
 ui.key(a,0xFFC3);ui.folder(find,window,str(store));wait(lambda r:'"state":"selected"' in log_path.read_text(),'native folder select');assert any(json.loads(line[14:]).get('path')==str(store) for line in log_path.read_text().splitlines() if line.startswith('NATIVE_FOLDER ')),'Native chooser selected a child rather than the typed parent'
 old_host=rows()[1]['host'];ui.key(a,0xFFC4);wait(lambda r:r[1]['host']!=old_host,'native host reopen');assert rows()[1]['values'][0]=='Synthetic clipboard';assert field(1,1)['nativeHandle']!=h2
 ui.key(a,0xFFC3);window(b'Select folder');os.killpg(app.pid,signal.SIGINT);assert app.wait(timeout=15)==0,log_path.read_text()[-2000:];assert not find(b'Select folder') and not find(b'Native input A') and not find(b'Native input B')
 print('Native GTK selection/word/clipboard/cut/paste/source undo-redo/View isolation/readonly-disabled/external selection/retained identity/hide-show/resize/Tab/native folder select-cancel/close-reopen/owner dialog cleanup PASS');print('Private evidence:',store)
finally:
 if app.poll() is None:
  os.killpg(app.pid,signal.SIGINT)
  try:app.wait(timeout=15)
  except subprocess.TimeoutExpired:os.killpg(app.pid,signal.SIGKILL);app.wait()
 log.close()
