"""I1-I3 pure candidates: exact values, dependencies and full affected validation.

No source writes, real accounts, providers, runtime execution or accepted grants.
"""
import copy, hashlib, json, os, pathlib, subprocess, sys, tempfile

repo = pathlib.Path(sys.argv[1]).resolve()
dotnet = os.environ.get('CONFECTORY_DOTNET', '/workspace/toolchains/dotnet-10.0.401/dotnet')
root = pathlib.Path(tempfile.mkdtemp(prefix='confectory-field-definitions-'))
n = 'Owned.Fields::'
owner = n + 'A'
items = {
    'Main': ('function', f'function {n}Main () -> int {{}}'),
    'Fn': ('function', f'function {n}Fn (long value) -> long {{}}'),
    'Impl': ('implementation', f'implementation {n}Impl for {n}Fn (long value) -> long {{body common "Impl.csbody";}}'),
    'Leaf': ('schema', f'schema {n}Leaf {{field HP single general long;}}'),
    'Leaf2': ('schema', f'schema {n}Leaf2 {{field HP single general long;field Note single general string;}}'),
    'Derived': ('schema', f'schema {n}Derived extends {n}Leaf {{}}'),
    'Local': ('schema', f'schema {n}Local {{field Value single general long;field Tree single compound {n}Leaf;field Ref single reference {n}Derived;field Values multiple general long;}}'),
    'Target': ('object', f'object {n}Target {{use schema {n}Derived;data HP=100;}}'),
    'A': ('object', f'object {owner} {{use schema {n}Local;data Value=9223372036854775806;data Tree={{HP=9223372036854775805;}};data Ref={n}Target;data Values=[9223372036854775804,2];}}'),
    'Other': ('object', f'object {n}Other {{}}'),
    'Info': ('schema', f'schema {n}Info {{field Value single general long;}}'),
}
foreign = root / 'registered'
foreign.mkdir()
(foreign / 'pack.cpack').write_text('pack External.Fields version "1" {element Leaf schema "Leaf.celem";element Fn function "Fn.celem";}')
(foreign / 'Leaf.celem').write_text('schema External.Fields::Leaf {field HP single general long;}')
(foreign / 'Fn.celem').write_text('function External.Fields::Fn (long value) -> long {}')
hidden = root / 'hidden'
hidden.mkdir()
(hidden / 'pack.cpack').write_text('pack Hidden.Fields version "1" {element Leaf schema "Leaf.celem";}')
(hidden / 'Leaf.celem').write_text('schema Hidden.Fields::Leaf {field HP single general long;}')
manifest = 'project Owned.Fields version "1" {standalone true;entry ' + n + 'Main;' + ''.join('element '+key+' '+kind+' "'+key+'.celem";' for key,(kind,text) in items.items()) + 'registry External.Fields "registered/pack.cpack";dependency External.Fields version "1";registry Hidden.Fields "hidden/pack.cpack";}'
project = root / 'project.cproj'
project.write_text(manifest)
for key,(kind,text) in items.items(): (root / (key+'.celem')).write_text(text)
(root / 'Impl.csbody').write_text('return value;')
original = {p:p.read_bytes() for p in root.rglob('*') if p.is_file()}
sha = lambda text:hashlib.sha256(text.encode()).hexdigest()
checks = 0

def check(label):
    global checks
    checks += 1
    print('PASS '+label, flush=True)

def request(id=owner):
    return dict(project=str(project), manifest=manifest, id=id, text=items[id.split('::')[1]][1], drafts=[{'id':n+key,'text':text} for key,(kind,text) in items.items() if n+key != id])

def call(operation, changes=None, ok=True, base=None, **extra):
    req = {**(base or request()), 'operation':operation, **extra}
    if changes is not None: req['changes'] = changes
    r = subprocess.run([dotnet, str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')], input=json.dumps(req), text=True, capture_output=True, timeout=60)
    assert r.returncode == 0, r.stderr
    reply = json.loads(r.stdout)
    assert reply['ok'] == ok, reply
    assert all(p.read_bytes() == raw for p,raw in original.items())
    return reply.get('result')

view = call('effective', definitionTypes=True, schemaView=True, observeSources=True)
assert view['status'] == 'available', view
catalogue = view['definitionTypes']
def choice(kind,type): return next(c for c in catalogue if c['kind']==kind and c['id']==type)
assert choice('compound','External.Fields::Leaf')['available']
assert choice('function','External.Fields::Fn')['available']
assert not any(c['id'].startswith('Hidden.Fields::') for c in catalogue)
assert choice('reference',n+'Leaf')['targets'] == [{'id':n+'Target','name':'Target'}]
assert choice('function',n+'Fn')['targets'] == [{'id':n+'Impl','name':'Impl'}]
assert all('/Impl.csbody' not in p['path'] for p in view['observations'])
check('read-only catalogue includes direct registered types and valid derived/implementation targets; hides undeclared namespace and reads no implementation body')

def shape(kind='general',type='long',cardinality='single'): return dict(kind=kind,type=type,cardinality=cardinality)
def field(name, old, new):
    return dict(type='schema-field',path=[name],contract=old,schema=n+'Local',schemaHash=sha(items['Local'][1]),definition=new,sources=None if new['kind']=='general' else choice(new['kind'],new['type'])['sources'])
def datum(name,old,value): return dict(type='data',path=[name],contract=old,valueJson=value)
single = shape()
multiple = shape(cardinality='multiple')
change = field('Value',single,multiple)
call('mixedOwnerCopyEdits',[dict(type='description',text='전체 미적용'),change],False)
converted = call('mixedOwnerCopyEdits',[change,datum('Value',single,'[9223372036854775806]')])
assert 'field Value multiple general long;' in converted['updates'][0]['text']
assert 'data Value = [9223372036854775806];' in converted['text']
assert '9223372036854775805' in converted['text'] and '9223372036854775804' in converted['text']
check('single-to-multiple requires explicit matching value in the same pure candidate and preserves exact 64-bit/nested/sibling data')
reduced = call('mixedOwnerCopyEdits',[field('Values',multiple,single),datum('Values',multiple,'9223372036854775804')])
assert 'data Values = 9223372036854775804;' in reduced['text']
peer = request()
next(d for d in peer['drafts'] if d['id']==n+'Other')['text'] = f'object {n}Other {{use schema {n}Local;data Value=5;}}'
call('mixedOwnerCopyEdits',[change,datum('Value',single,'[9223372036854775806]')],False,peer)
check('explicit multiple-to-single candidate is checked; incompatible other-owner usage rejects all changes without rewriting it')

tree = shape('compound',n+'Leaf')
ref = shape('reference',n+'Derived')
updated = call('mixedOwnerCopyEdits',[field('Tree',tree,shape('compound',n+'Leaf2')),field('Ref',ref,shape('reference',n+'Leaf'))])
assert 'compound '+n+'Leaf2' in updated['updates'][0]['text'] and 'reference '+n+'Leaf;' in updated['updates'][0]['text']
assert updated['text'] == items['A'][1]
call('mixedOwnerCopyEdits',[field('Tree',tree,shape('reference',n+'Leaf'))],False)
call('mixedOwnerCopyEdits',[field('Values',multiple,shape(type='bool',cardinality='multiple'))],False)
check('compatible compound/reference definition changes preserve inherited target and all raw object values; incompatible kind/array item changes reject')

def new(name,contract,value):
    return dict(type='typed-definition',name=name,contract=contract,sources=None if contract['kind']=='general' else choice(contract['kind'],contract['type'])['sources'],valueJson=value)
definitions=[new('Peer',shape('reference',n+'Leaf'),json.dumps({'$ref':n+'Target'})),new('Callback',shape('function',n+'Fn'),json.dumps({'$ref':n+'Impl'})),new('Registered',shape('compound','External.Fields::Leaf', 'multiple'),'[{"HP":9223372036854775803}]')]
created = call('mixedOwnerCopyEdits',definitions)
assert len(created['additions']) == 1
assert 'field Callback single function '+n+'Fn;' in created['additions'][0]['text']
assert '9223372036854775803' in created['text']
assert not created['updates']
check('new reference/function/registered multiple compound fields use one owned declaration+value candidate and never edit source/parent/registered type')
for bad in [new('Bad',shape('function',n+'Fn'),json.dumps({'$ref':n+'Target'})),new('Bad',shape('reference',n+'Leaf'),json.dumps({'$ref':n+'A'})),{**definitions[2],'sources':{}},{**definitions[2],'contract':shape('compound','Hidden.Fields::Leaf')},{**definitions[0],'name':'bad; injected'}]:
    call('mixedOwnerCopyEdits',definitions[:1]+[bad],False)
check('wrong target/signature, forged proof, undeclared imported type or injected identity reject the entire multi-field candidate')

base = request(n+'Info')
typed = [{**d,'name':'p_'+str(i),'displayName':label} for i,(d,label) in enumerate(zip(definitions,['참조 한글','함수 한글','등록 정보']))]
info = call('informationDefinitions',typed,base=base)
v = call('effective',base={**base,'text':info['text']},schemaView=True,validateObjects=True)
assert v['status']=='available',v
assert v['schemaModel']['data']['p_1']['reference']==n+'Impl'
assert v['schemaModel']['data']['p_2']['items'][0]['members']['HP']['scalar']==9223372036854775803
call('informationDefinitions',typed+[{**typed[0],'name':'p_wrong','valueJson':'{"$ref":"'+n+'A"}'}],False,base)
check('information defaults support the same typed choices/exact imported arrays and validate function association without calling it')
print(json.dumps(dict(checks=checks,evidence=str(root),pureMetadata=True,actualEngine=False,renderer=False,nativeWindows=False,accountOrInference=False)))
