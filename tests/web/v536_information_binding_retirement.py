"""Pure binding lifetime candidates over registered, isolated fixture sources."""
import copy
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import tempfile

repo = pathlib.Path(sys.argv[1]).resolve()
root = pathlib.Path(tempfile.mkdtemp(prefix='confectory-binding-retirement-'))
ns = 'Owned.Bindings::'
owner, peer = ns + 'Details', ns + 'Peer'
mode = 'information-binding-v1'
dotnet = os.environ.get('CONFECTORY_DOTNET', 'dotnet')
checks = []


def h(text):
    return hashlib.sha256(text.encode()).hexdigest()


def metadata(operation, ok=True, **request):
    result = subprocess.run([dotnet, str(repo / 'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],
                            input=json.dumps({'operation': operation, **request}), text=True, capture_output=True, check=True)
    value = json.loads(result.stdout)
    assert bool(value['ok']) == ok, value
    return value.get('result')


def fixture(owned=False, copied=False):
    function = owner + '_Function_' + 'a' * 32 if owned else ns + 'Slot'
    impl = ns + ('Impl_' + 'b' * 32 if copied else 'SharedBody')
    fntext = 'function ' + function + ' (long amount) -> long {}'
    attachment = 'contain function ' + function + ';' if owned else 'module ' + ns + 'Rules;'
    texts = {
        'Details': ('schema', 'schema ' + owner + ' extends ' + ns + 'Parent {field Power single general long;value editorInformationDefaults="typed-json-v1";value editorFieldDefault_Power="9223372036854775806";' + attachment + 'provide ' + function + ' with ' + impl + ';}'),
        'Peer': ('schema', 'schema ' + peer + ' {' + attachment.replace('contain function ' + function + ';', '') + 'provide ' + function + ' with ' + impl + ';}'),
        'Parent': ('schema', 'schema ' + ns + 'Parent {' + ('' if owned else 'module ' + ns + 'Rules;provide ' + function + ' with ' + ns + 'ParentBody;') + '}'),
        function.split('::')[1]: ('function', fntext),
        impl.split('::')[1]: ('implementation', 'implementation ' + impl + ' for ' + function + ' (long amount) -> long {body common "body.csbody";}'),
        'Main': ('function', 'function ' + ns + 'Main () -> int {provide ' + ns + 'Main with ' + ns + 'MainBody;}'),
        'MainBody': ('implementation', 'implementation ' + ns + 'MainBody for ' + ns + 'Main () -> int {body common "main.csbody";}'),
    }
    if not owned:
        texts['Rules'] = ('module', 'module ' + ns + 'Rules {require ' + function + ' (long) -> long;}')
        texts['ParentBody'] = ('implementation', 'implementation ' + ns + 'ParentBody for ' + function + ' (long amount) -> long {body common "parent.csbody";}')
    units = {}
    def add(id, kind, path, text):
        destination = root / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text)
        units[id] = {'id': id, 'kind': kind, 'path': path, 'draft': text, 'original': text, 'baseline': h(text), 'revision': 1}
    for local, (kind, text) in texts.items():
        add(ns + local, kind, 'elements/' + local + '.celem' if owned and ns + local == function else local + '.celem', text)
    add(impl + '/body:common', 'body', 'body.csbody', 'return amount + 3; // retained 한글')
    add(ns + 'MainBody/body:common', 'body', 'main.csbody', 'return 0;')
    if not owned:
        add(ns + 'ParentBody/body:common', 'body', 'parent.csbody', 'return amount + 10;')
    manifest = 'project Owned.Bindings version "1" {entry ' + ns + 'Main;' + ''.join('element ' + key.split('::')[1] + ' ' + unit['kind'] + ' "' + unit['path'] + '";' for key, unit in units.items() if '/body:' not in key) + '}'
    add(ns + 'ProjectManifest', 'project', 'project.cproj', manifest)
    if copied:
        units[impl]['creationOwner'] = owner
        units[impl]['copySource'] = {'id': ns + 'ParentBody', 'target': 'common', 'fingerprint': 'c' * 64}
    return units, function, impl


def run(action, units, ok=True, **request):
    return metadata('informationFunctionRetirement', ok, action=action, project=str(root / 'project.cproj'),
                    namespace='Owned.Bindings', scope={'participant': 'fixture-user', 'context': 'editor'},
                    units=units, retirements=request.pop('retirements', {}), **request)


def checked(label):
    checks.append(label)
    print('PASS ' + label, flush=True)


for owned, copied in [(False, False), (False, True), (True, False)]:
    units, function, impl = fixture(owned, copied)
    original = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}
    request = {'owner': owner, 'function': function, 'ownerHash': h(units[owner]['draft']), 'checkpointHash': 'd' * 64}
    if owned:
        request.update(mode='implementation-only-v1', functionHash=h(units[function]['draft']))
    else:
        request.update(mode=mode, implementation=impl)
    plan = run('plan', units, **request)
    assert plan['mode'] == mode and not plan['ids'] and not plan['entries'] and not plan['references']
    assert 'provide ' + function not in plan['ownerAfter'] and plan['afterManifest'] == units[ns + 'ProjectManifest']['draft']
    assert plan['binding']['provider']['origin'] == owner
    assert impl in plan['binding']['retained'] and impl + '/body:common' in plan['binding']['retained']
    applied = run('apply', units, evidence=plan)
    receipt = applied['retirements'][plan['token']]
    assert set(applied['units']) == set(units)
    assert all(applied['units'][id] == unit for id, unit in units.items() if id not in [owner, ns + 'ProjectManifest'])
    run('validate', applied['units'], receipt=receipt)
    if not owned:
        # Only local provide disappears; the parent's effective provider survives.
        run('plan', applied['units'], False, **{**request, 'ownerHash': h(applied['units'][owner]['draft'])})
    recovered = run('recover', applied['units'], retirements=applied['retirements'], evidence=receipt)
    assert not recovered['retirements'] and recovered['units'][owner]['draft'] == units[owner]['draft']
    assert original == {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}
    checked(('공유 자체 함수' if owned else '저장 copy' if copied else '공유/상속 슬롯') + '는 소유 연결만 보관/복구하고 선언·등록·모든 구현/본문·다른 사용처를 보존한다')
    for field in ['mode', 'ownerAfter', 'implementation']:
        forged = copy.deepcopy(receipt)
        forged[field] = 'unknown' if field != 'ownerAfter' else forged[field] + '\n// forged operation'
        run('validate', applied['units'], False, receipt=forged)
    wrong = copy.deepcopy(units)
    wrong[owner]['draft'] += '\n// peer draft'
    run('apply', wrong, False, evidence=plan)
    assert wrong[owner]['draft'].endswith('// peer draft')
    checked('알 수 없는 수명·변조된 연결/원문·동시 입력은 보관/복구 후보에 채택하지 않는다')
    # Simulate only the existing explicit compiler acceptance of this pure candidate.
    confirmed = copy.deepcopy(applied)
    receipt = confirmed['retirements'][plan['token']]
    receipt['state'] = 'confirmed'
    for id in [owner, ns + 'ProjectManifest']:
        unit = confirmed['units'][id]
        (root / unit['path']).write_text(unit['draft'])
        unit.update(original=unit['draft'], baseline=h(unit['draft']))
        unit.pop('retirementGroup', None)
    run('validate', confirmed['units'], receipt=receipt)
    restored = run('recover', confirmed['units'], retirements=confirmed['retirements'], evidence=receipt)
    cancelled = run('cancel', restored['units'], retirements=restored['retirements'], evidence=restored['retirements'][plan['token']])
    assert cancelled['units'][owner]['draft'] == confirmed['units'][owner]['draft'] and cancelled['retirements'][plan['token']]['state'] == 'confirmed'
    newer = copy.deepcopy(confirmed['units'])
    newer[owner]['draft'] = newer[owner]['draft'].replace('}', 'provide ' + function + ' with ' + ns + 'ParentBody;}', 1)
    run('recover', newer, False, retirements=confirmed['retirements'], evidence=receipt)
    changed = copy.deepcopy(confirmed['units'])
    changed[impl + '/body:common']['draft'] += '\n// newer provider input'
    run('validate', changed, receipt=receipt)  # stale archive stays readable
    run('recover', changed, False, retirements=confirmed['retirements'], evidence=receipt)
    assert changed[impl + '/body:common']['draft'].endswith('// newer provider input')
    checked('확정 복구/복구 취소를 분리하고 새 provider·바뀐 본문을 이전 기록으로 덮어쓰지 않는다')

print(json.dumps({'checks': checks, 'evidence': str(root), 'nativeCandidateOnly': True, 'actualCompilerConfirm': False}, ensure_ascii=False))
