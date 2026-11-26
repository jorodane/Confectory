from editor_navigation import goto_editor
"""Actual Agent clicks: no authoring for presentation, safe failure/retry and late-close fencing.

All settings and hosts belong to this fixture. No real account, installation or network request.
Durations are evidence; regression assertions use behavior/counts rather than machine speed.
"""
import hashlib, json, os, pathlib, re, shutil, signal, subprocess, sys, tempfile, time, urllib.request, uuid
from playwright.sync_api import sync_playwright, expect

expect.set_options(timeout=30000)
repo=pathlib.Path(sys.argv[1]).resolve()
report=json.loads(pathlib.Path(sys.argv[2]).read_text())
root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-connection-latency-'))
codex='Confectory.Agent.Codex::Connection'
original='object Confectory.AISettings::Settings extends '+codex+' {data model = "preserved-user-input";}\n'
evidence=[]; errors=[]

def state(url, endpoint=None, payload=None):
    origin,token=url.split('/#')
    def send(body):
        req=urllib.request.Request(origin+'/api/request',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':token})
        with urllib.request.urlopen(req,timeout=20) as response:return json.load(response)
    for _ in range(300):
        mounted=send({'op':'mount'})
        if mounted.get('error',{}).get('code')=='busy':time.sleep(.01);continue
        assert mounted['ok'],mounted;break
    else:raise AssertionError('read-only mount busy')
    try:
        if endpoint is None:return mounted['state']
        request_id=uuid.uuid4().hex
        envelope={'view':mounted['view'],'scope':mounted['scope']}
        assert send(dict(envelope,op='invoke',endpoint=endpoint,requestId=request_id,expectedRevision=mounted['revision'],input=payload))['ok']
        for _ in range(400):
            reply=send(dict(envelope,op='update'))
            assert reply['ok'],reply
            for result in reply.get('results',[]):
                if result['requestId']==request_id:return result
            time.sleep(.01)
        raise AssertionError('Connection invocation did not settle')
    finally:assert send({'op':'dispose','view':mounted['view']})['ok']

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu'])
    try:
        for scenario in ('fresh','partial-settings','manifest-only','missing-authoring'):
            owned=root/scenario;owned.mkdir();storage=owned/'storage'
            settings=storage/'ai-settings'/hashlib.sha256(codex.encode()).hexdigest()[:16]
            if scenario=='fresh':
                # A writable installation overlay owns only the Codex pack and root declaration.
                install=owned/'install';editor=install/'examples'/'editor-home';editor.mkdir(parents=True)
                for file in (repo/'examples'/'editor-home').glob('*.celem'):shutil.copy2(file,editor/file.name)
                shutil.copytree(repo/'packs',install/'packs');shutil.copytree(repo/'examples'/'editor-home'/'ui',editor/'ui')
                codex_pack=install/'packs'/'agent-codex'
                declaration=(repo/'examples'/'editor-home'/'project.cpack').read_text().replace('../../',str(repo)+'/').replace(str(repo/'packs'/'agent-codex'/'pack.cpack'),str(codex_pack/'pack.cpack'))
                (editor/'project.cpack').write_text(declaration)
                marker=install/'targets'/'dotnet';marker.mkdir(parents=True);(marker/'pack.cpack').write_text('pack Owned.Marker version \"1\" {standalone false;}')
            if scenario=='partial-settings':
                settings.mkdir(parents=True);(settings/'Settings.celem').write_text(original)
            env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_ENTRY_STORAGE=str(storage),CONFECTORY_HOME_STORAGE=str(storage),CONFECTORY_MCP_DIRECTORY=str(owned/'instances'),CONFECTORY_UI_TRACE='1');env.pop('CONFECTORY_WEB_PROJECT',None)
            if scenario=='fresh':env['CONFECTORY_EDITOR_REPO']=str(install)
            if scenario=='manifest-only':
                result=subprocess.run([env['CONFECTORY_DOTNET'],str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps({'operation':'connectionSettings','project':str(repo/'examples/editor-home/project.cpack'),'id':codex}),text=True,capture_output=True,check=True,env=env)
                generated=json.loads(result.stdout);assert generated['ok'],generated
                partial_manifest=generated['result']['manifest'];settings.mkdir(parents=True);(settings/'project.cpack').write_text(partial_manifest)
            if scenario=='missing-authoring':env['CONFECTORY_ELEMENT_AUTHORING_HOST']=str(owned/'missing'/'Confectory.ElementAuthoring.dll')
            log_path=owned/'host.log';log=log_path.open('w');host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            page=browser.new_page(viewport={'width':1360,'height':900});page.on('pageerror',lambda e:errors.append(str(e)))
            invocations=[]
            def request(req):
                if req.url.endswith('/api/request'):
                    body=req.post_data_json
                    if body.get('op')=='invoke':invocations.append(body['endpoint'])
            page.on('request',request)
            page.add_init_script("globalThis.confectoryWebUITrace=[];")
            try:
                for _ in range(600):
                    urls=[line.split(' ',1)[1] for line in log_path.read_text().splitlines() if line.startswith('CONFECTORY_WEB_UI ')]
                    if urls:url=urls[-1];break
                    assert host.poll() is None,log_path.read_text();time.sleep(.1)
                else:raise AssertionError('host startup timeout')
                goto_editor(page,url);expect(page.locator('#add-agent')).to_be_enabled()
                before=len(invocations)
                before_processes=log_path.read_text().count('"stage":"authoring-process"')
                # Installed cards and the engine route require no source scan or provider settings.
                for iteration in range(3):
                    page.locator('#add-agent').click();dialog=page.get_by_role('dialog',name='Agent 추가',exact=True);expect(dialog).to_be_visible()
                    expect(dialog.locator('[data-connection-choice]')).to_have_count(2)
                    expect(dialog.locator('[data-mcp-panel]')).to_have_count(0)
                    dialog.locator('[data-connection-cancel]').click();expect(dialog).to_have_count(0)
                assert invocations[before:]==[],invocations[before:]
                assert log_path.read_text().count('"stage":"authoring-process"')==before_processes
                if scenario=='manifest-only':assert (settings/'project.cpack').read_text()==partial_manifest
                else:assert not (settings/'project.cpack').exists()
                if scenario=='partial-settings':assert (settings/'Settings.celem').read_text()==original
                else:assert not (settings/'Settings.celem').exists()
                if scenario=='fresh':
                    unknown='Fixture.Unknown::Connection'
                    rejected=state(url,'connectionSetup',{'connection':unknown})
                    assert not rejected['ok'],rejected
                    assert state(url)['operationError']['code']=='connection_declarations_unavailable'
                    assert not (storage/'ai-settings'/hashlib.sha256(unknown.encode()).hexdigest()[:16]).exists()
                first_trace=log_path.read_text()
                # A double entry event owns exactly one modal; a closed dialog cannot render later.
                page.locator('#add-agent').evaluate('(button)=>{button.click();button.click();}')
                dialog=page.get_by_role('dialog',name='Agent 추가',exact=True);expect(dialog).to_have_count(1)
                dialog.get_by_role('button',name='Codex',exact=True).click()
                if scenario!='fresh':
                    diagnostic=dialog.locator('[data-connection-error]');code='connection_settings_incomplete' if scenario in ('partial-settings','manifest-only') else 'authoring_host_missing'
                    expect(diagnostic).to_have_attribute('data-code',code);expect(diagnostic).to_be_visible()
                    assert str(owned) not in diagnostic.inner_text()
                    snapshot=state(url);assert str(owned) not in json.dumps(snapshot.get('operationError'));assert snapshot['sourceError'] is None
                    if scenario=='manifest-only':
                        assert (settings/'project.cpack').read_text()==partial_manifest
                        assert not (settings/'Settings.celem').exists()
                        dialog.locator('[data-connection-cancel]').click();expect(dialog).to_have_count(0);continue
                    assert not (settings/'project.cpack').exists()
                    if scenario=='missing-authoring':
                        dialog.locator('[data-connection-cancel]').click();continue
                    assert (settings/'Settings.celem').read_text()==original
                    # Supply the missing fixture-owned recovery material; retry the failed action.
                    request_body={'operation':'connectionSettings','project':str(repo/'examples/editor-home/project.cpack'),'id':codex}
                    generated=subprocess.run([env['CONFECTORY_DOTNET'],str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(request_body),text=True,capture_output=True,check=True,env=env)
                    recovery=json.loads(generated.stdout);assert recovery['ok'],recovery
                    (settings/'project.cpack').write_text(recovery['result']['manifest'])
                    diagnostic.get_by_role('button',name='연결 화면 다시 열기').click()
                expect(dialog.locator('[data-cli-login]')).to_be_enabled()
                if scenario=='fresh':
                    created_trace=log_path.read_text()[len(first_trace):]
                    assert created_trace.count('"operation":"connectionSettings"')==1
                    assert '"operation":"connectionCatalog"' not in created_trace
                    assert '"operation":"connectionSettingsRepair"' not in created_trace
                    assert created_trace.count('"operation":"inspectEffective"')==1
                expect(dialog.locator('input,select,textarea,[data-connection-advanced],[data-connection-save],[data-installation-candidates],[data-home-candidates]')).to_have_count(0)
                dialog.locator('[data-connection-cancel]').click();expect(dialog).to_have_count(0)
                if scenario=='fresh':
                    # A healthy reopen verifies the exact installed and settings snapshots
                    # and reuses the previously validated presentation schema.
                    expect(page.locator('#add-agent')).to_be_enabled()
                    before_trace=log_path.read_text()
                    page.locator('#add-agent').click();dialog=page.get_by_role('dialog',name='Agent 추가',exact=True)
                    dialog.get_by_role('button',name='Codex',exact=True).click()
                    expect(dialog.locator('[data-cli-login]')).to_be_enabled()
                    reopened_trace=log_path.read_text()[len(before_trace):]
                    assert '"operation":"connectionRepairSchema"' not in reopened_trace
                    assert "CONFECTORY_SCHEMA_REUSED" in reopened_trace
                    assert '"operation":"connectionSettingsRepair"' not in reopened_trace
                    assert '"operation":"inspectEffective"' not in reopened_trace
                    assert '"operation":"connectionCatalog"' not in reopened_trace
                    dialog.locator('[data-connection-cancel]').click();expect(dialog).to_have_count(0)
                    # The installed declaration is also part of the proof. A missing
                    # schema must not display the cached successful form.
                    installed_manifest=codex_pack/'pack.cpack';installed_original=installed_manifest.read_text()
                    installed_manifest.write_text(installed_original.replace('element Settings schema "Settings.celem";', ''))
                    page.locator('#add-agent').click();dialog=page.get_by_role('dialog',name='Agent 추가',exact=True)
                    dialog.get_by_role('button',name='Codex',exact=True).click()
                    expect(dialog.locator('[data-connection-error]')).to_be_visible()
                    expect(dialog.locator('[data-cli-login]')).to_have_count(0)
                    installed_manifest.write_text(installed_original)
                    dialog.locator('[data-connection-error]').get_by_role('button',name='연결 화면 다시 열기').click()
                    expect(dialog.locator('[data-cli-login]')).to_be_enabled()
                    dialog.locator('[data-connection-cancel]').click();expect(dialog).to_have_count(0)
                    # A separate local change while the form is closed must still be
                    # invalidate the exact model proof and take the normal repair path.
                    manifest=settings/'project.cpack';source=settings/'Settings.celem'
                    current_manifest=manifest.read_text();current_source=source.read_bytes()
                    altered,count=re.subn(r'dependency\s+Confectory\.Agent\.Codex\s+version\s+"[^"\n]*"\s*;', '', current_manifest)
                    assert count==1
                    manifest.write_text(altered)
                    expect(page.locator('#add-agent')).to_be_enabled()
                    before_trace=log_path.read_text().count('"operation":"connectionCatalog"')
                    page.locator('#add-agent').click();dialog=page.get_by_role('dialog',name='Agent 추가',exact=True)
                    dialog.get_by_role('button',name='Codex',exact=True).click()
                    expect(dialog.locator('[data-cli-login]')).to_be_enabled()
                    assert log_path.read_text().count('"operation":"connectionCatalog"')==before_trace
                    backups=list(settings.glob('project.cpack.before-*'))
                    assert len(backups)==1 and backups[0].read_text()==altered
                    assert 'dependency Confectory.Agent.Codex version ' in manifest.read_text()
                    assert source.read_bytes()==current_source
                    dialog.locator('[data-connection-cancel]').click();expect(dialog).to_have_count(0)
                # Input retention still applies to the separate Responses form.
                page.locator('#add-agent').click();dialog=page.get_by_role('dialog',name='Agent 추가',exact=True)
                dialog.get_by_role('button',name='OpenAI Responses',exact=True).click();field=dialog.locator('[data-connection-field="model"]');field.fill('unapplied-kept-across-close')
                dialog.locator('[data-connection-cancel]').click();expect(dialog).to_have_count(0)
                page.locator('#add-agent').click();dialog=page.get_by_role('dialog',name='Agent 추가',exact=True);dialog.get_by_role('button',name='OpenAI Responses',exact=True).click()
                expect(dialog.locator('[data-connection-field="model"]')).to_have_value('unapplied-kept-across-close')
                dialog.locator('[data-connection-cancel]').click();expect(page.locator('#add-agent')).to_be_enabled()
                # Close after the backend request starts, before it can return its settings.
                page.locator('#add-agent').click();dialog=page.get_by_role('dialog',name='Agent 추가',exact=True);dialog.get_by_role('button',name='Codex',exact=True).click()
                dialog.locator('[data-connection-cancel]').click();expect(dialog).to_have_count(0);expect(page.locator('#add-agent')).to_be_enabled()
                page.locator('#add-agent').click();dialog=page.get_by_role('dialog',name='Agent 추가',exact=True);dialog.get_by_role('button',name='Codex',exact=True).click();expect(dialog.locator('[data-cli-login]')).to_be_enabled()
                assert state(url)['projectId']==''
                dialog.locator('[data-connection-cancel]').click()
                if scenario=='partial-settings':assert (settings/'Settings.celem').read_text()==original
            finally:
                evidence.append({'scenario':scenario,'invocations':invocations,'clientTimings':page.evaluate('globalThis.confectoryWebUITrace||[]') if not page.is_closed() else []})
                page.close()
                if host.poll() is None:os.killpg(host.pid,signal.SIGTERM)
                host.wait(timeout=15);log.close()
    finally:browser.close()
assert errors==[],errors
(root/'evidence.json').write_text(json.dumps(evidence,indent=2,ensure_ascii=False))
print('PASS Agent presentation zero invokes/processes; partial settings/missing host diagnostics; exact retry, retained input and late close; '+str(root))
