"""Bounded read-only authoring stream, run with CONFECTORY_DOTNET and CONFECTORY_ELEMENT_AUTHORING_HOST.

The ordinary authoring CLI remains supported. Each stream accepts only its own
project and allowed read requests; no source projection is cached across reads.
"""
import json
import os
from pathlib import Path
import subprocess
import shutil
import tempfile
from concurrent.futures import ThreadPoolExecutor

HOST = [os.environ['CONFECTORY_DOTNET'], os.environ['CONFECTORY_ELEMENT_AUTHORING_HOST']]
READY = 'CONFECTORY_INSPECT_STREAM_2'


def exercise(root):
    def project(name):
        folder = root / name
        folder.mkdir()
        manifest = folder / 'project.cpack'
        manifest.write_text('project Test.Stream version "1" { standalone false; '
                            'element Schema schema "Schema.celem"; '
                            'element Record object "Record.celem"; }')
        (folder / 'Schema.celem').write_text('schema Test.Stream::Schema { field Count single general int; }')
        (folder / 'Record.celem').write_text('object Test.Stream::Record { use schema Test.Stream::Schema; data Count = 2; }')
        return manifest

    a, b = project('a'), project('b')
    def request(manifest):
        return dict(operation='inspectEffective', project=str(manifest), manifest=manifest.read_text(),
                    id='Test.Stream::Record', kind='object', text=(manifest.parent / 'Record.celem').read_text(),
                    drafts=[], schemaView=True, schemaReuseProof=True)

    ordinary = subprocess.run(HOST, input=json.dumps(request(a)), text=True, capture_output=True, timeout=20, check=True)
    assert json.loads(ordinary.stdout)['ok']
    with ThreadPoolExecutor(max_workers=1) as executor:
        def read(process):
            try:
                return executor.submit(process.stdout.readline).result(timeout=20)
            except TimeoutError:
                process.kill()
                raise
        def start():
            process = subprocess.Popen(HOST + ['--inspect-stream'], stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            assert read(process).strip() == READY
            return process
        def send(process, payload):
            process.stdin.write(json.dumps(payload) + '\n')
            process.stdin.flush()
            return read(process)
        def finish(process):
            if process.poll() is None:
                process.kill()
            process.wait(timeout=5)
            for pipe in (process.stdin, process.stdout, process.stderr):
                if not pipe.closed:
                    pipe.close()

        proc = start()
        try:
            describe = dict(operation='describe', project=str(a), metadataOnly=True)
            inventory = dict(operation='catalog', project=str(a), request={'action':'inventory'})
            first = json.loads(send(proc, describe))
            assert first['ok'] and any(row['id']=='Test.Stream::Record' for row in first['result']['units'])
            assert json.loads(send(proc, inventory))['result']['status']=='available'
            initial = json.loads(send(proc, request(a)))
            assert initial['ok'] and 'Count' in initial['result']['effective']['fields']
            assert 'ExternalFlag' not in initial['result']['effective']['fields']
            schema = a.parent / 'Schema.celem'
            schema.write_text(schema.read_text().rstrip()[:-1] + ' field ExternalFlag single general string; }')
            updated = json.loads(send(proc, request(a)))
            assert updated['ok'] and 'ExternalFlag' in updated['result']['effective']['fields']
            # The same process must reread the current manifest, not hold a
            # cached activation registry or import another project's identity.
            extra = a.parent / 'Extra.celem'
            extra.write_text('object Test.Stream::Extra {}')
            a.write_text(a.read_text().rstrip()[:-1] + ' element Extra object "Extra.celem"; }')
            assert any(row['id']=='Test.Stream::Extra' for row in json.loads(send(proc, describe))['result']['units'])
            assert any(row['id']=='Test.Stream::Extra' for row in json.loads(send(proc, inventory))['result']['declarations'])
            assert send(proc, request(b)) == '' and proc.wait(timeout=5) == 2
        finally:
            finish(proc)
        proc = start()
        try:
            assert send(proc, dict(operation='describe', project=str(a), metadataOnly=False))==''
            assert proc.wait(timeout=5)==2
        finally:
            finish(proc)
        proc = start()
        try:
            assert send(proc, dict(operation='validatePresentationIcon', icon='test')) == ''
            assert proc.wait(timeout=5) == 2
        finally:
            finish(proc)
        proc = start()
        try:
            assert json.loads(send(proc, request(b)))['ok']
            proc.stdin.close()
            assert proc.wait(timeout=5) == 0
        finally:
            finish(proc)
        proc = start()
        try:
            # A known, pinned read-only context action remains discoverable.
            repo = Path(__file__).resolve().parents[2]
            menu = json.loads(send(proc, dict(operation='editorMenuDeclarations',
                project=str(repo / 'examples/editor-context-actions/project.cpack'), target='linux')))
            assert menu['ok'] and any(row['available'] for row in menu['result']['actions']), menu
        finally:
            finish(proc)
        copied = root / 'menu'
        shutil.copytree(repo / 'examples/editor-context-actions', copied)
        owned = root / 'schema-editing'
        shutil.copytree(repo / 'packs/schema-editing', owned)
        manifest = copied / 'project.cpack'
        manifest.write_text(manifest.read_text().replace('../../packs/schema-editing/pack.cpack',
            str(owned / 'pack.cpack')).replace('../../targets/dotnet/pack.cpack', str(repo / 'targets/dotnet/pack.cpack')))
        proc = start()
        try:
            payload = dict(operation='editorMenuDeclarations', project=str(manifest), target='linux')
            menu = json.loads(send(proc, payload))
            assert menu['ok'] and any(row['available'] for row in menu['result']['actions']), menu
            body = owned / 'Call.csbody'
            body.write_text(body.read_text() + '\n// Synthetic changed body\n')
            changed = json.loads(send(proc, payload))
            assert changed['ok'] and not any(row['available'] for row in changed['result']['actions']), changed
        finally:
            finish(proc)
        proc = start()
        try:
            assert proc.wait(timeout=40) == 0, 'idle stream did not retire'
        finally:
            finish(proc)


if __name__ == '__main__':
    with tempfile.TemporaryDirectory(prefix='confectory-read-stream-') as folder:
        exercise(Path(folder))
    print('PASS read stream: metadata activation and inventory, ordinary CLI, external schema/manifest, owner isolation, operation boundary, EOF and idle retirement')
