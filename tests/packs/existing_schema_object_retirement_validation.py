"""Exact registration-only retirement proof and static execution graph boundaries."""
import hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
host=[os.environ['CONFECTORY_DOTNET'],sys.argv[1]]
with tempfile.TemporaryDirectory(prefix='cf-object-retirement-') as folder:
    root=Path(folder);candidate=root/'candidate'
    manifest='project Alpha version "1" { standalone true; entry Alpha::Main; target linux Alpha::Target; target other Alpha::Target; element Main function "main.celem"; element Body implementation "body.celem"; element Target buildtarget "target.celem"; element Rules object "rules.celem"; element Fields schema "fields.celem"; element Child object "child.celem"; }'
    child='object Alpha::Child extends Alpha::Rules {}'
    sources={'main.celem':'function Alpha::Main () -> int { provide Alpha::Main with Alpha::Body; }','body.celem':'implementation Alpha::Body for Alpha::Main () -> int { body common "main.csbody"; }','target.celem':'buildtarget Alpha::Target { tool "not-called.dll"; }','main.csbody':'return 0;','rules.celem':'object Alpha::Rules { use schema Alpha::Fields; data Phase = 5; }','fields.celem':'schema Alpha::Fields { field Phase single general long; }','child.celem':child}
    candidate.mkdir()
    def call(old=manifest,override=None,changes=None,candidate_only=None):
        new=old.replace('element Child object "child.celem";','')
        for directory in (root,candidate):
            for key,value in dict(sources,**(override or {})).items():(directory/key).write_text(value)
        (root/'project.cpack').write_text(old);(candidate/'project.cpack').write_text(new)
        for key,value in (candidate_only or {}).items():(candidate/key).write_text(value)
        h=lambda s:hashlib.sha256(s.encode()).hexdigest()
        rows=['Alpha::ProjectManifest','project.cpack',h(old),new,'Alpha::Child','child.celem',h(child),child]
        if changes:changes(rows)
        request=dict(originalProject=str(root/'project.cpack'),candidateProject=str(candidate/'project.cpack'),target='linux',changes=rows)
        def invoke(operation,**payload):
            return json.loads(subprocess.check_output(host,input=json.dumps(dict(operation=operation,**payload)),text=True))
        candidate_manifest=candidate/'project.cpack';raw=candidate_manifest.read_bytes()
        combined=invoke('prepareExistingSchemaObjectRetirement',**request)
        assert candidate_manifest.read_bytes()==raw, 'Combined proof must be read-only'
        prepared=invoke('prepare',original=request['originalProject'],candidate=request['candidateProject'],additions=[])
        assert prepared['ok'] and combined['ok'],(prepared,combined)
        assert combined['result']['preparedManifest']==prepared['result']
        candidate_manifest.write_text(prepared['result'])
        legacy=invoke('validateExistingSchemaObjectRetirement',**request)
        assert legacy['ok'] and combined['result']['proof']==legacy['result'],(combined,legacy)
        return legacy
    def refused(reply):assert not reply['ok'] or not reply['result']['eligible'],reply
    proof=call();assert proof['ok'] and proof['result']['eligible'],proof
    assert {x['path'] for x in proof['result']['checks']}=={'project.cpack','child.celem'}
    assert {Path(x['path']).name for x in proof['result']['reads']}==set(sources)-{'child.celem'}
    always=call(old=manifest.replace('standalone true;','standalone true; always Alpha::Child;'));refused(always);assert always['result']['invalid'],always
    refused(call(override={'main.celem':sources['main.celem'].replace('provide','use object Alpha::Child; provide')}))
    refused(call(override={'main.csbody':'// Alpha::Child\nreturn 0;'}))
    refused(call(candidate_only={'fields.celem':sources['fields.celem'].replace('long','string')}))
    refused(call(changes=lambda rows:rows.__setitem__(6,'0'*64)))
    refused(call(changes=lambda rows:rows.__setitem__(3,rows[3].replace('version "1"','version "2"'))))
    refused(call(override={'body.celem':sources['body.celem'].replace('common','linux')}))
print('PASS combined read-only preparation matches legacy proof, exact unregister, all-target graph, always, references, source and mixed-change fallback')
