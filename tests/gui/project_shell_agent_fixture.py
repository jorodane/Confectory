"""Register a local Responses fixture through the existing editor API."""
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


def register_main_helper(command, repo, env, storage):
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
                assert not current['state']['helperAgents']['agents']
                state = call('connectionSetup', connection=AGENT)
                # Same uncontacted loopback endpoint used by the shell domain consumer.
                fields = {'model': 'owned-not-contacted', 'credentialReference': '',
                          'endpoint': 'http://127.0.0.1:1/responses'}
                for field, value in fields.items():
                    revision = state['connectionSetup']['schema']['revision']
                    state = call('editConnectionSetup', connection=AGENT, path=[field], value=value, revision=revision)
                call('saveConnectionSetup', connection=AGENT)
                state = call('helperGlobal', action='register', connection=AGENT)
                assert [row['id'] for row in state['helperAgents']['agents']]==[AGENT]
                state = call('helperGlobal', action='import', agent=AGENT)
                assert state['helperAgents']['assignments']['main-helper']==AGENT
                assert not state['helperAgents']['turns']
            finally:
                send({'op': 'dispose', 'view': view})
        finally:
            if host.poll() is None:
                os.killpg(host.pid, signal.SIGTERM)
                host.wait(timeout=20)
