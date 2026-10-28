"""Keep a real earlier module-copy seed across an old/new engine restart."""
import json
import sys
from pathlib import Path
import v536_information_inherited_copy_fixture as x

f = x.f
baseline_repo = Path(sys.argv[4]).resolve()
baseline_report = Path(sys.argv[5]).resolve()
assert baseline_repo != f.repo and baseline_report.is_file()
new_report, new_env = f.report, dict(f.env)
module_fn, source, copied = f.n + 'Slot', f.n + 'AliasBody', f.n + 'CompatibilityCopy'
info = f.project / 'FreeInfo.celem'
info.write_text(info.read_text().replace('{', '{module ' + f.n + 'Rules;provide ' + module_fn + ' with ' + source + ';', 1))
try:
    f.report = json.loads(baseline_report.read_text())
    f.env['CONFECTORY_EDITOR_REPO'] = str(baseline_repo)
    f.env['CONFECTORY_ELEMENT_AUTHORING_HOST'] = str(baseline_repo / 'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')
    f.start(0)
    f.invoke('select', {'id': x.owner})
    f.invoke('saveDraft', {})
    s = x.schema()
    before = x.rpc('readImplementationCopy', id=x.owner, function=module_fn,
                   source=source, target='common', implementation=copied,
                   revision=s['revision'], hash=s['textHash'])
    checkpoint = next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))
    original_seed = json.loads(checkpoint.read_text())['privateCopies'][copied]
    assert x.fn not in [r['function'] for r in s['requirements']]
    f.stop()
    f.report = new_report
    f.env.clear()
    f.env.update(new_env)
    f.start(1)
    f.invoke('select', {'id': x.owner})
    s = x.schema()
    after = x.rpc('readImplementationCopy', id=x.owner, function=module_fn,
                  source=source, target='common', implementation=copied,
                  revision=s['revision'], hash=s['textHash'])
    assert before['contentFingerprint'] == after['contentFingerprint']
    assert before['seedHash'] == after['seedHash']
    assert json.loads(checkpoint.read_text())['privateCopies'][copied] == original_seed
    f.checked('이전 게시 엔진의 실제 module copy snapshot/범위 식별자는 새 엔진 cold에서도 변하지 않는다')
    result = x.rpc('applySlots', id=x.owner, rows=[{
        'function': module_fn, 'implementation': copied, 'copySource': source,
        'copyTarget': 'common', 'basis': after['basis'],
        'edits': [{'type': 'source', 'node': 'body',
                   'text': 'slotCount=amount+7;slotReady=true;return amount+8;'}]}])
    assert result['atomic'] and result['checkpointSaved']
    assert next(r for r in x.schema()['providers'] if r['function'] == module_fn)['implementation'] == copied
    f.checked('업그레이드 후 기존 모듈 copy의 명시 저장은 새 소유 구현만 보관하며 새로운 함수/모듈 권한을 요구하지 않는다')
finally:
    f.stop()
    print(json.dumps({'checks': f.checks, 'evidence': str(f.case),
                      'actualEngine': True, 'actualWindows': False}, ensure_ascii=False))
