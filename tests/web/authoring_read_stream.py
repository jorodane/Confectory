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
READY = 'CONFECTORY_INSPECT_STREAM_8'


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
    imported=root/'imported';imported.mkdir()
    (imported/'pack.cpack').write_text('pack Test.Import version "1" { element F function "F.celem"; }')
    foreign=imported/'F.celem';foreign.write_text('function Test.Import::F () -> void {}')
    a.write_text(a.read_text().rstrip()[:-1]+' registry Test.Import "../imported/pack.cpack"; dependency Test.Import version "1"; element Work function "Work.celem"; element WorkBody implementation "WorkBody.celem"; }')
    (a.parent/'Work.celem').write_text('function Test.Stream::Work () -> void { provide Test.Stream::Work with Test.Stream::WorkBody; }')
    owned=a.parent/'WorkBody.celem';owned.write_text('implementation Test.Stream::WorkBody for Test.Stream::Work () -> void { import Test.Import::F as Foreign () -> void; body common "Work.csbody"; }')
    (a.parent/'Work.csbody').write_text('return;')
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

            # The checkpoint Save uses the same payload-only read guard in
            # the selected project's read stream. Preserve every returned CAS
            # observation, including a nonempty body receipt and stale refusal.
            import hashlib
            def property_unit(kind, path, text):
                return dict(kind=kind, path=path, draft=text, original=text,
                            baseline=hashlib.sha256(text.encode()).hexdigest())
            implementation='Test.Stream::WorkBody'
            graph_id=implementation+'/body:common'
            units={
                'Test.Stream::ProjectManifest':property_unit('project','project.cpack',a.read_text()),
                'Test.Stream::Work':property_unit('function','Work.celem',(a.parent/'Work.celem').read_text()),
                implementation:property_unit('implementation','WorkBody.celem',
                    'implementation Test.Stream::WorkBody for Test.Stream::Work () -> void { blueprint common "Work.graph.json"; }'),
                graph_id:property_unit('blueprint','Work.graph.json',json.dumps({'nodes':[]}))}
            sources={id:dict(path=unit['path'],kind=unit['kind'],hash=unit['baseline']) for id,unit in units.items()}
            units[graph_id]['propertyObservations']=dict(version=1,graph=graph_id,sources=sources)
            property_guard=dict(operation='blueprintPropertyObservations',namespace='Test.Stream',units=units)
            def ordinary_guard(payload):
                return json.loads(subprocess.run(HOST,input=json.dumps(payload),text=True,capture_output=True,timeout=20,check=True).stdout)
            result=ordinary_guard(property_guard)
            assert result['ok'] and len(result['result']['checks'])==4,result
            assert json.loads(send(proc,dict(property_guard,_streamProject=str(a))))==result
            stale=json.loads(json.dumps(property_guard));stale['units']['Test.Stream::Work']['baseline']='0'*64
            refusal=ordinary_guard(stale)
            assert not refusal['ok'] and json.loads(send(proc,dict(stale,_streamProject=str(a))))==refusal
            assert json.loads(send(proc,dict(property_guard,_streamProject=str(a))))==result

            override=dict(operation='blueprintOverrideContracts',action='readRootImports',project=str(a),text=owned.read_text())
            observed=json.loads(send(proc,override));assert observed['ok'] and observed['result']['snapshot']
            assert observed==json.loads(subprocess.run(HOST,input=json.dumps(override),text=True,capture_output=True,timeout=20,check=True).stdout)
            verify=dict(override,action='verifyRootImports',snapshot=observed['result']['snapshot'])
            assert json.loads(send(proc,verify))['ok']
            foreign.write_text(foreign.read_text()+'\n// external declaration revision\n')
            assert not json.loads(send(proc,verify))['ok']
            refreshed=json.loads(send(proc,override));assert refreshed['ok'] and refreshed['result']['snapshot']!=observed['result']['snapshot']
            assert refreshed==json.loads(subprocess.run(HOST,input=json.dumps(override),text=True,capture_output=True,timeout=20,check=True).stdout)

            # Root execution candidates are a pure payload projection with an
            # explicit transport owner. Invalid graph input still rejects and
            # the same stream remains available for the next scoped read.
            root_candidates=dict(operation='blueprintRootExecutionCandidates',id='Test.Stream::WorkBody/body:common',units={})
            expected=json.loads(subprocess.run(HOST,input=json.dumps(root_candidates),text=True,capture_output=True,timeout=20,check=True).stdout)
            assert not expected['ok'] and json.loads(send(proc,dict(root_candidates,_streamProject=str(a))))==expected

            document=dict(operation='inspect',text='object Test.Stream::Record {}')
            assert json.loads(send(proc,dict(document,_streamProject=str(a))))==json.loads(subprocess.run(HOST,input=json.dumps(document),text=True,capture_output=True,timeout=20,check=True).stdout)
            invalid=dict(operation='blueprintSourceValidateBatch',documents=[dict(id='bad',kind='blueprint',text='{}')])
            assert json.loads(send(proc,dict(invalid,_streamProject=str(a))))==json.loads(subprocess.run(HOST,input=json.dumps(invalid),text=True,capture_output=True,timeout=20,check=True).stdout)

            feature = dict(operation='blueprintPrepareFeature', id='Test.Stream::Fresh',
                           text='function Test.Stream::Fresh () -> int { description "Fresh"; }',
                           implementation='Test.Stream::FreshBody', graphPath='fresh.graph.json', nodePath='fresh.node.json')
            def ordinary_proposal(payload):
                return json.loads(subprocess.run(HOST, input=json.dumps(payload), text=True, capture_output=True, timeout=20, check=True).stdout)
            proposal = ordinary_proposal(feature)
            assert proposal['ok'], proposal
            assert json.loads(send(proc, dict(feature, _streamProject=str(a))))==proposal
            call = dict(operation='blueprintPrepareCall', id=feature['implementation'],
                        text=proposal['result']['implementation'], graph=proposal['result']['graph'],
                        targetText='function Test.Stream::Donor (int amount) -> void {}',
                        definition=dict(id='donor',feature='Test.Stream::Donor',intent='Call donor',control='next'))
            expected=ordinary_proposal(call)
            assert expected['ok'], expected
            assert json.loads(send(proc, dict(call,_streamProject=str(a))))==expected
            # Same transaction reuses an exact derived contract model, not
            # its authority: a different graph or declaration must be observed.
            import uuid
            token=uuid.uuid4().hex
            projection=dict(operation='blueprintDescribeOwned',project=str(a),id=feature['implementation'],
                            text=proposal['result']['implementation'],graph=proposal['result']['graph'],
                            draftContracts={feature['id']:proposal['result']['function']},bodyTarget='common',definitionsOnly=True)
            def projected(value):
                return json.loads(send(proc,dict(value,_projectionTransaction=token)))
            assert projected(projection)==ordinary_proposal(projection)
            assert projected(projection)==ordinary_proposal(projection)
            changed_graph=json.loads(json.dumps(projection['graph']))
            changed_graph['nodes'][0]['intent']='Different candidate cell'
            updated_projection=dict(projection,graph=changed_graph)
            updated=ordinary_proposal(updated_projection)
            assert updated!=ordinary_proposal(projection) and projected(updated_projection)==updated
            assert projected(projection)==ordinary_proposal(projection)
            foreign_call=dict(call,targetText=foreign.read_text(),
                              definition=dict(id='foreign',feature='Test.Import::F',intent='Foreign call',control='next'))
            foreign_prepared=ordinary_proposal(foreign_call)
            assert foreign_prepared['ok'], foreign_prepared
            linked=dict(projection,text=foreign_prepared['result']['implementation'],graph=foreign_prepared['result']['graph'])
            baseline=ordinary_proposal(linked)
            assert baseline['ok'] and baseline['result']['state']=='node-definitions',baseline
            assert projected(linked)==baseline and projected(linked)==baseline
            original_foreign=foreign.read_bytes();stamp=foreign.stat()
            try:
                foreign.write_text('function Test.Import::F (int changed) -> void {}')
                os.utime(foreign,ns=(stamp.st_atime_ns,stamp.st_mtime_ns))
                changed=ordinary_proposal(linked)
                assert changed!=baseline and projected(linked)==changed,changed
            finally:
                foreign.write_bytes(original_foreign)
            assert projected(linked)==ordinary_proposal(linked)
            # Retargeting a locator must not reuse the old parsed contract
            # even if its original file is still unchanged.
            if os.name != 'nt':
                outside=root/'unowned.celem';outside.write_bytes(original_foreign)
                original_path=foreign.with_suffix('.saved')
                foreign.rename(original_path)
                try:
                    foreign.symlink_to(outside)
                    rejected=ordinary_proposal(linked)
                    assert not rejected['ok'] and projected(linked)==rejected,rejected
                finally:
                    foreign.unlink();original_path.rename(foreign)
                assert projected(linked)==ordinary_proposal(linked)
            for value in ('blueprintEnumPreview','blueprintNodeFlow'):
                malformed=dict(operation=value)
                if value=='blueprintNodeFlow': malformed['ownerRequest']={'project':str(a)}
                assert json.loads(send(proc,dict(malformed,_streamProject=str(a))))==ordinary_proposal(malformed)

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
            assert json.loads(send(proc, request(a)))['ok']
            assert send(proc, dict(operation='blueprintNodeFlow', _streamProject=str(a),
                                   ownerRequest={'project':str(b)})) == ''
            assert proc.wait(timeout=5)==2
        finally:
            finish(proc)
        # Generation, description and effective validation share one settings
        # owner without reusing a project's source or performing a write.
        import hashlib
        installed = root / 'installed'; installed.mkdir()
        base = installed / 'base'; base.mkdir()
        agent = installed / 'agent'; agent.mkdir()
        (base / 'pack.cpack').write_text('pack Confectory.AIConnection version "1" { standalone false; element Connection object "Connection.celem"; }')
        (base / 'Connection.celem').write_text('object Confectory.AIConnection::Connection {}')
        (agent / 'pack.cpack').write_text('pack Test.Agent version "1" { standalone false; dependency Confectory.AIConnection version "1"; element Connection object "Connection.celem"; }')
        (agent / 'Connection.celem').write_text('object Test.Agent::Connection extends Confectory.AIConnection::Connection {}')
        manifest = installed / 'project.cpack'
        manifest.write_text('project Test.Install version "1" { standalone false; registry Confectory.AIConnection "base/pack.cpack"; registry Test.Agent "agent/pack.cpack"; }')
        connection = 'Test.Agent::Connection'
        settings = root / 'ai-settings' / hashlib.sha256(connection.encode()).hexdigest()[:16] / 'project.cpack'
        generation = dict(operation='connectionSettings', project=str(manifest), id=connection, settingsProject=str(settings))
        proc = start()
        try:
            proposed = json.loads(send(proc, dict(generation,presentation=True)))
            assert proposed['ok'], proposed
            assert proposed['result']['presentation']['status']=='available', proposed
            # The ordinary generation result is identical apart from its read projection.
            ordinary_generation = dict(proposed['result']); presentation = ordinary_generation.pop('presentation')
            assert ordinary_generation['manifest'] == json.loads(subprocess.run(HOST, input=json.dumps(generation), text=True, capture_output=True, timeout=20, check=True).stdout)['result']['manifest']
            assert not settings.parent.exists(), 'generation is only a proposal'
            settings.parent.mkdir(parents=True)
            pair = proposed['result']; settings.write_text(pair['manifest'])
            source = settings.parent / 'Settings.celem'; source.write_text(pair['source'])
            described = json.loads(send(proc, dict(operation='describe', project=str(settings), metadataOnly=True)))
            assert described['ok'] and described['result']['namespace']=='Confectory.AISettings', described
            inspection = dict(operation='inspectEffective', project=str(settings), manifest=pair['manifest'], id='Confectory.AISettings::Settings', kind='object', text=pair['source'], drafts=[], schemaView=True)
            validated = json.loads(send(proc, inspection))
            assert validated['ok'] and validated['result']['effective']['status']=='available', validated
            for key in ('schemaModel','fields','data','values','requirements','providers'):
                assert presentation[key]==validated['result']['effective'][key], key
            repair = dict(operation='connectionSettingsRepair', project=str(manifest), id=connection,
                          settingsProject=str(settings), repository=str(root), manifest=pair['manifest'], text=pair['source'])
            repaired = json.loads(send(proc, repair))
            assert repaired['ok'] and repaired['result']['state']=='unchanged', repaired
            combined = json.loads(send(proc, dict(inspection, operation='connectionRepairSchema', connectionRepair=repair)))
            assert combined['ok'] and combined['result']['repair']['state']=='unchanged' and combined['result']['effective']['status']=='available', combined
            assert send(proc, request(b)) == '' and proc.wait(timeout=5) == 2
        finally:
            finish(proc)
        proc = start()
        try:
            assert send(proc, dict(generation,settingsProject=str(a)))=='' and proc.wait(timeout=5)==2
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
    print('PASS read stream: connection proposal/repair/schema owner, metadata activation, inventory, live project view and relation map refresh, ordinary CLI, external schema/manifest, owner isolation, operation boundary, EOF and idle retirement')
