"""Owned inherited implementation; every source lives in a temporary fixture."""
import json
import v536_information_whole_body_fixture as b

f, d, n, owner, fn, mode = b.f, b.d, b.n, b.owner, b.fn, b.mode
imported_copy = __import__('os').environ.get('CONFECTORY_COPY_IMPORTS') == '1'
if imported_copy:
    # Existing typed imports and native parameter aliases, not a new callable
    # contract. The registered declaration/body are always read-only donors.
    foreign = 'External.Fields::Echo'
    registered = f.project / 'registered'
    pack = registered / 'pack.cpack'
    pack.write_text(pack.read_text().replace('}', 'element Echo function "Echo.celem";element EchoBody implementation "EchoBody.celem";}'))
    (registered / 'Echo.celem').write_text('function ' + foreign + ' (long foreignInput) -> long {provide ' + foreign + ' with ' + foreign + 'Body;}')
    (registered / 'EchoBody.celem').write_text('implementation ' + foreign + 'Body for ' + foreign + ' (long externalValue) -> long {body common "Echo.csbody";}')
    (registered / 'Echo.csbody').write_text('return checked(externalValue+3); // 외부 원문 · 9223372036854775806\r\n')
    b.cpp = b.cpp.replace('{body common', '{import ' + foreign + ' as ForeignEcho (long) -> long;body common')
    b.original = 'nativeTotal=checked(calls.ForeignEcho.Invoke(nativeAmount)+1);return nativeTotal; // 원래 별칭 · 9223372036854775806\r\n'
    (f.project / 'whole-original.csbody').write_bytes(b.original.encode())
child = fn + 'Body'
parent = fn + 'ParentBody'
parent_path = parent.split('::')[1] + '.celem'
(f.project / parent_path).write_text(b.cpp.replace(child, parent, 1))
b.implementation_file.write_text(
    'implementation ' + child + ' for ' + fn +
    ' (long nativeAmount,out long nativeTotal) -> long extends ' + parent +
    ' {description "상속 구현 · 부모 보존";}')
f.manifest.write_text(f.manifest.read_text().replace(
    'registry Confectory.Build.DotNet',
    'element ' + parent.split('::')[1] + ' implementation "' + parent_path +
    '";registry Confectory.Build.DotNet', 1))
copy_id = f.n + 'OwnedInheritedCopy'
original = b.original
edited = original.replace('원래 별칭', '소유한 상속 복사본 😀')
source_kind = 'csharp'
body_observations = {'whole-original.csbody'}
if 'blueprint-parent' in __import__('sys').argv[4:]:
    converted = f.metadata('blueprintConversion', project=str(f.manifest), id=parent,
                           text=(f.project / parent_path).read_text(), target='common',
                           graphPath='parent.graph.json', nodePath='parent.node.json')
    if 'serial-extra' in __import__('sys').argv[4:]:
        graph = converted['graph']
        writer = next(node for node in graph['nodes'] if node['kind'] == 'export')
        graph['nodes'].insert(1, {'id': 'extra', 'kind': 'code', 'control': 'next',
            'intent': '원본 추가 동작', 'signature': {'args': [{'name': 'value', 'type': 'long'}], 'return': 'long'},
            'arguments': {'value': {'node': 'body'}}, 'implementation': 'parent.extra.node.json'})
        writer['arguments']['value'] = {'node': 'extra'}
        graph['edges'] = [{'from': 'body', 'port': 'next', 'to': 'extra'},
                          {'from': 'extra', 'port': 'next', 'to': writer['id']}]
        definitions = f.metadata('featureBlueprintNodes', featureSource=b.function_file.read_text(),
                                  implementationContext=graph['nodes'][0]['implementationContext'], graph=graph)
        converted['node']['definitionHash'] = next(row['definitionHash'] for row in definitions['nodes'] if row['id'] == 'body')
        extra = {'schema': 1, 'node': 'extra', 'source': 'return value + 1; // 원본 추가 동작',
                 'definitionHash': next(row['definitionHash'] for row in definitions['nodes'] if row['id'] == 'extra')}
        (f.project / 'parent.extra.node.json').write_text(json.dumps(extra))
    (f.project / parent_path).write_text(converted['implementation'])
    (f.project / 'parent.graph.json').write_text(json.dumps(converted['graph']))
    (f.project / 'parent.node.json').write_text(json.dumps(converted['node']))
    source_kind = 'blueprint'
    body_observations = {'parent.graph.json', 'parent.node.json'}
    if 'serial-extra' in __import__('sys').argv[4:]:
        body_observations.add('parent.extra.node.json')
snapshot = {str(p.relative_to(f.project)): p.read_bytes()
            for p in f.project.rglob('*') if p.is_file()
            and '.confectory' not in p.relative_to(f.project).parts}
f.original = dict(snapshot)

def original_sources():
    assert all((f.project / p).read_bytes() == v for p, v in snapshot.items()
               if p not in ['FreeInfo.celem', 'project.cproj'])

def schema():
    f.invoke('schema', {'id': owner})
    return f.state()['schema']

def rpc(action, ok=True, **body):
    return f.invoke('blueprint', {'action': action, **body}, ok)['result'].get('result')

def prepare():
    s = schema()
    return rpc('readImplementationCopy', id=owner, function=fn, source=child,
               target='common', implementation=copy_id,
               revision=s['revision'], hash=s['textHash'])

def copy_row(prepared, text=edited):
    return {'function': fn, 'implementation': copy_id, 'copySource': child,
            'copyTarget': 'common', 'basis': prepared['basis'],
            'edits': [{'type': 'source', 'node': 'body', 'text': text}]}


def imported_copy_contract(rows, implementation):
    if not imported_copy:
        return
    graph = json.loads(rows[implementation + '/body:common']['draft'])
    context = next(node['implementationContext'] for node in graph['nodes']
                   if node.get('implementationContext'))
    assert context['signature'] == b.native
    assert context['imports'] == {'ForeignEcho': {'feature': foreign, 'scope': None,
           'signature': {'args': [{'name': 'arg0', 'type': 'long'}], 'return': 'long'}}}
    if implementation in rows:
        text = rows[implementation]['draft']
    else:
        # An unchanged confirmed header need not be exported as a dirty unit.
        # Read its real locator instead of inventing a pending creation member.
        header = next(row for row in f.metadata('describe', project=str(f.manifest))['units']
                      if row['id'] == implementation and row['kind'] == 'implementation')
        text = (f.project / header['path']).read_bytes().decode('utf-8-sig')
    assert 'import ' + foreign + ' as ForeignEcho (long) -> long;' in text
    record = rows[implementation + '/body:common/node:body']
    assert 'calls.ForeignEcho.Invoke(nativeAmount)' in json.loads(record['draft'])['source']
    original_sources()
