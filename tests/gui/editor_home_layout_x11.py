#!/usr/bin/env python3
"""Actual EditorHome: bounded panels, persistent native inputs and responsive proposal layout."""
from pathlib import Path
helper=Path(__file__).with_name('project_shell_x11.py');source=helper.read_text();marker='try:\n    a=launch();';assert source.count(marker)==1
exec(compile(source.split(marker)[0],str(helper),'exec'),globals())
def clean(t):return not t['job'] and not t['model']['status'].startswith('Error:')
def field(t,id):return json.loads(t['fields'][str(id)])
def window(t,id):return next(r for r in t['orderFrame']['windows'] if r['id']==id)
def bounded(t,id):
    b=window(t,id)['bounds'];chat=next(c['bounds'] for c in window(t,1)['controls'] if c['id']==39);assert b[0]>=0 and b[1]>=58 and b[0]+b[2]<=t['width'] and b[1]+b[3]<=chat[1]-8,(id,b,chat)
    # Every active panel control is fully inside its owner, including the bottom actions.
    for row in window(t,id)['controls']:
        x,y,w,h=row['bounds'];assert x>=b[0] and y>=b[1] and x+w<=b[0]+b[2] and y+h<=b[1]+b[3],(id,row,b)
try:
    a=launch();wait(lambda t:t['screen']=='intro','intro');click(a,1);click(a,2);click(a,10);type_text(a,'Layout Acceptance');click(a,13);t=wait(lambda t:t['screen']=='project' and clean(t),'project');context=t['model']['selected']['context']
    click(a,38);type_text(a,'Project chat remains separate');chat_handle=field(latest(),38)['nativeHandle'];click(a,55);wait(lambda t:'54' in t['fields'],'source');source_handle=field(latest(),54)['nativeHandle']
    click(a,8);click(a,23);click(a,20);wait(lambda t:'310' in t['fields'] and clean(t),'Helper conversation');click(a,310);type_text(a,'Helper conversation remains separate');wait(lambda t:field(t,310)['text']=='Helper conversation remains separate','Helper typed input');helper_handle=field(latest(),310)['nativeHandle']
    for width,height in [(960,700),(1200,900),(640,520),(960,700)]:
        resize(display,a,width,height);flush(display);t=wait(lambda t:t['width']==width and t['height']==height and '310' in t['fields'] and clean(t),'Helper resize');bounded(t,15)
        assert field(t,38)['visible'] and field(t,38)['text']=='Project chat remains separate' and field(t,38)['nativeHandle']==chat_handle
        assert field(t,310)['visible'] and field(t,310)['text']=='Helper conversation remains separate' and field(t,310)['nativeHandle']==helper_handle
        assert field(t,313)['visible'] and all(id in t['hits'][::5] for id in [25,26,27,28,42])
        screenshot(a,f'helper-layout-{width}x{height}')
    # A chat click must not dismiss or steal the Helper draft.
    click(a,38);type_text(a,' + still editable');assert field(latest(),310)['text']=='Helper conversation remains separate';click(a,42);wait(lambda t:'54' in t['fields'] and clean(t),'source retained');assert field(latest(),54)['nativeHandle']==source_handle
    click(a,17);t=wait(lambda t:clean(t) and t['model']['helperPanel']['mode']=='augment','proposal panel');bounded(t,16);assert sum(text.startswith('Proposal ') for text in t['texts'])>=3;screenshot(a,'three-proposal-columns')
    resize(display,a,640,520);flush(display);t=wait(lambda t:t['width']==640 and 323 in t['hits'][::5] and clean(t),'compact proposal paging');bounded(t,16);revision=t['model']['revision'];click(a,323);click(a,323);t=latest();assert 'Proposal 3 / 3' in t['texts'] and t['model']['revision']==revision and not t['model'].get('aiRuns');assert any(text.startswith('No proposal yet;') for text in t['texts']);bounded(t,16);screenshot(a,'compact-proposal-page')
    click(a,322);click(a,42);resize(display,a,1200,900);flush(display);wait(lambda t:t['width']==1200,'restore');click(a,8);click(a,20);t=wait(lambda t:'310' in t['fields'] and clean(t),'Helper returns');assert field(t,310)['nativeHandle']==helper_handle and field(t,310)['text']=='Helper conversation remains separate';bounded(t,15)
    end(a);print('Actual EditorHome bounded Helper/chat/Dock, responsive proposal columns/paging and input retention PASS');print('Evidence:',storage)
finally:
    if app and app.poll() is None:app.kill();app.wait()
