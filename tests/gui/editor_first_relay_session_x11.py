#!/usr/bin/env python3
"""First project through the pretrusted relay and a cold GTK re-admission.

Pass the local fixture image described by editor_relay_chat_x11.py and use an
owned Xorg display. The existing stdin fixture provisions test certificates
and single-use relay reservations. GTK creates both projects, selects and
seals both captures, issues invitations for the private clipboard, and sends
public messages.
"""
from pathlib import Path
import sys
import tempfile

from editor_first_lan_session_x11 import (
    AFTER_RESTART,
    BEFORE_ADMISSION,
    GUEST_DESCRIPTION,
    GUEST_MESSAGE,
    HOST_DESCRIPTION,
    HOST_MESSAGE,
    exercise,
)
from editor_lan_chat_x11 import eventually, internal_network, peer
from editor_relay_chat_x11 import (
    assert_isolated_routes,
    fixture_build,
    identity,
    issue,
    reservations,
    review,
)


def test(root, image, checkout, command):
    left, right = '192.0.2.35', '198.51.100.35'
    left_relay, right_relay = '192.0.2.34', '198.51.100.34'
    relay_key, relay_pin, _ = identity('relay.confectory.invalid')
    host_key, host_pin, fingerprint = identity('chat-host.confectory.invalid')

    with internal_network(image, '192.0.2.32/29') as (left_net, image_id), \
         internal_network(image, '198.51.100.32/29') as (right_net, _), \
         peer(root, left_net, image_id, left, checkout) as host, \
         peer(root, right_net, image_id, right, checkout) as guest, \
         peer(root, left_net, image_id, left_relay, checkout, other_network=(right_net, right_relay)) as relay, \
         reservations(relay, command, relay_key) as reserve:
        assert_isolated_routes(host, guest, relay, left, right)

        sessions = []
        first_editor_output = b''

        def launch():
            nonlocal first_editor_output
            # Provision a fresh pair only after both old editor processes
            # have exited. Never re-install their consumed relay grants.
            if sessions:
                first_editor_output = host.log.read_bytes() + guest.log.read_bytes()
            host_part, guest_part = reserve(240)
            sessions.append((host_part, guest_part))
            host.launch(command, dict(role='host', identity=host_key, relayPin=relay_pin,
                                      address=left_relay, reservations=[host_part]))
            guest.launch(command, dict(role='guest', identity=host_pin, relayPin=relay_pin,
                                       address=right_relay, reservations=[guest_part]))
            if len(sessions) == 1:
                host.click(450)
                home = host.wait(lambda row: row['lanMode'] == 'start', 'Public chat before any project exists')
                assert not {452, 462}.intersection(home['hits'][::5])
                host.click(451)
                host.wait(lambda row: row['screen'] == 'home', 'Return to the empty project listing')

        def publish():
            card = issue(host)
            host_part, _ = sessions[-1]
            assert card['reservation'] == host_part['id']
            assert not host.listeners() and not guest.listeners()
            return card

        def inspect(invite, owner):
            _, guest_part = sessions[-1]
            assert invite['reservation'] == guest_part['id']
            # The original clipboard content is still available after the
            # first peer leaves, even though the relay has closed that pair.
            review(guest, f"{right_relay}:{guest_part['port']}", fingerprint, owner)
            assert not guest.established_ports(), 'Review opened a connection before consent'
            assert not host.listeners() and not guest.listeners()

        codes = exercise(host, guest, launch, publish, inspect)
        assert len(sessions) == 2 and sessions[0][0]['id'] != sessions[1][0]['id']
        eventually(lambda: not host.established_ports() and not guest.established_ports(),
                   'Both editor processes released their relay connections')

        relay_output = relay.log.read_bytes()
        grants = [part['grant'] for pair in sessions for part in pair]
        visible_state = relay_output + first_editor_output + host.log.read_bytes() + guest.log.read_bytes()
        assert all(secret.encode() not in visible_state for secret in (*codes, *grants)), 'A test credential leaked'
        public_content = (BEFORE_ADMISSION, HOST_MESSAGE, GUEST_MESSAGE, AFTER_RESTART,
                          HOST_DESCRIPTION, GUEST_DESCRIPTION)
        assert all(value.encode() not in relay_output for value in public_content)
        assert not (relay.profile / 'project-chat').exists()
        print('PASS two unrouted test networks, pretrusted relay, single-use grants and no relay chat journal',
              flush=True)


if __name__ == '__main__':
    root = Path(tempfile.mkdtemp(prefix='cf-first-relay-session-'))
    print('Evidence:', root, flush=True)
    checkout, command = fixture_build(root)
    test(root, sys.argv[1], checkout, command)
