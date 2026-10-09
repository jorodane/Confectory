"""Opt-in installed CLI probe using captured production adapter requests.

Linux only. Empty auth home, explicit ephemeral credential store, cleared env,
owned cwd; irreversible child-only seccomp denies ALL socket/connect/send syscalls.
Never sends turn/start, account login, model/list or any user message. Stderr and
raw RPC responses stay unprinted. No firewall/global config/account file changes.
"""
import ctypes
import ctypes.util
import errno
import json
import os
import pathlib
import selectors
import shutil
import socket
import subprocess
import sys
import tempfile
import time


def deny_child_network():
    lib = ctypes.CDLL(ctypes.util.find_library("seccomp") or "libseccomp.so.2", use_errno=True)
    lib.seccomp_init.argtypes = [ctypes.c_uint32]
    lib.seccomp_init.restype = ctypes.c_void_p
    lib.seccomp_syscall_resolve_name.argtypes = [ctypes.c_char_p]
    lib.seccomp_syscall_resolve_name.restype = ctypes.c_int
    lib.seccomp_rule_add.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_int, ctypes.c_uint]
    lib.seccomp_load.argtypes = [ctypes.c_void_p]
    lib.seccomp_release.argtypes = [ctypes.c_void_p]
    context = lib.seccomp_init(0x7FFF0000)  # ALLOW except explicit network syscall denies.
    if not context:
        raise RuntimeError("No network guard; refusing to start CLI")
    try:
        # Prevent io_uring from performing networking outside these syscall hooks.
        for name in ("socket", "connect", "sendto", "sendmsg", "sendmmsg",
                     "io_uring_setup", "io_uring_enter", "io_uring_register"):
            number = lib.seccomp_syscall_resolve_name(name.encode())
            if number < 0 or lib.seccomp_rule_add(context, 0x50000 | errno.EPERM, number, 0) != 0:
                raise RuntimeError("Network guard rule unavailable")
        if lib.seccomp_load(context) != 0:
            raise RuntimeError("Network guard load failed")
    finally:
        lib.seccomp_release(context)
    # In this same child BEFORE exec, prove an Internet socket cannot be created.
    for family in (socket.AF_INET, socket.AF_INET6, socket.AF_UNIX):
        try:
            candidate = socket.socket(family)
        except PermissionError:
            continue
        candidate.close()
        raise RuntimeError("Network guard ineffective; refusing to exec")


binary, capture = sys.argv[1:]
assert sys.platform == "linux" and pathlib.Path(binary).is_absolute()
requests = [json.loads(line) for line in pathlib.Path(capture).read_text().splitlines()]
initialize = next(x for x in requests if x.get("method") == "initialize")
thread = next(x for x in requests if x.get("method") == "thread/start")
assert thread["params"]["environments"] == []
assert thread["params"]["dynamicTools"]  # Actual compiled public tool definitions.
assert all(x["type"] == "function" for x in thread["params"]["dynamicTools"])
owned = pathlib.Path(tempfile.mkdtemp(prefix="confectory-codex-offline-", dir="/tmp"))
home, scratch = owned / "empty-home", owned / "scratch"
home.mkdir()
scratch.mkdir()
env = {"CODEX_HOME": str(home), "TMPDIR": str(scratch), "TMP": str(scratch), "TEMP": str(scratch), "PATH": "/usr/bin:/bin"}
# This fresh home receives no copied auth, config or account state. CLI overrides
# affect this disposable subprocess only; parent/global settings are unchanged.
launch = json.loads(pathlib.Path(capture).with_name("owned-launch.json").read_text())
assert launch[:3] == ["app-server", "--stdio", "--strict-config"]
argv = [binary, *launch, "-c", 'cli_auth_credentials_store="ephemeral"']
process = None
try:
    process = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.DEVNULL, env=env, cwd=scratch,
                               preexec_fn=deny_child_network, start_new_session=True)
    selector = selectors.DefaultSelector()
    selector.register(process.stdout, selectors.EVENT_READ)
    pending = bytearray()
    serial = 0

    def read_message(deadline):
        while b"\n" not in pending:
            if not selector.select(max(0, deadline - time.monotonic())):
                raise TimeoutError("Installed CLI RPC timed out; no inference attempted")
            chunk = os.read(process.stdout.fileno(), 65536)
            if not chunk:
                raise RuntimeError("Installed CLI exited before RPC; diagnostics suppressed")
            pending.extend(chunk)
            if len(pending) > 1048576:
                raise RuntimeError("Bounded RPC buffer exceeded")
        line, _, remainder = pending.partition(b"\n")
        pending[:] = remainder
        return json.loads(line)

    def rpc(method, params):
        global serial
        assert method in {"initialize", "account/read", "config/read", "thread/start"}
        serial += 1
        process.stdin.write((json.dumps({"id": serial, "method": method, "params": params}) + "\n").encode())
        process.stdin.flush()
        deadline = time.monotonic() + 12
        for _ in range(256):
            message = read_message(deadline)
            if message.get("id") == serial and "method" not in message:
                if "error" in message:
                    raise RuntimeError("Installed RPC refused " + method + "; raw error suppressed")
                return message["result"]
        raise RuntimeError("Bounded RPC event count exceeded")

    rpc("initialize", initialize["params"])
    process.stdin.write(b'{"method":"initialized","params":{}}\n')
    process.stdin.flush()
    account = rpc("account/read", {"refreshToken": False})
    assert account.get("account") is None, "Unexpected account; stop without using it"
    config = rpc("config/read", {"includeLayers": False})["config"]
    # Never print configuration values; refuse unexpected credential mode/features.
    assert config.get("cli_auth_credentials_store") == "ephemeral"
    assert config.get("web_search") == "disabled"
    assert not config.get("model_providers"), "Inherited custom provider configuration; stop before thread"
    # Rebind only discovered extension IDs, as the real adapter does with config/read.
    # The captured fixture proves policy serialization; installed IDs differ by host.
    assert all(value is False and (key.startswith("plugins.") or key.startswith("mcp_servers."))
               for key, value in thread["params"]["config"].items())
    denied = {}
    for group in ("plugins", "mcp_servers"):
        entries = config.get(group) or {}
        assert isinstance(entries, dict) and len(entries) <= 256
        for name in entries:
            denied[group + "." + json.dumps(name) + ".enabled"] = False
    thread["params"]["config"] = denied
    for feature in ("shell_tool", "apps", "hooks", "multi_agent", "multi_agent_v2", "browser_use", "code_mode_host"):
        assert config.get("features", {}).get(feature) is False, "Feature disable was not effective"
    params = thread["params"]
    params["cwd"] = str(scratch)  # Original adapter-owned scratch has retired.
    result = rpc("thread/start", params)
    assert result.get("thread", {}).get("id")
    assert result["thread"].get("environments") == [], "Server retained an environment; stop"
    assert not result.get("instructionSources"), "Unexpected instruction files; stop"
    assert not (home / "auth.json").exists(), "Probe created auth storage"
    print("Installed no-inference preflight PASS: child network syscalls denied; account null; effective ephemeral credentials and disabled features; initialize and captured thread/start accepted; returned thread environments empty; thread extension-disable overrides accepted (capability filtering unverified); no instruction sources. Tool inventory/execution and live inference NOT verified.")
finally:
    if process is not None:
        process.stdin.close()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            import signal
            os.killpg(process.pid, signal.SIGKILL)
            process.wait(timeout=2)
    shutil.rmtree(owned)
