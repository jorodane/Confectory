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
READY = 'CONFECTORY_INSPECT_STREAM_5'


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
            for name in ('informationPropertyGroupGuards','informationTypeGuards','informationBodyGroupGuards'):
                guard=dict(operation=name,action='validate',project=str(a),namespace='Test.Stream',units={},selected=[])
                assert json.loads(send(proc,guard))==json.loads(subprocess.run(HOST,input=json.dumps(guard),text=True,capture_output=True,timeout=20,check=True).stdout)
            for action in ('headers','graphs'):
                guard=dict(operation='informationBodyGroupGuards',action=action,namespace='Test.Stream',units={},selected=[])
                assert json.loads(send(proc,dict(guard,_streamProject=str(a))))==json.loads(subprocess.run(HOST,input=json.dumps(guard),text=True,capture_output=True,timeout=20,check=True).stdout)

            document=dict(operation='inspect',text='object Test.Stream::Record {}')
            assert json.loads(send(proc,dict(document,_streamProject=str(a))))==json.loads(subprocess.run(HOST,input=json.dumps(document),text=True,capture_output=True,timeout=20,check=True).stdout)
            invalid=dict(operation='blueprintSourceValidateBatch',documents=[dict(id='bad',kind='blueprint',text='{}')])
            assert json.loads(send(proc,dict(invalid,_streamProject=str(a))))==json.loads(subprocess.run(HOST,input=json.dumps(invalid),text=True,capture_output=True,timeout=20,check=True).stdout)

            main = dict(operation='catalog', project=str(a), request={'action':'project-main-view'})
            windows = dict(operation='catalog', project=str(a), request={'action':'project-windows'})
            assert json.loads(send(proc, main)) == json.loads(subprocess.run(HOST, input=json.dumps(main), text=True, capture_output=True, timeout=20, check=True).stdout)
            assert json.loads(send(proc, windows)) == json.loads(subprocess.run(HOST, input=json.dumps(windows), text=True, capture_output=True, timeout=20, check=True).stdout)
            card_schema=a.parent/'CardSchema.celem'
            card_schema.write_text('schema Test.Stream::CardSchema { field Note single general string; }')
            card_object=a.parent/'CardObject.celem'
            card_object.write_text('object Test.Stream::CardObject { use schema Test.Stream::CardSchema; data Note = "Before"; }')
            desk=a.parent/'Desk.celem'
            desk.write_text('view Test.Stream::Desk { use object Test.Stream::CardObject; value editorName = "Desk"; value editorMain = "element-view-card"; value editorWindow = "element-view-card"; }')
            a.write_text(a.read_text().rstrip()[:-1]+' element CardSchema schema "CardSchema.celem"; element CardObject object "CardObject.celem"; element Desk view "Desk.celem"; }')
            assert json.loads(send(proc,main))['result']['window']['value']=='Before'
            assert json.loads(send(proc,windows))['result']['windows'][0]['id']=='Test.Stream::Desk'
            card_object.write_text(card_object.read_text().replace('"Before"','"External"'))
            desk.write_text(desk.read_text().replace('editorMain = "element-view-card"','editorMain = "element-view-table"').replace('value editorWindow = "element-view-card";',''))
            reopened=json.loads(send(proc,main))['result']['window']
            assert reopened['value']=='External' and reopened['renderer']=='element-view-table'
            assert not json.loads(send(proc,windows))['result']['windows']
            def relation():
                import hashlib
                text=(a.parent/'Record.celem').read_text()
                return dict(operation='relationsMap',project=str(a),units=[dict(id='Test.Stream::Record',kind='object',text=text,revision=0,textHash=hashlib.sha256(text.encode()).hexdigest(),dirty=False)])
            first_map=json.loads(send(proc,relation()))
            assert first_map['ok'] and first_map['result']['nodes'][0]['valid']
            record=a.parent/'Record.celem'
            record.write_text(record.read_text().rstrip()[:-1]+' value editorName = "Fresh"; }')
            assert json.loads(send(proc,relation()))['result']['nodes'][0]['title']=='Fresh'
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
            assert send(proc, dict(operation='catalog', project=str(a), request={'action':'project-window-setting'})) == ''
            assert proc.wait(timeout=5) == 2
        finally:
            finish(proc)
        proc = start()
        try:
            assert json.loads(send(proc,request(a)))['ok']
            assert send(proc, dict(operation='inspect',text='object Test.Stream::Record {}',_streamProject=str(b))) == ''
            assert proc.wait(timeout=5) == 2
        finally:
            finish(proc)
        proc = start()
        try:
            assert send(proc, dict(operation='inspect',text='object Test.Stream::Record {}')) == ''
            assert proc.wait(timeout=5) == 2
        finally:
            finish(proc)
        proc = start()
        try:
            assert send(proc, dict(operation='informationBodyGroupGuards',action='prepare',project=str(a),namespace='Test.Stream',units={})) == ''
            assert proc.wait(timeout=5) == 2
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
    print('PASS read stream: metadata activation, inventory, live project view and relation map refresh, ordinary CLI, external schema/manifest, owner isolation, operation boundary, EOF and idle retirement')
