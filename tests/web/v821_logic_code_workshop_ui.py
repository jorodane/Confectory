"""Run the supported Logic Code edits together in one local project and process."""
import ast
import hashlib
import json
import subprocess
from pathlib import Path
from types import SimpleNamespace
import uuid

from playwright.sync_api import expect, sync_playwright

import v536_wide_mixed as f

t = SimpleNamespace(feature=None)
ns = f.n
project = f.project
manifest = project / 'project.cproj'
units = {}
bodies = {}
model = 'Confectory.ObjectModel'

for file, selected in [
    ('v821_function_document_ui.py', {'panel', 'doc', 'pending', 'open_document', 'restart', 'review'}),
    ('v821_document_call_first_branch_ui.py', {'edit_body'}),
    ('v821_document_async_ui.py', {'mode', 'toggle', 'choose_completion'}),
]:
    path = Path(__file__).with_name(file)
    names = [item for item in ast.parse(path.read_text()).body
             if isinstance(item, ast.FunctionDef) and item.name in selected]
    exec(compile(ast.Module(body=names, type_ignores=[]), str(path), 'exec'), globals())


def write(filename, text):
    path = project / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text if isinstance(text, str) else json.dumps(text, ensure_ascii=False))


def item(name, kind, text):
    units[name] = (kind, text)
    write(name+'.celem', text)


def declare(name, signature, metadata=''):
    return f'function {ns}{name} {signature} {{{metadata}provide {ns}{name} with {ns}{name}Body;}}'


def native(name, signature, source, imports='', metadata=''):
    item(name, 'function', declare(name, signature, metadata))
    item(name+'Body', 'implementation',
         f'implementation {ns}{name}Body for {ns}{name} {signature} {{{imports}body common "{name}.csbody";}}')
    write(name+'.csbody', source)


def sig(args=(), result='void'):
    return dict(args=list(args), **{'return': result})


def arg(name, type_='int', mode=None):
    return dict(name=name, type=type_, **({'mode': mode} if mode else {}))


def use(name):
    return {'input': name}


def value(node, output='return'):
    return dict(node=node, output=output)


def edge(start, end, port='next'):
    return {'from': start, 'to': end, 'port': port}


def code(name, id_, source, args=(), bindings=None, result='void', owner=None, enum=None):
    path = f'{name}.{id_}.node.json'
    bodies[path] = source
    return dict(id=id_, kind='code', intent=id_, control='switch' if enum else 'next',
                signature=sig(args, result), arguments=bindings or {}, implementation=path,
                **({'branchOwner': owner} if owner else {}), **({'executionEnum': enum} if enum else {}))


def enum(*extra):
    return {'primary': 'next', 'members': [{'id': 'next', 'name': 'Continue', 'value': 0}]
            + [dict(id=id_, name=id_.capitalize(), value=index) for index, id_ in enumerate(extra, 1)]}


def start_graph(name, signature):
    item(name, 'function', declare(name, signature))
    prepared = f.metadata('blueprintPrepareFeature', id=ns+name, text=f'function {ns}{name} {signature} {{}}',
                          implementation=ns+name+'Body', graphPath=name+'.graph.json', nodePath=name+'.node.json')
    return prepared['graph'], prepared['implementation']


def call(name, target, graph, implementation, id_, bindings):
    prepared = f.metadata('blueprintPrepareCall', id=ns+name+'Body', text=implementation,
                          targetText=units[target][1], graph=graph,
                          definition=dict(id=id_, feature=ns+target, intent=id_, control='next'))
    row = next(row for row in prepared['graph']['nodes'] if row['id'] == id_)
    row['arguments'] = bindings
    return row, prepared['implementation']


def save_fixture_graph(name, graph, implementation):
    item(name+'Body', 'implementation', implementation)
    write(name+'.graph.json', graph)


def setup():
    item('WorkshopSchema', 'schema', f'schema {ns}WorkshopSchema {{field metric single general long;}}')
    item('WorkshopObject', 'object', f'object {ns}WorkshopObject {{use schema {ns}WorkshopSchema;}}')
    native('WorkshopNative', '(int input, out int audit) -> int',
           'audit=input*10;return input+3;', metadata='value blueprintPublishedOutputs = "[\\"return\\",\\"audit\\"]";')

    calc, impl = start_graph('Calc', '(object target) -> long')
    calc.update(profile='sync-acyclic-methods-v1', entry='mark',
                nodes=[code('Calc', 'mark', 'System.Console.WriteLine("property:mark");'),
                       code('Calc', 'consume', 'result=metric;', [arg('metric', 'long'), arg('result', 'long', 'out')],
                            {'metric': {'constant': 2}})],
                edges=[edge('mark', 'consume'), edge('consume', 'exit:return')],
                exits={'return': value('consume', 'result')})
    save_fixture_graph('Calc', calc, impl)

    pair, impl = start_graph('Pair', '(int amount) -> int')
    imported, impl = call('Pair', 'WorkshopNative', pair, impl, 'native', {'input': use('amount')})
    pair.update(profile='sync-acyclic-switch-v1', entry='routing',
                nodes=[
                    code('Pair', 'routing', 'return Result.Alternate;', enum=enum('alternate')),
                    code('Pair', 'onAlternate', 'System.Console.WriteLine("m11:alternate");', owner='routing'),
                    imported,
                    code('Pair', 'auditLog', 'System.Console.WriteLine("out:"+audit);', [arg('audit')],
                         {'audit': value('native', 'audit')}),
                ],
                edges=[edge('routing', 'native'), edge('routing', 'onAlternate', 'case:alternate'),
                       edge('onAlternate', 'return:routing'), edge('native', 'auditLog'), edge('auditLog', 'exit:return')],
                exits={'return': value('native')})
    save_fixture_graph('Pair', pair, impl)

    probe_imports = (f'import {ns}Pair as Pair (int) -> int;import {ns}Calc as Calc (object) -> long;'
                     f'import {model}::Create as Create (string,string[],object[]) -> object;')
    native('Probe', '() -> int', 'return 0;', probe_imports)
    main, impl = start_graph('Main', '() -> int')
    # Keep this switch within existing owned-code reconnection. The final
    # ordinary C# cell invokes the test harness via its declared import.
    probe_alias = 'fg_call_'+hashlib.sha256((ns+'Probe').encode()).hexdigest()[:24]
    impl = impl.replace('{', '{'+f'import {ns}Probe as {probe_alias} () -> int;', 1)
    probe = code('Main', 'probe', f'return {probe_alias}.Invoke();', result='int')
    probe['imports'] = [ns+'Probe']
    main.update(profile='sync-acyclic-switch-v1', entry='choose',
                nodes=[
                    code('Main', 'choose', 'return Result.Positive;', enum=enum('positive', 'negative')),
                    code('Main', 'positive', 'System.Console.WriteLine("case:restored");', owner='choose'),
                    code('Main', 'negative', 'System.Console.WriteLine("case:negative");', owner='choose'),
                    code('Main', 'work', 'result=12;return Result.Continue;', [arg('result', 'int', 'out')], enum=enum()),
                    code('Main', 'completed', 'System.Console.WriteLine("completion:"+item);',
                         [arg('item')], {'item': value('work', 'result')}, owner='work'),
                    probe,
                ],
                edges=[edge('choose', 'work'), edge('choose', 'return:choose', 'case:positive'),
                       edge('positive', 'return:choose'), edge('choose', 'negative', 'case:negative'),
                       edge('negative', 'return:choose'), edge('work', 'probe'), edge('completed', 'return:work'),
                       edge('probe', 'exit:return')],
                exits={'return': value('probe')})
    save_fixture_graph('Main', main, impl)

    write('project.cproj', f'project {ns[:-2]} version "1" {{standalone true;entry {ns}Main;'
          + ''.join(f'element {name} {kind} "{name}.celem";' for name, (kind, _) in units.items())
          + f'registry Confectory.Build.DotNet "{f.repo}/targets/dotnet/pack.cpack";'
          + f'dependency Confectory.Build.DotNet version "0.1.0";registry {model} "{f.repo}/packs/object-model/pack.cpack";'
          + f'dependency {model} version "0.1.0";target portable Confectory.Build.DotNet::Portable;}}')
    descriptor = f.metadata('blueprintPropertyCatalog', project=str(manifest), sourceId=ns+'CalcBody',
                            owner=ns+'WorkshopObject')['descriptor']
    field_id = next(row['id'] for row in descriptor['fields'] if row['name']=='metric')
    write('Probe.csbody', 'object target=calls.Create.Invoke('
          + json.dumps(json.dumps(descriptor, separators=(',', ':'))) + ',new[]{' + json.dumps(field_id)
          + '},new object[]{73L});System.Console.WriteLine("calc:"+calls.Calc.Invoke(target));'
          + 'foreach(int amount in new[]{5,8})System.Console.WriteLine("pair:"+calls.Pair.Invoke(amount));return 7;')

    for name, graph in [('Calc', calc), ('Pair', pair), ('Main', main)]:
        defs = f.metadata('blueprintDescribeOwned', project=str(manifest), id=ns+name+'Body',
                          text=units[name+'Body'][1], bodyTarget='common', graph=graph, definitionsOnly=True)
        assert defs['state'] == 'node-definitions', defs
        for cell in graph['nodes']:
            if cell['kind']!='code':
                continue
            digest = next(row['definitionHash'] for row in defs['nodes'] if row['id']==cell['id'])
            write(cell['implementation'], dict(schema=1, node=cell['id'], definitionHash=digest,
                                               source=bodies[cell['implementation']]))
    # Prepare an already supported M11 internal body before opening the editor.
    # All author actions below use the product's Logic Code controls.
    exits = dict(entry='body', exits={'shared': {'executionBranch': 'alternate'}},
                 edges=[edge('body', 'exit:shared'), edge('body', 'exit:shared', 'case:alternate')])
    wrapped = f.metadata('blueprintNodeFlow', id=graph_id('Pair'), node='routing', nonce=uuid.uuid4().hex,
                         record=(project/'Pair.routing.node.json').read_text(), graph=pair, executionExits=exits,
                         ownerRequest=dict(project=str(manifest), id=ns+'PairBody', text=units['PairBody'][1],
                                           bodyTarget='common'))
    write('Pair.graph.json', wrapped['graph'])
    write(wrapped['path'], wrapped['record'])


def graph_id(name):
    return ns+name+'Body/body:common'


def graph(name):
    return json.loads((project/(name+'.graph.json')).read_text())


def snapshot():
    return {path: path.read_bytes() for path in project.rglob('*')
            if path.is_file() and '.confectory' not in path.parts}


def unchanged(snapshot_, allowed=(), reserialized=()):
    for path, original in snapshot_.items():
        if path.name in allowed:
            continue
        actual = path.read_bytes()
        if path.name in reserialized:
            assert json.loads(actual) == json.loads(original), path
        else:
            assert actual == original, path


def open_feature(name):
    f.close_author()
    t.feature = ns+name
    open_document()
    logic()


def logic():
    expect(panel().get_by_role('tab', name='논리 코드', exact=True)).to_have_attribute('aria-selected', 'true')


def save_now():
    logic()
    panel().locator('[data-bp-save]').click()
    expect(panel().locator('.bp-status')).to_have_text('저장됨', timeout=120000)
    assert not pending()


def confirm_after_restart(number):
    restart(number)
    logic()
    before = snapshot()
    review().locator('[data-reject]').click()
    unchanged(before)
    dialog = review()
    expect(dialog.locator('#confirm')).to_be_enabled()
    dialog.locator('#confirm').click()
    expect(dialog).to_be_hidden(timeout=120000)
    f.idle()


def source(id_, text):
    doc().locator(f'[data-document-code="{id_}"]').click()
    editor = f.page.locator('.bp-script-dialog')
    edit_body(editor, text)
    editor.locator('[data-code-save]').click()
    expect(editor).to_be_hidden()


def select_case(id_, port):
    doc().locator(f'[data-document-branch="{port}"][data-document-owner="{id_}"]').click()
    return doc().locator(f'[data-document-cell="{id_}"] [data-document-panel="{port}"]')


def calculation():
    open_feature('Calc')
    initial = snapshot()
    doc().locator('[data-document-contract=consume]').click()
    doc().locator('[data-document-contract-side=inputs] [data-mobile-contract-add]').click()
    field = doc().locator('[data-mobile-contract-field=input1]')
    field.locator('[data-signature-type]').click()
    f.page.get_by_role('dialog', name='속성 타입 선택').locator('[data-type=long]').click()
    out_name = doc().locator('[data-mobile-contract-field=result] input')
    out_name.fill('produced')
    out_name.press('Enter')
    doc().locator('[data-document-value=consume][data-document-port="field:input1"]').click()
    search = f.page.get_by_role('dialog', name='핀 값 선택').get_by_role('searchbox', name='값 검색')
    search.fill('19')
    search.press('Enter')
    source('consume', 'produced=metric+input1;')
    save_now()
    confirm_after_restart(1)
    unchanged(initial, {'Calc.graph.json','Calc.consume.node.json'})
    assert graph('Calc')['exits']['return']==value('consume','produced')

    doc().locator('[data-document-add=mark]').click()
    f.page.get_by_role('dialog', name='다음 세부기능 추가').get_by_role('button', name='속성 읽기', exact=True).click()
    picker = f.page.get_by_role('dialog', name='속성 읽기 연결')
    picker.locator('[data-property-receiver]').select_option('target')
    picker.locator('[data-property-owner]').select_option(ns+'WorkshopObject')
    picker.locator('[data-property-field]').select_option('metric')
    expect(picker.locator('[data-property-connect]')).to_be_disabled()
    picker.locator('[data-property-consumer]').select_option('metric')
    picker.locator('[data-property-connect]').click()
    save_now()
    confirm_after_restart(2)
    f.checked('Same Calc document saved the out contract/value, then an explicit object/field/consumer property read, via cold Review/Confirm.')


def calls_and_returns():
    open_feature('Pair')
    doc().locator('[data-document-internal=routing]').click()
    select_case('body','case:alternate').locator('[data-document-branch-return]').click()
    f.page.get_by_role('dialog', name='다음 세부기능 추가').get_by_role('button', name='기본 기능', exact=True).click()
    f.page.get_by_role('dialog', name='기본 기능').get_by_role('button', name='분기 반환', exact=True).click()
    f.page.get_by_role('listbox', name='새 분기 반환 선택').locator('[data-branch-option=next]').click()
    save_now()
    confirm_after_restart(3)
    assert len(graph('Pair')['nodes'][0]['graph']['exits'])==2
    panel().locator('.bp-breadcrumbs button').first.click()
    f.idle()

    doc().locator('[data-document-call-first-branch=native]').click()
    editor = f.page.locator('.bp-script-dialog')
    edit_body(editor, 'return context.@return > 10 ? Result.분기1 : Result.NoBranch;')
    editor.locator('[data-code-save]').click()
    save_now()
    confirm_after_restart(4)
    original = graph('Pair')
    wrapped = next(row for row in original['nodes'] if row['id']=='native')
    case = next(row for row in wrapped['executionEnum']['members'] if row['id']!='next')
    port = 'case:'+case['id']
    f.invoke('select', {'id': ns+'WorkshopNative'})
    f.invoke('inspectDeclaration', {'id': ns+'WorkshopNative'})
    declaration = f.state()['declaration']
    f.invoke('editMetadata', dict(id=ns+'WorkshopNative', revision=declaration['revision'],
                                  hash=declaration['textHash'], field='blueprintPublishedOutputs', value='["return"]'))
    f.invoke('saveDraft', {})
    open_feature('Pair')
    branch = select_case('native',port)
    expect(branch.locator('[data-document-branch-add]')).to_be_disabled()
    doc().locator('[data-document-call-refresh=native]').click()
    save_now()
    branch.locator('[data-document-branch-add]').click()
    created, = [row['node'] for _, row in pending() if row['type']=='create']
    source(created, 'System.Console.WriteLine("wrapper:hit");')
    save_now()
    confirm_after_restart(5)
    actual = graph('Pair')
    assert actual['nodes'][:2] == original['nodes'][:2]
    assert actual['exits'] == original['exits']
    assert edge('native', created, port) in actual['edges']
    assert edge(created, 'return:native') in actual['edges']
    f.checked('Same Pair kept the M11 return, then refreshed an imported contract and wired its first branch without switching editor surfaces.')


def workflow():
    open_feature('Main')
    before = graph('Main')
    select_case('choose', 'case:positive').locator('[data-document-branch-target]').click()
    dialog = f.page.get_by_role('dialog', name='분기 실행 대상 선택')
    dialog.locator('[data-document-route-choice]').select_option('positive')
    dialog.locator('[data-route-apply]').click()
    save_now()
    confirm_after_restart(6)
    toggle('$entry')
    toggle('work')
    save_now()
    restart(7)
    choose_completion()
    save_now()
    confirm_after_restart(8)
    source('work','System.Console.WriteLine("task:start");await global::System.Threading.Tasks.Task.Yield();'
                  'result=12;System.Console.WriteLine("task:done");return Result.Continue;')
    save_now()
    confirm_after_restart(9)
    after = graph('Main')
    assert after['exits'] == before['exits']
    assert [row for row in after['nodes'] if row['id'] != 'work'] == [
        row for row in before['nodes'] if row['id'] != 'work']
    expected_edges = [row for row in before['edges'] if row != edge('choose', 'return:choose', 'case:positive')]
    expected_edges.extend([edge('choose', 'positive', 'case:positive'), edge('work', 'completed', 'completion')])
    assert len(after['edges']) == len(expected_edges) and all(row in after['edges'] for row in expected_edges)
    f.checked('Same Main restored a declared branch before applying explicit Task conversion and the existing completion port.')


def execute(label, expected):
    build = subprocess.run([f.env['CONFECTORY_DOTNET'],
                            str(f.repo/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),
                            'build', str(manifest), 'portable'], capture_output=True, text=True, env=f.env)
    (f.case/(label+'-build.log')).write_text(build.stdout+build.stderr)
    assert build.returncode==0, build.stdout[-4000:]+build.stderr[-4000:]
    run = subprocess.run(json.loads(build.stdout)['run'], capture_output=True, text=True, env=f.env)
    (f.case/(label+'-run.txt')).write_text(run.stdout)
    assert (run.returncode,run.stdout.splitlines()) == (7,expected), (run.returncode,run.stdout,run.stderr)


try:
    setup()
    initial = snapshot()
    execute('workshop-before', [
        'property:mark','calc:2','m11:alternate','out:50','pair:8','m11:alternate','out:80','pair:11',
    ])
    f.start(0)
    f.invoke('select', {'id': ns+'Calc'})
    f.invoke('saveDraft', {})
    with sync_playwright() as pw:
        expect.set_options(timeout=30000)
        f.browser = pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        f.page = f.setup()
        f.page.set_viewport_size({'width': 1800, 'height': 1400})
        calculation()
        calls_and_returns()
        workflow()
        assert json.loads(next(project.glob('.confectory/edit-workspaces/*/draft.json')).read_text())['version']==1
        # Async conversion serializes Main's owned records again. Require exact
        # record content (including C# and hashes) for its other cells.
        unchanged(initial, allowed={'Calc.graph.json','Calc.consume.node.json','CalcBody.celem',
                                   'Pair.graph.json','WorkshopNative.celem','Main.graph.json','Main.celem','Main.work.node.json'},
                  reserialized={'Main.choose.node.json','Main.positive.node.json','Main.negative.node.json',
                                'Main.completed.node.json','Main.probe.node.json'})
        execute('workshop-after', [
            'case:restored','task:start','task:done','completion:12','property:mark','calc:92',
            'out:50','pair:8','wrapper:hit','out:80','pair:11',
        ])
        assert not f.errors and not f.external, (f.errors,f.external)
        f.checked('One real .NET execution observes all three saved functions and the untouched default, sibling and output behavior.')
        f.browser.close()
finally:
    f.stop()
    print('Evidence:',f.case,flush=True)
