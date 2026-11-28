"""Exact before/after read reuse over real authoring, with optional prior tool comparison.
Usage: metadata_read_reuse.py NEW_TOOL [BASELINE_TOOL]. Synthetic 40/400 projects only.
"""
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import time
import statistics

host = os.environ['CONFECTORY_DOTNET']
new = [host, sys.argv[1]]
old = [host, sys.argv[2]] if len(sys.argv) > 2 else None


def run(tool, request, trace=False):
    env = dict(os.environ, CONFECTORY_METADATA_REUSE_TRACE='1' if trace else '0')
    result = subprocess.run(tool, input=json.dumps(request), text=True, capture_output=True,
                            env=env, check=True, timeout=30)
    return json.loads(result.stdout), result.stderr


with tempfile.TemporaryDirectory(prefix='confectory-metadata-read-reuse-') as tmp:
    for count in (40, 400):
        root = pathlib.Path(tmp) / str(count)
        root.mkdir()
        ns = 'Reuse'
        sources = {
            'Nested': ('schema', 'schema Reuse::Nested { field Flag single general bool; }'),
            'Info': ('schema', 'schema Reuse::Info { field Count single general long; field Note single general string; field Target single reference Reuse::Info; field Nested single compound Reuse::Nested; }'),
            'Root': ('object', 'object Reuse::Root { use schema Reuse::Info; value editorName = "현지"; data Count = 17; data Note = "old"; data Target = Reuse::Target0; data Nested = { Flag = true; }; }'),
            'Child': ('object', 'object Reuse::Child extends Reuse::Root { data Note = "child"; }'),
        }
        for i in range(count-2):
            name = f'Target{i}'
            sources[name] = ('object', f'object Reuse::{name} {{ use schema Reuse::Info; data Count = {i}; data Note = "peer"; }}')
        project = root / 'project.cpack'
        project.write_text('project Reuse version "1" { standalone false; ' + ''.join(
            f'element {name} {kind} "{name}.celem";' for name, (kind, _) in sources.items()) + '}')
        for name, (_, text) in sources.items():
            (root / f'{name}.celem').write_text(text)

        def unit(kind, path):
            text = path.read_text()
            return dict(kind=kind, path=path.name, draft=text, original=text, revision=1,
                        baseline=hashlib.sha256(text.encode()).hexdigest())

        units = {ns+'::ProjectManifest': unit('project', project)}
        units.update({ns+'::'+name: unit(kind, root/f'{name}.celem') for name,(kind, _) in sources.items()})
        base = dict(operation='mixedOwnerCopyEdits', project=str(project), manifest=project.read_text(),
                    id=ns+'::Root', text=sources['Root'][1], drafts=[], units=units, reuseLongPreparation=True,
                    reuseStringPreparation=True)
        requests = [dict(base, changes=[dict(type='data', path=[field], contract=dict(kind=kind,cardinality='single',type=type_),valueJson=json.dumps(value))])
                    for field,kind,type_,value in [('Count','general','long',123456),('Note','general','string','한글 · café'),('Target','reference','Reuse::Info',{'$ref':'Reuse::Target1'})]]

        for request in requests:
            candidate, trace = run(new, request, True)
            assert candidate['ok'], candidate
            if old:
                baseline, _ = run(old, request)
                assert candidate == baseline, (request['changes'], candidate, baseline)
            ordinary, _ = run(new, dict(request,reuseLongPreparation=False))
            assert ordinary['ok'], ordinary
            exact=dict(candidate['result']);exact.pop('repeatProof',None)
            ordinary_result=dict(ordinary['result']);ordinary_result.pop('repeatProof',None)
            assert exact == ordinary_result,(exact,ordinary_result)
            counts=json.loads(re.search(r'CONFECTORY_METADATA_REUSE (.+)',trace)[1])
            assert counts['captured']>=count-1 and counts['reused']>=count-1 and counts['parsedReused']>=count-1,counts
            print(count, request['changes'][0]['path'][0], counts, flush=True)

        # A resident stream must not retain a previous request's bytes, even
        # when an unrelated source changes without a timestamp change.
        proc = subprocess.Popen(new+['--inspect-stream'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        try:
            assert proc.stdout.readline().strip()=='CONFECTORY_INSPECT_STREAM_14'
            def send(request):
                proc.stdin.write(json.dumps(request)+'\n');proc.stdin.flush()
                return json.loads(proc.stdout.readline())
            assert send(requests[0])['ok']
            peer=root/'Target2.celem';original=peer.read_bytes();stat=peer.stat()
            peer.write_text('object Reuse::Target2 { use schema Reuse::Info; data Count = "invalid"; }')
            os.utime(peer,ns=(stat.st_atime_ns,stat.st_mtime_ns))
            assert not send(requests[0])['ok']
            peer.write_bytes(original)
            assert send(requests[0])['ok']
            if os.name=='posix':
                peer.chmod(0)
                try:
                    if not os.access(peer,os.R_OK):assert not send(requests[0])['ok']
                finally:peer.chmod(stat.st_mode)
                external=pathlib.Path(tmp)/f'outside-{count}.celem';external.write_bytes(original)
                peer.unlink();peer.symlink_to(external)
                try:assert not send(requests[0])['ok']
                finally:peer.unlink();peer.write_bytes(original)
            assert send(requests[0])['ok']
            proc.stdin.close();assert proc.wait(timeout=5)==0
        finally:
            if proc.poll() is None:proc.kill()
            proc.wait()
        assert (root/'Root.celem').read_text()==sources['Root'][1]
        if count==400 and old and os.environ.get('CONFECTORY_METADATA_PROFILE')=='1':
            readers=[subprocess.Popen(tool+['--inspect-stream'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True) for tool in (old,new)]
            samples=[[],[]]
            try:
                for reader in readers:assert reader.stdout.readline().strip()=='CONFECTORY_INSPECT_STREAM_14'
                for iteration in range(11):
                    request=requests[iteration%len(requests)];answers={}
                    for side in ((0,1) if iteration%2==0 else (1,0)):
                        reader=readers[side];started=time.perf_counter();reader.stdin.write(json.dumps(request)+'\n');reader.stdin.flush();answers[side]=json.loads(reader.stdout.readline());elapsed=(time.perf_counter()-started)*1000
                        assert answers[side]['ok'],answers[side]
                        if iteration>=2:samples[side].append(round(elapsed,1))
                    assert answers[0]==answers[1]
                print('warm exact mixedOwnerCopyEdits baseline/candidate',samples,'medians',[statistics.median(v) for v in samples],flush=True)
            finally:
                for reader in readers:
                    if reader.poll() is None:
                        reader.stdin.close()
                        try:reader.wait(timeout=5)
                        except subprocess.TimeoutExpired:reader.kill();reader.wait()
print('PASS exact read/parse reuse, full candidate equivalence, fresh invalid/unreadable/escaped source rejection, no writes')
