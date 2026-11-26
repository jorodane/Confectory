"""Endpoint-only timing of the existing owned-child-case insertion fixture. Not a Chromium input timing test."""
import ast,sys,time,copy,json,shutil
from pathlib import Path
fixture=Path(__file__).with_name('v821_child_case_insert_ui.py')
setup=ast.parse(fixture.read_text()).body
exec(compile(ast.Module(body=setup[:next(i for i,node in enumerate(setup) if isinstance(node,ast.Try) and i>10 and any(isinstance(item,ast.Expr) and isinstance(item.value,ast.Call) and isinstance(item.value.func,ast.Attribute) and item.value.func.attr=='build' for item in node.body))],type_ignores=[]),str(fixture),'exec'),globals())
def timed(label,call):
    start=time.perf_counter();out=call();print('TIMING',label,round((time.perf_counter()-start)*1000),flush=True);return out
try:
    x.build('before-perf-host',14,output())
    f.start(0);f.invoke('select',dict(id=t.feature));f.invoke('saveDraft',{})
    checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
    baseline=timed('read-first',read)
    for i in range(3):assert timed(f'read-repeat-{i}',read)['edges']==baseline['edges']
    if len(sys.argv)>4 and sys.argv[4]=='invalid':
        new_body='global::System.Console.WriteLine(MissingProbe);'
        result=f.invoke('blueprint',proposal(baseline))['result']['result'];assert result['settled']
        saved=read();held=checkpoint.read_bytes();ids=saved['reviewIds']
        reviewed=f.invoke('reviewGroup',dict(ids=ids))['state']['review'];assert not reviewed.get('errors'),reviewed
        response=f.invoke('confirmGroup',dict(ids=ids,token=reviewed['token']));rejected=response['result']['result'];message=json.dumps(response['state'],ensure_ascii=False)
        assert not rejected['sourceConfirmed'] and 'CS0103' in message and 'MissingProbe' in message,(rejected,'compiler diagnostic not projected by the web state')
        assert checkpoint.read_bytes()==held and not new_files();x.original()
        print('PASS actual Confirm compiler rejects invalid source and preserves checkpoint/originals',flush=True)
        raise SystemExit(0)
    peer_before=read(other)['nodes'];q=proposal(baseline)
    source=f.project/peer['implementation'];raw=source.read_bytes();source.write_bytes(raw+b' ')
    try:
        timed('stale-save',lambda:f.invoke('blueprint',q,False));assert checkpoint.read_bytes()==before
    finally:source.write_bytes(raw)
    q=proposal(read());result=timed('save',lambda:f.invoke('blueprint',q))['result']['result'];assert result['settled'],result
    saved=timed('read-after-save',read);assert any(n['id']=='cell_candidate' and n['source']==new_body for n in saved['nodes']);assert read(other)['nodes']==peer_before
    assert not new_files();x.original()
    ids=saved['reviewIds'];reviewed=timed('review',lambda:f.invoke('reviewGroup',dict(ids=ids)))['state']['review'];assert not reviewed.get('errors'),reviewed
    held=checkpoint.read_bytes();source.write_bytes(raw+b' ')
    try:
        result=timed('stale-confirm',lambda:f.invoke('confirmGroup',dict(ids=ids,token=reviewed['token'])))['result']['result'];assert not result['sourceConfirmed'] and checkpoint.read_bytes()==held
    finally:source.write_bytes(raw)
    reviewed=timed('review-again',lambda:f.invoke('reviewGroup',dict(ids=ids)))['state']['review'];assert not reviewed.get('errors'),reviewed
    result=timed('confirm',lambda:f.invoke('confirmGroup',dict(ids=ids,token=reviewed['token'])))['result']['result'];assert result['sourceConfirmed'],result
    files=new_files();assert len(files)==1 and json.loads(files[0].read_text())['source']==new_body
    lines=output().splitlines();lines.insert(lines.index('positive:7')+1,'inserted-case');x.build('after-perf-host',14,'\n'.join(lines))
    f.stop();f.start(1);assert any(n['id']=='cell_candidate' for n in read()['nodes']);assert read(other)['nodes']==peer_before
    print('PASS HOST SAVE, EXTERNAL CHANGE, CONFIRM, EXECUTION, REOPEN',flush=True)
finally:
    f.stop();print('EVIDENCE',f.case,flush=True)
