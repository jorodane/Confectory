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
storage=tempfile.mkdtemp(prefix='confectory-native-fields-');root_path=Path(storage);home_storage=root_path/'storage';home_storage.mkdir();projects=[root_path/'first',root_path/'second-project'];shutil.copytree(Path(repo)/'examples/button-game',projects[0],ignore=shutil.ignore_patterns('.confectory'));manifest=projects[0]/'project.cpack';manifest.write_text(manifest.read_text().replace('../../',repo+'/'))
p='Example.ButtonGame::';fixtures={'TableStats':('schema','schema '+p+'TableStats {field amount single general long;field zero single general long;field unsetText single general string;}'),'UnionOtherSchema':('schema','schema '+p+'UnionOtherSchema {field amount single general string;}'),'UnionOther':('object','object '+p+'UnionOther {use schema '+p+'UnionOtherSchema;data amount = "variant";value nullish = 0;}'),'UnionBare':('object','object '+p+'UnionBare {}'),'UnionBroken':('object','object '+p+'UnionBroken {}'),'UnionMany':('object','object '+p+'UnionMany {'+''.join('value field'+str(n).zfill(3)+' = '+str(n)+';' for n in range(80))+'}')}
for n in range(18):fixtures['UnionRow'+str(n).zfill(2)]=('object','object '+p+'UnionRow'+str(n).zfill(2)+' {value index = '+str(n)+';}')
for n in range(45):fixtures['ZPage'+str(n).zfill(2)]=('object','object '+p+'ZPage'+str(n).zfill(2)+' {}')
for name,(_,text) in fixtures.items():(projects[0]/(name+'.celem')).write_text(text)
score_file=projects[0]/'Score.celem';score_file.write_text(score_file.read_text().replace('{','{use schema '+p+'TableStats;data amount = 9223372036854775807;data zero = 0;value nullish = 1;value falsey = false;value empty = "";',1))
text=manifest.read_text();at=text.rfind('}');manifest.write_text(text[:at]+''.join('element '+name+' '+kind+' "'+name+'.celem";' for name,(kind,_) in fixtures.items())+text[at:]);(projects[0]/'UnionBroken.celem').write_text('broken owned declaration')
external=root_path/'external';external.mkdir();(external/'pack.cpack').write_text('pack NativeFieldExternal version "1" {element Foreign object "Foreign.celem";}');(external/'Foreign.celem').write_text('object NativeFieldExternal::Foreign {value hidden = 99;}');text=manifest.read_text();at=text.rfind('}');manifest.write_text(text[:at]+'registry NativeFieldExternal '+json.dumps(str(external/'pack.cpack'))+';dependency NativeFieldExternal version "1";'+text[at:])
shutil.copytree(projects[0],projects[1],ignore=shutil.ignore_patterns('.confectory'));second_score=projects[1]/'Score.celem';second_score.write_text(second_score.read_text().replace('9223372036854775807','41'))
catalog=home_storage/'projects.json';cards=[{'path':str(folder/'project.cpack'),'title':title,'description':'Owned native field comparison fixture'} for folder,title in zip(projects,['Native union A','Native union B'])];catalog.write_text(json.dumps(cards));original={p:p.read_bytes() for folder in [*projects,external] for p in folder.rglob('*') if p.is_file() and '.confectory' not in p.parts}
hold=root_path/'hold';entered=root_path/'entered';probe=root_path/'described';late=root_path/'late';late_done=root_path/'late-done';mutate=root_path/'mutate'
log_path=os.path.join(storage,'native.log');env=os.environ.copy();env.pop('CONFECTORY_UI',None);env.pop('CONFECTORY_WEB_PROJECT',None);env.update(CONFECTORY_EDITOR_REPO=repo,CONFECTORY_HOME_STORAGE=str(home_storage),CONFECTORY_ENTRY_STORAGE=str(home_storage),CONFECTORY_HOME_TRACE='1',CONFECTORY_ELEMENT_AUTHORING_HOST=os.path.join(repo,'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll'),XDG_DATA_HOME=str(root_path/'data'),XDG_CACHE_HOME=str(root_path/'cache'),CONFECTORY_NATIVE_FIELD_HOLD=str(hold),CONFECTORY_NATIVE_FIELD_ENTERED=str(entered),CONFECTORY_NATIVE_FIELD_PROBE=str(probe),CONFECTORY_NATIVE_FIELD_LATE=str(late),CONFECTORY_NATIVE_FIELD_LATE_DONE=str(late_done),CONFECTORY_NATIVE_FIELD_MUTATE=str(mutate))
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
    raise AssertionError(message+' '+str({k:(latest() or {}).get(k) for k in ['screen','operation','job','focus','nativeFieldStatus','message']}))

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
score=p+'Score';other=p+'UnionOther';bare=p+'UnionBare';broken=p+'UnionBroken';many=p+'UnionMany';amount='data:["amount"]';schema=projects[0]/'TableStats.celem'
def native_fill(window,id,text):
 state=wait(lambda t:id in t['hits'][::5] and (not t['job'] or t['screen']=='fields' and t['operation'] in ['native-fields-union','native-fields-objects']),'native editable field '+str(id));info=json.loads(state['fields'][str(id)]);assert info['native'] and info['provider']=='gtk3' and info['enabled'] and not info['readonly'];native_controls.text(int(info['nativeHandle']),text)
 if not text:native_controls.key(int(info['nativeHandle']),0xFF08)
 wait(lambda t:str(id) in t['fields'] and json.loads(t['fields'][str(id)])['text']==text,'native typed '+str(id))
def comparison(window):
 click(window,82);return wait(lambda t:t['screen']=='fields' and not t['job'] and (t.get('nativeFieldChoosing') and t.get('nativeFieldObjects') or t.get('nativeFieldResult')),'native comparison')
def union():return wait(lambda t:t['screen']=='fields' and t.get('nativeFieldResult') and not t['job'],'current readonly union')
def cell(id,key):return next(r for r in union()['nativeFieldResult']['rows'] if r['id']==id)['cells'][key]
def filter_fields(window,text):
 native_fill(window,431,text);click(window,449);return wait(lambda t:t.get('nativeFieldState',{}).get('query')==text and t.get('nativeFieldResult') and not t['job'],'field filter')
def toggle_choice(window,id):
 for attempt in range(30):
  state=wait(lambda t:t.get('nativeFieldObjects') is not None and not t['job'],'owned identity choices');objects=state['nativeFieldObjects'];ids=[row['id'] for row in objects['objects']];offset=state['nativeFieldObjectOffset'];visible=len([id for id in state['hits'][::5] if 500<=id<516]);assert visible>0,'resize to show native choices'
  if id in ids and offset<=ids.index(id)<offset+visible:click(window,500+ids.index(id)-offset);return
  if id in ids:click(window,443 if ids.index(id)<offset else 444)
  else:
   assert objects['page']*64+offset+visible<objects['total'],'owned target absent '+id
   click(window,444)
  wait(lambda t:not t['job'] and (t.get('nativeFieldObjectOffset')!=offset or (t.get('nativeFieldObjects') or {}).get('page')!=objects['page']),'native choice page')
 raise AssertionError('choice paging '+id)
def choose_fields(window,ids,apply=True):
 click(window,435);wait(lambda t:t.get('nativeFieldChoosing') and t.get('nativeFieldObjects') and not t['job'],'choose objects');click(window,447)
 for id in ids:toggle_choice(window,id)
 click(window,445 if apply else 446)
 if apply:wait(lambda t:not t['job'] and not t.get('nativeFieldChoosing') and (t.get('nativeFieldResult') or {}).get('ids')==sorted(ids),'explicit selection result')
 else:wait(lambda t:not t['job'] and not t.get('nativeFieldChoosing'),'cancel selection')
def refresh(window):
 prior=union()['nativeFieldResult']['request'];click(window,434);return wait(lambda t:not t['job'] and t.get('nativeFieldResult') and t['nativeFieldResult']['request']!=prior,'fresh native read')
def begin_hold(window):
 if entered.exists():entered.unlink()
 hold.write_text('owned');click(window,434);wait(lambda t:entered.exists() and t['job'] and 436 in t['hits'][::5],'metadata hold entered',20)
def invariant(context=None):
 state=latest();model=state['model'];assert all(f.read_bytes()==raw for f,raw in original.items()),'unexpected source write';assert len(model['cards'])==2 and len(list(root_path.rglob('project.cpack')))==2;assert not model.get('tables') and not model.get('ai') and not model.get('aiRuns') and not model.get('aiPreview');assert not model.get('aiBindings')
 if context:assert model['selected']['context']==context
 return state
def bases(context):return {name:{k:v for k,v in latest()[name].items() if k.startswith(context+'/')} for name in ['sourceInputVersions','propertyInputVersions']}
def pending(window):
 assert field(54)['text']==source_pending and field(54)['binding']==source_binding;assert field(38)['text']=='NATIVE UNION CHAT UNSENT' and field(38)['binding']==chat_binding;assert json.loads(latest()['fields']['400'])['text']=='5' and json.loads(latest()['fields']['400'])['binding']==cell_binding;assert bases(first)==original_bases;invariant(first)
def back(window):click(window,430);idle('project')
def restore_workspace(window):
 if latest()['model'].get('workspace') is None:
  click(window,55);wait(lambda t:(t['model'].get('workspace') or {}).get('unit') is not None and not t['job'],'explicit source workspace reopen')

def saved_ready():return wait(lambda t:not t['job'] and t.get('nativeFieldStatus','').startswith('View settings explicitly saved'),'native view saved')
try:
 a=launch();wait(lambda t:t['screen']=='intro' and 1 in t['hits'][::5],'intro');resize(display,a,1600,1150);flush(display);wait(lambda t:t['width']==1600 and t['height']==1150,'native resize');click(a,1);idle('home');click(a,100);idle('project');first=latest()['model']['selected']['context'];click(a,55);wait(lambda t:(t['model'].get('workspace') or {}).get('unit') and not t['job'],'source workspace');explore(a);select_id(a,score);click(a,83);wait(lambda t:'54' in t['fields'] and t['model']['workspace']['selected']==score and not t['job'],'owned source')
 click(a,74);wait(lambda t:'89' in t['fields'] and not t['job'],'property fields')
 for attempt in range(20):
  if json.loads(field(88)['text'])==['amount']:break
  click(a,99);wait(lambda t:not t['job'],'property next')
 assert json.loads(field(88)['text'])==['amount'];native_fill(a,89,'5');click(a,318);wait(lambda t:'400' in t['fields'] and not t['job'],'retained pending cell');cell_binding=field(400)['binding'];click(a,75);wait(lambda t:'54' in t['fields'],'source mode');source_pending=field(54)['text']+'\n// NATIVE_FIELD_PENDING';native_fill(a,54,source_pending);source_binding=field(54)['binding'];native_fill(a,38,'NATIVE UNION CHAT UNSENT');chat_binding=field(38)['binding'];original_bases=bases(first);draft_text=latest()['model']['workspace']['unit']['text'];pending(a)
 # Empty saved settings open an explicit chooser and never describe an unselected field.
 if probe.exists():probe.unlink()
 comparison(a);assert latest()['nativeFieldChoosing'] and not latest()['nativeFieldState']['ids'] and not probe.exists();assert all(not r['id'].startswith('NativeFieldExternal::') for r in latest()['nativeFieldObjects']['objects']);choose_fields(a,[score,other,bare,broken]);r=union()['nativeFieldResult'];assert r['failedRows']==1 and r['status']=='partial';assert cell(score,amount)['valueJson']=='9223372036854775807' and cell(other,amount)['valueJson']=='"variant"';assert cell(bare,amount)['state']=='missing' and cell(broken,amount)['defined'] is None;assert cell(score,'nullish')['valueJson']=='null' and cell(other,'nullish')['valueJson']=='0';assert cell(score,'data:["unsetText"]')['state']=='unset' and cell(score,'data:["zero"]')['valueJson']=='0';assert cell(score,'falsey')['valueJson']=='false' and cell(score,'empty')['valueJson']=='""';assert cell(bare,'description')['state']=='default';assert set(probe.read_text().splitlines())=={score,other,bare};assert all(not c['writable'] for row in r['rows'] for c in row['cells'].values());observed=field(432);assert observed['readonly'] and observed['provider']=='gtk3';raw=observed['text'];native_controls.text(int(observed['nativeHandle']),'MUST_NOT_EDIT_READONLY');wait(lambda t:json.loads(t['fields']['432'])['text']==raw,'native readonly input refused');assert 'row-unavailable | defined=unknown' in raw and 'JSON null (actual JSON null)' in raw;invariant(first)
 original_ids=latest()['nativeFieldState']['ids'];resize(display,a,960,700);flush(display);wait(lambda t:t['width']==960 and t['height']==700,'small native comparison');choose_fields(a,[p+'ZPage44'],False);resize(display,a,1600,1150);flush(display);wait(lambda t:t['width']==1600 and t['height']==1150,'restored native comparison');assert latest()['nativeFieldState']['ids']==original_ids;assert not any(s.startswith(p+'ZPage') for s in probe.read_text().splitlines());native_fill(a,448,'UnionBare');wait(lambda t:'shown 1 / 4' in json.loads(t['fields']['432'])['text'],'local native row filter');native_fill(a,448,'');filter_fields(a,'nullish');native_fill(a,431,'pending filter');assert latest()['nativeFieldState']['query']=='nullish';back(a);pending(a);old_widget=observed['nativeHandle'];assert subprocess.run(['xwininfo','-id',str(old_widget)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode!=0,'closed comparison GTK widget remained';comparison(a);assert field(431)['text']=='pending filter' and cell(score,'nullish')['valueJson']=='null';assert field(432)['binding']==observed['binding']
 # Cooperative cancellation completes while the owned hold remains, with no late publication.
 begin_hold(a);click(a,436);wait(lambda t:not t['job'] and t.get('nativeFieldStatus','').startswith('Cancelled'),'native cancellation');assert hold.exists();hold.unlink();assert latest()['nativeFieldState']['query']=='nullish'
 # The copied reader deliberately completes one cancelled request successfully; generation fencing must suppress it.
 previous_request=union()['nativeFieldResult']['request'];late.write_text('one owned noncooperative read');begin_hold(a);click(a,436);wait(lambda t:t['job'] and t.get('nativeFieldStatus','').startswith('Cancelled'),'cancelled late reader held');assert hold.exists();hold.unlink();wait(lambda t:not t['job'] and t.get('nativeFieldStatus','').startswith('Cancelled'),'successful late reply ignored');assert late_done.exists() and json.loads(late_done.read_text())['query']=='nullish';assert union()['nativeFieldResult']['request']==previous_request and json.loads(late_done.read_text())['request']!=previous_request
 begin_hold(a);native_fill(a,431,'zero');click(a,449);hold.unlink();wait(lambda t:not t['job'] and (t.get('nativeFieldResult') or {}).get('query')=='zero','superseded union ignored');assert [f['id'] for f in union()['nativeFieldResult']['fields']]==['data:["zero"]'];invariant(first)
 # A view close during a read cancels and drains before destroying widgets.
 begin_hold(a);click(a,430);idle('project');assert hold.exists();hold.unlink();pending(a);comparison(a);filter_fields(a,'amount')
 # Schema drift is rejected and a deliberate fresh read sees the new field.
 choose_fields(a,[score,other]);filter_fields(a,'amount');begin_hold(a);text=schema.read_text();schema.write_text(text[:text.rfind('}')]+'field newAmount single general long;}');original[schema]=schema.read_bytes();hold.unlink();wait(lambda t:not t['job'] and t.get('nativeFieldStatus','').startswith('Read/save unavailable'),'mid-read schema changed');r=refresh(a)['nativeFieldResult'];assert any(f['id']=='data:["newAmount"]' for f in r['fields']);assert bases(first)==original_bases
 # Both native page axes retain the shared service bounds and explicit target set.
 choose_fields(a,[many]);filter_fields(a,'field');r=union()['nativeFieldResult'];assert len(r['fields'])==16;first_column=r['fields'][0]['id'];click(a,442);r=wait(lambda t:not t['job'] and (t.get('nativeFieldResult') or {}).get('fieldPage')==1,'next native field page')['nativeFieldResult'];assert len(r['fields'])==16 and r['fields'][0]['id']!=first_column;click(a,437);saved_ready();back(a);pending(a);comparison(a);assert union()['nativeFieldResult']['fieldPage']==1
 rows=[p+'UnionRow'+str(n).zfill(2) for n in range(18)];choose_fields(a,rows);filter_fields(a,'index');assert len(union()['nativeFieldResult']['rows'])==16;click(a,440);r=wait(lambda t:not t['job'] and (t.get('nativeFieldResult') or {}).get('rowOffset')==16,'next native row page')['nativeFieldResult'];assert [row['id'] for row in r['rows']]==rows[16:];probes=probe.read_bytes();native_fill(a,448,'UnionRow17');wait(lambda t:'shown 1 / 2' in json.loads(t['fields']['432'])['text'],'local row filter page');assert probe.read_bytes()==probes;native_fill(a,448,'')
 # Exact private view state; rereading metadata cannot rebase its original CAS.
 choose_fields(a,[score,other]);filter_fields(a,'amount');native_fill(a,431,'unapplied filter input');click(a,437);saved_ready();files=list((home_storage/'native-field-unions').glob('*.json'));assert len(files)==1;saved_path=files[0];saved=saved_path.read_bytes();saved_state=json.loads(saved);assert set(saved_state)=={'version','projectId','ids','query','queryInput','rowOffset','fieldPage','rowFilter'} and saved_state['query']=='amount' and saved_state['queryInput']=='unapplied filter input';saved_path.write_bytes(saved+b'\n');refresh(a);click(a,437);wait(lambda t:not t['job'] and t.get('nativeFieldStatus','').startswith('Read/save unavailable'),'private settings stale CAS');assert saved_path.read_bytes()==saved+b'\n' and field(431)['text']=='unapplied filter input';saved_path.write_bytes(saved);saved_path.write_text('{broken');click(a,438);wait(lambda t:not t['job'] and t.get('nativeFieldStatus','').startswith('Read/save unavailable'),'corrupt settings retained');assert 437 not in latest()['hits'][::5] and saved_path.read_text()=='{broken';saved_path.write_bytes(saved);click(a,438);union();assert field(431)['text']=='unapplied filter input'
 for action in [449,434,437]:
  native_fill(a,431,'x'*257);click(a,action);wait(lambda t:t.get('nativeFieldStatus','').startswith('Filter limit 256') and not t['job'],'overlong native filter');assert field(431)['text']=='x'*257 and saved_path.read_bytes()==saved
 native_fill(a,431,'x'*257);back(a);pending(a);comparison(a);assert field(431)['text']=='x'*257 and latest()['nativeFieldState']['query']=='amount';native_fill(a,431,'unapplied filter input');back(a);pending(a)
 # A/B/A isolates view settings and all live source/chat/cell bindings.
 comparison(a);begin_hold(a);click(a,430);idle('project');hold.unlink();leave_project(a);idle('home');click(a,103);idle('project');second=latest()['model']['selected']['context'];assert second!=first;click(a,55);wait(lambda t:(t['model'].get('workspace') or {}).get('unit') and not t['job'],'B source workspace');comparison(a);assert latest()['nativeFieldChoosing'] and latest()['nativeFieldState']['ids']==[];choose_fields(a,[score]);filter_fields(a,'amount');assert cell(score,amount)['valueJson']=='41';click(a,437);saved_ready();back(a);leave_project(a);idle('home');click(a,100);idle('project');assert latest()['model']['selected']['context']==first;restore_workspace(a);pending(a);comparison(a);assert latest()['nativeFieldState']['ids']==sorted([score,other]) and field(431)['text']=='unapplied filter input';assert cell(score,amount)['valueJson']=='9223372036854775807';assert bases(first)==original_bases;invariant(first)
 # New owned source observation retains the original field-write revision; an old write is refused.
 mutate.write_text(json.dumps({'id':score,'from':'9223372036854775807','to':'9223372036854775806'}));refresh(a);assert not mutate.exists() and cell(score,amount)['valueJson']=='9223372036854775806' and bases(first)==original_bases;assert next(r for r in union()['nativeFieldResult']['rows'] if r['id']==score)['revision']==1;back(a);pending(a);click(a,319);wait(lambda t:400 in t['hits'][::5] and not t['job'],'retained cell made foreground');click(a,401);wait(lambda t:not t['job'] and (t['model']['status'].startswith('Error:') or (t['model'].get('workspaceViews',{}).get(first,{}).get('1',{}).get('workspace') or {}).get('conflict')),'old retained cell CAS refused');assert json.loads(latest()['fields']['400'])['text']=='5' and json.loads(latest()['fields']['400'])['binding']==cell_binding;assert field(54)['text']==source_pending and field(54)['binding']==source_binding;assert bases(first)==original_bases;invariant(first);comparison(a);union();screenshot(a,'native-fields-before-cold');evidence_dir=Path('/workspace/scratch/confectory-native-fields-ui');evidence_dir.mkdir(exist_ok=True);shutil.copyfile(root_path/'native-fields-before-cold.png',evidence_dir/'before-cold.png')
 # WM close during the readonly job drains it before releasing the session/controls.
 begin_hold(a);end(a);assert hold.exists();hold.unlink();score_file.write_text(score_file.read_text().replace('9223372036854775807','9223372036854775805'));original[score_file]=score_file.read_bytes();text=schema.read_text();schema.write_text(text[:text.rfind('}')]+'field coldAmount single general long;}');original[schema]=schema.read_bytes();a=launch();wait(lambda t:t['screen']=='intro' and 1 in t['hits'][::5],'cold intro');resize(display,a,1600,1150);flush(display);click(a,1);idle('home');click(a,100);idle('project');click(a,55);wait(lambda t:(t['model'].get('workspace') or {}).get('unit') and not t['job'],'cold source workspace');comparison(a);r=union()['nativeFieldResult'];assert latest()['nativeFieldState']==saved_state and field(431)['text']=='unapplied filter input';assert any(f['id']=='data:["coldAmount"]' for f in r['fields']) and cell(score,amount)['valueJson']=='9223372036854775805';assert not latest()['model'].get('tables');invariant();screenshot(a,'native-fields-after-cold');shutil.copyfile(root_path/'native-fields-after-cold.png',evidence_dir/'after-cold.png');end(a);assert not native_controls.errors,native_controls.errors
 print('PASS native field union actual GTK input: explicit owned targets and readonly exact JSON/missing/null/default/unknown, bounded native pages/filter, settings CAS/corruption, pending source/chat/cell binding and original write CAS, cooperative cancel/late response/view close/project A/B/A/WM disposal/latest cold schema; no source writes or AI; private evidence '+storage,flush=True)
except BaseException:
 print('Native field UI failure evidence '+storage,flush=True)
 if app and app.poll() is None:
  try:screenshot(find(b'Confectory - Projects'),'native-fields-failure')
  except Exception:pass
  os.killpg(app.pid,signal.SIGTERM);app.wait(timeout=15)
 if log:log.close()
 raise
