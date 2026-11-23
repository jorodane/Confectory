"""Run the protected public-chat host and guest in separate local .NET processes."""
import argparse
import base64
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import select
import shutil
import socket
import ssl
import struct
import subprocess
import tempfile
import time

repo = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("tool_checkout", nargs="?", type=Path, default=repo)
parser.add_argument("--target", choices=("linux", "windows"), default="linux")
parser.add_argument("--compile-only", action="store_true")
args = parser.parse_args()
tool_repo = args.tool_checkout.resolve()
dotnet = os.environ.get("CONFECTORY_DOTNET") or shutil.which("dotnet")
cli = tool_repo / "src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll"
assert dotnet and cli.is_file(), "Build the Release CLI and targets or pass their checkout"
env = dict(os.environ, CONFECTORY_DOTNET=dotnet, CONFECTORY_DEV_PUBLIC_CHAT_LOOPBACK="1",
           PATH=str(Path(dotnet).parent) + os.pathsep + os.environ["PATH"])

imports = """import Confectory.EditorHome::StartPublicChatLoopback as Start (string,string,object) -> object;
import Confectory.EditorHome::LocalPublicChat as LocalChat (string,string,string,string,string,string) -> string;
import Confectory.EditorHome::PublicChatInvitations as Invitations (string,string) -> object;
import Confectory.EditorHome.Model::CreatorHost as CreatorHost (string) -> bool;
import Confectory.ProjectChat::OpenProtectedLoopback as Listen (object) -> object;
import Confectory.ProjectChat::ConnectProtectedLoopback as Connect (int,object,string,string,string) -> object;
body common "ProtectedPublicChatFixture.csbody";"""


def message(index):
    return f"{index:032x}"


@contextmanager
def process(command, checkout, directory, mode):
    with tempfile.TemporaryFile(mode="w+t") as errors:
        child = subprocess.Popen(command, cwd=checkout, text=True, stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE, stderr=errors,
                                 env=dict(env, CONFECTORY_EDITOR_REPO=str(checkout),
                                          CONFECTORY_TLS_TEST_MODE=mode, CONFECTORY_TLS_TEST_ROOT=str(directory)))

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
            assert "error" in request(guest, "winner", "send-attachment", id=message(99), box="remote")
            assert guest("close", name="one") == {"status": "ok"}
            assert request(guest, "one", "read").get("error") == "ObjectDisposedException"
            rejoin = host("issue")["invitation"]
            assert connect(guest, route, rejoin, "two") == {"status": "ok"}
            seen(guest, "two")
            assert request(guest, "two", "attachment", id=message(5)) == {"status": "denied"}
            assert host("send", id=message(6), text="After rejoin") == {"status": "ok"}
            seen(guest, "two", 6)
            saved = host("history")
            assert [row["id"] for row in saved["messages"]] == list(map(message, range(1, 7)))
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
    print("PASS separate .NET processes, verified TLS, socket-only admission, race/replay, bounded frames, live attachment, stop and revocation")


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


with tempfile.TemporaryDirectory(prefix="confectory-protected-chat-") as directory:
    root = Path(directory)
    checkout = root / "checkout"
    home = checkout / "examples/editor-home"
    shutil.copytree(repo / "packs", checkout / "packs", ignore=shutil.ignore_patterns(".confectory"))
    shutil.copytree(repo / "examples/editor-home", home, ignore=shutil.ignore_patterns(".confectory"))
    (checkout / "targets").symlink_to(tool_repo / "targets", target_is_directory=True)
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
