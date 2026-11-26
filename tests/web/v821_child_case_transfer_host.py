"""Endpoint-only regression of the existing owned-child-case transfer fixture. Not a Chromium input test."""
import ast,sys,time,copy,json,shutil
from pathlib import Path
fixture=Path(__file__).with_name('v821_child_case_transfer_ui.py')
setup=ast.parse(fixture.read_text()).body
exec(compile(ast.Module(body=setup[:next(i for i,n in enumerate(setup) if isinstance(n,ast.Try) and any(isinstance(item,ast.Expr) and isinstance(item.value,ast.Call) and isinstance(item.value.func,ast.Attribute) and item.value.func.attr=='build' for item in n.body))],type_ignores=[]),str(fixture),'exec'),globals())
try:
    x.build('before-transfer-host',14,original_output)
    f.start(0);f.invoke('select',dict(id=t.feature));f.invoke('saveDraft',{})
    checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
    baseline=read();peer_before=read(other)['nodes'];q=transfer_request(baseline)
    duplicate=f.case/'other project same IDs';shutil.copytree(f.project,duplicate,ignore=shutil.ignore_patterns('.confectory'))
    duplicate_files={p:p.read_bytes() for p in duplicate.rglob('*') if p.is_file()}
    original_project=f.env['CONFECTORY_WEB_PROJECT'];f.stop()
    try:
        f.env['CONFECTORY_WEB_PROJECT']=str(duplicate/f.manifest.name);f.start(6);f.invoke('select',dict(id=t.feature));f.invoke('saveDraft',{})
        other_checkpoint=next(duplicate.glob('.confectory/edit-workspaces/*/draft.json'));other_before=other_checkpoint.read_bytes()
        same=read();assert same[key]==baseline[key] and same['checkpointHash']!=baseline['checkpointHash']
        f.invoke('blueprint',q,False);assert other_checkpoint.read_bytes()==other_before and all(p.read_bytes()==raw for p,raw in duplicate_files.items())
    finally:
        f.stop();f.env['CONFECTORY_WEB_PROJECT']=original_project
    f.start(7);baseline=read();q=transfer_request(baseline);assert checkpoint.read_bytes()==before
    source=f.project/peer['implementation'];raw=source.read_bytes();source.write_bytes(raw+b' ')
    try:f.invoke('blueprint',q,False);assert checkpoint.read_bytes()==before
    finally:source.write_bytes(raw)
    q=transfer_request(read());f.invoke('blueprint',q)
    settled=dict(q,action='settledAuthorBatch',settledProjection=True)
    def projection():return f.invoke('blueprint',settled)['result']['result']
    proof=projection();assert proof['settled'] and proof['projection'] is not None
    observed=read();assert all(proof['projection'][key]==observed[key] for key in ('id','rootId','nodes','edges','sources','checkpointHash'))
    source.write_bytes(raw+b' ')
    try:
        rejected=projection();assert not rejected['settled'] and rejected['projection'] is None
    finally:source.write_bytes(raw)
    assert projection()['settled']
    assert read()['edges']==changed['edges'];assert read(other)['nodes']==peer_before;x.original()
    for direction,edges in [('undo',baseline['edges']),('redo',changed['edges'])]:
        step=f.invoke('draftHistory',dict(action='inspect'))['result']['result'][direction]
        assert step['available'];assert f.invoke('draftHistory',dict(action=direction,token=step['token']))['result']['result']['accepted'];assert read()['edges']==edges and read(other)['nodes']==peer_before
    f.invoke('saveDraft',{})
    f.stop();f.start(1);assert read()['edges']==changed['edges'];x.original()
    ids=read()['reviewIds'];reviewed=f.invoke('reviewGroup',dict(ids=ids))['state']['review'];assert not reviewed.get('errors'),reviewed
    held=checkpoint.read_bytes();source.write_bytes(raw+b' ')
    try:
        result=f.invoke('confirmGroup',dict(ids=ids,token=reviewed['token']))['result']['result'];assert not result['sourceConfirmed'] and checkpoint.read_bytes()==held
    finally:source.write_bytes(raw)
    reviewed=f.invoke('reviewGroup',dict(ids=ids))['state']['review'];assert not reviewed.get('errors'),reviewed
    result=f.invoke('confirmGroup',dict(ids=ids,token=reviewed['token']))['result']['result'];assert result['sourceConfirmed'],result
    assert json.loads(graph_path.read_text())==expected and all(p.read_bytes()==raw for p,raw in x.physical.items() if p!=graph_path)
    x.build('after-transfer-host',14,changed_output)
    f.stop();f.start(2);assert read()['edges']==changed['edges'];assert read(other)['nodes']==peer_before
    print('PASS HOST CASE TRANSFER, STALE SAVE/CONFIRM, UNDO/REDO, EXECUTION AND REOPEN',flush=True)
finally:
    f.stop();print('EVIDENCE',f.case,flush=True)
