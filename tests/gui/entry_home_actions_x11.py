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
sys.path.insert(0,str(Path(repo)/'tests/web'))
from editor_context_actions import prepare_context_actions
storage=tempfile.mkdtemp(prefix='confectory-native-actions-');root_path=Path(storage);home_storage=root_path/'storage';project=root_path/'first';shutil.copytree(Path(repo)/'examples/button-game',project,ignore=shutil.ignore_patterns('.confectory'));manifest=project/'project.cpack';manifest.write_text(manifest.read_text().replace('../../',repo+'/'))
p='Example.ButtonGame::';score=p+'Score';other=p+'Menu';aid=p+'Menu'
(project/'TableStats.celem').write_text('schema '+p+'TableStats {field amount single general long;}')
source=project/'Score.celem';source.write_text(source.read_text().replace('{','{use schema '+p+'TableStats;data amount = 9;',1))
text=manifest.read_text();at=text.rfind('}');manifest.write_text(text[:at]+'element TableStats schema "TableStats.celem";'+text[at:])
prepare_context_actions(project,root_path,Path(repo));projects=[project,root_path/'second-project'];original={f:f.read_bytes() for folder in [*projects,root_path/'schema-editing',root_path/'menu-pack'] for f in folder.rglob('*') if f.is_file() and '.confectory' not in f.parts}
log_path=str(root_path/'native.log');env=os.environ.copy();env.pop('CONFECTORY_UI',None);env.pop('CONFECTORY_WEB_PROJECT',None);env.update(CONFECTORY_EDITOR_REPO=repo,CONFECTORY_HOME_STORAGE=str(home_storage),CONFECTORY_ENTRY_STORAGE=str(home_storage),CONFECTORY_HOME_TRACE='1',CONFECTORY_ELEMENT_AUTHORING_HOST=str(Path(repo)/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll'),XDG_DATA_HOME=str(root_path/'data'),XDG_CACHE_HOME=str(root_path/'cache'),CONFECTORY_NATIVE_ACTION_FIXTURE=storage)
hold=root_path/'hold';entered=root_path/'entered';late=root_path/'late';done=root_path/'late-done';replay=root_path/'replay';mutate=root_path/'mutate';calls=root_path/'calls'
app=None;log=None;launch_count=0

def launch():
    global app,log,launch_count
    if launch_count and os.path.isfile(log_path):shutil.copy2(log_path,os.path.join(storage,f"native-launch-{launch_count}.log"))
    launch_count+=1
    log=open(log_path,'w',encoding='utf-8');app=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    return await_window(b'Confectory - Projects')

def latest():
    with open(log_path,'rb') as stream:
        stream.seek(0,2);stream.seek(max(0,stream.tell()-8388608));lines=stream.read().splitlines()
    for line in reversed(lines):
        if line.startswith(b'HOME_UI '):
            try:return json.loads(line[8:])
            except (json.JSONDecodeError,UnicodeDecodeError):pass
    return None

def wait(predicate,message,seconds=30):
    end=time.monotonic()+seconds
    while time.monotonic()<end:
        state=latest()
        if state and predicate(state):return state
        if app.poll() is not None:raise AssertionError('Entry/home exited: '+open(log_path).read()[-3000:])
        time.sleep(.04)
    raise AssertionError(message+' '+str({k:(latest() or {}).get(k) for k in ['screen','operation','job','focus','nativeAction','message']}))

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
    if not text:native_controls.key(int(field['nativeHandle']),0xFF08)

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

def tree():return wait(lambda t:t.get('nativeTree') is not None and not t['job'],'native tree ready')
def search_tree(window,text):
 fill(window,77,text);click(window,78);wait(lambda t:t.get('nativeTreeState',{}).get('query')==text and not t['job'],'tree query applied')
def choose(window,key):
 for attempt in range(80):
  state=tree();rows=state['nativeTree']['rows'];index=next((n for n,r in enumerate(rows) if r['key']==key),None);assert index is not None,(key,[r['key'] for r in rows]);offset=min(state['nativeTreeState']['offset'],max(0,len(rows)-1));count=len([id for id in state['hits'][::5] if 210<=id<226]);assert count>0,state['height']
  if offset<=index<offset+count:click(window,210+index-offset);return wait(lambda t:t.get('nativeTreeState',{}).get('selection')==key,'tree selection')
  click(window,80 if index<offset else 81);wait(lambda t:t.get('nativeTreeState',{}).get('offset')!=state['nativeTreeState']['offset'],'tree page moved')
 raise AssertionError('tree item paging failed '+key)
def explore(window):
 if latest()['model'].get('workspace') is None:click(window,55);wait(lambda t:t['model'].get('workspace') is not None and not t['job'],'reopened source workspace')
 click(window,73);return tree()
def select_id(window,id):search_tree(window,id);return choose(window,'decl:'+id)

def text(id):return json.loads(latest()['fields'][str(id)])['text']
def native_fill(window,id,value):
 click(window,id);info=field(id);assert not info['readonly'];native_controls.text(int(info['nativeHandle']),value)
 if not value:native_controls.key(int(info['nativeHandle']),0xFF08)
 wait(lambda t:json.loads(t['fields'][str(id)])['text']==value,'native typed '+str(id))
def bases():return {n:latest()[n] for n in ['sourceInputVersions','propertyInputVersions']}
def count():return len(calls.read_text().splitlines()) if calls.exists() else 0
def current():return latest()['nativeAction']
def menu(window):
 click(window,324);return wait(lambda t:t['screen']=='actions' and not t['job'] and (t.get('nativeAction') or {}).get('token'),'native Actions listing')
def choose_action(window,action=aid):
 state=idle('actions');rows=state['nativeAction']['actions'];index=next(n for n,r in enumerate(rows) if r['id']==action)
 while 500+index not in latest()['hits'][::5]:click(window,444);index-=4
 click(window,500+index);wait(lambda t:t['nativeAction']['chosen']==action,'native declared action chosen')
def prepare(window,value='23',refresh=False):
 if latest()['screen']!='actions':menu(window)
 elif refresh:click(window,435);wait(lambda t:not t['job'] and (t.get('nativeAction') or {}).get('token'),'refreshed Actions listing')
 choose_action(window);native_fill(window,431,'initial');native_fill(window,432,value)
def invoke(window,status='completed'):
 click(window,434);return wait(lambda t:not t['job'] and (t.get('nativeAction') or {}).get('status')==status,'function '+status)
def back(window):click(window,430);idle('project')
def select_source(window,id):
 explore(window);select_id(window,id);click(window,83);wait(lambda t:'54' in t['fields'] and t['model']['workspace']['selected']==id and not t['job'],'source selected '+id)
def replay_old(window,token,project_id):
 replay.write_text(json.dumps(dict(operation='invoke',projectId=project_id,token=token,actionId=aid,field='initial',value='23')));n=count();click(window,434);wait(lambda t:not t['job'] and t['nativeAction']['status'].startswith('Failed:'),'old token rejected');assert count()==n and not replay.exists()
def invariant():
 assert all(f.read_bytes()==raw for f,raw in original.items()),'source bytes changed'
 state=latest()['model'];assert len(state['cards'])==2 and not state.get('ai') and not state.get('aiBindings') and not state.get('aiRuns') and not state.get('aiPreview')
def pending():
 assert field(54)['text']==source_pending and field(54)['binding']==source_binding
 assert field(38)['text']=='NATIVE ACTION CHAT UNSENT' and field(38)['binding']==chat_binding
 assert json.loads(latest()['fields']['400'])['text']=='5' and json.loads(latest()['fields']['400'])['binding']==cell_binding
 assert bases()==original_bases;invariant()
def begin_hold(window,noncooperative=False):
 if entered.exists():entered.unlink()
 if noncooperative:late.write_text('owned')
 hold.write_text('owned');click(window,434);wait(lambda t:entered.exists() and t['job'] and 436 in t['hits'][::5],'owned function barrier',25)
try:
 a=launch();wait(lambda t:t['screen']=='intro' and 1 in t['hits'][::5],'intro');resize(display,a,1600,1150);flush(display);wait(lambda t:t['width']==1600,'resize');click(a,1);idle('home');click(a,100);idle('project');first=latest()['model']['selected']['context'];project_id=latest()['model']['selected']['projectId'];click(a,55);wait(lambda t:(t['model'].get('workspace') or {}).get('unit') and not t['job'],'source workspace');select_source(a,score)
 click(a,74);wait(lambda t:'89' in t['fields'] and not t['job'],'properties')
 for attempt in range(20):
  if json.loads(field(88)['text'])==['amount']:break
  click(a,99);idle('project')
 assert json.loads(field(88)['text'])==['amount'];native_fill(a,89,'5');click(a,318);wait(lambda t:'400' in t['fields'] and not t['job'],'retained property');cell_binding=field(400)['binding'];click(a,75);wait(lambda t:'54' in t['fields'],'source');source_pending=field(54)['text']+'\n// NATIVE_ACTION_PENDING';native_fill(a,54,source_pending);source_binding=field(54)['binding'];native_fill(a,38,'NATIVE ACTION CHAT UNSENT');chat_binding=field(38)['binding'];original_bases=bases();draft=latest()['model']['workspace']['unit']['text'];pending()
 # Real native declaration controls include direct pack menus and unavailable items.
 menu(a);assert {r['id'] for r in current()['actions']}=={aid,p+'UnboundMenu','Example.ActionPack::Menu'};assert not next(r for r in current()['actions'] if r['id']==p+'UnboundMenu')['available'];choose_action(a,p+'UnboundMenu');assert 434 not in latest()['hits'][::5];assert count()==0
 prepare(a);old=current()['token'];n=count();invoke(a);assert count()==n+1 and 'value initial = 23;' in text(433) and 'data amount = 9;' in text(433);assert latest()['model']['workspace']['unit']['text']==draft
 result=field(433);assert result['readonly'];native_controls.text(int(result['nativeHandle']),'MUST_NOT_EDIT_RESULT');wait(lambda t:json.loads(t['fields']['433'])['text']==result['text'],'read-only proposal');invoke(a);assert count()==n+1,'duplicate dispatched function again';screenshot(a,'proposal');native_fill(a,432,'24');click(a,434);wait(lambda t:not t['job'] and t['nativeAction']['status'].startswith('Failed:'),'different input token reuse refused');assert count()==n+1 and text(432)=='24';back(a);pending();prepare(a);choose_action(a,'Example.ActionPack::Menu');invoke(a);assert 'value initial = 23;' in text(433);back(a);pending()
 # Input cancel and menu Escape retire tokens, preserve separate source/property CAS.
 prepare(a);canceled=current()['token'];click(a,436);idle('actions');assert text(431)==text(432)==text(433)=='' and not current()['token'];prepare(a,refresh=True);replay_old(a,canceled,project_id);press(a,0xFF1B);idle('project');pending();prepare(a);native_fill(a,432,'null');invoke(a,'failed');assert 'Scalar metadata required' in text(433) and text(432)=='null';back(a);pending()
 # Selection A -> B -> A cannot revive capabilities; raw object inputs survive.
 prepare(a);selection_token=current()['token'];back(a);select_source(a,other);select_source(a,score);prepare(a);replay_old(a,selection_token,project_id);back(a);pending()
 # Same selected object but competing draft revision rejects invocation and preserves old CAS.
 prepare(a);mutate.write_text('owned');n=count();invoke(a,'failed');assert count()==n and not mutate.exists();assert 'CURRENT_NATIVE_ACTION_DRAFT' in latest()['model']['workspace']['unit']['text'];back(a);pending();prepare(a,refresh=False);invoke(a);assert 'value initial = 23;' in text(433);back(a);pending()
 # Fresh discovery rejects changed canonical body/signature, old prepared menu never executes.
 for relative in ['SetValue.csbody','SetValue.celem']:
  prepare(a);target=root_path/'schema-editing'/relative;raw=target.read_bytes();target.write_bytes(raw+b'\n// STALE_NATIVE_ACTION_CONTRACT');n=count();invoke(a,'failed');assert count()==n;click(a,435);wait(lambda t:not t['job'] and t['nativeAction'].get('token'),'changed contract discovery');assert not next(r for r in current()['actions'] if r['id']==aid)['available'];target.write_bytes(raw);back(a);pending()
 # Cooperative cancel and noncooperative late success are both suppressed; no implicit application.
 prepare(a);n=count();begin_hold(a);click(a,436);wait(lambda t:not t['job'] and not (t.get('nativeAction') or {}).get('token'),'cooperative cancel');assert hold.exists() and count()==n;hold.unlink();assert text(433)=='';prepare(a,refresh=True);n=count();begin_hold(a,True);click(a,430);wait(lambda t:t['job'] and 'Canceling' in (t.get('nativeAction') or {}).get('status',''),'late back requested');hold.unlink();idle('project');assert done.exists() and count()==n+1;pending();prepare(a);assert text(433)=='';back(a)
 # Project A -> B -> A retires token; return retains each native input/write basis.
 prepare(a);project_token=current()['token'];back(a);leave_project(a);idle('home');click(a,103);idle('project');click(a,55);wait(lambda t:(t['model'].get('workspace') or {}).get('unit') and not t['job'],'second workspace');select_source(a,score);prepare(a);replay_old(a,project_token,project_id);back(a);leave_project(a);idle('home');click(a,100);idle('project');
 if latest()['model'].get('workspace') is None:click(a,55);wait(lambda t:(t['model'].get('workspace') or {}).get('unit') and not t['job'],'first reopened workspace')
 select_source(a,score);pending();prepare(a);replay_old(a,project_token,project_id);back(a);pending()
 # A real stale retained-cell write still conflicts after function reads; original typed input remains.
 click(a,319);wait(lambda t:400 in t['hits'][::5] and not t['job'],'retained cell foreground');click(a,401);wait(lambda t:not t['job'] and (t['model']['status'].startswith('Error:') or (t['model'].get('workspaceViews',{}).get(first,{}).get('1',{}).get('workspace') or {}).get('conflict')),'old CAS refused');pending()
 # WM close while a function is held cancels first and waits for owned completion.
 prepare(a);begin_hold(a);end(a);assert hold.exists();hold.unlink();invariant()
 evidence=Path('/workspace/scratch/confectory-native-actions-ui');evidence.mkdir(exist_ok=True);shutil.copy2(root_path/'proposal.png',evidence/'proposal.png');(evidence/'summary.json').write_text(json.dumps(dict(privateEvidence=storage,actualFunctionCalls=count(),sourceBytesPreserved=True,oldInputCasPreserved=True,cooperativeCancel=True,lateSuccessSuppressed=True,selectionReturnRejected=True,projectReturnRejected=True,staleBodyAndSignatureRejected=True,duplicateCallCached=True),indent=2)+'\n')
 print('PASS native declared context actions actual GTK input: shared discovery and typed SetValue proposal/failure, no source or draft application, input and menu cancel, duplicate cached, selection A/B/A and project A/B/A token retirement, competing revision and preserved native source/chat/property binding plus original CAS, stale body/signature and unavailable routes, cooperative cancel/late-success suppression/WM owner disposal; evidence '+storage,flush=True)
finally:
 if app is not None and app.poll() is None:
  for path in [hold]:
   if path.exists():path.unlink()
  os.killpg(app.pid,signal.SIGINT)
  try:app.wait(timeout=20)
  except subprocess.TimeoutExpired:os.killpg(app.pid,signal.SIGKILL);app.wait(timeout=10)
 if log is not None and not log.closed:log.close()
