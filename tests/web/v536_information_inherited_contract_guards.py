"""Renaming public pins never grants parent writes or a new native ABI."""
import copy
import json
import v536_information_inherited_contract_fixture as x

r = x.request()
prepared = x.n.prepare(r)
assert all(row['id'] not in [x.parent, x.child] for row in prepared['linkedUpdates'])
x.unchanged()
x.f.checked('공개 이름 대응·소유 copy·호출자 후보는 부모/자식 선언을 쓰지 않고 함께 준비한다')
for fault in ['parent-source', 'child-source', 'type', 'role', 'return', 'reorder']:
    bad = copy.deepcopy(r)
    change = bad['changes'][0]
    mapping = change['mapping']
    if fault == 'parent-source':
        mapping['bodies'][x.donor_id]['text'] += '// not authorized parent edit\n'
    elif fault == 'child-source':
        mapping['bodies'][x.child + '/body:common'] = copy.deepcopy(mapping['bodies'][x.donor_id])
    else:
        sig = change['signature']
        if fault == 'type':sig['args'][0]['type'] = 'double'
        elif fault == 'role':sig['args'][0]['mode'] = 'ref'
        elif fault == 'return':sig['return'] = 'double'
        else:sig['args'].reverse()
        for plan in mapping['bodies'].values():plan['contract'] = copy.deepcopy(sig)
    x.n.prepare(bad, False)
    x.unchanged()
x.f.checked('부모/자식 쓰기 위조·타입/역할/반환/순서의 불명확한 변경은 전체 미적용으로 거절한다')
parent = x.f.project / x.parent_path
before = parent.read_bytes()
try:
    parent.write_bytes(before + b'\n// concurrent parent source\n')
    x.n.prepare(r, False)
finally:
    parent.write_bytes(before)
x.unchanged()
x.f.checked('실제 부모 파일 경합은 원래 읽기 기준으로 차단하고 후보/복사본 원문을 보존한다')
print(json.dumps({'checks': x.f.checks, 'evidence': str(x.f.case),
                  'pureCandidate': True, 'actualWindows': False}, ensure_ascii=False))
