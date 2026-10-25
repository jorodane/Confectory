"""Unselected local call contracts used by two opaque C# nodes and their caller."""
import copy
import hashlib
import json
import v536_information_shared_return_types_fixture as base

f, d, n, owner, mode = base.f, base.d, base.n, base.owner, base.mode
functions, old, nexts = base.functions, base.old, base.nexts
new, removed, added = base.new, base.removed, base.added
destination, binding = base.destination, base.binding
stable = f.n + 'StableHelper'
stable_signature = {'args': [{'name': 'value', 'type': 'long'}], 'return': 'long'}
stable_source = 'function ' + stable + ' (long value) -> long {description "선택하지 않은 로컬 계약";provide ' + stable + ' with ' + stable + 'Body;}'
stable_body = 'return checked(value+7); // 선택하지 않은 본문 · 한글 😀\r\n'
for name, kind, source in [
    ('StableHelper', 'function', stable_source),
    ('StableHelperBody', 'implementation', 'implementation ' + stable + 'Body for ' + stable + ' (long value) -> long {body common "stable-helper.csbody";}'),
]:
    (f.project / (name + '.celem')).write_text(source)
    f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet',
        'element ' + name + ' ' + kind + ' "' + name + '.celem";registry Confectory.Build.DotNet', 1))
(f.project / 'stable-helper.csbody').write_bytes(stable_body.encode())
alias = 'fg_call_' + hashlib.sha256(stable.encode()).hexdigest()[:24]
graphs, records = base.graphs, base.records
for index, fn in enumerate(functions):
    path = f.project / (fn.split('::')[1] + 'Body.celem')
    path.write_text(path.read_text().replace('{', '{import ' + stable + ' as ' + alias + ' (long) -> long;', 1))
    node = next(row for row in graphs[fn]['nodes'] if row['kind'] == 'code')
    node['imports'] = [stable]
    definitions = f.metadata('featureBlueprintNodes', featureSource=(f.project / ('elements/' + fn.split('::')[1] + '.celem')).read_text(),
                             graph=graphs[fn], featureContracts={stable: stable_source})
    records[fn].update(definitionHash=next(row['definitionHash'] for row in definitions['nodes'] if row['id'] == 'body'),
        source='count=checked(' + alias + '.Invoke(amount)+' + str(index+1) + ');return amount; // opaque 원문 · 9223372036854775806')
    prefix = 'function' if index == 0 else 'second'
    (f.project / (prefix + '.graph.json')).write_text(json.dumps(graphs[fn]))
    (f.project / (prefix + '.node.json')).write_text(json.dumps(records[fn]))

graph = base.graph
linked = f.metadata('blueprintPrepareCall', id=n.caller+'Body', text=(f.project / 'CallerBody.celem').read_text(),
    targetText=stable_source, graph=graph,
    definition={'id': 'keep_local', 'feature': stable, 'intent': '선택 밖 호출의 식별자·입력 보존', 'control': 'next'})
graph.clear()
graph.update(linked['graph'])
graph['nodes'][-1]['arguments'] = {'value': {'node': 'invoke_second'}}
graph['edges'] = [{'from': 'invoke', 'port': 'next', 'to': 'invoke_second'},
                  {'from': 'invoke_second', 'port': 'next', 'to': 'keep_local'},
                  {'from': 'keep_local', 'port': 'next', 'to': 'exit:return'}]
(f.project / 'CallerBody.celem').write_text(linked['implementation'])
(f.project / 'caller.graph.json').write_text(json.dumps(graph))
snapshot = {str(p.relative_to(f.project)): p.read_bytes() for p in f.project.rglob('*')
            if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}
base.snapshot = snapshot
request = base.request


def unchanged():
    base.unchanged()


def verify_rows(rows):
    base.verify_rows(rows)
    shared = json.loads(rows[n.caller+'Body/body:common']['draft'])
    held = copy.deepcopy(graph['nodes'][-1])
    held['arguments'] = {'value': binding('invoke_second', destination)}
    assert shared['nodes'][-1] == held
    assert len(shared['nodes']) == 3
    for fn in functions:
        header = f.metadata('inspect', text=rows[fn+'Body']['draft'])
        assert any(r['role'] == 'import' and r['target'] == stable for r in header['relations']['edges'])
        node = next(row for row in json.loads(rows[fn+'Body/body:common']['draft'])['nodes'] if row['kind'] == 'code')
        assert node['imports'] == [stable]
    for path in ['StableHelper.celem', 'StableHelperBody.celem', 'stable-helper.csbody']:
        assert (f.project / path).read_bytes() == snapshot[path]


def verify(checkpoint):
    group = base.verify(checkpoint)
    rows = {row['id']: row for row in json.loads(checkpoint.read_text())['changes']}
    verify_rows(rows)
    assert not {stable, stable+'Body', stable+'Body/body:common'} & set(group)
    return group


def verify_live():
    units = f.metadata('describe', project=str(f.manifest))['units']
    verify_rows({row['id']: {'draft': (f.project / row['path']).read_text()} for row in units})
