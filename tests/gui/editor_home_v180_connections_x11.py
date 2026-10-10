#!/usr/bin/env python3
"""Production ProjectPack UI: scoped inputs and owned schema navigation, no provider calls."""
from pathlib import Path
helper=Path(__file__).with_name('project_shell_x11.py')
source=helper.read_text();marker='try:\n    a=launch();';assert source.count(marker)==1
exec(compile(source.split(marker)[0],str(helper),'exec'),globals())
def clean(t):return not t['job'] and not t['model']['status'].startswith('Error:')
def field(t,id):return json.loads(t['fields'][str(id)])
def replace(id,text):
    click(a,id);native_controls.key(int(field(latest(),id)['nativeHandle']),'a',(0xFFE3,));type_text(a,text)
def select(id):
    click(a,73);replace(82,id);click(a,83);wait(lambda t:clean(t) and t['model']['workspace']['selected']==id,'selected '+id)
def save():
    click(a,58);wait(lambda t:clean(t) and t['model']['status'].startswith('Local source draft saved'),'draft saved')
try:
    a=launch();wait(lambda t:t['screen']=='intro','intro');click(a,1);click(a,2);replace(10,'UI Connections');click(a,13)
    t=wait(lambda t:t['screen']=='project' and clean(t),'project');ns=t['model']['selected']['namespace'];context=t['model']['selected']['context'];path=t['model']['selected']['path']
    resize(display,a,1200,1000);flush(display);wait(lambda t:t['width']==1200,'larger editor')
    replace(38,'project draft stays here');click(a,317);wait(lambda t:'84' in t['fields'] and clean(t),'object browser')
    click(a,85);replace(84,ns+'::Shape');click(a,86);wait(lambda t:clean(t) and t['model']['workspace']['selected']==ns+'::Shape','create ordinary schema draft')
    click(a,75);replace(54,'schema '+ns+'::Shape { field count single general int; }');save()
    click(a,73)
    for _ in range(5):click(a,85)
    replace(84,ns+'::Thing');click(a,86);wait(lambda t:clean(t) and t['model']['workspace']['selected']==ns+'::Thing','create ordinary object draft')
    click(a,75);replace(54,'object '+ns+'::Thing { use schema '+ns+'::Shape; data count = 7; }');save();source_binding=field(latest(),54)['nativeHandle']
    click(a,74);t=wait(lambda t:clean(t) and t['model']['workspace'].get('schemaView'),'actual object schema');assert t['model']['workspace']['schemaView']['rows'][0]['schemaOrigin']==ns+'::Shape'
    click(a,307);t=wait(lambda t:clean(t) and t['model']['workspace']['selected']==ns+'::Shape' and t['model']['workspace'].get('schemaView'),'open resolved schema');assert t['model']['workspace']['unit']['kind']=='schema';screenshot(a,'resolved-owned-schema')
    click(a,75);replace(54,'schema '+ns+'::Shape { field count single general int; field note single general string; }');save();click(a,74);wait(lambda t:clean(t) and t['model']['workspace'].get('schemaView'),'schema refresh');click(a,308)
    t=wait(lambda t:clean(t) and t['model']['workspace']['selected']==ns+'::Thing' and len(t['model']['workspace'].get('schemaView',{}).get('rows',[]))==2,'return shares schema draft');assert t['model']['workspace']['schemaView']['rows'][0]['datum']['scalar']==7
    click(a,75);t=wait(lambda t:'54' in t['fields'],'original source');assert field(t,54)['nativeHandle']==source_binding and 'data count = 7' in field(t,54)['text']
    # Explorer search preserves the selected classification, with no domain mutation.
    click(a,73);click(a,203);wait(lambda t:clean(t) and t['model']['workspace']['kind']=='module','module filter');replace(77,'Missing');click(a,78);t=wait(lambda t:clean(t) and t['model']['workspace']['query']=='Missing','filtered search');assert t['model']['workspace']['kind']=='module'
    replace(77,'');click(a,204);wait(lambda t:clean(t) and t['model']['workspace']['kind']=='','all objects');select(ns+'::Thing')
    click(a,17);click(a,22);t=wait(lambda t:'309' in t['fields'],'direction');assert field(t,309)['text']=='';replace(309,'object direction only');direction_binding=field(latest(),309)['nativeHandle'];click(a,42);wait(lambda t:'309' not in t['fields'],'back to cards');click(a,22);t=wait(lambda t:'309' in t['fields'],'direction retained');assert field(t,309)['text']=='object direction only' and field(t,309)['nativeHandle']==direction_binding;assert t['model'].get('aiPreview') is None;click(a,42);click(a,42)
    select(ns+'::ProjectInfo');click(a,17);click(a,22);t=wait(lambda t:'309' in t['fields'],'other target direction');assert field(t,309)['text']=='';click(a,42);click(a,42);select(ns+'::Thing');click(a,17);click(a,22);t=wait(lambda t:'309' in t['fields'],'original target direction');assert field(t,309)['text']=='object direction only' and field(t,309)['nativeHandle']==direction_binding;click(a,42);click(a,42)
    # Each Helper gets its own local message draft; no Worker chat or hidden send.
    click(a,8);wait(lambda t:clean(t) and t['model'].get('helpers') is not None,'Helpers');click(a,23);wait(lambda t:clean(t) and len(t['model']['helpers'])==1,'main recruitment');click(a,20);t=wait(lambda t:clean(t) and '310' in t['fields'],'main Helper');main=t['model']['helperContext']['helper'];replace(310,'main helper draft');main_binding=field(latest(),310)['nativeHandle'];assert field(latest(),38)['text']=='project draft stays here';assert 311 not in latest()['hits'][::5]
    click(a,28);click(a,24);wait(lambda t:clean(t) and len(t['model']['helpers'])==2,'project recruitment');click(a,21);t=wait(lambda t:clean(t) and t['model']['helperContext']['helper']!=main and '310' in t['fields'],'other Helper');assert field(t,310)['text']=='';replace(310,'project helper draft');click(a,28);click(a,20);t=wait(lambda t:clean(t) and t['model']['helperContext']['helper']==main and '310' in t['fields'],'main restored');assert field(t,310)['text']=='main helper draft' and field(t,310)['nativeHandle']==main_binding;screenshot(a,'scoped-helper-input')
    resize(display,a,640,520);flush(display);t=wait(lambda t:t['width']==640 and '310' in t['fields'] and 42 in t['hits'][::5],'narrow Helper controls');close_index=t['hits'][::5].index(42)*5;_,x,y,w,h=t['hits'][close_index:close_index+5];assert x>=0 and y>=0 and x+w<=640 and y+h<=520 and field(t,310)['nativeHandle']==main_binding;resize(display,a,1200,1000);flush(display);wait(lambda t:t['width']==1200,'restore viewport')
    click(a,42);leave_project(a);t=wait(lambda t:t['screen']=='home','hide');index=next(i for i,row in enumerate(t['model']['cards']) if row['path']==path);click(a,100+index*3);wait(lambda t:t['screen']=='project' and t['model']['selected']['context']==context,'same project owner');click(a,8);click(a,20);t=wait(lambda t:clean(t) and '310' in t['fields'],'retained Helper input');assert field(t,310)['nativeHandle']==main_binding and field(t,310)['text']=='main helper draft'
    assert not t['model'].get('aiRuns');end(a);print('Production EditorHome scoped Helper/direction inputs, owned schema draft navigation and filtered search PASS');print('Evidence:',storage)
finally:
    if 'app' in globals() and app.poll() is None:app.kill();app.wait()
