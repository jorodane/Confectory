"""Owned inherited implementation; every source lives in a temporary fixture."""
import json
import v536_information_whole_body_fixture as b

f, d, n, owner, fn, mode = b.f, b.d, b.n, b.owner, b.fn, b.mode
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
