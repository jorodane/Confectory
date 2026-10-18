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
storage=tempfile.mkdtemp(prefix='confectory-native-tree-');root_path=Path(storage);home_storage=root_path/'storage';home_storage.mkdir();projects=[root_path/'first',root_path/'second-project'];shutil.copytree(Path(repo)/'examples/button-game',projects[0],ignore=shutil.ignore_patterns('.confectory'));manifest=projects[0]/'project.cpack';manifest.write_text(manifest.read_text().replace('../../',repo+'/'))
sys.path.insert(0,str(Path(repo)/'tests/web'));from v480_declaration_tree import prepare_tree
prepare_tree(projects[0],root_path,Path(repo));catalog=home_storage/'projects.json';cards=json.loads(catalog.read_text());original={p:p.read_bytes() for folder in [*projects,root_path/'tree-api'] for p in folder.rglob('*') if p.is_file() and '.confectory' not in p.parts}
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
def toggle_tree(window):
 before=tree()['nativeTreeState'];key=before['selection'];was=key in before['expanded'];click(window,79);return wait(lambda t:t.get('nativeTreeState') and ((key in t['nativeTreeState']['expanded'])!=was),'tree expansion changed')
def choose(window,key):
 for attempt in range(80):
  state=tree();rows=state['nativeTree']['rows'];index=next((n for n,r in enumerate(rows) if r['key']==key),None);assert index is not None,(key,[r['key'] for r in rows]);offset=min(state['nativeTreeState']['offset'],max(0,len(rows)-1));count=len([id for id in state['hits'][::5] if 210<=id<226]);assert count>0,state['height']
  if offset<=index<offset+count:click(window,210+index-offset);return wait(lambda t:t.get('nativeTreeState',{}).get('selection')==key,'tree selection')
  click(window,80 if index<offset else 81);wait(lambda t:t.get('nativeTreeState',{}).get('offset')!=state['nativeTreeState']['offset'],'tree page moved')
 raise AssertionError('tree item paging failed '+key)
def check_invariant(context=None):
 state=latest();model=state['model'];assert all(p.read_bytes()==raw for p,raw in original.items()),'tree wrote source';assert len(model['cards'])==2 and len(list(root_path.rglob('project.cpack')))==2;assert not model.get('ai') and not model.get('aiPreview') and not model.get('aiRuns') and not model.get('aiBindings');assert not (root_path/'tree-api/never-read.celem').exists()
 if context is not None:assert model['selected']['context']==context
 return state
def explore(window):
 if latest()['model'].get('workspace') is None:click(window,55);wait(lambda t:t['model'].get('workspace') is not None and not t['job'],'reopened source workspace')
 click(window,73);return tree()
def select_id(window,id):search_tree(window,id);return choose(window,'decl:'+id)
p='Example.ButtonGame::';leaf=p+'TreeLeaf';middle=p+'TreeMiddle';parent=p+'TreeRoot';score=p+'Score';foreign='TreeRegistered.Api::Parent'
try:
 a=launch();wait(lambda t:t['screen']=='intro' and 1 in t['hits'][::5],'intro');resize(display,a,1600,1150);flush(display);wait(lambda t:t["width"]==1600 and t["height"]==1150,"native resize observed");click(a,1);idle('home');click(a,100);idle('project');first=latest()['model']['selected']['context'];click(a,55);wait(lambda t:(t['model'].get('workspace') or {}).get('unit') and not t['job'],'source workspace');explore(a)
 select_id(a,leaf);assert tree()['nativeTree']['selected']['depth']==5;details=field(208);assert details['readonly'] and details['provider']=='gtk3' and 'contain' in details['text'] and 'schema' in details['text'];assert latest()['model']['workspace']['selected']!=leaf
 # Expansion is stored separately from temporary search-forced paths.
 for key in ['ns:Example','ns:Example.ButtonGame','decl:'+parent,'decl:'+middle]:choose(a,key);toggle_tree(a)
 search_tree(a,'');choose(a,'decl:'+middle);toggle_tree(a);assert not any(r['key']=='decl:'+leaf for r in tree()['nativeTree']['rows']);toggle_tree(a);assert any(r['key']=='decl:'+leaf for r in tree()['nativeTree']['rows'])
 for id,status in [(p+'ZZDangling','unresolved'),(p+'ZZDanglingChild','ancestor-unresolved'),(p+'ZZCycleA','cycle'),(p+'ZZCycleChild','ancestor-cycle'),(p+'Depth65','depth-limit')]:
  select_id(a,id);assert tree()['nativeTree']['selected']['row']['status']==status;assert status in field(208)['text']
 assert 'decl:Missing::Parent' not in [r['key'] for r in tree()['nativeTree']['rows']]
 select_id(a,foreign);assert tree()['nativeTree']['selected']['row']['status']=='unobserved';click(a,83);wait(lambda t:(t['model'].get('referenceDefinition') or {}).get('result',{}).get('status')=='available' and not t['job'],'gated registered read');assert 'Registered exact parent gate' in field(208)['text'];select_id(a,'TreeRegistered.Api::Unused');assert 83 not in latest()['hits'][::5],'unreferenced definition open enabled'
 # Open owned definition explicitly. Browsing must not Apply the pending source or chat.
 select_id(a,score);click(a,83);wait(lambda t:'54' in t['fields'] and t['model']['workspace']['selected']==score and not t['job'],'owned definition');source_before=field(54);pending=source_before['text']+'\n// NATIVE_TREE_PENDING';fill(a,54,pending);fill(a,38,'native tree pending chat');source_binding=field(54)['binding'];chat_binding=field(38)['binding'];draft_before=latest()['model']['workspace']['unit']['text'];explore(a);select_id(a,leaf);assert latest()['model']['workspace']['unit']['text']==draft_before;click(a,83);wait(lambda t:t['model']['workspace']['selected']==leaf and not t['job'],'other owned definition');explore(a);select_id(a,score);click(a,83);wait(lambda t:t['model']['workspace']['selected']==score and not t['job'],'original owned definition');assert field(54)['text']==pending and field(54)['binding']==source_binding and latest()['model']['workspace']['unit']['text']==draft_before;explore(a);select_id(a,leaf);click(a,226);wait(lambda t:t['model']['status'].startswith('Native tree view explicitly saved') and not t['job'],'tree saved');files=list((home_storage/'native-trees').glob('*.json'));assert len(files)==1;saved_path=files[0];saved=saved_path.read_bytes();value=json.loads(saved);assert value['selection']=='decl:'+leaf and value['query']==leaf and set(value)=={'version','projectId','selection','expanded','query','queryInput','group','offset'}
 # Unsaved view state survives hide/reopen; explicit Reload restores only saved state.
 select_id(a,parent);click(a,75);assert field(54)['text']==pending and field(54)['binding']==source_binding;assert field(38)['binding']==chat_binding and field(38)['text']=='native tree pending chat';explore(a);assert tree()['nativeTreeState']['selection']=='decl:'+parent;click(a,227);assert tree()['nativeTreeState']['selection']=='decl:'+leaf or wait(lambda t:t.get('nativeTreeState',{}).get('selection')=='decl:'+leaf,'saved state reloaded')
 saved_path.write_bytes(saved+b'\n');select_id(a,parent);click(a,87);tree();click(a,226);wait(lambda t:t['model']['status'].startswith('Error:') and not t['job'],'tree CAS refused');assert tree()['nativeTreeState']['selection']=='decl:'+parent and saved_path.read_bytes()==saved+b'\n';saved_path.write_bytes(saved);click(a,227);wait(lambda t:t.get('nativeTreeState',{}).get('selection')=='decl:'+leaf and not t['job'],'reload after CAS')
 saved_path.write_text('{broken');click(a,87);wait(lambda t:not t['job'] and t['model']['nativeTrees'][t['model']['selected']['projectId']]['storage']['status']=='unavailable','corrupt state unavailable');assert 226 not in latest()['hits'][::5] and saved_path.read_text()=='{broken';retained=tree()['nativeTreeState'].copy();click(a,227);wait(lambda t:not t['job'] and 'Saved tree unavailable' in t.get('message',''),'corrupt reload retained view');assert tree()['nativeTreeState']==retained and saved_path.read_text()=='{broken';saved_path.write_bytes(saved);click(a,87);tree()
 check_invariant(first);leave_project(a);idle('home');click(a,103);idle('project');second=latest()['model']['selected']['context'];assert second!=first;click(a,55);wait(lambda t:(t['model'].get('workspace') or {}).get('unit') and not t['job'],'second workspace');explore(a);assert tree()['nativeTreeState']['query']=='';select_id(a,leaf);assert tree()['nativeTree']['selected']['depth']==4;leave_project(a);idle('home');click(a,100);idle('project');explore(a);assert tree()['nativeTreeState']['selection']=='decl:'+leaf and tree()['nativeTree']['selected']['depth']==5;click(a,75);assert field(54)['text']==pending and field(54)['binding']==source_binding;assert field(38)['text']=='native tree pending chat' and field(38)['binding']==chat_binding;explore(a);check_invariant(first)
 screenshot(a,'native-tree-before-restart');end(a)
 # Cold state is explicit view state only; refresh metadata from external fixture edits.
 changed=projects[0]/'TreeLeaf.celem';changed.write_text(changed.read_text().replace(p+'TreeMiddle',parent));original[changed]=changed.read_bytes();registered=root_path/'tree-api/Parent.celem';registered.write_text('object TreeRegistered.Api::Parent {description "Fresh native registered definition";}');original[registered]=registered.read_bytes()
 a=launch();wait(lambda t:t['screen']=='intro' and 1 in t['hits'][::5],'cold intro');resize(display,a,1600,1150);flush(display);wait(lambda t:t["width"]==1600 and t["height"]==1150,"native resize observed");click(a,1);idle('home');click(a,100);idle('project');click(a,55);wait(lambda t:(t['model'].get('workspace') or {}).get('unit') and not t['job'],'cold workspace');explore(a);state=tree();assert state['nativeTreeState']['selection']=='decl:'+leaf and state['nativeTreeState']['query']==leaf;assert state['nativeTree']['selected']['depth']==4 and state['nativeTree']['selected']['row']['declaredParent']==parent;assert field(77)['text']==leaf;select_id(a,foreign);click(a,83);wait(lambda t:not t['job'] and 'Fresh native' in t['model'].get('referenceDefinition',{}).get('result',{}).get('text',''),'fresh registered read');assert 'Fresh native registered definition' in field(208)['text'];check_invariant();screenshot(a,'native-tree-cold');end(a)
 print('PASS native declaration tree input: GTK expand/search/select/page, explicit parent/contain/schema and direct-reference gate, unresolved/cycle/depth64, explicit saved state/CAS/corruption, two-project isolation, same pending source/chat bindings, reopen and cold latest metadata; unchanged widget budgets',flush=True)
 print('Native tree evidence: '+storage,flush=True)
finally:
 if app is not None and app.poll() is None:os.killpg(app.pid,signal.SIGTERM);app.wait(timeout=15)
 if log is not None and not log.closed:log.close()
