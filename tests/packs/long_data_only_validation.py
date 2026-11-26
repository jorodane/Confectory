"""Conservative source-only validation eligibility; no compiler invocation."""
import hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
host=[os.environ['CONFECTORY_DOTNET'],sys.argv[1]]
with tempfile.TemporaryDirectory(prefix='cf-data-only-') as folder:
    root=Path(folder);candidate=root/'candidate';candidate.mkdir();manifest='project Alpha version "1" { standalone true; entry Alpha::Main; element Main function "main.celem"; element Rules object "rules.celem"; element Fields schema "fields.celem"; }'
    old='object Alpha::Rules { use schema Alpha::Fields; data Phase = 5000; }';new=old.replace('5000','6000');schema='schema Alpha::Fields { field Phase single general long; }'
    for directory in (root,candidate):
        (directory/'project.cpack').write_text(manifest);(directory/'main.celem').write_text('function Alpha::Main () -> int {}');(directory/'fields.celem').write_text(schema)
    (root/'rules.celem').write_text(old)
    def call(text,**changes):
        (candidate/'rules.celem').write_text(text);args=dict(operation='validateLongDataOnly',originalProject=str(root/'project.cpack'),candidateProject=str(candidate/'project.cpack'),id='Alpha::Rules',relative='rules.celem',baseline=hashlib.sha256(old.encode()).hexdigest(),after=text)
        return json.loads(subprocess.check_output(host,input=json.dumps(dict(args,**changes)),text=True))
    proof=call(new);assert proof['ok'] and proof['result']['eligible'],proof
    assert {row['path'] for row in proof['result']['checks']}=={'project.cpack','fields.celem'}
    for invalid in [old,old.replace('5000','"6000"'),new.replace('use schema','description "changed"; use schema'),new.replace('Phase = 6000;','Phase = 6000; data Other = 1;')]:
        reply=call(invalid);assert not reply['ok'] or not reply['result']['eligible'],reply
    assert not call(new,baseline='0'*64)['ok']
    (candidate/'fields.celem').write_text(schema.replace('long','int'));assert not call(new)['ok']
    assert (root/'rules.celem').read_text()==old
print('PASS exact long-only delta and schema/manifest CAS proof, other edits fallback, stale rejection')
