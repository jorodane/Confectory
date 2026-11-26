"""Only a new owned, pure inherited data object is eligible for source validation."""
import hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
host=[os.environ['CONFECTORY_DOTNET'],sys.argv[1]]
with tempfile.TemporaryDirectory(prefix='cf-object-create-') as folder:
    root=Path(folder);candidate=root/'candidate'
    manifest='project Alpha version "1" { element Rules object "elements/Rules.celem"; element Fields schema "elements/Fields.celem"; }'
    registered=manifest.replace(' }',' element Child object "elements/Child.celem"; }')
    parent='object Alpha::Rules { use schema Alpha::Fields; data Phase = 5000; }'
    schema='schema Alpha::Fields { field Phase single general long; }'
    child='object Alpha::Child extends Alpha::Rules {}'
    for directory in (root,candidate):
        (directory/'elements').mkdir(parents=True);(directory/'project.cpack').write_text(manifest)
        (directory/'elements/Rules.celem').write_text(parent);(directory/'elements/Fields.celem').write_text(schema)
    def call(text=child,registration=registered,baseline='missing'):
        (candidate/'project.cpack').write_text(registration)
        (candidate/'elements/Child.celem').write_text(text)
        changes=['Alpha::ProjectManifest','project.cpack',hashlib.sha256(manifest.encode()).hexdigest(),registration,'Alpha::Child','elements/Child.celem',baseline,text]
        return json.loads(subprocess.check_output(host,input=json.dumps(dict(operation='validateExistingSchemaObjectCreation',originalProject=str(root/'project.cpack'),candidateProject=str(candidate/'project.cpack'),changes=changes)),text=True))
    def refused(reply):assert not reply['ok'] or not reply['result']['eligible'],reply
    proof=call();assert proof['ok'] and proof['result']['eligible'],proof
    assert {x['path'] for x in proof['result']['checks']}=={'project.cpack','elements/Rules.celem','elements/Fields.celem'}
    refused(call(child.replace('Alpha::Rules','Other::Rules')))
    refused(call(child.replace('{}','{ data Phase = 3; }')))
    refused(call(registration=registered.replace('version "1"','version "2"')))
    refused(call(baseline='0'*64))
    (root/'elements/Child.celem').write_text(child);refused(call());(root/'elements/Child.celem').unlink()
    (candidate/'elements/Rules.celem').write_text(parent.replace('5000','2000'));refused(call())
    (candidate/'elements/Rules.celem').write_text(parent)
    (candidate/'elements/Fields.celem').write_text(schema.replace('long','string'));refused(call())
print('PASS exact registration, parent/schema CAS, duplicate, foreign parent and other changes fallback')
