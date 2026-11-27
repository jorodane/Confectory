"""Real desktop link output, relocated installation, and verified preview invalidation.

Arguments: built source repository and ordinary Linux build report. Never logs in,
contacts a service, or edits original installation/profile files.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time

from playwright.sync_api import sync_playwright, expect
from editor_navigation import goto_editor

repo = Path(sys.argv[1]).resolve()
report = json.loads(Path(sys.argv[2]).read_text())
root = Path(tempfile.mkdtemp(prefix='confectory-linked-preview-'))
install, profile, runtime = root/'install', root/'profile', root/'runtime'
ignored = shutil.ignore_patterns('.confectory', 'bin', 'obj', '.git', '__pycache__')
for relative in ('packs', 'targets', 'examples/editor-home'):
    shutil.copytree(repo/relative, install/relative, ignore=ignored)
original_runtime = Path(report['run'][-1]).parent
shutil.copytree(original_runtime, runtime)
resource = runtime/'connection-preview-v1.json'
assert resource.is_file(), 'ordinary desktop build must emit the resource'
artifact = json.loads(resource.read_text())
assert artifact['formatVersion'] == 1 and len(artifact['entries']) >= 2
assert str(repo) not in resource.read_text(), 'resource must not reveal build-machine paths'
# A sidecar is not authoritative: remove it, then later replace it with an old
# invalid version. The application assembly alone owns the read-only model.
resource.unlink()
command = [str(runtime/Path(part).name) if Path(part).parent==original_runtime else part for part in report['run']]
env = os.environ.copy()
env.update(CONFECTORY_UI='web', CONFECTORY_EDITOR_REPO=str(install), CONFECTORY_HOME_STORAGE=str(profile), CONFECTORY_ENTRY_STORAGE=str(profile), CONFECTORY_MCP_DIRECTORY=str(root/'instances'), CONFECTORY_UI_TRACE='1')
env.pop('CONFECTORY_WEB_PROJECT', None)
codex = 'Confectory.Agent.Codex::Connection'
responses = 'Confectory.Agent.Responses::Connection'

def settings(connection):
    return profile/'ai-settings'/hashlib.sha256(connection.encode()).hexdigest()[:16]

def trace(path, before):
    return path.read_text()[before:]

def open_form(page, name):
    expect(page.locator('#add-agent')).to_be_enabled()
    page.locator('#add-agent').click()
    dialog=page.get_by_role('dialog', name='Agent 추가', exact=True)
    dialog.get_by_role('button', name=name, exact=True).click()
    return dialog

def close(dialog):
    dialog.locator('[data-connection-cancel]').click()
    expect(dialog).to_have_count(0)

def linked(log, before):
    observed=trace(log,before)
    assert 'CONFECTORY_CONNECTION_LINKED_PREVIEW' in observed, observed
    assert '"operation":"connectionSettings"' not in observed, observed

expect.set_options(timeout=30000)
with sync_playwright() as playwright, playwright.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu']) as browser:
    for iteration in range(2):
        log=root/f'host-{iteration}.log'
        with log.open('w') as output:
            host=subprocess.Popen(command,cwd=install,env=env,stdout=output,stderr=subprocess.STDOUT,start_new_session=True)
            page=browser.new_page(viewport={'width':1360,'height':900})
            try:
                for _ in range(600):
                    urls=[line.split(' ',1)[1] for line in log.read_text().splitlines() if line.startswith('CONFECTORY_WEB_UI ')]
                    if urls:break
                    assert host.poll() is None,log.read_text();time.sleep(.05)
                else:raise AssertionError('host startup timeout')
                origin=urls[-1].split('/#')[0]
                page.route('**/*',lambda route:route.continue_() if route.request.url.startswith(origin+'/') else route.abort())
                goto_editor(page,urls[-1])
                before=len(log.read_text());dialog=open_form(page,'Codex');expect(dialog.locator('[data-cli-login]')).to_be_enabled();linked(log,before);assert not settings(codex).exists();close(dialog)
                before=len(log.read_text());dialog=open_form(page,'Codex');expect(dialog.locator('[data-cli-login]')).to_be_enabled();assert 'CONFECTORY_CONNECTION_PREVIEW_REUSED' in trace(log,before);close(dialog)
                before=len(log.read_text());dialog=open_form(page,'OpenAI Responses');field=dialog.locator('[data-connection-field="model"]');expect(field).to_be_editable();original_model=field.input_value();linked(log,before);assert not settings(responses).exists();close(dialog)
                if iteration==0:
                    # Valid external declaration changes must be read through
                    # the ordinary source path, not the prepared defaults.
                    source=install/'packs/agent-responses/Connection.celem';original=source.read_bytes();text=original.decode('utf-8');assert 'data model =' not in text
                    source.write_text(text.rstrip()[:-1]+' data model = "fixture-external-model"; }')
                    before=len(log.read_text());dialog=open_form(page,'OpenAI Responses');expect(dialog.locator('[data-connection-field="model"]')).to_have_value('fixture-external-model');assert '"operation":"connectionSettings"' in trace(log,before);assert 'CONFECTORY_CONNECTION_LINKED_PREVIEW' not in trace(log,before);close(dialog)
                    source.write_bytes(original)
                    before=len(log.read_text());dialog=open_form(page,'OpenAI Responses');expect(dialog.locator('[data-connection-field="model"]')).to_have_value(original_model);linked(log,before);close(dialog)
                    # Broken external declaration must expose the existing
                    # diagnostic; restore/retry makes the exact resource valid.
                    pack=install/'packs/agent-codex/pack.cpack';original=pack.read_bytes();pack.write_bytes(original.replace(b'element Settings schema "Settings.celem";',b''))
                    before=len(log.read_text());dialog=open_form(page,'Codex');expect(dialog.locator('[data-connection-error]')).to_be_visible();assert '"operation":"connectionSettings"' in trace(log,before);assert 'CONFECTORY_CONNECTION_LINKED_PREVIEW' not in trace(log,before)
                    pack.write_bytes(original);before=len(log.read_text());dialog.locator('[data-connection-error]').get_by_role('button',name='연결 화면 다시 열기').click();expect(dialog.locator('[data-cli-login]')).to_be_enabled();restored=trace(log,before);assert ('CONFECTORY_CONNECTION_LINKED_PREVIEW' in restored or 'CONFECTORY_CONNECTION_PREVIEW_REUSED' in restored) and '"operation":"connectionSettings"' not in restored, restored;close(dialog)
                    resource.write_text('{"formatVersion":0,"entries":{}}')
                assert not settings(codex).exists() and not settings(responses).exists()
                if iteration==1:
                    # Pending real input cannot be admitted using an externally
                    # changed installed model. After exact restoration, the
                    # ordinary Save still performs a fresh schema query.
                    dialog=open_form(page,'OpenAI Responses');field=dialog.locator('[data-connection-field="model"]');expect(field).to_be_editable();field.fill('saved-linked-fixture')
                    source=install/'packs/agent-responses/Connection.celem';original=source.read_bytes();source.write_text(original.decode('utf-8').rstrip()[:-1]+' data model = "external-while-editing"; }')
                    dialog.locator('[data-connection-save]').click();expect(dialog.locator('[data-connection-error]')).to_be_visible();expect(field).to_have_value('saved-linked-fixture');assert not settings(responses).exists()
                    source.write_bytes(original);before=len(log.read_text());dialog.locator('[data-connection-save]').click();expect(dialog.locator('[data-connection-save]')).to_be_enabled();expect(field).to_have_value('saved-linked-fixture')
                    assert (settings(responses)/'project.cpack').is_file() and (settings(responses)/'Settings.celem').is_file()
                    saved_trace=trace(log,before)
                    assert '"operation":"inspectEffective"' in saved_trace
                    # The exact generated pair was checked before creation by the
                    # same selected-connection repair reader. Do not enumerate
                    # the installed catalog twice on this fresh admission.
                    assert saved_trace.count('"operation":"connectionSettingsRepair"')==1, saved_trace
                    assert '"operation":"connectionCatalog"' not in saved_trace, saved_trace
                    close(dialog)
            finally:
                page.close()
                if host.poll() is None:os.killpg(host.pid,signal.SIGTERM)
                host.wait(timeout=15)
print('PASS embedded preview, relocated install, ignored missing/old sidecar, external mutation/error/recovery, restart, preview no writes and explicit save:',root)
