#!/usr/bin/env python3
"""Ordinary actual EditorHome ProjectPack, multiple borrowed draft views via native input."""
from pathlib import Path
helper=Path(__file__).with_name('project_shell_x11.py');source=helper.read_text();marker='try:\n    a=launch();';assert source.count(marker)==1
exec(compile(source.split(marker)[0],str(helper),'exec'),globals())
def clean(t):return not t['job'] and not t['model']['status'].startswith('Error:')
def field(t,id):return json.loads(t['fields'][str(id)])
def replace(id,text):
    click(a,id);native_controls.key(int(field(latest(),id)['nativeHandle']),'a',(0xFFE3,));type_text(a,text)
def row(t,id):return next((r for r in t['orderFrame']['windows'] if r['id']==id),None)
def pointer(kind,x,y):
    event=Event(kind,0,1,display,a,root,0,100,x,y,0,0,256 if kind==6 else 0,1,1);buf=c.create_string_buffer(192);c.memmove(buf,c.byref(event),c.sizeof(event));assert send(display,a,0,0,buf);flush(display)
def raise_view(id):
    if id>=30:
        click(a,319+id-30);wait(lambda t:clean(t) and t['orderFrame']['active']==id,'activate retained view');time.sleep(.45);return
    b=row(latest(),id)['bounds'];pointer(4,b[0]+20,b[1]+3);pointer(5,b[0]+20,b[1]+3);wait(lambda t:t['orderFrame']['active']==id,'raise view '+str(id));time.sleep(.45)
def fold(id):
    b=row(latest(),id)['bounds']
    for _ in range(2):pointer(4,b[0]+20,b[1]+3);time.sleep(.05);pointer(5,b[0]+20,b[1]+3);time.sleep(.05)
def drag(id,dx,dy):
    b=row(latest(),id)['bounds'];x,y=b[0]+20,b[1]+3;pointer(4,x,y);time.sleep(.06);pointer(6,x+dx,y+dy);time.sleep(.06);pointer(5,x+dx,y+dy);time.sleep(.5)
def select(id):
    raise_view(6);click(a,73);replace(82,id);click(a,83);wait(lambda t:clean(t) and t['model']['workspace']['selected']==id,'selected '+id)
def save():click(a,58);wait(lambda t:clean(t) and t['model']['status'].startswith('Local source draft saved'),'saved')
def projection(t,slot):return t['model']['workspaceViews'][context][str(slot)]['workspace']
try:
    a=launch();wait(lambda t:t['screen']=='intro','intro');click(a,1);click(a,2);replace(10,'Multiple Views');click(a,13)
    t=wait(lambda t:t['screen']=='project' and clean(t),'project');ns=t['model']['selected']['namespace'];context=t['model']['selected']['context'];path=t['model']['selected']['path']
    resize(display,a,1400,1050);flush(display);wait(lambda t:t['width']==1400,'viewport');click(a,317)
    click(a,85);replace(84,ns+'::Shape');click(a,86);wait(lambda t:clean(t) and t['model']['workspace']['selected']==ns+'::Shape','schema');click(a,75);replace(54,'schema '+ns+'::Shape { field count single general int; field child single compound '+ns+'::Leaf; }');save();click(a,73)
    replace(84,ns+'::Leaf');click(a,86);wait(lambda t:clean(t) and t['model']['workspace']['selected']==ns+'::Leaf','leaf schema');click(a,75);replace(54,'schema '+ns+'::Leaf { field flag single general bool; }');save();click(a,73)
    for _ in range(5):click(a,85)
    for name,value in [('First',7),('Second',11)]:
        replace(84,ns+'::'+name);click(a,86);wait(lambda t:clean(t) and t['model']['workspace']['selected']==ns+'::'+name,'object');click(a,75);replace(54,'object '+ns+'::'+name+' { use schema '+ns+'::Shape; data count = '+str(value)+'; data child = { flag = false; }; }');save();click(a,73)
    select(ns+'::First');click(a,75);click(a,318);t=wait(lambda t:clean(t) and '400' in t['fields'],'first retained source');first_binding=field(t,400)['buffer'];first_handle=field(t,400)['nativeHandle'];assert field(t,54)['buffer']==first_binding
    # The two native views of one buffer must not overwrite the active input with an old mirror.
    first_text='object '+ns+'::First { use schema '+ns+'::Shape; data count = 9; data child = { flag = false; }; }'
    replace(400,first_text);t=wait(lambda t:field(t,400)['text']==first_text and field(t,54)['text']==first_text,'shared native source text');click(a,401);wait(lambda t:clean(t) and 'data count = 9' in projection(t,1)['unit']['text'],'save only first')
    raise_view(6);first_text=first_text.replace('count = 9','count = 10');replace(54,first_text);wait(lambda t:field(t,54)['text']==first_text and field(t,400)['text']==first_text,'primary edits shared native mirror');save()
    select(ns+'::Second');click(a,75);click(a,318);t=wait(lambda t:clean(t) and '404' in t['fields'],'second retained source');assert field(t,404)['buffer']!=first_binding;assert projection(t,1)['selected']==ns+'::First';assert projection(t,2)['selected']==ns+'::Second'
    second_text='object '+ns+'::Second { use schema '+ns+'::Shape; data count = 12; data child = { flag = false; }; }';replace(404,second_text);click(a,405);t=wait(lambda t:clean(t) and 'data count = 12' in projection(t,2)['unit']['text'],'save second');assert 'data count = 10' in projection(t,1)['unit']['text']
    screenshot(a,'two-owned-source-views');raise_view(30);fold(30);wait(lambda t:row(t,30)['bounds'][3]==26 and '400' not in t['fields'],'fold retains owner');drag(30,220,25);fold(30);t=wait(lambda t:'400' in t['fields'] and row(t,30)['bounds'][3]>26,'unfold');assert field(t,400)['nativeHandle']==first_handle and field(t,400)['text']==first_text
    # Close one presentation and reopen the same borrowed draft, without saving final sources.
    raise_view(30);first_text+=' // unsaved view input';replace(400,first_text);click(a,403);wait(lambda t:row(t,30) is None,'close first view');select(ns+'::First');click(a,75);click(a,318);t=wait(lambda t:clean(t) and '400' in t['fields'],'reopen first');assert field(t,400)['buffer']==first_binding and field(t,400)['nativeHandle']==first_handle and field(t,400)['text']==first_text;assert 'unsaved view input' not in projection(t,1)['unit']['text'];click(a,401);wait(lambda t:clean(t) and 'unsaved view input' in projection(t,1)['unit']['text'],'explicitly save reopened input')
    raise_view(6);click(a,74);wait(lambda t:clean(t) and t['model']['workspace'].get('schemaView'),'First properties')
    for _ in range(5):
        if field(latest(),88)['text']=='["child"]':break
        click(a,99)
    assert field(latest(),88)['text']=='["child"]';click(a,318);t=wait(lambda t:clean(t) and '408' in t['fields'],'compound view');assert json.loads(field(t,408)['text'])=={'flag':False};replace(408,'{"flag":true}');click(a,409);t=wait(lambda t:clean(t) and 'flag = true' in projection(t,1)['unit']['text'],'compound write updates source');assert projection(t,2)['selected']==ns+'::Second' and 'flag = false' in projection(t,2)['unit']['text']
    raise_view(6);wait(lambda t:json.loads(field(t,89)['text'])=={'flag':True},'clean primary form follows same draft');click(a,307);wait(lambda t:clean(t) and t['model']['workspace']['selected']==ns+'::Shape','real schema alongside object views');click(a,75);replace(54,'schema '+ns+'::Shape { field count single general int; field child single compound '+ns+'::Leaf; field note single general string; }');save();t=wait(lambda t:clean(t) and len(projection(t,3).get('schemaView',{}).get('rows',[]))==4,'schema edit refreshes retained compound view');assert projection(t,3)['selected']==ns+'::First';screenshot(a,'compound-and-schema-shared-draft')
    # Reuse a closed slot for the same object's general field alongside compound and source views.
    raise_view(31);click(a,407);wait(lambda t:row(t,31) is None,'close second source');select(ns+'::First');click(a,74);wait(lambda t:clean(t) and t['model']['workspace'].get('schemaView'),'First refreshed properties');
    for _ in range(4):
        t=latest();current=json.loads(field(t,88)['text'])
        if current==['count']:break
        paths=[r['path'] for r in t['model']['workspace']['schemaView']['rows']]
        click(a,99 if paths.index(current)<paths.index(['count']) else 98)
    wait(lambda t:field(t,88)['text']=='["count"]','general field');click(a,318);t=wait(lambda t:clean(t) and '404' in t['fields'],'general retained field');assert field(t,404)['text']=='10'
    raise_view(32);replace(408,'{"flag":false}');raise_view(31);replace(404,'15');click(a,405);wait(lambda t:clean(t) and 'count = 15' in projection(t,1)['unit']['text'],'general update leaves compound draft local');raise_view(32);click(a,409);t=wait(lambda t:not t['job'] and t['model']['status'].startswith('Error:'),'stale compound revision refused');assert 'revision conflict' in t['model']['status'] and 'flag = true' in projection(t,1)['unit']['text'] and field(t,408)['text']=='{"flag":false}'
    raise_view(6)
    for _ in range(4):
        t=latest();current=json.loads(field(t,88)['text'])
        if current==['child']:break
        paths=[r['path'] for r in t['model']['workspace']['schemaView']['rows']]
        click(a,99 if paths.index(current)<paths.index(['child']) else 98)
    click(a,90);t=wait(lambda t:not t['job'] and t['model']['status'].startswith('Error:'),'primary shared form also keeps its captured revision');assert 'revision conflict' in t['model']['status'] and 'flag = true' in t['model']['workspace']['unit']['text'];click(a,87);wait(lambda t:clean(t) and t['model']['workspace'].get('schemaView'),'refresh primary after conflict')
    raise_view(32);replace(408,'{"flag":true}');raise_view(31);wait(lambda t:clean(t),'explicit retained-view refresh');assert projection(latest(),2)['selected']==ns+'::First';select(ns+'::Second');click(a,75);assert 'count = 12' in field(latest(),54)['text'];
    for window,x,y in [(30,230,115),(31,740,115),(32,500,450)]:
        raise_view(window);b=row(latest(),window)['bounds'];drag(window,x-b[0],y-b[1])
    screenshot(a,'general-compound-and-source-views')
    raise_view(6)
    # Review/cancel is still the single explicit final-source boundary.
    click(a,73);replace(207,json.dumps([ns+'::First',ns+'::Second',ns+'::Shape',ns+'::Leaf',ns+'::ProjectManifest']));click(a,206);t=wait(lambda t:clean(t) and t['model']['workspace'].get('review'),'review group');assert t['model']['workspace']['review']['status']=='ready';click(a,66);wait(lambda t:clean(t) and t['model']['workspace'].get('review') is None,'cancel review');assert not (Path(path).parent/'elements'/'First.celem').exists()
    raise_view(30);binding=field(latest(),400)['nativeHandle'];leave_project(a);wait(lambda t:t['screen']=='home','hide');click(a,2);replace(10,'Different Owner');click(a,13);t=wait(lambda t:clean(t) and t['screen']=='project' and t['model']['selected']['context']!=context,'other project');assert not t['retainedViews'] and '400' not in t['fields'];leave_project(a);t=wait(lambda t:t['screen']=='home','hide other');index=next(i for i,r in enumerate(t['model']['cards']) if r['path']==path);click(a,100+index*3);t=wait(lambda t:clean(t) and t['screen']=='project' and t['model']['selected']['context']==context and '400' in t['fields'],'same owner restored');assert field(t,400)['nativeHandle']==binding and 'flag = true' in field(t,400)['text'];raise_view(30);assert projection(latest(),3)['selected']==ns+'::First'
    click(a,33);click(a,52);wait(lambda t:t['screen']=='home','complete close');click(a,100+index*3);t=wait(lambda t:clean(t) and t['screen']=='project' and t['model']['selected']['context']!=context,'fresh context');assert not t['retainedViews'] and context not in t['model'].get('workspaceViews',{})
    end(a);print('Actual EditorHome simultaneous owned views and shared native draft PASS');print('Evidence:',storage)
finally:
    if 'app' in globals() and app.poll() is None:app.kill();app.wait()
