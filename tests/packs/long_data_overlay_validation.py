"""The exact existing-long proof uses captured source bytes, not a copied project."""
import hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
host=[os.environ['CONFECTORY_DOTNET'],sys.argv[1]]
with tempfile.TemporaryDirectory(prefix='cf-data-overlay-') as folder:
    base=Path(folder);root=base/'project';root.mkdir();dep=base/'dep.cpack'
    dep.write_text('pack Dependency version "1" {}')
    manifest=f'project Alpha version "1" {{ registry Dependency "{dep.as_posix()}"; dependency Dependency version "1"; element Rules object "rules.celem"; element Fields schema "fields.celem"; }}'
    old='object Alpha::Rules { use schema Alpha::Fields; data Phase = 5000; }';new=old.replace('5000','6000');schema='schema Alpha::Fields { field Phase single general long; }'
    (root/'project.cpack').write_text(manifest);(root/'rules.celem').write_text(old);(root/'fields.celem').write_text(schema)
    def call(text=new,**changes):
        args=dict(operation='validateLongDataOverlay',originalProject=str(root/'project.cpack'),id='Alpha::Rules',relative='rules.celem',baseline=hashlib.sha256(old.encode()).hexdigest(),after=text)
        return json.loads(subprocess.check_output(host,input=json.dumps(dict(args,**changes)),text=True))
    def refused(reply):assert not reply['ok'] or not reply['result']['eligible'],reply
    proof=call();assert proof['ok'] and proof['result']['eligible'],proof
    assert {x['path'] for x in proof['result']['checks']}=={'project.cpack','fields.celem'}
    assert proof['result']['reads']==[{'path':str(dep),'hash':hashlib.sha256(dep.read_bytes()).hexdigest()}]
    assert set(p.name for p in root.iterdir())=={'project.cpack','rules.celem','fields.celem'}
    assert (root/'rules.celem').read_text()==old
    for text in (old,new.replace('6000','"x"'),new.replace('use schema','description "changed"; use schema'),new.replace('Phase = 6000;','Phase = 6000; data Extra = 1;')):refused(call(text))
    refused(call(baseline='0'*64));refused(call(id='Other::Rules'));refused(call(relative='../rules.celem'))
    (root/'fields.celem').write_text(schema.replace('long','int'));refused(call());(root/'fields.celem').write_text(schema)
    dep.write_text('pack Other version "1" {}');refused(call())
    assert (root/'rules.celem').read_text()==old
print('PASS exact overlay, owned manifest/schema and registered dependency observations, stale/foreign/unsupported refusal, no copied or written sources')
