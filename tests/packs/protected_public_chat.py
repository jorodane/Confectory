"""Run the protected public-chat host and guest in separate local .NET processes."""
import argparse
import base64
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import select
import secrets
import shutil
import socket
import ssl
import struct
import subprocess
import tempfile
import time
import uuid

repo = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("tool_checkout", nargs="?", type=Path, default=repo)
parser.add_argument("--target", choices=("linux", "windows"), default="linux")
parser.add_argument("--compile-only", action="store_true")
parser.add_argument("--isolated-docker-image", metavar="LOCAL_IMAGE",
                    help="also test two containers on a private Docker network using a locally built .NET runtime image")
parser.add_argument("--relay-docker-image", metavar="LOCAL_IMAGE",
                    help="verify the outbound relay across two non-routed internal networks")
args = parser.parse_args()
if (args.isolated_docker_image or args.relay_docker_image) and (args.compile_only or args.target != "linux"):
    parser.error("the isolated network fixture requires Linux execution")
tool_repo = args.tool_checkout.resolve()
dotnet = os.environ.get("CONFECTORY_DOTNET") or shutil.which("dotnet")
cli = tool_repo / "src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll"
assert dotnet and cli.is_file(), "Build the Release CLI and targets or pass their checkout"
env = dict(os.environ, CONFECTORY_DOTNET=dotnet, CONFECTORY_DEV_PUBLIC_CHAT_LOOPBACK="1",
           PATH=str(Path(dotnet).parent) + os.pathsep + os.environ["PATH"])

imports = """import Confectory.EditorHome::StartPublicChatLoopback as Start (string,string,object) -> object;
import Confectory.EditorHome::StartPublicChat as StartTransport (string,string,object,object) -> object;
import Confectory.ProjectChat::OpenProtectedChat as ListenTransport (object) -> object;
import Confectory.ProjectChat::ConnectProtectedChat as ConnectTransport (string,object,object,string,string,string) -> object;
import Confectory.EditorHome::LocalPublicChat as LocalChat (string,string,string,string,string,string) -> string;
import Confectory.EditorHome::PublicChatInvitations as Invitations (string,string) -> object;
import Confectory.EditorHome.Model::CreatorHost as CreatorHost (string) -> bool;
import Confectory.ProjectChat::OpenProtectedLoopback as Listen (object) -> object;
import Confectory.ProjectChat::ConnectProtectedLoopback as Connect (int,object,string,string,string) -> object;
import Confectory.EditorHome::StartPublicChatRelay as StartRelay (string,string,object,object) -> object;
import Confectory.ProjectChat::OpenOpaqueChatRelay as Relay (object) -> object;
import Confectory.ProjectChat::ConnectRelayedProtectedChat as ConnectRelay (object,object,string,string,string,object) -> object;
body common "ProtectedPublicChatFixture.csbody";"""


def message(index):
    return f"{index:032x}"


@contextmanager
def process(command, checkout, directory, mode, docker_launch=None):
    fixture_env = dict(CONFECTORY_EDITOR_REPO=str(checkout), CONFECTORY_TLS_TEST_MODE=mode,
                       CONFECTORY_TLS_TEST_ROOT=str(directory), CONFECTORY_TLS_TEST_ISOLATED="0")
    docker_cleanup = lambda: None
    if docker_launch is not None:
        command, docker_cleanup = docker_launch(command, checkout, directory, fixture_env)
    with tempfile.TemporaryFile(mode="w+t") as errors:
        child = subprocess.Popen(command, cwd=checkout, text=True, stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE, stderr=errors,
                                 env=dict(env, **fixture_env))

        def call(operation, **values):
            # The isolated runner passes synthetic codes over anonymous stdin/stdout pipes.
            # Error messages show operation names only.
            child.stdin.write(json.dumps(dict(op=operation, **values)) + "\n")
            child.stdin.flush()
            assert select.select([child.stdout], [], [], 30)[0], f"{mode}: no response to {operation}"
            line = child.stdout.readline()
            if not line:
                errors.seek(0)
                raise AssertionError(f"{mode} ended during {operation}: {errors.read()[-2000:]}")
            return json.loads(line)

        try:
            yield call
        finally:
            child.stdin.close()
            try:
                child.wait(timeout=15)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()
            child.stdout.close()
            docker_cleanup()
            if child.returncode != 0:
                errors.seek(0)
                raise AssertionError(f"{mode} exited with {child.returncode}: {errors.read()[-2000:]}")


def connect(guest, route, code, name, **values):
    return guest("connect", name=name, code=code, **route, **values)


def request(guest, name, operation, **values):
    return guest("request", name=name, request=dict(op=operation, **values))


def seen(guest, name, *indices):
    reply = request(guest, name, "read")
    assert reply.get("status") == "ok" and [row["id"] for row in reply["messages"]] == list(map(message, indices))


def verify_private(directory):
    for who in ("host", "guest"):
        private = directory / f"{who}-profile/helper-conversations"
        assert {entry.name: entry.read_bytes() for entry in private.iterdir()} == {"fixture.json": b'{"personal":true}\n'}
    assert not (directory / "guest-profile/project-chat").exists()


def make_profiles(directory):
    for who in ("host", "guest"):
        private = directory / f"{who}-profile/helper-conversations"
        private.mkdir(parents=True)
        (private / "fixture.json").write_bytes(b'{"personal":true}\n')


@contextmanager
def raw_tls(directory, route):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.load_verify_locations(cadata=ssl.DER_cert_to_PEM_cert((directory / "trusted.der").read_bytes()))
    with socket.create_connection(("127.0.0.1", route["port"]), timeout=5) as tcp:
        with context.wrap_socket(tcp, server_hostname="localhost") as channel:
            yield channel


def send_frame(channel, payload):
    body = json.dumps(payload).encode()
    channel.sendall(struct.pack("!I", len(body)) + body)


def read_frame(channel):
    with channel.makefile("rb") as reader:
        length, = struct.unpack("!I", reader.read(4))
        assert length <= 4096
        return json.loads(reader.read(length))


def regular_flow(command, checkout, directory):
    make_profiles(directory)
    with process(command, checkout, directory, "host") as host:
        with process(command, checkout, directory, "guest") as guest:
            assert host("start-disabled").get("error") == "InvalidOperationException"
            route = host("start")
            assert set(route) == {"port", "project"}
            assert host("start").get("error") == "InvalidOperationException"
            assert host("send", id=message(1), text="Old text") == {"status": "ok"}
            assert host("attachment", id=message(2), text="Old attachment") == {"status": "ok"}
            invite = host("issue")["invitation"]
            assert connect(guest, route, invite, "bad-pin", pin="wrong").get("error") == "AuthenticationException"
            with raw_tls(directory, route) as channel:
                send_frame(channel, {"op": "read", "session": "invented"})
                assert read_frame(channel) == {"status": "denied"}
            with raw_tls(directory, route) as channel:
                channel.sendall(struct.pack("!I", 16 * 1024 + 1))
                assert channel.recv(1) == b""
            assert connect(guest, route, invite, "one") == {"status": "ok"}
            assert "error" in connect(guest, route, invite, "replay")
            seen(guest, "one")
            assert request(guest, "one", "attachment", id=message(2)) == {"status": "denied"}

            race = host("issue")["invitation"]
            assert guest("race", name="winner", code=race, **route) == {"status": "ok"}
            seen(guest, "winner")
            assert host("send", id=message(3), text="Live host") == {"status": "ok"}
            assert request(guest, "one", "send", id=message(4), text="Live guest") == {"status": "committed"}
            assert request(guest, "one", "send", id=message(4), text="Live guest") == {"status": "committed"}
            assert host("attachment", id=message(5), text="Live attachment", capture=True) == {"status": "ok"}
            seen(guest, "one", 3, 4, 5)
            seen(guest, "winner", 3, 4, 5)
            assert request(guest, "winner", "read")["messages"][1]["sender"] == "Fixture Guest (guest)"
            pixels = bytes((23, 61, 201))
            assert request(guest, "winner", "attachment", id=message(5)) == {
                "status": "ok", "description": "Fixture seal", "items": [
                    {"kind": "semantic", "availability": "unavailable"},
                    {"kind": "image", "width": 1, "height": 1, "encoding": "rgb24-base64",
                     "hash": hashlib.sha256(pixels).hexdigest(),
                     "pixels": base64.b64encode(pixels).decode()},
                ]}
            journal, = (directory / "host-profile/project-chat").glob("*.json")
            before_upload = journal.read_bytes()
            image = {"kind": "image", "width": 1, "height": 1, "encoding": "rgb24-base64",
                     "hash": hashlib.sha256(pixels).hexdigest(), "pixels": base64.b64encode(pixels).decode()}
            projected = {"description": "Guest LaY", "items": [image]}

            def upload(body, who="one", text="Guest upload"):
                return request(guest, who, "send-attachment", id=message(7), text=text, attachment=body)

            for rejected in (
                dict(projected, items=[image, {"kind": "semantic"}]),
                dict(projected, items=[dict(image, source="unverified-source")]),
                dict(projected, items=[dict(image, hash="0" * 64)]),
                dict(projected, items=[dict(image, width=2)]),
                dict(projected, items=[dict(image, pixels="!!!!")]),
                dict(projected, items=[image] * 3),
                dict(projected, description="x" * 4097),
                dict(projected, attachmentId=message(42)),
            ):
                assert upload(rejected) == {"status": "denied"}
                assert journal.read_bytes() == before_upload
            assert upload(projected) == {"status": "committed"}
            after_upload = journal.read_bytes()
            assert upload(projected) == {"status": "committed"}
            assert upload(projected, text="Changed retry") == {"status": "denied"}
            assert upload(projected, who="winner") == {"status": "denied"}
            assert journal.read_bytes() == after_upload
            assert request(guest, "winner", "attachment", id=message(7)) == {
                "status": "ok", "description": "Guest LaY", "items": [image]}

            assert "error" in request(guest, "winner", "send-attachment", id=message(99), box="remote")
            assert guest("close", name="one") == {"status": "ok"}
            assert request(guest, "one", "read").get("error") == "ObjectDisposedException"
            rejoin = host("issue")["invitation"]
            assert connect(guest, route, rejoin, "two") == {"status": "ok"}
            seen(guest, "two")
            assert request(guest, "two", "attachment", id=message(5)) == {"status": "denied"}
            assert request(guest, "two", "attachment", id=message(7)) == {"status": "denied"}
            assert host("send", id=message(6), text="After rejoin") == {"status": "ok"}
            seen(guest, "two", 6)
            saved = host("history")
            assert [row["id"] for row in saved["messages"]] == list(map(message, (1, 2, 3, 4, 5, 7, 6)))
            journal, = (directory / "host-profile/project-chat").glob("*.json")
            before = journal.read_bytes()
            assert all(code.encode() not in before for code in (invite, race, rejoin))

            assert host("withdraw") == {"status": "ok"}
            assert host("wait") == {"status": "ok"}
            assert "error" in request(guest, "two", "read")
            assert host("restore") == {"status": "ok"}
            route = host("start")
            assert connect(guest, route, host("issue")["invitation"], "three") == {"status": "ok"}
            seen(guest, "three")
            assert host("leave") == {"status": "ok"}
            assert host("wait") == {"status": "ok"}
            assert "error" in request(guest, "three", "read")
            assert host("reopen") == {"status": "ok"}
            route = host("start")
            assert connect(guest, route, host("issue")["invitation"], "four") == {"status": "ok"}
            assert host("stop") == host("wait") == {"status": "ok"}
            assert "error" in request(guest, "four", "read")
            assert journal.read_bytes() == before
    verify_private(directory)
    print("PASS separate .NET processes, verified TLS, socket-only admission, race/replay, bounded frames, validated guest LaY and retry, stop and revocation")


def wait_for(path):
    deadline = time.monotonic() + 8
    while not path.exists() and time.monotonic() < deadline:
        time.sleep(0.01)
    assert path.exists(), f"Fixture did not reach {path.name}"


def lost_reply_flow(command, checkout, directory):
    make_profiles(directory)
    with process(command, checkout, directory, "loss") as host:
        with process(command, checkout, directory, "guest") as guest:
            route = host("start")
            assert host("send", id=message(1), text="Before the interrupted admission") == {"status": "ok"}
            lost = host("issue")["invitation"]
            assert host("arm-loss") == {"status": "ok"}
            marker = directory / "fault-fixture"
            try:
                with raw_tls(directory, route) as channel:
                    send_frame(channel, {"op": "join", "project": route["project"], "invitation": lost, "display": "Interrupted"})
                    wait_for(marker / "accepted")
                    # The actual engine has accepted. The fixture keeps the worker before its success reply.
                    channel.shutdown(socket.SHUT_RDWR)
            finally:
                (marker / "release").touch()
            wait_for(marker / "left")
            assert "error" in connect(guest, route, lost, "burned")
            assert connect(guest, route, host("issue")["invitation"], "fresh") == {"status": "ok"}
            seen(guest, "fresh")
            assert host("send", id=message(2), text="After fresh admission") == {"status": "ok"}
            seen(guest, "fresh", 2)
            assert host("stop") == host("wait") == {"status": "ok"}
    verify_private(directory)
    print("PASS dropped join acknowledgement releases the connection, keeps the invitation consumed, and requires a fresh empty admission")


@contextmanager
def isolated_docker(image):
    docker = ["docker", "--host=unix:///var/run/docker.sock"]
    docker_env = {key: value for key, value in os.environ.items()
                  if key not in ("DOCKER_HOST", "DOCKER_CONTEXT", "DOCKER_TLS", "DOCKER_TLS_VERIFY", "DOCKER_CERT_PATH")}
    network = "confectory-chat-" + uuid.uuid4().hex[:12]
    image_id = subprocess.check_output([*docker, "image", "inspect", "--format", "{{.Id}}", image],
                                       env=docker_env, text=True).strip()
    subprocess.run([*docker, "network", "create", "--internal", "--subnet", "192.0.2.0/29",
                    "--opt", "com.docker.network.bridge.inhibit_ipv4=true", network],
                   env=docker_env, stdout=subprocess.DEVNULL, check=True)
    try:
        inspected = subprocess.check_output([*docker, "network", "inspect", network], env=docker_env)
        scope, = json.loads(inspected)
        assert scope["Internal"] and scope["Options"]["com.docker.network.bridge.inhibit_ipv4"] == "true"
        assert not scope["Containers"]

        def launch(command, checkout, directory, fixture_env):
            host = fixture_env["CONFECTORY_TLS_TEST_MODE"] == "transport-host"
            name = network + ("-host" if host else "-guest")
            address = "192.0.2.2" if host else "192.0.2.3"
            machine_id = directory / "fixture-machine-id"
            machine_id.write_text(uuid.uuid4().hex + "\n")
            targets = (checkout / "targets").resolve()
            run = [*docker, "run", "--pull=never", "--rm", "--interactive", "--name", name,
                   "--network", network, "--ip", address, "--cap-drop", "ALL",
                   "--security-opt", "no-new-privileges", "--user", f"{os.getuid()}:{os.getgid()}",
                   "--mount", f"type=bind,src={checkout},dst={checkout},readonly",
                   "--mount", f"type=bind,src={directory},dst={directory}",
                   "--mount", f"type=bind,src={targets},dst={targets},readonly",
                   "--mount", f"type=bind,src={machine_id},dst=/etc/machine-id,readonly",
                   "--workdir", str(checkout)]
            for key, value in dict(fixture_env, CONFECTORY_TLS_TEST_ISOLATED="1", CONFECTORY_DOTNET=dotnet).items():
                run.extend(("--env", f"{key}={value}"))

            def cleanup():
                # Normal exit uses --rm. This releases a lingering fixture after a timeout.
                subprocess.run([*docker, "rm", "--force", name], env=docker_env,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)

            return ["env", "-u", "DOCKER_HOST", "-u", "DOCKER_CONTEXT", "-u", "DOCKER_TLS",
                    "-u", "DOCKER_TLS_VERIFY", "-u", "DOCKER_CERT_PATH", *run, image_id, *command], cleanup

        yield launch
    finally:
        subprocess.run([*docker, "network", "rm", network], env=docker_env,
                       stdout=subprocess.DEVNULL, check=True)


def transport_flow(command, checkout, directory, docker_launch=None):
    host_dir, guest_dir = directory / "host", directory / "guest"
    public_certs = ("trusted.der", "wrong.der")
    for state_dir in (host_dir, guest_dir):
        make_profiles(state_dir)

    with process(command, checkout, host_dir, "transport-host", docker_launch) as host:
        route = host("start")
        # The synthetic host's public trust material is transferred independently
        # of the socket and of the address selected by the native fixture.
        for name in public_certs:
            shutil.copyfile(host_dir / name, guest_dir / name)
        with process(command, checkout, guest_dir, "transport-guest", docker_launch) as guest:
            code = host("issue")["invitation"]
            assert connect(guest, route, code, "bad-pin", pin="wrong").get("error") == "AuthenticationException"
            assert connect(guest, route, code, "wrong-name", authority="other.confectory.test").get("error") == "AuthenticationException"
            assert connect(guest, route, code, "invalid-name", authority="https://chat-host.confectory.test").get("error") == "ArgumentException"
            other_project = dict(route, project=message(123))
            assert connect(guest, other_project, code, "wrong-project").get("error") == "UnauthorizedAccessException"
            assert connect(guest, route, code, "joined") == {"status": "ok"}
            assert connect(guest, route, code, "used").get("error") == "UnauthorizedAccessException"
            seen(guest, "joined")

            assert host("send", id=message(1), text="Host text over supplied transport") == {"status": "ok"}
            rgb = bytes((12, 34, 56)) * (96 * 96)
            image = {"kind": "image", "width": 96, "height": 96, "encoding": "rgb24-base64",
                     "hash": hashlib.sha256(rgb).hexdigest(), "pixels": base64.b64encode(rgb).decode()}
            attachment = {"description": "Fixture LaY", "items": [image]}
            upload = dict(id=message(2), text="Guest attached LaY", attachment=attachment)
            assert request(guest, "joined", "send-attachment", **upload) == {"status": "committed"}
            assert request(guest, "joined", "send-attachment", **upload) == {"status": "committed"}
            seen(guest, "joined", 1, 2)
            assert request(guest, "joined", "attachment", id=message(2)) == {"status": "ok", **attachment}
            journal, = (host_dir / "host-profile/project-chat").glob("*.json")
            saved, = [row for row in json.loads(journal.read_bytes())["messages"] if row["id"] == message(2)]
            capture, = saved["attachment"]["package"]["items"]
            assert saved["attachment"]["package"]["text"] == attachment["description"]
            assert hashlib.sha256(base64.b64decode(capture["capture"]["pixels"])).hexdigest() == image["hash"]

            assert guest("close", name="joined") == {"status": "ok"}
            assert request(guest, "joined", "read").get("error") == "ObjectDisposedException"
            assert connect(guest, route, host("issue")["invitation"], "fresh") == {"status": "ok"}
            seen(guest, "fresh")
            assert request(guest, "fresh", "attachment", id=message(2)) == {"status": "denied"}
            assert host("stop") == host("wait") == {"status": "ok"}
            assert "error" in request(guest, "fresh", "read")

    verify_private(host_dir)
    verify_private(guest_dir)
    route_name = "isolated non-loopback Docker" if docker_launch is not None else "loopback"
    print(f"PASS supplied {route_name} transport: pinned TLS identity, project-bound single use, text, LaY, and empty rejoin")


@contextmanager
def separated_relay_networks(image):
    docker = ["docker", "--host=unix:///var/run/docker.sock"]
    prefix = "confectory-relay-" + uuid.uuid4().hex[:12]
    networks = [(prefix + "-host", "192.0.2.0/29"), (prefix + "-guest", "198.51.100.0/29")]
    placed = []
    image_id = subprocess.check_output([*docker, "image", "inspect", "--format", "{{.Id}}", image],
                                       text=True).strip()
    try:
        for network, subnet in networks:
            subprocess.run([*docker, "network", "create", "--internal", "--subnet", subnet, "--opt",
                            "com.docker.network.bridge.inhibit_ipv4=true", network],
                           stdout=subprocess.DEVNULL, check=True)
            placed.append(network)
            inspected, = json.loads(subprocess.check_output([*docker, "network", "inspect", network]))
            assert inspected["Internal"] and inspected["Options"]["com.docker.network.bridge.inhibit_ipv4"] == "true"

        def launch(command, checkout, directory, fixture_env):
            mode = fixture_env["CONFECTORY_TLS_TEST_MODE"]
            name = prefix + "-" + mode
            machine_id = directory / "fixture-machine-id"
            machine_id.write_text(uuid.uuid4().hex + "\n")
            first, second = placed
            interfaces = {
                "relayed-host": [(first, "192.0.2.3")],
                "relayed-guest": [(second, "198.51.100.3")],
                "relay": [(first, "192.0.2.2"), (second, "198.51.100.2")],
            }[mode]
            run = [*docker, "run", "--pull=never", "--rm", "--interactive", "--name", name,
                   "--cap-drop", "ALL", "--security-opt", "no-new-privileges", "--user", f"{os.getuid()}:{os.getgid()}",
                   "--sysctl", "net.ipv4.ip_forward=0", "--workdir", str(checkout)]
            for network, address in interfaces:
                run += ["--network", f"name={network},ip={address}"]
            for source in (checkout, (checkout / "targets").resolve(), Path(dotnet).parent):
                run += ["--mount", f"type=bind,src={source},dst={source},readonly"]
            run += ["--mount", f"type=bind,src={directory},dst={directory}",
                    "--mount", f"type=bind,src={machine_id},dst=/etc/machine-id,readonly"]
            for key, value in dict(fixture_env, CONFECTORY_RELAY_TEST_ISOLATED="1", CONFECTORY_DOTNET=dotnet).items():
                run += ["--env", f"{key}={value}"]

            def cleanup():
                subprocess.run([*docker, "rm", "--force", name], stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL, check=False)

            return [*run, image_id, *command], cleanup

        yield launch
    finally:
        for network in reversed(placed):
            subprocess.run([*docker, "network", "rm", network], stdout=subprocess.DEVNULL, check=True)


def relay_flow(command, checkout, directory, launch):
    host_dir, guest_dir, relay_dir = (directory / side for side in ("host", "guest", "relay"))
    for side in (host_dir, guest_dir):
        make_profiles(side)
    relay_dir.mkdir(parents=True)
    sensitive = []

    with process(command, checkout, relay_dir, "relay", launch) as relay, \
         process(command, checkout, host_dir, "relayed-host", launch) as host, \
         process(command, checkout, guest_dir, "relayed-guest", launch) as guest:
        assert relay("ready") == {"status": "ok"}
        assert guest("probe-direct") == host("probe-direct") == {"route": "NetworkUnreachable"}
        assert host("history")["messages"] == []
        for side in (host_dir, guest_dir):
            shutil.copyfile(relay_dir / "relay.der", side / "relay.der")
        for name in ("trusted.der", "wrong.der"):
            shutil.copyfile(host_dir / name, guest_dir / name)
        shutil.copyfile(host_dir / "trusted.der", guest_dir / "wrong-relay.der")

        def routes(**limits):
            grants = [secrets.token_hex(32) for _ in range(2)]
            for grant in grants:
                sensitive.extend([grant.encode(), bytes.fromhex(grant)])
            reservation = relay("start", hostHash=hashlib.sha256(bytes.fromhex(grants[0])).hexdigest(),
                                guestHash=hashlib.sha256(bytes.fromhex(grants[1])).hexdigest(), **limits)
            assert isinstance(reservation.get("port"), int), reservation
            port = reservation["port"]
            return (dict(relayAddress="192.0.2.2", relayPort=port, relayGrant=grants[0]),
                    dict(relayAddress="198.51.100.2", relayPort=port, relayGrant=grants[1]))

        def start(host_route, guest_route):
            opened = host("start", **host_route)
            assert opened.get("port") == 0 and opened.get("project"), opened
            code = host("issue")["invitation"]
            sensitive.extend([opened["project"].encode(), code.encode(), bytes.fromhex(code)])
            return dict(guest_route, port=0, project=opened["project"], code=code)

        def finish():
            assert host("wait") == {"status": "ok"}
            assert relay("wait") == {"status": "ok"}

        host_route, guest_route = routes()
        assert host("withdraw") == {"status": "ok"}
        assert host("start", **host_route).get("error") == "UnauthorizedAccessException"
        assert host("restore") == {"status": "ok"}
        admitted = start(host_route, guest_route)
        historical = "relay fixture: private pre-admission history"
        text = "relay fixture: plaintext chat attached to original project"
        title = "relay fixture: LaY private description"
        sensitive.extend([historical.encode(), text.encode(), title.encode()])
        assert host("send", id=message(1), text=historical) == {"status": "ok"}
        assert guest("connect", name="wrong-relay", **admitted, relayPin="wrong").get("error") == "AuthenticationException"
        wrong_grant = dict(admitted, relayGrant=secrets.token_hex(32))
        assert "error" in guest("connect", name="wrong-grant", **wrong_grant)
        assert guest("connect", name="active", **admitted) == {"status": "ok"}
        seen(guest, "active")
        assert "error" in guest("connect", name="replay-grant", **admitted)
        assert host("send", id=message(2), text=text) == {"status": "ok"}
        rgb = bytes((19, 77, 212)) * (64 * 64)
        pixels = base64.b64encode(rgb).decode()
        sensitive.extend([rgb, pixels.encode(), b"Fixture Guest"])
        image = {"kind": "image", "width": 64, "height": 64, "encoding": "rgb24-base64",
                 "hash": hashlib.sha256(rgb).hexdigest(), "pixels": pixels}
        attachment = {"description": title, "items": [image]}
        payload = dict(id=message(3), text="relay fixture: guest upload", attachment=attachment)
        sensitive.append(payload["text"].encode())
        assert request(guest, "active", "send-attachment", **payload) == {"status": "committed"}
        assert request(guest, "active", "send-attachment", **payload) == {"status": "committed"}
        assert request(guest, "active", "attachment", id=message(3)) == {"status": "ok", **attachment}
        seen(guest, "active", 2, 3)

        journal, = (host_dir / "host-profile/project-chat").glob("*.json")
        saved = journal.read_bytes()
        assert [row["id"] for row in json.loads(saved)["messages"]] == list(map(message, (1, 2, 3)))
        assert host("withdraw") == {"status": "ok"}
        finish()
        assert "error" in request(guest, "active", "read")
        assert host("restore") == {"status": "ok"}

        bad_pin = start(*routes())
        assert guest("connect", name="wrong-host", **bad_pin, pin="wrong").get("error") == "AuthenticationException"
        finish()
        wrong_project = start(*routes())
        wrong_project["project"] = message(999)
        assert guest("connect", name="wrong-project", **wrong_project).get("error") == "UnauthorizedAccessException"
        finish()

        wrong_invite = start(*routes())
        wrong_invite["code"] = admitted["code"]
        assert guest("connect", name="replay-invite", **wrong_invite).get("error") == "UnauthorizedAccessException"
        finish()
        new = start(*routes())
        assert guest("connect", name="fresh", **new) == {"status": "ok"}
        seen(guest, "fresh")
        assert request(guest, "fresh", "attachment", id=message(3)) == {"status": "denied"}
        assert relay("stop") == {"status": "ok"}
        assert "error" in request(guest, "fresh", "read")
        finish()
        assert journal.read_bytes() == saved

        idle_host, _ = routes(seconds=3)
        assert host("start", **idle_host).get("project")
        assert host("stop") == {"status": "ok"}
        assert relay("wait") == {"status": "ok"}
        ended = host("wait")
        assert ended == {"status": "ok"} or ended.get("error") in {
            "EndOfStreamException", "IOException", "OperationCanceledException"
        }

        # Fail during inner TLS when a deliberately tiny relay byte cap is reached.
        limited = start(*routes(byteLimit=128))
        assert "error" in guest("connect", name="bounded", **limited)
        assert relay("wait") == {"status": "ok"}
        assert journal.read_bytes() == saved

    transcript = (relay_dir / "fixture-opaque.bin").read_bytes()
    assert b"chat-host.confectory.invalid" in transcript and len(transcript) > len(pixels)
    assert not any(value in transcript for value in sensitive)
    assert {path.name for path in relay_dir.iterdir()} == {"fixture-machine-id", "relay.der", "fixture-opaque.bin"}
    verify_private(host_dir)
    verify_private(guest_dir)
    assert not (guest_dir / "guest-profile/project-chat").exists()
    print("PASS separate non-routed networks: outbound-only creator and guest, both TLS pins, one-use pairing and project admission")
    print("PASS text/LaY and host-only journal; wrong pair/project/cert, revocation, empty rejoin and one-shot termination")
    print("PASS observed relay plaintext boundary contains only opaque inner TLS; relay expiry/stop and byte cap, no project or invite records")


with tempfile.TemporaryDirectory(prefix="confectory-protected-chat-") as directory:
    root = Path(directory)
    checkout = root / "checkout"
    home = checkout / "examples/editor-home"
    shutil.copytree(repo / "packs", checkout / "packs", ignore=shutil.ignore_patterns(".confectory"))
    shutil.copytree(repo / "examples/editor-home", home, ignore=shutil.ignore_patterns(".confectory"))
    (checkout / "targets").symlink_to(tool_repo / "targets", target_is_directory=True)
    if args.relay_docker_image:
        relay_body = checkout / "packs/project-chat/OpenOpaqueChatRelay.csbody"
        source = relay_body.read_text()
        write = "        await destination.WriteAsync(buffer.AsMemory(0, count), cancelled).ConfigureAwait(false);"
        assert source.count(write) == 1
        observe = """
        if (Environment.GetEnvironmentVariable("CONFECTORY_TLS_TEST_MODE") == "relay")
        {
            lock (gate)
            {
                string directory = Environment.GetEnvironmentVariable("CONFECTORY_TLS_TEST_ROOT")!;
                using var audit = System.IO.File.Open(System.IO.Path.Combine(directory, "fixture-opaque.bin"),
                    System.IO.FileMode.Append, System.IO.FileAccess.Write);
                audit.Write(buffer, 0, count);
            }
        }
"""
        relay_body.write_text(source.replace(write, observe + write))
    manifest = home / "project.cpack"
    manifest.write_text(manifest.read_text().replace("entry Confectory.EditorHome::Main;", "entry Confectory.EditorHome::VerifyShell;"))
    body = home / "VerifyShellBody.celem"
    body.write_text(body.read_text().replace('body common "VerifyShell.csbody";', imports))
    shutil.copyfile(repo / "tests/fixtures/protected-public-chat/Main.csbody", home / "ProtectedPublicChatFixture.csbody")
    compiled = subprocess.run([dotnet, str(cli), "build", str(manifest), args.target],
                              capture_output=True, text=True, timeout=240, env=env)
    assert compiled.returncode == 0, compiled.stdout[-7000:] + compiled.stderr[-7000:]
    report = json.loads(compiled.stdout)
    assert report["target"] == args.target and "Confectory.MultiPlay" not in report["includedPacks"]
    if args.compile_only:
        print(f"PASS {args.target} protected chat compiled; no target runtime executed")
    else:
        assert args.target == "linux", "Use --compile-only for a Windows target"
        regular_flow(report["run"], checkout, root / "regular")
        lost_reply_flow(report["run"], checkout, root / "loss")
        transport_flow(report["run"], checkout, root / "separated")
        if args.isolated_docker_image:
            with isolated_docker(args.isolated_docker_image) as launch:
                transport_flow(report["run"], checkout, root / "isolated", launch)
        if args.relay_docker_image:
            with separated_relay_networks(args.relay_docker_image) as launch:
                relay_flow(report["run"], checkout, root / "relay-fixture", launch)
