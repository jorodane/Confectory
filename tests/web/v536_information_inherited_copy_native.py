"""Read-only inherited source receipts and explicit local copy preparation."""
import json
import v536_information_inherited_copy_fixture as x

f = x.f
model = f.metadata('effective', project=str(f.manifest), manifest=f.manifest.read_text(),
                   id=x.owner, text=x.b.info.read_text(), observeSources=True)
provider = next(p for p in model['providers'] if p['function'] == x.fn)
assert provider['contract']['parent'] == x.parent
assert provider['contract']['bodyOrigins'] == {'common': x.parent}
assert provider['contract']['status'] == 'valid'
f.checked('상속 구현의 직접 ID와 실제 부모/본문 출처는 읽기 전용 metadata에서 구별한다')
prepared = f.metadata('implementationCopy', action='prepare', project=str(f.manifest),
                      feature=x.fn, source=x.child, target='common',
                      implementation=x.copy_id, owner=x.owner,
                      ownerText=x.b.info.read_text())
provenance = prepared['graph']['copySource']
assert provenance == {'implementation': x.child, 'target': 'common',
                      'bodyOrigin': x.parent, 'sourceKind': 'csharp'}
assert ' extends ' not in prepared['implementation']
assert x.copy_id in prepared['implementation']
assert prepared['records'][0]['record']['source'] == x.original
observed = {row['path'] for row in prepared['observations']}
assert {str(f.project / x.parent_path), str(x.b.implementation_file),
        str(f.project / 'whole-original.csbody')}.issubset(observed)
assert prepared['sourceWritten'] is False and prepared['compiled'] is False
assert all((f.project / p).read_bytes() == v for p, v in x.snapshot.items())
f.checked('명시 복사는 자식/부모 header와 부모 CRLF 본문 receipt를 묶고 원본·다른 호출자를 수정하지 않는다')
print(json.dumps({'checks': f.checks, 'pureCandidate': True,
                  'evidence': str(f.case), 'actualWindows': False}, ensure_ascii=False))
