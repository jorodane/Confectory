"""Declared parent context must be current before explicit Blueprint copy."""
import json
import subprocess
import v536_information_inherited_copy_fixture as x

assert x.source_kind == 'blueprint'
f = x.f
def query(ok=True):
    p = subprocess.run([f.env['CONFECTORY_DOTNET'],
        str(f.repo / 'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],
        input=json.dumps({'operation': 'implementationCopy', 'action': 'prepare',
            'project': str(f.manifest), 'feature': x.fn, 'source': x.child,
            'target': 'common', 'implementation': x.copy_id, 'owner': x.owner,
            'ownerText': x.b.info.read_text()}), text=True, capture_output=True, check=True, env=f.env)
    result = json.loads(p.stdout)
    assert bool(result['ok']) == ok, result
    return result

def compile_node(ok=True):
    p = subprocess.run([f.env['CONFECTORY_DOTNET'],
        str(f.repo / 'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],
        input=json.dumps({'operation': 'checkBlueprintNode', 'project': str(f.manifest),
            'target': 'portable', 'implementation': x.child, 'bodyTarget': 'common', 'node': 'body'}),
        text=True, capture_output=True, check=True, env=f.env)
    result = json.loads(p.stdout)
    assert bool(result['ok']) == ok, result
    return result

prepared = query()['result']
assert prepared['graph']['copySource']['bodyOrigin'] == x.parent
assert prepared['graph']['nodes'][0]['implementationContext']['implementation'] == x.copy_id
assert prepared['records'][0]['record']['source'] == x.original
f.checked('실제 부모의 whole-body 문맥을 검증한 뒤 선택한 소유 copy ID로만 결부한다')
compiled = compile_node()['result']
assert compiled['compiled'] and compiled['executed'] is False
assert all((f.project / p).read_bytes() == v for p, v in x.snapshot.items())
f.checked('같은 실제 상속 문맥은 원본 child의 compiler probe에서도 통과하고 본문을 실행하거나 다시 쓰지 않는다')
paths = [x.b.implementation_file, f.project / 'parent.graph.json', f.project / 'parent.node.json']
for path in paths:
    before = path.read_bytes()
    try:
        if path == x.b.implementation_file:
            path.write_text(path.read_text().replace('nativeAmount', 'childAlias'))
        else:
            value = json.loads(path.read_text())
            if path.name.endswith('.graph.json'):
                value['nodes'][0]['implementationContext']['implementation'] = f.n + 'ForeignContext'
            else:
                value['definitionHash'] = '0' * 64
            path.write_text(json.dumps(value))
        query(False)
        compile_node(False)
    finally:
        path.write_bytes(before)
    assert all((f.project / p).read_bytes() == v for p, v in x.snapshot.items())
f.checked('상속 child의 다른 native 별칭·위조된 문맥·오래된 부모 노드 정의는 추측 변환 없이 거절한다')
print(json.dumps({'checks': f.checks, 'evidence': str(f.case), 'pureCandidate': True,
                  'actualWindows': False}, ensure_ascii=False))
