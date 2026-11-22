"""Configure test Agents through the existing editor API without connecting them."""
import json
import os
from pathlib import Path
import signal
import subprocess
import time
from urllib.parse import urlsplit
from urllib.request import ProxyHandler, Request, build_opener
from uuid import uuid4


AGENT = 'Confectory.Agent.Responses::Connection'
CODEX = 'Confectory.Agent.Codex::Connection'


def prepare_agents(command, repo, env, storage, *, register_codex=False):
    env = dict(env, CONFECTORY_UI='web', CONFECTORY_MCP_DIRECTORY=str(Path(storage) / 'fixture-instances'))
    env.pop('CONFECTORY_WEB_PROJECT', None)
    log_path = Path(storage) / 'fixture-agent-setup.log'
    with log_path.open('w', encoding='utf-8') as log:
        host = subprocess.Popen(command, cwd=repo, env=env, stdout=log,
                                stderr=subprocess.STDOUT, start_new_session=True)
        try:
            for _ in range(600):
                url = next((line.removeprefix('CONFECTORY_WEB_UI ') for line in log_path.read_text().splitlines()
                            if line.startswith('CONFECTORY_WEB_UI ')), None)
                if url:
                    break
                assert host.poll() is None, 'Fixture editor exited during Agent setup'
                time.sleep(.05)
            else:
                raise AssertionError('Fixture Agent setup startup deadline')

            origin, token = url.split('/#')
            parsed = urlsplit(origin)
            assert parsed.scheme == 'http' and parsed.hostname == '127.0.0.1'
            client = build_opener(ProxyHandler({}))

            def send(body):
                request = Request(origin+'/api/request', data=json.dumps(body).encode(), headers={
                    'Content-Type': 'application/json', 'X-Confectory-Session': token,
                })
                with client.open(request, timeout=30) as response:
                    reply = json.load(response)
                assert reply['ok'], reply.get('error')
                return reply

            current = send({'op': 'mount'})
            view, scope = current['view'], current['scope']

            def call(endpoint, **args):
                nonlocal current
                rid = uuid4().hex
                send({'op': 'invoke', 'view': view, 'scope': scope, 'requestId': rid,
                      'expectedRevision': current['revision'], 'endpoint': endpoint, 'input': args})
                deadline = time.monotonic()+30
                while time.monotonic()<deadline:
                    current = send({'op': 'update', 'view': view, 'scope': scope})
                    for result in current.get('results', []):
                        if result['requestId']==rid:
                            assert result['ok'], (endpoint, result.get('error'))
                            return current['state']
                    time.sleep(.03)
                raise AssertionError(f'Fixture request did not complete: {endpoint}')

            try:
                if register_codex:
                    assert [row['id'] for row in current['state']['helperAgents']['agents']] == [AGENT]
                    state = call('helperGlobal', action='register', connection=CODEX)
                    expected = {AGENT, CODEX}
                else:
                    assert not current['state']['helperAgents']['agents']
                    settings = {
                        # None of these provider destinations are contacted by the fixture.
                        AGENT: {'model': 'owned-not-contacted', 'credentialReference': '',
                                'endpoint': 'http://127.0.0.1:1/responses'},
                        CODEX: {'model': 'owned-not-contacted', 'credentialReference': 'codex:managed',
                                'connectionMethod': 'local-cli',
                                'managedHome': str(Path(storage) / 'unused-codex-home'),
                                'executable': str(Path(storage) / 'nonexistent-codex')},
                    }
                    for connection, fields in settings.items():
                        state = call('connectionSetup', connection=connection)
                        for field, value in fields.items():
                            revision = state['connectionSetup']['schema']['revision']
                            state = call('editConnectionSetup', connection=connection, path=[field], value=value, revision=revision)
                        call('saveConnectionSetup', connection=connection)
                    call('helperGlobal', action='register', connection=AGENT)
                    state = call('helperGlobal', action='import', agent=AGENT)
                    expected = {AGENT}
                registry = state['helperAgents']
                assert {row['id'] for row in registry['agents']} == expected
                assert not any(row['accountVerified'] for row in registry['agents'])
                assert registry['assignments']['main-helper'] == AGENT
                assert not registry['turns']
            finally:
                send({'op': 'dispose', 'view': view})
        finally:
            if host.poll() is None:
                os.killpg(host.pid, signal.SIGTERM)
                host.wait(timeout=20)
