#!/usr/bin/env python3
"""First local project through LAN chat and cold re-admission in the GTK editor.

Use an isolated Xorg display, the Linux EditorHome build report, and the
local fixture image described in editor_lan_chat_x11.py. Both editor peers
create their own projects and captures through the UI. No project, invite,
journal, or YogiBox fixture is installed.
"""
import json
from pathlib import Path
import sys
import tempfile

from editor_create_lay_x11 import box_drag, make_box, point, view_capture
from editor_lan_chat_x11 import GUEST, HOST, internal_network, peer
from editor_lay_chat_x11 import open_project


HOST_TITLE = 'First LAN Project'
GUEST_TITLE = 'Guest Local Project'
HOST_DESCRIPTION = 'Host workspace capture'
GUEST_DESCRIPTION = 'Guest workspace capture'
HOST_MESSAGE = 'Host sent a local capture'
GUEST_MESSAGE = 'Guest sent a local capture'
BEFORE_ADMISSION = 'Host message before first admission'
AFTER_RESTART = 'New message after cold rejoin'


def issue(host):
    host.issue()
    address, port = next(iter(host.listeners()))
    assert address == HOST
    return port, host.copy_invite()['code']


def admit(host, guest, port):
    guest.review(host, port, HOST_TITLE)
    guest.click(458)
    state = guest.wait(lambda row: row['lanMode'] == 'joined' and
                       guest.field(row, 461).get('text') == 'No messages yet.' and 465 not in row['hits'][::5],
                       'An admitted guest has no earlier messages or attachments')
    assert 38 not in state['hits'][::5] and 452 not in state['hits'][::5]
    return state['model']['selected']['projectId']


def send_capture(editor, message):
    box_drag(editor, point(editor, 459))
    editor.wait(lambda row: 'attached to this draft' in row['lanStatus'], 'Prepared a sealed local box')
    editor.send(message)


def see_capture(editor, description, box, number):
    current = editor.wait(lambda row: any(text.startswith('View YogiBox ') for text in row['texts']),
                          'Public message has a YogiBox viewer')
    label = f'View YogiBox {number}'
    if label not in current['texts']:
        editor.click(466 if number == 1 else 467)
        editor.wait(lambda row: label in row['texts'], 'Select the attachment on its original message')
    view_capture(editor, description, box[2], box[1])
    editor.click(468)


def owner_and_drafts(host, guest, owner, participant):
    for editor, title, project in ((host, HOST_TITLE, owner), (guest, GUEST_TITLE, participant)):
        receipt, = (editor.profile / 'project-creators').glob('*.json')
        assert receipt.name == project['projectId'] + '.json'
        draft, = (editor.profile / 'project-chat-drafts').glob('*.json')
        assert json.loads(draft.read_text())['draft'] == title + ' private draft'
        assert not (editor.profile / 'helper-conversations').exists()
    assert not (guest.profile / 'project-chat').exists()


def retained_attachment(row, box, description, remote=False):
    sealed = json.loads(box[4])['package']
    attachment = row['attachment']
    archived = attachment['package']
    assert archived['sealed'] and archived['text'] == description
    if not remote:
        assert archived['items'] == sealed['items']
        return
    saved, = archived['items']
    original, = sealed['items']
    # The host retains the guest's pixels with host-assigned identity and no
    # guest workspace locator. Only the local owner's source metadata remains.
    assert attachment['namespace'] == 'remote-lay' and saved['item'] != original['item']
    capture = saved['capture']
    assert capture['source'] == capture['hash'] and (capture['view'], capture['x'], capture['y']) == (0, 0, 0)
    for field in ('width', 'height', 'encoding', 'hash', 'pixels'):
        assert capture[field] == original['capture'][field]


def exercise(host, guest, command):
    host.launch(command)
    guest.launch(command)
    for editor in (host, guest):
        model = editor.state()['model']
        assert not model['cards'] and not model['helperAgents']['agents']
        assert not editor.listeners() and not (editor.profile / 'project-chat').exists()

    host_box = make_box(host, HOST_TITLE, HOST_DESCRIPTION)
    guest_box = make_box(guest, GUEST_TITLE, GUEST_DESCRIPTION)
    owner, participant = host_box[0], guest_box[0]
    assert owner['projectId'] != participant['projectId']
    originals = {path: path.read_bytes() for project in (owner, participant)
                 for path in Path(project['path']).parent.iterdir() if path.is_file()}
    assert not host.listeners() and not guest.listeners()

    port, original = issue(host)
    host.send(BEFORE_ADMISSION)
    assert admit(host, guest, port) == participant['projectId']
    assert not guest.listeners()

    send_capture(host, HOST_MESSAGE)
    guest.wait(lambda row: HOST_MESSAGE + '  [YogiBox 1]' in guest.field(row, 461).get('text', ''),
               'Host text and sealed LaY reached the guest')
    see_capture(guest, HOST_DESCRIPTION, host_box, 1)
    send_capture(guest, GUEST_MESSAGE)
    host.wait(lambda row: GUEST_MESSAGE + '  [YogiBox 2]' in host.field(row, 461).get('text', ''),
              'Guest text and sealed LaY reached the host')
    see_capture(host, GUEST_DESCRIPTION, guest_box, 2)
    assert all(box[3].read_bytes() == box[4] for box in (host_box, guest_box))
    assert not (guest.profile / 'project-chat').exists()
    print('PASS first creator invitation, separate guest scope, empty admission and bidirectional exact LaY', flush=True)

    guest.click(451)
    guest.wait(lambda row: row['screen'] == 'project', 'Guest left the first connection')
    assert host.copy_invite()['code'] == original
    guest.review(host, port, HOST_TITLE)
    guest.click(458)
    guest.wait(lambda row: 'Could not join' in row['lanStatus'], 'The first consumed invitation is rejected')
    assert not (guest.profile / 'project-chat').exists()
    guest.click(451)
    guest.close()
    host.close()
    assert not host.listeners() and not guest.listeners()

    journal, = (host.profile / 'project-chat').glob('*.json')
    saved = journal.read_bytes()
    rows = json.loads(saved)['messages']
    assert [row['text'] for row in rows] == [BEFORE_ADMISSION, HOST_MESSAGE, GUEST_MESSAGE]
    retained_attachment(rows[1], host_box, HOST_DESCRIPTION)
    retained_attachment(rows[2], guest_box, GUEST_DESCRIPTION, remote=True)
    owner_and_drafts(host, guest, owner, participant)
    assert original.encode() not in saved + host.log.read_bytes() + guest.log.read_bytes()
    print('PASS consumed invite refused and only the host persisted the original messages and LaY', flush=True)

    host.launch(command)
    guest.launch(command)
    assert open_project(host, HOST_TITLE)['projectId'] == owner['projectId']
    assert open_project(guest, GUEST_TITLE)['projectId'] == participant['projectId']
    assert not host.listeners() and not guest.listeners()
    port, fresh = issue(host)
    assert fresh != original
    host.wait(lambda row: GUEST_MESSAGE + '  [YogiBox 2]' in host.field(row, 461).get('text', ''),
              'The restarted host restored history from its journal')
    see_capture(host, HOST_DESCRIPTION, host_box, 1)
    see_capture(host, GUEST_DESCRIPTION, guest_box, 2)
    assert journal.read_bytes() == saved
    assert admit(host, guest, port) == participant['projectId']

    host.send(AFTER_RESTART)
    latest = guest.wait(lambda row: AFTER_RESTART in guest.field(row, 461).get('text', ''),
                        'The new session receives new text')
    assert all(old not in guest.field(latest, 461)['text'] for old in (BEFORE_ADMISSION, HOST_MESSAGE, GUEST_MESSAGE))
    assert 465 not in latest['hits'][::5]
    host.close()
    guest.wait(lambda row: row['lanMode'] == 'closed' and not row['lanImageBounds'],
               'Closing the host clears the live guest view')
    guest.close()
    assert not host.listeners() and not guest.listeners()
    final = journal.read_bytes()
    final_rows = json.loads(final)['messages']
    assert final_rows[:-1] == rows and len(final_rows) == len(rows) + 1
    assert final_rows[-1]['text'] == AFTER_RESTART and 'attachment' not in final_rows[-1]
    assert all(code.encode() not in final + host.log.read_bytes() + guest.log.read_bytes()
               for code in (original, fresh))
    owner_and_drafts(host, guest, owner, participant)
    assert all(path.read_bytes() == content for path, content in originals.items())
    print('PASS cold host restored both attachments, fresh guest saw only new text, and private records stayed separate',
          flush=True)


if __name__ == '__main__':
    report = json.loads(Path(sys.argv[1]).read_text())
    image = sys.argv[2]
    assert report['target'] == 'linux'
    root = Path(tempfile.mkdtemp(prefix='cf-first-lan-session-'))
    print('Evidence:', root, flush=True)
    with internal_network(image) as (network, image_id), \
         peer(root, network, image_id, HOST) as host, peer(root, network, image_id, GUEST) as guest:
        exercise(host, guest, report['run'])
