#!/usr/bin/env python3
"""Actual Main presentation lifetime, using ordinary X11 gestures and product controls."""
from pathlib import Path
helper=Path(__file__).with_name('project_shell_x11.py')
source=helper.read_text();marker='try:\n    a=launch();';assert source.count(marker)==1
exec(compile(source.split(marker)[0],str(helper),'exec'),globals())
def row(t,id):return next((r for r in t['orderFrame']['windows'] if r['id']==id),None)
def pointer(kind,x,y):
    event=Event(kind,0,1,display,a,root,0,100,x,y,0,0,256 if kind==6 else 0,1,1)
    buf=c.create_string_buffer(192);c.memmove(buf,c.byref(event),c.sizeof(event));assert send(display,a,0,0,buf);flush(display)
def drag(id,dx,dy):
    b=row(latest(),id)['bounds'];x,y=b[0]+20,b[1]+3
    pointer(4,x,y);time.sleep(.06);pointer(6,x+dx,y+dy);time.sleep(.06);pointer(5,x+dx,y+dy)
def fold(id):
    b=row(latest(),id)['bounds'];x,y=b[0]+20,b[1]+3
    for _ in range(2):
        pointer(4,x,y);time.sleep(.04);pointer(5,x,y);time.sleep(.04)
try:
    a=launch();wait(lambda t:t['screen']=='intro','intro');click(a,1);click(a,2);click(a,10);type_text(a,'Window A');click(a,13)
    state=wait(lambda t:t['screen']=='project' and row(t,6),'project window');context=state['model']['selected']['context'];path=state['model']['selected']['path']
    click(a,55);state=wait(lambda t:t['model'].get('workspace') and '54' in t['fields'],'source workspace');original=json.loads(state['fields']['54']);native_handle=original['nativeHandle'];draft=original['text']
    click(a,54);native_controls.key(int(native_handle),'a',(0xFFE3,));type_text(a,'return 0; // retained window draft');click(a,58)
    state=wait(lambda t:not t['job'] and t['model']['status'].startswith('Local source draft saved'),'save owned draft');draft=json.loads(state['fields']['54'])['text']
    # Fold removes native bindings from the frame, without replacing draft/session ownership.
    fold(6);state=wait(lambda t:row(t,6)['bounds'][3]==26 and '54' not in t['fields'],'fold source');assert state['model']['selected']['context']==context
    drag(6,0,40);state=wait(lambda t:row(t,6)['bounds'][1]>80,'drag folded source');moved=row(state,6)['bounds'][:2]
    fold(6);state=wait(lambda t:row(t,6)['bounds'][3]>26 and '54' in t['fields'],'expand source');assert json.loads(state['fields']['54'])['nativeHandle']==native_handle and json.loads(state['fields']['54'])['text']==draft
    # Two independently retained windows, repeated idle frames, and actual activation order.
    click(a,33);state=wait(lambda t:row(t,10) is not None,'menu');drag(10,160,30);state=wait(lambda t:row(t,10)['bounds'][0]>300,'drag menu');menu_bounds=row(state,10)['bounds']
    fold(10);wait(lambda t:row(t,10)['bounds'][3]==26,'fold menu');screenshot(a,'folded-menu-source')
    click(a,33);wait(lambda t:row(t,10) is None,'hide menu');click(a,33);state=wait(lambda t:row(t,10) is not None,'reopen menu');assert row(state,10)['bounds'][3]==26 and row(state,10)['bounds'][:2]==menu_bounds[:2]
    fold(10);state=wait(lambda t:row(t,10)['bounds'][3]>26,'restore menu');saved=row(state,10)['bounds'];time.sleep(.5);assert row(latest(),10)['bounds']==saved
    source_bounds=row(state,6)['bounds'];pointer(4,source_bounds[0]+20,source_bounds[1]+3);pointer(5,source_bounds[0]+20,source_bounds[1]+3)
    state=wait(lambda t:t['orderFrame']['active']==6 and [r['id'] for r in t['orderFrame']['windows']][-1]==6,'raise source');screenshot(a,'source-raised')
    click(a,33);wait(lambda t:row(t,10) is None,'hide behind source');click(a,33);state=wait(lambda t:t['orderFrame']['active']==10,'reopen raises menu');assert row(state,10)['bounds']==saved
    # Resize constrains reachable handles; restoration recovers intent.
    resize(display,a,520,420);flush(display);state=wait(lambda t:t['width']==520,'small');assert row(state,10)['bounds'][0]<520 and row(state,10)['bounds'][1]<420
    resize(display,a,960,700);flush(display);state=wait(lambda t:t['width']==960 and row(t,10)['bounds']==saved,'resize recovery')
    click(a,15);wait(lambda t:t['screen']=='home','hide A');click(a,2);click(a,10);type_text(a,'Window B');click(a,13);state=wait(lambda t:t['screen']=='project' and t['model']['selected']['context']!=context,'B');click(a,33);state=wait(lambda t:row(t,10) is not None,'B menu');assert row(state,10)['bounds']!=saved
    click(a,15);state=wait(lambda t:t['screen']=='home','hide B');index=next(i for i,c in enumerate(state['model']['cards']) if c['path']==path);click(a,100+index*3);state=wait(lambda t:t['screen']=='project' and t['model']['selected']['context']==context,'A same context');click(a,55);state=wait(lambda t:'54' in t['fields'],'reopen retained source');assert json.loads(state['fields']['54'])['nativeHandle']==native_handle and json.loads(state['fields']['54'])['text']==draft;click(a,33);state=wait(lambda t:row(t,10) is not None,'A menu restored');assert row(state,10)['bounds']==saved
    click(a,52);wait(lambda t:t['screen']=='home','full close A');click(a,100+index*3);state=wait(lambda t:t['screen']=='project' and t['model']['selected']['context']!=context,'fresh A owner');click(a,33);state=wait(lambda t:row(t,10) is not None,'fresh A menu');assert row(state,10)['bounds']!=saved
    end(a);print('Actual EditorHome retained windows, fold/native binding, resize recovery, project isolation and close cleanup PASS');print('Evidence:',storage)
finally:
    if 'app' in globals() and app.poll() is None:app.kill();app.wait()
