"""Real EditorHome helper flow through an explicitly owned loopback HTTP fixture.

The fixture simulates service output; production packs, permissions and owners run unchanged.
"""
import http.server
import json
import os
import pathlib
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
from playwright.sync_api import sync_playwright, expect

expect.set_options(timeout=30000)
repo = pathlib.Path(sys.argv[1]).resolve()
report = json.loads(pathlib.Path(sys.argv[2]).read_text())
assert report['entry'] == 'Confectory.EditorHome::Main' and report['tool']['ok']
root = pathlib.Path(tempfile.mkdtemp(prefix='confectory-helper-ai-v318-'))
project = root / 'ordinary-button-game'
shutil.copytree(repo / 'examples/button-game', project, ignore=shutil.ignore_patterns('.confectory'))
manifest = project / 'project.cpack'
manifest.write_text(manifest.read_text().replace('../../', str(repo) + '/'))
before = {str(p.relative_to(project)): p.read_bytes() for p in project.rglob('*') if p.is_file()}
requests = []
fixture_errors = []
blocked = threading.Event()
release = threading.Event()

class Fixture(http.server.BaseHTTPRequestHandler):
 def log_message(self, *args): pass
 def do_POST(self):
  try:
   assert self.path == '/responses' and self.headers.get('Authorization') is None
   body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
   assert body['model'] == 'owned-helper-http-fixture'
   assert body['store'] is False and body['parallel_tool_calls'] is False
   request = json.loads(body['input'][0]['content'])
   assert request['kind'] == 'project-chat' and request['context']['projectId'] == request['projectId']
   assert all(key not in json.dumps(body) for key in ('toolCapability', 'credentialReference', 'authorization'))
   requests.append(request)
   if request['message'] == 'WAIT owned helper request':
    blocked.set()
    assert release.wait(20), 'Owned test did not release the HTTP response'
   if request['message'] == 'FAIL owned helper request':
    self.send_response(429); self.end_headers(); self.wfile.write(b'{"error":{"code":"owned_fixture_limit"}}'); return
   text = 'OWNED LOOPBACK FIXTURE: ' + request['context']['helper'] + ' / ' + request['message']
   response = json.dumps({'status': 'completed', 'output': [{'type': 'message', 'role': 'assistant', 'content': [{'type': 'output_text', 'text': text}]}]}).encode()
   self.send_response(200); self.send_header('Content-Type', 'application/json'); self.send_header('Content-Length', str(len(response))); self.end_headers(); self.wfile.write(response)
  except Exception as error:
   fixture_errors.append(repr(error)); self.send_error(500)

server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Fixture)
thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
endpoint = 'http://127.0.0.1:' + str(server.server_port) + '/responses'
env = os.environ.copy()
env.update(CONFECTORY_UI='web', CONFECTORY_EDITOR_REPO=str(repo), CONFECTORY_ENTRY_STORAGE=str(root / 'storage'), CONFECTORY_HOME_STORAGE=str(root / 'storage'), CONFECTORY_WEB_PROJECT=str(manifest))
if env.get('CONFECTORY_DOTNET'): env['PATH'] = str(pathlib.Path(env['CONFECTORY_DOTNET']).parent) + os.pathsep + env['PATH']
stream = (root / 'host.log').open('w')
host = subprocess.Popen(report['run'], cwd=repo, env=env, stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
try:
 deadline = time.monotonic() + 60; url = None
 while time.monotonic() < deadline:
  for line in (root / 'host.log').read_text().splitlines():
   if line.startswith('CONFECTORY_WEB_UI '): url = line.split(' ', 1)[1]
  if url: break
  assert host.poll() is None, (root / 'host.log').read_text()
  time.sleep(.1)
 assert url, (root / 'host.log').read_text()
 origin, token = url.split('/#')
 def state():
  def send(body):
   request = urllib.request.Request(origin + '/api/request', data=json.dumps(body).encode(), headers={'Content-Type': 'application/json', 'X-Confectory-Session': token})
   with urllib.request.urlopen(request, timeout=20) as response: return json.load(response)
  for _ in range(400):
   view = send({'op': 'mount'})
   if view.get('error', {}).get('code') == 'busy': time.sleep(.01); continue
   assert view['ok'], view; break
  else: raise AssertionError('Read-only mount remained busy')
  try: return view['state']
  finally: assert send({'op': 'dispose', 'view': view['view']})['ok']
 with sync_playwright() as p:
  browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox', '--disable-gpu'])
  page = browser.new_page(viewport={'width':1440, 'height':1000}); errors = []; page.on('pageerror', lambda error: errors.append(str(error)))
  try:
   page.goto(url); page.locator('.work-body').wait_for()
   project_id = state()['projectId']
   page.locator('#add-helper').click(); page.locator('[data-recruit="global"]').click()
   page.locator('#helper-list button').first.click(); expect(page.locator('#helper-summary')).to_contain_text('main-helper')
   for scope, text in [('project', 'OWNED CURRENT PROJECT MEMORY'), ('common', 'OWNED COMMON MEMORY')]:
    page.locator('#memory-scope').select_option(scope); page.locator('#helper-memory').fill(text); page.locator('#remember').click(); expect(page.locator('#status')).to_contain_text('로컬에 저장됨'); expect(page.locator('#remember')).to_be_enabled()
   expect(page.locator('#allow-common')).not_to_be_checked(); page.locator('.modal [data-close]').click(); expect(page.locator('.modal-shade')).to_have_count(0)
   page.locator('.home-side [data-helper="main-helper"]').first.click()
   card = page.locator('.participant-expanded-card[data-helper-id="main-helper"]')
   card.locator('textarea').fill('UNSENT selected helper input'); card.locator('button[type="submit"]').click()
   expect(page.locator('.window[data-key="connections"]')).to_be_visible(); assert not requests and state()['aiPreview'] is None
   expect(card.locator('textarea')).to_have_value('UNSENT selected helper input'); card.locator('[data-close]').click()
   responses = page.locator('[data-connection-row="Confectory.Agent.Responses::Connection"]')
   codex = page.locator('[data-connection-row="Confectory.Agent.Codex::Connection"]')
   expect(codex.locator('[data-connection-status]')).to_contain_text('실행 미지원')
   responses.locator('[data-connection-settings]').click()
   expect(page.locator('[data-schema-id]')).to_have_text('Confectory.AISettings::Settings')
   assert state()['projectId'] != project_id and any(row['projectId'] == project_id for row in state()['background'])
   for name, value in [('model', 'owned-helper-http-fixture'), ('endpoint', endpoint), ('credentialReference', '')]:
    field = page.locator('[data-schema-field="' + name + '"]'); field.fill(value); field.locator('..').get_by_role('button', name='Apply field', exact=True).click(); expect(page.locator('#status')).to_have_text('Shared field draft updated')
   page.locator('#semantic-save').click(); expect(page.locator('#status')).to_have_text('Draft saved; final sources unchanged')
   page.locator('.brand').click(); page.locator('[data-enter]').first.click(); expect(page.locator('.work-body')).to_be_visible()
   assert state()['projectId'] == project_id and not requests
   page.locator('#add-agent').click(); page.locator('#connection-list button').filter(has_text='Confectory.Agent.Responses::Connection').click()
   expect(page.locator('[data-connection-row="Confectory.Agent.Responses::Connection"] [data-connection-status]')).to_have_text('이 프로젝트에 설정 선택됨')
   page.locator('.window[data-key="connections"] [data-close]').click()

   def open_helper(helper):
    page.locator('.home-side [data-helper="' + helper + '"]').first.click()
    return page.locator('.participant-expanded-card[data-helper-id="' + helper + '"]')
   def prepare(card, message):
    if card.locator('.sd-character').count():
     if not card.locator('.sd-compose').is_visible(): card.locator('.sd-character').click()
     form = card.locator('.sd-compose')
    else: form = card.locator('form').first
    form.locator('textarea').fill(message); form.locator('button[type="submit"]').click()
    expect(page.locator('#ai-start')).to_be_disabled()
   def approve():
    for permission in ('contentApproved', 'usageApproved'):
     page.locator('[data-permission="' + permission + '"]').check()
    expect(page.locator('#ai-start')).to_be_enabled(); page.locator('#ai-start').click()
   def wait_for(outcome):
    deadline = time.monotonic() + 35
    while time.monotonic() < deadline:
     actual = state()
     if actual['aiState'] == outcome: return actual
     time.sleep(.05)
    raise AssertionError('AI did not reach ' + outcome + ': ' + json.dumps(actual))

   card = open_helper('main-helper'); expect(card.locator('textarea')).to_have_value('UNSENT selected helper input')
   prepare(card, 'FIRST owned helper message')
   preview = state()['aiPreview']; assert preview['helperContext']['helper'] == 'main-helper'
   assert [memory['text'] for memory in preview['helperContext']['memory']] == ['OWNED CURRENT PROJECT MEMORY']
   assert not requests
   page.locator('#cancel-preview').click(); expect(card).to_be_visible(); expect(card.locator('textarea')).to_have_value('FIRST owned helper message')
   prepare(card, 'FIRST owned helper message'); approve(); actual = wait_for('completed')
   assert actual['aiHelperId'] == 'main-helper' and actual['aiRequestId'] and actual['aiErrorCode'] is None
   assert len(requests) == 1 and requests[0]['context']['helper'] == 'main-helper'
   expect(card.locator('.messages')).to_contain_text('OWNED LOOPBACK FIXTURE: main-helper / FIRST owned helper message')
   expect(card.locator('[data-helper-ai-status]')).to_contain_text('응답 완료')
   card.locator('[data-close]').click()

   page.locator('#add-helper').click(); page.locator('[data-recruit="project"]').click()
   expect(page.locator('#helper-list .field')).to_have_count(2)
   other = next(helper['id'] for helper in state()['helpers'] if helper['membership'] == 'project')
   page.locator('#helper-list .field').filter(has_text=other).get_by_role('button', name='이 프로젝트에 선택', exact=True).click()
   page.locator('.modal [data-close]').click(); other_card = open_helper(other)
   expect(other_card.locator('.messages')).not_to_contain_text('FIRST owned helper message')
   expect(other_card.locator('textarea')).to_have_value('')
   assert state()['aiHelperId'] == 'main-helper'
   prepare(other_card, 'WAIT owned helper request'); approve(); assert blocked.wait(10)
   actual = state(); assert actual['aiState'] == 'running' and actual['aiHelperId'] == other and actual['aiOutput'] == ''
   expect(other_card.locator('[data-helper-ai-status]')).to_contain_text('AI 작업 중'); other_card.locator('[data-close]').click()
   page.locator('#title').click(); page.get_by_role('button', name='프로젝트 완전 종료', exact=True).click()
   expect(page.get_by_role('dialog', name='작업 중인 프로젝트 종료')).to_be_visible(); page.locator('[data-keep-project]').click()
   assert state()['aiState'] == 'running'
   page.locator('.brand').click(); expect(page.locator('.home-grid')).to_be_visible()
   assert any(row['projectId'] == project_id and row['aiState'] == 'running' for row in state()['background'])
   assert len(requests) == 2
   page.locator('[data-enter]').first.click(); expect(page.locator('.work-body')).to_be_visible(); assert state()['projectId'] == project_id
   release.set(); actual = wait_for('completed'); assert actual['aiHelperId'] == other
   assert requests[-1]['projectId'] == project_id and requests[-1]['context']['helper'] == other and requests[-1]['context']['memory'] == []
   other_card = open_helper(other); expect(other_card.locator('.messages')).to_contain_text('WAIT owned helper request')
   other_card.locator('.helper-window-pin').click()
   prepare(other_card, 'FAIL owned helper request'); approve(); actual = wait_for('error')
   assert actual['aiErrorCode'] and actual['aiOutput'] == '' and len(requests) == 3
   expect(other_card.locator('[data-helper-ai-status]')).to_contain_text('요청 실패')
   expect(other_card.locator('.messages')).not_to_contain_text('WAIT owned helper request')
   expect(other_card.locator('.sd-answer p')).to_contain_text('요청 실패')
   expect(other_card.locator('.sd-compose textarea')).to_have_value('FAIL owned helper request')
   other_card.locator('.sd-close').click(); page.locator('#title').click(); page.get_by_role('button', name='프로젝트 완전 종료', exact=True).click()
   expect(page.locator('.home-grid')).to_be_visible(); assert state()['projectId'] == '' and all(row['projectId'] != project_id for row in state()['background'])
   assert len(requests) == 3 and not fixture_errors and not errors
   assert all((project / name).read_bytes() == data for name, data in before.items()), 'Helper flow modified project source'
   (root / 'verification.json').write_text(json.dumps({'projectId':project_id, 'mainHelper':'main-helper', 'projectHelper':other, 'ownedHttpRequests':len(requests), 'sourceUnchanged':True, 'errorCode':actual['aiErrorCode'], 'realAccountCalled':False}, indent=2) + '\n')
  except Exception:
   print('Evidence:', root, flush=True); print('Current public state:', json.dumps(state()), flush=True); raise
  finally: browser.close()
finally:
 release.set()
 if host.poll() is None: os.killpg(host.pid, signal.SIGTERM)
 host.wait(timeout=15); stream.close(); server.shutdown(); server.server_close(); thread.join(timeout=3)
print('PASS ordinary ProjectPack helper connection settings, explicit approval, actual scoped HTTP output/error, hidden work and close confirmation; owned loopback fixture only; source unchanged', root)
