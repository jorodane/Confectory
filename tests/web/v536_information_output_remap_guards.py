"""An unimplemented owned declaration has no hidden writer consent or source edit."""
import copy
import json
import v536_information_output_remap_fixture as x

n, f = x.n, x.f
prior = n.fn
fn = n.a.functions[1]
file = f.project / ('elements/' + fn.split('::')[1] + '.celem')
original, manifest = file.read_bytes(), f.manifest.read_bytes()
body = fn.split('::')[1] + 'Body'
entry = 'element ' + body + ' implementation "' + body + '.celem";'
assert entry in manifest.decode()
try:
    n.fn = fn
    file.write_text(file.read_text().replace('provide ' + fn + ' with ' + fn + 'Body;', ''))
    f.manifest.write_text(f.manifest.read_text().replace(entry, ''))
    before = n.canonical(f.metadata('inspect', text=file.read_text())['signature'])
    new = copy.deepcopy(before)
    new['return'] = 'bool'
    r = n.request(new, {a['name']: a['name'] for a in before['args']})
    result = n.prepare(r)
    assert result['sourceWritten'] is False and not result['linkedUpdates']
    assert [row['id'] for row in result['updates']] == [fn]
    assert n.canonical(f.metadata('inspect', text=result['updates'][0]['text'])['signature']) == new
    print('PASS 실제 구현·소비자가 없는 소유 선언은 없는 writer를 만들지 않고 해당 계약만 명시 변경한다', flush=True)
    f.manifest.write_bytes(manifest)
    r = n.request(new, {a['name']: a['name'] for a in before['args']})
    n.prepare(r, False)
    del r['units'][fn + 'Body']
    n.prepare(r, False)
    print('PASS 등록된 C# 구현이나 누락시킨 실제 소스가 있으면 선언 전용으로 승격하지 않고 전체 거절한다', flush=True)
finally:
    file.write_bytes(original)
    f.manifest.write_bytes(manifest)
    n.fn = prior
assert all((f.project / p).read_bytes() == content for p, content in x.snapshot.items())
print(json.dumps({'checks': 2, 'pureCandidate': True, 'evidence': str(f.case), 'actualWindows': False}, ensure_ascii=False))
