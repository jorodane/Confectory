"""Order-aware same-owner raw/typed merge; isolated source fixture only."""
import copy
import json
import re
import subprocess
import v536_information_function_order_api as a

f, owner = a.f, a.owner
text = a.info.read_text()
checks = []


def meta(operation, ok=True, **request):
    result = subprocess.run([f.env['CONFECTORY_DOTNET'], str(f.repo / 'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')], input=json.dumps({'operation': operation, **request}), text=True, capture_output=True, env=f.env, check=True)
    value = json.loads(result.stdout)
    assert bool(value['ok']) == ok, value
    return value.get('result')


def order(source):
    return re.findall(r'contain\s+function\s+([^;\s]+)\s*;', re.sub(r'//[^\n]*', '', source))


def prepare(changes, raw=None, source=text, ok=True):
    return meta('informationDefinitions' if raw is None else 'rawOwnerEdits', ok, project=str(f.manifest), manifest=f.manifest.read_text(), id=owner, text=source, changes=changes, drafts=[], **({'rawText': raw} if raw is not None else {}))


def checked(label):
    checks.append(label)
    print('PASS ' + label, flush=True)


change = {'type': 'function-order', 'ids': a.desired}
p = prepare([change])
assert order(p['text']) == a.desired and not p['additions'] and not p['updates'] and p['manifest'] == f.manifest.read_text()
strip = lambda source: re.sub(r'contain\s+function\s+[^;]+;', '', source)
assert strip(p['text']) == strip(text)
checked('순서 후보는 기존 contain 문장만 이동하며 함수 정의·등록·다른 원문/정확한 수치를 변경하지 않는다')
for ids in [a.desired[:-1], a.desired + [a.desired[0]], [a.functions[0], a.locked[1], a.functions[1], a.locked[0], a.functions[2]], [*a.desired[:-1], 'Elsewhere::Function']]:
    prepare([{'type': 'function-order', 'ids': ids}], ok=False)
new = owner + '_Function_' + 'e' * 32
p = prepare([{'type': 'function-order', 'ids': [new, *a.desired]}, {'type': 'function-add', 'id': new, 'name': '새 기능', 'description': '원문'}])
assert order(p['text']) == [new, *a.desired] and [row['id'] for row in p['additions']] == [new]
checked('누락/중복/외부/보호 행 변경은 거절하고 같은 후보의 새 자체 기능만 명시 순서에 포함한다')
raw = text.replace('{', '{description "raw 입력 유지";', 1)
p = prepare([change], raw=raw)
assert order(p['text']) == a.desired and 'description "raw 입력 유지";' in p['text']
annotated = text.replace('contain function ' + a.functions[0] + ';', 'contain // 첫째의 주석 보존\n function ' + a.functions[0] + ';')
p = prepare([change], source=annotated)
assert order(p['text']) == a.desired and 'contain // 첫째의 주석 보존\n function ' + a.functions[0] + ';' in p['text']
checked('독립 raw 입력과 문장 내부 주석을 보존하며 함수 순서와 함께 병합한다')
def reordered(ids):
    positions = list(re.finditer(r'contain function [^;]+;', text))
    clauses = {id: 'contain function ' + id + ';' for id in a.original_order}
    result = text
    for match, id in reversed(list(zip(positions, ids))):
        result = result[:match.start()] + clauses[id] + result[match.end():]
    return result
other = [a.functions[1], a.locked[0], a.functions[0], a.locked[1], a.functions[2]]
prepare([change], raw=reordered(other), ok=False)
prepare([change], raw=text.replace('contain function ' + a.functions[1] + ';', ''), ok=False)
p = prepare([change], raw=reordered(a.desired))
assert order(p['text']) == a.desired
p = prepare([{'type': 'description', 'text': '일반 편집'}], raw=reordered(other))
assert order(p['text']) == other and meta('inspect', text=p['text'])['description'] == '일반 편집'
checked('실제 raw 순서/멤버십 경합은 전체 미적용이며 같은 선택은 허용하고 일반 편집은 raw 순서를 덮지 않는다')
f.originals()
print(json.dumps({'checks': checks, 'evidence': str(f.case), 'nativeCandidateOnly': True, 'nativeWindows': False}, ensure_ascii=False))
