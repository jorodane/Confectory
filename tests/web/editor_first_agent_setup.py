"""Responses is the first provider opened, with zero Agents and isolated profiles.

Uses the production runtime. Registration saves local configuration only; no provider,
account, login, paid model request, project or permission grant is exercised.
"""
import hashlib, json, os, pathlib, re, shutil, signal, subprocess, sys, tempfile, time, urllib.request
from playwright.sync_api import sync_playwright, expect

expect.set_options(timeout=30000)
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text())
root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-first-agent-ui-'))
connection='Confectory.Agent.Responses::Connection';errors=[];external=[];evidence=[]
owned=root/'installed-editor';editor=owned/'examples/editor-home';editor.mkdir(parents=True)
(owned/'targets/dotnet').mkdir(parents=True)
(owned/'targets/dotnet/pack.cpack').write_text('pack Owned.Marker version "1" {standalone false;}')
for file in (repo/'examples/editor-home').glob('*.celem'):shutil.copy2(file,editor/file.name)
shutil.copytree(repo/'examples/editor-home/ui',editor/'ui')
pack=root/'installed-responses';shutil.copytree(repo/'packs/agent-responses',pack)
pack_path=pack/'pack.cpack';pack_source=pack_path.read_text()
schema_path=pack/'Settings.celem';schema_source=schema_path.read_text()
manifest=(repo/'examples/editor-home/project.cpack').read_text().replace('../../',str(repo)+'/')
manifest=manifest.replace(json.dumps(str(repo/'packs/agent-responses/pack.cpack')),json.dumps(str(pack_path)))
# Installed/discoverable does not imply a root-project direct dependency.
manifest=re.sub(r'dependency\s+Confectory\.Agent\.(Responses|Codex)\s+version\s+"[^"\n]*"\s*;','',manifest)
(editor/'project.cpack').write_text(manifest)

def state(url):
    origin,token=url.split('/#')
    def send(body):
        req=urllib.request.Request(origin+'/api/request',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':token})
        with urllib.request.urlopen(req,timeout=20) as response:return json.load(response)
    for _ in range(400):
        mounted=send({'op':'mount'})
        if mounted.get('error',{}).get('code')=='busy':time.sleep(.01);continue
        assert mounted['ok'],mounted;break
    else:raise AssertionError('read-only mount busy')
    try:return mounted['state']
    finally:assert send({'op':'dispose','view':mounted['view']})['ok']

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu'])
    try:
        for scenario in ('fresh','missing-installed-schema','existing-invalid','old-registry','custom-old-registry','fresh-compound-missing'):
            storage=root/scenario/'storage';settings=storage/'ai-settings'/hashlib.sha256(connection.encode()).hexdigest()[:16]
            pack_path.write_text(pack_source)
            schema_path.write_text(schema_source)
            env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(owned),CONFECTORY_ENTRY_STORAGE=str(storage),CONFECTORY_HOME_STORAGE=str(storage),CONFECTORY_MCP_DIRECTORY=str(root/scenario/'instances'),CONFECTORY_ELEMENT_AUTHORING_HOST=str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll'),CONFECTORY_PROJECT_EXECUTION_HOST=str(repo/'targets/project-execution-host/bin/Release/net10.0/Confectory.ProjectExecutionHost.dll'));env.pop('CONFECTORY_WEB_PROJECT',None)
            original_manifest=None;original_source=None
            if scenario in ('existing-invalid','old-registry','custom-old-registry'):
                generated=subprocess.run([env['CONFECTORY_DOTNET'],env['CONFECTORY_ELEMENT_AUTHORING_HOST']],input=json.dumps({'operation':'connectionSettings','project':str(editor/'project.cpack'),'id':connection}),text=True,capture_output=True,check=True,env=env)
                generated=json.loads(generated.stdout);assert generated['ok'],generated
                original_manifest=generated['result']['manifest'];original_source='object Confectory.AISettings::Settings extends '+connection+' {data model = "preserved-existing-input";}\n'
                settings.mkdir(parents=True);(settings/'Settings.celem').write_text(original_source)
                if scenario=='existing-invalid':invalid=re.sub(r'element\s+Settings\s+object\s+"Settings\.celem";','',original_manifest)
                else:
                    invalid=re.sub(r'registry\s+Confectory\.InstantTable\s+"[^"\n]*"\s*;\s*','',original_manifest)
                    invalid=re.sub(r'dependency\s+Confectory\.InstantTable\s+version\s+"[^"\n]*"\s*;\s*','',invalid)
                    if scenario=='custom-old-registry':invalid+='// owned custom manifest\n'
                assert invalid!=original_manifest
                (settings/'project.cpack').write_text(invalid)
            else:assert not settings.exists()
            if scenario=='missing-installed-schema':
                broken=re.sub(r'element\s+Settings\s+schema\s+"Settings\.celem";','',pack_source);assert broken!=pack_source;pack_path.write_text(broken)
            if scenario=='fresh-compound-missing':schema_path.write_text(schema_source.replace('{','{ field unresolved single compound Missing.Installed::Details;'))
            log_path=root/scenario/'host.log';log_path.parent.mkdir(parents=True,exist_ok=True);log=log_path.open('w')
            host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            page=browser.new_page(viewport={'width':1440,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)));invocations=[]
            page.on('request',lambda request:invocations.append(request.post_data_json['endpoint']) if request.url.endswith('/api/request') and request.post_data_json.get('op')=='invoke' else None)
            try:
                for _ in range(600):
                    urls=[line.split(' ',1)[1] for line in log_path.read_text().splitlines() if line.startswith('CONFECTORY_WEB_UI ')]
                    if urls:url=urls[-1];break
                    assert host.poll() is None,log_path.read_text();time.sleep(.1)
                else:raise AssertionError('production host startup timeout')
                origin=url.split('/#')[0]
                def route(request):
                    if request.request.url.startswith(origin+'/') or request.request.url.startswith('data:'):request.continue_()
                    else:external.append(request.request.url);request.abort()
                page.route('**/*',route);page.goto(url)
                expect(page.locator('.welcome')).to_have_attribute('aria-busy','false');expect(page.locator('#connect')).to_be_enabled()
                assert state(url)['helperAgents']['agents']==[]
                # Responses is the very first Agent choice; no Codex form is opened.
                page.locator('#connect').click();dialog=page.get_by_role('dialog',name='Agent 추가',exact=True)
                dialog.get_by_role('button',name='OpenAI Responses',exact=True).click()
                if scenario not in ('fresh','old-registry'):
                    diagnostic=dialog.locator('[data-connection-error]');code='connection_declarations_unavailable' if scenario=='missing-installed-schema' else 'connection_settings_invalid'
                    expect(diagnostic).to_have_attribute('data-code',code);expect(diagnostic).to_be_visible();failed=state(url)
                    assert failed['operationError']['mode']==('new' if scenario in ('missing-installed-schema','fresh-compound-missing') else 'existing')
                    assert str(root) not in diagnostic.inner_text() and '기존 연결 설정의 선언' not in diagnostic.inner_text()
                    if scenario in ('custom-old-registry','fresh-compound-missing'):
                        assert failed['operationError']['cause']=='MISSING_NAMESPACE'
                        missing='Missing.Installed' if scenario=='fresh-compound-missing' else 'Confectory.InstantTable'
                        expect(diagnostic).to_contain_text('누락된 네임스페이스: '+missing)
                        assert failed['operationError']['namespaceDiagnostic']['missingNamespace']==missing
                        if scenario=='custom-old-registry':expect(diagnostic).to_contain_text('참조 팩: Confectory.EditorHome.Model');assert not list(settings.glob('project.cpack.before-*'))
                        else:expect(diagnostic).to_contain_text('첫 설정 화면');expect(diagnostic).to_contain_text('참조: Missing.Installed::Details')
                        page.screenshot(path=str(root/scenario/'missing-namespace.png'))
                    if scenario=='missing-installed-schema':assert not settings.exists();pack_path.write_text(pack_source)
                    elif scenario=='fresh-compound-missing':schema_path.write_text(schema_source)
                    else:
                        assert (settings/'Settings.celem').read_text()==original_source and (settings/'project.cpack').read_text()==invalid
                        (settings/'project.cpack').write_text(original_manifest)
                    diagnostic.get_by_role('button',name='설정 다시 읽기').click()
                expect(dialog.locator('[data-connection-field="model"]')).to_be_visible();expect(dialog.locator('[data-connection-error]')).to_be_hidden()
                expect(dialog).to_have_attribute('data-connection-mode','existing' if scenario in ('existing-invalid','old-registry','custom-old-registry') else 'new')
                for field in ('endpoint','maxRounds','credentialReference'):expect(dialog.locator('[data-connection-field="'+field+'"]').first).to_be_visible()
                assert state(url)['helperAgents']['agents']==[] and state(url)['projectId']==''
                assert 'dependency Confectory.Agent.Responses version ' in (settings/'project.cpack').read_text()
                if scenario in ('existing-invalid','old-registry','custom-old-registry'):expect(dialog.locator('[data-connection-field="model"]')).to_have_value('preserved-existing-input')
                if scenario=='old-registry':
                    backups=list(settings.glob('project.cpack.before-*'));assert len(backups)==1 and backups[0].read_text()==invalid and (settings/'Settings.celem').read_text()==original_source
                dialog.locator('[data-connection-field="model"]').fill('owned-first-registration')
                dialog.locator('[data-connection-field="endpoint"]').fill('http://127.0.0.1:1/v1/responses')
                dialog.locator('[data-connection-cancel]').click();expect(dialog).to_have_count(0)
                page.locator('#connect').click();dialog=page.get_by_role('dialog',name='Agent 추가',exact=True);dialog.get_by_role('button',name='OpenAI Responses',exact=True).click()
                expect(dialog.locator('[data-connection-field="model"]')).to_have_value('owned-first-registration')
                # This saves configuration and registers an unauthenticated local row only.
                dialog.locator('[data-agent-register]').click();expect(dialog.locator('[data-agent-registration-state]')).to_contain_text('Agent 등록됨')
                actual=state(url);assert len(actual['helperAgents']['agents'])==1 and actual['helperAgents']['agents'][0]['accountVerified'] is False and actual['projectId']==''
                expect(dialog).to_have_attribute('data-connection-mode','existing');page.screenshot(path=str(root/scenario/'registered.png'))
                saved=(settings/'Settings.celem').read_bytes();dialog.locator('[data-connection-cancel]').click();page.reload();expect(page.locator('#add-agent')).to_be_enabled()
                page.locator('#add-agent').click();dialog=page.get_by_role('dialog',name='Agent 추가',exact=True);dialog.get_by_role('button',name='OpenAI Responses',exact=True).click()
                expect(dialog.locator('[data-connection-field="model"]')).to_have_value('owned-first-registration');expect(dialog).to_have_attribute('data-connection-mode','existing');assert (settings/'Settings.celem').read_bytes()==saved
                dialog.locator('[data-connection-cancel]').click()
                assert not any(x in invocations for x in ('attemptConnectionSetup','startConnectionCheck','startInstallation','startLogin','globalStart','mcpGrant'))
                evidence.append({'scenario':scenario,'checks':['Responses-first','zero prior Agents','actual inherited fields','cancel-reopen input retained','local unauthenticated registration','reload-existing settings retained'],'invocations':invocations})
            finally:
                page.close()
                if host.poll() is None:os.killpg(host.pid,signal.SIGTERM)
                host.wait(timeout=15);log.close()
    finally:browser.close()
assert errors==[] and external==[],(errors,external)
(root/'evidence.json').write_text(json.dumps({'scenarios':evidence,'pageErrors':errors,'externalRequests':external},indent=2,ensure_ascii=False))
print('PASS first Responses Agent UI: clean installed-pack setup, declaration/settings retry, local registration and reload; '+str(root))
