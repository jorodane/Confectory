"""The single-long preparation proof covers both validated metadata projections."""
import hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
host=[os.environ['CONFECTORY_DOTNET'],sys.argv[1]]
with tempfile.TemporaryDirectory(prefix='cf-long-prepare-') as folder:
    root=Path(folder);dep=root/'dep';dep.mkdir();project=root/'project.cpack'
    dependency=dep/'pack.cpack';dependency.write_text('pack Dependency version "1" {}')
    manifest=f'project Alpha version "1" {{ registry Dependency "{dependency.as_posix()}"; dependency Dependency version "1"; element Rules object "rules.celem"; element Fields schema "fields.celem"; }}'
    old='object Alpha::Rules { use schema Alpha::Fields; data Phase = 5000; }';schema='schema Alpha::Fields { field Phase single general long; }'
    project.write_text(manifest);(root/'rules.celem').write_text(old);(root/'fields.celem').write_text(schema)
    change={'type':'data','path':['Phase'],'contract':{'kind':'general','cardinality':'single','type':'long'},'valueJson':'6000'}
    def call(changes=[change],reuse=True,text=old):
        args=dict(operation='mixedOwnerCopyEdits',project=str(project),manifest=manifest,id='Alpha::Rules',text=text,changes=changes,drafts=[{'id':'Alpha::Fields','text':schema}],units={})
        if reuse:args['reuseLongPreparation']=True
        return json.loads(subprocess.check_output(host,input=json.dumps(args),text=True))
    ordinary=call(reuse=False);candidate=call();assert ordinary['ok'] and candidate['ok'],(ordinary,candidate)
    proof=candidate['result'].pop('repeatProof');assert candidate==ordinary,(candidate,ordinary)
    assert proof['observations']==[{'path':str(dependency),'hash':hashlib.sha256(dependency.read_bytes()).hexdigest()}]
    assert {Path(x).name for x in proof['ownershipPaths']}=={'project.cpack','rules.celem','fields.celem','pack.cpack'}
    assert 'repeatProof' not in call([{'type':'description','text':'not a value'}])['result']
    assert 'repeatProof' not in call([change,{'type':'description','text':'mixed'}])['result']
    assert not call([{**change,'contract':{'kind':'general','cardinality':'single','type':'int'}}])['ok']
    assert (root/'rules.celem').read_text()==old
print('PASS same validated candidate, exact observed dependency and ownership proof, mixed/invalid requests retain ordinary handling')
