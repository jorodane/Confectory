#!/usr/bin/env python3
"""Real GTK editor invite and text through a pretrusted test relay on two internal networks.

Pass the local fixture image described by editor_lan_chat_x11.py, with Bash also
available at /bin/bash for the direct route check. The test compiles an
EditorHome copy with the existing stdin-only relay fixture and uses a private
Xorg display. Project invitations and relay grants never reach command lines.
"""
import base64
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import secrets
import select
import shutil
import subprocess
import sys
import tempfile
import uuid

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.oid import NameOID

from editor_lan_chat_x11 import DOCKER, docker, dotnet, eventually, internal_network, peer, repo


def fixture_build(root):
    checkout = root / "checkout"
    home = checkout / "examples/editor-home"
    for source, destination in ((repo / "packs", checkout / "packs"), (repo / "examples/editor-home", home)):
        shutil.copytree(source, destination, ignore=shutil.ignore_patterns(".confectory", "bin", "obj"))
    (checkout / "targets").symlink_to(repo / "targets", target_is_directory=True)
    body = home / "MainBody.celem"
    body.write_text(body.read_text().replace('body common "Main.csbody";',
        'import Confectory.ProjectChat::OpenOpaqueChatRelay as FixtureRelay (object) -> object;\nbody common "Main.csbody";'))
    entry = home / "Main.csbody"
    entry.write_text((repo / "tests/fixtures/isolated-relay-editor/Setup.csbody").read_text() + entry.read_text())
    cli = repo / "src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll"
    result = subprocess.run([dotnet, cli, "build", home / "project.cpack", "linux"],
                            text=True, capture_output=True, check=False, timeout=240)
    assert result.returncode == 0, result.stdout[-3000:] + result.stderr[-3000:]
    return checkout, json.loads(result.stdout)["run"]


def identity(dns):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, dns)])
    now = datetime.now(timezone.utc)
    certificate = (x509.CertificateBuilder().subject_name(name).issuer_name(name).public_key(key.public_key())
                   .serial_number(x509.random_serial_number()).not_valid_before(now - timedelta(minutes=1))
                   .not_valid_after(now + timedelta(hours=1))
                   .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
                   .add_extension(x509.SubjectAlternativeName([x509.DNSName(dns)]), critical=False)
                   .sign(key, hashes.SHA256()))
    bundle = pkcs12.serialize_key_and_certificates(b"fixture", key, certificate, None, serialization.NoEncryption())
    der = certificate.public_bytes(serialization.Encoding.DER)
    return base64.b64encode(bundle).decode(), base64.b64encode(der).decode(), hashlib.sha256(der).hexdigest().upper()


@contextmanager
def reservations(relay, command, relay_key):
    with relay.log.open("w") as log, subprocess.Popen(
        relay.command(command, setup=True, CONFECTORY_TEST_PUBLIC_CHAT_RELAY="1"),
        text=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=log,
    ) as service:
        def supply(data):
            service.stdin.write(json.dumps(data) + "\n")
            service.stdin.flush()

        def reserve(seconds):
            reservation, host_grant, guest_grant = uuid.uuid4().hex, secrets.token_hex(32), secrets.token_hex(32)
            supply(dict(seconds=seconds, hostHash=hashlib.sha256(bytes.fromhex(host_grant)).hexdigest(),
                        guestHash=hashlib.sha256(bytes.fromhex(guest_grant)).hexdigest()))
            assert select.select([service.stdout], [], [], 15)[0], "Relay did not allocate a port"
            port = int(service.stdout.readline())
            return dict(id=reservation, port=port, grant=host_grant), dict(id=reservation, port=port, grant=guest_grant)

        supply(dict(role="relay", identity=relay_key))
        try:
            yield reserve
        finally:
            service.stdin.close()
            assert service.wait(timeout=20) == 0, "Test relay did not stop cleanly"


def issue(host):
    host.click(450)
    host.click(462)
    host.wait(lambda row: row["lanMode"] == "issue", "Relay issuance confirmation")
    host.click(452)
    host.wait(lambda row: row["lanMode"] == "hosting", "Issue relay invitation")
    card = host.copy_invite(version=3)
    assert set(card) == {"version", "project", "code", "reservation", "title"}
    return card


def review(guest, endpoint, fingerprint, owner):
    guest.click(450)
    guest.click(463)
    guest.click(456)
    guest.key(456, "v", 0xFFE3)
    guest.fill(457, "GTK Relay Guest")
    guest.click(453)
    row = guest.wait(lambda state: state["lanMode"] == "review", "Review pasted relay invitation")
    rendered = "\n".join(row["texts"])
    assert f"Configured test relay: {endpoint}" in rendered
    assert owner["title"] in rendered and owner["projectId"] in rendered and fingerprint in rendered
    assert 458 in row["hits"][::5]
    assert guest.field(row, 456)["text"] == ""


def test(root, image, checkout, command):
    left, right = "192.0.2.19", "198.51.100.19"
    left_relay, right_relay = "192.0.2.18", "198.51.100.18"
    relay_key, relay_pin, _ = identity("relay.confectory.invalid")
    host_key, host_pin, fingerprint = identity("chat-host.confectory.invalid")
    with internal_network(image, "192.0.2.16/29") as (a, image_id), \
         internal_network(image, "198.51.100.16/29") as (b, _), \
         peer(root, a, image_id, left, checkout) as host, \
         peer(root, b, image_id, right, checkout) as guest, \
         peer(root, a, image_id, left_relay, checkout, other_network=(b, right_relay)) as relay, \
         reservations(relay, command, relay_key) as reserve:
        # Each editor has only its own network and loopback, no default route or
        # published ports. The dual-attached fixture must not forward IP packets.
        assert docker("exec", relay.container, "cat", "/proc/sys/net/ipv4/ip_forward").stdout.strip() == "0"
        for editor, destination in ((host, right), (guest, left)):
            result = subprocess.run([*DOCKER, "exec", editor.container, "/bin/bash", "-c",
                                     'exec 3<>"/dev/tcp/$1/12345"', "probe", destination],
                                    text=True, capture_output=True, timeout=5)
            assert result.returncode != 0 and "Network is unreachable" in result.stderr, "Direct editor route was not rejected"
        guest.launch(command)
        guest.click(450)
        state = guest.wait(lambda row: row["lanMode"] == "start", "Default public chat picker")
        assert 453 in state["hits"][::5] and not {462, 463}.intersection(state["hits"][::5])
        assert not guest.listeners()
        guest.close()

        pairs = [reserve(seconds) for seconds in (60, 240, 240)]
        host_setup = dict(role="host", identity=host_key, relayPin=relay_pin, address=left_relay,
                          reservations=[pair[0] for pair in pairs])
        guest_setup = dict(role="guest", identity=host_pin, relayPin=relay_pin, address=right_relay,
                           reservations=[pair[1] for pair in pairs])
        host.launch(command, host_setup)
        host.click(450)
        state = host.wait(lambda row: row["lanMode"] == "start", "Host profile without an original project")
        assert 462 not in state["hits"][::5]
        host.click(451)

        invalid = dict(guest_setup, address="127.0.0.1")
        guest.launch(command, invalid)
        guest.click(450)
        state = guest.wait(lambda row: row["lanMode"] == "start", "Untrusted route remains hidden")
        assert 453 in state["hits"][::5] and 463 not in state["hits"][::5] and not guest.listeners()
        guest.close()
        guest.launch(command, guest_setup)
        owner = host.create("GTK Relay Host", "Host private draft")
        participant = guest.create("GTK Guest Project", "Guest private draft")
        originals = {Path(item["path"]): Path(item["path"]).read_bytes() for item in (owner, participant)}
        assert not host.listeners() and not guest.listeners()

        cards = [issue(host)]
        host.wait(lambda row: row["lanMode"] == "closed", "Expired relay invitation disconnects", timeout=65)
        assert not host.listeners()
        host.click(451)

        cards.append(issue(host))
        host.send("Host text before any guest")
        endpoint = f"{right_relay}:{pairs[1][1]['port']}"
        review(guest, endpoint, fingerprint, owner)
        assert not guest.established_ports(), "Review opened a connection before confirmation"
        guest.click(451)
        guest.wait(lambda row: guest.field(row, 38).get("text") == "Guest private draft", "Private draft after review cancel")
        guest.fill(38, "Guest private draft after cancel")
        assert not guest.established_ports() and not (guest.profile / "project-chat").exists()

        assert host.copy_invite(version=3)["code"] == cards[1]["code"]
        review(guest, endpoint, fingerprint, owner)
        guest.click(458)
        guest.wait(lambda row: guest.field(row, 461).get("text") == "No messages yet.", "No history at admission")
        host.send("Relay host public text")
        guest.send("Relay guest public text")
        host.wait(lambda row: "Relay guest public text" in host.field(row, 461).get("text", ""), "Guest text on GTK host")
        guest.wait(lambda row: "Relay host public text" in guest.field(row, 461).get("text", ""), "Host text on GTK guest")
        row = guest.state()
        assert "Host text before any guest" not in guest.field(row, 461)["text"]
        assert not {38, 317, 324}.intersection(row["hits"][::5])
        assert not host.listeners() and not guest.listeners()
        print("PASS pretrusted relay review, actual GTK clipboard, cancel and editable draft, empty admission, two-way public text", flush=True)

        host.click(451)
        guest.wait(lambda row: row["lanMode"] == "closed" and '461' not in row["fields"], "Revocation disconnects and hides transcript")
        guest.click(451)
        review(guest, endpoint, fingerprint, owner)
        guest.click(458)
        guest.wait(lambda row: "Could not join" in row["lanStatus"], "Reject replay after revocation")
        guest.click(451)

        cards.append(issue(host))
        review(guest, f"{right_relay}:{pairs[2][1]['port']}", fingerprint, owner)
        guest.click(458)
        guest.wait(lambda row: guest.field(row, 461).get("text") == "No messages yet.", "New reservation has empty inbox")
        host.close()
        guest.wait(lambda row: row["lanMode"] == "closed", "Native host shutdown ends relay session")
        guest.close()
        eventually(lambda: not host.established_ports() and not guest.established_ports(), "Peers cleaned up relay connections")

        assert not (guest.profile / "project-chat").exists()
        journal, = (host.profile / "project-chat").glob("*.json")
        assert [item["text"] for item in json.loads(journal.read_text())["messages"]] == [
            "Host text before any guest", "Relay host public text", "Relay guest public text",
        ]
        assert all(path.read_bytes() == value for path, value in originals.items())
        for editor, expected in ((host, "Host private draft"), (guest, "Guest private draft after cancel")):
            private, = (editor.profile / "project-chat-drafts").glob("*.json")
            assert json.loads(private.read_text())["draft"] == expected
        observable = journal.read_text() + host.log.read_text() + guest.log.read_text() + relay.log.read_text()
        assert all(card["code"] not in observable for card in cards), "Project invitation leaked"
        assert all(part["grant"] not in observable for pair in pairs for part in pair), "Relay grant leaked"
        print("PASS hidden without trust, creator-only issue, timeout, replay rejection, revocation, empty re-entry, shutdown and host-only history", flush=True)


if __name__ == "__main__":
    root = Path(tempfile.mkdtemp(prefix="cf-native-relay-test-"))
    print("Native relay fixture logs at", root, flush=True)
    checkout, command = fixture_build(root)
    test(root, sys.argv[1], checkout, command)
